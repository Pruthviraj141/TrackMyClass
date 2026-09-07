"""
Attendance API Router
Thin layer handling HTTP endpoints and API responses.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from backend.api.dependencies import require_role
from backend.domain.identity import User, Role
from backend.application.attendance_service import AttendanceService
from backend.repositories.attendance_repository import AttendanceRepository
from backend.core.errors import ValidationError, SessionError

from backend.api.dependencies import get_current_user_from_token

def get_admin_user(current_user: User = Depends(get_current_user_from_token)) -> str:
    if not current_user.memberships:
        raise HTTPException(status_code=403, detail="No institution membership found within signed Claims")
    
    membership = current_user.memberships[0]
    if membership.role not in [Role.SUPER_ADMIN, Role.INSTITUTION_ADMIN, Role.TEACHER]:
        raise HTTPException(status_code=403, detail="Insufficient privileges.")
        
    return membership.institution_id


router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance"])

from backend.api.schemas.attendance import MarkAttendanceRequest, StartSessionRequest

@router.post("/session/start")
async def start_session(request: StartSessionRequest, institution_id: str = Depends(get_admin_user)):
    name = request.subject_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Subject name is required.")

    service = AttendanceService(institution_id)
    session = await service.start_session(name)
    return {
        "success": True,
        "message": f"Session started: {name}",
        "session": session.to_dict(),
    }

@router.post("/session/end")
async def end_session(institution_id: str = Depends(get_admin_user)):
    service = AttendanceService(institution_id)
    ended = await service.end_session()
    if ended:
        return {
            "success": True,
            "message": f"Session ended: {ended.subject_name}",
            "session": ended.to_dict(),
        }
    return {"success": False, "message": "No active session to end."}

@router.get("/session/status")
async def session_status(institution_id: str = Depends(get_admin_user)):
    service = AttendanceService(institution_id)
    session = await service.get_session_status()
    if session:
        return {
            "active": True,
            "session": session.to_dict()
        }
    return {"active": False, "session": None}

@router.get("/session/history")
async def session_history(institution_id: str = Depends(get_admin_user)):
    from backend.services.session_service import get_session_manager
    mgr = get_session_manager()
    return {"sessions": await mgr.get_session_history(institution_id)}

@router.post("/mark-attendance")
async def mark_attendance(request: MarkAttendanceRequest, institution_id: str = Depends(get_admin_user)):
    service = AttendanceService(institution_id)
    try:
        res = await service.mark_attendance(request.frame)
        return res
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SessionError as e:
        # Not active session
        return {
            "success": False,
            "faces_detected": 0,
            "faces_recognized": 0,
            "results": [],
            "session_active": False,
            "session_subject": ""
        }

@router.get("/attendance/{date}")
def get_attendance(date: str, institution_id: str = Depends(get_admin_user)):
    try:
        from datetime import datetime
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date")

    try:
        repo = AttendanceRepository()
        records = repo.get_by_date(institution_id, date)
        # Convert objects to dicts
        records_dict = [r.__dict__ for r in records]
        return {
            "date": date,
            "records": records_dict,
            "count": len(records),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ManualUpdateRequest(BaseModel):
    student_id: str
    date: str
    status: str
    subject_name: str = "Unknown"
    session_id: str = "manual_override"

@router.post("/manual-update")
def manual_update_attendance(request: ManualUpdateRequest, institution_id: str = Depends(get_admin_user)):
    """API endpoint to manually toggle a student's attendance between present and absent natively."""
    from backend.repositories.attendance_repository import AttendanceRepository
    from backend.domain.entities import AttendanceRecord
    import datetime

    repo = AttendanceRepository()

    try:
        # Guarantee subject isolation by mapping the manual session ID directly to the subject context
        safe_subject = request.subject_name.replace(" ", "_").lower()
        actual_session_id = request.session_id
        if actual_session_id == "manual_override":
            actual_session_id = f"manual_override_{safe_subject}"

        # Delete existing record for this specific session only
        repo.delete_by_date(institution_id, request.student_id, request.date, actual_session_id)
        
        if request.status == "present" or request.status == "late":
            # Add back a 1.0 confidence synthetic manual record
            dt = datetime.datetime.now()
            time_value = "LATE" if request.status == "late" else dt.strftime("%H:%M:%S")
            record = AttendanceRecord(
                id=None,
                institution_id=institution_id,
                student_id=request.student_id,
                name="Manual Entry", # name is fetched lazily safely via joined table usually
                session_id=actual_session_id,
                subject_name=request.subject_name,
                date=request.date,
                time=time_value,
                timestamp=dt.isoformat(),
                confidence=1.0
            )
            # If `infrastructure` relies on accurate name during join, we get it first 
            from backend.core.config import DATABASE_MODE
            if DATABASE_MODE == "firebase":
                from backend.infrastructure.database.firebase_impl import get_student_by_id
            else:
                from backend.infrastructure.database.sqlite_impl import get_student_by_id
            
            student = get_student_by_id(institution_id, request.student_id)
            if student:
                record.name = student.get("name", "Unknown")
                
            repo.add(record)

        return {"success": True, "message": f"Student {request.student_id} marked as {request.status}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
