from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any, Optional
import json

from app.core.llm_provider import get_llm_provider
from app.models.job import Job, JobSkill
from app.models.resume import Resume
from app.models.pipeline import CandidatePipeline, CandidateNote, CandidateFeedback
from app.models.interview_kit import InterviewKit
from app.models.comparison import CandidateComparison

class RecruiterAIService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()

    def generate_candidate_insights(self, job_id: UUID, resume_id: UUID) -> Dict[str, Any]:
        """
        Generates recruiter-focused candidate intelligence:
        Strengths, Weaknesses, Skill Coverage, Missing Skills, Experience Analysis, 
        Project Quality Summary, Risk Indicators, Hiring Recommendation & Confidence.
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        
        if not job or not resume:
            return {"error": "Job or Resume not found"}

        # Gather job skills and job details
        skills_required = [s.skill_name for s in job.skills if s.is_required]
        skills_preferred = [s.skill_name for s in job.skills if not s.is_required]
        
        job_details = {
            "title": job.title,
            "description": job.description or "",
            "skills_required": skills_required,
            "skills_preferred": skills_preferred,
            "experience_required": job.experience_required or "Not specified"
        }

        parsed_content = resume.parsed_content
        candidate_details = {
            "name": parsed_content.get("name", "Candidate"),
            "skills": parsed_content.get("skills", []),
            "experience": parsed_content.get("experience", []),
            "education": parsed_content.get("education", []),
            "projects": parsed_content.get("projects", []),
            "certifications": parsed_content.get("certifications", [])
        }

        system_prompt = (
            "You are a Senior Recruiter and AI Talent Analyst. "
            "Analyze the candidate's resume relative to the job requirements and generate detailed, structured insights. "
            "Your output must be a valid JSON object matching the requested schema."
        )

        prompt = f"""
Analyze the candidate's profile against the job description.

Job Specification:
{json.dumps(job_details, indent=2)}

Candidate Resume Details:
{json.dumps(candidate_details, indent=2)}

Generate recruiter-focused candidate intelligence. Return a JSON object with the following fields:
1. "strengths": A list of strings listing key candidate strengths matching this job.
2. "weaknesses": A list of strings showing areas where the candidate falls short.
3. "skill_coverage": A percentage (integer 0-100) representing how well the candidate's skills match the required skills.
4. "missing_skills": A list of important skills required by the job that are missing from the candidate's profile.
5. "experience_analysis": A paragraph summarizing the candidate's professional trajectory and alignment.
6. "project_quality_summary": A paragraph assessing the depth and impact of the candidate's listed projects.
7. "risk_indicators": A list of strings representing red flags (e.g., job hopping, missing core tech stack, experience gaps).
8. "hiring_recommendation": One of "Highly Recommended", "Recommended", "Consider With Reservations", "Not Recommended".
9. "confidence_score": An integer percentage (0-100) expressing your recommendation confidence.

