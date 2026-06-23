from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
# Import models to ensure they are registered during table creation
from app.models import (
    user, resume, jd, ats_result, jd_match, recruiter_upload,
    resume_version, interview, skill_gap, career_roadmap, job_application, coach,
    job, pipeline, comparison, interview_kit, recruiter_analytics, activity_log
)
# Phase 1 routers
from app.api.v1 import auth, resumes, ats, jds, recruiter
# Phase 2 routers
from app.api.v1 import rewriter, interview as interview_api, skill_gap as skill_gap_api
from app.api.v1 import roadmap, tracker, job_match, coach as coach_api
# Recruiter Workflow routers
from app.api.v1 import jobs, pipeline, recruiter_endpoints

# Initialize database schema tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"Error initializing database tables: {str(e)}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Resume Screening, ATS Optimization, and Career Growth Platform API.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 1 Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(ats.router, prefix="/api/v1")
app.include_router(jds.router, prefix="/api/v1")
app.include_router(recruiter.router, prefix="/api/v1")

# Phase 2 Routers
app.include_router(rewriter.router, prefix="/api/v1")
app.include_router(interview_api.router, prefix="/api/v1")
app.include_router(skill_gap_api.router, prefix="/api/v1")
app.include_router(roadmap.router, prefix="/api/v1")
app.include_router(tracker.router, prefix="/api/v1")
app.include_router(job_match.router, prefix="/api/v1")
app.include_router(coach_api.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(pipeline.router, prefix="/api/v1")
app.include_router(recruiter_endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
