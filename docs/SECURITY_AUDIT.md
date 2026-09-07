# Security Audit

This reviews the existing security mechanisms across the Phase 1 implementation.

## Vulnerabilities Identified

### 1. Hardcoded Administrator Authority
- **Issue**: `/login` verifies directly against `ADMIN_USERNAME` and `ADMIN_PASSWORD` parsed from `.env` loaded into Memory on startup.
- **Impact**: Any environment leak instantly grants full access to the DB. There is no multi-admin hierarchy, nor DB-backed users for administrators right now (students exist in DB but they have no portal capability yet).

### 2. Session Invalidations and Expiration (Missing)
- **Issue**: There is no JWT or standard session cookie implemented securely handling TTL (Time To Live). Simple local storage logic manages "is logged in" state right now natively in `auth_router.py`.
- **Impact**: Sessions aren't tied centrally. Logging out on one device wouldn't kill the session globally.

### 3. Biometrics Data Protection
- **Issue**: Embeddings are stored natively as basic stringified JSON lists (`[0.23, 0.14...]`).
- **Impact**: An SQL dump reveals exact embeddings. Standard biometric practices demand encryption-at-rest. The raw `[0...1]` floats aren't reversible to face images perfectly, but can trick other identical `vggface2` models.

### 4. Input Rate Limiting and DoS Limits
- **Issue**: `/api/v1/attendance/mark-attendance` receives `Base64` images. Max limit handled is `MAX_FRAME_SIZE_BYTES = 500 * 1024` but there is absolutely no limit on *how fast* an attacker can POST these.
- **Impact**: Heavy CPU usage MTCNN detection means spamming 50 frames synchronously will lock up the node instantly DOS'ing the Application server.

### 5. CORS Configurations
- `CORS_ORIGINS` pulls locally for Vite and generic `*`. Allowing wildcard sources is a dangerous misconfiguration on API deployments allowing CSRF vulnerabilities on the browser level.
