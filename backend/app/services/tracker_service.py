"""
Application Tracker Service
CRUD operations for job application tracking.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.job_application import JobApplication


class TrackerService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: str, data: dict) -> dict:
        """Create a new job application."""
        app = JobApplication(user_id=user_id, **data)
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return self._to_dict(app)
    
    def list_all(self, user_id: str) -> list[dict]:
        """List all applications for a user."""
        apps = (
            self.db.query(JobApplication)
            .filter(JobApplication.user_id == user_id)
            .order_by(JobApplication.updated_at.desc())
            .all()
        )
        return [self._to_dict(a) for a in apps]
    
    def update(self, app_id: str, user_id: str, data: dict) -> dict:
        """Update an application."""
        app = (
            self.db.query(JobApplication)
            .filter(JobApplication.id == app_id, JobApplication.user_id == user_id)
            .first()
        )
        if not app:
            raise ValueError("Application not found")
        
        for key, value in data.items():
            if value is not None and hasattr(app, key):
                setattr(app, key, value)
        
        self.db.commit()
        self.db.refresh(app)
        return self._to_dict(app)
    
    def delete(self, app_id: str, user_id: str) -> bool:
        """Delete an application."""
        app = (
            self.db.query(JobApplication)
            .filter(JobApplication.id == app_id, JobApplication.user_id == user_id)
            .first()
        )
        if not app:
            raise ValueError("Application not found")
        
        self.db.delete(app)
        self.db.commit()
        return True
    
    def get_stats(self, user_id: str) -> dict:
        """Get status distribution stats."""
        apps = (
            self.db.query(JobApplication)
            .filter(JobApplication.user_id == user_id)
            .all()
        )
        
        stats = {
            "total": len(apps),
            "applied": 0,
            "screening": 0,
            "interviewing": 0,
            "offer": 0,
            "rejected": 0,
            "accepted": 0,
            "withdrawn": 0,
        }
        
        for app in apps:
            status = app.status.lower()
            if status in stats:
                stats[status] += 1
        
        return stats
    
    def _to_dict(self, app: JobApplication) -> dict:
        return {
            "id": str(app.id),
            "company_name": app.company_name,
            "job_title": app.job_title,
            "job_url": app.job_url,
            "status": app.status,
            "applied_date": app.applied_date.isoformat() if app.applied_date else None,
            "salary_range": app.salary_range,
            "location": app.location,
            "notes": app.notes,
            "next_followup": app.next_followup.isoformat() if app.next_followup else None,
            "created_at": app.created_at.isoformat(),
            "updated_at": app.updated_at.isoformat(),
        }
