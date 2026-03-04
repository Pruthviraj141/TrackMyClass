"""
Centralized configuration for the attendance system.
All settings, thresholds, and paths are defined here.
Secrets and environment-specific values are loaded from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ──────────────────────────────────────────────
# Load .env file
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent  # backend/
ATTENDANCE_SYSTEM_DIR = BASE_DIR.parent     # attendance_system/
PROJECT_ROOT = BASE_DIR.parent.parent       # d:\DEEP learning attandace system\

# Load .env from attendance_system/ directory
_env_path = ATTENDANCE_SYSTEM_DIR / ".env"
load_dotenv(dotenv_path=_env_path)

# ──────────────────────────────────────────────
# Admin Credentials (from .env)
# ──────────────────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# ──────────────────────────────────────────────
# Session Security (from .env)
# ──────────────────────────────────────────────
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "change-me-to-a-random-string-in-production")

# ──────────────────────────────────────────────
# Path Configuration
# ──────────────────────────────────────────────
# Firebase service account key
_firebase_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "../firebase.json")
if os.path.isabs(_firebase_path):
    FIREBASE_CREDENTIALS_PATH = Path(_firebase_path)
else:
    FIREBASE_CREDENTIALS_PATH = (ATTENDANCE_SYSTEM_DIR / _firebase_path).resolve()

# SQLite fallback database path
SQLITE_DB_PATH = BASE_DIR / "database" / "attendance.db"

# Frontend paths
TEMPLATES_DIR = ATTENDANCE_SYSTEM_DIR / "frontend" / "templates"
STATIC_DIR = ATTENDANCE_SYSTEM_DIR / "frontend" / "static"

# ──────────────────────────────────────────────
# Deep Learning Settings (from .env with defaults)
# ──────────────────────────────────────────────
DEVICE = os.getenv("DEVICE", "cpu")  # Phase-1: CPU only

# MTCNN face detection thresholds
MTCNN_IMAGE_SIZE = 160        # Face crop size for FaceNet input
MTCNN_MARGIN = 20             # Margin around detected face (pixels)
MTCNN_MIN_FACE_SIZE = 40      # Minimum face size to detect (pixels)
MTCNN_THRESHOLDS = [0.6, 0.7, 0.7]  # P-Net, R-Net, O-Net thresholds

# FaceNet embedding
EMBEDDING_DIM = 512           # InceptionResnetV1 output dimension
FACENET_PRETRAINED = "vggface2"

# ──────────────────────────────────────────────
# Recognition Settings
# ──────────────────────────────────────────────
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.80"))
TOP_K_MATCHES = 1             # Return top-K matches (1 for Phase-1)

# ──────────────────────────────────────────────
# Registration Settings
# ──────────────────────────────────────────────
REGISTRATION_DURATION_SEC = 30    # Duration of video capture for registration
FRAME_CAPTURE_INTERVAL_SEC = 1.0  # Capture a frame every N seconds
MIN_FRAMES_REQUIRED = 5          # Minimum frames needed for valid registration
MAX_FRAME_SIZE_BYTES = 500 * 1024  # 500 KB max per frame

# ──────────────────────────────────────────────
# Session Management Settings
# ──────────────────────────────────────────────
SESSION_COOLDOWN_MINUTES = 5      # Ignore a student for N minutes after marking

# ──────────────────────────────────────────────
# Temporal Tracking Settings
# ──────────────────────────────────────────────
TEMPORAL_MIN_FRAMES = 4           # Must be seen in ≥ N frames before marking (~2s at 2FPS)
TEMPORAL_MIN_CONFIDENCE = 0.80    # Average confidence across tracked frames
TEMPORAL_TOLERANCE_MISSES = 1     # Allow N consecutive missed frames before reset
TEMPORAL_CLEANUP_SECONDS = 3.0    # Remove from buffer if unseen for N seconds

# ──────────────────────────────────────────────
# CPU Optimization Settings
# ──────────────────────────────────────────────
FRAME_RESIZE_WIDTH = 640          # Resize frame width before detection
SKIP_DETECTION_FRAMES = False     # If True, run MTCNN every alternate frame

# ──────────────────────────────────────────────
# API Settings (from .env)
# ──────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
_cors_origins = os.getenv("CORS_ORIGINS", "*")
CORS_ORIGINS = [origin.strip() for origin in _cors_origins.split(",")]

# ──────────────────────────────────────────────
# Database Mode Detection
# ──────────────────────────────────────────────
def get_database_mode() -> str:
    """
    Determine which database backend to use.
    Returns 'firebase' if credentials exist and are valid, else 'sqlite'.
    """
    import firebase_admin
    from firebase_admin import credentials
    import json
    
    firebase_json_env = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if firebase_json_env:
        try:
            cred_dict = json.loads(firebase_json_env)
            cred = credentials.Certificate(cred_dict)
            try:
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app(cred)
            return "firebase"
        except Exception as e:
            print(f"⚠️  Firebase JSON env setup failed: {e}")
            print("↪  Falling back to SQLite database.")
            return "sqlite"
    elif FIREBASE_CREDENTIALS_PATH.exists():
        try:
            cred = credentials.Certificate(str(FIREBASE_CREDENTIALS_PATH))
            # Check if already initialized
            try:
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app(cred)
            return "firebase"
        except Exception as e:
            print(f"⚠️  Firebase setup failed: {e}")
            print("↪  Falling back to SQLite database.")
            return "sqlite"
    else:
        print("⚠️  firebase.json not found and FIREBASE_CREDENTIALS_JSON env variable not set.")
        print("↪  Using SQLite database.")
        return "sqlite"

# Resolve database mode at import time
DATABASE_MODE = get_database_mode()
print(f"✅ Database mode: {DATABASE_MODE}")
