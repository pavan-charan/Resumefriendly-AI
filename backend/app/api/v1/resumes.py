from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.storage import storage_manager
from app.models.user import User
from app.repositories.resume import ResumeRepository
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.services.parser_service import ParserService

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", response_model=ResumeUploadResponse, status_code=201)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify file extension
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF or DOCX file."
        )

    # Save file locally
    file_path = storage_manager.save_file(file)
    
    try:
        # Parse content
        parser = ParserService()
        parsed = parser.parse_file(file_path)
        
        # Save to database
        resume_repo = ResumeRepository(db)
        db_resume = resume_repo.create(
            user_id=current_user.id,
            file_name=file.filename,
            file_path=file_path,
            raw_text=parsed["raw_text"],
            parsed_content=parsed["parsed_content"]
        )
        
        return ResumeUploadResponse(
            resume_id=db_resume.id,
            file_name=db_resume.file_name,
            parsed_content=db_resume.parsed_content
        )
    except Exception as e:
        # Cleanup file if saved
        storage_manager.delete_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and parse resume: {str(e)}"
        )

@router.get("/history", response_model=List[ResumeResponse])
def get_resume_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_repo = ResumeRepository(db)
    # returns list of resumes
    return resume_repo.get_all_by_user_id(current_user.id)

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
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
            detail="You do not have permission to access this resume"
        )
    return db_resume
