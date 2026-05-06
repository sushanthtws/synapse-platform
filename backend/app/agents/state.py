from typing import TypedDict, List, Optional


class SkillState(TypedDict):
    raw_content: str
    title: str
    summary: Optional[str]
    domain: Optional[str]
    tags: List[str]
    tools: List[str]
    languages: List[str]
    tech_stack: List[str]
    key_points: List[str]
    difficulty: Optional[str]
    repo_path: Optional[str]
    error: Optional[str]
