---
name: edison-pro-studio
description: Make Edison Ambrister's talking-head footage look filmed in a high-end professional studio — background/set replacement by compositing or AI video, matched lighting and perspective, presenter and speech fully preserved, plus a reusable studio preset. Use for studio background replacement, set redesign or recording/compositing briefs.
---

# Edison Pro Studio

Read `../_shared/edison-video-standard.md` first. "Premium studio" is an aesthetic brief, not a claim about real premises or spending.

## Establish the shot
Inspect footage: framing, aspect, camera movement, light direction, subject position, hair edges, hands, mic, chair, desk, objects crossing the silhouette. Stills can't prove temporal stability or lip sync. No footage yet → deliver a recording brief and a ready environment prompt.

**Proposed starting look (not approved):** obsidian/graphite architectural room, warm practical lamps, brushed gold and titanium-silver details, controlled crimson accent light, shallow depth behind Edison. Once he approves a look, save `brand/studio-preset/` with the reference image, prompt, palette, lens perspective, object positions and lighting — and reuse it instead of redesigning each time.

## Preserve the presenter
Identity, face, skin texture and tone, hair, body, clothes, hands, eye line, expressions, gestures, timing, voice, lip sync — unchanged unless asked. Replace the environment only; match light, camera height, perspective, focus falloff and scale. Reject drift.

## Routes
- **Static camera, recoverable foreground:** clean plate + per-frame masking + restrained colour match keeps his original pixels (add tracked parallax if the camera moves).
- **AI video replacement:** see `edison-studio-swap`; verify the live tool's limits first.
- **No video tools:** deliver prompt, reference brief, edit instructions and checks — clearly labelled as a handoff, never as a render.

Batches: one representative short test (speech, a turn, gestures, hard edges) first, then continue within the existing authorization and budget. Long takes: split at pauses with handles, inspect every join; prefer compositing when generated segments drift.

## Finish
Original audio at original timing; sync checked at start, middle, end and every join. Check edges, fingers, glasses, mic, chair, shadows, reflections, wall lines, flicker, breathing. Deliver the render, the preset and notes; keep a clean master before captions.
