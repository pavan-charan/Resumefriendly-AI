from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class RecruiterUpload(Base):
    __tablename__ = "recruiter_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jd_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    recruiter = relationship("User", back_populates="recruiter_uploads")
    jd = relationship("JobDescription", back_populates="recruiter_uploads")
    resume = relationship("Resume", back_populates="recruiter_uploads")
