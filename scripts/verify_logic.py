import os
import json
import numpy as np
from PIL import Image

def run_threshold_calibration():
    print("--- THRESHOLD CALIBRATION ---")
    np.random.seed(42)
    # Synthesize cluster centers (identities)
    num_identities = 50
    identities = np.random.randn(num_identities, 512).astype(np.float32)
    norms = np.linalg.norm(identities, axis=1, keepdims=True)
    identities = identities / norms
    
    # Generate positive pairs (same identity + noise)
    positive_pairs = []
    for i in range(1000):
        id_idx = np.random.randint(0, num_identities)
        base = identities[id_idx]
        # Add slight noise simulating camera conditions
        n1 = base + np.random.normal(0, 0.3, 512)
        n2 = base + np.random.normal(0, 0.3, 512)
        v1 = (n1 / np.linalg.norm(n1)).astype(np.float32)
        v2 = (n2 / np.linalg.norm(n2)).astype(np.float32)
        sim = np.dot(v1, v2)
        positive_pairs.append(sim)
        
    # Generate negative pairs (different identities)
    negative_pairs = []
    for i in range(1000):
        idx1, idx2 = np.random.choice(num_identities, 2, replace=False)
        base1 = identities[idx1]
        base2 = identities[idx2]
        n1 = base1 + np.random.normal(0, 0.3, 512)
        n2 = base2 + np.random.normal(0, 0.3, 512)
        v1 = (n1 / np.linalg.norm(n1)).astype(np.float32)
        v2 = (n2 / np.linalg.norm(n2)).astype(np.float32)
        sim = np.dot(v1, v2)
        negative_pairs.append(sim)
        
    thresholds = [0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
    res_thresh = {}
    for t in thresholds:
        tp = sum(1 for p in positive_pairs if p >= t)
        fn = sum(1 for p in positive_pairs if p < t)
        tn = sum(1 for n in negative_pairs if n < t)
        fp = sum(1 for n in negative_pairs if n >= t)
        
        tar = tp / (tp + fn) if (tp + fn) > 0 else 0
        far = fp / (fp + tn) if (fp + tn) > 0 else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tar # same
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
        
        res_thresh[str(t)] = {
            "TAR": float(tar), "FAR": float(far), 
            "FRR": float(1-tar), "Precision": float(prec), "F1": float(f1)
        }
    return res_thresh

def run_invalid_image_robustness():
    print("--- INVALID IMAGE ROBUSTNESS ---")
    os.environ["RECOGNITION_DEVICE"] = "cpu"
    from backend.ml.engine import RecognitionEngine
    engine = RecognitionEngine("TEST_TENANT")
    
    results = {}
    # 1. Empty Image
    img_black = Image.new('RGB', (100, 100), color='black')
    try:
        r = engine.process_frame(img_black)
        results["empty_image"] = len(r) == 0
    except Exception as e:
        results["empty_image"] = str(e)
        
    # 2. Grayscale Image
    img_grey = Image.new('L', (100, 100), color=128)
    img_conv = img_grey.convert("RGB")
    try:
        r = engine.process_frame(img_conv)
        results["grayscale_image"] = len(r) == 0
    except Exception as e:
        results["grayscale_image"] = str(e)
        
    return results

def tenant_isolation_test():
    print("--- TENANT ISOLATION ---")
    from backend.ml.matcher.optimized_recognition import StudentEmbeddingCache
    from backend.ml.domain import Embedding
    
    cacheA = StudentEmbeddingCache()
    cacheB = StudentEmbeddingCache()
    
    # Load institution A
    cacheA.student_ids = ["A_1"]
    cacheA.student_names = ["Student A"]
    cacheA.embedding_matrix = np.ones((1, 512)).astype(np.float32)
    cacheA._loaded = True
    
    # Load institution B
    cacheB.student_ids = ["B_1"]
    cacheB.student_names = ["Student B"]
    cacheB.embedding_matrix = (np.ones((1, 512)) * -1).astype(np.float32)
    cacheB._loaded = True
    
    q = np.ones(512).astype(np.float32)
    query_emb = Embedding(vector=q, dimension=512, model_version="v1", normalization_state=True)
    
    matchA = cacheA.find_match(query_emb, 0.75)
    matchB = cacheB.find_match(query_emb, 0.75)
    
    return {
        "A_matches_A": matchA is not None and matchA.candidate_identity == "A_1",
        "B_does_not_match_A": matchB is None
    }

if __name__ == "__main__":
    rep = {}
    rep['threshold_calibration'] = run_threshold_calibration()
    rep['invalid_image_robustness'] = run_invalid_image_robustness()
    rep['tenant_isolation'] = tenant_isolation_test()
    
    os.makedirs("benchmarks", exist_ok=True)
    with open("benchmarks/logic_report.json", "w") as f:
        json.dump(rep, f, indent=2)
    print("Done")
