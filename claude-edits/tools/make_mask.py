"""Make a person mask (person white, background black) from a clip, frame for frame.

Uses MediaPipe's multiclass selfie segmenter (free, runs locally on Linux/Windows).
Edges are refined against the real frame with a guided filter, smoothed over time
so hair and shoulders don't flicker, then lightly feathered.

The source clip is only read, never written.

Usage:
  .venv/bin/python tools/make_mask.py                      # public/talking.mp4 -> public/mask
  .venv/bin/python tools/make_mask.py IN.mp4 --out DIR

Writes to the output folder:
  frames/mask_00000.png ...  one greyscale PNG per source frame (used by BehindMe)
  talking-mask.mp4           the same mask as a black and white video, same size and fps
  meta.json                  width, height, fps, frameCount
"""

import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "tools" / "models" / "selfie_multiclass_256x256.tflite"

# Smoothing. Raise TEMPORAL to calm flicker more (at the cost of lag on fast moves).
TEMPORAL = 0.45  # share of the previous frame's mask kept (0 = none)
# Edges are refined at a working size whose long side is WORK_LONG_SIDE. Pixel sizes below are
# for a 1920-long-side frame (1080x1920) and are scaled for other sizes, e.g. doubled for 4K.
WORK_LONG_SIDE = 1920
GUIDE_RADIUS = 6  # guided filter radius, in working pixels at 960 long side
GUIDE_EPS = 2e-3
EDGE_LOW, EDGE_HIGH = 0.3, 0.7  # soft threshold band
FEATHER_SIGMA = 1.2  # final edge blur, in output pixels at 1920 long side
HOLE_MAX_FRACTION = 0.004  # enclosed background specks smaller than this share of the frame get filled
INTERIOR_PX = 8  # in working pixels at 960 long side: deeper inside the person is always solid white


def probe(path):
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames:stream_side_data=rotation",
            "-of", "json", str(path),
        ],
        check=True, capture_output=True, text=True,
    ).stdout
    s = json.loads(out)["streams"][0]
    w, h = int(s["width"]), int(s["height"])
    rotation = 0
    for sd in s.get("side_data_list", []):
        rotation = int(sd.get("rotation", 0))
    if abs(rotation) in (90, 270):
        w, h = h, w
    return w, h, s["r_frame_rate"], s.get("avg_frame_rate", s["r_frame_rate"])


def guided_filter(guide, src, r, eps):
    mean = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mi, mp_ = mean(guide), mean(src)
    cov = mean(guide * src) - mi * mp_
    var = mean(guide * guide) - mi * mi
    a = cov / (var + eps)
    b = mp_ - a * mi
    return mean(a) * guide + mean(b)


def fill_small_holes(p, interior_px):
    """Make the inside of the person solid, so dark clothing or shadows don't go see-through.

    Real background is clear background that touches the frame edge, or an enclosed gap big
    enough to be real (like the space between a hand on the hip and the body). Anything more
    than interior_px away from real background is set to fully person; the edge stays soft.
    """
    clear = (p < 0.2).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(clear, connectivity=4)
    h, w = p.shape
    max_area = HOLE_MAX_FRACTION * h * w
    real_bg = np.zeros_like(clear)
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        touches_edge = x == 0 or y == 0 or x + bw == w or y + bh == h
        if touches_edge or area >= max_area:
            real_bg[labels == i] = 1
    dist = cv2.distanceTransform(1 - real_bg, cv2.DIST_L2, 3)
    return np.where(dist > interior_px, 1.0, p).astype(np.float32)


