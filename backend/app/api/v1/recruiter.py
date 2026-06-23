from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import RoleChecker
from app.models.user import User
from app.schemas.recruiter import RecruiterScreenResponse
from app.services.recruiter_service import RecruiterService

from app.schemas.jd import JobDescriptionResponse

router = APIRouter(prefix="/recruiter", tags=["Recruiter Screening"])

# Enforce Recruiter role
is_recruiter = RoleChecker(["RECRUITER", "ADMIN"])

@router.post("/screen", response_model=RecruiterScreenResponse, status_code=201)
def screen_candidates(
    jd_title: str = Form(...),
    company_name: str = Form(...),
    department: Optional[str] = Form(None),
    jd_text: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    """
    Recruiter endpoint to upload multiple resumes, screen them against a job specification,
    and rank candidates based on semantic compatibility.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded for screening"
        )
        
    recruiter_service = RecruiterService(db)
    response = recruiter_service.screen_and_rank_candidates(
        recruiter_id=current_user.id,
        title=jd_title,
        company_name=company_name,
        department=department or "Engineering",
        jd_text=jd_text,
        files=files
    )
    
    return response

@router.get("/jobs", response_model=List[JobDescriptionResponse])
def get_recruiter_jobs(
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    from app.repositories.jd import JobDescriptionRepository
    jd_repo = JobDescriptionRepository(db)
    return jd_repo.get_all_by_creator_id(current_user.id)

@router.get("/jobs/{jd_id}", response_model=RecruiterScreenResponse)
def get_job_screening_results(
    jd_id: UUID,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    recruiter_service = RecruiterService(db)
    results = recruiter_service.get_ranked_candidates_for_jd(
        recruiter_id=current_user.id,
        jd_id=jd_id
    )
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found or not owned by recruiter"
        )
    return results
