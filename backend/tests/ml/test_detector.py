import pytest
from PIL import Image
from backend.ml.detector.face_detection import detect_faces

def test_detect_zero_faces_malformed():
    # A pure black image has no faces
    img = Image.new('RGB', (160, 160), color='black')
    results = detect_faces(img)
    assert len(results) == 0

def test_detect_graceful_small_image():
    # Extremely small image, no faces possible
    img = Image.new('RGB', (10, 10), color='white')
    results = detect_faces(img)
    assert len(results) == 0
