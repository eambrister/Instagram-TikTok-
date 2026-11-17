# NO HALF-REP PULL-UPS: production notes (v2)

**v2 (Edison's request): hip hop beat.** The original music bed is replaced with an original boom-bap beat from `video/tools/make_hiphop_beat.py`: 90 BPM, swung hats, kick, snare and clap, 808-style sub, and a dark minor keys loop (Cm9–Abmaj7–Fm9–G7b9). It is fully synthesized, with no samples and no licensing needed. It sits about 9 dB under the voice while Edison talks and comes up to carry both silent demos (music level 0.30). The picture is unchanged from v1, which remains in git history.

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
- **Music:** original hip hop beat (v2), ducked under speech.
- **SFX:** synthesized. Soft whooshes on regular titles; hits on NO HALF REPS. and GARBAGE.
- **Loudness:** −14.5 LUFS, −3.3 dBTP (oversampled limiter in the engine).

## Delivery checks (`pullup-form-v2.mp4`)
- 1080 × 1920, 30 fps, 1,561 frames, 52.0 s (A/V lengths match).
- Full decode with no errors. 41 MB.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
