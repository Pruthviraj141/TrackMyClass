# Phase 5 Final Report
## Real-Time Architecture Overhaul

**Date:** 2026-09-06  
**Status:** Completed

### Summary of Changes

Phase 5 successfully decouples face recognition (MTCNN + FaceNet) from the FastAPI HTTP event loop, transitioning the application from a synchronous API bottleneck to a high-performance, real-time bounding box stream.

- **WebSocket Transport:** Client now sends frames directly via raw binary payloads to the WebSocket gateway (`/api/v1/ws/monitor`).
- **Worker Process Isolation:** Deep learning models are now booted into an isolated Python process (`ProcessPoolExecutor` with `spawn`), effectively sidestepping the Python GIL.
- **Latency Bounding:** A `FrameQueue` limits incoming traffic memory footprint by implementing a `latest-frame-wins` drop policy on backpressure. Server-side token buckets ensure connection rate-limiting at 5 fps.

### Benchmark Results

Testing with the new WebSocket gateway against a simulated camera load while concurrently bombarding the lightweight FastAPI instance demonstrated exceptional isolation:
- Heavy ML workloads did **not** cause latency degradation on simple HTTP metadata requests.
- WebSocket overhead is minimal compared to the previous HTTP POST Base64 encoding.

### Next Directions

The system is now fully prepared to scale to dozens of class rooms simultaneously, since each room spawns at most 5 frames/sec, and identical back-ends can horizontally scale alongside an institutional caching layer. The client UX is greatly improved with native Web-Socket reconnection and direct `status=marked` toasts on the dashboard screen.
