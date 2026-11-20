"""Build Edison's "WHICH ONE ARE YOU?" mindset race (original animated Reel, CTD brand).

Four neon runners, one per mindset (MOTIVATION, EGO, TALENT, DISCIPLINE), race down a night track
whose gates count days (DAY 7 -> DAY 365). Motivation fades, Ego burns out, Talent coasts to a stop;
Discipline holds the same pace, crosses DAY 365 and keeps running. Rendered procedurally (pseudo-3D
perspective, additive glow), original synth bed + SFX, CTD end card. Inspired by the race-of-mindsets
format; characters, script, track and sound are our own.

    python3 -I tools/build_ea_mindset_race.py OUT_DIR --final OUT.mp4
"""
import argparse
import math
import pathlib
import subprocess
import sys

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, FPS, GOLD, H, IVORY, MONT_B, MONT_M, OBSIDIAN, PALE_GOLD, ROOT, W, ease, font,
    over, plain)
from mix_ea_50_more_days import impact, whoosh  # noqa: E402

SR = 48000
F = 1000.0           # focal length (px)
HORIZON = 760
CAM_H = 1.75
GO = 3.0             # race start (s)
END_CARD = 2.5

AMBER = (255, 150, 40)
RED = (235, 50, 70)
STEEL = (150, 190, 255)
GOLDN = (255, 205, 60)

RUNNERS = {
    "MOTIVATION": dict(x=-2.1, col=AMBER),
    "EGO": dict(x=-0.7, col=RED),
    "DISCIPLINE": dict(x=0.7, col=GOLDN),
    "TALENT": dict(x=2.1, col=STEEL),
}
V_D = 5.5
GATES = [(20.0, "DAY 7"), (45.0, "DAY 30"), (75.0, "DAY 90"), (92.0, "DAY 180"), (107.0, "DAY 365")]
FINISH_Z = GATES[-1][0]

LINES = [  # (start, end, runner, text)
    (3.4, 5.0, "MOTIVATION", "LET'S GOOO!"),
    (4.0, 5.6, "EGO", "CAMERA ON ME."),
    (5.5, 6.9, "TALENT", "natural."),
    (6.7, 8.3, "DISCIPLINE", "same pace."),
    (7.5, 9.1, "EGO", "who's the slow guy?"),
    (9.1, 10.7, "MOTIVATION", "I'll go hard Monday."),
    (9.7, 11.3, "TALENT", "I don't even need to train."),
    (10.8, 12.2, "DISCIPLINE", "same pace."),
    (11.6, 13.2, "EGO", "NOT LIKE THIS!"),
    (12.7, 14.2, "MOTIVATION", "...I'm done."),
    (14.3, 15.9, "TALENT", "wait... why is it hard now?"),
    (16.5, 18.1, "DISCIPLINE", "one more day."),
    (19.5, 21.1, "DISCIPLINE", "again tomorrow."),
]


# ---------------------------------------------------------------- motion
def speed(name, tau):
    """Speed (m/s) of each runner at race time tau (s since GO)."""
    if tau <= 0:
        return 0.0
    ramp = min(1.0, tau / 0.6)
    if name == "DISCIPLINE":
        return V_D * ramp
    if name == "MOTIVATION":
        v = np.interp(tau, [0, 3, 7, 9, 9.5], [9, 9, 2.5, 2.5, 0])
    elif name == "EGO":
        v = np.interp(tau, [0, 8.6, 9.2], [10.5, 10.5, 0])
    else:  # TALENT
        v = np.interp(tau, [0, 5, 9, 12, 14], [7, 7, 4.5, 2, 0])
    return float(v) * ramp


DT = 1 / (FPS * 4)
_ts = np.arange(0, 40, DT)
POS = {n: np.concatenate([[0], np.cumsum([speed(n, t - GO) * DT for t in _ts[:-1]])]) for n in RUNNERS}


def zpos(name, t):
    return float(np.interp(t, _ts, POS[name]))


T_FINISH = float(np.interp(FINISH_Z, POS["DISCIPLINE"], _ts))
T_TITLE = T_FINISH + 0.4
T_END = T_TITLE + 3.6        # end card starts
TOTAL = T_END + END_CARD


