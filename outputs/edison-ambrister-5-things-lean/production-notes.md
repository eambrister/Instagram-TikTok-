# 5 THINGS TO GET LEAN: production notes (v2, cut edit)

Made with `edison-full-message` and the cut-the-raw-footage rule (shared standard §4b). Built by `tools/build_ea_5_things_lean.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

**v2 vs v1:** v1 was the uncut raw take with graphics on top. Edison asked for a real edit, so v2 cuts dead air, filler, repeats and the flubbed retake. The source runs 101.3 s; the edit runs 78.1 s, plus the 2.5 s end card.

## Cuts
23 kept segments. Every jump cut alternates between a 1.0× and a 1.12× punch-in.

| Source | Reason | Words |
|---|---|---|
| 0.12–0.66 s | filler | "Alright," |
| 30.52–32.42 s | restates the protein point | "So make sure you hit your protein goal." |
| 68.49–69.59 s | repeat | "guaranteed," |
| 74.33–76.64 s | repeat + filler | "Guaranteed, you will become lean. Okay," |
| 92.10–99.20 s | retake | "If you don't get lean from these five steps, Steps, you have a lack in one of these areas." |

There are also 25 dead-air trims: every pause over about 0.4 s, cut back to a natural breath, totalling 10.5 s.

## Message
- 266 of 301 words are kept. Every point stays, in order:
  - The hook and the 5-things promise.
  - Sleep 7–8 h for recovery.
  - Calories, with deficit and surplus.
  - Protein over exact carbs and fats.
  - Steps (10k/15k/20k), done before bed.
  - Training 3–5× a week, with HYROX/CrossFit vs calisthenics.
  - "Do those five things… you will become lean / cannot fight it / cannot beat it / you have a lack in one of them".
  - The closing "Guaranteed."
- Edison confirmed "**calisthenics**" (both models heard "a static").
- "you have a **lack** in one of them" kept as captioned (both models heard "luck"/"lock"; closed without further change).

## Picture and sound
- **Picture:** the same daylight grade, **no vignette**. Head-tracked depth titles, now remapped to the cut timeline with a minimum hold of 1.1 s so the punch titles survive the trims. Step tracker, word-timed captions and the CTD end card as in v1.
- **Voice:** reassembled from the kept segments with 6 ms fades at every joint. High-pass, FFT denoise and compression; this is not neural isolation.
- **Music and SFX:** original music bed. Soft whooshes on regular titles, hits on the punch titles, ticks on the step tracker. All SFX are synthesized.
- **Loudness:** −14.7 LUFS integrated, −2.6 dBTP. Delivery: 1080 × 1920, 30 fps, 2,418 frames, 80.6 s, full decode with no errors and no black gaps.
- **No "GUARANTEED" titles on screen** (onboarding rule). The word stays in the audio and captions only.

## Not done
- No continuous real-time watch or listening pass. Edison should watch it once before posting.
- Not scheduled: Edison posts it himself.
