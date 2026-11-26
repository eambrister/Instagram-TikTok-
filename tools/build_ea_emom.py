"""Edison's 42-minute rotating EMOM for YouTube (16:9).

Rotating EMOM: minute 1 = 10 push-ups, minute 2 = 10 burpees, minute 3 = 20 squats, repeat x14
(140 push-ups, 140 burpees, 280 squats, 560 reps). His own interval beep is kept; the overlay is
synced to the first beep. The overlay changes once a second, so it is rendered as one PNG per
second and laid over the graded footage by ffmpeg (fast for a 42-minute piece).

    python3 -I tools/build_ea_emom.py overlays OUT_DIR --t0 SECONDS [--w 1920 --h 1080]
    python3 -I tools/build_ea_emom.py render SRC.MOV OUT_DIR OUT.mp4 --t0 SECONDS [--grade bright|moody] [--only a:b]
"""
import argparse
import math
import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import BARLOW, MONT_B, MONT_M, font  # noqa: E402

GOLD = (214, 169, 24)
PALE = (243, 216, 120)
IVORY = (246, 239, 226)
OBS = (7, 8, 10)
SILVER = (170, 176, 185)
CRIMSON = (214, 52, 70)

MOVES = [("PUSH-UPS", 10), ("BURPEES", 10), ("SQUATS", 20)]
MINUTES = 42
CYCLES = MINUTES // len(MOVES)

GRADES = {
    # v1 choice: lift mids/shadows with a curve that keeps true black (no milky lift), light denoise
    "clean": "hqdn3d=3:2:6:4,curves=all='0/0 0.06/0.07 0.18/0.30 0.45/0.62 0.8/0.88 1/1',"
             "eq=saturation=1.06,colorbalance=rs=0.02:bs=-0.01:rm=0.02,unsharp=5:5:0.45",
    # dark pre-dawn footage: lift shadows/exposure, clean low-light grain, keep skin natural
    "bright": "hqdn3d=3:2:6:4,eq=brightness=0.06:contrast=1.06:saturation=1.05:gamma=1.35,"
              "colorbalance=rs=0.02:bs=-0.02:rm=0.02:bm=-0.01,unsharp=5:5:0.4",
    # keep the early-morning mood: gentler lift, cool shadows, warm mids
    "moody": "hqdn3d=3:2:6:4,eq=brightness=0.02:contrast=1.10:saturation=0.92:gamma=1.18,"
             "colorbalance=rs=-0.02:bs=0.05:rm=0.03:bm=-0.02,unsharp=5:5:0.3",
}


def panel(size, r=26, alpha=200):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=OBS + (alpha,),
                                         outline=(GOLD[0], GOLD[1], GOLD[2], 150), width=2)
    return im


def shadowed(base, im, xy, blur=14, a=150):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    m = im.split()[3].point(lambda v: v * a // 255)
    sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (xy[0], xy[1] + 6), m)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(im, xy)


