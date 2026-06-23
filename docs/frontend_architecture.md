# Frontend Architecture Document - ResumeFriendly AI

This document establishes the layout principles, component hierarchies, state management solutions, and design tokens for the Next.js 15 App Router web client.

---

## 1. Directory Structure

The frontend application follows a clean feature-based modular design:

```text
frontend/src/
├── app/                  # Next.js 15 routing folder
│   ├── layout.tsx        # Global theme, font configurations, and context wrapper
│   ├── page.tsx          # Marketing Landing Page
│   ├── login/            # Candidate & Recruiter sign-in
│   ├── register/         # User creation
│   └── dashboard/        # Authenticated workspace shell
│       ├── layout.tsx    # Left collapsable menu + header toolbar
│       ├── candidate/    # Candidate score breakdown, keyword matching
│       └── recruiter/    # JD creations, multi-file screening
├── components/           # Reusable UI controls
│   ├── ui/               # Base design system (Button, Input, Alert, Card, Dialog)
│   ├── dashboard/        # Layout elements (sidebar.tsx, navbar.tsx)
│   └── landing/          # Landing sections (hero.tsx, pricing.tsx, footer.tsx)
├── services/             # API client methods
│   └── api.ts            # Axio-like backend client mapping all endpoints
├── hooks/                # Global React hooks
│   └── useAuth.ts        # Dynamic Auth state tracker
├── types/                # Strict TypeScript declaration types
│   └── index.ts          # Request/response interfaces
└── utils/                # Small utility helpers
    └── helpers.ts        # Date and text parsers
```

---

## 2. Design System & Theme

We leverage custom Tailind colors matching premium startup aesthetics (Vercel, Linear, Stripe):
- **Base Mode**: Dark mode by default, supporting toggling to Light mode.
- **Harmony HSL Color Palette**:
  - `background`: Dark Charcoal (`0 0% 4%`) / Light Gray (`0 0% 98%`)
  - `primary`: Modern Indigo (`250 84% 54%`)
  - `accent`: Electric Teal (`170 100% 45%`)
  - `card`: Dark Grey Glass (`0 0% 8%`) / White Card (`0 0% 100%`)
  - `border`: Sleek Outline (`0 0% 15%`) / Soft Line (`0 0% 90%`)
- **Typography**: Primary font family: Google Fonts **Inter** combined with **Outfit** for headings to achieve a modern, premium SaaS feel.

---

## 3. Component Design & Animations

1. **Animation Rules (Framer Motion)**:
   - *Fades*: Soft `opacity` transition on mount (duration: `0.3s`, ease: `easeInOut`).
   - *Button hover/press*: Micro-animations `scale: 1.02` on hover, `scale: 0.98` on click.
   - *Sidebar collapse*: Animate width transition with `spring` dynamics to prevent layout jerks.
2. **Interactive States**:
   - **Skeleton loaders**: Rendered during file upload and API parsing periods.
   - **Empty states**: Illustrated card placeholders prompting resume or job description uploads.
   - **Error banners**: Floating toast notification banners alert the user on parsing failures or credentials mistakes.

---

## 4. State Management Strategy

To maximize reliability and ensure low-latency responsiveness, state management uses:
- **Local React Contexts**:
  - `AuthContext`: Tracks current JWT token, session status, user role, and credentials.
- **Client Hooks**:
  - Data queries and mutations use simple wrappers around standard React lifecycle elements (`useState`, `useEffect`) and axios integrations, keeping state local to the feature components (e.g., candidate matches inside the candidate module) to avoid global store bloat.
- Session Cache:
  - Access tokens are cached in memory.
  - Refresh tokens are stored securely in cookies or `localStorage` to keep the user signed in across page reloads.

---

## 5. Phase 2 Candidate Dashboard Tabs & Interfaces

The Candidate Workspace Dashboard is organized as an interactive multi-tab component layout (using radix-ui tabs or equivalent React components), incorporating:

1. **AI Resume Rewriter Tab**:
   - Selector panel for target job role and tone parameter (Professional, Technical, Executive, Creative).
   - Side-by-side text diff screen displaying original resume sections alongside AI-rewritten bullet points.
   - Version history list letting candidates retrieve past saved iterations.

2. **Interview Prep Tab**:
   - Mock interview configuration panel (difficulty selector, questions count, role spec).
   - Card interface rendering individual question inputs.
   - AI STAR Method Feedback display indicating specific score values (0-10), strengths, and step-by-step suggestions.

3. **Skill Gap Tab**:
   - Readiness gauge/radar chart indicating estimated target role compatibility.
   - Comparative skill list table identifying core missing skills, priority level tags, and associated educational resources.

4. **Career Roadmap Tab**:
   - Interactive milestones timeline detailing target objectives, action plans, and suggested timeline milestones (in months).

5. **Application Tracker Tab**:
   - Kanban-board pipeline tracker displaying current applications in status cards (Applied, Screening, Interviewing, Offer, Rejected, Accepted).
   - Modal forms supporting add/edit details, salary parameters, follow-up dates, and recruiter notes.

6. **Job Match Tab**:
   - Job search listing indicating similarity scores against the candidate's active resume, matched skills, and recommendations.

7. **AI Career Coach Tab**:
   - Scrollable chat message bubble timeline with streaming message blocks.
   - Context panel referencing the candidate's active parsed resume.
   - Thread list enabling the candidate to manage multiple historic coaching discussions.

