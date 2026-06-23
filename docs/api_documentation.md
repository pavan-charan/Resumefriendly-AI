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

---

## 7. Recruiter Advanced Management APIs (Phase 2)

All recruiter Phase 2 endpoints require a valid JWT token of a user with role `RECRUITER` or `ADMIN` passed in the `Authorization: Bearer <access_token>` header.

### 7.1 Job Openings Management

#### 7.1.1 Get Recruiter Jobs Stats
- **Endpoint**: `/api/v1/jobs/stats`
- **Method**: `GET`
- **Response Body** (`200 OK`):
  ```json
  {
    "total_jobs": 5,
    "active_jobs": 3,
    "draft_jobs": 2,
    "total_candidates": 42
  }
  ```

#### 7.1.2 Create a Job Opening
- **Endpoint**: `/api/v1/jobs`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "title": "Senior Backend Developer",
    "department": "Engineering",
    "employment_type": "Full-time",
    "experience_required": "5+ years",
    "location": "Remote",
    "salary_range": "$130k - $160k",
    "description": "We are seeking a senior FastAPI/Python developer...",
    "skills_required": ["Python", "FastAPI", "PostgreSQL"],
    "skills_preferred": ["Docker", "AWS", "Kubernetes"]
  }
  ```
- **Response Body** (`201 Created`):
  ```json
  {
    "id": "e988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "title": "Senior Backend Developer",
    "status": "Active",
    "created_at": "2026-06-23T12:00:00Z"
  }
  ```

#### 7.1.3 List All Jobs
- **Endpoint**: `/api/v1/jobs`
- **Method**: `GET`
- **Query Parameters**:
  - `status`: Optional filter (e.g. `Active`, `Draft`, `Closed`)
- **Response Body** (`200 OK`):
  ```json
  [
    {
      "id": "e988d5e0-ff1e-450f-a9db-ef4e0a75f850",
      "title": "Senior Backend Developer",
      "department": "Engineering",
      "employment_type": "Full-time",
      "experience_required": "5+ years",
      "location": "Remote",
      "salary_range": "$130k - $160k",
      "description": "...",
      "status": "Active",
      "created_at": "2026-06-23T12:00:00Z"
    }
  ]
  ```

---

### 7.2 Kanban Pipeline & Movements

#### 7.2.1 Retrieve Candidates Mapped to Job Pipeline
- **Endpoint**: `/api/v1/pipeline/{job_id}`
- **Method**: `GET`
- **Query Parameters**:
  - `stage`: Optional stage filter (e.g. `Applied`, `Shortlisted`)
  - `min_score`: Optional minimum score filter
  - `search`: Optional query text string filtering candidate names or skills
- **Response Body** (`200 OK`):
  ```json
  [
    {
      "id": "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
      "job_id": "e988d5e0-ff1e-450f-a9db-ef4e0a75f850",
      "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064",
      "stage": "Applied",
      "ats_score": 85,
      "jd_match_score": 90,
      "candidate_name": "Jane Doe",
      "email": "jane.doe@example.com",
      "phone": "+1-555-0199",
      "skills": ["Python", "FastAPI", "Docker"],
      "education": "Master of Computer Science at State University",
      "experience": "Software Engineer at Tech Solutions",
      "created_at": "2026-06-23T12:10:00Z"
    }
  ]
  ```

#### 7.2.2 Move Candidate to New Pipeline Stage
- **Endpoint**: `/api/v1/pipeline/move`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "pipeline_id": "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "to_stage": "Shortlisted",
    "notes": "Excellent experience fits standard backend criteria."
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "id": "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "stage": "Shortlisted",
    "updated_at": "2026-06-23T12:20:00Z"
  }
  ```

#### 7.2.3 Fetch Candidate Activity Timeline Logs
- **Endpoint**: `/api/v1/pipeline/{pipeline_id}/timeline`
- **Method**: `GET`
- **Response Body** (`200 OK`):
  ```json
  [
    {
      "type": "stage_change",
      "title": "Moved to Shortlisted",
      "description": "Notes: Excellent experience fits standard backend criteria.",
      "timestamp": "2026-06-23T12:20:00Z",
      "user_name": "Sarah Recruiter"
    }
  ]
  ```

---

### 7.3 Advanced Candidates Search

#### 7.3.1 Search talent database profiles
- **Endpoint**: `/api/v1/candidates/search`
- **Method**: `GET`
- **Query Parameters**:
  - `job_id`: Optional filter to search within a specific job
  - `query`: Optional string match in candidate name, email, or skills
  - `skills`: Optional comma-separated list of exact skills required
  - `min_experience`: Optional minimum experience in years
  - `max_experience`: Optional maximum experience in years
  - `location`: Optional string matching location indicators
  - `min_ats`: Optional minimum ATS score
  - `min_jd_match`: Optional minimum Job Description match score
  - `sort_by`: Optional sort field: `best_match` (default), `highest_ats`, `most_experience`, `recent`
- **Response Body** (`200 OK`):
  ```json
  [
    {
      "pipeline_id": "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
      "job_id": "e988d5e0-ff1e-450f-a9db-ef4e0a75f850",
      "candidate_name": "Jane Doe",
      "email": "jane.doe@example.com",
      "stage": "Shortlisted",
      "ats_score": 85,
      "jd_match_score": 90,
      "skills": ["Python", "FastAPI", "Docker"]
    }
  ]
  ```

