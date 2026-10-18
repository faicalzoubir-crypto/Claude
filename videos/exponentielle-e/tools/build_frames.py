"""Exponentielle e — génère les 7 plans (compositions/frames/NN-*.html).

Décor commun Cobalt Grid (papier crème quadrillé, encre cobalt seule, filets haut/bas,
Newsreader / Hanken Grotesk / DM Mono ; ≈ → ∞ viennent de KaTeX_Main, absents de
Newsreader). Chaque plan = un <template> autonome ; le minutage des animations vient de
tools/timing.json (instants exacts des répliques de la voix off).

Canvas 1080×1920. Zones libres pour l'interface Reels : rien d'important au-dessus de
y=150 ni sous y=1600.

Usage : python tools/build_frames.py
"""
import json
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMING = json.loads((ROOT / "tools" / "timing.json").read_text())
W, H = 1080, 1920
# Palettes (choisie par la variable d'environnement PALETTE, « sombre » par défaut) :
#  - terracotta : « couleurs de Claude, brun orange » (crème, noir chaud, terre cuite)
#  - sombre     : référence « équations » (fond anthracite, formules blanc cassé, titres gris,
#                 cuivre réservé au nombre e et à la courbe eˣ)
PALETTES = {
    "terracotta": dict(INK="#1F1A17", SOFT="#7A5A48", PAPER="#F5F0E8", ACC="#CC6E50", ACCD="#B4532F",
                       SEG="#E2A283", BAR="#E2A283", PEACH="#F1E1D4", GRID="rgba(120,80,60,0.07)",
                       FAINT="@FAINT", RULE="rgba(31,26,23,0.28)", LABEL="#B4532F",
                       TITLE="#1F1A17", CARET="#1F1A17", CALLOUT="#CC6E50"),
    "sombre": dict(INK="#F2EFE9", SOFT="#A8A39B", PAPER="#1E1E1E", ACC="#CB7B4F", ACCD="#CB7B4F",
                   SEG="#3A3734", BAR="#B8704A", PEACH="#2A2826", GRID="rgba(255,255,255,0.035)",
                   FAINT="rgba(255,255,255,0.12)", RULE="rgba(255,255,255,0.2)", LABEL="#A8A39B",
                   TITLE="#B9B4AC", CARET="#CB7B4F", CALLOUT="#A8A39B"),
}
PALETTE = os.environ.get("PALETTE", "sombre")
PAL = PALETTES[PALETTE]
INK, INK_SOFT, PAPER, ACC = PAL["INK"], PAL["SOFT"], PAL["PAPER"], PAL["ACC"]

# Repère partagé par les plans 4 et 5 (même scène, fondu enchaîné entre les deux).
X0, Y0, U = 504, 1416, 192  # origine (px) et unité (px)
BOX = (72, 552, 1008, 1512)  # x0, y0, x1, y1 de la zone de tracé


def gx(x):
    return X0 + x * U


def gy(y):
    return Y0 - y * U


# ── petits outils de mise en forme mathématique (P = préfixe du plan) ───────────
def frac(a, b):
    return f'<span class="P-frac"><span>{a}</span><span>{b}</span></span>'


def sup(s):
    return f"<sup>{s}</sup>"


def i(s):
    return f"<i>{s}</i>"


LIM = '<span class="P-lim"><span>lim</span><span class="P-limsub"><i>n</i> → +∞</span></span>'
U_N = f'{i("u")}<sub>{i("n")}</sub>'
SEQ = f'(1 + {frac("1", i("n"))}){sup(i("n"))}'
EX = f'e{sup(i("x"))}'

FONTS = [
    ("Newsreader", 400, "normal", "newsreader-latin-400-normal"),
    ("Newsreader", 400, "italic", "newsreader-latin-400-italic"),
    ("Newsreader", 300, "normal", "newsreader-latin-300-normal"),
    ("Newsreader", 300, "italic", "newsreader-latin-300-italic"),
    ("Hanken Grotesk", 400, "normal", "hanken-grotesk-latin-400-normal"),
    ("Hanken Grotesk", 500, "normal", "hanken-grotesk-latin-500-normal"),
    ("Hanken Grotesk", 600, "normal", "hanken-grotesk-latin-600-normal"),
    ("DM Mono", 400, "normal", "dm-mono-latin-400-normal"),
    ("DM Mono", 500, "normal", "dm-mono-latin-500-normal"),
    ("KaTeX_Main", 400, "normal", "KaTeX_Main-Regular"),
    ("KaTeX_Main", 400, "italic", "KaTeX_Main-Italic"),
    ("Mrs Saint Delafield", 400, "normal", "mrs-saint-delafield-latin-400-normal"),
    ("Aref Ruqaa", 700, "normal", "aref-ruqaa-arabic-700-normal"),
]
FONT_FACES = "\n".join(
    f'      @font-face {{ font-family: "{fam}"; font-weight: {wt}; font-style: {st}; '
    f'src: url("assets/fonts/{fn}.woff2") format("woff2"); }}'
    for fam, wt, st, fn in FONTS
)

