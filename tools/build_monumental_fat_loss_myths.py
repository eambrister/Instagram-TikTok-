"""Build the Monumental-kit carousel "Fat-loss myths that keep you stuck".

Exact-photo mode: Edison's pixels are never reshaped or retouched. A person
segmentation mask (MediaPipe selfie_multiclass, run via ai-edge-litert) is used
only to grade the background separately from the subject.

Usage: python3 tools/build_monumental_fat_loss_myths.py [--model PATH]
"""
import argparse
import json
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/edison-ambrister-fat-loss-myths"
SRC = OUT / "source-photos"
TOKENS = json.loads((ROOT / "brand/monumental/tokens.json").read_text())
C = TOKENS["colors"]
W, H = 1080, 1350
TOTAL = 8
FOOTER = "DISCIPLINE · ACCOUNTABILITY · CONSISTENCY"


def rgb(hex_value):
    hex_value = hex_value.lstrip("#")
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))


BONE, GOLD, LGOLD, STONE, CHAR = (rgb(C[k]) for k in ("bone", "antique_gold", "light_gold", "stone", "charcoal"))


def font(path, size):
    return ImageFont.truetype(str(ROOT / path), size)


HEAD = "brand/fonts/Anton-Regular.ttf"
BODY = "brand/fonts/Montserrat-Medium.ttf"
UTIL = "brand/fonts/Montserrat-Bold.ttf"


# ---------------------------------------------------------------- masks

class Segmenter:
    def __init__(self, model_path):
        from ai_edge_litert.interpreter import Interpreter
        self.it = Interpreter(model_path=str(model_path))
        self.it.allocate_tensors()
        self.inp = self.it.get_input_details()[0]["index"]
        self.out = self.it.get_output_details()[0]["index"]

    def person(self, im):
        x = np.asarray(im.convert("RGB").resize((256, 256), Image.BILINEAR), dtype=np.float32) / 255.0
        self.it.set_tensor(self.inp, x[None])
        self.it.invoke()
        logits = self.it.get_tensor(self.out)[0]
        e = np.exp(logits - logits.max(-1, keepdims=True))
        p = 1.0 - (e / e.sum(-1, keepdims=True))[..., 0]
        return Image.fromarray((p * 255).astype("uint8")).resize(im.size, Image.BICUBIC)


# ---------------------------------------------------------------- grading

