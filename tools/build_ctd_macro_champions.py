#!/usr/bin/env python3
"""Build the four-slide CTD macro champions carousel."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/ctd-macro-champions"
SRC = OUT / "source-images"
W, H = 1080, 1350

HEAD = ROOT / "brand/fonts/BarlowCondensed-ExtraBold.ttf"
BODY = ROOT / "brand/fonts/Montserrat-Bold.ttf"
MEDIUM = ROOT / "brand/fonts/Montserrat-Medium.ttf"
LOGO = OUT / "ctd-cinematic-logo.png"

INK = "#10130F"
GOLD = "#C69616"
CRIMSON = "#9A271B"
CREAM = "#F6EFE2"
MUTED = "#5A554C"


def f(path, size):
    return ImageFont.truetype(str(path), size)


F = {
    "headline": f(HEAD, 94),
    "sub": f(BODY, 28),
    "note": f(MEDIUM, 22),
    "value": f(HEAD, 51),
    "label": f(HEAD, 27),
    "footer": f(BODY, 16),
    "plate_head": f(HEAD, 88),
    "plate_body": f(BODY, 28),
    "plate_small": f(MEDIUM, 22),
}


def fit_background(path):
    im = Image.open(path).convert("RGB")
    ratio = max(W / im.width, H / im.height)
    size = (round(im.width * ratio), round(im.height * ratio))
    im = im.resize(size, Image.Resampling.LANCZOS)
    left = (im.width - W) // 2
    top = (im.height - H) // 2
    return im.crop((left, top, left + W, top + H))


logo = Image.open(LOGO).convert("RGBA")
logo.thumbnail((92, 92), Image.Resampling.LANCZOS)


def text_center(d, xy, text, font, fill, **kwargs):
    d.text(xy, text, font=font, fill=fill, anchor="mm", **kwargs)


def common_header(im, number, headline, subtitle, note):
    d = ImageDraw.Draw(im)
    im.paste(logo, (40, 28), logo)
    d.text((142, 44), "CUTTHROAT", font=F["sub"], fill=INK)
    d.text((142, 76), "DISCIPLINE", font=F["sub"], fill=GOLD)
    d.rounded_rectangle((970, 36, 1040, 98), radius=28, fill=INK)
    text_center(d, (1005, 67), f"{number}/4", F["note"], CREAM)
    text_center(d, (W//2, 162), headline, F["headline"], INK, spacing=-6)
    d.line((72, 265, 235, 265), fill=GOLD, width=4)
    d.line((845, 265, 1008, 265), fill=GOLD, width=4)
    text_center(d, (W//2, 265), subtitle, F["sub"], CRIMSON)
    text_center(d, (W//2, 310), note, F["note"], MUTED)


def footer(im):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1286, W, H), fill=INK)
    text_center(d, (W//2, 1318), "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", F["footer"], CREAM)


def nutrition_slide(source, number, headline, subtitle, note, values, labels, value_ys):
    im = fit_background(source)
    d = ImageDraw.Draw(im)
    common_header(im, number, headline, subtitle, note)
    xs = [110, 325, 540, 755, 970]
    for x, value, label, y in zip(xs, values, labels, value_ys):
        text_center(d, (x, y), value, F["value"], CRIMSON)
        lines = label.split("\n")
        for i, line in enumerate(lines):
            text_center(d, (x, 1222 + i*26), line, F["label"], INK)
    footer(im)
    return im


def plate_slide(source):
    im = fit_background(source)
    d = ImageDraw.Draw(im)
    im.paste(logo, (40, 28), logo)
    d.text((142, 44), "CUTTHROAT", font=F["sub"], fill=INK)
    d.text((142, 76), "DISCIPLINE", font=F["sub"], fill=GOLD)
    d.rounded_rectangle((970, 36, 1040, 98), radius=28, fill=INK)
    text_center(d, (1005, 67), "4/4", F["note"], CREAM)
    d.text((62, 170), "BUILD A PLATE", font=F["plate_head"], fill=INK)
    d.text((62, 252), "THAT WORKS.", font=F["plate_head"], fill=GOLD)
    d.text((66, 370), "1/2", font=F["value"], fill=GOLD)
    d.text((160, 380), "VEGETABLES + FRUIT", font=F["plate_body"], fill=INK)
    d.text((66, 445), "1/4", font=F["value"], fill=GOLD)
    d.text((160, 455), "LEAN PROTEIN", font=F["plate_body"], fill=INK)
    d.text((66, 520), "1/4", font=F["value"], fill=GOLD)
    d.text((160, 530), "CARBOHYDRATES", font=F["plate_body"], fill=INK)
    d.rounded_rectangle((60, 620, 505, 785), radius=18, fill=(16, 19, 15, 232))
    d.text((90, 650), "PROTEIN ANCHORS.", font=F["sub"], fill=CREAM)
    d.text((90, 695), "CARBS FUEL.", font=F["sub"], fill=GOLD)
    d.text((90, 740), "FIBER FILLS.", font=F["sub"], fill=CREAM)
    d.text((64, 850), "Adjust portions to your calories,", font=F["plate_small"], fill=MUTED)
    d.text((64, 885), "training and progress—not someone else's plate.", font=F["plate_small"], fill=MUTED)
    footer(im)
    return im


def build():
    slides = [
        nutrition_slide(
            SRC / "01-protein.png", 1, "PROTEIN CHAMPIONS", "NO POWDER REQUIRED",
            "Approx. protein per 100g • cooked, drained or as served",
            ["31g", "26g", "26g", "13g", "11g"],
            ["CHICKEN\nBREAST", "CANNED\nTUNA", "LEAN\nBEEF", "EGGS", "COTTAGE\nCHEESE"],
            [535, 550, 540, 615, 700],
        ),
        nutrition_slide(
            SRC / "02-carbs.png", 2, "CARB CHAMPIONS", "TRAINING FUEL, NOT THE ENEMY",
            "Approx. carbohydrate per 100g • preparation matters",
            ["68g", "31g", "28g", "23g", "21g"],
            ["OATS\nDRY", "PASTA\nCOOKED", "WHITE RICE\nCOOKED", "BANANA", "POTATO\nBAKED"],
            [470, 490, 495, 510, 520],
        ),
        nutrition_slide(
            SRC / "03-fiber.png", 3, "FIBER CHAMPIONS", "FULLER MEALS. BETTER DIGESTION.",
            "Approx. fiber per 100g • cooked or raw as labeled",
            ["9g", "8g", "7g", "7g", "3g"],
            ["BLACK BEANS\nCOOKED", "LENTILS\nCOOKED", "AVOCADO\nRAW", "RASPBERRIES\nRAW", "BROCCOLI\nCOOKED"],
            [540, 555, 500, 550, 560],
        ),
        plate_slide(SRC / "04-plate.png"),
    ]
    names = ["01-protein-champions.png", "02-carb-champions.png", "03-fiber-champions.png", "04-build-your-plate.png"]
    for name, slide in zip(names, slides):
        slide.save(OUT / name, optimize=True)
    # compact horizontal review sheet
    overview = Image.new("RGB", (1080, 338), "#111111")
    for i, slide in enumerate(slides):
        thumb = slide.resize((270, 338), Image.Resampling.LANCZOS)
        overview.paste(thumb, (i*270, 0))
    overview.save(OUT / "overview.jpg", quality=90)
    slides[0].save(OUT / "preview.png", optimize=True)
    with ZipFile(OUT / "final-carousel.zip", "w", ZIP_DEFLATED) as z:
        for name in names:
            z.write(OUT / name, name)
        z.write(OUT / "caption.txt", "caption.txt")
        z.write(OUT / "nutrition-notes.md", "nutrition-notes.md")


if __name__ == "__main__":
    build()
