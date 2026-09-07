# Distributed State Architecture & Semantics

## Core Principles

1.  **Stateless API Layer:** The FastAPI API nodes operate immutably for heavy lifting, outsourcing shared-state caching exclusively to **Redis**.
2.  **Ephemerality of Redis:** Redis handles Transient Application States *only*. E.g., rate-limiting arrays, active institution markers, and Pub/Sub Event Triggers. SQLite maintains Durable System of Record capability.
3.  **Graceful Degradation:** Redis is treated as a brittle microservice. Outages are silently intercepted; token-buckets retreat to RAM memory algorithms, Session sync is ignored (allowing process-local isolated sessions), ensuring High Availability.

## Modules Migrated
- `Rate Limiting`: Converted to a distributed sliding window via Lua execution logic to prevent Race Conditions.
- `Session Coordinator`: Converted to sync Active `institution_id` keys over Redis for cross-node recognition.
- `Registration Service`: Emits a `cache:invalidation` event via Pub/Sub when a student record updates.
- `Inference Worker`: Contains an isolated threaded daemon listening to invalidations, hot-reloading `numpy` embedding caches.
- `Attendance Engine`: Validates duplicated incoming identical frames via Redis `SETNX` distributed locks to prevent SQLite unique constraint corruption.
