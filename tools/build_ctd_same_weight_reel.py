#!/usr/bin/env python3
"""Render the CTD 'Same Starting Weight' vertical comparison reel."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "ctd-same-weight-different-standards"
W, H, FPS, DURATION = 1080, 1920, 30, 15
GOLD = "#D8A817"
PALE_GOLD = "#FFE08A"
CRIMSON = "#A30F25"
RED = "#E43B43"
WHITE = "#F4F0E8"
SILVER = "#AEB4BE"
MUTED = "#777D88"
BLACK = "#07080A"

HEAD = ROOT / "brand/fonts/BarlowCondensed-ExtraBold.ttf"
BODY = ROOT / "brand/fonts/Montserrat-Bold.ttf"
LOGO = ROOT / "outputs/ctd-why-routine-matters/ctd-cinematic-logo.png"


def font(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


F = {
    "tiny": font(BODY, 22),
    "small": font(BODY, 27),
    "body": font(BODY, 34),
    "label": font(HEAD, 42),
    "counter": font(HEAD, 56),
    "headline": font(HEAD, 76),
    "end": font(HEAD, 92),
}


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def ease(v):
    v = clamp(v)
    return v * v * (3 - 2 * v)


def rgba(hex_color: str, alpha=255):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def centered(draw, xy, text, fnt, fill, anchor="mm", **kw):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor, **kw)


def glow_ellipse(base, box, color, blur=35, alpha=110):
    layer = Image.new("RGBA", base.size)
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=rgba(color, alpha))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def line(draw, pts, fill, width):
    draw.line(pts, fill=fill, width=width, joint="curve")


def draw_dumbbell(draw, x, y, scale, color):
    line(draw, [(x-62*scale, y), (x+62*scale, y)], color, int(14*scale))
    for dx in (-72, -53, 53, 72):
        draw.rounded_rectangle((x+(dx-10)*scale, y-31*scale, x+(dx+10)*scale, y+31*scale), radius=int(6*scale), fill=color)


def draw_plate(draw, x, y, scale, disciplined):
    edge = PALE_GOLD if disciplined else RED
    draw.ellipse((x-88*scale, y-32*scale, x+88*scale, y+32*scale), fill="#D7D8D4", outline=edge, width=max(2, int(5*scale)))
    if disciplined:
        draw.pieslice((x-64*scale, y-24*scale, x+64*scale, y+24*scale), 200, 340, fill="#7BA557")
        draw.ellipse((x-35*scale, y-15*scale, x+8*scale, y+15*scale), fill="#D1B07A")
        draw.ellipse((x+12*scale, y-15*scale, x+58*scale, y+15*scale), fill="#EEE7D2")
    else:
        draw.rounded_rectangle((x-55*scale, y-16*scale, x+25*scale, y+17*scale), radius=int(9*scale), fill="#D58530")
        draw.rectangle((x-50*scale, y-3*scale, x+20*scale, y+5*scale), fill="#F2CE4D")
        for dx in (42, 58, 73):
            line(draw, [(x+dx*scale, y-20*scale), (x+(dx+3)*scale, y+17*scale)], "#EBC64F", max(2, int(6*scale)))


def draw_avatar(base, cx, floor, scale, primary, accent, phase, disciplined, progress):
    """Original faceless geometric training mannequin with simple motion."""
    layer = Image.new("RGBA", base.size)
    d = ImageDraw.Draw(layer)
    squat = (0.5 + 0.5 * math.sin(phase * math.tau)) if phase >= 0 else 0
    squat = squat if disciplined else squat * 0.55
    muscle = (0.10 + 0.26 * progress) if disciplined else (0.12 + 0.08 * math.sin(progress * math.pi * 3))
    sy = floor - (345 - 92*squat) * scale
    head_r = 45 * scale
    hip_y = sy + (188 - 34*squat) * scale
    shoulder_y = sy + 88 * scale
    shoulder_w = (66 + 90*muscle) * scale
    hip_w = (48 + 38*muscle) * scale
    # shadow
    glow_ellipse(layer, (cx-155*scale, floor-35*scale, cx+155*scale, floor+26*scale), accent, 28, 100)
    # legs
    knee_spread = (36 + 35*squat) * scale
    knee_y = hip_y + (88 - 30*squat) * scale
    ankle_y = floor - 12*scale
    limb = max(10, int((24 + 28*muscle) * scale))
    line(d, [(cx-hip_w*.55, hip_y), (cx-knee_spread, knee_y), (cx-47*scale, ankle_y)], primary, limb)
    line(d, [(cx+hip_w*.55, hip_y), (cx+knee_spread, knee_y), (cx+47*scale, ankle_y)], primary, limb)
    # shoes
    d.rounded_rectangle((cx-78*scale, ankle_y-8*scale, cx-30*scale, ankle_y+15*scale), radius=int(8*scale), fill=accent)
    d.rounded_rectangle((cx+30*scale, ankle_y-8*scale, cx+78*scale, ankle_y+15*scale), radius=int(8*scale), fill=accent)
    # torso
    torso = [(cx-shoulder_w, shoulder_y), (cx+shoulder_w, shoulder_y), (cx+hip_w, hip_y), (cx-hip_w, hip_y)]
    d.polygon(torso, fill=primary)
    d.line(torso+[torso[0]], fill=accent, width=max(3, int(5*scale)), joint="curve")
    # head
    d.ellipse((cx-head_r, sy-head_r, cx+head_r, sy+head_r), fill=WHITE, outline=accent, width=max(3, int(5*scale)))
    # arms curl / idle
    curl = 0.5 + 0.5*math.sin(phase*math.tau + (0 if disciplined else 1.4))
    elbow_y = shoulder_y + 78*scale
    hand_y = elbow_y - 70*scale*curl
    line(d, [(cx-shoulder_w*.85, shoulder_y+12*scale), (cx-shoulder_w-20*scale, elbow_y), (cx-shoulder_w-65*scale, hand_y)], primary, limb)
    line(d, [(cx+shoulder_w*.85, shoulder_y+12*scale), (cx+shoulder_w+20*scale, elbow_y), (cx+shoulder_w+65*scale, hand_y)], primary, limb)
    if disciplined or progress < .5:
        draw_dumbbell(d, cx-shoulder_w-65*scale, hand_y, .42*scale, accent)
        draw_dumbbell(d, cx+shoulder_w+65*scale, hand_y, .42*scale, accent)
    # chest accent and status mark
    d.rounded_rectangle((cx-38*scale, shoulder_y+38*scale, cx+38*scale, shoulder_y+50*scale), radius=int(5*scale), fill=accent)
    base.alpha_composite(layer)


def weight_at(t, disciplined):
    marks = [0, 2.4, 4.4, 6.4, 8.4, 10.4, 12.4]
    values = ([222, 218, 224, 216, 226, 219, 222] if not disciplined else [222, 214, 203, 190, 174, 158, 142])
    for i in range(len(marks)-1):
        if marks[i] <= t < marks[i+1]:
            p = ease((t-marks[i])/(marks[i+1]-marks[i]))
            return round(values[i]*(1-p)+values[i+1]*p)
    return values[-1]


def event_for(t, disciplined):
    if t < 2.4: return "STARTING POINT"
    if t < 4.4: return "SCHEDULED WORKOUT" if disciplined else "TRAINS WHEN MOTIVATED"
    if t < 6.4: return "PROTEIN + PORTIONS" if disciplined else "GUESSES EVERY MEAL"
    if t < 8.4: return "WEEKLY CHECK-IN" if disciplined else "CHEAT WEEKEND"
    if t < 10.4: return "ADJUSTS THE PLAN" if disciplined else "STARTS AGAIN MONDAY"
    return "KEEPS EXECUTING" if disciplined else "REPEATS THE CYCLE"


def month_for(t):
    return min(18, max(1, round(1 + clamp(t/12.4)*17)))


logo_src = Image.open(LOGO).convert("RGBA")
logo_src.thumbnail((130, 130), Image.Resampling.LANCZOS)


def base_background(t):
    im = Image.new("RGBA", (W, H), rgba(BLACK))
    d = ImageDraw.Draw(im)
    # restrained architectural grid and central divide
    for y in range(330, 1680, 120):
        d.line((40, y, W-40, y), fill=(255,255,255,10), width=1)
    d.rectangle((0, 0, W//2, H), fill=(26, 4, 10, 75))
    d.rectangle((W//2, 0, W, H), fill=(35, 27, 4, 60))
    d.line((W//2, 290, W//2, 1650), fill=rgba("#545861", 120), width=2)
    # red and gold stage pools
    glow_ellipse(im, (80, 1260, 500, 1570), CRIMSON, 70, 115)
    glow_ellipse(im, (580, 1260, 1000, 1570), GOLD, 70, 95)
    return im


def draw_header(im, t):
    d = ImageDraw.Draw(im)
    im.alpha_composite(logo_src, (45, 42))
    d.text((185, 68), "CUTTHROAT", font=F["small"], fill=WHITE)
    d.text((185, 104), "DISCIPLINE", font=F["small"], fill=SILVER)
    d.line((45, 164, W-45, 164), fill=rgba("#555A62"), width=2)
    if t < 12.7:
        centered(d, (W//2, 218), "SAME STARTING WEIGHT.", F["headline"], WHITE)
        centered(d, (W//2, 292), "DIFFERENT STANDARDS.", F["headline"], GOLD)


def draw_main(t):
    im = base_background(t)
    d = ImageDraw.Draw(im)
    draw_header(im, t)
    # status area
    centered(d, (270, 390), "NO ACCOUNTABILITY", F["label"], RED)
    centered(d, (810, 390), "DISCIPLINED SYSTEM", F["label"], PALE_GOLD)
    centered(d, (270, 448), f"{weight_at(t, False)} LB", F["counter"], WHITE)
    centered(d, (810, 448), f"{weight_at(t, True)} LB", F["counter"], WHITE)
    centered(d, (W//2, 523), f"MONTH {month_for(t):02d}", F["body"], SILVER)
    # looping avatars
    phase = (t * 1.25) % 1
    prog = clamp(t/12.4)
    draw_avatar(im, 270, 1370, 1.20, SILVER, RED, phase, False, prog)
    draw_avatar(im, 810, 1370, 1.20, WHITE, GOLD, phase, True, prog)
    d = ImageDraw.Draw(im)
    # food tables for meal phases
    if 4.4 <= t < 8.4:
        draw_plate(d, 270, 1435, 1.05, False)
        draw_plate(d, 810, 1435, 1.05, True)
    # event captions
    centered(d, (270, 1532), event_for(t, False), F["tiny"], WHITE)
    centered(d, (810, 1532), event_for(t, True), F["tiny"], WHITE)
    centered(d, (270, 1590), "INTENTION WITHOUT A SYSTEM", F["tiny"], MUTED)
    centered(d, (810, 1590), "EXECUTION WITH A SYSTEM", F["tiny"], MUTED)
    # footer
    d.line((45, 1770, W-45, 1770), fill=rgba("#555A62"), width=2)
    centered(d, (W//2, 1822), "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", F["tiny"], SILVER)
    return im


def draw_end(t):
    im = base_background(t)
    d = ImageDraw.Draw(im)
    draw_header(im, 99)
    fade = ease((t-12.55)/.45)
    centered(d, (W//2, 330), "18 MONTHS LATER", F["body"], GOLD)
    centered(d, (270, 540), "222 LB", F["counter"], SILVER)
    centered(d, (270, 610), "STILL RESTARTING", F["label"], RED)
    centered(d, (810, 540), "142 LB", F["counter"], WHITE)
    centered(d, (810, 610), "STILL EXECUTING", F["label"], PALE_GOLD)
    d.line((W//2, 460, W//2, 730), fill=rgba("#555A62"), width=2)
    centered(d, (W//2, 920), "MOTIVATION STARTS.", F["end"], WHITE)
    centered(d, (W//2, 1010), "DISCIPLINE FINISHES.", F["end"], GOLD)
    logo = logo_src.copy()
    logo.thumbnail((245,245), Image.Resampling.LANCZOS)
    im.alpha_composite(logo, ((W-logo.width)//2, 1160))
    centered(d, (W//2, 1495), "YOUR RESULTS RECORD WHAT YOU REPEAT.", F["body"], WHITE)
    d.line((45, 1770, W-45, 1770), fill=rgba("#555A62"), width=2)
    centered(d, (W//2, 1822), "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", F["tiny"], SILVER)
    return im


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    silent = OUT / "same-weight-different-standards-silent.mp4"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(silent)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(FPS*DURATION):
        t = n/FPS
        im = draw_main(t) if t < 12.55 else draw_end(t)
        proc.stdin.write(im.tobytes())
        if n in (0, FPS*6, FPS*13):
            im.convert("RGB").save(OUT / f"preview-{n//FPS:02d}s.jpg", quality=92)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg video render failed")

    final = OUT / "same-weight-different-standards.mp4"
    # Original percussion-like pulse bed. Users can replace it with trending audio in Instagram.
    audio = (
        "aevalsrc='0.10*sin(2*PI*(52+3*sin(2*PI*t/4))*t)*(0.55+0.45*sin(2*PI*2*t))"
        "+0.035*sin(2*PI*104*t)':s=44100:d=15,"
        "highpass=f=35,lowpass=f=900,afade=t=in:st=0:d=0.25,afade=t=out:st=14.2:d=0.8"
    )
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent),
        "-f", "lavfi", "-i", audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", str(final)
    ], check=True)


if __name__ == "__main__":
    render()
