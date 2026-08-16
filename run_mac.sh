#!/usr/bin/env bash
# ==============================================================================
# RATS: Real-Time Attendance Tracking System - macOS Interactive Launcher
# ==============================================================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "  🍏 Real-Time Attendance Tracking System (macOS Launcher)"
echo "=========================================================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment 'venv' not found!"
    echo "Creating virtual environment using python3.11..."
    python3.11 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "Select the Attendance Tracking Mode to run:"
echo "----------------------------------------------------------"
echo "  [1] 🌟 Unified System (All Modes in One App) [Port 5001] [Recommended]"
echo "  [2] YOLOv8 + Eye Blink Liveness Attendance [Port 5003]"
echo "  [3] YOLOv8 + Hand Gesture Liveness Attendance [Port 5002]"
echo "  [4] YOLOv8 Standard Face Login Attendance [Port 5004]"
echo "  [5] YOLOv5 + Eye Blink Liveness Attendance [Port 5001]"
echo "  [6] YOLOv5 + Hand Gesture Liveness Attendance [Port 5005]"
echo "  [7] YOLOv5 Standard Face Login Attendance [Port 5006]"
echo "  [8] Exit"
echo "----------------------------------------------------------"
read -p "Enter your choice [1-8]: " choice

case $choice in
    1)
        echo "🚀 Starting Unified Attendance System on http://127.0.0.1:5001..."
        python app.py
        ;;
    2)
        echo "🚀 Starting YOLOv8 Eye Blink Detection on http://127.0.0.1:5003..."
        python legacy/Yolov8Eye.py
        ;;
    3)
        echo "🚀 Starting YOLOv8 Hand Gesture Detection on http://127.0.0.1:5002..."
        python legacy/Yolov8Hand.py
        ;;
    4)
        echo "🚀 Starting YOLOv8 Face Login Attendance on http://127.0.0.1:5004..."
        python legacy/Yolov8Login.py
        ;;
    5)
        echo "🚀 Starting YOLOv5 Eye Blink Detection on http://127.0.0.1:5001..."
        python legacy/Yolov5Eye.py
        ;;
    6)
        echo "🚀 Starting YOLOv5 Hand Gesture Detection on http://127.0.0.1:5005..."
        python legacy/Yolov5Hand.py
        ;;
    7)
        echo "🚀 Starting YOLOv5 Face Login Attendance on http://127.0.0.1:5006..."
        python legacy/Yolov5Login.py
        ;;
    8)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid selection. Exiting."
        exit 1
        ;;
esac
