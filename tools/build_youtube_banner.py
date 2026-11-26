"""YouTube channel banner (2560x1440): Calisthenics, self-mastery & discipline. Monumental kit + CTD logo.

Text and logo sit inside the 1546x423 safe area (visible on every device). Edison's photo sits on the
right edge, visible on desktop and TV.

Usage: python3 tools/build_youtube_banner.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from monumental_type import BONE, CHAR, GOLD, HEAD, LGOLD, ROOT, TOKENS, UTIL, font, tracked

OUT = ROOT / "outputs/edison-ambrister-youtube-banner"
BW, BH = 2560, 1440
SAFE = (507, 508, 2053, 931)
PHOTO = False  # Edison asked for no photo on the banner


def background():
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    dist = np.sqrt(((xx - BW * .5) / BW) ** 2 + ((yy - BH * .5) / (BH * 1.6)) ** 2)
    glow = np.clip(1 - dist / .55, 0, 1) ** 2
    char = np.array(CHAR, np.float32)
    warm = np.array([70, 52, 28], np.float32)
    a = char + glow[..., None] * (warm - char) * .6
    a += rng.normal(0, 3.5, (BH, BW))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def photo():
    im = ImageOps.exif_transpose(Image.open(ROOT / "outputs/edison-ambrister-yt-emom-endurance/source-images/edison-home.png")).convert("RGB")
    im = im.crop((0, 226, im.width, 2305))
    s = .65
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(.75)
    a = np.asarray(im, np.float32) / 255
    lum, sat = a.mean(axis=2), a.max(axis=2) - a.min(axis=2)
    bg = np.clip((lum - .38) / .25, 0, 1) * np.clip((.25 - sat) / .15, 0, 1)
    a = np.clip((a * (1 - bg[..., None] * .92)) ** 1.35 * np.array([1.08, .98, .82], np.float32), 0, 1)
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = np.clip(1 - (((xx - w * .55) / (w * .6)) ** 2 + ((yy - h * .32) / (h * .45)) ** 2), .05, 1) ** 1.3
    return Image.fromarray((a * vig[..., None] * 255).astype("uint8"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    img = background()
    if PHOTO:
        ph = photo()
        x0, y0 = BW - ph.width + 40, 575 - round((600 - 226) * .65)
        m = np.ones((ph.height, ph.width), np.float32)
        m[:, :260] *= np.linspace(0, 1, 260, dtype=np.float32)[None, :]
        m[:220] *= np.linspace(0, 1, 220, dtype=np.float32)[:, None]
        m[-260:] *= np.linspace(1, 0, 260, dtype=np.float32)[:, None]
        img.paste(ph, (x0, y0), Image.fromarray((m * 255).astype("uint8")))
    d = ImageDraw.Draw(img)

    sx0, sy0, sx1, sy1 = SAFE
    f1 = font(HEAD, 176)
    f2 = font(HEAD, 98)
    t2 = "SELF-MASTERY & DISCIPLINE"
    tw = max(f1.getlength("CALISTHENICS"), f2.getlength(t2))
    lw, gap = 330, 110
    x = (BW - (lw + gap + tw)) / 2
    logo = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((lw, lw), Image.LANCZOS)
    img.paste(logo, (round(x), sy0 + (sy1 - sy0 - lw) // 2), logo)
    d.line((x + lw + gap / 2, sy0 + 70, x + lw + gap / 2, sy1 - 70), fill=GOLD, width=2)
    tx = x + lw + gap
    tracked(d, tx, sy0 + 86, "EDISON AMBRISTER", font(UTIL, 30), LGOLD, 8)
    y = sy0 + 144
    d.text((tx, y - f1.getbbox("H")[1]), "CALISTHENICS", font=f1, fill=BONE)
    y += f1.getbbox("H")[3] - f1.getbbox("H")[1] + 26
    d.text((tx, y - f2.getbbox("H")[1]), t2, font=f2, fill=GOLD)

    img.save(OUT / "youtube-banner-2560x1440.png", optimize=True)
    img.convert("RGB").save(OUT / "youtube-banner-2560x1440.jpg", quality=92)
    # preview with the safe area marked (not for upload)
    pv = img.copy()
    pd = ImageDraw.Draw(pv)
    pd.rectangle(SAFE, outline=(200, 60, 60), width=4)
    pd.rectangle((0, 508, BW - 1, 931), outline=(80, 140, 220), width=4)
    pv.resize((1280, 720), Image.LANCZOS).save(OUT / "preview-safe-areas.jpg", quality=88)


if __name__ == "__main__":
    main()
