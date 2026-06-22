from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    raw_content = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="jds")
    jd_matches = relationship("JDMatch", back_populates="jd", cascade="all, delete-orphan")
    recruiter_uploads = relationship("RecruiterUpload", back_populates="jd", cascade="all, delete-orphan")
