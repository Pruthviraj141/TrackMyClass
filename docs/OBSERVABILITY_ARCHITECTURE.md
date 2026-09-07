# OBSERVABILITY ARCHITECTURE

## 1. Logs
All Python processes (API routes, Worker, Engine) utilize `backend.core.logger.get_structured_logger`.
This mounts a native JSONFormatter isolating contexts explicitly.
- **Trace correlation**: Generates `correlation_id` bound to standard `contextvars`. Passes into sub-processes.
- **Rules**: Zero printing of dense mathematical Tensors or Face Cropping binaries.

## 2. Telemetry and Latencies (Pipeline bounds)
The `/api/v1/diagnostics/metrics` route renders:
- Work queue bounds: Tracks drops exactly resolving lag saturation.
- `RecognitionEngine` breaks down processing implicitly bounding trace MS directly mapping detection, embedding, matching independently.

## 3. Worker Heartbeats & Liveness
Health dictionaries record exact Restart Counts, Dropped frames, and total jobs implicitly returning `status: unavailable/overloaded/ok` locally via multiprocessing values safely avoiding Redis pings inherently.
