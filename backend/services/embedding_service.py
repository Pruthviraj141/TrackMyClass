"""
Embedding generation service.
Uses FaceNet (InceptionResnetV1) to generate 512-d face embeddings.
"""

import torch
import numpy as np

from backend.models.facenet_model import get_facenet_model
from backend.config import DEVICE


def generate_embedding(face_tensor: torch.Tensor) -> np.ndarray:
    """
    Generate a 512-dimensional embedding for a single face.
    
    Args:
        face_tensor: Preprocessed face tensor of shape (3, 160, 160)
    
    Returns:
        Normalized 512-d numpy array
    """
    model = get_facenet_model()
    
    # Add batch dimension if needed
    if face_tensor.dim() == 3:
        face_tensor = face_tensor.unsqueeze(0)
    
    face_tensor = face_tensor.to(DEVICE)
    
    with torch.no_grad():
        embedding = model(face_tensor)
    
    # Convert to numpy and normalize to unit vector
    embedding = embedding.cpu().numpy().flatten()
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding


def generate_embeddings_batch(face_tensors: torch.Tensor) -> list:
    """
    Generate embeddings for a batch of faces.
    
    Args:
        face_tensors: Tensor of shape (N, 3, 160, 160)
    
    Returns:
        List of normalized 512-d numpy arrays
    """
    model = get_facenet_model()
    face_tensors = face_tensors.to(DEVICE)
    
    with torch.no_grad():
        embeddings = model(face_tensors)
    
    embeddings = embeddings.cpu().numpy()
    
    # Normalize each embedding to unit vector
    result = []
    for emb in embeddings:
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
        result.append(emb)
    
    return result


def generate_average_embedding(face_tensors_list: list) -> np.ndarray:
    """
    Generate an averaged embedding from multiple face captures.
    Used during registration for robust embedding from multi-angle frames.
    
    Args:
        face_tensors_list: List of face tensors, each of shape (3, 160, 160)
    
    Returns:
        Averaged and normalized 512-d numpy array
    
    Raises:
        ValueError: If no valid embeddings could be generated
    """
    embeddings = []
    
    for face_tensor in face_tensors_list:
        try:
            emb = generate_embedding(face_tensor)
            embeddings.append(emb)
        except Exception as e:
            print(f"⚠️  Skipping frame due to error: {e}")
            continue
    
    if len(embeddings) == 0:
        raise ValueError("No valid embeddings could be generated from the provided frames.")
    
    # Average all embeddings
    avg_embedding = np.mean(embeddings, axis=0)
    
    # Re-normalize the averaged embedding
    norm = np.linalg.norm(avg_embedding)
    if norm > 0:
        avg_embedding = avg_embedding / norm
    
    print(f"✅ Generated average embedding from {len(embeddings)} frames.")
    return avg_embedding