def grade(photo, mask):
    """Background: desaturated, deeper and cooler. Subject: original, lightly balanced."""
    a = np.asarray(photo, dtype=np.float32) / 255.0
    m = np.asarray(mask, dtype=np.float32) / 255.0
    m = np.clip((m - 0.3) / 0.4, 0, 1)
    m = np.asarray(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(3)), dtype=np.float32)[..., None] / 255.0

    lum = (a * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    bg = lum + (a - lum) * 0.28
    bg = bg ** 1.15 * 0.46
    bg = bg * np.array([0.94, 1.0, 1.07])

    subj = (a - 0.5) * 1.05 + 0.5
    subj = subj * np.array([1.02, 1.0, 0.97])

    out = np.clip(m * subj + (1 - m) * bg, 0, 1)
    return Image.fromarray((out * 255).astype("uint8"))


def scrim(img, direction, start, end, max_alpha):
    """Feathered charcoal gradient: full max_alpha at `start`, fading to 0 at `end` (pixels on the axis)."""
    axis = np.arange(W if direction in ("left", "right") else H, dtype=np.float32)
    if direction == "bottom":
        start, end = H - start, H - end
        axis = axis[::-1]
    t = np.clip((axis - start) / (end - start), 0, 1)
    t = t * t * (3 - 2 * t)
    alpha = (1 - t) * max_alpha
    if direction in ("left", "right"):
        alpha = np.tile(alpha, (H, 1))
    else:
        alpha = np.tile(alpha[:, None], (1, W))
    layer = Image.new("RGB", (W, H), CHAR)
    return Image.composite(layer, img, Image.fromarray((alpha * 255).astype("uint8")))


def dim_background(seg, img, box, factor):
    """Deepen only the background inside box (used to suppress third-party signage)."""
    m = np.asarray(seg.person(img), dtype=np.float32)[..., None] / 255.0
    a = np.asarray(img, dtype=np.float32)
    region = np.zeros(m.shape, dtype=np.float32)
    x0, y0, x1, y1 = box
    region[y0:y1, x0:x1] = 1.0
    region = np.asarray(Image.fromarray((region[..., 0] * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(40)), dtype=np.float32)[..., None] / 255.0
    k = 1 - region * (1 - m) * (1 - factor)
    return Image.fromarray(np.clip(a * k, 0, 255).astype("uint8"))


def grain(img, strength=5.0, seed=1):
    a = np.asarray(img, dtype=np.float32)
    noise = np.random.default_rng(seed).normal(0, strength, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + noise, 0, 255).astype("uint8"))


# ---------------------------------------------------------------- photo placement

def load(name):
    return Image.open(SRC / name).convert("RGB")


def crop_cover(seg, name, box):
    """Crop a source box (x0, y0, x1, y1) and scale it to the full canvas."""
    im = load(name)
    mask = seg.person(im)
    im, mask = im.crop(box), mask.crop(box)
    return grade(im.resize((W, H), Image.LANCZOS), mask.resize((W, H), Image.LANCZOS))


def fade_right(seg, name, x_offset, fade_width=260):
    """Photo scaled to canvas height and placed at x_offset; the left side is the same photo,
    blurred and deepened, so the frame stays photographic edge to edge."""
    im = load(name)
    mask = seg.person(im)
    scale = H / im.height
    size = (round(im.width * scale), H)
    graded = grade(im.resize(size, Image.LANCZOS), mask.resize(size, Image.LANCZOS))

    cover_scale = max(W / im.width, H / im.height)
    bg = grade(im.resize((round(im.width * cover_scale), round(im.height * cover_scale)), Image.LANCZOS),
               Image.new("L", (round(im.width * cover_scale), round(im.height * cover_scale)), 0))
    bg = bg.crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.eval(bg, lambda v: int(v * 0.55))

    alpha = np.ones((H, size[0]), dtype=np.float32)
    ramp = np.clip(np.arange(size[0], dtype=np.float32) / fade_width, 0, 1)
    alpha *= ramp * ramp * (3 - 2 * ramp)
    canvas = bg.copy()
    canvas.paste(graded, (x_offset, 0), Image.fromarray((alpha * 255).astype("uint8")))
    return canvas


def diptych(seg):
    canvas = Image.new("RGB", (W, H), CHAR)
    hero = load("p06-bedroom-mirror-tank.jpg")
    hm = seg.person(hero)
    box = (250, 0, 1056, 2016)
    canvas.paste(grade(hero.crop(box).resize((540, H), Image.LANCZOS), hm.crop(box).resize((540, H), Image.LANCZOS)), (0, 0))
    second = load("p05-bedroom-mirror-shirtless.png")
    sm = seg.person(second)
    box = (0, 60, 1086, 1337)
    canvas.paste(grade(second.crop(box).resize((540, 635), Image.LANCZOS), sm.crop(box).resize((540, 635), Image.LANCZOS)), (540, 715))
    d = ImageDraw.Draw(canvas)
    d.line((540, 0, 540, H), fill=GOLD, width=2)
    d.line((540, 715, W, 715), fill=GOLD, width=2)
    return canvas


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
    """Lays out a text column top-down and records glyph boxes for collision checks."""

    def __init__(self, d, x, y, width, align="left"):
        self.d, self.x, self.y, self.width, self.align = d, x, y, width, align
        self.boxes = []

    def _x(self, w):
        return self.x + (self.width - w) / 2 if self.align == "center" else self.x

    def eyebrow(self, text, gap=26):
        f = font(UTIL, 20)
        w = tracked_width(text, f, 3)
        top = f.getbbox(text)[1]
        tracked(self.d, self._x(w), self.y - top, text, f, GOLD, 3)
        self.boxes.append((self._x(w), self.y, self._x(w) + w, self.y + 20))
        self.y += 20 + gap

    def display(self, lines, colours, hi, lo, leading=1.0, gap=30, path=HEAD):
        size = fit_size(path, lines, self.width, hi, lo)
        f = font(path, size)
        cap = f.getbbox("H")
        for text, colour in zip(lines, colours):
            w = f.getlength(text)
            x = self._x(w)
            self.d.text((x, self.y - cap[1]), text, font=f, fill=colour)
            self.boxes.append((x, self.y, x + w, self.y + cap[3] - cap[1]))
            self.y += round(size * leading)
        self.y += gap - round(size * leading) + (cap[3] - cap[1])
        return size

    def rule(self, length=80, gap=30):
        x = self._x(length)
        self.d.line((x, self.y, x + length, self.y), fill=GOLD, width=2)
        self.y += gap

    def body(self, text, size=31, colour=BONE, gap=22):
        f = font(BODY, size)
        lines = wrap(f, text, self.width)
        asc = f.getbbox("Hg")
        for line in lines:
            w = f.getlength(line)
            x = self._x(w)
            self.d.text((x, self.y - asc[1]), line, font=f, fill=colour)
            self.boxes.append((x, self.y, x + w, self.y + asc[3] - asc[1]))
            self.y += round(size * 1.36)
        self.y += gap


def furniture(img, index):
    img.paste(scrim(img, "bottom", 1350, 1140, 0.72))
    d = ImageDraw.Draw(img)
    mono = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((64, 64), Image.LANCZOS)
    img.paste(mono, (80, 1206), mono)
    f = font(UTIL, 18)
    text = f"{FOOTER}  ·  {index:02d}/{TOTAL:02d}"
    w = tracked_width(text, f, 2)
    tracked(d, 1000 - w, 1240 - f.getbbox(text)[1], text, f, STONE, 2)
    d.line((166, 1248, 1000 - w - 28, 1248), fill=GOLD, width=1)


# ---------------------------------------------------------------- slides

def slide_01(seg):
    img = crop_cover(seg, "p01-gym-standing.jpg", (0, 586, 1170, 2048))
    img = scrim(img, "left", 300, 700, 0.82)
    b = Block(ImageDraw.Draw(img), 80, 330, 470)
    b.eyebrow("EDISON EATS")
    b.display(["YOU'RE", "FOLLOWING"], [BONE, BONE], 150, 96, leading=0.98, gap=8)
    b.display(["THE WRONG", "RULES."], [GOLD, GOLD], 150, 96, leading=0.98)
    b.rule()
    b.body("5 fat-loss myths that keep disciplined people stuck, and what to do instead.")
    return img, b


def myth(b, number, myth_lines, truth_lines, body, hi=110, lo=72):
    b.eyebrow(f"MYTH {number:02d}")
    b.display(myth_lines, [BONE] * len(myth_lines), hi, lo, leading=0.98)
    b.rule(gap=28)
    b.display(truth_lines, [GOLD] * len(truth_lines), 66, 44, leading=1.0, gap=26)
    b.body(body)


def slide_02(seg):
    img = crop_cover(seg, "p03-pec-deck.jpg", (0, 300, 1170, 1762))
    img = dim_background(seg, img, (0, 0, 280, 1100), 0.25)
    img = scrim(img, "top", 520, 760, 0.86)
    b = Block(ImageDraw.Draw(img), 80, 96, 860)
    myth(b, 1, ["“EAT AS LITTLE AS POSSIBLE.”"], ["SUSTAINABLE BEATS EXTREME."],
         "Crash diets drive up hunger, drain your training and make muscle harder to keep. "
         "Choose a deficit you can hold for months, not one you quit in two weeks.", hi=96, lo=64)
    return img, b


def slide_03(seg):
    img = crop_cover(seg, "p04-gym-mirror.jpg", (0, 340, 1040, 1640))
    img = scrim(img, "left", 380, 640, 0.86)
    b = Block(ImageDraw.Draw(img), 80, 170, 480)
    myth(b, 2, ["“CARBS MAKE", "YOU FAT.”"], ["A SURPLUS DOES."],
         "Fat loss comes from eating fewer calories than you burn. Rice, potatoes and oats can fit. "
         "Watch the portion, and what you pour on top.")
    return img, b


def slide_04(seg):
    img = fade_right(seg, "p09-outdoor.jpg", 330)
    img = scrim(img, "left", 300, 560, 0.7)
    b = Block(ImageDraw.Draw(img), 80, 150, 330)
    myth(b, 3, ["“IF IT SAYS", "PROTEIN, IT'S", "A PROTEIN", "SOURCE.”"], ["READ THE", "LABEL."],
         "Many bars and snacks get more of their calories from sugar and fat than from protein. "
         "Build meals around chicken, eggs, tuna or lean beef first.", hi=86, lo=60)
    return img, b


def slide_05(seg):
    img = crop_cover(seg, "p08-pool.jpg", (0, 130, 1170, 1592))
    img = scrim(img, "top", 470, 700, 0.84)
    b = Block(ImageDraw.Draw(img), 120, 96, 840, align="center")
    myth(b, 4, ["“WEEKENDS DON'T COUNT.”"], ["THEY'RE 2 DAYS OUT OF 7."],
         "Two unplanned days can undo five planned ones. Plan one meal out, keep your protein high and keep moving.",
         hi=100, lo=64)
    return img, b


def slide_06(seg):
    img = diptych(seg)
    b = Block(ImageDraw.Draw(img), 590, 110, 410)
    myth(b, 5, ["“THE SCALE WENT", "UP. IT'S NOT", "WORKING.”"], ["JUDGE THE TREND."],
         "Daily weight moves with water, salt, carbs and digestion. Weigh in each morning and compare weekly averages.",
         hi=80, lo=56)
    return img, b


def slide_07(seg):
    img = crop_cover(seg, "p02-home-full-body.jpg", (0, 0, 1170, 1462))
    img = scrim(img, "top", 560, 760, 0.62)
    img = scrim(img, "left", 260, 420, 0.6)
    d = ImageDraw.Draw(img)
    b = Block(d, 60, 64, 960, align="center")
    b.display(["STOP CHASING HACKS."], [BONE], 128, 96, leading=1.0, gap=14)
    b.display(["REPEAT THE", "BASICS."], [GOLD, GOLD], 188, 140, leading=0.97, gap=0)
    side = Block(d, 80, 880, 270)
    side.rule(gap=26)
    side.body("A deficit you can sustain. Protein at every meal. Training you repeat. Weeks you don't write off.", size=28)
    b.boxes += side.boxes
    return img, b


def slide_08(seg):
    img = fade_right(seg, "p07-portrait.jpg", 340)
    img = scrim(img, "left", 330, 600, 0.75)
    b = Block(ImageDraw.Draw(img), 80, 300, 360)
    b.eyebrow("YOUR TURN")
    b.display(["WHICH MYTH", "KEPT YOU"], [BONE, BONE], 96, 64, leading=0.98, gap=8)
    b.display(["STUCK?"], [GOLD], 150, 96, leading=1.0)
    b.rule()
    b.body("Comment the one you believed the longest. I'll reply with what to do instead.", size=30)
    return img, b


SLIDES = [
    ("01-hook", slide_01, "p01-gym-standing.jpg"),
    ("02-myth-undereating", slide_02, "p03-pec-deck.jpg"),
    ("03-myth-carbs", slide_03, "p04-gym-mirror.jpg"),
    ("04-myth-protein-labels", slide_04, "p09-outdoor.jpg"),
    ("05-myth-weekends", slide_05, "p08-pool.jpg"),
    ("06-myth-scale", slide_06, "p06-bedroom-mirror-tank.jpg + p05-bedroom-mirror-shirtless.png"),
    ("07-climax", slide_07, "p02-home-full-body.jpg"),
    ("08-close", slide_08, "p07-portrait.jpg"),
]


def subject_overlap(img_mask, boxes):
    """Share of text-box pixels that sit on the subject (mask > 0.5)."""
    m = np.asarray(img_mask, dtype=np.float32) / 255.0 > 0.5
    hits = total = 0
    for x0, y0, x1, y1 in boxes:
        x0, y0, x1, y1 = (max(0, int(v)) for v in (x0, y0, x1, y1))
        region = m[y0:y1, x0:x1]
        hits += region.sum()
        total += region.size
    return hits / max(total, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="path to selfie_multiclass_256x256.tflite")
    args = ap.parse_args()
    seg = Segmenter(args.model)

    files = []
    for i, (name, build, _) in enumerate(SLIDES, 1):
        img, block = build(seg)
        overlap = subject_overlap(seg.person(img), block.boxes)
        furniture(img, i)
        img = grain(img, seed=i)
        path = OUT / f"{name}.png"
        img.save(path, optimize=True)
        files.append(path)
        print(f"{name}: text-on-subject {overlap:.1%}, text bottom y={block.y}")

    thumbs = [Image.open(p).resize((360, 450), Image.LANCZOS) for p in files]
    sheet = Image.new("RGB", (4 * 360 + 5 * 20, 2 * 450 + 3 * 20), CHAR)
    for k, t in enumerate(thumbs):
        sheet.paste(t, (20 + (k % 4) * 380, 20 + (k // 4) * 470))
    sheet.save(OUT / "preview.jpg", quality=90)

    with zipfile.ZipFile(OUT / "final-carousel.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.name)
        for extra in ("caption.txt", "copy.txt"):
            if (OUT / extra).exists():
                z.write(OUT / extra, extra)


if __name__ == "__main__":
    main()
