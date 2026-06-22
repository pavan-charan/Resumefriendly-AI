# API Documentation - ResumeFriendly AI

This document catalogs the REST API endpoints exposed by the FastAPI backend, detailing query structures, JSON payloads, responses, and error handling.

---

## 1. Authentication APIs

### 1.1 Register
Create a new user account.
- **Endpoint**: `/api/v1/auth/register`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "candidate@resumefriendly.ai",
    "password": "SecurePassword123",
    "first_name": "Alex",
    "last_name": "Smith",
    "role": "CANDIDATE"
  }
  ```
- **Response Body** (`201 Created`):
  ```json
  {
    "id": "e2f1f0a1-77a8-48b4-a212-32bca5368a51",
    "email": "candidate@resumefriendly.ai",
    "first_name": "Alex",
    "last_name": "Smith",
    "role": "CANDIDATE",
    "created_at": "2026-06-22T16:21:00Z"
  }
  ```
- **Errors**:
  - `400 Bad Request` if email is already registered.
  - `422 Unprocessable Entity` for invalid email format.

### 1.2 Login
Authenticate credentials and issue authorization tokens.
- **Endpoint**: `/api/v1/auth/login`
- **Method**: `POST`
- **Request Form (OAuth2 Compatible)**:
  - `username`: `candidate@resumefriendly.ai`
  - `password`: `SecurePassword123`
- **Response Body** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user": {
      "id": "e2f1f0a1-77a8-48b4-a212-32bca5368a51",
      "email": "candidate@resumefriendly.ai",
      "role": "CANDIDATE"
    }
  }
  ```
- **Errors**:
  - `401 Unauthorized` for incorrect email or password.

---

## 2. Resume APIs

### 2.1 Upload Resume
Upload and parse a new resume file.
- **Endpoint**: `/api/v1/resumes/upload`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**: `multipart/form-data`
  - `file`: (binary payload of PDF or DOCX file)
- **Response Body** (`201 Created`):
  ```json
  {
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
    "file_name": "Alex_Smith_Resume.pdf",
    "parsed_content": {
      "name": "Alex Smith",
      "email": "alex.smith@example.com",
      "phone": "+1-555-0199",
      "skills": ["React", "TypeScript", "Node.js", "Python", "Docker"],
      "experience": [
        {
          "role": "Software Engineer",
          "company": "Tech Solutions Inc",
          "duration": "2 years",
          "description": "Developed cloud native applications using React and Docker."
        }
      ],
      "education": [
        {
          "degree": "Bachelor of Science",
          "major": "Computer Science",
          "school": "State University"
        }
      ],
      "projects": [],
      "certifications": []
    }
  }
  ```
- **Errors**:
  - `400 Bad Request` if file extension is unsupported or file size exceeds limit (10MB).
  - `401 Unauthorized` if token is missing or expired.

---

## 3. ATS Analysis APIs

### 3.1 Generate ATS Score
Calculate ATS score metrics for a previously parsed resume.
- **Endpoint**: `/api/v1/ats/score/{resume_id}`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response Body** (`200 OK`):
  ```json
  {
    "overall_score": 75,
    "breakdown": {
      "skills": 24,
      "keywords": 12,
      "experience": 15,
      "formatting": 10,
      "education": 10,
      "contact_info": 4
    },
    "explainability": {
      "missing_keywords": ["Kubernetes", "AWS", "CI/CD"],
      "missing_sections": ["Projects"],
      "formatting_issues": ["No layout issues detected. Resume text read cleanly."],
      "weak_content_areas": ["Quantify achievements in Tech Solutions role (add metrics)."],
      "strengths": ["Solid educational foundation", "Complete contact details"]
    }
  }
  ```

---

## 4. Job Description Matching APIs

### 4.1 Match Resume
Compute matching statistics between a resume and a Job Description.
- **Endpoint**: `/api/v1/jds/match`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
    "jd_text": "We are seeking a Software Engineer with experience in React, Python, Docker, AWS, and Kubernetes to build API engines..."
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "match_score": 78,
    "matched_skills": ["React", "Python", "Docker"],
    "missing_skills": ["AWS", "Kubernetes"],
    "recommendations": [
      "Add direct experience with AWS deployments",
      "Mention container orchestration using Kubernetes or ECS"
    ]
  }
  ```

---

## 5. Recruiter APIs

### 5.1 Upload Multiple Resumes
Upload and screen multiple candidates at once against a JD.
- **Endpoint**: `/api/v1/recruiter/screen`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**: `multipart/form-data`
  - `jd_title`: "Senior Python Engineer"
  - `company_name`: "Innovate Corp"
  - `jd_text`: "Required experience in FastAPI, PostgreSQL, and Sentence Transformers..."
  - `files`: (array of binary resume uploads)
- **Response Body** (`201 Created`):
  ```json
  {
    "job_id": "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "ranked_candidates": [
      {
        "rank": 1,
        "candidate_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "match_score": 92,
        "summary": {
          "skills": ["FastAPI", "PostgreSQL", "ChromaDB", "Python"],
          "experience": "5 years building backend services",
          "education": "Master of Computer Science",
          "match_percentage": 92
        }
      },
      {
        "rank": 2,
        "candidate_name": "Alex Smith",
        "email": "alex.smith@example.com",
        "match_score": 65,
        "summary": {
          "skills": ["React", "Python", "Docker"],
          "experience": "2 years Software Engineer",
          "education": "Bachelor of Computer Science",
          "match_percentage": 65
        }
      }
    ]
  }
  ```
- **Errors**:
  - `403 Forbidden` if logged-in user is not a Recruiter or Admin.
