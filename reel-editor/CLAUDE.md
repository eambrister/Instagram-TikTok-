# Eddie's reel editor: operating instructions for Claude

This folder is an automated editor that turns Eddie's original recordings into 1080×1920 Instagram Reels / TikTok videos. Read this before editing a video or changing the code. The repository-level `../CLAUDE_ONBOARDING.md` describes the wider brand; for reels, the rules below take precedence.

## When Eddie says "Edit this in my saved style"

His saved style (approved on the "Keeping your word… abnormal" reel, Oct 2026) is two passes: this editor, then
the finishing pass in `../claude-edits`. Do both. Add other effects or changes only when he asks for them on that video.

1. Put (or find) the recording in `input/` (a copy; never modify his original) and run:
   `npm run edit -- --input "input/<file>" --mode auto` (add `--topic`, `--intensity`, `--direction` only from his message).
   The house style already sets: backed-out framing (`framing.fullWidthFraction` 0.46: head and shoulders, wall plate
   above, sharp punch-ins), the opening-sentence title **pinned at the top for the whole video** (`hook.pinned`), captions
   at chest level from the first word, and an **original music bed** under his voice (`music.default`; `--music none` turns
   it off, `--music <file>` uses his own licensed track).
   The house style also locks the layout to full-screen talking head with no speech-planned cards or counters
   (`editor.mode`, `editor.speechGraphics`): illustrations come from the finishing pass. `--caption-gap "1.4-4.2"` leaves
   captions out for a finishing-pass graphic that shows those words (e.g. GlassGraph).
   For a ranking video where he states the ranks, pass `--rankings "Item=S, Item=F"` when the spoken parse could be ambiguous.
2. The job renders a short `preview.mp4` first, then the full video. Inspect, don't assume:
   - read `outputs/<job>/qa-report.md`;
   - look at `outputs/<job>/qa/contact-sheet.jpg`, `motion-strip-*.jpg`, `first-frame.jpg`, `last-frame.jpg`;
   - read `jobs/<job>/transcript.txt` for mishearings, and `edl.json` for what was cut.
3. Fix what you find without asking Eddie to touch keyframes:
   - transcript errors: write `jobs/<job>/corrections.json` `[{"at": 12.3, "from": "scan", "to": "scam"}]` and rerun (cached stages are reused);
   - a word the recogniser split in two ("abnormal." then a quiet low-confidence "normal."): `{"at": …, "from": "normal.", "to": "", "join": true}`.
     Never use `"to": ""` alone on a quiet low-confidence word right after a similar word: that cuts the end of his word;
   - wrong mode/intensity/pauses: rerun with `--mode`, `--intensity`, `--direction "keep the pauses"`;
   - layout/style bugs: fix the component or planner, run `npm test` and `npm run typecheck`, rerun.
4. Finishing pass (`../claude-edits/CLAUDE.md` → "Saved reel style"): an illustration card beside his head for each
   phrase, and one key word of his rising behind his head. Run `../claude-edits/tools/style_reel.sh <job> <name>`.
5. Return the finished `claude-edits/out/<name>.mp4`, its cover, captions, and this job's `qa-report.md`. State which checks
   passed, which were not checked, and anything flagged. Never call a video finished if its QA report has a FAIL you have not resolved.

Uncertain names and numbers are flagged, not guessed. Ask Eddie only about those, or about rankings he did not clearly state.

## House style

- Brand: **Eddie**. The Cutthroat Discipline name is retired. Do not invent a surname, handle, logo or tagline; `config/house-style.json` → `brand` holds only what Eddie confirms (currently name only, no on-screen mark).
- Look: bold, premium, cinematic fitness education. Readable first; graphics stay subordinate to what he is saying.
- Captions: uppercase, Gotham (fallback Inter Black), white with a `#FFD84D` active/emphasis word (provisional, configurable), dark outline, restrained shadow; 1–3 words, one line; words appear as spoken; never reveal a claim early.
- Headings: Heading Now (fallback Barlow Condensed ExtraBold). Font fallbacks are always reported.
- Motion: medium by default. Deterministic springs/eases only. Punch-ins 100→108–115 % capped by source resolution; layout switches are hard cuts on phrase boundaries; a visual change roughly every 2–4 s of speech.
- Panels: dark charcoal gradient with a thin accent seam (not the reference creator's purple). Red is not a brand colour; it only appears in tier rows C/D.
- Never: AI-generated people, synthetic presenters, face/body changes, dark edge vignettes, crushed skin tones, stock fitness models, raster image generation (unless Eddie asks), invented numbers/quotes/rankings/testimonials, the reference creator's face/voice/footage/branding.
- Numbers on screen come from Eddie's words (confidence ≥ 0.85) or a supplied source; estimates are labelled ESTIMATE.
- Hooks use his exact opening words.

## Modes

- `TALKING_HEAD`: full-screen speaker, captions, motivated zooms, takeaway cards from his own sentences.
- `EXPLAINER`: hard cuts between full-screen and panel-top/speaker-bottom; counters, comparisons, takeaways.
- `RANKING`: speaker top, S–F board bottom; item enters large when named, flies to its row when the tier is said, and stays.
Auto-selection: ≥ 2 spoken tier placements → RANKING; ≥ 2 spoken quantities with units (or quantities + comparisons ≥ 3) → EXPLAINER; else TALKING_HEAD. Plain-language overrides via `--direction` or `--mode`.

## Pipeline map

`src/pipeline/ingest.ts` (probe, orientation, VFR→CFR, HLG/PQ→SDR tone map, proxy) → `transcribe.ts` (local faster-whisper, content-keyed cache in `cache/transcripts`; OpenAI only if enabled + key set) → `edl.ts` (conservative cuts: lead/tail, confirmed-silent pauses > 0.6 s shortened to 0.3 s, restarts, fillers) → `src/shared/timeline.ts` (frame-snapped segments; one remap for video, audio, captions and graphics) → `captions.ts` (segmentation, emphasis, PIL font fitting, SRT) → `planner.ts` (mode, graphics from speech, layouts, zooms, tier events, placement) → `validate.ts` (rejects gaps, unsupported claims, missing assets) → `render.ts` (Remotion, silent picture) → `audio.ts` (same segments, micro-fades, highpass + light denoise, optional ducked music, two-pass loudnorm −14 LUFS / −1.5 dBTP, measured) → `qa.ts`.
Remotion components: `src/remotion/components/` — CaptionTrack, SpeakerFrame, FloatingCard, Counter, ComparisonPanel, ObjectCallout, TierBoard.

Jobs are isolated in `jobs/<name>-<sha8>/`; `stages.json` makes reruns resume. Deliverables go to `outputs/<job>/`.

## Environment notes

- Needs Node 20+, Python 3.10+, FFmpeg with libx264/zscale. `npm install && npm run setup` (add `-- --fetch-model` on a fresh machine).
- Rendering uses Remotion's headless Chromium; set `REMOTION_BROWSER` to use another Chrome headless shell. A crashed browser is retried once at lower concurrency.
- Remotion license: free for individuals and companies with up to 3 employees; larger companies need a company license (see `node_modules/remotion/LICENSE.md`).
- Publishing is out of scope. Do not connect or post to Instagram/TikTok without separate, explicit authorization from Eddie.
