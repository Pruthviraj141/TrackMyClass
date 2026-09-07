# Session State Transitions

Valid Lifecycles for TrackMyClass Attendance Sessions.

```plaintext
[ NULL State ]
      │
      ▼
(Session Started via API)
      │
      ▼
[[ ACTIVE ]] --(Websocket Streams Connect / Disconnect safely)--
      │
      ▼
(Session Ended via API)
      │
      ▼
[[ COMPLETED ]] -> (Stored in session_histories)
```

## Concurrent Transition Protections
1. **Double Start:** If user hits "Start Session" twice very fast, `SessionManager.start_session` checks `if self._active_sessions[institution_id].is_active`. It inherently drops the first session directly gracefully closing it and resolving the second one natively preventing duplicated overlap.
2. **Double End:** `end_session` checks if active locally and via Redis. Repeated calls simply return `{success: false}` bounding states gracefully.
