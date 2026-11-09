# NO ONE'S COMING TO SAVE YOU: production notes (v1)

Made with `edison-full-message` and the cut-the-raw-footage rule (shared standard §4b). Built by `tools/build_ea_no_one_coming.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

## Source
- Drive video (iPhone HEVC 2160 × 3838), 30 fps, SDR, 85.5 s. A single take, an indoor selfie (white walls, black tee).

## Cuts
The raw 85.5 s is cut to 73.1 s in 11 segments, plus the 2.5 s CTD end card. Every jump cut alternates between a 1.0× and a 1.12× punch-in.

| Source | Reason | Words |
|---|---|---|
| -0.04–0.18 s | filler opener | "So" |
| 6.92–8.02 s | filler | "saying, you know," |
| 18.28–24.34 s | rambling aside restating 'people will help you' | "Like, if you call up someone right now, I sure I have people like a call right now to assist me if I ever get inside like a bind or something, right?" |
| 83.41–85.52 s | filler sign-off | "Just so you know." |

There are also 9 dead-air trims, totalling 2.9 s.

- The aside "if you call up someone right now… bind or something" only illustrated "yes, people will help you", which is kept. It can be restored on request.
- Edison's three "When we say no one is coming to save you…" lines are kept as deliberate structure.
- The film ends on "You have to do everything."

## Message
272 of 312 words are kept, and every point stays in order:
- The post he's responding to.
- People will help you.
- Only you can change your life.
- Others can assist, but the decision is yours.
- No one will push you further than you push yourself.
- People are consumed with their own lives.
- Reach your goals for yourself, financial and physical.
- People help, but only so much: you have to do everything.

## Picture and sound
- **Picture:** light grade, no vignette. Head-tracked depth titles, word-timed captions, CTD end card.
- **Voice:** reassembled with 6 ms fades. High-pass, FFT denoise and compression; this is not neural isolation.
- **Music:** original bed.
- **SFX:** all synthesized. Soft whooshes on regular titles; hits on ONLY YOU., PUSH YOURSELF. and YOU DO EVERYTHING.

## Delivery checks (`no-one-coming-v1.mp4`)
- 1080 × 1920, 30 fps, 2,269 frames, 75.6 s (A/V lengths match).
- Full decode with no errors and no black gaps.
- −14.6 LUFS integrated, −2.7 dBTP.
- Every title was inspected at phone size.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
