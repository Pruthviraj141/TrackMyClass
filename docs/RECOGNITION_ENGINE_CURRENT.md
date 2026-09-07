# Recognition Engine Baseline (Pre-Phase 3)

## Current Architecture
The `backend/ml/engine.py` component currently orchestrates execution structurally decoupled from Web routers.
1. Takes pre-decoded `PIL.Image` objects implicitly.
2. Extracts boundaries `(tensors, bounds, probability)` natively via `facenet_pytorch.MTCNN`.
3. Processes bounds linearly in a `for` loop converting crops to 512-dim floats via `facenet_pytorch.InceptionResnetV1`.
4. Attempts math mapping utilizing a raw Cache layer natively extracting Euclidean/Cosine matches.
5. Injects candidate responses into `TemporalTracker` matching states across 4 consecutive identical frames implicitly producing tracking outputs.

## Missing Contracts
- Raw Tensors leak across API boundaries un-typed.
- Numpy matrices are extracted sequentially implicitly without batching logic causing potential iteration bottlenecking on multi-face images.
- Cache lifecycle ignores `institution_id` invalidations efficiently relying on manual resets via legacy `AttendanceService`.
- Lacks strict Separation between Math `distance < x` and actual "Identity Decision". Distance alone isn't always proof of explicit recognition depending strictly on cluster distributions. 

## Device Management
- Implicitly falls back natively without strict configurations on GPU/CPU targeting logic allowing PyTorch to grab unpredictable constraints.
- No `torch.inference_mode()` context wrappers surrounding predictions leading to potential memory gradient leaking over long sessions permanently exhausting RAM dynamically.
