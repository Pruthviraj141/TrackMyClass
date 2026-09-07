# Temporal Tracker Verification

## State Machine Definition

The `TemporalTracker` processes inputs frame by frame and maintains state for observed identities.

States:
- **Tracking**: A candidate identity is present. (Frame count < `TEMPORAL_MIN_FRAMES` or average confidence < `TEMPORAL_MIN_CONFIDENCE`).
- **Mark**: A candidate identity has reached the stability thresholds and is formally marked for attendance.
- **Cooldown**: An identity that was previously marked exists in the frame but is ignored because `SESSION_COOLDOWN_MINUTES` has not elapsed.
- **Already Marked**: An identity that was previously marked exists in the frame after cooldown elapsed.
- **Unknown**: A detected face yielded a `MatchResult` of `None`.

## Identity Switch Protection

When evaluating an identity switch (e.g., Person A is in bounding box X, but then Person B appears in bounding box X nearby):
- The `TemporalTracker` buffers state strictly using `student_id` (candidate identity) mapped to a `TrackedFace` instance.
- If match results drop Person A and report Person B, the `TrackedFace` state for Person A increments `consecutive_misses`.
- Simultaneously, a new `TrackedFace` instance begins for Person B with `frame_count = 1`.
- Person A's state does NOT carry over to Person B. Person B must independently satisfy `TEMPORAL_MIN_FRAMES` to reach the **Mark** state.

## Edge Cases

1. **Face Disappearance**: If a face is not detected for `TEMPORAL_TOLERANCE_MISSES` frames, and `TEMPORAL_CLEANUP_SECONDS` has elapsed, the `TrackedFace` object is deleted from memory.
2. **Session Reset**: Invoking `reset()` flushes the internal buffers (`_buffer` and `_session_marked`), ensuring no state bleeds between distinct class sessions.
3. **Multiple Simultaneous Faces**: The `.update()` method iterates over a list of matches. `TrackedFace` logic is processed per unique candidate identity, allowing concurrent stabilization without interference.
