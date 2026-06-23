from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import RoleChecker
from app.models.user import User
from app.schemas.jobs import JobCreate, JobUpdate, JobResponse, DashboardStatsResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Job Management"])
is_recruiter = RoleChecker(["RECRUITER", "ADMIN"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = JobService(db)
    return service.get_dashboard_stats(current_user.id)

@router.post("", response_model=JobResponse, status_code=201)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = JobService(db)
    return service.create_job(current_user.id, job_in.dict())

@router.get("", response_model=List[JobResponse])
def get_jobs(
    status: Optional[str] = None,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = JobService(db)
    return service.get_jobs(current_user.id, status)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = JobService(db)
    job = service.get_job(current_user.id, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not owned by recruiter"
        )
    return job

@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: UUID,
    job_in: JobUpdate,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = JobService(db)
    job = service.update_job(current_user.id, job_id, job_in.dict(exclude_unset=True))
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or update failed"
        )
    return job

@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: UUID,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = JobService(db)
    success = service.delete_job(current_user.id, job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or delete failed"
        )
    return None
