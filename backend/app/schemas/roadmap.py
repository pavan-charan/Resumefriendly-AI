from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoadmapRequest(BaseModel):
    resume_id: Optional[str] = None
    current_role: str
    target_role: str
    timeline_months: int = 12


class RoadmapPhase(BaseModel):
    phase_name: str
    duration_months: int
    milestones: list[str]
    skills_to_learn: list[str]
    resources: list[str]


class CertificationItem(BaseModel):
    name: str
    provider: str
    estimated_time: str


class RoadmapResponse(BaseModel):
    id: str
    current_role: str
    target_role: str
    timeline_months: int
    phases: list[RoadmapPhase]
    certifications: list[CertificationItem]
    target_companies: list[str]
    salary_progression: dict
    created_at: datetime


class RoadmapListItem(BaseModel):
    id: str
    current_role: str
    target_role: str
    timeline_months: int
    created_at: datetime
