# WebSocket Protocol

## Endpoint

```
ws://host/api/v1/ws/monitor/{session_id}?token=<jwt>
```

## Connection Lifecycle

```
CLIENT                          SERVER
  |                               |
  |-- WS Handshake + ?token= -->  |
  |                               |-- Validate JWT
  |                               |-- Verify session ownership
  |<-- {"type":"session.joined"}  |
  |                               |
  |-- [binary JPEG bytes] ------> |-- Rate limit check (5 fps max)
  |                               |-- Inference worker dispatch
  |<-- {"type":"recognition.result", ...} --
  |                               |
  |-- [binary JPEG bytes] ------> |
  |<-- {"type":"recognition.result", ...} --
  |                               |
  |-- WS Close (code=1000) -----> |
  |                               |-- Close cleanly
```

## Authentication

JWT token is passed as a **query parameter** (`?token=...`) because the browser WebSocket API does not support custom HTTP headers during the upgrade handshake.

The server validates the JWT using the same `get_current_user_from_token` function used by all HTTP endpoints. The institution_id is extracted from the token claims — **never trusted from the client payload**.

## Frame Format

Clients send **raw JPEG bytes** as binary WebSocket frames.

- Max frame size: **512 KB**
- Rate limit: **5 frames/s** per connection (server-enforced token bucket)
- Frames exceeding the size limit receive a `warning` message; oversized frames are dropped
- Frames exceeding the rate limit are silently dropped server-side

## Server → Client Messages

All server messages are JSON text frames.

### `session.joined`
```json
{
  "type": "session.joined",
  "session_id": "...",
  "subject": "Introduction to AI"
}
```

### `recognition.result`
```json
{
  "type": "recognition.result",
  "session_id": "...",
  "results": [
    {
      "student_id": "...",
      "name": "Jane Doe",
      "confidence": 0.92,
      "status": "marked",
      "box": [x1, y1, x2, y2]
    }
  ],
  "faces_detected": 1,
  "faces_recognized": 1,
  "session_active": true,
  "session_subject": "Introduction to AI",
  "processing_ms": 143.2
}
```

`status` values:
| Value | Meaning |
|---|---|
| `tracking` | Face detected; accumulating frames for temporal verification |
| `mark` | Stable — attendance will be marked |
| `marked` | Attendance record persisted |
| `already_marked` | Already marked in this session |
| `cooldown` | In re-mark cooldown window |
| `unknown` | Face detected but not recognized |

### `warning`
```json
{"type": "warning", "message": "Frame too large (612000 bytes). Max 524288."}
```

### `worker.unavailable`
```json
{"type": "worker.unavailable", "message": "Inference worker is unavailable"}
```

### `error`
```json
{"type": "error", "code": 4001, "message": "Invalid or expired token"}
```
Connection is closed after an `error` message.

### `ping`
```json
{"type": "ping"}
```
Sent by server every 30 s of inactivity to keep the connection alive.

## Close Codes

| Code | Reason |
|---|---|
| 1000 | Normal closure (user stopped tracking) |
| 4001 | Authentication failure |
| 4003 | Authorization failure (wrong institution / session) |
| 4004 | No active session |
| 1011 | Internal server error |

## What is Never Transmitted

- Raw face embeddings
- PyTorch tensors
- Internal model objects
- Passwords, secrets, or PII beyond student name
