"use client";

import { useState } from "react";
import Link from "next/navigation";
import LinkWrapper from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Brain, Lock, Mail, User as UserIcon, AlertCircle, Loader2, Users, Briefcase } from "lucide-react";
import { motion } from "framer-motion";

export default function RegisterPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"CANDIDATE" | "RECRUITER">("CANDIDATE");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await register({
        email,
        password,
        first_name: firstName || undefined,
        last_name: lastName || undefined,
        role
      });
    } catch (err: any) {
      setError(err.message || "Registration failed. Please check inputs.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4 py-8 relative">
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.08),transparent_50%)]" />

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md border border-border bg-[#141414]/90 p-8 rounded-2xl relative z-10 shadow-[0_0_40px_rgba(0,0,0,0.5)]"
      >
        <div className="flex flex-col items-center mb-6">
          <LinkWrapper href="/" className="bg-primary p-2.5 rounded-xl text-white mb-3">
            <Brain className="w-6 h-6" />
          </LinkWrapper>
          <h1 className="font-heading font-bold text-2xl text-white">Create Account</h1>
          <p className="text-sm text-muted-foreground mt-1">Get started with ResumeFriendly AI today</p>
        </div>

        {error && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 text-xs flex gap-2.5 items-start"
          >
            <AlertCircle className="w-4.5 h-4.5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Role Tab Selector */}
          <div>
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Select Your Role
            </label>
            <div className="grid grid-cols-2 gap-2 border border-border p-1.5 rounded-xl bg-[#0d0d0d]">
              <button
                type="button"
                onClick={() => setRole("CANDIDATE")}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  role === "CANDIDATE" 
                    ? "bg-primary text-white shadow-md" 
                    : "text-muted-foreground hover:text-white"
                }`}
              >
                <Users className="w-3.5 h-3.5" /> Candidate
              </button>
              <button
                type="button"
                onClick={() => setRole("RECRUITER")}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  role === "RECRUITER" 
                    ? "bg-primary text-white shadow-md" 
                    : "text-muted-foreground hover:text-white"
                }`}
              >
                <Briefcase className="w-3.5 h-3.5" /> Recruiter
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
                First Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-muted-foreground">
                  <UserIcon className="w-4 h-4" />
                </span>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="Alex"
                  className="w-full pl-10 pr-3 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-sm text-white placeholder-neutral-600 transition-all outline-none"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
                Last Name
              </label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Smith"
                className="w-full px-3 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-sm text-white placeholder-neutral-600 transition-all outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-muted-foreground">
                <Mail className="w-4 h-4" />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex.smith@example.com"
                className="w-full pl-10 pr-4 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-sm text-white placeholder-neutral-600 transition-all outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
              Password (min. 6 characters)
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-muted-foreground">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-sm text-white placeholder-neutral-600 transition-all outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-indigo-700 text-white font-medium py-3 rounded-xl transition-all shadow-[0_0_15px_rgba(99,102,241,0.4)] flex items-center justify-center gap-2 mt-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4.5 h-4.5 animate-spin" /> Registering...
              </>
            ) : (
              "Sign Up"
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Already have an account?{" "}
          <LinkWrapper href="/login" className="text-primary hover:text-indigo-400 font-medium">
            Sign in
          </LinkWrapper>
        </p>
      </motion.div>
    </div>
  );
}
