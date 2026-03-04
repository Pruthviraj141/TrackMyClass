"""
Temporal Face Tracker.
Implements a multi-frame stability buffer to avoid false positives.
A student is only marked present after being detected consistently
across multiple frames with high average confidence.
"""

import time
from typing import Optional
from dataclasses import dataclass, field

from backend.config import (
    TEMPORAL_MIN_FRAMES,
    TEMPORAL_MIN_CONFIDENCE,
    TEMPORAL_TOLERANCE_MISSES,
    TEMPORAL_CLEANUP_SECONDS,
    SESSION_COOLDOWN_MINUTES,
)


@dataclass
class TrackedFace:
    """Tracks a single student's detection state across frames."""

    student_id: str
    name: str
    first_seen: float                        # time.time() of first detection
    last_seen: float                         # time.time() of most recent detection
    frame_count: int = 0                     # total frames detected in
    consecutive_misses: int = 0              # frames not seen in a row
    confidence_scores: list[float] = field(default_factory=list)
    marked: bool = False                     # has attendance been marked?
    marked_time: Optional[float] = None      # when attendance was marked

    @property
    def avg_confidence(self) -> float:
        """Average confidence across all tracked frames."""
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)

    @property
    def is_stable(self) -> bool:
        """
        Has this face been detected stably enough to mark attendance?
        Requires:
          - Detected in >= TEMPORAL_MIN_FRAMES frames
          - Average confidence >= TEMPORAL_MIN_CONFIDENCE
        """
        return (
            self.frame_count >= TEMPORAL_MIN_FRAMES
            and self.avg_confidence >= TEMPORAL_MIN_CONFIDENCE
        )

    @property
    def is_in_cooldown(self) -> bool:
        """Is this student still in the post-marking cooldown window?"""
        if not self.marked or self.marked_time is None:
            return False
        elapsed = time.time() - self.marked_time
        return elapsed < (SESSION_COOLDOWN_MINUTES * 60)


class TemporalTracker:
    """
    In-memory temporal face buffer.
    Tracks recognition results across frames and decides when
    to promote a detection into a confirmed attendance mark.
    """

    def __init__(self):
        # student_id -> TrackedFace
        self._buffer: dict[str, TrackedFace] = {}
        # student_ids that have been fully processed (marked) in this session
        self._session_marked: set[str] = set()
        self._frame_number: int = 0

    # ── Public API ────────────────────────────

    def update(self, recognized_faces: list[dict]) -> list[dict]:
        """
        Update the tracker with the latest frame's recognition results.

        Args:
            recognized_faces: List of dicts with keys:
                - student_id (str)
                - name (str)
                - confidence (float)
                - box (list)
                - status: 'recognized' for known faces, 'unknown' for unknown

        Returns:
            List of action dicts, each with:
                - student_id, name, confidence, box
                - action: 'mark' | 'tracking' | 'cooldown' | 'already_marked' | 'unknown'
        """
        self._frame_number += 1
        now = time.time()
        seen_ids: set[str] = set()
        actions: list[dict] = []

        for face in recognized_faces:
            sid = face["student_id"]

            # Unknown faces are passed through directly
            if sid == "unknown" or face.get("status") == "unknown":
                actions.append({
                    "student_id": "unknown",
                    "name": "Unknown",
                    "confidence": 0.0,
                    "box": face.get("box", []),
                    "action": "unknown",
                })
                continue

            seen_ids.add(sid)

            # Already marked in this session — no further action needed
            if sid in self._session_marked:
                tracked = self._buffer.get(sid)
                if tracked and tracked.is_in_cooldown:
                    actions.append({
                        "student_id": sid,
                        "name": face["name"],
                        "confidence": face["confidence"],
                        "box": face.get("box", []),
                        "action": "cooldown",
                    })
                else:
                    actions.append({
                        "student_id": sid,
                        "name": face["name"],
                        "confidence": face["confidence"],
                        "box": face.get("box", []),
                        "action": "already_marked",
                    })
                continue

            # Update or create tracked entry
            if sid in self._buffer:
                tracked = self._buffer[sid]
                tracked.last_seen = now
                tracked.frame_count += 1
                tracked.consecutive_misses = 0
                tracked.confidence_scores.append(face["confidence"])
            else:
                tracked = TrackedFace(
                    student_id=sid,
                    name=face["name"],
                    first_seen=now,
                    last_seen=now,
                    frame_count=1,
                    confidence_scores=[face["confidence"]],
                )
                self._buffer[sid] = tracked

            # Check if stable enough to mark
            if tracked.is_stable and not tracked.marked:
                actions.append({
                    "student_id": sid,
                    "name": tracked.name,
                    "confidence": round(tracked.avg_confidence, 4),
                    "box": face.get("box", []),
                    "action": "mark",
                })
                tracked.marked = True
                tracked.marked_time = now
                self._session_marked.add(sid)
            else:
                actions.append({
                    "student_id": sid,
                    "name": tracked.name,
                    "confidence": round(tracked.avg_confidence, 4),
                    "box": face.get("box", []),
                    "action": "tracking",
                    "frames_so_far": tracked.frame_count,
                    "frames_needed": TEMPORAL_MIN_FRAMES,
                })

        # Update misses for faces that were tracked but not seen this frame
        stale_ids = []
        for sid, tracked in self._buffer.items():
            if sid not in seen_ids and sid not in self._session_marked:
                tracked.consecutive_misses += 1
                if tracked.consecutive_misses > TEMPORAL_TOLERANCE_MISSES:
                    # Check if stale
                    if (now - tracked.last_seen) > TEMPORAL_CLEANUP_SECONDS:
                        stale_ids.append(sid)

        # Cleanup stale entries
        for sid in stale_ids:
            del self._buffer[sid]

        return actions

    def reset(self):
        """Reset tracker state (call when session ends)."""
        self._buffer.clear()
        self._session_marked.clear()
        self._frame_number = 0

    def get_stats(self) -> dict:
        """Get current tracker statistics."""
        return {
            "tracked_faces": len(self._buffer),
            "marked_count": len(self._session_marked),
            "frame_number": self._frame_number,
        }


# ── Module-level singleton ──
_tracker = TemporalTracker()


def get_tracker() -> TemporalTracker:
    """Get the global TemporalTracker singleton."""
    return _tracker
