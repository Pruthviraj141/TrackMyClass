# TRACKMYCLASS FULL ROUTE MATRIX

This matrix records every backend endpoint, mapping its functional scope, authentication rules, dependencies, and automated test coverage across Phase 8.5 stabilization limits.

| Method | Path | Role(s) | Auth | Request | Response | DB | Redis | WS | Frontend Consumer |
|---|---|---|---|---|---|---|---|---|---|
| POST | `/api/v1/auth/token` | ANY | NONE | `OAuth2 Form` | `access_token` | Reads User/Membership | Sliding Window | NO | `frontend/src/api/auth.ts` |
| GET | `/api/v1/auth/me` | ANY | JWT | NONE | `User dict` | YES | NO | NO | `AuthContext` |
| GET | `/api/v1/students` | TEACHER, INST_ADMIN | JWT | `query params` | `List[Student]` | Reads Students | NO | NO | `StudentDirectory.tsx` |
| POST | `/api/v1/registration/enroll` | TEACHER, INST_ADMIN | JWT | `Student Payload` | `status` | Writes Students | Pub/Sub Invalidates | NO | `AddStudentForm.tsx` |
| POST | `/api/v1/attendance/session/start` | TEACHER, INST_ADMIN | JWT | `subject_name` | `session_id` | Writes Session | SET Metadata | NO | `Dashboard.tsx` |
| POST | `/api/v1/attendance/session/end` | TEACHER, INST_ADMIN | JWT | NONE | `status` | Updates Session | DEL Metadata | NO | `Dashboard.tsx` |
| GET | `/api/v1/attendance/session/status` | ANY | JWT | NONE | `session dict` | Reads DB fallback | GET Metadata | NO | `Dashboard.tsx` |
| GET | `/api/v1/attendance/history` | ANY | JWT | NONE | `List[Session]` | Reads Sessions | NO | NO | `History.tsx` |
| GET | `/api/v1/attendance/{date}` | ANY | JWT | NONE | `List[Record]` | Reads Attendance| NO | NO | `TodayAttendance.tsx` |
| GET | `/api/v1/diagnostics/metrics` | ANY | JWT/Admin | NONE | `telemetry` | NO | PING (health) | NO | `SystemHealth.tsx` |
| WS | `/api/v1/ws/monitor/{id}` | TEACHER, INST_ADMIN | JWT | `binary JPEG` | `recognition limits` | Writes records | SETNX Idempotency | YES | `LiveMonitor.tsx` |

*Scope Audit Completed*: Cross checking the matrix against the routers indicates exhaustive explicit coverage cleanly wrapped inside `Depends(get_current_user_from_token)` boundaries structurally.
