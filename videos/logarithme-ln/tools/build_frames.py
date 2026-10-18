"""Logarithme ln — génère les 7 plans (compositions/frames/NN-*.html).

Infrastructure reprise de videos/exponentielle-e/tools/build_frames.py (palette, polices, gabarit).

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
                       FAINT="rgba(120,80,60,0.18)", RULE="rgba(31,26,23,0.28)", LABEL="#B4532F",
                       TITLE="#1F1A17", CARET="#1F1A17", CALLOUT="#CC6E50", LIGHT="#E9B89A"),
    "sombre": dict(INK="#F2EFE9", SOFT="#A8A39B", PAPER="#1E1E1E", ACC="#CB7B4F", ACCD="#CB7B4F",
                   SEG="#3A3734", BAR="#B8704A", PEACH="#2A2826", GRID="rgba(255,255,255,0.035)",
                   FAINT="rgba(255,255,255,0.12)", RULE="rgba(255,255,255,0.2)", LABEL="#A8A39B",
                   TITLE="#B9B4AC", CARET="#CB7B4F", CALLOUT="#A8A39B", LIGHT="#E3B08F"),
}
PALETTE = os.environ.get("PALETTE", "sombre")
PAL = PALETTES[PALETTE]
INK, INK_SOFT, PAPER, ACC = PAL["INK"], PAL["SOFT"], PAL["PAPER"], PAL["ACC"]

# ── petits outils de mise en forme mathématique (P = préfixe du plan) ───────────
def frac(a, b):
    return f'<span class="P-frac"><span>{a}</span><span>{b}</span></span>'


def sup(s):
    return f"<sup>{s}</sup>"


def i(s):
    return f"<i>{s}</i>"


LN = '<span class="P-fn">ln</span>'
EX = f'e{sup(i("x"))}'


def lim(sub_html):
    return f'<span class="P-lim"><span>lim</span><span class="P-limsub">{sub_html}</span></span>'


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
      .P-fn { font-style: normal; margin-right: 0.12em; }
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
          <div class="P-chrome" style="left:72px;top:58px">LOGARITHME — ln</div>
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


def cue_end(num, cid):
    return TIMING["frames"][f"{num:02d}"]["cues"][cid]["end"]


def dur(num):
    return TIMING["frames"][f"{num:02d}"]["duration"]


# ── Repères (plans 3 et 5) ────────────────────────────────────────────────────
class Graph:
    """Un repère : origine (X0, Y0) en px, unité U px, zone de tracé box = (x0, y0, x1, y1)."""

    def __init__(self, X0, Y0, U, box, xticks, yticks):
        self.X0, self.Y0, self.U, self.box = X0, Y0, U, box
        self.xticks, self.yticks = xticks, yticks

    def gx(self, x):
        return self.X0 + x * self.U

    def gy(self, y):
        return self.Y0 - y * self.U

    def path(self, pts):
        return "M" + " L".join(f"{self.gx(x):.1f},{self.gy(y):.1f}" for x, y in pts)

    def axes(self):
        x0, y0, x1, y1 = self.box
        X0, Y0 = self.X0, self.Y0
        ticks = [f'<line x1="{self.gx(k):.1f}" y1="{Y0 - 10}" x2="{self.gx(k):.1f}" y2="{Y0 + 10}" />' for k in self.xticks]
        ticks += [f'<line x1="{X0 - 10}" y1="{self.gy(k):.1f}" x2="{X0 + 10}" y2="{self.gy(k):.1f}" />' for k in self.yticks]
        arrows = (f'<path d="M{x1},{Y0} l-18,-9 v18 z" fill="{INK}" stroke="none"/>'
                  f'<path d="M{X0},{y0} l-9,18 h18 z" fill="{INK}" stroke="none"/>')
        return (f'<g stroke="{INK}" stroke-width="3" fill="none">'
                f'<line x1="{x0}" y1="{Y0}" x2="{x1}" y2="{Y0}" /><line x1="{X0}" y1="{y1}" x2="{X0}" y2="{y0}" />'
                + "".join(ticks) + arrows + "</g>")

    def labels(self):
        out = []
        for k in self.xticks:
            out.append(f'<div class="P-tick P-m" style="left:{self.gx(k) - 30:.1f}px;top:{self.Y0 + 14}px;width:60px">{fmt(k)}</div>')
        for k in self.yticks:
            out.append(f'<div class="P-tick P-m" style="left:{self.X0 - 72}px;top:{self.gy(k) - 20:.1f}px;width:52px;text-align:right">{fmt(k)}</div>')
        out.append(f'<div class="P-tick P-m" style="left:{self.X0 - 44}px;top:{self.Y0 + 14}px;width:30px">0</div>')
        out.append(f'<div class="P-axname P-m" style="left:{self.box[2] - 34}px;top:{self.Y0 - 70}px"><i>x</i></div>')
        out.append(f'<div class="P-axname P-m" style="left:{self.X0 + 20}px;top:{self.box[1] - 10}px"><i>y</i></div>')
        return "\n".join("        " + o for o in out)


def fmt(v):
    """Nombre à la française : virgule décimale, vrai signe moins."""
    s = f"{v:g}".replace(".", ",")
    return s.replace("-", "−")


GRAPH_CSS = """
      .P-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
      .P-tick { position: absolute; font-size: 34px; line-height: 1; text-align: center; }
      .P-axname { position: absolute; font-size: 48px; line-height: 1; }
      .P-clabel { position: absolute; font-size: 56px; line-height: 1; background: @PAPER; padding: 0 6px; }
      .P-pt { position: absolute; width: 20px; height: 20px; }
      .P-plabel { position: absolute; font-size: 40px; line-height: 1; background: @PAPER; padding: 2px 6px; }
