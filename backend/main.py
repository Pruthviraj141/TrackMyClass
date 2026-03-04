"""
FastAPI Application Entry Point.
Mounts routers, static files, and serves HTML templates.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import CORS_ORIGINS, TEMPLATES_DIR, STATIC_DIR
from backend.routers import registration, attendance, auth_router, admin_router, student_router
from backend.auth import get_current_user


# ──────────────────────────────────────────────
# Lifespan: preload models on startup
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preload ML models and caches on startup for faster first request."""
    print("=" * 60)
    print("🚀 Starting Face Recognition Attendance System")
    print("=" * 60)
    
    # Preload MTCNN and FaceNet models
    from backend.services.face_detection import get_detector
    from backend.models.facenet_model import get_facenet_model
    
    get_detector()
    get_facenet_model()
    
    # Initialize services
    from backend.services.session_service import get_session_manager
    from backend.services.temporal_tracker import get_tracker
    from backend.services.optimized_recognition import get_embedding_cache
    
    get_session_manager()
    get_tracker()
    cache = get_embedding_cache()
    cache.load()  # Preload student embeddings
    
    print("=" * 60)
    print("✅ System ready! Open http://localhost:8000 in your browser.")
    print("=" * 60)
    
    yield  # App runs here
    
    # Cleanup: end any active session
    mgr = get_session_manager()
    if mgr.get_active_session():
        mgr.end_session()
    
    print("👋 Shutting down attendance system.")


# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────

app = FastAPI(
    title="Face Recognition Attendance System",
    description="Phase-1: Deep Learning attendance system using MTCNN + FaceNet",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API routers
app.include_router(registration.router)
app.include_router(attendance.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(student_router.router)


# ──────────────────────────────────────────────
# Page Routes
# ──────────────────────────────────────────────

@app.get("/")
async def registration_page(request: Request):
    """Serve the student registration page (public)."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/monitor")
async def monitoring_page(request: Request):
    """Serve the live monitoring page (admin-only)."""
    from fastapi.responses import RedirectResponse
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("monitor.html", {"request": request})

