# Technical Debt Register

Categorization of structural, technical, and performant flaws mapped against the current architecture to dictate focus in future Phase optimizations.

## P0 — Critical (Security / Stability Risk)
- **Problem**: Synchronous Blocking Vision Core
  - **Location**: `backend/routers/attendance.py:mark_attendance`
  - **Impact**: High latency. Every frame POST explicitly runs Detection -> Model Embedding completely suspending asyncio thread loops. Over 30 req/s will DDoS the CPU.
  - **Recommended Phase**: Phase 4 & Phase 5 (Real-time Arch).
- **Problem**: Missing Biometric Encryption.
  - **Location**: `backend/database/sqlite_service.py` -> `students.embedding`
  - **Impact**: Embeddings are clear-text JSON. Breaches compromise geometric identifiers explicitly.
  - **Recommended Phase**: Phase 2 (Security).

## P1 — High (Architecture / Performance)
- **Problem**: Non-existent Request Tracking & Observability.
  - **Location**: `main.py`
  - **Impact**: Debugging latency bottlenecks requires `print` logs. We don't know exact AI processing times on the EC2 instances.
  - **Recommended Phase**: Phase 8 (Observability).
- **Problem**: No Multi-tenant Authorization DB Logic.
  - **Location**: `backend/auth.py`
  - **Impact**: Solely checks `.env`. Hard-coded for single admins. Need true RBAC for scale.
  - **Recommended Phase**: Phase 2.

## P2 — Medium (Maintainability / UX)
- **Problem**: Expensive base64 parsing directly parsing frames per POST payload.
  - **Location**: `/mark-attendance`
  - **Impact**: Causes excessive byte decoding memory allocation. Sending frames via WebSocket native bytes drops overhead.
  - **Recommended Phase**: Phase 5 (WebSockets).
- **Problem**: Single Batch Processing.
  - **Location**: AI Pipeline Iterations.
  - **Impact**: `for i in range(len(face_tensors)): generate_embedding(...)`. It doesn't use PyTorch tensor batching `(N, C, H, W)` across a single GPU/CPU matrix operation drastically impacting multi-face frames.
  - **Recommended Phase**: Phase 4 (Performance).
- **Problem**: Weak test coverage (No end-to-end framework, no metrics pipeline tests).
  - **Location**: Tests dir.
  - **Recommended Phase**: Phase 9 (Testing Engineering).

## P3 — Low (Cleanup / Polish)
- **Problem**: No Pagination on Students / History.
  - **Location**: `admin_router.py`
  - **Impact**: Calling `GET /students` with 5,000 DB records will crash the DOM layout and throttle JSON parsing. 
  - **Recommended Phase**: Phase 12 (Analytics + Depth).