BASE_CSS = """
      #root { position: absolute; inset: 0; overflow: hidden; color: @INK; font-family: "Newsreader", "KaTeX_Main", serif; font-weight: 400; }
      .P-ground { position: absolute; inset: 0; background-color: @PAPER;
        background-image: linear-gradient(@GRID 1.5px, transparent 1.5px), linear-gradient(90deg, @GRID 1.5px, transparent 1.5px);
        background-size: 24px 24px; background-position: -0.75px -0.75px; }
      .P-rule { position: absolute; left: 44px; right: 44px; height: 1.5px; background: @RULE; }
      .P-chrome { position: absolute; font-family: "DM Mono", "KaTeX_Main", monospace; font-size: 22px; letter-spacing: 0.06em; color: @SOFT; }
      .P-abs { position: absolute; }
      .P-m { font-family: "Newsreader", "KaTeX_Main", serif; white-space: nowrap; letter-spacing: -0.008em; }
      .P-m i { font-style: italic; }
      .P-m sup { font-size: 0.58em; line-height: 0; position: relative; top: -0.05em; vertical-align: super; margin-left: 0.04em; }
      .P-m sub { font-size: 0.58em; line-height: 0; vertical-align: sub; margin-left: 0.02em; }
      .P-frac { display: inline-flex; flex-direction: column; align-items: center; vertical-align: middle; font-size: 0.74em; line-height: 1.04; margin: 0 0.06em; position: relative; top: -0.1em; }
      .P-frac > span:first-child { border-bottom: 0.06em solid currentColor; padding: 0 0.14em 0.03em; }
      .P-frac > span:last-child { padding: 0.04em 0.14em 0; }
      .P-lim { display: inline-flex; flex-direction: column; align-items: center; vertical-align: top; line-height: 1; margin-right: 0.12em; }
      .P-limsub { font-size: 0.34em; margin-top: 0.08em; letter-spacing: 0; }
      .P-label { font-family: "Hanken Grotesk", "KaTeX_Main", sans-serif; font-weight: 600; color: @LABEL; text-transform: uppercase; letter-spacing: 0.16em; }
      .P-mono { font-family: "DM Mono", "KaTeX_Main", monospace; letter-spacing: 0.05em; }
      .P-topbar { position: absolute; left: 72px; right: 72px; top: 176px; height: 112px; border-bottom: 2px solid @INK; }
      .P-topbar .P-title { position: absolute; left: 0; bottom: 14px; font-size: 84px; line-height: 1; letter-spacing: -0.01em; color: @TITLE; }
      .P-topbar .P-tag { position: absolute; right: 0; bottom: 22px; font-size: 26px; color: @LABEL; }
      .P-acc { color: @ACC; }
      .P-seg { position: absolute; height: 46px; border-radius: 10px; background: @SEG; }
      .P-caret { position: absolute; width: 4px; height: 64px; background: @CARET; }
      .P-glitch { position: absolute; background-color: @PAPER; background-image: repeating-linear-gradient(90deg, @INK 0 2px, transparent 2px 8px); }
      .P-qr { position: absolute; display: grid; grid-template-columns: repeat(8, 1fr); background: @PAPER; box-shadow: 0 0 0 2px @PAPER; }
      .P-qr > span { background: rgba(31,43,224,0.10); }
      .P-qr > span.on { background: @INK; }
"""


def qr(prefix, x, y, size, seed):
    """Patch QR 8×8 déterministe (pas d'aléatoire : motif dérivé de la graine)."""
    cells = []
    for r in range(8):
        for c in range(8):
            on = ((r * 7 + c * 11 + seed) * 2654435761 >> 7) % 5 < 2 or (r in (0, 1) and c in (0, 1))
            cells.append(f'<span class="{"on" if on else ""}"></span>')
    return (f'<div class="{prefix}-qr" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px">'
            + "".join(cells) + "</div>")


def segments(top, caret_x):
    """Barre en 4 segments arrondis (motif « timeline » de la référence), avec un curseur optionnel."""
    out, x0, gap, n = [], 108, 12, 4
    w = (W - 2 * x0 - (n - 1) * gap) / n
    for k in range(n):
        out.append(f'          <div id="P-seg{k}" class="P-seg" style="left:{x0 + k * (w + gap):.1f}px;width:{w:.1f}px;top:{top}px"></div>')
    if caret_x is not None:
        out.append(f'          <div id="P-caret" class="P-caret" style="left:{caret_x}px;top:{top - 9}px"></div>')
    return "\n".join(out)


def frame_doc(fid, num, dur, css, body, js):
    p = f"f{num:02d}"
    tag = f"{num:02d} / 07"
    furniture = f"""
        <div id="P-ground" class="clip P-ground" data-start="0" data-duration="{dur}" data-track-index="0">
          <div class="P-rule" style="top:40px"></div>
          <div class="P-rule" style="top:1878px"></div>
          <div class="P-chrome" style="left:72px;top:58px">EXPONENTIELLE — e</div>
          <div class="P-chrome" style="right:72px;top:1836px">{tag}</div>
        </div>"""
    html = f"""<template>
  <style>
{FONT_FACES}
{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{fid}" data-width="{W}" data-height="{H}">{furniture}
{body}
  </div>
  <script>
    (function () {{
      const P = "{p}";
      const q = (s) => document.querySelector('[data-composition-id="{fid}"] ' + s);
      const qa = (s) => document.querySelectorAll('[data-composition-id="{fid}"] ' + s);
      const tl = gsap.timeline({{ paused: true }});
      const E = "power3.out";
      const up = (s, t, d = 0.7, y = 28) => tl.fromTo(q(s), {{ opacity: 0, y }}, {{ opacity: 1, y: 0, duration: d, ease: E }}, t);
      const fade = (s, t, d = 0.6) => tl.fromTo(q(s), {{ opacity: 0 }}, {{ opacity: 1, duration: d, ease: "power2.out" }}, t);
      const grow = (s, t, d = 0.7, o = "left center") => tl.fromTo(q(s), {{ scaleX: 0, transformOrigin: o }}, {{ scaleX: 1, duration: d, ease: E }}, t);
      const pulse = (s, t, k = 1.2) => {{
        tl.fromTo(q(s), {{ scale: 1 }}, {{ scale: k, duration: 0.28, ease: "power2.out", transformOrigin: "50% 60%" }}, t);
        tl.fromTo(q(s), {{ scale: k }}, {{ scale: 1, duration: 0.45, ease: "power2.inOut", immediateRender: false }}, t + 0.28);
      }};
      const sweep = (s, t, d, w) => tl.fromTo(q(s), {{ attr: {{ width: 0 }} }}, {{ attr: {{ width: w }}, duration: d, ease: "power1.inOut" }}, t);
      const tan = (s, t, from, to, d = 0.9) => tl.fromTo(q(s), {{ attr: from }}, {{ attr: to, duration: d, ease: E }}, t);
{js}
      window.__timelines["{fid}"] = tl;
    }})();
  </script>
</template>
"""
    html = html.replace("P-", f"{p}-")
    for key in sorted(PAL, key=len, reverse=True):  # @ACCD avant @ACC
        html = html.replace("@" + key, PAL[key])
    return html


