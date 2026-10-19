# Brand — video look

The house look for every video in this repo. The user chose it (« I want the colors of the video of sliding scooter… Remember this colors because I want to brand it »). It comes from the Vespa slide film (`glissade-vespa-asr`, branch `claude/bold-wozniak-8xjfgp`). First used on `videos/compteur-roue-radar`.

## Palette

| Token | Hex | Use |
| --- | --- | --- |
| `bg` | `#0D1316` | every background, solid (no gradients) |
| `grid` | `#26343B` at ~55% | 60 px hairline grid over the background |
| `surface` | `#141D21` | panels, cards, bubbles |
| `line` | `#26343B` | hairlines, card borders, table rules |
| `fg` | `#E8EEEC` | primary text |
| `muted` | `#93A4A7` | secondary text, labels, rulers, gauge ticks |
| `faint` | `#6E8186` | tertiary marks only (never body text) |
| `accent` | `#F4A62A` | amber, the ONE highlight: what matters at each moment (key numbers, eyebrows, arrows, signals, needle, chips). Text on amber is `#0D1316`. |
| `object` | `#93CDBB` | mint, drawn objects only (vehicles, wheels, machines); never UI |
| `negative` | `#F25C54` | meaning only: above a reference / danger |
| `positive` | `#3CC98F` | meaning only: below a reference / safe |

Real-world objects keep their real colours (road signs, a radar's red digits, skin, uniforms).

## Rules

- One amber thing at a time; everything else is fg / muted / mint.
- Cards: `#141D21` fill, 1.5 px `#26343B` border, 10–14 px radius, no shadow.
- Section label top-left: amber accent line (60×4) + amber uppercase eyebrow, letter-spacing 0.08em.
- Bottom ~17% stays free for subtitles; a thin amber progress bar on the bottom edge.

## Type

Space Grotesk (titles, numbers, labels) + Inter (body), shipped in `assets/fonts/` per project. The Vespa film itself used Montserrat + IBM Plex Mono: switch if the user asks for the full Vespa type too.

## Sound

Synth music in the Vespa film's identity: 90 BPM, D minor, Dm – B♭ – F – C (two bars per chord), soft pad + bass + gentle arpeggio, kept low under the voice; mix to about −14 LUFS. Voice: Kokoro `ff_siwis` (French), normal speed.

## Using it in a HyperFrames project

Copy `brand/frame.md` to the project root as `frame.md` (it already carries these colours on the blue-professional layout preset), or set the `colors:` block by hand. Don't rely on `build-frame.mjs` brand remix for this dark palette: it keeps the light preset's roles.
