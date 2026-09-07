"""
Recognition Engine
A pure wrapper encapsulating ML Detection, Extraction, Matching, and Tracking via Domain constraints.
"""
from typing import List, Optional
from PIL import Image

from backend.ml.domain import RecognitionResult, FaceDetectionResult, MatchResult, TemporalVerificationResult
from backend.ml.detector.face_detection import detect_faces
from backend.ml.embedding.embedding_service import generate_embedding
from backend.ml.matcher.optimized_recognition import get_embedding_cache
from backend.ml.tracker.temporal_tracker import get_tracker
from backend.core.logger import get_structured_logger
import time

logger = get_structured_logger(__name__)


class RecognitionEngine:
    
    def __init__(self, institution_id: str):
        self.institution_id = institution_id
        self.cache = get_embedding_cache()
        self.tracker = get_tracker()
        
        # Load constraints
        if not self.cache.is_loaded(self.institution_id):
            self.cache.load(self.institution_id)

    def process_frame(self, session_id: str, image: Image.Image) -> List[RecognitionResult]:
        """
        Receives an image, extracts typed Domain bounds linearly.
        """
        t_start = time.monotonic()
        detected_faces = detect_faces(image)
        t_detect = time.monotonic()
        
        if not detected_faces:
            self.tracker.update(session_id, [])
            return []

        frame_matches = []
        t_emb_total = 0.0
        t_match_total = 0.0
        
        for face_data in detected_faces:
            try:
                emb_s = time.monotonic()
                embedding = generate_embedding(face_tensor=face_data.face_crop_tensor)
                t_emb_total += (time.monotonic() - emb_s)
            except Exception as e:
                logger.error(f"Engine embedding failure: {e}")
                continue

            match_s = time.monotonic()
            match_result = self.cache.find_match(embedding)
            t_match_total += (time.monotonic() - match_s)
            
            # Map into tracking tuple (MatchResult, FaceDetectionResult)
            frame_matches.append((match_result, face_data))
            
        tracker_verifications = self.tracker.update(session_id, frame_matches)
        
        logger.info("Pipeline Telemetry", extra={
            "telemetry_type": "pipeline",
            "detection_ms": round((t_detect - t_start)*1000, 2),
            "embedding_total_ms": round((t_emb_total)*1000, 2),
            "matching_total_ms": round((t_match_total)*1000, 2),
            "total_ms": round((time.monotonic() - t_start)*1000, 2),
            "faces_detected": len(detected_faces)
        })
        
        return tracker_verifications
        
    def reset_tracker(self, session_id: Optional[str] = None):
        self.tracker.reset(session_id)
        
    def refresh_cache(self):
        self.cache.refresh(self.institution_id)
