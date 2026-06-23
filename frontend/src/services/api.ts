const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const getHeaders = (isMultipart = false) => {
  const headers: HeadersInit = {};
  if (!isMultipart) {
    headers["Content-Type"] = "application/json";
  }
  
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
};

export const api = {
  // Authentication
  async register(payload: any) {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Registration failed");
    }
    return response.json();
  },

  async login(credentials: { email: string; password: string }) {
    // OAuth2PasswordRequestForm expects form-urlencoded body
    const formData = new URLSearchParams();
    formData.append("username", credentials.email);
    formData.append("password", credentials.password);

    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    });
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Incorrect email or password");
    }
    return response.json();
  },

  async getMe() {
    const response = await fetch(`${API_URL}/api/v1/auth/me`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Session expired");
    return response.json();
  },

  // Resumes
  async uploadResume(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/api/v1/resumes/upload`, {
      method: "POST",
      headers: getHeaders(true),
      body: formData,
    });
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Failed to upload resume");
    }
    return response.json();
  },

  async getHistory() {
    const response = await fetch(`${API_URL}/api/v1/resumes/history`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load resume list");
    return response.json();
  },

  async getResume(resumeId: string) {
    const response = await fetch(`${API_URL}/api/v1/resumes/${resumeId}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load resume");
    return response.json();
  },

  // ATS Scorings
  async generateATSScore(resumeId: string) {
    const response = await fetch(`${API_URL}/api/v1/ats/score/${resumeId}`, {
      method: "POST",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to run ATS score calculations");
    return response.json();
  },

  async getATSReport(resumeId: string) {
    const response = await fetch(`${API_URL}/api/v1/ats/report/${resumeId}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load ATS scoring details");
    return response.json();
  },

  // JD Matching
  async matchJD(resumeId: string, jdText: string) {
    const response = await fetch(`${API_URL}/api/v1/jds/match`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ resume_id: resumeId, jd_text: jdText }),
    });
    if (!response.ok) throw new Error("Failed to calculate JD matching analysis");
    return response.json();
  },

  // Recruiter Dashboard Screening
  async screenCandidates(payload: {
    jd_title: string;
    company_name: string;
    jd_text: string;
    files: File[];
  }) {
    const formData = new FormData();
    formData.append("jd_title", payload.jd_title);
    formData.append("company_name", payload.company_name);
    formData.append("jd_text", payload.jd_text);
    
    payload.files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await fetch(`${API_URL}/api/v1/recruiter/screen`, {
      method: "POST",
      headers: getHeaders(true),
      body: formData,
    });
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Candidate screening process failed");
    }
    return response.json();
  },

  async getRecruiterJobs() {
    const response = await fetch(`${API_URL}/api/v1/recruiter/jobs`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load recruiter job descriptions");
    return response.json();
  },

  async getJobScreeningResults(jdId: string) {
    const response = await fetch(`${API_URL}/api/v1/recruiter/jobs/${jdId}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load job screening results");
    return response.json();
  },

  // =============================================
  // Phase 2 APIs
  // =============================================

  // AI Resume Rewriter
  async rewriteResume(payload: { resume_id: string; target_role?: string; tone: string; focus_areas: string[] }) {
    const response = await fetch(`${API_URL}/api/v1/rewriter/rewrite`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Resume rewrite failed");
    }
    return response.json();
  },

  async getRewriteVersions(resumeId: string) {
    const response = await fetch(`${API_URL}/api/v1/rewriter/versions/${resumeId}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load rewrite versions");
    return response.json();
  },

  async getRewriteVersion(versionId: string) {
    const response = await fetch(`${API_URL}/api/v1/rewriter/version/${versionId}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load rewrite version");
    return response.json();
  },

  // Interview Preparation
  async startInterview(payload: { resume_id?: string; target_role: string; difficulty: string; question_count: number }) {
    const response = await fetch(`${API_URL}/api/v1/interview/start`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Failed to start interview");
    }
    return response.json();
  },

  async submitInterviewAnswer(questionId: string, answer: string) {
    const response = await fetch(`${API_URL}/api/v1/interview/answer/${questionId}`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ answer }),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Failed to submit answer");
    }
    return response.json();
  },

  async getInterviewSessions() {
    const response = await fetch(`${API_URL}/api/v1/interview/sessions`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load interview sessions");
    return response.json();
  },

  async getInterviewSession(sessionId: string) {
    const response = await fetch(`${API_URL}/api/v1/interview/session/${sessionId}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load interview session");
    return response.json();
  },

  // Skill Gap Analysis
  async analyzeSkillGap(payload: { resume_id?: string; target_role: string }) {
    const response = await fetch(`${API_URL}/api/v1/skills/analyze`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Skill gap analysis failed");
    }
    return response.json();
  },

  async getSkillGapHistory() {
    const response = await fetch(`${API_URL}/api/v1/skills/history`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load skill gap history");
    return response.json();
  },

  // Career Roadmap
  async generateRoadmap(payload: { resume_id?: string; current_role: string; target_role: string; timeline_months: number }) {
    const response = await fetch(`${API_URL}/api/v1/roadmap/generate`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Roadmap generation failed");
    }
    return response.json();
  },

  async getRoadmapHistory() {
    const response = await fetch(`${API_URL}/api/v1/roadmap/history`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load roadmap history");
    return response.json();
  },

  // Application Tracker
  async createApplication(payload: any) {
    const response = await fetch(`${API_URL}/api/v1/tracker/applications`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Failed to create application");
    }
    return response.json();
  },

  async getApplications() {
    const response = await fetch(`${API_URL}/api/v1/tracker/applications`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load applications");
    return response.json();
  },

  async updateApplication(appId: string, payload: { company_name?: string; job_title?: string; job_url?: string; status?: string; applied_date?: string; salary_range?: string; location?: string; notes?: string; next_followup?: string }) {
    const response = await fetch(`${API_URL}/api/v1/tracker/applications/${appId}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Failed to update application");
    }
    return response.json();
  },

  async deleteApplication(appId: string) {
    const response = await fetch(`${API_URL}/api/v1/tracker/applications/${appId}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to delete application");
    return response.json();
  },

  async getTrackerStats() {
    const response = await fetch(`${API_URL}/api/v1/tracker/stats`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load tracker stats");
    return response.json();
  },

  // Job Match Dashboard
  async findJobMatches(payload: { resume_id: string; preferred_roles?: string[]; preferred_locations?: string[] }) {
    const response = await fetch(`${API_URL}/api/v1/jobs/match`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Job matching failed");
    }
    return response.json();
  },

  // AI Career Coach
  async startCoachConversation(payload: { resume_id?: string; title?: string }) {
    const response = await fetch(`${API_URL}/api/v1/coach/conversations`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("Failed to start conversation");
    return response.json();
  },

  async sendCoachMessage(conversationId: string, message: string) {
    const response = await fetch(`${API_URL}/api/v1/coach/conversations/${conversationId}/chat`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ message }),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Chat failed");
    }
    return response.json();
  },

  async getCoachConversations() {
    const response = await fetch(`${API_URL}/api/v1/coach/conversations`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load conversations");
    return response.json();
  },

  async getCoachConversation(conversationId: string) {
    const response = await fetch(`${API_URL}/api/v1/coach/conversations/${conversationId}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to load conversation");
    return response.json();
  },
};
