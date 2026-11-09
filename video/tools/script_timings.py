"""Word timings for captions when the script is known (our own TTS voiceovers).

Finds the speech spans in each voice clip by energy, matches them to the
sentences of its line, and spreads each sentence's words across its span by
length. Accurate to roughly a word; use `hyperframes transcribe` (Whisper) for
footage whose words aren't known in advance.

Writes a JS file that sets window.CAPTION_WORDS = [{text, start, end}, ...].

    python tools/script_timings.py OUT.js START:CLIP.wav:"Line text" [...]
"""
import json
import re
import sys

import numpy as np
import soundfile as sf

FRAME = 0.01  # analysis hop in seconds
MIN_GAP = 0.12  # a pause at least this long splits sentences


def speech_spans(path):
    audio, sr = sf.read(path, always_2d=True)
    mono = audio.mean(axis=1)
    hop = int(sr * FRAME)
    rms = np.array([np.sqrt(np.mean(mono[i:i + hop] ** 2)) for i in range(0, len(mono) - hop, hop)])
    voiced = rms > max(rms.max() * 0.03, 1e-4)
    spans, start, quiet = [], None, 0
    for i, v in enumerate(voiced):
        if v:
            start = i if start is None else start
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet * FRAME >= MIN_GAP:
                spans.append((start * FRAME, (i - quiet + 1) * FRAME))
                start, quiet = None, 0
    if start is not None:
        spans.append((start * FRAME, (len(voiced) - quiet) * FRAME))
    return spans


def line_words(offset, path, text):
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
    spans = speech_spans(path)
    if len(spans) != len(sentences):  # pauses don't line up with sentences: treat as one span
        spans, sentences = [(spans[0][0], spans[-1][1])], [" ".join(sentences)]
    words = []
    for (s, e), sentence in zip(spans, sentences):
        tokens = sentence.split()
        weights = np.array([len(re.sub(r"\W", "", t)) + 2 for t in tokens], dtype=float)
        edges = s + np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * (e - s)
        words += [{"text": t, "start": round(offset + a, 2), "end": round(offset + b, 2)}
                  for t, a, b in zip(tokens, edges[:-1], edges[1:])]
    return words


def main():
    out, specs = sys.argv[1], sys.argv[2:]
    words = []
    for spec in specs:
        start, path, text = spec.split(":", 2)
        words += line_words(float(start), path, text)
    with open(out, "w") as f:
        f.write("window.CAPTION_WORDS = " + json.dumps(words, indent=1) + ";\n")
    print(f"{len(words)} words -> {out}")


if __name__ == "__main__":
    main()
