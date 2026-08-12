# 🍏 RATS: Mac Setup & Requirements Guide

**Project:** Real-Time Attendance Tracking System using YOLO & Face Recognition  
**Platform:** macOS (Apple Silicon M1/M2/M3/M4/M5 and Intel x86_64)  
**Python Version:** Python 3.11  

---

## 📌 1. What Happened Moving from Windows to Mac

When moving this project from Windows to macOS:

1. **Old Windows Virtual Environment (`rats/`)**:
   - Virtual environments contain hardcoded binary executables (`.exe`, `.ps1`) and system paths from Windows. They cannot be transferred across OSes.
   - **Solution:** Replaced with a native macOS `venv` built on Python 3.11.
2. **Windows Wheel (`.whl`) Files**:
   - `dlib-19.24.99-cp312-cp312-win_amd64.whl` only works on Windows x86_64.
   - **Solution:** On Apple Silicon Mac, `dlib` is compiled natively with `cmake`.
3. **`dlib` Compilation on Apple Silicon**:
   - `dlib` requires `cmake`, `pkg-config`, `libpng`, `libjpeg`, and `openblas` to build on macOS ARM64.
4. **Camera Index**:
   - Mac built-in FaceTime HD camera is **Camera Index 0** (`cv2.VideoCapture(0)`).
5. **AirPlay Receiver Port Conflict (Port 5000)**:
   - macOS uses port `5000` for AirPlay Receiver by default. `Yolov8Eye.py` runs on **Port 5003** to prevent conflicts.

---

## 🛠️ 2. System-Level Prerequisites

Install Homebrew and system build tools:

```bash
# 1. Add Homebrew to PATH
export PATH="/opt/homebrew/bin:$PATH"

# 2. Install CMake, pkg-config, and Python 3.11
brew install cmake pkg-config python@3.11 libpng libjpeg openblas
```

---

## 📦 3. Python Packages & Purpose

| Package | Version | Purpose |
| :--- | :--- | :--- |
| **`Flask`** | `3.1.3` | Web server, video streaming endpoints, and UI routes |
| **`opencv-python`** | `5.0.0` | Camera frame capture and video stream processing |
| **`ultralytics`** | `8.4.118` | YOLOv5 and YOLOv8 object/face detection (Metal MPS accelerated) |
| **`dlib`** | `20.0.1` | 68-point facial landmark predictor (`shape_predictor_68_face_landmarks.dat`) |
| **`face-recognition`** | `1.3.0` | 128-dimensional face embedding extraction |
| **`scikit-learn`** | `1.9.0` | KDTree spatial index for fast nearest-neighbor face lookups |
| **`scipy`** | `1.17.1` | Euclidean distance calculations for Eye Aspect Ratio (EAR) |
| **`mediapipe`** | `0.10.14` | Real-time hand landmark tracking and gesture recognition |
| **`setuptools`** | `<80` | Required for `pkg_resources` compatibility in `face_recognition_models` |

---

## 🚀 4. How to Activate & Run the Project

Open Terminal and execute:

```bash
# 1. Navigate to the project directory
cd "/Users/tirth/Downloads/my project/RATS_YOLO_ALL"

# 2. Activate the virtual environment
source venv/bin/activate
```

### Choose an Attendance Mode:

#### 👁️ Mode 1: YOLOv8 + Eye Blink Detection (Recommended)
```bash
python Yolov8Eye.py
```
> Open browser at: **`http://127.0.0.1:5003`**  
> *Liveness check: Student must look at the camera and blink to mark attendance.*

#### ✋ Mode 2: YOLOv8 + Hand Gesture Detection
```bash
python Yolov8Hand.py
```
> Open browser at: **`http://127.0.0.1:5000`**  
> *Liveness check: Student must raise a hand in front of the camera to mark attendance.*

#### 👤 Mode 3: YOLOv8 Standard Face Login
```bash
python Yolov8Login.py
```
> Open browser at: **`http://127.0.0.1:5000`**

---

## 🔑 5. Test Login Credentials

From [users.csv](file:///Users/tirth/Downloads/my%20project/RATS_YOLO_ALL/users.csv):

| Username | User ID |
| :--- | :--- |
| `tirth` | `AB1234CD` |
| `vishal` | `XY5678EF` |
| `ayush` | `GH9012IJ` |
| `deepak sir` | `1234QWER` |

---

## 💡 6. Mac Troubleshooting

* **Black Camera Feed**: Grant Camera permission to your Terminal or IDE in **System Settings > Privacy & Security > Camera**.
* **Port 5000 in use**: Disable AirPlay Receiver in **System Settings > General > AirDrop & AirPlay > AirPlay Receiver: OFF** or run `Yolov8Eye.py` (Port 5003).
* **Adding New Students**: Add clear image to `photos/` and add line in `known_faces.csv` (`photos/name.jpg,Student Name,ID`).
