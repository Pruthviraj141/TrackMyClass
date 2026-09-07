from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.config import DATABASE_MODE

if DATABASE_MODE == "firebase":
    # Fallback/stub for firebase if needed, or import if we wrote it
    # We will just stub it here for simplicity since we focused on SQLite
    def verify_college_code(code: str):
        if code == "DEMO2026":
            return {"code": "DEMO2026", "name": "Demo College Firebase", "active": 1}
        return None
else:
    from backend.infrastructure.database.sqlite_impl import verify_college_code

router = APIRouter(prefix="/api/v1/institutions", tags=["Institutions"])

from typing import Optional

class VerifyCodeRequest(BaseModel):
    code: str

class CreateInstitutionRequest(BaseModel):
    name: str
    type: Optional[str] = ""
    email: Optional[str] = ""
    code: Optional[str] = None

@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest):
    institution = verify_college_code(request.code.upper())
    if institution:
        return {
            "valid": True,
            "institutionName": institution["name"],
            "code": institution["code"]
        }
    return {"valid": False, "message": "Invalid college code"}

@router.post("/create")
async def create_new_institution(request: CreateInstitutionRequest):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="Institution name is required.")
        
    code = (request.code or "").strip().upper()
    if not code:
        # Generate code from name (e.g. "Harvard University" -> "HARVARD")
        clean_words = "".join([c for c in request.name.upper() if c.isalnum() or c.isspace()]).split()
        prefix = clean_words[0] if clean_words else "INST"
        code = f"{prefix[:8]}2026"

    if DATABASE_MODE == "firebase":
        from backend.infrastructure.database.firebase_impl import create_institution
    else:
        from backend.infrastructure.database.sqlite_impl import create_institution

    try:
        res = create_institution(code, request.name.strip(), request.type or "", request.email or "")
        return {
            "success": True,
            "code": res["code"],
            "institutionName": res["name"],
            "message": "Institution created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create institution.")

