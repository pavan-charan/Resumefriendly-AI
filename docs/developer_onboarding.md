# Developer Onboarding Guide - ResumeFriendly AI

Welcome to the team! This guide will walk you through setting up ResumeFriendly AI on your local workstation for development.

---

## 1. Prerequisites

Before starting, ensure your system has:
- **Python**: Version `3.12.x`
- **Node.js**: Version `18.x` or `20.x` (with `npm` v10+)
- **Docker & Docker Compose**: For containerized databases (PostgreSQL & ChromaDB)
- **Git**

---

## 2. Step-by-Step Local Setup

### 2.1 Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install standard requirements:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```
   *(Update `.env` secrets or database connection URLs if you plan to run PostgreSQL outside of Docker).*

### 2.2 Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Copy environment variables:
   ```bash
   cp .env.example .env.local
   ```

### 2.3 Starting Local Database Services
We use Docker to spin up database layers so we don't have to configure PostgreSQL locally.
In the project root, run:
```bash
docker-compose up -d postgres_db chroma_db
```
This launches Postgres at port `5432` and ChromaDB at port `8001`.

---

## 3. Running the Applications

### 3.1 Run Backend (FastAPI)
From the `backend/` directory with active `venv`:
```bash
uvicorn app.main:app --reload --port 8000
```
- API Docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger/OpenAPI).

### 3.2 Run Frontend (Next.js)
From the `frontend/` directory:
```bash
npm run dev
```
- The web app will be available at: [http://localhost:3000](http://localhost:3000).

---

## 4. Coding & Contribution Rules

1. **Strict TypeScript & PEP 8**: Ensure you run lint checks before committing code.
2. **DTO Pattern (Pydantic)**: Never pass raw ORM model entities to controllers. Always return valid Pydantic schemas.
3. **No Direct Database Calls**: Enforce the Repository Pattern. All DB reads/writes must reside in files inside `backend/app/repositories/`.
4. **Clean Git Commits**: Prepend commits with scope definitions, e.g., `feat(auth): add password strength checker` or `fix(parser): repair multi-column text extraction`.

---

## 5. Local Verification & Testing

To ensure code stability and correct parsing rules before creating pull requests:

### 5.1 CPU-only PyTorch Installation
To save local disk space and avoid downloading 2.5 GB of GPU dependencies on your local machine, install the CPU-only version of PyTorch in your virtual environment:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 5.2 Verification Scripts
Run the diagnostic and validation tests locally or inside the backend docker container:
1. **Parser & Rule Heuristics**:
   Validate email stripping, school/certification routing, month discarding, name extraction, and start/end graduation years parsing:
   ```bash
   # Inside backend docker container
   docker exec -it resumefriendly_backend python scratch/verify_parser.py
   ```
2. **Scorer & Embeddings Engine**:
   Validate service layer imports, the 0-100 ATS category scoring, and the Sentence Transformer + ChromaDB matching functionality:
   ```bash
   # Inside backend docker container
   docker exec -it resumefriendly_backend python scratch/verify_backend.py
   ```

