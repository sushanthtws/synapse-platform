from pydantic import BaseModel
from typing import List, Optional


class AnalyticsResponse(BaseModel):
    total_skills: int
    domains: List[str]
    top_tools: List[str]
    difficulty_breakdown: dict


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""


class ChatResponse(BaseModel):
    reply: str


class ValidationRequest(BaseModel):
    skill_id: int
    feedback: Optional[str] = ""


class ValidationResponse(BaseModel):
    skill_id: int
    status: str
    feedback: Optional[str] = ""
