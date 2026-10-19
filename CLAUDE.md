# Repository notes

## Videos (`videos/`)

- **Palette: always the colours of the Vespa slide film** (`glissade-vespa-asr`, branch `claude/bold-wozniak-8xjfgp`, `design.md`). The user first asked for « orange et marron comme claude », then: « I want the colors of the video of sliding scooter ». Dark instrument-panel background `#0D1316` with a 60 px hairline grid (`#26343B`), panels `#141D21`, text `#E8EEEC` / `#93A4A7`, one amber highlight `#F4A62A` for what matters at each moment, mint `#93CDBB` for drawn objects only (never UI). Red `#F25C54` / green `#3CC98F` only for meaning (above / below a reference). For a HyperFrames preset, set these values in `frame.md` `colors:` by hand (the brand remix keeps the light preset's roles). Reference project: `videos/compteur-roue-radar/frame.md`.
- Narration voice so far: Kokoro `ff_siwis` (French) at normal speed.
- GSAP and fonts are vendored per project (`vendor/gsap.min.js`, `assets/fonts/`): the render browser here cannot reach CDNs.