def cue(num, cid):
    return TIMING["frames"][f"{num:02d}"]["cues"][cid]["start"]


def dur(num):
    return TIMING["frames"][f"{num:02d}"]["duration"]


# ── Plan 1 — Le secret ───────────────────────────────────────────────────────
def frame1():
    n = 1
    css = """
      .P-kicker { left: 76px; top: 236px; font-size: 30px; }
      .P-fprime { left: 100px; top: 330px; font-size: 330px; line-height: 1; }
      .P-callout { left: 76px; top: 700px; font-size: 58px; font-style: italic; color: @CALLOUT; }
      .P-sep { position: absolute; left: 72px; width: 300px; top: 820px; height: 2px; background: @ACC; }
      .P-e { left: 66px; top: 872px; font-size: 150px; line-height: 1; }
      .P-elabel { left: 76px; top: 1080px; font-size: 28px; }
      .P-band { position: absolute; left: 0; right: 0; top: 1210px; height: 330px; }
    """
    glitch = segments(1330, caret_x=470)
    body = f"""
        <div id="P-glitch">
{glitch}
        </div>
        <div id="P-kicker" class="P-abs P-label P-kicker">Une fonction, un nombre</div>
        <div id="P-fprime" class="P-abs P-m P-fprime">{i("f")} ′ = {i("f")}</div>
        <div id="P-callout" class="P-abs P-callout">égale à sa propre dérivée</div>
        <div id="P-sep" class="P-sep"></div>
        <div id="P-e" class="P-abs P-m P-e"><span id="P-esym" class="P-acc" style="display:inline-block">e</span> <span id="P-approx">≈</span> <span id="P-digits">{{DIGITS}}</span></div>
        <div id="P-elabel" class="P-abs P-label P-elabel">Le nombre <span style="text-transform:none">e</span></div>
"""
    body = body.replace("{DIGITS}", "".join(f'<span class="P-dg">{c}</span>' for c in "2,71828…"))
    t = lambda c: cue(n, c)
    js = f"""
      tl.fromTo(qa(".P-seg"), {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: E, stagger: 0.08 }}, 0.05);
      tl.fromTo(q("#P-caret"), {{ x: -362 }}, {{ x: 0, duration: {dur(n)}, ease: "none" }}, 0);
      fade("#P-kicker", 0.05, 0.5);
      up("#P-fprime", {t("fonction")}, 0.9, 40);
      fade("#P-callout", 1.7, 0.8);
      grow("#P-sep", {t("secret")}, 0.6);
      fade("#P-esym", {t("secret") + 0.15}, 0.4);
      fade("#P-approx", {t("secret") + 0.3}, 0.4);
      tl.fromTo(qa(".P-dg"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.08, stagger: 0.11 }}, {t("secret") + 0.55});
      pulse("#P-esym", {t("secret") + 1.75}, 1.25);
      fade("#P-elabel", {t("secret") + 1.8}, 0.5);
"""
    return n, "01-le-secret", css, body, js


# ── Plan 2 — Trois chemins ───────────────────────────────────────────────────
def frame2():
    n = 2
    css = """
      .P-row { position: absolute; left: 72px; right: 72px; height: 400px; border-bottom: 1.5px solid @FAINT; }
      .P-num { position: absolute; left: 0; top: 70px; font-size: 40px; }
      .P-formula { position: absolute; left: 110px; top: 90px; font-size: 118px; line-height: 1; }
      .P-desc { position: absolute; left: 114px; top: 300px; font-size: 32px; }
    """
    rows = [
        ("01", f"{LIM}{SEQ}", "Une limite"),
        ("02", f"2{sup(i('x'))}<span style='display:inline-block;width:0.7em'></span>3{sup(i('x'))}", "Deux courbes"),
        ("03", f"({EX})′ = {EX}", "Une dérivée"),
    ]
    body = """
        <div id="P-topbar" class="P-topbar"><div class="P-title">Trois chemins</div><div class="P-tag P-mono">→ e</div></div>
"""
    for k, (num, formula, desc) in enumerate(rows):
        top = 330 + k * 410
        body += f"""        <div id="P-row{k}" class="P-row" style="top:{top}px">
          <div class="P-num P-mono" style="color:@LABEL">{num}</div>
          <div class="P-formula P-m">{formula}</div>
          <div class="P-desc P-label">{desc}</div>
        </div>
"""
    t = lambda c: cue(n, c)
    js = f"""
      up("#P-topbar", 0.05, 0.6, 16);
      up("#P-row0", {t("limite") - 0.15}, 0.6, 30);
      up("#P-row1", {t("courbes") - 0.15}, 0.6, 30);
      up("#P-row2", {t("derivee") - 0.15}, 0.6, 30);
"""
    return n, "02-trois-chemins", css, body, js


# ── Plan 3 — La limite ───────────────────────────────────────────────────────
ROWS3 = [
    ("1", "2", 2.0, "n1"),
    ("2", "2,25", 2.25, "n2"),
    ("3", "≈ 2,370", (4 / 3) ** 3, "n3"),
    ("10", "≈ 2,594", 1.1 ** 10, "n10"),
    ("100", "≈ 2,705", 1.01 ** 100, "n100"),
    ("1 000", "≈ 2,717", 1.001 ** 1000, "n1000"),
    ("1 000 000", "≈ 2,71828", (1 + 1e-6) ** 1e6, "n1e6"),
]
BAR_X, BAR_W = 640, 336  # la barre va de 2 (largeur 0) à e (largeur BAR_W)


