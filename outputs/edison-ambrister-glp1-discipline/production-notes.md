# GLP-1s vs DISCIPLINE: production notes (v1)

Made with `edison-full-message` and the cut-the-raw-footage rule (shared standard §4b). Built by `tools/build_ea_glp1_discipline.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

## Source
- Drive video (iPhone HEVC 2160 × 3838), 30 fps, SDR, 81.7 s. A single take, an indoor selfie.

## Cuts
The raw 81.7 s is cut to 70.8 s in 8 segments, plus the 2.5 s CTD end card. Every jump cut alternates between a 1.0× and a 1.12× punch-in.

| Source | Reason | Words |
|---|---|---|
| -0.04–0.34 s | filler opener | "And then" |
| 5.16–5.86 s | filler | "it's like" |
| 74.22–81.75 s | restates the 'put it all back on' point with a flubbed restart, then 'So yeah.' | "Because when you hop on them off, when you hop off of it, you're gonna put the weight back on. So yeah." |

There are also 8 dead-air trims, totalling 4.6 s. The film now ends on "But it does not build the mental discipline to reach your goals."

## Transcript
- 251 of 277 words are kept.
- "GLP ones" / "GLB one" are written as **GLP-1s / GLP-1**.
- "put an all the way back on" → **"put it all the way back on"** (confirmed by Whisper).
- **To confirm:** "I never suggest anybody **hop on** GLP-1s". Parakeet heard "help plan", Whisper "help me on".

## Health-claim handling
- Edison's audio is unchanged, including "statistics show that individuals who hop off the GLP-1s end up gaining all the weight". That line is his opinion as spoken.
- **No statistic or medical claim is on screen.** The titles are his own behaviour and opinion words (NOT THE SHOT., CALORIE DEFICIT., DISCIPLINE., HABITS., MINDSET., FIGHT YOUR MIND., MENTAL DISCIPLINE.).
- The post caption swaps "all the weight" for the published figure: about two-thirds regained within a year of stopping semaglutide (STEP 1 extension, Wilding et al., 2022). It also adds "not medical advice, talk to your doctor".

## Picture and sound
- **Picture:** light grade, no vignette. Head-tracked depth titles, word-timed captions, CTD end card.
- **Voice:** reassembled with 6 ms fades. High-pass, FFT denoise and compression; this is not neural isolation.
- **Music:** original bed.
- **SFX:** all synthesized. Soft whooshes on regular titles; hits on GLP-1s, CALORIE DEFICIT., FIGHT YOUR MIND. and MENTAL DISCIPLINE.

## Delivery checks (`glp1-discipline-v1.mp4`)
- 1080 × 1920, 30 fps, 2,198 frames, 73.3 s (A/V lengths match).
- Full decode with no errors and no black gaps.
- −14.6 LUFS integrated, −2.7 dBTP.
- Every title frame was inspected at phone size.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
