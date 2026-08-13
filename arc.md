# TrackMyClass: End-to-End System Architecture

This document provides a comprehensive technical breakdown of the `TrackMyClass` face recognition attendance system, covering user flow, system logic, data lifecycle, and backend deep learning integrations.

---

## 1. System Overview

**TrackMyClass** is an intelligent, real-time facial recognition attendance system. It replaces manual roll calls by dynamically scanning video feeds, detecting faces, recognizing registered students, and automatically marking attendance in a database.

**Core Technology Stack:**
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (MediaDevices API for camera), Jinja2 Templates.
- **Backend API**: Python 3.10+, FastAPI, Uvicorn, Asynchronous processing.
- **Deep Learning / AI**: PyTorch, `facenet-pytorch`.
  - **MTCNN**: Multi-task Cascaded Convolutional Networks for Face Detection & Cropping.
  - **FaceNet (InceptionResnetV1)**: For generating 512-dimensional facial embeddings.
- **Computer Vision**: OpenCV (handling image conversions).
- **Databases**: SQLite (Local Dev) or Firebase Firestore (Production Cloud).
- **Deployment**: Docker, Docker Compose, Nginx Reverse Proxy, AWS EC2, Systemd.

---

## 2. End-to-End User Flow

The application serves primarily two roles: the **Admin (Teacher/Professor)** and the **Student**.

### A. Admin Flow
1. **Authentication**: Admin logs into the dashboard via the `/login` portal.
2. **Dashboard**: The admin views the central dashboard (`/admin/dashboard`) showing today's attendance stats and past records.
3. **Session Management**: The admin selects a class/subject and starts a new tracking session.
4. **Live Monitoring**: The admin opens the `/monitor` page. A live camera feed begins, continuously capturing frames and showing real-time feedback (e.g., bounding boxes around recognized faces, displaying names like "Pruthvi - Present").
5. **Exporting Data**: After class, the admin ends the session and can download an Excel or PDF report of the day's attendance.

### B. Student Registration Flow
1. **Access Registration**: A student goes to the `/` (root) registration page.
2. **Form Submission**: The student enters their Name, Roll Number, and Department.
3. **Face Capture**: The web application requests camera permissions (preferring the rear-facing camera on mobile or default webcam on desktop). The student captures their face.
4. **Processing**: A loading overlay appears while the backend processes the image, ensures exactly one face is present, and saves their facial embedding to the database.
5. **Confirmation**: A success message is shown, and the student is now registered in the system.

---

## 3. End-to-End System Flow & Data Lifecycle

### A. Registration Data Flow
1. **Frontend**: JS captures a base64 encoded snapshot from the `<video>` element and posts it to `/api/v1/register/camera` along with student metadata.
2. **Backend Router**: The FastAPI route receives the payload, decoding the base64 image into a Numpy array.
3. **AI Pipeline**:
   - The image is passed to the **MTCNN Singleton**. It scans the image and returns bounding boxes.
   - If `0` faces or `>1` faces are detected, the API returns a 400 error.
   - If exactly `1` face is found, it is cropped and resized.
   - The cropped face is passed to the **FaceNet Singleton**, which passes it through the ResNet layers to generate a **512-dimensional vector** (embedding).
4. **Database Insertion**: The embedding vector (serialized to bytes or JSON) and the student's metadata are saved into SQLite/Firebase.
5. **Cache Invalidation**: The in-memory embedding cache is signaled to reload to include the new student.

### B. Live Monitoring & Attendance Data Flow
1. **Session Initialization**: When an admin starts a session, the backend pulls **all** student embeddings from the database and loads them into a fast **Numpy In-Memory Matrix** (`optimized_recognition.py`).
2. **Streaming Frames**: The `/monitor` page uses JS `setInterval` to continuously grab frames from the webcam (e.g., 5-10 times a second) and sends them as base64 to `/api/v1/attendance/process_frame`.
3. **Detection (MTCNN)**: The backend decodes the frame and runs MTCNN to find all faces in the image. Multiple faces can be detected simultaneously.
4. **Recognition (FaceNet + Vector Math)**:
   - Every detected face is cropped and converted into a 512-D embedding by FaceNet.
   - Instead of querying the database, the backend uses **Cosine Similarity** via Numpy matrix multiplication to compare the new embedding against all cached embeddings in a fraction of a millisecond.
   - If the similarity score exceeds the confidence threshold (e.g., > 0.75), a potential match is found.
5. **Temporal Tracker**: 
   - A single frame match is not enough (to prevent AI hallucinations or momentary false positives).
   - The match is passed to the `TemporalTracker` service. 
   - Only if the same student is confidently recognized for *N* consecutive frames (e.g., 4 frames), do they pass validation.
6. **Database Logging**: Once temporally validated, the backend checks if the student was already marked present today for this subject. If not, a new attendance record is inserted into the database.
7. **Frontend Feedback**: The API responds with bounding box coordinates and the recognized names. The frontend draws green squares over the video feed to give the Admin real-time visual confirmation.

---

## 4. Deep-Dive Backend Architecture

The backend is modularized for scalability, separating routing, business logic, and ML inference.

### Directory Structure Overview
- `backend/main.py`: The FastAPI entry point. Handles lifespan events (preloading gigabyte-sized ML models on startup so the first request isn't slow).
- `backend/routers/`: Connects HTTP endpoints to internal services.
- `backend/services/`: The core business logic.
- `backend/models/`: AI model singletons and database schemas.
- `backend/database/`: Database connection logic (Firebase / SQLite adapters).

### Key Architectural Patterns
1. **Singleton AI Models**: Loading PyTorch models takes seconds and consumes massive RAM. `get_detector()` (MTCNN) and `get_facenet_model()` are instantiated exactly once at application startup.
2. **In-Memory Vector Cache**: The bottleneck of face recognition is DB lookups. By caching all 512-D vectors in RAM as a Numpy array when a session starts, checking 1,000 faces takes under 1ms. 
3. **Temporal Stability Tracking**: Solves the "flickering" face problem. AI can easily misidentify a blurry frame. A temporal buffer requires continuous temporal stability before triggering a database write.
4. **Abstracted Database Layer**: The application can seamlessly switch between SQLite (for rapid local dev) and Firebase Firestore (for distributed cloud production) via a common interface, controlled entirely by the `.env` file.

### Infrastructure & Deployment
- **Multi-Stage Docker**: A slim Python image is used to keep container size manageable, though PyTorch inherently requires significant space.
- **Reverse Proxy**: Nginx handles client connections, enabling HTTPS via Let's Encrypt (Certbot), which is strictly required by mobile browsers to grant camera access (`getUserMedia` API).
- **Gunicorn/Uvicorn**: Runs the FastAPI async loop efficiently on AWS EC2 hardware.

---

## 5. Future Upgrade Path Considerations
- **Liveness Detection**: Integrating blink detection or depth-sensing to prevent presentation attacks (holding up a photo to the camera).
- **GPU Acceleration**: Modifying the Dockerfile to include NVIDIA CUDA libraries to run MTCNN/FaceNet on GPUs, increasing processing from ~5 FPS to 30+ FPS.
- **Batch Processing**: Instead of processing faces sequentially in a frame, batch them into a single tensor for FaceNet to process simultaneously.
- **Vector Database**: For scaling beyond 10,000+ students, replacing the Numpy cache with a dedicated Vector DB like Qdrant or Milvus.
