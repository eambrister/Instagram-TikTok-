"""Build three food-list posts in the Monumental kit from generated food rows.

- outputs/edison-ambrister-best-food-sources: B12, heme iron, zinc, omega-3 (unranked).
- outputs/edison-ambrister-protein-tier-list: single-slide tier list (Edison's opinion).
- outputs/edison-ambrister-egg-throne: single meme post.

Each generated row is a line of foods on black; items are cut out by finding the
gaps between them so every food can be placed in its own labelled cell.

Usage: python3 tools/build_monumental_food_lists.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from monumental_type import (BODY, BONE, GOLD, HEAD, INK, STONE, UTIL, H, W, font, frame, furniture, surface,
                             tracked, tracked_width, wrap)

ROOT = Path(__file__).resolve().parents[1]
CARD = (24, 24, 22)
RULE = (70, 62, 50)


# ---------------------------------------------------------------- cut-outs

def items(path, n):
    """Split a row of n foods on black into n RGBA cut-outs, left to right."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    mask = a.mean(axis=2) > 28
    occupied = mask.sum(axis=0) > 3
    runs, start = [], None
    for x, on in enumerate(occupied):
        if on and start is None:
            start = x
        if not on and start is not None:
            runs.append([start, x])
            start = None
    if start is not None:
        runs.append([start, len(occupied)])
    runs = [r for r in runs if r[1] - r[0] > 12]
    while len(runs) > n:
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        i = int(np.argmin(gaps))
        runs[i:i + 2] = [[runs[i][0], runs[i + 1][1]]]
    if len(runs) < n:
        x0, x1 = runs[0][0], runs[-1][1]
        step = (x1 - x0) / n
        runs = [[round(x0 + k * step), round(x0 + (k + 1) * step)] for k in range(n)]
    out = []
    for x0, x1 in runs:
        ys = np.where(mask[:, x0:x1].any(axis=1))[0]
        box = (max(0, x0 - 6), max(0, ys.min() - 6), min(im.width, x1 + 6), min(im.height, ys.max() + 6))
        crop = im.crop(box)
        lum = np.asarray(crop, dtype=np.float32).mean(axis=2)
        alpha = Image.fromarray((np.clip((lum - 14) / 26, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.5))
        crop.putalpha(alpha)
        out.append(crop)
    return out


def place(img, item, cx, cy, max_w, max_h):
    s = min(max_w / item.width, max_h / item.height)
    it = item.resize((max(1, round(item.width * s)), max(1, round(item.height * s))), Image.LANCZOS)
    img.paste(it, (round(cx - it.width / 2), round(cy - it.height / 2)), it)


def centred(d, y, text, f, fill):
    cap = f.getbbox("H")
    d.text(((W - f.getlength(text)) / 2, y - cap[1]), text, font=f, fill=fill)
    return y + cap[3] - cap[1]


def fit(path, text, size, max_w):
    f = font(path, size)
    while f.getlength(text) > max_w:
        f = font(path, f.size - 4)
    return f


# ---------------------------------------------------------------- best food sources

SOURCES = [
    ("b12", "VITAMIN B12", "Found naturally only in animal foods.",
     ["Clams", "Beef liver", "Salmon", "Sardines", "Beef", "Eggs"],
     "Plant-based? Use fortified foods or a supplement."),
    ("iron", "HEME IRON", "The form your body absorbs best.",
     ["Beef liver", "Oysters", "Beef", "Sardines", "Mussels", "Lamb"],
     "Eating plant iron? Pair it with vitamin C to absorb more."),
    ("zinc", "ZINC", "For immune function and recovery.",
     ["Oysters", "Beef", "Crab", "Lamb", "Pumpkin seeds", "Cheese"],
     "Oysters carry more zinc per serving than any other food."),
    ("omega", "OMEGA-3", "EPA and DHA come mainly from oily fish.",
     ["Salmon", "Mackerel", "Sardines", "Herring", "Anchovies", "Trout"],
     "Aim for two servings of oily fish a week."),
]


def source_slide(seed, key, title, sub, labels, note):
    src = ROOT / "outputs/edison-ambrister-best-food-sources/source-images" / f"{key}.png"
    img = surface(seed, light=(0.85, 0.05))
    d = ImageDraw.Draw(img)
    uf = font(UTIL, 24)
    tracked(d, (W - tracked_width("THE BEST FOOD SOURCES OF", uf, 5)) / 2, 74, "THE BEST FOOD SOURCES OF", uf, STONE, 5)
    y = centred(d, 124, title, fit(HEAD, title, 150, 940), GOLD) + 30
    sf = font(BODY, 32)
    d.text(((W - sf.getlength(sub)) / 2, y), sub, font=sf, fill=BONE)
    y += 80
    cuts = items(src, 6)
    cell_w, cell_h = 300, 330
    lf = font(UTIL, 26)
    for i, (cut, lab) in enumerate(zip(cuts, labels)):
        col, row = i % 3, i // 3
        x0 = 80 + col * (cell_w + 10)
        y0 = y + row * (cell_h + 20)
        d.rounded_rectangle((x0, y0, x0 + cell_w, y0 + cell_h), radius=18, fill=CARD, outline=RULE, width=1)
        place(img, cut, x0 + cell_w / 2, y0 + 130, cell_w - 40, 210)
        t = lab.upper()
        tracked(d, x0 + (cell_w - tracked_width(t, lf, 2)) / 2, y0 + cell_h - 62, t, lf, BONE, 2)
    y += 2 * cell_h + 20 + 36
    nf = font(BODY, 30)
    for ln in wrap(nf, note, 900):
        d.text(((W - nf.getlength(ln)) / 2, y), ln, font=nf, fill=STONE)
        y += 42
    return img


def text_slide(seed, eyebrow, bone, gold, body):
    img = surface(seed, light=(0.9, 0.0))
    frame(img)
    d = ImageDraw.Draw(img)
    y = 340
    ef = font(UTIL, 22)
    tracked(d, (W - tracked_width(eyebrow, ef, 4)) / 2, y, eyebrow, ef, GOLD, 4)
    y += 70
    for lines, colour in ((bone, BONE), (gold, GOLD)):
        for line in lines:
            y = centred(d, y, line, fit(HEAD, line, 150, 920), colour) + 24
    y += 30
    d.line((W / 2 - 48, y, W / 2 + 48, y), fill=GOLD, width=2)
    y += 44
    bf = font(BODY, 34)
    for ln in wrap(bf, body, 860):
        d.text(((W - bf.getlength(ln)) / 2, y), ln, font=bf, fill=BONE)
        y += 48
    return img


# ---------------------------------------------------------------- tier list

TIERS = [
    ("S", "BEST OF THE BEST", "s", ["Chicken breast", "Eggs", "Lean beef", "Greek yogurt", "Salmon"]),
    ("A", "GREAT CHOICES", "a", ["Tuna", "Turkey breast", "Shrimp", "Cottage cheese", "White fish"]),
    ("B", "SOLID OPTIONS", "b", ["Lentils", "Black beans", "Tofu", "Edamame", "Lean pork"]),
    ("C", "SOMETIMES", "c", ["Deli meat", "Protein bars", "Fried chicken", "Sausage", "Cheese"]),
]


def tier_slide():
    img = surface(11, light=(0.5, 0.0))
    d = ImageDraw.Draw(img)
    y = centred(d, 56, "PROTEIN FOOD", fit(HEAD, "PROTEIN FOOD", 92, 900), BONE) + 14
    y = centred(d, y, "TIER LIST", fit(HEAD, "TIER LIST", 92, 900), GOLD) + 20
    sf = font(BODY, 26)
    s = "Ranked for protein per calorie and how easy they are to eat every week."
    d.text(((W - sf.getlength(s)) / 2, y), s, font=sf, fill=STONE)
    y += 50
    row_h, label_w = 196, 150
    for k, (letter, desc, key, labels) in enumerate(TIERS):
        ry = y + k * (row_h + 12)
        d.rounded_rectangle((40, ry, 1040, ry + row_h), radius=16, fill=CARD, outline=RULE, width=1)
        d.rounded_rectangle((40, ry, 40 + label_w, ry + row_h), radius=16, fill=(48, 40, 26) if k == 0 else (34, 32, 28))
        lf = font(HEAD, 86)
        cap = lf.getbbox(letter)
        d.text((40 + (label_w - lf.getlength(letter)) / 2, ry + 22 - cap[1]), letter, font=lf, fill=GOLD)
        df = font(UTIL, 15)
        for j, word in enumerate(desc.split(" ", 1) if len(desc) > 10 else [desc]):
            tracked(d, 40 + (label_w - tracked_width(word, df, 2)) / 2, ry + 122 + j * 22, word, df, BONE, 2)
        cuts = items(ROOT / "outputs/edison-ambrister-protein-tier-list/source-images" / f"{key}.png", 5)
        cw = (1040 - 40 - label_w - 20) / 5
        nf = font(UTIL, 17)
        for i, (cut, lab) in enumerate(zip(cuts, labels)):
            cx = 40 + label_w + 10 + cw * (i + 0.5)
            place(img, cut, cx, ry + 78, cw - 18, 118)
            t = lab.upper()
            while tracked_width(t, nf, 1) > cw - 10:
                nf = font(UTIL, nf.size - 1)
            tracked(d, cx - tracked_width(t, nf, 1) / 2, ry + row_h - 38, t, nf, BONE, 1)
            nf = font(UTIL, 17)
    return img


# ---------------------------------------------------------------- throne meme

def throne_slide():
    im = Image.open(ROOT / "outputs/edison-ambrister-egg-throne/source-images/throne.png").convert("RGB")
    s = H / im.height
    im = im.resize((round(im.width * s), H), Image.LANCZOS)
    left = (im.width - W) // 2
    img = im.crop((left, 0, left + W, H))
    d = ImageDraw.Draw(img)
    return img, d, s, left


def label(d, text, cx, cy, size=44):
    f = font(HEAD, size)
    w = f.getlength(text)
    b = f.getbbox(text)
    x, y = cx - w / 2, cy - (b[1] + b[3]) / 2
    for dx in (-3, 0, 3):
        for dy in (-3, 0, 3):
            d.text((x + dx, y + dy), text, font=f, fill=INK)
    d.text((x, y), text, font=f, fill=BONE)


# Positions in source-image pixels (1280x720): the egg and the five knights.
THRONE_LABELS = [("EGGS", 640, 170, 84)]
KNIGHTS = [("CHICKEN", 385), ("BEEF", 500), ("SALMON", 635), ("TUNA", 770), ("TURKEY", 885)]
KNIGHT_Y = 462
FLOOR = [("RICE", 410, 520), ("OATS", 500, 545), ("BROCCOLI", 780, 520), ("BERRIES", 870, 545)]


def egg_throne():
    img, d, s, left = throne_slide()
    tx = lambda x: x * s - left
    for text, x, y, size in THRONE_LABELS:
        label(d, text, tx(x), y * s, size)
    for text, x in KNIGHTS:
        label(d, text, tx(x), KNIGHT_Y * s, 34)
    for text, x, y in FLOOR:
        if 60 < tx(x) < W - 60:
            label(d, text, tx(x), y * s, 28)
    # Top banner.
    band = Image.new("L", (W, H), 0)
    ImageDraw.Draw(band).rectangle((0, 1080, W, H), fill=225)
    band = band.filter(ImageFilter.GaussianBlur(40))
    img.paste(Image.new("RGB", (W, H), INK), (0, 0), band)
    d = ImageDraw.Draw(img)
    centred(d, 1105, "THE PROTEIN HIERARCHY", fit(HEAD, "THE PROTEIN HIERARCHY", 92, 960), GOLD)
    return img


# ---------------------------------------------------------------- output

def save(folder, slides):
    out = ROOT / "outputs" / folder
    (out / "jpg").mkdir(parents=True, exist_ok=True)
    pngs = []
    for i, (name, img) in enumerate(slides, 1):
        furniture(img, i, len(slides))
        img.save(out / f"{name}.png", optimize=True)
        img.save(out / "jpg" / f"{name}.jpg", quality=93)
        pngs.append(out / f"{name}.png")
    cols = min(3, len(pngs))
    rows = (len(pngs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 380 + 20, rows * 470 + 20), INK)
    for k, p in enumerate(pngs):
        sheet.paste(Image.open(p).resize((360, 450), Image.LANCZOS), (20 + (k % cols) * 380, 20 + (k // cols) * 470))
    sheet.save(out / "preview.jpg", quality=90)
    print(folder, len(pngs))


def main():
    slides = [("01-hook", text_slide(1, "EDISON EATS", ["EAT THESE"], ["ON PURPOSE."],
                                     "The best food sources of four nutrients most people under-eat. Not ranked. Just the best."))]
    for i, (key, title, sub, labels, note) in enumerate(SOURCES, 2):
        slides.append((f"{i:02d}-{key}", source_slide(i, key, title, sub, labels, note)))
    slides.append(("06-close", text_slide(6, "SAVE THIS", ["TAKE IT TO THE"], ["GROCERY STORE."],
                                          "Pick two from each list this week. Follow for more.")))
    save("edison-ambrister-best-food-sources", slides)
    save("edison-ambrister-protein-tier-list", [("01-tier-list", tier_slide())])
    save("edison-ambrister-egg-throne", [("01-egg-throne", egg_throne())])


if __name__ == "__main__":
    main()
