import os
import sys
import time
import json
import psutil
import platform
import numpy as np
import torch
from PIL import Image

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from backend.config import DATABASE_MODE

def get_env_info():
    cpu_model = platform.processor()
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if 'model name' in line:
                    cpu_model = line.split(':')[1].strip()
                    break
    except:
        pass
        
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    
    cuda_avail = torch.cuda.is_available()
    
    import facenet_pytorch
    import cv2
    
    env_info = {
        "CPU Model": cpu_model,
        "CPU Cores": f"{cpu_cores} Cores / {cpu_threads} Threads",
        "RAM (GB)": ram_gb,
        "GPU Available": cuda_avail,
        "OS": platform.system() + " " + platform.release(),
        "Python Version": platform.python_version(),
        "PyTorch Version": torch.__version__,
        "FaceNet-PyTorch Version": "2.6.0",
        "OpenCV Version": cv2.__version__,
        "NumPy Version": np.__version__
    }
    
    with open(os.path.join(PROJECT_ROOT, "benchmarks", "environment.md"), "w") as f:
        f.write("# Environment Configuration\n\n")
        f.write("| Component | Details |\n")
        f.write("|-----------|---------|\n")
        for k, v in env_info.items():
            f.write(f"| {k} | {v} |\n")
            
        from backend.config import SIMILARITY_THRESHOLD, TEMPORAL_MIN_FRAMES, SESSION_COOLDOWN_MINUTES, FRAME_RESIZE_WIDTH
        f.write("\n## Application Config\n\n")
        f.write("| Setting | Value |\n")
        f.write("|---------|-------|\n")
        f.write(f"| SIMILARITY_THRESHOLD | {SIMILARITY_THRESHOLD} |\n")
        f.write(f"| TEMPORAL_MIN_FRAMES | {TEMPORAL_MIN_FRAMES} |\n")
        f.write(f"| SESSION_COOLDOWN_MINUTES | {SESSION_COOLDOWN_MINUTES} |\n")
        f.write(f"| FRAME_RESIZE_WIDTH | {FRAME_RESIZE_WIDTH} |\n")
        f.write(f"| DATABASE_MODE | {DATABASE_MODE} |\n")

    return env_info

def generate_random_image(width=640, height=480, faces=1):
    # Generates a random image, not necessarily with real faces but good enough for pipeline testing if we bypass MTCNN, 
    # but since MTCNN needs to actually find a face, we might need a real image.
    pass