"""


def clip_rect(cid, box):
    x0, y0, x1, y1 = box
    return f'<clipPath id="{cid}c"><rect id="{cid}" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" /></clipPath>'


# ── Plan 1 — La question ─────────────────────────────────────────────────────
def frame1():
    n = 1
    css = """
      .P-kicker { left: 76px; top: 236px; font-size: 30px; }
      .P-q { left: 96px; top: 330px; font-size: 260px; line-height: 1; }
      .P-callout { left: 100px; top: 640px; font-size: 58px; font-style: italic; color: @CALLOUT; }
      .P-sep { position: absolute; left: 100px; width: 300px; top: 770px; height: 2px; background: @ACC; }
      .P-ans { left: 96px; top: 830px; font-size: 120px; line-height: 1; }
      .P-anslabel { left: 100px; top: 1010px; font-size: 28px; }
    """
    body = f"""
        <div id="P-glitch">
{segments(1330, caret_x=470)}
        </div>
        <div id="P-kicker" class="P-abs P-label P-kicker">La fonction logarithme</div>
        <div id="P-q" class="P-abs P-m P-q">{EX} = 5</div>
        <div id="P-callout" class="P-abs P-callout">combien vaut <i>x</i> ?</div>
        <div id="P-sep" class="P-sep"></div>
        <div id="P-ans" class="P-abs P-m P-ans"><span id="P-ax">{i("x")} =</span> <span id="P-aln" class="P-acc" style="display:inline-block">{LN}5</span> <span id="P-aval">≈ 1,609</span></div>
        <div id="P-anslabel" class="P-abs P-label P-anslabel">Le logarithme népérien</div>