def frame3():
    n = 3
    css = """
      .P-formula { left: 72px; top: 330px; font-size: 112px; line-height: 1; }
      .P-thead { position: absolute; left: 72px; right: 72px; top: 540px; height: 48px; border-bottom: 2px solid @INK; font-size: 24px; }
      .P-row { position: absolute; left: 72px; right: 72px; height: 92px; border-bottom: 1.5px solid @FAINT; }
      .P-n { position: absolute; left: 0; top: 16px; font-size: 52px; line-height: 1.05; }
      .P-u { position: absolute; left: 276px; top: 12px; font-size: 62px; line-height: 1.05; }
      .P-bar { position: absolute; top: 26px; height: 40px; border-radius: 9px; background: @BAR; }
      .P-eline { position: absolute; left: @EX_pxpx; top: 590px; width: 0; height: 652px; border-left: 3px dashed @ACC; }
      .P-elab { left: @EL_pxpx; top: 548px; font-size: 40px; color: @ACC; }
      .P-concl { position: absolute; left: 72px; right: 72px; top: 1290px; height: 290px; border-radius: 22px; background: @PEACH; }
      .P-concl1 { position: absolute; left: 40px; top: 40px; font-size: 92px; line-height: 1; }
      .P-concl2 { position: absolute; left: 40px; top: 186px; font-size: 72px; line-height: 1; }
    """.replace("@EX_px", str(BAR_X + BAR_W)).replace("@EL_px", str(BAR_X + BAR_W - 8))
    body = f"""
        <div id="P-topbar" class="P-topbar"><div class="P-title">La limite</div><div class="P-tag P-mono">PARTIE 1 / 3</div></div>
        <div id="P-formula" class="P-abs P-m P-formula">{U_N} = {SEQ}</div>
        <div id="P-thead" class="P-thead P-mono"><span class="P-abs P-m" style="left:0;top:0;font-size:36px"><i>n</i></span><span class="P-abs P-m" style="left:276px;top:0;font-size:36px">{U_N}</span><span class="P-abs P-acc" style="left:{BAR_X - 72}px;top:8px">VERS e</span></div>
        <div id="P-eline" class="P-eline"></div>
        <div id="P-elab" class="P-abs P-m P-elab">e</div>
"""
    for k, (nn, uu, val, _) in enumerate(ROWS3):
        top = 600 + k * 92
        width = round(BAR_W * (val - 2) / (math.e - 2), 1)
        body += f"""        <div id="P-row{k}" class="P-row" style="top:{top}px">
          <div id="P-n{k}" class="P-n P-m">{nn}</div>
          <div id="P-u{k}" class="P-u P-m">{uu}</div>
          <div id="P-bar{k}" class="P-bar" style="left:{BAR_X - 72}px;width:{width}px"></div>
        </div>
"""
    body += f"""        <div id="P-concl" class="P-concl">
          <div id="P-concl1" class="P-concl1 P-m">{LIM}{SEQ} = <span class="P-acc">e</span></div>
          <div id="P-concl2" class="P-concl2 P-m"><span class="P-acc">e</span> ≈ 2,71828…</div>
        </div>
"""
    t = lambda c: cue(n, c)
    delays = [0.6, 1.0, 1.2, 0.25, 0.2, 0.2, 0.3]
    rows_js = "".join(
        f"""
      fade("#P-n{k}", {t(c) - 0.05}, 0.4);
      fade("#P-u{k}", {t(c) + dl}, 0.4);
      grow("#P-bar{k}", {t(c) + dl}, 0.7);"""
        for k, ((_, _, _, c), dl) in enumerate(zip(ROWS3, delays))
    )
    js = f"""
      up("#P-topbar", 0.05, 0.6, 16);
      up("#P-formula", {t("formule")}, 0.8, 30);
      fade("#P-thead", 2.1, 0.5);
      tl.fromTo(q("#P-eline"), {{ scaleY: 0, transformOrigin: "50% 0%" }}, {{ scaleY: 1, duration: 1.0, ease: E }}, 2.3);
      fade("#P-elab", 2.5, 0.5);{rows_js}
      pulse("#P-elab", {t("grandit") + 1.4}, 1.45);
      up("#P-concl", {t("e") - 0.1}, 0.7, 30);
      fade("#P-concl2", {t("e") + 1.4}, 0.5);
"""
    return n, "03-la-limite", css, body, js


# ── Repère (plans 4 et 5) ─────────────────────────────────────────────────────
def curve_path(f, x_from=-2.25, x_to=2.625, step=0.01):
    pts = []
    x = x_from
    while x <= x_to + 1e-9:
        y = f(x)
        if y > 4.9:
            break
        pts.append(f"{gx(x):.1f},{gy(y):.1f}")
        x += step
    return "M" + " L".join(pts)


def axes_svg(prefix):
    x0, y0, x1, y1 = BOX
    ticks = []
    for k in (-2, -1, 1, 2):
        ticks.append(f'<line x1="{gx(k)}" y1="{Y0 - 10}" x2="{gx(k)}" y2="{Y0 + 10}" />')
    for k in (1, 2, 3, 4):
        ticks.append(f'<line x1="{X0 - 10}" y1="{gy(k)}" x2="{X0 + 10}" y2="{gy(k)}" />')
    arrows = (f'<path d="M{x1},{Y0} l-18,-9 v18 z" fill="{INK}" stroke="none"/>'
              f'<path d="M{X0},{y0} l-9,18 h18 z" fill="{INK}" stroke="none"/>')
    return (f'<g stroke="{INK}" stroke-width="3" fill="none">'
            f'<line x1="{x0}" y1="{Y0}" x2="{x1}" y2="{Y0}" /><line x1="{X0}" y1="{y1}" x2="{X0}" y2="{y0}" />'
            + "".join(ticks) + arrows + "</g>")


