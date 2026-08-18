# 🎯 YOLOv5-v8 Real-Time Attendance Tracking & Anti-Spoofing System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)](https://ultralytics.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Google-blueviolet.svg)](https://mediapipe.dev/)

An enterprise-grade, multi-engine biometric attendance tracking system combining **YOLOv8**, **YOLOv5**, **MediaPipe Hand Skeleton tracking**, **Dlib 68-Point Facial Landmarks Anti-Spoofing (Eye Blink EAR)**, and **Spatial KDTree Face Recognition** into a unified web application.

---

## 🚀 Quick Start (macOS & Linux)

```bash
# 1. Clone the repository
git clone https://github.com/Kku05/YOLOv5-v8_RealTime_Attendance_Tracking_system.git
cd YOLOv5-v8_RealTime_Attendance_Tracking_system

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip setuptools wheel
pip install cmake
pip install -r requirements.txt

# 4. Start the application
python app.py
```
Open **[http://127.0.0.1:5001](http://127.0.0.1:5001)** in your browser.

---

## 🔑 Pre-Configured Accounts

| Username | Password | Role | Assigned Classes |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | Administrator | `ALL` (Full Admin Access + Delete permissions) |
| **`tirth`** | `AB1234CD` | Lead Instructor | `CSE-AIML`, `CSE-4A` (Can also take substitute sessions) |
| **`teacher`** | `1234` | Faculty | `IT-A`, `Grade-11` |

---

## ✨ 6 AI Detection Engines

1. ⚡ **YOLOv8 + Eye Blink**: Neural object detection combined with Dlib 68-landmark Eye Aspect Ratio (EAR) anti-spoofing verification.
2. ✋ **YOLOv8 + Hand Gesture**: YOLOv8 face recognition with MediaPipe 21-keypoint hand gesture liveness check.
3. 👤 **YOLOv8 Standard Face**: High-speed real-time face tracking.
4. 👁️ **YOLOv5 + Eye Blink**: YOLOv5s neural network with eye blink verification.
5. ✋ **YOLOv5 + Hand Gesture**: YOLOv5s neural network with hand landmark verification.
6. 👤 **YOLOv5 Standard Face**: Direct YOLOv5s face classification baseline.

---

## 📚 Documentation

- 📖 **[Project Architecture & Workflow Specification](PROJECT_OVERVIEW.md)**: Full pipeline diagrams, AI engines, database schema, and performance benchmarks.
- 📋 **[System & Technical Requirements](REQUIREMENTS.md)**: Hardware, camera, RAM, and Python dependency specifications.
- ⚙️ **[Installation & Setup Guide](SETUP.md)**: Step-by-step installation, student enrollment guide, and troubleshooting.
- 📜 **[Third-Party License Audit](THIRD_PARTY_LICENSES.md)**: Open-source legal compliance audit.

---

## 📁 Repository Structure

```
YOLOv5-v8_RealTime_Attendance_Tracking_system/
├── app.py                                  # Core Flask application & multi-model pipeline
├── users.csv                               # User credentials & RBAC permissions (PBKDF2 SHA-256)
├── classes.csv                             # Course offerings & department index
├── known_faces.csv                         # Biometric face embeddings & student registry
├── attendance/                             # Structured attendance records by instructor & class
├── shape_predictor_68_face_landmarks.dat   # Dlib 68-point facial landmark model
├── yolov8/yolov8n.pt                       # YOLOv8 neural network weights
├── yolov5/yolov5s.pt                       # YOLOv5 neural network weights
├── templates/                              # Modern Flask UI templates
│   ├── login.html
│   ├── home.html
│   ├── take_attendance.html
│   ├── register_student.html
│   └── see_attendance.html
├── static/css/                             # Premium dark/glassmorphic styling
├── requirements.txt                        # Python dependencies
├── REQUIREMENTS.md                         # Technical specifications
├── SETUP.md                                # Setup & configuration guide
├── PROJECT_OVERVIEW.md                     # Architecture specification
├── THIRD_PARTY_LICENSES.md                 # Open-source license audit
├── LICENSE                                 # MIT License
└── README.md                               # Project documentation
```

---

## 📜 License

This project is licensed under the **[MIT License](LICENSE)** (Copyright © 2026 Tirth / Kku05).
