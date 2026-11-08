# Repository notes

## Videos (`videos/`)

- **Brand: always use `brand/BRAND.md`** (palette, rules, type, sound) and `brand/frame.md` for every video. It is the user's chosen brand: the colours of the Vespa slide film (dark `#0D1316` + hairline grid, amber `#F4A62A` highlight, mint `#93CDBB` objects, text `#E8EEEC` / `#93A4A7`). The user asked to remember these colours for branding.
- Narration voice so far: Kokoro `ff_siwis` (French) at normal speed.
- Arabic narration: Piper `ar_JO-kareem-medium` with hand-written tashkeel (`tools/voice.py` in `videos/minurso-sahara` and `videos/samir-raffinage`). The model downloads from huggingface.co (allowed in the cloud environment `claude`).
- 3D refinery footage for `videos/samir-raffinage` is rendered from `refinery/samir-3d` by `tools/render3d/` (Playwright + SwiftShader), not inside the HyperFrames render.
- GSAP and fonts are vendored per project (`vendor/gsap.min.js`, `assets/fonts/`): the render browser here cannot reach CDNs.
