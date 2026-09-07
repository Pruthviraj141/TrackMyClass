"""
FrameQueue — bounded, latest-frame-wins queue.

Depth is always 1. When a new frame arrives while a frame is already
waiting to be processed, the stale frame is evicted and the fresh frame
takes its place. This guarantees:

  - No unbounded memory growth
  - Inference always runs on the freshest available frame
  - Under backpressure (inference slower than camera) frames are dropped
    gracefully instead of accumulating
"""
import threading
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QueuedFrame:
    institution_id: str
    session_id: str
    frame_bytes: bytes
    enqueued_at: float = field(default_factory=time.monotonic)


class FrameQueue:
    """Thread-safe bounded queue with depth=1 latest-frame-wins policy."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._item: Optional[QueuedFrame] = None
        self._dropped: int = 0
        self._total_enqueued: int = 0

    def put(self, frame: QueuedFrame) -> bool:
        """
        Enqueue a frame.

        If a frame is already waiting, it is evicted (dropped) and the new
        frame takes its place. Returns True if a stale frame was dropped.
        """
        with self._condition:
            dropped = self._item is not None
            if dropped:
                self._dropped += 1
            self._item = frame
            self._total_enqueued += 1
            self._condition.notify_all()
        return dropped

    def get(self, timeout: float = 1.0) -> Optional[QueuedFrame]:
        """
        Block until a frame is available or timeout expires.

        Returns the frame (and clears the slot) or None on timeout.
        """
        with self._condition:
            if not self._item:
                self._condition.wait(timeout=timeout)
            frame = self._item
            self._item = None
        return frame

    @property
    def stats(self) -> dict:
        with self._lock:
            return {
                "pending": 1 if self._item else 0,
                "total_enqueued": self._total_enqueued,
                "total_dropped": self._dropped,
                "drop_rate": round(self._dropped / max(self._total_enqueued, 1), 3),
            }
