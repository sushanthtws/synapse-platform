import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.skill import Skill

router = APIRouter(tags=["analytics"])


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    domains = list({s.domain for s in skills if s.domain})
    all_tools = [t for s in skills for t in json.loads(s.tools or "[]")]
    tool_counts: dict = {}
    for t in all_tools:
        tool_counts[t] = tool_counts.get(t, 0) + 1
    top_tools = sorted(tool_counts, key=tool_counts.get, reverse=True)[:5]  # type: ignore[arg-type]
    difficulty: dict = {}
    for s in skills:
        d = s.difficulty or "medium"
        difficulty[d] = difficulty.get(d, 0) + 1
    return {
        "total_skills": len(skills),
        "domains": domains,
        "top_tools": top_tools,
        "difficulty_breakdown": difficulty,
    }
