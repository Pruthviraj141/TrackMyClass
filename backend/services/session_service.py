"""
Session Management Service.
Controls class sessions for attendance tracking.
Only one session can be active at a time.
"""

import uuid
from datetime import datetime
from typing import Optional


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
    Manages class sessions.
    Only one session active at a time.
    Attendance is only allowed during an active session.
    """

    def __init__(self):
        self._active_session: Optional[Session] = None
        self._session_history: list[Session] = []

    def start_session(self, subject_name: str) -> Session:
        """
        Start a new class session.
        Automatically ends the previous session if one is still active.

        Args:
            subject_name: Name of the class/subject (e.g. "Java", "NLP")

        Returns:
            The newly created Session object.
        """
        # End any currently active session first
        if self._active_session and self._active_session.is_active:
            self.end_session()

        session = Session(subject_name=subject_name)
        self._active_session = session
        print(f"📗 Session started: {subject_name} [{session.session_id[:8]}]")
        return session

    def end_session(self) -> Optional[Session]:
        """
        End the currently active session.

        Returns:
            The ended Session object, or None if no session was active.
        """
        if self._active_session and self._active_session.is_active:
            self._active_session.end()
            self._session_history.append(self._active_session)
            print(
                f"📕 Session ended: {self._active_session.subject_name} "
                f"[{self._active_session.session_id[:8]}] — "
                f"{self._active_session.attendance_count} marked"
            )
            ended = self._active_session
            self._active_session = None
            return ended
        return None

    def get_active_session(self) -> Optional[Session]:
        """Get the currently active session, or None."""
        if self._active_session and self._active_session.is_active:
            return self._active_session
        return None

    def increment_attendance(self):
        """Increment the attendance count for the active session."""
        if self._active_session and self._active_session.is_active:
            self._active_session.attendance_count += 1

    def get_session_history(self) -> list[dict]:
        """Get all past sessions as a list of dicts."""
        history = [s.to_dict() for s in self._session_history]
        if self._active_session:
            history.append(self._active_session.to_dict())
        return history


# ── Module-level singleton ──
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global SessionManager singleton."""
    return _session_manager
