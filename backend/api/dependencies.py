"""
API Dependencies for Security boundaries.
Automatically injects the authenticated User and Context into the routes.
"""
from fastapi import Request, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
import json

from backend.core.security import decode_access_token
from backend.domain.identity import User, InstitutionMembership, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user_from_token(token: str = Security(oauth2_scheme)) -> User:
    """Decodes JWT and returns Domain User."""
    print(f"DEBUG: get_current_user_from_token called with token: {token}")
    payload = decode_access_token(token)
    print(f"DEBUG: payload: {payload}")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    user_id = payload.get("sub")
    username = payload.get("username")
    memberships_raw = payload.get("memberships", [])
    
    memberships = []
    for m in memberships_raw:
        memberships.append(InstitutionMembership(
            institution_id=m["institution_id"],
            role=Role(m["role"])
        ))
        
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject")
        
    return User(
        user_id=user_id,
        username=username,
        memberships=memberships
    )

def require_role(institution_id: str, allowed_roles: list[Role]):
    """Returns a dependency injecting role verifications explicitly."""
    def role_checker(user: User = Security(get_current_user_from_token)) -> User:
        user_role = user.get_role(institution_id)
        
        # Super Admins bypass institution-specific blocks implicitly
        if user.has_role(institution_id, Role.SUPER_ADMIN):
            return user
            
        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient privileges.")
            
        return user
    return role_checker
