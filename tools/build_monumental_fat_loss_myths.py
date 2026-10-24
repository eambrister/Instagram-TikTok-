"""Build the Monumental-kit carousel "Fat-loss myths that keep you stuck" (typographic edition).

No photographs: the Monumental look comes from the type hierarchy, a charcoal
surface with a stone-like texture, one warm light source, oversized serif
numerals and fine gold rules.

Usage: python3 tools/build_monumental_fat_loss_myths.py
"""
import json
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/edison-ambrister-fat-loss-myths"
TOKENS = json.loads((ROOT / "brand/monumental/tokens.json").read_text())
C = TOKENS["colors"]
W, H = 1080, 1350
TOTAL = 8
FOOTER = "DISCIPLINE · ACCOUNTABILITY · CONSISTENCY"

HEAD = "brand/fonts/Anton-Regular.ttf"
NUMERAL = "brand/fonts/BodoniModa-Black.ttf"
BODY = "brand/fonts/Montserrat-Medium.ttf"
UTIL = "brand/fonts/Montserrat-Bold.ttf"


def rgb(hex_value):
    hex_value = hex_value.lstrip("#")
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))


BONE, GOLD, LGOLD, STONE, CHAR, INK = (rgb(C[k]) for k in ("bone", "antique_gold", "light_gold", "stone", "charcoal", "ink"))


def font(path, size):
    return ImageFont.truetype(str(ROOT / path), size)


# ---------------------------------------------------------------- surface

