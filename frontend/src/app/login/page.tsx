"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Brain, Lock, Mail, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4 relative">
      {/* Background Gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.08),transparent_50%)]" />
      
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md border border-border bg-[#141414]/90 p-8 rounded-2xl relative z-10 shadow-[0_0_40px_rgba(0,0,0,0.5)]"
      >
        <div className="flex flex-col items-center mb-8">
          <Link href="/" className="bg-primary p-2.5 rounded-xl text-white mb-3">
            <Brain className="w-6 h-6" />
          </Link>
          <h1 className="font-heading font-bold text-2xl text-white">Welcome back</h1>
          <p className="text-sm text-muted-foreground mt-1">Sign in to your ResumeFriendly AI account</p>
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

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
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
                placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-3 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-sm text-white placeholder-neutral-600 transition-all outline-none"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Password
              </label>
              <Link href="#" className="text-xs text-primary hover:text-indigo-400">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-muted-foreground">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-3 bg-[#0d0d0d] border border-border focus:border-primary focus:ring-1 focus:ring-primary rounded-xl text-sm text-white placeholder-neutral-600 transition-all outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-indigo-700 text-white font-medium py-3 rounded-xl transition-all shadow-[0_0_15px_rgba(99,102,241,0.4)] flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4.5 h-4.5 animate-spin" /> Signing In...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <p className="mt-8 text-center text-xs text-muted-foreground">
          Don't have an account?{" "}
          <Link href="/register" className="text-primary hover:text-indigo-400 font-medium">
            Sign up
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