def cam_z(t):
    zd = zpos("DISCIPLINE", min(t, T_FINISH + 0.8))
    if t > T_FINISH:  # camera eases to a stop while Discipline keeps going
        u = min(1.0, (t - T_FINISH) / 1.6)
        zd = zpos("DISCIPLINE", T_FINISH) + V_D * 1.6 * (1 - (1 - u) ** 2) / 2
    intro = 3.6 * (1 - ease(min(1.0, t / (GO + 0.6))))
    return zd - 4.4 - intro


CAM_X = 0.2


def proj(x, y, z, zc):
    d = z - zc
    if d < 0.35:
        return None
    return (W / 2 + F * (x - CAM_X) / d, HORIZON + F * (CAM_H - y) / d, F / d)


# ---------------------------------------------------------------- static background
def background():
    a = np.zeros((H, W, 3), np.float32)
    ys = np.arange(H)[:, None]
    top = np.array([3, 5, 10], np.float32)
    hor = np.array([18, 24, 40], np.float32)
    g = np.clip(ys / HORIZON, 0, 1)[..., None]
    a[:] = top * (1 - g) + hor * g
    a[HORIZON:] = np.array([8, 10, 15], np.float32)
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    # stands: dark band with tiny seat lights
    d.rectangle([0, HORIZON - 150, W, HORIZON], fill=(12, 14, 22))
    rng = np.random.default_rng(7)
    for _ in range(900):
        x, y = rng.integers(0, W), rng.integers(HORIZON - 145, HORIZON - 6)
        c = int(rng.integers(30, 80))
        d.point((x, y), fill=(c, c, c + 15))
    for x in range(0, W, 6):
        d.line([(x, HORIZON - 150), (x, HORIZON - 150 - (8 if x % 60 else 22))], fill=(16, 18, 28))
    glow = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(glow)
    for fx, fy in [(120, 300), (390, 250), (690, 250), (960, 300)]:  # floodlights
        gd.polygon([(fx - 40, fy), (fx + 40, fy), (W / 2 + (fx - W / 2) * 0.3 + 160, HORIZON),
                    (W / 2 + (fx - W / 2) * 0.3 - 160, HORIZON)], fill=(6, 7, 11))
        gd.rectangle([fx - 46, fy - 16, fx + 46, fy + 16], fill=(235, 240, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    base = np.asarray(im, np.float32) + np.asarray(glow, np.float32) * 2.2
    sharp = Image.new("RGB", (W, H))
    sd = ImageDraw.Draw(sharp)
    for fx, fy in [(120, 300), (390, 250), (690, 250), (960, 300)]:
        for i in range(4):
            for j in range(2):
                sd.ellipse([fx - 40 + i * 22, fy - 12 + j * 14, fx - 30 + i * 22, fy - 2 + j * 14], fill=(255, 255, 250))
    return np.clip(base + np.asarray(sharp, np.float32), 0, 255)


# ---------------------------------------------------------------- figures
def pose(name, t, z):
    """Joint positions (metres, x right / y up, back view) for a runner at time t."""
    tau = t - GO
    v = speed(name, tau)
    ph = z * math.pi / 1.35 + {"MOTIVATION": 0.4, "EGO": 1.9, "DISCIPLINE": 0, "TALENT": 2.8}[name]
    state = "run"
    if tau < 0:
        state = "ready"
    elif name == "EGO" and tau > 8.7:
        state = "kneel"
    elif name == "MOTIVATION" and tau > 9.4:
        state = "sit"
    elif name == "TALENT" and tau > 13.6:
        state = "bent"
    amp = 1.0 if v > 4 else max(0.35, v / 4)
    if state == "run":
        bob = 0.05 * abs(math.sin(ph)) * amp
        hip, sh, head = 0.95 + bob, 1.42 + bob, 1.62 + bob
        J = {"head": (0, head)}
        segs = [((0, sh), (0, hip))]
        for s in (-1, 1):
            lift = max(0.0, math.sin(ph + (0 if s < 0 else math.pi))) * amp
            knee = (s * 0.13, 0.5 + 0.2 * lift)
            foot = (s * 0.1, 0.02 + 0.38 * lift)
            segs += [((s * 0.09, hip), knee), (knee, foot)]
            sw = math.sin(ph + (math.pi if s < 0 else 0)) * amp
            elbow = (s * 0.3, sh - 0.26 + 0.1 * sw)
            hand = (s * 0.2, sh - 0.42 + 0.3 * sw)
            segs += [((s * 0.2, sh), elbow), (elbow, hand)]
        segs.append(((-0.2, sh), (0.2, sh)))
    elif state == "ready":
        sway = 0.02 * math.sin(t * 3 + len(name))
        hip, sh = 0.92, 1.4
        J = {"head": (sway, 1.6)}
        segs = [((0, sh), (0, hip)), ((-0.2, sh), (0.2, sh))]
        for s in (-1, 1):
            segs += [((s * 0.09, hip), (s * 0.15, 0.48)), ((s * 0.15, 0.48), (s * 0.13, 0.02)),
                     ((s * 0.2, sh), (s * 0.3, 1.14)), ((s * 0.3, 1.14), (s * 0.24, 0.9))]
    elif state == "kneel":  # Ego: down on both knees, head dropped
        u = min(1.0, (tau - 8.7) / 0.35)
        hip = 0.95 - 0.45 * u
        sh = hip + 0.4
        J = {"head": (0.04, sh + 0.12)}
        segs = [((0, sh), (0, hip)), ((-0.2, sh), (0.2, sh))]
        for s in (-1, 1):
            segs += [((s * 0.1, hip), (s * 0.2, 0.06)), ((s * 0.2, 0.06), (s * 0.16, 0.02)),
                     ((s * 0.2, sh), (s * 0.28, sh - 0.25)), ((s * 0.28, sh - 0.25), (s * 0.3, 0.05))]
    elif state == "sit":  # Motivation: sits down on the track
        u = min(1.0, (tau - 9.4) / 0.5)
        hip = 0.95 - 0.7 * u
        sh = hip + 0.43
        J = {"head": (0, sh + 0.17)}
        segs = [((0, sh), (0, hip)), ((-0.2, sh), (0.2, sh))]
        for s in (-1, 1):
            segs += [((s * 0.1, hip), (s * 0.42, hip + 0.12)), ((s * 0.42, hip + 0.12), (s * 0.5, 0.02)),
                     ((s * 0.2, sh), (s * 0.34, sh - 0.22)), ((s * 0.34, sh - 0.22), (s * 0.4, hip + 0.1))]
    else:  # bent: Talent, hands on knees
        u = min(1.0, (tau - 13.6) / 0.5)
        hip = 0.92
        sh = 1.4 - 0.28 * u
        J = {"head": (0, sh + 0.12 - 0.05 * u)}
        segs = [((0, sh), (0, hip)), ((-0.2, sh), (0.2, sh))]
        for s in (-1, 1):
            segs += [((s * 0.09, hip), (s * 0.16, 0.5)), ((s * 0.16, 0.5), (s * 0.12, 0.02)),
                     ((s * 0.2, sh), (s * 0.24, sh - 0.25)), ((s * 0.24, sh - 0.25), (s * 0.17, 0.55))]
    return J, segs


def draw_runner(d, name, t, zc):
    r = RUNNERS[name]
    z = zpos(name, t)
    p = proj(r["x"], 0, z, zc)
    if p is None:
        return None
    sx, sy, s = p
    if sy > H + 400:
        return None
    J, segs = pose(name, t, z)
    lw = max(2, int(0.085 * s))
    col = r["col"]
    for (a, b) in segs:
        d.line([(sx + a[0] * s, sy - a[1] * s), (sx + b[0] * s, sy - b[1] * s)], fill=col, width=lw)
    for (a, b) in segs:  # rounded joints
        for q in (a, b):
            d.ellipse([sx + q[0] * s - lw / 2, sy - q[1] * s - lw / 2, sx + q[0] * s + lw / 2, sy - q[1] * s + lw / 2], fill=col)
    hx, hy = J["head"]
    rr = 0.13 * s
    d.ellipse([sx + hx * s - rr, sy - hy * s - rr, sx + hx * s + rr, sy - hy * s + rr], fill=col)
    return (sx + hx * s, sy - hy * s - rr, s)


# ---------------------------------------------------------------- track / gates
_plaques = {}


def plaque(label, final):
    if label not in _plaques:
        f = font(BARLOW, 150)
        tw = int(f.getlength(label)) + 80
        im = Image.new("RGBA", (tw, 200), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        col = GOLDN if final else (225, 230, 240)
        dd.rounded_rectangle([4, 4, tw - 4, 196], 22, fill=(8, 9, 13, 235), outline=col + (255,), width=8)
        dd.text((tw / 2, 100), label, font=f, fill=col + (255,), anchor="mm")
        _plaques[label] = im
    return _plaques[label]


def draw_track(d, neon, zc, plates):
    near, far = zc + 0.4, zc + 260
    edge = [proj(x, 0, z, zc) for x, z in ((-2.9, near), (2.9, near), (2.9, far), (-2.9, far))]
    d.polygon([(p[0], p[1]) for p in edge], fill=(20, 22, 31))
    for x in (-2.8, -1.4, 0.0, 1.4, 2.8):
        a, b = proj(x, 0, near, zc), proj(x, 0, far, zc)
        outer = abs(x) == 2.8
        neon.line([a[:2], b[:2]], fill=(190, 200, 220) if outer else (70, 76, 92), width=6 if outer else 3)
    for name, r in RUNNERS.items():  # lane light strips in each runner's colour
        k0 = int(math.floor((zc + 0.8) / 2.5))
        for k in range(k0, k0 + 40):
            z0 = k * 2.5
            if z0 - zc > 100:
                break
            a, b = proj(r["x"] - 0.55, 0, z0, zc), proj(r["x"] - 0.55, 0, z0 + 0.9, zc)
            if a is None or b is None:
                continue
            fog = math.exp(-(z0 - zc) / 60)
            c = tuple(int(v * 0.7 * fog) for v in r["col"])
            neon.line([a[:2], b[:2]], fill=c, width=max(1, int(0.1 * a[2])))
    for gz, label in GATES:  # overhead day gates
        final = label == GATES[-1][1]
        if not (zc + 6.0 < gz < zc + 140):
            continue
        fog = math.exp(-(gz - zc) / 90) * min(1.0, (gz - zc - 6.0) / 4.0)
        col = tuple(int(v * fog) for v in (GOLDN if final else (200, 210, 230)))
        pl, pr = proj(-3.1, 0, gz, zc), proj(3.1, 0, gz, zc)
        tl, tr = proj(-3.1, 4.0, gz, zc), proj(3.1, 4.0, gz, zc)
        w = max(2, int(0.12 * pl[2]))
        neon.line([pl[:2], tl[:2]], fill=col, width=w)
        neon.line([pr[:2], tr[:2]], fill=col, width=w)
        neon.line([tl[:2], tr[:2]], fill=col, width=w)
        if final:  # finish line across the track
            neon.line([proj(-2.9, 0, gz, zc)[:2], proj(2.9, 0, gz, zc)[:2]], fill=col, width=max(3, int(0.25 * pl[2])))
        mid = proj(0, 4.0, gz, zc)
        img = plaque(label, final)
        tw = 2.6 * mid[2]
        if tw > 12:
            plates.append((gz, img, mid, tw, fog))


# ---------------------------------------------------------------- overlays
_bubbles = {}


def bubble(name, text):
    key = (name, text)
    if key not in _bubbles:
        col = RUNNERS[name]["col"]
        ft, fn = font(MONT_B, 44), font(BARLOW, 34)
        tw = int(ft.getlength(text))
        nw = int(fn.getlength(name)) + 12
        bw, bh = max(tw, nw) + 64, 150
        im = Image.new("RGBA", (bw, bh + 26), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.rounded_rectangle([3, 3, bw - 3, bh - 3], 30, fill=(8, 9, 13, 235), outline=col + (255,), width=5)
        dd.polygon([(bw / 2 - 18, bh - 6), (bw / 2 + 18, bh - 6), (bw / 2, bh + 22)], fill=col + (255,))
        dd.text((32, 22), name, font=fn, fill=col + (255,))
        dd.text((32, 68), text, font=ft, fill=IVORY + (255,))
        _bubbles[key] = im
    return _bubbles[key]


def headline():
    a = plain("DISCIPLINE DOESN'T SPRINT.", font(BARLOW, 118), IVORY, 3, 0.7)
    b = plain("IT JUST DOESN'T STOP.", font(BARLOW, 150), PALE_GOLD, 3, 0.7)
    fit = lambda im: im.resize((W - 90, int(im.height * (W - 90) / im.width)), Image.LANCZOS) if im.width > W - 90 else im
    return fit(a), fit(b)


def render(out, stills=None):
    bg = background()
    title_a = plain("WHICH ONE", font(BARLOW, 150), IVORY, 4, 0.7)
    title_b = plain("ARE YOU?", font(BARLOW, 170), PALE_GOLD, 4, 0.7)
    tags = {n: plain(n, font(BARLOW, 50), RUNNERS[n]["col"], 3, 0.8) for n in RUNNERS}
    nums = {k: plain(k, font(BARLOW, 260), PALE_GOLD, 0, 0.7) for k in ("3", "2", "1", "GO")}
    day_lbl = plain("DAY", font(MONT_B, 40), IVORY, 8, 0.6)
    pill = Image.new("RGBA", (300, 205), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, 299, 204], 34, fill=(8, 9, 13, 255), outline=(120, 96, 30, 255), width=3)
    hl_a, hl_b = headline()
    logo = Image.open(ROOT / "brand/assets/ctd-cinematic-logo.png").convert("RGBA").resize((520, 520), Image.LANCZOS)
    name_img = plain("EDISON AMBRISTER", font(MONT_B, 50), IVORY, 10, 0.3)
    foot = plain("DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", font(MONT_M, 30), PALE_GOLD, 4, 0.3)
    gz = [0.0] + [g for g, _ in GATES]
    gd = [1, 7, 30, 90, 180, 365]

    want = {int(round(x * FPS)) for x in stills} if stills else None
    enc = None if stills else subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "16", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-colorspace", "bt709", str(out / "video-only.mp4")], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    last = None
    for k in range(n):
        t = k / FPS
        if want is not None and k not in want and not (t >= T_END and k - 1 in want):
            if k > max(want):
                break
            if not (t >= T_END and last is None):
                continue
        if t >= T_END:
            u = ease(min(1.0, (t - T_END) / 0.6))
            comp = last * (1 - 0.92 * u) + np.array(OBSIDIAN, np.float32) * 0.92 * u
            over(comp, logo, (W - 520) // 2, 560, u)
            over(comp, name_img, (W - name_img.width) // 2, 1110, u)
            over(comp, foot, (W - foot.width) // 2, 1195, u)
            emit(enc, comp, out, k, t)
            continue
        zc = cam_z(t)
        base_im = Image.fromarray(bg.astype(np.uint8))
        neon_im = Image.new("RGB", (W, H))
        bd, nd = ImageDraw.Draw(base_im), ImageDraw.Draw(neon_im)
        plates = []
        draw_track(bd, nd, zc, plates)
        heads = {}
        for name in sorted(RUNNERS, key=lambda nm: -zpos(nm, t)):  # far to near
            hp = draw_runner(nd, name, t, zc)
            if hp:
                heads[name] = hp
        neon = np.asarray(neon_im, np.float32)
        small = neon_im.resize((W // 3, H // 3), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7))
        glow = np.asarray(small.resize((W, H), Image.BILINEAR), np.float32)
        comp = np.asarray(base_im, np.float32) + neon + glow * 1.6
        for gzz, img, mid, tw, fog in sorted(plates, key=lambda p: -p[0]):
            pw = int(tw)
            ph = int(img.height * pw / img.width)
            top = int(mid[1] - ph - 0.15 * mid[2])
            if pw > 900 or top < 400:
                continue
            im2 = img.resize((pw, ph), Image.LANCZOS)
            over(comp, im2, int(mid[0] - pw / 2), int(mid[1] - ph - 0.15 * mid[2]), min(1.0, fog * 1.3))
        # intro: title, tags, countdown
        if t < GO + 0.6:
            a = 1 - ease(max(0.0, (t - GO) / 0.6))
            ai = ease(min(1.0, t / 0.4))
            over(comp, title_a, (W - title_a.width) // 2, 250, a * ai)
            over(comp, title_b, (W - title_b.width) // 2, 390, a * ai)
            for name, (hx, hy, s) in heads.items():
                tg = tags[name]
                lift = 70 if name in ("EGO", "TALENT") else 0  # stagger neighbours so tags never collide
                over(comp, tg, int(min(max(hx - tg.width / 2, 10), W - 10 - tg.width)), int(hy - tg.height - 6 - lift), a * ai)
            for i, (k0, lab) in enumerate(((1.2, "3"), (1.8, "2"), (2.4, "1"), (GO, "GO"))):
                if k0 <= t < k0 + 0.55:
                    u = (t - k0) / 0.55
                    im = nums[lab]
                    sc = 1.25 - 0.25 * ease(min(1.0, u * 3))
                    im2 = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
                    over(comp, im2, (W - im2.width) // 2, 1300 - im2.height // 2, 1 - max(0.0, u - 0.6) / 0.4)
        # day counter
        if GO - 0.2 < t < T_TITLE + 0.3:
            day = int(round(np.interp(zpos("DISCIPLINE", t), gz, gd)))
            a = min(1.0, (t - GO + 0.2) / 0.4) * (1 - max(0.0, (t - T_TITLE) / 0.3))
            num = plain(str(day), font(BARLOW, 120), PALE_GOLD, 2, 0.7)
            over(comp, pill, (W - pill.width) // 2, 1392, a * 0.88)
            over(comp, day_lbl, (W - day_lbl.width) // 2, 1395, a)
            over(comp, num, (W - num.width) // 2, 1430, a)
        # speech bubbles
        placed = []
        for (t0, t1, name, text) in LINES:
            if t0 <= t < t1 and name in heads:
                hx, hy, s = heads[name]
                b = bubble(name, text)
                u = min(1.0, (t - t0) / 0.12)
                sc = 0.85 + 0.15 * ease(u)
                b2 = b.resize((int(b.width * sc), int(b.height * sc)), Image.LANCZOS) if sc < 1 else b
                x = int(min(max(hx - b2.width / 2, 30), W - 30 - b2.width))
                y = int(min(max(hy - b2.height - 14, 300), 1180))
                for (px, py, pw2, ph2) in placed:
                    if x < px + pw2 and px < x + b2.width and y < py + ph2 and py < y + b2.height:
                        y = py - b2.height - 12
                placed.append((x, y, b2.width, b2.height))
                over(comp, b2, x, y, min(1.0, (t1 - t) / 0.15, u * 1.5))
        # finale headline
        if t >= T_TITLE:
            u = ease(min(1.0, (t - T_TITLE) / 0.35))
            over(comp, hl_a, (W - hl_a.width) // 2, 300 + int(30 * (1 - u)), u)
            if t >= T_TITLE + 0.8:
                u2 = ease(min(1.0, (t - T_TITLE - 0.8) / 0.3))
                sc = 1.15 - 0.15 * u2
                im2 = hl_b.resize((int(hl_b.width * sc), int(hl_b.height * sc)), Image.LANCZOS)
                over(comp, im2, (W - im2.width) // 2, 440 - (im2.height - hl_b.height) // 2, u2)
        comp = np.clip(comp, 0, 255)
        last = comp
        emit(enc, comp, out, k, t)
    if enc:
        enc.stdin.close()
        enc.wait()
    print("video", round(TOTAL, 2), "s; finish at", round(T_FINISH, 2))


def emit(enc, comp, out, k, t):
    if enc:
        enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())
    else:
        Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8)).save(out / f"still_{t:05.2f}.png")


# ---------------------------------------------------------------- sound
def tone(freq, dur, amp=0.3, decay=6.0):
    t = np.arange(int(dur * SR)) / SR
    return (amp * np.sin(2 * np.pi * freq * t) * np.exp(-decay * t)).astype(np.float32)


def music(total):
    """Original 120 BPM synth-run bed in A minor: pad intro, drums + bass from GO, drums out at the finish."""
    n = int(total * SR)
    out = np.zeros(n, np.float32)
    t = np.arange(n) / SR
    beat = 0.5
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 196.0, 261.63), (196.0, 246.94, 293.66)]
    bassn = [110.0, 87.31, 65.41, 98.0]
    for i, c in enumerate(chords * 8):  # pads, 2 s per chord
        s0 = i * 2.0
        if s0 > total:
            break
        seg = (t >= s0) & (t < s0 + 2.05)
        tt = t[seg] - s0
        env = np.minimum(1, tt / 0.3) * np.minimum(1, (2.05 - tt) / 0.3)
        for f in c:
            out[seg] += 0.045 * env * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.003 * tt))
    rng = np.random.default_rng(3)
    k = 0
    while GO + k * beat / 2 < min(total, T_FINISH + 0.05):
        s = GO + k * beat / 2
        i0 = int(s * SR)
        if k % 2 == 0:  # kick
            kt = np.arange(int(0.25 * SR)) / SR
            kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 12) * 0.55
            out[i0:i0 + len(kick)] += kick[:n - i0]
        else:  # off-beat hat
            ht = int(0.05 * SR)
            hat = rng.standard_normal(ht).astype(np.float32)
            hat = np.diff(hat, prepend=0) * np.exp(-np.arange(ht) / SR * 70) * 0.08
            out[i0:i0 + ht] += hat[:n - i0]
        if k % 8 == 4:  # clap on 2 and 4
            ct = int(0.12 * SR)
            clap = rng.standard_normal(ct).astype(np.float32) * np.exp(-np.arange(ct) / SR * 30) * 0.12
            out[i0:i0 + ct] += clap[:n - i0]
        # bass 8ths following the chord
        bi = int(s // 2.0) % 4
        bt = np.arange(int(0.22 * SR)) / SR
        ph = 2 * np.pi * bassn[bi] * bt
        saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
        bass = (0.6 * np.sin(ph) + 0.25 * saw) * np.exp(-bt * 9) * 0.22
        out[i0:i0 + len(bass)] += bass[:n - i0]
        k += 1
    # riser into GO
    seg = (t > GO - 2.0) & (t < GO)
    tt = t[seg] - (GO - 2.0)
    out[seg] += (rng.standard_normal(seg.sum()) * 0.05 * (tt / 2.0) ** 2).astype(np.float32)
    fade = np.ones(n, np.float32)
    fade[-int(1.0 * SR):] = np.linspace(1, 0, int(1.0 * SR))
    return out * fade


def mix(out):
    n = int(TOTAL * SR)
    m = music(TOTAL)
    sfx = np.zeros(n, np.float32)

    def place(t, clip, g=1.0):
        i = int(t * SR)
        clip = clip[:max(0, n - i)]
        sfx[i:i + len(clip)] += clip * g

    for k0 in (1.2, 1.8, 2.4):
        place(k0, tone(880, 0.16, 0.22, 14))
    place(GO, tone(1760, 0.5, 0.25, 5))
    for (t0, _, _, _) in LINES:  # bubble pops
        place(t0, tone(1300, 0.07, 0.12, 45) + tone(1950, 0.07, 0.05, 50))
    place(11.6, impact(), 0.9)          # Ego hits the wall
    for gzz, label in GATES:            # whoosh as each gate passes overhead
        tg = float(np.interp(gzz - 5.0, POS["DISCIPLINE"], _ts))
        if tg < T_FINISH:
            place(tg - 0.2, whoosh(0.5, 0.12), 0.6)
    chord = sum(tone(f, 2.5, 0.12, 1.4) for f in (880, 1108.73, 1318.5, 1760))
    place(T_FINISH, chord)
    place(T_TITLE + 0.8, impact(), 0.7)
    place(T_END - 0.3, whoosh(0.6, 0.16), 0.6)
    mixd = m + sfx
    sf.write(out / "mix.wav", mixd / max(1.0, np.abs(mixd).max() / 0.95), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "mix.wav"), "-af",
                    "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-14:TP=-2.5:LRA=7",
                    "-ar", str(SR), str(out / "mix_ln.wav")], check=True)
    src, gain = out / "mix_ln.wav", 0.0
    for _ in range(4):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        integ = float([ln for ln in r.splitlines() if ln.strip().startswith("I:")][-1].split()[1])
        if src != out / "mix_ln.wav" and integ > -14.6:
            break
        gain = -14.0 - integ
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                        f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=false,"
                        "aresample=48000", "-ar", str(SR), str(out / "mix_final.wav")], check=True)
        subprocess.run(["cp", str(out / "mix_final.wav"), str(out / "mix_pass.wav")], check=True)
        src = out / "mix_pass.wav"


def finish(out, final):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "video-only.mp4"), "-i", str(out / "mix_final.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                    "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(final)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--final")
    ap.add_argument("--frames", help="comma-separated times: write PNG stills only")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.frames:
        render(out, stills=[float(x) for x in a.frames.split(",")])
        return
    render(out)
    mix(out)
    if a.final:
        finish(out, a.final)


if __name__ == "__main__":
    main()
