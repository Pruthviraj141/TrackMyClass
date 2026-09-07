"""
Optimized Recognition Service.
Preloads student embeddings into memory at session start and uses
vectorized numpy operations for fast comparison on i5 CPU.
Avoids database queries on every frame.
"""

import logging
import numpy as np
from typing import Optional, List, Dict, Any

from backend.core.config import SIMILARITY_THRESHOLD, DATABASE_MODE

logger = logging.getLogger(__name__)


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
        self._current_institution: str = ""

    def load(self, institution_id: str = "DEMO2026"):
        """
        Load all student embeddings from the database into memory.
        Call once at session start.
        """
        # Import here to avoid circular imports; DB service is resolved at runtime
        if DATABASE_MODE == "firebase":
            from backend.infrastructure.database.firebase_impl import get_all_students
        else:
            from backend.infrastructure.database.sqlite_impl import get_all_students

        try:
            students = get_all_students(institution_id)

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
            self._current_institution = institution_id
            logger.info(f"📦 Loaded {len(self.student_ids)} student embeddings into cache for {institution_id}.")
        except Exception as e:
            logger.error(f"❌ Failed to load student embeddings: {e}")
            self.embedding_matrix = None
            self._loaded = False

    def is_loaded(self, institution_id: str = "DEMO2026") -> bool:
        return self._loaded and self._current_institution == institution_id

    def find_match(
        self,
        embedding: "Embedding",
        threshold: Optional[float] = None,
    ) -> Optional["MatchResult"]:
        """
        Find the best matching student using vectorized cosine similarity directly mapping to Domains.
        """
        from backend.ml.domain import MatchResult
        
        if threshold is None:
            threshold = SIMILARITY_THRESHOLD

        if self.embedding_matrix is None or len(self.student_ids) == 0:
            return None

        # Extract normalized vector directly from typed Embedding boundary
        vec = embedding.vector

        # Vectorized cosine similarity: (N, 512) @ (512,) -> (N,)
        similarities = self.embedding_matrix @ vec

        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score >= threshold:
            return MatchResult(
                candidate_identity=self.student_ids[best_idx],
                similarity=round(best_score, 4),
                threshold_applied=threshold,
                is_accepted=True
            )

        return None

    def refresh(self, institution_id: str = "DEMO2026"):
        """Reload the cache (e.g. after a new student registers)."""
        self.load(institution_id)


def get_embedding_cache() -> StudentEmbeddingCache:
    """Get or create the global StudentEmbeddingCache singleton."""
    global _student_cache
    if _student_cache is None:
        _student_cache = StudentEmbeddingCache()
    return _student_cache
