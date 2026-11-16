"""Build Edison's "NVIDIA scandal → lust" talking-head Reel with B-roll.

Raw 6:34 take (Drive id 1PjM1A547ezXHS4xvo3eiHJcF-q9O2nqd) + Edison's B-roll folder
(Drive 1o_42ogzRGQKTgkyHRs3tdsoHJAl8REvg). Cut with tools/ea_cut_edit.py (retakes and dead air
removed; lines kept as Edison recorded them, at his direction). Depth titles sit on the face
sections only; B-roll (stock clips + headline screenshots) covers the factual beats, with the
word-timed captions continuing over it. No vignette, CTD end card.

    python3 -I tools/build_ea_nvidia_lust.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR BROLL_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, FPS, H, IVORY, OBSIDIAN, PALE_GOLD, SILVER, W,
    dimensional, ease, font)

BROLL_DIR = None
WORDS = None

# Retakes / flubs to cut (word indices in outputs/edison-ambrister-nvidia-lust/transcript-words.json).
CUTS = [
    (31, 41, "retake: first '$4.5 trillion' attempt"),
    (61, 73, "retake: first 'in less than a week, he was gone. So, here's what happened.'"),
    (127, 176, "retakes: four flubbed starts of the November 8th letter line"),
    (354, 365, "retake: first 'HP CEO Mark Hurd in 2010…' start"),
    (410, 429, "retake: first 'It took them years… one decision.'"),
    (459, 473, "retake: 'Now here's the part that relates to you. You may not necessarily have a fault.'"),
    (498, 515, "retake: first 'But you have something that you've been building…' list"),
]

# B-roll beats: (first word index, word index whose start ends the beat, file, kind)
BROLL = [
    (0, 3, "v11267667.mp4", "video"),     # "Thirty three years." clock
    (13, 18, "IMG_8239.jpg", "image"),    # co-founded 1993: NVIDIA HQ
    (18, 26, "v15429436.mp4", "video"),   # graphics card company: glowing chip
    (26, 31, "v2792370.mp4", "video"),    # engine behind AI: chip lines
    (49, 61, "IMG_8244.jpg", "image"),    # $4.5T, most valuable companies
    (98, 110, "IMG_8256.png", "image"),   # close relationship: CNN admits affair
    (110, 118, "IMG_8257.png", "image"),  # alleged spy: CNN explainer
    (177, 195, "IMG_8258.png", "image"),  # letter to all his employees
    (195, 202, "v6689830.mp4", "video"),  # unfaithful to his wife: ring hands
    (234, 243, "v3945008.mp4", "video"),  # stock started falling: red chart
    (243, 258, "IMG_8262.png", "image"),  # $500B wiped out: Yahoo Finance
    (258, 266, "IMG_8263.png", "image"),  # Nov 12 resignation: NVIDIA release
    (282, 302, "IMG_8264.png", "image"),  # Tiger Woods
    (302, 330, "IMG_8265.png", "image"),  # Steve Easterbrook
    (330, 354, "IMG_8266.png", "image"),  # Brian Krzanich
    (366, 396, "IMG_8267.png", "image"),  # Mark Hurd
    (448, 459, "v15230857.mp4@7.0", "video"),  # burn it all down: match (from 7 s, flame lit)
    (483, 498, "v16857566.mp4", "video"), # trillion / billion-dollar company: trading screens
    (530, 540, "v5894890.mp4", "video"),  # people depending on you: family
]


def _w(i):
    """Start time of word i (past the last word: its end plus a short tail)."""
    return WORDS[i]["t"] if i < len(WORDS) else WORDS[-1]["t"] + 0.9


def build_events():
    big = font(BARLOW, 230)
    huge = font(BARLOW, 300)
    serif = font(BODONI, 190)
    ev = []

    def depth(a, b, img, slam=False):
        ev.append(dict(t0=_w(a) - 0.05, t1=_w(b) - 0.05, img=img, y=None, rise=0, slam=slam,
                       kind="depth"))

    g = 1.0  # light wall behind Edison: stronger dark halo so thin serif/silver titles read
    gold = lambda s, f=big, tr=4: dimensional(s, f, face=PALE_GOLD, edge=(110, 80, 8), tracking=tr, glow=g)
    ivory = lambda s, f=big, tr=4: dimensional(s, f, face=IVORY, edge=(90, 90, 96), tracking=tr, glow=g)
    silver = lambda s, f=big, tr=4: dimensional(s, f, face=SILVER, edge=(60, 64, 72), tracking=tr, glow=g)
    crimson = lambda s, f=huge, tr=2: dimensional(s, f, face=(214, 52, 70), edge=(70, 10, 20), tracking=tr, glow=g)

    depth(3, 13, gold("33 YEARS."))
    depth(80, 83, crimson("GONE."), slam=True)
    depth(119, 127, ivory("ALLEGATIONS."))
    depth(203, 207, ivory("THE CRAZY PART."))
    depth(271, 282, ivory("NOT THE FIRST."))
    depth(399, 410, gold("SAME STORY.", serif, 0))
    depth(430, 448, gold("YEARS TO BUILD.", serif, 0))
    depth(475, 480, ivory("THE PART FOR YOU."))
    depth(519, 524, gold("WHAT YOU'RE BUILDING.", serif, 0))
    depth(547, 559, crimson("LUST."), slam=True)
    depth(563, 568, silver("THE HERE & NOW"))
    depth(570, 573, gold("STANDARDS.", serif, 0))
    depth(586, 590, silver("DON'T ANSWER."))
    depth(600, 606, gold("STAY FOCUSED."))
    depth(611, 614, silver("IN PRIVATE."))
    depth(618, 620, crimson("IN PUBLIC."), slam=True)
    depth(641, 646, gold("PROTECT IT."))
    depth(646, 649, gold("LOCKED IN."), slam=True)
    return ev


# ---------------------------------------------------------------- B-roll layer
_STATE = {}


def _card(path):
    """Headline screenshot / photo as a rounded card with shadow on a dark graphite field."""
    im = Image.open(path).convert("RGB")
    s = min(960 / im.width, 1040 / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 26, fill=255)
    card = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    sh = Image.new("L", card.size, 0)
    sh.paste(mask, (40, 52))
    card.paste(Image.new("RGBA", card.size, (0, 0, 0, 170)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
    card.paste(im, (40, 40), mask)
    return card


def _bg():
    g = np.linspace(0, 1, H)[:, None, None]
    top = np.array((41, 45, 52), np.float32)
    bot = np.array(OBSIDIAN, np.float32)
    return (top * (1 - g) + bot * g).repeat(W, axis=1).astype(np.float32)


def _push(frame, z):
    if z <= 1.0005:
        return frame
    im = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - ch) / 2
    return np.asarray(im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)), np.float32)


def front(comp, t, rm):
    if "beats" not in _STATE:
        beats = []
        for a, b, f, kind in BROLL:
            t0, t1 = rm(_w(a) - 0.06), rm(_w(b) - 0.06)
            if t1 - t0 > 0.4:
                beats.append(dict(t0=t0, t1=t1, f=f, kind=kind))
        _STATE["beats"] = beats
        _STATE["bg"] = _bg()
    for i, bt in enumerate(_STATE["beats"]):
        if not (bt["t0"] <= t < bt["t1"]):
            continue
        u = (t - bt["t0"]) / (bt["t1"] - bt["t0"])
        if bt["kind"] == "image":
            if "card" not in bt:
                bt["card"] = _card(BROLL_DIR / bt["f"])
            card = bt["card"]
            sc = 0.97 + 0.05 * u
            c = card.resize((int(card.width * sc), int(card.height * sc)), Image.BILINEAR)
            frame = _STATE["bg"].copy()
            from build_ea_50_more_days import over
            y = max(170, 720 - c.height // 2)
            over(frame, c, (W - c.width) // 2, y + int(30 * (1 - ease(min(1, (t - bt["t0"]) / 0.3)))),
                 min(1.0, (t - bt["t0"]) / 0.12))
        else:
            if "proc" not in bt:
                name, _, ss = bt["f"].partition("@")
                bt["proc"] = subprocess.Popen(
                    ["ffmpeg", "-v", "error", "-ss", ss or "0", "-i", str(BROLL_DIR / name), "-vf",
                     f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                     "eq=contrast=1.05:saturation=0.95", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                    stdout=subprocess.PIPE)
                bt["last"] = None
            buf = bt["proc"].stdout.read(W * H * 3)
            if len(buf) == W * H * 3:
                bt["last"] = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
            frame = _push(bt["last"], 1.0 + 0.06 * u) if bt["last"] is not None else comp.copy()
        comp[:] = frame
        return
    # close finished video readers
    for bt in _STATE["beats"]:
        if "proc" in bt and t >= bt["t1"] and bt["proc"].poll() is None:
            bt["proc"].kill()


def main():
    global BROLL_DIR, WORDS
    import ea_cut_edit as eng
    ap = argparse.ArgumentParser()
    for k in ("src", "words", "selfie", "out", "broll"):
        ap.add_argument(k)
    ap.add_argument("--only")
    ap.add_argument("--final")
    a = ap.parse_args()
    BROLL_DIR = pathlib.Path(a.broll)
    WORDS = json.load(open(a.words))
    film = sys.modules[__name__]
    eng.render(a.src, a.words, a.selfie, a.out, film, a.only)
    if not a.only:
        eng.mix(a.src, a.out, film)
        if a.final:
            eng.finish(a.out, a.final)


if __name__ == "__main__":
    main()
