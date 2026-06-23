from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class JobSkillBase(BaseModel):
    skill_name: str
    is_required: bool

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    employment_type: Optional[str] = "Full-time"
    experience_required: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "Active"
    skills_required: List[str] = []
    skills_preferred: List[str] = []

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    experience_required: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None

class JobResponse(BaseModel):
    id: UUID
    recruiter_id: UUID
    title: str
    department: Optional[str] = None
    employment_type: Optional[str] = None
    experience_required: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    skills: List[JobSkillBase] = []

    class Config:
        from_attributes = True

class DashboardStatsResponse(BaseModel):
    open_jobs: int
    closed_jobs: int
    draft_jobs: int
    archived_jobs: int
    total_applications: int
    active_hiring_pipelines: int
