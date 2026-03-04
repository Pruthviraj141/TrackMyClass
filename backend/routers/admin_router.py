"""
Admin Dashboard Router.
Protected routes for managing the attendance system.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from backend.auth import get_current_user
from backend.config import TEMPLATES_DIR, DATABASE_MODE
from backend.services.session_service import get_session_manager
from backend.services.report_service import generate_session_report, generate_custom_report, generate_excel_report, generate_pdf_report

if DATABASE_MODE == "firebase":
    from backend.database.firebase_service import get_all_students, get_attendance_by_session_id, get_attendance_by_date
else:
    from backend.database.sqlite_service import get_all_students, get_attendance_by_session_id, get_attendance_by_date

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def get_admin_user(request: Request):
    """Dependency to check if user is authenticated admin."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    # Check auth manually to redirect instead of 401 response
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/manage-students", response_class=HTMLResponse)
async def manage_students_page(request: Request):
    """Page to remove student registrations."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("manage_students.html", {"request": request})

@router.get("/api/students")
async def list_students(admin: str = Depends(get_admin_user)):
    """API to list students for management."""
    students = get_all_students()
    # Sort by name
    students.sort(key=lambda x: x.get("name", "").lower())
    return students

@router.get("/api/dashboard-data")
async def get_dashboard_data(admin: str = Depends(get_admin_user)):
    """API endpoint to get dynamic dashboard data."""
    mgr = get_session_manager()
    session = mgr.get_active_session()
    is_active = session is not None
    
    # If no active session, try to get the most recent past session
    if not session and mgr._session_history:
        session = mgr._session_history[-1]
    
    all_students = get_all_students()
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
        attendance_records = get_attendance_by_session_id(session.session_id)
        present_student_ids = {record["student_id"] for record in attendance_records}
        
        student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
        
        present_list = []
        for record in attendance_records:
            record["roll_number"] = student_map.get(record["student_id"], "N/A")
            present_list.append(record)
            
        total_present = len(present_student_ids)
        
        absent_list = [
            {"student_id": student["student_id"], "name": student["name"], "roll_number": student.get("roll_number", "N/A")} 
            for student in all_students if student["student_id"] not in present_student_ids
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
        "attendance_pct": attendance_pct,
        "present_list": present_list,
        "absent_list": absent_list
    }

@router.get("/export-csv")
async def export_csv(format: str = "csv", admin: str = Depends(get_admin_user)):
    """Generate and return report for the active session in chosen format."""
    mgr = get_session_manager()
    session = mgr.get_active_session()
    
    # Allow exporting the last session if no session is active
    if not session and mgr._session_history:
        session = mgr._session_history[-1]
    
    if not session:
        raise HTTPException(status_code=400, detail="No session available to export.")
        
    attendance_records = get_attendance_by_session_id(session.session_id)
    
    all_students = get_all_students()
    student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
    
    for record in attendance_records:
        record["roll_number"] = student_map.get(record["student_id"], "N/A")
        
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


@router.get("/api/historical-data")
async def get_historical_data(date: str, subject: str = None, admin: str = Depends(get_admin_user)):
    """API endpoint to get historical attendance data by date and optionally subject."""
    all_students = get_all_students()
    total_registered = len(all_students)
    student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
    
    attendance_records = get_attendance_by_date(date)
    
    # Extract available subjects for this date
    available_subjects = list(set(r.get("subject_name", "Unknown") for r in attendance_records))
    
    # Filter by subject if provided
    if subject and subject != "All":
        attendance_records = [r for r in attendance_records if r.get("subject_name") == subject]
    
    present_student_ids = {record["student_id"] for record in attendance_records}
    
    present_list = []
    for record in attendance_records:
        r_copy = dict(record)
        r_copy["roll_number"] = student_map.get(record["student_id"], "N/A")
        present_list.append(r_copy)
        
    total_present = len(present_student_ids)
    
    absent_list = [
        {"student_id": student["student_id"], "name": student["name"], "roll_number": student_map.get(student["student_id"], "N/A")} 
        for student in all_students if student["student_id"] not in present_student_ids
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
        "attendance_pct": attendance_pct,
        "present_list": present_list,
        "absent_list": absent_list
    }


@router.get("/export-historical-csv")
async def export_historical_csv(date: str, subject: str = None, format: str = "csv", admin: str = Depends(get_admin_user)):
    """Generate and return report for a given date and subject."""
    all_students = get_all_students()
    student_map = {s["student_id"]: s.get("roll_number", "N/A") for s in all_students}
    
    attendance_records = get_attendance_by_date(date)
    
    if subject and subject != "All":
        attendance_records = [r for r in attendance_records if r.get("subject_name") == subject]
        
    if not attendance_records:
        raise HTTPException(status_code=400, detail="No attendance records found for given date/subject.")
        
    # Inject roll numbers
    for record in attendance_records:
        record["roll_number"] = student_map.get(record["student_id"], "N/A")
        
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

