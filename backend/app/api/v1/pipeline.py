from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import RoleChecker
from app.models.user import User
from app.schemas.pipeline import PipelineMoveRequest, CandidatePipelineResponse, TimelineItemResponse
from app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/pipeline", tags=["Hiring Pipeline"])
is_recruiter = RoleChecker(["RECRUITER", "ADMIN"])

@router.get("/{job_id}", response_model=List[CandidatePipelineResponse])
def get_job_pipeline(
    job_id: UUID,
    stage: Optional[str] = None,
    min_score: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = PipelineService(db)
    return service.get_pipeline(
        recruiter_id=current_user.id,
        job_id=job_id,
        stage=stage,
        min_score=min_score,
        search_query=search
    )

@router.post("/move", response_model=CandidatePipelineResponse)
def move_candidate_pipeline(
    req: PipelineMoveRequest,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = PipelineService(db)
    try:
        updated = service.move_candidate(
            recruiter_id=current_user.id,
            pipeline_id=req.pipeline_id,
            to_stage=req.to_stage,
            notes=req.notes
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline entry not found or unauthorized"
            )
        
        # Map DB model directly back to matching response schema
        resume = updated.resume
        content = resume.parsed_content
        candidate_name = content.get("name", "Unknown Candidate")
        email = content.get("email", "N/A")
        skills = content.get("skills", [])
        
        education_list = content.get("education", [])
        edu_summary = f"{education_list[0].get('degree')} at {education_list[0].get('school')}" if education_list else "N/A"
        
        experience_list = content.get("experience", [])
        exp_summary = f"{experience_list[0].get('role')} at {experience_list[0].get('company')}" if experience_list else "N/A"

        return CandidatePipelineResponse(
            id=updated.id,
            job_id=updated.job_id,
            resume_id=updated.resume_id,
            stage=updated.stage,
            ats_score=updated.ats_score,
            jd_match_score=updated.jd_match_score,
            candidate_name=candidate_name,
            email=email,
            phone=content.get("phone", "N/A"),
            skills=skills,
            education=edu_summary,
            experience=exp_summary,
            projects=content.get("projects", []),
            certifications=content.get("certifications", []),
            created_at=updated.created_at,
            updated_at=updated.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{pipeline_id}/timeline", response_model=List[TimelineItemResponse])
def get_candidate_timeline(
    pipeline_id: UUID,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = PipelineService(db)
    return service.get_candidate_timeline(current_user.id, pipeline_id)
