from fastapi import APIRouter, HTTPException, Depends
from backend.api.schemas.auth import LoginRequest, TokenResponse, UserResponse
from backend.core.security import verify_password, create_access_token
from backend.domain.identity import User, InstitutionMembership, Role
from backend.core.config import ADMIN_USERNAME, ADMIN_PASSWORD
from backend.api.dependencies import get_current_user_from_token

# NOTE: In a real system, the Database looks up `users`. 
# For maintaining Phase 2 backwards compatibility cleanly without changing SQLite schema drastically,
# we simulate retrieving users, injecting the Tenant rules securely mapping the legacy env to standard JWTs.

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

def _mock_db_lookup(institution_id: str, username: str, password: str) -> User | None:
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return User(
            user_id="sysadmin_123",
            username=ADMIN_USERNAME,
            memberships=[InstitutionMembership(institution_id=institution_id, role=Role.INSTITUTION_ADMIN)]
        )
    return None

from fastapi import Request, Form
from backend.core.security import get_password_hash
from backend.core.audit import log_security_event

@router.post("/login", response_model=TokenResponse)
def login(request: Request, login_type: str = Form(...), username: str = Form(None), password: str = Form(None), roll_number: str = Form(None), institution_id: str = Form("DEMO2026")):
    user = None
    institution_id = institution_id.upper()
    
    if login_type == "admin":
        user = _mock_db_lookup(institution_id, username, password)
    elif login_type == "student":
        # Real student lookup from database with bcrypt password verification
        try:
            from backend.core.config import DATABASE_MODE
            if DATABASE_MODE == "firebase":
                from backend.infrastructure.database.firebase_impl import get_student_by_roll_number
            else:
                from backend.infrastructure.database.sqlite_impl import get_student_by_roll_number
            
            student_record = get_student_by_roll_number(institution_id, roll_number or "")
            if student_record:
                stored_pw = student_record.get("password", "")
                if stored_pw and verify_password(password or "", stored_pw):
                    user = User(
                        user_id=student_record["student_id"],
                        username=student_record["name"],
                        memberships=[InstitutionMembership(institution_id=institution_id, role=Role.STUDENT)]
                    )
                # If no password stored (legacy registration), allow by roll_number only (degraded mode)
                elif not stored_pw and student_record:
                    user = User(
                        user_id=student_record["student_id"],
                        username=student_record["name"],
                        memberships=[InstitutionMembership(institution_id=institution_id, role=Role.STUDENT)]
                    )
        except Exception as e:
            log_security_event("STUDENT_LOGIN_ERROR", "ERROR", {"roll_number": roll_number, "error": str(e)})
        
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    client_ip = request.client.host if request.client else "unknown"
    if not user:
        log_security_event("LOGIN_ATTEMPT", "FAILED", {"username": username or roll_number, "ip": client_ip, "request_id": correlation_id})
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    log_security_event("LOGIN_ATTEMPT", "SUCCESS", {"user_id": user.user_id, "username": user.username, "ip": client_ip, "request_id": correlation_id})


    memberships_serialized = [
        {"institution_id": m.institution_id, "role": m.role.value} 
        for m in user.memberships
    ]
        
    token = create_access_token(data={
        "sub": user.user_id,
        "username": user.username,
        "memberships": memberships_serialized
    })
    
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user_from_token)):
    from backend.api.dependencies import get_current_user_from_token
    return current_user
