# 📋 YOLO Attendance System — System Requirements & Technical Specifications

This document defines the software, hardware, and environment specifications for running the **YOLOv5/v8 Real-Time Attendance Tracking & Anti-Spoofing System**.

---

## 1. Software & Environment Requirements

| Component | Minimum Version | Recommended Version | Notes |
| :--- | :--- | :--- | :--- |
| **Python** | `3.9.x` | `3.10.x` / `3.11.x` | Required Python runtime |
| **pip** | `20.0+` | Latest | Python package manager |
| **CMake** | `3.18+` | Latest | Required to compile `dlib` C++ bindings |
| **Operating System** | macOS 11+, Windows 10/11, Ubuntu 20.04+ | macOS 14+ (Apple Silicon M1–M5) | Optimized for Apple Silicon MPS / CPU acceleration |

---

## 2. Hardware Specifications

### Minimum Requirements:
* **Processor:** 2.0 GHz Quad-Core 64-bit CPU
* **RAM:** 4 GB RAM (App uses ~200–350 MB RAM during active multi-model inference)
* **Storage:** 1.5 GB free disk space (includes YOLO weights & dlib 68-landmarks model)
* **Camera:** 720p HD integrated webcam (MacBook FaceTime HD Camera) or external USB camera

### Recommended Setup:
* **Processor:** Apple Silicon M-Series (M1 / M2 / M3 / M4 / M5) or Intel Core i7 / AMD Ryzen 7
* **RAM:** 8 GB+ RAM
* **Camera:** 1080p Full HD USB Camera (30 FPS) with good classroom/indoor lighting

---

## 3. Python Package Dependencies (`requirements.txt`)

| Package | Purpose | License |
| :--- | :--- | :--- |
| **`Flask`** | Web dashboard, role-based authentication, and video stream routing | BSD-3-Clause |
| **`opencv-python`** | Real-time webcam frame acquisition, rendering, and visual bounding boxes | Apache 2.0 |
| **`ultralytics`** | YOLOv8 and YOLOv5 neural network real-time object & person detection | AGPL-3.0 |
| **`face-recognition`** | 128-dimensional deep metric face embedding generation | MIT |
| **`dlib`** | 68-point facial landmark predictor for Anti-Spoofing Eye Aspect Ratio (EAR) | Boost 1.0 |
| **`mediapipe`** | Hand skeleton landmark tracker for Anti-Spoofing Hand Gesture Verification | Apache 2.0 |
| **`scikit-learn`** | KDTree high-speed spatial indexing for instant $\mathcal{O}(\log N)$ face recognition | BSD-3-Clause |
| **`scipy`** | Spatial Euclidean distance metrics for eye aspect ratios | BSD-3-Clause |
| **`numpy`** | Multi-dimensional array operations on video frames and face vectors | BSD-3-Clause |
| **`setuptools`** | Backward-compatible `pkg_resources` interface (`<80`) | MIT |

---

## 4. Port & Networking
* **Default Port:** `5001` (avoids conflict with macOS default AirPlay Receiver on port 5000).
* **Localhost URL:** `http://127.0.0.1:5001`
