"""
Identity Domain Boundaries
Establishes the fundamental structure uniting Tenants and Users.
"""
from dataclasses import dataclass
from typing import List
from enum import Enum

class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    INSTITUTION_ADMIN = "INSTITUTION_ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"

@dataclass
class InstitutionMembership:
    institution_id: str
    role: Role

@dataclass
class User:
    user_id: str
    username: str
    memberships: List[InstitutionMembership]
    
    def has_role(self, institution_id: str, required_role: Role) -> bool:
        """Determines if the user possesses the role for a specific tenant."""
        if required_role == Role.SUPER_ADMIN:
             for m in self.memberships:
                 if m.role == Role.SUPER_ADMIN:
                     return True
        for m in self.memberships:
            if m.institution_id == institution_id and m.role == required_role:
                return True
        return False
        
    def get_role(self, institution_id: str) -> Role | None:
        """Fetch the exact explicit role bound to this context."""
        for m in self.memberships:
            if m.institution_id == institution_id:
                return m.role
        return None
