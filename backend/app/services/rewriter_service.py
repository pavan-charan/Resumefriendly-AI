"""
AI Resume Rewriter Service
Uses LLM to rewrite resume sections based on target role, tone, and focus areas.
"""
import json
from sqlalchemy.orm import Session
from app.core.llm_provider import get_llm_provider
from app.models.resume import Resume
from app.models.resume_version import ResumeVersion


class RewriterService:
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()
    
    def rewrite_resume(
        self,
        resume_id: str,
        user_id: str,
        target_role: str = None,
        tone: str = "professional",
        focus_areas: list[str] = None,
    ) -> dict:
        """Rewrite resume content using AI."""
        if focus_areas is None:
            focus_areas = ["summary", "experience", "skills"]
        
        # Fetch the resume
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("Resume not found")
        
        parsed = resume.parsed_content
        
        # Build the prompt
        prompt = self._build_rewrite_prompt(parsed, target_role, tone, focus_areas)
        
        system_prompt = """You are an expert resume writer and career consultant.
You rewrite resumes to be more impactful, ATS-friendly, and tailored to specific roles.
Always respond with valid JSON containing the rewritten sections and a list of improvements made.

Your JSON response must have this exact structure:
{
    "rewritten": {
        "summary": "A compelling professional summary",
        "experience": [{"role": "...", "company": "...", "duration": "...", "description": "..."}],
        "skills": ["skill1", "skill2"],
        "projects": ["project description 1"],
        "education": [{"degree": "...", "school": "...", "grad_year": "..."}]
    },
    "improvements": ["improvement 1", "improvement 2"]
}"""

        result = self.llm.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000,
        )
        
        # Determine version number
        existing_count = (
            self.db.query(ResumeVersion)
            .filter(ResumeVersion.resume_id == resume_id)
            .count()
        )
        version_number = existing_count + 1
        
        # Save the version
        version = ResumeVersion(
            resume_id=resume_id,
            user_id=user_id,
            version_number=version_number,
            original_content=parsed,
            rewritten_content=result.get("rewritten", {}),
            target_role=target_role,
            tone=tone,
            focus_areas=focus_areas,
            improvements=result.get("improvements", []),
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        return {
            "version_id": str(version.id),
            "version_number": version.version_number,
            "original": parsed,
            "rewritten": result.get("rewritten", {}),
            "improvements": result.get("improvements", []),
            "target_role": target_role,
            "tone": tone,
            "created_at": version.created_at.isoformat(),
        }
    
    def get_versions(self, resume_id: str) -> list[dict]:
        """Get all versions for a resume."""
        versions = (
            self.db.query(ResumeVersion)
            .filter(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.version_number.desc())
            .all()
        )
        return [
            {
                "id": str(v.id),
                "version_number": v.version_number,
                "target_role": v.target_role,
                "tone": v.tone,
                "created_at": v.created_at.isoformat(),
            }
            for v in versions
        ]
    
    def get_version(self, version_id: str) -> dict:
        """Get a specific version with full content."""
        version = self.db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
        if not version:
            raise ValueError("Version not found")
        return {
            "version_id": str(version.id),
            "version_number": version.version_number,
            "original": version.original_content,
            "rewritten": version.rewritten_content,
            "improvements": version.improvements or [],
            "target_role": version.target_role,
            "tone": version.tone,
            "created_at": version.created_at.isoformat(),
        }
    
    def _build_rewrite_prompt(
        self, parsed: dict, target_role: str, tone: str, focus_areas: list[str]
    ) -> str:
        """Build the LLM prompt for resume rewriting."""
        sections = []
        
        if "summary" in focus_areas or "experience" in focus_areas:
            exp = parsed.get("experience", [])
            exp_text = "\n".join([
                f"- {e.get('role', 'N/A')} at {e.get('company', 'N/A')} ({e.get('duration', 'N/A')}): {e.get('description', '')}"
                for e in exp
            ]) if exp else "No experience listed"
            sections.append(f"EXPERIENCE:\n{exp_text}")
        
        if "skills" in focus_areas:
            skills = parsed.get("skills", [])
            sections.append(f"SKILLS: {', '.join(skills) if skills else 'None listed'}")
        
        if "projects" in focus_areas:
            projects = parsed.get("projects", [])
            sections.append(f"PROJECTS: {json.dumps(projects) if projects else 'None listed'}")
        
        education = parsed.get("education", [])
        edu_text = "\n".join([
            f"- {e.get('degree', '')} from {e.get('school', '')} ({e.get('grad_year', '')})"
            for e in education
        ]) if education else "No education listed"
        sections.append(f"EDUCATION:\n{edu_text}")
        
        candidate_name = parsed.get("name", "Candidate")
        
        prompt = f"""Rewrite the following resume for {candidate_name} to be more impactful and ATS-friendly.

TARGET ROLE: {target_role or 'General improvement'}
TONE: {tone}
FOCUS AREAS: {', '.join(focus_areas)}

CURRENT RESUME CONTENT:
{chr(10).join(sections)}

Instructions:
1. Make bullet points action-oriented with quantifiable achievements where possible
2. Use industry-standard keywords for the target role
3. Ensure ATS compatibility (no special characters, clear formatting)
4. Maintain accuracy - do not fabricate experience or skills
5. Apply the {tone} tone throughout
6. Focus improvements on: {', '.join(focus_areas)}

Return a JSON object with "rewritten" (containing the improved sections) and "improvements" (a list of what you changed and why)."""

        return prompt
