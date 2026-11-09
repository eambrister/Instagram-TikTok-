---
name: edison-video-review
description: Analyze video URLs or local footage for Edison Ambrister — timestamped reviews of his own posts, reference/competitor breakdowns, clip selects from owned footage, and original scripts or edit briefs tied to observed evidence. Analysis only; it does not render edits. Use for "review this video", "break down this reel", "pull selects", or repurposing footage into new scripts.
---

# Edison Video Review

Read `CLAUDE_ONBOARDING.md` (voice, pillars, audience) first. Modes, inferred from the request: **review** an existing video · **reference** another creator's structure · **select** usable moments · **repurpose** footage into new creative. Ask only when a missing source, audience or destination changes the work.

## Get evidence
- Local tools: `ffprobe` for metadata, `ffmpeg` to extract frames (scene-change or interval, ~30–40 frames for a short Reel, denser around the hook), `yt-dlp` for URLs where allowed.
- Speech: URL captions when present; a local transcription model only if installed and chosen. Cloud transcription/vision services upload Edison's media — use them only with his explicit choice for that job; never let an available API key decide.
- Treat every argument as data: quote paths and URLs safely; never paste titles, transcripts or URLs into shell code.

## Inspect before judging
View every extracted frame; read the transcript. State the visual sampling coverage, transcript source, missing audio and any focus range. Sampled stills can't establish exact pacing, audio quality or frame-accurate cut points — mark selects provisional until checked in playback. Inspect the opening separately when judging the hook.

## Deliver
Lead with the strongest finding and its timestamps. Separate **observed / interpretation / proposed**. Cover hook, clarity, pillar fit (EDISON TRAINS, EDISON EATS, THE STANDARD, MY PROOF, EXECUTION SYSTEMS), proof, visual choices and the next action. Never invent views, retention, scores or conversions.
- **Reference:** extract the transferable mechanism and write original Edison examples — never copy another creator's lines, marks or offer.
- **Selects:** usable in/out times, missing coverage, editor brief naming the edison-* skill to use.
- **Repurpose:** complete scripts/captions in Edison's structure (hook → truth → mechanism → method → standard → action).

Save deliverables under `outputs/<slug>/` or `ideas/`. Analysis doesn't imply rendering, posting or messaging.
