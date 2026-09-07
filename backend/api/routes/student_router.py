"""
Student Router.
Student dashboard to view their own attendance history.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

from backend.api.dependencies import get_current_user_from_token
from backend.domain.identity import User
from backend.core.config import TEMPLATES_DIR, DATABASE_MODE

if DATABASE_MODE == "firebase":
    from backend.infrastructure.database.firebase_impl import get_attendance_by_date, get_student_by_id
else:
    from backend.infrastructure.database.sqlite_impl import get_attendance_by_date, get_student_by_id

router = APIRouter(prefix="/api/v1/student", tags=["Student"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _require_student(user: User = Depends(get_current_user_from_token)) -> User:
    if not user:
        raise HTTPException(status_code=401)
    return user


@router.get("/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request):
    """Student dashboard page."""
    student = get_current_student(request)
    if not student:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="student_dashboard.html")


@router.get("/my-profile")
async def my_profile(session: User = Depends(_require_student)):
    """Get current student profile info."""
    institution_id = session.memberships[0].institution_id if session.memberships else "DEMO2026"
    student = get_student_by_id(institution_id, session.user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    return {
        "student_id": student["student_id"],
        "name": student["name"],
        "roll_number": student.get("roll_number", "N/A"),
        "gender": student.get("gender", "N/A"),
        "created_at": student.get("created_at", "N/A"),
    }


@router.get("/my-attendance")
async def my_attendance(session: User = Depends(_require_student)):
    """Get all attendance records for the logged-in student."""
    student_id = session.user_id
    institution_id = session.memberships[0].institution_id if session.memberships else "DEMO2026"

    try:
        from backend.core.config import DATABASE_MODE
        if DATABASE_MODE == "firebase":
            from backend.infrastructure.database.firebase_impl import _get_db, get_student_attendance_stats
            from firebase_admin import firestore
            db = _get_db()
            docs = (
                db.collection("attendance")
                .where(filter=firestore.FieldFilter("institution_id", "==", institution_id))
                .where(filter=firestore.FieldFilter("student_id", "==", student_id))
                .stream()
            )
            records = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                records.append(data)
            
            stats = get_student_attendance_stats(institution_id, student_id)
        else:
            from backend.infrastructure.database.sqlite_impl import get_attendance_by_student, get_student_attendance_stats
            records = get_attendance_by_student(institution_id, student_id)
            stats = get_student_attendance_stats(institution_id, student_id)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch attendance: {e}")

    return {
        "records": records,
        "total": len(records),
        "student_name": session.username,
        "overall_stats": stats["overall_stats"],
        "subject_stats": stats["subject_stats"]
    }


class UpdateFaceRequest(BaseModel):
    frames: List[str]

@router.post("/update-face")
async def update_face(request: UpdateFaceRequest, session: User = Depends(_require_student)):
    """Update face embeddings securely for the authenticated student."""
    from backend.application.registration_service import RegistrationService
    from backend.core.errors import ValidationError
    
    institution_id = session.memberships[0].institution_id if session.memberships else "DEMO2026"
    service = RegistrationService(institution_id)
    
    try:
        service.update_student_embedding(
            student_id=session.user_id,
            frames=request.frames
        )
        return {"success": True, "message": "Face profile updated successfully."}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

