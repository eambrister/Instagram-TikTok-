# claude-edits

Remotion effects for vertical Reels and TikTok: 1080 × 1920, 30 fps, with important text and graphics kept
between x = 120 and x = 960.

## Renders

| File | What it is |
| --- | --- |
| `out/OverTheShoulder.mp4` | Proof cards behind you, over each shoulder, with camera pushes |
| `out/GlassGraph.mp4` | Glass card with a counting number and a self-drawing graph |
| `out/FreezeFrame.mp4` | Freeze, grey background, sticker outline, name tag |
| `out/TierList.mp4` | S to D tier list that fills item by item |
| `out/TextBehind.mp4` | Huge word behind your head |
| `out/ColorGrade.mp4` | Flat LOG to cinematic grade with a light wipe |
| `out/ChatRender.mp4` | The chat intro, followed by GlassGraph |
| `out/full-reel.mp4` | All six with intros, then the grid and call to action |

## Values to replace

The placeholders are the `...Defaults` objects at the top of each file in `src/compositions/`:

- `OverTheShoulder.tsx`: before and after numbers (now 1,204 and 412K views)
- `GlassGraph.tsx`: title, from, to (now "Views this month", 1,204 to 412K)
- `FreezeFrame.tsx`: name and role (now Edison Ambrister, FITNESS COACH)
- `TierList.tsx`: topic and items (now protein sources)
- `TextBehind.tsx`: the word (now VIRAL)
- `FullReel.tsx`: call to action (now Comment CLAUDE)

Logos for TierList go in `public/logos`, named after the item (`greek-yogurt.png`). Music for FullReel goes in
`public/music.mp3`.

## Commands

```bash
npm install                      # once
tools/setup_mask.sh              # once, for the mask tools
.venv/bin/python tools/make_mask.py   # after replacing public/talking.mp4
npx remotion studio              # preview
npx remotion render FullReel out/full-reel.mp4
.venv/bin/python tools/safe_zone_audit.py FullReel 1
```

`public/talking.mp4` and `public/mask/` are not in git (too large). The source clip is in Google Drive.
