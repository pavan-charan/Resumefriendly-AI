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
        if request.resume_id:
            from app.models.resume import Resume
            resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")
            if resume.user_id != current_user.id and current_user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="You do not have permission to start an interview for this resume")

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
        from app.models.interview import InterviewQuestion
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        if question.session.user_id != current_user.id and current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="You do not have permission to answer this question")

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
        from app.models.interview import InterviewSession
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != current_user.id and current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="You do not have permission to access this session")

        service = InterviewService(db)
        return service.get_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
