"""
WebSocket Live Monitor endpoint.

URL: ws://host/api/v1/ws/monitor/{session_id}?token=<jwt>

Connection lifecycle:
  CONNECT → AUTHENTICATE → JOIN_SESSION → STREAM → DISCONNECT

Authentication:
  - JWT extracted from ?token= query param
  - Validated server-side; institution derived from token claims
  - Session ownership verified against SessionManager

Frame ingestion:
  - Client sends raw JPEG bytes (binary WebSocket frames)
  - Max frame size: 512 KB
  - Rate limit: 5 frames/s per connection (token bucket)

Result delivery:
  - After inference, JSON result pushed back over same connection:
    {"type": "recognition.result", "session_id": "...", "results": [...]}

Error messages:
  {"type": "error", "code": 4001, "message": "..."} then close
"""
import json
import time
import asyncio
import logging

import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from starlette.websockets import WebSocketState

from backend.api.dependencies import get_current_user_from_token
from backend.application.attendance_service import AttendanceService
from backend.worker.worker_manager import get_worker_manager
from backend.core.logger import get_structured_logger, correlation_id_ctx, session_id_ctx

logger = get_structured_logger(__name__)

router = APIRouter(tags=["WebSocket"])

# ── Constants ──────────────────────────────────────────────────────────────────
_MAX_FRAME_BYTES = 512 * 1024   # 512 KB hard limit per frame
_RATE_LIMIT_FPS = 5             # max frames accepted per second per connection
_RATE_LIMIT_WINDOW = 1.0        # rolling window in seconds


async def _close(ws: WebSocket, code: int, reason: str) -> None:
    """Send an error message then close the WebSocket gracefully."""
    try:
        if ws.client_state == WebSocketState.CONNECTED:
            await ws.send_json({"type": "error", "code": code, "message": reason})
            await ws.close(code=code)
    except Exception:
        pass


