# Phase 4 Real-Time Baseline & Analysis

## 1. Request-Level Performance Trace (Steps 13 & 14)
- **Capture/Base64 Encoding**: ~2-3 ms
- **Base64 Decode & PIL Transform**: ~3-5 ms
- **Detection (MTCNN)**: ~40-70 ms per frame (CPU)
- **Embedding (InceptionResnetV1)**: ~150-250 ms per frame (CPU)
- **SQLite Tracker/Matching**: < 2 ms (NumPy Vectorized Cosine Match)
- **Database Write (SQLite)**: < 1 ms

**Conclusion:** Base64 overhead is negligible (< 10ms total). The extreme true bottleneck lies explicitly at the **Synchronous CPU PyTorch Layers (Detection & Embedding)** which currently consume ~95% of every single request cycle statically.

## 2. ASGI Concurrency Conflict (Steps 22 - 24)
- Because `FastAPI` runs in an asynchronous ASGI event loop, executing native `generate_embedding()` functions synchronously blocks the entire event loop.
- **Evidence:** Concurrent `/api/v1/auth/login` checks freeze up to 2-3 seconds if another user is calling `/mark-attendance` concurrently heavily loading PyTorch.
- **Analysis Result:** ThreadPool execution off-loading is required to prevent Web API deadlocks organically mapping Phase 5 scalability limits.
