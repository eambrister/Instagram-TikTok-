# Eddie's automated reel editor

Turns an original iPhone recording into a finished 1080×1920 Reel/TikTok: word-synced captions, conservative trims, motivated zooms, and explainer or tier-board graphics built from what Eddie actually says. No timeline editor.

```bash
npm run edit -- --input "input/my-video.mov" --mode auto
```

Outputs land in `outputs/<video>-<id>/`: `final.mp4`, `preview.mp4`, `cover.jpg`, `captions.srt`, `scene-plan.json`, `qa-report.md`, `qa/` (frames for review).

Or ask Claude Code: **"Edit this in my saved style."** (see `CLAUDE.md`).

## Options

| Flag | Meaning |
|---|---|
| `--mode auto\|talking_head\|explainer\|ranking` | Layout mode (auto picks from the speech) |
| `--intensity light\|medium\|high` | Motion level (default medium) |
| `--direction "keep the pauses, less motion"` | Plain-language notes (mode, motion, pauses, no zooms, no graphics) |
| `--topic "Breakfast habits"` | Small label above the hook / board title (never put in his mouth) |
| `--rankings "Eggs=S, Granola=F"` | Explicit ranking instructions for RANKING mode |
| `--music original` | Compose an original instrumental bed for this video (no licensing needed), kept ~16-23 dB under the voice |
| `--music licensed-media/music/x.mp3` | Use your own licensed track instead, same ducking |
| `--preview-only` | Stop after the short preview |
| `--force` | Ignore completed stages and redo everything |

`npm run batch -- --dir input` edits every video in a folder (memory-aware parallelism). Interrupted jobs resume from the last completed stage.

## Setup

```bash
cd reel-editor
npm install
npm run setup -- --fetch-model   # Python env, fonts, local Whisper model
npm test && npm run typecheck
npm run demo                      # synthetic end-to-end test of all three modes
```

Requirements: Node 20+, Python 3.10+, FFmpeg 6 with libx264 and zscale, ~2 GB free RAM per render tab, ~2 GB disk per minute of 4K source.

### Where to run it (Chromebook)

- **Claude Code on the web (what was used to build this).** Upload the recording to the session and ask Claude to edit it. Nothing to install on the Chromebook; it runs on the cloud container included with your Claude plan. Rendering a 60 s reel takes a few minutes there.
- **Locally on the Chromebook** only if Linux development environment is enabled (Settings → Advanced → Developers → Linux), the Chromebook has ≥ 8 GB RAM and ≥ 15 GB free for Linux. Then `sudo apt install ffmpeg python3-venv`, install Node 20+, and follow Setup. ARM Chromebooks may need a Chromium path via `REMOTION_BROWSER`. This has not been tested on your specific Chromebook.

### Transcription model

Default is local **faster-whisper** (Whisper "small", int8, CPU). Your audio never leaves the machine.

In the build environment Hugging Face was blocked, so `--fetch-model` downloads the same MIT-licensed Whisper-small CTranslate2 conversion from four third-party npm data packages (`@skillninja/shortmovie-telop-model-p0..p3`). Only data files are extracted (no install scripts). The checksum check proves the parts were reassembled intact; it does **not** prove upstream provenance. Where Hugging Face is reachable you can instead place `Systran/faster-whisper-small` (or `-medium` for better accuracy) in `cache/models/...` and point `transcription.local.modelDir` at it.

Optional paid alternative: set `transcription.provider` to `"openai"`, `transcription.openai.enabled` to `true`, and export `OPENAI_API_KEY`. That sends the audio to OpenAI and costs about US$0.006 per minute (check current pricing). It is off by default and never used without both settings.

Transcripts are cached by source content + model config, so revisions never re-transcribe.

## Costs

Remotion is free for individuals and companies up to 3 employees (company license otherwise; see `node_modules/remotion/LICENSE.md`). FFmpeg, Whisper, Inter, Barlow Condensed and OpenCV are free/open. Heading Now and Gotham are commercial fonts you must license yourself. Optional OpenAI transcription is paid.

## Folders

`input/` originals (never modified) · `references/` style references (git-ignored, not used in exports) · `brand-assets/fonts/` licensed fonts · `licensed-media/` owned/licensed objects, B-roll, music + `manifest.json` · `cache/` models, transcripts · `jobs/` per-video working files · `outputs/` deliverables · `config/house-style.json` colours, caption sizes, motion, audio targets.

See `STYLE_ANALYSIS.md` for what was observed in the reference reels and how it maps to settings.
