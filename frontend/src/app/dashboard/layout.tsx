"use client";

import { useEffect, useState, Suspense } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import Link from "next/link";
import { 
  Brain, FileText, CheckSquare, Settings, LogOut, Menu, X, 
  Bell, Sun, Moon, Loader2, Sparkles, User as UserIcon
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function SidebarNav({ navigation, pathname }: { navigation: any[]; pathname: string }) {
  const searchParams = useSearchParams();
  const currentTab = searchParams.get("tab") || "ats";

  return (
    <nav className="space-y-1.5">
      {navigation.map((item, idx) => {
        const Icon = item.icon;
        const isActive = item.activeKey
          ? (pathname === "/dashboard/candidate" || pathname === "/dashboard/recruiter") && currentTab === item.activeKey
          : pathname === item.href;

        return (
          <Link
            key={idx}
            href={item.href}
            className={`flex items-center gap-3 py-2.5 px-4 rounded-xl text-xs font-semibold tracking-wide transition-all ${
              isActive
                ? "bg-primary text-white shadow-md shadow-primary/20"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            <Icon className="w-4.5 h-4.5" />
            {item.name}
          </Link>
        );
      })}
    </nav>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [showNotifications, setShowNotifications] = useState(false);

  // Authenticate and check authorization
  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    if (typeof window !== "undefined") {
      const html = document.documentElement;
      if (newTheme === "light") {
        html.classList.remove("dark");
        html.classList.add("light");
      } else {
        html.classList.remove("light");
        html.classList.add("dark");
      }
    }
  };

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex flex-col items-center justify-center text-muted-foreground gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <span className="text-sm font-medium">Loading session...</span>
      </div>
    );
  }

  const isRecruiter = user.role === "RECRUITER" || user.role === "ADMIN";

  const navigation = isRecruiter 
    ? [
        { name: "Screening Dashboard", href: "/dashboard/recruiter?tab=screen", icon: CheckSquare, activeKey: "screen" },
        { name: "Job Listings", href: "/dashboard/recruiter?tab=jobs", icon: Brain, activeKey: "jobs" },
        { name: "Settings", href: "#", icon: Settings },
      ]
    : [
        { name: "ATS Optimizer", href: "/dashboard/candidate?tab=ats", icon: FileText, activeKey: "ats" },
        { name: "JD Matcher", href: "/dashboard/candidate?tab=jd", icon: Brain, activeKey: "jd" },
        { name: "Settings", href: "#", icon: Settings },
      ];

  return (
    <div className={`min-h-screen ${theme === "dark" ? "bg-[#0a0a0a] text-[#ededed]" : "bg-[#fafafa] text-[#171717]"} flex`}>
      {/* Sidebar Navigation */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.aside 
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 260, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className={`border-r border-border h-screen sticky top-0 flex flex-col justify-between p-4 z-40 shrink-0 ${
              theme === "dark" ? "bg-[#141414]" : "bg-white"
            }`}
          >
            <div>
              {/* App Brand Header */}
              <div className="flex justify-between items-center mb-8 px-2">
                <Link href="/" className="flex items-center gap-2">
                  <div className="bg-primary p-1.5 rounded-lg text-white">
                    <Brain className="w-5 h-5" />
                  </div>
                  <span className="font-heading font-bold text-sm tracking-tight bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                    ResumeFriendly
                  </span>
                </Link>
                <button 
                  onClick={() => setSidebarOpen(false)}
                  className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Nav Items */}
              <Suspense fallback={<div className="h-28" />}>
                <SidebarNav navigation={navigation} pathname={pathname} />
              </Suspense>
            </div>

            {/* User Profile Card Footer */}
            <div className="border-t border-border pt-4 px-2 space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm uppercase">
                  {user.first_name ? user.first_name[0] : user.email[0]}
                </div>
                <div className="overflow-hidden">
                  <h4 className="font-bold text-xs truncate">
                    {user.first_name ? `${user.first_name} ${user.last_name || ""}` : "Candidate"}
                  </h4>
                  <p className="text-[10px] text-muted-foreground truncate">{user.email}</p>
                </div>
              </div>
              <button 
                onClick={logout}
                className="w-full flex items-center justify-center gap-2 border border-border py-2 rounded-xl text-xs font-medium hover:bg-red-500/10 hover:text-red-500 hover:border-red-500/30 transition-all"
              >
                <LogOut className="w-3.5 h-3.5" /> Sign Out
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header Toolbar */}
        <header className={`sticky top-0 z-30 border-b border-border py-3 px-6 md:px-8 flex justify-between items-center shrink-0 ${
          theme === "dark" ? "bg-[#0a0a0a]/90" : "bg-[#fafafa]/90"
        } backdrop-blur-md`}>
          <div className="flex items-center gap-4">
            {!sidebarOpen && (
              <button 
                onClick={() => setSidebarOpen(true)}
                className="p-1.5 rounded-lg border border-border hover:bg-muted transition-colors"
              >
                <Menu className="w-4.5 h-4.5" />
              </button>
            )}
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold bg-muted text-muted-foreground px-2.5 py-1 rounded-full uppercase tracking-wider">
                {user.role}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Notifications Menu */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-xl border border-border hover:bg-muted text-muted-foreground hover:text-foreground transition-all relative"
              >
                <Bell className="w-4.5 h-4.5" />
                <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-primary" />
              </button>
              
              <AnimatePresence>
                {showNotifications && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className={`absolute right-0 mt-3 w-80 border border-border rounded-2xl p-4 shadow-xl z-50 space-y-3 ${
                      theme === "dark" ? "bg-[#141414]" : "bg-white"
                    }`}
                  >
                    <div className="flex justify-between items-center pb-2 border-b border-border">
                      <h4 className="font-bold text-xs text-foreground">Notifications</h4>
                      <button className="text-[10px] text-primary hover:underline">Clear all</button>
                    </div>
                    <div className="text-xs space-y-2.5 text-muted-foreground max-h-60 overflow-y-auto">
                      <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-foreground">
                        <p className="font-semibold text-[11px] text-primary">System Ready</p>
                        <p className="text-[10px] mt-0.5">Welcome to ResumeFriendly AI. Start optimizing your document files.</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Dark Mode Switcher */}
            <button 
              onClick={toggleTheme}
              className="p-2 rounded-xl border border-border hover:bg-muted text-muted-foreground hover:text-foreground transition-all"
            >
              {theme === "dark" ? <Sun className="w-4.5 h-4.5" /> : <Moon className="w-4.5 h-4.5" />}
            </button>
          </div>
        </header>

        {/* Content Panel Scroll */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
