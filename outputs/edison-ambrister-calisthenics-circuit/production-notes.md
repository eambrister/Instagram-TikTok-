# CALISTHENICS CIRCUIT: production notes (v1)

A workout film, not a talking head. Rendered directly with ffmpeg; the commands are recorded below.

## Source
- Drive video, iPhone HEVC 3840 × 2160, rotated to vertical, 30 fps, SDR, 2:17.2.
- Locked-off outdoor shot at the bars, sunny.
- The audio is a song playing from a speaker during the workout, not Edison's voice.

## Content (source times)
| Time | Exercise |
|---|---|
| 0:08–0:15 | Pull-ups (round 1) |
| 0:16–0:41 | Burpees |
| 0:42–1:05 | Squats (deep, hands at head) |
| 1:06–1:19 | Pull-ups (round 2) |
| 1:20–1:40 | Burpees |
| 1:41–2:13 | Squats |

## Edison's choices for this edit
- **Full real time, no cuts.** Only the walk-in (0:00–0:06.2) and the walk-up and lens cover at the end (after 2:13.4) are trimmed.
- **No on-screen text:** no exercise names, round labels, tracker bar or rep counter.
- **Keep the original song.** Edison was told it is copyrighted with explicit lyrics, and that platforms may mute or flag it.

## Picture
- Light saved grade (contrast 1.07, saturation 0.93, gamma 0.97, slight warm mids), **no vignette**, full-frame 1080 × 1920.
- 0.6 s crossfade into the 3.1 s CTD end card (logo, EDISON AMBRISTER, footer).

## Sound
- The original audio, which was very quiet as recorded (about −28 LUFS).
- 40 Hz high-pass, an oversampled brickwall limiter, then measured make-up gain.
- Fades out over the end card.

## Delivery checks (`calisthenics-circuit-v1.mp4`)
- 1080 × 1920, 30 fps, 3,891 frames, 129.7 s (A/V lengths match).
- Full decode with no errors and no black gaps.
- −14.0 LUFS integrated, −1.9 dBTP. 91 MB.
- Frames were inspected across every exercise and the end card.

## Not done
- No continuous real-time watch or listening pass.
- Not scheduled: Edison posts it himself.
