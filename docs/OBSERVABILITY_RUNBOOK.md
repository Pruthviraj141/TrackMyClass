# OBSERVABILITY RUNBOOK

This runbook acts as the standard protocol guiding failure analysis uniquely via Phase 8 structural constraints.

## 1. High recognition latency
- **Symptom**: `latency_p50_ms` on `/api/v1/diagnostics/metrics` is > 1500 MS continuously.
- **Diagnostics**: Read explicit `Pipeline Telemetry` JSON logs filtering `embedding_total_ms`. Identify if PyTorch threads are overloaded.
- **Solution**: Restart workers or bounds capacity.

## 2. Queue Saturation
- **Symptom**: `frames_dropped` increases linearly.
- **Diagnostics**: ML Worker limits frame arrays to 2 per processor inherently. Increased drops indicate too high WebSocket input frequency.
- **Solution**: Decrease `_RATE_LIMIT_FPS`.

## 3. Worker Unavailable
- **Symptom**: `diagnostics` reports `worker.status == unavailable`.
- **Diagnostics**: View worker restart increments natively. Follow logs identifying exact model binding corruptions natively. Needs hard process kills.
