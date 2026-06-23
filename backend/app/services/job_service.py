from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.job import Job, JobSkill, TeamMember
from app.models.pipeline import CandidatePipeline
from app.models.activity_log import ActivityLog
from app.models.user import User

class JobService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self, recruiter_id: UUID) -> Dict[str, Any]:
        """Calculates dashboard summary metrics for a recruiter's active pipeline."""
        # 1. Total jobs and status counts
        all_jobs = self.db.query(Job).filter(Job.recruiter_id == recruiter_id).all()
        open_jobs = len([j for j in all_jobs if j.status == "Active"])
        closed_jobs = len([j for j in all_jobs if j.status == "Closed"])
        draft_jobs = len([j for j in all_jobs if j.status == "Draft"])
        archived_jobs = len([j for j in all_jobs if j.status == "Archived"])

        # 2. Total applications across recruiter's jobs
        job_ids = [j.id for j in all_jobs]
        total_apps = 0
        active_pipelines = 0
        if job_ids:
            total_apps = self.db.query(CandidatePipeline).filter(CandidatePipeline.job_id.in_(job_ids)).count()
            
            # Count jobs that have at least 1 applicant
            for j_id in job_ids:
                has_apps = self.db.query(CandidatePipeline).filter(CandidatePipeline.job_id == j_id).count() > 0
                job_active = any(j.id == j_id and j.status == "Active" for j in all_jobs)
                if job_active and has_apps:
                    active_pipelines += 1

        return {
            "open_jobs": open_jobs,
            "closed_jobs": closed_jobs,
            "draft_jobs": draft_jobs,
            "archived_jobs": archived_jobs,
            "total_applications": total_apps,
            "active_hiring_pipelines": active_pipelines
        }

    def get_jobs(self, recruiter_id: UUID, status: Optional[str] = None) -> List[Job]:
        """List jobs matching the optional status filter."""
        query = self.db.query(Job).filter(Job.recruiter_id == recruiter_id)
        if status:
            query = query.filter(Job.status == status)
        return query.order_by(Job.created_at.desc()).all()

    def get_job(self, recruiter_id: UUID, job_id: UUID) -> Optional[Job]:
        """Fetch a specific job by ID, ensuring ownership."""
        return self.db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter_id).first()

    def create_job(self, recruiter_id: UUID, data: Dict[str, Any]) -> Job:
        """Create a new job and insert required/preferred skills."""
        job = Job(
            recruiter_id=recruiter_id,
            title=data["title"],
            department=data.get("department"),
            employment_type=data.get("employment_type"),
            experience_required=data.get("experience_required"),
            location=data.get("location"),
            salary_range=data.get("salary_range"),
            description=data.get("description"),
            status=data.get("status", "Active")
        )
        self.db.add(job)
        self.db.flush() # Populate job.id

        # Insert skills
        skills_required = data.get("skills_required", [])
        skills_preferred = data.get("skills_preferred", [])
        
        for skill in skills_required:
            js = JobSkill(job_id=job.id, skill_name=skill.strip(), is_required=True)
            self.db.add(js)
            
        for skill in skills_preferred:
            js = JobSkill(job_id=job.id, skill_name=skill.strip(), is_required=False)
            self.db.add(js)

        # Log activity
        log = ActivityLog(
            user_id=recruiter_id,
            action_type="CREATE_JOB",
            details=f"Created job opening '{job.title}'"
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_job(self, recruiter_id: UUID, job_id: UUID, data: Dict[str, Any]) -> Optional[Job]:
        """Update job fields, and optional replacement of job skills."""
        job = self.get_job(recruiter_id, job_id)
        if not job:
            return None

        # Update columns
        fields = ["title", "department", "employment_type", "experience_required", "location", "salary_range", "description", "status"]
        for f in fields:
            if f in data:
                setattr(job, f, data[f])

        # If skills specified, clear old skills and add new
        if "skills_required" in data or "skills_preferred" in data:
            self.db.query(JobSkill).filter(JobSkill.job_id == job_id).delete()
            
            skills_required = data.get("skills_required", [])
            for skill in skills_required:
                js = JobSkill(job_id=job.id, skill_name=skill.strip(), is_required=True)
                self.db.add(js)
                
            skills_preferred = data.get("skills_preferred", [])
            for skill in skills_preferred:
                js = JobSkill(job_id=job.id, skill_name=skill.strip(), is_required=False)
                self.db.add(js)

        # Log activity
        log = ActivityLog(
            user_id=recruiter_id,
            action_type="UPDATE_JOB",
            details=f"Updated job opening '{job.title}'"
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, recruiter_id: UUID, job_id: UUID) -> bool:
        """Deletes a job and logs the action."""
        job = self.get_job(recruiter_id, job_id)
        if not job:
            return False

        job_title = job.title
        self.db.delete(job)
        
        # Log activity
        log = ActivityLog(
            user_id=recruiter_id,
            action_type="DELETE_JOB",
            details=f"Deleted job opening '{job_title}'"
        )
        self.db.add(log)
        self.db.commit()
        return True
