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

## Type scale (1920×1080)

- Title: Montserrat 900, 104px, tracking -0.03em
- Statement: Montserrat 700, 52–64px
- Body: Montserrat 400, 34–40px
- Label: IBM Plex Mono 700, 22–26px, uppercase, tracking 0.12em
- Data: IBM Plex Mono 400/700, 28–40px

## Layout

- 160px side margins; content anchored to the left column, media anchored right.
- Section index label at top-left in amber mono: `01 — IMAGES RÉELLES`, `02 — LE LIEU`, `03 — LE TABLEAU DE BORD`, `04 — L'EXPLICATION`, `05 — EN RÉSUMÉ`.
- Background: solid `--bg` + 60px hairline grid in `--line` at low opacity, slow drift; one soft radial glow behind the focal media.
- Vertical footage sits in a rounded panel (radius 22px, 2px `--line` border), full-height minus 40px top/bottom.

## Motion

- Entrances 0.4–0.7s, `power3.out` / `expo.out`; exits 0.3–0.4s `power2.in`.
- Section changes: 0.6s cross-dissolve through `--bg` with a slight scale (1.03 → 1), never a hard flash.
- Amber elements draw on (stroke / scaleX), they do not pop.
