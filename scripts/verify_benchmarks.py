import os
import psutil
import torch
import numpy as np
import time
import json
import gc

def get_rss_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

report = {}
report['hardware'] = "cuda" if torch.cuda.is_available() else "cpu"
report['embedding_dimension'] = 512
report['data_type'] = "float32"

print(f"Initial RSS before imports: {get_rss_mb():.2f} MB")
report['rss_baseline'] = get_rss_mb()

# Override for environment
os.environ["RECOGNITION_DEVICE"] = report['hardware'] 
from backend.ml.embedding.embedding_service import generate_embeddings_batch, generate_embedding
from backend.ml.matcher.optimized_recognition import StudentEmbeddingCache
from backend.ml.domain import Embedding

# Init Model
print("Running Initialization...")
dummy = torch.randn(3, 160, 160)
generate_embedding(dummy)
report['rss_post_init'] = get_rss_mb()
print(f"Post-init RSS: {report['rss_post_init']:.2f} MB")

# 1. Matching
print("Running Vector Matching...")
cache = StudentEmbeddingCache()
query = np.random.randn(512).astype(np.float32)
query_norm = query / np.linalg.norm(query)
query_emb = Embedding(vector=query_norm, dimension=512, model_version="facenet_v1", normalization_state=True)

match_results = {}
sizes = [100, 1000, 5000, 10000, 25000]
for s in sizes:
    cache.student_ids = [f"id_{i}" for i in range(s)]
    cache.student_names = [f"Name {i}" for i in range(s)]
    mat = np.random.randn(s, 512).astype(np.float32)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    cache.embedding_matrix = (mat / norms).astype(np.float32)
    cache._loaded = True
    
    # Warmup
    for _ in range(20): cache.find_match(query_emb, 0.75)
    
    times = []
    for _ in range(500):
        t0 = time.perf_counter_ns()
        cache.find_match(query_emb, 0.75)
        t1 = time.perf_counter_ns()
        times.append((t1-t0)/1e6) # ms
    
    match_results[str(s)] = {
        "mean_ms": np.mean(times),
        "median_ms": np.median(times),
        "p95_ms": np.percentile(times, 95),
        "p99_ms": np.percentile(times, 99),
        "throughput_queries_per_sec": 1000 / np.mean(times)
    }
report['matching'] = match_results

# 2. Batch Inference
print("Running Batch Inference...")
batch_results = {}
batch_sizes = [1, 2, 4, 8, 16]
for bs in batch_sizes:
    tensors = torch.randn(bs, 3, 160, 160)
    generate_embeddings_batch(tensors) # warmup
    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        generate_embeddings_batch(tensors)
        t1 = time.perf_counter()
        times.append(t1-t0)
        
    avg_t = np.mean(times)
    fps = bs / avg_t
    batch_results[str(bs)] = {
        "total_batch_latency_sec": avg_t,
        "latency_per_face_sec": avg_t / bs,
        "throughput_fps": fps
    }
report['batch_inference'] = batch_results

# 3. Sustained Memory
print("Running Sustained Memory...")
report['rss_pre_sustained'] = get_rss_mb()
rss_history = []
for i in range(1, 1001):
    t = torch.randn(3, 160, 160)
    generate_embedding(t)
    if i % 100 == 0:
        rss = get_rss_mb()
        rss_history.append({"frame": i, "rss_mb": rss})
        print(f"Frame {i}: RSS {rss:.2f} MB")
        
report['rss_history'] = rss_history
report['rss_post_sustained'] = get_rss_mb()

os.makedirs("benchmarks", exist_ok=True)
with open("benchmarks/verification_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("Done.")
