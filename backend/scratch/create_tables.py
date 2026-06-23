import sys
import os
from sqlalchemy import create_engine, inspect

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from app.core.database import Base, engine
# Import all models to register them on Base metadata
from app.models import (
    user, resume, jd, ats_result, jd_match, recruiter_upload,
    resume_version, interview, skill_gap, career_roadmap, job_application, coach,
    job, pipeline, comparison, interview_kit, recruiter_analytics, activity_log
)

def create_and_verify():
    print("Initializing table creation...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Base.metadata.create_all executed successfully!")
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Current tables in database: {tables}")
        
        required_tables = [
            "jobs", "job_skills", "candidate_pipeline", "candidate_stage_history",
            "candidate_notes", "candidate_feedback", "candidate_comparisons",
            "interview_kits", "recruiter_analytics", "team_members", "activity_logs"
        ]
        
        missing = [t for t in required_tables if t not in tables]
        if not missing:
            print("[SUCCESS] All new recruiter tables created successfully!")
            return True
        else:
            print(f"[FAIL] Missing tables: {missing}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error during table creation: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_and_verify()
    sys.exit(0 if success else 1)
