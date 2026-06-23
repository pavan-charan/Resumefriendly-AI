from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SkillGapRequest(BaseModel):
    resume_id: Optional[str] = None
    target_role: str


class SkillItem(BaseModel):
    name: str
    proficiency: int  # 1-10


class MissingSkillItem(BaseModel):
    name: str
    importance: str  # critical, important, nice-to-have
    resources: list[str] = []


class SkillGapResponse(BaseModel):
    id: str
    target_role: str
    current_skills: list[SkillItem]
    missing_skills: list[MissingSkillItem]
    overall_readiness: int  # 0-100
    recommendations: list[str]
    created_at: datetime


class SkillGapListItem(BaseModel):
    id: str
    target_role: str
    overall_readiness: int
    created_at: datetime