def frame_times(path):
    """Presentation time (seconds) of every video frame, in display order, starting at 0."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
         "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    times = sorted(float(line.split(",")[0]) for line in out.split() if line.strip() and line != "N/A")
    return [t - times[0] for t in times]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", default=str(ROOT / "public" / "talking.mp4"))
    ap.add_argument("--out", default=str(ROOT / "public" / "mask"))
    args = ap.parse_args()

    src = Path(args.input)
    out = Path(args.out)
    if not src.exists():
        sys.exit(f"Clip not found: {src}")
    w, h, r_rate, avg_rate = probe(src)
    fps = Fraction(r_rate)
    times = frame_times(src)
    if Fraction(avg_rate) != fps:
        print(f"Note: slightly variable frame rate ({avg_rate} avg vs {r_rate}); the mask keeps every frame's exact time.")

    long_side = max(w, h)
    work_scale = min(1.0, WORK_LONG_SIDE / long_side)
    ww, wh = round(w * work_scale) // 2 * 2, round(h * work_scale) // 2 * 2
    work_factor = max(ww, wh) / 960
    guide_radius = max(1, round(GUIDE_RADIUS * work_factor))
    interior_px = INTERIOR_PX * work_factor
    feather = FEATHER_SIGMA * long_side / 1920

    frames_dir = out / "frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    decoder = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(src), "-map", "0:v:0", "-fps_mode", "passthrough",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE,
    )

    options = mp.tasks.vision.ImageSegmenterOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        output_confidence_masks=True,
        output_category_mask=False,
    )
    frame_bytes = w * h * 3
    prev = None
    n = 0
    with mp.tasks.vision.ImageSegmenter.create_from_options(options) as segmenter:
        while True:
            buf = decoder.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                break
            rgb = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
            result = segmenter.segment_for_video(image, round(times[min(n, len(times) - 1)] * 1000))
            # Category 0 is background; everything else (hair, skin, clothes, accessories) is the person.
            person = 1.0 - result.confidence_masks[0].numpy_view().astype(np.float32)

            # Refine edges at the working size, guided by the real frame.
            guide = cv2.cvtColor(cv2.resize(rgb, (ww, wh), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
            guide = guide.astype(np.float32) / 255.0
            p = cv2.resize(person, (ww, wh), interpolation=cv2.INTER_LINEAR)
            p = np.clip(guided_filter(guide, p, guide_radius, GUIDE_EPS), 0, 1)
            p = fill_small_holes(p, interior_px)

            # Temporal smoothing against flicker.
            if prev is not None:
                p = TEMPORAL * prev + (1 - TEMPORAL) * p
            prev = p

            # Clean, slightly soft edge.
            t = np.clip((p - EDGE_LOW) / (EDGE_HIGH - EDGE_LOW), 0, 1)
            t = t * t * (3 - 2 * t)
            m = cv2.resize(t, (w, h), interpolation=cv2.INTER_LINEAR)
            m = cv2.GaussianBlur(m, (0, 0), feather)
            m8 = (m * 255 + 0.5).astype(np.uint8)

            cv2.imwrite(str(frames_dir / f"mask_{n:05d}.png"), m8, [cv2.IMWRITE_PNG_COMPRESSION, 6])
            n += 1
            if n % 30 == 0:
                print(f"  {n} frames", flush=True)

    decoder.wait()
    if decoder.returncode:
        sys.exit("ffmpeg failed while decoding")
    if n != len(times):
        sys.exit(f"Frame count mismatch: decoded {n}, timestamps {len(times)}")

    # Black and white video of the mask, with every frame at the same time as in the clip.
    concat = out / "frames.ffconcat"
    lines = ["ffconcat version 1.0"]
    for i in range(n):
        dur = (times[i + 1] - times[i]) if i + 1 < n else float(1 / fps)
        lines += [f"file frames/mask_{i:05d}.png", f"duration {dur:.6f}"]
    lines.append(f"file frames/mask_{n - 1:05d}.png")
    concat.write_text("\n".join(lines) + "\n")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-fps_mode", "vfr", "-frames:v", str(n), "-video_track_timescale", "600",
         "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(out / "talking-mask.mp4")],
        check=True,
    )
    concat.unlink()

    meta = {"source": src.name, "width": w, "height": h, "fps": float(fps), "fpsRational": r_rate,
            "frameCount": n, "frameTimes": [round(t, 6) for t in times]}
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Done: {n} mask frames at {w}x{h}, {r_rate} fps -> {out}")


if __name__ == "__main__":
    main()
