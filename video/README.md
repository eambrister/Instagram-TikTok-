# Video pipeline (HyperFrames)

Branded 1080×1920 Reels rendered from HTML. Free, local, no API keys.

## Setup (new session)

```bash
cd video
npm ci                                   # HyperFrames 0.8.150 + GSAP
python3 -m venv .venv && .venv/bin/pip install kokoro-onnx soundfile   # only to make new voiceovers
source env.sh                            # uses the container's Chrome, disables telemetry
```

## Make the sample Reel

```bash
cd sample-reel
# 1. Voiceover lines (Kokoro-82M, voice am_michael); activate .venv first
npx hyperframes tts "Motivation fades." -v am_michael -o assets/audio/vo1.wav
# 2. Original music bed (no samples, no license needed)
../.venv/bin/python -I ../tools/make_music.py assets/audio/music.wav --seconds 11
# 3. Validate, render, and normalize loudness to -14 LUFS
npx hyperframes check
npx hyperframes render -o /tmp/reel_raw.mp4
../tools/finish_audio.sh /tmp/reel_raw.mp4 ../../outputs/edison-ambrister-sample-reel/reel.mp4
```

Audio timing lives in `index.html` (`<audio data-start=… data-volume=…>`). Music sits at
`data-volume="0.13"`, about 11 dB under the voice.

## Stop

Render exits on its own. Preview: `npx hyperframes preview --background` / `--stop`.
