"""
Face detection service using MTCNN.
Handles multi-face detection and face cropping/alignment.
"""
from typing import List, Optional
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN

from backend.core.config import (
    MTCNN_IMAGE_SIZE,
    MTCNN_MARGIN,
    MTCNN_MIN_FACE_SIZE,
    MTCNN_THRESHOLDS,
)
from backend.ml.config import RECOGNITION_DEVICE as DEVICE
from backend.ml.domain import FaceDetectionResult

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


def detect_faces(image: Image.Image) -> List[FaceDetectionResult]:
    """
    Detect all faces in an image natively wrapped with domain limits.
    """
    detector = get_detector()
    
    with torch.inference_mode():
        boxes, probs = detector.detect(image)
        
        if boxes is None or len(boxes) == 0:
            return []
        
        face_tensors = detector(image)
        
    if face_tensors is None:
        return []
        
    if face_tensors.dim() == 3:
        face_tensors = face_tensors.unsqueeze(0)
        
    results = []
    for i in range(len(face_tensors)):
        results.append(
            FaceDetectionResult(
                bounding_box=boxes[i].tolist(),
                detection_confidence=float(probs[i]),
                face_crop_tensor=face_tensors[i]
            )
        )
    return results


def detect_single_face(image: Image.Image) -> Optional[FaceDetectionResult]:
    """
    Detect the most prominent face natively extracting a single Domain construct.
    """
    faces = detect_faces(image)
    if not faces:
        return None
        
    # Pick face with highest detection probability
    best_face = max(faces, key=lambda f: f.detection_confidence)
    return best_face
