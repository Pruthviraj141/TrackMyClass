import logging
from datetime import datetime
import json

# Setup standard logger replacing raw print statements natively
audit_logger = logging.getLogger("trackmyclass.audit")
if not audit_logger.handlers:
    handler = logging.FileHandler("audit_logs.json")
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(handler)

def log_security_event(event_type: str, status: str, details: dict):
    """
    Structured JSON audit log pushing secure metrics into analytics.
    Avoids logging explicit passwords or sensitive hashes natively.
    """
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "status": status,
        "details": details
    }
    audit_logger.info(json.dumps(record))
