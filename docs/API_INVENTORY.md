# Backend API Inventory

## 1. Authentication Router (`auth_router.py`)
| Endpoint | Method | Function | Auth Required | Body/Params | DB Interaction | Status/Concerns |
|----------|--------|----------|---------------|-------------|----------------|-----------------|
| `/login` | `POST` | `login` | No | `username`, `password` (FormData) | Verified explicitly against `ADMIN_USERNAME` in `.env` | Extremely weak. Hardcoded single admin account. No Database connection. |
| `/logout`| `POST` | `logout` | No | None | None | Mostly client side deletion, lacks server-side session invalidation structure since no JWT/Redis is currently used. |

## 2. Attendance Router (`attendance.py`)
| Endpoint | Method | Function | Auth Required | Body/Params | AI/DB Interaction | Status/Concerns |
|----------|--------|----------|---------------|-------------|-------------------|-----------------|
| `/session/start` | `POST` | `start_session` | Yes (Admin) | `subject_name` | Flushes tracking buffer, DB Loads embeddings. | Sync. Blocking thread while loading thousands of floats. |
| `/session/end` | `POST` | `end_session` | Yes (Admin) | None | Frees tracker buffers. | No specific issues. |
| `/session/status` | `GET` | `session_status` | Yes (Admin) | None | Memory state reads | Good for polling. |
| `/session/history` | `GET` | `session_history` | Yes (Admin) | None | Firebase/Sqlite reads | Paging missing, might scale poorly. |
| `/mark-attendance`| `POST` | `mark_attendance` | Yes (Admin) | `frame` (base64) | Invokes MTCNN + FaceNet + Cosine Similarity | Heavy synchronous payload. Decodes base64 string directly in main thread blocking FastAPI. |
| `/attendance/{date}`| `GET` | `get_attendance` | Yes (Admin) | `date` param | DB retrieval | Missing filters/limits. |

## 3. Registration Router (`registration.py`)
| Endpoint | Method | Function | Auth Required | Body/Params | AI/DB Interaction | Status/Concerns |
|----------|--------|----------|---------------|-------------|-------------------|-----------------|
| `/register` | `POST` | `register_student` | No | `name`, `roll`, `frames` | Detects, embeds, writes to DB. | VERY slow synchronous iteration over base64 array causing potential HTTP timeout on large registers. |
| `/students` | `GET` | `list_students` | Yes (Admin) | None | Fetches all students | Potential memory/bandwidth leak without pagination. |
| `/students/{id}`| `DELETE`| `remove_student` | Yes (Admin) | Path Param | Cascade deletes | Good. |

## 4. Admin Analytics (`admin_router.py`)
| Endpoint | Method | Function | Auth Required | Status/Concerns |
|----------|--------|----------|---------------|-----------------|
| `/dashboard-data` | `GET` | `get_dashboard_stats` | Yes (Admin) | Scrapes multiple collections sequentially, slow. |
| `/export-csv` | `GET` | `export_csv` | Yes | Uses pandas to dump CSV inline blocking async IO. | 

## Security Weaknesses
- End-to-end endpoints have **synchronous** dependencies blocking the ASGI async workers.
- The Single Admin user bypasses the DB structure (`students` table has passwords but isn't used for login).
- Lack of rate limiting on endpoints serving Heavy AI (DDoS risk by spamming `/mark-attendance`).
