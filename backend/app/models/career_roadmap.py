from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    current_role = Column(String(200), nullable=False)
    target_role = Column(String(200), nullable=False)
    timeline_months = Column(Integer, default=12, nullable=False)
    roadmap_data = Column(JSONB, nullable=False)
    # roadmap_data structure:
    # {
    #   phases: [{phase_name, duration_months, milestones: [], skills_to_learn: [], resources: []}],
    #   certifications: [{name, provider, estimated_time}],
    #   target_companies: [],
    #   salary_progression: {current_estimate, target_estimate}
    # }
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="career_roadmaps")
    resume = relationship("Resume", back_populates="career_roadmaps")
