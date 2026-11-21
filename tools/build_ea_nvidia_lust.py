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
    (396, 396, "v3: 'Now,' cut, his eyes are still on his notes as he says it (Edison's 2:01 note)"),
]


def fix_edl(keep, vkeep):
    """v3 fixes from Edison's review of v2. Each boundary keeps its L/J offset (picture minus audio)
    unless the fix sets one, so audio and picture stay the same total length."""
    K, V = [list(x) for x in keep], [list(x) for x in vkeep]

    def at_end(t):
        return min(range(len(K)), key=lambda k: abs(K[k][1] - t))

    def set_end(t, new_end, offset=None):
        k = at_end(t)
        o = V[k][1] - K[k][1] if offset is None else offset
        K[k][1] = new_end
        V[k][1] = new_end + o
        if k + 1 < len(K):
            V[k + 1][0] = K[k + 1][0] + o

    set_end(26.23, 26.23, offset=0.16)  # 0:12: next clip ("Going into November") opened on eyes coming up
    set_end(50.43, 50.22)               # 0:22: end on "world." before his head drops
    set_end(253.97, 253.93, offset=0.0) # 2:01: no hold after "millions." (eyes drop at 254.0)
    set_end(364.2, 363.35, offset=0.0)  # 2:54: "purpose." ends 363.3; the rest was a breath while eyes dropped
    return [tuple(x) for x in K], [tuple(x) for x in V]

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


CUT_BY_WORDS = True   # v2: cut on the words, not the pauses (no glance down at the notes at clip ends)
GAZE = None           # set in main(): per-frame eyes-down score from tools/gaze_track.py (10 fps)
MATTE_MODEL = None    # set in main(): RobustVideoMatting HQ model for clean head edges
# v2 caption corrections (index -> text; "" hides a word that was merged into the previous one)
CAPTION_FIX = {
    97: "Huang,", 98: "the", 177: "On", 255: "NVIDIA", 261: "NVIDIA", 263: "Mr. Huang's", 264: "",
    285: "2009,", 286: "", 287: "", 305: "2019,", 306: "", 326: "$100", 327: "", 328: "million.", 329: "",
    333: "Krzanich.", 335: "2018", 336: "", 397: "These", 495: "hundred-thousand-dollar", 496: "",
    647: "LOCKED", 648: "IN.",
}


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


# ---------------------------------------------------------------- B-roll layer (v2: card above his head)
# v2: Edison asked for the B-roll to sit ABOVE his head while he keeps talking, instead of replacing
# the frame. Each beat is a rounded card in the wall space over his head; his head (RVM matte) passes
# in front of the card's lower edge so it reads as layered. Phone screenshots are cropped to their
# headline (and photo where it matters) so the card stays readable.
CROPS = {  # source-pixel crop boxes for the tall phone screenshots
    "IMG_8256.png": (0, 0, 1170, 560),     # CNN: "admits affair ... foreign spy claims"
    "IMG_8257.png": (0, 0, 1170, 1160),    # CNN: Alice Huang headline + dinner photo
    "IMG_8258.png": (0, 0, 1170, 700),     # NVIDIA newsroom letter opening
    "IMG_8262.png": (0, 430, 1170, 900),   # Yahoo: market cap plunges $490B
    "IMG_8263.png": (0, 0, 1170, 900),     # NVIDIA Announces CEO Transition
    "IMG_8264.png": (0, 0, 1170, 620),     # UC Davis: Tiger Woods scandal cost
    "IMG_8265.png": (0, 0, 1170, 560),     # AP: McDonald's fired CEO returns $105M
    "IMG_8266.png": (0, 640, 1170, 1250),  # Intel CEO Brian Krzanich quits
    "IMG_8267.png": (0, 0, 1170, 760),     # NBC: HP's CEO Hurd quits
}
CARD_W, CARD_H, CARD_TOP = 960, 540, 250   # max card box; never above the 250 px safe line
_STATE = {}
VIDEO_W, VIDEO_H = 960, 540


def _round(im, r=28):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    return mask


def _frame_card(im):
    """Wrap a picture as an RGBA card: rounded corners, thin ivory rim, soft drop shadow."""
    mask = _round(im)
    pad = 44
    card = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("L", card.size, 0)
    sh.paste(mask, (pad, pad + 14))
    card.paste(Image.new("RGBA", card.size, (0, 0, 0, 190)), (0, 0), sh.filter(ImageFilter.GaussianBlur(20)))
    card.paste(im.convert("RGBA"), (pad, pad), mask)
    rim = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle((pad, pad, pad + im.width - 1, pad + im.height - 1), 28,
                                          outline=(246, 239, 226, 150), width=3)
    return Image.alpha_composite(card, rim)


