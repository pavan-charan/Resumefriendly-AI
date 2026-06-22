from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.repositories.resume import ResumeRepository
from app.repositories.jd import JobDescriptionRepository
from app.schemas.jd import JobDescriptionCreate, JobDescriptionResponse, JDMatchRequest, JDMatchResponse
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/jds", tags=["Job Descriptions"])

@router.post("/", response_model=JobDescriptionResponse, status_code=201)
def create_job_description(
    jd_in: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jd_repo = JobDescriptionRepository(db)
    db_jd = jd_repo.create(
        creator_id=current_user.id,
        title=jd_in.title,
        company_name=jd_in.company_name,
        department=jd_in.department,
        raw_content=jd_in.raw_content,
        requirements=jd_in.requirements or jd_in.raw_content
    )
    return db_jd

@router.post("/match", response_model=JDMatchResponse)
def match_resume_to_jd(
    match_in: JDMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Fetch Resume
    resume_repo = ResumeRepository(db)
    db_resume = resume_repo.get_by_id(match_in.resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
        
    # Check ownership
    if db_resume.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to match this resume"
        )

    # 2. Run Match
    matcher = MatchingService()
    results = matcher.match_resume_to_jd(
        resume_text=db_resume.raw_text,
        resume_skills=db_resume.parsed_content.get("skills", []),
        jd_text=match_in.jd_text
    )
    
    return results
