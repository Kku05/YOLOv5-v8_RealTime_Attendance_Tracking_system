#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "📦 1. Installing build tools with compatible setuptools (<80)..."
pip install --upgrade pip wheel cmake
# CRITICAL: setuptools 80+ drops pkg_resources compatibility required by face_recognition_models
pip install "setuptools<80"

echo "⚡ 2. Installing lightweight CPU-only PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "🛠️ 3. Setting single-threaded compile limit to prevent OOM..."
export CMAKE_BUILD_PARALLEL_LEVEL=1

echo "📦 4. Installing project requirements..."
pip install -r requirements.txt

echo "🧪 5. Verifying imports..."
python -c "import setuptools; print('Setuptools:', setuptools.__version__); import face_recognition; import cv2; import ultralytics; print('✅ All AI & CV dependencies successfully verified!')"

echo "🎉 Build completed successfully!"
