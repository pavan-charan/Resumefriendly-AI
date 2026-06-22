import re
from typing import Dict, Any, List

class ATSScorer:
    ADVANCED_KEYWORDS = ["Kubernetes", "AWS", "CI/CD", "Docker", "FastAPI", "React", "TypeScript", "PostgreSQL", "Next.js", "Machine Learning"]

    def calculate_score(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates ATS Score out of 100 based on standard weighted categories.
        """
        skills = parsed_content.get("skills", [])
        experience = parsed_content.get("experience", [])
        education = parsed_content.get("education", [])
        projects = parsed_content.get("projects", [])
        certifications = parsed_content.get("certifications", [])
        name = parsed_content.get("name")
        email = parsed_content.get("email")
        phone = parsed_content.get("phone")
        raw_text = parsed_content.get("raw_text", "")

        # 1. Contact Information Score (Max 5)
        contact_score = 0
        if name and name != "Unknown Candidate":
            contact_score += 1
        if email:
            contact_score += 2
        if phone:
            contact_score += 2

        # 2. Education Score (Max 10)
        education_score = 0
        if education:
            education_score = 8
            # Upgrade if advanced degree found
            for edu in education:
                degree_lower = edu.get("degree", "").lower()
                if "master" in degree_lower or "phd" in degree_lower or "m.s" in degree_lower:
                    education_score = 10
                    break

        # 3. Experience Score (Max 20)
        experience_score = 0
        if experience:
            if len(experience) == 1:
                experience_score = 12
            elif len(experience) >= 2:
                experience_score = 20

        # 4. Formatting Score (Max 15)
        formatting_score = 15
        missing_sections = []
        formatting_issues = []
        
        if not projects:
            formatting_score -= 5
            missing_sections.append("Projects")
            formatting_issues.append("Missing a dedicated Projects section to demonstrate applied knowledge.")
        if not certifications:
            formatting_score -= 5
            missing_sections.append("Certifications")
            formatting_issues.append("No Certification list found. Certifications build authority.")
            
        # Ensure minimum formatting score of 5
        formatting_score = max(5, formatting_score)

        # 5. Skills Score (Max 30)
        skills_score = 0
        num_skills = len(skills)
        if num_skills > 0:
            if num_skills <= 3:
                skills_score = 10
            elif num_skills <= 7:
                skills_score = 20
            else:
                skills_score = 30

        # 6. Keywords Score (Max 20)
        keywords_score = 0
        matched_keywords = []
        missing_keywords = []
        
        # Combine skills list & raw text for keyword searching
        combined_text = (", ".join(skills) + " " + raw_text).lower()
        
        for keyword in self.ADVANCED_KEYWORDS:
            if keyword.lower() in combined_text:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
                
        num_matched_kw = len(matched_keywords)
        if num_matched_kw > 0:
            if num_matched_kw <= 2:
                keywords_score = 8
            elif num_matched_kw <= 4:
                keywords_score = 15
            else:
                keywords_score = 20

        # Overall sum
        overall_score = contact_score + education_score + experience_score + formatting_score + skills_score + keywords_score

        # Explainability & Recommendations
        weak_content_areas = []
        strengths = []

        if overall_score >= 80:
            strengths.append("Excellent keyword optimization and layout formatting.")
        elif overall_score >= 60:
            strengths.append("Decent resume structure. Solid baseline metrics.")
        else:
            weak_content_areas.append("Your overall score is low. Please incorporate missing skills and section markers.")

        # Check for metrics/quantified results in experience descriptions
        metrics_found = False
        for exp in experience:
            desc = exp.get("description", "")
            # Look for percentages or numbers
            if re.search(r"\b\d+%\b|\b\d+\s*percent\b|\$\s*\d+|\b\d+\s*x\b", desc):
                metrics_found = True
                break
                
        if not metrics_found:
            weak_content_areas.append("Add quantified achievements (e.g., 'scaled performance by 40%', 'reduced latency by 200ms') in job descriptions.")
        else:
            strengths.append("Includes quantified business outcomes and metrics.")

        if not email or not phone:
            weak_content_areas.append("Ensure contact methods (Email & Phone) are clearly visible at the top.")
        else:
            strengths.append("Contact information is complete and well-positioned.")

        if missing_keywords:
            weak_content_areas.append(f"Incorporate advanced keyword terms such as: {', '.join(missing_keywords[:3])}.")

        # Package breakdown & detail maps
        breakdown = {
            "skills": skills_score,
            "keywords": keywords_score,
            "experience": experience_score,
            "formatting": formatting_score,
            "education": education_score,
            "contact_info": contact_score
        }

        explainability = {
            "missing_keywords": missing_keywords,
            "missing_sections": missing_sections,
            "formatting_issues": formatting_issues,
            "weak_content_areas": weak_content_areas,
            "strengths": strengths
        }

        return {
            "overall_score": overall_score,
            "breakdown": breakdown,
            "explainability": explainability
        }
