# TrackMyClass: End-to-End Routing & Architecture Summary

This document provides a comprehensive summary of all backend (FastAPI) and frontend (React/Vite) routes in the TrackMyClass system. It is designed to be fed to an AI agent to quickly build context on the system's architecture, data flow, and endpoint availability.

---

## 1. Frontend Routing Architecture (React Router)

The frontend is a modern React SPA using `react-router-dom`. It employs a strict **College Code Gate** architecture, meaning almost all routes are structurally isolated under a dynamic `/:collegeCode` parameter.

### Public Routes
- **`/` (Landing Page)**: The root entry point. Contains an input form for users to enter their `collegeCode`. It calls the backend verification endpoint. If valid, navigates to `/:collegeCode`.
- **`/:collegeCode` (Institution Portal)**: The gateway screen scoped to a specific institution. Displays the college name and offers two paths: "I'm a Student" or "I'm a Teacher".
- **`/:collegeCode/register` (Student Registration)**: A mobile-first flow where students input their details and capture 5 face samples via webcam (`getUserMedia`) to create embeddings.
- **`/:collegeCode/login` (Admin/Teacher Login)**: The authentication screen for admins and teachers to access the dashboard.

### Admin Routes (Protected)
*These routes are wrapped in an `<AdminLayout />` component that checks for active authentication and displays the sidebar/navigation.*
- **`/:collegeCode/admin/dashboard`**: Displays high-level statistics (total students, active sessions, recent attendance).
- **`/:collegeCode/admin/sessions/:sessionId/monitor`**: The core live-monitoring console. Renders the webcam stream with an HTML canvas overlay drawing bounding boxes for recognized faces. Handles the "N-consecutive frames" logic for confirming attendance.
- **`/:collegeCode/admin/students`**: A directory table listing all registered students, allowing admins to search, filter, and delete student records.
- **`/:collegeCode/admin/reports`**: Data tables for historical attendance records, featuring Excel/CSV export functionality.

---

## 2. Backend API Endpoints (FastAPI)

The backend is built with FastAPI and runs on Uvicorn. It uses SQLite (or Firebase) for the database layer and relies heavily on `facenet-pytorch` and `MTCNN` for facial recognition.

### Authentication & Institutions (`auth_router.py`, `institution_router.py`)
- **`POST /api/institutions/verify-code`**: 
  - **Payload**: `{"code": "string"}`
  - **Returns**: `{"valid": bool, "institutionName": "string", "code": "string"}`
  - **Purpose**: Validates the college code entered on the frontend Landing page.
- **`POST /login`**: 
  - **Payload**: `FormData (username, password, login_type)`
  - **Returns**: Sets an `HTTPOnly` session cookie and returns `{success: true, role: "admin"}`.
- **`POST /logout`**: 
  - **Purpose**: Clears the session cookie.

### Student Registration (`registration.py`)
- **`POST /register`**: 
  - **Payload**: JSON containing `name`, `roll_number`, `gender`, `password`, and a list of 5 `frames` (base64 JPEG strings).
  - **Purpose**: Processes the images through MTCNN to find faces, extracts 512-D embeddings via FaceNet, averages them, and saves the student record to the database.

### Core Attendance & Sessions (`attendance.py`)
- **`POST /session/start`**: Starts a new attendance session for the day/class.
- **`POST /session/end`**: Ends the currently active session.
- **`GET /session/status`**: Returns the state of the active session, if any.
- **`GET /session/history`**: Returns a list of past sessions.
- **`POST /mark-attendance`**:
  - **Payload**: `{"frame": "base64_string", "session_id": "string"}`
  - **Returns**: List of recognized faces in the frame with bounding boxes, names, and confidence scores. Updates the attendance database if a face is confidently matched against the cached embeddings.
- **`GET /attendance/{date}`**: Fetches attendance records for a specific date.

### Admin Management (`admin_router.py`)
- **`GET /api/dashboard-data`**: Aggregates statistics (counts of students, sessions) for the admin dashboard.
- **`GET /api/students`**: Retrieves all registered students.
- **`DELETE /api/students/{student_id}`**: Deletes a student and cascades the deletion to their attendance records.
- **`GET /api/historical-data`**: Fetches paginated/filtered historical attendance data.
- **`GET /export-csv`**: Triggers a CSV file download for the current day's attendance.
- **`GET /export-historical-csv`**: Triggers a CSV file download for historical date ranges.

### Student Portal (Legacy/Current `student_router.py`)
- **`GET /api/my-profile`**: Fetches the currently logged-in student's details.
- **`GET /api/my-attendance`**: Fetches the attendance history specific to the logged-in student.

---

## 3. Global State & Network Rules
- **State Management**: The frontend uses `Zustand` with `localStorage` persistence to store the `collegeCode` and `institutionName`. This ensures users do not lose their routing context on hard refreshes.
- **Security Interceptors**: The frontend utilizes Axios response interceptors (`src/lib/api.ts`). If the backend ever returns a `401 Unauthorized` (e.g., session cookie expires), the frontend automatically clears the user state and redirects to `/:collegeCode/login`.
- **CORS**: FastAPI is configured to allow origins dynamically, facilitating smooth local development via the Vite dev server (usually `localhost:5173`).
