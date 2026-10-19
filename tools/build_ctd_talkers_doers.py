#!/usr/bin/env python3
"""Build the CUTTHROAT DISCIPLINE Talkers vs Doers typography carousel."""
from pathlib import Path
from base64 import b64encode
from zipfile import ZipFile, ZIP_DEFLATED
import html
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/ctd-talkers-vs-doers"
LOGO = ROOT / "outputs/ctd-why-routine-matters/ctd-cinematic-logo.png"
W, H = 1080, 1350

BLACK = "#090A0C"
CHARCOAL = "#15171B"
WHITE = "#F3EFE6"
SILVER = "#AEB3BA"
GOLD = "#D6A928"
GOLD_HI = "#F1CF63"
CRIMSON = "#8D1721"
HEAD = "Barlow Condensed"
BODY = "Montserrat"

slides = [
    ("hook", ["STOP", "SAYING", "TOMORROW.", "START", "TODAY."], "", ""),
    ("talkers", ["TALKERS", "ANNOUNCE.", "DOERS", "EXECUTE."], "", ""),
    ("avoidance", ["YOUR GOAL", "ISN'T", "CONFUSED.", "YOU KEEP", "DODGING IT."], "", ""),
    ("tomorrow", ["TOMORROW", "IS WHERE", "EXCUSES", "GO TO", "SURVIVE."], "", ""),
    ("intention", ["WANTING IT", "EARNS YOU", "NOTHING.", "WORK", "DOES."], "", ""),
    ("start", ["SERIOUS", "PEOPLE", "START", "BEFORE THEY", "FEEL READY."], "", ""),
    ("quiet", ["QUIET", "WORK.", "LOUD", "RESULTS."], "", ""),
    ("command", ["CLOSE", "THIS POST.", "DO ONE", "THING.", "NOW."], "", ""),
]

GOLD_LINES = {"TOMORROW.", "TODAY.", "DOERS", "EXECUTE.", "DODGING IT.",
              "SURVIVE.", "NOTHING.", "DOES.", "START", "FEEL READY.",
              "RESULTS.", "NOW."}

def esc(value):
    return html.escape(str(value), quote=True)

def uri(path):
    return "data:image/png;base64," + b64encode(path.read_bytes()).decode("ascii")

