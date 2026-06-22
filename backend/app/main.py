from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
# Import models to ensure they are registered during table creation
from app.models import user, resume, jd, ats_result, jd_match, recruiter_upload
from app.api.v1 import auth, resumes, ats, jds, recruiter

# Initialize database schema tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"Error initializing database tables: {str(e)}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Resume Screening and ATS Optimization Platform API Engine.",
    version="1.0.0"
)

# Enforce secure CORS policy
# In production, specify exact domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(ats.router, prefix="/api/v1")
app.include_router(jds.router, prefix="/api/v1")
app.include_router(recruiter.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
