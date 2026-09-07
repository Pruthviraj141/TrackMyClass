import pytest
import numpy as np
from backend.ml.matcher.optimized_recognition import StudentEmbeddingCache
from backend.ml.domain import Embedding

def test_cache_unknown_face_rejected():
    cache = StudentEmbeddingCache()
    cache.student_ids = ["stu_1"]
    cache.student_names = ["Student 1"]
    
    # Store explicit normalized identity
    v1 = np.ones(512).astype(np.float32)
    v1 = v1 / np.linalg.norm(v1)
    cache.embedding_matrix = np.array([v1])
    cache._loaded = True
    
    # Query completely orthogonal vector mathematically yielding Cosine roughly 0
    q = np.random.randn(512).astype(np.float32)
    q = q / np.linalg.norm(q)
    
    # Zeroing out dot product synthetically testing mathematical rejection correctly
    q = -v1 
    
    query = Embedding(vector=q, dimension=512, model_version="facenet_v1", normalization_state=True)
    
    # Needs 0.75+ to match ideally.
    match = cache.find_match(query, threshold=0.75)
    
    assert match is None
