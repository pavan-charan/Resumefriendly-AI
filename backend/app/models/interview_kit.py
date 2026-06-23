from sqlalchemy import Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class InterviewKit(Base):
    __tablename__ = "interview_kits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    technical_questions = Column(JSONB, nullable=True)
    behavioral_questions = Column(JSONB, nullable=True)
    scenario_questions = Column(JSONB, nullable=True)
    role_specific_questions = Column(JSONB, nullable=True)
    evaluation_rubric = Column(Text, nullable=True)
    scoring_template = Column(Text, nullable=True)
    interviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="interview_kits")
    resume = relationship("Resume")
