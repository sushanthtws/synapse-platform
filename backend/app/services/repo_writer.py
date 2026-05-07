"""Persistence layer for skill bundles.

Each skill is stored under a per-slug folder containing every uploaded file
verbatim. Local filesystem is active; GCS implementation is included but
commented out — see README "Switching skill file storage" section.
"""
import os
import io
import json
import re
import zipfile
from typing import Iterable, List, Tuple

from app.core.config import settings


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip("-")


# ── Local helpers ──────────────────────────────────────────────────────────────

def _save_local(slug: str, files: List[Tuple[str, bytes]], skill_card: dict) -> str:
    """Write skill_card.json + every uploaded file (with relative path preserved)."""
    repo_path = os.path.join(settings.base_skill_dir, slug)
    os.makedirs(repo_path, exist_ok=True)

    # 1. Refined skill card
    with open(os.path.join(repo_path, "skill_card.json"), "w") as f:
        json.dump(skill_card, f, indent=2)

    # 2. Every uploaded file as-is, preserving its relative path
    for rel_path, data in files:
        rel_path = rel_path.lstrip("/")
        # Defensive: never escape the skill folder
        if ".." in rel_path.split("/"):
            continue
        full = os.path.join(repo_path, rel_path)
        os.makedirs(os.path.dirname(full) or repo_path, exist_ok=True)
        with open(full, "wb") as f:
            f.write(data)
    return repo_path


def _list_local(repo_path: str) -> List[dict]:
    """List all files (excluding skill_card.json) under a local skill folder."""
    out: List[dict] = []
    if not os.path.isdir(repo_path):
        return out
    for root, _, names in os.walk(repo_path):
        for n in names:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, repo_path)
            if rel == "skill_card.json":
                continue
            out.append({"path": rel, "size": os.path.getsize(full)})
    return out


def _read_local(repo_path: str, rel_path: str) -> bytes:
    rel_path = rel_path.lstrip("/")
    if ".." in rel_path.split("/"):
        raise ValueError("invalid path")
    full = os.path.join(repo_path, rel_path)
    if not full.startswith(os.path.abspath(repo_path)):
        raise ValueError("invalid path")
    with open(full, "rb") as f:
        return f.read()


def _zip_local(repo_path: str) -> bytes:
    """Zip a local skill folder into an in-memory archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, names in os.walk(repo_path):
            for n in names:
                full = os.path.join(root, n)
                rel = os.path.relpath(full, repo_path)
                zf.write(full, rel)
    return buf.getvalue()


# ── GCS helpers ────────────────────────────────────────────────────────────────

def _save_gcs(slug: str, files: List[Tuple[str, bytes]], skill_card: dict) -> str:
    from google.cloud import storage  # lazy import — not needed in dev

    bucket_name = settings.gcs_bucket
    prefix = f"skills/{slug}"
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    bucket.blob(f"{prefix}/skill_card.json").upload_from_string(
        json.dumps(skill_card, indent=2),
        content_type="application/json",
    )
    for rel_path, data in files:
        rel_path = rel_path.lstrip("/")
        if ".." in rel_path.split("/"):
            continue
        bucket.blob(f"{prefix}/{rel_path}").upload_from_string(data)
    return f"gs://{bucket_name}/{prefix}"


def _list_gcs(repo_path: str) -> List[dict]:
    from google.cloud import storage

    bucket_name, prefix = _parse_gs(repo_path)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    out: List[dict] = []
    for blob in bucket.list_blobs(prefix=prefix + "/"):
        rel = blob.name[len(prefix) + 1:]
        if rel == "skill_card.json":
            continue
        out.append({"path": rel, "size": blob.size or 0})
    return out


def _read_gcs(repo_path: str, rel_path: str) -> bytes:
    from google.cloud import storage

    bucket_name, prefix = _parse_gs(repo_path)
    client = storage.Client()
    return client.bucket(bucket_name).blob(f"{prefix}/{rel_path.lstrip('/')}").download_as_bytes()


def _zip_gcs(repo_path: str) -> bytes:
    from google.cloud import storage

    bucket_name, prefix = _parse_gs(repo_path)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for blob in bucket.list_blobs(prefix=prefix + "/"):
            rel = blob.name[len(prefix) + 1:]
            zf.writestr(rel, blob.download_as_bytes())
    return buf.getvalue()


def _parse_gs(repo_path: str) -> Tuple[str, str]:
    # gs://bucket/skills/<slug>
    no_scheme = repo_path[5:]
    bucket, _, rest = no_scheme.partition("/")
    return bucket, rest


# ── Public API ─────────────────────────────────────────────────────────────────

def save_skill_to_repo(skill: dict, files: List[Tuple[str, bytes]]) -> str:
    """Persist a skill bundle. `files` is a list of (relative_path, bytes)."""
    slug = skill.get("slug") or slugify(skill.get("title", "unknown"))

    # ── Local storage (active) ────────────────────────────────────────────────
    return _save_local(slug, files, skill)

    # ── GCS storage (enable on Cloud Run — see README) ────────────────────────
    # if settings.gcs_bucket:
    #     return _save_gcs(slug, files, skill)
    # return _save_local(slug, files, skill)


def list_skill_files(repo_path: str) -> List[dict]:
    # ── Local (active) ────────────────────────────────────────────────────────
    return _list_local(repo_path)
    # ── GCS (commented) ───────────────────────────────────────────────────────
    # if repo_path.startswith("gs://"):
    #     return _list_gcs(repo_path)
    # return _list_local(repo_path)


def read_skill_file(repo_path: str, rel_path: str) -> bytes:
    return _read_local(repo_path, rel_path)
    # if repo_path.startswith("gs://"):
    #     return _read_gcs(repo_path, rel_path)
    # return _read_local(repo_path, rel_path)


def zip_skill(repo_path: str) -> bytes:
    return _zip_local(repo_path)
    # if repo_path.startswith("gs://"):
    #     return _zip_gcs(repo_path)
    # return _zip_local(repo_path)
