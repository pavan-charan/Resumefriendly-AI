from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # Null for recruiter direct uploads
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_content = Column(JSONB, nullable=False) # {skills: [], experience: [], education: []...}
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="resumes")
    ats_result = relationship("ATSResult", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    jd_matches = relationship("JDMatch", back_populates="resume", cascade="all, delete-orphan")
    recruiter_uploads = relationship("RecruiterUpload", back_populates="resume", cascade="all, delete-orphan")
