from app.agents.state import SkillState
from app.services.refiner import refine_skill


def analyze_skill_node(state: SkillState) -> SkillState:
    raw = {"title": state.get("title", "Untitled"), "description": state.get("summary", ""), "raw_content": state.get("raw_content", ""), "tags": state.get("tags", [])}
    return {**state, **refine_skill(raw)}
