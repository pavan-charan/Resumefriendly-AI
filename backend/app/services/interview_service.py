"""
Interview Preparation Engine Service
Generates role-specific interview questions and evaluates answers using LLM.
"""
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.llm_provider import get_llm_provider
from app.models.resume import Resume
from app.models.interview import InterviewSession, InterviewQuestion


class InterviewService:
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()
    
    def start_session(
        self,
        user_id: str,
        target_role: str,
        difficulty: str = "medium",
        question_count: int = 5,
        resume_id: str = None,
    ) -> dict:
        """Start a new interview session with generated questions."""
        
        # Get resume context if provided
        resume_context = ""
        if resume_id:
            resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                parsed = resume.parsed_content
                skills = parsed.get("skills", [])
                exp = parsed.get("experience", [])
                resume_context = f"""
Candidate Skills: {', '.join(skills[:15])}
Recent Experience: {json.dumps(exp[:3]) if exp else 'None'}"""
        
        # Generate questions via LLM
        questions_data = self._generate_questions(target_role, difficulty, question_count, resume_context)
        
        # Create session
        session = InterviewSession(
            user_id=user_id,
            resume_id=resume_id,
            target_role=target_role,
            difficulty=difficulty,
        )
        self.db.add(session)
        self.db.flush()
        
        # Create question records
        question_records = []
        for q in questions_data:
            question = InterviewQuestion(
                session_id=session.id,
                question_text=q.get("question", ""),
                category=q.get("category", "behavioral"),
            )
            self.db.add(question)
            question_records.append(question)
        
        self.db.commit()
        self.db.refresh(session)
        
        return {
            "id": str(session.id),
            "target_role": session.target_role,
            "difficulty": session.difficulty,
            "total_score": None,
            "questions": [
                {
                    "id": str(q.id),
                    "question_text": q.question_text,
                    "category": q.category,
                    "user_answer": None,
                    "ai_feedback": None,
                    "score": None,
                }
                for q in question_records
            ],
            "created_at": session.created_at.isoformat(),
        }
    
    def submit_answer(self, question_id: str, answer: str) -> dict:
        """Submit an answer and get AI feedback."""
        question = self.db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        session = question.session
        
        # Evaluate with LLM
        feedback = self._evaluate_answer(
            question.question_text,
            question.category,
            answer,
            session.target_role,
            session.difficulty,
        )
        
        # Update question
        question.user_answer = answer
        question.ai_feedback = feedback
        question.score = feedback.get("score", 5)
        question.answered_at = datetime.now(timezone.utc)
        
        # Update session total score
        answered = [q for q in session.questions if q.score is not None]
        if answered:
            session.total_score = sum(q.score for q in answered) * 10 // len(session.questions)
        
        self.db.commit()
        
        return {
            "question_id": str(question.id),
            "score": question.score,
            "feedback": feedback,
        }
    
    def get_sessions(self, user_id: str) -> list[dict]:
        """Get all interview sessions for a user."""
        sessions = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
            .all()
        )
        return [
            {
                "id": str(s.id),
                "target_role": s.target_role,
                "difficulty": s.difficulty,
                "total_score": s.total_score,
                "question_count": len(s.questions),
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
    
    def get_session(self, session_id: str) -> dict:
        """Get a specific session with all questions."""
        session = self.db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
        
        return {
            "id": str(session.id),
            "target_role": session.target_role,
            "difficulty": session.difficulty,
            "total_score": session.total_score,
            "questions": [
                {
                    "id": str(q.id),
                    "question_text": q.question_text,
                    "category": q.category,
                    "user_answer": q.user_answer,
                    "ai_feedback": q.ai_feedback,
                    "score": q.score,
                }
                for q in session.questions
            ],
            "created_at": session.created_at.isoformat(),
        }
    
    def _generate_questions(
        self, target_role: str, difficulty: str, count: int, resume_context: str
    ) -> list[dict]:
        """Generate interview questions using LLM."""
        prompt = f"""Generate {count} interview questions for a {target_role} position at {difficulty} difficulty level.
{resume_context}

Mix the categories: include behavioral, technical, and situational questions.

Return a JSON object with a "questions" key containing an array of objects, each with:
- "question": the interview question text
- "category": one of "behavioral", "technical", or "situational"

Example:
{{"questions": [{{"question": "Tell me about a time you led a team project.", "category": "behavioral"}}]}}"""

        result = self.llm.generate_json(
            prompt=prompt,
            system_prompt="You are an expert interviewer and hiring manager. Generate realistic, role-specific interview questions. Always respond with valid JSON.",
            temperature=0.8,
        )
        
        return result.get("questions", [{"question": "Tell me about yourself.", "category": "behavioral"}])
    
    def _evaluate_answer(
        self, question: str, category: str, answer: str, target_role: str, difficulty: str
    ) -> dict:
        """Evaluate an interview answer using LLM."""
        prompt = f"""Evaluate this interview answer for a {target_role} position ({difficulty} difficulty).

Question ({category}): {question}

Candidate's Answer: {answer}

Rate the answer and provide detailed feedback. Return a JSON object with:
- "score": integer 1-10
- "strengths": list of what the candidate did well
- "improvements": list of specific suggestions for improvement
- "sample_answer": a model answer for comparison

Be fair but rigorous in scoring:
- 1-3: Poor (missing key points, irrelevant)
- 4-5: Below average (partially answers, lacks depth)
- 6-7: Good (covers main points, could be stronger)
- 8-9: Excellent (comprehensive, well-structured)
- 10: Outstanding (exceptional, memorable)"""

        result = self.llm.generate_json(
            prompt=prompt,
            system_prompt="You are an expert interviewer evaluating candidate responses. Be constructive but honest. Always respond with valid JSON.",
            temperature=0.6,
        )
        
        # Ensure required fields
        if "score" not in result:
            result["score"] = 5
        if "strengths" not in result:
            result["strengths"] = []
        if "improvements" not in result:
            result["improvements"] = []
        
        return result
