"""Cut-edit engine for Edison's talking-head Reels (shared standard §4b).

Turns a raw single-take selfie into a tight edit: removes listed word ranges (filler, repeats,
flubbed retakes) and trims dead air, disguises each jump cut with alternating punch-ins, then
renders head-tracked depth titles, word-timed captions, an optional film-specific front layer
and the CTD end card. Titles/captions are authored in SOURCE time and remapped automatically.
Also assembles the voice on the new timeline and mixes music + designed SFX.

Film scripts (e.g. build_ea_5_things_lean.py) supply: build_events(), CUTS, and optionally
STEPS / front(t_out, remap) for extra graphics.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np
import soundfile as sf
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    END_CARD, FPS, GRADE, H, IVORY, MONT_B, MONT_M, OBSIDIAN, PALE_GOLD, ROOT, W, BARLOW,
    caption_groups, ease, env, font, over, plain, refine_mask, render_caption)
from mix_ea_50_more_days import impact, tick, whoosh  # noqa: E402

SR = 48000
ZOOMS = (1.0, 1.12)
ZOOM_CENTER = (0.5, 0.40)  # face sits in the upper-middle of these selfies


# ---------------------------------------------------------------- edit decision list
def vad_silences(wav16, min_len=0.4, above_floor_db=8):
    a, sr = sf.read(wav16, dtype="float32")
    hop = int(0.02 * sr)
    n = len(a) // hop
    rms = np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9
    db = 20 * np.log10(rms)
    act = db > np.percentile(db, 10) + above_floor_db
    out, i = [], 0
    while i < n:
        if act[i]:
            i += 1
            continue
        j = i
        while j < n and not act[j]:
            j += 1
        if (j - i) * 0.02 >= min_len:
            out.append((i * 0.02, j * 0.02))
        i = j
    return out, len(a) / sr


def plan_edl(words, cuts, wav16, keep_breath=0.13):
    """Return frame-quantized kept segments [(s, e)] in source seconds plus a cut log."""
    sil, dur = vad_silences(wav16)
    starts = [w["t"] for w in words]
    removed, log = [], []
    for (i0, i1, why) in cuts:
        s = words[i0]["t"] - 0.04
        e = words[i1 + 1]["t"] - 0.06 if i1 + 1 < len(words) else dur
        removed.append((s, e))
        log.append(dict(src=(round(s, 2), round(e, 2)), why=why,
                        text=" ".join(w["w"] for w in words[i0:i1 + 1])))
    for (s, e) in sil:
        # split the pause at any word start inside it, never cutting into a word's onset
        edges = [s] + [t for t in starts if s + 0.05 < t < e - 0.05] + [e]
        for a0, b0 in zip(edges[:-1], edges[1:]):
            inner_word = a0 != s  # sub-gap begins at a word start: that word is speaking
            if inner_word:
                continue
            lead = 0.10 if b0 != e else keep_breath
            cs, ce = a0 + keep_breath, b0 - lead
            if ce - cs > 0.12:
                removed.append((cs, ce))
                log.append(dict(src=(round(cs, 2), round(ce, 2)), why="silence"))
    removed.append((0.0, max(0.0, words[0]["t"] - 0.12)))
    removed.append((min(dur, words[-1]["t"] + 0.9), dur))
    removed.sort()
    keep, cur = [], 0.0
    for s, e in removed:
        if s > cur:
            keep.append((cur, s))
        cur = max(cur, e)
    if cur < dur:
        keep.append((cur, dur))
    q = lambda x: round(x * FPS) / FPS
    keep = [(q(s), q(e)) for s, e in keep if q(e) - q(s) >= 0.2]
    return keep, log


class Remap:
    def __init__(self, keep):
        self.keep = keep
        self.offs = np.cumsum([0] + [e - s for s, e in keep])[:-1]
        self.total = sum(e - s for s, e in keep)

    def seg_of(self, t):
        for i, (s, e) in enumerate(self.keep):
            if s <= t < e:
                return i
        return None

    def __call__(self, t):
        """Source time -> output time (times inside a cut snap to the next kept frame)."""
        for i, (s, e) in enumerate(self.keep):
            if t < e:
                return float(self.offs[i] + max(0.0, t - s))
        return float(self.total)


def remap_words(words, rm):
    out = []
    for w in words:
        i = rm.seg_of(w["t"])
        if i is None:
            continue
        s, e = rm.keep[i]
        out.append(dict(w=w["w"], t=rm(w["t"]), e=rm(min(w["e"], e - 1e-3))))
    return out


def remap_events(events, rm, min_len=0.25):
    out = []
    for e in events:
        e = dict(e)
        e["t0"], e["t1"] = rm(e["t0"]), rm(e["t1"])
        if e["t1"] - e["t0"] >= min_len:
            out.append(e)
    return out


# ---------------------------------------------------------------- picture
def zoom(frame, z):
    if z == 1.0:
        return frame
    im = Image.fromarray(frame.astype(np.uint8))
    cw, ch = W / z, H / z
    cx, cy = W * ZOOM_CENTER[0], H * ZOOM_CENTER[1]
    x0 = min(max(cx - cw / 2, 0), W - cw)
    y0 = min(max(cy - ch / 2, 0), H - ch)
    return np.asarray(im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)), np.float32)


def render(src, words_path, selfie, out_dir, film, only=None):
    from ai_edge_litert.interpreter import Interpreter

    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    words = json.load(open(words_path))
    wav16 = out / "a16.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
                    str(wav16)], check=True)
    keep, log = plan_edl(words, film.CUTS, wav16)
    rm = Remap(keep)
    json.dump(dict(keep=keep, cuts=log, out_duration=rm.total), open(out / "edl.json", "w"), indent=1)
    caps = caption_groups(remap_words(words, rm))
    events = remap_events(film.build_events(), rm)
    capf = font(BARLOW, 84)

    it = Interpreter(model_path=selfie)
    it.allocate_tensors()
    iin, iout = it.get_input_details()[0]["index"], it.get_output_details()[0]["index"]
    lo, hi = (float(v) for v in only.split(":")) if only else (0.0, rm.total)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", GRADE + f",fps={FPS}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    name = "proof.mp4" if only else "video-only.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-movflags", "+faststart", str(out / name)], stdin=subprocess.PIPE)
    logo = Image.open(ROOT / "brand/assets/ctd-cinematic-logo.png").convert("RGBA")
    prev_m, last, head = None, None, 450.0
    fsize, k, n_out = W * H * 3, 0, 0
    while True:
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize:
            break
        ts = k / FPS
        k += 1
        si = rm.seg_of(ts + 1e-4)
        if si is None:
            continue
        t = rm(ts + 1e-4)
        n_out += 1
        if not (lo <= t < hi):
            continue
        frame = zoom(np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32), ZOOMS[si % 2])
        x = np.asarray(Image.fromarray(frame.astype(np.uint8)).resize((256, 256), Image.BILINEAR),
                       np.float32)[None] / 255.0
        it.set_tensor(iin, x)
        it.invoke()
        m = refine_mask(it.get_tensor(iout)[0, ..., 0], frame)
        new_seg = prev_m is None or getattr(render, "_seg", None) != si
        render._seg = si
        if not new_seg:  # temporal smoothing only within a shot
            m = 0.6 * m + 0.4 * prev_m
        prev_m = m
        rows = np.where((m[:, 330:750] > 0.5).any(1))[0]
        if len(rows):
            ht = float(np.clip(rows[0], 300, 560))
            head = ht if new_seg else 0.85 * head + 0.15 * ht

        comp = frame.copy()
        shake = (0, 0)
        for e in events:
            al = env(t, e["t0"], e["t1"], 0.12 if e["slam"] else 0.25)
            if al <= 0:
                continue
            img = e["img"]
            if e["slam"]:
                sc = 1.25 - 0.25 * ease((t - e["t0"]) / 0.12)
                if t - e["t0"] < 0.2:
                    j = min(int((t - e["t0"]) * FPS), 5)
                    shake = ((-14, 10, -7, 5, -3, 0)[j], (8, -10, 6, -4, 2, 0)[j])
            else:
                sc = 1.04 - 0.04 * ease((t - e["t0"]) / 0.4)
            sc *= min(1.0, (W - 80) / (img.width * sc))
            gt, gb = img.info.get("glyph", (40, img.height - 40))
            img = img.resize((int(img.width * sc), int(img.height * sc)), Image.BILINEAR)
            y = max(int(head + 18 - gb * sc), 235 - int(gt * sc))
            y += int(24 * (1 - ease((t - e["t0"]) / 0.3)))
            over(comp, img, (W - img.width) // 2, y, al)
        mm = m[..., None]
        comp = frame * mm + comp * (1 - mm)
        last = np.clip(frame, 0, 255).astype(np.uint8)
        if shake != (0, 0):
            im = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
            canvas = Image.new("RGB", (W + 40, H + 40))
            canvas.paste(im, (20 + shake[0], 20 + shake[1]))
            comp = np.asarray(canvas.crop((20, 20, 20 + W, 20 + H)), np.float32).copy()
        if hasattr(film, "front"):
            film.front(comp, t, rm)
        for g in caps:
            if g["t0"] <= t < g["t1"]:
                ci = render_caption(g, t, capf)
                if ci.width > W - 96:
                    ci = ci.resize((W - 96, int(ci.height * (W - 96) / ci.width)), Image.LANCZOS)
                over(comp, ci, (W - ci.width) // 2, 1330, env(t, g["t0"], g["t1"], 0.08, 0.06))
                break
        enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())

    if not only and last is not None:
        lg = logo.resize((520, 520), Image.LANCZOS)
        name_img = plain("EDISON AMBRISTER", font(MONT_B, 50), IVORY, 10, 0.3)
        foot = plain("DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", font(MONT_M, 30), PALE_GOLD, 4, 0.3)
        for j in range(int(END_CARD * FPS)):
            u = ease(j / 18)
            comp = last.astype(np.float32) * (1 - 0.9 * u) + np.array(OBSIDIAN, np.float32) * 0.9 * u
            over(comp, lg, (W - 520) // 2, 560, u)
            over(comp, name_img, (W - name_img.width) // 2, 1110, u)
            over(comp, foot, (W - foot.width) // 2, 1195, u)
            enc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print("frames", n_out, "-> output", round(rm.total, 2), "s (source", round(k / FPS, 2), "s)")
    return keep, rm, events


# ---------------------------------------------------------------- sound
def mix(src, out_dir, film):
    """Voice assembled on the cut timeline (6 ms fades at every joint) + bed + designed SFX."""
    out = pathlib.Path(out_dir)
    keep = [tuple(x) for x in json.load(open(out / "edl.json"))["keep"]]
    rm = Remap(keep)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", str(SR),
                    "-af", "highpass=f=85,afftdn=nf=-28,"
                    "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=160:makeup=2",
                    str(out / "voice_raw.wav")], check=True)
    raw, _ = sf.read(out / "voice_raw.wav", dtype="float32")
    f = int(0.006 * SR)
    ramp = np.linspace(0, 1, f, dtype=np.float32)
    parts = []
    for s, e in keep:
        p = raw[int(s * SR):int(e * SR)].copy()
        if len(p) > 2 * f:
            p[:f] *= ramp
            p[-f:] *= ramp[::-1]
        parts.append(p)
    voice = np.concatenate(parts)
    speech_end = len(voice)
    total = speech_end + int(END_CARD * SR)
    voice = np.pad(voice, (0, total - len(voice)))

    subprocess.run([sys.executable, "-I", str(ROOT / "video/tools/make_music.py"),
                    str(out / "music_src.wav"), "--seconds", f"{total / SR + 1:.2f}"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "music_src.wav"), "-ac", "1",
                    "-ar", str(SR), str(out / "music_48k.wav")], check=True)
    music, _ = sf.read(out / "music_48k.wav", dtype="float32")
    music = np.pad(music[:total], (0, max(0, total - len(music))))
    envv = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = np.clip(1 - envv / (envv.max() * 0.18), 0.35, 1.0)
    level = np.full(total, 0.16)
    level[speech_end:] = np.linspace(0.16, 0.42, total - speech_end)
    fade = np.ones(total)
    fade[:SR] = np.linspace(0, 1, SR)
    fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR))
    music = music / (np.abs(music).max() + 1e-9) * level * duck * fade

    sfx = np.zeros(total, np.float32)

    def place(t, clip):
        i = int(t * SR)
        j = min(total, i + len(clip))
        if 0 <= i < total:
            sfx[i:j] += clip[:j - i]

    soft = whoosh(gain=0.055)  # regular titles: soft (Edison's preference)
    for e in remap_events(film.build_events(), rm):
        place(e["t0"] - (0.02 if e["slam"] else 0.22), impact() if e["slam"] else soft)
    for _, s in getattr(film, "STEPS", []):
        place(rm(s) - 0.2, tick(0.16))
    place(speech_end / SR - 0.35, whoosh(0.6, 0.16))
    place(speech_end / SR + 0.1, impact(0.4))

    for nm, a in (("voice", voice), ("music", music), ("sfx", sfx)):
        sf.write(out / f"{nm}.wav", a, SR)
    m = voice + music + sfx
    sf.write(out / "mix.wav", m / max(1.0, np.abs(m).max() / 0.95), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "mix.wav"), "-af",
                    "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,"
                    "alimiter=limit=0.35:attack=1:release=60:level=false,"
                    "loudnorm=I=-14:TP=-2.5:LRA=7", "-ar", str(SR), str(out / "mix_final.wav")],
                   check=True)
    print("mix", round(total / SR, 2), "s")


def finish(out_dir, final_mp4):
    out = pathlib.Path(out_dir)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "video-only.mp4"),
                    "-i", str(out / "mix_final.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-maxrate", "7M",
                    "-bufsize", "14M", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                    "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k",
                    "-ar", str(SR), "-shortest", "-movflags", "+faststart", str(final_mp4)], check=True)
