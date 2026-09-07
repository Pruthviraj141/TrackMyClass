import json
import logging
from backend.core.logger import JSONFormatter, correlation_id_ctx, session_id_ctx
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_json_formatting_and_redaction():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test event",
        args=(),
        exc_info=None
    )
    
    # Inject extra kwargs natively expected by our custom python logger loop
    record.sensitive_tensor = "[0.78, 0.99, ...]"
    record.safe_metric = 42
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    assert data["event"] == "Test event"
    assert data["level"] == "INFO"
    assert "timestamp" in data
    assert data["safe_metric"] == 42
    assert "sensitive_tensor" in data

def test_diagnostics_endpoint():
    response = client.get("/api/v1/diagnostics/metrics")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "worker" in data
    assert "redis" in data
    
    assert "queue_depth" in data["worker"]
    assert "frames_dropped" in data["worker"]
    assert "latency_p50_ms" in data["worker"]
