# TARGET ARCHITECTURE

As part of the Phase 1 effort to establish strict logical boundaries, TrackMyClass will shift from a monolithic router-centric pattern to a layered application domain.

## 1. API Layer
**Location:** `backend/api/`
- Only manages parsing inbound HTTP models, executing dependency injections via FastAPI `Depends`, returning proper HTTP Codes (`200 OK`, `400 Bad Request`), and managing exceptions mapped from the Core domain.
- **Rule**: Absolutely no database logic, temporal logic, or vector generation is present here.

## 2. Application Layer
**Location:** `backend/application/`
- Houses Use Case logic. Controls the orchestration between ML Engines and Repositories.
- Example: `AttendanceService.mark_frame()` receives a generic session ID and a byte array. It requests the Engine to inspect the byte array and requests the DB Repository to log the verified results.

## 3. Domain Layer
**Location:** `backend/domain/`
- Standard native Python objects representing the core business schema without dependencies on FastAPI or SQLite mapping frameworks.
- Example: `entities.Student()`, `entities.Session()`, `value_objects.RecognitionResult()`.

## 4. ML Layer (Recognition Engine)
**Location:** `backend/ml/`
- Purely functional implementation of FaceNet and MTCNN handling raw PyTorch iterations and multi-face batch detections.
- Defines a single integration interface `RecognitionEngine` exposing `.process_frame()`.
- Internals (`temporal_tracker`, vector matrix caches) hide their stateful loops inside this boundary away from HTTP workers.

## 5. Infrastructure Layer
**Location:** `backend/infrastructure/`
- `repositories/`: Database IO using explicit contracts mapped from SQLite and Firebase.
- Will eventually handle Background Async IO or external service storage mechanisms.

## Next Phase Transitions
We are explicitly **avoiding** multi-process queues (Celery/Kafka) acting between the Application layer and the ML Engine in Phase 1 to preserve behavior seamlessly. The invocation of Engine operations retains the same `async`/`sync` threading properties until Phase 2-4 optimization.
