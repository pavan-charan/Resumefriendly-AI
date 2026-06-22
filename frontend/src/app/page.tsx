"use client";

import Link from "next/link";
import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Brain, CheckCircle, FileText, Sparkles, Upload, Activity, 
  ChevronRight, Users, ArrowRight, ShieldCheck, HelpCircle, Briefcase, Star
} from "lucide-react";

export default function LandingPage() {
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#ededed]">
      {/* Dynamic Grid Background Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f1f1f_1px,transparent_1px),linear-gradient(to_bottom,#1f1f1f_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-35" />

      {/* Navigation Toolbar */}
      <header className="sticky top-0 z-50 glass border-b border-border py-4 px-6 md:px-12 flex justify-between items-center">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-primary p-2 rounded-lg text-white">
            <Brain className="w-6 h-6 animate-pulse" />
          </div>
          <span className="font-heading font-bold text-xl tracking-tight bg-gradient-to-r from-white via-neutral-200 to-neutral-400 bg-clip-text text-transparent">
            ResumeFriendly AI
          </span>
        </Link>
        <nav className="hidden md:flex gap-8 text-sm font-medium text-muted-foreground">
          <Link href="#features" className="hover:text-white transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-white transition-colors">How It Works</Link>
          <Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link>
          <Link href="#faq" className="hover:text-white transition-colors">FAQ</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium hover:text-white transition-colors">
            Sign In
          </Link>
          <Link href="/register" className="bg-primary hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-all shadow-[0_0_15px_rgba(99,102,241,0.4)] hover:shadow-[0_0_25px_rgba(99,102,241,0.6)]">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-16 px-6 max-w-6xl mx-auto text-center">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-semibold tracking-wider uppercase mb-8"
        >
          <Sparkles className="w-3.5 h-3.5" /> Next-Gen Hiring Intelligence
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="font-heading text-4xl md:text-6xl font-bold tracking-tight text-white mb-6 leading-tight"
        >
          Optimize Your Resume.<br />
          <span className="bg-gradient-to-r from-primary via-indigo-400 to-accent bg-clip-text text-transparent">
            Automate Screen Checks.
          </span>
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          ResumeFriendly AI uses semantic embedding matrices to audit resumes for modern Applicant Tracking Systems and help recruiters screen candidate batches instantly.
        </motion.p>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <Link href="/register" className="w-full sm:w-auto flex items-center justify-center gap-2 bg-primary hover:bg-indigo-700 text-white font-medium px-8 py-4 rounded-xl transition-all shadow-[0_0_20px_rgba(99,102,241,0.5)]">
            Create Free Account <ArrowRight className="w-4 h-4" />
          </Link>
          <Link href="#how-it-works" className="w-full sm:w-auto border border-border bg-neutral-900/60 hover:bg-neutral-900 text-white font-medium px-8 py-4 rounded-xl transition-colors">
            See How it Works
          </Link>
        </motion.div>

        {/* Dashboard Visual Mockup */}
        <motion.div 
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-16 border border-border/80 rounded-2xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)] relative group bg-[#141414]"
        >
          <div className="absolute top-0 inset-x-0 h-10 bg-neutral-900 border-b border-border flex items-center px-4 gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-red-500/80" />
            <span className="w-3.5 h-3.5 rounded-full bg-yellow-500/80" />
            <span className="w-3.5 h-3.5 rounded-full bg-green-500/80" />
            <span className="text-xs text-muted-foreground ml-4">resumefriendly.ai/dashboard</span>
          </div>
          <div className="pt-10 bg-[#0f0f0f] aspect-[16/9] flex items-center justify-center p-8 relative">
            <div className="w-full h-full border border-dashed border-border/60 rounded-lg flex flex-col items-center justify-center p-6 text-center bg-[#141414]/50">
              <div className="bg-primary/10 border border-primary/20 p-4 rounded-full text-primary mb-4">
                <Upload className="w-8 h-8 animate-bounce" />
              </div>
              <span className="text-lg font-medium text-white mb-2">Simulate ATS Scanning Flow</span>
              <span className="text-sm text-muted-foreground max-w-sm">Create an account to upload PDF or DOCX files and display interactive analytics logs.</span>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 border-t border-border relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">Empowering Both Candidates and Recruiters</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">ResumeFriendly AI packages specialized utilities tailored for job seek compliance and recruiter workflows.</p>
          </div>

          <motion.div 
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid md:grid-cols-3 gap-8"
          >
            {/* Feat 1 */}
            <motion.div variants={itemVariants} className="border border-border bg-[#141414]/40 hover:bg-[#141414]/90 p-8 rounded-2xl transition-all hover:scale-[1.02]">
              <div className="bg-primary/10 border border-primary/20 text-primary w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-2">Automated Resume Parser</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Instantly parses names, contact info, tech skills, education history, and certifications from PDF/DOCX layouts.</p>
            </motion.div>
            
            {/* Feat 2 */}
            <motion.div variants={itemVariants} className="border border-border bg-[#141414]/40 hover:bg-[#141414]/90 p-8 rounded-2xl transition-all hover:scale-[1.02]">
              <div className="bg-accent/10 border border-accent/20 text-accent w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-2">ATS Score Breakdown</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Calculates an algorithmic compatibility score out of 100 based on standard industry weighting metrics.</p>
            </motion.div>

            {/* Feat 3 */}
            <motion.div variants={itemVariants} className="border border-border bg-[#141414]/40 hover:bg-[#141414]/90 p-8 rounded-2xl transition-all hover:scale-[1.02]">
              <div className="bg-primary/10 border border-primary/20 text-primary w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-2">JD Match & Recommendations</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Compares resume text to target descriptions using local Sentence Transformer vector alignments.</p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 px-6 border-t border-border bg-[#0d0d0d]/60 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground">Go from raw file submissions to structured score matrices in seconds.</p>
          </div>

          <div className="grid md:grid-cols-4 gap-8 relative">
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white font-bold mb-4 shadow-[0_0_10px_rgba(99,102,241,0.5)]">1</div>
              <h3 className="font-bold mb-2">Upload Files</h3>
              <p className="text-xs text-muted-foreground">Select candidate resumes or enter targeted job requirements.</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center text-white font-bold mb-4">2</div>
              <h3 className="font-bold mb-2">Structured Parsing</h3>
              <p className="text-xs text-muted-foreground">Our heuristics engine identifies skills, locations, emails, and experience durations.</p>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center text-white font-bold mb-4">3</div>
              <h3 className="font-bold mb-2">Embed & Compare</h3>
              <p className="text-xs text-muted-foreground">Vector transformations match documents semantically against JDs.</p>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center text-white font-bold mb-4">4</div>
              <h3 className="font-bold mb-2">Optimized Audit</h3>
              <p className="text-xs text-muted-foreground">Review actionable feedback lists, ranking spreadsheets, and summaries.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-24 px-6 border-t border-border relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">Loved by Hundreds of Professionals</h2>
            <p className="text-muted-foreground">Hear how job seekers and recruiters optimize hiring loops using our analytics.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="border border-border p-8 rounded-2xl bg-[#141414]/30">
              <div className="flex gap-1 text-yellow-500 mb-4">
                {[...Array(5)].map((_, i) => <Star key={i} className="w-4 h-4 fill-yellow-500" />)}
              </div>
              <p className="text-sm text-muted-foreground italic mb-6 leading-relaxed">
                "I was getting instant automated rejections for software engineering roles. After running my resume through the explainability panel and updating keywords, I landed 3 interviews in two weeks."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary text-sm">AS</div>
                <div>
                  <h4 className="font-bold text-sm text-white">Alex S.</h4>
                  <p className="text-xs text-muted-foreground">Candidate (Full Stack Developer)</p>
                </div>
              </div>
            </div>

            <div className="border border-border p-8 rounded-2xl bg-[#141414]/30">
              <div className="flex gap-1 text-yellow-500 mb-4">
                {[...Array(5)].map((_, i) => <Star key={i} className="w-4 h-4 fill-yellow-500" />)}
              </div>
              <p className="text-sm text-muted-foreground italic mb-6 leading-relaxed">
                "Scanning 150+ resume folders manually used to take hours. Now we just upload the batch and rank candidates instantly based on semantic matching. The candidate summaries are incredibly accurate."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center font-bold text-accent text-sm">SD</div>
                <div>
                  <h4 className="font-bold text-sm text-white">Sarah D.</h4>
                  <p className="text-xs text-muted-foreground">Recruiter (Talent Acquisition Lead)</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 px-6 border-t border-border bg-[#0d0d0d]/60 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-muted-foreground mb-6">Choose a plan tailored to your job hunting or screening scale.</p>
            
            <div className="inline-flex items-center gap-2 border border-border p-1.5 rounded-xl bg-neutral-900">
              <button 
                onClick={() => setBillingPeriod("monthly")} 
                className={`text-xs font-semibold px-4 py-2 rounded-lg transition-colors ${billingPeriod === "monthly" ? "bg-primary text-white" : "text-muted-foreground"}`}
              >
                Monthly
              </button>
              <button 
                onClick={() => setBillingPeriod("yearly")} 
                className={`text-xs font-semibold px-4 py-2 rounded-lg transition-colors ${billingPeriod === "yearly" ? "bg-primary text-white" : "text-muted-foreground"}`}
              >
                Yearly (Save 20%)
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            {/* Free */}
            <div className="border border-border bg-[#141414]/50 p-8 rounded-2xl flex flex-col justify-between">
              <div>
                <span className="text-sm font-semibold text-primary uppercase">Candidate Plan</span>
                <div className="mt-4 flex items-baseline">
                  <span className="text-4xl font-bold text-white">$0</span>
                  <span className="text-sm text-muted-foreground">/ forever</span>
                </div>
                <p className="text-xs text-muted-foreground mt-2">Perfect for single resume tuning and formatting updates.</p>
                <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary" /> 3 Resume uploads per month</li>
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary" /> Full ATS score breakdown</li>
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary" /> Explainability suggestions</li>
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary" /> Side-by-side JD match simulator</li>
                </ul>
              </div>
              <Link href="/register" className="mt-8 block text-center border border-border bg-neutral-900 hover:bg-neutral-800 text-white text-sm font-medium py-3 rounded-lg transition-colors">
                Start Free Optimization
              </Link>
            </div>

            {/* Recruiter */}
            <div className="border border-primary/50 bg-[#141414]/90 p-8 rounded-2xl relative flex flex-col justify-between shadow-[0_0_30px_rgba(99,102,241,0.2)]">
              <div className="absolute -top-3 right-6 bg-primary text-white text-xs font-bold px-3 py-1 rounded-full">RECOMMENDED</div>
              <div>
                <span className="text-sm font-semibold text-accent uppercase">Recruiter Plan</span>
                <div className="mt-4 flex items-baseline">
                  <span className="text-4xl font-bold text-white">
                    {billingPeriod === "monthly" ? "$49" : "$39"}
                  </span>
                  <span className="text-sm text-muted-foreground">/ month</span>
                </div>
                <p className="text-xs text-muted-foreground mt-2">Automate large screening pipelines with batch uploads.</p>
                <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-accent" /> Unlimited job post listings</li>
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-accent" /> Upload up to 100 resumes in a batch</li>
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-accent" /> Vector ranked match tables</li>
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-accent" /> Instant candidate summary card creator</li>
                  <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-accent" /> Local vector search features</li>
                </ul>
              </div>
              <Link href="/register" className="mt-8 block text-center bg-primary hover:bg-indigo-700 text-white text-sm font-medium py-3 rounded-lg transition-colors shadow-lg">
                Get Recruiter Access
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-24 px-6 border-t border-border relative z-10">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-muted-foreground">Answers to common inquiries about the platform.</p>
          </div>

          <div className="space-y-4">
            {[
              {
                q: "What file formats do you support?",
                a: "For Phase 1 MVP, we support PDF (.pdf) and Word (.docx) document uploads. Text extraction operates locally for these formats."
              },
              {
                q: "How does the ATS score engine calculate its values?",
                a: "The score is calculated out of 100 based on custom weighted markers: Skills (30%), Keywords (20%), Experience (20%), Layout Formatting (15%), Education backgrounds (10%), and complete contact profiles (5%)."
              },
              {
                q: "Is my personal resume data kept private?",
                a: "Absolutely. All resume contents, email logs, and extracted metrics are stored locally inside sandboxed configurations and databases."
              },
              {
                q: "Can I swap the local storage with AWS S3 later?",
                a: "Yes. The backend codebase is configured with a LocalStorageManager class that adheres to a clean storage adapter interface, meaning S3 integrations can be connected with minimal configuration edits."
              }
            ].map((faq, idx) => (
              <div key={idx} className="border border-border rounded-xl overflow-hidden bg-[#141414]/30">
                <button 
                  onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                  className="w-full flex justify-between items-center p-6 text-left font-bold text-sm md:text-base hover:bg-neutral-900/50 transition-colors"
                >
                  <span>{faq.q}</span>
                  <HelpCircle className="w-5 h-5 text-muted-foreground" />
                </button>
                {activeFaq === idx && (
                  <div className="p-6 border-t border-border bg-neutral-950/40 text-sm text-muted-foreground leading-relaxed">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer Section */}
      <footer className="border-t border-border py-12 px-6 bg-[#090909] text-center text-sm text-muted-foreground relative z-10">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="bg-primary/20 p-1.5 rounded text-primary">
              <Brain className="w-4 h-4" />
            </div>
            <span className="font-heading font-bold text-white tracking-wide">ResumeFriendly AI</span>
          </div>
          <p>© 2026 ResumeFriendly AI Inc. All rights reserved.</p>
          <div className="flex gap-6">
            <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-white transition-colors">Terms of Service</Link>
            <Link href="#" className="hover:text-white transition-colors">Security Audit</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
