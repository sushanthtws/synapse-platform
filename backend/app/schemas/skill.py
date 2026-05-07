import json
from pydantic import BaseModel, field_validator
from typing import List, Optional


class SkillBase(BaseModel):
    title: str
    slug: Optional[str] = ""
    summary: Optional[str] = ""
    domain: Optional[str] = "unknown"
    usage: Optional[str] = "unknown"
    tags: Optional[List[str]] = []
    tools: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    tech_stack: Optional[List[str]] = []
    key_points: Optional[List[str]] = []
    artifacts: Optional[List[dict]] = []
    where_to_use: Optional[str] = ""
    why_to_use: Optional[str] = ""
    how_to_use: Optional[str] = ""
    is_in_use: Optional[bool] = False
    used_at: Optional[str] = ""
    repo_path: Optional[str] = ""
    is_complete: Optional[bool] = False

    @field_validator("tags", "tools", "languages", "tech_stack", "key_points", "artifacts", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []


class SkillResponse(SkillBase):
    id: int

    class Config:
        from_attributes = True
