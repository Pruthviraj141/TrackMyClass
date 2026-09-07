# TrackMyClass — Production-Hardening & Portfolio Upgrade Mission

> **How to use this file:** Same as last time — paste this whole thing as a new task in Antigravity's **Agent Manager** surface, in your existing `TrackMyClass` workspace, and let it run. Unlike the last session, this one isn't fixed to one hour — it's structured in strict priority tiers instead, so it self-paces to whatever time you actually give it and always finishes a tier cleanly before starting the next one.

---

## ROLE & OPERATING MODE

You are acting as a senior staff engineer doing a hardening and portfolio-readiness pass on TrackMyClass, which is already working and deployed. You have full autonomy for this session — there is no human available to answer questions.

1. **Never pause to ask a clarifying question.** Pick the most defensible, production-grade default, log a one-line rationale to `docs/DECISIONS.md`, and keep moving.
2. **Work in strict tier order.** Do not start Tier 1 until Tier 0 is fully done — build passing, tests passing, committed. A completely finished Tier 0 is worth far more than a half-finished Tier 2; a security gap you didn't get to is worse than a polish item you didn't get to.
3. **Maintain a living task-list Artifact.** Update it continuously.
4. **Commit after every working checkpoint** — small, atomic commits.
5. **When your session budget runs out, stop cleanly at the end of whichever tier/item you're mid-way through** (finish the item, don't abandon it half-edited), commit, and write the handoff report.
6. **Work on a new branch, not directly on the current branch.** Before touching anything, create and switch to a branch named `hardening/tier-0-and-beyond` (or similar via a new Antigravity worktree if available). This keeps the currently-working main branch untouched and reviewable as a diff, so a bad call in Tier 0's route migration can never take down what's already deployed.
7. **Verify everything visually and functionally** — run it, look at it via the browser subagent, check the console, run the actual test suite — before marking anything done.

---

## CONTEXT — VERIFIED CURRENT ARCHITECTURE

This reflects the real, already-implemented system — not a guess. Confirm it's still accurate in your own quick pass, but trust it more than you'd trust a cold-start audit.

**Frontend (React + `react-router-dom`), gated under `/:collegeCode`:**
- `/` — landing, college-code entry
- `/:collegeCode` — institution portal ("I'm a Student" / "I'm a Teacher")
- `/:collegeCode/register` — student registration, captures 5 face frames via `getUserMedia`
- `/:collegeCode/login` — admin/teacher login
- `/:collegeCode/admin/dashboard`, `/:collegeCode/admin/sessions/:sessionId/monitor`, `/:collegeCode/admin/students`, `/:collegeCode/admin/reports` — protected via `<AdminLayout />`
- State: Zustand + `localStorage` persistence for `collegeCode`/`institutionName`. Axios interceptor in `src/lib/api.ts` clears state and redirects to login on any `401`.

**Backend (FastAPI + SQLite/Firebase + facenet-pytorch/MTCNN):**
- `POST /api/institutions/verify-code` → `{code}` → `{valid, institutionName, code}`
- `POST /login` → form data `(username, password, login_type)` → sets `HTTPOnly` session cookie, `{success, role}`
- `POST /logout`
- `POST /register` → `{name, roll_number, gender, password, frames: [5x base64 jpeg]}` → averages 5 FaceNet embeddings, saves student
- `POST /session/start`, `POST /session/end`, `GET /session/status`, `GET /session/history`
- `POST /mark-attendance` → `{frame, session_id}` → recognized faces (boxes, names, confidence); writes attendance on confident match
- `GET /attendance/{date}`
- `GET /api/dashboard-data`, `GET /api/students`, `DELETE /api/students/{id}`, `GET /api/historical-data`, `GET /export-csv`, `GET /export-historical-csv`
- `GET /api/my-profile`, `GET /api/my-attendance` — **student portal endpoints that exist but have no corresponding frontend routes yet**

---

## MISSION

Take TrackMyClass from "a working project" to something you'd hand a hiring manager or a real college's procurement team without flinching: correct multi-tenant security you can prove, automated tests, a real-time monitoring pipeline, biometric-data consent and deletion, and a demo experience a total stranger can click through without you in the room.

---

## TIER 0 — SECURITY & CORRECTNESS (do this first, non-negotiable, do not skip or shortcut)

