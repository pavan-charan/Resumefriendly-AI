from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
from fastapi import UploadFile

from app.core.storage import storage_manager
from app.repositories.jd import JobDescriptionRepository
from app.repositories.resume import ResumeRepository
from app.services.parser_service import ParserService
from app.services.matching_service import MatchingService
from app.schemas.recruiter import RecruiterScreenResponse, RankedCandidate, CandidateSummary

class RecruiterService:
    def __init__(self, db: Session):
        self.db = db
        self.jd_repo = JobDescriptionRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.parser_service = ParserService()
        self.matching_service = MatchingService()

    def screen_and_rank_candidates(
        self, 
        recruiter_id: UUID,
        title: str,
        company_name: str,
        department: str,
        jd_text: str,
        files: List[UploadFile]
    ) -> RecruiterScreenResponse:
        """
        Creates job posting, uploads files, parses contents, scores similarity, and ranks candidates.
        """
        # 1. Create Job Description record
        db_jd = self.jd_repo.create(
            creator_id=recruiter_id,
            title=title,
            company_name=company_name,
            department=department,
            raw_content=jd_text,
            requirements=jd_text
        )

        ranked_candidates = []
        
        # 2. Process each resume in batch
        for idx, file in enumerate(files):
            # Save file to storage
            file_path = storage_manager.save_file(file)
            
            try:
                # Parse resume text & structure sections
                parsed = self.parser_service.parse_file(file_path)
                raw_text = parsed["raw_text"]
                content = parsed["parsed_content"]
                
                # Save Resume record to DB
                db_resume = self.resume_repo.create(
                    user_id=None, # Anonymous upload on behalf of candidate
                    file_name=file.filename,
                    file_path=file_path,
                    raw_text=raw_text,
                    parsed_content=content
                )
                
                # Link upload to recruiter tracking
                self.jd_repo.create_recruiter_upload(
                    recruiter_id=recruiter_id,
                    jd_id=db_jd.id,
                    resume_id=db_resume.id
                )
                
                # Match against job description requirements
                match_results = self.matching_service.match_resume_to_jd(
                    resume_text=raw_text,
                    resume_skills=content.get("skills", []),
                    jd_text=jd_text
                )
                
                # Save JDMatch record to DB
                self.jd_repo.create_jd_match(
                    resume_id=db_resume.id,
                    jd_id=db_jd.id,
                    match_score=match_results["match_score"],
                    match_details=match_results
                )
                
                # Construct clean experience summary sentence
                experience_list = content.get("experience", [])
                exp_summary = "Not specified"
                if experience_list:
                    primary = experience_list[0]
                    exp_summary = f"{primary.get('role', 'Professional')} at {primary.get('company', 'Organization')} ({primary.get('duration', 'N/A')})"
                
                # Construct clean education summary sentence
                education_list = content.get("education", [])
                edu_summary = "Degree not specified"
                college_name = "N/A"
                graduation_year = "N/A"
                if education_list:
                    primary = education_list[0]
                    edu_summary = f"{primary.get('degree', 'Degree')} in {primary.get('major', 'Major')} from {primary.get('school', 'School')}"
                    college_name = primary.get('school', 'N/A')
                    graduation_year = primary.get('grad_year', 'N/A')

                summary = CandidateSummary(
                    skills=content.get("skills", []),
                    experience=exp_summary,
                    education=edu_summary,
                    college_name=college_name,
                    graduation_year=graduation_year,
                    match_percentage=match_results["match_score"]
                )
                
                ranked_candidates.append({
                    "candidate_name": content.get("name", "Unknown Candidate"),
                    "email": content.get("email") or f"no-email-{idx}@example.com",
                    "match_score": match_results["match_score"],
                    "summary": summary
                })
                
                # Index in ChromaDB for fast retrieval
                self.matching_service.add_resume_to_vector_store(
                    resume_id=str(db_resume.id),
                    text=raw_text,
                    metadata={"name": content.get("name"), "email": content.get("email")}
                )
                
            except Exception as e:
                # Log parsing failure and continue other candidates to avoid failing entire batch
                # In production, use standard python logger
                print(f"Failed to parse resume {file.filename}: {str(e)}")
                # Delete corrupted file if needed
                storage_manager.delete_file(file_path)

        # 3. Sort candidates by match score in descending order
        ranked_candidates.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 4. Map ranks
        ranked_list = []
        for rank, cand in enumerate(ranked_candidates, start=1):
            ranked_list.append(
                RankedCandidate(
                    rank=rank,
                    candidate_name=cand["candidate_name"],
                    email=cand["email"],
                    match_score=cand["match_score"],
                    summary=cand["summary"]
                )
            )

        return RecruiterScreenResponse(
            job_id=db_jd.id,
            ranked_candidates=ranked_list
        )
