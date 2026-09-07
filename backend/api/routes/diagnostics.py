"""
Diagnostics & Health Router
Aggregates internal latencies and metrics returning safe observational boundaries.
"""
from fastapi import APIRouter
from backend.worker.worker_manager import get_worker_manager

router = APIRouter(prefix="/api/v1/diagnostics", tags=["System Health"])

@router.get("/metrics")
async def get_metrics():
    """
    Returns Phase 8 aggregate telemetry.
    No sensitive tokens or bio-metrics are rendered. Allows zero-credential monitoring safely.
    """
    manager = get_worker_manager()
    worker_health = manager.health
    
    # Check dependencies (Redis/DB)
    redis_status = "unavailable"
    from backend.core.redis_client import RedisManager
    try:
        rc = RedisManager.get_client()
        if rc:
            await rc.ping()
            redis_status = "ok"
    except Exception:
        pass
        
    return {
        "status": "healthy" if worker_health["status"] == "ok" and redis_status == "ok" else "degraded",
        "worker": {
            "status": worker_health.get("status"),
            "queue_depth": worker_health.get("queue_depth"),
            "frames_dropped": worker_health.get("frames_dropped_total"),
            "total_restarts": worker_health.get("restarts_total"),
            "jobs_processed": worker_health.get("jobs_processed"),
            "latency_p50_ms": worker_health.get("average_latency_ms")
        },
        "redis": {
            "status": redis_status
        }
    }
