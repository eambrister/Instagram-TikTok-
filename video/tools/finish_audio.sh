#!/usr/bin/env bash
# Normalize a rendered Reel's audio to social-media loudness (-14 LUFS, -1.5 dBTP).
# The video stream is copied untouched. Usage: tools/finish_audio.sh IN.mp4 OUT.mp4
set -euo pipefail
in=$1 out=$2
target="I=-14:TP=-1.5:LRA=7"

stats=$(ffmpeg -hide_banner -i "$in" -af "loudnorm=$target:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
measured=$(python3 -I -c "import json,sys; d=json.load(sys.stdin); print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")" <<<"$stats")

ffmpeg -v error -y -i "$in" -c:v copy -af "loudnorm=$target:$measured:linear=true" \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$out"
ffmpeg -hide_banner -i "$out" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
