# Pull-up variations: production notes

Made in the saved style with the cut rule (shared standard §4b), **no music** (as Edison asked). Built by `tools/build_ea_pullup_variations.py` with the engine in `tools/ea_cut_edit.py`. The edit decision list is in `edl.json`.

- **Source:** single 55.6 s outdoor take at the bars (Drive id 1vxLoLfah4m4yP4NkLGouw6arUgAn4K1Q), 4K HEVC.
- **Cut:** 55.6 s → 39.7 s + 2.5 s CTD end card. Cut the walk-in, "You know," and the dead air between grips (wind kept the auto-detector from seeing it, so these gaps are marked by hand in `DEAD`). All five grip demos are protected and play in full.
- **Titles (head-tracked, depth):** A FEW TYPES → PULL-UPS. (slam) → WIDE GRIP. → CLOSE GRIP. → DEADLIFT GRIP. → THIS ONE? → COMMANDO GRIP. → VARIATIONS. (slam) → EXTRA WIDE. → MIX IT UP.
- **COMMANDO GRIP:** Edison says he can't remember this grip's name. On camera it's side-on to the bar with his hands close together, one in front of the other, which is the commando pull-up. Change the label if he meant another grip.
- **Captions:** word-by-word, with the current word in gold. Words no longer stay on screen through silent demos: the engine caps a word at 0.6 s when its ASR end time runs over a pause.
- **Audio:** voice + soft whooshes + slam hits, no music bed. −14.5 LUFS, −3.5 dBTP.
- **Engine changes:**
  - `DEAD` lets a film mark dead air by hand.
  - With `MUSIC_LEVEL = 0`, no music is generated at all.
  - Make-up gain is re-measured after the limiter.
