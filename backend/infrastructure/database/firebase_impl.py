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


def create_institution(code: str, name: str, inst_type: str = "", email: str = "") -> dict:
    """Create a new institution entry in Firestore."""
    db = _get_db()
    doc_ref = db.collection("institutions").document(code)
    if doc_ref.get().exists:
        raise ValueError("Institution code already exists.")
    data = {"code": code, "name": name, "type": inst_type, "email": email, "active": 1, "created_at": datetime.now().isoformat()}
    doc_ref.set(data)
    return data



# ──────────────────────────────────────────────
# Student Operations
# ──────────────────────────────────────────────

def add_student(institution_id: str, student_id: str, name: str, roll_number: str, gender: str, embedding: list, password: str = "") -> dict:
    """
    Add a new student with their face embedding, scoped to an institution.
    """
    db = _get_db()
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
    db.collection("students").document(student_id).set(student_data)
    return student_data


def get_all_students(institution_id: str) -> list:
    """
    Retrieve all registered students for an institution.
    
    Returns:
        List of student dicts (each contains student_id, name, roll_number,
        gender, embedding, created_at)
    """
    db = _get_db()
    docs = db.collection("students").where(filter=firestore.FieldFilter("institution_id", "==", institution_id)).stream()
    students = []
    for doc in docs:
        data = doc.to_dict()
        students.append(data)
    return students


def get_student_directory(institution_id: str) -> list:
    """Aggregate global attendance natively safely scaling dynamically natively securely smoothly exactly."""
    db = _get_db()
    
    students_docs = db.collection("students").where(filter=firestore.FieldFilter("institution_id", "==", institution_id)).stream()
    students = []
    for doc in students_docs:
        d = doc.to_dict()
        students.append({
            "student_id": d["student_id"],
            "name": d["name"],
            "roll_number": d.get("roll_number", "N/A"),
            "created_at": d.get("created_at")
        })
    
    attendance_docs = db.collection("attendance").where(filter=firestore.FieldFilter("institution_id", "==", institution_id)).stream()
    session_set = set()
    student_sessions = {}
    
    for doc in attendance_docs:
        req = doc.to_dict()
        sid = req.get("session_id")
        stid = req.get("student_id")
        if not sid or not stid:
            continue
        session_set.add(sid)
        if stid not in student_sessions:
            student_sessions[stid] = set()
        student_sessions[stid].add(sid)
        
    total_sessions = len(session_set)
    
    directory = []
    for s in students:
        attended = len(student_sessions.get(s["student_id"], set()))
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
    db = _get_db()
    doc = db.collection("students").document(student_id).get()
    if doc.exists:
        data = doc.to_dict()
        if data.get("institution_id") == institution_id:
            return data
    return None


def delete_attendance_by_date(institution_id: str, student_id: str, date: str) -> bool:
    """Delete attendance record for a student on a specific date (Manual override to absent)."""
    db = _get_db()
    if not db:
        return False
        
    docs = db.collection("attendance")\
        .where("institution_id", "==", institution_id)\
        .where("student_id", "==", student_id)\
        .where("date", "==", date)\
        .stream()
        
    deleted = False
    for doc in docs:
        db.collection("attendance").document(doc.id).delete()
        deleted = True
        
    return deleted


