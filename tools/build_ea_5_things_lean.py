"""Build Edison's "5 THINGS TO GET LEAN" talking-head Reel (edison-full-message skill).

Single ~101 s selfie take (Drive id 13HeHk1l3mzfzG9FhYGArAqdbrlN0U7sG). Whole take kept;
reuses the 50 MORE DAYS engine helpers (head-tracked depth titles, per-frame selfie masks,
word-timed captions, CTD end card) and adds a 5-step tracker that lights up per step.
No vignette (Edison's standing rule).

    python3 -I tools/build_ea_5_things_lean.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b]
"""
import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, CRIMSON, END_CARD, FPS, GOLD, GRADE, H, IVORY, MONT_B, MONT_M, OBSIDIAN,
    PALE_GOLD, ROOT, SILVER, W, caption_groups, dimensional, ease, env, font, over, plain,
    refine_mask, render_caption)

STEPS = [  # label, start time of "Number N"
    ("SLEEP", 4.72), ("CALORIES", 10.72), ("PROTEIN", 20.56), ("STEPS", 32.48), ("TRAINING", 44.39)]
RECAP = (85.8, 92.0)  # "you have a lack in one of them": all five pulse


def build_events():
    big = font(BARLOW, 230)
    huge = font(BARLOW, 300)
    serif = font(BODONI, 190)
    ev = []

    def depth(t0, t1, img, slam=False, rise=0):
        ev.append(dict(t0=t0, t1=t1, img=img, y=None, rise=rise, slam=slam, kind="depth"))

    gold = lambda s, f=big, tr=4: dimensional(s, f, face=PALE_GOLD, edge=(110, 80, 8), tracking=tr)
    ivory = lambda s, f=big, tr=4: dimensional(s, f, face=IVORY, edge=(90, 90, 96), tracking=tr)
    silver = lambda s, f=big, tr=4: dimensional(s, f, face=SILVER, edge=(60, 64, 72), tracking=tr)
    crimson = lambda s, f=huge, tr=2: dimensional(s, f, face=(214, 52, 70), edge=(70, 10, 20), tracking=tr)

    depth(1.10, 2.25, ivory("GET LEAN"))
    depth(2.25, 4.65, gold("5 THINGS"), slam=True)
    # 1 sleep
    depth(4.70, 7.30, ivory("1 · SLEEP"))
    depth(7.35, 9.50, gold("7–8 HOURS"))
    depth(9.55, 10.65, gold("RECOVERY.", serif, 0))
    # 2 calories
    depth(10.70, 13.20, ivory("2 · CALORIES"))
    depth(16.45, 18.85, silver("DEFICIT"))
    depth(18.90, 20.50, silver("SURPLUS"))
    # 3 protein
    depth(20.55, 23.80, ivory("3 · PROTEIN"))
    depth(24.90, 28.50, silver("CARBS? FATS?"))
    depth(29.60, 32.40, gold("PROTEIN.", serif, 0), slam=True)
    # 4 steps
    depth(32.45, 35.05, ivory("4 · STEPS"))
    depth(35.08, 35.98, gold("10K"))
    depth(36.00, 36.88, gold("15K"))
    depth(36.90, 38.80, gold("20K", huge), slam=True)
    depth(41.60, 44.30, gold("BEFORE BED.", serif, 0))
    # 5 training
    depth(44.35, 47.80, ivory("5 · TRAINING"))
    depth(47.85, 48.45, silver("3×"))
    depth(48.45, 49.15, silver("3× · 4×"))
    depth(49.15, 50.60, silver("3× · 4× · 5×"))
    depth(63.30, 65.20, gold("EVERY SINGLE DAY.", serif, 0))
    # close (no "GUARANTEED" titles: onboarding bans guaranteed-outcome copy on screen)
    depth(65.30, 68.40, ivory("DO ALL 5."))
    depth(70.55, 74.30, crimson("LEAN."), slam=True)
    depth(81.20, 85.60, gold("FOLLOW THE 5 STEPS."))
    depth(99.20, 101.30, gold("5 STEPS. EVERY DAY."))
    return ev


