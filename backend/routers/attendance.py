"""
Attendance API router — Phase-1 Intelligent Upgrade.
Handles session management, real-time attendance marking with temporal
stability tracking, and attendance record retrieval.
"""

import base64
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from PIL import Image

from backend.config import DATABASE_MODE, MAX_FRAME_SIZE_BYTES, FRAME_RESIZE_WIDTH
from backend.services.face_detection import detect_faces
from backend.services.embedding_service import generate_embedding
from backend.services.session_service import get_session_manager
from backend.services.temporal_tracker import get_tracker
from backend.services.optimized_recognition import get_embedding_cache

# Import the appropriate database service
if DATABASE_MODE == "firebase":
    from backend.database.firebase_service import (
        add_attendance,
        get_attendance_by_date,
    )
else:
    from backend.database.sqlite_service import (
        add_attendance,
        get_attendance_by_date,
    )

router = APIRouter(prefix="/api", tags=["Attendance"])


# ──────────────────────────────────────────────
# Request / Response Models
# ──────────────────────────────────────────────

class MarkAttendanceRequest(BaseModel):
    frame: str  # Single base64-encoded JPEG frame


class StartSessionRequest(BaseModel):
    subject_name: str


class DetectedFace(BaseModel):
    student_id: str
    name: str
    confidence: float
    status: str  # "marked", "tracking", "already_marked", "cooldown", "unknown"
    box: list = []  # Bounding box [x1, y1, x2, y2]
    frames_tracked: int = 0
    frames_needed: int = 0


class MarkAttendanceResponse(BaseModel):
    success: bool
    faces_detected: int
    faces_recognized: int
    results: list[DetectedFace]
    session_active: bool = False
    session_subject: str = ""


# ──────────────────────────────────────────────
# Session Endpoints
# ──────────────────────────────────────────────

@router.post("/session/start")
def start_session(request: StartSessionRequest):
    """Start a new class session. Ends any previous active session."""
    name = request.subject_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Subject name is required.")

    mgr = get_session_manager()
    tracker = get_tracker()
    cache = get_embedding_cache()

    # Reset tracker for the new session
    tracker.reset()

    # Preload student embeddings into cache
    cache.load()

    session = mgr.start_session(name)
    return {
        "success": True,
        "message": f"Session started: {name}",
        "session": session.to_dict(),
    }


@router.post("/session/end")
def end_session():
    """End the currently active session."""
    mgr = get_session_manager()
    tracker = get_tracker()

    ended = mgr.end_session()
    tracker.reset()

    if ended:
        return {
            "success": True,
            "message": f"Session ended: {ended.subject_name}",
            "session": ended.to_dict(),
        }
    return {"success": False, "message": "No active session to end."}


@router.get("/session/status")
def session_status():
    """Get current session status."""
    mgr = get_session_manager()
    tracker = get_tracker()

    session = mgr.get_active_session()
    if session:
        return {
            "active": True,
            "session": session.to_dict(),
            "tracker": tracker.get_stats(),
        }
    return {"active": False, "session": None, "tracker": tracker.get_stats()}


@router.get("/session/history")
def session_history():
    """Get all past sessions."""
    mgr = get_session_manager()
    return {"sessions": mgr.get_session_history()}


# ──────────────────────────────────────────────
# Attendance Marking Endpoint
# ──────────────────────────────────────────────

