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
from fontTools.ttLib import TTFont

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
HEAD_FONT = ROOT / "brand/fonts/BarlowCondensed-ExtraBold.ttf"
HEAD_METRICS = TTFont(HEAD_FONT)

slides = [
    {"slug":"hook", "start":285, "lines":[
        ("YOU KEEP SAYING", WHITE, 124, 4), ("TOMORROW.", GOLD, 190, 78),
        ("HOW MANY", GOLD, 174, 0), ("TOMORROWS", WHITE, 166, 0),
        ("DO YOU NEED?", WHITE, 150, 0)]},
    {"slug":"false-progress", "start":280, "lines":[
        ("TALKING ABOUT IT", WHITE, 120, 0), ("MAKES YOU FEEL", WHITE, 126, 0),
        ("PRODUCTIVE.", WHITE, 165, 78), ("IT ISN'T", GOLD, 194, 0),
        ("PROGRESS.", GOLD, 202, 0)]},
    {"slug":"contrast", "start":305, "lines":[
        ("TALKERS", WHITE, 205, 0), ("ANNOUNCE.", WHITE, 176, 100),
        ("DOERS", GOLD, 224, 0), ("EXECUTE.", GOLD, 192, 0)]},
    {"slug":"excuse", "start":275, "lines":[
        ("“I'LL START", SILVER, 158, 0), ("TOMORROW”", SILVER, 184, 48),
        ("IS USUALLY ANOTHER WAY OF SAYING:", SILVER, 27, 54, "body"),
        ("“I DON'T WANT", WHITE, 132, 0), ("TO BE", WHITE, 136, 0),
        ("UNCOMFORTABLE", GOLD, 139, 0), ("TODAY.”", GOLD, 192, 0)]},
    {"slug":"accountability", "start":270, "lines":[
        ("YOUR GOAL", WHITE, 160, 0), ("ISN'T CONFUSED.", WHITE, 142, 62),
        ("YOU KNOW", WHITE, 160, 0), ("WHAT TO DO.", WHITE, 155, 62),
        ("YOU KEEP", WHITE, 150, 0), ("AVOIDING IT.", GOLD, 170, 0)]},
    {"slug":"evidence", "start":285, "lines":[
        ("WANTING IT", WHITE, 160, 0), ("EARNS YOU", WHITE, 170, 0),
        ("NOTHING.", GOLD, 205, 92), ("COMPLETED WORK", WHITE, 132, 0),
        ("IS THE RECEIPT.", GOLD, 145, 0)]},
    {"slug":"quiet-execution", "start":285, "lines":[
        ("STOP", WHITE, 222, 0), ("ANNOUNCING", WHITE, 164, 0),
        ("THE PLAN.", WHITE, 181, 110), ("BUILD THE", GOLD, 180, 0),
        ("EVIDENCE.", GOLD, 200, 0)]},
    {"slug":"immediate-action", "start":330, "lines":[
        ("CLOSE", WHITE, 213, 0), ("THIS POST.", WHITE, 184, 58),
        ("DO ONE THING", WHITE, 150, 0), ("RIGHT NOW.", GOLD, 185, 46),
        ("10 SQUATS  •  10-MINUTE WALK", SILVER, 26, 11, "body"),
        ("PREP ONE MEAL", SILVER, 26, 44, "body"),
        ("PICK ONE. FINISH IT.", GOLD, 42, 0, "body-bold")]},
]

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

def head_width(value, size):
    cmap = HEAD_METRICS.getBestCmap()
    total = sum(HEAD_METRICS["hmtx"][cmap.get(ord(ch), ".notdef")][0] for ch in value)
    return total / HEAD_METRICS["head"].unitsPerEm * size

def fit_head(value, preferred, maximum=948):
    size = preferred
    while head_width(value, size) > maximum and size > 72:
        size -= 1
    return size

def svg(number, slide):
    slug = slide["slug"]
    x = 66
    blocks = []
    y = slide["start"]
    rendered_lines = []
    prepared = []
    for spec in slide["lines"]:
        value, color, preferred, gap = spec[:4]
        kind = spec[4] if len(spec) > 4 else "head"
        if kind == "head":
            size = fit_head(value, preferred)
        else:
            size = preferred
        prepared.append((value, color, size, gap, kind))
    for index, (value, color, size, gap, kind) in enumerate(prepared):
        if kind == "head":
            blocks.append(text(x, y, value, size, color, HEAD, 800, tracking=-.8))
        else:
            weight = 700 if kind == "body-bold" else 600
            blocks.append(text(x, y, value, size, color, BODY, weight, tracking=.2))
        rendered_lines.append(value)
        if index < len(prepared) - 1:
            next_size = prepared[index + 1][2]
            if kind.startswith("body") and prepared[index + 1][4].startswith("body"):
                advance = max(size, next_size) * 1.45
            else:
                advance = max(size, next_size) * .82
            y += advance + gap
    accent_x1, accent_x2 = 66, 350
    number_outline = text(540, 760, f"{number:02d}", 690, "#FFFFFF", HEAD, 800,
                          "middle", -16, .025)
    # Slide-specific large typographic shapes. All are text/vector only.
    motifs = {
        1: '<path d="M66 205 H1014" stroke="#D6A928" stroke-width="2"/><path d="M66 215 H320" stroke="#8D1721" stroke-width="7"/>',
        2: '<path d="M66 720 H1014" stroke="#D6A928" stroke-width="2"/><path d="M66 732 H430" stroke="#8D1721" stroke-width="6"/>',
        3: '<path d="M66 680 H1014" stroke="#D6A928" stroke-width="2"/><rect x="66" y="690" width="150" height="7" fill="#8D1721"/>',
        4: '<text x="944" y="515" fill="#AEB3BA" fill-opacity=".06" font-family="Barlow Condensed" font-size="430" font-weight="800" text-anchor="end">“</text>',
        5: '<path d="M66 1132 H590" stroke="#8D1721" stroke-width="8"/><path d="M600 1132 H1014" stroke="#D6A928" stroke-width="2"/>',
        6: '<g fill="none" stroke="#D6A928" opacity=".18"><rect x="690" y="750" width="320" height="145"/><rect x="650" y="710" width="320" height="145"/><rect x="610" y="670" width="320" height="145"/></g>',
        7: '<g fill="none" stroke="#D6A928" opacity=".18"><rect x="690" y="815" width="320" height="140"/><rect x="650" y="775" width="320" height="140"/><rect x="610" y="735" width="320" height="140"/></g>',
        8: '<path d="M66 1000 H1014" stroke="#D6A928" stroke-width="2"/><path d="M66 1011 H270" stroke="#8D1721" stroke-width="7"/>',
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
    return "\n".join(body), rendered_lines

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
        for number, slide in enumerate(slides, 1):
            slug = slide["slug"]
            stem = f"{number:02d}-{slug}"
            svg_path = OUT / f"{stem}.svg"
            png_path = OUT / f"{stem}.png"
            artwork, rendered_lines = svg(number, slide)
            svg_path.write_text(artwork, encoding="utf-8")
            subprocess.run(["inkscape", str(svg_path), "--export-type=png", "--export-filename", str(png_path),
                            "--export-width=1080", "--export-height=1350"], check=True, env=env)
            pngs.append(png_path)
            copy.extend([f"SLIDE {number}", *rendered_lines])
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
