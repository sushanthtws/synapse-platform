import json

from app.workers.celery_app import celery_app
from app.services.refiner import refine_skill
from app.db.base import engine
from app.db.session import SessionLocal
from app.models.skill import Skill


@celery_app.task
def process_skill_async(raw_skill: dict):
    clean_skill = refine_skill(raw_skill)
    db = SessionLocal()
    try:
        skill = Skill(
            title=clean_skill.get("title"),
            summary=clean_skill.get("summary"),
            domain=clean_skill.get("domain"),
            usage=clean_skill.get("usage"),
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
    finally:
        db.close()
    return clean_skill
