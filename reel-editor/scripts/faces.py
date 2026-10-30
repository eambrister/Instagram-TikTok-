"""Face track for framing and caption avoidance (OpenCV Haar cascade, CPU only).

Usage: python -I faces.py <video> <out.json> [--fps 3] [--t0 0] [--t1 end]

Output boxes are normalised to the video frame (0..1): {"t", "cx", "cy", "w", "h"}.
Frames without a confident detection are omitted; callers interpolate or fall back.
"""
import argparse
import json

import cv2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=3.0)
    a = ap.parse_args()

    cap = cv2.VideoCapture(a.video)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    step = max(1, round(src_fps / a.fps))
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    out, idx = [], 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if idx % step == 0:
            ok, frame = cap.retrieve()
            if ok:
                scale = 480.0 / max(W, H)
                small = cv2.resize(frame, None, fx=scale, fy=scale)
                gray = cv2.equalizeHist(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
                faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6,
                                                 minSize=(int(small.shape[1] * 0.08),) * 2)
                if len(faces):
                    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                    sw, sh = small.shape[1], small.shape[0]
                    out.append({"t": round(idx / src_fps, 3), "cx": round((x + w / 2) / sw, 4),
                                "cy": round((y + h / 2) / sh, 4), "w": round(w / sw, 4), "h": round(h / sh, 4)})
        idx += 1
    with open(a.out, "w") as f:
        json.dump({"width": W, "height": H, "fps": src_fps, "samples": idx // step, "faces": out}, f)


if __name__ == "__main__":
    main()