def axis_labels(prefix):
    out = []
    for k in (-2, -1, 1, 2):
        txt = str(k).replace("-", "−")
        out.append(f'<div class="{prefix}-tick {prefix}-m" style="left:{gx(k) - 30}px;top:{Y0 + 14}px;width:60px">{txt}</div>')
    for k in (1, 2, 3, 4):
        out.append(f'<div class="{prefix}-tick {prefix}-m" style="left:{X0 - 64}px;top:{gy(k) - 20}px;width:40px;text-align:right">{k}</div>')
    out.append(f'<div class="{prefix}-tick {prefix}-m" style="left:{X0 - 44}px;top:{Y0 + 14}px;width:30px">0</div>')
    out.append(f'<div class="{prefix}-axname {prefix}-m" style="left:{BOX[2] - 34}px;top:{Y0 - 70}px"><i>x</i></div>')
    out.append(f'<div class="{prefix}-axname {prefix}-m" style="left:{X0 + 20}px;top:{BOX[1] - 10}px"><i>y</i></div>')
    return "\n".join("        " + o for o in out)


GRAPH_CSS = """
      .P-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
      .P-tick { position: absolute; font-size: 34px; line-height: 1; text-align: center; }
      .P-axname { position: absolute; font-size: 48px; line-height: 1; }
      .P-clabel { position: absolute; font-size: 64px; line-height: 1; background: @PAPER; padding: 0 6px; }
"""


def tangent(m, xa, xb):
    return f'x1="{gx(xa):.1f}" y1="{gy(1 + m * xa):.1f}" x2="{gx(xb):.1f}" y2="{gy(1 + m * xb):.1f}"'


# ── Plan 4 — Entre 2 et 3 ────────────────────────────────────────────────────
def frame4():
    n = 4
    css = GRAPH_CSS + """
      .P-legend { position: absolute; left: 72px; right: 72px; height: 76px; border-bottom: 1.5px solid @FAINT; }
      .P-sw { position: absolute; left: 0; top: 36px; width: 96px; height: 0; }
      .P-lname { position: absolute; left: 130px; top: 8px; font-size: 56px; line-height: 1; }
      .P-lwhat { position: absolute; left: 270px; top: 28px; font-size: 24px; }
      .P-lval { position: absolute; right: 0; top: 6px; font-size: 58px; line-height: 1; }
      .P-between { left: 84px; top: 640px; font-size: 88px; line-height: 1; background: @PAPER; padding: 6px 12px; }
      .P-between-sub { left: 84px; top: 760px; font-size: 52px; line-height: 1.1; background: @PAPER; padding: 4px 12px; }
      .P-pt { position: absolute; width: 20px; height: 20px; background: @INK; }
      .P-ptlab { left: 524px; top: 1236px; font-size: 38px; background: @PAPER; padding: 2px 6px; }
    """
    ln2, ln3 = math.log(2), math.log(3)
    legend = [
        ("2", "≈ 0,69", f"border-top: 3.5px dashed {INK}"),
        ("e", "= 1", f"border-top: 7px solid {ACC}"),
        ("3", "≈ 1,10", f"border-top: 3.5px dashed {INK}"),
    ]
    body = """
        <div id="P-topbar" class="P-topbar"><div class="P-title">Deux courbes</div><div class="P-tag P-mono">PARTIE 2 / 3</div></div>
"""
    for k, (base, val, sw) in enumerate(legend):
        body += f"""        <div id="P-leg{k}" class="P-legend" style="top:{300 + k * 78}px">
          <div class="P-sw" style="{sw}"></div>
          <div class="P-lname P-m">{base}{sup(i('x'))}</div>
          <div class="P-lwhat P-label">pente en 0</div>
          <div id="P-lval{k}" class="P-lval P-m">{val}</div>
        </div>
"""
    body += f"""
        <svg class="P-svg" viewBox="0 0 1080 1920">
          <defs>
            <clipPath id="P-box"><rect x="{BOX[0]}" y="{BOX[1]}" width="{BOX[2] - BOX[0]}" height="{BOX[3] - BOX[1]}" /></clipPath>
            <clipPath id="P-cr2"><rect id="P-r2" x="{BOX[0]}" y="{BOX[1]}" width="{BOX[2] - BOX[0]}" height="{BOX[3] - BOX[1]}" /></clipPath>
            <clipPath id="P-cr3"><rect id="P-r3" x="{BOX[0]}" y="{BOX[1]}" width="{BOX[2] - BOX[0]}" height="{BOX[3] - BOX[1]}" /></clipPath>
            <clipPath id="P-cre"><rect id="P-re" x="{BOX[0]}" y="{BOX[1]}" width="{BOX[2] - BOX[0]}" height="{BOX[3] - BOX[1]}" /></clipPath>
          </defs>
          <g id="P-axes">{axes_svg("P")}</g>
          <g clip-path="url(#P-box)" fill="none" stroke="{INK}" stroke-linecap="square">
            <line id="P-tan2" {tangent(ln2, -1.6, 2.2)} stroke-width="2.5" stroke-opacity="0.45" />
            <line id="P-tan3" {tangent(ln3, -1.3, 1.9)} stroke-width="2.5" stroke-opacity="0.45" />
            <line id="P-tane" {tangent(1.0, -1.45, 2.0)} stroke-width="3.5" stroke="{ACC}" />
            <path id="P-c2" clip-path="url(#P-cr2)" d="{curve_path(lambda x: 2 ** x)}" stroke-width="3.5" stroke-dasharray="12 9" />
            <path id="P-c3" clip-path="url(#P-cr3)" d="{curve_path(lambda x: 3 ** x)}" stroke-width="3.5" stroke-dasharray="12 9" />
            <path id="P-ce" clip-path="url(#P-cre)" d="{curve_path(math.exp)}" stroke-width="7" stroke="{ACC}" />
          </g>
        </svg>
{axis_labels("P")}
        <div id="P-pt" class="P-pt" style="left:{X0 - 10}px;top:{gy(1) - 10}px"></div>
        <div id="P-ptlab" class="P-abs P-m P-ptlab">(0 ; 1)</div>
        <div id="P-l2" class="P-clabel P-m" style="left:{gx(2.02) + 6}px;top:{gy(3.6)}px">2{sup(i('x'))}</div>
        <div id="P-l3" class="P-clabel P-m" style="left:{gx(1.0) - 118}px;top:{gy(3.75)}px">3{sup(i('x'))}</div>
        <div id="P-le" class="P-clabel P-m P-acc" style="left:{gx(1.42) + 14}px;top:{gy(4.32)}px">e{sup(i('x'))}</div>
        <div id="P-between" class="P-abs P-m P-between">2 &lt; <span class="P-acc">e</span> &lt; 3</div>
        <div id="P-between-sub" class="P-abs P-m P-between-sub"><span class="P-acc">e</span> = {LIM}{SEQ}</div>
"""
    t = lambda c: cue(n, c)
    bw = BOX[2] - BOX[0]
    def tl_attr(m, xa, xb):
        return ("{ x1: %d, y1: %.1f, x2: %d, y2: %.1f }" % (X0, gy(1), X0, gy(1)),
                "{ x1: %.1f, y1: %.1f, x2: %.1f, y2: %.1f }" % (gx(xa), gy(1 + m * xa), gx(xb), gy(1 + m * xb)))
    f2, t2 = tl_attr(ln2, -1.6, 2.2)
    f3, t3 = tl_attr(ln3, -1.3, 1.9)
    fe, te = tl_attr(1.0, -1.45, 2.0)
    js = f"""
      up("#P-topbar", 0.05, 0.6, 16);
      fade("#P-axes", {t("tracons")}, 0.6);
      tl.fromTo(qa(".P-tick, .P-axname"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, stagger: 0.03 }}, {t("tracons") + 0.2});
      sweep("#P-r2", 0.9, 1.6, {bw});
      sweep("#P-r3", 1.5, 1.6, {bw});
      fade("#P-l2", 2.3, 0.5);
      fade("#P-l3", 2.8, 0.5);
      tl.fromTo(q("#P-pt"), {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2)" }}, {t("point") + 0.1});
      fade("#P-ptlab", {t("point") + 0.6}, 0.5);
      up("#P-leg0", {t("pente2")}, 0.6, 20);
      tan("#P-tan2", {t("pente2") + 0.4}, {f2}, {t2});
      fade("#P-lval0", {t("pente2") + 2.6}, 0.5);
      up("#P-leg2", {t("pente3")}, 0.6, 20);
      tan("#P-tan3", {t("pente3") + 0.3}, {f3}, {t3});
      fade("#P-lval2", {t("pente3") + 1.6}, 0.5);
      sweep("#P-re", {t("base") + 0.3}, 1.5, {bw});
      fade("#P-le", {t("base") + 1.6}, 0.5);
      up("#P-leg1", {t("base") + 1.9}, 0.6, 20);
      tan("#P-tane", {t("base") + 2.1}, {fe}, {te});
      fade("#P-lval1", {t("base") + 2.6}, 0.5);
      up("#P-between", {t("cest_e")}, 0.7, 24);
      fade("#P-between-sub", {t("cest_e") + 1.0}, 0.6);
"""
    return n, "04-entre-2-et-3", css, body, js


