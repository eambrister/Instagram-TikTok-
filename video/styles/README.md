# Edit styles

Named looks and treatments for Edison Ambrister videos. Ask for one by name ("use
captions-gold", "add voiceover-music") and Claude applies it to the video you're working on.
Nothing here runs or installs until it's requested.

| Style | What it does | Status | Cost |
|---|---|---|---|
| `brand-kinetic-type` | Big Barlow Condensed headlines on obsidian, gold accents, logo upper-left, footer rule. The base look of [`sample-reel`](../sample-reel/index.html). | Ready | $0 |
| `voiceover-music` | Kokoro voice (default `am_michael`) per scene, original music bed 11 dB under the voice, loudness normalized to -14 LUFS. | Ready | $0 |
| `captions-gold` | Word-by-word captions: up to 3 words per screen, the spoken word sits on a gold pill. Lower third by default, or centered. [Preview](../../outputs/edit-style-previews/captions-gold.mp4) | Ready for our own voiceovers; for other footage needs `huggingface.co` allowed | $0 |
| `catalog:<name>` | Any HyperFrames catalog block, pulled with `npx hyperframes add <name>` and adapted to 1080×1920, brand fonts and colors, local GSAP. | On request | $0 |
| `clip-long-video` | Cut a long recording or YouTube video into ranked 9:16 Shorts (AI-Youtube-Shorts-Generator, MIT). | On request: `styles/clip-long-video/install.sh` | ≈ cents per video (Gemini or OpenAI key) |

## captions-gold

Files: `captions-gold/captions-gold.css`, `captions-gold/captions-gold.js`.

1. Make word timings.
   - Our own voiceover (script known):
     ```bash
     .venv/bin/python -I tools/script_timings.py <project>/assets/captions.words.js \
       "0.15:<project>/assets/audio/vo1.wav:Motivation fades." "2.4:<project>/assets/audio/vo2.wav:Discipline shows up."
     ```
     Each argument is `start-seconds:clip.wav:exact line text`, matching the clip's `<audio data-start>`.
   - Any footage: `npx hyperframes transcribe <video> -l en`, then convert its words to
     `window.CAPTION_WORDS`. Requires `huggingface.co` in the environment's allowed domains.
2. Copy the CSS and JS into the project's `assets/` and wire them up:
   ```html
   <link rel="stylesheet" href="assets/captions-gold.css" />
   <div id="captions" class="clip" data-start="0" data-duration="11"></div>  <!-- add data-position="center" to center -->
   <script src="assets/captions.words.js"></script>
   <script src="assets/captions-gold.js"></script>
   <script> /* after creating tl */ CaptionsGold.attach(tl, "#captions"); </script>
   ```
   The host must declare the Barlow Condensed ExtraBold `@font-face`.

## Catalog shortlist that fits the brand

`caption-kinetic-slam`, `caption-editorial-emphasis`, `caption-pill-karaoke`, `caption-clip-wipe`,
`caption-weight-shift`, `mk-callout-highlight`, `mk-progress-stat`. Browse everything with
`npx hyperframes catalog`. Catalog files are 1920×1080 and load fonts and GSAP from CDNs, which
the renderer here can't reach, so they always need the adaptation step.

## clip-long-video

Install on request (about 1 minute), then run in local mode with a key set in the environment
settings, never in chat or a committed file:

```bash
styles/clip-long-video/install.sh
cd .tools/shorts-generator && LLM_PROVIDER=gemini .venv/bin/python main.py "<video path or URL>" --mode local --num-clips 3
```

Its local transcription (faster-whisper) also downloads models from `huggingface.co`.
