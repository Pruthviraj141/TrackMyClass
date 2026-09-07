import os
import time
import base64
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

ADMIN_CREDS = {"login_type": "admin", "username": "admin", "password": "admin"} 

def main():
    print("--- Phase 4: Native API Realtime Benchmarking ---")
    
    # 1. Login
    resp = client.post("/api/v1/auth/login", data=ADMIN_CREDS)
    if resp.status_code != 200:
        print(f"Login Failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "DEMO2026"}
    print("✅ Authenticated.")
    
    # 2. Register Student 
    face_path = "benchmarks/sample_face.jpg"
    if not os.path.exists(face_path):
        print("Missing sample_face.jpg")
        return
        
    with open(face_path, "rb") as f:
        file_bytes = f.read()
        resp = client.post(
            "/api/v1/registration/register",
            headers=headers,
            data={
                "name": "Live Student A",
                "roll_number": "LIVE_A",
                "institution_id": "DEMO2026",
                "gender": "Other"
            },
            files={"file": ("sample_face.jpg", file_bytes, "image/jpeg")}
        )
    print(f"✅ Registration (Step 3) HTTP {resp.status_code}: {resp.json().get('message')}")
    
    # 3. Start Session
    resp = client.post(
        "/api/v1/attendance/session/start",
        headers=headers,
        json={"institution_id": "DEMO2026", "subject_name": "Performance Testing"}
    )
    if resp.status_code != 200:
        print(f"Session Start Failed: {resp.text}")
        return
    session_id = resp.json()["session_id"]
    print(f"✅ Session Started (Step 7) ID: {session_id}")

    # 4. Simulate Live Stream (Continuous hits for 10 seconds to emulate Sustained Session)
    print("🎥 Beginning Live Stream Mock (Step 4, 8, 11)...")
    start_time = time.time()
    frames = 0
    t_start = time.time()
    
    encoded_string = base64.b64encode(file_bytes).decode('utf-8')
    payload = {
        "session_id": session_id,
        "image_data": f"data:image/jpeg;base64,{encoded_string}",
        "timestamp": int(time.time() * 1000)
    }

    # Hit 20 frames mapping roughly 2 FPS logic internally
    results = []
    
    for i in range(20):
        t0 = time.time()
        resp = client.post("/api/v1/attendance/mark-attendance", headers=headers, json=payload)
        latency = (time.time() - t0) * 1000
        frames += 1
        
        try:
            recognized = resp.json().get('results', [{}])[0].get('name', 'UNKNOWN')
        except:
            recognized = "ERROR"
            
        print(f"  Frame {frames:02d} | Latency: {latency:.1f}ms | Detected: {recognized}")
        results.append(latency)

    print(f"✅ Live Stream Simulation Complete. Avg Latency: {sum(results)/len(results):.1f}ms")
    
if __name__ == "__main__":
    main()
