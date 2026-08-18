#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "📦 1. Installing build tools with compatible setuptools (<80)..."
pip install --upgrade pip wheel cmake --retries 10 --timeout 120
pip install "setuptools<80" --retries 10 --timeout 120

echo "⚡ 2. Installing lightweight CPU-only PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --retries 10 --timeout 120

echo "🛠️ 3. Setting single-threaded compile limit to prevent OOM..."
export CMAKE_BUILD_PARALLEL_LEVEL=1

echo "📦 4. Installing project requirements (pinning mediapipe <1.0.0 for mp.solutions API)..."
pip install -r requirements.txt --retries 10 --timeout 120

echo "🧪 5. Verifying imports..."
python -c "import setuptools; import face_recognition; import cv2; import ultralytics; import mediapipe as mp; print('MediaPipe:', mp.__version__); print('mp.solutions present:', hasattr(mp, 'solutions')); print('✅ All dependencies successfully verified!')"

echo "🎉 Build completed successfully!"
