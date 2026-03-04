"""
Firebase Firestore database service.
Handles all CRUD operations for students and attendance records.
"""

from datetime import datetime
from typing import Optional

from firebase_admin import firestore


def _get_db():
    """Get Firestore client instance."""
    return firestore.client()


# ──────────────────────────────────────────────
# Student Operations
# ──────────────────────────────────────────────

def add_student(student_id: str, name: str, roll_number: str, gender: str, embedding: list, password: str = "") -> dict:
    """
    Add a new student with their face embedding.
    """
    db = _get_db()
    student_data = {
        "student_id": student_id,
        "name": name,
        "roll_number": roll_number,
        "gender": gender,
        "embedding": embedding,
        "password": password,
        "created_at": datetime.now().isoformat(),
    }
    db.collection("students").document(student_id).set(student_data)
    return student_data


def get_all_students() -> list:
    """
    Retrieve all registered students.
    
    Returns:
        List of student dicts (each contains student_id, name, roll_number,
        gender, embedding, created_at)
    """
    db = _get_db()
    docs = db.collection("students").stream()
    students = []
    for doc in docs:
        data = doc.to_dict()
        students.append(data)
    return students


def get_student_by_id(student_id: str) -> Optional[dict]:
    """Get a single student by their ID."""
    db = _get_db()
    doc = db.collection("students").document(student_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


def get_student_by_roll_number(roll_number: str) -> Optional[dict]:
    """Get a student by their roll number (for login)."""
    db = _get_db()
    docs = db.collection("students").where("roll_number", "==", roll_number).limit(1).stream()
    for doc in docs:
        return doc.to_dict()
    return None


def delete_student(student_id: str) -> bool:
    """Delete a student and all their attendance records."""
    db = _get_db()
    
    # 1. Delete all attendance records for this student
    attendance_refs = db.collection("attendance").where("student_id", "==", student_id).stream()
    for doc in attendance_refs:
        doc.reference.delete()
        
    # 2. Delete student record
    doc_ref = db.collection("students").document(student_id)
    if doc_ref.get().exists:
        doc_ref.delete()
        return True
    return False


# ──────────────────────────────────────────────
# Attendance Operations
# ──────────────────────────────────────────────

def add_attendance(student_id: str, name: str, session_id: str, subject_name: str, date: str, time: str, timestamp: str, confidence: float) -> dict:
    """
    Record an attendance entry.
    
    Args:
        student_id: FK to students collection
        name: Student name (denormalized for quick display)
        session_id: The active session ID
        subject_name: The active subject
        date: Date string (YYYY-MM-DD)
        time: Time string (HH:MM:SS)
        timestamp: ISO format timestamp
        confidence: Cosine similarity score
    
    Returns:
        dict with the stored attendance data
    """
    db = _get_db()
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
    db.collection("attendance").add(attendance_data)
    return attendance_data



def get_attendance_by_date(date: str) -> list:
    """
    Get all attendance records for a specific date.
    
    Args:
        date: Date string (YYYY-MM-DD)
    
    Returns:
        List of attendance dicts
    """
    db = _get_db()
    docs = db.collection("attendance").where("date", "==", date).stream()
    records = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        records.append(data)
    return records


def get_attendance_by_session_id(session_id: str) -> list:
    """
    Get all attendance records for a specific session.
    """
    db = _get_db()
    docs = db.collection("attendance").where("session_id", "==", session_id).stream()
    records = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        records.append(data)
    return records


def is_already_marked(student_id: str, date: str) -> bool:
    """
    Check if attendance is already marked for a student on a given date.
    Prevents duplicate marking.
    
    Args:
        student_id: Student identifier
        date: Date string (YYYY-MM-DD)
    
    Returns:
        True if already marked, False otherwise
    """
    db = _get_db()
    docs = (
        db.collection("attendance")
        .where("student_id", "==", student_id)
        .where("date", "==", date)
        .limit(1)
        .stream()
    )
    return any(True for _ in docs)
