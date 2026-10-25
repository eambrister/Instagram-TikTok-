"""Where the head is during a section, from the person mask, for framing effects.

Usage: .venv/bin/python tools/head_position.py START_FRAME [FRAMES]
Prints the head's horizontal centre (0 to 1 of the clip width) and its top and chin (source px)
as the median over the section.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
start = int(sys.argv[1])
count = int(sys.argv[2]) if len(sys.argv) > 2 else 90
centres, tops, chins = [], [], []
for i in range(start, start + count, 3):
    m = cv2.imread(str(ROOT / f"public/mask/frames/mask_{i:05d}.png"), cv2.IMREAD_GRAYSCALE)
    if m is None:
        sys.exit(f"Mask frame {i} not made yet")
    person = m > 128
    rows = np.nonzero(person.any(axis=1))[0]
    top = rows.min()
    # Head: from the top down to where the outline widens sharply into the shoulders.
    widths = person.sum(axis=1)
    head_w = np.median(widths[top + 100:top + 400])
    chin = top + 400 + int(np.argmax(widths[top + 400:] > head_w * 1.6))
    xs = np.nonzero(person[top:chin])[1]
    centres.append(xs.mean() / m.shape[1])
    tops.append(top)
    chins.append(chin)
print(f"centerX={np.median(centres):.3f} (range {min(centres):.3f}-{max(centres):.3f}) "
      f"top={int(np.median(tops))} chin={int(np.median(chins))}")
