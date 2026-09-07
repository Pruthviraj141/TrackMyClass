# ADR-008: Redis for Transient Distributed State 

## Context
With inference process isolations complete and horizontal API scaling inevitable, TrackMyClass inherently struggles natively with local-memory bottlenecks preventing clean scale limits. Things like Rate Limiting and Embedding Caches naturally drift if scaled locally globally.

## Decision
We explicitly adopt **Redis** to execute transient distributed coordination limits over the FastAPI cluster natively cleanly. We are *specifically* preventing Redis from absorbing heavy payloads.

## Constraints
1. **No Image Buffers:** Redis will not transport bounded JPEG streams over the wire due to performance overhead risks gracefully.
2. **No Raw Embedding Tensors:** Matrices remain isolated securely in process-local `WorkerManager` limits strictly. Redis acts merely as a Pub/Sub trigger alerting nodes to re-query the SQLite database natively cleanly.
3. **Primary State Authoritative Source:** Redis is *never* used as permanent object mappings cleanly natively. SQLite retains permanent durable state properly inherently.

## Implementation Zones
- Lua Script Distributed Rate Limits securely globally.
- PubSub channels triggering `INVALIDATE_STUDENT_EMBEDDING` messages across Worker nodes natively.
- Light coordination locks gracefully handling attendance deduplication natively globally avoiding Database race condition explosions correctly cleanly.
