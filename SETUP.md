# 🚀 YOLO Attendance System — Setup & Installation Guide

A complete installation, hardware configuration, and startup guide for the **YOLOv5/v8 Real-Time Attendance Tracking & Anti-Spoofing System**.

---

## 1. Quick Start (macOS & Linux)

### Step 1: Open Terminal & Navigate to Project
```bash
cd "/Users/tirth/Downloads/my project/YOLOv5-v8_RealTime_Attendance_Tracking_system"
```

### Step 2: Activate the Virtual Environment
```bash
source venv/bin/activate
```
*(If you need to recreate the environment: `python3.11 -m venv venv && source venv/bin/activate`)*

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install cmake
pip install -r requirements.txt
```

### Step 4: Start the Application
```bash
python app.py
```
Open your browser at:
👉 **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

---

## 2. Pre-Configured Login Credentials

| Username | Password | Role | Assigned Classes |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | Administrator | `ALL` (Full Admin Access + Delete permissions) |
| **`tirth`** | `AB1234CD` | Lead Instructor | `CSE-AIML`, `CSE-4A` (Can also take substitute sessions) |
| **`teacher`** | `1234` | Faculty | `IT-A`, `Grade-11` |

---

## 3. How to Use the System

### 📸 1. Registering a Student
1. Log in to the dashboard.
2. Click **"Register Student"**.
3. Fill in **Student Name**, **Student ID**, and select their **Class**.
4. Click **"Capture Webcam Snapshot"** (or upload an image) and click **"Save & Enroll Student"**.
5. The system instantly crops the face, calculates the 128-d embedding, and updates [`known_faces.csv`](known_faces.csv).

### 📹 2. Taking Attendance
1. Click **"Take Attendance"**.
2. Select the **Class** and choose one of the **6 AI Detection Engines**:
   - ⚡ `YOLOv8 + Eye Blink` (Recommended: High accuracy + Anti-spoofing)
   - ✋ `YOLOv8 + Hand Gesture` (Raise hand to mark present)
   - 👤 `YOLOv8 Standard Face` (Direct fast face tracking)
   - 👁️ `YOLOv5 + Eye Blink`
   - ✋ `YOLOv5 + Hand Gesture`
   - 👤 `YOLOv5 Standard Face`
3. Click **"Start Live Attendance"**.
4. The live webcam stream will detect registered students and log their attendance with duplicate lockout.
5. Click **"Save Attendance & Exit"** when the class session is finished.

### 📊 3. Viewing Records
1. Click **"Attendance Records"**.
2. Filter by **Class** and **Date**.
3. View summary stats (Present, Absent, Attendance Rate %) and download CSV reports.

---

## 4. One-Click Startup Script (`run_mac.sh`)
You can also launch the app with a single command:
```bash
./run_mac.sh
```
