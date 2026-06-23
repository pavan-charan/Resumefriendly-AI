"use client";

import { useState, useEffect } from "react";
import { api } from "@/services/api";
import { RecruiterScreenResult, RankedCandidate } from "@/types";
import { 
  Users, CheckCircle, Upload, Search, Activity, Sparkles, 
  ArrowRight, Loader2, FileSpreadsheet, Eye, ChevronRight, X, Brain, Briefcase
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useSearchParams, useRouter } from "next/navigation";

export default function RecruiterDashboard() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const currentTab = searchParams.get("tab") || "screen";

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

  // Job listings tab states
  const [jobs, setJobs] = useState<any[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(false);

  useEffect(() => {
    if (currentTab === "jobs") {
      fetchJobs();
    }
  }, [currentTab]);

  const fetchJobs = async () => {
    setLoadingJobs(true);
    setError(null);
    try {
      const data = await api.getRecruiterJobs();
      setJobs(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch job specifications.");
    } finally {
      setLoadingJobs(false);
    }
  };

  const selectJob = async (jobId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getJobScreeningResults(jobId);
      const selectedJob = jobs.find(j => j.id === jobId);
      if (selectedJob) {
        setJobTitle(selectedJob.title);
        setCompanyName(selectedJob.company_name);
        setDepartment(selectedJob.department || "");
        setJdText(selectedJob.raw_content);
      }
      setResult(data);
      router.push("/dashboard/recruiter?tab=screen");
    } catch (err: any) {
      setError(err.message || "Failed to load job screening results");
    } finally {
      setLoading(false);
    }
  };

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

  const handleExportExcel = () => {
    console.log("handleExportExcel triggered");
    const currentResult = result;
    if (!currentResult) {
      console.warn("Export aborted: result is null");
      return;
    }
    if (!currentResult.ranked_candidates || currentResult.ranked_candidates.length === 0) {
      console.warn("Export aborted: ranked_candidates list is empty");
      return;
    }

    try {
      // CSV Headers
      const headers = [
        "Rank",
        "Candidate Name",
        "Email",
        "Match Score (%)",
        "College Name",
        "Graduation Start Year",
        "Graduation End Year",
        "Matched Skills",
        "Primary Experience",
        "Education Profile"
      ];

      // Build CSV Rows safely ensuring no null reference crashes
      const rows = currentResult.ranked_candidates.map(cand => {
        const rank = cand.rank || 0;
        const name = (cand.candidate_name || "Unknown").replace(/"/g, '""');
        const email = (cand.email || "").replace(/"/g, '""');
        const score = cand.match_score || 0;
        const college = (cand.summary?.college_name || "N/A").replace(/"/g, '""');
        const gradStart = (cand.summary?.graduation_start_year || "N/A").replace(/"/g, '""');
        const gradEnd = (cand.summary?.graduation_end_year || "N/A").replace(/"/g, '""');
        const skills = ((cand.summary && cand.summary.skills) || []).join(", ").replace(/"/g, '""');
        const exp = ((cand.summary && cand.summary.experience) || "").replace(/"/g, '""').replace(/\n/g, ' ');
        const edu = ((cand.summary && cand.summary.education) || "").replace(/"/g, '""').replace(/\n/g, ' ');
        
        return [
          rank,
          `"${name}"`,
          `"${email}"`,
          score,
          `"${college}"`,
          `"${gradStart}"`,
          `"${gradEnd}"`,
          `"${skills}"`,
          `"${exp}"`,
          `"${edu}"`
        ];
      });

      const csvContent = [
        headers.join(","),
        ...rows.map(row => row.join(","))
      ].join("\n");

      console.log("CSV Content compiled successfully. Length:", csvContent.length);

      // Create a Data URI with UTF-8 BOM to ensure Excel opens special characters correctly
      const BOM = "\uFEFF";
      const csvDataUri = "data:text/csv;charset=utf-8," + BOM + encodeURIComponent(csvContent);
      
      const link = document.createElement("a");
      link.setAttribute("href", csvDataUri);
      
      // File name: ranked_candidates_JobTitle_Company.csv
      const formattedJob = (jobTitle || "").replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const filename = `ranked_candidates_${formattedJob || "screener"}.csv`;
      
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log("Export download triggered successfully for:", filename);
    } catch (err) {
      console.error("Failed to generate and download CSV:", err);
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

      {currentTab === "jobs" ? (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-heading font-bold text-lg text-foreground flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-primary" /> Previous Job Screenings ({jobs.length})
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5">Select a past job description to reload its ranked candidates</p>
            </div>
            <button
              type="button"
              onClick={fetchJobs}
              className="bg-muted hover:bg-neutral-800 text-foreground text-xs font-semibold py-2 px-4 rounded-xl border border-border transition-colors flex items-center gap-2"
            >
              {loadingJobs ? <Loader2 className="w-3.5 h-3.5 animate-spin text-primary" /> : "Refresh List"}
            </button>
          </div>

          {loadingJobs ? (
            <div className="border border-border bg-card rounded-2xl p-20 text-center flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">Loading historical job postings...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="border border-border bg-card rounded-2xl p-20 flex flex-col items-center justify-center text-center">
              <div className="bg-muted p-4 rounded-full text-muted-foreground mb-4">
                <Briefcase className="w-8 h-8" />
              </div>
              <h3 className="font-heading font-bold text-base text-foreground">No jobs screened yet</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs">Use the Screening Dashboard to perform candidate comparisons against a target specification.</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.map((job) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ y: -4 }}
                  className="border border-border bg-card hover:border-primary/40 rounded-2xl p-5 space-y-4 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
                  onClick={() => selectJob(job.id)}
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 bg-primary/10 border border-primary/20 text-primary rounded-full">
                        {job.department || "General"}
                      </span>
                    </div>
                    <h4 className="font-heading font-bold text-sm text-foreground line-clamp-1">{job.title}</h4>
                    <p className="text-[10px] text-muted-foreground">{job.company_name}</p>
                    <p className="text-[10px] text-muted-foreground line-clamp-3 leading-relaxed mt-2 bg-[#0a0a0a]/50 p-2.5 rounded-xl border border-neutral-900/60 min-h-[60px]">
                      {job.raw_content}
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between pt-3 border-t border-border mt-2 text-[9px] text-muted-foreground">
                    <span>Created: {new Date(job.created_at).toLocaleDateString()}</span>
                    <span className="text-primary font-bold flex items-center gap-1">
                      View Rankings <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      ) : (
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
                  <button
                    type="button"
                    onClick={handleExportExcel}
                    className="bg-primary/20 hover:bg-primary/30 text-primary border border-primary/30 py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all"
                  >
                    <FileSpreadsheet className="w-4 h-4" /> Export Excel (CSV)
                  </button>
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
      )}

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
