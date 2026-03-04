"""
Recognition service.
Matches face embeddings against stored student embeddings using cosine similarity.
"""

import numpy as np
from typing import Optional

from backend.config import SIMILARITY_THRESHOLD


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings.
    Both embeddings should be unit-normalized for best results.
    
    Args:
        embedding1: First 512-d embedding
        embedding2: Second 512-d embedding
    
    Returns:
        Cosine similarity score between -1 and 1
    """
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def find_match(
    embedding: np.ndarray,
    all_students: list,
    threshold: float = None,
) -> Optional[dict]:
    """
    Find the best matching student for a given face embedding.
    
    Args:
        embedding: 512-d face embedding to match
        all_students: List of student dicts (each must have 'embedding', 
                      'student_id', 'name' keys)
        threshold: Minimum cosine similarity for a valid match.
                   Defaults to SIMILARITY_THRESHOLD from config.
    
    Returns:
        dict with keys: student_id, name, confidence
        or None if no match above threshold
    """
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD
    
    if not all_students:
        return None
    
    best_match = None
    best_score = -1.0
    
    for student in all_students:
        stored_embedding = np.array(student["embedding"], dtype=np.float32)
        score = cosine_similarity(embedding, stored_embedding)
        
        if score > best_score:
            best_score = score
            best_match = student
    
    if best_score >= threshold and best_match is not None:
        return {
            "student_id": best_match["student_id"],
            "name": best_match["name"],
            "confidence": round(best_score, 4),
        }
    
    return None


def find_all_matches(
    embeddings: list,
    all_students: list,
    threshold: float = None,
) -> list:
    """
    Find matches for multiple face embeddings (used for multi-face detection).
    
    Args:
        embeddings: List of 512-d face embeddings
        all_students: List of student dicts
        threshold: Minimum cosine similarity threshold
    
    Returns:
        List of match dicts (or None entries for unmatched faces)
    """
    results = []
    for emb in embeddings:
        match = find_match(emb, all_students, threshold)
        results.append(match)
    return results
