from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.coach_service import CoachService
from app.schemas.coach import StartConversationRequest, ChatRequest

router = APIRouter(prefix="/coach", tags=["AI Career Coach"])


@router.post("/conversations")
def start_conversation(
    request: StartConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new coaching conversation."""
    if request.resume_id:
        from app.models.resume import Resume
        resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        if resume.user_id != current_user.id and current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="You do not have permission to start a conversation for this resume")

    service = CoachService(db)
    return service.start_conversation(
        user_id=str(current_user.id),
        resume_id=request.resume_id,
        title=request.title,
    )


@router.post("/conversations/{conversation_id}/chat")
def chat(
    conversation_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the career coach."""
    try:
        from app.models.coach import CoachConversation
        convo = db.query(CoachConversation).filter(CoachConversation.id == conversation_id).first()
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if convo.user_id != current_user.id and current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="You do not have permission to chat in this conversation")

        service = CoachService(db)
        return service.chat(conversation_id, request.message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all coaching conversations."""
    service = CoachService(db)
    return service.get_conversations(str(current_user.id))


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific conversation with all messages."""
    try:
        from app.models.coach import CoachConversation
        convo = db.query(CoachConversation).filter(CoachConversation.id == conversation_id).first()
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if convo.user_id != current_user.id and current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="You do not have permission to access this conversation")

        service = CoachService(db)
        return service.get_conversation(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
