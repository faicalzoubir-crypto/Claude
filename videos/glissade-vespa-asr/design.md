# Design — Glissade Vespa / ASR

**Concept.** An incident report that reads like telemetry: the real footage and the map are the evidence, and every graphic speaks in the calm voice of a data log (mono labels, timecodes, wheel speeds) on a dark instrument-panel background. Amber is reserved for the one thing that matters at each moment.

**Type tension.** Montserrat (the human account: titles, statements) against IBM Plex Mono (the machine: timecodes, labels, sensor values). The story is literally a human ride failed by an electronic system. Both are bundled with the renderer (offline, deterministic).

## Palette

| Token        | Hex       | Use                                                    |
| ------------ | --------- | ------------------------------------------------------ |
| `--bg`       | `#0D1316` | every section background (solid, no linear gradients)  |
| `--surface`  | `#141D21` | panels, cards                                          |
| `--line`     | `#26343B` | hairlines, grid, panel borders                         |
| `--fg`       | `#E8EEEC` | primary text                                           |
| `--muted`    | `#93A4A7` | secondary text, metadata                               |
| `--accent`   | `#F4A62A` | the single highlight colour: labels, circles, markers  |
| `--scooter`  | `#93CDBB` | object colour only (overlay + 3D scooter), never UI    |

## Type scale (1080×1920, vertical)

- Title: Montserrat 900, 128px, tracking -0.035em (one word per line allowed for display titles)
- Statement: Montserrat 700, 56–64px
- Body: Montserrat 400, 40–52px
- Label: IBM Plex Mono 700, 26–28px, uppercase, tracking 0.12em
- Data: IBM Plex Mono 400/700, 30–44px

## Layout

- Title-safe box: 108px side margins, 192px top/bottom; text kept out of the bottom 26% (platform UI) and left-aligned at x=96–108.
- Real footage and phone captures are full-bleed (they are 9:16 natively); text sits on a top scrim.
- Section index label at top-left in amber mono: `01 — IMAGES RÉELLES`, `02 — LE LIEU`, `03 — LE TABLEAU DE BORD`, `04 — L'EXPLICATION`, `05 — EN RÉSUMÉ`.
- Background: solid `--bg` + 60px hairline grid in `--line` at low opacity, slow drift; one soft radial glow behind the focal media.
- Diagrams and the 3D scenes use the full frame; labels stack in the upper half.

## Motion

- Entrances 0.4–0.7s, `power3.out` / `expo.out`; exits 0.3–0.4s `power2.in`.
- Section changes: 0.6s cross-dissolve through `--bg` with a slight scale (1.03 → 1), never a hard flash.
- Amber elements draw on (stroke / scaleX), they do not pop.
