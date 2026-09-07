import base64
from io import BytesIO
from datetime import datetime
from PIL import Image

from backend.ml.engine import RecognitionEngine
from backend.repositories.attendance_repository import AttendanceRepository
from backend.services.session_service import get_session_manager
from backend.core.config import FRAME_RESIZE_WIDTH, MAX_FRAME_SIZE_BYTES
from backend.core.errors import ValidationError, SessionError

class AttendanceService:
    def __init__(self, institution_id: str):
        self.institution_id = institution_id
        self.engine = RecognitionEngine(institution_id)
        self.attendance_repo = AttendanceRepository()
        self.session_mgr = get_session_manager()
        
    async def start_session(self, subject_name: str):
        self.engine.reset_tracker()
        self.engine.refresh_cache()
        return await self.session_mgr.start_session(self.institution_id, subject_name)
        
    async def end_session(self):
        ended = await self.session_mgr.end_session(self.institution_id)
        self.engine.reset_tracker()
        return ended
        
    async def get_session_status(self):
        return await self.session_mgr.get_active_session(self.institution_id)

    async def mark_attendance(self, frame_base64: str) -> dict:
        session = await self.session_mgr.get_active_session(self.institution_id)
        if not session:
            return {
                "success": False,
                "faces_detected": 0,
                "faces_recognized": 0,
                "results": [],
                "session_active": False,
                "session_subject": ""
            }
            
        try:
            frame_bytes = base64.b64decode(frame_base64)
            if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
                raise ValidationError("Frame size exceeds limit.")
            image = Image.open(BytesIO(frame_bytes)).convert("RGB")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Invalid frame data: {e}")

        w, h = image.size
        # Resize to handle MTCNN overload
        if w > FRAME_RESIZE_WIDTH:
            ratio = FRAME_RESIZE_WIDTH / w
            new_h = int(h * ratio)
            image = image.resize((FRAME_RESIZE_WIDTH, new_h), Image.BILINEAR)

        # ML Engine boundaries handle all extraction, tracking, and matching
        results = self.engine.process_frame(image)

        today_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        from backend.domain.entities import AttendanceRecord
        faces_recognized = 0
        final_results = []

        for r in results:
            if r.recognition_state == "mark":
                record = AttendanceRecord(
                    id=None,
                    institution_id=self.institution_id,
                    student_id=r.student_id,
                    name=r.name,
                    session_id=session.session_id,
                    subject_name=session.subject_name,
                    date=today_date,
                    time=current_time,
                    timestamp=datetime.now().isoformat(),
                    confidence=r.similarity
                )
                try:
                    self.attendance_repo.add(record)
                    await self.session_mgr.increment_attendance(self.institution_id)
                    faces_recognized += 1
                    r.recognition_state = "marked"
                except Exception as e:
                    print(f"Service Error marking DB: {e}")
            final_results.append({
                "student_id": r.student_id,
                "name": r.name,
                "confidence": r.similarity,
                "status": r.recognition_state,
                "box": r.bounding_box,
            })
            
        return {
            "success": True,
            "faces_detected": len(results) if len(results) > 0 else 0, # Note: if 0 faces, length is 0. 
            "faces_recognized": faces_recognized,
            "results": final_results,
            "session_active": True,
            "session_subject": session.subject_name
        }
