from app.core.database import Base
from app.models.user import User
from app.models.resume import Resume
from app.models.jd import JobDescription
from app.models.ats_result import ATSResult
from app.models.jd_match import JDMatch
from app.models.recruiter_upload import RecruiterUpload
# Phase 2 models
from app.models.resume_version import ResumeVersion
from app.models.interview import InterviewSession, InterviewQuestion
from app.models.skill_gap import SkillGapAnalysis
from app.models.career_roadmap import CareerRoadmap
from app.models.job_application import JobApplication
from app.models.coach import CoachConversation, CoachMessage

__all__ = [
    "Base",
    "User",
    "Resume",
    "JobDescription",
    "ATSResult",
    "JDMatch",
    "RecruiterUpload",
    "ResumeVersion",
    "InterviewSession",
    "InterviewQuestion",
    "SkillGapAnalysis",
    "CareerRoadmap",
    "JobApplication",
    "CoachConversation",
    "CoachMessage",
]
