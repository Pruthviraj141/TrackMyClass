"""
SQLite fallback database service.
Identical interface to firebase_service.py for seamless switching.
Auto-creates tables on first use.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config import SQLITE_DB_PATH


def _get_connection() -> sqlite3.Connection:
    """Get SQLite connection with auto-create tables."""
    # Ensure directory exists
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection):
    """Create tables if they don't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            gender TEXT NOT NULL,
            embedding TEXT NOT NULL,
            password TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            session_id TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            confidence REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_date 
        ON attendance(date)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_session 
        ON attendance(session_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_student_session 
        ON attendance(student_id, session_id)
    """)
    
    # Migration: add password column if missing (for existing DBs)
    try:
        conn.execute("ALTER TABLE students ADD COLUMN password TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()


# ──────────────────────────────────────────────
# Student Operations
# ──────────────────────────────────────────────

def add_student(student_id: str, name: str, roll_number: str, gender: str, embedding: list, password: str = "") -> dict:
    """
    Add a new student with their face embedding.
    Embedding is stored as JSON string in SQLite.
    """
    conn = _get_connection()
    student_data = {
        "student_id": student_id,
        "name": name,
        "roll_number": roll_number,
        "gender": gender,
        "embedding": embedding,
        "password": password,
        "created_at": datetime.now().isoformat(),
    }
    conn.execute(
        "INSERT OR REPLACE INTO students (student_id, name, roll_number, gender, embedding, password, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (student_id, name, roll_number, gender, json.dumps(embedding), password, student_data["created_at"]),
    )
    conn.commit()
    conn.close()
    return student_data


def get_all_students() -> list:
    """Retrieve all registered students."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM students")
    students = []
    for row in cursor:
        data = dict(row)
        data["embedding"] = json.loads(data["embedding"])
        students.append(data)
    conn.close()
    return students


def get_student_by_id(student_id: str) -> Optional[dict]:
    """Get a single student by their ID."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["embedding"] = json.loads(data["embedding"])
        return data
    return None


def get_student_by_roll_number(roll_number: str) -> Optional[dict]:
    """Get a student by their roll number (for login)."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM students WHERE roll_number = ?", (roll_number,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["embedding"] = json.loads(data["embedding"])
        return data
    return None


def delete_student(student_id: str) -> bool:
    """Delete a student and all their attendance records."""
    conn = _get_connection()
    # Delete attendance records first
    conn.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    # Delete student record
    cursor = conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ──────────────────────────────────────────────
# Attendance Operations
# ──────────────────────────────────────────────

def add_attendance(student_id: str, name: str, session_id: str, subject_name: str, date: str, time: str, timestamp: str, confidence: float) -> dict:
    """Record an attendance entry."""
    conn = _get_connection()
    # Check if table has new columns. Since SQLite doesn't support IF EXISTS easily for columns, 
    # if it throws an error on insert because of old schema, we could recreate it, but assuming new DB for phase-1.
    attendance_data = {
        "student_id": student_id,
        "name": name,
        "session_id": session_id,
        "subject_name": subject_name,
        "date": date,
        "time": time,
        "timestamp": timestamp,
        "confidence": round(confidence, 4),
    }
    conn.execute(
        "INSERT INTO attendance (student_id, name, session_id, subject_name, date, time, timestamp, confidence) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (student_id, name, session_id, subject_name, date, time, timestamp, round(confidence, 4)),
    )
    conn.commit()
    conn.close()
    return attendance_data


def get_attendance_by_date(date: str) -> list:
    """Get all attendance records for a specific date."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM attendance WHERE date = ?", (date,))
    records = [dict(row) for row in cursor]
    conn.close()
    return records


def get_attendance_by_session_id(session_id: str) -> list:
    """Get all attendance records for a specific session."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM attendance WHERE session_id = ?", (session_id,))
    records = [dict(row) for row in cursor]
    conn.close()
    return records


def is_already_marked(student_id: str, date: str) -> bool:
    """Check if attendance is already marked for a student on a given date."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM attendance WHERE student_id = ? AND date = ? LIMIT 1",
        (student_id, date),
    )
    result = cursor.fetchone() is not None
    conn.close()
    return result
