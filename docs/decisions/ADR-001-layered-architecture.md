# ADR 001: Layered Architecture Refactoring

## Context
TrackMyClass originally possessed a monolithic router setup. The CPU-bound Machine Learning logic (PyTorch/FaceNet iteration) was directly coupled into the FastAPI request parsers.

## Problem
Processing tensors inside a synchronous Web Route blocks ASGI event loops causing extreme scaling deficiencies, destroying unit-testability since components couldn't be evaluated cleanly without HTTP scopes.

## Decision
We implemented a strict layered architecture in Phase 1:
- `backend/core`: Native python types.
- `backend/domain`: Clean entity representations (e.g. `Student`, `RecognitionResult`).
- `backend/infrastructure`: Repository mappings hiding Firebase/SQLite toggles.
- `backend/ml`: The core Inference logic completely extracted under `RecognitionEngine`.
- `backend/application`: Services manipulating Domain abstractions and ML boundaries without touching HTTP details.
- `backend/api/routes`: Decoupled lightweight endpoints solely mapping HTTP into Domain models.

## Documenting CPU-Bound Inference (Step 11)
**Crucial Architectural Note**: Extracting the CPU-heavy inference (`mark_attendance()`) into the `RecognitionEngine` explicitly isolated the logic effectively. However, the top-level API router ultimately invokes the Application Service synchronously currently because PyTorch MTCNN is inherently a CPU blocking execution flow stringing together tensor computations. This explicitly means that although boundaries are perfectly established, calling `.process_frame()` *still functionally blocks the local thread execution*. 
We are not utilizing async worker threads or multi-process offloading (Kafka/Celery) in Phase 1 per constraints. This will be the priority in a later performance phase.

## Alternatives Considered
- Introducing Background Workers immediately: Rejected as Phase 1 constrained major architectural topology jumps beyond logic isolation.

## Decision rationale
By doing zero backend database modifications and sticking strictly to logical module decoupling via standard Python namespaces, we can establish tests to verify isolation while guaranteeing backwards compatibility across the old React UI flawlessly.
