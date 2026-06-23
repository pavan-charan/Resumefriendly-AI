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

// =============================================
// Phase 2 Types
// =============================================

// AI Resume Rewriter
export interface RewriteRequest {
  resume_id: string;
  target_role?: string;
  tone: "professional" | "creative" | "executive" | "technical";
  focus_areas: string[];
}

export interface RewriteVersion {
  version_id: string;
  version_number: number;
  original: ParsedResumeContent;
  rewritten: Record<string, any>;
  improvements: string[];
  target_role?: string;
  tone: string;
  created_at: string;
}

export interface VersionListItem {
  id: string;
  version_number: number;
  target_role?: string;
  tone: string;
  created_at: string;
}

// Interview Preparation
export interface InterviewQuestion {
  id: string;
  question_text: string;
  category: string;
  user_answer?: string;
  ai_feedback?: {
    score: number;
    strengths: string[];
    improvements: string[];
    sample_answer?: string;
  };
  score?: number;
}

export interface InterviewSession {
  id: string;
  target_role: string;
  difficulty: string;
  total_score?: number;
  questions: InterviewQuestion[];
  created_at: string;
}

export interface InterviewSessionListItem {
  id: string;
  target_role: string;
  difficulty: string;
  total_score?: number;
  question_count: number;
  created_at: string;
}

// Skill Gap Analysis
export interface SkillItem {
  name: string;
  proficiency: number;
}

export interface MissingSkillItem {
  name: string;
  importance: "critical" | "important" | "nice-to-have";
  resources: string[];
}

export interface SkillGapResult {
  id: string;
  target_role: string;
  current_skills: SkillItem[];
  missing_skills: MissingSkillItem[];
  overall_readiness: number;
  recommendations: string[];
  created_at: string;
}

// Career Roadmap
export interface RoadmapPhase {
  phase_name: string;
  duration_months: number;
  milestones: string[];
  skills_to_learn: string[];
  resources: string[];
}

export interface CertificationItem {
  name: string;
  provider: string;
  estimated_time: string;
}

export interface CareerRoadmap {
  id: string;
  current_role: string;
  target_role: string;
  timeline_months: number;
  phases: RoadmapPhase[];
  certifications: CertificationItem[];
  target_companies: string[];
  salary_progression: Record<string, string>;
  created_at: string;
}

// Application Tracker
export interface JobApplicationData {
  id: string;
  company_name: string;
  job_title: string;
  job_url?: string;
  status: string;
  applied_date?: string;
  salary_range?: string;
  location?: string;
  notes?: string;
  next_followup?: string;
  created_at: string;
  updated_at: string;
}

export interface TrackerStats {
  total: number;
  applied: number;
  screening: number;
  interviewing: number;
  offer: number;
  rejected: number;
  accepted: number;
  withdrawn: number;
}

// Job Match Dashboard
export interface JobMatchItem {
  job_id: string;
  title: string;
  company_name: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
}

export interface JobMatchResult {
  matches: JobMatchItem[];
  total_jobs_scanned: number;
}

// AI Career Coach
export interface CoachMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface CoachConversation {
  id: string;
  title: string;
  messages: CoachMessage[];
  created_at: string;
  updated_at: string;
}

export interface CoachConversationListItem {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}
