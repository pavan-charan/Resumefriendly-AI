# ResumeFriendly AI

ResumeFriendly AI is a production-ready, AI-powered hiring intelligence and Applicant Tracking System (ATS) optimization platform. It features comprehensive candidate and recruiter interfaces.

---

## 🌟 Key Features

### For Candidates
- **ATS Analysis**: Upload resumes (PDF/DOCX) and generate structural scoring (out of 100).
- **Explainability Engine**: Detailed lists of missing keywords, missing sections, formatting flags, and recommendations.
- **JD Matcher**: Paste a job description to obtain a semantic similarity percentage, list matched vs. missing skills, and get personalized resume adjustments.

### For Recruiters
- **Job Creation**: Define requirements and skills tags for a job listing.
- **Batch Screening**: Upload multiple candidate resumes simultaneously.
- **Candidate Ranking**: View resumes sorted by semantic alignment (cosine similarity vectors).
- **Automated Summaries**: Read concise resume breakdowns (skills, years of experience, degree, and score match).

---

## 🛠️ Technology Stack
- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS, Shadcn UI, Framer Motion
- **Backend**: FastAPI, Python 3.12, SQLAlchemy, Uvicorn
- **Databases**: PostgreSQL (relational profiles), ChromaDB (embeddings index)
- **AI Engine**: Local Sentence Transformers (`all-MiniLM-L6-v2` - 384 dimensions)
- **Storage**: Local filesystem storage abstraction (extensible to AWS S3)

---

## 📂 Documentation List
Detailed technical documentations can be found in the `docs/` folder:
- [Product Requirements Document (PRD)](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/prd.md)
- [System Design Document](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/system_design.md)
- [Database Schema Document](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/database_design.md)
- [API Reference Manual](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/api_documentation.md)
- [Frontend Architecture](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/frontend_architecture.md)
- [Backend Architecture](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/backend_architecture.md)
- [Deployment Manual](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/deployment_guide.md)
- [Developer Onboarding](file:///c:/Users/sirap/OneDrive/Desktop/Resumefriendly/docs/developer_onboarding.md)

---

## 🚀 Quick Start (Docker Compose)

Spin up all containers (Next.js, FastAPI, PostgreSQL, ChromaDB) with a single command:

1. **Clone & Configure Env**:
   ```bash
   cp .env.example .env
   ```
2. **Build and Run**:
   ```bash
   docker-compose up -d --build
   ```
3. **Access Services**:
   - Web Frontend: [http://localhost:3000](http://localhost:3000)
   - API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔁 CI/CD Pipeline (GitHub Actions)

The repository now includes two workflows under `.github/workflows/`:

- **CI (`ci.yml`)**
  - Triggered on pull requests and pushes to `main`, `master`, and `develop`.
  - Backend job installs Python dependencies and validates the app with `python -m compileall app`.
  - Frontend job installs Node dependencies and runs `npm run build`.

- **CD (`cd.yml`)**
  - Triggered on pushes to `main` and manual `workflow_dispatch`.
  - Builds Docker images for backend and frontend.
  - Publishes both images to GitHub Container Registry (`ghcr.io`).
  - Optionally calls a deployment webhook if `DEPLOY_WEBHOOK_URL` is configured.

### Optional repository secrets

- `DEPLOY_WEBHOOK_URL` (optional): endpoint invoked after successful image publishing.
