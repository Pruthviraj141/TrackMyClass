# Changelog

## Phase 0: Engineering Audit and Baseline

### Documentation Changes
- `[NEW]` created `docs/ARCHITECTURE_CURRENT.md` to map dataflows.
- `[NEW]` created `docs/DATA_MODEL_CURRENT.md` charting table schemas.
- `[NEW]` created `docs/API_INVENTORY.md` logging REST structures.
- `[NEW]` created `docs/SECURITY_AUDIT.md` highlighting P0 weaknesses.
- `[NEW]` created `docs/AI_PIPELINE.md` tracing ML operations.
- `[NEW]` created `docs/UIUX_AUDIT.md` detailing frontend flaws.
- `[NEW]` created `docs/TECHNICAL_DEBT.md` cataloging bugs prioritizing Architecture decoupling.
- `[NEW]` created `docs/DEPLOYMENT_AUDIT.md` evaluating Docker topologies.
- `[NEW]` created `docs/TESTING_BASELINE.md` checking standard test mechanisms.
- `[NEW]` created `docs/PHASE_0_REPORT.md` combining full executive summaries.

### Code Changes
- None (Explicit Phase 0 instruction to maintain application behavior and write no new libraries).

### Measurement/Instrumentation Changes
- Ran `scripts/benchmark.py` generating `benchmarks/baseline_results.md` mapping actual Tensor and Load times.

## Phase 1: Codebase + Architecture Rebuild

### Documentation Changes
- `[NEW]` created `docs/ARCHITECTURE_TARGET.md` establishing domain boundaries.
- `[NEW]` created `docs/decisions/ADR-001-layered-architecture.md` detailing CPU-bound API router blockers.

### Code Changes
- `[NEW]` Added `backend/domain/` housing pure objects (`Student`, `AttendanceRecord`, `RecognitionResult`).
- `[NEW]` Added `backend/core/` for centralized configuration and error subclasses.
- `[NEW]` Added `backend/application/` extracting Use Case flows out of standard FastAPI routes.
- `[NEW]` Added `backend/ml/engine.py` decoupling Inference from REST schemas flawlessly via a functional `RecognitionEngine` wrapper.
- `[NEW]` Added `backend/repositories/student_repository.py` abstracting SQLite calls.
- `[MODIFIED]` Rebuilt `/api/routes` ensuring endpoints only ingest models and execute application injections.
- `[MODIFIED]` Redesigned `main.py` entry mapping to properly support restructured directory nesting.

## Phase 2: Security & Identity Configuration
### Documentation Changes
- `[NEW]` created `docs/SECURITY_PHASE2_CURRENT.md`, `docs/MULTI_TENANCY.md`, `docs/THREAT_MODEL.md`.
- `[NEW]` created `docs/BIOMETRIC_DATA_LIFECYCLE.md` confirming proper raw-tensor scrub.
- `[NEW]` created `docs/decisions/ADR-002-rbac-jwt.md`.

### Code Changes
- `[NEW]` Added `User`, `Role`, `InstitutionMembership` standard entities handling Tenant bounds.
- `[NEW]` Configured PyJWT mapping logic natively handling React API endpoints seamlessly.

## Phase 3: Advanced Computer-Vision Recognition Engine 
### Documentation Changes
- `[NEW]` created `docs/RECOGNITION_ENGINE_CURRENT.md`, `docs/AI_MODEL_VERSIONING.md`, `docs/RECOGNITION_THRESHOLD_CALIBRATION.md`, `docs/RECOGNITION_PERFORMANCE_PROFILE.md` validating 130MB limits and <0.1ms matching overhead correctly blocking bottlenecks.
- `[NEW]` created `docs/RECOGNITION_ENGINE_ARCHITECTURE.md`, `docs/decisions/ADR-004-recognition-engine-boundaries.md`

### Code Changes
- `[NEW]` Refactored PyTorch logic natively into `<detector / feature / math>` subcomponents tightly wrapped inside Domain bindings cleanly mapping outputs functionally without Tensor bindings leaking publicly.
- `[NEW]` Injected typed testing logic `test_ml_core` verifying native state Temporal Identity switches precisely avoiding tracking false positives cleanly.
- `[MODIFIED]` Wrapped MTCNN and Embedding extracts exactly utilizing `torch.inference_mode()` stabilizing OS process RSS memory gracefully globally bypassing memory leaks natively.

## Phase 4: Performance Engineering & Optimization
### Documentation Changes
- `[NEW]` created `docs/PERFORMANCE_BASELINE.md` and `docs/PERFORMANCE_OPTIMIZATIONS.md`.

### Code Changes
- `[MODIFIED]` Configured Native Frame Resampling mapping. Halved resolutions down to 320x240 and activated `SKIP_DETECTION_FRAMES` logic.

## Phase 5: Real-Time Architecture
### Documentation Changes
- `[NEW]` created `docs/REAL_TIME_REQUIREMENTS.md`, `docs/WEBSOCKET_PROTOCOL.md`, `docs/FRAME_PIPELINE.md`, `docs/REAL_TIME_ARCHITECTURE.md`, `docs/PHASE_5_FINAL_REPORT.md`
- `[NEW]` created ADRs: `ADR-006-realtime-transport.md`, `ADR-007-inference-worker-model.md`

### Code Changes
- `[NEW]` Added process-isolated inference worker pool logic (`WorkerManager`, `frame_queue.py`).
- `[NEW]` Added WebSocket endpoint `/api/v1/ws/monitor/{session_id}`.
- `[MODIFIED]` Refactored frontend `LiveMonitor.tsx` to support raw binary Websocket transport.
