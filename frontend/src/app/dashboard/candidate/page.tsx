"use client";

import { useEffect, useState, Suspense } from "react";
import { api } from "@/services/api";
import { Resume, ATSReport, JDMatch, RewriteVersion, InterviewSession, InterviewQuestion, SkillGapResult, CareerRoadmap, JobApplicationData, TrackerStats, JobMatchResult, CoachConversation, CoachConversationListItem, CoachMessage as CoachMessageType } from "@/types";
import { 
  Upload, FileText, Activity, AlertTriangle, CheckCircle, 
  Sparkles, Code, ChevronRight, HelpCircle, ArrowRight, Loader2, ListFilter,
  PenTool, MessageSquare, BarChart3, Map, ClipboardList, Briefcase, Bot,
  Send, Plus, Trash2, ExternalLink, Target, BookOpen, Award, TrendingUp,
  ChevronDown, Star, Clock, Calendar
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useSearchParams } from "next/navigation";

type TabKey = "ats" | "jd" | "rewriter" | "interview" | "skills" | "roadmap" | "tracker" | "jobs" | "coach";

function CandidateDashboardContent() {
  const [history, setHistory] = useState<Resume[]>([]);
  const [activeResume, setActiveResume] = useState<Resume | null>(null);
  const [report, setReport] = useState<ATSReport | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>("ats");
  const [uploading, setUploading] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [matching, setMatching] = useState(false);
  
  // JD Match state
  const [jdText, setJdText] = useState("");
  const [matchReport, setMatchReport] = useState<JDMatch | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Phase 2 states
  // Rewriter
  const [rewriting, setRewriting] = useState(false);
  const [rewriteResult, setRewriteResult] = useState<RewriteVersion | null>(null);
  const [rewriteTone, setRewriteTone] = useState("professional");
  const [rewriteRole, setRewriteRole] = useState("");
  // Interview
  const [interviewLoading, setInterviewLoading] = useState(false);
  const [interviewSession, setInterviewSession] = useState<InterviewSession | null>(null);
  const [interviewRole, setInterviewRole] = useState("");
  const [interviewDifficulty, setInterviewDifficulty] = useState("medium");
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [answerLoading, setAnswerLoading] = useState(false);
  const [activeQuestionIdx, setActiveQuestionIdx] = useState(0);
  // Skill Gap
  const [skillGapLoading, setSkillGapLoading] = useState(false);
  const [skillGapResult, setSkillGapResult] = useState<SkillGapResult | null>(null);
  const [skillGapRole, setSkillGapRole] = useState("");
  // Roadmap
  const [roadmapLoading, setRoadmapLoading] = useState(false);
  const [roadmapResult, setRoadmapResult] = useState<CareerRoadmap | null>(null);
  const [roadmapCurrentRole, setRoadmapCurrentRole] = useState("");
  const [roadmapTargetRole, setRoadmapTargetRole] = useState("");
  const [roadmapTimeline, setRoadmapTimeline] = useState(12);
  // Tracker
  const [applications, setApplications] = useState<JobApplicationData[]>([]);
  const [trackerStats, setTrackerStats] = useState<TrackerStats | null>(null);
  const [showAddApp, setShowAddApp] = useState(false);
  const [newApp, setNewApp] = useState({ company_name: "", job_title: "", job_url: "", status: "applied", location: "", salary_range: "", notes: "" });
  // Job Match
  const [jobMatchLoading, setJobMatchLoading] = useState(false);
  const [jobMatchResult, setJobMatchResult] = useState<JobMatchResult | null>(null);
  // Coach
  const [coachConversations, setCoachConversations] = useState<CoachConversationListItem[]>([]);
  const [activeConversation, setActiveConversation] = useState<CoachConversation | null>(null);
  const [coachMessage, setCoachMessage] = useState("");
  const [coachLoading, setCoachLoading] = useState(false);

  const searchParams = useSearchParams();
  const tab = searchParams.get("tab");

  useEffect(() => {
    if (tab && ["ats", "jd", "rewriter", "interview", "skills", "roadmap", "tracker", "jobs", "coach"].includes(tab)) {
      setActiveTab(tab as TabKey);
    }
  }, [tab]);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    if (activeTab === "tracker") loadTracker();
    if (activeTab === "coach") loadCoachConversations();
  }, [activeTab]);

  const loadHistory = async () => {
    try {
      const data = await api.getHistory();
      setHistory(data);
      if (data.length > 0 && !activeResume) {
        handleSelectResume(data[0]);
      }
    } catch (err: any) {
      console.error("Failed to load history:", err);
    }
  };

  const handleSelectResume = async (resume: Resume) => {
    setActiveResume(resume);
    setMatchReport(null);
    setScoring(true);
    try {
      let r: ATSReport;
      try {
        r = await api.getATSReport(resume.id);
      } catch (err) {
        r = await api.generateATSScore(resume.id);
      }
      setReport(r);
    } catch (err: any) {
      console.error("Scoring failed:", err);
    } finally {
      setScoring(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;
    
    setError(null);
    setUploading(true);
    try {
      const result = await api.uploadResume(fileList[0]);
      await loadHistory();
      const freshHistory = await api.getHistory();
      const match = freshHistory.find((r: Resume) => r.id === result.resume_id);
      if (match) {
        await handleSelectResume(match);
      }
    } catch (err: any) {
      setError(err.message || "Failed to process resume file.");
    } finally {
      setUploading(false);
    }
  };

  const handleJDMatch = async () => {
    if (!activeResume || !jdText.trim()) return;
    setMatching(true);
    setError(null);
    try {
      const result = await api.matchJD(activeResume.id, jdText);
      setMatchReport(result);
    } catch (err: any) {
      setError(err.message || "Failed to match job description.");
    } finally {
      setMatching(false);
    }
  };

  // Phase 2 handlers
  const handleRewrite = async () => {
    if (!activeResume) return;
    setRewriting(true);
    try {
      const result = await api.rewriteResume({
        resume_id: activeResume.id,
        target_role: rewriteRole || undefined,
        tone: rewriteTone,
        focus_areas: ["summary", "experience", "skills"],
      });
      setRewriteResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setRewriting(false);
    }
  };

  const handleStartInterview = async () => {
    if (!interviewRole.trim()) return;
    setInterviewLoading(true);
    try {
      const session = await api.startInterview({
        resume_id: activeResume?.id,
        target_role: interviewRole,
        difficulty: interviewDifficulty,
        question_count: 5,
      });
      setInterviewSession(session);
      setActiveQuestionIdx(0);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setInterviewLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!interviewSession || !currentAnswer.trim()) return;
    const question = interviewSession.questions[activeQuestionIdx];
    setAnswerLoading(true);
    try {
      const feedback = await api.submitInterviewAnswer(question.id, currentAnswer);
      const updatedQuestions = [...interviewSession.questions];
      updatedQuestions[activeQuestionIdx] = {
        ...question,
        user_answer: currentAnswer,
        ai_feedback: feedback.feedback,
        score: feedback.score,
      };
      setInterviewSession({ ...interviewSession, questions: updatedQuestions });
      setCurrentAnswer("");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAnswerLoading(false);
    }
  };

  const handleSkillGap = async () => {
    if (!skillGapRole.trim()) return;
    setSkillGapLoading(true);
    try {
      const result = await api.analyzeSkillGap({
        resume_id: activeResume?.id,
        target_role: skillGapRole,
      });
      setSkillGapResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSkillGapLoading(false);
    }
  };

  const handleRoadmap = async () => {
    if (!roadmapCurrentRole.trim() || !roadmapTargetRole.trim()) return;
    setRoadmapLoading(true);
    try {
      const result = await api.generateRoadmap({
        resume_id: activeResume?.id,
        current_role: roadmapCurrentRole,
        target_role: roadmapTargetRole,
        timeline_months: roadmapTimeline,
      });
      setRoadmapResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setRoadmapLoading(false);
    }
  };

  const loadTracker = async () => {
    try {
      const [apps, stats] = await Promise.all([api.getApplications(), api.getTrackerStats()]);
      setApplications(apps);
      setTrackerStats(stats);
    } catch (err: any) {
      console.error("Failed to load tracker:", err);
    }
  };

  const handleAddApplication = async () => {
    try {
      await api.createApplication(newApp);
      setNewApp({ company_name: "", job_title: "", job_url: "", status: "applied", location: "", salary_range: "", notes: "" });
      setShowAddApp(false);
      loadTracker();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDeleteApplication = async (id: string) => {
    try {
      await api.deleteApplication(id);
      loadTracker();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      await api.updateApplication(id, { status });
      loadTracker();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleJobMatch = async () => {
    if (!activeResume) return;
    setJobMatchLoading(true);
    try {
      const result = await api.findJobMatches({ resume_id: activeResume.id });
      setJobMatchResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setJobMatchLoading(false);
    }
  };

  const loadCoachConversations = async () => {
    try {
      const convos = await api.getCoachConversations();
      setCoachConversations(convos);
    } catch (err: any) {
      console.error("Failed to load conversations:", err);
    }
  };

  const handleStartConversation = async () => {
    try {
      const convo = await api.startCoachConversation({ resume_id: activeResume?.id });
      setActiveConversation(convo);
      loadCoachConversations();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleSendCoachMessage = async () => {
    if (!activeConversation || !coachMessage.trim()) return;
    const userMsg = coachMessage;
    setCoachMessage("");
    setCoachLoading(true);
    
    // Optimistic update
    const optimisticMsg = { id: "temp", role: "user" as const, content: userMsg, created_at: new Date().toISOString() };
    setActiveConversation(prev => prev ? { ...prev, messages: [...prev.messages, optimisticMsg] } : prev);
    
    try {
      const aiResponse = await api.sendCoachMessage(activeConversation.id, userMsg);
      // Reload full conversation
      const updated = await api.getCoachConversation(activeConversation.id);
      setActiveConversation(updated);
      loadCoachConversations();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCoachLoading(false);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      const convo = await api.getCoachConversation(id);
      setActiveConversation(convo);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Helper component for input fields
  const InputField = ({ label, value, onChange, placeholder, type = "text" }: any) => (
    <div>
      <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e: any) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-4 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-xs text-white placeholder-neutral-600 outline-none transition-all"
      />
    </div>
  );

  const statusColors: Record<string, string> = {
    applied: "bg-blue-500/15 text-blue-400 border-blue-500/25",
    screening: "bg-yellow-500/15 text-yellow-400 border-yellow-500/25",
    interviewing: "bg-purple-500/15 text-purple-400 border-purple-500/25",
    offer: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
    rejected: "bg-red-500/15 text-red-400 border-red-500/25",
    accepted: "bg-green-500/15 text-green-400 border-green-500/25",
    withdrawn: "bg-neutral-500/15 text-neutral-400 border-neutral-500/25",
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Page Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl md:text-3xl text-foreground flex items-center gap-2.5">
            <Sparkles className="text-primary w-7 h-7" /> Career Growth Suite
          </h1>
          <p className="text-sm text-muted-foreground mt-1">AI-powered tools to optimize your resume, prepare for interviews, and accelerate your career</p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Side: Upload & History List */}
        <div className="lg:col-span-4 space-y-6">
          {/* Uploader Card */}
          <div className="border border-border bg-card p-6 rounded-2xl">
            <h3 className="font-heading font-bold text-sm text-foreground mb-4">Upload New Resume</h3>
            <label className="border border-dashed border-border hover:border-primary/50 bg-[#0d0d0d]/40 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all hover:bg-neutral-900/10 text-center relative group">
              <input 
                type="file" 
                accept=".pdf,.docx" 
                onChange={handleFileUpload} 
                className="hidden" 
                disabled={uploading}
              />
              {uploading ? (
                <div className="py-4 flex flex-col items-center">
                  <Loader2 className="w-8 h-8 animate-spin text-primary mb-2" />
                  <span className="text-xs font-semibold text-white">Extracting text...</span>
                </div>
              ) : (
                <>
                  <div className="bg-primary/10 border border-primary/20 text-primary p-3 rounded-full mb-3 group-hover:scale-110 transition-transform">
                    <Upload className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-foreground">Click to upload resume</span>
                  <span className="text-[10px] text-muted-foreground mt-1.5">PDF or DOCX (Max 10MB)</span>
                </>
              )}
            </label>
            {error && <p className="text-[11px] text-red-400 mt-3 text-center font-medium">{error}</p>}
          </div>

          {/* History log */}
          <div className="border border-border bg-card p-6 rounded-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-heading font-bold text-sm text-foreground">Uploaded Documents</h3>
              <ListFilter className="w-4 h-4 text-muted-foreground" />
            </div>
            
            {history.length === 0 ? (
              <div className="py-8 text-center text-xs text-muted-foreground">
                No uploads found. Upload a PDF/DOCX to begin.
              </div>
            ) : (
              <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
                {history.map((resume) => {
                  const isActive = activeResume?.id === resume.id;
                  return (
                    <button
                      key={resume.id}
                      onClick={() => handleSelectResume(resume)}
                      className={`w-full flex items-start gap-3 p-3 rounded-xl text-left transition-all text-xs border ${
                        isActive
                          ? "bg-primary/10 border-primary text-foreground"
                          : "border-border hover:bg-muted text-muted-foreground"
                      }`}
                    >
                      <FileText className={`w-4 h-4 shrink-0 mt-0.5 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
                      <div className="overflow-hidden">
                        <p className="font-bold text-foreground truncate">{resume.file_name}</p>
                        <p className="text-[10px] text-muted-foreground mt-0.5">
                          Uploaded {new Date(resume.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Tab Content */}
        <div className="lg:col-span-8">
          {scoring ? (
            <div className="border border-border bg-card rounded-2xl p-16 flex flex-col items-center justify-center text-center">
              <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
              <h3 className="font-heading font-bold text-base text-foreground">Parsing & Scoring</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs">Building scoring breakdowns, auditing structure layers, and indexing keywords...</p>
            </div>
          ) : activeResume && report ? (
            <div className="space-y-6">

              {/* ============ ATS TAB ============ */}
              {activeTab === "ats" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="border border-border bg-card p-6 rounded-2xl flex flex-col items-center justify-center text-center">
                      <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Overall Score</span>
                      <div className="relative w-36 h-36 flex items-center justify-center mt-4">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="40" stroke="var(--border)" strokeWidth="8" fill="transparent" />
                          <circle cx="50" cy="50" r="40" stroke="var(--primary)" strokeWidth="8" fill="transparent" strokeDasharray={2 * Math.PI * 40} strokeDashoffset={2 * Math.PI * 40 * (1 - report.overall_score / 100)} strokeLinecap="round" />
                        </svg>
                        <span className="absolute font-heading text-3xl font-extrabold text-foreground">{report.overall_score}</span>
                      </div>
                      <span className="text-[10px] text-muted-foreground mt-4">Target score: 80+ for optimal ATS pass</span>
                    </div>
                    <div className="border border-border bg-card p-6 rounded-2xl md:col-span-2 space-y-4">
                      <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider">Score Category Breakdown</h4>
                      <div className="grid sm:grid-cols-2 gap-4 text-xs">
                        {[
                          { name: "Skills (30%)", score: report.breakdown.skills, max: 30 },
                          { name: "Keywords (20%)", score: report.breakdown.keywords, max: 20 },
                          { name: "Experience (20%)", score: report.breakdown.experience, max: 20 },
                          { name: "Formatting (15%)", score: report.breakdown.formatting, max: 15 },
                          { name: "Education (10%)", score: report.breakdown.education, max: 10 },
                          { name: "Contact Info (5%)", score: report.breakdown.contact_info, max: 5 },
                        ].map((cat, idx) => (
                          <div key={idx} className="space-y-1.5">
                            <div className="flex justify-between font-medium">
                              <span>{cat.name}</span>
                              <span className="font-bold text-foreground">{cat.score} / {cat.max}</span>
                            </div>
                            <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                              <div className="bg-accent h-full rounded-full transition-all" style={{ width: `${(cat.score / cat.max) * 100}%` }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                      <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-accent" /> Audited Strengths</h4>
                      <ul className="text-xs space-y-2.5 text-muted-foreground">
                        {report.explainability.strengths.length === 0 ? <li>Standard layout validation complete.</li> : report.explainability.strengths.map((str, idx) => (<li key={idx} className="flex gap-2"><span className="text-accent shrink-0">✓</span> {str}</li>))}
                      </ul>
                    </div>
                    <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                      <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><AlertTriangle className="w-4 h-4 text-red-400" /> Improvement Areas</h4>
                      <ul className="text-xs space-y-2.5 text-muted-foreground">
                        {report.explainability.weak_content_areas.length === 0 ? <li className="text-accent">No critical structural warnings detected!</li> : report.explainability.weak_content_areas.map((weak, idx) => (<li key={idx} className="flex gap-2"><span className="text-red-400 shrink-0">!</span> {weak}</li>))}
                      </ul>
                    </div>
                  </div>
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                    <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><Code className="w-4.5 h-4.5 text-primary" /> Parsed Candidate Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {activeResume.parsed_content.skills.length === 0 ? <span className="text-xs text-muted-foreground">No matching keywords parsed.</span> : activeResume.parsed_content.skills.map((skill, idx) => (<span key={idx} className="bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider">{skill}</span>))}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* ============ JD MATCHER TAB ============ */}
              {activeTab === "jd" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                    <div>
                      <h4 className="font-heading font-bold text-sm text-foreground">Target Job Description</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">Paste target qualifications requirements to analyze semantic fits.</p>
                    </div>
                    <textarea value={jdText} onChange={(e) => setJdText(e.target.value)} placeholder="We are looking for a Software Engineer with experience in Python, FastAPI, React, Docker..." className="w-full min-h-40 p-4 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-xs text-white placeholder-neutral-600 outline-none transition-all resize-y" />
                    <div className="flex justify-end">
                      <button onClick={handleJDMatch} disabled={matching || !jdText.trim()} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all shadow-md shadow-primary/20">
                        {matching ? <><Loader2 className="w-4 h-4 animate-spin" /> Aligning vectors...</> : <>Calculate Match Compatibility <ArrowRight className="w-4.5 h-4.5" /></>}
                      </button>
                    </div>
                  </div>
                  {matchReport && (
                    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                      <div className="grid md:grid-cols-3 gap-6">
                        <div className="border border-border bg-card p-6 rounded-2xl flex flex-col items-center justify-center text-center">
                          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Semantic Match</span>
                          <div className="mt-4 font-heading text-5xl font-extrabold text-foreground bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">{matchReport.match_score}%</div>
                          <span className="text-[10px] text-muted-foreground mt-3">Cosine similarity calculation</span>
                        </div>
                        <div className="border border-border bg-card p-6 rounded-2xl md:col-span-2 space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-accent" /> Tailored Advice</h4>
                          <ul className="text-xs space-y-2 text-muted-foreground">{matchReport.recommendations.map((rec, idx) => (<li key={idx} className="flex gap-2"><span className="text-primary shrink-0">✦</span> {rec}</li>))}</ul>
                        </div>
                      </div>
                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-accent" /> Matched Skills</h4>
                          <div className="flex flex-wrap gap-1.5">{matchReport.matched_skills.length === 0 ? <span className="text-xs text-muted-foreground">No overlapping skills.</span> : matchReport.matched_skills.map((skill, idx) => (<span key={idx} className="bg-accent/15 border border-accent/25 text-accent text-[9px] font-bold px-2 py-0.5 rounded-md uppercase">{skill}</span>))}</div>
                        </div>
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><AlertTriangle className="w-4 h-4 text-red-400" /> Missing Skills</h4>
                          <div className="flex flex-wrap gap-1.5">{matchReport.missing_skills.length === 0 ? <span className="text-xs text-accent">Excellent! You cover all parsed job details.</span> : matchReport.missing_skills.map((skill, idx) => (<span key={idx} className="bg-red-500/10 border border-red-500/20 text-red-400 text-[9px] font-bold px-2 py-0.5 rounded-md uppercase">{skill}</span>))}</div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* ============ AI REWRITER TAB ============ */}
              {activeTab === "rewriter" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-5">
                    <div>
                      <h4 className="font-heading font-bold text-sm text-foreground flex items-center gap-2"><PenTool className="w-4 h-4 text-primary" /> AI Resume Rewriter</h4>
                      <p className="text-xs text-muted-foreground mt-1">Transform your resume content with AI-powered rewriting optimized for your target role.</p>
                    </div>
                    <div className="grid sm:grid-cols-2 gap-4">
                      <InputField label="Target Role" value={rewriteRole} onChange={setRewriteRole} placeholder="e.g., Senior Software Engineer" />
                      <div>
                        <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block mb-1.5">Tone</label>
                        <select value={rewriteTone} onChange={(e) => setRewriteTone(e.target.value)} className="w-full px-4 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary rounded-xl text-xs text-white outline-none transition-all">
                          <option value="professional">Professional</option>
                          <option value="creative">Creative</option>
                          <option value="executive">Executive</option>
                          <option value="technical">Technical</option>
                        </select>
                      </div>
                    </div>
                    <button onClick={handleRewrite} disabled={rewriting} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all shadow-md shadow-primary/20">
                      {rewriting ? <><Loader2 className="w-4 h-4 animate-spin" /> Rewriting with AI...</> : <><PenTool className="w-4 h-4" /> Rewrite Resume</>}
                    </button>
                  </div>
                  {rewriteResult && (
                    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                      <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                        <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-accent" /> Improvements Made</h4>
                        <ul className="text-xs space-y-2 text-muted-foreground">{rewriteResult.improvements.map((imp, idx) => (<li key={idx} className="flex gap-2"><span className="text-accent shrink-0">✦</span> {imp}</li>))}</ul>
                      </div>
                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-red-400 uppercase tracking-wider">Original</h4>
                          {activeResume.parsed_content.experience.slice(0, 3).map((exp, idx) => (
                            <div key={idx} className="text-xs text-muted-foreground p-3 bg-red-500/5 border border-red-500/10 rounded-lg">
                              <p className="font-bold text-foreground">{exp.role} at {exp.company}</p>
                              <p className="mt-1">{exp.description}</p>
                            </div>
                          ))}
                        </div>
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-accent uppercase tracking-wider">Rewritten</h4>
                          {(rewriteResult.rewritten?.experience || []).slice(0, 3).map((exp: any, idx: number) => (
                            <div key={idx} className="text-xs text-muted-foreground p-3 bg-accent/5 border border-accent/10 rounded-lg">
                              <p className="font-bold text-foreground">{exp.role} at {exp.company}</p>
                              <p className="mt-1">{exp.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      {rewriteResult.rewritten?.skills && (
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider">Optimized Skills</h4>
                          <div className="flex flex-wrap gap-2">{rewriteResult.rewritten.skills.map((skill: string, idx: number) => (<span key={idx} className="bg-accent/15 border border-accent/25 text-accent text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">{skill}</span>))}</div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* ============ INTERVIEW PREP TAB ============ */}
              {activeTab === "interview" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  {!interviewSession ? (
                    <div className="border border-border bg-card p-6 rounded-2xl space-y-5">
                      <div>
                        <h4 className="font-heading font-bold text-sm text-foreground flex items-center gap-2"><MessageSquare className="w-4 h-4 text-primary" /> Interview Preparation</h4>
                        <p className="text-xs text-muted-foreground mt-1">Practice with AI-generated interview questions tailored to your target role and resume.</p>
                      </div>
                      <div className="grid sm:grid-cols-2 gap-4">
                        <InputField label="Target Role" value={interviewRole} onChange={setInterviewRole} placeholder="e.g., Full Stack Developer" />
                        <div>
                          <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block mb-1.5">Difficulty</label>
                          <select value={interviewDifficulty} onChange={(e) => setInterviewDifficulty(e.target.value)} className="w-full px-4 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary rounded-xl text-xs text-white outline-none transition-all">
                            <option value="easy">Easy</option>
                            <option value="medium">Medium</option>
                            <option value="hard">Hard</option>
                          </select>
                        </div>
                      </div>
                      <button onClick={handleStartInterview} disabled={interviewLoading || !interviewRole.trim()} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all shadow-md shadow-primary/20">
                        {interviewLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating questions...</> : <>Start Mock Interview <ArrowRight className="w-4 h-4" /></>}
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Progress bar */}
                      <div className="border border-border bg-card p-4 rounded-2xl">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs font-bold text-foreground">Question {activeQuestionIdx + 1} / {interviewSession.questions.length}</span>
                          <span className="text-[10px] text-muted-foreground uppercase">{interviewSession.target_role} • {interviewSession.difficulty}</span>
                        </div>
                        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                          <div className="bg-primary h-full rounded-full transition-all" style={{ width: `${((activeQuestionIdx + 1) / interviewSession.questions.length) * 100}%` }} />
                        </div>
                      </div>

                      {/* Question card */}
                      {interviewSession.questions.map((q, idx) => idx === activeQuestionIdx && (
                        <div key={q.id} className="border border-border bg-card p-6 rounded-2xl space-y-4">
                          <div className="flex items-start gap-3">
                            <span className={`text-[9px] font-bold px-2 py-0.5 rounded-md uppercase border ${q.category === "technical" ? "bg-blue-500/15 text-blue-400 border-blue-500/25" : q.category === "behavioral" ? "bg-purple-500/15 text-purple-400 border-purple-500/25" : "bg-yellow-500/15 text-yellow-400 border-yellow-500/25"}`}>{q.category}</span>
                          </div>
                          <p className="text-sm font-medium text-foreground">{q.question_text}</p>
                          
                          {!q.ai_feedback ? (
                            <div className="space-y-3">
                              <textarea value={currentAnswer} onChange={(e) => setCurrentAnswer(e.target.value)} placeholder="Type your answer here..." className="w-full min-h-32 p-4 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-xs text-white placeholder-neutral-600 outline-none transition-all resize-y" />
                              <button onClick={handleSubmitAnswer} disabled={answerLoading || !currentAnswer.trim()} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all">
                                {answerLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Evaluating...</> : <><Send className="w-4 h-4" /> Submit Answer</>}
                              </button>
                            </div>
                          ) : (
                            <div className="space-y-3">
                              <div className="p-3 bg-[#0d0d0d] border border-border rounded-lg text-xs text-muted-foreground"><p className="font-bold text-foreground mb-1">Your Answer:</p>{q.user_answer}</div>
                              <div className="flex items-center gap-3">
                                <div className="bg-primary/15 border border-primary/25 px-3 py-1.5 rounded-lg text-primary font-bold text-sm">{q.score}/10</div>
                                <span className="text-xs text-muted-foreground">{q.score && q.score >= 7 ? "Great answer!" : q.score && q.score >= 5 ? "Good, but can improve" : "Needs improvement"}</span>
                              </div>
                              {q.ai_feedback.strengths && q.ai_feedback.strengths.length > 0 && (
                                <div className="p-3 bg-accent/5 border border-accent/10 rounded-lg text-xs">
                                  <p className="font-bold text-accent mb-1">Strengths:</p>
                                  <ul className="space-y-1 text-muted-foreground">{q.ai_feedback.strengths.map((s: string, i: number) => <li key={i}>✓ {s}</li>)}</ul>
                                </div>
                              )}
                              {q.ai_feedback.improvements && q.ai_feedback.improvements.length > 0 && (
                                <div className="p-3 bg-yellow-500/5 border border-yellow-500/10 rounded-lg text-xs">
                                  <p className="font-bold text-yellow-400 mb-1">Improvements:</p>
                                  <ul className="space-y-1 text-muted-foreground">{q.ai_feedback.improvements.map((s: string, i: number) => <li key={i}>→ {s}</li>)}</ul>
                                </div>
                              )}
                              {q.ai_feedback.sample_answer && (
                                <div className="p-3 bg-primary/5 border border-primary/10 rounded-lg text-xs">
                                  <p className="font-bold text-primary mb-1">Sample Answer:</p>
                                  <p className="text-muted-foreground">{q.ai_feedback.sample_answer}</p>
                                </div>
                              )}
                              <button onClick={() => { if (activeQuestionIdx < interviewSession.questions.length - 1) { setActiveQuestionIdx(activeQuestionIdx + 1); setCurrentAnswer(""); } }} disabled={activeQuestionIdx >= interviewSession.questions.length - 1} className="text-primary text-xs font-semibold flex items-center gap-1 hover:underline disabled:text-neutral-500">Next Question <ArrowRight className="w-3 h-3" /></button>
                            </div>
                          )}
                        </div>
                      ))}
                      <button onClick={() => { setInterviewSession(null); setActiveQuestionIdx(0); }} className="text-xs text-muted-foreground hover:text-foreground transition-colors">← Start New Session</button>
                    </div>
                  )}
                </motion.div>
              )}

              {/* ============ SKILL GAP TAB ============ */}
              {activeTab === "skills" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-5">
                    <div>
                      <h4 className="font-heading font-bold text-sm text-foreground flex items-center gap-2"><BarChart3 className="w-4 h-4 text-primary" /> Skill Gap Analysis</h4>
                      <p className="text-xs text-muted-foreground mt-1">Identify the skills you need to develop for your target role.</p>
                    </div>
                    <InputField label="Target Role" value={skillGapRole} onChange={setSkillGapRole} placeholder="e.g., Machine Learning Engineer" />
                    <button onClick={handleSkillGap} disabled={skillGapLoading || !skillGapRole.trim()} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all shadow-md shadow-primary/20">
                      {skillGapLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</> : <><Target className="w-4 h-4" /> Analyze Skill Gap</>}
                    </button>
                  </div>
                  {skillGapResult && (
                    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                      <div className="border border-border bg-card p-6 rounded-2xl flex items-center gap-6">
                        <div className="relative w-24 h-24 flex items-center justify-center">
                          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="40" stroke="var(--border)" strokeWidth="8" fill="transparent" />
                            <circle cx="50" cy="50" r="40" stroke="var(--primary)" strokeWidth="8" fill="transparent" strokeDasharray={2 * Math.PI * 40} strokeDashoffset={2 * Math.PI * 40 * (1 - skillGapResult.overall_readiness / 100)} strokeLinecap="round" />
                          </svg>
                          <span className="absolute font-heading text-xl font-extrabold text-foreground">{skillGapResult.overall_readiness}%</span>
                        </div>
                        <div>
                          <h4 className="font-heading font-bold text-base text-foreground">Readiness for {skillGapResult.target_role}</h4>
                          <p className="text-xs text-muted-foreground mt-1">{skillGapResult.current_skills.length} skills assessed • {skillGapResult.missing_skills.length} gaps identified</p>
                        </div>
                      </div>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-accent" /> Current Skills</h4>
                          <div className="space-y-2">{skillGapResult.current_skills.slice(0, 10).map((skill, idx) => (
                            <div key={idx} className="flex items-center justify-between text-xs">
                              <span className="text-foreground font-medium">{skill.name}</span>
                              <div className="flex items-center gap-2">
                                <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden"><div className="bg-accent h-full rounded-full" style={{ width: `${skill.proficiency * 10}%` }} /></div>
                                <span className="text-muted-foreground w-6 text-right">{skill.proficiency}</span>
                              </div>
                            </div>
                          ))}</div>
                        </div>
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><AlertTriangle className="w-4 h-4 text-red-400" /> Missing Skills</h4>
                          <div className="space-y-2">{skillGapResult.missing_skills.map((skill, idx) => (
                            <div key={idx} className="p-2.5 border border-border rounded-lg">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-foreground">{skill.name}</span>
                                <span className={`text-[9px] font-bold px-2 py-0.5 rounded-md uppercase border ${skill.importance === "critical" ? "bg-red-500/15 text-red-400 border-red-500/25" : skill.importance === "important" ? "bg-yellow-500/15 text-yellow-400 border-yellow-500/25" : "bg-blue-500/15 text-blue-400 border-blue-500/25"}`}>{skill.importance}</span>
                              </div>
                              {skill.resources.length > 0 && <p className="text-[10px] text-muted-foreground mt-1">📚 {skill.resources[0]}</p>}
                            </div>
                          ))}</div>
                        </div>
                      </div>
                      {skillGapResult.recommendations.length > 0 && (
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><BookOpen className="w-4 h-4 text-primary" /> Recommendations</h4>
                          <ul className="text-xs space-y-2 text-muted-foreground">{skillGapResult.recommendations.map((rec, idx) => (<li key={idx} className="flex gap-2"><span className="text-primary shrink-0">✦</span> {rec}</li>))}</ul>
                        </div>
                      )}
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* ============ CAREER ROADMAP TAB ============ */}
              {activeTab === "roadmap" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-5">
                    <div>
                      <h4 className="font-heading font-bold text-sm text-foreground flex items-center gap-2"><Map className="w-4 h-4 text-primary" /> Career Roadmap Generator</h4>
                      <p className="text-xs text-muted-foreground mt-1">Get a personalized career progression plan with milestones and resources.</p>
                    </div>
                    <div className="grid sm:grid-cols-3 gap-4">
                      <InputField label="Current Role" value={roadmapCurrentRole} onChange={setRoadmapCurrentRole} placeholder="e.g., Junior Developer" />
                      <InputField label="Target Role" value={roadmapTargetRole} onChange={setRoadmapTargetRole} placeholder="e.g., Tech Lead" />
                      <InputField label="Timeline (months)" value={roadmapTimeline} onChange={(v: string) => setRoadmapTimeline(parseInt(v) || 12)} placeholder="12" type="number" />
                    </div>
                    <button onClick={handleRoadmap} disabled={roadmapLoading || !roadmapCurrentRole.trim() || !roadmapTargetRole.trim()} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all shadow-md shadow-primary/20">
                      {roadmapLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating roadmap...</> : <><Map className="w-4 h-4" /> Generate Roadmap</>}
                    </button>
                  </div>
                  {roadmapResult && (
                    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                      <div className="border border-border bg-card p-6 rounded-2xl">
                        <h4 className="font-heading font-bold text-base text-foreground mb-1">{roadmapResult.current_role} → {roadmapResult.target_role}</h4>
                        <p className="text-xs text-muted-foreground">{roadmapResult.timeline_months} month plan • {roadmapResult.phases.length} phases</p>
                        {roadmapResult.salary_progression && (
                          <div className="mt-3 flex gap-4 text-xs">
                            <span className="text-muted-foreground">Current: <span className="text-foreground font-bold">{roadmapResult.salary_progression.current_estimate || "N/A"}</span></span>
                            <span className="text-muted-foreground">Target: <span className="text-accent font-bold">{roadmapResult.salary_progression.target_estimate || "N/A"}</span></span>
                          </div>
                        )}
                      </div>
                      {/* Timeline phases */}
                      <div className="space-y-3">
                        {roadmapResult.phases.map((phase, idx) => (
                          <div key={idx} className="border border-border bg-card p-5 rounded-2xl">
                            <div className="flex items-center gap-3 mb-3">
                              <div className="w-8 h-8 rounded-full bg-primary/15 border border-primary/25 flex items-center justify-center text-primary font-bold text-xs">{idx + 1}</div>
                              <div>
                                <h5 className="font-bold text-sm text-foreground">{phase.phase_name}</h5>
                                <span className="text-[10px] text-muted-foreground">{phase.duration_months} months</span>
                              </div>
                            </div>
                            <div className="grid sm:grid-cols-3 gap-3 text-xs">
                              <div><p className="font-bold text-muted-foreground mb-1">Milestones</p><ul className="space-y-1">{phase.milestones.map((m, i) => <li key={i} className="text-foreground">• {m}</li>)}</ul></div>
                              <div><p className="font-bold text-muted-foreground mb-1">Skills</p><div className="flex flex-wrap gap-1">{phase.skills_to_learn.map((s, i) => <span key={i} className="bg-primary/10 border border-primary/20 text-primary text-[9px] font-bold px-2 py-0.5 rounded-md">{s}</span>)}</div></div>
                              <div><p className="font-bold text-muted-foreground mb-1">Resources</p><ul className="space-y-1">{phase.resources.map((r, i) => <li key={i} className="text-muted-foreground">📖 {r}</li>)}</ul></div>
                            </div>
                          </div>
                        ))}
                      </div>
                      {roadmapResult.certifications.length > 0 && (
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5"><Award className="w-4 h-4 text-primary" /> Recommended Certifications</h4>
                          <div className="grid sm:grid-cols-2 gap-3">{roadmapResult.certifications.map((cert, idx) => (
                            <div key={idx} className="p-3 border border-border rounded-lg text-xs">
                              <p className="font-bold text-foreground">{cert.name}</p>
                              <p className="text-muted-foreground mt-0.5">{cert.provider} • {cert.estimated_time}</p>
                            </div>
                          ))}</div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* ============ APPLICATION TRACKER TAB ============ */}
              {activeTab === "tracker" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  {/* Stats row */}
                  {trackerStats && (
                    <div className="grid grid-cols-4 gap-3">
                      {[
                        { label: "Total", value: trackerStats.total, color: "text-foreground" },
                        { label: "Active", value: trackerStats.applied + trackerStats.screening + trackerStats.interviewing, color: "text-blue-400" },
                        { label: "Offers", value: trackerStats.offer + trackerStats.accepted, color: "text-accent" },
                        { label: "Rejected", value: trackerStats.rejected, color: "text-red-400" },
                      ].map((stat, idx) => (
                        <div key={idx} className="border border-border bg-card p-4 rounded-2xl text-center">
                          <div className={`font-heading text-2xl font-extrabold ${stat.color}`}>{stat.value}</div>
                          <p className="text-[10px] text-muted-foreground mt-0.5 uppercase tracking-wider">{stat.label}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Add button */}
                  <div className="flex justify-between items-center">
                    <h4 className="font-heading font-bold text-sm text-foreground flex items-center gap-2"><ClipboardList className="w-4 h-4 text-primary" /> Applications</h4>
                    <button onClick={() => setShowAddApp(!showAddApp)} className="bg-primary hover:bg-indigo-700 text-white text-xs font-semibold px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all"><Plus className="w-3.5 h-3.5" /> Add</button>
                  </div>

                  {/* Add form */}
                  {showAddApp && (
                    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="border border-border bg-card p-5 rounded-2xl space-y-4">
                      <div className="grid sm:grid-cols-2 gap-4">
                        <InputField label="Company" value={newApp.company_name} onChange={(v: string) => setNewApp({ ...newApp, company_name: v })} placeholder="Google" />
                        <InputField label="Job Title" value={newApp.job_title} onChange={(v: string) => setNewApp({ ...newApp, job_title: v })} placeholder="Software Engineer" />
                        <InputField label="Location" value={newApp.location} onChange={(v: string) => setNewApp({ ...newApp, location: v })} placeholder="Remote / New York" />
                        <InputField label="Salary Range" value={newApp.salary_range} onChange={(v: string) => setNewApp({ ...newApp, salary_range: v })} placeholder="$120k - $150k" />
                      </div>
                      <InputField label="Job URL" value={newApp.job_url} onChange={(v: string) => setNewApp({ ...newApp, job_url: v })} placeholder="https://careers.google.com/..." />
                      <div className="flex justify-end gap-3">
                        <button onClick={() => setShowAddApp(false)} className="text-xs text-muted-foreground hover:text-foreground">Cancel</button>
                        <button onClick={handleAddApplication} disabled={!newApp.company_name.trim() || !newApp.job_title.trim()} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all">Save Application</button>
                      </div>
                    </motion.div>
                  )}

                  {/* Applications list */}
                  <div className="space-y-2.5">
                    {applications.length === 0 ? (
                      <div className="border border-border bg-card rounded-2xl p-12 text-center">
                        <ClipboardList className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                        <p className="text-xs text-muted-foreground">No applications tracked yet. Click "Add" to start tracking!</p>
                      </div>
                    ) : applications.map((app) => (
                      <div key={app.id} className="border border-border bg-card p-4 rounded-xl flex items-center justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-bold text-sm text-foreground truncate">{app.job_title}</span>
                            <span className={`text-[9px] font-bold px-2 py-0.5 rounded-md uppercase border ${statusColors[app.status] || statusColors.applied}`}>{app.status}</span>
                          </div>
                          <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                            <span>{app.company_name}</span>
                            {app.location && <span>📍 {app.location}</span>}
                            {app.salary_range && <span>💰 {app.salary_range}</span>}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <select value={app.status} onChange={(e) => handleUpdateStatus(app.id, e.target.value)} className="bg-[#0d0d0d] border border-border rounded-lg text-[10px] text-white px-2 py-1 outline-none">
                            {["applied", "screening", "interviewing", "offer", "rejected", "accepted", "withdrawn"].map(s => <option key={s} value={s}>{s}</option>)}
                          </select>
                          {app.job_url && <a href={app.job_url} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors"><ExternalLink className="w-3.5 h-3.5" /></a>}
                          <button onClick={() => handleDeleteApplication(app.id)} className="text-muted-foreground hover:text-red-400 transition-colors"><Trash2 className="w-3.5 h-3.5" /></button>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* ============ JOB MATCH TAB ============ */}
              {activeTab === "jobs" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                    <div>
                      <h4 className="font-heading font-bold text-sm text-foreground flex items-center gap-2"><Briefcase className="w-4 h-4 text-primary" /> Job Match Dashboard</h4>
                      <p className="text-xs text-muted-foreground mt-1">Find the best-matching jobs based on your resume skills and experience.</p>
                    </div>
                    <button onClick={handleJobMatch} disabled={jobMatchLoading} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all shadow-md shadow-primary/20">
                      {jobMatchLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Scanning jobs...</> : <><Briefcase className="w-4 h-4" /> Find Matching Jobs</>}
                    </button>
                  </div>
                  {jobMatchResult && (
                    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                      <p className="text-xs text-muted-foreground">{jobMatchResult.total_jobs_scanned} jobs scanned • {jobMatchResult.matches.length} matches found</p>
                      {jobMatchResult.matches.length === 0 ? (
                        <div className="border border-border bg-card rounded-2xl p-12 text-center">
                          <Briefcase className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                          <p className="text-xs text-muted-foreground">No matching jobs found. Recruiters haven't posted matching job descriptions yet.</p>
                        </div>
                      ) : jobMatchResult.matches.map((job, idx) => (
                        <div key={idx} className="border border-border bg-card p-5 rounded-2xl space-y-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <h5 className="font-bold text-sm text-foreground">{job.title}</h5>
                              <p className="text-xs text-muted-foreground">{job.company_name}</p>
                            </div>
                            <div className="bg-primary/15 border border-primary/25 px-3 py-1.5 rounded-lg text-primary font-bold text-sm">{job.match_score}%</div>
                          </div>
                          <div className="grid sm:grid-cols-2 gap-3">
                            <div><p className="text-[10px] font-bold text-accent uppercase mb-1">Matched</p><div className="flex flex-wrap gap-1">{job.matched_skills.slice(0, 8).map((s, i) => <span key={i} className="bg-accent/15 border border-accent/25 text-accent text-[9px] font-bold px-2 py-0.5 rounded-md">{s}</span>)}</div></div>
                            <div><p className="text-[10px] font-bold text-red-400 uppercase mb-1">Missing</p><div className="flex flex-wrap gap-1">{job.missing_skills.slice(0, 8).map((s, i) => <span key={i} className="bg-red-500/10 border border-red-500/20 text-red-400 text-[9px] font-bold px-2 py-0.5 rounded-md">{s}</span>)}</div></div>
                          </div>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* ============ AI COACH TAB ============ */}
              {activeTab === "coach" && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="font-heading font-bold text-sm text-foreground flex items-center gap-2"><Bot className="w-4 h-4 text-primary" /> AI Career Coach</h4>
                    <button onClick={handleStartConversation} className="bg-primary hover:bg-indigo-700 text-white text-xs font-semibold px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all"><Plus className="w-3.5 h-3.5" /> New Chat</button>
                  </div>

                  <div className="grid grid-cols-12 gap-4" style={{ minHeight: "500px" }}>
                    {/* Conversation list */}
                    <div className="col-span-4 border border-border bg-card rounded-2xl p-3 overflow-y-auto" style={{ maxHeight: "500px" }}>
                      {coachConversations.length === 0 ? (
                        <div className="py-8 text-center text-xs text-muted-foreground">No conversations yet. Click "New Chat" to start!</div>
                      ) : coachConversations.map((convo) => (
                        <button key={convo.id} onClick={() => loadConversation(convo.id)} className={`w-full text-left p-3 rounded-xl text-xs transition-all mb-1.5 ${activeConversation?.id === convo.id ? "bg-primary/10 border border-primary" : "hover:bg-muted border border-transparent"}`}>
                          <p className="font-bold text-foreground truncate">{convo.title}</p>
                          <p className="text-[10px] text-muted-foreground mt-0.5">{convo.message_count} messages</p>
                        </button>
                      ))}
                    </div>

                    {/* Chat area */}
                    <div className="col-span-8 border border-border bg-card rounded-2xl flex flex-col" style={{ maxHeight: "500px" }}>
                      {!activeConversation ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
                          <Bot className="w-12 h-12 text-muted-foreground mb-4" />
                          <h5 className="font-bold text-sm text-foreground">Start a conversation</h5>
                          <p className="text-xs text-muted-foreground mt-1 max-w-xs">Ask about career advice, resume tips, interview strategies, salary negotiation, or anything career-related.</p>
                        </div>
                      ) : (
                        <>
                          <div className="flex-1 overflow-y-auto p-4 space-y-3">
                            {activeConversation.messages.map((msg) => (
                              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                                <div className={`max-w-[80%] p-3 rounded-2xl text-xs ${msg.role === "user" ? "bg-primary text-white rounded-br-md" : "bg-muted text-foreground rounded-bl-md"}`}>
                                  <p className="whitespace-pre-wrap">{msg.content}</p>
                                </div>
                              </div>
                            ))}
                            {coachLoading && (
                              <div className="flex justify-start">
                                <div className="bg-muted p-3 rounded-2xl rounded-bl-md"><Loader2 className="w-4 h-4 animate-spin text-primary" /></div>
                              </div>
                            )}
                          </div>
                          <div className="border-t border-border p-3 flex gap-2">
                            <input value={coachMessage} onChange={(e) => setCoachMessage(e.target.value)} onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSendCoachMessage()} placeholder="Ask your career coach..." className="flex-1 px-4 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary rounded-xl text-xs text-white placeholder-neutral-600 outline-none transition-all" />
                            <button onClick={handleSendCoachMessage} disabled={coachLoading || !coachMessage.trim()} className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 text-white p-2.5 rounded-xl transition-all"><Send className="w-4 h-4" /></button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          ) : (
            <div className="border border-border bg-card rounded-2xl p-16 flex flex-col items-center justify-center text-center">
              <div className="bg-muted p-4 rounded-full text-muted-foreground mb-4">
                <FileText className="w-8 h-8" />
              </div>
              <h3 className="font-heading font-bold text-base text-foreground">Select a Resume to View</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs">Upload a resume or click an item from the history panel to render audits and optimizer charts.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CandidateDashboard() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex flex-col items-center justify-center text-muted-foreground gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <span className="text-sm font-medium">Loading candidate dashboard...</span>
      </div>
    }>
      <CandidateDashboardContent />
    </Suspense>
  );
}
