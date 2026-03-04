"""
Optimized Recognition Service.
Preloads student embeddings into memory at session start and uses
vectorized numpy operations for fast comparison on i5 CPU.
Avoids database queries on every frame.
"""

import numpy as np
from typing import Optional

from backend.config import SIMILARITY_THRESHOLD, DATABASE_MODE


# ── Module-level cache ──
_student_cache: Optional["StudentEmbeddingCache"] = None


class StudentEmbeddingCache:
    """
    In-memory cache of all student embeddings.
    Preloaded once at session start; avoids per-frame DB calls.
    Uses numpy matrix operations for vectorized cosine similarity.
    """

    def __init__(self):
        self.student_ids: list[str] = []
        self.student_names: list[str] = []
        self.embedding_matrix: Optional[np.ndarray] = None  # (N, 512)
        self._loaded: bool = False

    def load(self):
        """
        Load all student embeddings from the database into memory.
        Call once at session start.
        """
        # Import here to avoid circular imports; DB service is resolved at runtime
        if DATABASE_MODE == "firebase":
            from backend.database.firebase_service import get_all_students
        else:
            from backend.database.sqlite_service import get_all_students

        students = get_all_students()

        self.student_ids = []
        self.student_names = []
        embeddings = []

        for s in students:
            self.student_ids.append(s["student_id"])
            self.student_names.append(s["name"])
            emb = np.array(s["embedding"], dtype=np.float32)
            # Normalize
            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm
            embeddings.append(emb)

        if embeddings:
            self.embedding_matrix = np.stack(embeddings, axis=0)  # (N, 512)
        else:
            self.embedding_matrix = None

        self._loaded = True
        print(f"📦 Loaded {len(self.student_ids)} student embeddings into cache.")

    def is_loaded(self) -> bool:
        return self._loaded

    def find_match(
        self,
        embedding: np.ndarray,
        threshold: float = None,
    ) -> Optional[dict]:
        """
        Find the best matching student using vectorized cosine similarity.

        Args:
            embedding: Normalized 512-d numpy array
            threshold: Minimum similarity (defaults to config value)

        Returns:
            dict with student_id, name, confidence or None
        """
        if threshold is None:
            threshold = SIMILARITY_THRESHOLD

        if self.embedding_matrix is None or len(self.student_ids) == 0:
            return None

        # Ensure input is normalized
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        # Vectorized cosine similarity: (N, 512) @ (512,) -> (N,)
        similarities = self.embedding_matrix @ embedding

        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score >= threshold:
            return {
                "student_id": self.student_ids[best_idx],
                "name": self.student_names[best_idx],
                "confidence": round(best_score, 4),
            }

        return None

    def refresh(self):
        """Reload the cache (e.g. after a new student registers)."""
        self.load()


def get_embedding_cache() -> StudentEmbeddingCache:
    """Get or create the global StudentEmbeddingCache singleton."""
    global _student_cache
    if _student_cache is None:
        _student_cache = StudentEmbeddingCache()
    return _student_cache
