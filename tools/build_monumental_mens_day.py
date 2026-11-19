"""International Men's Day poster (19 Nov): gritty single image in the Monumental kit.

Original AI scene (ElevenLabs), a Black man who is not Edison. Cutthroat Discipline logo via furniture().
Usage: python3 tools/build_monumental_mens_day.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

from monumental_type import BODY, BONE, GOLD, HEAD, INK, LGOLD, UTIL, H, W, font, furniture, tracked, tracked_width, wrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/edison-ambrister-mens-day"


def fit(path, text, size, width):
    f = font(path, size)
    while f.getlength(text) > width:
        f = font(path, f.size - 2)
    return f


def ctext(d, y, text, f, fill):
    cap = f.getbbox("H")
    d.text(((W - f.getlength(text)) / 2, y - cap[1]), text, font=f, fill=fill)
    return y + cap[3] - cap[1]


def main():
    (OUT / "jpg").mkdir(parents=True, exist_ok=True)
    src = Image.open(OUT / "source-images/scene.png").convert("RGB")
    cx, cw = 610, 760  # subject centre in the chosen variation
    x0 = min(max(0, cx - cw // 2), src.width - cw)
    src = src.crop((x0, 0, x0 + cw, src.height))
    src = ImageEnhance.Contrast(ImageEnhance.Color(src).enhance(0.8)).enhance(1.08)
    src = src.resize((W, round(src.height * W / cw)), Image.LANCZOS)

    img = Image.new("RGB", (W, H), INK)
    img.paste(src, (0, 0))
    # darken top for the eyebrow and fade the bottom into ink for the type
    shade = np.zeros((H, W), dtype=np.float32)
    y = np.arange(H, dtype=np.float32)[:, None]
    shade += np.clip((180 - y) / 180, 0, 1) * 0.55
    shade += np.clip((y - 560) / (src.height - 560), 0, 1) ** 1.3
    shade = np.clip(shade, 0, 1)
    a = np.asarray(img, dtype=np.float32)
    ink = np.array(INK, dtype=np.float32)
    a = a * (1 - shade[..., None]) + ink * shade[..., None]
    rng = np.random.default_rng(19)
    a += rng.normal(0, 5, (H, W))[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))

    d = ImageDraw.Draw(img)
    ef = font(UTIL, 22)
    eb = "19 NOVEMBER  ·  INTERNATIONAL MEN'S DAY"
    tracked(d, (W - tracked_width(eb, ef, 5)) / 2, 76, eb, ef, LGOLD, 5)

    y = ctext(d, 690, "HAPPY MEN'S DAY.", fit(HEAD, "HAPPY MEN'S DAY.", 112, 920), BONE) + 22
    y = ctext(d, y, "NOW WAKE UP.", fit(HEAD, "NOW WAKE UP.", 150, 940), GOLD) + 34
    d.line((W / 2 - 60, y, W / 2 + 60, y), fill=GOLD, width=2)
    y += 28
    bf = font(BODY, 30)
    for line in ("There's nothing to celebrate if you're still", "undisciplined, still weak, still soft."):
        d.text(((W - bf.getlength(line)) / 2, y), line, font=bf, fill=BONE)
        y += 42
    y += 16
    tf = font(UTIL, 22)
    tag = "MASTER YOUR MIND  ·  MASTER YOUR BODY  ·  RULE YOURSELF"
    while tracked_width(tag, tf, 4) > 940:
        tf = font(UTIL, tf.size - 1)
    tracked(d, (W - tracked_width(tag, tf, 4)) / 2, y, tag, tf, GOLD, 4)

    furniture(img, 1, 1)
    img.save(OUT / "01-mens-day.png", optimize=True)
    img.save(OUT / "jpg/01-mens-day.jpg", quality=93)


if __name__ == "__main__":
    main()
