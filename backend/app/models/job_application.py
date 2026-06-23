from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    job_url = Column(String(500), nullable=True)
    status = Column(String(30), default="applied", nullable=False)
    # Status values: applied, screening, interviewing, offer, rejected, accepted, withdrawn
    applied_date = Column(Date, nullable=True)
    salary_range = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    next_followup = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="job_applications")
