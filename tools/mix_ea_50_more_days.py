"""Audio for "50 MORE DAYS": Edison's original voice (cleaned), an original music bed and
designed (synthesized) SFX timed to the graphics in build_ea_50_more_days.py.

    python3 -I tools/mix_ea_50_more_days.py SRC.MOV OUT_DIR [FILM_MODULE]

FILM_MODULE (default build_ea_50_more_days) supplies build_events() and optional STEPS.

Writes voice.wav, music.wav, sfx.wav (stems, pre-limiter) and mix.wav.
Voice is never retimed or replaced. No speech-separation model is used here:
cleanup is high-pass + FFT denoise + gentle compression.
"""
import pathlib
import subprocess
import sys
import wave

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import importlib  # noqa: E402

from build_ea_50_more_days import END_CARD  # noqa: E402

SR = 48000


def read_wav(p):
    with wave.open(str(p)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels()).mean(1) if w.getnchannels() > 1 else a


def write_wav(p, a):
    a = np.clip(a, -1, 1)
    st = np.stack([a, a], 1) if a.ndim == 1 else a
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def whoosh(dur=0.45, gain=0.10):
    n = int(dur * SR)
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n)
    # sweep a one-pole low-pass upward for an airy rise
    out = np.zeros(n)
    y = 0.0
    for i in range(n):
        a = 0.02 + 0.25 * (i / n) ** 2
        y += a * (x[i] - y)
        out[i] = y
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return out / (np.abs(out).max() + 1e-9) * e * gain


def impact(gain=0.55):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 95 * np.exp(-t * 5) + 38
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    rng = np.random.default_rng(3)
    crack = rng.standard_normal(n) * np.exp(-t * 60) * 0.5
    return (sub + crack) * gain


def tick(gain=0.12):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120) * gain


def main():
    src, out = sys.argv[1], pathlib.Path(sys.argv[2])
    film = importlib.import_module(sys.argv[3] if len(sys.argv) > 3 else "build_ea_50_more_days")
    build_events = film.build_events
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", str(SR),
                    "-af", "highpass=f=85,afftdn=nf=-28,"
                    "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=160:makeup=2",
                    str(out / "voice_raw.wav")], check=True)
    voice = read_wav(out / "voice_raw.wav")
    total = len(voice) + int(END_CARD * SR)
    voice = np.pad(voice, (0, total - len(voice)))

    secs = total / SR + 1
    subprocess.run([sys.executable, "-I", str(ROOT / "video/tools/make_music.py"),
                    str(out / "music_src.wav"), "--seconds", f"{secs:.2f}"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "music_src.wav"), "-ac", "1",
                    "-ar", str(SR), str(out / "music_48k.wav")], check=True)
    music = read_wav(out / "music_48k.wav")[:total]
    music = np.pad(music, (0, total - len(music)))
    # duck under speech (envelope follower on the voice), lift into the end card
    env = np.abs(voice)
    k = int(0.25 * SR)
    env = np.convolve(env, np.ones(k) / k, "same")
    duck = np.clip(1 - env / (env.max() * 0.18), 0.35, 1.0)
    level = np.full(total, 0.16)
    speech_end = len(voice) - int(END_CARD * SR)
    level[speech_end:] = np.linspace(0.16, 0.42, total - speech_end)
    fade = np.ones(total)
    fade[:int(1.0 * SR)] = np.linspace(0, 1, int(1.0 * SR))
    fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR))
    music = music / (np.abs(music).max() + 1e-9) * level * duck * fade

    sfx = np.zeros(total)

    def place(t, clip):
        i = int(t * SR)
        j = min(total, i + len(clip))
        if 0 <= i < total:
            sfx[i:j] += clip[:j - i]

    w = whoosh(gain=0.055)  # regular-title whooshes ~5 dB softer (Edison, v2); punch-word hits unchanged
    for e in build_events():
        if e["kind"] == "depth":
            if e.get("slam"):
                place(e["t0"] - 0.02, impact())
            else:
                place(e["t0"] - 0.22, w)
        elif e["kind"] == "progress":
            for i in range(10):
                place(e["t0"] + 0.3 + i * 0.22, tick())
        elif e["kind"] == "newyear":
            place(30.30, impact(0.35))
    for _, s in getattr(film, "STEPS", []):  # step-tracker light-ups
        place(s - 0.2, tick(0.16))
    place(speech_end / SR - 0.35, whoosh(0.6, 0.16))
    place(speech_end / SR + 0.1, impact(0.4))

    write_wav(out / "voice.wav", voice)
    write_wav(out / "music.wav", music)
    write_wav(out / "sfx.wav", sfx)
    mix = voice + music + sfx
    write_wav(out / "mix.wav", mix / max(1.0, np.abs(mix).max() / 0.95))
    print("mix", total / SR, "s ->", out / "mix.wav")


if __name__ == "__main__":
    main()
