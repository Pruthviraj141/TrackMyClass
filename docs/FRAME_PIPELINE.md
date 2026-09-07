# Frame Pipeline

## Design Principle

> The system must prefer fresh frames over stale frames. Under backpressure, drop old frames rather than accumulate an unbounded queue.

## Architecture

```
WebSocket handler          FrameQueue (depth=1)      Inference Worker Process
       |                         |                           |
  receive binary frame ------> put()                        |
       |                         |  evict stale frame        |
       |                  [frame slot]                       |
       |                         |                           |
                                get() <-------------------- poll (0.5 s timeout)
                                 |                           |
                                 +------> process_frame() --+
                                                            |
                                               result_queue.put(result)
                                                            |
                              WorkerManager <---- result reader thread
                                    |
                              Future.set_result()
                                    |
                         WS handler await submit_frame()
                                    |
                         push recognition.result to client
```

## Queue Parameters

| Parameter | Value | Rationale |
|---|---|---|
| Queue depth | 1 | Latest-frame-wins: no benefit in reviewing stale frames |
| Drop policy | Evict-on-put | When a new frame arrives, the pending stale frame is discarded |
| Frame ordering | Not preserved across evictions | Freshness preferred |
| Worker poll timeout | 0.5 s | Minimum heartbeat latency |
| Max frame size | 512 KB | Validated before enqueue; oversized frames rejected |
| Backend mp.Queue maxsize | 2 | Acts as a secondary safety buffer between the FrameQueue and the OS queue |

## Backpressure Behavior

When the camera produces frames faster than inference can process them:

1. WS handler calls `FrameQueue.put(new_frame)`
2. If a frame is already in the queue, it is count-incremented to `dropped` and evicted
3. New frame occupies the single queue slot
4. Inference worker picks up only the latest frame available

**Result**: Memory is bounded regardless of camera FPS or inference speed.

## Rate Limiter

An additional server-side token bucket limits client submissions to **5 frames/s** per connection:

- Rolling 1-second window
- Frames that exceed the budget are silently dropped at the WS handler before they reach `FrameQueue`
- This prevents a malicious or poorly-configured client from flooding the queue

## Frame Format

Frames are transmitted as **raw JPEG bytes** over binary WebSocket frames.

| Format | Phase 4 (Base64 JSON) | Phase 5 (Binary JPEG) |
|---|---|---|
| 640×480 frame size | ~43 KB (base64 overhead) | ~30 KB |
| Encoding overhead | ~33% inflation | None |
| CPU encode (client) | `canvas.toDataURL()` + JSON.stringify | `canvas.toBlob()` |
| CPU decode (server) | base64.b64decode + json parse | Direct `BytesIO(raw)` |

## Failure Modes

| Scenario | Behavior |
|---|---|
| Worker unavailable | `worker.unavailable` WS message; frame not queued |
| Worker crashes | `WorkerManager` detects dead process; auto-restarts with 2 s backoff |
| Frame too large | `warning` WS message; frame dropped before queue |
| Client sends too fast | Rate-limited frames silently dropped |
| Inference timeout (5 s) | Future times out; `inference.error` sent to client |
