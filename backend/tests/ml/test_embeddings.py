import pytest
import torch
import numpy as np
import os
from backend.ml.embedding.embedding_service import generate_embedding, generate_embeddings_batch
from backend.ml.config import EMBEDDING_DIMENSION

def test_generate_single_embedding():
    os.environ["RECOGNITION_DEVICE"] = "cpu"
    # Create fake normalized face tensor (3, 160, 160)
    tensor = torch.randn(3, 160, 160)
    emb = generate_embedding(tensor)
    
    assert emb.dimension == EMBEDDING_DIMENSION
    assert len(emb.vector) == EMBEDDING_DIMENSION
    assert emb.normalization_state is True
    # Verify unitary sphere normalization cleanly mathematically
    norm = np.linalg.norm(emb.vector)
    assert np.isclose(norm, 1.0, atol=1e-5)

def test_batch_embedding_generation():
    os.environ["RECOGNITION_DEVICE"] = "cpu"
    tensors = torch.randn(4, 3, 160, 160)
    embs = generate_embeddings_batch(tensors)
    
    assert len(embs) == 4
    for emb in embs:
        norm = np.linalg.norm(emb.vector)
        assert np.isclose(norm, 1.0, atol=1e-5)
