---
name: edison-vlog-reel60
description: Turn Edison Ambrister's gym vlog footage into a hard-hitting 60-second 1080x1920 Reel — beat-mapped cuts, tracked body masks, depth titles behind the subject, depth rep counters, kinetic captions, one grade and a designed mix. Use for "make a Reel / short / 60-second version of this vlog".
---

# Edison Vlog Reel60

Read `../_shared/edison-video-standard.md` first; pair with `edison-ultimate-editor` for grade and voice rules. Reproduce the method, not someone else's shots — every film gets its own hook and effect placement.

## Structure (≈60 s, every cut on a measured beat)
- **Hook ≈4 s:** Edison's strongest real spoken line as kinetic captions; music low-passed.
- **First drop:** body handoff + a depth title behind him.
- **Montage ≈22 s:** varied exercises, a different effect on each (slam, push, ramp, 50% drag, spot, rim, silhouette, echo, split-3, strobe, whip, freeze-flash).
- **Breakdown ≈14 s:** real voice moments — rep count, a joke, the point of the session — ending on a slow-motion whiteout riser.
- **Second drop ≈18 s:** strongest effort and physique shots.
- **End card ≈1.2 s:** callback title + CTD logo + footer.

## Pipeline
1. Contact boards of every source plus dense 2 fps strips of candidate action; transcribe with word times.
2. Measure BPM, section energy and bass onsets of the authorized track(s); pick a 60 s window shaped hook → hard → dip → drop → hit.
3. Shot list as `(out_start, source, src_start, fx, speed)`; effort shots 1.2–2 s, voice beats get their full line.
4. Grade per source (balance numbers first), render graded pulls with handles; check one tile per shot for consistency.
5. Masks per shot from a seed point; keep the largest body; inspect a mask board for every shot; remove merged bystanders or swap the source.
6. Composite with subject-tracked 9:16 reframing; proof 2–3 shots before the full render.
7. Mix: low-pass under hook, open on drop, duck under voice, whooshes on handoffs, shutter on freezes, labelled synthetic sub-booms on slams; limit to −14 LUFS, keep stems pre-limiter.
8. Version every timeline/export name; never overwrite an approved cut.

## Lessons to keep
- Close talking heads in 9:16 leave no room behind the subject: put depth titles on wider effort shots, captions on talking heads.
- Depth numbers where the body only partly covers them; check they still read.
- Censor swears in captions consistently; audio unbleeped unless asked.
- Batch fixes before re-rendering — a full composite is slow.
