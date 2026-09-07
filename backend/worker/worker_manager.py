"""
WorkerManager — singleton that manages the inference subprocess lifecycle.

Responsibilities:
  - Start / stop the worker process
  - Submit frames and route results back to waiting WebSocket handlers
  - Health probe: classify worker as ok / unavailable / overloaded
  - Auto-restart on crash (with backoff)
  - Guarantee queue bounds enforcing MAX_QUEUE_SIZE replacing oldest items.

Usage (from WebSocket handler):
  mgr = get_worker_manager()
  result = await mgr.submit_frame(institution_id, session_id, frame_bytes)
"""
import asyncio
import multiprocessing
import queue
import time
import threading
import uuid
from typing import Dict, Optional

from backend.worker.inference_worker import _worker_main

# Maximum seconds between worker heartbeats before we consider it hung
_HEARTBEAT_TIMEOUT = 10.0
# Hard configuration bound for the queue
MAX_QUEUE_SIZE = 2
# Seconds between restart attempts after a crash
_RESTART_BACKOFF = 2.0


class WorkerManager:
    def __init__(self) -> None:
        self._process: Optional[multiprocessing.Process] = None
        self._task_queue: Optional[multiprocessing.Queue] = None
        self._result_queue: Optional[multiprocessing.Queue] = None
        self._heartbeat: Optional[multiprocessing.Value] = None
        self._stop_event: Optional[multiprocessing.Event] = None

        # Maps a correlation_id → asyncio.Future so results reach callers
        self._pending: Dict[str, asyncio.Future] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        self._started = False
        self._crashed = False
        self._lock = threading.Lock()
        
        # Telemetry Bounds
        self._frames_dropped_total = 0
        self._jobs_processed_total = 0
        self._restarts_total = 0
        self._latency_samples = []

        # Background thread that reads the result queue and resolves futures
        self._reader_thread: Optional[threading.Thread] = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        with self._lock:
            if self._started:
                return
            self._loop = loop
            self._launch_process()
            self._started = True

    def _launch_process(self) -> None:
        """Spawn a fresh worker process and start the result-reader thread."""
        self._restarts_total += 1
        ctx = multiprocessing.get_context("spawn")
        self._task_queue = ctx.Queue(maxsize=MAX_QUEUE_SIZE)
        self._result_queue = ctx.Queue()
        self._heartbeat = ctx.Value("d", time.monotonic())
        self._stop_event = ctx.Event()
        self._crashed = False

        self._process = ctx.Process(
            target=_worker_main,
            args=(self._task_queue, self._result_queue, self._heartbeat, self._stop_event),
            daemon=True,
            name="TrackMyClass-InferenceWorker",
        )
        self._process.start()

        # (Re)start result reader thread
        self._reader_thread = threading.Thread(
            target=self._result_reader, daemon=True, name="ResultReader"
        )
        self._reader_thread.start()

    def stop(self) -> None:
        with self._lock:
            if self._stop_event:
                self._stop_event.set()
            if self._process and self._process.is_alive():
                self._process.join(timeout=3)
                if self._process.is_alive():
                    self._process.kill()
            self._started = False

    # ── Health ───────────────────────────────────────────────────────────────

    @property
    def health(self) -> dict:
        base = {
            "queue_depth": self._task_queue.qsize() if self._task_queue else 0,
            "frames_dropped_total": self._frames_dropped_total,
            "restarts_total": self._restarts_total,
            "jobs_processed": self._jobs_processed_total,
            "average_latency_ms": sum(self._latency_samples[-10:]) / 10 if len(self._latency_samples) >= 10 else 0
        }
        
        if not self._started or self._crashed:
            base["status"] = "unavailable"
            return base
            
        if self._process and not self._process.is_alive():
            base["status"] = "unavailable"
            return base
            
        if self._heartbeat:
            age = time.monotonic() - self._heartbeat.value
            base["heartbeat_age_s"] = round(age, 1)
            if age > _HEARTBEAT_TIMEOUT:
                base["status"] = "overloaded"
                return base
                
        base["status"] = "ok"
        return base

    # ── Frame submission ─────────────────────────────────────────────────────

    async def submit_frame(
        self,
        institution_id: str,
        session_id: str,
        frame_bytes: bytes,
    ) -> dict:
        """
        Submit a frame for inference and await the result.

        Returns a result dict (same schema as attendance_service).
        Raises RuntimeError if the worker is unavailable.
        """
        if self.health["status"] == "unavailable":
            # Attempt restart in background
            self._maybe_restart()
            raise RuntimeError("Inference worker is unavailable")

        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()

        with self._lock:
            self._pending[correlation_id] = future

        task = {
            "correlation_id": correlation_id,
            "institution_id": institution_id,
            "session_id": session_id,
            "frame_bytes": frame_bytes,
        }

        try:
            # Non-blocking put
            self._task_queue.put_nowait(task)
        except queue.Full:
            # LATEST_FRAME_WINS bound logic: drop oldest eligible frame 
            try:
                stale = self._task_queue.get_nowait()
                old_cid = stale.get("correlation_id")
                with self._lock:
                    if old_cid in self._pending:
                        future_stale = self._pending.pop(old_cid)
                        if not future_stale.done():
                            self._loop.call_soon_threadsafe(future_stale.set_exception, RuntimeError("Frame dropped (LATEST-FRAME-WINS queue limit)"))
            except queue.Empty:
                pass
            
            try:
                self._task_queue.put_nowait(task)
                self._frames_dropped_total += 1
            except queue.Full:
                with self._lock:
                    self._pending.pop(correlation_id, None)
                self._frames_dropped_total += 1
                raise RuntimeError("Worker queue absolutely full — frame dropped")

        try:
            result = await asyncio.wait_for(future, timeout=5.0)
        except asyncio.TimeoutError:
            with self._lock:
                self._pending.pop(correlation_id, None)
            raise RuntimeError("Inference timed out")

        return result

    # ── Result reader (runs in a background thread) ──────────────────────────

    def _result_reader(self) -> None:
        """Pull results from the multiprocessing Queue and resolve Futures."""
        while True:
            try:
                if self._result_queue is None:
                    break
                result = self._result_queue.get(timeout=1.0)
            except Exception:
                # Check if process died
                if self._process and not self._process.is_alive() and not (self._stop_event and self._stop_event.is_set()):
                    self._crashed = True
                    self._fail_all_pending("Worker process crashed")
                    self._maybe_restart()
                continue

            cid = result.pop("correlation_id", None)
            
            # Extract latency measurements if yielded from the neural loops
            proc_ms = result.get("processing_ms")
            if proc_ms:
                self._latency_samples.append(proc_ms)
                if len(self._latency_samples) > 100:
                    self._latency_samples.pop(0)
            self._jobs_processed_total += 1
            
            if cid and self._loop:
                with self._lock:
                    future = self._pending.pop(cid, None)
                if future and not future.done():
                    self._loop.call_soon_threadsafe(future.set_result, result)

    def _fail_all_pending(self, reason: str) -> None:
        if not self._loop:
            return
        with self._lock:
            pending = list(self._pending.items())
            self._pending.clear()
        for cid, future in pending:
            if not future.done():
                self._loop.call_soon_threadsafe(
                    future.set_exception, RuntimeError(reason)
                )

    def _maybe_restart(self) -> None:
        def _restart():
            time.sleep(_RESTART_BACKOFF)
            with self._lock:
                if self._started:
                    self._launch_process()
        t = threading.Thread(target=_restart, daemon=True)
        t.start()


# ── Module-level singleton ────────────────────────────────────────────────────
_manager: Optional[WorkerManager] = None


def get_worker_manager() -> WorkerManager:
    global _manager
    if _manager is None:
        _manager = WorkerManager()
    return _manager
