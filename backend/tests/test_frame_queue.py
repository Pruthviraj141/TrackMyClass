"""
Tests for FrameQueue — bounded queue with latest-frame-wins policy.
"""
import time
import threading
import pytest

from backend.worker.frame_queue import FrameQueue, QueuedFrame


def _make_frame(n: int = 0) -> QueuedFrame:
    return QueuedFrame(
        institution_id="TEST",
        session_id="sess-1",
        frame_bytes=b"fake-jpeg-" + str(n).encode(),
    )


class TestFrameQueueBasic:
    def test_put_and_get(self):
        q = FrameQueue()
        f = _make_frame(1)
        q.put(f)
        result = q.get(timeout=0.1)
        assert result is f

    def test_get_returns_none_on_timeout(self):
        q = FrameQueue()
        result = q.get(timeout=0.05)
        assert result is None

    def test_queue_is_empty_after_get(self):
        q = FrameQueue()
        q.put(_make_frame(1))
        q.get(timeout=0.1)
        # Second get should time out
        result = q.get(timeout=0.05)
        assert result is None


class TestLatestFrameWins:
    def test_stale_frame_evicted(self):
        q = FrameQueue()
        old_frame = _make_frame(1)
        new_frame = _make_frame(2)
        q.put(old_frame)   # slot occupied
        dropped = q.put(new_frame)  # old_frame evicted
        assert dropped is True
        result = q.get(timeout=0.1)
        assert result is new_frame

    def test_multiple_overwrites_stats(self):
        q = FrameQueue()
        for i in range(10):
            q.put(_make_frame(i))
        # Only the last frame survives
        result = q.get(timeout=0.1)
        assert result is not None
        assert result.frame_bytes == b"fake-jpeg-9"
        stats = q.stats
        assert stats["total_dropped"] == 9
        assert stats["total_enqueued"] == 10
        assert stats["pending"] == 0


class TestBackpressure:
    def test_bounded_memory_under_load(self):
        """Putting 1000 frames should never grow queue beyond 1 item."""
        q = FrameQueue()
        for i in range(1000):
            q.put(_make_frame(i))
        stats = q.stats
        assert stats["pending"] <= 1
        assert stats["total_dropped"] == 999

    def test_producer_consumer_concurrency(self):
        """Concurrent producer and consumer should not deadlock or corrupt state."""
        q = FrameQueue()
        received = []

        def producer():
            for i in range(50):
                q.put(_make_frame(i))
                time.sleep(0.001)

        def consumer():
            for _ in range(50):
                f = q.get(timeout=0.5)
                if f:
                    received.append(f)
                time.sleep(0.002)

        t1 = threading.Thread(target=producer)
        t2 = threading.Thread(target=consumer)
        t1.start(); t2.start()
        t1.join(); t2.join()

        # At least some frames should have been received
        assert len(received) > 0
        # All received frames must be valid
        for f in received:
            assert f.institution_id == "TEST"
