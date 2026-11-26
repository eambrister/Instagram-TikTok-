"""YouTube thumbnail (1280x720): 42-round calisthenics endurance EMOM, Monumental kit + CTD logo.

Usage: python3 tools/build_youtube_thumb_emom.py
Source photo: outputs/edison-ambrister-yt-emom-endurance/source-images/edison-flex.jpg (Edison's own photo)
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
    im = ImageOps.exif_transpose(Image.open(OUT / "source-images/edison-flex.jpg")).convert("RGB")
    im = im.crop((0, 20, im.width, 1640))
    im = im.resize((round(im.width * TH / im.height), TH), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    lum, sat = a.mean(axis=2), a.max(axis=2) - a.min(axis=2)
    # grey wall and the painting: bright and/or low saturation, unlike his skin
    wall = np.clip((lum - .42) / .2, 0, 1) * np.clip((.2 - sat) / .12, 0, 1)
    wall = np.asarray(Image.fromarray((wall * 255).astype("uint8")).filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    a = a * (1 - wall[..., None] * .88)
    a = np.clip(a ** 1.06 * np.array([1.04, 1.0, .94], np.float32), 0, 1)
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = np.clip(1.15 - (((xx - w * .48) / (w * .6)) ** 2 + ((yy - h * .5) / (h * .85)) ** 2), .06, 1)
    a = a * vig[..., None]
    return Image.fromarray((a * 255).astype("uint8"))


def main():
    (OUT / "jpg").mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (TW, TH), INK)
    ph = photo()
    x0 = TW - ph.width
    fade = np.ones((TH, ph.width), np.float32)
    ramp = np.linspace(0, 1, 120, dtype=np.float32)
    fade[:, :120] *= ramp[None, :]
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