"""
    t, te = (lambda c: cue(n, c)), (lambda c: cue_end(n, c))
    js = f"""
      tl.fromTo(qa(".P-seg"), {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: E, stagger: 0.08 }}, 0.05);
      tl.fromTo(q("#P-caret"), {{ x: -362 }}, {{ x: 0, duration: {dur(n)}, ease: "none" }}, 0);
      fade("#P-kicker", 0.05, 0.5);
      up("#P-q", {t("question")}, 0.9, 40);
      fade("#P-callout", {t("question") + 1.5}, 0.7);
      grow("#P-sep", {t("nom")}, 0.6);
      fade("#P-ax", {t("nom") + 0.2}, 0.4);
      fade("#P-anslabel", {t("nom") + 1.3}, 0.5);
      tl.fromTo(q("#P-aln"), {{ opacity: 0, scale: 0.7, transformOrigin: "50% 60%" }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)" }}, {te("nom") - 0.45});
      fade("#P-aval", {te("nom") + 0.15}, 0.5);
"""
    return n, "01-la-question", css, body, js


# ── Plan 2 — Quatre idées ────────────────────────────────────────────────────
def frame2():
    n = 2
    css = """
      .P-row { position: absolute; left: 72px; right: 72px; height: 300px; border-bottom: 1.5px solid @FAINT; }
      .P-num { position: absolute; left: 0; top: 64px; font-size: 40px; }
      .P-formula { position: absolute; left: 110px; top: 70px; font-size: 92px; line-height: 1; }
      .P-desc { position: absolute; left: 114px; top: 218px; font-size: 30px; }
    """
    rows = [
        ("01", f"{i('y')} = {LN}{i('x')} ⟺ {i('x')} = e{sup(i('y'))}", "Réciproque de exp"),
        ("02", f"{LN}({i('ab')}) = {LN}{i('a')} + {LN}{i('b')}", "Produits en sommes"),
        ("03", f"({LN}{i('x')})′ = {frac('1', i('x'))}", "Dérivée"),
        ("04", f"{lim(i('x') + ' → +∞')}{LN}{i('x')} = +∞", "Limites et variations"),
    ]
    body = """
        <div id="P-topbar" class="P-topbar"><div class="P-title">Quatre idées</div><div class="P-tag P-mono">→ ln</div></div>
"""
    for k, (num, formula, desc) in enumerate(rows):
        body += f"""        <div id="P-row{k}" class="P-row" style="top:{320 + k * 312}px">
          <div class="P-num P-mono" style="color:@LABEL">{num}</div>
          <div class="P-formula P-m">{formula}</div>
          <div class="P-desc P-label">{desc}</div>
        </div>
"""
    t = lambda c: cue(n, c)
    js = f"""
      up("#P-topbar", 0.05, 0.6, 16);
      up("#P-row0", {t("reci") - 0.15}, 0.6, 30);
      up("#P-row1", {t("prod") - 0.15}, 0.6, 30);
      up("#P-row2", {t("deriv") - 0.15}, 0.6, 30);
      up("#P-row3", {t("lim") - 0.15}, 0.6, 30);
"""
    return n, "02-quatre-idees", css, body, js


# ── Plan 3 — Réciproque ──────────────────────────────────────────────────────
G3 = Graph(X0=439.7, Y0=1018.3, U=167.14, box=(72, 450, 1008, 1386), xticks=(-2, -1, 1, 2, 3), yticks=(-2, -1, 1, 2, 3))


def frame3():
    n = 3
    g = G3
    e = math.e
    exp_pts = [(x / 100, math.exp(x / 100)) for x in range(-220, 123)]
    css = GRAPH_CSS + f"""
      .P-def {{ left: 72px; top: 318px; font-size: 76px; line-height: 1; }}
      .P-cond {{ left: 760px; top: 340px; font-size: 40px; color: @SOFT; }}
      .P-flip {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: {g.X0}px {g.Y0}px; }}
      .P-res {{ top: 1430px; font-size: 84px; line-height: 1; }}
    """
    flip_svg = (f'<svg class="P-svg" viewBox="0 0 1080 1920"><path d="{g.path(exp_pts)}" fill="none" '
                f'stroke="{ACC}" stroke-width="6" stroke-linecap="round" /></svg>')
    pts = [("P-pa", 0, 1, INK), ("P-pb", 1, 0, ACC), ("P-pc", 1, e, INK), ("P-pd", e, 1, ACC)]
    pt_html = "\n".join(
        f'        <div id="{pid}" class="P-pt" style="left:{g.gx(x) - 10:.1f}px;top:{g.gy(y) - 10:.1f}px;background:{col}"></div>'
        for pid, x, y, col in pts)
    body = f"""
        <div id="P-topbar" class="P-topbar"><div class="P-title">Réciproque</div><div class="P-tag P-mono">PARTIE 1 / 4</div></div>
        <div id="P-def" class="P-abs P-m P-def">{i('y')} = {LN}{i('x')} ⟺ {i('x')} = e{sup(i('y'))}</div>
        <div id="P-cond" class="P-abs P-m P-cond">({i('x')} &gt; 0)</div>
        <svg class="P-svg" viewBox="0 0 1080 1920">
          <defs>
            <clipPath id="P-box"><rect x="{g.box[0]}" y="{g.box[1]}" width="{g.box[2] - g.box[0]}" height="{g.box[3] - g.box[1]}" /></clipPath>
            {clip_rect("P-rexp", g.box)}
            {clip_rect("P-rid", g.box)}
          </defs>
          <g id="P-axes">{g.axes()}</g>
          <g clip-path="url(#P-box)" fill="none">
            <line id="P-id" clip-path="url(#P-ridc)" x1="{g.gx(-2.6):.1f}" y1="{g.gy(-2.6):.1f}" x2="{g.gx(3.6):.1f}" y2="{g.gy(3.6):.1f}" stroke="{INK_SOFT}" stroke-width="2.5" stroke-dasharray="4 10" stroke-linecap="round" />
            <path id="P-exp" clip-path="url(#P-rexpc)" d="{g.path(exp_pts)}" stroke="{INK}" stroke-width="3.5" stroke-dasharray="12 9" />
            <line id="P-c1" x1="{g.gx(0):.1f}" y1="{g.gy(1):.1f}" x2="{g.gx(1):.1f}" y2="{g.gy(0):.1f}" stroke="{INK_SOFT}" stroke-width="2" stroke-dasharray="6 8" />
            <line id="P-c2" x1="{g.gx(1):.1f}" y1="{g.gy(e):.1f}" x2="{g.gx(e):.1f}" y2="{g.gy(1):.1f}" stroke="{INK_SOFT}" stroke-width="2" stroke-dasharray="6 8" />
          </g>
        </svg>
{g.labels()}
        <div id="P-flip" class="P-flip">{flip_svg}</div>
{pt_html}
        <div id="P-lexp" class="P-clabel P-m" style="left:{g.gx(1.3):.1f}px;top:{g.gy(3.38):.1f}px">{EX}</div>
        <div id="P-lid" class="P-clabel P-m" style="left:{g.gx(2.45):.1f}px;top:{g.gy(3.3):.1f}px;color:{INK_SOFT}">{i('y')} = {i('x')}</div>
        <div id="P-lln" class="P-clabel P-m P-acc" style="left:{g.gx(2.7):.1f}px;top:{g.gy(0.72):.1f}px">{LN}</div>
        <div id="P-la" class="P-plabel P-m" style="left:{g.gx(-1.0):.1f}px;top:{g.gy(1.3):.1f}px">(0 ; 1)</div>
        <div id="P-lb" class="P-plabel P-m P-acc" style="left:{g.gx(1.1):.1f}px;top:{g.gy(-0.12):.1f}px">(1 ; 0)</div>
        <div id="P-lc" class="P-plabel P-m" style="left:{g.gx(1.14):.1f}px;top:{g.gy(e + 0.12):.1f}px">(1 ; e)</div>
        <div id="P-ld" class="P-plabel P-m P-acc" style="left:{g.gx(e + 0.12):.1f}px;top:{g.gy(1.45):.1f}px">(e ; 1)</div>
        <div id="P-r1" class="P-abs P-m P-res" style="left:72px">{LN}1 = <span class="P-acc">0</span></div>
        <div id="P-r2" class="P-abs P-m P-res" style="left:600px">{LN}e = <span class="P-acc">1</span></div>
