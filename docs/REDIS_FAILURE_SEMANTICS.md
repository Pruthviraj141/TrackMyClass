# REDIS FAILURE SEMANTICS (Post-audit)

The architecture designates explicit delineations of behavior when the coordination server (Redis) suffers a hard failure, timeout, or partition.

## Category A — Safe Local Fallback
Operations failing under Category A permit local degradation preventing large outage windows without sacrificing overall data integrity or authorization.

1. **Distributed Rate Limiting (Token Bucket):**
   * **Behavior:** Falls back to in-memory python dictionary sliding windows natively.
   * **Result:** Node continues to accept traffic capped at local ceilings independently. 

2. **Session Coordinations & Metadata Syncs:**
   * **Behavior:** Nodes fail to advertise Session bounds globally.
   * **Result:** Local nodes rely safely on process RAM dictionaries natively. Session states stay clean across individual containers cleanly.

3. **Cache Synchronization Events:**
   * **Behavior:** Registration vectors fail to trigger Pub/Sub commands.
   * **Result:** Workers use stale vectors for matching implicitly bound up to standard DB flush operations, preserving system availability over consistency gracefully.

## Category B — Must Fail Closed
Operations that rely on strict mutual exclusion or authorization assertions explicitly fail closed.

1. **Distributed Idempotency Keys (Attendance SETNX):**
   * **Behavior:** If `setnx` execution fails, `AttendanceService` actively pivots seamlessly directly executing exact SQL reads across the authoritative Database structure mapping Unique bounds naturally via row scans prior to insertion.
   * **Result:** Strict safety over duplicated events.
   * *NOTE*: Unlike Local Memory Limits where bypassing limits is acceptable, bypassing exact identity duplicate checking breaks durability fundamentally.

2. **Distributed Locks (Session Ownership Context):**
   * **Behavior:** Hard timeouts fail closed throwing `RuntimeError` immediately blocking processing implicitly protecting ownership conflicts globally safely!
