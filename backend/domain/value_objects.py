"""
Value Objects
Immutable representations of data used across boundaries.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class InitialDetection:
    tensor: np.ndarray # PyTorch face tensor representation
    box: List[float]
    prob: float

@dataclass
class RecognitionResult:
    student_id: str
    name: str
    confidence: float
    box: List[float]
    status: str
    frames_tracked: int = 0
    frames_needed: int = 0
