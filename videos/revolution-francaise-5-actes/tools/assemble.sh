#!/usr/bin/env bash
# Rebuild every frame and re-assemble index.html (audio, transitions) from STORYBOARD.md.
# Run from the project root:  bash tools/assemble.sh
set -euo pipefail
S="$(cd "$(dirname "$0")/../../../.claude/skills/faceless-explainer/scripts" && pwd)"
node tools/build_frames.mjs
node "$S/assemble-index.mjs" --storyboard ./STORYBOARD.md --hyperframes . --audio-meta ./audio_meta.json
# GSAP is vendored: the render machine has no CDN access
sed -i 's#<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"[^>]*></script>#<script src="vendor/gsap.min.js"></script>#' index.html
node "$S/transitions.mjs" inject --storyboard ./STORYBOARD.md --hyperframes .
node "$S/transitions.mjs" verify --storyboard ./STORYBOARD.md --index ./index.html