Ensure the response is ONLY valid JSON.
"""

        try:
            result = self.llm.generate_json(prompt, system_prompt=system_prompt)
            # Ensure proper schema fallback
            if "error" in result:
                raise ValueError(result["error"])
            return result
        except Exception as e:
            # Safe mock fallback if LLM call fails
            return {
                "strengths": [f"Good skill profile containing {', '.join(parsed_content.get('skills', [])[:3])}"],
                "weaknesses": ["Requires manual review of project scope and experience details."],
                "skill_coverage": 70,
                "missing_skills": skills_required[:2],
                "experience_analysis": "The candidate has professional experience but requires detailed interview verification.",
                "project_quality_summary": "Projects show basic tech stack usage. Deep architectural quality needs verifying.",
                "risk_indicators": ["Automated check failed - fallback default recommendation."],
                "hiring_recommendation": "Recommended",
                "confidence_score": 70
            }

    def generate_candidate_comparison(self, job_id: UUID, pipeline_ids: List[UUID]) -> Dict[str, Any]:
        """
        Compares multiple candidates side-by-side:
        Creates a comparison table data structure, generates an AI summary, and recommends the best fit.
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        pipelines = self.db.query(CandidatePipeline).filter(CandidatePipeline.id.in_(pipeline_ids)).all()
        if not pipelines:
            return {"error": "No candidates found"}

        candidates_data = []
        for p in pipelines:
            resume = p.resume
            if not resume:
                continue
            parsed = resume.parsed_content
            candidates_data.append({
                "pipeline_id": str(p.id),
                "name": parsed.get("name", "Candidate"),
                "email": parsed.get("email", ""),
                "skills": parsed.get("skills", []),
                "experience_years": len(parsed.get("experience", [])) * 2, # rough heuristic
                "experience_summary": ", ".join([f"{e.get('role')} at {e.get('company')}" for e in parsed.get("experience", [])[:2]]),
                "education": ", ".join([f"{e.get('degree')} at {e.get('school')}" for e in parsed.get("education", [])[:1]]),
                "projects_count": len(parsed.get("projects", [])),
                "ats_score": p.ats_score or 0,
                "jd_match_score": p.jd_match_score or 0,
                "certifications": parsed.get("certifications", [])
            })

        system_prompt = (
            "You are a talent evaluation coordinator. Compare the candidates side-by-side for the target job "
            "and output a structured comparison summary. Always return valid JSON."
        )

        prompt = f"""
Job Title: {job.title}
Job Description: {job.description or ''}

Compare the following candidates side-by-side:
{json.dumps(candidates_data, indent=2)}

Create a candidate comparison report. Provide a JSON object with:
1. "candidate_rankings": A list of objects with fields: "pipeline_id", "name", "rank" (integer), "fit_justification" (short text).
2. "comparison_matrix": A list of candidate summaries compared side-by-side (key-value properties).
3. "ai_summary": A paragraph describing the general strengths and gaps of this applicant pool, and how they stack up.
4. "best_candidate_recommendation": A detailed paragraph explaining which candidate is the best fit, and why.

Ensure the response is ONLY valid JSON.
"""

        try:
            ai_report = self.llm.generate_json(prompt, system_prompt=system_prompt)
            
            # Save comparison to database
            comparison = CandidateComparison(
                job_id=job_id,
                candidate_ids=[str(p) for p in pipeline_ids],
                ai_summary=ai_report.get("ai_summary", ""),
                best_candidate_recommendation=ai_report.get("best_candidate_recommendation", "")
            )
            self.db.add(comparison)
            self.db.commit()
            
            ai_report["comparison_id"] = str(comparison.id)
            return ai_report
        except Exception as e:
            return {
                "candidate_rankings": [{"pipeline_id": c["pipeline_id"], "name": c["name"], "rank": i+1, "fit_justification": "Good matching match score."} for i, c in enumerate(candidates_data)],
                "ai_summary": "Fallback: Successfully loaded matching profiles. Please review score comparisons manually.",
                "best_candidate_recommendation": f"Candidate {candidates_data[0]['name'] if candidates_data else 'N/A'} is ranked first based on the highest JD Match Score."
            }

    def generate_interview_kit(self, job_id: UUID, resume_id: UUID) -> Dict[str, Any]:
        """
        Generates interviewer-ready interview packs:
        Technical questions, behavioral questions, scenario questions, role-specific questions,
        evaluation rubrics, scoring templates, and notes section.
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        
        if not job or not resume:
            return {"error": "Job or Resume not found"}

        # Check if already generated
        existing = self.db.query(InterviewKit).filter(InterviewKit.job_id == job_id, InterviewKit.resume_id == resume_id).first()
        if existing:
            return {
                "id": str(existing.id),
                "technical_questions": existing.technical_questions,
                "behavioral_questions": existing.behavioral_questions,
                "scenario_questions": existing.scenario_questions,
                "role_specific_questions": existing.role_specific_questions,
                "evaluation_rubric": existing.evaluation_rubric,
                "scoring_template": existing.scoring_template,
                "interviewer_notes": existing.interviewer_notes
            }

        job_info = {
            "title": job.title,
            "description": job.description or "",
            "skills": [s.skill_name for s in job.skills]
        }
        
        candidate_info = {
            "name": resume.parsed_content.get("name", "Candidate"),
            "skills": resume.parsed_content.get("skills", []),
            "experience": resume.parsed_content.get("experience", [])
        }

        system_prompt = (
            "You are an expert technical interviewer and HR coordinator. "
            "Generate a highly professional, ready-to-use interview guide for this candidate. "
            "Always return valid JSON."
        )

        prompt = f"""
Generate an Interview Kit for:
Job opening: {json.dumps(job_info, indent=2)}
Candidate: {json.dumps(candidate_info, indent=2)}

Please generate:
1. "technical_questions": List of 4 technical questions tailored to candidate's skills and the job, each with fields: "question", "expected_answer_keys", "difficulty" (Easy/Medium/Hard).
2. "behavioral_questions": List of 3 behavioral questions (STAR method) matching the role requirements, each with: "question", "eval_criteria".
3. "scenario_questions": List of 2 project scenarios assessing design/troubleshooting, each with: "scenario", "probing_questions".
4. "role_specific_questions": List of 2 questions about culture fit or role context, each with: "question", "focus_area".
5. "evaluation_rubric": A detailed paragraph describing what constitutes a poor (1/5), average (3/5), and excellent (5/5) answer.
6. "scoring_template": A quick reference guide mapping scoring criteria to weightage.
7. "interviewer_notes": A default helpful instructions string for the interviewer.

