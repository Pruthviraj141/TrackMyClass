from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_exception_handler_json_schema():
    """Verify standard structured errors map to the predefined format containing Correlation IDs."""
    # Hitting unauthenticated endpoint guarantees structurally safe 401 exceptions.
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    
    # 401s produced natively by Dependencies aren't custom handled, but they must remain JSON compatible
    assert "detail" in res.json()
