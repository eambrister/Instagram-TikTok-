"""Original instrumental bed, synthesised from scratch (no samples, no third-party audio).

Usage: python -I make_music.py <out.wav> <seconds> [--bpm 84] [--seed 1] [--mood discipline|calm|hiphop]

--mood hiphop: a boom-bap beat (kick, snare, soft swung hats), electric-piano minor 7ths and an 808-style
bass, at 88 BPM unless --bpm is given.

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


def hiphop(seconds: float, bpm: float, rng: np.random.Generator) -> np.ndarray:
    """Boom-bap bed: drums carry the groove; keys and bass stay under 2 kHz, hats sit quietly above the voice."""
    beat = 60 / bpm
    bar = 4 * beat
    total = seconds + 2.0
    n = int(total * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    swing = beat * 0.5 * 0.16  # late off-beat 8ths

    # Electric piano: minor 7th voicings, two hits per bar (1 and the "and" of 2), soft bell tone.
    chords = [["A", "C", "E", "G"], ["F", "A", "C", "E"], ["D", "F", "A", "C"], ["E", "G", "B", "D"]]
    for b in range(int(np.ceil(total / bar)) + 1):
        for off, g in ((0.0, 1.0), (beat * 1.5 + swing, 0.6)):
            s0 = b * bar + off
            i0, i1 = int(s0 * SR), min(n, int((s0 + beat * 2.2) * SR))
            if i0 >= n:
                continue
            tt = t[i0:i1] - s0
            env = np.exp(-tt / 0.9) * np.clip(tt / 0.008, 0, 1)
            for k, note in enumerate(chords[b % len(chords)]):
                f = hz(note, 3 if k < 2 else 4) * (1 + rng.uniform(-0.001, 0.001))
                v = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.15)) * env * g * 0.05
                out[i0:i1, 0] += v * (0.6 if k % 2 else 0.4)
                out[i0:i1, 1] += v * (0.4 if k % 2 else 0.6)
    out = lowpass(out, 1800, 2.5)

    drums = np.zeros(n)
    hats = np.zeros(n)
    for i in range(int(total / bar) + 1):
        b0 = i * bar
        # Kick: 1, the "and" of 2, 3 (boom-bap), sub sweep.
        for off, g in ((0.0, 1.0), (beat * 1.5 + swing, 0.7), (beat * 2, 0.9)):
            s = b0 + off
            i0, i1 = int(s * SR), min(n, int((s + 0.4) * SR))
            if i0 >= n:
                continue
            tt = t[i0:i1] - s
            sweep = 48 + 90 * np.exp(-tt / 0.025)
            drums[i0:i1] += np.sin(2 * np.pi * np.cumsum(sweep) / SR) * np.exp(-tt / 0.16) * 0.55 * g
        # Snare: 2 and 4, a tone plus band-limited noise.
        for off in (beat, beat * 3):
            s = b0 + off
            i0, i1 = int(s * SR), min(n, int((s + 0.25) * SR))
            if i0 >= n:
                continue
            tt = t[i0:i1] - s
            noise = rng.normal(0, 1, i1 - i0)
            drums[i0:i1] += (0.25 * np.sin(2 * np.pi * 185 * tt) * np.exp(-tt / 0.05) + 0.3 * noise * np.exp(-tt / 0.07))
        # Hats: swung 8ths, very quiet.
        for e in range(8):
            s = b0 + e * beat / 2 + (swing if e % 2 else 0)
            i0, i1 = int(s * SR), min(n, int((s + 0.05) * SR))
            if i0 >= n:
                continue
            tt = t[i0:i1] - s
            hats[i0:i1] += rng.normal(0, 1, i1 - i0) * np.exp(-tt / 0.012) * (0.05 if e % 2 else 0.08)
    drums = lowpass(drums, 5000, 2)
    hats = highpass(hats, 7000)

    # 808-style bass on the kicks, gliding root per bar.
    roots = ["A", "F", "D", "E"]
    bass = np.zeros(n)
    for i in range(int(total / bar) + 1):
        f = hz(roots[i % len(roots)], 1)
        for off, ln in ((0.0, beat * 1.4), (beat * 2, beat * 1.8)):
            s = i * bar + off
            i0, i1 = int(s * SR), min(n, int((s + ln) * SR))
            if i0 >= n:
                continue
            tt = t[i0:i1] - s
            bass[i0:i1] += np.tanh(1.6 * np.sin(2 * np.pi * f * tt)) * np.exp(-tt / 0.7) * np.clip(tt / 0.01, 0, 1) * 0.3
    bass = lowpass(bass, 220, 2)
    out += (drums + bass)[:, None]
    out[:, 0] += hats * 0.9
    out[:, 1] += np.roll(hats, 240)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("seconds", type=float)
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--mood", default="discipline")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    if a.mood == "hiphop":
        finish(hiphop(a.seconds, a.bpm or 88, rng), a.seconds, a.out)
        return
    a.bpm = a.bpm or 84
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

    finish(out, a.seconds, a.out)


def finish(out: np.ndarray, seconds: float, path: str) -> None:
    # Fades and normalisation to -1 dBFS peak (the mixer sets the final level under the voice).
    out = out[: int(seconds * SR)]
    m = out.shape[0]
    fade = np.ones(m)
    fi, fo = int(1.5 * SR), int(2.5 * SR)
    fade[:fi] = np.linspace(0, 1, fi) ** 2
    fade[-fo:] = np.linspace(1, 0, fo) ** 2
    out *= fade[:, None]
    out *= 10 ** (-1 / 20) / max(1e-9, np.abs(out).max())
    pcm = (out * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main()
