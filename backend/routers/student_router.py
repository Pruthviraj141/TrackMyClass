"""
Student Router.
Student dashboard to view their own attendance history.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.auth import get_current_student
from backend.config import TEMPLATES_DIR, DATABASE_MODE

if DATABASE_MODE == "firebase":
    from backend.database.firebase_service import get_attendance_by_date, get_student_by_id
else:
    from backend.database.sqlite_service import get_attendance_by_date, get_student_by_id

router = APIRouter(prefix="/student", tags=["Student"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _require_student(request: Request) -> dict:
    """Helper: redirect to login if student is not authenticated."""
    student = get_current_student(request)
    if not student:
        raise HTTPException(status_code=401)
    return student


@router.get("/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request):
    """Student dashboard page."""
    student = get_current_student(request)
    if not student:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("student_dashboard.html", {"request": request})


@router.get("/api/my-profile")
async def my_profile(request: Request):
    """Get current student profile info."""
    session = _require_student(request)
    student = get_student_by_id(session["user_id"])
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    return {
        "student_id": student["student_id"],
        "name": student["name"],
        "roll_number": student.get("roll_number", "N/A"),
        "gender": student.get("gender", "N/A"),
        "created_at": student.get("created_at", "N/A"),
    }


@router.get("/api/my-attendance")
async def my_attendance(request: Request, date: str = ""):
    """Get attendance records for the logged-in student."""
    session = _require_student(request)
    student_id = session["user_id"]

    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    all_records = get_attendance_by_date(date)
    my_records = [r for r in all_records if r.get("student_id") == student_id]

    return {
        "date": date,
        "records": my_records,
        "total": len(my_records),
        "student_name": session["name"],
    }
