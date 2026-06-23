from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.rewriter_service import RewriterService
from app.schemas.rewriter import RewriteRequest

router = APIRouter(prefix="/rewriter", tags=["AI Resume Rewriter"])


@router.post("/rewrite")
def rewrite_resume(
    request: RewriteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-rewritten version of a resume."""
    try:
        service = RewriterService(db)
        result = service.rewrite_resume(
            resume_id=request.resume_id,
            user_id=str(current_user.id),
            target_role=request.target_role,
            tone=request.tone,
            focus_areas=request.focus_areas,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {str(e)}")


@router.get("/versions/{resume_id}")
def get_versions(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all rewritten versions for a resume."""
    service = RewriterService(db)
    return service.get_versions(resume_id)


@router.get("/version/{version_id}")
def get_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific rewritten version."""
    try:
        service = RewriterService(db)
        return service.get_version(version_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
