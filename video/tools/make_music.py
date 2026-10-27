"""Generate an original, royalty-free music bed for Reels (no samples, no models).

Dark, steady A-minor pulse at 96 BPM: sub bass, soft pad, kick and hi-hats.
Deterministic: the same arguments always produce the same file.

    python tools/make_music.py OUT.wav --seconds 11
"""
import argparse
import wave

import numpy as np

SR = 44100
BPM = 96
BEAT = 60 / BPM
# Am - F - C - G, one chord per bar (4 beats); root frequencies plus triad notes.
CHORDS = [
    (55.00, [220.00, 261.63, 329.63]),  # Am
    (43.65, [174.61, 220.00, 261.63]),  # F
    (65.41, [196.00, 261.63, 329.63]),  # C
    (49.00, [196.00, 246.94, 293.66]),  # G
]


def envelope(n, attack, release):
    env = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    env[:a] = np.linspace(0, 1, a)
    env[n - r:] *= np.linspace(1, 0, r)
    return env


def render(seconds):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    rng = np.random.default_rng(7)

    bar = 4 * BEAT
    for i, start in enumerate(np.arange(0, seconds, bar)):
        root, triad = CHORDS[i % len(CHORDS)]
        s, e = int(start * SR), min(int((start + bar) * SR), n)
        seg = t[s:e] - start
        env = envelope(e - s, 0.4, 0.4)
        bass = np.sin(2 * np.pi * root * seg) + 0.3 * np.sin(2 * np.pi * root * 2 * seg)
        pad = sum(np.sin(2 * np.pi * f * seg + 0.3 * np.sin(2 * np.pi * 0.3 * seg)) for f in triad)
        out[s:e] += env * (0.35 * bass + 0.06 * pad)

    for k, start in enumerate(np.arange(0, seconds, BEAT / 2)):
        s = int(start * SR)
        if k % 2 == 0:  # kick on every beat: pitch-dropping sine
            m = min(int(0.35 * SR), n - s)
            kt = np.arange(m) / SR
            freq = 50 + 90 * np.exp(-kt * 30)
            out[s:s + m] += 0.6 * np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-kt * 9)
        m = min(int(0.05 * SR), n - s)  # hi-hat on every eighth: short noise burst
        hat = rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 90)
        out[s:s + m] += (0.05 if k % 2 else 0.025) * np.diff(hat, prepend=0)

    out *= envelope(n, 0.3, 1.5)
    out /= np.max(np.abs(out)) / 0.8
    stereo = np.stack([out, np.roll(out, 40)], axis=1)  # slight width
    return (stereo * 32767).astype(np.int16)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--seconds", type=float, default=11)
    args = p.parse_args()
    with wave.open(args.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(render(args.seconds).tobytes())


if __name__ == "__main__":
    main()
