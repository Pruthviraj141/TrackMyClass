"""
Authentication Service.
Handles admin and student authentication.
Sessions are persisted in Firebase/SQLite to survive server restarts.
"""

import hashlib
from datetime import datetime
from fastapi import Request

from backend.config import DATABASE_MODE, ADMIN_USERNAME, ADMIN_PASSWORD


# ──────────────────────────────────────────────
# Password hashing
# ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password with SHA-256 for storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Compare a plain text password against its hash."""
    return hash_password(plain) == hashed


# ──────────────────────────────────────────────
# Admin Authentication
# ──────────────────────────────────────────────

def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin username/password from .env config."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


# Keep backward-compatible alias
verify_credentials = verify_admin_credentials


# ──────────────────────────────────────────────
# Student Authentication
# ──────────────────────────────────────────────

def verify_student_credentials(roll_number: str, password: str) -> dict | None:
    """
    Look up a student by roll_number and verify password.
    Returns student dict on success, None on failure.
    """
    if DATABASE_MODE == "firebase":
        from backend.database.firebase_service import get_student_by_roll_number
    else:
        from backend.database.sqlite_service import get_student_by_roll_number

    student = get_student_by_roll_number(roll_number)
    if not student:
        return None

    stored_pw = student.get("password", "")
    if not stored_pw:
        return None

    if verify_password(password, stored_pw):
        return student
    return None


# ──────────────────────────────────────────────
# Persistent Session Management (Firebase/SQLite)
# ──────────────────────────────────────────────

def _get_sessions_collection():
    """Get the sessions collection/table handle."""
    if DATABASE_MODE == "firebase":
        from firebase_admin import firestore
        db = firestore.client()
        return db.collection("auth_sessions")
    return None


def _get_sqlite_connection():
    """Get SQLite connection and ensure sessions table exists."""
    import sqlite3
    from backend.config import SQLITE_DB_PATH
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS auth_sessions (
            session_id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            user_id TEXT NOT NULL DEFAULT '',
            name TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def create_auth_session(session_id: str, role: str = "admin", user_id: str = "", name: str = ""):
    """Persist session to database so it survives server restarts."""
    session_data = {
        "session_id": session_id,
        "role": role,
        "user_id": user_id,
        "name": name,
        "created_at": datetime.now().isoformat(),
    }

    if DATABASE_MODE == "firebase":
        col = _get_sessions_collection()
        col.document(session_id).set(session_data)
    else:
        conn = _get_sqlite_connection()
        conn.execute(
            "INSERT OR REPLACE INTO auth_sessions (session_id, role, user_id, name, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, user_id, name, session_data["created_at"]),
        )
        conn.commit()
        conn.close()


def destroy_auth_session(session_id: str):
    """Remove session from database."""
    if DATABASE_MODE == "firebase":
        col = _get_sessions_collection()
        col.document(session_id).delete()
    else:
        conn = _get_sqlite_connection()
        conn.execute("DELETE FROM auth_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()


def _lookup_session(session_id: str) -> dict | None:
    """Look up a session from the database."""
    if not session_id:
        return None

    if DATABASE_MODE == "firebase":
        col = _get_sessions_collection()
        doc = col.document(session_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    else:
        conn = _get_sqlite_connection()
        cursor = conn.execute("SELECT * FROM auth_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None


def get_current_user(request: Request) -> str | None:
    """Extract session cookie and verify. Returns 'admin' if admin logged in."""
    session_id = request.cookies.get("session_id")
    session = _lookup_session(session_id)
    if session and session.get("role") == "admin":
        return "admin"
    return None


def get_current_student(request: Request) -> dict | None:
    """Extract session cookie and return student info dict if student is logged in."""
    session_id = request.cookies.get("session_id")
    session = _lookup_session(session_id)
    if session and session.get("role") == "student":
        return session
    return None


def get_session_info(request: Request) -> dict | None:
    """Get full session info regardless of role."""
    session_id = request.cookies.get("session_id")
    return _lookup_session(session_id)
