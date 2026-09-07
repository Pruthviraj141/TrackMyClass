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

from backend.core.config import SQLITE_DB_PATH


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
            institution_id TEXT NOT NULL,
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
            institution_id TEXT NOT NULL,
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
    # Migrations
    try:
        conn.execute("ALTER TABLE students ADD COLUMN password TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        conn.execute("ALTER TABLE students ADD COLUMN institution_id TEXT NOT NULL DEFAULT 'DEMO2026'")
    except sqlite3.OperationalError:
        pass
        
    try:
        conn.execute("ALTER TABLE attendance ADD COLUMN institution_id TEXT NOT NULL DEFAULT 'DEMO2026'")
    except sqlite3.OperationalError:
        pass

    # Create indices after migrations
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
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_institution 
        ON attendance(institution_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_students_institution 
        ON students(institution_id)
    """)
    # Fix 5: Unique constraint to prevent duplicate attendance at the DB level
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique 
        ON attendance(student_id, session_id)
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS institutions (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)
    
    # Insert demo institution if none exist
    cursor = conn.execute("SELECT COUNT(*) FROM institutions")
    if cursor.fetchone()[0] == 0:
        conn.execute("INSERT INTO institutions (code, name, active) VALUES (?, ?, ?)", ("DEMO2026", "Demo College", 1))
    
    conn.commit()


# ──────────────────────────────────────────────
# Institution Operations
# ──────────────────────────────────────────────

def verify_college_code(code: str) -> Optional[dict]:
    """Verify if a college code is valid and active."""
    conn = _get_connection()
    cursor = conn.execute("SELECT code, name, active FROM institutions WHERE code = ? AND active = 1", (code,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def create_institution(code: str, name: str, inst_type: str = "", email: str = "") -> dict:
    """Create a new institution entry in SQLite."""
    conn = _get_connection()
    cursor = conn.execute("SELECT code FROM institutions WHERE code = ?", (code,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Institution code already exists.")
        
    conn.execute(
        "INSERT INTO institutions (code, name, active) VALUES (?, ?, 1)",
        (code, name)
    )
    conn.commit()
    conn.close()
    return {"code": code, "name": name, "type": inst_type, "email": email}


# ──────────────────────────────────────────────
# Student Operations
# ──────────────────────────────────────────────

def add_student(institution_id: str, student_id: str, name: str, roll_number: str, gender: str, embedding: list, password: str = "") -> dict:
    """
    Add a new student with their face embedding, scoped to an institution.
    """
    conn = _get_connection()
    student_data = {
        "institution_id": institution_id,
        "student_id": student_id,
        "name": name,
        "roll_number": roll_number,
        "gender": gender,
        "embedding": embedding,
        "password": password,
        "created_at": datetime.now().isoformat(),
    }
    conn.execute(
        "INSERT OR REPLACE INTO students (institution_id, student_id, name, roll_number, gender, embedding, password, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (institution_id, student_id, name, roll_number, gender, json.dumps(embedding), password, student_data["created_at"]),
    )
    conn.commit()
    conn.close()
    return student_data


def get_all_students(institution_id: str) -> list:
    """Retrieve all registered students for an institution."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM students WHERE institution_id = ?", (institution_id,))
    students = []
    for row in cursor:
        data = dict(row)
        data["embedding"] = json.loads(data["embedding"])
        students.append(data)
    conn.close()
    return students


def get_student_directory(institution_id: str) -> list:
    """Retrieve all students and calculate their aggregate attendance."""
    conn = _get_connection()
    
    cursor = conn.execute("SELECT student_id, name, roll_number, created_at FROM students WHERE institution_id = ?", (institution_id,))
    students = [dict(row) for row in cursor]
    
    cursor = conn.execute("SELECT COUNT(DISTINCT session_id) FROM attendance WHERE institution_id = ?", (institution_id,))
    total_sessions = cursor.fetchone()[0] or 0
    
    cursor = conn.execute("SELECT student_id, COUNT(DISTINCT session_id) as attended_count FROM attendance WHERE institution_id = ? GROUP BY student_id", (institution_id,))
    attendance_map = {row["student_id"]: row["attended_count"] for row in cursor}
    
    conn.close()
    
    directory = []
    for s in students:
        attended = attendance_map.get(s["student_id"], 0)
        attendance_pct = round((attended / total_sessions * 100), 1) if total_sessions > 0 else 0.0
        
        status = "Inactive" if (total_sessions > 0 and attended == 0) else "Active"
        
        class_name = "C1" if int(s["roll_number"][-1] if s["roll_number"][-1].isdigit() else "0") % 2 == 0 else "C2"
        
        directory.append({
            "student_id": s["student_id"],
            "name": s["name"],
            "roll_number": s["roll_number"],
            "class_name": class_name,
            "attendance_pct": attendance_pct,
            "status": status,
            "created_at": s["created_at"]
        })
        
    return directory



def get_student_by_id(institution_id: str, student_id: str) -> Optional[dict]:
    """Get a single student by their ID and institution."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM students WHERE institution_id = ? AND student_id = ?", (institution_id, student_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["embedding"] = json.loads(data["embedding"])
        return data
    return None


def get_student_by_roll_number(institution_id: str, roll_number: str) -> Optional[dict]:
    """Get a student by their roll number (for login)."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM students WHERE institution_id = ? AND roll_number = ?", (institution_id, roll_number))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["embedding"] = json.loads(data["embedding"])
        return data
    return None


