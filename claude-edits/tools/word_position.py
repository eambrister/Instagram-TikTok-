"""Where to put the word that rises behind the head, from a finished edit's person mask.

Usage: .venv/bin/python tools/word_position.py MASK_DIR SECONDS
Prints the head's top edge over the 3 seconds from SECONDS and the centerY to use, so the head covers
the lower half of the letters (the TextBehind look).
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
mask_dir = ROOT / "public" / sys.argv[1]
at = float(sys.argv[2])
meta = json.loads((mask_dir / "meta.json").read_text())
fps = meta["fps"]
tops = []
for f in range(int(at * fps), min(meta["frameCount"], int((at + 3) * fps)), 5):
    m = cv2.imread(str(mask_dir / "frames" / f"mask_{f:05d}.png"), cv2.IMREAD_GRAYSCALE)
    ys = np.nonzero((m > 128).any(axis=1))[0]
    if len(ys):
        tops.append(int(ys.min()))
if not tops:
    sys.exit("Nobody in shot at that time")
print(f"head top over the word: {min(tops)}-{max(tops)} px (median {int(np.median(tops))})")
print(f"centerY: {int(np.median(tops))}")
