from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class JobDescriptionCreate(BaseModel):
    title: str
    company_name: str
    department: Optional[str] = None
    raw_content: str
    requirements: Optional[str] = None

class JobDescriptionResponse(BaseModel):
    id: UUID
    creator_id: UUID
    title: str
    company_name: str
    department: Optional[str] = None
    raw_content: str
    requirements: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class JDMatchRequest(BaseModel):
    resume_id: UUID
    jd_text: str

class JDMatchResponse(BaseModel):
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]
