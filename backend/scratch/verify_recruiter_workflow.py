import sys
import os
from sqlalchemy.orm import Session
import uuid

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.resume import Resume
from app.services.job_service import JobService
from app.services.pipeline_service import PipelineService
from app.services.recruiter_ai_service import RecruiterAIService
from app.services.analytics_service import AnalyticsService

def run_integration_test():
    print("Starting recruiter workflow end-to-end integration validation...")
    db: Session = SessionLocal()
    
    try:
        # 1. Fetch or create a test recruiter user
        recruiter = db.query(User).filter(User.role == "RECRUITER").first()
        if not recruiter:
            print("Creating test recruiter...")
            recruiter = User(
                email="test_recruiter@example.com",
                password_hash="hashed_pw",
                first_name="Test",
                last_name="Recruiter",
                role="RECRUITER"
            )
            db.add(recruiter)
            db.commit()
            db.refresh(recruiter)
        print(f"[OK] Recruiter user active: {recruiter.email} (ID: {recruiter.id})")

        # 2. Fetch or create a test resume profile
        resume = db.query(Resume).first()
        if not resume:
            print("Creating test candidate resume...")
            resume = Resume(
                file_name="jane_doe_cv.pdf",
                file_path="/uploads/jane_doe_cv.pdf",
                raw_text="Jane Doe. Python software engineer with experience in FastAPI, Docker, and AWS.",
                parsed_content={
                    "name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "phone": "555-0199",
                    "skills": ["Python", "FastAPI", "Docker", "AWS"],
                    "experience": [
                        {"role": "Backend Engineer", "company": "Tech Innovators LLC", "duration": "3 years"}
                    ],
                    "education": [
                        {"degree": "Bachelor of Science", "major": "Computer Science", "school": "State Tech University"}
                    ],
                    "projects": ["Built AI ATS parser scaling microservices to 10k users."],
                    "certifications": ["AWS Certified Solutions Architect"]
                }
            )
            db.add(resume)
            db.commit()
            db.refresh(resume)
        print(f"[OK] Candidate resume active: {resume.file_name} (ID: {resume.id})")

        # 3. Job Management: Create job spec
        job_service = JobService(db)
        job_data = {
            "title": "Senior FastAPI Developer",
            "department": "Engineering",
            "employment_type": "Full-time",
            "experience_required": "3-5 years",
            "location": "Remote",
            "salary_range": "$120,000 - $140,000",
            "description": "Looking for a backend engineer who knows Python, FastAPI, and AWS.",
            "skills_required": ["Python", "FastAPI"],
            "skills_preferred": ["AWS", "Docker"]
        }
        job = job_service.create_job(recruiter.id, job_data)
        print(f"[OK] Job spec created: {job.title} (ID: {job.id})")

        # 4. Pipeline setup: Add candidate to Applied stage
        from app.models.pipeline import CandidatePipeline
        pipeline_entry = CandidatePipeline(
            job_id=job.id,
            resume_id=resume.id,
            stage="Applied",
            ats_score=85,
            jd_match_score=90
        )
        db.add(pipeline_entry)
        db.commit()
        db.refresh(pipeline_entry)
        print(f"[OK] Candidate added to Kanban Pipeline. Stage: {pipeline_entry.stage} (ID: {pipeline_entry.id})")

        # 5. Pipeline transitions: Move candidate from Applied -> Shortlisted
        pipeline_service = PipelineService(db)
        moved = pipeline_service.move_candidate(
            recruiter_id=recruiter.id,
            pipeline_id=pipeline_entry.id,
            to_stage="Shortlisted",
            notes="Strong compatibility with FastAPI requirements."
        )
        print(f"[OK] Candidate transitioned in Kanban. New Stage: {moved.stage}")

        # 6. Collaboration: Add recruiter notes & feedback
        db_note = pipeline_service.db.query(User).filter(User.id == recruiter.id).first() # verification check
        note = pipeline_service.move_candidate(recruiter.id, pipeline_entry.id, "Interview Scheduled", "Scheduled first round interview.")
        print(f"[OK] Add Candidate Note & stage movement log successfully recorded.")

        # 7. AI Intelligence: Generate candidate insights
        ai_service = RecruiterAIService(db)
        insights = ai_service.generate_candidate_insights(job.id, resume.id)
        print(f"[OK] AI Insights generated successfully. Recommendation: {insights.get('hiring_recommendation')} (Confidence: {insights.get('confidence_score')}%)")

        # 8. AI Interview Kit: Generate guide pack
        kit = ai_service.generate_interview_kit(job.id, resume.id)
        print(f"[OK] Structured Interview Kit generated. Technical question count: {len(kit.get('technical_questions', []))}")

        # 9. AI Recopilot: Simulate copilot chat querying candidates
        chat_reply = ai_service.run_recopilot_prompt = ai_service.run_recopilot_prompt = ai_service.run_recruiter_copilot(
            recruiter_id=recruiter.id,
            messages=[{"role": "user", "content": "Show all Python candidates ready for interview."}],
            selected_job_id=job.id
        )
        print(f"[OK] AI Recopilot chatbot conversation succeeded. Bot reply sample: {chat_reply[:60]}...")

        # 10. Analytics: Get dashboard metrics
        analytics_service = AnalyticsService(db)
        analytics = analytics_service.get_recruiter_analytics(recruiter.id)
        print(f"[OK] Analytics summaries compiled. Conversion Rate: {analytics['metrics']['pipeline_conversion_rate']}%")

        # Clean up database test entries
        db.delete(pipeline_entry)
        db.delete(job)
        db.commit()
        print("Cleaned up database test records successfully.")
        
        print("\n[SUCCESS] End-to-end integration test completed successfully!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Workflow validation encountered an error: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
