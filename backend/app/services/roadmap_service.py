"""
Career Roadmap Generator Service
Creates personalized career progression plans using LLM.
"""
import json
from sqlalchemy.orm import Session
from app.core.llm_provider import get_llm_provider
from app.models.resume import Resume
from app.models.career_roadmap import CareerRoadmap


class RoadmapService:
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()
    
    def generate(
        self,
        user_id: str,
        current_role: str,
        target_role: str,
        timeline_months: int = 12,
        resume_id: str = None,
    ) -> dict:
        """Generate a career roadmap."""
        
        # Get resume context
        parsed = {}
        if resume_id:
            resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                parsed = resume.parsed_content
        
        skills = parsed.get("skills", [])
        experience = parsed.get("experience", [])
        education = parsed.get("education", [])
        
        prompt = f"""Create a detailed career roadmap for transitioning from {current_role} to {target_role} within {timeline_months} months.

CANDIDATE'S CURRENT SKILLS: {', '.join(skills) if skills else 'Not specified'}
CANDIDATE'S EXPERIENCE: {json.dumps(experience[:3]) if experience else 'Not specified'}
CANDIDATE'S EDUCATION: {json.dumps(education) if education else 'Not specified'}

Return a JSON object with:
- "phases": array of phases, each containing:
  - "phase_name": descriptive name (e.g., "Foundation Building")
  - "duration_months": number of months for this phase
  - "milestones": array of specific, measurable milestones
  - "skills_to_learn": array of skills to acquire
  - "resources": array of learning resources (courses, books, platforms)
- "certifications": array of recommended certifications, each with:
  - "name": certification name
  - "provider": who offers it
  - "estimated_time": how long to complete
- "target_companies": array of companies hiring for the target role
- "salary_progression": object with "current_estimate" and "target_estimate" salary ranges

Make the plan realistic and actionable. Phase durations should sum to approximately {timeline_months} months."""

        result = self.llm.generate_json(
            prompt=prompt,
            system_prompt="You are a career counselor specializing in tech career transitions. Create detailed, actionable career roadmaps. Always respond with valid JSON.",
            temperature=0.7,
            max_tokens=4000,
        )
        
        # Save to database
        roadmap = CareerRoadmap(
            user_id=user_id,
            resume_id=resume_id,
            current_role=current_role,
            target_role=target_role,
            timeline_months=timeline_months,
            roadmap_data=result,
        )
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)
        
        return {
            "id": str(roadmap.id),
            "current_role": current_role,
            "target_role": target_role,
            "timeline_months": timeline_months,
            "phases": result.get("phases", []),
            "certifications": result.get("certifications", []),
            "target_companies": result.get("target_companies", []),
            "salary_progression": result.get("salary_progression", {}),
            "created_at": roadmap.created_at.isoformat(),
        }
    
    def get_history(self, user_id: str) -> list[dict]:
        """Get past roadmaps."""
        roadmaps = (
            self.db.query(CareerRoadmap)
            .filter(CareerRoadmap.user_id == user_id)
            .order_by(CareerRoadmap.created_at.desc())
            .all()
        )
        return [
            {
                "id": str(r.id),
                "current_role": r.current_role,
                "target_role": r.target_role,
                "timeline_months": r.timeline_months,
                "created_at": r.created_at.isoformat(),
            }
            for r in roadmaps
        ]
