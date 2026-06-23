from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    employment_type = Column(String(100), nullable=True) # Full-time, Part-time, Contract, Internship
    experience_required = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    salary_range = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="Active", nullable=False) # Draft, Active, Closed, Archived
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    pipeline_entries = relationship("CandidatePipeline", back_populates="job", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="job", cascade="all, delete-orphan")
    comparisons = relationship("CandidateComparison", back_populates="job", cascade="all, delete-orphan")
    interview_kits = relationship("InterviewKit", back_populates="job", cascade="all, delete-orphan")


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="skills")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(100), nullable=False) # e.g. Recruiter, Hiring Manager
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="team_members")
    user = relationship("User")
