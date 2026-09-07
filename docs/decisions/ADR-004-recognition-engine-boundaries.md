# ADR-004: Recognition Engine Domain Isolation

## Context
Our Core ML bindings originally consisted of nested PyTorch tuples leaking raw mathematical Tensors directly into arbitrary FastAPI dependencies resulting in loose structures and heavy structural coupling preventing simple profiling isolation.

## Decision
We chose to execute strict Domain Typed classes globally wrapped entirely out of the FastAPI bounds (`Embedding`, `MatchResult`, `FaceDetectionResult`). The Web layer endpoints receive sanitized logic arrays strictly lacking ML Pointer logic preserving memory cleanly.

## Alternatives
We could have utilized PyDantic schemas across the core endpoints mapping the logic universally into JSON immediately, however that generates massive string conversion overhead causing internal ML operations to execute slowly blocking frame processors explicitly. Standard pure python dataclass domains keep CPU buffers low securely.

## Consequences
- Requires mapping logic explicitly bridging out inside the Engine `process_frame`.
- PyTorch logic is fully isolated into `backend/ml/` allowing isolated PyTest blocks entirely decoupled from Database configurations natively!
