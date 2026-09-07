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

Rebuild TrackMyClass's frontend from server-rendered Jinja2 + vanilla JS into a modern, production-grade **React** application that looks and feels like a funded startup's product — not a tutorial project, a student assignment, or an AI-scaffolded admin template. Correctly re-architect the routing/navigation for the whole app, including a new institution-gated entry flow (see Route Architecture below). The FastAPI backend's existing API contracts are the source of truth; extend them minimally, and only when the UI genuinely needs it.

**Primary user reality check:** the person opening this app most often is a teacher, standing in a classroom, on their phone — not a developer on a 27" monitor. Judge every screen first at mobile width, and first for how it feels to a non-technical adult under time pressure. If it wouldn't feel fast and trustworthy on a school-issued Android phone with average Wi-Fi, it isn't done.

---

## HARD CONSTRAINTS

- Do **not** break the existing working FastAPI backend or its deployed behavior on EC2. Treat `backend/` as an API-only service going forward; enable CORS for local dev against the new frontend.
- New frontend lives in `frontend/` (Vite). **Move** the old Jinja2 templates to `legacy/` rather than deleting them — don't destroy a working fallback while migration is incomplete.
- Everything must build cleanly: `npm run build` must succeed with **zero TypeScript errors** before any phase counts as "done."
- Everything must be responsive from a **360px** mobile viewport up through **1440px** desktop. Test both — not just one and assume the other works.
- The college-code gate must be a real backend concept, not a frontend illusion. If the real repo has no notion of an "institution" yet, add the smallest possible additive model/endpoint for it — e.g. a table of `{code, name, active}` and a public `POST /api/v1/institutions/verify-code` returning `{valid, institutionName}`. Never modify or break the shape of the existing registration/attendance endpoints to do this — add, don't rewrite. If you run out of time before wiring true per-institution data scoping end-to-end, it's fine to ship the gate against a minimal/stubbed check — but say so plainly in the session report, don't silently fake it as fully wired.

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

The single biggest failure mode: **this must not look like a generic AI-scaffolded admin template**, and it must not read as a student side-project either — it needs to feel like a small, well-funded startup's product. Ground every decision in real, shipped products, not in your own default instincts.

**Study these, don't clone them — extract the specific pattern, then apply it to TrackMyClass's own brand:**
- **Linear** — radical restraint: near-monochrome surfaces, exactly one accent color, quiet low-contrast borders, information density that never feels crowded because everything non-essential is simply absent. This is the reference for the admin shell's overall chrome.
- **Stripe** — data tables as the primary interface: impeccable column alignment, inline sparklines, drill-downs that never lose your place. Apply this to `/:collegeCode/admin/students` and `/:collegeCode/admin/reports`.
- **Mercury / Ramp** — the fintech-trust pattern: lead with *one* clear number ("24 / 30 present"), never a wall of data. A teacher opening this mid-class needs reassurance in half a second, not a dashboard to decode. This is the emotional register for the dashboard and the monitor's roster panel.
- **Notion** — progressive disclosure and generous whitespace on tools people open dozens of times a day, so daily use doesn't fatigue the user.
- **The category incumbents, as a cautionary reference, not a template:** ClassDojo and Seesaw are the default teacher-facing apps, and teachers commonly describe both as having gotten cluttered and "clunky" as they've grown. The opening here is to be the calmer, faster, more trustworthy alternative — not to out-cute them with mascots, points, or gamification. TrackMyClass should feel closer to a fintech ops tool a teacher happens to use than to a classroom-rewards app.

**Explicitly banned — these are the exact tells of an AI-generated site, avoid every one of them:**
- Inter (or any system font) used completely untouched with zero customization, as the only typeface
- Any indigo-to-violet / blue-to-purple gradient, anywhere — hero background, buttons, icons
- Vague hero copy like "Build the future of attendance" or "Empowering education with AI" — write real, specific copy about what the product actually does
- Uniform 16px border-radius on every single card/button/input with no variation or intent
- Stock "undraw"-style illustrated people, generic 3D blob shapes, or generic AI-generated hero photography
- The default centered-hero-plus-two-CTA-buttons ("Get Started" / "Learn More") landing skeleton
- Glassmorphism used as a default rather than a deliberate, sparing choice
- Emoji-heavy microcopy or exclamation-mark enthusiasm in UI text

