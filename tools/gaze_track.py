"""Per-frame "eyes down" score for a seated talking head (MediaPipe face landmarker, run on LiteRT).

Edison reads notes below the lens; a glance down shows as the iris dropping toward the lower lid and
the eye aperture closing. Score = iris drop (0 top .. 1 bottom of the eye opening) + lid closure.

    python3 -I tools/gaze_track.py SRC.MOV FACELM_DIR OUT.json [--fps 10] [--center x,y] [--size px]
"""
import argparse
import json
import subprocess

import numpy as np
from ai_edge_litert.interpreter import Interpreter
from PIL import Image

W, H = 1080, 1920
L_UP, L_LO, L_IN, L_OUT, L_IRIS = 159, 145, 133, 33, 468
R_UP, R_LO, R_IN, R_OUT, R_IRIS = 386, 374, 362, 263, 473


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("facelm")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--center", default="600,920")
    ap.add_argument("--size", type=float, default=560)
    a = ap.parse_args()
    it = Interpreter(model_path=a.facelm + "/face_landmarks_detector.tflite")
    it.allocate_tensors()
    iin = it.get_input_details()[0]["index"]
    outs = {d["name"]: d["index"] for d in it.get_output_details()}
    cx, cy = (float(v) for v in a.center.split(","))
    size = a.size
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-vf", f"fps={a.fps},scale={W}:{H}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    res, k = [], 0
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = Image.frombytes("RGB", (W, H), buf)

        def run(c_x, c_y, sz):
            box = tuple(int(round(v)) for v in (c_x - sz / 2, c_y - sz / 2, c_x + sz / 2, c_y + sz / 2))
            x = np.asarray(fr.crop(box).resize((256, 256), Image.BILINEAR), np.float32)[None] / 255.0
            it.set_tensor(iin, x)
            it.invoke()
            return float(it.get_tensor(outs["Identity_1"]).ravel()[0]), it.get_tensor(outs["Identity"]).reshape(-1, 3), box

        logit, lm, box = run(cx, cy, size)
        if logit < 8:  # lost or weak: search nearby crops and keep the most confident
            for dx in (-140, 0, 140):
                for dy in (-160, 0, 160):
                    for sz in (480, 620, 780):
                        r = run(cx + dx, cy + dy, sz)
                        if r[0] > logit:
                            logit, lm, box = r
        size = box[2] - box[0]
        pres = float(1 / (1 + np.exp(-(logit - 4))))
        p = lm[:, :2] / 256.0 * size + np.array([box[0], box[1]])

        def eye(up, lo, i0, o0, ir):
            ap_ = p[lo, 1] - p[up, 1]
            width = np.linalg.norm(p[i0] - p[o0])
            drop = (p[ir, 1] - p[up, 1]) / max(ap_, 1e-3)
            return drop, ap_ / max(width, 1e-3)

        dl, al = eye(L_UP, L_LO, L_IN, L_OUT, L_IRIS)
        dr, ar = eye(R_UP, R_LO, R_IN, R_OUT, R_IRIS)
        face_h = np.linalg.norm(p[10] - p[152])
        pitch = ((p[1, 1] - p[168, 1]) / max(face_h, 1e-3))  # nose tip below brow-centre: grows as the head tips down
        res.append(dict(t=round(k / a.fps, 3), drop=round(float((dl + dr) / 2), 3), aperture=round(float((al + ar) / 2), 3),
                        pitch=round(float(pitch), 3), presence=round(pres, 3)))
        if pres > 0.5:  # re-centre the crop on the face for the next frame
            fc = p[[10, 152, 234, 454]].mean(0)
            cx, cy = 0.7 * (box[0] + size / 2) + 0.3 * fc[0], 0.7 * (box[1] + size / 2) + 0.3 * fc[1]
            size = 0.8 * size + 0.2 * float(np.clip(face_h * 1.9, 420, 900))
        k += 1
    json.dump(res, open(a.out, "w"))
    print(len(res), "frames")


if __name__ == "__main__":
    main()
