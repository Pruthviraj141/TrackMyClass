# TrackMyClass — 60-Minute Autonomous Upgrade Mission

> **How to use this file:** In Antigravity, open the **Agent Manager** surface (not an inline Editor chat — you want an async, long-running task, not a synchronous back-and-forth). Start a new agent task in your `TrackMyClass` workspace, paste everything below as the initial task, and let it run. Check the **Artifacts** panel occasionally (task list, screenshots, browser recordings) — you can leave comments directly on an Artifact if you want to redirect it, and it will absorb that feedback without stopping its execution loop. Don't reply in chat unless something is actually broken; the whole point of this prompt is that it doesn't need you to.

---

## ROLE & OPERATING MODE

You are acting as a senior staff frontend engineer and product designer embedded on the TrackMyClass team. You have **full autonomy for the next ~60 minutes**. There is no human available to answer questions during this session.

Rules of engagement — these override your default instincts to check in:

1. **Never pause execution to ask a clarifying question.** When you hit an ambiguous decision, pick the most defensible, production-grade default, write a one-line rationale to `docs/DECISIONS.md`, and keep moving.
2. **Work in a continuous loop:** plan → implement → verify visually (via the browser subagent, at both a mobile and a desktop viewport) → fix → commit → next task. Do not stop after a single file or a single component and wait.
3. **Maintain a living task-list Artifact** and check items off as you go, so progress is visible even when I'm not watching.
4. **Commit to git after every working checkpoint** — small, atomic commits — so nothing is ever left in a broken, uncommitted state if the hour runs out mid-task.
5. **Time-box yourself against the phase plan below.** Track elapsed time. If you're running behind, cut scope from the *bottom* of the priority list — never leave the app unbuildable or visually broken just to "finish" everything on the list.

---

## PROJECT CONTEXT

TrackMyClass is a real-time facial recognition attendance system, currently working and deployed on AWS EC2:

