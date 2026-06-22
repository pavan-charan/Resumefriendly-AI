import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import { AuthProvider } from "@/hooks/useAuth";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ResumeFriendly AI - AI-Powered Resume Scoring & Recruiter Screening",
  description: "Optimize your resume score, match against job requirements, and automate screen checks for recruiter dashboards. Designed with premium hiring intelligence.",
  keywords: "ATS Optimizer, Resume Parser, Hiring Intelligence, Job Matching, Resume Scorer, Candidate Screen",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${outfit.variable} antialiased`}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
