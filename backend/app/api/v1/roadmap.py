from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.roadmap_service import RoadmapService
from app.schemas.roadmap import RoadmapRequest

router = APIRouter(prefix="/roadmap", tags=["Career Roadmap"])


@router.post("/generate")
def generate_roadmap(
    request: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a career roadmap."""
    try:
        if request.resume_id:
            from app.models.resume import Resume
            resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")
            if resume.user_id != current_user.id and current_user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="You do not have permission to generate a roadmap for this resume")

        service = RoadmapService(db)
        return service.generate(
            user_id=str(current_user.id),
            current_role=request.current_role,
            target_role=request.target_role,
            timeline_months=request.timeline_months,
            resume_id=request.resume_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get past roadmaps."""
    service = RoadmapService(db)
    return service.get_history(str(current_user.id))
