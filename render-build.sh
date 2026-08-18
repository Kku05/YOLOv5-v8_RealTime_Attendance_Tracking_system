#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "📦 1. Upgrading build tools..."
pip install --upgrade pip setuptools wheel cmake --retries 10 --timeout 120

echo "⚡ 2. Installing lightweight CPU-only PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --retries 10 --timeout 120

echo "🛠️ 3. Setting single-threaded compile limit to prevent OOM..."
export CMAKE_BUILD_PARALLEL_LEVEL=1

echo "📦 4. Installing face recognition models..."
pip install face_recognition_models --retries 10 --timeout 120

echo "📦 5. Installing remaining project requirements..."
pip install -r requirements.txt --retries 10 --timeout 120

echo "✅ Build completed successfully!"