def overlay(sec, W, H):
    """Overlay for second `sec` after the first beep (0 .. MINUTES*60-1)."""
    s = W / 1920
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    minute = sec // 60          # 0-based
    left = 60 - sec % 60
    mv, reps = MOVES[minute % 3]
    nmv, nreps = MOVES[(minute + 1) % 3]
    cycle = minute // 3 + 1

    # --- top-left: minute, current move, next ---
    pw, ph = int(560 * s), int(250 * s)
    p = panel((pw, ph))
    d = ImageDraw.Draw(p)
    d.text((int(30 * s), int(22 * s)), f"MIN {minute + 1:02d} / {MINUTES}", font=font(MONT_B, int(30 * s)), fill=PALE)
    d.text((int(30 * s), int(62 * s)), f"{mv}", font=font(BARLOW, int(110 * s)), fill=IVORY)
    tw = d.textlength(mv, font=font(BARLOW, int(110 * s)))
    d.text((int(30 * s + tw + 18 * s), int(96 * s)), f"×{reps}", font=font(BARLOW, int(72 * s)), fill=PALE)
    if minute + 1 < MINUTES:
        d.text((int(30 * s), int(196 * s)), f"NEXT: {nmv} ×{nreps}", font=font(MONT_M, int(26 * s)), fill=SILVER)
    else:
        d.text((int(30 * s), int(196 * s)), "LAST MINUTE. FINISH IT.", font=font(MONT_B, int(26 * s)), fill=CRIMSON)
    shadowed(im, p, (int(48 * s), int(44 * s)))

    # --- top-right: countdown ring ---
    R = int(105 * s)
    ring = Image.new("RGBA", (2 * R + 20, 2 * R + 20), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((10, 10, 10 + 2 * R, 10 + 2 * R), fill=OBS + (200,))
    rd.arc((14, 14, 6 + 2 * R, 6 + 2 * R), 0, 360, fill=(60, 62, 70, 255), width=int(12 * s))
    frac = left / 60
    col = CRIMSON if left <= 5 else GOLD
    rd.arc((14, 14, 6 + 2 * R, 6 + 2 * R), -90, -90 + 360 * frac, fill=col + (255,), width=int(12 * s))
    txt = f"0:{left:02d}" if left < 60 else "1:00"
    f = font(BARLOW, int(86 * s))
    rd.text((10 + R, 10 + R - int(8 * s)), txt, font=f, fill=IVORY, anchor="mm")
    rd.text((10 + R, 10 + R + int(52 * s)), "LEFT", font=font(MONT_M, int(20 * s)), fill=SILVER, anchor="mm")
    shadowed(im, ring, (W - ring.width - int(48 * s), int(36 * s)))

    # --- bottom: totals + round ---
    done = [0, 0, 0]
    for m in range(minute):  # completed minutes only
        done[m % 3] += MOVES[m % 3][1]
    bw, bh = int(1180 * s), int(96 * s)
    b = panel((bw, bh), r=int(22 * s))
    bd = ImageDraw.Draw(b)
    x = int(28 * s)
    bd.text((x, bh // 2), f"ROUND {cycle} / {CYCLES}", font=font(BARLOW, int(46 * s)), fill=PALE, anchor="lm")
    x += int(250 * s)
    for i, (name, r_) in enumerate(MOVES):
        tot = r_ * CYCLES
        active = i == minute % 3
        bd.text((x, bh // 2 - int(14 * s)), name, font=font(MONT_B, int(18 * s)), fill=IVORY if active else SILVER, anchor="lm")
        bd.text((x, bh // 2 + int(16 * s)), f"{done[i]} / {tot}", font=font(BARLOW, int(38 * s)),
                fill=PALE if active else IVORY, anchor="lm")
        # progress bar
        bx, by, bwid = x + int(150 * s), bh // 2 + int(14 * s), int(110 * s)
        bd.rounded_rectangle((bx, by - 4, bx + bwid, by + 4), 4, fill=(60, 62, 70, 255))
        bd.rounded_rectangle((bx, by - 4, bx + max(8, int(bwid * done[i] / tot)), by + 4), 4,
                             fill=(GOLD if active else SILVER) + (255,))
        x += int(300 * s)
    shadowed(im, b, ((W - bw) // 2, H - bh - int(44 * s)))
    return im


def title_card(W, H, kind):
    """Intro (before the first beep) and finish (after the last minute) overlays."""
    s = W / 1920
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(150 * max(0.0, 1 - y / (H * 0.55))))
    im.paste(Image.new("RGBA", (W, H), OBS + (255,)), (0, 0), grad.resize((W, H)))
    d = ImageDraw.Draw(im)
    if kind == "intro":
        d.text((W // 2, int(150 * s)), "42-MINUTE ROTATING EMOM", font=font(BARLOW, int(120 * s)), fill=IVORY, anchor="mm")
        d.text((W // 2, int(250 * s)), "MIN 1: 10 PUSH-UPS   ·   MIN 2: 10 BURPEES   ·   MIN 3: 20 SQUATS",
               font=font(MONT_B, int(34 * s)), fill=PALE, anchor="mm")
        d.text((W // 2, int(312 * s)), "14 ROUNDS  ·  560 REPS  ·  NO GYM", font=font(MONT_M, int(30 * s)), fill=SILVER, anchor="mm")
    else:
        d.text((W // 2, int(150 * s)), "42 MINUTES. DONE.", font=font(BARLOW, int(130 * s)), fill=IVORY, anchor="mm")
        d.text((W // 2, int(255 * s)), "140 PUSH-UPS  ·  140 BURPEES  ·  280 SQUATS  ·  560 REPS",
               font=font(MONT_B, int(34 * s)), fill=PALE, anchor="mm")
    return im


def make_overlays(out, W, H):
    title_card(W, H, "intro").save(out / "intro.png")
    title_card(W, H, "finish").save(out / "finish.png")
    out.mkdir(parents=True, exist_ok=True)
    for sec in range(MINUTES * 60):
        overlay(sec, W, H).save(out / f"ov_{sec:05d}.png", compress_level=1)


def end_card(out, W, H, secs=3.0):
    """CTD end card clip (logo, name, footer) with silent audio."""
    from build_ea_50_more_days import ROOT
    im = Image.new("RGB", (W, H), OBS)
    logo = Image.open(ROOT / "brand/assets/ctd-cinematic-logo.png").convert("RGBA").resize((int(420 * W / 1920),) * 2)
    im.paste(logo, ((W - logo.width) // 2, int(H * 0.22)), logo)
    d = ImageDraw.Draw(im)
    s = W / 1920
    d.text((W // 2, int(H * 0.22) + logo.height + int(60 * s)), "EDISON AMBRISTER", font=font(MONT_B, int(46 * s)), fill=IVORY, anchor="mm")
    d.text((W // 2, int(H * 0.22) + logo.height + int(120 * s)), "DISCIPLINE  ·  ACCOUNTABILITY  ·  CONSISTENCY",
           font=font(MONT_M, int(26 * s)), fill=PALE, anchor="mm")
    im.save(out / "endcard.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "24", "-t", str(secs), "-i", str(out / "endcard.png"),
                    "-f", "lavfi", "-t", str(secs), "-i", "anullsrc=r=48000:cl=stereo",
                    "-vf", "fade=in:0:12,format=yuv420p", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(out / "endcard.mp4")], check=True)


def render(src, out, final, t0, grade, only=None):
    """One pass: grade + per-second overlays (synced to the first beep at t0) + intro/finish cards,
    loudness-normalised audio, then the CTD end card appended."""
    out.mkdir(parents=True, exist_ok=True)
    W, H = 1920, 1080
    end_t = t0 + MINUTES * 60
    ss, dur = 0.0, None
    if only:
        ss, e = (float(v) for v in only.split(":"))
        dur = e - ss
    end_card(out, W, H)
    first = max(0, int(ss - t0))           # first overlay second inside the window
    off = t0 + first - ss                   # when that overlay starts, in window time
    fc = (f"[0:v]{GRADES[grade]},fps=24,format=yuv420p[g];"
          f"[1:v]fps=24,setpts=PTS-STARTPTS+({off})/TB[o];"
          f"[g][o]overlay=eof_action=pass:format=auto[v1];"
          f"[v1][2:v]overlay=enable='lt(t,{t0 - ss - 0.3})':format=auto:shortest=1[v2];"
          f"[v2][3:v]overlay=enable='gte(t,{end_t - ss})':format=auto:shortest=1,format=yuv420p,setsar=1[vb];"
          f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo[ab];"
          f"[4:v]fps=24,format=yuv420p,setsar=1[ve];[4:a]aformat=channel_layouts=stereo,aresample=48000[ae];"
          f"[vb][ab][ve][ae]concat=n=2:v=1:a=1[v][a]")
    cmd = (["ffmpeg", "-v", "error", "-y", "-ss", str(ss)] + (["-t", str(dur)] if dur else []) + ["-i", src,
           "-framerate", "1", "-start_number", str(first), "-i", str(out / "ov_%05d.png"),
           "-loop", "1", "-framerate", "24", "-i", str(out / "intro.png"),
           "-loop", "1", "-framerate", "24", "-i", str(out / "finish.png"),
           "-i", str(out / "endcard.mp4"),
           "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", final])
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["overlays", "render", "still"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--grade", default="bright")
    ap.add_argument("--only")
    a = ap.parse_args()
    if a.cmd == "overlays":
        pathlib.Path(a.args[0]).mkdir(parents=True, exist_ok=True)
        make_overlays(pathlib.Path(a.args[0]), a.w, a.h)
    elif a.cmd == "render":
        render(a.args[0], pathlib.Path(a.args[1]), a.args[2], a.t0, a.grade, a.only)
    elif a.cmd == "still":
        overlay(int(a.args[1]), a.w, a.h).save(a.args[0])


if __name__ == "__main__":
    main()
