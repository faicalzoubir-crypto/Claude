#!/usr/bin/env bash
# Exponentielle e — reconstruit les plans, l'index et les transitions.
# (voix : python tools/voice.py ; musique : python tools/music.py — à relancer seulement si le texte change)
set -euo pipefail
cd "$(dirname "$0")/.."
SKILL="${FACELESS_SKILL:-../../.claude/skills/faceless-explainer}"
python3 -I tools/build_frames.py
node "$SKILL/scripts/assemble-index.mjs" --storyboard ./STORYBOARD.md --hyperframes .
# GSAP local (le CDN n'est pas joignable au rendu) et langue du document
sed -i 's#<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"[^>]*></script>#<script src="vendor/gsap.min.js"></script>#; s/<html lang="en">/<html lang="fr">/' index.html
node "$SKILL/scripts/transitions.mjs" inject --storyboard ./STORYBOARD.md --hyperframes .
node "$SKILL/scripts/transitions.mjs" verify --storyboard ./STORYBOARD.md --index ./index.html
