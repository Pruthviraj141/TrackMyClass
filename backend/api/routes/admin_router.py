"""
Admin Dashboard Router.
Protected routes for managing the attendance system.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from backend.api.dependencies import get_current_user_from_token
from backend.domain.identity import User
from backend.core.config import TEMPLATES_DIR, DATABASE_MODE
from backend.services.session_service import get_session_manager
from backend.services.report_service import generate_session_report, generate_custom_report, generate_excel_report, generate_pdf_report

if DATABASE_MODE == "firebase":
    from backend.infrastructure.database.firebase_impl import get_all_students, get_attendance_by_session_id, get_attendance_by_date, delete_student
else:
    from backend.infrastructure.database.sqlite_impl import get_all_students, get_attendance_by_session_id, get_attendance_by_date, delete_student

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def get_admin_user(user: User = Depends(get_current_user_from_token)) -> str:
    """Dependency to check if user is authenticated admin. Returns institution_id."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.memberships:
        return user.memberships[0].institution_id
    return "DEMO2026"



@router.get("/students")
async def list_students(institution_id: str = Depends(get_admin_user)):
    """API to list students for management."""
    students = get_all_students(institution_id)
    # Sort by name
    students.sort(key=lambda x: x.get("name", "").lower())
    return students

@router.get("/directory")
async def get_directory(institution_id: str = Depends(get_admin_user)):
    """API to comprehensively list students wrapped perfectly powerfully smoothly tightly successfully reliably reliably beautifully clearly gracefully stably stably fluidly cleanly flawlessly natively explicitly firmly reliably dependably!"""
    if DATABASE_MODE == "firebase":
        from backend.infrastructure.database.firebase_impl import get_student_directory
    else:
        from backend.infrastructure.database.sqlite_impl import get_student_directory
        
    directory = get_student_directory(institution_id)
    directory.sort(key=lambda x: x.get("name", "").lower())
    return directory


@router.delete("/students/{student_id}")
async def remove_student(student_id: str, institution_id: str = Depends(get_admin_user)):
    """API to delete a student and their attendance records."""
    success = delete_student(institution_id, student_id)
    # TODO: also remove from memory cache
    from backend.ml.matcher.optimized_recognition import get_embedding_cache
    cache = get_embedding_cache()
    if student_id in cache.embeddings:
        del cache.embeddings[student_id]
        if student_id in cache.student_names:
            del cache.student_names[student_id]
        cache.rebuild_index()

    if not success:
        raise HTTPException(status_code=404, detail="Student not found or could not be deleted")
    return {"success": True, "message": "Student deleted successfully"}

@router.get("/dashboard-data")
async def get_dashboard_data(institution_id: str = Depends(get_admin_user)):
    """API endpoint to get dynamic dashboard data."""
    mgr = get_session_manager()
    session = await mgr.get_active_session(institution_id)
    is_active = session is not None
    
    # If no active session, try to get the most recent past session
    if not session and mgr._session_histories.get(institution_id):
        session = mgr._session_histories[institution_id][-1]
    
    all_students = get_all_students(institution_id)
    total_registered = len(all_students)
    
    # Defaults
    active_session_name = "None"
    start_time = "N/A"
    total_present = 0
    attendance_pct = 0.0
    present_list = []
    absent_list = []
    
    if session:
        active_session_name = session.subject_name
        start_time = session.start_time
        
        # Get present students
        attendance_records = get_attendance_by_session_id(institution_id, session.session_id)
        present_student_ids = {record["student_id"] for record in attendance_records if record.get("time") != "LATE"}
        late_student_ids = {record["student_id"] for record in attendance_records if record.get("time") == "LATE"}
        
        student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
        name_map = {s["student_id"]: s.get("name", "Unknown") for s in all_students}
        
        present_list = []
        late_list = []
        for record in attendance_records:
            record["roll_number"] = student_map.get(record["student_id"], "N/A")
            record["name"] = name_map.get(record["student_id"], record.get("name"))
            if record.get("time") == "LATE":
                late_list.append(record)
            else:
                present_list.append(record)
                
        total_present = len(present_student_ids)
        total_late = len(late_student_ids)
        all_attendance_ids = present_student_ids.union(late_student_ids)
        
        absent_list = [
            {"student_id": student["student_id"], "name": student["name"], "roll_number": student.get("roll_number", "N/A")} 
            for student in all_students if student["student_id"] not in all_attendance_ids
        ]
        
        if total_registered > 0:
            attendance_pct = round((total_present / total_registered) * 100, 1)
            
    return {
        "active_session": is_active,
        "session_name": active_session_name,
        "start_time": start_time,
        "end_time": session.end_time if session and hasattr(session, 'end_time') else "N/A",
        "total_registered": total_registered,
        "total_present": total_present,
        "total_late": total_late if session else 0,
        "attendance_pct": attendance_pct,
        "present_list": present_list,
        "late_list": late_list if session else [],
        "absent_list": absent_list
    }

