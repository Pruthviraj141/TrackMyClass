# Failure Inventory and Reliability Model

## Core Architecture Inventory

### 1. Frontend (React / Vite)
- **Failure:** Silent browser tab suspension, unhandled script crashes, WebGL/Camera API revocation.
- **Blast Radius:** Single client.
- **Expected Recovery:** Page reload (hard state flush).
- **Mitigation:** Global React error boundaries, manual JS disconnect catchers.

### 2. FastAPI API (Main Controller)
- **Failure:** Uvicorn process crash (OOM or Segfault), Threadpool exhaustion.
- **Blast Radius:** All actively routed sessions for this specific Node instance.
- **Expected Recovery:** Orchestrator (Docker/Systemd) restarts binary. Active Websockets break instantly.
- **Mitigation:** Stateless session tokens, token buckets fallback, transient memory tracking.

### 3. WebSocket Gateway
- **Failure:** Disconnect storms, binary payload corruption mapping memory exhaustion.
- **Blast Radius:** Active classroom sessions tracking ML outputs drop.
- **Expected Recovery:** Client-side reconnect loop re-establishes socket and fetches `session:active`.
- **Mitigation:** Enforced 512KB frame limits, rolling sliding-window 5FPS ingest logic.

### 4. Inference Worker (ProcessPool)
- **Failure:** `sys.exit` crashes, PyTorch Cuda memory errors.
- **Blast Radius:** All frame analytics processing completely halts. Application remains online but produces no matches.
- **Expected Recovery:** `WorkerManager` must detect stale heartbeats or process death and cleanly restart the multiprocess child and re-trigger model compilation.
- **Mitigation:** Heartbeat daemon logic, isolated process boundaries.

### 5. RecognitionEngine (Numpy/PyTorch Core)
- **Failure:** Input dimension mismatch, NaNs inside embedding extraction.
- **Blast Radius:** Bounded to the individual frame yielding the failure.
- **Expected Recovery:** Drops frame cleanly without crashing the overarching worker loop.
- **Mitigation:** Strict ML domain constraints, try/except guards inside process loop.

### 6. Redis (Coordination Layer)
- **Failure:** Connection timeouts, container crash.
- **Blast Radius:** Horizontally scaled servers lose synchronicity. Fallback to process-local algorithms safely.
- **Expected Recovery:** Python `redis.asyncio` retries connections aggressively. 
- **Mitigation:** `try/except` wraps everywhere, TokenBucket drops to memory, Sessions drop to local maps, Idempotency `SETNX` permits direct DB persistence natively.

### 7. Database (SQLite / Persistence)
- **Failure:** `database is locked`, corruption.
- **Blast Radius:** Application-wide complete write exhaustion.
- **Expected Recovery:** Restart required natively or manual WAL recovery.
- **Mitigation:** None yet externally applied besides standard connection retries. WAL configurations.

### 8. Cache (Student Vector Matrix)
- **Failure:** Stale representations persisting natively after new student registrations.
- **Blast Radius:** New students go undetected, deleted students incorrectly matched.
- **Expected Recovery:** Next session restart or Pub/Sub cache invalidation trigger natively flushes cache.
- **Mitigation:** Fast-reloading memory structures.
