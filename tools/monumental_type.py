"""Shared building blocks for typographic Monumental-kit carousels (no photographs).

A carousel is a list of slide specs (dicts with a "type" key). render_carousel()
draws each slide on a charcoal stone surface and writes numbered PNG and JPEG
files, a contact sheet and a posting ZIP.
"""
import json
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "brand/monumental/tokens.json").read_text())
C = TOKENS["colors"]
W, H = 1080, 1350
FOOTER = "DISCIPLINE · ACCOUNTABILITY · CONSISTENCY"

HEAD = "brand/fonts/Anton-Regular.ttf"
NUMERAL = "brand/fonts/BodoniModa-Black.ttf"
BODY = "brand/fonts/Montserrat-Medium.ttf"
UTIL = "brand/fonts/Montserrat-Bold.ttf"


def rgb(hex_value):
    hex_value = hex_value.lstrip("#")
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))


BONE, GOLD, LGOLD, STONE, CHAR, INK = (rgb(C[k]) for k in ("bone", "antique_gold", "light_gold", "stone", "charcoal", "ink"))
LIGHTS = [(0.95, 0.0), (0.9, 0.05), (0.1, 0.05), (0.5, 0.0), (0.85, 0.1), (0.15, 0.0)]


def font(path, size):
    return ImageFont.truetype(str(ROOT / path), size)


# ---------------------------------------------------------------- surface

