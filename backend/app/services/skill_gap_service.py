"""
Skill Gap Analysis Service
Analyzes the gap between user's current skills and target role requirements using LLM.
"""
import json
from sqlalchemy.orm import Session
from app.core.llm_provider import get_llm_provider
from app.models.resume import Resume
from app.models.skill_gap import SkillGapAnalysis


class SkillGapService:
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()
    
    def analyze(self, user_id: str, target_role: str, resume_id: str = None) -> dict:
        """Analyze skill gap for a target role."""
        
        # Get resume context
        parsed = {}
        if resume_id:
            resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                parsed = resume.parsed_content
        
        skills = parsed.get("skills", [])
        experience = parsed.get("experience", [])
        education = parsed.get("education", [])
        
        prompt = f"""Analyze the skill gap between the candidate's current profile and the target role.

TARGET ROLE: {target_role}

CANDIDATE'S CURRENT SKILLS: {', '.join(skills) if skills else 'None listed'}

CANDIDATE'S EXPERIENCE:
{json.dumps(experience[:5]) if experience else 'None listed'}

CANDIDATE'S EDUCATION:
{json.dumps(education) if education else 'None listed'}

Return a JSON object with:
- "current_skills": array of {{"name": "skill name", "proficiency": 1-10}} for each of the candidate's skills, rated by their likely proficiency based on experience
- "missing_skills": array of {{"name": "skill name", "importance": "critical"|"important"|"nice-to-have", "resources": ["resource1", "resource2"]}} for skills they need for the target role
- "overall_readiness": integer 0-100 indicating how ready they are for the target role
- "recommendations": array of actionable recommendations to close the gap

Be thorough and specific. Consider industry standards for {target_role}."""

        result = self.llm.generate_json(
            prompt=prompt,
            system_prompt="You are a career development expert specializing in skill assessment and gap analysis. Provide detailed, actionable analysis. Always respond with valid JSON.",
            temperature=0.6,
            max_tokens=4000,
        )
        
        # Save to database
        analysis = SkillGapAnalysis(
            user_id=user_id,
            resume_id=resume_id,
            target_role=target_role,
            analysis_result=result,
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        
        return {
            "id": str(analysis.id),
            "target_role": target_role,
            "current_skills": result.get("current_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "overall_readiness": result.get("overall_readiness", 50),
            "recommendations": result.get("recommendations", []),
            "created_at": analysis.created_at.isoformat(),
        }
    
    def get_history(self, user_id: str) -> list[dict]:
        """Get past skill gap analyses."""
        analyses = (
            self.db.query(SkillGapAnalysis)
            .filter(SkillGapAnalysis.user_id == user_id)
            .order_by(SkillGapAnalysis.created_at.desc())
            .all()
        )
        return [
            {
                "id": str(a.id),
                "target_role": a.target_role,
                "overall_readiness": a.analysis_result.get("overall_readiness", 50) if a.analysis_result else 50,
                "created_at": a.created_at.isoformat(),
            }
            for a in analyses
        ]
