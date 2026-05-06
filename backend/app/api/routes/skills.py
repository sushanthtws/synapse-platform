import json
import traceback

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import frontmatter
import structlog

from app.api.deps import verify_api_key
from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillResponse
from app.services.refiner import refine_skill
from app.services.repo_writer import save_skill_to_repo

router = APIRouter(tags=["skills"])
log = structlog.get_logger(__name__)


@router.get("/skills", response_model=list[SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    return db.query(Skill).all()


@router.post("/skills/upload")
async def upload_skill(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        content = await file.read()
        text = content.decode("utf-8")
        post = frontmatter.loads(text)
        tags = post.get("allowed-tools", [])
        if not isinstance(tags, list):
            tags = [str(tags)]
        raw_skill = {
            "title": post.get("name", "Untitled Skill"),
            "description": post.get("description", "No description provided"),
            "tags": tags,
            "model": post.get("model", "N/A"),
            "effort": post.get("effort", "N/A"),
            "raw_content": text,
        }
        log.info("skill.upload.start", title=raw_skill["title"])
        clean_skill = refine_skill(raw_skill)
        clean_skill["raw_content"] = text[:50_000]  # cap at 50k chars for DB storage
        clean_skill["repo_path"] = save_skill_to_repo(clean_skill)
        skill = Skill(
            title=clean_skill.get("title"),
            summary=clean_skill.get("summary"),
            domain=clean_skill.get("domain"),
            usage=clean_skill.get("usage"),
            difficulty=clean_skill.get("difficulty", "medium"),
            tags=json.dumps(clean_skill.get("tags", [])),
            tools=json.dumps(clean_skill.get("tools", [])),
            languages=json.dumps(clean_skill.get("languages", [])),
            tech_stack=json.dumps(clean_skill.get("tech_stack", [])),
            key_points=json.dumps(clean_skill.get("key_points", [])),
            repo_path=clean_skill.get("repo_path"),
            raw_content=clean_skill.get("raw_content"),
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
        log.info("skill.upload.success", title=skill.title, id=skill.id)
        return clean_skill
    except Exception as e:
        log.error("skill.upload.failed", error=str(e), trace=traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset-db", tags=["admin"])
def reset_db(_=Depends(verify_api_key), db: Session = Depends(get_db)):
    """Clear all skills from the database."""
    try:
        db.query(Skill).delete()
        db.commit()
        return {"status": "db cleared"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
