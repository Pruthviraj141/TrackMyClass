# AI Model Versioning

## Concept
Facial feature embeddings are mathematically bound directly to the exact Model, Version, and Dataset weights utilized during Extraction. Changing any component without re-computing the underlying baseline database breaks similarity matrices inherently.

## Standard Object Contract
All tensors extracted by TrackMyClass are natively coerced into the following versioned shape logic explicitly defining bounds.
```python
@dataclass
class Embedding:
    vector: np.ndarray 
    dimension: int          # e.g 512
    model_version: str      # e.g "facenet_v1"
    normalization_state: bool # True (x / ||x||)
```

## Current Configuration
### `facenet_v1`
- **Model**: `facenet_pytorch.InceptionResnetV1(pretrained='vggface2')`
- **Detector Pipeline**: `MTCNN` (Keep all faces, Pre-Processing ON)
- **Embedding Dimension**: 512
- **Vector Space**: Unit Normalized (Euclidean boundaries map to Cosine distance safely)
- **Minimum Match Threshold**: `0.75` (Optimized targeting False Acceptance avoidance)

## Migration Strategy
If TrackMyClass upgrades to a fundamentally different backbone architecture natively (e.g. ArcFace creating 512-dim or 1024-dim tensors):
1. The `model_version` tag blocks structural comparisons intrinsically.
2. The Database must be migrated structurally regenerating all original images (`frames`) backwards onto the new model.
3. Mix-and-Matching embedding configurations across one session is mathematically invalid and blocked safely by these Object definitions.
