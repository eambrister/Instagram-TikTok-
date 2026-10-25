# claude-edits: Remotion effects project

Every video: 1080 × 1920, 30 fps. Keep important text and graphics between x = 120 and x = 960
(use `SafeArea` from `src/settings.ts` / `src/SafeArea.tsx`).

Source clip: `public/talking.mp4`. Never modify, re-encode, overwrite or delete it. Effects only read it.

For every effect requested:
1. Build it as its own composition in `src/compositions/<EffectName>.tsx`, registered in `src/Root.tsx` with id `<EffectName>`.
2. Open Remotion Studio (`npx remotion studio`) for preview.
3. Render to `out/<EffectName>.mp4` and state the full path.
4. Show 3 or 4 still frames (`npx remotion still <EffectName> out/stills/<EffectName>-fNNN.png --frame=NNN`).