def surface(seed, light=(0.85, 0.08), strength=1.0):
    """Charcoal stone surface: low-frequency mottling, one warm light source, fine grain."""
    rng = np.random.default_rng(seed)
    base = np.zeros((H, W), dtype=np.float32)
    for scale, weight in ((6, 0.5), (18, 0.3), (60, 0.2)):
        small = rng.normal(0, 1, (H // scale + 2, W // scale + 2)).astype(np.float32)
        base += np.asarray(Image.fromarray(small).resize((W, H), Image.BICUBIC)) * weight
    base = (base - base.mean()) / base.std()

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.sqrt((xx - light[0] * W) ** 2 + (yy - light[1] * H) ** 2) / np.hypot(W, H)
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
    ImageDraw.Draw(layer).text((x, y), text, font=font(NUMERAL, size), fill=int(255 * alpha))
    img.paste(Image.new("RGB", (W, H), GOLD), (0, 0), layer)


def frame(img, inset=36):
    ImageDraw.Draw(img).rectangle((inset, inset, W - inset, H - inset), outline=GOLD, width=1)


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

    def rows(self, items, size=50, gap=0):
        """Numbered list: gold serif numeral, bone condensed text, fine dividers."""
        nf, tf = font(NUMERAL, 46), font(HEAD, size)
        text_x = self.x + 110
        cap = tf.getbbox("H")
        row_h = (cap[3] - cap[1]) + 64
        for i, item in enumerate(items, 1):
            lines = wrap(tf, item, self.width - 110)
            h = row_h + (len(lines) - 1) * round(size * 1.02)
            if not self.dry:
                self.d.line((self.x, self.y, self.x + self.width, self.y), fill=(70, 62, 50), width=1)
                self.d.text((self.x, self.y + 30 - nf.getbbox("0")[1] + 2), f"{i:02d}", font=nf, fill=GOLD)
                ty = self.y + 32
                for line in lines:
                    self.d.text((text_x, ty - cap[1]), line, font=tf, fill=BONE)
                    ty += round(size * 1.02)
            self.y += h
        if not self.dry:
            self.d.line((self.x, self.y, self.x + self.width, self.y), fill=(70, 62, 50), width=1)
        self.y += gap


def fit_build(make, x, width, top, bottom, align="left", start=210, floor=110):
    """Return make(hi) for the largest headline ceiling whose layout fits between top and bottom."""
    for hi in range(start, floor - 1, -10):
        probe = Block(None, x, 0, width, align, dry=True)
        make(hi)(probe)
        if probe.y <= bottom - top:
            return make(hi)
    return make(floor)


def centred(img, build, x, width, top=110, bottom=1150, align="left"):
    """Run build() once to measure, then again centred between top and bottom."""
    probe = Block(None, x, 0, width, align, dry=True)
    build(probe)
    y = top + max(0, (bottom - top - probe.y) // 2)
    block = Block(ImageDraw.Draw(img), x, y, width, align)
    build(block)
    return block


def furniture(img, index, total):
    d = ImageDraw.Draw(img)
    mono = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((64, 64), Image.LANCZOS)
    img.paste(mono, (80, 1206), mono)
    f = font(UTIL, 18)
    text = f"{FOOTER}  ·  {index:02d}/{total:02d}"
    w = tracked_width(text, f, 2)
    tracked(d, 1000 - w, 1240 - f.getbbox(text)[1], text, f, STONE, 2)
    d.line((166, 1248, 1000 - w - 28, 1248), fill=GOLD, width=1)


# ---------------------------------------------------------------- slide types

def hook(s, seed):
    img = surface(seed, light=LIGHTS[0])
    frame(img)

    def make(hi):
        def build(b):
            b.eyebrow(s["eyebrow"])
            b.display(s["bone"], [BONE] * len(s["bone"]), hi, 100, gap=14)
            b.display(s["gold"], [GOLD] * len(s["gold"]), hi, 100)
            b.rule()
            b.body(s["body"], size=36)
        return build

    centred(img, fit_build(make, 92, 860, 120, 1110), 92, 860, top=120, bottom=1110)
    d = ImageDraw.Draw(img)
    f = font(UTIL, 20)
    tracked(d, 1000 - tracked_width("SWIPE  →", f, 4), 1150, "SWIPE  →", f, LGOLD, 4)
    return img


def point(s, seed, position):
    """Numbered teaching slide: eyebrow, headline (last line gold), rule, body."""
    img = surface(seed, light=LIGHTS[seed % len(LIGHTS)])
    variant = ("right", "left", "centre")[position % 3]
    num = s.get("numeral")
    if variant == "right":
        if num:
            big_numeral(img, num, 470, -60)
        x, width, top, bottom, align = 92, 880, 130, 1150, "left"
    elif variant == "left":
        if num:
            big_numeral(img, num, -30, -60)
        x, width, top, bottom, align = 92, 880, 330, 1170, "left"
    else:
        if num:
            f = font(NUMERAL, 760)
            big_numeral(img, num, (W - f.getlength(num)) / 2, 120, size=760, alpha=0.08)
        x, width, top, bottom, align = 80, 920, 130, 1150, "center"
    head = s["head"]
    colours = [BONE] * (len(head) - 1) + [GOLD]

    def build(b):
        b.eyebrow(s["eyebrow"])
        if s.get("label"):
            b.eyebrow(s["label"], colour=STONE, gap=22)
        b.display(head, colours, s.get("hi", 140), 84)
        b.rule(gap=40)
        b.body(s["body"])

    centred(img, build, x, width, top=top, bottom=bottom, align=align)
    return img


def listing(s, seed):
    img = surface(seed, light=LIGHTS[seed % len(LIGHTS)])

    def build(b):
        b.eyebrow(s["eyebrow"])
        b.display(s["head"], [BONE] * (len(s["head"]) - 1) + [GOLD], 130, 84, gap=44)
        b.rows(s["items"], size=s.get("size", 50), gap=36 if s.get("body") else 0)
        if s.get("body"):
            b.body(s["body"], size=30, colour=STONE)

    centred(img, build, 92, 896, top=120, bottom=1160)
    return img


def chart(s, seed):
    """Expectation-vs-reality line chart (illustrative, not data)."""
    img = surface(seed, light=LIGHTS[1])
    d = ImageDraw.Draw(img)
    top = 140
    b = Block(d, 92, top, 896)
    b.eyebrow(s["eyebrow"])
    b.display(s["head"], [BONE] * (len(s["head"]) - 1) + [GOLD], 110, 72, gap=40)

    x0, x1, y0, y1 = 120, 960, b.y + 20, b.y + 420
    d.line((x0, y0, x0, y1), fill=STONE, width=2)
    d.line((x0, y1, x1, y1), fill=STONE, width=2)
    sf = font(UTIL, 18)
    tracked(d, x0 + 12, y0 - 8, "WEIGHT", sf, STONE, 3)
    tracked(d, x1 - tracked_width("WEEKS", sf, 3), y1 + 14, "WEEKS", sf, STONE, 3)

    # Expectation: straight dashed bone line.
    sx, sy, ex, ey = x0 + 20, y0 + 60, x1 - 20, y1 - 60
    for t in np.linspace(0, 1, 28)[::2]:
        t2 = min(t + 1 / 27, 1)
        d.line((sx + (ex - sx) * t, sy + (ey - sy) * t, sx + (ex - sx) * t2, sy + (ey - sy) * t2), fill=BONE, width=4)
    # Reality: a downward trend with fluctuations and flat stretches (fixed, illustrative).
    # Each point is (time 0-1, progress 0-1 toward the end weight): bumps up, flat weeks, sudden drops.
    path = [(0, 0), (0.05, -0.06), (0.1, 0.1), (0.15, 0.04), (0.2, 0.14), (0.27, 0.13), (0.34, 0.15),
            (0.4, 0.12), (0.44, 0.36), (0.5, 0.3), (0.55, 0.42), (0.6, 0.38), (0.66, 0.41), (0.72, 0.39),
            (0.76, 0.66), (0.82, 0.6), (0.87, 0.74), (0.92, 0.7), (1, 0.97)]
    pts = [(sx + (ex - sx) * t, sy + (ey - sy) * p) for t, p in path]
    d.line(pts, fill=GOLD, width=6, joint="curve")

    lf = font(UTIL, 20)
    lx, ly = x0 + 40, y1 + 64
    d.line((lx, ly + 10, lx + 56, ly + 10), fill=BONE, width=4)
    tracked(d, lx + 72, ly, "WHAT YOU EXPECT", lf, BONE, 3)
    d.line((lx + 420, ly + 10, lx + 476, ly + 10), fill=GOLD, width=6)
    tracked(d, lx + 492, ly, "WHAT ACTUALLY HAPPENS", lf, GOLD, 3)

    b.y = ly + 80
    b.body(s["body"], size=32)
    nf = font(BODY, 20)
    d.text((92, b.y + 24), "Illustration, not real data.", font=nf, fill=STONE)
    return img


def statement(s, seed):
    img = surface(seed, light=LIGHTS[3], strength=1.2)
    frame(img)

    def build(b):
        b.display(s["bone"], [BONE] * len(s["bone"]), 130, 84, gap=26)
        b.display(s["gold"], [GOLD] * len(s["gold"]), 230, 120, leading=0.96, gap=46 if s.get("body") else 0)
        if s.get("body"):
            b.rule(gap=44)
            b.body(s["body"], size=36)

    centred(img, build, 80, 920, top=110, bottom=1150, align="center")
    return img


def close(s, seed):
    img = surface(seed, light=LIGHTS[5])
    frame(img)

    def make(hi):
        def build(b):
            b.eyebrow(s.get("eyebrow", "YOUR TURN"))
            b.display(s["bone"], [BONE] * len(s["bone"]), round(hi * 0.73), 100, gap=14)
            b.display(s["gold"], [GOLD] * len(s["gold"]), hi, 120)
            b.rule()
            b.body(s["body"], size=36)
        return build

    centred(img, fit_build(make, 92, 860, 120, 1150, start=260, floor=140), 92, 860, top=120, bottom=1150)
    return img


# ---------------------------------------------------------------- output

def render_carousel(out_dir, slides, seed_base=0):
    out_dir = Path(out_dir)
    (out_dir / "jpg").mkdir(parents=True, exist_ok=True)
    total = len(slides)
    pngs, jpgs = [], []
    position = 0
    for i, s in enumerate(slides, 1):
        seed = seed_base + i
        kind = s["type"]
        if kind == "point":
            img = point(s, seed, position)
            position += 1
        else:
            img = {"hook": hook, "listing": listing, "chart": chart, "statement": statement, "close": close}[kind](s, seed)
        furniture(img, i, total)
        name = f"{i:02d}-{s['slug']}"
        png = out_dir / f"{name}.png"
        img.save(png, optimize=True)
        jpg = out_dir / "jpg" / f"{name}.jpg"
        img.save(jpg, quality=93)
        pngs.append(png)
        jpgs.append(jpg)

    cols = 4
    rows = (total + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 360 + (cols + 1) * 20, rows * 450 + (rows + 1) * 20), INK)
    for k, p in enumerate(pngs):
        sheet.paste(Image.open(p).resize((360, 450), Image.LANCZOS), (20 + (k % cols) * 380, 20 + (k // cols) * 470))
    sheet.save(out_dir / "preview.jpg", quality=90)

    with zipfile.ZipFile(out_dir / "final-carousel.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in pngs:
            z.write(p, p.name)
        for extra in ("caption.txt", "copy.txt"):
            if (out_dir / extra).exists():
                z.write(out_dir / extra, extra)
    with zipfile.ZipFile(out_dir / "jpg" / "slides-jpg.zip", "w") as z:
        for p in jpgs:
            z.write(p, p.name)
    return pngs


def copy_text(title, slides):
    """Plain-text transcript of every slide's words, for review."""
    out = [title, ""]
    for i, s in enumerate(slides, 1):
        parts = [s.get("eyebrow", ""), s.get("label", "")]
        for key in ("bone", "gold", "head", "items"):
            if s.get(key):
                parts.append(" / ".join(s[key]))
        parts.append(s.get("body", ""))
        out.append(f"{i:02d} " + " | ".join(p for p in parts if p))
    return "\n".join(out) + "\n"
