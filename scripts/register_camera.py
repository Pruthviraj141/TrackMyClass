"""
CLI Script: 30-second camera registration.
Captures face frames from webcam and sends to the registration API.
"""

import sys
import time
import base64
import json

import cv2
import requests

API_URL = "http://localhost:8000/api/register"
CAPTURE_DURATION = 30  # seconds
CAPTURE_INTERVAL = 1.0  # seconds between captures


def main():
    print("=" * 50)
    print("  Face Recognition — Student Registration")
    print("=" * 50)
    
    # Get student details
    name = input("\n👤 Enter student name: ").strip()
    if not name or len(name) < 2:
        print("❌ Name must be at least 2 characters.")
        return
    
    roll_number = input("🔢 Enter roll number: ").strip()
    if not roll_number:
        print("❌ Roll number is required.")
        return
    
    gender = input("⚧ Enter gender (male/female/other): ").strip().lower()
    if gender not in ("male", "female", "other"):
        print("❌ Gender must be 'male', 'female', or 'other'.")
        return
    
    # Open webcam
    print("\n📷 Opening camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera.")
        return
    
    print(f"\n🎬 Recording will start in 3 seconds...")
    print("   Move your head slowly for best results.")
    time.sleep(3)
    
    frames = []
    start_time = time.time()
    last_capture = 0
    
    print(f"\n🔴 RECORDING — {CAPTURE_DURATION} seconds")
    print("   [Look straight, then slowly turn left/right and tilt up/down]")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        elapsed = time.time() - start_time
        
        if elapsed >= CAPTURE_DURATION:
            break
        
        # Capture frame at interval
        if elapsed - last_capture >= CAPTURE_INTERVAL:
            last_capture = elapsed
            
            # Encode to JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            b64_frame = base64.b64encode(buffer).decode('utf-8')
            frames.append(b64_frame)
            
            remaining = int(CAPTURE_DURATION - elapsed)
            print(f"   📸 Frame {len(frames)} captured — {remaining}s remaining")
        
        # Show preview
        cv2.putText(frame, f"Recording: {int(CAPTURE_DURATION - elapsed)}s left", 
                     (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"Frames: {len(frames)}", 
                     (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Registration — Press Q to stop early", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✅ Captured {len(frames)} frames.")
    
    if len(frames) < 5:
        print(f"❌ Need at least 5 frames, got {len(frames)}. Try again.")
        return
    
    # Send to API
    print("🔄 Sending to registration API...")
    payload = {
        "name": name,
        "roll_number": roll_number,
        "gender": gender,
        "frames": frames,
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print(f"\n🎉 {data['message']}")
            print(f"   Student ID: {data['student_id']}")
        else:
            print(f"\n❌ Registration failed: {data.get('detail', 'Unknown error')}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the server. Is it running on http://localhost:8000?")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
