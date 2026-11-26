"""YouTube thumbnail (1280x720): 42-round calisthenics endurance EMOM, Monumental kit + CTD logo.

Usage: python3 tools/build_youtube_thumb_emom.py
Source photo: outputs/edison-ambrister-yt-emom-endurance/source-images/edison.jpg (Edison's own photo)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from monumental_type import BONE, GOLD, HEAD, INK, LGOLD, NUMERAL, ROOT, STONE, TOKENS, UTIL, font, tracked, tracked_width

OUT = ROOT / "outputs/edison-ambrister-yt-emom-endurance"
TW, TH = 1280, 720


def fit(path, text, size, width):
    f = font(path, size)
    while f.getlength(text) > width:
        f = font(path, f.size - 2)
    return f


def photo():
    im = ImageOps.exif_transpose(Image.open(OUT / "source-images/edison.jpg")).convert("RGB")
    im = im.crop((0, 60, im.width, 60 + round(im.width / 0.86)))
    im = im.resize((round(TH * im.width / im.height), TH), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.75)
    a = np.asarray(im, np.float32) / 255
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    # pull down bright, low-saturation background (sky, walls) and the overall exposure
    bg = np.clip((lum - .55) / .3, 0, 1) * np.clip((.22 - sat) / .15, 0, 1)
    a = a * (1 - bg[..., None] * .8)
    a = np.clip(a ** 1.35, 0, 1)
    warm = np.array([1.08, .98, .82], np.float32)
    a = np.clip(a * warm, 0, 1)
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = np.clip(1 - (((xx - w * .55) / (w * .75)) ** 2 + ((yy - h * .42) / (h * .8)) ** 2), .15, 1)
    a = a * vig[..., None]
    return Image.fromarray((a * 255).astype("uint8"))


def main():
    (OUT / "jpg").mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (TW, TH), INK)
    ph = photo()
    x0 = TW - ph.width + 40
    fade = np.ones((TH, ph.width), np.float32)
    ramp = np.linspace(0, 1, 220, dtype=np.float32)
    fade[:, :220] *= ramp[None, :]
    img.paste(ph, (x0, 0), Image.fromarray((fade * 255).astype("uint8")))
    d = ImageDraw.Draw(img)

    ef = font(UTIL, 22)
    tracked(d, 56, 48, "42-MINUTE ROTATING EMOM  ·  NO EQUIPMENT", ef, LGOLD, 4)
    f1 = fit(HEAD, "CALISTHENICS", 118, 700)
    d.text((52, 88 - f1.getbbox("H")[1]), "CALISTHENICS", font=f1, fill=BONE)
    f2 = fit(HEAD, "ENDURANCE", 150, 700)
    y = 88 + f1.getbbox("H")[3] - f1.getbbox("H")[1] + 16
    d.text((52, y - f2.getbbox("H")[1]), "ENDURANCE", font=f2, fill=GOLD)
    y += f2.getbbox("H")[3] - f2.getbbox("H")[1] + 30

    rows = [("140", "PUSH-UPS"), ("140", "BURPEES"), ("280", "SQUATS")]
    nf, lf = font(NUMERAL, 76), font(HEAD, 54)
    for num, lab in rows:
        d.text((56, y - nf.getbbox("0")[1]), num, font=nf, fill=GOLD)
        d.text((56 + 190, y + 8 - lf.getbbox("H")[1]), lab, font=lf, fill=BONE)
        y += 80
    y += 2
    d.rectangle((52, y, 560, y + 74), fill=GOLD)
    tf = font(HEAD, 54)
    t = "560 TOTAL REPS"
    d.text((52 + (508 - tf.getlength(t)) / 2, y + 12 - tf.getbbox("H")[1] + 6), t, font=tf, fill=INK)

    logo = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((118, 118), Image.LANCZOS)
    img.paste(logo, (TW - 150, 28), logo)

    img.save(OUT / "yt-thumbnail-emom-endurance.png", optimize=True)
    img.save(OUT / "jpg/yt-thumbnail-emom-endurance.jpg", quality=92)


if __name__ == "__main__":
    main()
