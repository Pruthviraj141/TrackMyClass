from fastapi.testclient import TestClient
from backend.main import app
from backend.api.schemas.attendance import MAX_BASE64_LENGTH

client = TestClient(app)

def test_oversized_payload_rejected():
    """Verify that attempting to abuse endpoints with 4MB payloads (above 3MB limit) trigger 422 constraints instantaneously before hitting memory parsers."""
    # Generate mock token
    from backend.core.security import create_access_token
    token = create_access_token(data={
        "sub": "t123",
        "username": "teacher",
        "memberships": [{"institution_id": "DEMO2026", "role": "TEACHER"}]
    })
    
    # 3MB + 1 byte
    giant_string = "A" * (MAX_BASE64_LENGTH + 1)
    
    res = client.post(
        "/api/v1/attendance/mark-attendance", 
        json={"frame": giant_string},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert res.status_code == 422
