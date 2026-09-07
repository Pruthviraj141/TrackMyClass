from dataclasses import dataclass
from typing import List, Tuple, Any, Optional

@dataclass
class FaceDetectionResult:
    bounding_box: List[float]
    detection_confidence: float
    face_crop_tensor: Any  # torch.Tensor representation (Kept structurally isolated from Web bounds)

@dataclass
class Embedding:
    vector: Any  # Raw numpy array
    dimension: int
    model_version: str
    normalization_state: bool

@dataclass
class MatchResult:
    candidate_identity: str
    similarity: float
    threshold_applied: float
    is_accepted: bool

@dataclass
class TemporalVerificationResult:
    identity: str
    stability_score: int
    consecutive_observations: int
    is_verified: bool

@dataclass
class RecognitionResult:
    student_id: str
    name: str
    bounding_box: List[float]
    similarity: float
    recognition_state: str  # 'unknown', 'candidate', 'stable', etc.
    verification_state: bool
