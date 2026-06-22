from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.repositories.resume import ResumeRepository
from app.schemas.ats import ATSReportResponse
from app.services.ats_scorer import ATSScorer

router = APIRouter(prefix="/ats", tags=["ATS Score Engine"])

@router.post("/score/{resume_id}", response_model=ATSReportResponse)
def generate_ats_score(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_repo = ResumeRepository(db)
    db_resume = resume_repo.get_by_id(resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
        
    # Check ownership
    if db_resume.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to analyze this resume"
        )

    # Calculate score
    scorer = ATSScorer()
    # Scorer takes raw text + parsed structure
    analysis_input = {
        "skills": db_resume.parsed_content.get("skills", []),
        "experience": db_resume.parsed_content.get("experience", []),
        "education": db_resume.parsed_content.get("education", []),
        "projects": db_resume.parsed_content.get("projects", []),
        "certifications": db_resume.parsed_content.get("certifications", []),
        "name": db_resume.parsed_content.get("name"),
        "email": db_resume.parsed_content.get("email"),
        "phone": db_resume.parsed_content.get("phone"),
        "raw_text": db_resume.raw_text
    }
    
    report = scorer.calculate_score(analysis_input)
    
    # Save to database
    resume_repo.create_ats_result(
        resume_id=resume_id,
        scores={
            "overall": report["overall_score"],
            "skills": report["breakdown"]["skills"],
            "keywords": report["breakdown"]["keywords"],
            "experience": report["breakdown"]["experience"],
            "formatting": report["breakdown"]["formatting"],
            "education": report["breakdown"]["education"],
            "contact": report["breakdown"]["contact_info"]
        },
        details=report["explainability"]
    )
    
    return report

@router.get("/report/{resume_id}", response_model=ATSReportResponse)
def get_ats_report(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_repo = ResumeRepository(db)
    db_resume = resume_repo.get_by_id(resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
        
    # Check ownership
    if db_resume.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this analysis"
        )
        
    db_report = resume_repo.get_ats_result_by_resume_id(resume_id)
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ATS Report not generated yet. Please trigger /score first."
        )
        
    return {
        "overall_score": db_report.overall_score,
        "breakdown": {
            "skills": db_report.skills_score,
            "keywords": db_report.keywords_score,
            "experience": db_report.experience_score,
            "formatting": db_report.formatting_score,
            "education": db_report.education_score,
            "contact_info": db_report.contact_score
        },
        "explainability": db_report.details
    }
