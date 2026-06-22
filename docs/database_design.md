# Database Design Document - ResumeFriendly AI

This document details the normalized relational database schemas, entity relationship (ER) models, field types, and optimization strategies for the ResumeFriendly AI PostgreSQL backend.

---

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        string role "CANDIDATE | RECRUITER | ADMIN"
        timestamp created_at
        timestamp updated_at
    }

    RESUMES {
        uuid id PK
        uuid user_id FK "References USERS(id)"
        string file_name
        string file_path
        string raw_text
        jsonb parsed_content "JSON structured skills, experience, edu"
        timestamp uploaded_at
    }

    JOB_DESCRIPTIONS {
        uuid id PK
        uuid creator_id FK "References USERS(id)"
        string title
        string company_name
        string department
        string raw_content
        string requirements
        timestamp created_at
    }

    ATS_RESULTS {
        uuid id PK
        uuid resume_id FK "References RESUMES(id)"
        integer overall_score
        integer skills_score
        integer keywords_score
        integer experience_score
        integer formatting_score
        integer education_score
        integer contact_score
        jsonb details "Explainability, missing keywords, recommendations"
        timestamp generated_at
    }

    JD_MATCHES {
        uuid id PK
        uuid resume_id FK "References RESUMES(id)"
        uuid jd_id FK "References JOB_DESCRIPTIONS(id)"
        integer match_score
        jsonb match_details "Matched/missing skills, advice"
        timestamp matched_at
    }

    RECRUITER_UPLOADS {
        uuid id PK
        uuid recruiter_id FK "References USERS(id)"
        uuid jd_id FK "References JOB_DESCRIPTIONS(id)"
        uuid resume_id FK "References RESUMES(id)"
        timestamp uploaded_at
    }

    USERS ||--o{ RESUMES : "uploads"
    USERS ||--o{ JOB_DESCRIPTIONS : "creates"
    USERS ||--o{ RECRUITER_UPLOADS : "batch_uploads"
    RESUMES ||--o| ATS_RESULTS : "analyzed_into"
    RESUMES ||--o{ JD_MATCHES : "scored_against"
    JOB_DESCRIPTIONS ||--o{ JD_MATCHES : "scores"
    JOB_DESCRIPTIONS ||--o{ RECRUITER_UPLOADS : "contains"
    RESUMES ||--o{ RECRUITER_UPLOADS : "uploaded_as"
```

---

## 2. Table Specifications

### 2.1 USERS
Stores accounts, hashed credentials, and platform roles.
- `id`: `UUID` (Primary Key, default: `gen_random_uuid()`)
- `email`: `VARCHAR(255)` (Unique, Not Null, Indexed)
- `password_hash`: `VARCHAR(255)` (Not Null)
- `first_name`: `VARCHAR(100)`
- `last_name`: `VARCHAR(100)`
- `role`: `VARCHAR(50)` (Not Null, default: `'CANDIDATE'`)
- `created_at`: `TIMESTAMP WITH TIME ZONE` (default: `NOW()`)
- `updated_at`: `TIMESTAMP WITH TIME ZONE` (default: `NOW()`)

### 2.2 RESUMES
Metadata and structured representation of candidate resumes.
- `id`: `UUID` (Primary Key)
- `user_id`: `UUID` (Foreign Key -> `USERS(id)`, Nullable for quick/anonymous recruiter uploads)
- `file_name`: `VARCHAR(255)` (Not Null)
- `file_path`: `VARCHAR(512)` (Not Null)
- `raw_text`: `TEXT` (Not Null)
- `parsed_content`: `JSONB` (Not Null - structured data: skills list, experience objects, education details, projects)
- `uploaded_at`: `TIMESTAMP WITH TIME ZONE` (default: `NOW()`)

### 2.3 JOB_DESCRIPTIONS
Job profiles defined by recruiters.
- `id`: `UUID` (Primary Key)
- `creator_id`: `UUID` (Foreign Key -> `USERS(id)`, Not Null)
- `title`: `VARCHAR(255)` (Not Null)
- `company_name`: `VARCHAR(255)` (Not Null)
- `department`: `VARCHAR(255)` (Nullable)
- `raw_content`: `TEXT` (Not Null)
- `requirements`: `TEXT` (Nullable)
- `created_at`: `TIMESTAMP WITH TIME ZONE` (default: `NOW()`)

### 2.4 ATS_RESULTS
ATS score analysis breakdown and optimization alerts.
- `id`: `UUID` (Primary Key)
- `resume_id`: `UUID` (Foreign Key -> `RESUMES(id)`, Cascade Delete, Unique)
- `overall_score`: `INTEGER` (Not Null)
- `skills_score`: `INTEGER` (Not Null)
- `keywords_score`: `INTEGER` (Not Null)
- `experience_score`: `INTEGER` (Not Null)
- `formatting_score`: `INTEGER` (Not Null)
- `education_score`: `INTEGER` (Not Null)
- `contact_score`: `INTEGER` (Not Null)
- `details`: `JSONB` (Not Null - contains lists of: missing keywords, missing sections, formatting issues, content recommendations)
- `generated_at`: `TIMESTAMP WITH TIME ZONE` (default: `NOW()`)

### 2.5 JD_MATCHES
Scores and gaps identified between a candidate's resume and a specific JD.
- `id`: `UUID` (Primary Key)
- `resume_id`: `UUID` (Foreign Key -> `RESUMES(id)`, Cascade Delete)
- `jd_id`: `UUID` (Foreign Key -> `JOB_DESCRIPTIONS(id)`, Cascade Delete)
- `match_score`: `INTEGER` (Not Null)
- `match_details`: `JSONB` (Not Null - matched skills, missing skills, customized optimization feedback)
- `matched_at`: `TIMESTAMP WITH TIME ZONE` (default: `NOW()`)

### 2.6 RECRUITER_UPLOADS
Map of resumes uploaded by recruiters to screen against job specifications.
- `id`: `UUID` (Primary Key)
- `recruiter_id`: `UUID` (Foreign Key -> `USERS(id)`)
- `jd_id`: `UUID` (Foreign Key -> `JOB_DESCRIPTIONS(id)`)
- `resume_id`: `UUID` (Foreign Key -> `RESUMES(id)`)
- `uploaded_at`: `TIMESTAMP WITH TIME ZONE` (default: `NOW()`)

---

## 3. Indexing & Optimization Strategy

To maintain sub-second queries for active dashboards as files and users scale, we define target indexes:

1. **B-Tree Indexes**:
   - `idx_users_email` ON `users(email)`: For fast user lookup at login.
   - `idx_resumes_user_id` ON `resumes(user_id)`: Speeds up fetching history on candidate profiles.
   - `idx_jds_creator_id` ON `job_descriptions(creator_id)`: Speeds up dashboard listings for active recruiters.
   - `idx_jd_matches_lookup` ON `jd_matches(resume_id, jd_id)`: Quick evaluation of historic evaluations.
   - `idx_rec_upload_lookup` ON `recruiter_uploads(recruiter_id, jd_id)`: Quickly lists resumes queued for a job description.

2. **JSONB Indexing**:
   - `idx_resumes_skills` ON `resumes USING gin ((parsed_content -> 'skills'))`: Speeds up custom recruiter searches filtering resumes by exact skill tags.
