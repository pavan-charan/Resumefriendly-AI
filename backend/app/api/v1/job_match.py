from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.job_match_service import JobMatchService
from app.schemas.job_match_dashboard import JobMatchRequest

router = APIRouter(prefix="/jobs", tags=["Job Match Dashboard"])


@router.post("/match")
def find_job_matches(
    request: JobMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Find job matches for a resume."""
    try:
        service = JobMatchService(db)
        return service.find_matches(
            resume_id=request.resume_id,
            preferred_roles=request.preferred_roles,
            preferred_locations=request.preferred_locations,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job matching failed: {str(e)}")