def text(x, y, value, size, color=WHITE, family=HEAD, weight=800,
         anchor="start", tracking=0, opacity=1, text_length=None):
    length = (f' textLength="{text_length}" lengthAdjust="spacingAndGlyphs"'
              if text_length else "")
    return (f'<text x="{x}" y="{y}" fill="{color}" fill-opacity="{opacity}" '
            f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" letter-spacing="{tracking}"{length}>{esc(value)}</text>')

def svg(number, slug, headline, strike, support):
    # Alternating alignment creates controlled aggression without sacrificing hierarchy.
    right = number in (2, 4, 6)
    anchor = "end" if right else "start"
    x = 1014 if right else 66
    if number == 8:
        x = 82
    top = 325
    bottom = 1115
    lead = (bottom - top) / max(1, len(headline)-1)
    blocks = []
    for index, line in enumerate(headline):
        color = GOLD if line in GOLD_LINES else WHITE
        target_width = min(948, max(610, len(line) * 66))
        blocks.append(text(x, top + index*lead, line, 190, color, anchor=anchor,
                           tracking=-1.5, text_length=target_width))
    accent_x1, accent_x2 = (730, 1014) if right else (66, 350)
    number_outline = text(540, 760, f"{number:02d}", 690, "#FFFFFF", HEAD, 800,
                          "middle", -16, .025)
    # Slide-specific large typographic shapes. All are text/vector only.
    motifs = {
        1: '<path d="M66 208 H1014" stroke="#D6A928" stroke-width="2"/><path d="M66 218 H520" stroke="#8D1721" stroke-width="10"/>',
        2: '<text x="50" y="1110" fill="#8D1721" fill-opacity=".2" font-family="Barlow Condensed" font-size="410" font-weight="800">DO</text>',
        3: '<path d="M900 170 L180 1040" stroke="#8D1721" stroke-width="24" stroke-opacity=".22"/>',
        4: '<g opacity=".18" stroke="#D6A928" fill="none"><circle cx="185" cy="965" r="105" stroke-width="3"/><path d="M185 965 L185 894 M185 965 L244 1000" stroke-width="8"/></g>',
        5: '<path d="M70 660 H1010" stroke="#8D1721" stroke-width="18" opacity=".32"/>',
        6: '<path d="M70 1025 H1010" stroke="#D6A928" stroke-width="3"/><path d="M960 995 L1010 1025 L960 1055" fill="none" stroke="#D6A928" stroke-width="3"/>',
        7: '<g fill="none" stroke="#D6A928" opacity=".2"><rect x="690" y="760" width="320" height="155"/><rect x="645" y="715" width="320" height="155"/><rect x="600" y="670" width="320" height="155"/></g>',
        8: '<rect x="65" y="175" width="950" height="985" fill="none" stroke="#D6A928" stroke-width="3"/>',
    }[number]
    body = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">',
        '<defs>',
        '<radialGradient id="bg" cx="50%" cy="12%" r="105%"><stop stop-color="#24272C"/><stop offset=".5" stop-color="#101216"/><stop offset="1" stop-color="#07080A"/></radialGradient>',
        '<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F1CF63"/><stop offset=".45" stop-color="#D6A928"/><stop offset="1" stop-color="#8B6514"/></linearGradient>',
        '<filter id="grain"><feTurbulence baseFrequency=".72" numOctaves="4" seed="'+str(30+number)+'"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .07"/></feComponentTransfer></filter>',
        '</defs>',
        '<rect width="1080" height="1350" fill="url(#bg)"/>',
        '<rect width="1080" height="1350" filter="url(#grain)" opacity=".42"/>',
        f'<rect x="24" y="24" width="1032" height="1302" fill="none" stroke="#4B4E54" stroke-width="1"/>',
        number_outline, motifs,
        f'<image href="{uri(LOGO)}" x="56" y="48" width="82" height="82" preserveAspectRatio="xMidYMid meet"/>',
        text(154, 78, "CUTTHROAT", 18, WHITE, BODY, 700, tracking=2),
        text(154, 104, "DISCIPLINE", 18, SILVER, BODY, 700, tracking=2),
        text(1018, 84, f"{number:02d} / 08", 18, SILVER, BODY, 700, "end", 1.6),
        '<path d="M66 150 H1014" stroke="#464950" stroke-width="1"/>',
        f'<path d="M{accent_x1} 150 H{accent_x2}" stroke="#D6A928" stroke-width="5"/>',
        *blocks,
    ]
    body.extend([
        '<path d="M66 1268 H1014" stroke="#464950" stroke-width="1"/>',
        text(540, 1307, "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", 15, SILVER, BODY, 700, "middle", 1.5),
        '</svg>'
    ])
    return "\n".join(body)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pngs = []
    copy = []
    with tempfile.TemporaryDirectory(prefix="ctd-talkers-") as temp_name:
        temp = Path(temp_name)
        cache = temp / "font-cache"
        profile = temp / "inkscape"
        cache.mkdir()
        profile.mkdir()
        config = temp / "fonts.conf"
        config.write_text(
            '<?xml version="1.0"?><fontconfig>'
            f'<dir>{ROOT / "brand/fonts"}</dir><cachedir>{cache}</cachedir>'
            '<config><rescan><int>0</int></rescan></config></fontconfig>',
            encoding="utf-8")
        env = dict(os.environ)
        env.update(FONTCONFIG_FILE=str(config), XDG_CACHE_HOME=str(cache),
                   INKSCAPE_PROFILE_DIR=str(profile))
        for number, (slug, headline, strike, support) in enumerate(slides, 1):
            stem = f"{number:02d}-{slug}"
            svg_path = OUT / f"{stem}.svg"
            png_path = OUT / f"{stem}.png"
            svg_path.write_text(svg(number, slug, headline, strike, support), encoding="utf-8")
            subprocess.run(["inkscape", str(svg_path), "--export-type=png", "--export-filename", str(png_path),
                            "--export-width=1080", "--export-height=1350"], check=True, env=env)
            pngs.append(png_path)
            copy.extend([f"SLIDE {number}", *headline])
            if strike:
                copy.append(strike)
            if support:
                copy.append(support)
            copy.append("")
    (OUT / "copy.txt").write_text("\n".join(copy).rstrip() + "\n", encoding="utf-8")
    subprocess.run(["montage", *map(str, pngs), "-thumbnail", "270x338", "-tile", "4x2",
                    "-geometry", "+12+12", "-background", "#090A0C", str(OUT / "overview.jpg")], check=True)
    shutil.copyfile(pngs[0], OUT / "preview.png")
    package = [*pngs, OUT / "caption.txt", OUT / "copy.txt", OUT / "alt-text.txt",
               OUT / "production-notes.txt", OUT / "README.md", OUT / "preview.png", OUT / "overview.jpg"]
    with ZipFile(OUT / "final-carousel.zip", "w", ZIP_DEFLATED, compresslevel=6) as archive:
        for path in package:
            archive.write(path, path.name)

if __name__ == "__main__":
    main()