---

### 7.4 Multi-Candidate Comparisons & Interview Kits

#### 7.4.1 Side-by-Side Comparison Analysis
- **Endpoint**: `/api/v1/candidates/compare`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "job_id": "e988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "pipeline_ids": [
      "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
      "c1f7a064-bc5a-4ea0-e448-bd541f71a111"
    ]
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "id": "f8d8d5e0-ff1e-450f-a9db-ef4e0a75f990",
    "comparison_matrix": [
      {
        "candidate_name": "Jane Doe",
        "skills": ["Python", "FastAPI", "Docker"],
        "experience": "Backend Engineer (3 years)",
        "education": "Master of Computer Science"
      }
    ],
    "ai_summary": "Both candidates demonstrate strong technical proficiency, but Jane Doe possesses directly aligned FastAPI experience...",
    "best_candidate_recommendation": "Recommend advancing Jane Doe to the technical round interview."
  }
  ```

#### 7.4.2 Generate Structured Interview Kit
- **Endpoint**: `/api/v1/interview-kit/generate`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "job_id": "e988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "resume_id": "bfd6b6e4-4ea0-4e78-bc5a-bd541f71a064"
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "id": "e1f7a064-bc5a-4ea0-e448-bd541f71a888",
    "technical_questions": [
      {
        "question": "How do you handle background tasks in FastAPI?",
        "expected_answer": "Interviewer should look for references to BackgroundTasks or Celery."
      }
    ],
    "behavioral_questions": [],
    "scenario_questions": [],
    "role_specific_questions": [],
    "evaluation_rubric": "Score candidates on a scale of 1-5 across coding depth and deployment familiarity.",
    "scoring_template": "1: Unfamiliar, 3: Intermediate, 5: Expert level design.",
    "interviewer_notes": "Pay attention to experience managing Docker production builds."
  }
  ```

---

### 7.5 Collaborations & Analytics

#### 7.5.1 Add Candidate Comment (Note)
- **Endpoint**: `/api/v1/notes`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "pipeline_id": "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "content": "Candidate has cleared initial recruiter chat."
  }
  ```
- **Response Body** (`201 Created`):
  ```json
  {
    "id": "b1f7a064-bc5a-4ea0-e448-bd541f71a441",
    "recruiter_name": "Sarah Recruiter",
    "content": "Candidate has cleared initial recruiter chat.",
    "created_at": "2026-06-23T12:30:00Z"
  }
  ```

#### 7.5.2 Get Notes for Candidate
- **Endpoint**: `/api/v1/notes/{candidate_id}`
- **Method**: `GET`
- **Response Body** (`200 OK`):
  ```json
  [
    {
      "id": "b1f7a064-bc5a-4ea0-e448-bd541f71a441",
      "recruiter_name": "Sarah Recruiter",
      "content": "Candidate has cleared initial recruiter chat.",
      "created_at": "2026-06-23T12:30:00Z"
    }
  ]
  ```

#### 7.5.3 Log Candidate Interview Feedback
- **Endpoint**: `/api/v1/feedback`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "pipeline_id": "a988d5e0-ff1e-450f-a9db-ef4e0a75f850",
    "score": 4,
    "feedback_text": "Strong communication. Answered technical questions cleanly."
  }
  ```
- **Response Body** (`201 Created`):
  ```json
  {
    "id": "c1f7a064-bc5a-4ea0-e448-bd541f71a442",
    "interviewer_name": "Sarah Recruiter",
    "score": 4,
    "feedback_text": "Strong communication. Answered technical questions cleanly.",
    "created_at": "2026-06-23T12:35:00Z"
  }
  ```

#### 7.5.4 Get Recruiter Hiring Funnel Analytics
- **Endpoint**: `/api/v1/analytics/recruiter`
- **Method**: `GET`
- **Response Body** (`200 OK`):
  ```json
  {
    "metrics": {
      "pipeline_conversion_rate": 20.0,
      "average_days_in_pipeline": 12.5,
      "active_jobs_count": 3,
      "total_candidates_tracked": 42
    },
    "stage_distributions": {
      "Applied": 15,
      "Shortlisted": 8,
      "Interview Scheduled": 5,
      "Hired": 2,
      "Rejected": 12
    },
    "funnel_stats": [
      {"stage": "Applied", "count": 42, "percentage": 100},
      {"stage": "Shortlisted", "count": 27, "percentage": 64.2}
    ]
  }
  ```

---

### 7.6 AI Recopilot Assistant Chat

#### 7.6.1 Send Message to Assistant Chat
- **Endpoint**: `/api/v1/recruiter/chat`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "message": "Which candidates have python skills and are ready to interview?",
    "history": [
      {"role": "user", "content": "Hi"},
      {"role": "assistant", "content": "Hello! How can I assist you with your talent pipeline today?"}
    ],
    "selected_job_id": "e988d5e0-ff1e-450f-a9db-ef4e0a75f850"
  }
  ```
- **Response Body** (`200 OK`):
  ```json
  {
    "reply": "Based on the talent pool mapped to Senior Backend Developer: \n\n1. **Jane Doe** has Python skills and is currently in the **Shortlisted** stage. She was moved there by Sarah Recruiter with comments regarding strong FastAPI experience."
  }
  ```


