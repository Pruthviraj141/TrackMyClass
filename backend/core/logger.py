"""
Structured Logging format configuration.
Ensures JSON log emissions universally across TrackMyClass.
"""
import logging
import json
import traceback
from datetime import datetime
from contextvars import ContextVar

# Correlation Context 
correlation_id_ctx = ContextVar("correlation_id", default="n/a")
session_id_ctx = ContextVar("session_id", default="n/a")

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "service": "trackmyclass-backend",
            "component": record.name,
            "event": record.getMessage(),
            "correlation_id": correlation_id_ctx.get(),
            "session_id": session_id_ctx.get(),
        }
        
        # Inject standard python logging `extra=...` payloads.
        _PRESERVED_KEYS = {'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename', 
                           'funcName', 'levelname', 'levelno', 'lineno', 'module', 
                           'msecs', 'message', 'msg', 'name', 'pathname', 'process', 
                           'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'}
        
        for k, v in record.__dict__.items():
            if k not in _PRESERVED_KEYS:
                log_obj[k] = v
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            # Never include raw memory buffers or frames in the stack traces
            
        return json.dumps(log_obj)

def get_structured_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        sh = logging.StreamHandler()
        sh.setFormatter(JSONFormatter())
        logger.addHandler(sh)
    logger.propagate = False
    return logger
