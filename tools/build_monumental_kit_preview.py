"""Render the Monumental kit palette and type specimen (brand/monumental/kit-preview.png)."""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "brand/monumental/tokens.json").read_text())
C = TOKENS["colors"]
W, H = 1080, 1350
OUT = ROOT / "brand/monumental/kit-preview.png"


def font(key, size):
    return ImageFont.truetype(str(ROOT / TOKENS["fonts"][key]), size)


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def backdrop():
    # Placeholder atmosphere: charcoal base, warm practical light upper-right, cool shadow lower-left.
    img = Image.new("RGB", (W, H), hex_rgb(C["charcoal"]))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((560, -220, 1380, 700), fill=(120, 86, 40))
    g.ellipse((-400, 900, 500, 1700), fill=hex_rgb(C["storm_teal_optional"]))
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.blend(img, glow, 0.55)
    # Doorway silhouette as the one symbolic element.
    d = ImageDraw.Draw(img)
    d.rectangle((800, 420, 1030, 1180), fill=(26, 22, 17))
    d.rectangle((826, 450, 1004, 1180), fill=(70, 52, 28))
    light = Image.new("L", (W, H), 0)
    ImageDraw.Draw(light).polygon([(826, 1180), (1004, 1180), (1080, 1350), (700, 1350)], fill=90)
    light = light.filter(ImageFilter.GaussianBlur(30))
    img.paste((120, 92, 52), (0, 0), light)
    # Feathered readability scrim behind the text column.
    scrim = Image.new("L", (W, H), 0)
    ImageDraw.Draw(scrim).rectangle((0, 0, 640, H), fill=170)
    scrim = scrim.filter(ImageFilter.GaussianBlur(90))
    img.paste(hex_rgb(C["charcoal"]), (0, 0), scrim)
    # Fine grain, applied last.
    rnd = random.Random(7)
    noise = Image.new("L", (W, H))
    noise.putdata([128 + rnd.randint(-10, 10) for _ in range(W * H)])
    return Image.blend(img, Image.merge("RGB", (noise,) * 3), 0.04)


def tracked(draw, xy, text, fnt, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def main():
    img = backdrop()
    d = ImageDraw.Draw(img)
    bone, gold, stone = hex_rgb(C["bone"]), hex_rgb(C["antique_gold"]), hex_rgb(C["stone"])

    tracked(d, (80, 92), "SECOND BRAND KIT  ·  MONUMENTAL V1.0", font("utility", 20), gold, 3)

    head = font("headline_default", 104)
    y = 170
    for line, colour in (("BECOME", bone), ("SOMEONE", bone), ("YOUR GOALS", gold), ("CAN TRUST.", bone)):
        d.text((80, y), line, font=head, fill=colour)
        bottom = y + head.getbbox(line)[3]
        y += 104
    y = bottom + 36
    d.line((80, y, 160, y), fill=gold, width=2)
    y += 32
    body = font("body", 32)
    for line in ("Small promises, kept daily.", "That is how self-trust is built."):
        d.text((80, y), line, font=body, fill=bone)
        y += int(32 * 1.35)

    y += 44
    tracked(d, (80, y), "CONDENSED VARIANT", font("utility", 18), stone, 3)
    y += 34
    d.text((80, y), "MOTIVATION STARTS.", font=font("headline_condensed_variant", 64), fill=bone)
    y += 70
    d.text((80, y), "DISCIPLINE FINISHES.", font=font("headline_condensed_variant", 64), fill=gold)

    # Palette swatches.
    y = 1030
    tracked(d, (80, y), "PALETTE", font("utility", 18), stone, 3)
    labels = font("utility", 15)
    x = 80
    for name in ("charcoal", "ink", "bone", "antique_gold", "light_gold", "stone", "storm_teal_optional"):
        d.rectangle((x, y + 34, x + 112, y + 96), fill=hex_rgb(C[name]), outline=(60, 56, 50))
        d.text((x, y + 104), C[name], font=labels, fill=stone)
        x += 126

    # Lower-left monogram, gold rule, lower-right footer and folio.
    mono = Image.open(ROOT / TOKENS["logo"]["compact"]).convert("RGBA").resize((64, 64), Image.LANCZOS)
    img.paste(mono, (80, 1206), mono)
    rule_end = 1000 - sum(d.textlength(ch, font=font("utility", 18)) + 2 for ch in "DISCIPLINE · ACCOUNTABILITY · CONSISTENCY  ·  01/09") - 24
    d.line((166, 1254, rule_end, 1254), fill=gold, width=1)
    foot = font("utility", 18)
    text = "DISCIPLINE · ACCOUNTABILITY · CONSISTENCY  ·  01/09"
    width = sum(d.textlength(ch, font=foot) + 2 for ch in text)
    tracked(d, (1000 - width, 1244), text, foot, stone, 2)

    img.save(OUT, optimize=True)
    print(OUT, img.size)


if __name__ == "__main__":
    main()
