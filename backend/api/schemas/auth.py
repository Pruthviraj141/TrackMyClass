from pydantic import BaseModel
from typing import List

class LoginRequest(BaseModel):
    institution_id: str
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MembershipResponse(BaseModel):
    institution_id: str
    role: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    memberships: List[MembershipResponse]