def surface(seed, light=(0.85, 0.08), strength=1.0):
    """Charcoal stone surface: low-frequency mottling, one warm light source, fine grain."""
    rng = np.random.default_rng(seed)
    base = np.zeros((H, W), dtype=np.float32)
    for scale, weight in ((6, 0.5), (18, 0.3), (60, 0.2)):
        small = rng.normal(0, 1, (H // scale + 2, W // scale + 2)).astype(np.float32)
        layer = np.asarray(Image.fromarray(small).resize((W, H), Image.BICUBIC))
        base += layer * weight
    base = (base - base.mean()) / base.std()

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lx, ly = light[0] * W, light[1] * H
    dist = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2) / np.hypot(W, H)
    glow = np.clip(1 - dist / 0.75, 0, 1) ** 2.2 * strength

    char = np.array(CHAR, dtype=np.float32)
    warm = np.array([92, 68, 36], dtype=np.float32)
    img = char + glow[..., None] * (warm - char) * 0.55
    img = img + base[..., None] * 4.0
    img = img + rng.normal(0, 3.5, (H, W))[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8"))


def big_numeral(img, text, x, y, size=560, alpha=0.11):
    """Oversized serif numeral as an engraved background mark."""
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    f = font(NUMERAL, size)
    d.text((x, y), text, font=f, fill=int(255 * alpha))
    gold = Image.new("RGB", (W, H), GOLD)
    img.paste(gold, (0, 0), layer)


def frame(img, inset=36):
    d = ImageDraw.Draw(img)
    d.rectangle((inset, inset, W - inset, H - inset), outline=GOLD, width=1)


# ---------------------------------------------------------------- typography

def fit_size(path, lines, max_width, hi, lo):
    for size in range(hi, lo - 1, -2):
        f = font(path, size)
        if max(f.getlength(t) for t in lines) <= max_width:
            return size
    return lo


def wrap(f, text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(d, x, y, text, f, fill, tracking):
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + tracking
    return x


def tracked_width(text, f, tracking):
    return sum(f.getlength(ch) + tracking for ch in text) - tracking


class Block:
    """Lays out a text column top-down; measure first with dry=True to centre vertically."""

    def __init__(self, d, x, y, width, align="left", dry=False):
        self.d, self.x, self.y, self.width, self.align, self.dry = d, x, y, width, align, dry
        self.top = y

    def _x(self, w):
        return self.x + (self.width - w) / 2 if self.align == "center" else self.x

    def eyebrow(self, text, colour=GOLD, gap=30):
        f = font(UTIL, 22)
        w = tracked_width(text, f, 4)
        if not self.dry:
            tracked(self.d, self._x(w), self.y - f.getbbox(text)[1], text, f, colour, 4)
        self.y += 22 + gap

    def display(self, lines, colours, hi, lo, leading=0.98, gap=34, path=HEAD):
        size = fit_size(path, lines, self.width, hi, lo)
        f = font(path, size)
        cap = f.getbbox("H")
        for text, colour in zip(lines, colours):
            if not self.dry:
                self.d.text((self._x(f.getlength(text)), self.y - cap[1]), text, font=f, fill=colour)
            self.y += round(size * leading)
        self.y += gap - round(size * leading) + (cap[3] - cap[1])

    def rule(self, length=96, gap=34):
        if not self.dry:
            x = self._x(length)
            self.d.line((x, self.y, x + length, self.y), fill=GOLD, width=2)
        self.y += gap

    def body(self, text, size=34, colour=BONE, gap=0):
        f = font(BODY, size)
        asc = f.getbbox("Hg")
        for line in wrap(f, text, self.width):
            if not self.dry:
                self.d.text((self._x(f.getlength(line)), self.y - asc[1]), line, font=f, fill=colour)
            self.y += round(size * 1.38)
        self.y += gap - round(size * 1.38) + (asc[3] - asc[1])


def centred(img, build, x, width, top=110, bottom=1150, align="left"):
    """Run build() once to measure, then again centred between top and bottom."""
    probe = Block(None, x, 0, width, align, dry=True)
    build(probe)
    y = top + max(0, (bottom - top - probe.y) // 2)
    block = Block(ImageDraw.Draw(img), x, y, width, align)
    build(block)
    return block


def furniture(img, index):
    d = ImageDraw.Draw(img)
    mono = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((64, 64), Image.LANCZOS)
    img.paste(mono, (80, 1206), mono)
    f = font(UTIL, 18)
    text = f"{FOOTER}  ·  {index:02d}/{TOTAL:02d}"
    w = tracked_width(text, f, 2)
    tracked(d, 1000 - w, 1240 - f.getbbox(text)[1], text, f, STONE, 2)
    d.line((166, 1248, 1000 - w - 28, 1248), fill=GOLD, width=1)


# ---------------------------------------------------------------- slides

def slide_01():
    img = surface(1, light=(0.95, 0.0))
    frame(img)

    def build(b):
        b.eyebrow("EDISON EATS")
        b.display(["YOU'RE", "FOLLOWING"], [BONE, BONE], 210, 150, gap=14)
        b.display(["THE WRONG", "RULES."], [GOLD, GOLD], 210, 150)
        b.rule()
        b.body("5 fat-loss myths that keep disciplined people stuck, and what to do instead.", size=36)

    centred(img, build, 92, 860, top=120, bottom=1130)
    d = ImageDraw.Draw(img)
    f = font(UTIL, 20)
    text = "SWIPE  →"
    tracked(d, 1000 - tracked_width(text, f, 4), 1150, text, f, LGOLD, 4)
    return img


def myth(index, number, myth_lines, truth_lines, body, light):
    img = surface(index, light=light)
    variant = ("right", "left", "centre", "right", "left")[number - 1]
    if variant == "right":
        big_numeral(img, f"{number:02d}", 470, -60)
        x, width, top, bottom, align = 92, 880, 130, 1150, "left"
    elif variant == "left":
        big_numeral(img, f"{number:02d}", -30, -60)
        x, width, top, bottom, align = 92, 880, 330, 1170, "left"
    else:
        f = font(NUMERAL, 760)
        big_numeral(img, f"{number:02d}", (W - f.getlength(f"{number:02d}")) / 2, 120, size=760, alpha=0.08)
        x, width, top, bottom, align = 80, 920, 130, 1150, "center"

    def build(b):
        b.eyebrow(f"MYTH {number:02d} / 05")
        b.eyebrow("THE MYTH", colour=STONE, gap=22)
        b.display(myth_lines, [BONE] * len(myth_lines), 128, 84)
        b.rule(gap=40)
        b.eyebrow("THE TRUTH", colour=STONE, gap=22)
        b.display(truth_lines, [GOLD] * len(truth_lines), 104, 72, gap=40)
        b.body(body)

    centred(img, build, x, width, top=top, bottom=bottom, align=align)
    return img


def slide_07():
    img = surface(7, light=(0.5, 0.0), strength=1.2)
    frame(img)

    def build(b):
        b.display(["STOP CHASING HACKS."], [BONE], 130, 96, gap=26)
        b.display(["REPEAT", "THE BASICS."], [GOLD, GOLD], 260, 160, leading=0.96, gap=46)
        b.rule(gap=44)
        b.body("A deficit you can sustain. Protein at every meal. Training you repeat. Weeks you don't write off.", size=36)

    centred(img, build, 80, 920, top=110, bottom=1150, align="center")
    return img


def slide_08():
    img = surface(8, light=(0.1, 0.0))
    frame(img)

    def build(b):
        b.eyebrow("YOUR TURN")
        b.display(["WHICH MYTH", "KEPT YOU"], [BONE, BONE], 190, 130, gap=14)
        b.display(["STUCK?"], [GOLD], 300, 200)
        b.rule()
        b.body("Comment the one you believed the longest. I'll reply with what to do instead.", size=36)

    centred(img, build, 92, 860, top=120, bottom=1150)
    return img


SLIDES = [
    ("01-hook", slide_01),
    ("02-myth-undereating", lambda: myth(2, 1, ["“EAT AS LITTLE", "AS POSSIBLE.”"], ["SUSTAINABLE", "BEATS EXTREME."],
        "Crash diets drive up hunger, drain your training and make muscle harder to keep. "
        "Choose a deficit you can hold for months, not one you quit in two weeks.", (0.9, 0.05))),
    ("03-myth-carbs", lambda: myth(3, 2, ["“CARBS MAKE", "YOU FAT.”"], ["A SURPLUS DOES."],
        "Fat loss comes from eating fewer calories than you burn. Rice, potatoes and oats can fit. "
        "Watch the portion, and what you pour on top.", (0.1, 0.05))),
    ("04-myth-protein-labels", lambda: myth(4, 3, ["“IF IT SAYS PROTEIN,", "IT'S A PROTEIN", "SOURCE.”"], ["READ THE LABEL."],
        "Many bars and snacks get more of their calories from sugar and fat than from protein. "
        "Build meals around chicken, eggs, tuna or lean beef first.", (0.9, 0.05))),
    ("05-myth-weekends", lambda: myth(5, 4, ["“WEEKENDS", "DON'T COUNT.”"], ["THEY'RE 2 DAYS", "OUT OF 7."],
        "Two unplanned days can undo five planned ones. Plan one meal out, keep your protein high and keep moving.",
        (0.1, 0.05))),
    ("06-myth-scale", lambda: myth(6, 5, ["“THE SCALE WENT UP.", "IT'S NOT WORKING.”"], ["JUDGE THE TREND."],
        "Daily weight moves with water, salt, carbs and digestion. Weigh in each morning and compare weekly averages.",
        (0.9, 0.05))),
    ("07-climax", slide_07),
    ("08-close", slide_08),
]


def main():
    files = []
    for i, (name, build) in enumerate(SLIDES, 1):
        img = build()
        furniture(img, i)
        path = OUT / f"{name}.png"
        img.save(path, optimize=True)
        files.append(path)
        print(name)

    thumbs = [Image.open(p).resize((360, 450), Image.LANCZOS) for p in files]
    sheet = Image.new("RGB", (4 * 360 + 5 * 20, 2 * 450 + 3 * 20), INK)
    for k, t in enumerate(thumbs):
        sheet.paste(t, (20 + (k % 4) * 380, 20 + (k // 4) * 470))
    sheet.save(OUT / "preview.jpg", quality=90)

    with zipfile.ZipFile(OUT / "final-carousel.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.name)
        for extra in ("caption.txt", "copy.txt", "alt-text.txt"):
            if (OUT / extra).exists():
                z.write(OUT / extra, extra)


if __name__ == "__main__":
    main()
