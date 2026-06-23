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

### 4.2 Recruiter Features (Phase 1)
- **Job Description Upload**: Dashboard panel to submit Job Title, Company, and Job Description text.
- **Multi-Resume Upload**: Drag-and-drop area to upload multiple candidate resumes (PDF/DOCX) in a single batch.
- **Ranked Candidates List**: Ranks the batch based on semantic similarity to the Job Description, displaying name, score, and contact details.
- **Candidate Summary Generator**: Extracts highlights of experience, key skills, education, and match statistics in an easy-to-read recruiter profile card.

### 4.3 Recruiter Management Platform (Phase 2)
- **Job Openings Management**: Configure comprehensive job profiles (title, employment type, location, experience requirements, salary range, description) and specify required and preferred skills. Collaborate with other team members (recruiters, hiring managers).
- **Kanban Hiring Pipeline**: Track candidates across standard hiring stages (Applied, Screening, Shortlisted, Interview Scheduled, Technical Round, Manager Round, HR Round, Offer, Hired, Rejected). Automatically record movement timestamps and Stage Transition Histories.
- **Advanced Candidate Search**: Search and filter candidate database profiles using parameters like skills, years of experience, locations, minimum ATS scores, and minimum JD match values.
- **Candidate Comparisons**: Cross-evaluate and compare selected candidates side-by-side on skills, experience highlights, and educational backgrounds, supplemented by AI-generated comparison summaries and recommendations.
- **Structured Interview Kits**: Automatically generate candidate-specific and job-tailored interview kits, including behavioral, technical, scenario, and role-specific questions, evaluation rubrics, and print-ready templates.
- **Collaboration & Logs**: Log recruiter notes and candidate feedback metrics. Audit user activity logs (`activity_logs`) across operations like job creation, pipeline progression updates, and notes attachments.
- **Recruiter Hiring Analytics**: Monitor aggregate metrics, pipeline conversion rates, active jobs counts, total candidate count, and visual SVG charts showing stage conversions and funnel statistics.
- **AI Recopilot Chat Assistant**: An interactive assistant loaded with job requirements and candidate profiles context, facilitating natural language queries to retrieve, filter, and review profiles.

### 4.4 Candidate Career Growth Platform (Phase 2)
- **AI Resume Rewriter**: Enhances parsed sections (summaries, bullet points) using LLMs with customizable tones (Professional, Executive, Technical, Creative) and focus areas, persisting versions.
- **Interview Prep Engine**: Generates role-specific behavioral, technical, and situational mock interview questions and rates candidate answers on a 0-10 scale using the STAR (Situation, Task, Action, Result) method.
- **Skill Gap Analysis**: Compares candidate's skills against industry standards for target roles, assessing proficiency level gaps, readiness scores, and learning resources.
- **Career Roadmap Generator**: Creates interactive milestone-based career progression roadmaps based on timeline choices (months) and target roles.
- **Job Application Tracker**: Full CRUD dashboard tracking application pipelines across Kanban status lanes (Applied, Screening, Interviewing, Offer, Rejected, Accepted).
- **Job Match Dashboard**: Matches candidate profiles against live recruiter jobs using ChromaDB vector database index.
- **AI Career Coach**: A persistent conversational chatbot assistant loaded with candidate profile context to deliver customized career coaching.

---

## 5. User Flows

### Candidate Flow
1. Register/Login -> Candidate Dashboard.
2. Drag-and-drop resume -> File parsed and analyzed.
3. View ATS report: score gauge, structural logs, formatting issues, and skills list.
4. Input JD in "JD Matcher" tab -> View semantic similarity score, matched skills, missing skills, and detailed advice on updating the resume.
5. Access Career Platform Tabs:
   - **Rewriter**: Select tone, request AI rewrite, view diffs, and save new versions.
   - **Interview Prep**: Choose target role, practice QA session, and review AI STAR feedback.
   - **Skill Gap**: Run analysis against target roles to identify missing competencies and training resources.
   - **Roadmap**: Generate a visual career path with milestone timelines.
   - **Tracker**: Log, edit, and move job application entries across lanes.
   - **Job Match**: View ranked matches from recruiter job posts with compatibility scores.
   - **Career Coach**: Chat with the conversational AI assistant loaded with resume context.

### Recruiter Flow
1. Register/Login -> Select role "Recruiter" -> Recruiter Dashboard.
2. **Job Post Management**: Click "Create Job Post" -> Enter full configurations (title, location, salary, required/preferred skills, etc.) -> Saved in `jobs` database table.
3. **Pipeline Board**: Drag-and-drop resumes into a job to parse them and automatically add candidates to the Kanban board (`Applied` stage).
4. **Kanban Pipeline Operations**: Move candidate cards across stages (Applied, Screening, Shortlisted, Interview Scheduled, etc.). Click a candidate to open their detail drawer, showing timeline transition logs, attaching notes, and recording interview feedback scores.
5. **Talent Search**: Navigate to "Talent Search" -> Query the database by candidate name, skills, location, or match scores to find fitting profiles.
6. **Candidate Comparisons**: Select up to 3 candidates -> Click "Compare Candidates" -> View side-by-side matrices and AI evaluations.
7. **Interview Kits**: Click "Generate Interview Kit" on a candidate profile -> AI generates tailored questions and evaluation templates. Click "Print" to export to physical or PDF formats.
8. **Hiring Analytics**: Check the "Analytics" tab to inspect aggregate performance, funnel conversion charts, and activity streams.
9. **Recopilot Chat**: Ask the AI Recopilot overlay (e.g., "Summarize the top candidate for this role") for instant hiring answers.
10. Click "Export CSV" -> Download ranked CSV records of all candidate profiles.

---

## 6. Success Metrics (KPIs)
- **Parser Accuracy**: >95% correct identification of contact information, schools, years, and core skills on standard formatting.
- **Analysis Latency**: Scoring and explainability returned in under 3 seconds per resume.
- **Candidate Matching Speed**: Under 10 seconds for batch-matching of 20 resumes.
- **AI Response Latency**: Core LLM generations (coaching, rewriting, roadmap, etc.) returned in under 5 seconds.
- **User Engagement**: Low friction navigation, clean dashboard visualization, and 90%+ intuitive scoring report comprehension.

