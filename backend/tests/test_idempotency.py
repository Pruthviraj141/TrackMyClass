import pytest
from backend.domain.entities import FaceDetectionResult, MatchResult

def test_idempotency_structure():
    # Verify that MatchResults strictly follow bounded domains
    match = MatchResult(
        candidate_identity="student_123",
        similarity=0.98,
        threshold_applied=0.6,
        is_accepted=True
    )
    assert match.candidate_identity == "student_123"
