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
│       ├── jobs.py           # Job management CRUD APIs (Phase 2)
│       ├── pipeline.py       # Kanban hiring pipeline & timeline APIs (Phase 2)
│       ├── recruiter.py      # Recruiter batch screening (Phase 1)
│       └── recruiter_endpoints.py # Advanced Recruiter Workflows & Recopilot (Phase 2)
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
│   ├── recruiter_upload.py
│   ├── job.py                # Job specification, skills, team members tables (Phase 2)
│   ├── pipeline.py           # Kanban Pipeline stage, history, notes, feedback (Phase 2)
│   ├── comparison.py         # AI candidate comparison sessions table (Phase 2)
│   ├── interview_kit.py      # AI structured interview kits table (Phase 2)
│   ├── recruiter_analytics.py # Performance metrics tracking table (Phase 2)
│   └── activity_log.py       # Audit trail logger table (Phase 2)
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
│   ├── recruiter.py
│   ├── jobs.py               # Job request & response Pydantic schemas (Phase 2)
│   ├── pipeline.py           # Stage movement & notes schema validations (Phase 2)
│   └── recruiter_workflow.py # Comparisons, kits, chat request schemas (Phase 2)
├── services/                 # Core business & processing logic
│   ├── auth_service.py       # Authentication logic
│   ├── parser_service.py     # Document text parsing and regex info extraction
│   ├── ats_scorer.py         # Breakdown score algorithms
│   ├── matching_service.py   # Embeddings comparisons via Sentence Transformers
│   ├── recruiter_service.py  # Ranked queues screening (Phase 1)
│   ├── job_service.py        # Job configurations & dashboard stats service (Phase 2)
│   ├── pipeline_service.py   # Kanban board card movements & note logging (Phase 2)
│   ├── recruiter_ai_service.py # AI evaluations, comparisons, kits, Recopilot chat (Phase 2)
│   └── analytics_service.py  # Aggregate metrics & stage conversion funnels (Phase 2)
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

---

## 4. Phase 2 Services

Phase 2 introduces pluggable AI and workflows for both Candidate Career Growth and Recruiter Management:

### 4.1 Career Growth Services

1. **LLM Provider Abstraction (`llm_provider.py`)**:
   - Outlines an abstract base `LLMProvider` class defining the standard text generation signature: `generate(prompt, system_prompt, temperature, max_tokens, json_mode)`.
   - Implements a concrete `OpenRouterProvider` utilizing the official `openai` Python SDK. It communicates with OpenRouter API using configured key and model variables (`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`).
   - Standardizes error logging, rate-limit retries, and formats JSON outputs via a helper factory `get_llm_provider()`.

2. **Rewriter Service (`rewriter_service.py`)**:
   - Employs the LLM to rewrite specific sections of parsed resumes. Accepts target roles, tones (Professional, Executive, Technical, Creative), and focus areas. Saves results as incremented versions in `ResumeVersion` tables.

3. **Interview Service (`interview_service.py`)**:
   - Dynamically constructs a list of technical, behavioral, and situational interview questions.
   - Evaluates submitted answers on a 0-10 score scale. AI response formatting follows the **STAR method** (Situation, Task, Action, Result) structure.

4. **Skill Gap Service (`skill_gap_service.py`)**:
   - Cross-references parsed skills against typical industry requirements for a target role. Calculates a readiness index score, lists critical missing skills, and suggests targeted educational/learning guides.

5. **Roadmap Service (`roadmap_service.py`)**:
   - Maps milestone timelines (in months) for transitioning from a current role to a target career role, indicating concrete actions and certs required in each phase.

6. **Tracker Service (`tracker_service.py`)**:
   - Lightweight CRUD logic managing job applications. Aggregates statistical metrics on total applications in each status lane.

7. **Job Match Service (`job_match_service.py`)**:
   - Match candidate resumes against active recruiter-submitted JDs, reusing the vector matching capabilities of the existing matching service.

8. **Coach Service (`coach_service.py`)**:
   - Maintains messaging history to simulate a conversational career advisor, passing user resume context to guide all conversations.

### 4.2 Recruiter Advanced Workflow Services

1. **Job Service (`job_service.py`)**:
   - Manages job openings CRUD, adds skills mappings, and associates team members (collaborators).
   - Generates summary statistics of jobs counts (active, draft, total candidate count) for the recruiter dashboard.

2. **Pipeline Service (`pipeline_service.py`)**:
   - Handles the Kanban card stage movements and checks recruiter ownership.
   - Saves stage transition logs to candidate stage history.
   - Records reviewer comments (candidate notes) and interviewer rating scores (candidate feedback).
   - Returns a structured timeline of stage logs, notes, and feedback.

3. **Recruiter AI Service (`recruiter_ai_service.py`)**:
   - Generates candidate insights (fit reasons, flags, confidence score, hiring recommendation) utilizing OpenRouter.
   - Evaluates and compares multiple candidates side-by-side on skills, experience, and education, generating an AI summary recommendation.
   - Assembles tailor-made, candidate-specific interview kits containing behavioral/technical question groups, rubrics, and evaluation forms.
   - Powers the AI Recopilot chat assistant using a custom system prompt containing all available candidate profiles and job details.

4. **Analytics Service (`analytics_service.py`)**:
   - Measures candidate conversion rates, calculates average days spent in pipeline stages, and counts candidate allocations.
   - Formulates aggregate funnel statistics and returns timeline arrays for visualization in Next.js.

---

## 5. Deployment Build Optimizations

To avoid long deployment build delays due to large library dependencies:
- **CPU-only PyTorch Setup**: The `backend/Dockerfile` pre-installs the CPU-only version of PyTorch (`torch --index-url https://download.pytorch.org/whl/cpu`) before installing the general `requirements.txt`.
- **93% Build Size Reduction**: This configuration skips the heavy NVIDIA GPU CUDA packages (e.g., `nvidia-cublas`, `nvidia-cudnn`), shrinking the Docker image download volume from 2.5 GB to ~190 MB, ensuring fast deployment pipelines.
- **Pre-baked Cache**: The `all-MiniLM-L6-v2` Sentence Transformer model is downloaded during the image build stage (`RUN python -c "..."`) to avoid latency on container startup.

