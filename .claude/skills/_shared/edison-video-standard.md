# Edison video standard (shared by every edison-* skill)

Every `edison-*` skill applies these rules first. A skill's own rules sit on top of them, and the current brief from Edison overrides both.

These skills adapt editing *techniques* from a private collection of video-editing workflows that Edison was given for personal use. They are rewritten here for Edison's brand. The original creator's name, marks, slogans, offers, music, sound library, LUTs, scripts and example footage are **not** part of this repository and must never appear in Edison's work.

## 1. Identity

- **Setting:** Edison does not train at a gym. Where a skill says "gym", read it as wherever he actually trains or films, such as home, outdoor or bodyweight work. Never invent gym equipment or locations. Adapt each skill to his real footage when it's first used.
- **Subject:** Edison Ambrister, from his real footage only. Never alter his face, physique or skin tone, and never invent exercises, reactions, a second camera, or results.
- **Name in copy, credits and captions:** Edison Ambrister (`@edisonambrister` on Instagram, `@e.pamb` on TikTok).
- **Logo: Cut Throat Discipline.** Edison's instruction on 2026-11-08 sets the CTD logo as the mark for these video skills. This overrides the "CTD emblem retired" line in `brand/README.md`, but only for work made with these skills.
  - Mark: `brand/assets/ctd-cinematic-logo.png` (1254 × 1254 RGBA, so use its real alpha and never a white plaque).
  - Reel overlay and safe area: `brand/templates/ctd-reel-overlay-1080x1920.png`, `brand/templates/ctd-reel-safe-area-guide.png`.
  - Post overlay and safe area: `brand/templates/ctd-post-overlay-1080x1350.png`, `brand/templates/ctd-post-safe-area-guide.png`.
  - Placement: upper-left on covers, posts and end cards. Inside a film, show it on the opening ident or end card only, with no permanent watermark over the action.
- **Footer** on covers, end cards and carousel slides: `DISCIPLINE - ACCOUNTABILITY - CONSISTENCY`.
- Read `CLAUDE_ONBOARDING.md` before writing any copy. It holds the voice, the five pillars (EDISON TRAINS, EDISON EATS, THE STANDARD, MY PROOF, EXECUTION SYSTEMS) and the claims rules.

## 2. Look

Where an original technique called for "charcoal / brass / bone / crimson / blue-amber", map it to Edison's tokens (`brand/tokens.json`):

| Role | Token | Hex |
|---|---|---|
| Deep background, shadows | obsidian | `#07080A` |
| Environment depth | graphite | `#292D34` |
| Sustained readable type | ivory | `#F6EFE2` (Monumental: bone `#EEE9DF`) |
| Emphasis word, metal accent | gold / pale gold | `#D6A918` / `#F3D878` |
| Cool steel accent, rules | silver | `#AAB0B9` |
| Edge light, contour, single hit word | crimson | `#981B2E` |

- **Display sans:** Barlow Condensed ExtraBold (stand-in for the requested Heading Now). **Support:** Montserrat Medium/Bold (stand-in for Gotham). **Editorial serif:** Bodoni Moda Bold/Black, which replaces any Bodoni, Didot or Baskerville call in the originals. All of these are in `brand/fonts/`. Disclose a substitution whenever a brief names a licensed font.
- **Grade intent:** obsidian blacks with detail, graphite/blue-neutral environment, controlled highlights, warm, readable skin, and black clothing that keeps its texture. Balance every shot first, then apply one creative finish. Never guess a log transform from a DJI filename or a BT.709 tag.
- **Edison LUTs:** none exist yet. Do not borrow or describe another creator's LUT as Edison's. Once Edison approves a grade, save it as `brand/luts/EA-OBSIDIAN-709-v1.cube`, with notes on what input it expects.
- **Monumental kit** (`brand/monumental/`) is the serif / bone / antique-gold variant. Use it when the brief or skill calls for editorial serif treatment.

## 3. Formats

- **Reels and TikTok:** 1080 × 1920, 9:16, side margin 48 px, critical text between y 250 and 1580. Keep captions clear of the bottom UI (around y 1300 to 1460 is the sweet spot).
- **Posts and carousels:** 1080 × 1350, 4:5, safe margin 46 px.
- **Covers:** 1080 × 1920 PNG. Check that the 4:5 grid crop still reads.
- Cadence follows the source footage (24, 25 or 30 fps). Never call upscaled footage native 4K.

## 4. Copy and captions

- Voice: direct, disciplined, demanding, practical. Light profanity at most. No guaranteed outcomes, invented statistics, medical certainty or AI-sounding slogans.
- Structure: hook → truth → mechanism → method → standard → action. Captions follow `brand/monumental/CAPTION_SYSTEM.md`: one CTA, exactly five relevant hashtags and a short search-keyword bank.
- The 80-lb story (222 → about 142 lb in under two years) is Edison's personal experience, never a promise.
- **No offer, price or "DM me" CTA posts** until Edison finalizes the coaching offer. No invented testimonials, client results or credentials.

## 5. Honesty and verification (every film)

- Inspect the actual footage before planning. Say what was sampled and what was watched in motion. Thumbnails are not a watch-through.
- Keep speech meaning intact: negations, qualifications and uncertainty. Never fabricate a voiceover or quote as Edison's own words. A text-to-speech narration (for example Kokoro in `video/`) must be presented as narration, never as Edison speaking.
- Moving masks are built per frame. A frozen cutout, a shifted duplicate or frame blending must be described as exactly what it is.
- Use only music Edison has authorized (or the original beds from `video/tools/make_music.py`). Record the file and offset. Label synthesized SFX as designed.
- Before calling anything done: fully decode the export, verify dimensions, frame count, duration and A/V length, meter integrated loudness (about −14 LUFS) and true peak, and inspect every effect and transition boundary. Never claim listening from meters.
- Deliver a versioned MP4, a source/frame ledger, grade notes, sound provenance and a QA note in `outputs/<slug>/`. Preserve originals and earlier approved versions.
- Editing never authorizes posting, messaging, purchases, paid generations or uploading footage to outside services.

## 6. Where these skills run

| Need | Edison's computer | This cloud repo |
|---|---|---|
| DaVinci Resolve timeline, Fusion, native grade | yes (Resolve open) | no |
| Apple Vision person masks (macOS) | yes | no; needs a substitute segmenter |
| ffmpeg cuts, grading math, Pillow titles, loudness | yes | yes (ffmpeg, Python, Pillow, NumPy) |
| HTML-rendered Reels with captions and voiceover | yes | yes (`video/`, HyperFrames) |
| Higgsfield or other paid generation | Edison's own account and credits | no |

If a required capability is missing, name exactly what's missing, finish everything that doesn't depend on it, and never present a plan as a rendered film.
