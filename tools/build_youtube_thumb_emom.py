"""YouTube thumbnail (1280x720): 42-round calisthenics endurance EMOM, Monumental kit + CTD logo.

Usage: python3 tools/build_youtube_thumb_emom.py
Source photo: outputs/edison-ambrister-yt-emom-endurance/source-images/edison-mirror.jpg (Edison's own photo)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from monumental_type import BONE, GOLD, HEAD, INK, LGOLD, NUMERAL, ROOT, STONE, TOKENS, UTIL, font, tracked, tracked_width

OUT = ROOT / "outputs/edison-ambrister-yt-emom-endurance"
TW, TH = 1280, 720


def fit(path, text, size, width):
    f = font(path, size)
    while f.getlength(text) > width:
        f = font(path, f.size - 2)
    return f


def photo():
    im = ImageOps.exif_transpose(Image.open(OUT / "source-images/edison-mirror.jpg")).convert("RGB")
    im = im.crop((0, 430, im.width, 430 + round(im.width / 0.86)))
    im = im.resize((round(TH * im.width / im.height), TH), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # the wall is mustard yellow: red and green close together, blue well below; skin has red clearly above green
    yellow = np.clip(((r + g) / 2 - b - .12) / .1, 0, 1) * np.clip((.075 - np.abs(r - g)) / .045, 0, 1)
    yellow = np.asarray(Image.fromarray((yellow * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    a = a * (1 - yellow[..., None] * .85)
    a = np.clip(a ** 1.08 * np.array([1.04, 1.0, .94], np.float32), 0, 1)
    h, w = r.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = np.clip(1.1 - (((xx - w * .45) / (w * .62)) ** 2 + ((yy - h * .45) / (h * .75)) ** 2), .08, 1)
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

    logo = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((100, 100), Image.LANCZOS)
    img.paste(logo, (TW - 116, 18), logo)

    img.save(OUT / "yt-thumbnail-emom-endurance.png", optimize=True)
    img.save(OUT / "jpg/yt-thumbnail-emom-endurance.jpg", quality=92)


if __name__ == "__main__":
    main()
