from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import RoleChecker
from app.models.user import User
from app.models.pipeline import CandidatePipeline, CandidateNote, CandidateFeedback
from app.models.resume import Resume
from app.models.job import Job
from app.schemas.recruiter_workflow import CandidateCompareRequest, InterviewKitRequest, RecruiterChatRequest
from app.schemas.pipeline import CandidateNoteCreate, CandidateFeedbackCreate, CandidateNoteResponse, CandidateFeedbackResponse
from app.services.recruiter_ai_service import RecruiterAIService
from app.services.analytics_service import AnalyticsService
from app.services.pipeline_service import PipelineService

router = APIRouter(tags=["Recruiter Advanced Workflows"])
is_recruiter = RoleChecker(["RECRUITER", "ADMIN"])

@router.get("/candidates/search")
def search_candidates(
    job_id: Optional[UUID] = None,
    query: Optional[str] = None,
    skills: Optional[str] = None, # Comma separated
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
    location: Optional[str] = None,
    min_ats: Optional[int] = None,
    min_jd_match: Optional[int] = None,
    sort_by: Optional[str] = "best_match", # best_match, highest_ats, most_experience, recent
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    """
    Search talent database. Filters and sorts parsed profiles.
    """
    pipeline_query = db.query(CandidatePipeline)
    if job_id:
        pipeline_query = pipeline_query.filter(CandidatePipeline.job_id == job_id)
    else:
        # Get all recruiter jobs
        jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
        job_ids = [j.id for j in jobs]
        if not job_ids:
            return []
        pipeline_query = pipeline_query.filter(CandidatePipeline.job_id.in_(job_ids))

    entries = pipeline_query.all()
    results = []

    for entry in entries:
        resume = entry.resume
        if not resume:
            continue
        parsed = resume.parsed_content
        name = parsed.get("name", "Unknown Candidate")
        email = parsed.get("email", "N/A")
        phone = parsed.get("phone", "N/A")
        cand_skills = parsed.get("skills", [])
        
        # Apply filters
        # 1. General query (name, email, skills)
        if query:
            q = query.lower()
            in_name = q in name.lower()
            in_email = q in email.lower()
            in_skills = any(q in s.lower() for s in cand_skills)
            if not (in_name or in_email or in_skills):
                continue
                
        # 2. Skills filter
        if skills:
            filter_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]
            has_all_skills = all(any(fs in cs.lower() for cs in cand_skills) for fs in filter_skills)
            if not has_all_skills:
                continue

        # 3. Experience filter (rough heuristic based on number of experience entries)
        exp_entries = parsed.get("experience", [])
        exp_years = len(exp_entries) * 2 # heuristic: assume 2 years per job if not specified
        if min_experience is not None and exp_years < min_experience:
            continue
        if max_experience is not None and exp_years > max_experience:
            continue

        # 4. Location filter
        cand_location = "N/A"
        education_entries = parsed.get("education", [])
        if education_entries:
            cand_location = education_entries[0].get("school", "N/A") # using school as fallback location indicator
        if location and location.lower() not in cand_location.lower():
            continue

        # 5. Score filters
        ats = entry.ats_score or 0
        jd_match = entry.jd_match_score or 0
        if min_ats is not None and ats < min_ats:
            continue
        if min_jd_match is not None and jd_match < min_jd_match:
            continue

        results.append({
            "pipeline_id": entry.id,
            "job_id": entry.job_id,
            "job_title": entry.job.title if entry.job else "General Position",
            "resume_id": entry.resume_id,
            "candidate_name": name,
            "email": email,
            "phone": phone,
            "stage": entry.stage,
            "ats_score": ats,
            "jd_match_score": jd_match,
            "skills": cand_skills,
            "experience_years": exp_years,
            "created_at": entry.created_at
        })

    # Sorting
    if sort_by == "highest_ats":
        results.sort(key=lambda x: x["ats_score"], reverse=True)
    elif sort_by == "most_experience":
        results.sort(key=lambda x: x["experience_years"], reverse=True)
    elif sort_by == "recent":
        results.sort(key=lambda x: x["created_at"], reverse=True)
    else: # best_match
        results.sort(key=lambda x: x["jd_match_score"], reverse=True)

    return results

