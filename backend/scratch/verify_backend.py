import sys
import os

# Append workspace path to system import search
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

def test_imports_and_scorer():
    print("Testing backend modules setup...")
    
    try:
        from app.services.parser_service import ParserService
        from app.services.ats_scorer import ATSScorer
        from app.services.matching_service import MatchingService
        print("[OK] Successfully imported services (ParserService, ATSScorer, MatchingService).")
    except ImportError as e:
        print(f"[FAIL] Failed to import services: {str(e)}")
        return False

    # Mock parsed profile
    mock_profile = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0199",
        "skills": ["Python", "FastAPI", "React", "Docker", "AWS"],
        "experience": [
            {
                "role": "Software Engineer",
                "company": "Tech Corp",
                "duration": "3 years",
                "description": "Built robust microservices with FastAPI and Docker. Scaled performance by 25%."
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "major": "Computer Science",
                "school": "State University"
            }
        ],
        "projects": ["Build ATS Optimizer Platform using FastAPI and React."],
        "certifications": ["AWS Certified Solutions Architect"],
        "raw_text": "Experienced Python Software Engineer skilled in FastAPI, React, Docker, and AWS."
    }

    try:
        scorer = ATSScorer()
        results = scorer.calculate_score(mock_profile)
        print(f"[OK] ATS Scorer executed successfully. Overall score: {results['overall_score']}/100.")
        print(f"  Breakdown: {results['breakdown']}")
        print(f"  Strengths: {results['explainability']['strengths']}")
    except Exception as e:
        print(f"[FAIL] ATS Scorer failed to compute: {str(e)}")
        return False

    try:
        # Check matching algorithms
        matcher = MatchingService()
        jd_text = "Looking for a Python Developer who knows FastAPI, React, and AWS."
        match_results = matcher.match_resume_to_jd(
            resume_text=mock_profile["raw_text"],
            resume_skills=mock_profile["skills"],
            jd_text=jd_text
        )
        print(f"[OK] Matching Engine computed successfully. Similarity: {match_results['match_score']}%")
        print(f"  Matched Skills: {match_results['matched_skills']}")
        print(f"  Missing Skills: {match_results['missing_skills']}")
    except Exception as e:
        print(f"[FAIL] Matching Engine initialization failed: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    success = test_imports_and_scorer()
    sys.exit(0 if success else 1)