"""
    t = lambda c: cue(n, c)
    bw = g.box[2] - g.box[0]
    js = f"""
      const flip = q("#P-flip"), F = {{ a: 0 }};
      const setFlip = () => {{ flip.style.transform = "perspective(2600px) rotate(-45deg) rotateX(" + F.a + "deg) rotate(45deg)"; }};
      setFlip();
      up("#P-topbar", 0.05, 0.6, 16);
      up("#P-def", {t("def")}, 0.8, 26);
      fade("#P-cond", {t("def") + 1.6}, 0.5);
      fade("#P-axes", 1.2, 0.6);
      tl.fromTo(qa(".P-tick, .P-axname"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, stagger: 0.03 }}, 1.4);
      sweep("#P-rexp", 2.0, 1.8, {bw});
      fade("#P-lexp", 3.6, 0.5);
      sweep("#P-rid", {t("reflet") + 0.2}, 1.0, {bw});
      fade("#P-lid", {t("reflet") + 1.0}, 0.5);
      tl.fromTo(flip, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t("reflet") + 1.3});
      tl.fromTo(F, {{ a: 0 }}, {{ a: 180, duration: 2.8, ease: "power2.inOut", onUpdate: setFlip }}, {t("reflet") + 1.6});
      fade("#P-lln", {t("reflet") + 4.5}, 0.5);
      tl.fromTo(qa("#P-pa, #P-pb"), {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)", stagger: 0.5 }}, {t("p1") + 0.1});
      fade("#P-c1", {t("p1") + 0.5}, 0.5);
      fade("#P-la", {t("p1") + 0.3}, 0.4);
      fade("#P-lb", {t("p1") + 0.9}, 0.4);
      up("#P-r1", {t("ln1")}, 0.6, 20);
      tl.fromTo(qa("#P-pc, #P-pd"), {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)", stagger: 0.5 }}, {t("p2") + 0.1});
      fade("#P-c2", {t("p2") + 0.5}, 0.5);
      fade("#P-lc", {t("p2") + 0.3}, 0.4);
      fade("#P-ld", {t("p2") + 0.9}, 0.4);
      up("#P-r2", {t("lne")}, 0.6, 20);
"""
    return n, "03-reciproque", css, body, js


# ── Plan 4 — Produits en sommes ──────────────────────────────────────────────
BX, U4 = 440, 316  # début des barres (px) et px par unité


def frame4():
    n = 4
    ln2, ln3, ln6 = math.log(2), math.log(3), math.log(6)
    css = """
      .P-formula { left: 72px; top: 318px; font-size: 96px; line-height: 1; }
      .P-cond { left: 76px; top: 440px; font-size: 26px; }
      .P-blab { position: absolute; left: 72px; font-size: 54px; line-height: 1; }
      .P-bar { position: absolute; height: 44px; border-radius: 9px; }
      .P-end { position: absolute; width: 0; border-left: 3px dashed @SOFT; }
      .P-eq { left: 72px; top: 980px; font-size: 80px; line-height: 1; }
      .P-ded { left: 76px; top: 1130px; font-size: 26px; }
      .P-cons { left: 72px; font-size: 80px; line-height: 1; }
    """
    rows = [  # (id, étiquette, valeur, y, barres [(id, x, largeur, couleur)])
        ("A", f"{LN}2", "≈ 0,693", 545, [("P-bA", BX, ln2 * U4, "@ACC")]),
        ("B", f"{LN}3", "≈ 1,099", 640, [("P-bB", BX, ln3 * U4, "@LIGHT")]),
        ("C", f"{LN}2 + {LN}3", "", 755, [("P-bC1", BX, ln2 * U4, "@ACC"), ("P-bC2", BX + ln2 * U4, ln3 * U4, "@LIGHT")]),
        ("D", f"{LN}6", "≈ 1,792", 850, [("P-bD", BX, ln6 * U4, "@ACC")]),
    ]
    body = f"""
        <div id="P-topbar" class="P-topbar"><div class="P-title">Produits en sommes</div><div class="P-tag P-mono">PARTIE 2 / 4</div></div>
        <div id="P-formula" class="P-abs P-m P-formula"><span id="P-fl">{LN}({i('ab')})</span> <span id="P-fr">= {LN}{i('a')} + {LN}{i('b')}</span></div>
        <div id="P-cond" class="P-abs P-label P-cond">pour <span style="text-transform:none"><i>a</i> &gt; 0 et <i>b</i> &gt; 0</span></div>
"""
    for rid, lab, val, y, bars in rows:
        vspan = f' <span id="P-v{rid}" style="color:@SOFT">{val}</span>' if val else ""
        body += f'        <div id="P-l{rid}" class="P-blab P-m" style="top:{y - 6}px">{lab}{vspan}</div>\n'
        for bid, x, w, col in bars:
            r = "border-radius:9px 0 0 9px;" if bid == "P-bC1" else ("border-radius:0 9px 9px 0;" if bid == "P-bC2" else "")
            body += f'        <div id="{bid}" class="P-bar" style="left:{x:.1f}px;width:{w:.1f}px;top:{y}px;background:{col};{r}"></div>\n'
    body += f"""        <div id="P-end" class="P-end" style="left:{BX + ln6 * U4 - 1.5:.1f}px;top:735px;height:180px"></div>
        <div id="P-eq" class="P-abs P-m P-eq">{LN}2 + {LN}3 = <span class="P-acc">{LN}6</span></div>
        <div id="P-ded" class="P-abs P-label P-ded">On en déduit</div>
        <div id="P-q" class="P-abs P-m P-cons" style="top:1190px">{LN}{frac(i('a'), i('b'))} = {LN}{i('a')} − {LN}{i('b')}</div>
        <div id="P-p" class="P-abs P-m P-cons" style="top:1360px">{LN}({i('a')}{sup(i('n'))}) = {i('n')} {LN}{i('a')}</div>
"""
    t = lambda c: cue(n, c)
    grow_bar = lambda bid, at, d=0.7: f'      grow("#{bid}", {at:.3f}, {d});\n'
    js = f"""
      up("#P-topbar", 0.05, 0.6, 16);
      fade("#P-fl", {t("prop") + 0.3}, 0.6);
      fade("#P-fr", {t("formule") + 0.4}, 0.7);
      fade("#P-cond", {t("formule") + 1.6}, 0.5);
      fade("#P-lA", {t("ex") + 0.6}, 0.4);
{grow_bar("P-bA", t("ex") + 0.7)}      fade("#P-lB", {t("ex") + 1.5}, 0.4);
{grow_bar("P-bB", t("ex") + 1.6)}      fade("#P-lC", {t("ex") + 2.2}, 0.4);
{grow_bar("P-bC1", t("ex") + 2.3, 0.5)}{grow_bar("P-bC2", t("ex") + 2.8, 0.5)}      fade("#P-lD", {t("ex") + 3.0}, 0.4);
{grow_bar("P-bD", t("ex") + 3.1)}      tl.fromTo(q("#P-end"), {{ scaleY: 0, transformOrigin: "50% 0%" }}, {{ scaleY: 1, duration: 0.6, ease: E }}, {t("ex") + 3.6});
      fade("#P-vA", {t("nums") + 0.4}, 0.4);
      fade("#P-vB", {t("nums") + 2.3}, 0.4);
      fade("#P-vD", {t("nums") + 4.4}, 0.4);
      up("#P-eq", {t("nums") + 5.2}, 0.7, 20);
      fade("#P-ded", {t("quot")}, 0.4);
      up("#P-q", {t("quot") + 1.0}, 0.7, 24);
      up("#P-p", {t("puiss") + 0.3}, 0.7, 24);
"""
    return n, "04-produits-en-sommes", css, body, js


# ── Plan 5 — La dérivée ──────────────────────────────────────────────────────
G5 = Graph(X0=133.0, Y0=814.7, U=203.48, box=(72, 540, 1008, 1140), xticks=(1, 2, 3, 4), yticks=(-1, 1))


def frame5():
    n = 5
    g = G5
    ln_pts = [(math.exp(y / 100), y / 100) for y in range(-160, 136)]
    css = GRAPH_CSS + """
      .P-read { position: absolute; top: 300px; width: 452px; height: 210px; border-top: 2px solid @INK; }
      .P-rlab { position: absolute; left: 0; top: 18px; font-size: 26px; }
      .P-rval { position: absolute; left: 0; top: 62px; font-size: 120px; line-height: 1; }
      .P-proof { position: absolute; left: 72px; font-size: 60px; line-height: 1; }
      .P-plab { left: 76px; top: 1180px; font-size: 26px; }
      .P-box2 { position: absolute; left: 72px; right: 72px; top: 1440px; height: 140px; border-radius: 22px; background: @PEACH; }
      .P-box2 .P-m { position: absolute; left: 0; right: 0; top: 26px; text-align: center; font-size: 88px; line-height: 1; }
    """
    body = f"""
        <div id="P-topbar" class="P-topbar"><div class="P-title">La dérivée</div><div class="P-tag P-mono">PARTIE 3 / 4</div></div>
        <div id="P-read0" class="P-read" style="left:72px"><div class="P-rlab P-label">Abscisse <span style="text-transform:none"><i>x</i></span></div><div id="P-xval" class="P-rval P-m">1</div></div>
        <div id="P-read1" class="P-read" style="left:556px"><div class="P-rlab P-label">Pente = 1/<span style="text-transform:none"><i>x</i></span></div><div id="P-pval" class="P-rval P-m P-acc">1</div></div>
        <svg class="P-svg" viewBox="0 0 1080 1920">
          <defs>
            <clipPath id="P-box"><rect x="{g.box[0]}" y="{g.box[1]}" width="{g.box[2] - g.box[0]}" height="{g.box[3] - g.box[1]}" /></clipPath>
          </defs>
          {g.axes()}
          <g clip-path="url(#P-box)" fill="none">
            <path id="P-ln" d="{g.path(ln_pts)}" stroke="{ACC}" stroke-width="6" />
            <line id="P-tan" x1="0" y1="0" x2="0" y2="0" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" />
          </g>
        </svg>
{g.labels()}
        <div id="P-pt" class="P-pt" style="left:0;top:0;background:{INK}"></div>
        <div id="P-lln" class="P-clabel P-m P-acc" style="left:{g.gx(3.45):.1f}px;top:{g.gy(0.95):.1f}px">{LN}</div>
        <div id="P-plab" class="P-abs P-label P-plab">Preuve</div>
        <div id="P-l1" class="P-proof P-m" style="top:1225px">e{sup(LN + i('x'))} = {i('x')} <span style="color:@SOFT;font-size:0.6em">pour {i('x')} &gt; 0</span></div>
        <div id="P-l2" class="P-proof P-m" style="top:1300px">({LN}{i('x')})′ × e{sup(LN + i('x'))} = 1</div>
        <div id="P-l3" class="P-proof P-m" style="top:1372px">({LN}{i('x')})′ × {i('x')} = 1</div>
        <div id="P-res" class="P-box2"><div class="P-m">({LN}{i('x')})′ = <span class="P-acc">{frac('1', i('x'))}</span></div></div>
"""
    t, te = (lambda c: cue(n, c)), (lambda c: cue_end(n, c))
    js = f"""
      const X0 = {g.X0}, Y0 = {g.Y0}, U = {g.U};
      const gx = (x) => X0 + x * U, gy = (y) => Y0 - y * U;
      const pt = q("#P-pt"), tg = q("#P-tan"), xv = q("#P-xval"), pv = q("#P-pval");
      // valeurs exactes aux arrêts (1 ; 2 ; 0,5), sinon valeurs arrondies précédées de « ≈ »
      const exact = {{ "1": ["1", "1"], "2": ["2", "0,5"], "0.5": ["0,5", "2"] }};
      const fr = (v) => v.toFixed(2).replace(".", ",");
      const apply = (x) => {{
        const y = Math.log(x), m = 1 / x, h = 0.95 / Math.sqrt(1 + m * m);
        pt.style.left = (gx(x) - 10) + "px"; pt.style.top = (gy(y) - 10) + "px";
        tg.setAttribute("x1", gx(x - h)); tg.setAttribute("y1", gy(y - m * h));
        tg.setAttribute("x2", gx(x + h)); tg.setAttribute("y2", gy(y + m * h));
        const key = Object.keys(exact).find((k) => Math.abs(x - Number(k)) < 5e-4);
        if (key) {{ xv.textContent = exact[key][0]; pv.textContent = exact[key][1]; }}
        else {{ const xr = Math.round(x * 100) / 100; xv.textContent = "≈ " + fr(xr); pv.textContent = "≈ " + fr(1 / xr); }}
      }};
      const P0 = {{ x: 0.3 }};
      apply(P0.x);
      const go = (from, to, at, d, ease = "power2.inOut") =>
        tl.fromTo(P0, {{ x: from }}, {{ x: to, duration: d, ease, immediateRender: false, onUpdate: () => apply(P0.x) }}, at);
      up("#P-topbar", 0.05, 0.6, 16);
      fade("#P-lln", 0.4, 0.5);
      tl.fromTo(qa(".P-read"), {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: E, stagger: 0.15 }}, {t("glisse")});
      tl.fromTo([pt, tg], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t("glisse") + 0.3});
      go(0.3, 3.4, {t("glisse") + 0.5}, 1.6);
      go(3.4, 1.0, {t("glisse") + 2.2}, 1.0);
      go(1.0, 2.0, {t("x2") - 0.1}, 0.7);
      go(2.0, 0.5, {t("xdemi") - 0.1}, 0.8);
      go(0.5, 3.6, {t("toujours") + 0.1}, 1.6, "sine.inOut");
      go(3.6, 1.5, {t("toujours") + 1.8}, 1.1);
      fade("#P-plab", {t("preuve")}, 0.4);
      up("#P-l1", {t("preuve") + 0.6}, 0.6, 20);
      up("#P-l2", {t("obtient") + 0.2}, 0.6, 20);
      up("#P-l3", {t("obtient") + 1.6}, 0.6, 20);
      tl.fromTo(q("#P-res"), {{ opacity: 0, scale: 0.94 }}, {{ opacity: 1, scale: 1, duration: 0.7, ease: E }}, {t("donc")});
