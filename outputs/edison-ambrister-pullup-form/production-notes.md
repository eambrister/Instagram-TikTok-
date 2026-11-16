# NO HALF-REP PULL-UPS: production notes (v1)

Made with the saved style and the cut rule (shared standard §4b). Built by `tools/build_ea_pullup_form.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

## Source
- Drive video, iPhone HEVC 4K rotated to vertical, 30 fps, 58.3 s.
- A wide outdoor shot at the bars: the rule, a full-rep demo (26–38 s), a half-rep demo (45–51 s) and the verdict.

## Edit
- **Length:** 58.3 s → 49.5 s in 4 segments, plus the 2.5 s CTD end card.
- **Cut:** the walk-off at the end, dead air in the talking parts, and the repeated first "That's what I want to see." (restated as "This is what I want to see" right before the demo).
- **Protected:** both demos are excluded from dead-air trimming, so every rep plays in full.
- **Captions:** each word's on-screen time is capped, so captions clear during the silent demos.
- **Words:** 72 of 78 kept.

## Picture and sound
- **Titles:** head-tracked depth titles in the sky: NO HALF REPS. → FULL LOCKOUT → CHIN OVER BAR → 90° → FULL REP. (gold, over the good demo) → NOT THIS. → HALF REP. (crimson, over the bad demo) → GARBAGE.
- **Picture:** word-timed captions, light grade, no vignette, alternating punch-ins on cuts, CTD end card.
- **Voice:** reassembled with 6 ms fades. High-pass, FFT denoise and compression.
- **Music:** original bed.
- **SFX:** synthesized. Soft whooshes on regular titles; hits on NO HALF REPS. and GARBAGE.
- **Loudness:** the final pass used an oversampled limiter, now built into the engine: −13.9 LUFS, −2.6 dBTP.

## Delivery checks (`pullup-form-v1.mp4`)
- 1080 × 1920, 30 fps, 1,561 frames, 52.0 s (A/V lengths match).
- Full decode with no errors. 41 MB.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
