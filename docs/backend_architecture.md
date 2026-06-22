# Backend Architecture Document - ResumeFriendly AI

This document outlines the backend design principles, service-repository patterns, dependency injections, and security flows in the FastAPI application.

---

## 1. Directory Structure & Architecture Layers

The backend follows a layered architecture to achieve high testability, maintenance, and separation of concerns:

```text
backend/app/
├── api/
│   └── v1/                   # FastAPI routing endpoints
│       ├── auth.py           # Login, registration, token refresh APIs
│       ├── resumes.py        # Resume uploads and metadata lookups
│       ├── ats.py            # ATS score calculation triggers
│       ├── jds.py            # JD creations and resume JD matching
│       └── recruiter.py      # Recruiter dashboard features (batch screening)
├── core/
│   ├── config.py             # App environment variables & parameters
│   ├── database.py           # SQLAlchemy engines and session pools
│   ├── security.py           # Bcrypt hashing & JWT verification
│   └── storage.py            # File upload abstractions (Local vs S3)
├── models/                   # SQLAlchemy database schemas
│   ├── user.py
│   ├── resume.py
│   ├── jd.py
│   ├── ats_result.py
│   ├── jd_match.py
│   └── recruiter_upload.py
├── repositories/             # Relational Database Access layer (CRUD)
│   ├── user.py
│   ├── resume.py
│   ├── jd.py
│   └── matching.py
├── schemas/                  # Pydantic schemas (DTO validation layer)
│   ├── auth.py
│   ├── resume.py
│   ├── jd.py
│   ├── ats.py
│   └── recruiter.py
├── services/                 # Core business & processing logic
│   ├── auth_service.py       # Authentication logic
│   ├── parser_service.py     # Document text parsing and regex info extraction
│   ├── ats_scorer.py         # Breakdown score algorithms
│   ├── matching_service.py   # Embeddings comparisons via Sentence Transformers
│   └── recruiter_service.py  # Ranked queues screening
├── utils/                    # Common helper utilities
└── main.py                   # App entrypoint and CORS setups
```

---

## 2. Core Service Designs

1. **Parser Service (`parser_service.py`)**:
   - Accepts PDF or DOCX file streams.
   - Extracts characters using `pypdf` or `python-docx` tools.
   - Normalizes text and runs regex search matches for Contact Info (Emails, Phones).
   - Scans text structures against structured dictionary mappings to categorize Skills, Experience highlights, Education degrees, and Certifications.
2. **ATS Scorer (`ats_scorer.py`)**:
   - Calculates a combined weighted score out of 100 based on exact keywords presence, experience timelines, contact details, formatting elements, and education profiles.
   - Assembles granular JSON response showing strength areas and optimization suggestions.
3. **Matching Service (`matching_service.py`)**:
   - Instantiates a local `sentence-transformers` engine using the lightweight `all-MiniLM-L6-v2` model (converts strings to 384-dimensional dense vectors).
   - Generates embedding arrays for Job Descriptions and Candidate Resumes.
   - Measures semantic similarity using Cosine Distance calculations.
   - Employs ChromaDB to index vector collections.

---

## 3. Dependency Injection & Repository Patterns

We enforce standard patterns to ensure clean, mockable logic:
- **Repository Pattern**: All database interactions pass through repositories (e.g., `UserRepository`, `ResumeRepository`). Services do not make raw SQL calls. This decouples database choice (SQLAlchemy) from core logic.
- **FastAPI Dependency Injection (`Depends`)**:
  - Database sessions (`get_db`) are injected into repositories.
  - Repositories are injected into services.
  - Authentication tokens are parsed via an injected dependencies check (`get_current_user`), which validates claims, verifies signature, check roles, and automatically raises `401 Unauthorized` or `403 Forbidden` exceptions on failures.
