from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.services.skill_gap_service import SkillGapService
from app.schemas.skill_gap import SkillGapRequest

router = APIRouter(prefix="/skills", tags=["Skill Gap Analysis"])


@router.post("/analyze")
def analyze_skill_gap(
    request: SkillGapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run a skill gap analysis for a target role."""
    try:
        if request.resume_id:
            resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")
            if resume.user_id != current_user.id and current_user.role != "ADMIN":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to analyze this resume")

        service = SkillGapService(db)
        return service.analyze(
            user_id=str(current_user.id),
            target_role=request.target_role,
            resume_id=request.resume_id,
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get past skill gap analyses."""
    service = SkillGapService(db)
    return service.get_history(str(current_user.id))
