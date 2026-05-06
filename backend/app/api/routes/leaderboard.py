import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillResponse

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard", response_model=list[SkillResponse])
def leaderboard(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    return sorted(skills, key=lambda s: len(json.loads(s.key_points or "[]")), reverse=True)[:10]
