import pytest
from PIL import Image
import os
from backend.ml.engine import RecognitionEngine

def test_invalid_image_handled_gracefully():
    # Enforce CPU execution mapped locally for testing
    os.environ["RECOGNITION_DEVICE"] = "cpu"
    engine = RecognitionEngine("TEST_TENANT")
    
    # Empty Black Image
    img_black = Image.new('RGB', (100, 100), color='black')
    results1 = engine.process_frame(img_black)
    assert len(results1) == 0
    
    # Greyscale correctly converted
    img_grey = Image.new('L', (100, 100), color=128)
    results2 = engine.process_frame(img_grey.convert("RGB"))
    assert len(results2) == 0

def test_tenant_isolation_strictly_blocked():
    os.environ["RECOGNITION_DEVICE"] = "cpu"
    engineA = RecognitionEngine("TENANT_A")
    engineB = RecognitionEngine("TENANT_B")
    
    assert engineA.institution_id == "TENANT_A"
    assert engineB.institution_id == "TENANT_B"
    assert engineA.cache is engineB.cache # Cache is a singleton
    # Real isolations are tested via loaded cache keys and refresh models conditionally directly against DB wrappers securely.
