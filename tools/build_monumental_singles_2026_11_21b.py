"""Three more single-image posts (21 Nov 2026), drawn in the Monumental kit (no AI images).

your-circle (rotting orange idea), success-switches (toggle list), iceberg (training vs nutrition,
corrected: no fake 80/20 statistic).

Usage: python3 tools/build_monumental_singles_2026_11_21b.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from build_monumental_singles_2026_11_13 import body_lines, ctext, eyebrow, fit, folder, save
from build_monumental_singles_2026_11_21 import CRIMSON, DIM
from monumental_type import BONE, GOLD, HEAD, INK, LGOLD, STONE, UTIL, H, W, font, frame, surface, tracked, tracked_width

MOULD = (92, 98, 88)


def disc(img, cx, cy, r, base, spots=(), seed=0):
    """A shaded fruit-like sphere with optional mould spots (x, y, r relative to centre)."""
    rng = np.random.default_rng(seed)
    size = r * 2 + 4
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) - (r + 2)
    dist = np.sqrt(xx ** 2 + yy ** 2)
    mask = np.clip(r - dist, 0, 1)
    light = np.clip(1.15 - np.sqrt((xx + r * .35) ** 2 + (yy + r * .4) ** 2) / (r * 1.7), .35, 1.1)
    col = np.array(base, np.float32)[None, None, :] * light[..., None]
    col += rng.normal(0, 6, (size, size))[..., None]
    for sx, sy, sr in spots:
        d = np.sqrt((xx - sx * r) ** 2 + (yy - sy * r) ** 2) / (sr * r)
        a = np.clip(1.25 - d, 0, 1) ** .8
        rim = np.clip(1 - abs(d - 1.0) * 4, 0, 1) * .6
        mould = np.array(MOULD, np.float32) + rng.normal(0, 18, (size, size))[..., None]
        col = col * (1 - rim[..., None]) + np.array((40, 30, 20), np.float32) * rim[..., None]
        col = col * (1 - a[..., None]) + mould * a[..., None]
    tile = Image.fromarray(np.clip(col, 0, 255).astype("uint8"))
    alpha = Image.fromarray((mask * 255).astype("uint8"))
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse((cx - r * .9, cy + r * .78, cx + r * .9, cy + r * 1.02), fill=150)
    img.paste(Image.new("RGB", (W, H), (4, 4, 4)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(18)))
    img.paste(tile, (cx - r - 2, cy - r - 2), alpha)


def your_circle():
    slug = "your-circle"
    src = Image.open(folder(slug) / "source-images/oranges.png").convert("RGB")
    src = src.resize((W, round(src.height * W / src.width)), Image.LANCZOS)
    img = Image.new("RGB", (W, H), INK)
    img.paste(src, (0, (H - src.height) // 2))
    a = np.asarray(img, np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]
    shade = np.clip((yy - 1060) / 140, 0, 1) * .75 + np.clip((420 - yy) / 420, 0, 1) * .35
    a = a * (1 - shade[..., None]) + np.array(INK, np.float32) * shade[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(img)
    eyebrow(d, 96, "CHOOSE CAREFULLY")
    y = ctext(d, 146, "WHO YOU SURROUND", font(HEAD, 92), BONE) + 16
    y = ctext(d, y, "YOURSELF WITH", font(HEAD, 92), BONE) + 16
    ctext(d, y, "MATTERS.", font(HEAD, 124), GOLD)
    lf = font(UTIL, 18)
    for cx, t, c in ((195, "ROT", STONE), (538, "SPREADING", LGOLD), (888, "UNTOUCHED", GOLD)):
        tracked(d, cx - tracked_width(t, lf, 4) / 2, 1052, t, lf, c, 4)
    body_lines(d, 1104, "Rot spreads. So does discipline. Choose your circle.", 28, 940, BONE)
    save(img, slug, "01-your-circle")


SWITCHES = [("CONSISTENCY", True), ("DISCIPLINE", True), ("EXCUSES", False), ("HARD WORK", True),
            ("PROCRASTINATION", False), ("SELF-PITY", False)]


def toggle(d, x, y, on):
    w, h = 150, 64
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=GOLD if on else (34, 32, 30),
                        outline=GOLD if on else DIM, width=2)
    kx = x + w - h // 2 if on else x + h // 2
    d.ellipse((kx - 24, y + 8, kx + 24, y + h - 8), fill=INK if on else STONE)


def success_switches():
    slug = "success-switches"
    img = surface(82, light=(0.9, 0.05))
    frame(img)
    d = ImageDraw.Draw(img)
    eyebrow(d, 130, "SETTINGS")
    ctext(d, 180, "SUCCESS", font(HEAD, 150), BONE)
    top, rh = 420, 112
    for i, (name, on) in enumerate(SWITCHES):
        y0 = top + i * rh
        hf = fit(HEAD, name, 58, 560)
        d.text((180, y0 + 32 - hf.getbbox("H")[1]), name, font=hf, fill=BONE if on else STONE)
        toggle(d, 750, y0 + 4, on)
    body_lines(d, top + 6 * rh + 30, "You don't find these settings. You choose them every morning.", 26, 940, LGOLD)
    save(img, slug, "01-success-switches")


def iceberg():
    slug = "iceberg"
    img = surface(83, light=(0.5, 0.0))
    d = ImageDraw.Draw(img)
    eyebrow(d, 80, "WHAT ACTUALLY CHANGES YOUR BODY")
    ctext(d, 126, "THE PART", font(HEAD, 104), BONE)
    ctext(d, 236, "NOBODY SEES.", font(HEAD, 104), GOLD)
    water = 520
    # water below the line
    a = np.asarray(img, np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]
    deep = np.clip((yy - water) / 700, 0, 1) * (yy > water)
    a = a * (1 - deep[..., None] * .45) + np.array((14, 18, 22), np.float32) * deep[..., None] * .45
    img = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(img)
    tip = [(470, water), (520, 420), (560, 440), (600, 395), (660, water)]
    d.polygon(tip, fill=BONE)
    body = [(430, water), (690, water), (770, 590), (835, 700), (815, 820), (850, 900), (760, 990),
            (640, 1035), (540, 1020), (430, 1040), (330, 950), (300, 830), (265, 720), (330, 610)]
    under = Image.new("L", (W, H), 0)
    ImageDraw.Draw(under).polygon(body, fill=255)
    img.paste(Image.new("RGB", (W, H), (58, 54, 46)), (0, 0), under.filter(ImageFilter.GaussianBlur(1)))
    d = ImageDraw.Draw(img)
    d.polygon(body, outline=GOLD, width=2)
    d.line((60, water, W - 60, water), fill=GOLD, width=2)
    lf = font(UTIL, 20)
    tracked(d, 700, 445, "TRAINING", lf, BONE, 4)
    lines = ["NUTRITION", "SLEEP", "DAILY STEPS", "CONSISTENCY"]
    y = 625
    for t in lines:
        f = font(HEAD, 54)
        ctext(d, y, t, f, GOLD, cx=555)
        y += 100
    body_lines(d, 1085, "It's not an exact 80/20. But you can't out-train your plate.", 28, 900, BONE)
    save(img, slug, "01-iceberg")


def main():
    your_circle()
    success_switches()
    iceberg()


if __name__ == "__main__":
    main()
