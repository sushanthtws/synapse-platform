import json
import traceback
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Body
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import frontmatter
import structlog

from app.api.deps import verify_api_key
from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillResponse
from app.services.refiner import refine_skill
from app.services.repo_writer import (
    save_skill_to_repo,
    slugify,
    list_skill_files,
    read_skill_file,
    zip_skill,
)
from app.services.artifact_classifier import classify, pick_primary_markdown

router = APIRouter(tags=["skills"])
log = structlog.get_logger(__name__)


@router.get("/skills", response_model=list[SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    return db.query(Skill).all()


@router.post("/skills/upload")
async def upload_skill(
    files: List[UploadFile] = File(...),
    relative_paths: List[str] | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a skill as either a single file or a folder.

    - Single file: send one entry in `files`.
    - Folder: send N entries in `files` plus matching N entries in `relative_paths`
      (browser webkitRelativePath values). When omitted, file.filename is used.
    """
    try:
        # ── 1. Read every uploaded file ───────────────────────────────────────
        bundle: list[tuple[str, bytes]] = []
        for i, f in enumerate(files):
            content = await f.read()
            rel = (relative_paths[i] if relative_paths and i < len(relative_paths) else f.filename) or f.filename
            # Browsers may send full paths like "MySkill/SKILL.md" — keep as-is
            bundle.append((rel, content))
        if not bundle:
            raise HTTPException(status_code=400, detail="no files uploaded")

        # ── 2. Pick the primary markdown to drive title + AI refinement ──────
        rel_paths = [p for p, _ in bundle]

        # Reject bundles that contain more than one skill (multiple SKILL.md
        # or, failing that, multiple README.md at distinct folder roots).
        skill_md = [p for p in rel_paths if p.rsplit("/", 1)[-1].lower() in ("skill.md", "skills.md")]
        if len(skill_md) > 1:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Multiple skills detected in this folder ({len(skill_md)} SKILL.md files: "
                    f"{', '.join(skill_md)}). Upload each skill folder separately."
                ),
            )
        if not skill_md:
            readme_md = [p for p in rel_paths if p.rsplit("/", 1)[-1].lower() == "readme.md"]
            if len(readme_md) > 1:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Multiple skills detected in this folder ({len(readme_md)} README.md files: "
                        f"{', '.join(readme_md)}). Upload each skill folder separately."
                    ),
                )

        primary_rel = pick_primary_markdown(rel_paths)
        if not primary_rel:
            raise HTTPException(status_code=400, detail="bundle must contain at least one .md file")

        primary_bytes = next(b for p, b in bundle if p == primary_rel)
        primary_text = primary_bytes.decode("utf-8", errors="replace")

        post = frontmatter.loads(primary_text)
        title = post.get("name") or post.get("title") or _title_from_filename(primary_rel)
        slug = slugify(title)

        # ── 3. Reject re-upload of a finalised skill ─────────────────────────
        existing = db.query(Skill).filter(Skill.slug == slug).first()
        if existing and existing.is_complete:
            raise HTTPException(
                status_code=409,
                detail=f"Skill '{slug}' is already marked complete. Upload as a new unique skill.",
            )

        # ── 4. Classify every file in the bundle ─────────────────────────────
        artifacts = []
        for rel, data in bundle:
            t, role = classify(rel)
            artifacts.append({"path": rel, "type": t, "role": role, "size": len(data)})

        # ── 5. Refine via LLM with file-listing context ──────────────────────
        raw_tags = post.get("allowed-tools", [])
        if not isinstance(raw_tags, list):
            raw_tags = [str(raw_tags)]
        raw_skill = {
            "title": title,
            "description": post.get("description", "No description provided"),
            "tags": raw_tags,
            "model": post.get("model", "N/A"),
            "effort": post.get("effort", "N/A"),
            "raw_content": primary_text,
            "file_listing": rel_paths,
        }
        log.info("skill.upload.start", title=title, files=len(bundle), slug=slug)
        clean = refine_skill(raw_skill)
        clean["title"] = clean.get("title") or title
        clean["slug"] = slug
        clean["artifacts"] = artifacts
        clean["raw_content"] = primary_text[:50_000]
        clean["is_complete"] = False
        # Surface review-wizard fields with safe defaults
        clean.setdefault("where_to_use", "")
        clean.setdefault("why_to_use", "")
        clean.setdefault("how_to_use", "")
        clean["is_in_use"] = False
        clean["used_at"] = ""

        # ── 6. Persist files (verbatim) + skill_card.json ────────────────────
        clean["repo_path"] = save_skill_to_repo(clean, bundle)

        # ── 7. Insert/update DB ──────────────────────────────────────────────
        if existing:
            # Same slug, not yet complete — overwrite the draft record
            existing.title = clean.get("title")
            existing.summary = clean.get("summary")
            existing.domain = clean.get("domain")
            existing.usage = clean.get("usage")
            existing.tags = json.dumps(clean.get("tags", []))
            existing.tools = json.dumps(clean.get("tools", []))
            existing.languages = json.dumps(clean.get("languages", []))
            existing.tech_stack = json.dumps(clean.get("tech_stack", []))
            existing.key_points = json.dumps(clean.get("key_points", []))
            existing.artifacts = json.dumps(artifacts)
            existing.where_to_use = clean.get("where_to_use", "")
            existing.why_to_use = clean.get("why_to_use", "")
            existing.how_to_use = clean.get("how_to_use", "")
            existing.repo_path = clean.get("repo_path")
            existing.raw_content = clean.get("raw_content")
            db.commit()
            db.refresh(existing)
            skill = existing
        else:
            skill = Skill(
                title=clean.get("title"),
                slug=slug,
                summary=clean.get("summary"),
                domain=clean.get("domain"),
                usage=clean.get("usage"),
                tags=json.dumps(clean.get("tags", [])),
                tools=json.dumps(clean.get("tools", [])),
                languages=json.dumps(clean.get("languages", [])),
                tech_stack=json.dumps(clean.get("tech_stack", [])),
                key_points=json.dumps(clean.get("key_points", [])),
                artifacts=json.dumps(artifacts),
                where_to_use=clean.get("where_to_use", ""),
                why_to_use=clean.get("why_to_use", ""),
                how_to_use=clean.get("how_to_use", ""),
                repo_path=clean.get("repo_path"),
                raw_content=clean.get("raw_content"),
                is_complete=False,
                is_in_use=False,
                used_at="",
            )
            db.add(skill)
            db.commit()
            db.refresh(skill)

        log.info("skill.upload.success", title=skill.title, id=skill.id)
        # Returned shape includes the prompt-for-completion flag so the UI can ask.
        return {
            **clean,
            "id": skill.id,
            "needs_completion_confirmation": True,
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("skill.upload.failed", error=str(e), trace=traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


class SkillEdit(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    domain: Optional[str] = None
    usage: Optional[str] = None
    where_to_use: Optional[str] = None
    why_to_use: Optional[str] = None
    how_to_use: Optional[str] = None
    tags: Optional[list[str]] = None
    tools: Optional[list[str]] = None
    tech_stack: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    key_points: Optional[list[str]] = None


@router.patch("/skills/{skill_id}")
def edit_skill(skill_id: int, payload: SkillEdit, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")
    if skill.is_complete:
        raise HTTPException(status_code=409, detail="skill is finalized; edits not allowed")

    data = payload.model_dump(exclude_unset=True)
    # Scalar fields
    for f in ("title", "summary", "domain", "usage",
              "where_to_use", "why_to_use", "how_to_use"):
        if f in data and data[f] is not None:
            setattr(skill, f, data[f])
    # List fields stored as JSON
    for f in ("tags", "tools", "tech_stack", "languages", "key_points"):
        if f in data and data[f] is not None:
            setattr(skill, f, json.dumps(data[f]))

    # Mirror edits into skill_card.json on disk so the bundle stays consistent
    try:
        import os
        if skill.repo_path and os.path.isdir(skill.repo_path):
            card_path = os.path.join(skill.repo_path, "skill_card.json")
            if os.path.exists(card_path):
                with open(card_path) as f:
                    card = json.load(f)
                card.update({k: v for k, v in data.items() if v is not None})
                with open(card_path, "w") as f:
                    json.dump(card, f, indent=2)
    except Exception:
        # Best-effort; DB is source of truth
        pass

    db.commit()
    db.refresh(skill)
    return {"id": skill.id, "ok": True}


class CompleteRequest(BaseModel):
    is_in_use: Optional[bool] = False
    used_at: Optional[str] = ""


@router.patch("/skills/{skill_id}/complete")
def mark_skill_complete(skill_id: int, payload: CompleteRequest | None = None, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")
    skill.is_complete = True
    if payload:
        skill.is_in_use = bool(payload.is_in_use)
        skill.used_at = (payload.used_at or "").strip()
    db.commit()
    return {"id": skill.id, "is_complete": True, "is_in_use": skill.is_in_use, "used_at": skill.used_at}


@router.get("/skills/{skill_id}/files")
def list_files(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")
    raw_files = list_skill_files(skill.repo_path or "")
    artifacts = json.loads(skill.artifacts or "[]")
    artifact_by_path = {a["path"].lstrip("/"): a for a in artifacts}
    out = []
    for f in raw_files:
        meta = artifact_by_path.get(f["path"].lstrip("/"))
        if meta:
            out.append({**f, "type": meta.get("type", "other"), "role": meta.get("role", "")})
        else:
            t, role = classify(f["path"])
            out.append({**f, "type": t, "role": role})
    return out


@router.get("/skills/{skill_id}/file")
def get_file(skill_id: int, path: str, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")
    try:
        data = read_skill_file(skill.repo_path or "", path)
    except Exception:
        raise HTTPException(status_code=404, detail="file not found")
    return Response(content=data, media_type="text/plain; charset=utf-8")


@router.get("/skills/{skill_id}/download")
def download_zip(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")
    data = zip_skill(skill.repo_path or "")
    fname = f"{skill.slug or 'skill'}.zip"
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.delete("/reset-db", tags=["admin"])
def reset_db(_=Depends(verify_api_key), db: Session = Depends(get_db)):
    """Clear all skills from the database."""
    try:
        db.query(Skill).delete()
        db.commit()
        return {"status": "db cleared"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _title_from_filename(rel_path: str) -> str:
    base = rel_path.rsplit("/", 1)[-1]
    base = base.rsplit(".", 1)[0]
    return base.replace("_", " ").replace("-", " ").title() or "Untitled Skill"
