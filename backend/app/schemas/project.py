from pydantic import BaseModel
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class ProjectResponse(ProjectCreate):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
