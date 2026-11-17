# CALISTHENICS WORKS LEGS: production notes (v1)

Made with the saved style and the cut rule (shared standard §4b). Built by `tools/build_ea_calisthenics_legs.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

## Source
- Drive video, iPhone HEVC 4K rotated to vertical, 30 fps, 51.8 s.
- A wide outdoor shot: the point, squats and lunges, the combo demo (25–39 s) with Edison counting reps out loud, and the 500 goal.

## Edit
- **Length:** 51.8 s → 42.6 s in 4 segments, plus the 2.5 s CTD end card.
- **Cut:** the "And then" opener, a filler "like", the "a good… a good" stutter, the walk-off, and dead air.
- **Protected:** the combo demo is excluded from dead-air trimming, so every rep plays in full.
- **Words:** 62 of 67 kept.

## Transcript
- During the demo Parakeet heard "plus one / plus two / That's true". Whisper heard the rep count **"That's one / That's two / That's three"**, which fits the demo, so the captions use Whisper's wording.
- "usually you can combine it" also follows Whisper.
- "how calisthenics is work legs" is left as both models heard it.

## Picture and sound
- **Titles:** head-tracked depth titles: CALISTHENICS → LEGS. → ALWAYS. → SQUATS. → LUNGES. → COMBINE IT. → MY FAVORITE. → **1 → 2 → 3** (on Edison's own count) → AS MANY AS POSSIBLE. → **500.**
- **Picture:** word-timed captions, light grade, no vignette, punch-ins on cuts, CTD end card.
- **Voice:** reassembled with 6 ms fades. High-pass, FFT denoise and compression.
- **Music:** the default original bed (level 0.22, to carry the demo).
- **SFX:** synthesized. Soft whooshes on regular titles; hits on LEGS., the 1/2/3 count and 500.

## Delivery checks (`calisthenics-legs-v1.mp4`)
- 1080 × 1920, 30 fps, 1,352 frames, 45.1 s (A/V lengths match).
- Full decode with no errors. −14.9 LUFS, −3.3 dBTP. 40 MB.
- Every title was inspected at phone size.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
