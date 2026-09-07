import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.core.config import CORS_ORIGINS, TEMPLATES_DIR, STATIC_DIR
from backend.api.routes import (
    registration,
    attendance,
    auth_router,
    admin_router,
    student_router,
    institution_router,
    diagnostics
)
from backend.auth import get_current_user
from backend.ml.detector.face_detection import get_detector
from backend.ml.embedding.facenet_model import get_facenet_model
from contextlib import asynccontextmanager

from backend.api.ws import monitor_ws
from backend.worker.worker_manager import get_worker_manager
from backend.core.redis_client import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload ML models in the main process (warm-up the singletons)
    print("Loading AI Models into memory...")
    get_detector()
    get_facenet_model()
    print("AI Models Ready.")

    # Start the inference worker process
    loop = asyncio.get_event_loop()
    worker_mgr = get_worker_manager()
    worker_mgr.start(loop)
    print("Inference worker started.")
    
    # Init Distributed State (Redis)
    await init_redis()

    yield

    worker_mgr.stop()
    await close_redis()
    print("Shutting down Application Layer.")


from backend.api.middleware import RequestContextMiddleware
from fastapi.responses import JSONResponse
from backend.core.errors import TrackMyClassError
from fastapi.exceptions import RequestValidationError
import traceback

app = FastAPI(title="TrackMyClass", version="1.0.0", lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(RequestContextMiddleware)

@app.exception_handler(TrackMyClassError)
async def domain_error_handler(request: Request, exc: TrackMyClassError):
    # Logs internal causes if chained via 'from e' safely inside backend logs.
    print(f"[Error: {request.state.correlation_id}] Domain Exception: {exc}")
    if exc.__cause__:
        print(f"Caused by: {exc.__cause__}") 
        
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.__class__.__name__,
                "message": str(exc),
                "request_id": getattr(request.state, "correlation_id", "unknown")
            }
        }
    )

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return await http_exception_handler(request, exc)
        
    print(f"[Error: {request.state.correlation_id}] Unhandled Exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred processing the request.",
                "request_id": getattr(request.state, "correlation_id", "unknown")
            }
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(registration.router)
app.include_router(attendance.router)
app.include_router(admin_router.router)
app.include_router(student_router.router)
app.include_router(institution_router.router)
app.include_router(diagnostics.router)
app.include_router(monitor_ws.router)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
