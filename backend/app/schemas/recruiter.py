from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class CandidateSummary(BaseModel):
    skills: List[str]
    experience: str
    education: str
    match_percentage: int

class RankedCandidate(BaseModel):
    rank: int
    candidate_name: str
    email: str
    match_score: int
    summary: CandidateSummary

class RecruiterScreenResponse(BaseModel):
    job_id: UUID
    ranked_candidates: List[RankedCandidate]
