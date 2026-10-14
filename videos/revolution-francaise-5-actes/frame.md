---
version: alpha
name: Les flammes de la liberté — Frame (video / frame layer)
description: >
  Frame spec for « La frise en flammes », the animated version of Yazid Tragha's revision sheet
  « Les flammes de la liberté — La Révolution française en 5 actes ». Built from the
  editorial-forest preset's bones (serif-led editorial, flat paper, hairline rules, mono chrome),
  re-dressed in the PDF's own identity: cream paper, the blue and red edge bands of the cover,
  Merriweather Black titles in bordeaux / blue, and ONE accent color per act, exactly as in the PDF.
unit: the frame — 1920×1080 (16:9)
principle: the PDF is the brand · one act, one color · the flame is the only light source

colors:
  # ground + text (from the PDF)
  paper: "#FFFDF7"        # page background (cover + every page)
  card: "#FFF8E6"         # gold-bordered info boxes
  white: "#FFFFFF"        # event cards
  ink: "#2B2118"          # body text (warm near-black)
  ink-soft: "#6B5A3A"     # secondary text, captions
  brown: "#7A5A3A"        # kicker « HISTOIRE · CHAPITRE 1 · PREMIÈRE »
  gold: "#D4A017"         # rules, stars ★, quote dividers
  gold-soft: "#E3BF63"    # card borders
  navy: "#1B3A6B"         # problématique + réponse box, « Yazid Tragha »
  # tricolor edge bands of the cover
  band-blue: "#2C5AA0"
  band-red: "#C0392B"
  # one color per act (cover chips + act headers of the PDF)
  acte1: "#C0392B"        # 1789 · L'embrasement
  acte2: "#D68910"        # 1790-91 · Le feu couve
  acte3: "#2C5AA0"        # 1792 · Le brasier se réveille
  acte4: "#7B1D14"        # 1793-94 · La fureur des flammes
  acte5: "#5D6D7E"        # 1795-99 · Sous les cendres
  # light tints of each act (event-card washes in the PDF)
  acte1-tint: "#FDECEA"
  acte2-tint: "#FDF3E1"
  acte3-tint: "#E8EEF8"
  acte4-tint: "#F6E6E4"
  acte5-tint: "#ECEFF1"
  # the flame (the only glowing element)
  flame-core: "#FFE08A"
  flame-mid: "#F5A623"
  flame-edge: "#E2501C"

typography:
  # — display: Merriweather (the PDF's titles are a bold serif: DejaVu Serif Bold) —
  display-hero: { fontFamily: "Merriweather", px: 150, weight: 900, lineHeight: 1.02, tracking: "-0.01em" }
  display:      { fontFamily: "Merriweather", px: 104, weight: 900, lineHeight: 1.04, tracking: "-0.01em" }
  headline:     { fontFamily: "Merriweather", px: 72, weight: 900, lineHeight: 1.1 }
  title-card:   { fontFamily: "Merriweather", px: 52, weight: 700, lineHeight: 1.15 }
  date-figure:  { fontFamily: "Merriweather", px: 132, weight: 900, lineHeight: 1.0, tracking: "-0.02em" }
  quote:        { fontFamily: "Merriweather", px: 46, weight: 400, lineHeight: 1.4, italic: true }
  # — reading: Inter (the PDF body is a humanist sans: DejaVu Sans) —
  body:         { fontFamily: "Inter", px: 38, weight: 500, lineHeight: 1.4 }
  body-strong:  { fontFamily: "Inter", px: 38, weight: 700, lineHeight: 1.4 }
  date-pill:    { fontFamily: "Inter", px: 30, weight: 700, lineHeight: 1.0 }
  # — chrome: JetBrains Mono, uppercase, wide tracking (the PDF's spaced kicker) —
  label:        { fontFamily: "JetBrains Mono", px: 26, weight: 500, tracking: "0.22em", upper: true }
  caption-mono: { fontFamily: "JetBrains Mono", px: 22, weight: 500, tracking: "0.14em", upper: true }

spacing:
  slide-pad: "96px"
  band: "40px"            # blue band left edge, red band right edge (cover + title frames)
  rule: "3px"             # gold rules
  rule-thin: "2px"
  radius-card: "14px"     # PDF event cards are softly rounded
  radius-pill: "8px"      # date pills
  timeline-stroke: "10px" # the frise bar

