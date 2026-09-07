"""
Integration tests for WebSocket authentication and authorization.

These use starlette's TestClient with WebSocket support.
They test the auth/authz boundaries WITHOUT requiring a real inference worker.
"""
import pytest
import jwt as pyjwt
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.security import SECRET_KEY, ALGORITHM


def _make_token(user_id: str, institution_id: str, role: str = "INSTITUTION_ADMIN") -> str:
    from backend.core.security import create_access_token
    return create_access_token(data={
        "sub": user_id,
        "username": "testuser",
        "memberships": [{"institution_id": institution_id, "role": role}],
    })


SESSION_ID = "test-session-abc"


class TestWSAuthentication:
    """WebSocket connections must be authenticated before any frame is processed."""

    def test_no_token_closes_with_error(self):
        client = TestClient(app)
        with client.websocket_connect(f"/api/v1/ws/monitor/{SESSION_ID}") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "error"
            assert msg["code"] == 4001

    def test_invalid_token_closes_with_error(self):
        client = TestClient(app)
        with client.websocket_connect(
            f"/api/v1/ws/monitor/{SESSION_ID}?token=not_a_real_jwt"
        ) as ws:
            msg = ws.receive_json()
            assert msg["type"] == "error"
            assert msg["code"] == 4001

    def test_expired_token_closes_with_error(self):
        """A manually crafted expired token should be rejected."""
        import time
        expired_payload = {
            "sub": "user123",
            "username": "admin",
            "memberships": [{"institution_id": "DEMO2026", "role": "INSTITUTION_ADMIN"}],
            "exp": int(time.time()) - 3600,  # expired 1 hour ago
        }
        expired_token = pyjwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        client = TestClient(app)
        with client.websocket_connect(
            f"/api/v1/ws/monitor/{SESSION_ID}?token={expired_token}"
        ) as ws:
            msg = ws.receive_json()
            assert msg["type"] == "error"
            assert msg["code"] == 4001


class TestWSAuthorization:
    """Session must belong to the connecting user's institution."""

    def test_no_active_session_closes_with_4004(self):
        """Connect with a valid token but no session started → 4004."""
        token = _make_token("admin1", "NOINST999")
        client = TestClient(app)
        with client.websocket_connect(
            f"/api/v1/ws/monitor/{SESSION_ID}?token={token}"
        ) as ws:
            msg = ws.receive_json()
            assert msg["type"] == "error"
            assert msg["code"] in (4004, 4003)

    def test_forged_session_id_rejected(self):
        """Token for DEMO2026 trying to connect to a different session → 4003."""
        token = _make_token("admin2", "DEMO2026")
        # Start a real session for DEMO2026
        from backend.services.session_service import get_session_manager
        mgr = get_session_manager()
        real_session = mgr.start_session("DEMO2026", "Test Subject")

        # Try to join with a FORGED session_id
        forged_id = "00000000-0000-0000-0000-000000000000"
        client = TestClient(app)
        with client.websocket_connect(
            f"/api/v1/ws/monitor/{forged_id}?token={token}"
        ) as ws:
            msg = ws.receive_json()
            assert msg["type"] == "error"
            assert msg["code"] == 4003

        mgr.end_session("DEMO2026")
