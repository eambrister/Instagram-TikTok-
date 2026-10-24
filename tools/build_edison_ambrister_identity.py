#!/usr/bin/env python3
"""Build the Edison Ambrister personal-brand logo system."""

from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "brand/assets/edison-ambrister"
FONT_DIR = ROOT / "brand/fonts"
HEAD = FONT_DIR / "BarlowCondensed-ExtraBold.ttf"
BODY = FONT_DIR / "Montserrat-Bold.ttf"

GOLD = "#D6A918"
PALE_GOLD = "#F3D878"
SILVER = "#AAB0B9"
WHITE = "#F3F0E9"
CRIMSON = "#981B2E"
BLACK = "#07080A"


def svg_shell(width, height, body, background="none"):
    bg = "" if background == "none" else f'<rect width="100%" height="100%" fill="{background}"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    @font-face {{ font-family: BarlowCTD; src: url("{HEAD.as_uri()}"); font-weight: 800; }}
    @font-face {{ font-family: MontserratCTD; src: url("{BODY.as_uri()}"); font-weight: 700; }}
    .head {{ font-family: BarlowCTD, 'Arial Narrow', sans-serif; font-weight: 800; }}
    .body {{ font-family: MontserratCTD, Arial, sans-serif; font-weight: 700; }}
  </style>
  {bg}
  {body}
</svg>'''


def monogram_group(x=0, y=0, scale=1):
    return f'''
  <g transform="translate({x} {y}) scale({scale})">
    <circle cx="500" cy="500" r="430" fill="none" stroke="{GOLD}" stroke-width="28"/>
    <circle cx="500" cy="500" r="392" fill="none" stroke="{PALE_GOLD}" stroke-width="5" opacity="0.8"/>
    <circle cx="500" cy="500" r="355" fill="{BLACK}" fill-opacity="0.88" stroke="{SILVER}" stroke-width="4" opacity="0.98"/>
    <text x="238" y="675" class="head" font-size="540" fill="{SILVER}" stroke="{WHITE}" stroke-width="3">E</text>
    <text x="475" y="675" class="head" font-size="540" fill="{GOLD}" stroke="{PALE_GOLD}" stroke-width="3">A</text>
    <path d="M475 760 L660 225 L710 225 L525 760 Z" fill="{CRIMSON}"/>
    <path d="M494 740 L665 245" stroke="{PALE_GOLD}" stroke-width="9" opacity="0.85"/>
  </g>'''


def write_svg(name, content):
    path = OUT / name
    path.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n")
    return path


def export(svg, png, width, height):
    subprocess.run([
        "inkscape", str(svg), "--export-type=png", f"--export-filename={png}",
        f"--export-width={width}", f"--export-height={height}", "--export-background-opacity=0"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build():
    OUT.mkdir(parents=True, exist_ok=True)

    emblem = svg_shell(1000, 1000, monogram_group())
    emblem_svg = write_svg("ea-monogram.svg", emblem)
    export(emblem_svg, OUT / "ea-monogram.png", 1200, 1200)

    horizontal_body = f'''
  {monogram_group(20, 10, 0.52)}
  <text x="570" y="250" class="head" font-size="190" letter-spacing="4" fill="{WHITE}">EDISON</text>
  <text x="570" y="435" class="head" font-size="190" letter-spacing="3" fill="{GOLD}">AMBRISTER</text>
  <rect x="575" y="485" width="1135" height="10" fill="{CRIMSON}"/>
  <text x="575" y="550" class="body" font-size="31" letter-spacing="4" fill="{SILVER}">DISCIPLINE  •  ACCOUNTABILITY  •  CONSISTENCY</text>
  '''
    horizontal_svg = write_svg("edison-ambrister-horizontal.svg", svg_shell(1800, 640, horizontal_body))
    export(horizontal_svg, OUT / "edison-ambrister-horizontal.png", 1800, 640)

    stacked_body = f'''
  {monogram_group(210, 10, 0.78)}
  <text x="600" y="870" text-anchor="middle" class="head" font-size="150" letter-spacing="4" fill="{WHITE}">EDISON</text>
  <text x="600" y="1015" text-anchor="middle" class="head" font-size="150" letter-spacing="3" fill="{GOLD}">AMBRISTER</text>
  <rect x="230" y="1055" width="740" height="9" fill="{CRIMSON}"/>
  <text x="600" y="1125" text-anchor="middle" class="body" font-size="27" letter-spacing="3" fill="{SILVER}">DISCIPLINE  •  ACCOUNTABILITY  •  CONSISTENCY</text>
  '''
    stacked_svg = write_svg("edison-ambrister-stacked.svg", svg_shell(1200, 1200, stacked_body))
    export(stacked_svg, OUT / "edison-ambrister-stacked.png", 1200, 1200)

    avatar_body = monogram_group(0, 0, 1)
    avatar_svg = write_svg("edison-ambrister-profile.svg", svg_shell(1000, 1000, avatar_body, BLACK))
    export(avatar_svg, OUT / "edison-ambrister-profile.png", 1080, 1080)

    preview = Image.new("RGB", (1600, 1000), BLACK)
    horizontal = Image.open(OUT / "edison-ambrister-horizontal.png").convert("RGBA")
    horizontal.thumbnail((1450, 510), Image.Resampling.LANCZOS)
    preview.paste(horizontal, ((1600-horizontal.width)//2, 45), horizontal)
    emblem_png = Image.open(OUT / "ea-monogram.png").convert("RGBA")
    emblem_png.thumbnail((330, 330), Image.Resampling.LANCZOS)
    preview.paste(emblem_png, (150, 575), emblem_png)
    stacked_png = Image.open(OUT / "edison-ambrister-stacked.png").convert("RGBA")
    stacked_png.thumbnail((380, 380), Image.Resampling.LANCZOS)
    preview.paste(stacked_png, (610, 555), stacked_png)
    profile_png = Image.open(OUT / "edison-ambrister-profile.png").convert("RGBA")
    profile_png.thumbnail((330, 330), Image.Resampling.LANCZOS)
    preview.paste(profile_png, (1120, 575), profile_png)
    label_font = ImageFont.truetype(str(BODY), 24)
    pd = ImageDraw.Draw(preview)
    pd.text((315, 970), "MONOGRAM", font=label_font, fill=SILVER, anchor="mm")
    pd.text((800, 970), "STACKED LOCKUP", font=label_font, fill=SILVER, anchor="mm")
    pd.text((1285, 970), "PROFILE MARK", font=label_font, fill=SILVER, anchor="mm")
    preview.save(OUT / "identity-preview.jpg", quality=94)


if __name__ == "__main__":
    build()
