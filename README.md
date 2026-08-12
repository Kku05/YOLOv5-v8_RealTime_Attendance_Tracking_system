# 🎓 Real-Time Attendance Tracking System (RATS)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v5%20%2F%20v8-orange.svg)](https://docs.ultralytics.com/)
[![Dlib](https://img.shields.io/badge/dlib-20.0.1-red.svg)](http://dlib.net/)
[![macOS Apple Silicon](https://img.shields.io/badge/macOS-Apple%20Silicon%20%2F%20Metal-black.svg)](https://apple.com)

**RATS** is an automated computer vision web application designed for smart attendance tracking. It uses **Ultralytics YOLO (v5 & v8)** for face detection, **Dlib & face_recognition** for 128-dimensional biometric matching via KD-Tree, and **Liveness Verification (Eye Blink EAR & MediaPipe Hand Gestures)** to prevent spoofing and proxy attendance.

---

## 🌟 Key Features

* **Real-time Face Detection**: High-speed detection using YOLOv8 & YOLOv5.
* **Biometric Face Recognition**: 128-d facial embeddings with KD-Tree sub-millisecond nearest neighbor search.
* **Anti-Spoofing & Liveness**:
  * **Eye Blink Verification**: Dlib 68 facial landmarks measuring Eye Aspect Ratio (EAR).
  * **Hand Gesture Verification**: MediaPipe Hands detecting raised hand participation.
* **Interactive Teacher Dashboard**:
  * Teacher authentication ([users.csv](users.csv)).
  * Live camera stream with bounding box and student ID annotations.
  * Real-time attendance logging.
  * Historical attendance log viewer and filter by class and date.
* **Apple Silicon & Cross-Platform Support**: Optimized for macOS (M1/M2/M3/M4/M5 Metal MPS acceleration) and Linux/Windows.

---

## 📁 Repository Structure

```
├── Yolov8Eye.py            # Main App: YOLOv8 + Eye Blink Liveness Attendance (Port 5003)
├── Yolov8Hand.py           # Main App: YOLOv8 + MediaPipe Hand Gesture Attendance (Port 5000)
├── Yolov8Login.py          # Main App: YOLOv8 Face Recognition Attendance (Port 5000)
├── Yolov5Eye.py            # YOLOv5 + Eye Blink Attendance (Port 5001)
├── Yolov5Hand.py           # YOLOv5 + MediaPipe Hand Gesture Attendance (Port 5000)
├── Yolov5Login.py          # YOLOv5 Face Recognition Attendance (Port 5000)
│
├── shape_predictor_68_face_landmarks.dat  # Dlib 68-point landmark model (~99MB)
│
├── yolov8/                 # YOLOv8 Weights (yolov8n.pt, yolov8l.pt)
├── yolov5/                 # YOLOv5 Weights (yolov5s.pt, yolov5su.pt)
│
├── users.csv               # Teacher login credentials
├── known_faces.csv         # Enrolled student database index
├── photos/                 # Enrolled student facial images
├── attendance/             # Generated daily attendance records
│
├── templates/              # Flask Jinja2 HTML templates
├── static/                 # UI assets and illustrations
│
├── requirements.txt        # Python package dependencies
├── MAC_SETUP_AND_REQUIREMENTS.md # Detailed Mac setup and troubleshooting guide
└── PROJECT_OVERVIEW.md     # Detailed architecture and workflow document
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites (macOS)
```bash
brew install cmake pkg-config python@3.11 libpng libjpeg openblas
```

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/Kku05/YOLOv5-v8_RealTime_Attendance_Tracking_system.git
cd YOLOv5-v8_RealTime_Attendance_Tracking_system

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Application

* **Eye Blink Detection Mode (Recommended)**:
  ```bash
  python Yolov8Eye.py
  ```
  *Open your browser at `http://127.0.0.1:5003`*

* **Hand Gesture Mode**:
  ```bash
  python Yolov8Hand.py
  ```
  *Open your browser at `http://127.0.0.1:5000`*

* **Face Recognition Login Mode**:
  ```bash
  python Yolov8Login.py
  ```
  *Open your browser at `http://127.0.0.1:5000`*

---

## 🔑 Default Login Credentials

| Username | User ID |
| :--- | :--- |
| `tirth` | `AB1234CD` |
| `vishal` | `XY5678EF` |
| `ayush` | `GH9012IJ` |
| `deepak sir` | `1234QWER` |

---

## 📄 Documentation

* [Mac Setup & Requirements Guide](MAC_SETUP_AND_REQUIREMENTS.md)
* [Comprehensive Project Overview](PROJECT_OVERVIEW.md)
