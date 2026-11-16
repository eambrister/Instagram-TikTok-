# NVIDIA SCANDAL → LUST: production notes (v1)

Made with `edison-full-message` and the cut-the-raw-footage rule (shared standard §4b). Built by `tools/build_ea_nvidia_lust.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

## Source
- Raw take: Drive video, iPhone HEVC 4K rotated to vertical, 30 fps, 6:33.7. A seated talking head against a light wall.
- B-roll: Edison's Drive folder, 21 files: 8 stock clips and 13 headline screenshots or photos.

## Cuts
The raw 6:33.7 is cut to 226.4 s in 30 segments, plus the 2.5 s CTD end card. 510 of 649 words are kept; the rest are retakes and flubs.

| Source | Reason |
|---|---|
| 30.5–40.2 s | retake:  first '$4.5 trillion' attempt |
| 53.5–61.4 s | retake:  first 'in less than a week, he was gone. So, here's what happened.' |
| 92.7–120.4 s | retakes:  four flubbed starts of the November 8th letter line |
| 233.6–241.9 s | retake:  first 'HP CEO Mark Hurd in 2010…' start |
| 266.4–278.2 s | retake:  first 'It took them years… one decision.' |
| 291.3–297.8 s | retake:  'Now here's the part that relates to you. You may not necessarily have a fault.' |
| 311.4–323.4 s | retake:  first 'But you have something that you've been building…' list |

There are also 41 dead-air trims, totalling 90.8 s.

Lines are kept as Edison recorded them, at his direction. See `broll-and-factcheck.md` for the fact-check notes he chose not to apply.

## B-roll (19 beats, full-frame, word-timed captions continue over them)
- Clock → "Thirty-three years"
- NVIDIA HQ → "co-founded it in 1993"
- Glowing chip → "graphics card company"
- Chip lines → "engine behind AI"
- Most-valuable-companies chart → "$4.5 trillion"
- CNN "admits affair" → the relationship line
- CNN Alice Huang explainer → "alleged spy"
- NVIDIA letter → the Nov 8 letter
- Ring hands → "unfaithful to his wife"
- Red chart → "stock started falling"
- Yahoo $490B → "$500 billion"
- NVIDIA CEO Transition → the Nov 12 resignation
- UC Davis Tiger Woods / AP Easterbrook / Intel Krzanich / NBC Hurd → each case
- Burning match (from 7 s, when the flame is lit) → "burn it all down"
- Trading screens → "trillion-dollar company"
- Family → "people depending on you"

Screenshots sit as rounded cards on a graphite field with a slow push; clips are cover-cropped to 9:16 with a slow push.

Not supplied, so Edison stays on camera instead: empty chair, corporate ladder, phone, DM and night-phone shots.

## Picture and sound
- **Picture:** light grade, no vignette. Head-tracked depth titles on the face sections only (33 YEARS., GONE., ALLEGATIONS., THE CRAZY PART., NOT THE FIRST., SAME STORY., YEARS TO BUILD., THE PART FOR YOU., WHAT YOU'RE BUILDING., LUST., THE HERE & NOW, STANDARDS., DON'T ANSWER., STAY FOCUSED., IN PRIVATE., IN PUBLIC., PROTECT IT., LOCKED IN.). The dark halo is strengthened so titles read on the light wall. CTD end card.
- **Voice:** reassembled with 6 ms fades. High-pass, FFT denoise and compression; this is not neural isolation.
- **Music:** original bed.
- **SFX:** all synthesized. Soft whooshes on regular titles; hits on GONE., LUST., IN PUBLIC. and LOCKED IN.

## Delivery checks (`nvidia-lust-v1.mp4`)
- 1080 × 1920, 30 fps, 6,866 frames, 228.9 s (A/V lengths match).
- Full decode with no errors and no black gaps.
- −14.7 LUFS integrated, −2.1 dBTP.
- Every B-roll beat and every title was inspected at phone size.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
