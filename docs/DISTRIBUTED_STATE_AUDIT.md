# Distributed State Audit

## Overview
Phase 5 introduced process isolation for multi-core inference scaling, naturally distributing local memory. This audit reviews what state exists natively in current instances and designates how it transitions into the Phase 6 distributed architecture gracefully.

### 1. TokenBuckets (Rate Limiting)
- **Current State:** Reside in standard `dict` memory limits globally on FastAPI endpoints.
- **Problem:** If deployed over 4 horizontally scaled API containers, limits fail as attackers are bottlenecked per container separately, yielding effectively 4x traffic limits.
- **Action:** Migrate into shared Transient Store (Redis Lua Scripts).

### 2. Active Session Metadata
- **Current State:** Polled off SQLite heavily, with transient Websocket connections pinning themselves locally to singular node memory blocks.
- **Problem:** Other nodes lack immediate visibility into active state metrics inherently gracefully without causing DB spikes.
- **Action:** Transition core metadata (`session_id=>status`) to Redis Sets/Hashes inherently protecting the primary database structurally.

### 3. FrameQueue & Processing
- **Current State:** Bound tightly in `<worker/frame_queue.py>` natively handling raw JPEG binary loops natively.
- **Action:** Ensure this stays LOCAL. Moving multi-megabyte frame payloads structurally through Redis yields no functional benefits natively and massively craters throughput securely.

### 4. Embedding Matrices & Tensors
- **Current State:** Explicit process-local Numpy arrays functionally cached strictly within MTCNN execution block paths securely.
- **Problem:** If Student A is enrolled, Worker 1 updates but Worker 2 natively holds stale variables essentially failing Face Recognition structurally.
- **Action:** Remain LOCAL, but integrate **Redis Pub/Sub** to securely deliver cache-invalidation "reload" pings across all active workers instantaneously effectively preventing cross-node drift inherently.
