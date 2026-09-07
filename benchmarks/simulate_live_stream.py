import os
import time
import requests
import base64
import json

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_CREDS = {"login_type": "admin", "username": "admin", "password": "password"} 
# Wait, I changed password to "admin" previously in tests but left standard in .env as admin
ADMIN_CREDS["password"] = "admin"

def main():
    print("--- Phase 4: API Realtime Benchmarking ---")
    
    # 1. Login
    resp = requests.post(f"{BASE_URL}/auth/login", data=ADMIN_CREDS)
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
        resp = requests.post(
            f"{BASE_URL}/registration/register",
            headers=headers,
            data={
                "name": "Live Student A",
                "roll_number": "LIVE_A",
                "institution_id": "DEMO2026",
                "gender": "Other"
            },
            files={"file": ("sample_face.jpg", f, "image/jpeg")}
        )
    print(f"✅ Registration (Step 3) HTTP {resp.status_code}: {resp.json().get('message')}")
    
    # 3. Start Session
    resp = requests.post(
        f"{BASE_URL}/attendance/session/start",
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
    while time.time() - start_time < 10.0:
        with open(face_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
        
        t0 = time.time()
        resp = requests.post(
            f"{BASE_URL}/attendance/mark-attendance",
            headers=headers,
            json={
                "session_id": session_id,
                "image_data": f"data:image/jpeg;base64,{encoded_string}",
                "timestamp": int(time.time() * 1000)
            }
        )
        latency = (time.time() - t0) * 1000
        frames += 1
        
        try:
            recognized = resp.json().get('results', [{}])[0].get('name', 'UNKNOWN')
        except:
            recognized = "ERROR"
            
        print(f"  Frame {frames:02d} | Latency: {latency:.1f}ms | Detected: {recognized}")
        time.sleep(0.5) # Simulate 2 FPS

    print("✅ Live Stream Simulation Complete.")
    
if __name__ == "__main__":
    main()
