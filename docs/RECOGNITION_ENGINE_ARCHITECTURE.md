# Recognition Engine Architecture

## Component Separation
Phase 3 fundamentally decoupled the Computer Vision PyTorch logic natively from Web frameworks ensuring stateless, domain-typed bounded executions structurally verified entirely out of scope.

```mermaid
flowchart TD
    A[app/attendance.py] -->|PIL.Image| B(RecognitionEngine)
    B --> C[detect_faces]
    C -->|List[FaceDetectionResult]| D[generate_embedding]
    D -->|List[Embedding]| E(VectorMatcher)
    E -->|MatchResult * Vector Math| F{TemporalTracker}
    F -->|Stability Analysis| G(RecognitionResult)
    G --> A
```

## Boundaries
1. **PyTorch Leaks**: Tensors are implicitly destroyed directly inside `generate_embedding()` preventing Web Application routers from hoarding Memory Pointers infinitely causing RAM exhaustion crashes.
2. **Batch Inference**: Embeddings rely implicitly on strict Matrix shapes `[B, 3, 160, 160]`. Loops execute efficiently without blocking the AST pipeline natively.
3. **Temporal States**: `TemporalTracker` buffers identity transitions requiring identical boxes scaling `TEMPORAL_MIN_FRAMES` to output securely preventing single-frame False Positives securely bounding "Identity Switches".
