"""Build Edison's "50 MORE DAYS" talking-head Reel (edison-full-message skill).

Single 78-second selfie take (IMG_8021.MOV): full message kept, word-timed captions,
depth titles behind the moving head (per-frame selfie segmentation), a 2026 progress
card, strike-through "NEW YEAR, NEW ME", rising "HIGHER" titles, slam shakes, a light
grade and a CTD end card.

    python3 -I tools/build_ea_50_more_days.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only 0:10]

WORDS.json is a list of {"w","t","e"} from local ASR. Writes video-only.mp4 into OUT_DIR;
audio is built separately by tools/mix_ea_50_more_days.py.
"""
import argparse
import json
import pathlib
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS = ROOT / "brand/fonts"
W, H, FPS = 1080, 1920, 30
END_CARD = 2.5  # seconds appended after the speech

OBSIDIAN = (7, 8, 10)
IVORY = (246, 239, 226)
GOLD = (214, 169, 24)
PALE_GOLD = (243, 216, 120)
SILVER = (170, 176, 185)
CRIMSON = (152, 27, 46)

GRADE = ("scale=1080:1920:flags=lanczos,"
         "eq=contrast=1.07:saturation=0.93:gamma=0.97,"
         "colorbalance=rs=0.02:bs=0.03:rm=0.02:bm=-0.02,"
         "vignette=PI/5")


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


BARLOW = "BarlowCondensed-ExtraBold.ttf"
BODONI = "BodoniModa-Black.ttf"
MONT_B = "Montserrat-Bold.ttf"
MONT_M = "Montserrat-Medium.ttf"


# ---------------------------------------------------------------- text rendering
def text_size(f, s, tracking=0):
    w = sum(f.getlength(c) for c in s) + tracking * max(len(s) - 1, 0)
    asc, desc = f.getmetrics()
    return int(w), asc + desc


def draw_tracked(d, xy, s, f, fill, tracking=0):
    x, y = xy
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += f.getlength(c) + tracking


def dimensional(s, f, face=IVORY, edge=(120, 92, 12), tracking=0, depth=7, glow=0.55):
    """Ivory/gold face with an extruded edge, top-light gradient and a soft dark halo."""
    tw, th = text_size(f, s, tracking)
    pad = 40
    cw, ch = tw + pad * 2 + depth, th + pad * 2 + depth
    mask = Image.new("L", (cw, ch), 0)
    draw_tracked(ImageDraw.Draw(mask), (pad, pad), s, f, 255, tracking)
    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    # soft halo for readability on bright sky
    halo = mask.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * glow))
    out.paste(Image.new("RGBA", (cw, ch), OBSIDIAN + (255,)), (0, 0), halo)
    # extrusion
    for k in range(depth, 0, -1):
        shade = tuple(int(c * (0.55 + 0.45 * (1 - k / depth))) for c in edge)
        out.paste(Image.new("RGBA", (cw, ch), shade + (255,)), (k, k), mask)
    # face with vertical light gradient
    grad = np.linspace(1.08, 0.86, ch)[:, None, None]
    facearr = np.clip(np.array(face, np.float32)[None, None, :] * grad, 0, 255).astype(np.uint8)
    facearr = np.repeat(facearr, cw, axis=1)
    out.paste(Image.fromarray(facearr, "RGB"), (0, 0), mask)
    bb = mask.getbbox()
    out.info["glyph"] = (bb[1], bb[3] + depth)
    return out


def plain(s, f, fill, tracking=0, shadow=0.5):
    tw, th = text_size(f, s, tracking)
    pad = 24
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    draw_tracked(ImageDraw.Draw(m), (pad, pad), s, f, 255, tracking)
    sh = m.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * shadow))
    img.paste(Image.new("RGBA", img.size, OBSIDIAN + (255,)), (2, 4), sh)
    img.paste(Image.new("RGBA", img.size, fill + (255,)), (0, 0), m)
    return img


