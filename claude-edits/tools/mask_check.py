"""Side-by-side check sheets for a mask: original | mask | edge overlay | hair/shoulder close-up.

Usage: .venv/bin/python tools/mask_check.py [N frames, default 5]
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
meta = json.loads((ROOT / "public/mask/meta.json").read_text())
count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
total = meta["frameCount"]
picks = [round(i * (total - 1) / (count - 1)) for i in range(count)]
cap = cv2.VideoCapture(str(ROOT / "public" / meta["source"]))
out_dir = ROOT / "out" / "stills"
out_dir.mkdir(parents=True, exist_ok=True)

i = 0
for f in picks:
    while i <= f:
        ok, frame = cap.read()
        i += 1
    mask = cv2.imread(str(ROOT / f"public/mask/frames/mask_{f:05d}.png"), cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(mask, 60, 180)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    overlay = frame.copy()
    overlay[edges > 0] = (0, 0, 255)
    # Close-up around the top of the person (hair and shoulders).
    ys, xs = np.nonzero(mask > 128)
    top, cx = int(ys.min()), int(np.median(xs))
    x0 = max(0, min(frame.shape[1] - 540, cx - 270))
    y0 = max(0, min(frame.shape[0] - 540, top - 120))
    crop = np.hstack([overlay[y0:y0 + 540, x0:x0 + 540], cv2.cvtColor(mask[y0:y0 + 540, x0:x0 + 540], cv2.COLOR_GRAY2BGR)])
    small = lambda im: cv2.resize(im, (540, 960), interpolation=cv2.INTER_AREA)
    row = np.hstack([small(frame), small(cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)), small(overlay)])
    crop = cv2.resize(crop, (row.shape[1], row.shape[1] // 2), interpolation=cv2.INTER_CUBIC)
    sheet = np.vstack([row, crop])
    cv2.putText(sheet, f"frame {f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 3)
    path = out_dir / f"mask-check-f{f:03d}.jpg"
    cv2.imwrite(str(path), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(path)
