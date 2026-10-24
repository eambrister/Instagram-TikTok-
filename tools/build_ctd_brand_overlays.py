#!/usr/bin/env python3
"""Create reusable transparent Edison Ambrister overlays for posts and Reels."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "brand"
OUT = BRAND / "templates"
LOGO = BRAND / "assets/edison-ambrister/edison-ambrister-horizontal.png"
FONT = BRAND / "fonts/Montserrat-Bold.ttf"
SILVER = "#AAB0B9"
GOLD = "#D6A918"
FOOTER = "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY"


def make(size, reel=False):
    w, h = size
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    logo = Image.open(LOGO).convert("RGBA")
    max_width = 360 if reel else 315
    logo.thumbnail((max_width, 128 if reel else 112), Image.Resampling.LANCZOS)
    margin = 48 if reel else 46
    im.alpha_composite(logo, (margin, 34 if reel else 28))
    font = ImageFont.truetype(str(FONT), 18 if reel else 16)
    if not reel:
        d.line((margin, h-72, w-margin, h-72), fill=SILVER, width=2)
        d.text((w//2, h-38), FOOTER, font=font, fill=SILVER, anchor="mm")
    else:
        # Subtle safe-area guides are provided in a separate guide image, not the publishing overlay.
        pass
    return im


def guide(size, reel=False):
    im = Image.new("RGBA", size, (7, 8, 10, 255))
    d = ImageDraw.Draw(im)
    w, h = size
    margin = 48 if reel else 46
    d.rectangle((margin, margin, w-margin, h-margin), outline=(214, 169, 24, 210), width=3)
    if reel:
        d.rectangle((margin, 250, w-margin, 1580), outline=(170, 176, 185, 220), width=3)
        d.rectangle((0, 1580, w, h), fill=(152, 27, 46, 80))
        d.text((w//2, 1750), "INSTAGRAM INTERFACE-RISK AREA", font=ImageFont.truetype(str(FONT), 26), fill="#F3F0E9", anchor="mm")
    else:
        d.line((margin, 160, w-margin, 160), fill=SILVER, width=2)
        d.line((margin, 1278, w-margin, 1278), fill=SILVER, width=2)
    return im


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    make((1080, 1350)).save(OUT / "edison-ambrister-post-overlay-1080x1350.png")
    make((1080, 1920), True).save(OUT / "edison-ambrister-reel-overlay-1080x1920.png")
    guide((1080, 1350)).save(OUT / "post-safe-area-guide-1080x1350.png")
    guide((1080, 1920), True).save(OUT / "reel-safe-area-guide-1080x1920.png")


if __name__ == "__main__":
    build()
