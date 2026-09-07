"""
Domain Entities
Pure python representations of core business concepts.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Student:
    student_id: str
    institution_id: str
    name: str
    roll_number: str
    gender: str
    embedding: List[float]
    password: Optional[str] = None
    created_at: Optional[str] = None

@dataclass
class ActiveSession:
    session_id: str
    institution_id: str
    subject_name: str
    start_time: str
    
    def to_dict(self):
        return {
            "session_id": self.session_id,
            "institution_id": self.institution_id,
            "subject_name": self.subject_name,
            "start_time": self.start_time
        }

@dataclass
class AttendanceRecord:
    id: Optional[int]
    institution_id: str
    student_id: str
    name: str
    session_id: str
    subject_name: str
    date: str
    time: str
    timestamp: str
    confidence: float
