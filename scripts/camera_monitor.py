"""
CLI Script: Real-time camera attendance monitor with session support.
Opens webcam, detects faces, and marks attendance via API.
Draws bounding boxes with names and tracking status on the live feed.
Requires an active session to be running on the server.
"""

import time
import base64
import sys

import cv2
import requests

API_BASE = "http://localhost:8000/api"
FRAME_INTERVAL = 0.5  # Send a frame every 0.5 seconds (~2 FPS)


def check_session():
    """Check if a session is active on the server."""
    try:
        resp = requests.get(f"{API_BASE}/session/status", timeout=5)
        data = resp.json()
        return data.get("active", False), data.get("session", {})
    except Exception:
        return False, {}


def start_session_cli():
    """Prompt user and start a session via API."""
    subject = input("  Enter subject/class name: ").strip()
    if not subject:
        print("  ❌ Subject name is required.")
        return False

    try:
        resp = requests.post(
            f"{API_BASE}/session/start",
            json={"subject_name": subject},
            timeout=10,
        )
        data = resp.json()
        if data.get("success"):
            print(f"  ✅ Session started: {subject}")
            return True
        else:
            print(f"  ❌ {data.get('detail', 'Could not start session')}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def end_session_cli():
    """End the active session via API."""
    try:
        resp = requests.post(f"{API_BASE}/session/end", timeout=5)
        data = resp.json()
        if data.get("success"):
            session = data.get("session", {})
            print(f"  📕 Session ended: {session.get('subject_name', '?')} — "
                  f"{session.get('attendance_count', 0)} students marked")
        return True
    except Exception as e:
        print(f"  ⚠️ Error ending session: {e}")
        return False


def main():
    print("=" * 55)
    print("  Face Recognition — Live Attendance Monitor (CLI)")
    print("=" * 55)

    # ── Check or start session ──
    active, session_info = check_session()
    if active:
        print(f"\n📗 Active session found: {session_info.get('subject_name', '?')}")
        use = input("  Use this session? (Y/n): ").strip().lower()
        if use == 'n':
            end_session_cli()
            if not start_session_cli():
                return
    else:
        print("\n⚠️  No active session.")
        if not start_session_cli():
            return

    # ── Open webcam ──
    print("\n📷 Opening camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera.")
        return

    print("✅ Camera opened. Press Q to quit, E to end session.\n")

    last_send_time = 0
    detection_results = []
    marked_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        # Send frame at configured interval
        if current_time - last_send_time >= FRAME_INTERVAL:
            last_send_time = current_time

            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            b64_frame = base64.b64encode(buffer).decode('utf-8')

            try:
                response = requests.post(
                    f"{API_BASE}/mark-attendance",
                    json={"frame": b64_frame},
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()

                    if not data.get("session_active", True) and not data.get("success", True):
                        # Session ended externally
                        print("  ⚠️ Session is no longer active on the server.")
                        detection_results = []
                    else:
                        detection_results = data.get("results", [])

                        for face in detection_results:
                            status = face["status"]
                            if status == "marked":
                                marked_count += 1
                                print(f"  ✅ Attendance marked: {face['name']} "
                                      f"({face['confidence']:.1%}) — Total: {marked_count}")
                            elif status == "tracking":
                                ft = face.get("frames_tracked", 0)
                                fn = face.get("frames_needed", 4)
                                print(f"  🔍 Tracking: {face['name']} "
                                      f"({ft}/{fn} frames) — {face['confidence']:.1%}")

            except requests.exceptions.ConnectionError:
                detection_results = []
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
                detection_results = []

        # ── Draw bounding boxes ──
        for face in detection_results:
            if face.get("box") and len(face["box"]) == 4:
                x1, y1, x2, y2 = [int(v) for v in face["box"]]
                status = face["status"]

                # Color based on status
                if status == "marked":
                    color = (0, 220, 100)    # green
                elif status == "already_marked" or status == "cooldown":
                    color = (0, 200, 255)    # yellow
                elif status == "tracking":
                    color = (255, 140, 80)   # blue (BGR)
                else:
                    color = (0, 80, 255)     # red

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                label = face["name"]
                if face["confidence"] > 0:
                    label += f" ({face['confidence']:.0%})"
                if status == "tracking":
                    ft = face.get("frames_tracked", 0)
                    fn = face.get("frames_needed", 4)
                    label += f" [{ft}/{fn}]"
                elif status == "marked":
                    label += " ✓"

                # Label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x1, y1 - label_size[1] - 10),
                              (x1 + label_size[0] + 6, y1), color, -1)
                cv2.putText(frame, label, (x1 + 3, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Show info overlay
        cv2.putText(frame, "Face Attendance | Q=Quit  E=End Session",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Face Attendance Monitor", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            print("\n📕 Ending session...")
            end_session_cli()
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n👋 Monitor stopped. Total marked: {marked_count}")


if __name__ == "__main__":
    main()
