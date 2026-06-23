from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.tracker_service import TrackerService
from app.schemas.tracker import ApplicationCreate, ApplicationUpdate

router = APIRouter(prefix="/tracker", tags=["Application Tracker"])


@router.post("/applications")
def create_application(
    request: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job application."""
    service = TrackerService(db)
    data = request.model_dump(exclude_none=True)
    return service.create(str(current_user.id), data)


@router.get("/applications")
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all job applications."""
    service = TrackerService(db)
    return service.list_all(str(current_user.id))


@router.put("/applications/{app_id}")
def update_application(
    app_id: str,
    request: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a job application."""
    try:
        service = TrackerService(db)
        data = request.model_dump(exclude_none=True)
        return service.update(app_id, str(current_user.id), data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/applications/{app_id}")
def delete_application(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job application."""
    try:
        service = TrackerService(db)
        service.delete(app_id, str(current_user.id))
        return {"message": "Application deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get application status distribution stats."""
    service = TrackerService(db)
    return service.get_stats(str(current_user.id))
