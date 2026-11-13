"""Build the "lean vs bulk" meme post: original AI scene, bone labels, Monumental furniture.

Format reference: a two-figure "lean vs bulk" meme Edison saved. The scene here is newly
generated (no film still, no licensed character).

Usage: python3 tools/build_monumental_lean_vs_bulk.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from monumental_type import BONE, GOLD, HEAD, INK, H, W, font, furniture

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/edison-ambrister-lean-vs-bulk"

# (text, centre x, centre y) on the 1080x1350 canvas, placed on the chosen image.
LEFT = [("STAYING LEAN", 230, 400), ("6 PACK", 230, 560), ("DEFINITION", 230, 720), ("SMALL", 230, 880)]
RIGHT = [("BULK", 840, 330), ("STRONG", 840, 500), ("LOOK HUGE", 840, 670), ("NO 6 PACK", 840, 840)]


def label(d, text, cx, cy, size=58):
    f = font(HEAD, size)
    w = f.getlength(text)
    b = f.getbbox(text)
    x, y = cx - w / 2, cy - (b[1] + b[3]) / 2
    for dx in range(-4, 5, 2):
        for dy in range(-4, 5, 2):
            d.text((x + dx, y + dy), text, font=f, fill=INK)
    d.text((x, y), text, font=f, fill=BONE)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "jpg").mkdir(exist_ok=True)
    im = Image.open(OUT / "source-images/scene.png").convert("RGB")
    im = im.crop((160, 0, 1080, im.height))
    s = W / im.width
    im = im.resize((W, round(im.height * s)), Image.LANCZOS)
    top = 215
    img = Image.new("RGB", (W, H), INK)
    fade = Image.new("L", im.size, 255)
    fd = ImageDraw.Draw(fade)
    for i in range(90):
        a = round(255 * i / 90)
        fd.line((0, i, W, i), fill=a)
        fd.line((0, im.height - 1 - i, W, im.height - 1 - i), fill=a)
    img.paste(im, (0, top), fade)
    d = ImageDraw.Draw(img)
    t = "LEAN VS BULK"
    f = font(HEAD, 120)
    b = f.getbbox(t)
    d.text(((W - f.getlength(t)) / 2, 70 - b[1]), t, font=f, fill=BONE)
    for t, x, y in LEFT + RIGHT:
        label(d, t, x, y)
    q = "WHICH ONE ARE YOU CHASING?"
    f = font(HEAD, 78)
    while f.getlength(q) > 960:
        f = font(HEAD, f.size - 2)
    b = f.getbbox(q)
    d.text(((W - f.getlength(q)) / 2, 1140 - b[1]), q, font=f, fill=GOLD)
    furniture(img, 1, 1)
    img.save(OUT / "01-lean-vs-bulk.png", optimize=True)
    img.save(OUT / "jpg/01-lean-vs-bulk.jpg", quality=93)


if __name__ == "__main__":
    main()
