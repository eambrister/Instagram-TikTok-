"""Generate an original, royalty-free boom-bap hip hop beat (no samples, no models).

90 BPM, swung 16th hats, punchy kick, snare + clap layer, 808-style sub bass and a dark
minor electric-piano loop (Cm9 - Abmaj7 - Fm9 - G7b9). Deterministic: the same arguments
always give the same file.

    python tools/make_hiphop_beat.py OUT.wav --seconds 60 [--bpm 90]
"""
import argparse
import wave

import numpy as np

SR = 44100


def env(n, a, d, sustain=0.0, r=None):
    """Attack / exponential-decay envelope of n samples."""
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), np.exp(-(t - a) / max(d, 1e-4)))
    return e * (1 - sustain) + sustain


def kick(n):
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.28)
    click = np.random.default_rng(1).standard_normal(n) * env(n, 0.0005, 0.006) * 0.35
    return np.tanh((body + click) * 1.8) * 0.95


def snare(n, seed=2):
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n)
    # band-limit the noise a little (one-pole high-pass then low-pass)
    hp = noise - np.concatenate([[0], noise[:-1]]) * 0.85
    tone = np.sin(2 * np.pi * 190 * t) * env(n, 0.001, 0.05)
    s = hp * env(n, 0.001, 0.12) * 0.55 + tone * 0.5
    clap = np.zeros(n)
    for k, off in enumerate((0.0, 0.009, 0.018)):  # three quick bursts = clap
        i = int(off * SR)
        m = n - i
        clap[i:] += rng.standard_normal(m) * env(m, 0.0005, 0.02 if k < 2 else 0.11) * 0.35
    return np.tanh((s + clap) * 1.4) * 0.8


def hat(n, open_=False, seed=3):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    x = x - np.concatenate([[0, 0], x[:-2]])  # crude high-pass
    return x * env(n, 0.0005, 0.09 if open_ else 0.018) * 0.16


def ep_note(freq, n):
    """Soft electric-piano tone: sine + bell partial, tremolo, slow decay."""
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t)
            + 0.12 * np.sin(2 * np.pi * freq * 3.01 * t) * np.exp(-t * 6))
    trem = 1 + 0.18 * np.sin(2 * np.pi * 4.2 * t)
    return tone * trem * env(n, 0.004, 1.6, sustain=0.0) * 0.11


def sub(freq, n):
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
    return np.tanh(s * 1.5) * env(n, 0.006, 0.55, sustain=0.25) * 0.42


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# one chord per bar: (bass root midi, chord tones midi)
PROG = [
    (36, [60, 63, 67, 70, 74]),   # Cm9
    (44, [56, 60, 63, 67]),       # Abmaj7
    (41, [56, 60, 63, 65, 67]),   # Fm9-ish
    (43, [55, 59, 62, 65, 68]),   # G7b9
]


def build(seconds, bpm):
    beat = 60.0 / bpm
    six = beat / 4
    swing = six * 0.18  # push every off-16th late
    total = int(seconds * SR) + SR
    out = np.zeros((total, 2))

    def place(x, t, pan=0.0, gain=1.0):
        i = int(t * SR)
        j = min(total, i + len(x))
        if i >= total:
            return
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        out[i:j, 0] += x[:j - i] * gain * l * 1.41
        out[i:j, 1] += x[:j - i] * gain * r * 1.41

    K, S = kick(int(0.6 * SR)), snare(int(0.4 * SR))
    H, HO = hat(int(0.12 * SR)), hat(int(0.3 * SR), True)
    bar = beat * 4
    nbars = int(seconds / bar) + 1
    # boom-bap kick pattern on 16th steps
    kicks = [0, 7, 10]
    kicks_alt = [0, 3, 7, 10, 14]
    for b in range(nbars):
        t0 = b * bar
        root, chord = PROG[b % 4]
        for step in (kicks_alt if b % 4 == 3 else kicks):
            place(K, t0 + step * six + (swing if step % 2 else 0))
        for step in (4, 12):
            place(S, t0 + step * six, pan=0.05)
        for step in range(16):
            tt = t0 + step * six + (swing if step % 2 else 0)
            if step in (14,) and b % 2 == 1:
                place(HO, tt, pan=0.3)
            else:
                place(H, tt, pan=0.3, gain=1.0 if step % 4 == 0 else 0.6)
        # keys: chord hit on 1, a softer re-voice on the "and" of 3
        for k, m in enumerate(chord):
            place(ep_note(midi(m), int(bar * SR)), t0 + k * 0.012, pan=-0.25)
            place(ep_note(midi(m + 12), int(beat * 2 * SR)) * 0.45, t0 + 2.5 * beat + k * 0.01, pan=-0.35)
        # 808-style bass: root on 1, octave-pickup on the "a" of 2, root on 3
        place(sub(midi(root - 12), int(1.5 * beat * SR)), t0)
        place(sub(midi(root), int(0.4 * beat * SR)) * 0.7, t0 + 7 * six + swing)
        place(sub(midi(root - 12), int(1.4 * beat * SR)), t0 + 10 * six)

    # gentle master: soft clip + fade in/out
    out = np.tanh(out * 0.9)
    n = int(seconds * SR)
    out = out[:n]
    fi, fo = int(0.25 * SR), int(1.5 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return out / (np.abs(out).max() + 1e-9) * 0.89


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--seconds", type=float, default=60)
    p.add_argument("--bpm", type=float, default=90)
    a = p.parse_args()
    x = build(a.seconds, a.bpm)
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
