"""Local word-timestamp transcription with faster-whisper.

Usage: python -I transcribe.py <audio> <model_dir> <out.json> [--language en] [--prompt "..."] [--threads N]

Audio is decoded by FFmpeg into a float array (avoids PyAV version issues).
Output: {"engine", "model", "language", "words": [{"text","start","end","p"}], "segments": [...]}
"""
import argparse
import json
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel


def decode(path: str) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("model_dir")
    ap.add_argument("out")
    ap.add_argument("--language", default="en")
    ap.add_argument("--prompt", default="")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()

    model = WhisperModel(a.model_dir, device="cpu", compute_type="int8", cpu_threads=a.threads)
    segments, info = model.transcribe(
        decode(a.audio),
        language=a.language or None,
        word_timestamps=True,
        initial_prompt=a.prompt or None,
        condition_on_previous_text=False,
        beam_size=5,
    )
    words, segs = [], []
    for s in segments:
        segs.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()})
        for w in s.words or []:
            t = w.word.strip()
            if t:
                words.append({"text": t, "start": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 3)})
    with open(a.out, "w") as f:
        json.dump({"engine": "faster-whisper", "model": a.model_dir, "language": info.language,
                   "words": words, "segments": segs}, f, indent=1)
    print(f"transcribed {len(words)} words", file=sys.stderr)


if __name__ == "__main__":
    main()