# ── Plan 5 — La tangente glisse ──────────────────────────────────────────────
def frame5():
    n = 5
    css = GRAPH_CSS + """
      .P-read { position: absolute; top: 300px; width: 452px; height: 230px; border-top: 2px solid @INK; }
      .P-rlab { position: absolute; left: 0; top: 18px; font-size: 26px; }
      .P-rval { position: absolute; left: 0; top: 62px; font-size: 128px; line-height: 1; }
      .P-xval { left: 72px; top: 540px; font-size: 44px; line-height: 1; }
      .P-pt { position: absolute; width: 22px; height: 22px; background: @ACC; }
      .P-drop { position: absolute; width: 0; border-left: 2.5px dashed @SOFT; }
      .P-rexact { position: absolute; left: 0; top: 62px; font-size: 128px; line-height: 1; color: @ACC; }
      .P-eqv { position: absolute; left: 92px; top: 100px; font-size: 64px; line-height: 1; color: @SOFT; }
    """
    x = 1.0
    y = math.exp(x)
    body = f"""
        <div id="P-topbar" class="P-topbar"><div class="P-title">Une dérivée</div><div class="P-tag P-mono">PARTIE 3 / 3</div></div>
        <div id="P-read0" class="P-read" style="left:72px"><div class="P-rlab P-label">Hauteur du point</div><div id="P-hval" class="P-rval P-m">≈ 2,72</div><div id="P-hexact" class="P-rexact P-m">e</div><div id="P-eqh" class="P-eqv P-m">≈ 2,72</div></div>
        <div id="P-read1" class="P-read" style="left:556px"><div class="P-rlab P-label">Pente de la tangente</div><div id="P-pval" class="P-rval P-m">≈ 2,72</div><div id="P-pexact" class="P-rexact P-m">e</div><div id="P-eqp" class="P-eqv P-m">≈ 2,72</div></div>
        <div id="P-xval" class="P-abs P-m P-xval"><i>x</i> = <span id="P-xnum">1,00</span></div>
        <svg class="P-svg" viewBox="0 0 1080 1920">
          <defs>
            <clipPath id="P-box"><rect x="{BOX[0]}" y="{BOX[1]}" width="{BOX[2] - BOX[0]}" height="{BOX[3] - BOX[1]}" /></clipPath>
          </defs>
          {axes_svg("P")}
          <g clip-path="url(#P-box)" fill="none" stroke="{INK}" stroke-linecap="square">
            <path id="P-ce" d="{curve_path(math.exp)}" stroke-width="7" stroke="{ACC}" />
            <line id="P-tan" x1="{gx(x - 1.1):.1f}" y1="{gy(y - 1.1 * y):.1f}" x2="{gx(x + 1.1):.1f}" y2="{gy(y + 1.1 * y):.1f}" stroke-width="3.5" />
          </g>
        </svg>
{axis_labels("P")}
        <div id="P-drop" class="P-drop" style="left:{gx(x) - 1}px;top:{gy(y)}px;height:{Y0 - gy(y)}px"></div>
        <div id="P-pt" class="P-pt" style="left:{gx(x) - 11}px;top:{gy(y) - 11}px"></div>
        <div id="P-le" class="P-clabel P-m P-acc" style="left:{gx(1.0) - 100}px;top:{gy(3.95)}px">e{sup(i('x'))}</div>
"""
    t = lambda c: cue(n, c)
    js = f"""
      const X0 = {X0}, Y0 = {Y0}, U = {U};
      const gx = (x) => X0 + x * U, gy = (y) => Y0 - y * U;
      const fr = (v) => v.toFixed(2).replace(".", ",").replace("-", "−");  // virgule décimale, vrai signe moins
      const pt = q("#P-pt"), tg = q("#P-tan"), dr = q("#P-drop");
      const hv = q("#P-hval"), pv = q("#P-pval"), xv = q("#P-xnum");
      const apply = (x) => {{
        const y = Math.exp(x);
        pt.style.left = (gx(x) - 11) + "px"; pt.style.top = (gy(y) - 11) + "px";
        dr.style.left = (gx(x) - 1) + "px"; dr.style.top = gy(y) + "px"; dr.style.height = (Y0 - gy(y)) + "px";
        tg.setAttribute("x1", gx(x - 1.1)); tg.setAttribute("y1", gy(y - 1.1 * y));
        tg.setAttribute("x2", gx(x + 1.1)); tg.setAttribute("y2", gy(y + 1.1 * y));
        // valeurs affichées cohérentes entre elles : calculées à partir du x arrondi affiché
        const xr = Math.round(x * 100) / 100, yr = Math.exp(xr);
        hv.textContent = "≈ " + fr(yr); pv.textContent = "≈ " + fr(yr); xv.textContent = fr(xr);
      }};
      const P0 = {{ x: -1.5 }};
      apply(P0.x);
      up("#P-topbar", 0.05, 0.6, 16);
      tl.fromTo(qa(".P-read"), {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: E, stagger: 0.15 }}, {t("glisser")});
      fade("#P-xval", {t("glisser") + 0.3}, 0.5);
      tl.fromTo([pt, tg, dr], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {t("glisser") + 0.6});
      tl.fromTo(P0, {{ x: -1.5 }}, {{ x: 1.45, duration: 4.6, ease: "sine.inOut", onUpdate: () => apply(P0.x) }}, 1.0);
      tl.fromTo(P0, {{ x: 1.45 }}, {{ x: 1.0, duration: 1.4, ease: "power2.inOut", immediateRender: false, onUpdate: () => apply(P0.x) }}, 5.8);
      // en x = 1 : la valeur exacte est e (2,72 n'en est qu'une valeur approchée)
      tl.fromTo(qa("#P-hval, #P-pval"), {{ opacity: 1 }}, {{ opacity: 0, duration: 0.35 }}, {t("x1") + 0.8});
      fade("#P-hexact", {t("x1") + 1.0}, 0.45);
      fade("#P-pexact", {t("x1") + 1.1}, 0.45);
      fade("#P-eqh", {t("x1") + 1.3}, 0.45);
      fade("#P-eqp", {t("x1") + 1.4}, 0.45);
"""
    return n, "05-la-tangente-glisse", css, body, js


