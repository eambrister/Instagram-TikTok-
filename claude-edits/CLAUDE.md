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

## Saved reel style (Eddie's edit style; finishing pass after reel-editor)

Approved reference: `out/abnormal-reel.mp4`, made from `src/reels/abnormal.json`. Apply this to every video he asks
to have edited "in my saved style". Add other effects or changes only when he asks for them.

1. reel-editor makes the edit (see `../reel-editor/CLAUDE.md`): backed-out framing, title pinned at the top, chest
   captions, original music.
2. `tools/style_reel.sh <job> <name>` copies the edit to `public/reel/<name>.mp4` and builds its person mask
   (`public/reel-mask-<name>`).
3. Write `src/reels/<name>.json` (same shape as `abnormal.json`), from the job's `scene-plan.json` captions:
   - **One illustration per phrase**, about every 2 to 3 s, timed to the words they show (`from`/`to` in edit seconds).
   - **Labels are his own words**, 1 to 3 words, uppercase. Never invent claims, numbers or names.
   - **Alternate sides** (left/right). A second card may overlap on the other side; never two on the same side.
   - Pick from the illustration library in `src/illustrations.tsx` (registered in `StyledReel.tsx` → `ART`). If nothing
     fits what he says, draw a new one in the same style: 200 x 200 line art, white strokes (9 px, round caps), one yellow
     `#FFD84D` accent, a small motion. No photos, stock people, AI images or anything that looks like him.
   - **One key word behind his head** (`word`): a single strong word he actually says, usually the one the video is
     about or the one in his call to action. `at` is 0.2 s before he says it; `centerY` comes from
     `tools/word_position.py reel-mask-<name> <at>`. Leave the sides empty while the word is up.
   - Cards sit beside his head (x 120-330 and 750-960, top 560), so the face is never covered and labels never hide
     behind him; the person mask keeps him in front of them.
   - **Extra effects he asks for** go in the same file. GlassGraph for a number he says: `graph` (`at`, `title` from his
     words, `from`/`to`, `fullNumber`, `top`/`scale` so it sits below his chin); render the edit with reel-editor
     `--caption-gap "start-end"` for those seconds so the card doesn't sit on captions. Reference: `src/reels/million-steps.json`.
   - **B-roll he sends** (his own footage only) goes in the edit itself: reel-editor `--broll "licensed-media/broll/<clip>.mp4@start-end"`.
     Crop off phone status bars, app buttons and other people's names/replies first, mute it (story songs are not
     licensed), record it in `licensed-media/manifest.json`, and keep cards out of that window.
   - **Suggest effects, then wait.** With every video he sends, before rendering, send him a short numbered list of
     2 to 4 suggested effects: the moment (edit seconds), the effect, the words it shows (his own words and real numbers
     only), and one line on why. Pick the moments that matter (hook, a number, a list, the turning point, the call to
     action) and match the effect to what he says: numbers → graph (GlassGraph, `liquid-glass-graph`, `graph-bento`),
     lists → `apple-toggles`/`checklist`, a strong one-liner → word behind his head/`glitter-spotlight`/`led-sign`/
     `red-collage`, a myth he calls out → `reject-stamp`, emphasis → `lean-in`/`slow-push`. Never on his face, never on
     the pinned title or captions, never in a B-roll window. Add only the ones he approves.
   - **The 42-effect pack** lives at `~/.claude/skills/effects` (the `effects` skill; clone
     `https://github.com/Vibha-Ramprakash/claude-video-effects` there and run `scripts/setup.sh` if it is missing).
     Replace its placeholder text, handle (@vibha.in.progress) and numbers with his. Apply pack effects to the finished
     `out/<name>.mp4` with `scripts/fx.py --plan`, writing a new file (e.g. `out/<name>-fx.mp4`); check stills first.
4. Run `tools/style_reel.sh <job> <name>` again to render `out/<name>.mp4`. It also runs the safe-zone audit, which must
   report everything inside x = 120 to 960.
5. Check stills across the whole reel before sending, and send the MP4 plus a contact sheet.
6. **Posting (after he approves the video): a post-ready kit, not Metricool.** He schedules each post himself in
   Meta Business Suite (Instagram/Facebook), TikTok Studio (desktop web) and YouTube Studio; his Metricool plan is at
   its limit. Do not schedule through Metricool unless he asks for it on that video. Commit and push the final MP4,
   then send him one kit (a file in `out/<name>-post.md`, also pasted in chat) with:
   - the MP4 download link (raw GitHub URL of `claude-edits/out/<name>-fx.mp4`, or `<name>.mp4` if no pack effects);
   - the caption to paste (his own words, ending with his call to action and `#discipline #consistency`);
   - the TikTok title, the YouTube Shorts title, category Sports, not made for kids, AI label off;
   - the cover frame (which second) and the suggested day and time (Toronto), avoiding slots he already uses.
