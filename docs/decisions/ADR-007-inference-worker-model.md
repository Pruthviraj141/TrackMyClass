# ADR-007: Inference Worker Model

**Status**: Accepted  
**Date**: 2026-09-06

## Context

MTCNN face detection and FaceNet embedding generation are CPU-bound PyTorch operations taking ~100–230 ms per frame. Running these inside the ASGI event loop blocks all concurrent requests during inference.

Two isolation models were evaluated: threading vs. subprocess.

## Options Evaluated

### Threading (`ThreadPoolExecutor`)
- Python GIL is released during I/O but **held during CPU-bound PyTorch C-extension execution**
- Multiple threads do not achieve true parallelism for CPU-bound NumPy/PyTorch code
- Shared memory simplifies result passing but introduces potential race conditions
- No process-level isolation: a segfault in MTCNN/FaceNet would crash the ASGI worker

### Process (`ProcessPoolExecutor` / `multiprocessing`)
- Each worker runs in its own OS process with its own GIL
- True CPU parallelism for PyTorch operations
- Model state fully isolated from the API process
- Communication via `multiprocessing.Queue` (picklable data only)
- Startup cost: model loading once per worker process lifetime (~2–4 s); amortized across all frames
- Crash isolation: If the inference process segfaults, the API process continues serving HTTP/WS

## Decision

**Separate process** using Python `multiprocessing` with `spawn` context.

Models (MTCNN + FaceNet) are loaded **once** at worker startup and reused for the lifetime of that process.

## Consequences

- API event loop is never blocked by inference
- Light API endpoints (`/api/v1/admin/dashboard-data`) remain responsive during heavy recognition
- Frame data must be picklable (raw `bytes` — no PIL Image objects or PyTorch Tensors across process boundary)
- `WorkerManager` handles lifecycle: start, health probe, crash detection, auto-restart with backoff
- One worker process per application instance (sufficient for current single-server deployment)