# ── Plan 6 — Pourquoi ────────────────────────────────────────────────────────
def frame6():
    n = 6
    css = """
      .P-line { position: absolute; left: 72px; font-size: 92px; line-height: 1; }
      .P-step { position: absolute; left: 72px; font-size: 26px; }
      .P-note { position: absolute; left: 72px; font-size: 46px; font-style: italic; color: @CALLOUT; }
      .P-result { position: absolute; left: 72px; right: 72px; top: 1270px; height: 300px; border-radius: 22px; background: @PEACH; }
      .P-result .P-m { position: absolute; left: 0; right: 0; top: 70px; text-align: center; font-size: 150px; line-height: 1; }
    """
    taux = frac(f"e{sup(i('x') + ' + ' + i('h'))} − e{sup(i('x'))}", i("h"))
    fact = f"= e{sup(i('x'))} × {frac(f'e{sup(i('h'))} − 1', i('h'))}"
    limh = f"{frac(f'e{sup(i('h'))} − 1', i('h'))} → 1"
    body = f"""
        <div id="P-topbar" class="P-topbar"><div class="P-title">Pourquoi ?</div><div class="P-tag P-mono">PARTIE 3 / 3</div></div>
        <div id="P-s1" class="P-step P-label" style="top:330px">Taux d'accroissement</div>
        <div id="P-l1" class="P-line P-m" style="top:400px">{taux}</div>
        <div id="P-l2" class="P-line P-m" style="top:600px;left:150px">{fact}</div>
        <div id="P-s2" class="P-step P-label" style="top:840px">Quand <span style="text-transform:none">h</span> → 0</div>
        <div id="P-l3" class="P-line P-m" style="top:910px">{limh}</div>
        <div id="P-n3" class="P-note" style="top:1120px">c'est la pente de e<sup style="font-size:0.6em">x</sup> en 0 (partie 2)</div>
        <div id="P-result" class="P-result"><div class="P-m">({EX})′ = {EX}</div></div>
"""
    t = lambda c: cue(n, c)
    js = f"""
      up("#P-topbar", 0.05, 0.6, 16);
      fade("#P-s1", {t("taux")}, 0.5);
      up("#P-l1", {t("taux") + 0.2}, 0.7, 24);
      up("#P-l2", {t("taux") + 2.5}, 0.7, 24);
      fade("#P-s2", {t("tend")}, 0.5);
      up("#P-l3", {t("tend") + 0.4}, 0.7, 24);
      fade("#P-n3", {t("pente0")}, 0.6);
      tl.fromTo(q("#P-result"), {{ opacity: 0, scale: 0.94 }}, {{ opacity: 1, scale: 1, duration: 0.7, ease: E }}, {t("donc")});
"""
    return n, "06-pourquoi", css, body, js