@router.websocket("/api/v1/ws/monitor/{session_id}")
async def ws_monitor(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(default=""),
) -> None:
    await websocket.accept()

    # ── 1. AUTHENTICATE ───────────────────────────────────────────────────────
    if not token:
        await _close(websocket, 4001, "Missing authentication token")
        return

    try:
        current_user = get_current_user_from_token(token)
    except Exception:
        await _close(websocket, 4001, "Invalid or expired token")
        return

    # Extract institution_id from the first membership claim
    memberships = getattr(current_user, "memberships", [])
    if not memberships:
        await _close(websocket, 4003, "No institution membership found")
        return
    institution_id = memberships[0].institution_id

    # ── 2. JOIN_SESSION ───────────────────────────────────────────────────────
    from backend.services.session_service import get_session_manager
    session_mgr = get_session_manager()
    session = await session_mgr.get_active_session(institution_id)

    if not session:
        await _close(websocket, 4004, "No active session for your institution")
        return

    if session.session_id != session_id:
        await _close(websocket, 4003, "Session ID does not match active session")
        return

    await websocket.send_json({
        "type": "session.joined",
        "session_id": session_id,
        "subject": session.subject_name,
    })

    # ── 3. LOAD ROLL NUMBERS ──────────────────────────────────────────────────
    from backend.core.config import DATABASE_MODE
    if DATABASE_MODE == "firebase":
        from backend.infrastructure.database.firebase_impl import get_all_students
    else:
        from backend.infrastructure.database.sqlite_impl import get_all_students
        
    all_students = get_all_students(institution_id)
    roll_number_map = {s["student_id"]: s.get("roll_number", "") for s in all_students}
    name_map = {s["student_id"]: s.get("name", "") for s in all_students}
    
    # ── 4. STREAM ─────────────────────────────────────────────────────────────
    worker_mgr = get_worker_manager()
    attendance_svc = AttendanceService(institution_id)

    # Token-bucket rate limiter state
    frame_times: list[float] = []

    try:
        while True:
            # Generate correlation bounds for loop
            corr_id = str(uuid.uuid4())
            correlation_id_ctx.set(corr_id)
            session_id_ctx.set(session_id)
            
            # Receive raw binary frame from client
            try:
                raw = await asyncio.wait_for(websocket.receive_bytes(), timeout=30.0)
            except asyncio.TimeoutError:
                # Ping to keep connection alive
                await websocket.send_json({"type": "ping"})
                continue

            # ── Frame size guard ─────────────────────────────────────────────
            if len(raw) > _MAX_FRAME_BYTES:
                await websocket.send_json({
                    "type": "warning",
                    "message": f"Frame too large ({len(raw)} bytes). Max {_MAX_FRAME_BYTES}.",
                })
                continue

            # ── Rate limiting (token bucket, rolling window) ─────────────────
            now = time.monotonic()
            frame_times = [t for t in frame_times if now - t < _RATE_LIMIT_WINDOW]
            if len(frame_times) >= _RATE_LIMIT_FPS:
                # Drop silently — client is sending too fast
                continue
            frame_times.append(now)

            # ── Submit to inference worker ───────────────────────────────────
            try:
                result = await worker_mgr.submit_frame(
                    institution_id=institution_id,
                    session_id=session_id,
                    frame_bytes=raw,
                )
            except RuntimeError as exc:
                await websocket.send_json({
                    "type": "worker.unavailable",
                    "message": str(exc),
                })
                continue

            if result.get("error"):
                await websocket.send_json({
                    "type": "inference.error",
                    "message": result["error"],
                })
                continue

            # ── Persist attendance for stable faces ──────────────────────────
            faces = result.get("results", [])
            for face in faces:
                # Inject roll number and name unconditionally
                sid = face.get("student_id")
                face["roll_number"] = roll_number_map.get(sid, "")
                face["name"] = name_map.get(sid, str(sid))
                
                if face.get("status") == "mark":
                    try:
                        # Re-use service to persist; it handles idempotency via tracker
                        # We call with a tiny base64 just to trigger the session-aware path
                        # Actually we already have processed results — persist directly
                        from datetime import datetime
                        from backend.domain.entities import AttendanceRecord
                        from backend.repositories.attendance_repository import AttendanceRepository
                        repo = AttendanceRepository()
                        active = await session_mgr.get_active_session(institution_id)
                        if active:
                            # Distributed SETNX lock to guarantee idempotency across multiple workers/nodes
                            from backend.core.redis_client import RedisManager
                            rc = RedisManager.get_client()
                            
                            lock_key = f"attendance:{active.session_id}:{face['student_id']}"
                            can_mark = True
                            
                            if rc:
                                try:
                                    is_new = await rc.setnx(lock_key, "1")
                                    if is_new:
                                        await rc.expire(lock_key, 86400)
                                    else:
                                        can_mark = False
                                        face["status"] = "marked"  # Update ui without db insert
                                except Exception as auth_exec:
                                    logger.warning(f"Idempotency redis fail. Falling back safely: {auth_exec}")
                                    # Fall back to DB lookup
                                    existing = repo.get_by_date(institution_id, datetime.now().strftime("%Y-%m-%d"))
                                    if any(x.student_id == face["student_id"] and x.session_id == active.session_id for x in existing):
                                        can_mark = False
                                        face["status"] = "marked"
                            else:
                                existing = repo.get_by_date(institution_id, datetime.now().strftime("%Y-%m-%d"))
                                if any(x.student_id == face["student_id"] and x.session_id == active.session_id for x in existing):
                                    can_mark = False
                                    face["status"] = "marked"

                            if can_mark:
                                record = AttendanceRecord(
                                    id=None,
                                    institution_id=institution_id,
                                    student_id=face["student_id"],
                                    name=face["name"],
                                    session_id=active.session_id,
                                    subject_name=active.subject_name,
                                    date=datetime.now().strftime("%Y-%m-%d"),
                                    time=datetime.now().strftime("%H:%M:%S"),
                                    timestamp=datetime.now().isoformat(),
                                    confidence=face.get("confidence", 0.0),
                                )
                                repo.add(record)
                                await session_mgr.increment_attendance(institution_id)
                                face["status"] = "marked"
                    except Exception as e:
                        logger.error("Attendance persist error: %s", e)

            active = await session_mgr.get_active_session(institution_id)
            await websocket.send_json({
                "type": "recognition.result",
                "session_id": session_id,
                "results": faces,
                "faces_detected": len(faces),
                "faces_recognized": active.attendance_count if active else 0,
                "session_active": active is not None,
                "session_subject": active.subject_name if active else "",
                "processing_ms": result.get("processing_ms", 0),
            })

    except WebSocketDisconnect:
        logger.info("WS disconnect: session=%s institution=%s", session_id, institution_id)
    except Exception as exc:
        logger.exception("WS error: %s", exc)
        await _close(websocket, 1011, "Internal server error")
