#!/usr/bin/env python3
"""Typeset the eight-slide burpees campaign and render 1080 × 1350 PNGs.

Usage: python3 tools/build_ctd_burpees.py [--output PATH] [--svg-only]

Requires Inkscape, ImageMagick's montage, and fontTools. Inputs are content.json,
scene-assets/01-scene.png through 08-scene.png, the canonical CTD logo, and the
licensed open font substitutes in brand/fonts. No scenes are generated here.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "brand/fonts"
DEFAULT_OUT = ROOT / "outputs/ctd-burpees"
CANONICAL_LOGO = ROOT / "outputs/ctd-why-routine-matters/ctd-cinematic-logo.png"
WIDTH, HEIGHT = 1080, 1350
MARGIN = 64
TEXT_WIDTH = WIDTH - MARGIN * 2
INK = "#101114"
WHITE = "#F5F1E9"
SILVER = "#BEC2C8"
CRIMSON = "#E04450"
HEAD = "Barlow Condensed"
BODY = "Montserrat"
FONT_FILES = {
    "head": FONT_DIR / "BarlowCondensed-ExtraBold.ttf",
    "medium": FONT_DIR / "Montserrat-Medium.ttf",
    "bold": FONT_DIR / "Montserrat-Bold.ttf",
}
FOOTER = "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


class Typesetter:
    """Conservative advance-width estimates; rendered bounds are checked too."""

    def __init__(self) -> None:
        self.fonts = {name: TTFont(path) for name, path in FONT_FILES.items()}
        self.ids: list[str] = []

    def width(self, text: str, size: float, face: str, tracking: float = 0) -> float:
        font = self.fonts[face]
        cmap = font.getBestCmap()
        units = sum(font["hmtx"][cmap.get(ord(ch), ".notdef")][0] for ch in text)
        return units / font["head"].unitsPerEm * size + max(0, len(text) - 1) * tracking

    def wrap(self, text: str, size: float, face: str, width: float) -> list[str]:
        result: list[str] = []
        line = ""
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if line and self.width(candidate, size, face) > width:
                result.append(line)
                line = word
            else:
                line = candidate
        if line:
            result.append(line)
        return result

    def text(self, ident: str, value: str, x: float, y: float, size: float,
             face: str = "medium", color: str = WHITE, tracking: float = 0,
             anchor: str = "start", max_width: float = TEXT_WIDTH) -> str:
        estimate = self.width(value, size, face, tracking)
        if estimate > max_width:
            raise ValueError(f"{ident}: estimated text width {estimate:.1f} > {max_width}: {value}")
        self.ids.append(ident)
        family = HEAD if face == "head" else BODY
        weight = {"head": 800, "medium": 500, "bold": 700}[face]
        return (f'<text id="{ident}" x="{x:.2f}" y="{y:.2f}" '
                f'font-family="{family}" font-weight="{weight}" font-size="{size:.2f}" '
                f'letter-spacing="{tracking:.2f}" text-anchor="{anchor}" '
                f'fill="{color}">{esc(value)}</text>')


def font_css() -> str:
    specs = [("head", HEAD, 800), ("medium", BODY, 500), ("bold", BODY, 700)]
    return "\n".join(
        f"@font-face {{font-family:'{family}';font-style:normal;font-weight:{weight};"
        f"src:url('{data_uri(FONT_FILES[key], 'font/ttf')}') format('truetype');}}"
        for key, family, weight in specs
    )


def render_svg(number: int, slide: dict, scene: Path, logo: Path,
               fonts: str) -> tuple[str, list[str]]:
    type_ = Typesetter()
    headlines = slide["headline"]
    if isinstance(headlines, str):
        headlines = [headlines]
    if not 1 <= len(headlines) <= 3:
        raise ValueError(f"Slide {number}: headline must have one to three lines")
    headline_size = 94.0
    while max(type_.width(line, headline_size, "head") for line in headlines) > TEXT_WIDTH - 8:
        headline_size -= 1
    if headline_size < 70:
        raise ValueError(f"Slide {number}: shorten the headline instead of shrinking below 70px")
    headline_y = 254
    leading = headline_size * .98
    headline_bottom = headline_y + leading * (len(headlines) - 1)
    band_bottom = max(356, headline_bottom + 28)
    heading_transition = 64
    if slide.get("labels"):
        # All three demonstrations must remain visible, including the raised
        # fingertips and planted hands. Compress only this short two-line title.
        headline_size = min(headline_size, 84)
        headline_y = 238
        leading = headline_size * .98
        band_bottom = 340
        heading_transition = 24
    body = slide.get("body", [])
    if isinstance(body, str):
        body = [body]
    body_size = 30.0
    body_lines: list[str] = []
    for paragraph in body:
        body_lines.extend(type_.wrap(paragraph, body_size, "medium", TEXT_WIDTH - 8))
    if len(body_lines) > 3:
        raise ValueError(f"Slide {number}: supporting copy needs {len(body_lines)} lines; use at most three")
    subhead = slide.get("subhead", "")
    subhead_size = 32.0
    while type_.width(subhead, subhead_size, "bold") > TEXT_WIDTH - 8:
        subhead_size -= 1
    if subhead_size < 27:
        raise ValueError(f"Slide {number}: shorten subhead instead of shrinking below 27px")
    support_y = 1087
    items = [f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350">
<title>{esc(' '.join(headlines))}</title>
<desc>{esc(subhead + ' ' + ' '.join(body))}</desc>
<defs>
<style>{fonts}</style>
<linearGradient id="heading-transition" x1="0" y1="0" x2="0" y2="1">
  <stop stop-color="{INK}" stop-opacity="1"/>
  <stop offset="1" stop-color="{INK}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="copy-transition" x1="0" y1="0" x2="0" y2="1">
  <stop stop-color="{INK}" stop-opacity="0"/>
  <stop offset="1" stop-color="{INK}" stop-opacity="1"/>
</linearGradient>
</defs>
<rect width="1080" height="1350" fill="{INK}"/>
<image x="0" y="0" width="1080" height="1350" preserveAspectRatio="xMidYMid slice" xlink:href="{data_uri(scene, 'image/png')}"/>
<rect width="1080" height="{band_bottom:.2f}" fill="{INK}"/>
<rect y="{band_bottom:.2f}" width="1080" height="{heading_transition}" fill="url(#heading-transition)"/>
<rect y="{support_y-12}" width="1080" height="12" fill="url(#copy-transition)"/>
<rect y="{support_y}" width="1080" height="{HEIGHT-support_y}" fill="{INK}"/>
<image x="64" y="40" width="79" height="79" preserveAspectRatio="xMidYMid meet" xlink:href="{data_uri(logo, 'image/png')}"/>
''']
    items += [
        type_.text("brand-top", "CUTTHROAT", 157, 73, 18, "bold", tracking=1.7),
        type_.text("brand-bottom", "DISCIPLINE", 157, 99, 18, "bold", color=SILVER, tracking=1.7),
        type_.text("slide-number", f"{number:02d} / 08", 1016, 85, 20, "bold", color=SILVER, anchor="end"),
        '<path d="M64 139 H1016" stroke="#34363C" stroke-width="1"/>',
        '<path d="M64 139 H126" stroke="#E04450" stroke-width="3"/>',
        type_.text("kicker", slide["kicker"].upper(), 64, 167, 18, "bold", color=CRIMSON, tracking=2.4),
    ]
    for j, line in enumerate(headlines):
        items.append(type_.text(f"headline-{j}", line.upper(), 64, headline_y + j * leading,
                                headline_size, "head"))
    labels = slide.get("labels", [])
    if labels:
        if len(labels) != 3:
            raise ValueError("The variation slide must supply three labels")
        items.append('<rect x="0" y="1005" width="1080" height="82" fill="#101114" fill-opacity=".96"/>')
        for j, label in enumerate(labels):
            x = 64 + j * 327
            label_title = label["title"].upper()
            label_size = 26.0
            while type_.width(label_title, label_size, "bold") > 300:
                label_size -= 1
            items.append(type_.text(f"variation-title-{j}", label_title, x, 1036,
                                    label_size, "bold", color=WHITE, max_width=300))
            items.append(type_.text(f"variation-body-{j}", label["body"], x, 1068,
                                    21, "medium", color=SILVER, max_width=300))
    if number == 1:
        items.append(type_.text("subhead", subhead.upper(), 64, 1167, 100, "head"))
        body_y = 1207
    else:
        items.append('<path d="M64 1100 H114" stroke="#E04450" stroke-width="3"/>')
        if subhead:
            items.append(type_.text("subhead", subhead.upper(), 64, 1138, subhead_size, "bold"))
        body_y = 1178
    for j, line in enumerate(body_lines):
        items.append(type_.text(f"body-{j}", line, 64, body_y + j * 38, body_size))
    items += [
        '<path d="M64 1273 H1016" stroke="#34363C" stroke-width="1"/>',
        type_.text("footer", FOOTER, 540, 1313, 16, "bold", color=SILVER, tracking=1.5, anchor="middle"),
        '</svg>',
    ]
    return "\n".join(items), type_.ids


def render_env(temp: Path) -> dict[str, str]:
    cache = temp / "font-cache"
    cache.mkdir()
    profile = temp / "inkscape"
    profile.mkdir()
    config = temp / "fonts.conf"
    config.write_text(f'''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><dir>{esc(FONT_DIR)}</dir><cachedir>{esc(cache)}</cachedir>
<config><rescan><int>0</int></rescan></config></fontconfig>
''', encoding="utf-8")
    env = dict(os.environ)
    env.update(FONTCONFIG_FILE=str(config), XDG_CACHE_HOME=str(cache),
               INKSCAPE_PROFILE_DIR=str(profile))
    return env


def query_text_bounds(svg: Path, ids: list[str], env: dict) -> list[dict]:
    query = subprocess.run(["inkscape", str(svg), "--query-all"], env=env,
                           check=True, capture_output=True, text=True)
    records = {}
    for line in query.stdout.splitlines():
        fields = line.split(",")
        if len(fields) == 5 and fields[0] in ids:
            records[fields[0]] = [float(value) for value in fields[1:]]
    missing = set(ids) - set(records)
    if missing:
        raise ValueError(f"Missing rendered text bounds in {svg.name}: {missing}")
    results = []
    for ident in ids:
        x, y, width, height = records[ident]
        if x < 59 or x + width > 1021 or y < 38 or y + height > 1322:
            raise ValueError(f"Text leaves safe canvas bounds: {svg.name} {ident} {records[ident]}")
        results.append({"id": ident, "x": x, "y": y, "width": width, "height": height})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--svg-only", action="store_true")
    args = parser.parse_args()
    out = args.output.resolve()
    content = json.loads((out / "content.json").read_text(encoding="utf-8"))
    slides = content["slides"] if isinstance(content, dict) else content
    if len(slides) != 8:
        raise ValueError("The campaign must have exactly eight slides")
    logo = out / "ctd-cinematic-logo.png"
    if not logo.exists():
        shutil.copy2(CANONICAL_LOGO, logo)
    fonts = font_css()
    required = list(FONT_FILES.values()) + [out / f"scene-assets/{i:02d}-scene.png" for i in range(1, 9)]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing production inputs:\n" + "\n".join(missing))
    artwork: list[tuple[Path, list[str]]] = []
    for i, slide in enumerate(slides, 1):
        slug = slide["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Invalid slide slug: {slug}")
        svg, ids = render_svg(i, slide, out / f"scene-assets/{i:02d}-scene.png", logo, fonts)
        path = out / f"{i:02d}-{slug}.svg"
        path.write_text(svg, encoding="utf-8")
        artwork.append((path, ids))
    if args.svg_only:
        print(f"Wrote {len(artwork)} self-contained editable SVGs to {out}")
        return
    audit = {"canvas": [WIDTH, HEIGHT], "fonts": [path.name for path in FONT_FILES.values()],
             "safe_text_bounds": [59, 38, 1021, 1322], "slides": []}
    with tempfile.TemporaryDirectory(prefix="ctd-burpees-") as temp:
        env = render_env(Path(temp))
        for svg, ids in artwork:
            png = svg.with_suffix(".png")
            subprocess.run(["inkscape", str(svg), "--export-type=png", "--export-area-page",
                            f"--export-filename={png}", "--export-width=1080", "--export-height=1350"],
                           env=env, check=True, capture_output=True, text=True)
            bounds = query_text_bounds(svg, ids, env)
            audit["slides"].append({"file": svg.name, "text_bounds": bounds})
            print(f"Rendered and checked {png.name}", flush=True)
        pngs = [str(svg.with_suffix(".png")) for svg, _ in artwork]
        subprocess.run(["montage", *pngs, "-thumbnail", "270x338", "-tile", "4x2",
                        "-geometry", "+8+8", "-background", "#1C1E22", "-quality", "92",
                        str(out / "preview.jpg")], env=env, check=True)
    (out / "render-validation.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(f"Complete: {len(artwork)} slides, preview.jpg and render-validation.json in {out}")


if __name__ == "__main__":
    main()
