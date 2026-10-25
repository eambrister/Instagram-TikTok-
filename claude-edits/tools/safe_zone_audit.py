"""Check that text and graphics stay between x=120 and x=960.

Renders a composition in audit mode (footage and full-screen backgrounds hidden, transparent
background), then reports every frame with something drawn outside the safe zone.

Usage: .venv/bin/python tools/safe_zone_audit.py [COMPOSITION] [EVERY_NTH_FRAME]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
comp = sys.argv[1] if len(sys.argv) > 1 else "FullReel"
nth = sys.argv[2] if len(sys.argv) > 2 else "2"
out = ROOT / "out" / "audit"
shutil.rmtree(out, ignore_errors=True)
subprocess.run(
    ["npx", "remotion", "render", comp, str(out), "--sequence", "--image-format=png",
     f"--every-nth-frame={nth}", "--props", json.dumps({"audit": True}), "--log=error"],
    cwd=ROOT, check=True,
)

SAFE_LEFT, SAFE_RIGHT = 120, 960
problems = []
frames = sorted(out.glob("*.png"))
for path in frames:
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    alpha = img[:, :, 3] if img.shape[2] == 4 else np.full(img.shape[:2], 255, np.uint8)
    cols = np.nonzero((alpha > 110).sum(axis=0) > 4)[0]  # ignore soft shadows and single pixels
    if len(cols) and (cols.min() < SAFE_LEFT or cols.max() > SAFE_RIGHT):
        frame = int("".join(c for c in path.stem if c.isdigit())) * int(nth)  # files are numbered in order
        problems.append((frame, int(cols.min()), int(cols.max())))

print(f"Checked {len(frames)} frames of {comp}.")
if not problems:
    print("Everything stays inside x=120 to x=960.")
for frame, lo, hi in problems:
    print(f"  frame {frame}: drawn from x={lo} to x={hi}")
