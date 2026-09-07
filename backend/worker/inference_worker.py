"""
InferenceWorker — process-isolated CPU-bound recognition.

Designed to run in a separate OS process via multiprocessing so that
Python's GIL does not block the ASGI event loop during MTCNN + FaceNet
inference.

Lifecycle:
  1. Worker process starts → loads MTCNN + FaceNet once (heavy, ~2-4 s)
  2. Enters poll loop → reads from a multiprocessing Queue
  3. For each frame: runs RecognitionEngine.process_frame()
  4. Pushes result dict to result Queue
  5. Updates a shared heartbeat value so the manager can detect hangs

Frame format sent to this worker:
  {
    "institution_id": str,
    "session_id": str,
    "frame_bytes": bytes,   # raw JPEG
  }

Result format pushed back:
  {
    "session_id": str,
    "institution_id": str,
    "results": List[dict],  # same schema as attendance_service returns
    "processing_ms": float,
    "error": str | None,
  }
"""
import time
import multiprocessing
import traceback
from io import BytesIO

from PIL import Image
from backend.core.logger import get_structured_logger

logger = get_structured_logger(__name__)


def _pubsub_listener():
    """
    Background daemon thread within the worker process.
    Subscribes to Redis cache invalidation events.
    """
    try:
        import redis
        from backend.core.config import REDIS_URL
        from backend.ml.matcher.optimized_recognition import get_embedding_cache
        
        r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        p = r.pubsub()
        p.subscribe("cache:invalidation")
        print("Worker Pub/Sub listener active.")
        for msg in p.listen():
            if msg['type'] == 'message':
                inst_id = msg['data']
                logger.info(f"Worker received cache invalidation for {inst_id}")
                get_embedding_cache().refresh(inst_id)
    except Exception as e:
        logger.exception(f"Worker Redis Subscriber failed: {e}")


def _worker_main(
    task_queue: multiprocessing.Queue,
    result_queue: multiprocessing.Queue,
    heartbeat: multiprocessing.Value,
    stop_event: multiprocessing.Event,
) -> None:
    """
    Entry point for the worker subprocess.

    Loads ML models once then processes frames until stop_event is set.
    """
    # ── Model init (runs once per worker lifetime) ──────────────────────────
    try:
        from backend.ml.detector.face_detection import get_detector
        from backend.ml.embedding.facenet_model import get_facenet_model
        # Warm up both singletons inside this process
        get_detector()
        get_facenet_model()
    except Exception as exc:
        result_queue.put({"error": f"Worker model init failed: {exc}", "results": []})
        return

    import threading
    t = threading.Thread(target=_pubsub_listener, daemon=True)
    t.start()

    # ── Frame processing loop ────────────────────────────────────────────────
    while not stop_event.is_set():
        try:
            task = task_queue.get(timeout=0.5)
        except Exception:
            # Timed out — update heartbeat and loop
            with heartbeat.get_lock():
                heartbeat.value = time.monotonic()
            continue

        # Extract parent process WS correlation IDs
        from backend.core.logger import correlation_id_ctx, session_id_ctx
        institution_id = task.get("institution_id", "")
        session_id = task.get("session_id", "")
        corr_id = task.get("correlation_id", "n/a")
        correlation_id_ctx.set(corr_id)
        session_id_ctx.set(session_id)
        
        t0 = time.monotonic()
        frame_bytes = task.get("frame_bytes", b"")

        result = {
            "correlation_id": corr_id,
            "session_id": session_id,
            "institution_id": institution_id,
            "results": [],
            "processing_ms": 0.0,
            "error": None,
        }

        try:
            from backend.ml.engine import RecognitionEngine
            from backend.core.config import FRAME_RESIZE_WIDTH

            if not frame_bytes:
                raise ValueError("Empty frame")

            try:
                image = Image.open(BytesIO(frame_bytes)).convert("RGB")
            except Exception:
                # Silently ignore unidentifiable image errors (e.g. on stream start)
                image = None
                
            if image:
                w, h = image.size
                ratio = 1.0
                if w > FRAME_RESIZE_WIDTH:
                    ratio = FRAME_RESIZE_WIDTH / w
                    image = image.resize((FRAME_RESIZE_WIDTH, int(h * ratio)), Image.BILINEAR)

                engine = RecognitionEngine(institution_id)
                raw_results = engine.process_frame(session_id, image)

                result["results"] = []
                for r in raw_results:
                    inv_scale = 1.0 / ratio
                    x1, y1, x2, y2 = r.bounding_box
                    result["results"].append({
                        "student_id": r.student_id,
                        "name": r.name,
                        "confidence": r.similarity,
                        "status": r.recognition_state,
                        "box": [x1 * inv_scale, y1 * inv_scale, x2 * inv_scale, y2 * inv_scale],
                    })
        except Exception as exc:
            logger.exception("Worker recognition error inside engine block")
            result["error"] = str(exc)

        result["processing_ms"] = round((time.monotonic() - t0) * 1000, 2)
        result_queue.put(result)

        with heartbeat.get_lock():
            heartbeat.value = time.monotonic()
