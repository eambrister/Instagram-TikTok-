"""Build Edison's "ONCE A MONTH / ONCE A WEEK / ONCE A DAY" food-frequency Reel.

Format reference: a creator standing still while food cutouts in three labelled slots swap each
cycle. This is not a talking head, so it has no captions, depth titles or whooshes. Edison stands
on the right and points up-left (month), left (week) and down-left (day); each food pops into the
matching slot on the beat. Resets between cycles and the walk in/out are cut, and every pause over 0.2 s
inside or between cycles is trimmed to a quick beat (standing rule §4b).
Food cutouts come from Edison's own craving-swaps / protein-tier-list source images.
No vignette, CTD end card.

    python3 -I tools/build_ea_once_a.py SRC.MOV WORDS.json OUT_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np
import soundfile as sf
from PIL import Image, ImageFilter
from scipy import ndimage

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, END_CARD, FPS, GRADE, H, IVORY, MONT_B, MONT_M, OBSIDIAN, PALE_GOLD, ROOT, W,
    ease, font, over, plain)

SR = 48000
SWAPS = ROOT / "outputs/edison-ambrister-craving-swaps/source-images"
TIER = ROOT / "outputs/edison-ambrister-protein-tier-list/source-images"
# (source image, object index left-to-right) per food; Month / Week / Day for each cycle.
SETS = [  # indices as reviewed on the cut-out contact sheet
    (("sugar-crave", 0), ("chocolate-crave", 2), ("chocolate-swap", 0)),   # sundae / choc bar / strawberries
    (("carbs-crave", 1), ("carbs-crave", 2), (TIER / "s.png", 1)),          # burger / spaghetti / chicken
    (("salty-crave", 1), ("salty-swap", 0), ("sugar-swap", 2)),             # chips / popcorn / apple + PB
    (("chocolate-crave", 0), ("chocolate-crave", 3), ("sugar-swap", 0)),    # cake / cookies / yogurt + berries
    (("sugar-crave", 3), ("salty-crave", 0), (TIER / "s.png", 3)),          # donuts / fries / eggs
    (("salty-crave", 2), (TIER / "s.png", 2), (TIER / "s.png", 0)),         # hot dog / steak / salmon
]
LABELS = ("ONCE A MONTH", "ONCE A WEEK", "ONCE A DAY")
# slot centre (x, y) and max box for Month / Week / Day: matched to where Edison points
SLOTS = [((262, 600), (420, 330)), ((252, 1055), (410, 320)), ((262, 1510), (420, 330))]


def cutout(src, idx):
    """idx-th object of a source strip, in the component order of the reviewed contact sheet
    (labels from a mx>28 matte). Cropped at the bottom of the food's solid body so the black
    studio floor's reflection is dropped."""
    path = src if isinstance(src, pathlib.Path) else SWAPS / f"{src}.png"
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    mx = im.max(2)
    m = ndimage.binary_fill_holes(ndimage.binary_closing(
        ndimage.binary_opening(mx > 28, iterations=2), iterations=6))
    lab, _ = ndimage.label(m)
    objs = [(sl, i + 1) for i, sl in enumerate(ndimage.find_objects(lab))
            if (sl[0].stop - sl[0].start) * (sl[1].stop - sl[1].start) >= 0.004 * m.size]
    sl, k = objs[idx]
    region = ndimage.binary_fill_holes(lab == k)
    # solid inside (dark chocolate must not turn see-through); feather only the outer 2 px
    alpha = np.clip(ndimage.distance_transform_edt(region) / 2.0, 0, 1)
    strong = (region & (mx > 85))[sl[0], sl[1]]
    rows = np.where(strong.sum(1) > 0.03 * strong.shape[1])[0]
    bottom = rows[-1] + 4 if len(rows) else strong.shape[0]
    # mirror reflections sit below the food and are clearly darker: cut at the first row in the
    # lower half whose mean brightness falls well under the body's
    reg = region[sl[0], sl[1]][:bottom]
    mxs = mx[sl[0], sl[1]][:bottom]
    cnt = reg.sum(1)
    rmean = np.where(cnt > 0, (mxs * reg).sum(1) / np.maximum(cnt, 1), 0)
    body = np.median(rmean[: max(1, int(len(rmean) * 0.6))])
    for r in range(int(len(rmean) * 0.55), len(rmean)):
        if rmean[r] < 0.62 * body and rmean[min(r + 6, len(rmean) - 1)] < 0.62 * body:
            bottom = r + 2
            break
    rgba = np.dstack([im, alpha * 255])[sl[0], sl[1]][:bottom].astype(np.uint8)
    img = Image.fromarray(rgba, "RGBA")
    return img.crop(img.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())


