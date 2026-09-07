"""
Session Management Service.
Controls class sessions for attendance tracking.
Only one session can be active at a time.
"""

import uuid
import json
from datetime import datetime
from typing import Optional
from backend.core.redis_client import RedisManager


class Session:
    """Represents a single class session."""

    def __init__(self, subject_name: str):
        self.session_id: str = str(uuid.uuid4())
        self.subject_name: str = subject_name
        self.start_time: str = datetime.now().isoformat()
        self.end_time: Optional[str] = None
        self.is_active: bool = True
        self.attendance_count: int = 0

    def end(self):
        """Mark this session as ended."""
        self.end_time = datetime.now().isoformat()
        self.is_active = False

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "subject_name": self.subject_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_active": self.is_active,
            "attendance_count": self.attendance_count,
        }


class SessionManager:
    """
    Manages class sessions per institution.
    Only one session active at a time per institution.
    """

    def __init__(self):
        # Maps institution_id -> active Session
        self._active_sessions: dict[str, Session] = {}
        # Maps institution_id -> list of historical Sessions
        self._session_histories: dict[str, list[Session]] = {}

    async def _sync_redis(self, institution_id: str, session: Optional[Session]):
        """Persists lightweight distributed session tracking state."""
        redis = RedisManager.get_client()
        if not redis:
            return
        key = f"session:active:{institution_id}"
        if session:
            try:
                await redis.set(key, json.dumps(session.to_dict()), ex=86400) # 24h expire
            except Exception:
                pass
        else:
            try:
                await redis.delete(key)
            except Exception:
                pass

    async def start_session(self, institution_id: str, subject_name: str) -> Session:
        """Start a new class session for an institution."""
        active = await self.get_active_session(institution_id)
        if active:
            await self.end_session(institution_id)

        session = Session(subject_name=subject_name)
        self._active_sessions[institution_id] = session
        await self._sync_redis(institution_id, session)
        print(f"📗 Session started [{institution_id}]: {subject_name} [{session.session_id[:8]}]")
        return session

    async def end_session(self, institution_id: str) -> Optional[Session]:
        """End the currently active session for an institution."""
        active = await self.get_active_session(institution_id)
        if active:
            active.end()
            if institution_id not in self._session_histories:
                self._session_histories[institution_id] = []
            self._session_histories[institution_id].append(active)
            print(
                f"📕 Session ended [{institution_id}]: {active.subject_name} "
                f"[{active.session_id[:8]}] — "
                f"{active.attendance_count} marked"
            )
            del self._active_sessions[institution_id]
            await self._sync_redis(institution_id, None)
            return active
        return None

    async def get_active_session(self, institution_id: str) -> Optional[Session]:
        """Get the currently active session for an institution."""
        active = self._active_sessions.get(institution_id)
        if active and active.is_active:
            return active
            
        # Distributed Fetch across horizontally scaled nodes
        redis = RedisManager.get_client()
        if redis:
            try:
                data = await redis.get(f"session:active:{institution_id}")
                if data:
                    s_data = json.loads(data)
                    s = Session(subject_name=s_data.get("subject_name", ""))
                    s.session_id = s_data.get("session_id")
                    s.start_time = s_data.get("start_time")
                    s.end_time = s_data.get("end_time")
                    s.is_active = s_data.get("is_active", True)
                    s.attendance_count = s_data.get("attendance_count", 0)
                    self._active_sessions[institution_id] = s
                    return s
            except Exception:
                pass
        return None

    async def increment_attendance(self, institution_id: str):
        """Increment the attendance count for the active session of an institution."""
        active = await self.get_active_session(institution_id)
        if active:
            active.attendance_count += 1
            await self._sync_redis(institution_id, active)

    async def get_session_history(self, institution_id: str) -> list[dict]:
        """Get all past sessions for an institution as a list of dicts."""
        history = [s.to_dict() for s in self._session_histories.get(institution_id, [])]
        active = await self.get_active_session(institution_id)
        if active:
            history.append(active.to_dict())
        return history


# ── Module-level singleton ──
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global SessionManager singleton."""
    return _session_manager
