---
name: edison-gym-reel-cover
description: Design Edison Ambrister's gym Reel covers as photographic cinematic posters — real athlete frame, huge condensed dimensional ivory/crimson title, obsidian-steel grade, CTD logo, crop-safe type. Use for any gym Reel cover, even when the film used a different editing style.
---

# Edison Gym Reel Cover

Read `../_shared/edison-video-standard.md` first. Output: one finished **1080×1920 PNG** saved beside the video in `outputs/<slug>/cover.png`, whatever the film's aspect ratio.

## Design system
- **Photo:** a real, inspected frame of Edison mid-effort or at the payoff. Graphite/navy gym depth, warm readable skin, controlled crimson (`#981B2E`) edge light. Keep his identity, physique, clothes and exercise anatomy exactly.
- **Title:** the film's own title (never a stock title), 1–3 words, Barlow Condensed ExtraBold, very tight tracking, ivory `#F6EFE2` face with a crimson or gold bevel/extrusion and a soft moving-light highlight. It may sit partly behind his body only with a real mask.
- **Hierarchy:** title dominant → small credit line `EDISON AMBRISTER` (Montserrat Bold, tracked) → CTD logo upper-left from `brand/assets/ctd-cinematic-logo.png` → footer `DISCIPLINE - ACCOUNTABILITY - CONSISTENCY` small at the bottom.
- **Crop safety:** all critical type inside y 250–1580 and inside the central 1080×1350 so the profile-grid crop still reads. Check both crops before delivering.

## Workflow
1. Pick 3–5 candidate frames; inspect at full size; choose the sharpest with clean silhouette and negative space.
2. Grade the frame (balance first, then the obsidian finish). Generated or edited backgrounds must use the real frame as identity reference; inspect and reject any face or body drift.
3. Build type as editable layers (Pillow or the design tool), composite, export PNG and a 4:5 crop preview.
4. Record source frame, prompt (if any generation was used) and font list in `outputs/<slug>/cover-notes.md`.

Include a training partner only when the brief authorizes that person for this film. Cover-only requests do not need a new edit.
