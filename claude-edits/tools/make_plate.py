"""Make a clean wall "plate" for the space above the clip in a vertical frame.

The clip is horizontal, so vertical effects show it lower down and fill the space above it
with wall. This fits the plain wall's smooth colour gradient along the top of the clip (ignoring
the person by brightness) at a given time, so the plate matches that section's exposure.

Usage: .venv/bin/python tools/make_plate.py SECONDS [SECONDS ...]
Writes public/plates/plate_<frame>.png (frame at 30 fps) and prints the head's horizontal
centre (0 to 1) at that time, for framing.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
BAND = 260  # source rows used to read the wall colour
PLATE_HEIGHT = 64


def main():
    out_dir = ROOT / "public" / "plates"
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(ROOT / "public" / "talking.mp4"))
    rng = np.random.default_rng(7)
    for arg in sys.argv[1:]:
        t = float(arg)
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            sys.exit(f"Could not read frame at {t}s")
        h, w = frame.shape[:2]
        band = frame[:BAND].astype(np.float32)
        lum = band.mean(axis=2)
        wall = lum > np.percentile(lum, 35) - 10  # hair and skin are much darker than the wall
        # Fit each channel along x with a smooth curve, using wall pixels only.
        ys, xs = np.nonzero(wall)
        x = xs / w
        basis = np.stack([np.ones_like(x), x, x**2, x**3], axis=1)
        row = np.empty((w, 3), np.float32)
        xx = np.arange(w) / w
        full = np.stack([np.ones_like(xx), xx, xx**2, xx**3], axis=1)
        for c in range(3):
            coef, *_ = np.linalg.lstsq(basis, band[ys, xs, c], rcond=None)
            row[:, c] = full @ coef
        plate = np.repeat(row[None], PLATE_HEIGHT, axis=0)
        plate += rng.normal(0, 1.2, plate.shape)  # a little grain so it doesn't look flat
        frame_no = round(t * 30)
        cv2.imwrite(str(out_dir / f"plate_{frame_no}.png"), np.clip(plate, 0, 255).astype(np.uint8))

        # Head centre: dark pixels in the upper part of the frame.
        upper = frame[int(h * 0.05):int(h * 0.35)].mean(axis=2)
        dark_x = np.nonzero(upper < 90)[1]
        centre = float(np.median(dark_x) / w) if len(dark_x) else 0.5
        print(f"{t}s -> frame {frame_no}: plate_{frame_no}.png, head centre x = {centre:.3f}")


if __name__ == "__main__":
    main()
