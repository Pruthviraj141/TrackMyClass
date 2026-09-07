"""
Temporal Face Tracker.
Isolates multi-frame stability cleanly bounding 'Identity Switches'.
Produces explicit RecognitionResult instances.
"""
import time
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

from backend.core.config import (
    TEMPORAL_MIN_FRAMES,
    TEMPORAL_MIN_CONFIDENCE,
    TEMPORAL_TOLERANCE_MISSES,
    TEMPORAL_CLEANUP_SECONDS,
    SESSION_COOLDOWN_MINUTES,
)
from backend.ml.domain import RecognitionResult, MatchResult, FaceDetectionResult

@dataclass
class TrackedFace:
    student_id: str
    name: str
    first_seen: float
    last_seen: float
    frame_count: int = 0
    consecutive_misses: int = 0
    confidence_scores: list[float] = field(default_factory=list)
    marked: bool = False
    marked_time: Optional[float] = None

    @property
    def avg_confidence(self) -> float:
        if not self.confidence_scores: return 0.0
        return sum(self.confidence_scores) / len(self.confidence_scores)

    @property
    def is_stable(self) -> bool:
        return (
            self.frame_count >= TEMPORAL_MIN_FRAMES
            and self.avg_confidence >= TEMPORAL_MIN_CONFIDENCE
        )

    @property
    def is_in_cooldown(self) -> bool:
        if not self.marked or self.marked_time is None: return False
        elapsed = time.time() - self.marked_time
        return elapsed < (SESSION_COOLDOWN_MINUTES * 60)

class TemporalTracker:
    def __init__(self):
        # Scoped by session_id
        self._buffers: dict[str, dict[str, TrackedFace]] = {}
        self._session_marked: dict[str, set[str]] = {}

    def update(self, session_id: str, frame_matches: List[Tuple[Optional[MatchResult], FaceDetectionResult]]) -> List[RecognitionResult]:
        now = time.time()
        seen_ids: set[str] = set()
        results: List[RecognitionResult] = []

        if session_id not in self._buffers:
            self._buffers[session_id] = {}
        if session_id not in self._session_marked:
            self._session_marked[session_id] = set()

        current_buffer = self._buffers[session_id]
        current_marked = self._session_marked[session_id]

        for match, detection in frame_matches:
            if match is None:
                # Unknown face
                results.append(RecognitionResult(
                    student_id="unknown",
                    name="Unknown",
                    bounding_box=detection.bounding_box,
                    similarity=0.0,
                    recognition_state="unknown",
                    verification_state=False
                ))
                continue
            
            sid = match.candidate_identity
            seen_ids.add(sid)

            if sid in current_marked:
                tracked = current_buffer.get(sid)
                if tracked and tracked.is_in_cooldown:
                    state = "cooldown"
                else:
                    state = "already_marked"
                    
                results.append(RecognitionResult(
                    student_id=sid,
                    name=tracked.name if tracked else sid,
                    bounding_box=detection.bounding_box,
                    similarity=match.similarity,
                    recognition_state=state,
                    verification_state=True
                ))
                continue

            if sid in current_buffer:
                tracked = current_buffer[sid]
                tracked.last_seen = now
                tracked.frame_count += 1
                tracked.consecutive_misses = 0
                tracked.confidence_scores.append(match.similarity)
            else:
                tracked = TrackedFace(
                    student_id=sid,
                    name=sid,
                    first_seen=now,
                    last_seen=now,
                    frame_count=1,
                    confidence_scores=[match.similarity],
                )
                self._buffers[session_id][sid] = tracked

            if tracked.is_stable and not tracked.marked:
                tracked.marked = True
                tracked.marked_time = now
                current_marked.add(sid)
                results.append(RecognitionResult(
                    student_id=sid,
                    name=tracked.name,
                    bounding_box=detection.bounding_box,
                    similarity=match.similarity,
                    recognition_state="mark",
                    verification_state=True
                ))
            else:
                results.append(RecognitionResult(
                    student_id=sid,
                    name=tracked.name,
                    bounding_box=detection.bounding_box,
                    similarity=match.similarity,
                    recognition_state="tracking",
                    verification_state=False
                ))

        stale_ids = []
        for sid, tracked in current_buffer.items():
            if sid not in seen_ids and sid not in current_marked:
                tracked.consecutive_misses += 1
                if tracked.consecutive_misses > TEMPORAL_TOLERANCE_MISSES:
                    if (now - tracked.last_seen) > TEMPORAL_CLEANUP_SECONDS:
                        stale_ids.append(sid)

        for sid in stale_ids:
            del current_buffer[sid]

        return results

    def reset(self, session_id: Optional[str] = None):
        if session_id:
            if session_id in self._buffers:
                del self._buffers[session_id]
            if session_id in self._session_marked:
                del self._session_marked[session_id]
        else:
            self._buffers.clear()
            self._session_marked.clear()

_tracker = TemporalTracker()

def get_tracker() -> TemporalTracker:
    return _tracker
