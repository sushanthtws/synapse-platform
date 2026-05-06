import os
import json
import re

from app.core.config import settings


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip("-")


# ── Local helpers ──────────────────────────────────────────────────────────────

def _save_local(skill: dict, slug: str) -> str:
    repo_path = os.path.join(settings.base_skill_dir, slug)
    os.makedirs(repo_path, exist_ok=True)
    with open(os.path.join(repo_path, "skill_card.json"), "w") as f:
        json.dump(skill, f, indent=2)
    with open(os.path.join(repo_path, "README.md"), "w") as f:
        f.write(f"# {skill.get('title')}\n\n{skill.get('summary')}\n")
    return repo_path


# ── GCS helpers ────────────────────────────────────────────────────────────────

def _save_gcs(skill: dict, slug: str) -> str:
    from google.cloud import storage  # lazy import — not needed in dev

    bucket_name = settings.gcs_bucket
    prefix = f"skills/{slug}"

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Upload skill_card.json
    blob_json = bucket.blob(f"{prefix}/skill_card.json")
    blob_json.upload_from_string(
        json.dumps(skill, indent=2),
        content_type="application/json",
    )

    # Upload README.md
    blob_readme = bucket.blob(f"{prefix}/README.md")
    blob_readme.upload_from_string(
        f"# {skill.get('title')}\n\n{skill.get('summary')}\n",
        content_type="text/markdown",
    )

    return f"gs://{bucket_name}/{prefix}"


# ── Public API ─────────────────────────────────────────────────────────────────

def save_skill_to_repo(skill: dict) -> str:
    """
    Save skill files locally (development) or to GCS (production).
    Controlled by APP_ENV and GCS_BUCKET in .env.
    """
    slug = slugify(skill.get("title", "unknown"))

    if settings.app_env == "production" and settings.gcs_bucket:
        return _save_gcs(skill, slug)

    return _save_local(skill, slug)
