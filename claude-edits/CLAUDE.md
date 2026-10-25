# claude-edits: Remotion effects project

Every video: 1080 × 1920, 30 fps. Keep important text and graphics between x = 120 and x = 960
(use `SafeArea` from `src/settings.ts` / `src/SafeArea.tsx`).

Source clip: `public/talking.mp4`. Never modify, re-encode, overwrite or delete it. Effects only read it.

For every effect requested:
1. Build it as its own composition in `src/compositions/<EffectName>.tsx`, registered in `src/Root.tsx` with id `<EffectName>`.
2. Open Remotion Studio (`npx remotion studio`) for preview.
3. Render to `out/<EffectName>.mp4` and state the full path.
4. Show 3 or 4 still frames (`npx remotion still <EffectName> out/stills/<EffectName>-fNNN.png --frame=NNN`).

## Person mask and BehindMe

- Setup once: `tools/setup_mask.sh`. Make the mask: `.venv/bin/python tools/make_mask.py`
  (reads `public/talking.mp4`, writes `public/mask/frames/mask_NNNNN.png`, `public/mask/talking-mask.mp4`, `public/mask/meta.json`).
- Check it: `.venv/bin/python tools/mask_check.py` writes 5 check sheets to `out/stills/mask-check-fNNN.jpg`.
- Re-run make_mask.py whenever talking.mp4 is replaced.
- `<BehindMe framing={...}>{graphic}</BehindMe>` (src/BehindMe.tsx) draws the clip, then the graphic, then the person on top.
  `usePersonMask(framing)` gives the same mask for custom layering (FreezeFrame uses it).

## Framing (talking.mp4 is horizontal 4K)

- `src/Footage.tsx` places the clip at the bottom of the 1080x1920 frame (`FRAME_SOURCE_WIDTH` source px
  across) and fills the space above with a wall plate fitted to that section: `tools/make_plate.py SECONDS`
  writes `public/plates/plate_<frame>.png`. Each effect passes `framing={{ startFrom, centerX }}`.
- `tools/head_position.py START_FRAME` gives the head's centre and chin for a section, from the mask.
- Sections in use: OverTheShoulder 1200, GlassGraph 1440, FreezeFrame 1080, TierList 1560,
  TextBehind 1320, ColorGrade 1800.

## Effects, intro and reel

- Effects live in `src/compositions/`; `src/effects.ts` lists them with their `/command` and description.
- `ChatRender` (props: effect, command, description) plays the chat intro, then hard-cuts to the effect.
- `FullReel` plays ChatRender + effect for all six, then the grid with the call to action.
  Music: put `public/music.mp3` in place; the clip's own audio is always muted.
- Safe zone check: `.venv/bin/python tools/safe_zone_audit.py FullReel 1` renders with footage hidden and
  lists frames with anything drawn outside x = 120 to 960.