components:
  tricolor-bands:
    description: "Full-height blue band (left) and red band (right), 40px each, on the paper ground — the cover's frame. Used on the title frame, the problématique, and the conclusion."
  act-header:
    backgroundColor: "{colors.acteN}"
    rounded: "{spacing.radius-card}"
    typography: "{typography.label} « ACTE » + giant numeral (Merriweather 900) | italic quote-subtitle (the act's fire metaphor) + {typography.headline} title in white + {typography.date-pill} years"
    description: "Mirror of the PDF's act banners. Paper-white text on the act color."
  event-card:
    backgroundColor: "{colors.white}, washed with {colors.acteN-tint} on ★ events"
    border: "3px solid {colors.acteN} (★) / 2px {colors.gold-soft} (others)"
    rounded: "{spacing.radius-card}"
    typography: "{typography.date-pill} in a {colors.acteN} pill → {typography.title-card} in {colors.acteN} → one {typography.body} line"
    description: "One event = date + title + ONE key line. Never the PDF paragraph. A gold ★ follows the title on starred events."
  icon-medallion:
    border: "5px solid {colors.acteN}"
    rounded: "50%"
    size: "120px"
    description: "Circled icon on the frise (crown, hand, Bastille, flame, scroll, bread, carriage, guillotine, bonnet, scales, temple, bicorne) — redrawn as flat SVG, warm browns + the act color."
  frise:
    stroke: "{spacing.timeline-stroke}"
    description: "The horizontal timeline 1789 → 1799, segmented in the five act colors with the PDF's proportions (1789 · 1790-91 · 1792 · 1793-94 · 1795-99). Ticks + date labels in Inter 700; event labels below in Inter 500."
  flame:
    description: "The travelling flame that rides the frise. Layered SVG teardrops (flame-edge → flame-mid → flame-core) with a soft radial glow. Its size follows the act: medium (acte 1), small embers (acte 2), growing (acte 3), huge (acte 4), embers fading to ash grey (acte 5)."
  arrow-box:
    backgroundColor: "{colors.card}"
    typography: "« → » + {typography.body} with key words in {typography.body-strong}"
    description: "The PDF's cream conclusion strip (« → C'est une déclaration de guerre… »)."
  problem-box:
    backgroundColor: "{colors.navy}"
    typography: "{typography.label} « PROBLÉMATIQUE » in light grey-blue + {typography.headline}-scale question in white"
    description: "The navy box of page 2, reused for the answer on page 12."
---

# Les flammes de la liberté — frame spec

## Source of truth

The brand is the PDF itself (`source/Frise_Revolution_francaise_Yazid_Tragha.pdf`). Every color above was sampled from its pages; every component mirrors one of its blocks (cover, act banner, event card, arrow strip, problématique box). A student who watches the video must recognize their revision sheet.

## The act-color law

- Each frame belongs to one act and uses **that act's color as its only accent** on the paper ground. The intro and conclusion use the cover's blue + red bands and the navy box.
- The full five-color frise appears only where the whole decade is shown (title, overview, recap). Elsewhere the frise is visible as a strip, with the current act lit and the others at 30% opacity.
- Text on an act color is white; text on paper is ink, titles in the act color. Never put small ink text on the bordeaux or slate fills.

## Type

- Titles: Merriweather 900 (display ramp), act color or bordeaux / blue like the cover (« Les flammes » bordeaux, « liberté » blue).
- Body: Inter 500, one line per event, key words in Inter 700. Legibility floor 30px.
- Chrome: JetBrains Mono uppercase with wide tracking, used only for kickers (« ACTE », « PROBLÉMATIQUE », « HISTOIRE · CHAPITRE 1 · PREMIÈRE ») and the footline.

## Depth & light

Flat paper, like the PDF: cards separated by borders and tints, at most a very soft card shadow (0 8px 24px rgba(43,33,24,0.08)). **The flame is the only light source** — it alone may glow (radial gradient + blur), and its warm light may tint the paper around it.

## Chrome

- Footline (bottom, caption-mono, ink-soft): « La Révolution française en 5 actes — Yazid Tragha », like the PDF footer.
- During the acts, a slim frise strip at the top shows where we are in the decade (current act lit).

## Numerals & claims

Every date, figure and name comes from the PDF. Nothing is added: no image of a real painting, no quote outside the PDF, no figure the PDF does not give.