"""
    return n, "05-la-derivee", css, body, js


# ── Plan 6 — Limites et variations ───────────────────────────────────────────
def frame6():
    n = 6
    L, R, T = 72, 1008, 450  # tableau : gauche, droite, haut
    COL, R1, R2, B = 322, 540, 630, 900  # séparateur vertical, lignes, bas
    XA, XB, XC = 368, 668, 962  # abscisses 0, 1, +∞
    css = GRAPH_CSS + """
      .P-l1 { left: 72px; top: 312px; font-size: 60px; line-height: 1; }
      .P-tv { position: absolute; width: 160px; margin-left: -80px; text-align: center; font-size: 54px; line-height: 1; }
      .P-tl { position: absolute; left: 96px; font-size: 54px; line-height: 1; }
      .P-limrow { left: 72px; font-size: 62px; line-height: 1; }
      .P-slow { left: 72px; top: 1180px; font-size: 44px; font-style: italic; color: @CALLOUT; }
      .P-big { left: 72px; top: 1260px; font-size: 104px; line-height: 1; }
      .P-bigcap { left: 76px; top: 1420px; font-size: 26px; }
    """
    grid = (f'<g stroke="{INK}" stroke-width="2" fill="none">'
            f'<rect x="{L}" y="{T}" width="{R - L}" height="{B - T}" />'
            f'<line x1="{L}" y1="{R1}" x2="{R}" y2="{R1}" /><line x1="{L}" y1="{R2}" x2="{R}" y2="{R2}" />'
            f'<line x1="{COL}" y1="{T}" x2="{COL}" y2="{B}" />'
            f'<line x1="{XA - 26}" y1="{R1}" x2="{XA - 26}" y2="{B}" /><line x1="{XA - 18}" y1="{R1}" x2="{XA - 18}" y2="{B}" />'
            '</g>')

    def arrow(aid, x1, y1, x2, y2):
        ang = math.atan2(y2 - y1, x2 - x1)
        hx, hy = x2 - 22 * math.cos(ang), y2 - 22 * math.sin(ang)
        px, py = -math.sin(ang) * 9, math.cos(ang) * 9
        return (f'<g id="{aid}"><line x1="{x1}" y1="{y1}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{ACC}" stroke-width="4" stroke-linecap="round" />'
                f'<path d="M{x2},{y2} L{hx + px:.1f},{hy + py:.1f} L{hx - px:.1f},{hy - py:.1f} Z" fill="{ACC}" /></g>')

    body = f"""
        <div id="P-topbar" class="P-topbar"><div class="P-title">Variations</div><div class="P-tag P-mono">PARTIE 4 / 4</div></div>
        <div id="P-l1" class="P-abs P-m P-l1">({LN}{i('x')})′ = {frac('1', i('x'))} &gt; 0 sur ]0 ; +∞[</div>
        <svg class="P-svg" viewBox="0 0 1080 1920">
          <g id="P-grid">{grid}</g>
          {arrow("P-a1", XA + 102, B - 50, XB - 40, (R2 + B) / 2 + 10)}
          {arrow("P-a2", XB + 40, (R2 + B) / 2 - 10, XC - 80, R2 + 60)}
        </svg>
        <div id="P-tlx" class="P-tl P-m" style="top:{T + 18}px"><i>x</i></div>
        <div id="P-tld" class="P-tl P-m" style="top:{R1 + 18}px">({LN}{i('x')})′</div>
        <div id="P-tll" class="P-tl P-m" style="top:{(R2 + B) / 2 - 27}px">{LN}{i('x')}</div>
        <div id="P-x0" class="P-tv P-m" style="left:{XA}px;top:{T + 18}px">0</div>
        <div id="P-x1" class="P-tv P-m" style="left:{XB}px;top:{T + 18}px">1</div>
        <div id="P-x2" class="P-tv P-m" style="left:{XC}px;top:{T + 18}px">+∞</div>
        <div id="P-s1" class="P-tv P-m P-acc" style="left:{(XA + XB) / 2}px;top:{R1 + 18}px">+</div>
        <div id="P-s2" class="P-tv P-m P-acc" style="left:{(XB + XC) / 2}px;top:{R1 + 18}px">+</div>
        <div id="P-vm" class="P-tv P-m" style="left:{XA + 40}px;top:{B - 70}px">−∞</div>
        <div id="P-v0" class="P-tv P-m" style="left:{XB}px;top:{(R2 + B) / 2 - 27}px">0</div>
        <div id="P-vp" class="P-tv P-m" style="left:{XC - 30}px;top:{R2 + 16}px">+∞</div>
        <div id="P-lim0" class="P-abs P-m P-limrow" style="top:950px">{lim(i('x') + ' → 0<sup>+</sup>')}{LN}{i('x')} = −∞</div>
        <div id="P-liminf" class="P-abs P-m P-limrow" style="top:1070px">{lim(i('x') + ' → +∞')}{LN}{i('x')} = +∞</div>
        <div id="P-slow" class="P-abs P-slow">… mais très lentement</div>
        <div id="P-big" class="P-abs P-m P-big">{LN}(1 000 000) <span class="P-acc">≈ <span id="P-cnt">13,8</span></span></div>
        <div id="P-bigcap" class="P-abs P-label P-bigcap">Un million → à peine 13,8</div>
"""
    t, te = (lambda c: cue(n, c)), (lambda c: cue_end(n, c))
    js = f"""
      const cnt = q("#P-cnt"), C = {{ v: 0 }};
      const showC = () => {{ cnt.textContent = C.v.toFixed(1).replace(".", ","); }};
      up("#P-topbar", 0.05, 0.6, 16);
      up("#P-l1", {t("croiss")}, 0.7, 20);
      fade("#P-grid", 1.4, 0.6);
      tl.fromTo(qa("#P-tlx, #P-tld, #P-tll"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, stagger: 0.12 }}, 1.6);
      tl.fromTo(qa("#P-x0, #P-x1, #P-x2"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, stagger: 0.12 }}, 1.9);
      tl.fromTo(qa("#P-s1, #P-s2"), {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1, duration: 0.4, stagger: 0.15 }}, 2.1);
      tl.fromTo(qa("#P-a1, #P-a2"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, stagger: 0.4 }}, {te("croiss") - 1.2});
      fade("#P-v0", {te("croiss") - 0.7}, 0.4);
      up("#P-lim0", {t("lim0") + 0.2}, 0.6, 18);
      fade("#P-vm", {te("lim0") - 0.6}, 0.4);
      up("#P-liminf", {t("liminf") + 0.2}, 0.6, 18);
      fade("#P-vp", {te("liminf") - 0.7}, 0.4);
      fade("#P-slow", {t("lent")}, 0.5);
      up("#P-big", {t("million")}, 0.6, 20);
      tl.fromTo(C, {{ v: 0 }}, {{ v: 13.8, duration: 2.0, ease: "power2.out", onUpdate: showC }}, {t("million") + 0.6});
      fade("#P-bigcap", {te("million") - 0.4}, 0.5);
