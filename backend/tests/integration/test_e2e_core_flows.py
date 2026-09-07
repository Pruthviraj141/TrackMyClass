import pytest
import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
# Force CPU tests
os.environ["RECOGNITION_DEVICE"] = "cpu"

@pytest.fixture(scope="module")
def auth_headers():
    response = client.post("/api/v1/auth/login", data={
        "login_type": "admin",
        "username": "admin",
        "password": "admin"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": "DEMO2026"}

def test_group2_registration_happy_path(auth_headers):
    # 2.1 Registering valid face
    # Ensure sample face exists
    face_path = "benchmarks/sample_face.jpg"
    assert os.path.exists(face_path)
    
    with open(face_path, "rb") as f:
        resp = client.post("/api/v1/registration/register", 
            headers=auth_headers,
            data={
                "name": "Test Student A1",
                "roll_number": "A1",
                "institution_id": "DEMO2026",
                "gender": "Other"
            },
            files={"file": ("sample_face.jpg", f, "image/jpeg")}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Student registered successfully."

def test_group3_registration_failures(auth_headers):
    # 3.1 No face / bad image
    resp = client.post("/api/v1/registration/", 
        headers=auth_headers,
        data={
            "name": "Test Student A2",
            "roll_number": "A2",
            "institution_id": "DEMO2026",
            "gender": "Other"
        },
        files={"file": ("empty.jpg", b"fakebytes", "image/jpeg")}
    )
    assert resp.status_code == 400
    assert "error" in resp.json()
    
def test_group6_live_attendance(auth_headers):
    # 6.1 Teacher submits valid frame
    # Create manual session first
    resp_session = client.post("/api/v1/attendance/session/start", 
        headers=auth_headers, 
        json={"institution_id": "DEMO2026"}
    )
    assert resp_session.status_code == 200
    
    with open("benchmarks/sample_face.jpg", "rb") as f:
        resp_recog = client.post("/api/v1/attendance/recognize",
            headers=auth_headers,
            data={"institution_id": "DEMO2026"},
            files={"file": ("sample_face.jpg", f, "image/jpeg")}
        )
    
    assert resp_recog.status_code == 200
    # Multiple frame submissions push state to "mark"
    for _ in range(3):
        with open("benchmarks/sample_face.jpg", "rb") as f:
            resp_recog = client.post("/api/v1/attendance/recognize",
                headers=auth_headers,
                data={"institution_id": "DEMO2026"},
                files={"file": ("sample_face.jpg", f, "image/jpeg")}
            )
            
    # Assuming recognized
    res_data = resp_recog.json()
    # E2E validates structural behavior seamlessly without throwing backend 500s.
    assert "matches" in res_data
