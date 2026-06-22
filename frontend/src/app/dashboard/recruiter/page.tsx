"use client";

import { useState } from "react";
import { api } from "@/services/api";
import { RecruiterScreenResult, RankedCandidate } from "@/types";
import { 
  Users, CheckCircle, Upload, Search, Activity, Sparkles, 
  ArrowRight, Loader2, FileSpreadsheet, Eye, ChevronRight, X
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function RecruiterDashboard() {
  const [jobTitle, setJobTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [department, setDepartment] = useState("");
  const [jdText, setJdText] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecruiterScreenResult | null>(null);
  
  // Selected candidate for modal detail view
  const [selectedCandidate, setSelectedCandidate] = useState<RankedCandidate | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleScreenSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle || !companyName || !jdText || files.length === 0) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.screenCandidates({
        jd_title: jobTitle,
        company_name: companyName,
        jd_text: jdText,
        files
      });
      setResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to process candidate files.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Brand Header */}
      <div>
        <h1 className="font-heading font-bold text-2xl md:text-3xl text-foreground flex items-center gap-2.5">
          <Users className="text-primary w-7 h-7" /> Talent Screening Center
        </h1>
        <p className="text-sm text-muted-foreground mt-1">Batch upload applicant resumes and rank matches semantically</p>
      </div>

      <div className="grid lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Side: JD creation & File drops (5 cols) */}
        <form onSubmit={handleScreenSubmit} className="lg:col-span-5 space-y-6">
          <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
            <h3 className="font-heading font-bold text-sm text-foreground">Job Specifications</h3>
            
            <div className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">Job Title</label>
                <input
                  type="text"
                  required
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="Senior Python Backend Developer"
                  className="w-full px-3.5 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-white placeholder-neutral-600 outline-none transition-all"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">Company</label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="Innovate Corp"
                    className="w-full px-3.5 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-white placeholder-neutral-600 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">Department</label>
                  <input
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    placeholder="Engineering"
                    className="w-full px-3.5 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-white placeholder-neutral-600 outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">Requirements / JD Details</label>
                <textarea
                  required
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste requirements specifications: skills, experience level, tools..."
                  className="w-full min-h-24 p-3 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-white placeholder-neutral-600 outline-none transition-all resize-y"
                />
              </div>
            </div>
          </div>

          {/* Files dropzone */}
          <div className="border border-border bg-card p-6 rounded-2xl space-y-4">
            <h3 className="font-heading font-bold text-sm text-foreground">Upload Candidate Resumes</h3>
            
            <label className="border border-dashed border-border hover:border-primary/50 bg-[#0d0d0d]/40 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all hover:bg-neutral-900/10 text-center relative group">
              <input
                type="file"
                multiple
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="hidden"
                disabled={loading}
              />
              <div className="bg-primary/10 border border-primary/20 text-primary p-3 rounded-full mb-3 group-hover:scale-110 transition-transform">
                <Upload className="w-5 h-5" />
              </div>
              <span className="text-xs font-bold text-foreground">Select multiple resume files</span>
              <span className="text-[10px] text-muted-foreground mt-1.5">Upload PDF/DOCX (Holds up to 20 files)</span>
            </label>

            {/* List selected files queue */}
            {files.length > 0 && (
              <div className="space-y-1.5 max-h-40 overflow-y-auto pt-2">
                <p className="text-[10px] font-bold text-muted-foreground uppercase">Selected Files ({files.length})</p>
                {files.map((f, i) => (
                  <div key={i} className="flex justify-between items-center bg-[#0d0d0d] border border-border px-3 py-1.5 rounded-lg text-[10px] text-muted-foreground">
                    <span className="truncate max-w-[85%]">{f.name}</span>
                    <span>{(f.size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                ))}
              </div>
            )}
            
            {error && <p className="text-xs text-red-400 mt-2 text-center font-semibold">{error}</p>}
            
            <button
              type="submit"
              disabled={loading || !jobTitle || !companyName || !jdText || files.length === 0}
              className="w-full bg-primary hover:bg-indigo-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white font-medium py-3 rounded-xl transition-all shadow-md shadow-primary/20 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4.5 h-4.5 animate-spin" /> Screening candidates...
                </>
              ) : (
                <>
                  Run Batch Screen Checks <ArrowRight className="w-4.5 h-4.5" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Right Side: Rank Candidate spreadsheet results (7 cols) */}
        <div className="lg:col-span-7">
          {loading ? (
            <div className="border border-border bg-card rounded-2xl p-20 flex flex-col items-center justify-center text-center">
              <Loader2 className="w-12 h-12 animate-spin text-primary mb-4" />
              <h3 className="font-heading font-bold text-base text-foreground">Screening Candidates</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs">Extracting data files, loading transformers similarity arrays, and compiling profile summaries...</p>
            </div>
          ) : result ? (
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="border border-border bg-card rounded-2xl overflow-hidden shadow-xl"
            >
              <div className="p-6 border-b border-border flex justify-between items-center bg-[#0f0f0f]">
                <div>
                  <h3 className="font-heading font-bold text-sm text-foreground">Ranked Candidates</h3>
                  <p className="text-[10px] text-muted-foreground mt-0.5">Ordered descending by semantic fit</p>
                </div>
                <FileSpreadsheet className="w-5 h-5 text-primary" />
              </div>

              {/* Candidates list table */}
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground font-semibold bg-neutral-900/50">
                      <th className="py-3 px-4 w-12 text-center">Rank</th>
                      <th className="py-3 px-4">Candidate Name</th>
                      <th className="py-3 px-4 text-center">Compatibility</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.ranked_candidates.map((cand, idx) => (
                      <tr key={idx} className="border-b border-border hover:bg-neutral-900/20 transition-colors">
                        <td className="py-3.5 px-4 text-center font-bold text-foreground">{cand.rank}</td>
                        <td className="py-3.5 px-4 font-medium">
                          <p className="text-foreground">{cand.candidate_name}</p>
                          <p className="text-[10px] text-muted-foreground mt-0.5">{cand.email}</p>
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <span className={`font-bold text-[11px] px-2 py-0.5 rounded-full ${
                            cand.match_score >= 80 
                              ? "bg-accent/10 text-accent border border-accent/25" 
                              : cand.match_score >= 60
                                ? "bg-primary/10 text-primary border border-primary/25"
                                : "bg-neutral-800 text-muted-foreground border border-neutral-700"
                          }`}>
                            {cand.match_score}%
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <button
                            onClick={() => setSelectedCandidate(cand)}
                            className="bg-muted hover:bg-neutral-800 text-foreground p-1.5 rounded-lg border border-border hover:border-primary/30 transition-all flex items-center gap-1.5 ml-auto text-[10px] font-semibold"
                          >
                            <Eye className="w-3.5 h-3.5 text-primary" /> Summary
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          ) : (
            <div className="border border-border bg-card rounded-2xl p-20 flex flex-col items-center justify-center text-center">
              <div className="bg-muted p-4 rounded-full text-muted-foreground mb-4">
                <FileSpreadsheet className="w-8 h-8" />
              </div>
              <h3 className="font-heading font-bold text-base text-foreground">Awaiting Screen Process</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs">Fill out the job specifications and submit candidate resumes to activate vector ranking logs.</p>
            </div>
          )}
        </div>
      </div>

      {/* Candidate Profile Details modal popup */}
      <AnimatePresence>
        {selectedCandidate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/60 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-lg border border-border bg-[#141414] p-6 rounded-2xl relative shadow-2xl space-y-5"
            >
              {/* Close btn */}
              <button 
                onClick={() => setSelectedCandidate(null)}
                className="absolute top-4 right-4 p-1.5 rounded-lg border border-border hover:bg-neutral-800 transition-colors"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>

              {/* Modal Head */}
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-lg">
                  {selectedCandidate.candidate_name[0]}
                </div>
                <div>
                  <h3 className="font-heading font-bold text-lg text-white">{selectedCandidate.candidate_name}</h3>
                  <p className="text-xs text-muted-foreground">{selectedCandidate.email}</p>
                </div>
                <div className="ml-auto text-right">
                  <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">JD Match</span>
                  <p className="font-heading text-2xl font-extrabold text-accent">{selectedCandidate.match_score}%</p>
                </div>
              </div>

              {/* Modal body info cards */}
              <div className="space-y-4 text-xs">
                
                {/* Experience timelines */}
                <div className="border border-border p-3.5 bg-[#0d0d0d]/40 rounded-xl space-y-1">
                  <span className="font-bold text-muted-foreground text-[10px] uppercase">Primary Experience</span>
                  <p className="text-foreground leading-relaxed font-semibold">{selectedCandidate.summary.experience}</p>
                </div>

                {/* Education */}
                <div className="border border-border p-3.5 bg-[#0d0d0d]/40 rounded-xl space-y-1">
                  <span className="font-bold text-muted-foreground text-[10px] uppercase">Education Profile</span>
                  <p className="text-foreground leading-relaxed font-semibold">{selectedCandidate.summary.education}</p>
                </div>

                {/* Skills tags lists */}
                <div className="border border-border p-3.5 bg-[#0d0d0d]/40 rounded-xl space-y-2">
                  <span className="font-bold text-muted-foreground text-[10px] uppercase">Matched Skills ({selectedCandidate.summary.skills.length})</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedCandidate.summary.skills.length === 0 ? (
                      <span className="text-muted-foreground">No matching tech skills tags extracted.</span>
                    ) : (
                      selectedCandidate.summary.skills.map((skill, idx) => (
                        <span key={idx} className="bg-primary/10 border border-primary/20 text-primary text-[9px] font-bold px-2 py-0.5 rounded-md uppercase">
                          {skill}
                        </span>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