- **Backend**: Python 3.10+, FastAPI, Uvicorn. `facenet-pytorch` (MTCNN for detection, FaceNet/InceptionResnetV1 for 512-D embeddings), OpenCV. SQLite or Firebase Firestore behind an abstracted DB layer. Deployed via Docker + Nginx + Gunicorn/Uvicorn on EC2.
- **Current frontend**: HTML5 + vanilla JS (MediaDevices API for camera) + Jinja2 server-rendered templates. This is what you are replacing.
- **Key existing endpoints** (verify exact paths/shapes in the real repo, don't trust this list blindly): `POST /api/v1/register/camera` (student registration + face capture), `POST /api/v1/attendance/process_frame` (live frame → bounding boxes + recognized names), plus session/dashboard/report endpoints under `/admin`.
- **Existing flows to preserve functionally**: student self-registration with a single-face check; admin login → dashboard → start a session → live `/monitor` view with bounding boxes and a `TemporalTracker`-backed "N consecutive frames" confirmation before marking present → end session → export Excel/PDF report.

Do not take this summary as gospel — **Phase 0 below requires you to verify it against the actual code.**

---

## MISSION

Rebuild TrackMyClass's frontend from server-rendered Jinja2 + vanilla JS into a modern, production-grade **React** application that looks and feels like a funded startup's product — not a tutorial project or an AI-scaffolded admin template. Correctly re-architect the routing/navigation for the whole app. The FastAPI backend's existing API contracts are the source of truth; extend them minimally, and only when the UI genuinely needs it.

---

## HARD CONSTRAINTS

- Do **not** break the existing working FastAPI backend or its deployed behavior on EC2. Treat `backend/` as an API-only service going forward; enable CORS for local dev against the new frontend.
- New frontend lives in `frontend/` (Vite). **Move** the old Jinja2 templates to `legacy/` rather than deleting them — don't destroy a working fallback while migration is incomplete.
- Everything must build cleanly: `npm run build` must succeed with **zero TypeScript errors** before any phase counts as "done."
- Everything must be responsive from a **360px** mobile viewport up through **1440px** desktop. Test both — not just one and assume the other works.

---

## TECH STACK

Use this stack; don't improvise a different one mid-session.

- **React 18+, TypeScript, Vite**
- **Tailwind CSS** (latest) + **shadcn/ui** (Radix primitives) as the component foundation — but heavily re-themed (see Design Principles). Do **not** ship the default shadcn zinc/slate look untouched.
- **React Router** (latest data router, v6/v7) for all routing, with nested layout routes
- **TanStack Query** for all server-state and data fetching against the FastAPI backend
- **React Hook Form + Zod** for the registration form and any admin forms
- **Framer Motion** for purposeful micro-interactions — not gratuitous animation everywhere
- **Recharts** or **Tremor** for dashboard stats/charts
- **Lucide-react** for icons, **Sonner** for toasts
- **Zustand** (or Context — your call, document it) for lightweight client state: active session, auth token

---

## DESIGN PRINCIPLES — THIS IS THE PART MOST LIKELY TO GO WRONG

The single biggest failure mode to avoid: **this must not look like a generic AI-scaffolded admin template.** Concretely:

- Before writing a single component, pick and commit to a **real, specific brand identity** for TrackMyClass: a distinct primary color (not the default indigo-to-violet gradient every AI demo reaches for), a real typeface pairing (e.g. a geometric sans for headings + Inter/Geist for body — pick one and use it consistently), and a defined spacing/radius/elevation system. Encode this as Tailwind theme config / CSS variables and document it briefly in `frontend/src/styles/design-tokens.md`.
- No centered-card-on-gray-background cliché for register/login. No untouched default shadcn palette. No stock gradient hero blobs.
- The **admin dashboard and live monitor** are dense, data-tool UIs — think Linear or Vercel's dashboard density, not a spaced-out marketing page. The **registration screen** can be warmer and more consumer-friendly, since students use it on their phones.
- Real empty states, real skeleton loaders (not spinners everywhere), real error states — for every screen that fetches data. If a backend endpoint doesn't exist yet, show an honest "not available yet" state — never fabricate numbers or fake data to make a screen look populated.
- **`/admin/sessions/:sessionId/monitor` is the hero screen of the entire product.** Camera feed with a canvas overlay drawing bounding boxes + recognized name + confidence, a live-updating present/absent roster beside it, a session timer, and a present-count. This should feel like a real-time ops console, not a webcam demo.
- Motion should be purposeful and specific: a roster row animating in when a student is confirmed present, a subtle pulse on the live indicator, page transitions on route change — not decorative spinners and fade-ins on everything.

---

## ROUTE ARCHITECTURE

Implement exactly this (adjust only if Phase 0's audit of the real repo surfaces a meaningful reason to differ — log any such deviation in `docs/DECISIONS.md`):

**Public**
- `/` — marketing/landing page for the institution deploying TrackMyClass, with a clear CTA into `/register`
- `/register` — student self-registration (name, roll number, department, camera capture) — **mobile-first**, this is primarily used on phones
- `/login` — admin/teacher login

**Admin** — protected by an auth guard, wrapped in a persistent layout shell (sidebar on desktop, collapsible into a bottom nav or drawer on mobile) with a top bar showing the active session / live indicator
- `/admin` → redirect to `/admin/dashboard`
- `/admin/dashboard` — today's stats, recent sessions, quick actions
- `/admin/sessions` — list/create class sessions
- `/admin/sessions/:sessionId/monitor` — the live recognition console (hero screen, see above)
- `/admin/students` — registered students directory, search/filter
- `/admin/reports` — attendance history, Excel/PDF export
- `/admin/settings` — recognition threshold, camera source, etc. — only if the backend actually supports it; otherwise a clearly-labeled "coming soon" stub, not fake controls

---

## EXECUTION PLAN — WORK THESE PHASES IN ORDER

**Phase 0 — Audit (~5 min).** Actually open and read the real repository. Confirm the real FastAPI route paths, request/response shapes, and DB fields in `backend/routers/` and `backend/models/` — do not assume the summary above is fully accurate. Write your findings and your working plan into `docs/PLAN.md` as your task-list artifact.

**Phase 1 — Scaffold (~5–8 min).** `npm create vite@latest frontend -- --template react-ts`; install the stack above; init Tailwind + shadcn; set up design tokens; stub out every route above with React Router; set up a TanStack Query client and an `src/lib/api.ts` client pointed at the FastAPI base URL via `.env`. Prove CORS works end-to-end with one trivial real request before moving on.

**Phase 2 — Design system (~5 min).** Build the reusable primitives once, themed per the Design Principles: Button, Card, Input, Badge, Skeleton, the admin layout shell (sidebar/topbar/mobile nav). Every later screen reuses these — don't reinvent per page.

**Phase 3 — Student registration flow (~10 min).** `/register`: RHF+Zod validated form, camera capture component (`getUserMedia`, rear camera preferred on mobile, works on mobile Safari and Chrome), base64 capture posted to the real registration endpoint, loading state, success state, and a clear retry UX for "no face / multiple faces detected."

**Phase 4 — Admin auth + dashboard (~8 min).** `/login`, a route guard, `/admin/dashboard` pulling real stats from the backend where endpoints exist — honest zero/empty states where they don't. No fabricated numbers.

**Phase 5 — Live monitor console (~12–15 min, the centerpiece).** Webcam stream, a canvas overlay sized/positioned to match the video element, frames posted to `process_frame` at a sane interval, bounding boxes + name + confidence drawn from the real response, a live roster panel of present students, session start/stop controls, elapsed timer.

**Phase 6 — Reports / students directory (~5–8 min).** Searchable/sortable/paginated table (client-side pagination is fine), export buttons wired to whatever the backend already exposes.

**Phase 7 — Mobile QA + polish (~5–8 min).** Use the browser subagent to load every route at ~390px and ~1440px, screenshot each, fix overflow/touch-target/contrast issues, and specifically verify the camera flows on the mobile viewport.

**Phase 8 — Final verification + handoff report (~5 min).** Full `npm run build`, fix any remaining errors, commit, then write `docs/SESSION_REPORT.md`: what's done, what's stubbed or mocked, what's genuinely left, every autonomous decision you made and why, and exact next steps for me. This is the first thing I'll read when I sit back down.

---

## THE VERIFICATION LOOP (repeat continuously — this is the actual "loop")

For every screen or feature: implement → run it locally → use the browser subagent to load the real page and **screenshot it at both viewports** → look critically at your own screenshot and ask "would this pass as a real funded startup's UI, or does it read as a scaffold?" → fix what doesn't → check the browser console for errors → commit → tick the task-list artifact → move on. **Never mark something done without having actually seen it render.**

---

## DEFINITION OF DONE FOR THIS SESSION

- `npm run build` succeeds with zero TypeScript errors
- Every route above renders without crashing at both 390px and 1440px
- Registration works end-to-end against the real backend, or is clearly flagged as blocked with a specific reason in the session report
- The live monitor screen is visually the strongest screen in the app
- `docs/SESSION_REPORT.md` exists and is honest about what's real vs. mocked
- Everything is committed to git in small, reviewable commits

**Begin with Phase 0 now. Do not wait for confirmation.**
