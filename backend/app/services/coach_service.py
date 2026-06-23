"""
AI Career Coach Service
Conversational AI assistant for career guidance with context from user's resume.
"""
import json
from sqlalchemy.orm import Session
from app.core.llm_provider import get_llm_provider
from app.models.resume import Resume
from app.models.coach import CoachConversation, CoachMessage


COACH_SYSTEM_PROMPT = """You are an expert AI Career Coach with deep knowledge of:
- Resume optimization and career branding
- Job search strategies and networking
- Interview preparation and negotiation
- Career transitions and skill development
- Industry trends and salary benchmarks
- Professional development and leadership

You provide personalized, actionable advice based on the user's resume and career goals.
Be encouraging but honest. Give specific, practical steps the user can take.
Keep responses concise but thorough (2-4 paragraphs max unless asked for detail).
If the user's resume context is provided, reference their specific skills and experience."""


class CoachService:
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()
    
    def start_conversation(self, user_id: str, resume_id: str = None, title: str = "New Conversation") -> dict:
        """Start a new coaching conversation."""
        conversation = CoachConversation(
            user_id=user_id,
            resume_id=resume_id,
            title=title,
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "messages": [],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
    
    def chat(self, conversation_id: str, user_message: str) -> dict:
        """Send a message and get AI response."""
        conversation = self.db.query(CoachConversation).filter(CoachConversation.id == conversation_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Save user message
        user_msg = CoachMessage(
            conversation_id=conversation.id,
            role="user",
            content=user_message,
        )
        self.db.add(user_msg)
        self.db.flush()
        
        # Build context
        resume_context = ""
        if conversation.resume_id:
            resume = self.db.query(Resume).filter(Resume.id == conversation.resume_id).first()
            if resume:
                parsed = resume.parsed_content
                resume_context = f"""
The user's resume contains:
- Name: {parsed.get('name', 'N/A')}
- Skills: {', '.join(parsed.get('skills', [])[:20])}
- Experience: {json.dumps(parsed.get('experience', [])[:3])}
- Education: {json.dumps(parsed.get('education', []))}"""
        
        system_prompt = COACH_SYSTEM_PROMPT
        if resume_context:
            system_prompt += f"\n\nUSER'S RESUME CONTEXT:{resume_context}"
        
        # Build conversation history for context
        messages = []
        for msg in conversation.messages:
            if str(msg.id) != str(user_msg.id):  # Exclude the one we just added
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        ai_response = self.llm.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1500,
        )
        
        # Save AI response
        ai_msg = CoachMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
        )
        self.db.add(ai_msg)
        
        # Update conversation title if it's the first message
        if len(conversation.messages) <= 1:
            # Generate a short title from the first message
            short_title = user_message[:50] + ("..." if len(user_message) > 50 else "")
            conversation.title = short_title
        
        self.db.commit()
        
        return {
            "id": str(ai_msg.id),
            "role": "assistant",
            "content": ai_response,
            "created_at": ai_msg.created_at.isoformat(),
        }
    
    def get_conversations(self, user_id: str) -> list[dict]:
        """List all conversations for a user."""
        conversations = (
            self.db.query(CoachConversation)
            .filter(CoachConversation.user_id == user_id)
            .order_by(CoachConversation.updated_at.desc())
            .all()
        )
        return [
            {
                "id": str(c.id),
                "title": c.title,
                "message_count": len(c.messages),
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in conversations
        ]
    
    def get_conversation(self, conversation_id: str) -> dict:
        """Get a specific conversation with all messages."""
        conversation = self.db.query(CoachConversation).filter(CoachConversation.id == conversation_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                }
                for m in conversation.messages
            ],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
