from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class ATSResult(Base):
    __tablename__ = "ats_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False)
    overall_score = Column(Integer, nullable=False)
    skills_score = Column(Integer, nullable=False)
    keywords_score = Column(Integer, nullable=False)
    experience_score = Column(Integer, nullable=False)
    formatting_score = Column(Integer, nullable=False)
    education_score = Column(Integer, nullable=False)
    contact_score = Column(Integer, nullable=False)
    details = Column(JSONB, nullable=False) # {missing_keywords: [], missing_sections: [], recommendations: [], strengths: []}
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="ats_result")
