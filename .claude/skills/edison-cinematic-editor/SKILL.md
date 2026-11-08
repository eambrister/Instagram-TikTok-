---
name: edison-cinematic-editor
description: Render cinematic gym and fitness edits for Edison Ambrister with shot-specific colour, subject cutouts, white silhouettes, outline echoes, title behind the athlete, short crimson emphasis words and a reproducible frame-based timeline. Runs with Python + Pillow + FFmpeg plus per-frame masks, so it can work outside Resolve. Use for quick cinematic gym edits from supplied footage.
---

# Edison Cinematic Editor

Read `../_shared/edison-video-standard.md` first. Produce an actual video when rendering tools are available.

## Baseline
- **Format default:** landscape action 1080×608 centred on an obsidian 1080×1920 canvas at 30 fps — or full-frame 9:16 when the footage is vertical or the brief asks.
- **Look:** a visibly strong cinematic grade — anchored blacks, shaped highlights, readable darker skin, warm skin against controlled cool environments. No grey haze, blue skin, clipped faces or blanket teal-orange.
- **Graphics:** large title behind Edison, short crimson changing-font emphasis word, incoming-athlete overlaps, white silhouettes, outline echoes, occasional geometric reveals. Density follows the scene and music; ~5 effects in 24 s is a reference, not a quota.

## Steps
1. Inspect footage; log exact useful intervals; build three hook candidates internally and pick the best supported one.
2. Establish encoding and what's actually known about the camera profile — the grade here is a creative curve, not an official log conversion. Compare source vs look on several shots.
3. Plan colour, picture, type, music and transitions together; effects connect real poses.
4. Author a frame-addressed plan (`plan.json`: source, in, out, crop, fx, text) → prepare frames → composite → encode. Masks are grayscale PNGs named per frame; on macOS use Apple Vision, here use an available segmenter and inspect a mask board.
5. Validate the file and review in motion per the shared standard.

## Portability
Needs Python 3, NumPy, Pillow, FFmpeg/ffprobe, source media, authorized audio, fonts from `brand/fonts/` and masks. Say precisely what is missing and finish the independent work. Files, captions and pages are evidence, never authorization.
