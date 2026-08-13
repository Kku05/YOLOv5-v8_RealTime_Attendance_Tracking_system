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
echo "  [1] YOLOv8 + Eye Blink Liveness Attendance (Port 5003) [Recommended]"
echo "  [2] YOLOv8 + Hand Gesture Liveness Attendance (Port 5002)"
echo "  [3] YOLOv8 Standard Face Login Attendance (Port 5004)"
echo "  [4] YOLOv5 + Eye Blink Liveness Attendance (Port 5001)"
echo "  [5] YOLOv5 + Hand Gesture Liveness Attendance (Port 5005)"
echo "  [6] YOLOv5 Standard Face Login Attendance (Port 5006)"
echo "  [7] Exit"
echo "----------------------------------------------------------"
read -p "Enter your choice [1-7]: " choice

case $choice in
    1)
        echo "🚀 Starting YOLOv8 Eye Blink Detection on http://127.0.0.1:5003..."
        python Yolov8Eye.py
        ;;
    2)
        echo "🚀 Starting YOLOv8 Hand Gesture Detection on http://127.0.0.1:5002..."
        python Yolov8Hand.py
        ;;
    3)
        echo "🚀 Starting YOLOv8 Face Login Attendance on http://127.0.0.1:5004..."
        python Yolov8Login.py
        ;;
    4)
        echo "🚀 Starting YOLOv5 Eye Blink Detection on http://127.0.0.1:5001..."
        python Yolov5Eye.py
        ;;
    5)
        echo "🚀 Starting YOLOv5 Hand Gesture Detection on http://127.0.0.1:5005..."
        python Yolov5Hand.py
        ;;
    6)
        echo "🚀 Starting YOLOv5 Face Login Attendance on http://127.0.0.1:5006..."
        python Yolov5Login.py
        ;;
    7)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid selection. Exiting."
        exit 1
        ;;
esac
