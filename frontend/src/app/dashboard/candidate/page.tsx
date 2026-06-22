"use client";

import { useEffect, useState, Suspense } from "react";
import { api } from "@/services/api";
import { Resume, ATSReport, JDMatch } from "@/types";
import { 
  Upload, FileText, Activity, AlertTriangle, CheckCircle, 
  Sparkles, Code, ChevronRight, HelpCircle, ArrowRight, Loader2, ListFilter
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useSearchParams } from "next/navigation";

function CandidateDashboardContent() {
  const [history, setHistory] = useState<Resume[]>([]);
  const [activeResume, setActiveResume] = useState<Resume | null>(null);
  const [report, setReport] = useState<ATSReport | null>(null);
  const [activeTab, setActiveTab] = useState<"ats" | "jd">("ats");
  const [uploading, setUploading] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [matching, setMatching] = useState(false);
  
  // JD Match state
  const [jdText, setJdText] = useState("");
  const [matchReport, setMatchReport] = useState<JDMatch | null>(null);
  const [error, setError] = useState<string | null>(null);

  const searchParams = useSearchParams();
  const tab = searchParams.get("tab");

  useEffect(() => {
    if (tab === "jd") {
      setActiveTab("jd");
    } else if (tab === "ats") {
      setActiveTab("ats");
    }
  }, [tab]);

  useEffect(() => {
    loadHistory();
  }, []);

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
      // Fetch report
      let r: ATSReport;
      try {
        r = await api.getATSReport(resume.id);
      } catch (err) {
        // Generate if not cached
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
      // Load the newly uploaded resume
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

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Page Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl md:text-3xl text-foreground flex items-center gap-2.5">
            <Sparkles className="text-primary w-7 h-7" /> Resume Auditing Suite
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Optimize and align your resume keywords with real-world ATS schemas</p>
        </div>
      </div>

      {/* Main Grid: Upload & History in col 1, Reports in col 2 */}
      <div className="grid lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Side: Upload & History List (4 cols) */}
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

        {/* Right Side: Score Reports & JD Match (8 cols) */}
        <div className="lg:col-span-8">
          {scoring ? (
            <div className="border border-border bg-card rounded-2xl p-16 flex flex-col items-center justify-center text-center">
              <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
              <h3 className="font-heading font-bold text-base text-foreground">Parsing & Scoring</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs">Building scoring breakdowns, auditing structure layers, and indexing keywords...</p>
            </div>
          ) : activeResume && report ? (
            <div className="space-y-6">
              
              {/* Tab Selector */}
              <div className="flex border-b border-border">
                <button
                  onClick={() => setActiveTab("ats")}
                  className={`py-3.5 px-6 text-xs font-bold tracking-wide uppercase border-b-2 transition-all ${
                    activeTab === "ats" 
                      ? "border-primary text-primary" 
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  ATS Score Analysis
                </button>
                <button
                  onClick={() => setActiveTab("jd")}
                  className={`py-3.5 px-6 text-xs font-bold tracking-wide uppercase border-b-2 transition-all ${
                    activeTab === "jd" 
                      ? "border-primary text-primary" 
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Job Description Matcher
                </button>
              </div>

              {/* Tab Content 1: ATS SCORE */}
              {activeTab === "ats" && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* Gauge & Category Breakdown */}
                  <div className="grid md:grid-cols-3 gap-6">
                    {/* Big Gauge */}
                    <div className="border border-border bg-card p-6 rounded-2xl flex flex-col items-center justify-center text-center">
                      <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Overall Score</span>
                      <div className="relative w-36 h-36 flex items-center justify-center mt-4">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="40" stroke="var(--border)" strokeWidth="8" fill="transparent" />
                          <circle 
                            cx="50" cy="50" r="40" 
                            stroke="var(--primary)" strokeWidth="8" fill="transparent" 
                            strokeDasharray={2 * Math.PI * 40}
                            strokeDashoffset={2 * Math.PI * 40 * (1 - report.overall_score / 100)}
                            strokeLinecap="round"
                          />
                        </svg>
                        <span className="absolute font-heading text-3xl font-extrabold text-foreground">{report.overall_score}</span>
                      </div>
                      <span className="text-[10px] text-muted-foreground mt-4">Target score: 80+ for optimal ATS pass</span>
                    </div>

                    {/* Category breakdowns */}
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
                              <div 
                                className="bg-accent h-full rounded-full transition-all"
                                style={{ width: `${(cat.score / cat.max) * 100}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Recommendations, missing keywords & sections */}
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Strengths & Weaknesses */}
                    <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                      <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5">
                        <CheckCircle className="w-4 h-4 text-accent" /> Audited Strengths
                      </h4>
                      <ul className="text-xs space-y-2.5 text-muted-foreground">
                        {report.explainability.strengths.length === 0 ? (
                          <li>Standard layout validation complete.</li>
                        ) : (
                          report.explainability.strengths.map((str, idx) => (
                            <li key={idx} className="flex gap-2">
                              <span className="text-accent shrink-0">✓</span> {str}
                            </li>
                          ))
                        )}
                      </ul>
                    </div>

                    <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                      <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4 text-red-400" /> Improvement Areas
                      </h4>
                      <ul className="text-xs space-y-2.5 text-muted-foreground">
                        {report.explainability.weak_content_areas.length === 0 ? (
                          <li className="text-accent">No critical structural warnings detected!</li>
                        ) : (
                          report.explainability.weak_content_areas.map((weak, idx) => (
                            <li key={idx} className="flex gap-2">
                              <span className="text-red-400 shrink-0">!</span> {weak}
                            </li>
                          ))
                        )}
                      </ul>
                    </div>
                  </div>

                  {/* Skills lists */}
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                    <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5">
                      <Code className="w-4.5 h-4.5 text-primary" /> Parsed Candidate Skills
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {activeResume.parsed_content.skills.length === 0 ? (
                        <span className="text-xs text-muted-foreground">No matching keywords parsed. Update skills format.</span>
                      ) : (
                        activeResume.parsed_content.skills.map((skill, idx) => (
                          <span key={idx} className="bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider">
                            {skill}
                          </span>
                        ))
                      )}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Tab Content 2: JD MATCHER */}
              {activeTab === "jd" && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* paste text */}
                  <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
                    <div>
                      <h4 className="font-heading font-bold text-sm text-foreground">Target Job Description</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">Paste target qualifications requirements to analyze semantic fits.</p>
                    </div>
                    <textarea
                      value={jdText}
                      onChange={(e) => setJdText(e.target.value)}
                      placeholder="We are looking for a Software Engineer with experience in Python, FastAPI, React, Docker..."
                      className="w-full min-h-40 p-4 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-xs text-white placeholder-neutral-600 outline-none transition-all resize-y"
                    />
                    <div className="flex justify-end">
                      <button
                        onClick={handleJDMatch}
                        disabled={matching || !jdText.trim()}
                        className="bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold px-5 py-3 rounded-xl flex items-center gap-2 transition-all shadow-md shadow-primary/20"
                      >
                        {matching ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" /> Aligning vectors...
                          </>
                        ) : (
                          <>
                            Calculate Match Compatibility <ArrowRight className="w-4.5 h-4.5" />
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Match Results Display */}
                  {matchReport && (
                    <motion.div 
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-6"
                    >
                      {/* Match Score Indicator */}
                      <div className="grid md:grid-cols-3 gap-6">
                        <div className="border border-border bg-card p-6 rounded-2xl flex flex-col items-center justify-center text-center">
                          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Semantic Match</span>
                          <div className="mt-4 font-heading text-5xl font-extrabold text-foreground bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                            {matchReport.match_score}%
                          </div>
                          <span className="text-[10px] text-muted-foreground mt-3">Cosine similarity calculation</span>
                        </div>

                        {/* Recommendation advice */}
                        <div className="border border-border bg-card p-6 rounded-2xl md:col-span-2 space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5">
                            <Sparkles className="w-4 h-4 text-accent" /> Tailored Advice
                          </h4>
                          <ul className="text-xs space-y-2 text-muted-foreground">
                            {matchReport.recommendations.map((rec, idx) => (
                              <li key={idx} className="flex gap-2">
                                <span className="text-primary shrink-0">✦</span> {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {/* Matched vs Missing list */}
                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5">
                            <CheckCircle className="w-4 h-4 text-accent" /> Matched Skills
                          </h4>
                          <div className="flex flex-wrap gap-1.5">
                            {matchReport.matched_skills.length === 0 ? (
                              <span className="text-xs text-muted-foreground">No overlapping skills matching the description.</span>
                            ) : (
                              matchReport.matched_skills.map((skill, idx) => (
                                <span key={idx} className="bg-accent/15 border border-accent/25 text-accent text-[9px] font-bold px-2 py-0.5 rounded-md uppercase">
                                  {skill}
                                </span>
                              ))
                            )}
                          </div>
                        </div>

                        <div className="border border-border bg-card p-6 rounded-2xl space-y-3">
                          <h4 className="font-heading font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5">
                            <AlertTriangle className="w-4 h-4 text-red-400" /> Missing Skills
                          </h4>
                          <div className="flex flex-wrap gap-1.5">
                            {matchReport.missing_skills.length === 0 ? (
                              <span className="text-xs text-accent">Excellent! You cover all parsed job details.</span>
                            ) : (
                              matchReport.missing_skills.map((skill, idx) => (
                                <span key={idx} className="bg-red-500/10 border border-red-500/20 text-red-400 text-[9px] font-bold px-2 py-0.5 rounded-md uppercase">
                                  {skill}
                                </span>
                              ))
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
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