def tracker(t, f_num, f_lab):
    """Row of five step pills; past steps gold with a check, current step bright, future dim."""
    if t < STEPS[0][1] - 0.2:
        return None
    pw, ph, gap = 196, 80, 6
    img = Image.new("RGBA", (5 * pw + 4 * gap, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cur = max(i for i, (_, s) in enumerate(STEPS) if t >= s - 0.2)
    pulse = RECAP[0] <= t <= RECAP[1]
    for i, (lab, _) in enumerate(STEPS):
        x = i * (pw + gap)
        if pulse:
            on = 0.55 + 0.45 * abs(np.sin((t - RECAP[0]) * 3.2 + i * 0.6))
            fill, txt, num = OBSIDIAN + (int(200 * on),), PALE_GOLD, GOLD
        elif i < cur:
            fill, txt, num = OBSIDIAN + (175,), PALE_GOLD, GOLD
        elif i == cur:
            fill, txt, num = GOLD + (235,), OBSIDIAN, OBSIDIAN
        else:
            fill, txt, num = OBSIDIAN + (110,), SILVER, SILVER
        d.rounded_rectangle((x, 0, x + pw - 1, ph - 1), 16, fill=fill)
        if i < cur and not pulse:  # done: gold check where the number was
            d.line((x + 14, 42, x + 24, 54, x + 40, 26), fill=GOLD, width=6)
        else:
            d.text((x + 14, 14), str(i + 1), font=f_num, fill=num)
        d.text((x + 48, 27), lab, font=f_lab, fill=txt)
    return img


def main():
    ap = argparse.ArgumentParser()
    for k in ("src", "words", "selfie", "out"):
        ap.add_argument(k)
    ap.add_argument("--only")
    a = ap.parse_args()
    from ai_edge_litert.interpreter import Interpreter

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    caps = caption_groups(json.load(open(a.words)))
    events = build_events()
    capf = font(BARLOW, 84)
    f_num, f_lab = font(BARLOW, 50), font(MONT_B, 25)

    it = Interpreter(model_path=a.selfie)
    it.allocate_tensors()
    iin, iout = it.get_input_details()[0]["index"], it.get_output_details()[0]["index"]
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.src]))
    ss, to = (float(v) for v in a.only.split(":")) if a.only else (0.0, dur)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-to", str(to), "-i", a.src,
                            "-vf", GRADE + f",fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    name = "proof.mp4" if a.only else "video-only.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-movflags", "+faststart", str(out / name)], stdin=subprocess.PIPE)
    logo = Image.open(ROOT / "brand/assets/ctd-cinematic-logo.png").convert("RGBA")
    prev_m, last, head, n = None, None, 450.0, 0
    fsize = W * H * 3
    while True:
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize:
            break
        t = ss + n / FPS
        n += 1
        frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
        x = np.asarray(Image.fromarray(frame.astype(np.uint8)).resize((256, 256), Image.BILINEAR),
                       np.float32)[None] / 255.0
        it.set_tensor(iin, x)
        it.invoke()
        m = refine_mask(it.get_tensor(iout)[0, ..., 0], frame)
        if prev_m is not None:
            m = 0.6 * m + 0.4 * prev_m
        prev_m = m
        rows = np.where((m[:, 330:750] > 0.5).any(1))[0]
        if len(rows):
            head = 0.85 * head + 0.15 * float(np.clip(rows[0], 300, 560))

        comp = frame.copy()
        shake = (0, 0)
        for e in events:
            al = env(t, e["t0"], e["t1"], 0.12 if e["slam"] else 0.25)
            if al <= 0:
                continue
            img = e["img"]
            if e["slam"]:
                sc = 1.25 - 0.25 * ease((t - e["t0"]) / 0.12)
                if t - e["t0"] < 0.2:
                    k = min(int((t - e["t0"]) * FPS), 5)
                    shake = ((-14, 10, -7, 5, -3, 0)[k], (8, -10, 6, -4, 2, 0)[k])
            else:
                sc = 1.04 - 0.04 * ease((t - e["t0"]) / 0.4)
            sc *= min(1.0, (W - 80) / (img.width * sc))
            gt, gb = img.info.get("glyph", (40, img.height - 40))
            img = img.resize((int(img.width * sc), int(img.height * sc)), Image.BILINEAR)
            y = max(int(head + 18 - gb * sc), 235 - int(gt * sc))
            y += int(24 * (1 - ease((t - e["t0"]) / 0.3)))
            over(comp, img, (W - img.width) // 2, y, al)
        mm = m[..., None]
        comp = frame * mm + comp * (1 - mm)
        last = np.clip(frame, 0, 255).astype(np.uint8)
        if shake != (0, 0):
            im = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
            canvas = Image.new("RGB", (W + 40, H + 40))
            canvas.paste(im, (20 + shake[0], 20 + shake[1]))
            comp = np.asarray(canvas.crop((20, 20, 20 + W, 20 + H)), np.float32).copy()

        tr = tracker(t, f_num, f_lab)
        if tr is not None:
            over(comp, tr, (W - tr.width) // 2, 1478, ease((t - STEPS[0][1] + 0.2) / 0.4))
        for g in caps:
            if g["t0"] <= t < g["t1"]:
                ci = render_caption(g, t, capf)
                if ci.width > W - 96:
                    ci = ci.resize((W - 96, int(ci.height * (W - 96) / ci.width)), Image.LANCZOS)
                over(comp, ci, (W - ci.width) // 2, 1330, env(t, g["t0"], g["t1"], 0.08, 0.06))
                break
        enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())

    if not a.only and last is not None:
        lg = logo.resize((520, 520), Image.LANCZOS)
        name_img = plain("EDISON AMBRISTER", font(MONT_B, 50), IVORY, 10, 0.3)
        foot = plain("DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", font(MONT_M, 30), PALE_GOLD, 4, 0.3)
        for k in range(int(END_CARD * FPS)):
            u = ease(k / 18)
            comp = last.astype(np.float32) * (1 - 0.9 * u) + np.array(OBSIDIAN, np.float32) * 0.9 * u
            over(comp, lg, (W - 520) // 2, 560, u)
            over(comp, name_img, (W - name_img.width) // 2, 1110, u)
            over(comp, foot, (W - foot.width) // 2, 1195, u)
            enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print("frames", n, "->", out / name)


if __name__ == "__main__":
    main()
