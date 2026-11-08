# 50 MORE DAYS: production notes (v1)

Made with the `edison-full-message` skill. Built by `tools/build_ea_50_more_days.py` (picture) and `tools/mix_ea_50_more_days.py` (sound).

## Source
- `IMG_8021.MOV` from Edison's Drive: iPhone HEVC, 2160 × 3838, 30 fps, BT.709 SDR, AAC stereo, 77.87 s. It is a single take, a low-angle outdoor selfie with no cuts.
- Kept outside the repo; the original file is unchanged in Drive.

## Message retention
- **100%.** The whole take plays in order at natural speed: 250 of 250 transcribed words, nothing removed and nothing retimed.
- Transcript: local NVIDIA Parakeet TDT 0.6B v2 (sherpa-onnx), cross-checked with Whisper small.en. No audio left this session.
- **Line to confirm (around 36 s):** Parakeet heard "But most likely, you're gonna change yourself." Whisper heard "most likely you can change yourself." From the context, Edison may have said "you're **not** gonna" or "you **can't**". The caption shows Parakeet's wording. If it's wrong, fix the words in `transcript-words.json` and re-render.
- Around 57 s, the two models agree on "because you cannot get the habits…", and the caption is fixed to read that way as one sentence.

## Picture
- **Grade:** a light, natural one, because the footage is sunny daylight and forcing it dark would look fake. Slight contrast lift, saturation 0.93, a touch of warmth in the mids, cooler sky, soft vignette.
- **Depth titles:** 24 thesis words placed in the sky behind Edison's head. A selfie segmenter (MediaPipe, run on LiteRT) makes a mask for every frame, and the sky colour is used to tighten the hair and shoulder edges. Each title follows his head height frame by frame so it overlaps by about 18 px.
- **Fonts:** Barlow Condensed ExtraBold for ivory, gold and crimson titles; Bodoni Moda Black for thesis words (COMPLETELY, START NOW, HABITS, COMMITTED, HIGHER SELF, HIGHER HEIGHTS).
- **Front graphics:**
  - "2026 · % GONE" progress card at 9.7–14.7 s. 315 of 365 days is derived from Edison's own "50 more days" (86.3%), not an outside statistic.
  - "NEW YEAR, NEW ME" types on, then is struck through on "Nonsense."
- **Captions:** word-timed ivory captions with the current word in pale gold, 2–4 words per group, no box, at y ≈ 1330. The same text is in `captions.srt`.
- **Motion:** slam scale and shake on NOTHING / NONSENSE / WHY / LOSER and the second START NOW, plus a slow 3.5% push-in over the closing 14 s.
- **End card (2.5 s):** clean graded frame fading to obsidian, Cut Throat Discipline logo, EDISON AMBRISTER, and the DISCIPLINE - ACCOUNTABILITY - CONSISTENCY footer.
- All effects are baked into the MP4. There is no editable DaVinci Resolve project for this version.

## Sound
- **Voice:** Edison's original recording. High-pass 85 Hz, FFT denoise, gentle compression. This is basic cleanup, not neural voice isolation (no separation model was available here). No retiming.
- **Music:** original A-minor bed from `video/tools/make_music.py` (no samples or licence needed), ducked under speech and lifted into the end card.
- **SFX:** all **synthesized** designed effects: air whooshes on title entries, sub-boom impacts on the slams, ticks on the progress card.
- **Delivery mix:** −14.4 LUFS integrated, −2.4 dBTP.

## Delivery checks (`50-more-days-v1.mp4`)
- 1080 × 1920, 30 fps, H.264 High / AAC 48 kHz, 2,411 frames, 80.37 s. Video 80.367 s and audio 80.362 s.
- The whole file decodes with no errors and no black gaps.
- Frames sampled at every title beat and on the end card were inspected at phone size.
- **Not done:** a continuous real-time watch and a listening pass. Meters and sampled frames aren't the same as watching and listening, so Edison should watch it once before posting.

## Not done
- Scheduled (not yet posted) in Metricool for Wed 11 Nov 2026, 4:00 PM ET, to Instagram and TikTok.
