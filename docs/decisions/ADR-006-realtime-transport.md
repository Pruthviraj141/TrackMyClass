# ADR-006: Real-Time Transport Selection

**Status**: Accepted  
**Date**: 2026-09-06

## Context

The existing Phase 4 architecture uses `POST /attendance/mark-attendance` — a synchronous HTTP endpoint polled every 1 second by the frontend. Each request:
- Blocks the ASGI worker for ~100–230 ms (MTCNN + FaceNet inference)
- Sends a Base64-encoded frame in the JSON body (~30–50 KB overhead per frame)
- Has no backpressure or freshness guarantees

Phase 5 requires a transport that supports bidirectional streaming for live recognition.

## Options Evaluated

| Criterion | HTTP Polling | Server-Sent Events | **WebSocket** |
|---|---|---|---|
| Bidirectional | ❌ | ❌ | ✅ |
| Binary frame support | ✓ (body) | ❌ | ✅ (binary frames) |
| Browser support | ✅ | ✅ | ✅ |
| Per-frame overhead | High (HTTP headers) | N/A | Low (2-byte WS frame header) |
| Reconnection handling | Client retries | EventSource API | Manual but well-understood |
| Implementation complexity | Low | Low | Medium |
| Backpressure control | None | None | Server-side rate limiter |

SSE is one-directional: it cannot receive frames from the browser.  
HTTP polling adds ~5–15 ms per round-trip of HTTP overhead and cannot pipeline.  
WebSocket is the only option supporting both binary frame upload (camera → server) and result push (server → browser) in the same connection.

## Decision

**WebSocket** is selected.

## Consequences

- Frontend `LiveMonitor.tsx` opens a single WS connection; sends raw JPEG binary frames; receives JSON recognition results
- Eliminates per-frame HTTP header overhead (~1–3 KB/frame saved)
- Single authenticated connection reduces repeated token validation overhead
- Requires explicit reconnection logic in the client
- JWT authentication via `?token=` query param on WS handshake (WebSocket browser API does not support custom headers)
