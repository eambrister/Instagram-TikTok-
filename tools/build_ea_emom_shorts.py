"""Three vertical Shorts/Reels/TikToks from the last round of Edison's 42-minute rotating EMOM.

TikTok / Instagram Reels / YouTube Shorts standard: 1080 x 1920 (9:16), 30 fps, H.264 High,
yuv420p, AAC 48 kHz stereo, -14 LUFS, under 60 s. All text sits inside the shared safe area
(clear of the top 250 px status/UI band, the right-hand button column and the bottom caption band).

Each Short is one real-time set (cropped 9:16 around Edison), a few seconds of him walking it off,
the beep-synced minute clock, and the CTD end card.

    python3 -I tools/build_ea_emom_shorts.py SRC.MOV OUT_DIR
"""
import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import BARLOW, MONT_B, MONT_M, ROOT, font  # noqa: E402

W, H, FPS = 1080, 1920, 30
GOLD, PALE, IVORY, OBS, SILVER, CRIMSON = (214, 169, 24), (243, 216, 120), (246, 239, 226), (7, 8, 10), (170, 176, 185), (214, 52, 70)
T0 = 21.96          # first beep (source seconds); minute m starts at T0 + 60*(m-1)
CROP_X = 1070       # Edison's working position (source x centre); 608x1080 crop -> 1080x1920

SHORTS = [  # minute, move, reps, clip start/end (source s), hook lines, done-card
    dict(name="short-1-pushups-min40", minute=40, move="PUSH-UPS", reps=10, a=2361.6, b=2379.0,
         hook=("MINUTE 40 OF 42", "10 PUSH-UPS"), finale=False),
    dict(name="short-2-burpees-min41", minute=41, move="BURPEES", reps=10, a=2421.6, b=2457.5,
         hook=("MINUTE 41 OF 42", "10 BURPEES"), finale=False),
    dict(name="short-3-squats-last-minute", minute=42, move="SQUATS", reps=20, a=2481.6, b=2514.0,
         hook=("THE LAST MINUTE", "20 SQUATS"), finale=True),
]


def _panel(size, r=24, a=205):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=OBS + (a,),
                                         outline=GOLD + (150,), width=2)
    return im


def _shadow(base, im, xy):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 150)), (xy[0], xy[1] + 8), im.split()[3])
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    base.alpha_composite(im, xy)


