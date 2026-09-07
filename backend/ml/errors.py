"""
Recognition Error Taxonomy.
Isolates Internal ML bugs mathematically away from API/FastAPI context leaks.
"""

class RecognitionError(Exception):
    """Base exception for all internal Computer Vision errors."""
    pass

class RecognitionInputError(RecognitionError):
    """Triggered when an image explicitly violates shape/size processing checks."""
    pass

class FaceDetectionError(RecognitionError):
    """Triggered when MTCNN execution fails explicitly on tensor extraction."""
    pass

class EmbeddingGenerationError(RecognitionError):
    """Triggered when PyTorch Graph memory or mapping strictly fails during conversion."""
    pass

class ModelUnavailableError(RecognitionError):
    """Triggered when CUDA or CPU fallback parameters are exhausted on load."""
    pass

class MatchingError(RecognitionError):
    """Triggered when Numpy Euclidean boundaries fail on structural mismatches."""
    pass

class TrackingError(RecognitionError):
    """Triggered by broken frame IDs entering the Temporal tracker blindly."""
    pass
