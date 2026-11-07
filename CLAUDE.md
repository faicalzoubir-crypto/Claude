# Repository notes

## Videos (`videos/`)

- **Brand: always use `brand/BRAND.md`** (palette, rules, type, sound) and `brand/frame.md` for every video. It is the user's chosen brand: the colours of the Vespa slide film (dark `#0D1316` + hairline grid, amber `#F4A62A` highlight, mint `#93CDBB` objects, text `#E8EEEC` / `#93A4A7`). The user asked to remember these colours for branding.
- Narration voice so far: Kokoro `ff_siwis` (French) at normal speed.
- Arabic videos: Kokoro has no Arabic voice and HeyGen is blocked by this environment's network, so the user records the Arabic voiceover themselves (`videos/pub-moto-electrique`). Whisper turbo for Arabic transcription comes from the sherpa-onnx GitHub release (Hugging Face is blocked).
- GSAP and fonts are vendored per project (`vendor/gsap.min.js`, `assets/fonts/`): the render browser here cannot reach CDNs.
