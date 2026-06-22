from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.jd import JobDescription
from app.models.jd_match import JDMatch
from app.models.recruiter_upload import RecruiterUpload

class JobDescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, jd_id: UUID) -> Optional[JobDescription]:
        return self.db.query(JobDescription).filter(JobDescription.id == jd_id).first()

    def get_all_by_creator_id(self, creator_id: UUID) -> List[JobDescription]:
        return self.db.query(JobDescription).filter(JobDescription.creator_id == creator_id).order_by(JobDescription.created_at.desc()).all()

    def create(self, creator_id: UUID, title: str, company_name: str, department: Optional[str], raw_content: str, requirements: Optional[str]) -> JobDescription:
        db_jd = JobDescription(
            creator_id=creator_id,
            title=title,
            company_name=company_name,
            department=department,
            raw_content=raw_content,
            requirements=requirements
        )
        self.db.add(db_jd)
        self.db.commit()
        self.db.refresh(db_jd)
        return db_jd

    def create_jd_match(self, resume_id: UUID, jd_id: UUID, match_score: int, match_details: dict) -> JDMatch:
        existing = self.db.query(JDMatch).filter(
            JDMatch.resume_id == resume_id,
            JDMatch.jd_id == jd_id
        ).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        db_match = JDMatch(
            resume_id=resume_id,
            jd_id=jd_id,
            match_score=match_score,
            match_details=match_details
        )
        self.db.add(db_match)
        self.db.commit()
        self.db.refresh(db_match)
        return db_match

    def get_jd_match(self, resume_id: UUID, jd_id: UUID) -> Optional[JDMatch]:
        return self.db.query(JDMatch).filter(
            JDMatch.resume_id == resume_id,
            JDMatch.jd_id == jd_id
        ).first()

    def create_recruiter_upload(self, recruiter_id: UUID, jd_id: UUID, resume_id: UUID) -> RecruiterUpload:
        db_upload = RecruiterUpload(
            recruiter_id=recruiter_id,
            jd_id=jd_id,
            resume_id=resume_id
        )
        self.db.add(db_upload)
        self.db.commit()
        self.db.refresh(db_upload)
        return db_upload

    def get_recruiter_uploads_by_jd(self, jd_id: UUID) -> List[RecruiterUpload]:
        return self.db.query(RecruiterUpload).filter(RecruiterUpload.jd_id == jd_id).all()
