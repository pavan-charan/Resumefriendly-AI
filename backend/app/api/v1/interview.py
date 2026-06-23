from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.interview_service import InterviewService
from app.schemas.interview import StartSessionRequest, SubmitAnswerRequest

router = APIRouter(prefix="/interview", tags=["Interview Preparation"])


@router.post("/start")
def start_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new mock interview session."""
    try:
        service = InterviewService(db)
        result = service.start_session(
            user_id=str(current_user.id),
            target_role=request.target_role,
            difficulty=request.difficulty,
            question_count=request.question_count,
            resume_id=request.resume_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.post("/answer/{question_id}")
def submit_answer(
    question_id: str,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer for evaluation."""
    try:
        service = InterviewService(db)
        return service.submit_answer(question_id, request.answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answer: {str(e)}")


@router.get("/sessions")
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all interview sessions."""
    service = InterviewService(db)
    return service.get_sessions(str(current_user.id))


@router.get("/session/{session_id}")
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific session with all questions."""
    try:
        service = InterviewService(db)
        return service.get_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
