from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    original_content = Column(JSONB, nullable=False)
    rewritten_content = Column(JSONB, nullable=False)
    target_role = Column(String(200), nullable=True)
    tone = Column(String(50), default="professional", nullable=False)  # professional, creative, executive, technical
    focus_areas = Column(JSONB, nullable=True)  # ["summary", "experience", "skills"]
    improvements = Column(JSONB, nullable=True)  # list of change descriptions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="versions")
    user = relationship("User", back_populates="resume_versions")
