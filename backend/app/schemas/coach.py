from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StartConversationRequest(BaseModel):
    resume_id: Optional[str] = None
    title: Optional[str] = "New Conversation"


class ChatRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    title: str
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime


class ConversationListItem(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