1. **Tenant isolation audit and enforcement.** For every backend route listed above, confirm the institution/tenant scope is derived *only* from the authenticated session server-side, and enforced on every single query. **The `:collegeCode` in the URL is for routing and display only — it must never be trusted as an authorization input.** Add an `institution_id` column/field anywhere it's missing (students, sessions, attendance records).
2. **Write a pytest suite specifically proving isolation** — this is the single most valuable artifact of this entire session, do not skip it. Create two test institutions, log in as an admin of each, and assert every relevant endpoint returns only that institution's data, and returns a clean `403`/`404` (never a `500`, never someone else's data) on cross-tenant access attempts.
3. **Consolidate routing under `/api/v1/`** with consistent resource-based naming (e.g. `POST /api/v1/auth/login`, `POST /api/v1/students/register`, `POST /api/v1/sessions/start`, `POST /api/v1/attendance/mark`). Update `src/lib/api.ts` to match. It's fine to keep the old paths as thin redirects for one commit while you migrate, then remove them.
4. **Informed consent for biometric capture.** Before any camera frame is captured on `/:collegeCode/register`, show plain-language copy explaining that facial data is stored for attendance matching, behind a required checkbox — don't capture a single frame before it's checked.
5. **Real data deletion.** Extend `DELETE /api/students/{id}` (or add a dedicated endpoint) to actually remove stored face embeddings, not just the display record, and expose a "delete my data" action reachable from the student portal you're building in Tier 1.
6. **Clean OpenAPI docs.** Add Pydantic response models (not just request models) to every endpoint so FastAPI's auto-generated `/docs` is genuinely presentable — a five-minute change that makes the whole API look far more professional to anyone who opens it.
7. **`GET /api/v1/health`** plus basic structured logging (request id, institution id, latency) on the ML inference path.

---


admin can delete the student wihtout permission or face levle check of student 

## TIER 1 — THE FEATURES AND INFRASTRUCTURE THAT MAKE THIS A PORTFOLIO PIECE

1. **Student portal frontend.** The backend already has `/api/my-profile` and `/api/my-attendance` — build `/:collegeCode/student/login` (or route by `login_type` off the existing login) and `/:collegeCode/student/dashboard`: attendance percentage, a present/absent calendar or list, a low-attendance warning state. Highest leverage item in this whole session — the backend work is already done.
2. **Real-time monitor via WebSocket.** Replace the interval-based `POST /mark-attendance` polling on the monitor screen with a WebSocket connection — client streams frames, server pushes recognition events back as they're confirmed. Keep the existing HTTP endpoint working as a documented fallback in case a school's network blocks WebSocket upgrades.
3. **CI pipeline.** A GitHub Actions workflow running on every push: backend `pytest` (including the Tier-0 isolation suite), frontend `npm run build` + `eslint` + `vitest` for critical components. Add a status badge to the README.
4. **One real end-to-end test** (Playwright): college code → register a student (mocked camera frames) → admin login → start session → mark attendance via a mocked frame → confirm it appears in `/admin/reports`.
5. **Seeded demo institution.** A `DEMO2026` college code seeded with fake students (generated or stock imagery used only locally, never real people) and fabricated historical attendance, so a recruiter can log in and explore the entire product without you present. Label demo data as demo data everywhere it shows up.
6. **README overhaul, written for a hiring manager reading it in two minutes:** a one-line pitch, a Mermaid architecture diagram (frontend ↔ FastAPI ↔ ML pipeline ↔ DB), the interesting engineering decisions and why (tenant isolation, WebSocket pipeline, the embedding-averaging trade-off), the `DEMO2026` live-demo path front and center, and the CI badge.

---

## TIER 2 — POLISH, 

1. Store multiple face embeddings per student instead of one averaged vector, matching against best-of instead of a centroid — note the trade-off in `docs/DECISIONS.md`.
2. Accessibility pass: keyboard navigation through the admin app, visible focus states, ARIA live regions on the monitor screen so a screen reader can announce "student X marked present."
3. Offline resilience: queue `mark-attendance` calls client-side with retry/backoff on failure, so flaky classroom Wi-Fi doesn't silently drop attendance.
4. A basic recognition-health panel for admins: rolling average confidence, count of low-confidence/rejected matches per session — shows you're treating the ML pipeline as a monitored system, not a black box.

---

## VERIFICATION LOOP (repeat continuously)

For every change: implement → run the real test suite → for UI changes, load the real page via the browser subagent and screenshot it at both ~390px and ~1440px → check the console for errors → commit → update the task-list artifact → next item. Never mark something done without having actually run it.

---

## DEFINITION OF DONE

- Tier 0 fully complete: isolation tests passing and committed, `/api/v1/` consistent, consent + deletion flow shipped, `/docs` is clean
- Whatever tier you reach beyond that is *fully* finished, not partially started
- `docs/SESSION_REPORT.md` states exactly which tier you reached, what's real vs. stubbed (especially: is tenant isolation actually enforced and tested, or partially?), and precise next steps

**Begin with Tier 0, item 1. Do not wait for confirmation.**
