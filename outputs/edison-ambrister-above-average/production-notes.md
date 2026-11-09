# ABOVE AVERAGE: production notes (v1)

Made with `edison-full-message` and the cut-the-raw-footage rule (shared standard §4b). Built by `tools/build_ea_above_average.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

## Source
- Drive video (iPhone HEVC 2160 × 3838), 30 fps, SDR, 53.8 s. A single take, an indoor selfie.

## Cuts
The raw 53.8 s is cut to 47.4 s in 13 segments, plus the 2.5 s CTD end card. Every jump cut alternates between a 1.0× and a 1.12× punch-in.

| Source | Reason | Words |
|---|---|---|
| 8.92–9.30 s | filler | "Like," |
| 24.86–26.36 s | repeat | "They ain't doing nothing." |
| 34.38–35.24 s | repeat | "They just don't care." |

There are also 10 dead-air trims, totalling 3.4 s.

## Message
- 170 of 179 words are kept, and every point stays in order:
  - It's easy to be above average; nobody is doing anything.
  - People talk but don't do.
  - Setting a goal and following through puts you above 99% of people.
  - Fitness and health: people aren't working out, have no goals, don't care.
  - Hit your goals every day you wake up.
  - People still won't in 2027.
  - "Have goals, set them, hit them. Trust me, you'll be fine."
- Edison's "bro"s are kept as part of his voice.
- "Above 99%" is Edison's opinion, so it appears as a title only, never as a chart or statistic.

## Picture and sound
- **Picture:** light grade, no vignette. Head-tracked depth titles, word-timed captions, CTD end card.
- **Voice:** reassembled from the kept segments with 6 ms fades. High-pass, FFT denoise and compression; this is not neural isolation.
- **Music:** original bed.
- **SFX:** all synthesized. Soft whooshes on regular titles; hits on ABOVE AVERAGE., ABOVE 99%, DON'T CARE. and HIT THEM.

## Delivery checks (`above-average-v1.mp4`)
- 1080 × 1920, 30 fps, 1,497 frames, 49.9 s (A/V lengths match).
- Full decode with no errors and no black gaps.
- −14.6 LUFS integrated, −2.7 dBTP.
- Frames sampled at every title and on the end card were inspected at phone size.

## Not done
- No continuous real-time watch or listening pass. Edison should watch it once.
- Not scheduled: Edison posts it himself.
