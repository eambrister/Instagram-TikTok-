---
name: edison-cinematic-visualizer
description: Edison Ambrister's cinematic video carousels — four-second footage selects per slide, scene-specific editorial serif headlines with quiet sans support, sculpted gradient/glow accents on meaningful phrases, and optional original mythic composites only when they earn their place. Use for video carousels, "cinematic carousel" or animated-slide sets.
---

# Edison Cinematic Visualizer

Read `../_shared/edison-video-standard.md`, `brand/CONTENT_SYSTEM.md` and `brand/monumental/STYLE_GUIDE.md` first. This is the carousel style; the acceptance check is the content system's QA checklist.

## Voice
Edison's: direct, earned confidence, concrete details from his real process (prepping the same meals, the 80-lb change as his experience, showing up on a bad day). Short slide thoughts build a story; the caption carries depth. No invented biography or generic slogans.

## Art direction
- Real footage carries each scene. Lay out every slide around the subject's movement and real negative space — never stamp one copy block on every slide. Vary shot scale and reading density.
- Tall editorial serif headline (Bodoni Moda) + quiet Montserrat support + occasional intimate italic. Bone/ivory for sustained reading; gold or a scene-motivated gradient for one meaningful phrase. Glow supports sharp glyphs, never blurs them. Some slides stay quiet so the big ones land.
- **Already-edited photos keep their supplied colour, exposure, contrast and saturation:** crop/resize and separate graphic layers only — no extra LUT, grade or global darkening. Shade minimally and locally behind lettering if needed.
- Mythic figures/props are optional, original (no copied characters), integrated with matching light, scale, grounded shadow, grain and occlusion. Never one floating bust repeated across a set; if it looks pasted on, fix or remove it.
- CTD logo upper-left and footer `DISCIPLINE - ACCOUNTABILITY - CONSISTENCY` per the content system; slide numbering consistent.

## Production
- **Default canvas: 1080×1350 (4:5)** per Edison's saved standard; 4 s per slide; uniform crop math, no stretching. Square or 4K only when the brief asks; never imply upscaled footage was native 4K.
- Inspect each source across its duration; verify proposed 4-s selects in motion; log in/out and any speed change. Prefer stable meaningful movement over whip pans. A slide can't carry more reading than 4 s allows — shorten or recompose.
- Finish overlay layers before rendering; never overwrite a plate an encoder is reading.
- Deliver numbered H.264 MP4 slides, a sequential preview, contact sheet, copy/timecode manifest, caption and posting ZIP in `outputs/<slug>/`. Inspect start/middle/end of every slide at phone size; review the contact sheet for repeated layouts.

Here in the repo, render overlays with Pillow and the fonts in `brand/fonts/`, then composite and encode slides with FFmpeg.
