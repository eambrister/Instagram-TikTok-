"""Original instrumental bed, synthesised from scratch (no samples, no third-party audio).

Usage: python -I make_music.py <out.wav> <seconds> [--bpm 84] [--seed 1] [--mood discipline]

Designed to sit under speech: energy is kept below ~2 kHz (voice clarity band left open), no vocals,
no busy hi-hats, slow attacks. Deterministic for a given seed.
"""
import argparse
import wave

import numpy as np

SR = 48000
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
MOODS = {
    # (chords as note lists, bass roots) — minor, steady, determined
    "discipline": ([["A", "C", "E"], ["F", "A", "C"], ["C", "E", "G"], ["G", "B", "D"]], ["A", "F", "C", "G"]),
    "calm": ([["C", "E", "G"], ["A", "C", "E"], ["F", "A", "C"], ["G", "B", "D"]], ["C", "A", "F", "G"]),
}


def hz(name: str, octave: int) -> float:
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


def lowpass(x: np.ndarray, cutoff: float, slope: float = 2.0) -> np.ndarray:
    spec = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    gain = 1 / np.sqrt(1 + (f / cutoff) ** (2 * slope))
    return np.fft.irfft(spec * (gain[:, None] if x.ndim > 1 else gain), n=x.shape[0], axis=0)


def highpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    spec = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    gain = 1 / np.sqrt(1 + (cutoff / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(spec * (gain[:, None] if x.ndim > 1 else gain), n=x.shape[0], axis=0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("seconds", type=float)
    ap.add_argument("--bpm", type=float, default=84)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--mood", default="discipline")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    chords, roots = MOODS[a.mood]
    beat = 60 / a.bpm
    bar = 4 * beat
    total = a.seconds + 2.0
    n = int(total * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))

    # Pad: additive saw-ish voices (8 harmonics), detuned pairs, panned, crossfaded per bar.
    for b in range(int(np.ceil(total / bar)) + 1):
        c = chords[b % len(chords)]
        s0 = b * bar - 0.6
        i0, i1 = max(0, int(s0 * SR)), min(n, int((s0 + bar + 1.2) * SR))
        if i0 >= i1:
            continue
        tt = t[i0:i1] - s0
        dur = bar + 1.2
        env = np.clip(tt / 0.9, 0, 1) * np.clip((dur - tt) / 0.9, 0, 1)
        env = env ** 1.5
        for k, note in enumerate(c):
            for octave, amp in ((3, 1.0), (4, 0.45)):
                f0 = hz(note, octave)
                for det, pan in ((-0.0035, 0.3), (0.0035, 0.7)):
                    f = f0 * (1 + det + rng.uniform(-0.0005, 0.0005))
                    phase = rng.uniform(0, 2 * np.pi)
                    v = sum(np.sin(2 * np.pi * f * h * tt + phase * h) / h for h in range(1, 9))
                    v *= amp * env * 0.06
                    out[i0:i1, 0] += v * (1 - pan + 0.2 * (k - 1) * 0.3)
                    out[i0:i1, 1] += v * (pan + 0.2 * (1 - k) * 0.3)
    out = lowpass(out, 1400, 2.5)

    # Slow filter "breath": gentle amplitude swell over each 4-bar phrase.
    phrase = 4 * bar
    out *= (0.85 + 0.15 * np.sin(2 * np.pi * t / phrase - np.pi / 2))[:, None]

    # Sub bass on beats 1 and 3, following the chord root.
    bass = np.zeros(n)
    for i in range(int(total / beat) + 1):
        if i % 4 not in (0, 2):
            continue
        s = i * beat
        i0, i1 = int(s * SR), min(n, int((s + beat * 1.8) * SR))
        tt = t[i0:i1] - s
        f = hz(roots[(i // 4) % len(roots)], 1)
        bass[i0:i1] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.9) * np.clip(tt / 0.02, 0, 1) * 0.32

    # Heartbeat pulse: soft pitched kick on 1 and the "and" of 1 (lub-dub), no hats or snares.
    kick = np.zeros(n)
    for i in range(int(total / bar) + 1):
        for off, g in ((0.0, 1.0), (beat * 0.5, 0.55)):
            s = i * bar + off
            i0, i1 = int(s * SR), min(n, int((s + 0.35) * SR))
            if i0 >= n:
                continue
            tt = t[i0:i1] - s
            sweep = 45 + 70 * np.exp(-tt / 0.03)
            kick[i0:i1] += np.sin(2 * np.pi * np.cumsum(sweep) / SR) * np.exp(-tt / 0.12) * 0.42 * g
    low = lowpass(bass + kick, 180, 2)
    out += low[:, None]

    # Air: very quiet filtered noise swell, kept below the voice band.
    air = highpass(lowpass(rng.normal(0, 1, n), 900, 2), 300) * 0.012
    out += np.stack([air, np.roll(air, 2400)], axis=1)

    # Fades and normalisation to -1 dBFS peak (the mixer sets the final level under the voice).
    out = out[: int(a.seconds * SR)]
    m = out.shape[0]
    fade = np.ones(m)
    fi, fo = int(1.5 * SR), int(2.5 * SR)
    fade[:fi] = np.linspace(0, 1, fi) ** 2
    fade[-fo:] = np.linspace(1, 0, fo) ** 2
    out *= fade[:, None]
    out *= 10 ** (-1 / 20) / max(1e-9, np.abs(out).max())
    pcm = (out * 32767).astype("<i2")
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main()
