#!/usr/bin/env bash
# Finishing pass for Eddie's saved reel style: illustrations and the word behind the head on top of a
# finished reel-editor edit. Write src/reels/<name>.json first (see CLAUDE.md), with
# "video": "reel/<name>.mp4" and "maskDir": "reel-mask-<name>".
#
# Usage: tools/style_reel.sh <reel-editor job id> <name>
#   1st run: copies the edit and makes its person mask, then renders if src/reels/<name>.json exists.
set -euo pipefail
cd "$(dirname "$0")/.."
job="$1"
name="$2"
edit="../reel-editor/outputs/$job"
mkdir -p public/reel out/stills
if ! cmp -s "$edit/final.mp4" "public/reel/$name.mp4"; then
  cp "$edit/final.mp4" "public/reel/$name.mp4"
  .venv/bin/python tools/make_mask.py "public/reel/$name.mp4" --out "public/reel-mask-$name"
fi
if [ ! -f "src/reels/$name.json" ]; then
  echo "Mask ready. Now write src/reels/$name.json, then run this again."
  exit 0
fi
npx remotion render StyledReel "out/$name.mp4" --props="src/reels/$name.json" --log=error
npx remotion still StyledReel "out/stills/$name-cover.png" --props="src/reels/$name.json" --frame=30 --log=error
cp "$edit/cover.jpg" "out/$name-cover.jpg"
cp "$edit/captions.srt" "out/$name-captions.srt"
.venv/bin/python tools/safe_zone_audit.py StyledReel 1 --props "src/reels/$name.json" | head -5
echo "Done: out/$name.mp4"
