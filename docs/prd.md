# Product Requirements Document (PRD) - ResumeFriendly AI

## 1. Product Vision
ResumeFriendly AI (ResumeFlow AI) is a next-generation, AI-powered hiring intelligence and applicant tracking system (ATS) optimization platform. It bridges the gap between Job Candidates trying to optimize their resumes for modern screening systems, and Recruiters trying to parse, screen, rank, and summarize large volume resume submissions instantly and accurately.

---

## 2. Problem Statement
The hiring ecosystem suffers from two primary issues:
1. **The Candidate Dilemma**: Traditional Applicant Tracking Systems filter out up to 75% of qualified candidates due to simple formatting anomalies, missing standard keywords, or poorly optimized sections, leaving candidates blind to why their applications were rejected.
2. **The Recruiter Bottleneck**: Recruiters spend hours scanning hundreds of resumes per job opening. Simple keyword matching fails to capture semantic relevance, leading to poor candidate selection, manual bias, and excessive time-to-hire.

---

## 3. User Personas

### Persona A: Alex, The Job Seeker (Candidate)
- **Role**: Software Engineer looking for a new role.
- **Pain Points**: Rejects without feedback; doesn't know if their resume matches ATS algorithms; lacks clarity on how to highlight relevant experience for specific roles.
- **Needs**: Instant feedback on resume structure, score breakdown, actionable suggestions, and a quick way to simulate matching against a target Job Description.

### Persona B: Sarah, The Talent Acquisition Lead (Recruiter)
- **Role**: HR Lead at a scaling startup.
- **Pain Points**: Receives 300+ resumes per job post; struggles to organize, screen, and compare candidates; spends hours writing summaries for hiring managers.
- **Needs**: Simple dashboard to define a JD, drop multiple resumes, obtain a ranked order of candidates with high-quality profiles, and read automated generated summaries instantly.

---

## 4. Feature Specifications

### 4.1 Candidate Features
- **Authentication**: JWT-based secure sign-up, sign-in, and session refresh.
- **Resume Upload**: Upload PDF and DOCX files. Files are parsed securely and cached in local storage.
- **Resume Parsing**: AI-powered scanner extracts Name, Email, Phone, Skills, Experience, Education, Projects, and Certifications.
- **ATS Score Engine**: Generates a score out of 100 based on standard industry weighting:
  - *Skills*: 30%
  - *Keywords*: 20%
  - *Experience*: 20%
  - *Formatting*: 15%
  - *Education*: 10%
  - *Contact Info*: 5%
- **ATS Explainability**: Provides exact reasons for the score, listing missing keywords, missing sections, and structural issues.
- **JD Matching**: Candidates paste a target Job Description and receive a matching score, list of matching/missing skills, and custom optimization advice.
- **Actionable Recommendations**: High-impact resume changes (e.g., adding metrics, rewriting weak summaries, inserting tools like AWS, Docker).

### 4.2 Recruiter Features
- **Job Description Upload**: Dashboard panel to submit Job Title, Company, and Job Description text.
- **Multi-Resume Upload**: Drag-and-drop area to upload multiple candidate resumes (PDF/DOCX) in a single batch.
- **Ranked Candidates List**: Ranks the batch based on semantic similarity to the Job Description, displaying name, score, and contact details.
- **Candidate Summary Generator**: Extracts highlights of experience, key skills, education, and match statistics in an easy-to-read recruiter profile card.

---

## 5. User Flows

### Candidate Flow
1. Register/Login -> Candidate Dashboard.
2. Drag-and-drop resume -> File parsed and analyzed.
3. View ATS report: score gauge, structural logs, formatting issues, and skills list.
4. Input JD in "JD Matcher" tab -> View semantic similarity score, matched skills, missing skills, and detailed advice on updating the resume.

### Recruiter Flow
1. Register/Login -> Select role "Recruiter" -> Recruiter Dashboard.
2. Click "Create Job Post" -> Enter details and JD text.
3. Drag-and-drop 10+ resumes -> Backend processes files, computes embeddings, index in ChromaDB.
4. View Ranked List -> Order by Cosine Similarity.
5. Click Candidate name -> View detailed Candidate Summary (Skills, Experience years, education background, score).

---

## 6. Success Metrics (KPIs)
- **Parser Accuracy**: >95% correct identification of contact information and core skills on standard formatting.
- **Analysis Latency**: Scoring and explainability returned in under 3 seconds per resume.
- **Candidate Matching Speed**: Under 10 seconds for batch-matching of 20 resumes.
- **User Engagement**: Low friction navigation, clean dashboard visualization, and 90%+ intuitive scoring report comprehension.