def _image(path, name):
    im = Image.open(path).convert("RGB")
    if name in CROPS:
        im = im.crop(CROPS[name])
    sc = min(CARD_W / im.width, CARD_H / im.height)
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def front(comp, t, rm):
    import ea_cut_edit as eng
    from build_ea_50_more_days import over
    if "beats" not in _STATE:
        beats = []
        for a, b, f, kind in BROLL:
            t0, t1 = rm(_w(a) - 0.06), rm(_w(b) - 0.06)
            if t1 - t0 > 0.4:
                beats.append(dict(t0=t0, t1=t1, f=f, kind=kind))
        _STATE["beats"] = beats
        _STATE["hy"] = None
    cur = eng.CURRENT
    hr = cur.get("head_raw")
    if hr is not None:
        _STATE["hy"] = hr if _STATE["hy"] is None or cur.get("new_seg") else 0.85 * _STATE["hy"] + 0.15 * hr
    for bt in _STATE["beats"]:
        if "proc" in bt and t >= bt["t1"] and bt["proc"].poll() is None:
            bt["proc"].kill()
    for bt in _STATE["beats"]:
        if not (bt["t0"] <= t < bt["t1"]):
            continue
        u = (t - bt["t0"]) / max(1e-3, bt["t1"] - bt["t0"])
        name, _, ss = bt["f"].partition("@")
        if bt["kind"] == "image":
            if "pic" not in bt:
                bt["pic"] = _image(BROLL_DIR / name, name)
            pic = bt["pic"]
            z = 1.0 + 0.04 * u  # slow push inside the card
            cw, ch = pic.width / z, pic.height / z
            pic = pic.resize(pic.size, Image.BILINEAR, box=((pic.width - cw) / 2, (pic.height - ch) / 2,
                                                             (pic.width + cw) / 2, (pic.height + ch) / 2))
        else:
            if "proc" not in bt:
                bt["proc"] = subprocess.Popen(
                    ["ffmpeg", "-v", "error", "-ss", ss or "0", "-i", str(BROLL_DIR / name), "-vf",
                     f"fps={FPS},scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
                     f"crop={VIDEO_W}:{VIDEO_H},eq=contrast=1.05:saturation=0.95",
                     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
                bt["last"] = None
            buf = bt["proc"].stdout.read(VIDEO_W * VIDEO_H * 3)
            if len(buf) == VIDEO_W * VIDEO_H * 3:
                bt["last"] = Image.frombytes("RGB", (VIDEO_W, VIDEO_H), buf)
            if bt["last"] is None:
                return
            pic = bt["last"]
        card = _frame_card(pic)
        inn = ease(min(1.0, (t - bt["t0"]) / 0.28))
        a = min(1.0, (t - bt["t0"]) / 0.12, (bt["t1"] - t) / 0.15)
        sc = 0.94 + 0.06 * inn
        if sc < 0.999:
            card = card.resize((int(card.width * sc), int(card.height * sc)), Image.BILINEAR)
        head = _STATE["hy"] if _STATE["hy"] is not None else 640.0
        bottom = head + 60 + 44  # card's lower edge tucks ~60 px behind the top of his head
        y = int(max(CARD_TOP - 44, bottom - card.height)) - int(40 * (1 - inn))
        x = (W - card.width) // 2
        before = comp.copy()
        over(comp, card, x, y, a)
        m = cur.get("mask")
        if m is not None:  # his head in front of the card
            mm = np.clip(m, 0, 1)[..., None]
            comp[:] = comp * (1 - mm) + before * mm
        return


def main():
    global BROLL_DIR, WORDS, GAZE, MATTE_MODEL
    import ea_cut_edit as eng
    ap = argparse.ArgumentParser()
    for k in ("src", "words", "selfie", "out", "broll"):
        ap.add_argument(k)
    ap.add_argument("--only")
    ap.add_argument("--final")
    ap.add_argument("--gaze")
    ap.add_argument("--matte")
    a = ap.parse_args()
    GAZE, MATTE_MODEL = a.gaze, a.matte
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
