# 🎯 Deep Learning Face Recognition Attendance System

An advanced, intelligent, real-time facial recognition attendance system built with state-of-the-art Deep Learning models. This system automatically detects faces, matches them against registered students with high precision, and effortlessly logs subject-wise and date-wise attendance.

---

## ✨ Features

- **🧠 Deep Learning Core**: Powered by **PyTorch**, utilizing **MTCNN** for robust face detection and **FaceNet (InceptionResnetV1)** for generating high-accuracy facial embeddings.
- **⚡ Fast & Async Backend**: Built on **FastAPI** for blisteringly fast API responses and asynchronous processing. 
- **🎥 Real-Time Monitoring**: Process camera feeds locally using **OpenCV** with a temporal stability tracker that prevents duplicate marks and false positives.
- **📊 Interactive Admin Dashboard**: A sleek, glassmorphic UI for tracking active sessions, registering students, viewing attendance history, and filtering records by date and subject.
- **🗄️ Dual Database Support**: Seamlessly switch between local **SQLite** for rapid testing or cloud-based **Firebase Firestore** for production deployments.
- **📄 Extensible Exports**: Instantly download professional attendance reports in **Excel (.xlsx)** and **PDF** formats directly from the dashboard.
- **🐳 Docker Ready**: Easily containerized for cloud deployment (Azure, AWS, GCP) using the provided `Dockerfile`.

---

## 🛠️ Technology Stack

| Component         | Technology Used                                                                 |
| ----------------- | ------------------------------------------------------------------------------- |
| **Backend API**   | Python, FastAPI, Uvicorn                                                        |
| **AI Models**     | PyTorch, facenet-pytorch (MTCNN / InceptionResnetV1), OpenCV                    |
| **Databases**     | Firebase Admin SDK (Firestore), SQLite3                                         |
| **Data Export**   | Pandas, OpenPyXL (Excel), FPDF (PDF)                                            |
| **Frontend UI**   | HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates                               |
| **Deployment**    | Docker                                                                          |

---

## 🚀 Getting Started (Local Development)

### 1. Prerequisites
- **Python 3.10+**
- **Git**
- A webcam (for registering students and scanning attendance).

### 2. Installation Setup

Clone the repository and install the dependencies within a virtual environment.

```bash
git clone https://github.com/your-username/face-attendance-system.git
cd face-attendance-system

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (use `.env.example` as a template). 

```ini
DATABASE_MODE=sqlite # Change to 'firebase' for cloud syncing
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
SESSION_SECRET_KEY=generate_a_secure_random_string

# Only required if using Firebase
FIREBASE_CREDENTIALS_PATH=firebase.json 
```

### 4. Run the Server
Start the FastAPI server locally:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to `http://localhost:8000` to access the login page and admin dashboard.

---

## ☁️ Deployment (AWS EC2)

This application can easily be deployed on an **AWS EC2** instance using Docker or systemd. Due to PyTorch and OpenCV's memory footprint, a **t3.large** instance (or larger) is recommended.

### Prerequisites
- An EC2 instance running Ubuntu 22.04+ (t3.large minimum).
- Security Group rules: Allow inbound on ports **22 (SSH)**, **80 (HTTP)**, and **443 (HTTPS)**. Do **not** expose port 8000 externally.
- A domain name pointing to your EC2 public IP.

### Deployment Steps (via Docker)

1. SSH into your EC2 instance and clone the repository.
2. Install Docker and Docker Compose.
3. Copy `.env.example` to `.env` and fill in your secrets.
4. Run the application:
   ```bash
   docker-compose up -d --build
   ```
5. Install **Nginx** and configure the reverse proxy using the provided `nginx.conf`.
6. (Crucial for Mobile) Run **Certbot** to provision an SSL certificate. Mobile browsers require HTTPS to allow camera access via `getUserMedia`.

*Note: Avoid committing `.env` or `firebase.json` text files. Use secure secret management or environment variables.*

---

## 🤝 Contributing
Contributions, issues, and feature requests are always welcome! Feel free to check the issues page.

## 📝 License
This project is licensed under the MIT License.
