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

  async login(credentials: { email: string; password: str }) {
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
};
