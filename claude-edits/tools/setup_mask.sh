#!/usr/bin/env bash
# One-time setup for tools/make_mask.py: Python environment and the MediaPipe model.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -q mediapipe opencv-python-headless numpy
mkdir -p tools/models
[ -f tools/models/selfie_multiclass_256x256.tflite ] || curl -sSfL -o tools/models/selfie_multiclass_256x256.tflite \
  https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite
# On Linux, MediaPipe also needs libEGL (Debian/Ubuntu: sudo apt-get install libegl1 libgles2).
echo "Ready. Run: .venv/bin/python tools/make_mask.py"
