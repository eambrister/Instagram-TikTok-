"""Typography covers for the 42-minute rotating EMOM (no photo): 1080x1920 TikTok/Reel cover and 1080x1350 IG post.

Everything on the 9:16 cover sits inside the centre 1080x1350 band, so the Instagram grid crop keeps it.
Usage: python3 tools/build_emom_typography_covers.py
"""
import numpy as np
from PIL import Image, ImageDraw

from monumental_type import (BONE, CHAR, GOLD, HEAD, INK, LGOLD, NUMERAL, ROOT, STONE, TOKENS, UTIL, font, furniture,
                             tracked, tracked_width)

OUT = ROOT / "outputs/edison-ambrister-emom-endurance-covers"
W = 1080
STEPS = [("MIN 1", "10", "PUSH-UPS"), ("MIN 2", "10", "BURPEES"), ("MIN 3", "20", "SQUATS")]
TOTALS = [("140", "PUSH-UPS"), ("140", "BURPEES"), ("280", "SQUATS")]


def background(h, seed):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:W].astype(np.float32)
    dist = np.sqrt(((xx - W * .5) / W) ** 2 + ((yy - h * .38) / h) ** 2)
    glow = np.clip(1 - dist / .7, 0, 1) ** 2
    char = np.array(CHAR, np.float32)
    a = char + glow[..., None] * (np.array([78, 58, 30], np.float32) - char) * .55
    a += rng.normal(0, 3.5, (h, W))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def ctext(d, y, text, f, fill):
    cap = f.getbbox("H")
    d.text(((W - f.getlength(text)) / 2, y - cap[1]), text, font=f, fill=fill)
    return y + cap[3] - cap[1]


def ctracked(d, y, text, f, fill, t=5):
    tracked(d, (W - tracked_width(text, f, t)) / 2, y, text, f, fill, t)


def block(img, top, logo=True):
    """Draw the cover content starting at y=top; returns the bottom y."""
    d = ImageDraw.Draw(img)
    y = top
    if logo:
        lg = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((120, 120), Image.LANCZOS)
        img.paste(lg, ((W - 120) // 2, top), lg)
        y += 160
    ctracked(d, y, "42-MINUTE ROTATING EMOM", font(UTIL, 26), LGOLD, 6)
    y = ctext(d, y + 58, "CALISTHENICS", font(HEAD, 150), BONE) + 22
    y = ctext(d, y, "ENDURANCE", font(HEAD, 186), GOLD) + 54
    # the rotation
    for i, (m, n, ex) in enumerate(STEPS):
        mf, nf, ef = font(UTIL, 22), font(NUMERAL, 64), font(HEAD, 60)
        x = 290
        tracked(d, x, y + 22, m, mf, STONE, 4)
        d.text((x + 150, y + 2 - nf.getbbox("0")[1]), n, font=nf, fill=GOLD)
        d.text((x + 260, y + 6 - ef.getbbox("H")[1]), ex, font=ef, fill=BONE)
        y += 86
    ctracked(d, y + 4, "REPEAT  ×  14 ROUNDS", font(UTIL, 24), LGOLD, 6)
    y += 70
    d.line((150, y, W - 150, y), fill=GOLD, width=2)
    y += 36
    # totals
    cw = (W - 300) / 3
    for i, (n, ex) in enumerate(TOTALS):
        cx = 150 + cw * (i + .5)
        nf = font(NUMERAL, 84)
        d.text((cx - nf.getlength(n) / 2, y - nf.getbbox("0")[1]), n, font=nf, fill=BONE)
        lf = font(UTIL, 20)
        tracked(d, cx - tracked_width(ex, lf, 4) / 2, y + 96, ex, lf, STONE, 4)
    y += 150
    d.rectangle((150, y, W - 150, y + 96), fill=GOLD)
    tf = font(HEAD, 70)
    t = "560 TOTAL REPS"
    d.text(((W - tf.getlength(t)) / 2, y + 48 - (tf.getbbox("H")[1] + tf.getbbox("H")[3]) / 2), t, font=tf, fill=INK)
    return y + 96


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # measure the block height once
    img = background(1920, 3)
    block(img, 300)  # clear of TikTok's bottom caption overlay, inside the Instagram grid crop (y 285-1635)
    covers = [("cover-1080x1920", img)]
    img = background(1350, 4)
    block(img, 92, logo=False)
    furniture(img, 1, 1)
    covers.append(("post-1080x1350", img))
    for name, img in covers:
        img.save(OUT / f"{name}.png", optimize=True)
        img.save(OUT / f"{name}.jpg", quality=93)
        print(name)


if __name__ == "__main__":
    main()