"""
    return n, "06-limites-et-variations", css, body, js


# ── Plan 7 — Voilà ln ────────────────────────────────────────────────────────
def frame7():
    n = 7
    css = """
      .P-f { left: 0; right: 0; text-align: center; font-size: 80px; line-height: 1; }
      .P-paths { left: 0; right: 0; top: 1000px; text-align: center; font-size: 28px; }
      /* signature de l'utilisateur, d'après son canevas « Faïçal Zoubir Signature » */
      .P-sigwrap { position: absolute; left: 0; right: 0; top: 1150px; text-align: center; }
      .P-sig { display: inline-block; padding: 0 40px; font-family: "Mrs Saint Delafield", cursive; font-size: 172px; line-height: 1.15; color: @INK; white-space: nowrap; }
      .P-swash { position: absolute; left: 180px; top: 1322px; width: 720px; height: 56px; overflow: visible; }
      .P-ar { position: absolute; left: 0; right: 0; top: 1416px; display: flex; align-items: center; justify-content: center; gap: 24px; }
      .P-arrule { width: 90px; height: 1.5px; background: @ACC; }
      .P-artext { font-family: "Aref Ruqaa", serif; font-weight: 700; font-size: 48px; line-height: 1.2; color: @ACC; }
    """
    lnacc = '<span class="P-fn P-acc">ln</span>'
    body = f"""
        <div id="P-glitch">
{segments(330, caret_x=None)}
        </div>
        <div id="P-f1" class="P-abs P-m P-f" style="top:520px">{i('y')} = {lnacc}{i('x')} ⟺ {i('x')} = e{sup(i('y'))}</div>
        <div id="P-f2" class="P-abs P-m P-f" style="top:680px">{lnacc}({i('ab')}) = {lnacc}{i('a')} + {lnacc}{i('b')}</div>
        <div id="P-f3" class="P-abs P-m P-f" style="top:840px">({lnacc}{i('x')})′ = {frac('1', i('x'))}</div>
        <div id="P-paths" class="P-abs P-label P-paths"><span id="P-w0">Réciproque</span><span id="P-w1"> · Produits</span><span id="P-w2"> · Dérivée</span></div>
        <div class="P-sigwrap"><span id="P-sig" class="P-sig">Faïçal Zoubir</span></div>
        <svg id="P-swash" class="P-swash" viewBox="0 0 800 60" fill="none" aria-hidden="true">
          <path id="P-sw1" d="M14 44 C 170 12, 360 58, 560 30 S 740 8, 788 20" stroke="@ACC" stroke-width="3" stroke-linecap="round" stroke-dasharray="1000" />
          <path id="P-sw2" d="M120 50 C 300 34, 520 46, 690 36" stroke="@ACC" stroke-width="1.2" stroke-linecap="round" opacity="0.6" stroke-dasharray="1000" />
        </svg>
        <div id="P-ar" class="P-ar"><span class="P-arrule"></span><span class="P-artext" lang="ar" dir="rtl">فيصل زبير</span><span class="P-arrule"></span></div>
