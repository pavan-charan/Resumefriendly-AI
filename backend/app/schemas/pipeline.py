from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class PipelineMoveRequest(BaseModel):
    pipeline_id: UUID
    to_stage: str = Field(..., pattern="^(Applied|Screening|Shortlisted|Interview Scheduled|Technical Round|Manager Round|HR Round|Offer|Hired|Rejected)$")
    notes: Optional[str] = None

class CandidatePipelineResponse(BaseModel):
    id: UUID
    job_id: UUID
    resume_id: UUID
    stage: str
    ats_score: Optional[int] = None
    jd_match_score: Optional[int] = None
    candidate_name: str
    email: str
    phone: str
    skills: List[str]
    education: str
    experience: str
    projects: List[str]
    certifications: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TimelineItemResponse(BaseModel):
    type: str # applied, stage_move, note, feedback
    title: str
    timestamp: datetime
    details: str

class CandidateNoteCreate(BaseModel):
    pipeline_id: UUID
    content: str

class CandidateFeedbackCreate(BaseModel):
    pipeline_id: UUID
    score: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None

class CandidateNoteResponse(BaseModel):
    id: UUID
    pipeline_id: UUID
    recruiter_name: str
    content: str
    created_at: datetime

class CandidateFeedbackResponse(BaseModel):
    id: UUID
    pipeline_id: UUID
    interviewer_name: str
    score: int
    feedback_text: Optional[str] = None
    created_at: datetime
