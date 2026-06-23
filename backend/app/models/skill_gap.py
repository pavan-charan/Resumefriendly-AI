from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    target_role = Column(String(200), nullable=False)
    analysis_result = Column(JSONB, nullable=False)
    # analysis_result structure:
    # {
    #   current_skills: [{name, proficiency: 1-10}],
    #   missing_skills: [{name, importance: "critical"|"important"|"nice-to-have", resources: []}],
    #   overall_readiness: 0-100,
    #   recommendations: []
    # }
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="skill_gap_analyses")
    resume = relationship("Resume", back_populates="skill_gap_analyses")
