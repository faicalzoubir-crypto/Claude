# Repository notes

## Videos (`videos/`)

- **Palette: always Claude's orange and brown** (the user's standing request: « Tjr utilise les couleur orange et marron comme claude »). Ivory background `#FAF9F5`, Claude orange `#C15F3C` as the accent, dark-brown text `#33241A`, brown-grey secondary text `#7A6556`. Red and green only for meaning (above / below a reference). For a HyperFrames frame preset, put these in `capture/extracted/tokens.json` `colors` before `build-frame.mjs`, then set `text-muted` back to `#7A6556` in `frame.md`. Reference project: `videos/compteur-roue-radar/frame.md`.
- Narration voice so far: Kokoro `ff_siwis` (French) at normal speed.
- GSAP and fonts are vendored per project (`vendor/gsap.min.js`, `assets/fonts/`): the render browser here cannot reach CDNs.
