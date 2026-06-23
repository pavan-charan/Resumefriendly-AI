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

---

## 6. Career Growth Platform APIs (Phase 2)

All Phase 2 endpoints require a valid JWT Candidate token passed in the `Authorization: Bearer <access_token>` header.

### 6.1 AI Resume Rewriter

#### 6.1.1 Rewrite Resume Sections
- **Endpoint**: `/api/v1/rewriter/rewrite`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
    "target_role": "Senior Full-Stack Engineer",
    "tone": "executive",
    "focus_areas": ["Quantify experience", "Highlight system architecture"]
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "version_id": "c1f7a064-bc5a-4ea0-e448-bd541f71a111",
    "version_number": 1,
    "original": {
      "summary": "Full Stack developer with React and Node.",
      "experience": ["Developed web apps."]
    },
    "rewritten": {
      "summary": "Results-driven Senior Full-Stack Engineer with 5+ years driving web architectures...",
      "experience": ["Architected scalable applications using React, boosting response times by 30%."]
    },
    "improvements": [
      "Transformed summary to executive tone focusing on leadership metrics.",
      "Quantified first experience bullet point with exact percentages."
    ]
  }
  ```

#### 6.1.2 Get Version History
- **Endpoint**: `/api/v1/rewriter/versions/{resume_id}`
- **Method**: `GET`
- **Response Body** (`200 OK`):
  ```json
  [
    {
      "id": "c1f7a064-bc5a-4ea0-e448-bd541f71a111",
      "version_number": 1,
      "target_role": "Senior Full-Stack Engineer",
      "tone": "executive",
      "created_at": "2026-06-23T11:00:00Z"
    }
  ]
  ```

---

### 6.2 Interview Preparation Engine

#### 6.2.1 Start Mock Interview Session
- **Endpoint**: `/api/v1/interview/start`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
    "target_role": "Senior Full-Stack Engineer",
    "difficulty": "hard",
    "question_count": 3
  }
  ```
- **Response Body** (`201 Created`):
  ```json
  {
    "session_id": "d2f1f0a1-77a8-48b4-a212-32bca5368a62",
    "target_role": "Senior Full-Stack Engineer",
    "difficulty": "hard",
    "questions": [
      {
        "id": "e3f1f0a1-77a8-48b4-a212-32bca5368a73",
        "question_text": "Tell me about a time you had to optimize a slow database query in a production environment.",
        "category": "technical"
      }
    ]
  }
  ```

#### 6.2.2 Submit Mock Answer for Evaluation
- **Endpoint**: `/api/v1/interview/answer/{question_id}`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "user_answer": "I noticed our Postgres CPU utilization was spiking. I ran EXPLAIN ANALYZE on our active collections..."
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "score": 9,
    "ai_feedback": {
      "strengths": "Clear application of the STAR method. Good technical depth regarding Postgres explain tools.",
      "improvements": "Provide exact latency numbers in the 'Result' phase.",
      "star_rating": {
        "situation": "Excellent context regarding CPU load.",
        "task": "Identified query constraints.",
        "action": "Ran optimization analyses and indexes.",
        "result": "Resolved spike but lacked metrics."
      }
    }
  }
  ```

---

### 6.3 Skill Gap Analysis

#### 6.3.1 Analyze Competencies and Gaps
- **Endpoint**: `/api/v1/skills/analyze`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
    "target_role": "Senior Full-Stack Engineer"
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "id": "a1f7a064-bc5a-4ea0-e448-bd541f71a222",
    "target_role": "Senior Full-Stack Engineer",
    "overall_readiness": 70,
    "current_skills": [
      {"name": "React", "level": "expert"},
      {"name": "Python", "level": "intermediate"}
    ],
    "missing_skills": ["Kubernetes", "AWS CloudFormation"],
    "recommendations": [
      {
        "skill": "Kubernetes",
        "priority": "high",
        "resources": ["CKA Certification Guide on Udemy", "Kubernetes Official Docs"]
      }
    ],
    "created_at": "2026-06-23T11:00:00Z"
  }
  ```

---

### 6.4 Career Roadmap Generator

#### 6.4.1 Generate Progression Roadmap
- **Endpoint**: `/api/v1/roadmap/generate`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
    "current_role": "Software Engineer",
    "target_role": "Engineering Manager",
    "timeline_months": 12
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "id": "b1f7a064-bc5a-4ea0-e448-bd541f71a333",
    "current_role": "Software Engineer",
    "target_role": "Engineering Manager",
    "timeline_months": 12,
    "milestones": [
      {
        "phase": "Months 1-3: Technical Leadership",
        "objectives": ["Mentor junior devs", "Lead architecture reviews"],
        "certifications": ["AWS Certified Solutions Architect"]
      }
    ],
    "created_at": "2026-06-23T11:00:00Z"
  }
  ```

---

### 6.5 Application Tracker

#### 6.5.1 Create Job Application Record
- **Endpoint**: `/api/v1/tracker/applications`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "company_name": "Google",
    "job_title": "Senior Engineer",
    "job_url": "https://careers.google.com/jobs/...",
    "status": "applied",
    "applied_date": "2026-06-23",
    "salary_range": "$150k - $180k",
    "notes": "Referred by Alex."
  }
  ```
- **Response Body** (`201 Created`):
  ```json
  {
    "id": "e1f7a064-bc5a-4ea0-e448-bd541f71a444",
    "company_name": "Google",
    "job_title": "Senior Engineer",
    "status": "applied",
    "created_at": "2026-06-23T11:00:00Z"
  }
  ```

#### 6.5.2 Update Application Status
- **Endpoint**: `/api/v1/tracker/applications/{id}`
- **Method**: `PUT`
- **Request Body**:
  ```json
  {
    "status": "interviewing",
    "notes": "Completed initial recruiter phone screen successfully."
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "id": "e1f7a064-bc5a-4ea0-e448-bd541f71a444",
    "status": "interviewing",
    "updated_at": "2026-06-23T11:15:00Z"
  }
  ```

#### 6.5.3 Fetch Status Distributions
- **Endpoint**: `/api/v1/tracker/stats`
- **Method**: `GET`
- **Response Body** (`200 OK`):
  ```json
  {
    "applied": 12,
    "screening": 4,
    "interviewing": 2,
    "offer": 1,
    "rejected": 5,
    "accepted": 0
  }
  ```

---

### 6.6 AI Career Coach

#### 6.6.1 Start Coaching Thread
- **Endpoint**: `/api/v1/coach/conversations`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
    "title": "Transitioning to Management"
  }
  ```
- **Response Body** (`201 Created`):
  ```json
  {
    "conversation_id": "f1f7a064-bc5a-4ea0-e448-bd541f71a555",
    "title": "Transitioning to Management",
    "created_at": "2026-06-23T11:00:00Z"
  }
  ```

#### 6.6.2 Send Chat Message
- **Endpoint**: `/api/v1/coach/conversations/{conversation_id}/chat`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "content": "What certifications would look best for moving into management?"
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "response": "Given your resume showing 5 years as a Software Engineer, the best certifications to target would be Scrum Master (CSM) or PMP..."
  }
  ```