# ── Plan 7 — Un seul nombre ──────────────────────────────────────────────────
def frame7():
    n = 7
    css = """
      .P-e { left: 0; right: 0; top: 570px; text-align: center; font-size: 150px; line-height: 1; }
      .P-d { left: 0; right: 0; top: 820px; text-align: center; font-size: 112px; line-height: 1; }
      .P-paths { left: 0; right: 0; top: 1030px; text-align: center; font-size: 28px; }
      /* signature de l'utilisateur, d'après son canevas « Faïçal Zoubir Signature » */
      .P-sigwrap { position: absolute; left: 0; right: 0; top: 1150px; text-align: center; }
      .P-sig { display: inline-block; padding: 0 40px; font-family: "Mrs Saint Delafield", cursive; font-size: 172px; line-height: 1.15; color: @INK; white-space: nowrap; }
      .P-swash { position: absolute; left: 180px; top: 1322px; width: 720px; height: 56px; overflow: visible; }
      .P-ar { position: absolute; left: 0; right: 0; top: 1416px; display: flex; align-items: center; justify-content: center; gap: 24px; }
      .P-arrule { width: 90px; height: 1.5px; background: @ACC; }
      .P-artext { font-family: "Aref Ruqaa", serif; font-weight: 700; font-size: 48px; line-height: 1.2; color: @ACC; }
    """
    glitch = segments(330, caret_x=None)
    body = f"""
        <div id="P-glitch">
{glitch}
        </div>
        <div id="P-e" class="P-abs P-m P-e"><span id="P-esym" class="P-acc" style="display:inline-block">e</span> ≈ 2,71828…</div>
        <div id="P-d" class="P-abs P-m P-d">({EX})′ = {EX}</div>
        <div id="P-paths" class="P-abs P-label P-paths"><span id="P-w0">Limite</span><span id="P-w1"> · Courbes</span><span id="P-w2"> · Dérivée</span></div>
        <div class="P-sigwrap"><span id="P-sig" class="P-sig">Faïçal Zoubir</span></div>
        <svg id="P-swash" class="P-swash" viewBox="0 0 800 60" fill="none" aria-hidden="true">
          <path id="P-sw1" d="M14 44 C 170 12, 360 58, 560 30 S 740 8, 788 20" stroke="@ACC" stroke-width="3" stroke-linecap="round" stroke-dasharray="1000" />
          <path id="P-sw2" d="M120 50 C 300 34, 520 46, 690 36" stroke="@ACC" stroke-width="1.2" stroke-linecap="round" opacity="0.6" stroke-dasharray="1000" />
        </svg>
        <div id="P-ar" class="P-ar"><span class="P-arrule"></span><span class="P-artext" lang="ar" dir="rtl">فيصل زبير</span><span class="P-arrule"></span></div>
"""
    t = lambda c: cue(n, c)
    js = f"""
      tl.fromTo(qa(".P-seg"), {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: E, stagger: 0.08 }}, 0.05);
      fade("#P-w0", {t("trois") + 0.1}, 0.4);
      fade("#P-w1", {t("trois") + 0.75}, 0.4);
      fade("#P-w2", {t("trois") + 1.35}, 0.4);
      up("#P-d", {t("trois") + 1.45}, 0.7, 24);
      up("#P-e", {t("un_seul")}, 0.8, 30);
      pulse("#P-esym", {t("un_seul") + 0.95}, 1.25);
      // zone de révélation plus large que la boîte du texte : les boucles du F et du Z en dépassent
      tl.fromTo(q("#P-sig"), {{ clipPath: "inset(-70% 120% -70% -20%)" }}, {{ clipPath: "inset(-70% -20% -70% -20%)", duration: 1.8, ease: "power3.inOut" }}, {t("un_seul") + 1.4});
      tl.fromTo(qa("#P-sw1, #P-sw2"), {{ strokeDashoffset: 1000 }}, {{ strokeDashoffset: 0, duration: 1.2, ease: "power2.out" }}, {t("un_seul") + 2.8});
      up("#P-ar", {t("un_seul") + 3.4}, 0.8, 8);
"""
    return n, "07-un-seul-nombre", css, body, js


def fix_index():
    """Peint le fond de la racine de index.html avec le papier de la palette (l'assembleur lit frame.md)."""
    idx = ROOT / "index.html"
    html = re.sub(r"(#root \{[^}]*?background: )#[0-9A-Fa-f]{6}", lambda m: m.group(1) + PAPER, idx.read_text(), count=1)
    idx.write_text(html)


def main():
    if "--fix-index" in sys.argv:
        fix_index()
        return
    out = ROOT / "compositions" / "frames"
    out.mkdir(parents=True, exist_ok=True)
    for make in (frame1, frame2, frame3, frame4, frame5, frame6, frame7):
        num, fid, css, body, js = make()
        html = frame_doc(fid, num, dur(num), css, body, js)
        (out / f"{fid}.html").write_text(html)
        print("wrote", fid, dur(num), "s", f"({PALETTE})")


if __name__ == "__main__":
    main()
