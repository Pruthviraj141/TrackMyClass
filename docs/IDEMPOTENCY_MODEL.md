# Idempotency Model

## Externally-Triggerable Operations

| Operation | Safe to Retry? | Protection Mechanism | Details |
|---|---|---|---|
| **Session Start** | Yes | Transactional / Key | `SessionManager.start_session` forcefully ends existing sessions for the same institution. Concurrent starts resolve to the last executed (LWW). |
| **Session End** | Yes | Safe to retry | If a session is already ended or None, returns gracefully. |
| **Attendance Mark** | Yes | Requires ID Key | Redis `SETNX` locking ensures duplicate ML classifications across distributed workers mapping to `attendance:session_id:student_id` are ignored uniquely. |
| **Student Registration** | No | Requires DB Uniqueness | Unique DB combinations over `roll_number` and `institution_id` reject duplicates aggressively natively. |
| **Student Update** | Yes | Safe to retry | Overwrites representations and triggers `cache:invalidation` pub/sub natively flushing horizontally safely. | 

## Security Posture: Fail Closed vs Fail Open

1. **Rate Limiting:** Fail Open (fallback to Memory Limits gracefully).
2. **Attendance Commits:** Fail Closed (If network disconnects from db, attendance is discarded safely preventing ghost states).
3. **Authentication:** Fail Closed (Strict 401 unauthenticated drops).
