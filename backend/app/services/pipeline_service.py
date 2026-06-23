from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.pipeline import CandidatePipeline, CandidateStageHistory, CandidateNote, CandidateFeedback
from app.models.job import Job
from app.models.resume import Resume
from app.models.activity_log import ActivityLog

class PipelineService:
    VALID_STAGES = [
        "Applied", "Screening", "Shortlisted", "Interview Scheduled",
        "Technical Round", "Manager Round", "HR Round", "Offer", "Hired", "Rejected"
    ]

    def __init__(self, db: Session):
        self.db = db

    def get_pipeline(
        self, 
        recruiter_id: UUID, 
        job_id: UUID,
        stage: Optional[str] = None,
        min_score: Optional[int] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches all pipeline entries for a job, optionally filtered.
        Includes details from CandidateProfile / Resume records.
        """
        # Ensure recruiter owns the job
        job = self.db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter_id).first()
        if not job:
            return []

        query = self.db.query(CandidatePipeline).filter(CandidatePipeline.job_id == job_id)
        
        if stage:
            query = query.filter(CandidatePipeline.stage == stage)
        if min_score is not None:
            query = query.filter(CandidatePipeline.jd_match_score >= min_score)
            
        results = query.order_by(CandidatePipeline.jd_match_score.desc()).all()
        
        pipeline_list = []
        for entry in results:
            resume = entry.resume
            if not resume:
                continue
                
            content = resume.parsed_content
            candidate_name = content.get("name", "Unknown Candidate")
            email = content.get("email", "N/A")
            skills = content.get("skills", [])
            
            # Apply text search filter if provided
            if search_query:
                q = search_query.lower()
                matches_name = q in candidate_name.lower()
                matches_email = q in email.lower()
                matches_skills = any(q in s.lower() for s in skills)
                if not (matches_name or matches_email or matches_skills):
                    continue

            # Construct education summary
            education_list = content.get("education", [])
            edu_summary = "N/A"
            if education_list:
                primary = education_list[0]
                edu_summary = f"{primary.get('degree', 'Degree')} in {primary.get('major', 'Major')} from {primary.get('school', 'School')}"

            # Construct experience summary
            experience_list = content.get("experience", [])
            exp_summary = "N/A"
            if experience_list:
                primary = experience_list[0]
                exp_summary = f"{primary.get('role', 'Professional')} at {primary.get('company', 'Company')} ({primary.get('duration', 'Duration')})"

            pipeline_list.append({
                "id": entry.id,
                "job_id": entry.job_id,
                "resume_id": entry.resume_id,
                "stage": entry.stage,
                "ats_score": entry.ats_score,
                "jd_match_score": entry.jd_match_score,
                "candidate_name": candidate_name,
                "email": email,
                "phone": content.get("phone", "N/A"),
                "skills": skills,
                "education": edu_summary,
                "experience": exp_summary,
                "projects": content.get("projects", []),
                "certifications": content.get("certifications", []),
                "created_at": entry.created_at,
                "updated_at": entry.updated_at
            })
            
        return pipeline_list

    def move_candidate(
        self,
        recruiter_id: UUID,
        pipeline_id: UUID,
        to_stage: str,
        notes: Optional[str] = None
    ) -> Optional[CandidatePipeline]:
        """
        Updates stage of a candidate pipeline entry, saves movement history, and logs activity.
        """
        if to_stage not in self.VALID_STAGES:
            raise ValueError(f"Invalid pipeline stage: {to_stage}. Must be one of {self.VALID_STAGES}")

        entry = self.db.query(CandidatePipeline).filter(CandidatePipeline.id == pipeline_id).first()
        if not entry:
            return None

        # Ensure recruiter owns the job associated with this pipeline entry
        job = self.db.query(Job).filter(Job.id == entry.job_id, Job.recruiter_id == recruiter_id).first()
        if not job:
            return None

        from_stage = entry.stage
        if from_stage == to_stage:
            return entry # No change

        # Update stage
        entry.stage = to_stage
        entry.updated_at = datetime.utcnow()

        # Add movement history record
        history = CandidateStageHistory(
            pipeline_id=pipeline_id,
            from_stage=from_stage,
            to_stage=to_stage,
            moved_by=recruiter_id,
            notes=notes
        )
        self.db.add(history)

        # Log activity
        candidate_name = entry.resume.parsed_content.get("name", "Unknown Candidate")
        log = ActivityLog(
            user_id=recruiter_id,
            action_type="MOVE_CANDIDATE",
            details=f"Moved candidate '{candidate_name}' from '{from_stage}' to '{to_stage}' for job '{job.title}'"
        )
        self.db.add(log)
        
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_candidate_timeline(self, recruiter_id: UUID, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """
        Compiles a chronological timeline feed of a candidate's application history, 
        combining stage moves, team notes, and feedbacks.
        """
        entry = self.db.query(CandidatePipeline).filter(CandidatePipeline.id == pipeline_id).first()
        if not entry:
            return []

        # Ensure recruiter ownership
        job = self.db.query(Job).filter(Job.id == entry.job_id, Job.recruiter_id == recruiter_id).first()
        if not job:
            return []

        timeline = []

        # 1. Initial Application Date
        timeline.append({
            "type": "applied",
            "title": "Application Received",
            "timestamp": entry.created_at,
            "details": f"Candidate profile imported and initial screening score evaluated (JD Match: {entry.jd_match_score}%)"
        })

        # 2. Stage Movements
        history = self.db.query(CandidateStageHistory).filter(CandidateStageHistory.pipeline_id == pipeline_id).all()
        for item in history:
            mover_name = "Recruiter"
            if item.mover:
                mover_name = f"{item.mover.first_name or ''} {item.mover.last_name or ''}".strip() or item.mover.email
                
            timeline.append({
                "type": "stage_move",
                "title": f"Moved to {item.to_stage}",
                "timestamp": item.moved_at,
                "details": f"Transitioned from '{item.from_stage}' by {mover_name}. Notes: {item.notes or 'None'}"
            })

        # 3. Candidate Notes
        notes = self.db.query(CandidateNote).filter(CandidateNote.pipeline_id == pipeline_id).all()
        for note in notes:
            author_name = "Recruiter"
            if note.recruiter:
                author_name = f"{note.recruiter.first_name or ''} {note.recruiter.last_name or ''}".strip() or note.recruiter.email
                
            timeline.append({
                "type": "note",
                "title": f"Note by {author_name}",
                "timestamp": note.created_at,
                "details": note.content
            })

        # 4. Interview Feedbacks
        feedbacks = self.db.query(CandidateFeedback).filter(CandidateFeedback.pipeline_id == pipeline_id).all()
        for feedback in feedbacks:
            author_name = "Interviewer"
            if feedback.interviewer:
                author_name = f"{feedback.interviewer.first_name or ''} {feedback.interviewer.last_name or ''}".strip() or feedback.interviewer.email
                
            timeline.append({
                "type": "feedback",
                "title": f"Feedback Rating: {feedback.score}/5 by {author_name}",
                "timestamp": feedback.created_at,
                "details": feedback.feedback_text
            })

        # Sort timeline descending by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline
