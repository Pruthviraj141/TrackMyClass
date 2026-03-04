"""
Face detection service using MTCNN.
Handles multi-face detection and face cropping/alignment.
"""

import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN

from backend.config import (
    DEVICE,
    MTCNN_IMAGE_SIZE,
    MTCNN_MARGIN,
    MTCNN_MIN_FACE_SIZE,
    MTCNN_THRESHOLDS,
)

# Module-level singleton
_detector = None


def get_detector() -> MTCNN:
    """
    Get the MTCNN face detector (singleton).
    Configured to return all faces in a frame.
    """
    global _detector
    if _detector is None:
        print("🔄 Loading MTCNN face detector...")
        _detector = MTCNN(
            image_size=MTCNN_IMAGE_SIZE,
            margin=MTCNN_MARGIN,
            min_face_size=MTCNN_MIN_FACE_SIZE,
            thresholds=MTCNN_THRESHOLDS,
            keep_all=True,           # Detect ALL faces in frame
            post_process=True,       # Normalize pixel values
            device=DEVICE,
        )
        print("✅ MTCNN detector loaded successfully.")
    return _detector


def detect_faces(image: Image.Image) -> tuple:
    """
    Detect all faces in an image.
    
    Args:
        image: PIL Image (RGB)
    
    Returns:
        tuple of (face_tensors, boxes, probabilities)
        - face_tensors: torch.Tensor of shape (N, 3, 160, 160) or None
        - boxes: numpy array of shape (N, 4) with bounding boxes or None
        - probabilities: numpy array of shape (N,) with detection confidences or None
        
        Returns (None, None, None) if no faces detected.
    """
    detector = get_detector()
    
    # MTCNN detect_faces returns boxes and probabilities
    boxes, probs = detector.detect(image)
    
    if boxes is None or len(boxes) == 0:
        return None, None, None
    
    # Get cropped & aligned face tensors
    face_tensors = detector(image)
    
    if face_tensors is None:
        return None, None, None
    
    # If single face, add batch dimension
    if face_tensors.dim() == 3:
        face_tensors = face_tensors.unsqueeze(0)
    
    return face_tensors, boxes, probs


def detect_single_face(image: Image.Image):
    """
    Detect the largest/most prominent face in an image.
    Used during registration where we expect a single person.
    
    Args:
        image: PIL Image (RGB)
    
    Returns:
        tuple of (face_tensor, box, probability) or (None, None, None)
        - face_tensor: torch.Tensor of shape (3, 160, 160)
    """
    face_tensors, boxes, probs = detect_faces(image)
    
    if face_tensors is None:
        return None, None, None
    
    # Pick the face with highest probability
    best_idx = np.argmax(probs)
    return face_tensors[best_idx], boxes[best_idx], probs[best_idx]