def fit(img, box):
    s = min(box[0] / img.width, box[1] / img.height)
    img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    rgb = img.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2, percent=90, threshold=2))
    rgb.putalpha(img.getchannel("A"))
    return rgb


def shadowed(img):
    """Soft contact shadow so cutouts sit on the light wall instead of floating."""
    pad = 30
    out = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: int(v * 0.45))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", img.size, (20, 18, 16, 255)), (pad + 6, pad + 12), a)
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(10)))
    out.alpha_composite(img, (pad, pad))
    return out


def plan(words):
    """Cycles = each 'Once a month … once a day'. Keep each cycle tight; cut the resets."""
    starts = [i for i, w in enumerate(words) if w["w"].lower().startswith("once")
              and i + 2 < len(words) and words[i + 2]["w"].lower().startswith("month")]
    q = lambda x: round(x * FPS) / FPS
    cyc, segs = [], []
    for n, i in enumerate(starts):
        month, week, day = i, i + 3, i + 6
        assert words[day + 2]["w"].lower().startswith("day"), words[day:day + 3]
        # each phrase: from just before "once" to just after its last word (month/week/day)
        phr = [(words[j]["t"] - 0.08, words[j + 2]["t"] + 0.42) for j in (month, week, day)]
        merged = [list(phr[0])]
        for s, e in phr[1:]:
            if s - merged[-1][1] <= 0.20:  # tiny gap: keep continuous
                merged[-1][1] = e
            else:  # pause > 0.2 s: cut it down to a quick 0.1 s beat
                merged[-1][1] += 0.05
                merged.append([s - 0.05, e])
        for s, e in merged:
            segs.append(dict(s=q(s), e=q(e), cycle=n))
        cyc.append(dict(s=segs[-len(merged)]["s"], e=segs[-1]["e"],
                        beats=(words[month]["t"], words[week]["t"], words[day]["t"])))
    return cyc, segs


