#!/usr/bin/env bash
# Pull AI-Youtube-Shorts-Generator (MIT) on request, pinned to a reviewed commit.
# Installs into video/.tools/shorts-generator (git-ignored) with its own virtualenv.
# Run from the video/ folder:  styles/clip-long-video/install.sh
set -euo pipefail
REPO=https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator
COMMIT=315ea8d390b4791cc47151b14fd2cb5dfa94b147  # 2026-10-27 main
DEST=.tools/shorts-generator

if [ ! -d "$DEST/.git" ]; then
  git clone --filter=blob:none "$REPO" "$DEST"
fi
git -C "$DEST" fetch --quiet origin "$COMMIT"
git -C "$DEST" checkout --quiet "$COMMIT"

python3 -m venv "$DEST/.venv"
"$DEST/.venv/bin/pip" install --quiet -r "$DEST/requirements-local.txt"
echo "Installed at $DEST ($COMMIT)."
echo "Needs GEMINI_API_KEY or OPENAI_API_KEY in the environment (never in a committed .env)."
