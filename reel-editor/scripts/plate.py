"""Clean wall plate for the space above a backed-out full-screen shot.

Usage: python -I plate.py <video> <out.png> [--samples 12]

Reads the plain wall along the top of the frame at several moments (ignoring the person, who is much
darker than the wall), fits each colour channel with a smooth curve across the width, and takes the
median over the samples. Writes a short strip the full width of the video that the renderer stretches
upward, so the extended wall matches the real one's brightness and gradient.
"""
import argparse

import cv2
import numpy as np

BAND = 0.12  # share of the frame height read from the top edge
HEIGHT = 64


def wall_row(frame):
    h, w = frame.shape[:2]
    band = frame[: max(8, int(h * BAND))].astype(np.float32)
    lum = band.mean(axis=2)
    wall = lum > np.percentile(lum, 35) - 10
    ys, xs = np.nonzero(wall)
    if len(xs) < w:
        return None
    x = xs / w
    basis = np.stack([np.ones_like(x), x, x**2, x**3], axis=1)
    xx = np.arange(w) / w
    full = np.stack([np.ones_like(xx), xx, xx**2, xx**3], axis=1)
    row = np.empty((w, 3), np.float32)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(basis, band[ys, xs, c], rcond=None)
        row[:, c] = full @ coef
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--samples", type=int, default=12)
    a = ap.parse_args()

    cap = cv2.VideoCapture(a.video)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    rows = []
    for i in range(a.samples):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * (i + 0.5) / a.samples))
        ok, frame = cap.read()
        if ok:
            r = wall_row(frame)
            if r is not None:
                rows.append(r)
    if not rows:
        raise SystemExit("could not read the wall from the video")
    row = np.median(np.stack(rows), axis=0)
    plate = np.repeat(row[None], HEIGHT, axis=0)
    plate += np.random.default_rng(7).normal(0, 1.2, plate.shape)  # light grain so it isn't flat
    cv2.imwrite(a.out, np.clip(plate, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    main()
