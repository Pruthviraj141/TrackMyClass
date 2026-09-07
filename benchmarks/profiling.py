"""
Phase 3 Performance Benchmarking Suite.
Executes Batch Inference profiling, Vector Optimization measuring, and explicit Memory profiling logic escaping web layers.
"""
import time
import os
import psutil
import torch
from PIL import Image
import numpy as np

os.environ["RECOGNITION_DEVICE"] = "cpu"
from backend.ml.detector.face_detection import detect_faces
from backend.ml.embedding.embedding_service import generate_embeddings_batch, generate_embedding
from backend.ml.matcher.optimized_recognition import StudentEmbeddingCache


def get_memory_mb():
    # Helper extracting pure OS memory bindings
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def benchmark_batch_inference():
    """
    Step 20: Batch inference evaluation
    """
    print("\n--- Running Batch Inference Benchmark ---")
    # Provide synthetic empty/random tensors mapped identically to expected (3, 160, 160) boundaries
    sizes = [1, 2, 4, 8, 16]
    results = []
    for s in sizes:
        batch_tensors = torch.randn(s, 3, 160, 160)
        start = time.perf_counter()
        _ = generate_embeddings_batch(batch_tensors)
        end = time.perf_counter()
        print(f"Batch ({s} faces): {end - start:.4f} seconds")


def benchmark_numpy_vectorization():
    """
    Step 21: Vector matching engineering
    """
    print("\n--- Running Vector Matching Benchmark ---")
    cache = StudentEmbeddingCache()
    # Mocking preloaded embeddings artificially
    sizes = [100, 1000, 5000, 10000, 25000]
    for s in sizes:
        cache.student_ids = [f"mock_{i}" for i in range(s)]
        cache.student_names = [f"Mock {i}" for i in range(s)]
        
        # Load massive random 512 dimensions simulating cached tensor memory footprint natively
        cache.embedding_matrix = np.random.randn(s, 512).astype(np.float32)
        cache._loaded = True
        
        # Mock incoming typed query embedding vector
        from backend.ml.domain import Embedding
        q = np.random.randn(512).astype(np.float32)
        query_emb = Embedding(vector=q, dimension=512, model_version="facenet_v1", normalization_state=True)
        
        start = time.perf_counter()
        _ = cache.find_match(query_emb, threshold=0.7)
        end = time.perf_counter()
        
        print(f"Matching ({s} students): {end - start:.5f} seconds")


def benchmark_memory_accumulation():
    """
    Step 19: Memory Management diagnostics
    """
    print("\n--- Running PyTorch Profiler Accumulation Test ---")
    dummy_img = Image.new('RGB', (640, 480), color='white')
    
    start_mem = get_memory_mb()
    print(f"Baseline Memory: {start_mem:.2f} MB")
    
    # Process 50 dummy frames looking for graph leakages.
    for i in range(50):
        # MTCNN returns nothing on black/white frames, so we manually invoke tensor inference logic
        # simulating a real workload stream natively skipping MTCNN.
        fake_face = torch.randn(3, 160, 160)
        _ = generate_embedding(fake_face)
        
    end_mem = get_memory_mb()
    print(f"Post-Inference (50 frames) Memory: {end_mem:.2f} MB")
    print(f"Total Accumulation: {end_mem - start_mem:.2f} MB")


if __name__ == "__main__":
    print(f"Using Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    benchmark_batch_inference()
    benchmark_numpy_vectorization()
    benchmark_memory_accumulation()
    print("\nBenchmarks Complete!")
