# ONCE A MONTH / WEEK / DAY: production notes (v1)

A format edit, not a talking head. Built by `tools/build_ea_once_a.py`; cycle timings are in `edl.json`.

## Reference and format
- Edison supplied a reference video: a creator standing still while food cutouts in three labelled slots ("Everyday / Once a Week / Once a Month") swap every cycle.
- The reference's people, account and footage are not used. Only the format is borrowed.
- Per the brief: **no captions, no depth titles, no whooshes.**

## Source
- Drive video, iPhone HEVC 3840 × 2160, rotated to vertical, 30 fps, SDR, 45.8 s.
- Edison stands on the right against a plain wall with a mic and says "once a month, once a week, once a day" six times.
- He points up-left for month, left for week and down-left for day.

## Edit
- **Kept:** the 6 cycles. Each runs from 0.3 s before "once a month" to 0.85 s after "day".
- **Cut** (standing rule §4b): the walk-in, the 2–3 s resets between cycles, and the walk-out.
- **Length:** 45.8 s raw → 30.2 s, plus the 2.5 s CTD end card.
- **No punch-ins.** The slot layout needs a locked frame; the new food set motivates each cut.

## Graphics
- **Slots:** three slots in the open left side of the frame, placed where Edison points. Each slot has a fixed ivory Barlow Condensed label: ONCE A MONTH / ONCE A WEEK / ONCE A DAY, using Edison's spoken wording.
- **Foods:** each one pops in (scale 0.55 → 1.08 → 1.0) on its spoken word, gets a soft contact shadow, and fades out at the end of the cycle.
- **Food sets** (month / week / day):
  1. Sundae / chocolate bar / strawberries
  2. Cheeseburger / spaghetti / grilled chicken
  3. Chips / popcorn / apple + peanut butter
  4. Chocolate cake / cookies / yogurt + berries
  5. Donuts / fries / boiled eggs
  6. Hot dog / steak / salmon
- **Cutout source:** Edison's own craving-swaps and protein-tier-list images, cut out of their black backgrounds with floor reflections trimmed. No new images were generated.
- **Picture:** light grade, no vignette, CTD end card.

## Sound
- Edison's voice only, on the cut timeline with 6 ms fades. High-pass, FFT denoise and compression; this is not neural isolation.
- No music or SFX, per the brief.
- Oversampled brickwall limiter plus measured make-up gain: −14.0 LUFS integrated, −2.6 dBTP.

## Delivery checks (`once-a-v1.mp4`)
- 1080 × 1920, 30 fps, 979 frames, 32.6 s (A/V lengths match).
- Full decode with no errors. 9.7 MB.
- Every set was inspected at phone size.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
