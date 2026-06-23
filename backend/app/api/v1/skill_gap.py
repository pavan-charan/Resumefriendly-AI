from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
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
        service = SkillGapService(db)
        return service.analyze(
            user_id=str(current_user.id),
            target_role=request.target_role,
            resume_id=request.resume_id,
        )
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
