# Dependency Map (Phase 1)

## Current Coupling
- **API <-> ML Inference**: The `backend/routers/attendance.py` and `registration.py` directly import and execute `detect_faces()` and `generate_embedding()`. This intrinsically binds HTTP context (`Request`, Base64 decoding, Resizing) with heavy PyTorch math execution on the same thread.
- **API <-> Tracking/Cache**: Router endpoints directly mutate `StudentEmbeddingCache` and `TemporalTracker` states.
- **Services <-> Configuration**: Nearly all files import implicitly from `backend.config.py` including structural toggles like `DATABASE_MODE`.
- **Database <-> Global Config**: `sqlite_service.py` is invoked statically instead of dependency injection through `Depends()`.

## High-Risk Modules
1. `backend/routers/attendance.py`: Contains >350 lines combining decoding, detection, embedding math iteration, tracking buffer mutations, AND persistence logic in a single function (`mark_attendance`).
2. `backend/services/optimized_recognition.py`: Manages the Numpy float matrix cache. It is stateful singleton logic that can OOM (out-of-memory) if heavily spammed or unloaded.
3. `backend.database.firebase_service`/`sqlite_service`: Directly bound inside functions via runtime `if DATABASE_MODE == "firebase"` evaluated inside routers. They are not interfaces.

## Candidates for Extraction
1. **RecognitionEngine**: Creating an abstraction that perfectly receives a raw image and returns `RecognitionResult` containing the `Matched Student` and `Confidence`, isolating FaceNet/MTCNN from the application logic entirely.
2. **Repositories**: Moving `sqlite_service.py` into `Infrastructure -> Database` that maps into an `AttendanceRepository`, breaking direct usage of `add_attendance(..., confidence=)` inside `mark_attendance`.
3. **ApplicationServices**: Creating an `AttendanceAppService` which receives the `frame`, invokes `RecognitionEngine`, pulls the session context, updates tracker, and commands the `AttendanceRepository`.

## Modules to Remain Untouched
We do not intend to modify `frontend/` components during Phase 1 except endpoints if they change formats (though we intend to keep API interfaces identically backwards compatible per instructions). We also will leave `facenet_model.py` and PyTorch parameters untouched, merely wrapping them.
