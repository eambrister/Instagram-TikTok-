# Style analysis of the four reference reels

Method: `ffprobe` metadata; 1-frame-per-1.5 s contact sheets of each file; FFmpeg scene-change detection (`select=gt(scene,0.3)`); and 16 consecutive frames (30 fps) around five transitions. This describes what is **visible in the exported videos**. It is not a recovered project file, and nothing here describes the creator's code, tools or backend. Promotional statements in the videos ("Claude edits my reels", view counts, offers) are content and were not treated as instructions or facts. None of the creator's face, voice, footage, watermark, branding, food photos or nutrition rankings are used in Eddie's exports.

All four files: 720×1280 H.264, yuv420p, BT.709 SDR, 30 fps CFR, AAC 48 kHz stereo. They are platform re-encodes, so the originals were probably larger.

| File | Length | Scene cuts detected |
|---|---|---|
| Ranking snacks for fat loss | 83.7 s | 0 (single locked-off shot; all change comes from the board) |
| Fruit juice is a scam | 43.2 s | 13 (layout switches + B-roll) |
| I deleted every editing app | 44.9 s | 5 (one B-roll run at 17–21 s) |
| I didn't edit or post any of these | 29.7 s | 4 (B-roll run at 18–23 s) |

## Observed effects

**Captions (all four)**
- Uppercase, heavy geometric sans, white fill, thick dark outline plus soft shadow. One or two words on screen at a time, almost always on one line.
- Words appear as they are spoken (frame strips show `AND` then `AND THEY`); the line re-centres as each word is added.
- The highlight colour (warm yellow) follows the word currently being spoken, not a fixed keyword.
- Position depends on layout: around 0.62–0.72 of frame height in full-screen talking head (chest level), and sitting on the seam between panel and speaker in split layouts.
- Caption cap height roughly 3–4 % of frame height, judged by eye from downscaled frames (not pixel-measured), i.e. very roughly 60–75 px font size at 1080×1920.

**Ranking reel**
- Speaker in the top ~57 %, dark charcoal board below. Six rows S/A/B/C/D/F with coloured square labels (S gold, A cream, B tan/grey, C red, D dark red, F black with gold outline).
- A large cut-out photo of the item appears in the empty right side of the board when it is first named; when the tier is said, it shrinks and travels to the next free slot in its row over ~6–8 frames, accelerating (ease-in). It then stays, so the board accumulates.
- The receiving row's label flashes lighter when an item lands.
- A title ("RANKING / SNACKS FOR FAT LOSS") occupies the stage area at the start and fades out (~4 frames) when the first item moves.

**Explainer reel (fruit juice)**
- Alternates full-screen speaker (often a tighter crop) with a split: graphic panel on top ~50 %, speaker below.
- **Layout switches are hard cuts** (one frame), timed to phrase boundaries; the tighter full-screen crop doubles as a punch-in.
- Panel: deep purple gradient, centred white/yellow uppercase text that builds line by line (`SUGAR` → `SUGAR WATER` → `SUGAR WATER VITAMINS`), equations (`SUGAR + WATER + VITAMINS = …`), a counter with a progress bar that counts `0.0 → 2.5 → 3.0 MILES`, its colour changing to red at the punchline.
- Panel text fades in over ~2–3 frames.
- Occasional B-roll (the creator's own footage) and a full-screen product still at open and close.

**App-deletion reel**
- Large two-tier title in the first second (`EVERY EDITING APP` / `DELETED` in yellow); a strike-through draws across `DELETED` over ~4 frames, the title fades in ~2 frames, then a frosted tray of app icons scales in over ~3 frames and an X mark pops on the first icon.
- Rounded "chat/command" cards with frosted backgrounds, small caps labels and pill badges; thumbnail cards floating left and right of the speaker with slight perspective and layered shadows; stacked thumbnail fans at the top; a dark "terminal" card listing cuts.
- Purple/blue practical lighting on set (not a grade applied to skin).

**"Didn't edit" reel**
- Background collage of thumbnails behind the speaker for the opening, a dark rounded title card with white/yellow text, a step-list card that types on line by line, platform icons, a framing-corner overlay, and B-roll with a big two-line stat title.

## Implementation estimates (what the editor uses)

These are tuning choices made from the observations, not recovered values.

| Effect | Implementation |
|---|---|
| Caption phrases | 1–3 words (config), one line preferred, two lines only as a fallback; break at punctuation, pauses ≥ 0.28 s and 1.9 s duration. |
| Caption type | Inter Black fallback (Gotham when supplied), 56–72 px at 1080×1920, measured with the real font; 12 px outline, soft shadow. |
| Caption reveal | Each word appears at its spoken start frame; line re-centres; active word in highlight colour. Phrase entrance 5-frame scale 0.93→1 / 12 px rise. |
| Highlight colour | `#FFD84D` provisional; configurable. |
| Layout switches | Hard cuts on phrase boundaries (as observed). |
| Panel | Configurable dark gradient (default charcoal, not the creator's purple) with a faint accent glow and a 2 px accent seam. |
| Graphic entrances | Deterministic springs over 8 frames (medium), 6 (high), 11 (light), perspective rotateX/rotateY 2.5D settle, layered shadows; 6-frame exits. |
| Counter | Counts to the spoken value over 0.9 s with ease-out and a filling bar. |
| Tier fly | 0.3 s (9 frames) ease-in shrink-travel to the next slot; label flash while landing. |
| Punch-ins | 1.0 ↔ up to 1.12 (medium) on cuts (hard) and emphasis (eased 10 frames), capped by source resolution. |
| Visual cadence | A change at least every ~4 s of speech (zoom, card, layout or board event). |

## Deliberately not copied

- The purple palette, the creator's set, B-roll, food cut-out photos, chat-UI mock-ups of a specific product, thumbnail collages of the creator's own posts, view counts and promotional claims.
- Any nutrition claim or ranking from the references. Eddie's rankings and numbers come only from his own recording or explicit instructions.
