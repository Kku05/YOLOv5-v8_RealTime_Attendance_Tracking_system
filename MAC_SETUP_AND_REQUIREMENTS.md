# 🍏 RATS: Mac Setup & Requirements Guide

**Project:** Real-Time Attendance Tracking System (RATS)  
**Platform:** macOS (Apple Silicon M1/M2/M3/M4/M5 and Intel x86_64)  
**Python Version:** Python 3.11  

---

## 📌 1. System-Level Prerequisites on macOS

Ensure you have Homebrew and native C/C++ compilation tools installed:

```bash
# 1. Ensure Homebrew is in PATH
export PATH="/opt/homebrew/bin:$PATH"

# 2. Install CMake, pkg-config, Python 3.11 and image libraries
brew install cmake pkg-config python@3.11 libpng libjpeg openblas
```

---

## 📦 2. Python Dependencies (`requirements.txt`)

| Package | Purpose |
| :--- | :--- |
| **`Flask`** | Web server, video streaming MJPEG endpoints, and web UI routes |
| **`opencv-python`** | HD camera frame capture, rendering bounding boxes and overlays |
| **`ultralytics`** | YOLOv8 and YOLOv5 person/object detection |
| **`dlib`** | 68-point facial landmark predictor (`shape_predictor_68_face_landmarks.dat`) |
| **`face-recognition`** | 128-dimensional deep face embedding extraction |
| **`scikit-learn`** | KDTree spatial index for $\mathcal{O}(\log N)$ nearest-neighbor face lookups |
| **`scipy`** | Euclidean distance calculation for Eye Aspect Ratio (EAR) blink detection |
| **`mediapipe==0.10.14`** | Real-time 21-point hand skeleton tracking and gesture verification |
| **`setuptools<80`** | `pkg_resources` compatibility layer for `face_recognition_models` |

---

## 🚀 3. How to Activate & Run the Application

```bash
# 1. Open Terminal and navigate to the project directory
cd "/Users/tirth/Downloads/my project/YOLOv5-v8_RealTime_Attendance_Tracking_system"

# 2. Activate the macOS virtual environment
source venv/bin/activate

# 3. Launch the unified application
python app.py
```

Open your browser at **[http://127.0.0.1:5001](http://127.0.0.1:5001)**.

You can also use the interactive terminal launcher:
```bash
./run_mac.sh
```

---

## 🔑 4. Active Login Credentials & Roles

| Username | Password / Security ID | Assigned Role | Assigned Classes |
| :--- | :--- | :--- | :--- |
| **`admin`** | **`admin123`** | **Administrator** | `ALL` *(All institutional classes & profile deletion)* |
| **`tirth`** | **`AB1234CD`** | **Lead Instructor** | `CSE-AIML`, `CSE-4A` *(Assigned + Substitute access)* |
| **`teacher`** | **`1234`** | **Faculty** | `IT-A`, `Grade-11` *(Assigned + Substitute access)* |

---

## 💡 5. macOS Troubleshooting & Tips

1. **Camera Permission on Mac**:
   - If the video feed is blank or black, grant Camera access to Terminal / IDE in:
     `System Settings > Privacy & Security > Camera`.
2. **AirPlay Port 5000 Conflict**:
   - macOS uses port `5000` for AirPlay Receiver. The application defaults to port `5001`. You can customize the port anytime:
     ```bash
     PORT=8080 python app.py
     ```
3. **Hardware Acceleration**:
   - PyTorch and OpenCV on macOS Apple Silicon leverage hardware acceleration natively.
