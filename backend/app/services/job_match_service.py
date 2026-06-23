"""
Job Match Service
Matches candidate resume against available job descriptions using existing matching engine.
"""
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.models.jd import JobDescription
from app.services.matching_service import MatchingService


class JobMatchService:
    
    def __init__(self, db: Session):
        self.db = db
        self.matching = MatchingService()
    
    def find_matches(self, resume_id: str, preferred_roles: list[str] = None, preferred_locations: list[str] = None) -> dict:
        """Find job matches for a resume against all stored job descriptions."""
        
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("Resume not found")
        
        parsed = resume.parsed_content
        skills = parsed.get("skills", [])
        
        # Get all job descriptions
        jds = self.db.query(JobDescription).all()
        
        matches = []
        for jd in jds:
            # Calculate match using the existing matching service
            try:
                match_result = self.matching.calculate_match(
                    resume_skills=skills,
                    resume_text=resume.raw_text,
                    jd_text=jd.raw_content,
                )
                
                match_score = match_result.get("match_score", 0)
                matched_skills = match_result.get("matched_skills", [])
                missing_skills = match_result.get("missing_skills", [])
                
                matches.append({
                    "job_id": str(jd.id),
                    "title": jd.title,
                    "company_name": jd.company_name or "Unknown Company",
                    "match_score": round(match_score, 1),
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                })
            except Exception as e:
                print(f"Error matching JD {jd.id}: {e}")
                continue
        
        # Sort by match score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Filter by preferred roles if specified
        if preferred_roles:
            role_lower = [r.lower() for r in preferred_roles]
            filtered = [m for m in matches if any(r in m["title"].lower() for r in role_lower)]
            if filtered:
                matches = filtered
        
        return {
            "matches": matches[:20],  # Top 20 matches
            "total_jobs_scanned": len(jds),
        }
