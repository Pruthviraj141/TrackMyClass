"""
FaceNet model loader.
Provides a singleton InceptionResnetV1 model pretrained on VGGFace2.
"""

import torch
from facenet_pytorch import InceptionResnetV1

from backend.config import DEVICE, FACENET_PRETRAINED

# Module-level singleton
_model = None


def get_facenet_model() -> InceptionResnetV1:
    """
    Load and return the FaceNet model (singleton).
    
    The model is loaded once and cached for subsequent calls.
    Uses InceptionResnetV1 pretrained on VGGFace2 dataset.
    Outputs 512-dimensional embeddings.
    
    Returns:
        InceptionResnetV1 model in eval mode on the configured device
    """
    global _model
    if _model is None:
        print("🔄 Loading FaceNet model (InceptionResnetV1 / VGGFace2)...")
        _model = InceptionResnetV1(pretrained=FACENET_PRETRAINED).eval().to(DEVICE)
        print("✅ FaceNet model loaded successfully.")
    return _model
