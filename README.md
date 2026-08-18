# 🎓 Real-Time Attendance Tracking System (RATS)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v5%20%2F%20v8-orange.svg)](https://docs.ultralytics.com/)
[![Dlib](https://img.shields.io/badge/dlib-20.0.1-red.svg)](http://dlib.net/)
[![macOS Apple Silicon](https://img.shields.io/badge/macOS-Apple%20Silicon%20%2F%20Metal-black.svg)](https://apple.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**RATS** is an enterprise-grade automated computer vision platform designed for smart classroom attendance tracking. It uses **Ultralytics YOLO (v8 & v5)** for person and face detection, **Dlib & face_recognition** for 128-dimensional biometric matching via KD-Tree, and **Dual Anti-Spoofing Verification (Eye Blink EAR & MediaPipe 3D Hand Gestures)** to prevent photo and proxy attendance.

---

## 🌟 Key Features

* **Unified Enterprise Web App (`app.py`)**: All 6 AI detection engines dynamically switchable inside a single web interface.
* **Biometric Face Recognition**: 128-D facial embeddings with KD-Tree spatial sub-millisecond nearest neighbor matching.
* **Dual Anti-Spoofing & Liveness**:
  * **Eye Blink Verification**: Dlib 68 facial landmarks measuring Eye Aspect Ratio (EAR < 0.28).
  * **Hand Gesture Verification**: MediaPipe Hands tracking 21 3D skeleton joints.
* **Student Face & Profile Registry**:
  * Enroll students using live webcam snapshots or image uploads with real-time face embedding validation.
  * Role-based deletion protection (Admin only).
* **Institutional Academic Catalog & Substitute Support**:
  * Central class catalog (`classes.csv`) and teacher assignments (`users.csv`).
  * Automatic `[Substitute Session]` audit tagging when covering for colleagues.
  * Cross-instructor attendance log discovery and PDF/CSV reporting.
* **Security Hardening**:
  * Salted cryptographic password hashes (`werkzeug.security` scrypt).
  * Persistent 32-byte session secret token.

---

## 📁 Repository Structure

```
├── app.py                      # Unified Enterprise Web Application [Port 5001]
├── run_mac.sh                  # macOS Interactive Terminal Launcher
│
├── shape_predictor_68_face_landmarks.dat  # Dlib 68-point landmark model (~99MB)
│
├── yolov8/                     # Pretrained YOLOv8 Weights (yolov8n.pt, yolov8l.pt)
├── yolov5/                     # Pretrained YOLOv5 Weights (yolov5s.pt, yolov5su.pt)
│
├── classes.csv                 # Institutional class catalog
├── users.csv                   # User database (salted scrypt hashes & roles)
├── known_faces.csv             # Enrolled student database index
├── photos/                     # Enrolled student portrait images gallery
├── attendance/                 # Generated session logs (attendance/<instructor>/<class>/<date>/)
│
├── templates/                  # Jinja2 HTML templates
│   ├── login.html              # Secure instructor/admin login
│   ├── home.html               # Teacher dashboard with assigned class pills
│   ├── register_student.html   # Student webcam enrollment & directory management
│   ├── take_attendance.html    # Live multi-model AI camera stream & real-time attendance feed
│   └── see_attendance.html     # Historical attendance analytics & substitute discovery
│
├── static/                     # UI assets and illustrations
├── legacy/                     # Standalone legacy scripts
│
├── requirements.txt            # Python package dependencies
├── MAC_SETUP_AND_REQUIREMENTS.md # Detailed Mac setup and troubleshooting guide
└── PROJECT_OVERVIEW.md         # Detailed architecture and workflow document
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites (macOS)
```bash
brew install cmake pkg-config python@3.11 libpng libjpeg openblas
```

### 2. Setup Virtual Environment
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
> Open your browser at: **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

Or use the interactive terminal launcher:
```bash
./run_mac.sh
```

---

## 🔑 Default Login Credentials

| Username | Password / Security ID | Assigned Role | Assigned Classes |
| :--- | :--- | :--- | :--- |
| **`admin`** | **`admin123`** | **Administrator** | `ALL` *(Full system access & student profile deletion)* |
| **`tirth`** | **`AB1234CD`** | **Lead Instructor** | `CSE-AIML`, `CSE-4A` *(Assigned + Substitute access)* |
| **`teacher`** | **`1234`** | **Faculty** | `IT-A`, `Grade-11` *(Assigned + Substitute access)* |

---

## 📄 Documentation

* [Mac Setup & Requirements Guide](MAC_SETUP_AND_REQUIREMENTS.md)
* [Comprehensive Project Overview](PROJECT_OVERVIEW.md)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
