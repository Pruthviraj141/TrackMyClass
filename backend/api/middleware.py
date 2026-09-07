import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api.rate_limiting import apply_rate_limit

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or pass through correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # Attach to request state for downstream loggers
        request.state.correlation_id = correlation_id
        
        # Throw 429 safely stopping internal processing
        try:
            await apply_rate_limit(request)
        except Exception as e:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=429, content={"error": {"code": "TOO_MANY_REQUESTS", "message": "Rate limit exceeded"}})

        # Process the pipeline
        response = await call_next(request)
        
        # Ensure client receives it back
        response.headers["X-Correlation-ID"] = correlation_id
        return response