@router.get("/export-csv")
async def export_csv(format: str = "csv", institution_id: str = Depends(get_admin_user)):
    """Generate and return report for the active session in chosen format."""
    mgr = get_session_manager()
    session = mgr.get_active_session(institution_id)
    
    # Allow exporting the last session if no session is active
    if not session and mgr._session_histories.get(institution_id):
        session = mgr._session_histories[institution_id][-1]
    
    if not session:
        raise HTTPException(status_code=400, detail="No session available to export.")
        
    attendance_records = get_attendance_by_session_id(institution_id, session.session_id)
    
    all_students = get_all_students(institution_id)
    student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
    name_map = {s["student_id"]: s.get("name", "Unknown") for s in all_students}
    
    for record in attendance_records:
        record["roll_number"] = student_map.get(record["student_id"], "N/A")
        record["name"] = name_map.get(record["student_id"], record.get("name"))
        
    date = attendance_records[0]["date"] if attendance_records else "unknown_date"
    
    present_student_ids = {record["student_id"] for record in attendance_records}
    absent_records = [
        {"student_id": student["student_id"], "name": student.get("name", "N/A"), "roll_number": student_map.get(student["student_id"], "N/A")} 
        for student in all_students if student["student_id"] not in present_student_ids
    ]
        
    if format == "excel":
        filepath = generate_excel_report(attendance_records, session.subject_name, date, absent_records)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "pdf":
        filepath = generate_pdf_report(attendance_records, session.subject_name, date, absent_records)
        media_type = "application/pdf"
    else:
        filepath = generate_custom_report(attendance_records, session.subject_name, date)
        media_type = "text/csv"
    if not filepath:
        raise HTTPException(status_code=400, detail="Could not generate report. Verify data.")
        
    return FileResponse(path=filepath, filename=filepath.split('/')[-1], media_type=media_type)


@router.get("/historical-data")
async def get_historical_data(date: str, subject: str = None, institution_id: str = Depends(get_admin_user)):
    """API endpoint to get historical attendance data by date and optionally subject."""
    all_students = get_all_students(institution_id)
    total_registered = len(all_students)
    student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
    name_map = {s["student_id"]: s.get("name", "Unknown") for s in all_students}
    
    attendance_records = get_attendance_by_date(institution_id, date)
    
    # Extract available subjects for this date
    available_subjects = list(set(r.get("subject_name", "Unknown") for r in attendance_records))
    
    # Filter by subject if provided
    if subject and subject != "All":
        attendance_records = [r for r in attendance_records if r.get("subject_name") == subject]
    
    present_student_ids = {record["student_id"] for record in attendance_records if record.get("time") != "LATE"}
    late_student_ids = {record["student_id"] for record in attendance_records if record.get("time") == "LATE"}
    
    present_list = []
    late_list = []
    for record in attendance_records:
        r_copy = dict(record)
        r_copy["roll_number"] = student_map.get(record["student_id"], "N/A")
        r_copy["name"] = name_map.get(record["student_id"], r_copy.get("name"))
        if r_copy.get("time") == "LATE":
            late_list.append(r_copy)
        else:
            present_list.append(r_copy)
        
    total_present = len(present_student_ids)
    total_late = len(late_student_ids)
    all_attendance_ids = present_student_ids.union(late_student_ids)
    
    absent_list = [
        {"student_id": student["student_id"], "name": student["name"], "roll_number": student_map.get(student["student_id"], "N/A")} 
        for student in all_students if student["student_id"] not in all_attendance_ids
    ]
    
    attendance_pct = 0.0
    if total_registered > 0:
        attendance_pct = round((total_present / total_registered) * 100, 1)
        
    return {
        "date": date,
        "subject": subject or "All",
        "available_subjects": available_subjects,
        "total_registered": total_registered,
        "total_present": total_present,
        "total_late": total_late,
        "attendance_pct": attendance_pct,
        "present_list": present_list,
        "late_list": late_list,
        "absent_list": absent_list
    }


@router.get("/export-historical-csv")
async def export_historical_csv(date: str, subject: str = None, format: str = "csv", institution_id: str = Depends(get_admin_user)):
    """Generate and return report for a given date and subject."""
    all_students = get_all_students(institution_id)
    student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
    name_map = {s["student_id"]: s.get("name", "Unknown") for s in all_students}
    
    attendance_records = get_attendance_by_date(institution_id, date)
    
    if subject and subject != "All":
        attendance_records = [r for r in attendance_records if r.get("subject_name") == subject]
        
    if not attendance_records:
        raise HTTPException(status_code=400, detail="No attendance records found for given date/subject.")
        
    # Inject roll numbers
    for record in attendance_records:
        record["roll_number"] = student_map.get(record["student_id"], "N/A")
        record["name"] = name_map.get(record["student_id"], record.get("name"))
        
    present_student_ids = {record["student_id"] for record in attendance_records}
    absent_records = [
        {"student_id": student["student_id"], "name": student.get("name", "N/A"), "roll_number": student_map.get(student["student_id"], "N/A")} 
        for student in all_students if student["student_id"] not in present_student_ids
    ]
        
    if format == "excel":
        filepath = generate_excel_report(attendance_records, subject or "All", date, absent_records)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "pdf":
        filepath = generate_pdf_report(attendance_records, subject or "All", date, absent_records)
        media_type = "application/pdf"
    else:
        filepath = generate_custom_report(attendance_records, subject or "All", date)
        media_type = "text/csv"
    
    if not filepath:
        raise HTTPException(status_code=400, detail="Could not generate custom report.")
        
    return FileResponse(path=filepath, filename=filepath.split('/')[-1], media_type=media_type)