# ---------------------------------------------------------------- compositing helpers
def over(base, rgba, x, y, alpha=1.0):
    """Alpha-composite an RGBA PIL image onto a float32 HxWx3 array in place."""
    a = np.asarray(rgba, np.float32)
    h, w = a.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    src = a[y0 - y:y1 - y, x0 - x:x1 - x]
    al = src[..., 3:4] / 255.0 * alpha
    reg = base[y0:y1, x0:x1]
    reg[:] = reg * (1 - al) + src[..., :3] * al


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def env(t, t0, t1, fin=0.25, fout=0.2):
    if t < t0 or t > t1:
        return 0.0
    return min(ease((t - t0) / fin), ease((t1 - t) / fout))


# ---------------------------------------------------------------- the edit
def build_events():
    """Depth titles (behind the head) and front cards, keyed to spoken word times."""
    big = font(BARLOW, 230)
    huge = font(BARLOW, 300)
    serif = font(BODONI, 190)
    small = font(MONT_B, 44)
    ev = []

    def depth(t0, t1, img, y=None, rise=0, slam=False, kind="depth"):
        ev.append(dict(t0=t0, t1=t1, img=img, y=y, rise=rise, slam=slam, kind=kind))

    gold = lambda s, f=big, tr=4: dimensional(s, f, face=PALE_GOLD, edge=(110, 80, 8), tracking=tr)
    ivory = lambda s, f=big, tr=4: dimensional(s, f, face=IVORY, edge=(90, 90, 96), tracking=tr)
    crimson = lambda s, f=huge, tr=2: dimensional(s, f, face=(214, 52, 70), edge=(70, 10, 20), tracking=tr)

    depth(0.70, 4.05, gold("50 MORE DAYS"))
    depth(4.12, 5.95, crimson("NOTHING."), slam=True)
    depth(7.15, 9.60, ivory("DECEMBER"))
    depth(19.00, 21.95, gold("COMPLETELY.", serif, 0))
    depth(23.00, 25.25, gold("START NOW.", serif, 0))
    depth(24.70, 25.25, gold("START NOW.", serif, 0), slam=True)
    depth(25.65, 28.40, ivory("2027?"))
    depth(30.60, 32.55, crimson("NONSENSE.", huge), slam=True)
    depth(33.95, 35.85, gold("HABITS.", serif, 0))
    depth(37.95, 41.50, ivory("OTHER PEOPLE"))
    depth(41.55, 42.35, crimson("WHY?"), slam=True)
    depth(42.40, 45.60, gold("COMMITTED.", serif, 0))
    depth(48.15, 49.30, ivory("SAME HABITS"))
    depth(49.30, 49.85, ivory("OVER"))
    depth(49.85, 50.35, ivory("AND OVER"))
    depth(50.35, 51.95, ivory("AND OVER AGAIN."))
    depth(52.00, 52.90, ivory("3 YEARS", huge))
    depth(52.90, 55.20, gold("5 YEARS", huge))
    depth(55.20, 56.65, ivory("SAME POSITION"))
    depth(60.90, 63.15, gold("HIGHER SELF", serif, 0), rise=110)
    depth(64.55, 65.60, gold("50 MORE DAYS."))
    depth(72.40, 74.30, gold("HIGHER HEIGHTS", serif, 0), rise=110)
    depth(75.38, 76.30, crimson("LOSER?"), slam=True)
    depth(76.35, 77.87, ivory("UP TO YOU."))

    # front: strike-through "NEW YEAR, NEW ME" (typed on), then struck at "Nonsense"
    ev.append(dict(t0=28.50, t1=30.75, kind="newyear", f=font(BARLOW, 120)))
    # front: 2026 progress card while he talks about the year (50 days left -> 315/365 gone)
    ev.append(dict(t0=9.70, t1=14.70, kind="progress", f=small, fb=font(BARLOW, 96)))
    return ev


