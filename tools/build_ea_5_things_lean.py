"""Build Edison's "5 THINGS TO GET LEAN" talking-head Reel (edison-full-message skill).

Single ~101 s selfie take (Drive id 13HeHk1l3mzfzG9FhYGArAqdbrlN0U7sG). Whole take kept;
reuses the 50 MORE DAYS engine helpers (head-tracked depth titles, per-frame selfie masks,
word-timed captions, CTD end card) and adds a 5-step tracker that lights up per step.
No vignette (Edison's standing rule).

    python3 -I tools/build_ea_5_things_lean.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b] [--final OUT.mp4]

v2 cuts the raw take (tools/ea_cut_edit.py): filler, repeats, the flubbed retake and dead air.
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


# Word ranges to cut (indices in outputs/edison-ambrister-5-things-lean/transcript-words.json).
CUTS = [
    (0, 0, "filler: 'Alright,'"),
    (128, 135, "restates the protein point: 'So make sure you hit your protein goal.'"),
    (236, 236, "repeat: second 'guaranteed,'"),
    (241, 246, "repeat + filler: 'Guaranteed, you will become lean. Okay,'"),
    (281, 299, "retake: second 'If you don't get lean from these five steps, steps, ... areas.'"),
]
TRACK_F = None


def front(comp, t, rm):
    global TRACK_F
    if TRACK_F is None:
        TRACK_F = (font(BARLOW, 50), font(MONT_B, 25))
    src = _out_to_src(t, rm)
    tr = tracker(src, *TRACK_F)
    if tr is not None:
        over(comp, tr, (W - tr.width) // 2, 1478, ease((t - rm(STEPS[0][1] - 0.2)) / 0.4))


def _out_to_src(t, rm):
    for (s, e), o in zip(rm.keep, rm.offs):
        if t < o + (e - s):
            return s + (t - o)
    return rm.keep[-1][1]


def main():
    import ea_cut_edit as eng
    ap = argparse.ArgumentParser()
    for k in ("src", "words", "selfie", "out"):
        ap.add_argument(k)
    ap.add_argument("--only")
    ap.add_argument("--final")
    a = ap.parse_args()
    film = sys.modules[__name__]
    eng.render(a.src, a.words, a.selfie, a.out, film, a.only)
    if not a.only:
        eng.mix(a.src, a.out, film)
        if a.final:
            eng.finish(a.out, a.final)


if __name__ == "__main__":
    main()
