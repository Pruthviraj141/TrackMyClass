from pydantic import BaseModel, Field
from typing import List

MAX_BASE64_LENGTH = 3 * 1024 * 1024

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    roll_number: str = Field(..., min_length=2, max_length=50)
    # Require at least 1 frame, no more than 35 per registration burst (frontend sends 30)
    frames: List[str] = Field(..., min_items=1, max_items=35)
    gender: str | None = None
    password: str | None = None
    consent: bool | None = None
    collegeCode: str | None = None  # used to scope institution_id on public registration
