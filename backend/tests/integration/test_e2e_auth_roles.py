import pytest
import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_group1_admin_auth_success():
    # 1.1 Valid credentials
    response = client.post("/api/v1/auth/login", data={
        "login_type": "admin",
        "username": "admin",
        "password": "password"  # Default test password
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    
def test_group1_admin_auth_failure():
    # 1.2 Invalid password
    response = client.post("/api/v1/auth/login", data={
        "login_type": "admin",
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    
    # 1.3 Unknown account
    response = client.post("/api/v1/auth/login", data={
        "login_type": "admin",
        "username": "nobody",
        "password": "password"
    })
    assert response.status_code == 401

def test_group19_role_enforcement():
    # Attempting to hit an auth-protected route without tokens
    resp = client.get("/api/v1/institutions/")
    assert resp.status_code == 401