def caption_groups(words):
    words = [dict(w) for w in words]
    for w in words:  # verified cross-model: "...because you cannot get the habits..."
        if w["w"] == "cannot.":
            w["w"] = "cannot"
        if w["w"] == "Get":
            w["w"] = "get"
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        gap = words[i + 1]["t"] - w["e"] if i + 1 < len(words) else 9
        if w["w"][-1] in ".,?!" or len(cur) == 4 or gap > 0.35:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    out = []
    for gi, g in enumerate(groups):
        t1 = g[-1]["e"] + 0.15
        if gi + 1 < len(groups):
            t1 = min(t1, groups[gi + 1][0]["t"])
        out.append(dict(t0=g[0]["t"] - 0.05, t1=t1, words=g))
    return out


def render_caption(group, t, f):
    toks = [w["w"].upper() for w in group["words"]]
    sp = 22
    widths = [text_size(f, s, 1)[0] for s in toks]
    total = sum(widths) + sp * (len(toks) - 1)
    pad = 30
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (total + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    m_all = Image.new("L", img.size, 0)
    d_all = ImageDraw.Draw(m_all)
    x = pad
    active = None
    for k, (s, wd) in enumerate(zip(toks, widths)):
        draw_tracked(d_all, (x, pad), s, f, 255, 1)
        if group["words"][k]["t"] <= t:
            active = (k, x, wd)
        x += wd + sp
    sh = m_all.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.75))
    img.paste(Image.new("RGBA", img.size, OBSIDIAN + (255,)), (2, 4), sh)
    img.paste(Image.new("RGBA", img.size, IVORY + (255,)), (0, 0), m_all)
    if active is not None:
        k, ax, wd = active
        m = Image.new("L", img.size, 0)
        draw_tracked(ImageDraw.Draw(m), (ax, pad), toks[k], f, 255, 1)
        img.paste(Image.new("RGBA", img.size, PALE_GOLD + (255,)), (0, 0), m)
    return img


