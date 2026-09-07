# TRACKMYCLASS FULL FEATURE MATRIX

This chart explicitly dictates RBAC domains dictating permission access for every primary application dimension.

| Feature | Student | Teacher | Institution Admin | Super Admin |
|---|---|---|---|---|
| **Authentication** | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| **Logout** | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| **Registration / Add Student** | DENIED | ALLOWED | ALLOWED | ALLOWED (global) |
| **Student Directory View** | DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Session Start** | DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Session End** | DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Live Monitor / WebSocket** | DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Recognition Result Broadcasts**| DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Attendance Creation** | DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Student Own Attendance** | ALLOWED | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE |
| **Student Profile View** | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| **Attendance History (Class)** | DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Reports / Exports (CSV)** | DENIED | ALLOWED | ALLOWED | ALLOWED |
| **Diagnostics Dashboard** | DENIED | DENIED | DENIED | ALLOWED |
| **Audit Logs** | DENIED | DENIED | ALLOWED | ALLOWED |

## Validation Steps
The above constraints map perfectly against `require_role(institution_id, [ROLES])` within `backend/api/dependencies.py`.
Students possess NO capabilities to instigate WS channels or force SQLite mutations manually outside of viewing their unique `[student_id]` footprints via `/student/` endpoints.