def get_student_by_roll_number(institution_id: str, roll_number: str) -> Optional[dict]:
    """Get a student by their roll number (for login)."""
    db = _get_db()
    docs = (
        db.collection("students")
        .where(filter=firestore.FieldFilter("institution_id", "==", institution_id))
        .where(filter=firestore.FieldFilter("roll_number", "==", roll_number))
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None


def delete_student(institution_id: str, student_id: str) -> bool:
    """Delete a student and all their attendance records."""
    db = _get_db()
    
    # Verify student belongs to institution
    doc = db.collection("students").document(student_id).get()
    if not doc.exists or doc.to_dict().get("institution_id") != institution_id:
        return False

    # 1. Delete all attendance records for this student
    attendance_refs = db.collection("attendance").where(filter=firestore.FieldFilter("student_id", "==", student_id)).stream()
    for att_doc in attendance_refs:
        att_doc.reference.delete()
        
    # 2. Delete student record
    db.collection("students").document(student_id).delete()
    return True


def update_student_embedding(institution_id: str, student_id: str, embedding: list) -> bool:
    """Update only the face embedding of an existing student."""
    db = _get_db()
    doc_ref = db.collection("students").document(student_id)
    doc = doc_ref.get()
    
    if not doc.exists or doc.to_dict().get("institution_id") != institution_id:
        return False
        
    doc_ref.update({"embedding": embedding})
    return True


# ──────────────────────────────────────────────
# Attendance Operations
# ──────────────────────────────────────────────

def add_attendance(institution_id: str, student_id: str, name: str, session_id: str, subject_name: str, date: str, time: str, timestamp: str, confidence: float) -> dict:
    """
    Record an attendance entry.
    """
    db = _get_db()
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
    db.collection("attendance").add(attendance_data)
    return attendance_data



def get_attendance_by_date(institution_id: str, date: str) -> list:
    """
    Get all attendance records for a specific date and institution.
    """
    db = _get_db()
    docs = (
        db.collection("attendance")
        .where(filter=firestore.FieldFilter("institution_id", "==", institution_id))
        .where(filter=firestore.FieldFilter("date", "==", date))
        .stream()
    )
    records = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        records.append(data)
    return records


def get_student_attendance_stats(institution_id: str, student_id: str) -> dict:
    """Calculate mathematically accurate attendance stats derived from domain records."""
    db = _get_db()
    docs_stream = db.collection("attendance") \
             .where(filter=firestore.FieldFilter("institution_id", "==", institution_id)) \
             .stream()
    docs = list(docs_stream)
             
    institution_session_map = {} # subject_name -> set(session_id)
    student_session_map = {}     # subject_name -> set(session_id)
    
    for doc in docs:
        data = doc.to_dict()
        subject = data.get("subject_name", "General Session")
        sid = data.get("session_id")
        std_id = data.get("student_id")
        
        if not sid:
            continue
            
        if subject not in institution_session_map:
            institution_session_map[subject] = set()
        institution_session_map[subject].add(sid)
        
        if std_id == student_id:
            if subject not in student_session_map:
                student_session_map[subject] = set()
            student_session_map[subject].add(sid)
            
    subject_stats = []
    total_eligible = 0
    total_present = 0
    
    calendar_map = {}
    
    for subject, present_sessions in student_session_map.items():
        present = len(present_sessions)
        
        # map calendar eligible dates
        # iterate all institutional documents where subject_name matches
        for d in docs:
            dt = d.to_dict()
            if dt.get("subject_name", "General Session") == subject:
                calendar_map[dt.get("date")] = "Absent"
        
        total = len(institution_session_map.get(subject, set()))
        
        total = max(total, present)
        
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
        
    for d in docs:
        dt = d.to_dict()
        if dt.get("student_id") == student_id:
            calendar_map[dt.get("date")] = "Present"
            
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


def get_attendance_by_session_id(institution_id: str, session_id: str) -> list:
    """
    Get all attendance records for a specific session.
    """
    db = _get_db()
    docs = (
        db.collection("attendance")
        .where(filter=firestore.FieldFilter("institution_id", "==", institution_id))
        .where(filter=firestore.FieldFilter("session_id", "==", session_id))
        .stream()
    )
    records = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        records.append(data)
    return records


def is_already_marked(institution_id: str, student_id: str, date: str) -> bool:
    """
    Check if attendance is already marked for a student on a given date.
    Prevents duplicate marking.
    """
    db = _get_db()
    docs = (
        db.collection("attendance")
        .where(filter=firestore.FieldFilter("institution_id", "==", institution_id))
        .where(filter=firestore.FieldFilter("student_id", "==", student_id))
        .where(filter=firestore.FieldFilter("date", "==", date))
        .limit(1)
        .stream()
    )
    return any(True for _ in docs)
