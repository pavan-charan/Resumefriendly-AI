from pydantic import BaseModel
from typing import List
from uuid import UUID

class ATSScoreBreakdown(BaseModel):
    skills: int
    keywords: int
    experience: int
    formatting: int
    education: int
    contact_info: int

class ATSScoreExplainability(BaseModel):
    missing_keywords: List[str]
    missing_sections: List[str]
    formatting_issues: List[str]
    weak_content_areas: List[str]
    strengths: List[str]

class ATSReportResponse(BaseModel):
    overall_score: int
    breakdown: ATSScoreBreakdown
    explainability: ATSScoreExplainability