@router.post("/candidates/compare")
def compare_candidates(
    req: CandidateCompareRequest,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    ai_service = RecruiterAIService(db)
    return ai_service.generate_candidate_comparison(req.job_id, req.pipeline_ids)

@router.post("/interview-kit/generate")
def generate_interview_kit(
    req: InterviewKitRequest,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    ai_service = RecruiterAIService(db)
    return ai_service.generate_interview_kit(req.job_id, req.resume_id)

@router.post("/notes", response_model=CandidateNoteResponse, status_code=201)
def add_candidate_note(
    req: CandidateNoteCreate,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    pipeline_entry = db.query(CandidatePipeline).filter(CandidatePipeline.id == req.pipeline_id).first()
    if not pipeline_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline entry not found"
        )
        
    db_note = CandidateNote(
        pipeline_id=req.pipeline_id,
        recruiter_id=current_user.id,
        content=req.content
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    recruiter_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    return CandidateNoteResponse(
        id=db_note.id,
        pipeline_id=db_note.pipeline_id,
        recruiter_name=recruiter_name,
        content=db_note.content,
        created_at=db_note.created_at
    )

@router.get("/notes/{candidate_id}", response_model=List[CandidateNoteResponse])
def get_candidate_notes(
    candidate_id: UUID, # this represents pipeline_id in the frontend context
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    notes = db.query(CandidateNote).filter(CandidateNote.pipeline_id == candidate_id).order_by(CandidateNote.created_at.desc()).all()
    response = []
    for n in notes:
        recruiter_name = f"{n.recruiter.first_name or ''} {n.recruiter.last_name or ''}".strip() or n.recruiter.email if n.recruiter else "Recruiter"
        response.append(
            CandidateNoteResponse(
                id=n.id,
                pipeline_id=n.pipeline_id,
                recruiter_name=recruiter_name,
                content=n.content,
                created_at=n.created_at
            )
        )
    return response

@router.post("/feedback", response_model=CandidateFeedbackResponse, status_code=201)
def add_candidate_feedback(
    req: CandidateFeedbackCreate,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    pipeline_entry = db.query(CandidatePipeline).filter(CandidatePipeline.id == req.pipeline_id).first()
    if not pipeline_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline entry not found"
        )
        
    db_feedback = CandidateFeedback(
        pipeline_id=req.pipeline_id,
        interviewer_id=current_user.id,
        score=req.score,
        feedback_text=req.feedback_text
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)

    interviewer_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    return CandidateFeedbackResponse(
        id=db_feedback.id,
        pipeline_id=db_feedback.pipeline_id,
        interviewer_name=interviewer_name,
        score=db_feedback.score,
        feedback_text=db_feedback.feedback_text,
        created_at=db_feedback.created_at
    )

@router.get("/analytics/recruiter")
def get_recruiter_analytics(
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    service = AnalyticsService(db)
    return service.get_recruiter_analytics(current_user.id)

@router.post("/recruiter/chat")
def chatbot_recruiter(
    req: RecruiterChatRequest,
    current_user: User = Depends(is_recruiter),
    db: Session = Depends(get_db)
):
    ai_service = RecruiterAIService(db)
    
    # Structure messages for history
    chat_messages = []
    for h in req.history:
        chat_messages.append({
            "role": h.get("role", "user"),
            "content": h.get("content", "")
        })
    # Add new prompt message
    chat_messages.append({
        "role": "user",
        "content": req.message
    })

    bot_reply = ai_service.run_recruiter_copilot(
        recruiter_id=current_user.id,
        messages=chat_messages,
        selected_job_id=req.selected_job_id
    )
    return {"reply": bot_reply}