**Mobile is the primary design mode, not a breakpoint to check afterward** — because the primary user is a teacher on a phone:
- Primary actions live in a thumb-reachable zone; consider a sticky bottom action bar for the monitor screen's start/stop/end-session controls
- Minimum 44px touch targets everywhere; nothing depends on hover
- Use bottom sheets/drawers for admin navigation on mobile instead of a squeezed sidebar — reserve the persistent sidebar for desktop widths
- Skeleton loaders instead of spinners, so layout never jumps when data loads over a school's patchy Wi-Fi
- Design for one-handed operability: a teacher is often holding the phone in one hand

**Screen-specific direction:**
- Real empty states, real skeleton loaders, real error states for every screen that fetches data. If a backend endpoint doesn't exist yet, show an honest "not available yet" state — never fabricate numbers to make a screen look populated.
- **The live monitor console is the hero screen of the entire product.** Camera feed with a canvas overlay drawing bounding boxes + recognized name + confidence, a live-updating present/absent roster beside it, a session timer, and a present-count front and center. This should feel like a real-time ops console, not a webcam demo.
- Motion should be purposeful and specific: a roster row animating in when a student is confirmed present, a subtle pulse on the live indicator, page transitions on route change — not decorative spinners and fade-ins on everything.
- **The antidote to "AI slop" is restraint, not decoration:** fewer colors, fewer font weights, one confident accent color used consistently, real specific copy grounded in what this product does — not generic SaaS marketing language.

---

## ROUTE ARCHITECTURE

