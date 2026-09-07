# Reliability Requirements

## Application Goals

### Acceptable Downtime
The ML process may fail temporarily, but the overarching FastAPI API must remain reachable (no full 500 routing failures unless DB is completely gone). Model inferences can experience `6-10 seconds` of downtime during a worker crash restart.

### Data-Loss Tolerance
Zero tolerance for durable Database (Student/Institution) losses. Attendance records currently held in queue buffers map as acceptable losses during hard crash limits since clients will continuously submit subsequent frames inherently fixing dropped queues transparently.

### Duplicate Tolerance
System must strictly prevent logical duplicate Attendance Records (mapping `session_id` and `student_id`). Physical HTTP duplicate events must gracefully fail via `HTTP 409` or `200 OK` silent ignores natively mapping Idempotency strictly over Redis `SETNX`.

### Stale-State Tolerance
Transient stale states (e.g., student matrix vectors missing novel registration elements) are tolerated tightly capped around the time of initialization (max `2 seconds` delay before Pub/Sub pushes cache flush). Session cache staleness is acceptable up to `24 hours` before natural expirations occur across mis-scaled horizontally disconnected nodes natively.

### User-Visible Behavior
Users should not see ambiguous `Internal Server Error` boundaries. Failed WebSockets must cleanly trigger generic reconnection dialogues. ML delays gracefully map into "System Re-routing" or blank tracking behaviors inherently avoiding crash stacks explicitly.
