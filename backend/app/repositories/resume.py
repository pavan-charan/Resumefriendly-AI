from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.resume import Resume
from app.models.ats_result import ATSResult

class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, resume_id: UUID) -> Optional[Resume]:
        return self.db.query(Resume).filter(Resume.id == resume_id).first()

    def get_by_user_id(self, user_id: UUID) -> List[Resume]:
        return self.db.query(Resume).filter(Resume.user_id == user_id).order_with(Resume.uploaded_at.desc()).all()

    def get_all_by_user_id(self, user_id: UUID) -> List[Resume]:
        return self.db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc()).all()

    def create(self, user_id: Optional[UUID], file_name: str, file_path: str, raw_text: str, parsed_content: dict) -> Resume:
        db_resume = Resume(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            raw_text=raw_text,
            parsed_content=parsed_content
        )
        self.db.add(db_resume)
        self.db.commit()
        self.db.refresh(db_resume)
        return db_resume

    def create_ats_result(self, resume_id: UUID, scores: dict, details: dict) -> ATSResult:
        # Delete existing if any (since unique relationship)
        existing = self.db.query(ATSResult).filter(ATSResult.resume_id == resume_id).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        db_ats = ATSResult(
            resume_id=resume_id,
            overall_score=scores["overall"],
            skills_score=scores["skills"],
            keywords_score=scores["keywords"],
            experience_score=scores["experience"],
            formatting_score=scores["formatting"],
            education_score=scores["education"],
            contact_score=scores["contact"],
            details=details
        )
        self.db.add(db_ats)
        self.db.commit()
        self.db.refresh(db_ats)
        return db_ats

    def get_ats_result_by_resume_id(self, resume_id: UUID) -> Optional[ATSResult]:
        return self.db.query(ATSResult).filter(ATSResult.resume_id == resume_id).first()
