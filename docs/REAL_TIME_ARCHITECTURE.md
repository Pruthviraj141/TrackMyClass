# Real-Time Architecture — Phase 5

## System Flow

```
Browser (Admin)
      |
      | WebSocket (binary JPEG + JSON)
      ↓
FastAPI WebSocket Gateway  (/api/v1/ws/monitor/{session_id}?token=)
      |
      | JWT authentication (token claims)
      | Session authorization (institution_id from token)
      | Rate limiting (5 fps / conn)
      | 512 KB frame size guard
      ↓
WorkerManager (asyncio bridge, Future-based dispatch)
      |
      | multiprocessing.Queue (maxsize=2)
      ↓
FrameQueue (depth=1, latest-frame-wins)
      |
      ↓
InferenceWorker (separate OS process)
      |
      | MTCNN → FaceDetectionResult
      | FaceNet → Embedding
      | EmbeddingCache → MatchResult (in-memory vectorized)
      | TemporalTracker → RecognitionResult
      ↓
Result (via multiprocessing.Queue)
      |
      ↓
WorkerManager Result Reader (background thread)
      |
      | Future.set_result()
      ↓
WS Gateway (await submit_frame result)
      |
      | AttendanceService → AttendanceRepository → Firebase/SQLite
      |                     (for status=="mark" faces)
      ↓
recognition.result JSON message
      |
      ↓
Browser (bounding boxes + attendance toast)
```

## Component Responsibilities

| Component | Responsibility |
|---|---|
| `monitor_ws.py` | WS lifecycle, auth, rate limiting, frame routing, result delivery |
| `WorkerManager` | Worker process lifecycle, Future dispatch, health probe, auto-restart |
| `FrameQueue` | latest-frame-wins depth-1 queue with drop stats |
| `InferenceWorker` | CPU-bound MTCNN + FaceNet inference; no I/O |
| `TemporalTracker` | Multi-frame stability; prevents single-frame false positives |
| `EmbeddingCache` | In-memory vectorized embedding store; per-institution |
| `AttendanceService` | Session lookup, idempotency, DB persistence |
| `SessionManager` | In-memory session registry; single active session per institution |

## Security Boundaries

- JWT validated server-side on every WS connect; institution_id derived from token claims only
- Session ID validated against `session_manager.get_active_session(institution_id)` — forged session IDs are rejected
- Cross-tenant access blocked: institution derived from token, not from client message
- Frame rate limited per connection; oversized frames rejected before inference
- Embeddings and tensors **never** cross the process boundary as objects (raw bytes only)

## Performance Characteristics

| Metric | Phase 4 (HTTP polling) | Phase 5 (WebSocket) |
|---|---|---|
| Transport overhead | ~2 KB HTTP headers per frame | 2-byte WS frame header |
| Frame encoding | Base64 JSON (~43 KB) | Raw JPEG (~30 KB) |
| API block during inference | Yes (100–230 ms) | No (separate process) |
| API health endpoint during inference | Blocked | Responsive |
| Frame freshness guarantee | None | latest-frame-wins queue |
| Max queue depth | Unbounded | 1 frame |
| Reconnection | Client retry | Exponential backoff, max 5 attempts |
