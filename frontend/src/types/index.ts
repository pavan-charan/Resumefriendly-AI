export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: "CANDIDATE" | "RECRUITER" | "ADMIN";
  created_at: string;
}

export interface ExperienceItem {
  role?: string;
  company?: string;
  duration?: string;
  description?: string;
}

export interface EducationItem {
  degree?: string;
  major?: string;
  school?: string;
  grad_year?: string;
  graduation_start_year?: string;
  graduation_end_year?: string;
}

export interface ParsedResumeContent {
  name?: string;
  email?: string;
  phone?: string;
  skills: string[];
  experience: ExperienceItem[];
  education: EducationItem[];
  projects: string[];
  certifications: string[];
}

export interface Resume {
  id: string;
  user_id?: string;
  file_name: string;
  file_path: string;
  parsed_content: ParsedResumeContent;
  uploaded_at: string;
}

export interface ATSScoreBreakdown {
  skills: number;
  keywords: number;
  experience: number;
  formatting: number;
  education: number;
  contact_info: number;
}

export interface ATSScoreExplainability {
  missing_keywords: string[];
  missing_sections: string[];
  formatting_issues: string[];
  weak_content_areas: string[];
  strengths: string[];
}

export interface ATSReport {
  overall_score: number;
  breakdown: ATSScoreBreakdown;
  explainability: ATSScoreExplainability;
}

export interface JDMatch {
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  recommendations: string[];
}

export interface CandidateSummary {
  skills: string[];
  experience: string;
  education: string;
  college_name?: string;
  graduation_year?: string;
  graduation_start_year?: string;
  graduation_end_year?: string;
  match_percentage: number;
}

export interface RankedCandidate {
  rank: number;
  candidate_name: string;
  email: string;
  match_score: number;
  summary: CandidateSummary;
}

export interface RecruiterScreenResult {
  job_id: string;
  ranked_candidates: RankedCandidate[];
}
