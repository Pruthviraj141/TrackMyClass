"""
Embedding generation service.
Uses FaceNet (InceptionResnetV1) to generate 512-d face embeddings.
"""
from typing import List
import torch
import numpy as np

from backend.ml.embedding.facenet_model import get_facenet_model
from backend.ml.config import RECOGNITION_DEVICE as DEVICE, MODEL_VERSION, EMBEDDING_DIMENSION
from backend.ml.domain import Embedding


def generate_embedding(face_tensor: torch.Tensor) -> Embedding:
    """Generate normalized 512-d Embedding domain object natively protecting the memory graph."""
    model = get_facenet_model()
    
    if face_tensor.dim() == 3:
        face_tensor = face_tensor.unsqueeze(0)
    
    face_tensor = face_tensor.to(DEVICE)
    
    with torch.inference_mode():
        embedding = model(face_tensor)
    
    embedding = embedding.cpu().numpy().flatten()
    norm = np.linalg.norm(embedding)
    normalized = embedding / norm if norm > 0 else embedding
    
    return Embedding(
        vector=normalized,
        dimension=EMBEDDING_DIMENSION,
        model_version=MODEL_VERSION,
        normalization_state=True
    )


def generate_embeddings_batch(face_tensors: torch.Tensor) -> List[Embedding]:
    """Generate batch of 512-d Embedding objects safely."""
    model = get_facenet_model()
    face_tensors = face_tensors.to(DEVICE)
    
    with torch.inference_mode():
        embeddings = model(face_tensors)
    
    embeddings = embeddings.cpu().numpy()
    
    results = []
    for emb in embeddings:
        norm = np.linalg.norm(emb)
        normalized = emb / norm if norm > 0 else emb
        results.append(
            Embedding(
                vector=normalized,
                dimension=EMBEDDING_DIMENSION,
                model_version=MODEL_VERSION,
                normalization_state=True
            )
        )
    return results


def generate_average_embedding(face_tensors_list: list) -> Embedding:
    """Generate an averaged embedding from multiple tensors."""
    embeddings = []
    for face_tensor in face_tensors_list:
        try:
            emb_obj = generate_embedding(face_tensor)
            embeddings.append(emb_obj.vector)
        except Exception as e:
            print(f"⚠️  Skipping frame due to error: {e}")
            continue
    
    if not embeddings:
        raise ValueError("No valid embeddings could be generated from the provided frames.")
    
    avg_embedding = np.mean(embeddings, axis=0)
    norm = np.linalg.norm(avg_embedding)
    normalized = avg_embedding / norm if norm > 0 else avg_embedding
    
    return Embedding(
        vector=normalized,
        dimension=EMBEDDING_DIMENSION,
        model_version=MODEL_VERSION,
        normalization_state=True
    )
