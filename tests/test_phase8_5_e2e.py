import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import create_access_token
from backend.domain.identity import User, InstitutionMembership, Role
from datetime import timedelta
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Helper to generate mock tokens efficiently without full Firebase auth roundtrips globally during profiling
def encode_mock_token(user_id: str, username: str, inst_id: str, role: Role):
    return create_access_token(data={
        "sub": user_id,
        "username": username,
        "memberships": [{"institution_id": inst_id, "role": role.value}]
    }, expires_delta=timedelta(minutes=10))

def test_student_workflow_rbac_rejections():
    # Student attempts teacher routes natively
    st_token = encode_mock_token("ST_1", "student@demo.com", "DEMO2026", Role.STUDENT)
    headers = {"Authorization": f"Bearer {st_token}"}
    
    res = client.get("/api/v1/students", headers=headers)
    assert res.status_code == 403 # Only Teacher / Inst Admin

def test_teacher_workflow():
    tc_token = encode_mock_token("TC_1", "teacher@demo.com", "DEMO2026", Role.TEACHER)
    headers = {"Authorization": f"Bearer {tc_token}"}
    
    # Can access directory
    res = client.get("/api/v1/students", headers=headers)
    assert res.status_code == 200
    
    # Session lifecycle verification
    res = client.post("/api/v1/attendance/session/start", json={"subject_name": "CS101"}, headers=headers)
    assert res.status_code == 200
    assert "session_id" in res.json()["session"]
    
    res = client.post("/api/v1/attendance/session/end", headers=headers)
    assert res.status_code == 200

def test_cross_tenant_boundaries_forbidden():
    tc_token_other = encode_mock_token("OTHER_1", "evil@other.com", "OTHER_INST", Role.TEACHER)
    headers = {"Authorization": f"Bearer {tc_token_other}"}
    
    # Should get isolated lists, not DEMO2026
    res = client.get("/api/v1/students", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) == 0 # Clean db for OTHER_INST
    
def test_diagnostics_overhead():
    # Ping diagnostics route
    res = client.get("/api/v1/diagnostics/metrics")
    assert res.status_code == 200
    assert "status" in res.json()
