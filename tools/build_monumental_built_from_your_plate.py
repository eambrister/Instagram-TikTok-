"""Build "Built from your plate": AI food-sculpture body parts with labelled callouts.

Format reference: a food-anatomy carousel Edison saved (one body part per slide,
whole foods sculpted into its shape, callout labels, one-word title). Imagery here
is newly generated; copy, food pairings and layout are Edison's own.

Usage: python3 tools/build_monumental_built_from_your_plate.py
Source images: outputs/edison-ambrister-built-from-your-plate/source-images/NN.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from monumental_type import (BODY, BONE, GOLD, HEAD, INK, LGOLD, STONE, UTIL, H, W, font, furniture, tracked,
                             tracked_width, wrap)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/edison-ambrister-built-from-your-plate"
SRC = OUT / "source-images"

# Each label: (text, point x, point y, label side). Points are in canvas pixels on the
# final 1080x1350 slide and were placed by eye on the chosen generation.
SLIDES = [
    {"slug": "hook", "image": "01.png", "kind": "hook",
     "eyebrow": "EDISON EATS", "bone": ["YOUR BODY IS BUILT"], "gold": ["FROM YOUR PLATE."],
     "body": "6 body parts and the whole foods that support them."},
    {"slug": "muscles", "image": "02.png", "title": "MUSCLES",
     "line": "Protein gives your body the building blocks to repair and grow muscle after training.",
     "labels": [('Eggs', 286, 414, 150, 230), ('Chicken breast', 471, 686, 330, 860), ('Greek yogurt', 800, 729, 880, 860), ('Lean beef', 771, 200, 440, 130)]},
    {"slug": "heart", "image": "03.png", "title": "HEART",
     "line": "Oily fish, oats, nuts and beans are staples of heart-healthy eating patterns.",
     "labels": [('Walnuts', 329, 329, 120, 250), ('Salmon', 600, 171, 860, 110), ('Oats', 357, 643, 130, 770), ('Lentils & beans', 614, 686, 880, 800)]},
    {"slug": "bones", "image": "04.png", "title": "BONES",
     "line": "Calcium-rich foods help keep bones strong. Sardines with the bones in count.",
     "labels": [('Tofu', 543, 143, 800, 110), ('Greek yogurt', 529, 300, 240, 300), ('Kale', 543, 600, 800, 560), ('Sardines (bones in)', 571, 757, 250, 830)]},
    {"slug": "gut", "image": "05.png", "title": "GUT",
     "line": "Fibre from oats, beans and fruit, plus yogurt with live cultures, feeds your gut.",
     "labels": [('Yogurt', 614, 271, 880, 140), ('Oats', 529, 800, 230, 860), ('Banana', 364, 379, 120, 250), ('Beans & lentils', 800, 643, 900, 760)]},
    {"slug": "brain", "image": "06.png", "title": "BRAIN",
     "line": "Omega-3 fats from fish and walnuts, choline from eggs, colour from berries.",
     "labels": [('Walnuts', 500, 257, 380, 90), ('Eggs', 357, 500, 220, 870), ('Blueberries', 871, 471, 900, 110), ('Salmon', 643, 671, 860, 880)]},
    {"slug": "eyes", "image": "07.png", "title": "EYES",
     "line": "Orange vegetables bring vitamin A. Leafy greens and egg yolks bring lutein.",
     "labels": [('Carrot', 471, 471, 300, 120), ('Egg yolk', 700, 486, 820, 120), ('Spinach', 357, 580, 200, 830), ('Sweet potato', 857, 657, 880, 830)]},
    {"slug": "close", "image": "08.png", "kind": "close",
     "bone": ["BUILD THE PLATE."], "gold": ["THEN REPEAT IT."],
     "body": "Save this for your next shop. Follow for more ways to feed the body you're training."},
]


def photo(name, box=(70, 880), max_w=980):
    """Crop the generation to its subject and enlarge it into the top of the canvas.

    The generations are 16:9 with a small subject on black, so the subject is found by
    brightness, cropped with a margin, scaled to fit the image area and feathered into
    the black canvas.
    """
    im = Image.open(SRC / name).convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    lum = a.mean(axis=2)
    ys, xs = np.where(lum > 28)
    pad = 24
    x0, x1 = max(0, xs.min() - pad), min(im.width, xs.max() + pad)
    y0, y1 = max(0, ys.min() - pad), min(im.height, ys.max() + pad)
    crop = im.crop((x0, y0, x1, y1))
    top, bottom = box
    scale = min(max_w / crop.width, (bottom - top) / crop.height)
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
    # Matte by brightness so the generator's near-black backdrop disappears into the canvas.
    lum = np.asarray(crop, dtype=np.float32).mean(axis=2)
    mask = np.clip((lum - 14) / 26, 0, 1)
    mask = np.asarray(Image.fromarray((mask * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2)),
                      dtype=np.float32) / 255
    canvas = Image.new("RGB", (W, H), INK)
    px = (W - crop.width) // 2
    py = top + (bottom - top - crop.height) // 2
    canvas.paste(crop, (px, py), Image.fromarray((mask * 255).astype("uint8")))
    return canvas


def callout(d, text, px, py, lx, ly):
    """Gold dot on the food at (px, py), leader line to (lx, ly), label in a dark pill beside it."""
    f = font(UTIL, 26)
    tw = tracked_width(text, f, 1)
    d.line((px, py, lx, ly), fill=LGOLD, width=3)
    d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=LGOLD, outline=INK, width=2)
    tx = lx - tw - 16 if lx < px else lx + 16
    tx = max(40, min(W - 40 - tw, tx))
    bbox = f.getbbox(text)
    d.rounded_rectangle((tx - 14, ly - 25, tx + tw + 14, ly + 25), radius=25, fill=(8, 9, 9), outline=GOLD, width=1)
    tracked(d, tx, ly - (bbox[1] + bbox[3]) / 2, text, f, BONE, 1)


def organ_slide(s):
    img = photo(s["image"])
    d = ImageDraw.Draw(img)
    for label in s["labels"]:
        callout(d, *label)
    f = font(HEAD, 160)
    cap = f.getbbox("H")
    title_top = 905
    d.text(((W - f.getlength(s["title"])) / 2, title_top - cap[1]), s["title"], font=f, fill=GOLD)
    y = title_top + (cap[3] - cap[1]) + 30
    bf = font(BODY, 30)
    for line in wrap(bf, s["line"], 860):
        d.text(((W - bf.getlength(line)) / 2, y), line, font=bf, fill=BONE)
        y += 42
    return img


def text_slide(s):
    img = photo(s["image"])
    d = ImageDraw.Draw(img)
    y = 830
    if s.get("eyebrow"):
        ef = font(UTIL, 22)
        tracked(d, (W - tracked_width(s["eyebrow"], ef, 4)) / 2, y, s["eyebrow"], ef, GOLD, 4)
        y += 52
    for lines, colour, size in ((s["bone"], BONE, 96), (s["gold"], GOLD, 120)):
        f = font(HEAD, size)
        for line in lines:
            while f.getlength(line) > 960:
                f = font(HEAD, f.size - 4)
            cap = f.getbbox("H")
            d.text(((W - f.getlength(line)) / 2, y - cap[1]), line, font=f, fill=colour)
            y += (cap[3] - cap[1]) + 18
    y += 14
    bf = font(BODY, 30)
    for line in wrap(bf, s["body"], 860):
        d.text(((W - bf.getlength(line)) / 2, y), line, font=bf, fill=STONE if s["kind"] == "close" else BONE)
        y += 42
    return img


def main():
    (OUT / "jpg").mkdir(parents=True, exist_ok=True)
    pngs = []
    for i, s in enumerate(SLIDES, 1):
        img = text_slide(s) if s.get("kind") in ("hook", "close") else organ_slide(s)
        furniture(img, i, len(SLIDES))
        name = f"{i:02d}-{s['slug']}"
        img.save(OUT / f"{name}.png", optimize=True)
        img.save(OUT / "jpg" / f"{name}.jpg", quality=93)
        pngs.append(OUT / f"{name}.png")
        print(name)
    sheet = Image.new("RGB", (4 * 380 + 20, 2 * 470 + 20), INK)
    for k, p in enumerate(pngs):
        sheet.paste(Image.open(p).resize((360, 450), Image.LANCZOS), (20 + (k % 4) * 380, 20 + (k // 4) * 470))
    sheet.save(OUT / "preview.jpg", quality=90)


if __name__ == "__main__":
    main()
