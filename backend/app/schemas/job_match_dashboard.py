from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobMatchRequest(BaseModel):
    resume_id: str
    preferred_roles: list[str] = []
    preferred_locations: list[str] = []


class JobMatchItem(BaseModel):
    job_id: str
    title: str
    company_name: str
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]


class JobMatchResponse(BaseModel):
    matches: list[JobMatchItem]
    total_jobs_scanned: int
