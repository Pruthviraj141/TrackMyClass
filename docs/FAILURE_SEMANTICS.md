# Redis Failure Semantics

TrackMyClass requires an aggressive stance on gracefully mitigating infrastructural collapse. If Redis (`redis-trackmyclass`) restarts, crashes, or pauses:

## 1. Rate Limiting Failover
- TokenBucket limits gracefully catch the `redis.exceptions.ConnectionError`.
- FastApi falls back to `local_memory_buckets` tracked internally per route process.
- No user sees a 500.

## 2. Session Integrity Check
- `session_service.py` is fully wrapped with `try/except`.
- An inactive connection doesn't drop the active session; the node defaults to fetching its local RAM Active trackers.

## 3. Worker Pub/Sub Recovery
- The Daemon pub/sub listener runs continuously.
- Reconnect handles are deferred entirely by `redis.Redis().pubsub()`, ensuring that it connects when available, silently awaiting otherwise.
- The Numpy embeddings matrix continues running linearly over outdated cache arrays until connections restore and the next sync emits correctly.

## 4. Idempotency Overlap Risk During Failure
- The Redis `SETNX` lock is wrapped in logic allowing `can_mark`.
- If `RedisManager.get_client()` returns `None`, it allows SQLite to resolve the unique constraints directly.