def render(src, words_path, out_dir, only=None):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cyc, segs = plan(json.load(open(words_path)))
    offs = np.cumsum([0] + [g["e"] - g["s"] for g in segs])
    total = float(offs[-1])
    json.dump(dict(cycles=cyc, segments=segs, out_duration=total), open(out / "edl.json", "w"), indent=1)

    items = [[shadowed(fit(cutout(*f), SLOTS[k][1])) for k, f in enumerate(s)] for s in SETS]
    lab_f = font(BARLOW, 72)
    labels = [plain(t, lab_f, IVORY, 3, 0.85) for t in LABELS]

    lo, hi = (float(v) for v in only.split(":")) if only else (0.0, total)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", GRADE + f",fps={FPS}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    name = "proof.mp4" if only else "video-only.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-movflags", "+faststart", str(out / name)], stdin=subprocess.PIPE)
    fsize, k, last = W * H * 3, 0, None
    while True:
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize:
            break
        ts = k / FPS + 1e-4
        k += 1
        gi = next((i for i, g in enumerate(segs) if g["s"] <= ts < g["e"]), None)
        if gi is None:
            continue
        ci = segs[gi]["cycle"]
        c = cyc[ci]
        t = offs[gi] + ts - segs[gi]["s"]
        if not (lo <= t < hi):
            continue
        comp = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32).copy()
        last = comp.copy()
        for slot in range(3):
            # labels stay on screen the whole film (as in the reference)
            lb = labels[slot]
            (cx, cy), (bw, bh) = SLOTS[slot]
            over(comp, lb, cx - lb.width // 2, cy - bh // 2 - lb.height + 4, min(1.0, t / 0.3))
            beat = c["beats"][slot] - 0.08
            if ts < beat:
                continue
            u = (ts - beat) / 0.28
            sc = 0.55 + 0.55 * ease(min(u, 1)) - 0.10 * max(0.0, min(1, (u - 1) * 2))  # pop, settle
            sc = min(sc, 1.08) if u < 1 else max(1.0, 1.08 - 0.08 * min(1, (u - 1) * 2))
            img = items[ci][slot]
            im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)
            fade = min(1.0, (c["e"] - ts) / 0.12)
            over(comp, im, cx - im.width // 2, cy - im.height // 2, min(1.0, u * 2) * fade)
        enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())

    if not only and last is not None:
        logo = Image.open(ROOT / "brand/assets/ctd-cinematic-logo.png").convert("RGBA")
        lg = logo.resize((520, 520), Image.LANCZOS)
        name_img = plain("EDISON AMBRISTER", font(MONT_B, 50), IVORY, 10, 0.3)
        foot = plain("DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", font(MONT_M, 30), PALE_GOLD, 4, 0.3)
        for j in range(int(END_CARD * FPS)):
            u = ease(j / 18)
            comp = last * (1 - 0.9 * u) + np.array(OBSIDIAN, np.float32) * 0.9 * u
            over(comp, lg, (W - 520) // 2, 560, u)
            over(comp, name_img, (W - name_img.width) // 2, 1110, u)
            over(comp, foot, (W - foot.width) // 2, 1195, u)
            enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print("output", round(total, 2), "s from", len(cyc), "cycles")
    return cyc, offs


def audio(src, out_dir):
    """Edison's voice on the cut timeline (6 ms fades), cleaned; no music or SFX (per brief)."""
    out = pathlib.Path(out_dir)
    cyc = json.load(open(out / "edl.json"))["segments"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", str(SR),
                    "-af", "highpass=f=85,afftdn=nf=-28,"
                    "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=160:makeup=2",
                    str(out / "voice_raw.wav")], check=True)
    raw, _ = sf.read(out / "voice_raw.wav", dtype="float32")
    f = int(0.006 * SR)
    ramp = np.linspace(0, 1, f, dtype=np.float32)
    parts = []
    for c in cyc:
        p = raw[int(c["s"] * SR):int(c["e"] * SR)].copy()
        p[:f] *= ramp
        p[-f:] *= ramp[::-1]
        parts.append(p)
    v = np.concatenate(parts + [np.zeros(int(END_CARD * SR), np.float32)])
    sf.write(out / "voice.wav", v, SR)
    # voice-only is peaky: oversampled brickwall limiter, then measured make-up gain to -14 LUFS
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "voice.wav"), "-af",
                    "aresample=192000,alimiter=limit=0.20:attack=1:release=50:level=false,aresample=48000",
                    str(out / "lim.wav")], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out / "lim.wav"), "-af", "ebur128",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    integ = float([ln for ln in r.splitlines() if ln.strip().startswith("I:")][-1].split()[1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "lim.wav"), "-af",
                    f"volume={-14.0 - integ:.2f}dB", "-ar", str(SR), str(out / "mix_final.wav")], check=True)


def main():
    ap = argparse.ArgumentParser()
    for k in ("src", "words", "out"):
        ap.add_argument(k)
    ap.add_argument("--only")
    ap.add_argument("--final")
    a = ap.parse_args()
    render(a.src, a.words, a.out, a.only)
    if not a.only:
        audio(a.src, a.out)
        if a.final:
            import ea_cut_edit as eng
            eng.finish(a.out, a.final)


if __name__ == "__main__":
    main()
