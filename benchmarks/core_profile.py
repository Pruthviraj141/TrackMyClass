import time
import os
import io
import torch
import numpy as np
from PIL import Image

def benchmark():
    print("--- Phase 4: Component Latency Trace (Step 13, 14, 15) ---")
    
    # 1. Loading overhead
    print("🔄 Loading Models (Isolating Initialization)...")
    t0 = time.time()
    from backend.ml.detection.detector import detect_faces
    from backend.ml.embeddings.generator import generate_embedding
    print(f"✅ Models initialized in: {(time.time() - t0)*1000:.1f}ms")

    # 2. Image Load & Base64 Simulation
    face_path = "benchmarks/sample_face.jpg"
    with open(face_path, "rb") as f:
        raw_bytes = f.read()

    # Step 15: Base64 Cost Analysis
    t_enc = time.time()
    import base64
    b64_str = base64.b64encode(raw_bytes).decode('utf-8')
    t_enc_end = time.time()
    
    t_dec = time.time()
    decoded = base64.b64decode(b64_str)
    img = Image.open(io.BytesIO(decoded)).convert('RGB')
    t_dec_end = time.time()

    print(f"📊 Base64 Encode: {(t_enc_end - t_enc)*1000:.2f}ms")
    print(f"📊 Base64 Decode & PIL Open: {(t_dec_end - t_dec)*1000:.2f}ms")

    # Step 13, 14, 17: Request-Level Trace
    times_det = []
    times_emb = []
    
    # Warmup
    _ = detect_faces(img)

    for i in range(5):
        # Detection
        t_det = time.time()
        detections = detect_faces(img)
        dt_det = (time.time() - t_det)*1000
        times_det.append(dt_det)

        if not detections:
            print("No faces detected!")
            continue
            
        box, prob = detections[0]
        face_img = img.crop(box)

        # Embedding
        t_emb = time.time()
        embedding = generate_embedding(face_img)
        dt_emb = (time.time() - t_emb)*1000
        times_emb.append(dt_emb)
        
    print(f"\n📈 Core Trace Averages over 5 frames:")
    print(f"   [Decode]: {(t_dec_end - t_dec)*1000:.1f} ms")
    print(f"   [MTCNN Detect]: {np.mean(times_det):.1f} ms")
    print(f"   [FaceNet Embed]: {np.mean(times_emb):.1f} ms")
    print(f"   [Total Logic]: {(t_dec_end - t_dec)*1000 + np.mean(times_det) + np.mean(times_emb):.1f} ms / frame (~{1000/((t_dec_end - t_dec)*1000 + np.mean(times_det) + np.mean(times_emb)):.1f} FPS MAX)")

if __name__ == "__main__":
    benchmark()
