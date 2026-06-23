from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    job_url: Optional[str] = None
    status: str = "applied"
    applied_date: Optional[date] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    next_followup: Optional[date] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[date] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    next_followup: Optional[date] = None


class ApplicationResponse(BaseModel):
    id: str
    company_name: str
    job_title: str
    job_url: Optional[str] = None
    status: str
    applied_date: Optional[date] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    next_followup: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class TrackerStats(BaseModel):
    total: int
    applied: int
    screening: int
    interviewing: int
    offer: int
    rejected: int
    accepted: int
    withdrawn: int
