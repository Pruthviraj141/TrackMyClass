# TrackMyClass - Project Overview & Technical Guide

This document provides a comprehensive overview of the `TrackMyClass` intelligent face recognition attendance project, detailing the architecture, UI/UX flow, and a complete breakdown of internal routes and endpoints. It serves as a unified reference guide for future development.

---

## 🏗️ Architecture & Technology Stack

The project separates logic into a Python-based intelligent backend (FastAPI/PyTorch) and a modern frontend interface (React/Vite).

- **Backend Component**: FastAPI, Uvicorn, Python 3.10+.
- **AI Core**: PyTorch, MTCNN (face detection), InceptionResnetV1 (FaceNet for 512-D embeddings), OpenCV.
- **Frontend App**: React, Vite, Tailwind CSS, TypeScript.
- **Databases**: Firebase Firestore (Production Cloud) / SQLite (Local testing).

---

## 🎨 UI & UX Flow

The application offers two primary user scopes: **Public/Student** and **Admin/Institution**. The user-experience focuses on sleek, fast operations minimizing manual intervention through automated facial recognition.

### 1. Public & Student Facing (Registration)
- **Landing Page** (`/src/pages/public/Landing.tsx`): The main entry point.
- **Face Registration Workflow** (`/src/pages/public/Register.tsx`):
  - **UX**: Students input metadata (Name, Roll Number, Department). It utilizes `.MediaDevices` Web API (defaulting to the rear-facing `environment` camera for mobile devices). The capture overlay includes real-time feedback. Submits metadata alongside a base64 encoded snapshot.
- **Institution Portal** (`/src/pages/public/InstitutionPortal.tsx`): An entry mechanism (e.g., verify join code).
- **Student Dashboard** (`student_router.py` logic): Access individual profiles and attendance history.

### 2. Admin Portal (Monitoring & Management)
- **Login** (`/src/pages/public/Login.tsx`): Authentication flow via admin credentials.
- **Main Dashboard** (`/src/pages/admin/Dashboard.tsx`): Centralized hub indicating "Today's Attendance Stats", overall counts, and recent tracking activities. Glassmorphic sleek UI.
- **Live Monitor** (`/src/pages/admin/LiveMonitor.tsx`):
  - **UX**: Opens the live feed for classroom scanning. Continuously samples frames via `setInterval`, forwarding frames to the AI processing backend. Draws responsive bounding-box overlays indicating matched names ("Pruthvi - Present") using data returned from PyTorch matrix comparisons.
- **Students Directory** (`/src/pages/admin/StudentsDir.tsx`): Interface for administrators to view all registered students and perform CRUD actions.
- **Reporting & Exports** (`/src/pages/admin/Reports.tsx`): Generate customized historical spreadsheets and PDFs (via Pandas).

---

## 🛣️ API Routes & Use Cases Breakdown

The backend enforces modularity using FastAPI APIRouters within `backend/routers`. It includes health checks and core AI integration tasks.

### General / Base endpoints
- `GET /`: Serves root UI index / legacy template context.
- `GET /health`: AWS Application Load Balancer / uptime health check verification returning `{"status": "healthy"}`.

### 1. Authentication Router (`auth_router.py`)
- `POST /login`: Authenticates an admin against configured `.env` credentials and assigns session tokens.
- `POST /logout`: Ends the authenticated session.

### 2. Registration API (`registration.py`)
- `POST /register`: Receives user schema + `base64` image. Runs it through backend MTCNN singleton; returns 400 if `0` or `>1` faces are found, otherwise extracts the FaceNet embedding and syncs to vector DB/SQLite.
- `GET /students`/`DELETE /students/{id}`: Basic student records orchestration operations.

### 3. Core Attendance & AI (`attendance.py`)
Handles the real-time intensive computation for classroom scanning.
- `POST /session/start`: Initates a class session tracking pool. Loads thousands of previously embedded Vectors from Database into highly optimized RAM-based Numpy matrix cache to eliminate IO bottleneck.
- `POST /session/end`: Flushes cache, validates, clears states and stops the active tracker.
- `GET /session/status`: Retrieves real-time session tracking parameters.
- `GET /session/history`: Past sessions history arrays.
- `POST /mark-attendance`: Given base64 frame stream, the API executes:
  - MTCNN bounding box multi-face detection.
  - Runs detected crops against cached RAM Matrix (cosine similarity calculation, `<1ms`).
  - Processes matched identities through `TemporalTracker` buffers (mitigating single frame glitches/hallucinations by enforcing a ~4-frame consecutive hit criteria).
  - Validates and saves DB log per entity. Responds with coordinates and green-box tags.
- `GET /attendance/{date}`: Day-specific attendance history retrieval.

### 4. Administrative Data API (`admin_router.py`)
- `GET /dashboard-data`: High-level aggregated statistics (total counts, class completion ratios) intended for `Dashboard.tsx`.
- `GET /export-csv`: Streams a download attachment representing current day's CSV roster.
- `GET /historical-data`: Paged or filtered past datasets payload endpoint.
- `GET /export-historical-csv`: Downloadable attachment for archived dates parsing Pandas to CSV responses.

### 5. Institutional & Student Supplemental
- `POST /verify-code` (`institution_router.py`): Logic to associate new registrations to authorized class sessions.
- `GET /dashboard`, `GET /my-profile`, `GET /my-attendance` (`student_router.py`): Legacy or supplemental personal views for verified student actors (returning TemplateResponse HTML logic in phase 1 implementation).
