"""
Registration API router.
Handles student registration with name, roll number, gender, and face frames.
"""

import base64
import uuid
from io import BytesIO

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator
from PIL import Image

from backend.config import DATABASE_MODE, MAX_FRAME_SIZE_BYTES, MIN_FRAMES_REQUIRED
from backend.services.face_detection import detect_single_face
from backend.services.embedding_service import generate_average_embedding
from backend.auth import get_current_user

# Import the appropriate database service
if DATABASE_MODE == "firebase":
    from backend.database.firebase_service import add_student, get_all_students, delete_student
else:
    from backend.database.sqlite_service import add_student, get_all_students, delete_student

router = APIRouter(prefix="/api", tags=["Registration"])


# ──────────────────────────────────────────────
# Request / Response Models
# ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    roll_number: str
    gender: str
    password: str  # Student login password
    frames: list[str]  # List of base64-encoded JPEG frames
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if not v or len(v) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        if len(v) > 100:
            raise ValueError("Name must be less than 100 characters.")
        return v
    
    @field_validator("roll_number")
    @classmethod
    def validate_roll_number(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Roll number is required.")
        if len(v) > 50:
            raise ValueError("Roll number must be less than 50 characters.")
        return v
    
    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        v = v.strip().lower()
        if v not in ("male", "female", "other"):
            raise ValueError("Gender must be 'male', 'female', or 'other'.")
        return v
    
    @field_validator("frames")
    @classmethod
    def validate_frames(cls, v):
        if len(v) < MIN_FRAMES_REQUIRED:
            raise ValueError(f"At least {MIN_FRAMES_REQUIRED} frames are required.")
        return v


class RegisterResponse(BaseModel):
    success: bool
    message: str
    student_id: str = ""


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("/register", response_model=RegisterResponse)
async def register_student(request: RegisterRequest):
    """
    Register a new student.
    Accepts name, roll number, gender, and multiple base64-encoded face frames.
    Extracts faces, generates averaged embedding, and stores in database.
    """
    face_tensors = []
    skipped_frames = 0
    
    for i, frame_b64 in enumerate(request.frames):
        try:
            # Validate frame size
            frame_bytes = base64.b64decode(frame_b64)
            if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
                skipped_frames += 1
                continue
            
            # Decode to PIL Image
            image = Image.open(BytesIO(frame_bytes)).convert("RGB")
            
            # Detect face
            face_tensor, box, prob = detect_single_face(image)
            
            if face_tensor is not None:
                face_tensors.append(face_tensor)
            else:
                skipped_frames += 1
                
        except Exception as e:
            print(f"⚠️  Error processing frame {i}: {e}")
            skipped_frames += 1
            continue
    
    # Check minimum valid faces
    if len(face_tensors) < MIN_FRAMES_REQUIRED:
        raise HTTPException(
            status_code=400,
            detail=f"Only {len(face_tensors)} valid faces detected out of {len(request.frames)} frames. "
                   f"Need at least {MIN_FRAMES_REQUIRED}. Please ensure your face is clearly visible."
        )
    
    # Generate averaged embedding
    try:
        avg_embedding = generate_average_embedding(face_tensors)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Store in database
    student_id = str(uuid.uuid4())
    
    # Hash the password for secure storage
    from backend.auth import hash_password
    hashed_pw = hash_password(request.password)
    
    try:
        add_student(
            student_id=student_id,
            name=request.name,
            roll_number=request.roll_number,
            gender=request.gender,
            embedding=avg_embedding.tolist(),
            password=hashed_pw,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    # Refresh the in-memory embedding cache so the new student is immediately recognizable
    from backend.services.optimized_recognition import get_embedding_cache
    get_embedding_cache().refresh()
    
    return RegisterResponse(
        success=True,
        message=f"Successfully registered {request.name} with {len(face_tensors)} face samples. "
                f"({skipped_frames} frames skipped)",
        student_id=student_id,
    )


@router.get("/students")
async def list_students():
    """List all registered students (without embeddings for security)."""
    try:
        students = get_all_students()
        # Remove embeddings from response
        safe_students = []
        for s in students:
            safe_students.append({
                "student_id": s["student_id"],
                "name": s["name"],
                "roll_number": s.get("roll_number", "N/A"),
                "gender": s.get("gender", "N/A"),
                "created_at": s["created_at"],
            })
        return {"students": safe_students, "count": len(safe_students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching students: {e}")


@router.delete("/students/{student_id}")
async def remove_student(student_id: str, request: Request):
    """
    Remove a student from the database.
    Admin-only: requires authenticated session.
    """
    # Check admin authentication
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Admin authentication required to delete students.")
    
    try:
        success = delete_student(student_id)
        if not success:
            raise HTTPException(status_code=404, detail="Student not found.")
        # Refresh embedding cache
        from backend.services.optimized_recognition import get_embedding_cache
        get_embedding_cache().refresh()
        return {"success": True, "message": "Student removed successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting student: {e}")