def delete_student(institution_id: str, student_id: str) -> bool:
    """Delete a student and all their attendance records."""
    conn = _get_connection()
    conn.execute("DELETE FROM attendance WHERE institution_id = ? AND student_id = ?", (institution_id, student_id))
    cursor = conn.execute("DELETE FROM students WHERE institution_id = ? AND student_id = ?", (institution_id, student_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def update_student_embedding(institution_id: str, student_id: str, embedding: list) -> bool:
    """Update only the face embedding of an existing student."""
    conn = _get_connection()
    cursor = conn.execute(
        "UPDATE students SET embedding = ? WHERE institution_id = ? AND student_id = ?",
        (json.dumps(embedding), institution_id, student_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

# ──────────────────────────────────────────────
# Attendance Operations
# ──────────────────────────────────────────────

def add_attendance(institution_id: str, student_id: str, name: str, session_id: str, subject_name: str, date: str, time: str, timestamp: str, confidence: float) -> dict:
    """Record an attendance entry. Uses INSERT OR IGNORE to respect the UNIQUE(student_id, session_id) constraint."""
    conn = _get_connection()
    attendance_data = {
        "institution_id": institution_id,
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
        "INSERT OR IGNORE INTO attendance (institution_id, student_id, name, session_id, subject_name, date, time, timestamp, confidence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (institution_id, student_id, name, session_id, subject_name, date, time, timestamp, round(confidence, 4)),
    )
    conn.commit()
    conn.close()
    return attendance_data


def get_attendance_by_date(institution_id: str, date: str) -> list:
    """Get all attendance records for a specific date and institution."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM attendance WHERE institution_id = ? AND date = ?", (institution_id, date))
    records = [dict(row) for row in cursor]
    conn.close()
    return records


def get_attendance_by_session_id(institution_id: str, session_id: str) -> list:
    """Get all attendance records for a specific session."""
    conn = _get_connection()
    cursor = conn.execute("SELECT * FROM attendance WHERE institution_id = ? AND session_id = ?", (institution_id, session_id))
    records = [dict(row) for row in cursor]
    conn.close()
    return records


def get_attendance_by_student(institution_id: str, student_id: str) -> list:
    """Get all attendance records for a specific student within their institution."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT * FROM attendance WHERE institution_id = ? AND student_id = ?",
        (institution_id, student_id),
    )
    records = [dict(row) for row in cursor]
    conn.close()
    return records


def get_student_attendance_stats(institution_id: str, student_id: str) -> dict:
    """Calculate mathematically accurate attendance stats derived from domain records."""
    conn = _get_connection()
    
    c_total = conn.execute("SELECT subject_name, COUNT(DISTINCT session_id) as total FROM attendance WHERE institution_id = ? GROUP BY subject_name", (institution_id,))
    institution_totals = {r["subject_name"]: r["total"] for r in c_total}
    
    c_present = conn.execute("SELECT subject_name, COUNT(DISTINCT session_id) as present FROM attendance WHERE institution_id = ? AND student_id = ? GROUP BY subject_name", (institution_id, student_id))
    student_presents = {r["subject_name"]: r["present"] for r in c_present}
    # Calendar Map derivation
    c_dates = conn.execute("SELECT DISTINCT date FROM attendance WHERE institution_id = ? AND student_id = ?", (institution_id, student_id))
    present_dates = [r["date"] for r in c_dates]
    
    calendar_map = {}
    if student_presents:
        placeholders = ','.join(['?'] * len(student_presents))
        query = f"SELECT DISTINCT date FROM attendance WHERE institution_id = ? AND subject_name IN ({placeholders})"
        c_eligible = conn.execute(query, [institution_id] + list(student_presents.keys()))
        for r in c_eligible:
            calendar_map[r["date"]] = "Absent"
            
    for d in present_dates:
        calendar_map[d] = "Present"
        
    conn.close()

    subject_stats = []
    total_eligible = 0
    total_present = 0

    for subject, present in student_presents.items():
        total = institution_totals.get(subject, present)
        subject_stats.append({
            "subject_name": subject,
            "present": present,
            "absent": total - present,
            "late": 0,
            "total_classes": total,
            "percentage": round((present / total) * 100, 1) if total > 0 else 0.0
        })
        total_eligible += total
        total_present += present

    overall = round((total_present / total_eligible) * 100, 1) if total_eligible > 0 else 0.0
    
    return {
        "subject_stats": subject_stats,
        "overall_stats": {
            "present": total_present,
            "absent": total_eligible - total_present,
            "late": 0,
            "total_classes": total_eligible,
            "percentage": overall,
            "calendar_map": calendar_map
        }
    }


def is_already_marked(institution_id: str, student_id: str, date: str) -> bool:
    """Check if attendance is already marked for a student on a given date."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM attendance WHERE institution_id = ? AND student_id = ? AND date = ? LIMIT 1",
        (institution_id, student_id, date),
    )
    result = cursor.fetchone() is not None
    conn.close()
    return result


def delete_attendance_by_date(institution_id: str, student_id: str, date: str, session_id: str = None) -> bool:
    """Delete attendance record for a student. When session_id is provided, only deletes for that specific session (subject isolation)."""
    conn = _get_connection()
    if session_id:
        cursor = conn.execute(
            "DELETE FROM attendance WHERE institution_id = ? AND student_id = ? AND date = ? AND session_id = ?",
            (institution_id, student_id, date, session_id),
        )
    else:
        cursor = conn.execute(
            "DELETE FROM attendance WHERE institution_id = ? AND student_id = ? AND date = ?",
            (institution_id, student_id, date),
        )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
