from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ExperienceItem(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None

class EducationItem(BaseModel):
    degree: Optional[str] = None
    major: Optional[str] = None
    school: Optional[str] = None

class ParsedResumeContent(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    projects: List[str] = []
    certifications: List[str] = []

class ResumeResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    file_name: str
    file_path: str
    parsed_content: ParsedResumeContent
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    resume_id: UUID
    file_name: str
    parsed_content: ParsedResumeContent
