from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class JDMatch(Base):
    __tablename__ = "jd_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    jd_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Integer, nullable=False)
    match_details = Column(JSONB, nullable=False) # {matched_skills: [], missing_skills: [], recommendations: []}
    matched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="jd_matches")
    jd = relationship("JobDescription", back_populates="jd_matches")
