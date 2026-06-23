from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StartSessionRequest(BaseModel):
    resume_id: Optional[str] = None
    target_role: str
    difficulty: str = "medium"  # easy, medium, hard
    question_count: int = 5


class SubmitAnswerRequest(BaseModel):
    answer: str


class QuestionResponse(BaseModel):
    id: str
    question_text: str
    category: str
    user_answer: Optional[str] = None
    ai_feedback: Optional[dict] = None
    score: Optional[int] = None


class SessionResponse(BaseModel):
    id: str
    target_role: str
    difficulty: str
    total_score: Optional[int] = None
    questions: list[QuestionResponse]
    created_at: datetime


class SessionListItem(BaseModel):
    id: str
    target_role: str
    difficulty: str
    total_score: Optional[int] = None
    question_count: int
    created_at: datetime


class AnswerFeedbackResponse(BaseModel):
    question_id: str
    score: int
    feedback: dict
