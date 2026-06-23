from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RewriteRequest(BaseModel):
    resume_id: str
    target_role: Optional[str] = None
    tone: str = "professional"  # professional, creative, executive, technical
    focus_areas: list[str] = ["summary", "experience", "skills"]


class RewriteResponse(BaseModel):
    version_id: str
    version_number: int
    original: dict
    rewritten: dict
    improvements: list[str]
    target_role: Optional[str] = None
    tone: str
    created_at: datetime


class VersionListItem(BaseModel):
    id: str
    version_number: int
    target_role: Optional[str] = None
    tone: str
    created_at: datetime