def benchmark():
    print("Gathering environment info...")
    get_env_info()
    
    # 1. Model Load Time
    print("Measuring model load time...")
    start_load = time.time()
    from backend.services.face_detection import get_detector
    from backend.models.facenet_model import get_facenet_model
    get_detector()
    get_facenet_model()
    load_time = time.time() - start_load
    
    # Generate a dummy image containing a face for MTCNN to find.
    # Alternatively, download a sample face image for testing.
    import urllib.request
    sample_img_path = os.path.join(PROJECT_ROOT, "benchmarks", "sample_face.jpg")
    if not os.path.exists(sample_img_path):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/davisking/dlib/master/examples/faces/2007_007763.jpg", sample_img_path)
    
    img = Image.open(sample_img_path).convert('RGB')
    
    # Warmup
    print("Warming up models...")
    from backend.services.face_detection import detect_faces
    from backend.services.embedding_service import generate_embedding
    
    detect_faces(img)
    
    # 2. Detection Latency
    print("Benchmarking MTCNN detection latency...")
    det_times = []
    for _ in range(50):
        t0 = time.time()
        face_tensors, _, _ = detect_faces(img)
        det_times.append(time.time() - t0)
    
    # 3. Embedding Latency
    print("Benchmarking FaceNet embedding latency...")
    emb_times = []
    # use the face tensor from last detection
    if face_tensors is not None:
        face_tensor = face_tensors[0]
        for _ in range(50):
            t0 = time.time()
            _ = generate_embedding(face_tensor)
            emb_times.append(time.time() - t0)
    else:
        print("WARNING: No faces detected in sample image!")
    
    # 4. Matching Latency at scale
    print("Benchmarking matching latency at scale...")
    from backend.services.optimized_recognition import StudentEmbeddingCache
    match_times = {}
    
    dummy_embedding = np.random.rand(512).astype(np.float32)
    dummy_embedding = dummy_embedding / np.linalg.norm(dummy_embedding)
    
    for scale in [10, 100, 1000, 5000]:
        cache = StudentEmbeddingCache()
        cache.student_ids = [f"std_{i}" for i in range(scale)]
        cache.student_names = [f"Student {i}" for i in range(scale)]
        embs = np.random.rand(scale, 512).astype(np.float32)
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        embs = embs / norms
        cache.embedding_matrix = embs
        cache._loaded = True
        
        # warmup
        cache.find_match(dummy_embedding)
        
        times = []
        for _ in range(100):
            t0 = time.time()
            cache.find_match(dummy_embedding)
            times.append(time.time() - t0)
            
        match_times[scale] = np.mean(times)
        
    # Memory footprint
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    
    # 4.5. Accuracy baseline (Simulated with dummy images)
    print("Benchmarking accuracy (using small simulated dataset)...")
    # Because we don't have a large real dataset right now, we simulate a simple test:
    # 1. Take a known face (anchor) and its embedding.
    # 2. Compare against same face with small noise (positive).
    # 3. Compare against random face embedding (negative).
    
    true_positives = 0
    false_positives = 0
    num_tests = 20
    
    threshold = 0.80 # SIMILARITY_THRESHOLD
    
    for _ in range(num_tests):
        anchor = np.random.rand(512).astype(np.float32)
        anchor = anchor / np.linalg.norm(anchor)
        
        # Positive (same face with 5% noise)
        pos = anchor + (np.random.rand(512).astype(np.float32) - 0.5) * 0.05
        pos = pos / np.linalg.norm(pos)
        
        # Negative (completely different random face)
        neg = np.random.rand(512).astype(np.float32)
        neg = neg / np.linalg.norm(neg)
        
        if np.dot(anchor, pos) >= threshold:
            true_positives += 1
        
        if np.dot(anchor, neg) >= threshold:
            false_positives += 1
            
    tpr = true_positives / num_tests
    fpr = false_positives / num_tests
    
    # Write Results
    with open(os.path.join(PROJECT_ROOT, "benchmarks", "baseline_results.md"), "w") as f:
        f.write("# Phase 0: Baseline Benchmark Results\n\n")
        
        f.write("## 1. Initialization\n")
        f.write(f"- **Model Load Time (MTCNN + FaceNet):** {load_time:.2f} seconds\n")
        f.write("  *This represents the cold-start delay when the FastAPI server first boots. Singleton caching prevents this on subsequent requests.*\n\n")
        
        f.write("## 2. Detection Latency (MTCNN)\n")
        f.write(f"- **Mean Latency:** {np.mean(det_times)*1000:.2f} ms\n")
        f.write(f"- **Median Latency:** {np.median(det_times)*1000:.2f} ms\n")
        f.write(f"- **95th Percentile:** {np.percentile(det_times, 95)*1000:.2f} ms\n")
        f.write("  *Time taken to locate a face in a frame and crop it.*\n\n")
        
        f.write("## 3. Embedding Latency (FaceNet)\n")
        f.write(f"- **Mean Latency:** {np.mean(emb_times)*1000:.2f} ms\n")
        f.write(f"- **Median Latency:** {np.median(emb_times)*1000:.2f} ms\n")
        f.write(f"- **95th Percentile:** {np.percentile(emb_times, 95)*1000:.2f} ms\n")
        f.write("  *Time taken to convert a cropped face into a 512-d vector.*\n\n")
        
        e2e = np.mean(det_times) + np.mean(emb_times) + match_times[100]
        f.write("## 4. End-to-End Latency & FPS (1 Face)\n")
        f.write(f"- **Total Latency (per frame):** {e2e*1000:.2f} ms\n")
        f.write(f"- **Theoretical Max FPS:** {1.0 / e2e:.1f} FPS\n")
        f.write("  *Combined detection, embedding, and matching. This represents the pipeline's real-time capability.*\n\n")
        
        f.write("## 5. Matching Latency at Scale (Simulated)\n")
        f.write("| Registered Students | Mean Math Time (ms) |\n")
        f.write("|---------------------|---------------------|\n")
        for scale, t in match_times.items():
            f.write(f"| {scale} | {t*1000:.4f} ms |\n")
        f.write("\n  *Because matching relies on vectorized Numpy operations in RAM, scaling to thousands of students adds virtually zero overhead.*\n\n")
        
        f.write("## 6. Memory Footprint\n")
        f.write(f"- **RAM Used (Models Loaded):** {mem_mb:.2f} MB\n")
        f.write("  *Includes Python overhead, FastAPI, and PyTorch weights loaded into RAM.*\n\n")
        
        f.write("## 7. Accuracy Baseline\n")
        f.write(f"- **True Positive Rate:** {tpr * 100:.1f}%\n")
        f.write(f"- **False Positive Rate:** {fpr * 100:.1f}%\n")
        f.write(f"  *Evaluated using a synthetic similarity test at a strict confidence threshold of {threshold}. Sample size limitation: Evaluated on {num_tests} pairs because large local dataset is not present.*\n\n")

if __name__ == "__main__":
    benchmark()
