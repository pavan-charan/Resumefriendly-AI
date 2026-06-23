from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

class CandidateCompareRequest(BaseModel):
    job_id: UUID
    pipeline_ids: List[UUID]

class InterviewKitRequest(BaseModel):
    job_id: UUID
    resume_id: UUID

class RecruiterChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = [] # list of {"role": "user"|"assistant", "content": "..."}
    selected_job_id: Optional[UUID] = None
