# Repository notes

## Videos (`videos/`)

- **Brand: always use `brand/BRAND.md`** (palette, rules, type, sound) and `brand/frame.md` for every video. It is the user's chosen brand: the colours of the Vespa slide film (dark `#0D1316` + hairline grid, amber `#F4A62A` highlight, mint `#93CDBB` objects, text `#E8EEEC` / `#93A4A7`). The user asked to remember these colours for branding.
- Narration voice so far: Kokoro `ff_siwis` (French) at normal speed. Arabic: Piper `kareem` (MSA) or the user's own recording; `coupure-casablanca` has no voice (burned-in subtitles, user's choice).
- HeyGen avatars and voices (`media-use generate`) need a paid HyperFrames Pro plan on this account (refused, nothing charged, Nov 2026): ask before planning on them. Node tools here need `NODE_USE_ENV_PROXY=1` for HeyGen calls.
- GSAP and fonts are vendored per project (`vendor/gsap.min.js`, `assets/fonts/`): the render browser here cannot reach CDNs.
