"""Build "Craving swaps": craving row on top, a better swap below, in the Monumental kit.

Format reference: a "if you crave X, you need Y" carousel Edison saved. That framing
implies cravings signal deficiencies, which the evidence doesn't support, so this
version is honest: "Craving X? Swap it for Y" with a practical reason.

Usage: python3 tools/build_monumental_craving_swaps.py
Source images: outputs/edison-ambrister-craving-swaps/source-images/<slug>-crave.png / -swap.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from monumental_type import (BODY, BONE, GOLD, HEAD, INK, STONE, UTIL, H, W, font, frame, furniture, surface,
                             tracked, tracked_width, wrap)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/edison-ambrister-craving-swaps"
SRC = OUT / "source-images"

SWAPS = [
    {"slug": "sugar", "crave": "SUGAR", "swap": "PROTEIN + FRUIT",
     "note": "Greek yogurt and berries, eggs, apple with peanut butter. Sweet enough, and it keeps you full."},
    {"slug": "chocolate", "crave": "CHOCOLATE", "swap": "PORTION IT",
     "note": "Two squares of dark chocolate, almonds, strawberries, cocoa yogurt. Have it. Just plan the amount."},
    {"slug": "salty", "crave": "SALTY SNACKS", "swap": "CRUNCH, NOT FRYER",
     "note": "Air-popped popcorn, salted edamame, cucumber with sea salt, olives. Same crunch, far fewer calories."},
    {"slug": "carbs", "crave": "CARBS", "swap": "PORTIONED CARBS",
     "note": "Rice, potatoes, oats, pasta, measured. Carbs aren't the enemy. Oversized portions and extras are."},
]


def strip(name, top, height):
    """Matte the generated row onto the canvas area (top, top+height), centred."""
    im = Image.open(SRC / name).convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    ys, xs = np.where(a.mean(axis=2) > 28)
    im = im.crop((max(0, xs.min() - 16), max(0, ys.min() - 16), min(im.width, xs.max() + 16), min(im.height, ys.max() + 16)))
    scale = min(1000 / im.width, height / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    lum = np.asarray(im, dtype=np.float32).mean(axis=2)
    mask = Image.fromarray((np.clip((lum - 14) / 26, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2))
    return im, mask, ((W - im.width) // 2, top + (height - im.height) // 2)


def centre(d, y, text, f, fill):
    cap = f.getbbox("H")
    d.text(((W - f.getlength(text)) / 2, y - cap[1]), text, font=f, fill=fill)
    return y + cap[3] - cap[1]


def label_line(d, y, small, big, big_colour):
    sf, bf = font(UTIL, 26), font(HEAD, 96)
    while bf.getlength(big) > 940:
        bf = font(HEAD, bf.size - 4)
    tracked(d, (W - tracked_width(small, sf, 5)) / 2, y, small, sf, STONE, 5)
    return centre(d, y + 44, big, bf, big_colour)


def swap_slide(s, seed):
    img = surface(seed, light=(0.85, 0.05))
    d = ImageDraw.Draw(img)
    y = label_line(d, 70, "IF YOU'RE CRAVING", s["crave"], BONE)
    im, mask, pos = strip(f"{s['slug']}-crave.png", y + 20, 330)
    img.paste(im, pos, mask)
    y = pos[1] + im.height + 24
    d.line((W / 2 - 60, y, W / 2 + 60, y), fill=GOLD, width=2)
    y = label_line(d, y + 26, "SWAP IT FOR", s["swap"], GOLD)
    im, mask, pos = strip(f"{s['slug']}-swap.png", y + 20, 330)
    img.paste(im, pos, mask)
    y = pos[1] + im.height + 22
    nf = font(BODY, 30)
    for line in wrap(nf, s["note"], 900):
        d.text(((W - nf.getlength(line)) / 2, y), line, font=nf, fill=BONE)
        y += 42
    return img


def text_slide(seed, eyebrow, bone, gold, body):
    img = surface(seed, light=(0.9, 0.0))
    frame(img)
    d = ImageDraw.Draw(img)
    y = 330
    ef = font(UTIL, 22)
    tracked(d, (W - tracked_width(eyebrow, ef, 4)) / 2, y, eyebrow, ef, GOLD, 4)
    y += 70
    for lines, colour in ((bone, BONE), (gold, GOLD)):
        f = font(HEAD, 150)
        for line in lines:
            while f.getlength(line) > 920:
                f = font(HEAD, f.size - 4)
            y = centre(d, y, line, f, colour) + 24
    y += 30
    d.line((W / 2 - 48, y, W / 2 + 48, y), fill=GOLD, width=2)
    y += 44
    bf = font(BODY, 34)
    for line in wrap(bf, body, 860):
        d.text(((W - bf.getlength(line)) / 2, y), line, font=bf, fill=BONE)
        y += 48
    return img


def main():
    (OUT / "jpg").mkdir(parents=True, exist_ok=True)
    slides = [("01-hook", text_slide(1, "EDISON EATS", ["CRAVINGS", "AREN'T"], ["THE ENEMY."],
                                     "Here's what to reach for instead, so one craving doesn't become the whole day."))]
    for i, s in enumerate(SWAPS, 2):
        slides.append((f"{i:02d}-{s['slug']}", swap_slide(s, i)))
    slides.append(("06-close", text_slide(6, "THE RULE", ["DON'T BAN IT."], ["PLAN IT."],
                                          "Eat protein first, then decide if you still want it. Save this for your next craving.")))
    pngs = []
    for i, (name, img) in enumerate(slides, 1):
        furniture(img, i, len(slides))
        img.save(OUT / f"{name}.png", optimize=True)
        img.save(OUT / "jpg" / f"{name}.jpg", quality=93)
        pngs.append(OUT / f"{name}.png")
        print(name)
    sheet = Image.new("RGB", (3 * 380 + 20, 2 * 470 + 20), INK)
    for k, p in enumerate(pngs):
        sheet.paste(Image.open(p).resize((360, 450), Image.LANCZOS), (20 + (k % 3) * 380, 20 + (k // 3) * 470))
    sheet.save(OUT / "preview.jpg", quality=90)


if __name__ == "__main__":
    main()
