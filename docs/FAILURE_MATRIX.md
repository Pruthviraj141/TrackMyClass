# Failure Matrix 

*A systematic evaluation of fault injections mapped to TrackMyClass.*

| Component | Failure | Detection | User impact | Data impact | Automatic recovery | Recovery time | Remaining risk |
|---|---|---|---|---|---|---|---|
| **FastAPI API** | Unhandled App Crash or Threadpool Exhaust | Load-balancer checks drop | Connection aborts mid-stream. Needs page reload. | Zero. Only pending queued frames lost which wasn't saved yet. | Yes, Docker or OS restarts container. | < 5s | In-flight non-idempotent routines break (prevented mostly by transactions). |
| **Worker Process** | MTCNN PyTorch Memory overflow | Heartbeat timeout threshold exceeded. | Minor frames dropped. UI shows "worker unavailable". | Zero. Faces simply aren't tracked for those few seconds. | Yes, ProcessPool spins up a new worker. | 2s-4s (ML model loading) | Sudden storm of pending frames causes backpressure on startup. |
| **Redis** | Network outage to DB. | Connection error stacktraces globally. | None. Sliding rate limits retreat to basic memory limits cleanly. | Transients (Cache pub/subs lost). SQLite safe. | Yes, `redis.asyncio` aggressively re-polls. | Instant upon network restore | High burst rates allowed while Local memory rate limits take over instead of Lua. |
| **SQLite (DB)** | Hard failure or locked WAL. | FastAPI error handler captures unique constraint failures or locked blocks. | Cannot mark attendance properly, failures reported. | Faces recognized but not durably saved. Lost attendance. | No, requires systemic intervention if DB persists failure. | N/A | Highest risk. | 
| **Client Network** | Browser disconnect mid WS. | ASGI detects Closed Socket Protocol. | UI stalls. | Zero impact on ML. | Auto-reconnect triggered from frontend hooks. | ~2s | None |
