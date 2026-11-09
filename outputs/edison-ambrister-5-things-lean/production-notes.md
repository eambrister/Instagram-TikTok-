# 5 THINGS TO GET LEAN: production notes (v1)

Made with the `edison-full-message` skill. Built by `tools/build_ea_5_things_lean.py` (picture, reusing the 50 MORE DAYS engine) and `tools/mix_ea_50_more_days.py … build_ea_5_things_lean` (sound).

## Source
- Drive video (iPhone HEVC 3840 × 2160, rotated to vertical), 30 fps, BT.709 SDR, AAC, 101.34 s. It is a single take, an outdoor selfie under blue sky.

## Message retention
- **100%.** The whole take plays in order at natural speed, including pauses and the repeated "steps, steps". All 301 words are kept.
- Transcript: local Parakeet, with Whisper small.en cross-checking the uncertain words.
- Fixed by hand:
  - "Hyrocks" → **HYROX** (Whisper heard "high rocks").
  - "Cross fits" → **CrossFit**.
- **To confirm with Edison:**
  - At 0:62, both models heard "I just do a static"; the caption says **"I just do aesthetics."**
  - At 0:87 and 0:96, the models heard "luck"/"lock"; the captions say **"you have a lack in one of them / these areas."**

## Picture
- **Grade:** the same light daylight grade as 50 MORE DAYS. **No vignette** (standing rule).
- **Depth titles:** head-tracked titles behind Edison: GET LEAN, 5 THINGS, the five step titles, the numbers he says (7–8 HOURS, 10K/15K/20K, 3× · 4× · 5×), RECOVERY., DEFICIT / SURPLUS, CARBS? FATS?, PROTEIN., BEFORE BED., EVERY SINGLE DAY., DO ALL 5., LEAN., FOLLOW THE 5 STEPS., 5 STEPS. EVERY DAY.
- **No "GUARANTEED" titles.** The onboarding rules ban guaranteed-outcome copy, so the spoken "guaranteed" stays in the audio and captions only.
- **Step tracker:** five pills at y ≈ 1478 (SLEEP · CALORIES · PROTEIN · STEPS · TRAINING). The current step is gold, finished steps get a gold check, and all five pulse at "you have a lack in one of them".
- Word-timed captions as in 50 MORE DAYS, followed by a 2.5 s CTD end card.

## Sound
- **Voice:** Edison's original, with high-pass, FFT denoise and gentle compression. This is not neural isolation.
- **Music:** original bed from `video/tools/make_music.py`, ducked under speech.
- **SFX:** all synthesized:
  - Soft, low whooshes on regular titles.
  - Hits on 5 THINGS, PROTEIN., 20K and LEAN.
  - Ticks when each step lights up.
- **Delivery mix:** −14.5 LUFS integrated, −2.4 dBTP.

## Delivery checks (`5-things-lean-v1.mp4`)
- 1080 × 1920, 30 fps, 3,115 frames, 103.83 s (A/V lengths match). Full decode with no errors and no black gaps. 80 MB.
- Frames sampled at every title and tracker change and on the end card were inspected at phone size.
- **Not done:** a continuous real-time watch and a listening pass. Edison should watch it once before posting.
- Not scheduled or posted.
