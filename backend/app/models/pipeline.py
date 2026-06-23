from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class CandidatePipeline(Base):
    __tablename__ = "candidate_pipeline"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(100), default="Applied", nullable=False) # Applied, Screening, Shortlisted, Interview Scheduled, Technical Round, Manager Round, HR Round, Offer, Hired, Rejected
    ats_score = Column(Integer, nullable=True)
    jd_match_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="pipeline_entries")
    resume = relationship("Resume")
    stage_history = relationship("CandidateStageHistory", back_populates="pipeline_entry", cascade="all, delete-orphan")
    notes = relationship("CandidateNote", back_populates="pipeline_entry", cascade="all, delete-orphan")
    feedbacks = relationship("CandidateFeedback", back_populates="pipeline_entry", cascade="all, delete-orphan")


class CandidateStageHistory(Base):
    __tablename__ = "candidate_stage_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("candidate_pipeline.id", ondelete="CASCADE"), nullable=False)
    from_stage = Column(String(100), nullable=False)
    to_stage = Column(String(100), nullable=False)
    moved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    moved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    pipeline_entry = relationship("CandidatePipeline", back_populates="stage_history")
    mover = relationship("User")


class CandidateNote(Base):
    __tablename__ = "candidate_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("candidate_pipeline.id", ondelete="CASCADE"), nullable=False)
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    pipeline_entry = relationship("CandidatePipeline", back_populates="notes")
    recruiter = relationship("User")


class CandidateFeedback(Base):
    __tablename__ = "candidate_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("candidate_pipeline.id", ondelete="CASCADE"), nullable=False)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False) # 1-5 rating
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    pipeline_entry = relationship("CandidatePipeline", back_populates="feedbacks")
    interviewer = relationship("User")
