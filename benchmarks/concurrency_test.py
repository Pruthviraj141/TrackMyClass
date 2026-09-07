import time
import os
import requests
import base64
import numpy as np
import concurrent.futures

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_CREDS = {"login_type": "admin", "username": "admin", "password": "admin"} 

def benchmark_health():
    t0 = time.time()
    try:
        resp = requests.get(f"http://localhost:8000/")  # assuming root has health or similar, actually /docs serves as a good lightweight test
    except:
        return 9999.9
    return (time.time() - t0) * 1000

def main():
    print("--- Phase 4: Final Acceptance Gate Concurrency & ASGI Validation ---")
    
    # 1. Login
    resp = requests.post(f"{BASE_URL}/auth/login", data=ADMIN_CREDS)
    if resp.status_code != 200:
        print(f"Login Failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "DEMO2026"}
    
    # 2. Register & Start
    face_path = "benchmarks/sample_face.jpg"
    with open(face_path, "rb") as f:
        file_bytes = f.read()
        resp = requests.post(
            f"{BASE_URL}/registration/register",
            headers=headers,
            data={"name": "Gate Student", "roll_number": "GATE_1", "institution_id": "DEMO2026", "gender": "Other"},
            files={"file": ("sample_face.jpg", file_bytes, "image/jpeg")}
        )
    
    resp = requests.post(f"{BASE_URL}/attendance/session/start", headers=headers, json={"institution_id": "DEMO2026", "subject_name": "Gate Test"})
    session_id = resp.json()["session"]["session_id"]
    
    encoded_string = base64.b64encode(file_bytes).decode('utf-8')
    payload = {
        "session_id": session_id,
        "image_data": f"data:image/jpeg;base64,{encoded_string}",
        "timestamp": int(time.time() * 1000)
    }

    # Base Health Check
    t_h = benchmark_health()
    print(f"✅ Baseline `/docs` lightweight latency: {t_h:.2f}ms")

    # Concurrent Execution
    def test_single_frame():
        t0 = time.time()
        res = requests.post(f"{BASE_URL}/attendance/mark-attendance", headers=headers, json=payload)
        return (time.time() - t0) * 1000

    def run_concurrency(num_requests):
        print(f"\n🚀 Running {num_requests} concurrent requests (Gate 11 - Real Server Concurrency)...")
        latencies = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            t_start = time.time()
            future_to_req = {executor.submit(test_single_frame): i for i in range(num_requests)}
            
            # Immediately fire a health check while it's executing! (Gate 12 - ASGI Blocking Proof)
            health_latency = benchmark_health()

            for future in concurrent.futures.as_completed(future_to_req):
                try:
                    lat = future.result()
                    latencies.append(lat)
                except Exception as exc:
                    print(f"Request generated an exception: {exc}")

            total_time = (time.time() - t_start) * 1000

        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        print(f"   Throughput: {num_requests / (total_time/1000):.2f} RPS")
        print(f"   P50: {p50:.2f} ms | P95: {p95:.2f} ms")
        print(f"   🚧 ASGI Block Check (Health during load): {health_latency:.2f} ms")

    run_concurrency(2)
    run_concurrency(5)
    run_concurrency(10)

if __name__ == "__main__":
    main()