def refine_mask(m256, frame):
    """Upsample the 256x256 selfie mask, then pull bright blue sky out of the edge band."""
    m = np.asarray(Image.fromarray((m256 * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                   np.float32) / 255.0
    m = np.clip((m - 0.3) / 0.4, 0, 1)
    r, g, b = frame[..., 0], frame[..., 1], frame[..., 2]
    sky = np.clip((b - r - 45) / 40, 0, 1) * np.clip((b - 150) / 40, 0, 1)
    band = (m > 0.02) & (m < 0.98)
    m[band] *= 1 - sky[band]
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("words")
    ap.add_argument("selfie")
    ap.add_argument("out")
    ap.add_argument("--only", help="start:end seconds for proofs")
    a = ap.parse_args()
    from ai_edge_litert.interpreter import Interpreter

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    words = json.load(open(a.words))
    caps = caption_groups(words)
    events = build_events()
    capf = font(BARLOW, 84)

    it = Interpreter(model_path=a.selfie)
    it.allocate_tensors()
    iin = it.get_input_details()[0]["index"]
    iout = it.get_output_details()[0]["index"]

    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.src]))
    ss, to = 0.0, dur
    if a.only:
        ss, to = (float(v) for v in a.only.split(":"))
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
    prev_m = None
    last = None
    head = 450.0  # smoothed head-top row; titles sit so the head overlaps them by ~30 px
    n = 0
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
            head = 0.85 * head + 0.15 * float(np.clip(rows[0], 380, 540))

        comp = frame.copy()
        # depth layer: titles sit between sky and the real moving body
        shake = (0, 0)
        for e in events:
            if e["kind"] != "depth":
                continue
            al = env(t, e["t0"], e["t1"], 0.12 if e["slam"] else 0.25)
            if al <= 0:
                continue
            img = e["img"]
            u = (t - e["t0"]) / max(e["t1"] - e["t0"], 1e-3)
            sc = 1.0
            if e["slam"]:
                sc = 1.25 - 0.25 * ease((t - e["t0"]) / 0.12)
                if t - e["t0"] < 0.2:
                    k = int((t - e["t0"]) * FPS)
                    shake = ((-14, 10, -7, 5, -3, 0)[min(k, 5)], (8, -10, 6, -4, 2, 0)[min(k, 5)])
            else:
                sc = 1.04 - 0.04 * ease((t - e["t0"]) / 0.4)
            fit = min(1.0, (W - 80) / (img.width * sc))
            sc *= fit
            if sc != 1.0:
                img = img.resize((int(img.width * sc), int(img.height * sc)), Image.BILINEAR)
            gt, gb = e["img"].info.get("glyph", (40, e["img"].height - 40))
            y = int(head + 30 - gb * sc)
            y = max(y, 235 - int(gt * sc))  # keep glyph tops inside the safe area
            y -= int(e["rise"] * ease(u)) - int(24 * (1 - ease((t - e["t0"]) / 0.3)))
            over(comp, img, (W - img.width) // 2, y, al)
        mm = m[..., None]
        comp = frame * mm + comp * (1 - mm)

        # whole-picture camera move: slam shake, plus a slow push through the closing minute
        push = 1.0 + 0.035 * ease((t - 63.0) / 14.0) if t > 63 else 1.0
        if push != 1.0 or shake != (0, 0):
            im = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
            nw, nh = int(W * push), int(H * push)
            im = im.resize((nw, nh), Image.BILINEAR)
            ox = (nw - W) // 2 - shake[0]
            oy = (nh - H) // 2 - shake[1]
            canvas = Image.new("RGB", (W + 40, H + 40))
            canvas.paste(im, (20 - ox, 20 - oy))
            comp = np.asarray(canvas.crop((20, 20, 20 + W, 20 + H)), np.float32).copy()

        last = np.clip(comp, 0, 255).astype(np.uint8)  # end-card freeze: no captions
        # front layer: progress card, new-year strike, captions
        for e in events:
            al = env(t, e["t0"], e["t1"])
            if al <= 0:
                continue
            if e["kind"] == "progress":
                u = ease((t - e["t0"] - 0.3) / 2.2)
                pct = 315 / 365 * u
                card = Image.new("RGBA", (760, 170), (0, 0, 0, 0))
                d = ImageDraw.Draw(card)
                d.rounded_rectangle((0, 0, 759, 169), 18, fill=OBSIDIAN + (178,))
                d.text((34, 22), "2026", font=e["fb"], fill=IVORY)
                d.text((250, 34), f"{pct * 100:4.1f}% GONE", font=e["f"], fill=PALE_GOLD)
                d.text((250, 88), "50 DAYS LEFT" if u > 0.98 else "LOADING...", font=e["f"],
                       fill=SILVER)
                d.rectangle((34, 142, 725, 150), fill=(60, 64, 72))
                d.rectangle((34, 142, 34 + int(691 * pct), 150), fill=GOLD)
                over(comp, card, (W - 760) // 2, 262, al)
            elif e["kind"] == "newyear":
                s = "NEW YEAR, NEW ME"
                typed = s[:max(0, min(len(s), int((t - e["t0"]) / 1.2 * len(s)) + 1))]
                img = plain(typed, e["f"], IVORY, 3)
                full_w = text_size(e["f"], s, 3)[0]
                if t >= 30.30:
                    d = ImageDraw.Draw(img)
                    k = ease((t - 30.30) / 0.15)
                    d.rectangle((24, img.height // 2 - 2, 24 + int(full_w * k), img.height // 2 + 10),
                                fill=CRIMSON + (255,))
                over(comp, img, (W - full_w) // 2 - 24, 250, al)
        for g in caps:
            if g["t0"] <= t < g["t1"]:
                ci = render_caption(g, t, capf)
                if ci.width > W - 96:
                    ci = ci.resize((W - 96, int(ci.height * (W - 96) / ci.width)), Image.LANCZOS)
                over(comp, ci, (W - ci.width) // 2, 1330, env(t, g["t0"], g["t1"], 0.08, 0.06))
                break

        enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())

    # end card: freeze the last frame, fade to obsidian, CTD logo + name + footer
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