Implement exactly this (adjust only if Phase 0's audit of the real repo surfaces a meaningful reason to differ — log any such deviation in `docs/DECISIONS.md`):

**Entry flow — no direct path into Register or Admin without a valid college code:**
- `/` — landing page. Hero explaining what TrackMyClass is, plus a single primary flow: an inline "Enter your college code" input + submit — not a link the visitor has to go find, and not a modal that hides the product's identity. **Do not show Register or Admin Login as options on `/` before a valid code is entered.**
- On submit, the code is validated against the backend. A valid code navigates to `/:collegeCode` — a lightweight institution portal screen that confirms the institution by name (builds trust: "you found the right college") and only now presents two clear paths: **"I'm a Student — Register"** and **"I'm a Teacher / Admin — Sign In."**
- An invalid code shows a clear, specific inline error on `/` — never a generic toast, never a full-page error.

**Deep-linking exception:** if a visitor lands directly on `/:collegeCode/register` or `/:collegeCode/login` (e.g. from a QR code the college printed and stuck on a classroom wall — a realistic distribution channel for this product), validate the code silently in the background and proceed straight in; don't force them back through `/` first.

**Scoped public routes:**
- `/:collegeCode/register` — student self-registration (name, roll number, department, camera capture), scoped to that institution — **mobile-first**, this is primarily used on phones
- `/:collegeCode/login` — admin/teacher login, scoped to that institution

**Admin** — protected by an auth guard, nested under the resolved college code, wrapped in a persistent layout shell (sidebar on desktop, collapsible into a bottom nav or drawer on mobile) with a top bar showing the active session / live indicator
- `/:collegeCode/admin` → redirect to `/:collegeCode/admin/dashboard`
- `/:collegeCode/admin/dashboard` — today's stats, recent sessions, quick actions
- `/:collegeCode/admin/sessions` — list/create class sessions
- `/:collegeCode/admin/sessions/:sessionId/monitor` — the live recognition console (hero screen, see Design Principles)
- `/:collegeCode/admin/students` — registered students directory, search/filter
- `/:collegeCode/admin/reports` — attendance history, Excel/PDF export
- `/:collegeCode/admin/settings` — recognition threshold, camera source, etc. — only if the backend actually supports it; otherwise a clearly-labeled "coming soon" stub, not fake controls

**Client state:** once a code is verified, persist `{collegeCode, institutionName, institutionId}` in Zustand plus `sessionStorage` so a teacher isn't re-typing the code every time they reopen the app within the same session/device.

---

## EXECUTION PLAN — WORK THESE PHASES IN ORDER

**Phase 0 — Audit (~5 min).** Actually open and read the real repository. Confirm the real FastAPI route paths, request/response shapes, and DB fields in `backend/routers/` and `backend/models/` — do not assume the summary above is fully accurate. Specifically check whether any "institution/college" concept already exists. Write your findings and your working plan into `docs/PLAN.md` as your task-list artifact.

**Phase 1 — Scaffold (~6 min).** `npm create vite@latest frontend -- --template react-ts`; install the stack above; init Tailwind + shadcn; set up design tokens; stub out every route above with React Router; set up a TanStack Query client and an `src/lib/api.ts` client pointed at the FastAPI base URL via `.env`. Prove CORS works end-to-end with one trivial real request before moving on.

**Phase 2 — Design system (~5 min).** Build the reusable primitives once, themed per the Design Principles: Button, Card, Input, Badge, Skeleton, the admin layout shell (sidebar/topbar/mobile nav). Every later screen reuses these — don't reinvent per page.

**Phase 3 — College-code gate + institution portal (~6 min).** `/` landing with the inline code-entry flow; the minimal `verify-code` backend endpoint from Hard Constraints if it doesn't already exist; the `/:collegeCode` institution portal screen with the two entry paths; deep-link handling for direct `/:collegeCode/register` and `/:collegeCode/login` visits; client-side persistence of the resolved code.

**Phase 4 — Student registration flow (~8 min).** `/:collegeCode/register`: RHF+Zod validated form, camera capture component (`getUserMedia`, rear camera preferred on mobile, works on mobile Safari and Chrome), base64 capture posted to the real registration endpoint, loading state, success state, and a clear retry UX for "no face / multiple faces detected."

**Phase 5 — Admin auth + dashboard (~7 min).** `/:collegeCode/login`, a route guard, `/:collegeCode/admin/dashboard` pulling real stats from the backend where endpoints exist — honest zero/empty states where they don't. No fabricated numbers.

**Phase 6 — Live monitor console (~10–12 min, the centerpiece).** Webcam stream, a canvas overlay sized/positioned to match the video element, frames posted to `process_frame` at a sane interval, bounding boxes + name + confidence drawn from the real response, a live roster panel of present students, session start/stop controls, elapsed timer.

**Phase 7 — Reports / students directory (~5 min).** Searchable/sortable/paginated table (client-side pagination is fine), export buttons wired to whatever the backend already exposes.

**Phase 8 — Mobile QA + polish (~5–6 min).** Use the browser subagent to load every route at ~390px and ~1440px, screenshot each, fix overflow/touch-target/contrast issues, and specifically re-verify the code-gate flow and the camera flows on the mobile viewport — that's the primary device for the primary user.

**Phase 9 — Final verification + handoff report (~4 min).** Full `npm run build`, fix any remaining errors, commit, then write `docs/SESSION_REPORT.md`: what's done, what's stubbed or mocked (including whether the institution concept is fully wired or a minimal stub), what's genuinely left, every autonomous decision you made and why, and exact next steps for me. This is the first thing I'll read when I sit back down.

---

## THE VERIFICATION LOOP (repeat continuously — this is the actual "loop")

For every screen or feature: implement → run it locally → use the browser subagent to load the real page and **screenshot it at both viewports** → look critically at your own screenshot and ask "would this pass as a real funded startup's UI, or does it read as a scaffold?" → fix what doesn't → check the browser console for errors → commit → tick the task-list artifact → move on. **Never mark something done without having actually seen it render.**

---

## DEFINITION OF DONE FOR THIS SESSION

- `npm run build` succeeds with zero TypeScript errors
- Every route above renders without crashing at both 390px and 1440px
- The college-code gate genuinely gates Register and Admin — neither is reachable from `/` without a valid code, invalid codes fail gracefully, and the deep-link exception works
- Registration works end-to-end against the real backend, or is clearly flagged as blocked with a specific reason in the session report
- The live monitor screen is visually the strongest screen in the app
- `docs/SESSION_REPORT.md` exists and is honest about what's real vs. mocked
- Everything is committed to git in small, reviewable commits

**Begin with Phase 0 now. Do not wait for confirmation.**
