#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "📦 1. Upgrading build tools..."
pip install --upgrade pip setuptools wheel cmake

echo "⚡ 2. Installing lightweight CPU-only PyTorch (prevents 4GB CUDA bloat)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "🛠️ 3. Setting single-threaded compile limit to prevent OOM..."
export CMAKE_BUILD_PARALLEL_LEVEL=1

echo "📦 4. Installing remaining project requirements..."
pip install -r requirements.txt

echo "✅ Build completed successfully!"