"""
    t, te = (lambda c: cue(n, c)), (lambda c: cue_end(n, c))
    js = f"""
      tl.fromTo(qa(".P-seg"), {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: E, stagger: 0.08 }}, 0.05);
      up("#P-f1", {t("resume") + 0.1}, 0.7, 22);
      fade("#P-w0", {t("resume") + 0.3}, 0.4);
      up("#P-f2", {t("resume") + 1.7}, 0.7, 22);
      fade("#P-w1", {t("resume") + 1.9}, 0.4);
      up("#P-f3", {t("resume") + 2.9}, 0.7, 22);
      fade("#P-w2", {t("resume") + 3.1}, 0.4);
      // zone de révélation plus large que la boîte du texte : les boucles du F et du Z en dépassent
      tl.fromTo(q("#P-sig"), {{ clipPath: "inset(-70% 120% -70% -20%)" }}, {{ clipPath: "inset(-70% -20% -70% -20%)", duration: 1.8, ease: "power3.inOut" }}, {te("voila") + 0.3});
      tl.fromTo(qa("#P-sw1, #P-sw2"), {{ strokeDashoffset: 1000 }}, {{ strokeDashoffset: 0, duration: 1.2, ease: "power2.out" }}, {te("voila") + 1.7});
      up("#P-ar", {te("voila") + 2.3}, 0.8, 8);
"""
    return n, "07-voila-ln", css, body, js


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
