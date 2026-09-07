import asyncio
import time
from backend.ml.domain import MatchResult, FaceDetectionResult
from backend.ml.tracker.temporal_tracker import get_tracker

async def test_tracker_scoping():
    print("Testing ML Tracker Scoping by session_id...")
    tracker = get_tracker()
    tracker.reset()

    # Mock detection
    detection = FaceDetectionResult(bounding_box=(0, 0, 10, 10), face_crop_tensor=None)
    match = MatchResult(candidate_identity="98634d00-47ab-4ebd-b227-bf5135a8be10", similarity=0.90)

    print("\n--- Session 1 ---")
    session1 = "session_aaaa"
    # Send frame 1
    r1 = tracker.update(session1, [(match, detection)])
    print(f"Frame 1 (Session 1): {r1[0].recognition_state}") # Should be 'tracking'

    time.sleep(0.1) # Simulate FPS

    # Send frame 2 (makes it stable since TEMPORAL_MIN_FRAMES=2)
    r2 = tracker.update(session1, [(match, detection)])
    print(f"Frame 2 (Session 1): {r2[0].recognition_state}") # Should be 'mark'

    time.sleep(0.1)

    # Send frame 3 (already marked)
    r3 = tracker.update(session1, [(match, detection)])
    print(f"Frame 3 (Session 1): {r3[0].recognition_state}") # Should be 'already_marked'

    print("\n--- Session 2 ---")
    session2 = "session_bbbb"
    
    # In the bugged version, this would be 'already_marked' because _session_marked leaked
    # In the fixed version, this should be 'tracking'
    r4 = tracker.update(session2, [(match, detection)])
    print(f"Frame 1 (Session 2): {r4[0].recognition_state}")
    assert r4[0].recognition_state == "tracking", f"Expected 'tracking', got {r4[0].recognition_state}"

    time.sleep(0.1)
    
    r5 = tracker.update(session2, [(match, detection)])
    print(f"Frame 2 (Session 2): {r5[0].recognition_state}")
    assert r5[0].recognition_state == "mark", f"Expected 'mark', got {r5[0].recognition_state}"

    print("\nSUCCESS! Tracker handles sessions elegantly without leaking!")

if __name__ == "__main__":
    asyncio.run(test_tracker_scoping())
