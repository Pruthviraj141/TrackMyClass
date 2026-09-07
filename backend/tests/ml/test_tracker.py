import pytest
from backend.ml.domain import FaceDetectionResult, MatchResult
from backend.ml.tracker.temporal_tracker import TemporalTracker

def test_stable_identity_marking():
    tracker = TemporalTracker()
    box = [0, 0, 100, 100]
    match = MatchResult("person_a", 0.95, 0.75, True)
    fdr = FaceDetectionResult(box, 0.99, None)
    
    # 4 consecutive frames required for TEMPORAL_MIN_FRAMES
    tracker.update([(match, fdr)])
    tracker.update([(match, fdr)])
    tracker.update([(match, fdr)])
    res = tracker.update([(match, fdr)])
    
    assert len(res) == 1
    assert res[0].student_id == "person_a"
    assert res[0].recognition_state == "mark"
    assert res[0].verification_state is True

def test_identity_switch_no_bleeding():
    tracker = TemporalTracker()
    box = [0, 0, 100, 100]
    fdr = FaceDetectionResult(box, 0.99, None)
    
    # A A A (Not marked yet)
    tracker.update([(MatchResult("A", 0.95, 0.75, True), fdr)])
    tracker.update([(MatchResult("A", 0.95, 0.75, True), fdr)])
    tracker.update([(MatchResult("A", 0.95, 0.75, True), fdr)])
    
    # Suddenly jumps to B
    res_b = tracker.update([(MatchResult("B", 0.95, 0.75, True), fdr)])
    
    # B must NOT inherit A's stability. It must start tracking from 0.
    assert len(res_b) == 1
    assert res_b[0].student_id == "B"
    assert res_b[0].recognition_state == "tracking"
    assert res_b[0].verification_state is False

def test_session_reset_purges_tracker():
    tracker = TemporalTracker()
    box = [0, 0, 100, 100]
    
    res = tracker.update([(MatchResult("A", 0.95, 0.75, True), FaceDetectionResult(box, 0.99, None))])
    assert len(tracker._buffer) == 1
    
    tracker.reset()
    assert len(tracker._buffer) == 0
    assert len(tracker._session_marked) == 0
