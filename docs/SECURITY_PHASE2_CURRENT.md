# Security Phase 2 Context: Current Architecture

### 1. Authentication Mechanisms
- **Admin**: Hardcoded `ADMIN_USERNAME` and `ADMIN_PASSWORD` checked against `.env` directly using `verify_admin_credentials`.
- **Student**: Stored SHA-256 hashes inside the database; checked via a simple boolean equality with the DB response. No salt mechanism apparent in `backend/auth.py`.

### 2. Session Handling
- Heavy stateful database-driven sessions.
- UUID string (`session_id`) sits in cookies.
- Backend intercepts the cookie and hits SQLite/Firebase table `auth_sessions` for every single request natively blocking IO.
- Fallback Institution ID `DEMO2026` is aggressively hardcoded.

### 3. Role-Based Access Control (RBAC)
- Only two implicit string boundaries exist: `"admin"` and `"student"`.
- Validated manually inside `get_current_user` (`if session.get("role") == "admin"`).
- Completely misses proper `SUPER_ADMIN`, `TEACHER`, and `INSTITUTION_ADMIN` scales.

### 4. Tenant Isolation
- Barebones implementation relying primarily upon UI filtering. `backend/auth.py` literally injects `DEMO2026` rather than looking up the actual organizational structure of the invoking party.

### 5. Multi-Tenant Gap
- The system is inherently susceptible to IDOR logic attacks if a teacher bypasses the frontend and sends standard POST bodies referencing remote `institution_id` keys directly.
