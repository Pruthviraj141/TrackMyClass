from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List

from backend.api.dependencies import require_role
from backend.domain.identity import User, Role
from backend.application.registration_service import RegistrationService
from backend.core.errors import ValidationError

def get_admin_user(current_user: User = Depends(require_role("DEMO2026", [Role.INSTITUTION_ADMIN, Role.TEACHER]))) -> str:
    return "DEMO2026"

router = APIRouter(prefix="/api/v1/registration", tags=["Registration"])

from backend.api.schemas.registration import RegisterRequest

@router.post("/register")
def register_student(request: RegisterRequest):
    # Public endpoint — no auth required. Institution is derived from the request.
    institution_id = (request.collegeCode or "DEMO2026").upper()
    name = request.name.strip()
    roll = request.roll_number.strip()
    
    if not name or not roll:
        raise HTTPException(status_code=400, detail="Missing fields")
        
    service = RegistrationService(institution_id)
    try:
        student_id = service.register_student(
            name=name, 
            roll_number=roll, 
            frames=request.frames,
            gender=request.gender or "unknown",
            password=request.password
        )
        return {
            "success": True,
            "message": f"Successfully registered {name}",
            "student_id": student_id
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students")
def list_students(institution_id: str = Depends(get_admin_user)):
    from backend.repositories.student_repository import StudentRepository
    repo = StudentRepository()
    students = repo.get_all(institution_id)
    # Exclude embeddings from wire return
    for s in students:
        s.embedding = []
        s.password = None
    return {"students": [s.__dict__ for s in students], "count": len(students)}

@router.delete("/students/{student_id}")
def remove_student(student_id: str, institution_id: str = Depends(get_admin_user)):
    from backend.repositories.student_repository import StudentRepository
    repo = StudentRepository()
    success = repo.delete(institution_id, student_id)
    
    if success:
        from backend.ml.matcher.optimized_recognition import get_embedding_cache
        get_embedding_cache().refresh(institution_id)
        return {"success": True, "message": "Deleted"}
    
    raise HTTPException(status_code=404, detail="Student not found")