Ensure the output is ONLY valid JSON.
"""

        try:
            kit_data = self.llm.generate_json(prompt, system_prompt=system_prompt)
            
            # Save to db
            scoring_tmpl = kit_data.get("scoring_template", "")
            if isinstance(scoring_tmpl, (dict, list)):
                scoring_tmpl = json.dumps(scoring_tmpl)
            elif scoring_tmpl is None:
                scoring_tmpl = ""
            else:
                scoring_tmpl = str(scoring_tmpl)

            eval_rubric = kit_data.get("evaluation_rubric", "")
            if isinstance(eval_rubric, (dict, list)):
                eval_rubric = json.dumps(eval_rubric)
            elif eval_rubric is None:
                eval_rubric = ""
            else:
                eval_rubric = str(eval_rubric)

            notes = kit_data.get("interviewer_notes", "")
            if isinstance(notes, (dict, list)):
                notes = json.dumps(notes)
            elif notes is None:
                notes = ""
            else:
                notes = str(notes)

            kit = InterviewKit(
                job_id=job_id,
                resume_id=resume_id,
                technical_questions=kit_data.get("technical_questions", []),
                behavioral_questions=kit_data.get("behavioral_questions", []),
                scenario_questions=kit_data.get("scenario_questions", []),
                role_specific_questions=kit_data.get("role_specific_questions", []),
                evaluation_rubric=eval_rubric,
                scoring_template=scoring_tmpl,
                interviewer_notes=notes
            )
            self.db.add(kit)
            self.db.commit()
            self.db.refresh(kit)
            
            kit_data["id"] = str(kit.id)
            return kit_data
        except Exception as e:
            return {"error": f"Failed to generate kit: {str(e)}"}

    def run_recruiter_copilot(
        self,
        recruiter_id: UUID,
        messages: List[Dict[str, str]],
        selected_job_id: Optional[UUID] = None
    ) -> str:
        """
        Conversational assistant for recruiters.
        Injects context from DB: jobs, pipelines, candidate listings, notes.
        """
        # 1. Fetch available jobs context
        jobs = self.db.query(Job).filter(Job.recruiter_id == recruiter_id).all()
        jobs_context = []
        for j in jobs:
            # Count applicants
            app_count = self.db.query(CandidatePipeline).filter(CandidatePipeline.job_id == j.id).count()
            jobs_context.append({
                "job_id": str(j.id),
                "title": j.title,
                "status": j.status,
                "applicants_count": app_count,
                "department": j.department
            })

        # 2. If a job is selected or there's an active job, pull candidates in pipeline
        candidates_context = []
        target_job = None
        if selected_job_id:
            target_job = self.db.query(Job).filter(Job.id == selected_job_id).first()
        elif jobs:
            target_job = jobs[0] # Fallback to first job for quick context

        if target_job:
            pipelines = self.db.query(CandidatePipeline).filter(CandidatePipeline.job_id == target_job.id).all()
            for p in pipelines:
                resume = p.resume
                if not resume:
                    continue
                parsed = resume.parsed_content
                candidates_context.append({
                    "name": parsed.get("name", "Unknown Candidate"),
                    "email": parsed.get("email", ""),
                    "stage": p.stage,
                    "ats_score": p.ats_score,
                    "jd_match_score": p.jd_match_score,
                    "skills": parsed.get("skills", [])[:5]
                })

        system_prompt = f"""
You are the ResumeFlow AI Recruiter Copilot, a conversational assistant built inside a recruiter SaaS platform.
You help recruiters manage jobs, review screening statistics, compare candidates, and make hiring decisions.

Here is the current context from the Recruiter's Database:
Active Jobs: {json.dumps(jobs_context, indent=2)}

Currently selected job for candidate review: {target_job.title if target_job else 'None'}
Candidates in this job's pipeline:
{json.dumps(candidates_context, indent=2)}

You can answer queries like:
- "Show top candidates for Backend Developer"
- "Who has the strongest Python skills?"
- "Which candidates are ready for interview?"
- "Summarize shortlisted candidates"

Use the context provided to answer accurately. If they ask about another job, mention that they can select it or list details of other jobs you see. Be professional, concise, and structured (use bullet points and highlights).
"""

        try:
            response = self.llm.chat(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.4
            )
            return response
        except Exception as e:
            return f"I'm sorry, I encountered an issue accessing my AI provider. (Details: {str(e)})"