def hud(sp, left):
    """Compact HUD for one second: exercise panel (top-left), countdown ring (top-right)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = _panel((600, 220))
    d = ImageDraw.Draw(p)
    d.text((28, 22), f"MIN {sp['minute']} / 42  ·  ROUND 14 / 14", font=font(MONT_B, 26), fill=PALE)
    d.text((28, 62), sp["move"], font=font(BARLOW, 112), fill=IVORY)
    tw = d.textlength(sp["move"], font=font(BARLOW, 112))
    d.text((28 + tw + 16, 98), f"×{sp['reps']}", font=font(BARLOW, 72), fill=PALE)
    _shadow(im, p, (48, 270))
    R = 92
    ring = Image.new("RGBA", (2 * R + 20, 2 * R + 20), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((10, 10, 10 + 2 * R, 10 + 2 * R), fill=OBS + (205,))
    rd.arc((14, 14, 6 + 2 * R, 6 + 2 * R), 0, 360, fill=(60, 62, 70, 255), width=11)
    col = CRIMSON if left <= 5 else GOLD
    rd.arc((14, 14, 6 + 2 * R, 6 + 2 * R), -90, -90 + 360 * left / 60, fill=col + (255,), width=11)
    rd.text((10 + R, 10 + R - 8), f"0:{left:02d}" if left < 60 else "1:00", font=font(BARLOW, 76), fill=IVORY, anchor="mm")
    rd.text((10 + R, 10 + R + 46), "LEFT", font=font(MONT_M, 18), fill=SILVER, anchor="mm")
    _shadow(im, ring, (W - ring.width - 150, 280))  # clear of the right-hand button column
    return im


def hook(sp):
    """Big opening hook (first ~2.5 s), centred in the upper safe area."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 720), sp["hook"][0], font=font(BARLOW, 120), fill=PALE, anchor="mm", stroke_width=6, stroke_fill=OBS)
    d.text((W // 2, 860), sp["hook"][1], font=font(BARLOW, 170), fill=IVORY, anchor="mm", stroke_width=7, stroke_fill=OBS)
    return im


def finale_card():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    im.paste(Image.new("RGBA", (W, 520), OBS + (170,)), (0, 560))
    d.text((W // 2, 680), "42 MINUTES.", font=font(BARLOW, 150), fill=IVORY, anchor="mm")
    d.text((W // 2, 820), "560 REPS. DONE.", font=font(BARLOW, 130), fill=PALE, anchor="mm")
    d.text((W // 2, 940), "140 PUSH-UPS · 140 BURPEES · 280 SQUATS", font=font(MONT_B, 30), fill=IVORY, anchor="mm")
    d.text((W // 2, 1010), "FULL WORKOUT ON MY YOUTUBE", font=font(MONT_M, 30), fill=SILVER, anchor="mm")
    return im


def end_card(out, secs=1.6):
    im = Image.new("RGB", (W, H), OBS)
    logo = Image.open(ROOT / "brand/assets/ctd-cinematic-logo.png").convert("RGBA").resize((520, 520))
    im.paste(logo, ((W - 520) // 2, 560), logo)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 1150), "EDISON AMBRISTER", font=font(MONT_B, 50), fill=IVORY, anchor="mm")
    d.text((W // 2, 1225), "DISCIPLINE · ACCOUNTABILITY · CONSISTENCY", font=font(MONT_M, 28), fill=PALE, anchor="mm")
    im.save(out / "endcard_v.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(secs), "-i", str(out / "endcard_v.png"),
                    "-f", "lavfi", "-t", str(secs), "-i", "anullsrc=r=48000:cl=stereo", "-vf", "fade=in:0:8,format=yuv420p",
                    "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-shortest", str(out / "endcard_v.mp4")], check=True)


def build(src, out, sp):
    d = out / sp["name"]
    d.mkdir(parents=True, exist_ok=True)
    m0 = T0 + 60 * (sp["minute"] - 1)
    dur = sp["b"] - sp["a"]
    # per-second HUD frames aligned to the beep (index 0 = clip start)
    import math
    j0 = math.floor(sp["a"] - m0)          # beep-second containing the clip start
    n = int(dur) + 3
    for k in range(n):
        left = 60 - (j0 + k)
        hud(sp, max(1, min(60, left))).save(d / f"hud_{k:03d}.png", compress_level=1)
    hook(sp).save(d / "hook.png")
    finale_card().save(d / "finale.png")
    x0 = CROP_X - 304
    fin_t = (sp["b"] - 3.2 - sp["a"]) if sp["finale"] else 1e9
    off = m0 + j0 - sp["a"]                 # when HUD frame 0 starts, in clip time (<= 0)
    fc = (f"[0:v]crop=608:1080:{x0}:0,scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5,fps={FPS},format=yuv420p[v0];"
          f"[1:v]setpts=PTS-STARTPTS+({off})/TB,fps={FPS}[h];"
          f"[v0][h]overlay=format=auto:enable='lt(t,{fin_t})'[v1];"
          f"[v1][2:v]overlay=format=auto:enable='lt(t,2.6)'[v2];"
          f"[v2][3:v]overlay=format=auto:enable='gte(t,{fin_t})',format=yuv420p,setsar=1[vb];"
          f"[0:a]aresample=48000,aformat=channel_layouts=stereo[ab];"
          f"[4:v]fps={FPS},format=yuv420p,setsar=1[ve];[4:a]aformat=channel_layouts=stereo[ae];"
          f"[vb][ab][ve][ae]concat=n=2:v=1:a=1[v][a0];[a0]loudnorm=I=-14:TP=-2:LRA=9[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sp["a"]), "-t", str(dur), "-i", src,
                    "-framerate", "1", "-i", str(d / "hud_%03d.png"),
                    "-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", str(d / "hook.png"),
                    "-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", str(d / "finale.png"),
                    "-i", str(out / "endcard_v.mp4"),
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-r", str(FPS),
                    "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "19", "-maxrate", "12M", "-bufsize", "24M",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
                    str(out / f"{sp['name']}.mp4")], check=True)


def main():
    src, out = sys.argv[1], pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    end_card(out)
    for sp in SHORTS:
        build(src, out, sp)
        print("built", sp["name"])


if __name__ == "__main__":
    main()