@router.post("/mark-attendance", response_model=MarkAttendanceResponse)
def mark_attendance(request: MarkAttendanceRequest):
    """
    Detect faces in a frame and mark attendance for recognized students.
    Requires an active session. Uses temporal tracking for stability.
    """
    mgr = get_session_manager()
    session = mgr.get_active_session()

    # Require active session
    if not session:
        return MarkAttendanceResponse(
            success=False,
            faces_detected=0,
            faces_recognized=0,
            results=[],
            session_active=False,
            session_subject="",
        )

    # Decode frame
    try:
        frame_bytes = base64.b64decode(request.frame)
        if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="Frame size exceeds limit.")
        image = Image.open(BytesIO(frame_bytes)).convert("RGB")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid frame data: {e}")

    # ── CPU Optimization: resize frame ──
    w, h = image.size
    if w > FRAME_RESIZE_WIDTH:
        ratio = FRAME_RESIZE_WIDTH / w
        new_h = int(h * ratio)
        image = image.resize((FRAME_RESIZE_WIDTH, new_h), Image.BILINEAR)

    # Detect all faces
    face_tensors, boxes, probs = detect_faces(image)

    if face_tensors is None:
        # No faces — still pass empty to tracker to update misses
        get_tracker().update([])
        return MarkAttendanceResponse(
            success=True,
            faces_detected=0,
            faces_recognized=0,
            results=[],
            session_active=True,
            session_subject=session.subject_name,
        )

    # ── Recognition using cached embeddings ──
    cache = get_embedding_cache()
    if not cache.is_loaded():
        cache.load()

    recognized_faces = []
    for i in range(len(face_tensors)):
        face_tensor = face_tensors[i]
        box = boxes[i].tolist() if boxes is not None else []

        try:
            embedding = generate_embedding(face_tensor)
        except Exception as e:
            print(f"⚠️  Error generating embedding for face {i}: {e}")
            continue

        match = cache.find_match(embedding)

        if match is not None:
            recognized_faces.append({
                "student_id": match["student_id"],
                "name": match["name"],
                "confidence": match["confidence"],
                "box": box,
                "status": "recognized",
            })
        else:
            recognized_faces.append({
                "student_id": "unknown",
                "name": "Unknown",
                "confidence": 0.0,
                "box": box,
                "status": "unknown",
            })

    # ── Temporal tracking ──
    tracker = get_tracker()
    actions = tracker.update(recognized_faces)

    # ── Process actions: mark attendance for stable detections ──
    today_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    results = []
    faces_recognized = 0

    for action in actions:
        act = action["action"]

        if act == "mark":
            # Stable detection — record in database
            try:
                add_attendance(
                    student_id=action["student_id"],
                    name=action["name"],
                    session_id=session.session_id,
                    subject_name=session.subject_name,
                    date=today_date,
                    time=current_time,
                    timestamp=datetime.now().isoformat(),
                    confidence=action["confidence"],
                )

                mgr.increment_attendance()
                faces_recognized += 1
                results.append(DetectedFace(
                    student_id=action["student_id"],
                    name=action["name"],
                    confidence=action["confidence"],
                    status="marked",
                    box=action.get("box", []),
                ))
            except Exception as e:
                print(f"⚠️  Error marking attendance for {action['name']}: {e}")

        elif act == "tracking":
            results.append(DetectedFace(
                student_id=action["student_id"],
                name=action["name"],
                confidence=action["confidence"],
                status="tracking",
                box=action.get("box", []),
                frames_tracked=action.get("frames_so_far", 0),
                frames_needed=action.get("frames_needed", 0),
            ))

        elif act == "already_marked":
            results.append(DetectedFace(
                student_id=action["student_id"],
                name=action["name"],
                confidence=action["confidence"],
                status="already_marked",
                box=action.get("box", []),
            ))

        elif act == "cooldown":
            results.append(DetectedFace(
                student_id=action["student_id"],
                name=action["name"],
                confidence=action["confidence"],
                status="cooldown",
                box=action.get("box", []),
            ))

        elif act == "unknown":
            results.append(DetectedFace(
                student_id="unknown",
                name="Unknown",
                confidence=0.0,
                status="unknown",
                box=action.get("box", []),
            ))

    return MarkAttendanceResponse(
        success=True,
        faces_detected=len(face_tensors),
        faces_recognized=faces_recognized,
        results=results,
        session_active=True,
        session_subject=session.subject_name,
    )


# ──────────────────────────────────────────────
# Attendance Records Endpoint
# ──────────────────────────────────────────────

@router.get("/attendance/{date}")
def get_attendance(date: str):
    """
    Get attendance records for a specific date.
    Date format: YYYY-MM-DD
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    try:
        records = get_attendance_by_date(date)
        return {
            "date": date,
            "records": records,
            "count": len(records),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {e}")
