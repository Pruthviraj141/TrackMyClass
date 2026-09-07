from pydantic import BaseModel, Field

# Rough estimate: A very large Base64 encoded web frame is ~1-3MB string. Limit to 3MB arbitrarily.
MAX_BASE64_LENGTH = 3 * 1024 * 1024

class MarkAttendanceRequest(BaseModel):
    frame: str = Field(..., max_length=MAX_BASE64_LENGTH, description="Base64 encoded JPEG/PNG frame.")

class StartSessionRequest(BaseModel):
    subject_name: str = Field(..., max_length=100, min_length=1)
