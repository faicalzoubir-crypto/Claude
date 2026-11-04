"""Génère les 11 scènes HTML (1080×1920) de compteur-vespa-13 dans compositions/frames/.

Lit tools/plan.json (écrit par tools/construire.py) pour les durées.

  python3 tools/scenes.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = {s["id"]: s for s in json.loads((ROOT / "tools/plan.json").read_text())["scenes"]}
IDS = list(PLAN)
N = len(IDS)

FONTS = """    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-500-normal.woff2") format("woff2"); font-weight: 500; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-600-normal.woff2") format("woff2"); font-weight: 600; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-700-normal.woff2") format("woff2"); font-weight: 700; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-Regular.woff2") format("woff2"); font-weight: 400; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-Medium.woff2") format("woff2"); font-weight: 500; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-SemiBold.woff2") format("woff2"); font-weight: 600; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-Bold.woff2") format("woff2"); font-weight: 700; }"""

BASE_CSS = """    #root { position: absolute; inset: 0; overflow: hidden; font-family: "Inter", sans-serif; color: #E8EEEC; }
    #PX-bg { position: absolute; inset: 0; background: #0D1316; background-image: linear-gradient(to right, rgba(38, 52, 59, 0.55) 1.5px, transparent 1.5px), linear-gradient(to bottom, rgba(38, 52, 59, 0.55) 1.5px, transparent 1.5px); background-size: 60px 60px; }
    #PX-eyebrow { position: absolute; left: 108px; top: 170px; display: flex; align-items: center; gap: 18px;
      font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 28px; letter-spacing: 0.08em; text-transform: uppercase; color: #F4A62A; }
    #PX-eyebrow .PX-line { width: 60px; height: 4px; border-radius: 2px; background: #F4A62A; }
    #PX-h2 { position: absolute; left: 108px; top: 214px; width: 864px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 54px; line-height: 1.12; letter-spacing: -0.02em; }
    .PX-hl { color: #F4A62A; }
    .PX-card { position: absolute; border-radius: 14px; background: #141D21; border: 1.5px solid #26343B; overflow: hidden; }
    .PX-fig { position: absolute; border-radius: 14px; border: 1.5px solid #26343B; overflow: hidden; background: #2A3136; }
    .PX-fig img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
    .PX-ring { position: absolute; border-radius: 50%; border: 5px solid #F4A62A; box-shadow: 0 0 0 6px rgba(244, 166, 42, 0.18); }
    .PX-tag { position: absolute; padding: 8px 16px; border-radius: 100px; background: #F4A62A; color: #0D1316;
      font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 28px; white-space: nowrap; }
    #PX-progress { position: absolute; left: 0; bottom: 0; height: 6px; background: #F4A62A; }"""


def scene(sid, css, body, js):
    i = IDS.index(sid)
    d = PLAN[sid]["duree"]
    px = "f" + sid[:2]
    w0, w1 = round(i / N * 100, 2), round((i + 1) / N * 100, 2)
    html = f"""<template>
  <script src="vendor/gsap.min.js"></script>
  <style>
{FONTS}
{BASE_CSS}
{css}
  </style>

  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920" data-duration="{d}">
    <div id="PX-bg" class="clip" data-start="0" data-duration="{d}" data-track-index="0"></div>
    <div id="PX-stage">
{body}
      <div id="PX-progress"></div>
    </div>
  </div>

  <script>
    (function () {{
      const D = {d}, E = "power3.out";
      const tl = gsap.timeline({{ paused: true }});
      const rise = (sel, at, dy = 24, dur = 0.55) => tl.fromTo(sel, {{ opacity: 0, y: dy }}, {{ opacity: 1, y: 0, duration: dur, ease: E }}, at);
      const pop = (sel, at, dur = 0.45) => tl.fromTo(sel, {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: dur, ease: "back.out(1.6)" }}, at);
      tl.fromTo("#PX-progress", {{ width: "{w0}%" }}, {{ width: "{w1}%", duration: D, ease: "none" }}, 0);
{js}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""
    (ROOT / f"compositions/frames/{sid}.html").write_text(html.replace("PX", px), encoding="utf-8")


def eyebrow(texte):
    return f'      <div id="PX-eyebrow"><span class="PX-line"></span><span>{texte}</span></div>'


INTRO_JS = """      tl.fromTo("#PX-eyebrow", { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.5, ease: E }, 0.05);
      rise("#PX-h2", 0.15);"""

# Figure : roue avant (à droite, sous le tablier) à 78 % / 57 % de l'image, roue arrière à 48 % / 77 %.
FIG_W, FIG_H = 2238, 1742
AV = (0.754, 0.593, 0.122)  # centre x, centre y, rayon (en part de la largeur)


def figure(fid, x, y, w, h=None, ring=True, tag=None, tag_dy=-70, pos_y=0.5):
    """Carte avec la figure 3D de la Vespa ; anneau ambre sur la roue avant.

    pos_y : cadrage vertical quand la carte rogne l'image (0 = haut, 1 = bas)."""
    h = h or round(w * FIG_H / FIG_W)
    # object-fit: cover → échelle et décalage de l'image dans la carte
    s = max(w / FIG_W, h / FIG_H)
    ox, oy = (w - FIG_W * s) / 2, (h - FIG_H * s) * pos_y
    cx, cy, r = ox + AV[0] * FIG_W * s, oy + AV[1] * FIG_H * s, AV[2] * FIG_W * s
    out = f'      <div id="{fid}" class="PX-fig" data-layout-allow-overflow style="left: {x}px; top: {y}px; width: {w}px; height: {h}px">\n'
    out += f'        <img src="assets/images/vespa-3d.jpg" alt="La Vespa de l’utilisateur" style="object-position: 50% {pos_y * 100:.0f}%" />\n'
    if ring:
        out += f'        <div id="{fid}-ring" class="PX-ring" style="left: {cx - r:.0f}px; top: {cy - r:.0f}px; width: {2 * r:.0f}px; height: {2 * r:.0f}px"></div>\n'
    if tag:
        out += f'        <div id="{fid}-tag" class="PX-tag" style="right: 24px; top: {max(16, cy - r + tag_dy):.0f}px">{tag}</div>\n'
    return out + "      </div>"


# ---------------------------------------------------------------------------
# Dessins réutilisés


def roue(cx, cy, r, rim_ratio, rid, rayons=6, couleur="#93CDBB"):
    """Roue vue de côté (pneu, jante menthe, rayons)."""
    rr = r * rim_ratio
    spokes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx + rr * 0.92 * __import__("math").cos(k * 2 * 3.14159 / rayons):.1f}" y2="{cy + rr * 0.92 * __import__("math").sin(k * 2 * 3.14159 / rayons):.1f}" stroke="{couleur}" stroke-width="5" stroke-linecap="round" />'
        for k in range(rayons))
    return (f'<g id="{rid}"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#1F2B31" />'
            f'<circle cx="{cx}" cy="{cy}" r="{r - 6}" fill="none" stroke="#3E525C" stroke-width="6" stroke-dasharray="14 16" />'
            f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="#16252B" stroke="{couleur}" stroke-width="5" />'
            f'{spokes}<circle cx="{cx}" cy="{cy}" r="{rr * 0.18:.1f}" fill="{couleur}" /></g>')


def vespa_cote(prefix, transparent=False):
    """Vespa vue de côté (vers la droite), viewBox 0 0 900 560. Les pièces de
    transmission sont sous le capot arrière, visibles si transparent."""
    capot_op = "0.28" if transparent else "1"
    return f"""<g id="{prefix}-roueAR">{roue(235, 452, 92, 0.6, prefix + "-rAR")}</g>
          <g id="{prefix}-roueAV">{roue(700, 452, 92, 0.6, prefix + "-rAV")}</g>
          <path d="M 640 150 C 660 140 690 150 700 175 L 676 430 L 600 430 Z" fill="#93CDBB" />
          <path d="M 612 372 C 650 330 760 330 790 380 L 790 392 C 760 360 650 358 620 392 Z" fill="#7FB8A6" />
          <rect x="370" y="402" width="250" height="30" rx="10" fill="#93CDBB" />
          <path id="{prefix}-capot" d="M 112 372 C 112 300 160 250 230 246 L 440 246 C 476 250 482 300 470 340 L 456 404 L 150 404 C 124 404 112 392 112 372 Z" fill="#93CDBB" opacity="{capot_op}" />
          <rect x="170" y="214" width="280" height="38" rx="16" fill="#1F2A2F" />
          <rect x="96" y="120" width="150" height="110" rx="8" fill="#1E2A30" stroke="#3E525C" stroke-width="3" />
          <rect x="96" y="214" width="150" height="14" rx="4" fill="#93CDBB" opacity="0.6" />
          <line x1="678" y1="160" x2="700" y2="96" stroke="#3E525C" stroke-width="10" stroke-linecap="round" />
          <line x1="652" y1="92" x2="742" y2="104" stroke="#1F2A2F" stroke-width="12" stroke-linecap="round" />
          <ellipse cx="716" cy="122" rx="30" ry="22" fill="#93CDBB" />
          <circle cx="740" cy="122" r="12" fill="#FFF4CC" />
          <rect x="102" y="300" width="16" height="22" rx="4" fill="#F25C54" />"""


def jauge(gid, cx, cy, r, vmax=120):
    """Compteur à aiguille : arc 0 → vmax, graduations tous les 20."""
    import math
    parts = [f'<g id="{gid}">',
             f'<path d="M {cx - r * math.cos(math.radians(30)):.1f} {cy + r * math.sin(math.radians(30)):.1f} A {r} {r} 0 1 1 {cx + r * math.cos(math.radians(30)):.1f} {cy + r * math.sin(math.radians(30)):.1f}" fill="none" stroke="#26343B" stroke-width="14" stroke-linecap="round" />']
    for v in range(0, vmax + 1, 20):
        a = math.radians(210 - 240 * v / vmax)
        x1, y1 = cx + (r - 26) * math.cos(a), cy - (r - 26) * math.sin(a)
        x2, y2 = cx + (r - 4) * math.cos(a), cy - (r - 4) * math.sin(a)
        xt, yt = cx + (r - 62) * math.cos(a), cy - (r - 62) * math.sin(a) + 10
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#93A4A7" stroke-width="4" />')
        parts.append(f'<text x="{xt:.1f}" y="{yt:.1f}" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="600" font-size="28" fill="#93A4A7">{v}</text>')
    parts.append(f'<g id="{gid}-needle" style="transform-origin: {cx}px {cy}px"><line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - r + 34}" stroke="#F4A62A" stroke-width="8" stroke-linecap="round" /></g>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="16" fill="#F4A62A" /></g>')
    return "".join(parts)


def angle_aiguille(v, vmax=120):
    """Rotation CSS (degrés, sens horaire depuis la verticale) pour la valeur v."""
    return -120 + 240 * v / vmax


# ---------------------------------------------------------------------------
# 01 — La question
scene("01-question", """
    #PX-q { position: absolute; left: 108px; top: 230px; width: 864px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; font-size: 68px; line-height: 1.1; letter-spacing: -0.02em; }
    #PX-q2 { position: absolute; left: 108px; top: 1150px; width: 864px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 52px; line-height: 1.15; letter-spacing: -0.01em; }
    #PX-chips { position: absolute; left: 108px; top: 1390px; display: flex; gap: 18px; }
    .PX-chip { padding: 12px 26px; border-radius: 100px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; font-size: 40px; }
    .PX-old { background: #141D21; border: 1.5px solid #26343B; color: #93A4A7; }
    .PX-new { background: #F4A62A; color: #0D1316; }
    .PX-arrow { font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 44px; color: #F4A62A; align-self: center; }""",
      eyebrow("Ma Vespa") + """
      <div id="PX-q">J’ai passé mes roues de <span class="PX-hl">12</span> à <span class="PX-hl">13 pouces</span>…</div>
""" + figure("PX-figure", 108, 470, 864) + """
      <div id="PX-q2">Mon compteur affiche-t-il toujours <span class="PX-hl">la vraie vitesse</span> ?</div>
      <div id="PX-chips"><span class="PX-chip PX-old">12″</span><span class="PX-arrow">→</span><span class="PX-chip PX-new">13″</span></div>""",
      """      // tout est déjà à l'écran à 0 s : la première image sert de vignette
      tl.fromTo("#PX-q", { scale: 1.04 }, { scale: 1, duration: 0.8, ease: E, transformOrigin: "0% 50%" }, 0);
      tl.fromTo("#PX-figure img", { scale: 1.0 }, { scale: 1.07, duration: D, ease: "none" }, 0);
      tl.fromTo("#PX-figure-ring", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)" }, 1.0);
      rise("#PX-q2", 1.5);
      gsap.utils.toArray("#PX-chips > *").forEach((el, i) => rise(el, 2.2 + i * 0.15, 16, 0.4));""")

# 02 — Titre et réponse courte
scene("02-titre", """
    #PX-title { position: absolute; left: 108px; top: 300px; width: 864px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; font-size: 84px; line-height: 1.05; letter-spacing: -0.03em; }
    #PX-wheel { position: absolute; left: 290px; top: 700px; width: 500px; height: 500px; }
    #PX-count { position: absolute; left: 108px; top: 1240px; width: 864px; text-align: center; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; font-size: 64px; color: #F4A62A; }
    #PX-count small { font-family: "Inter", sans-serif; font-weight: 500; font-size: 32px; color: #93A4A7; margin-left: 12px; }""",
      eyebrow("Pourquoi ton compteur peut te mentir") + """
      <div id="PX-title">Ton compteur ne mesure pas <span class="PX-hl">ta vitesse</span>.</div>
      <svg id="PX-wheel" viewBox="0 0 500 500" width="500" height="500">""" + roue(250, 250, 230, 0.62, "PX-w", rayons=8) + """
        <circle cx="250" cy="20" r="14" fill="#F4A62A" />
      </svg>
      <div id="PX-count"><span id="PX-n" data-layout-ignore>0</span> tour<span id="PX-s"></span><small>… pas des kilomètres</small></div>""",
      """      tl.fromTo("#PX-eyebrow", { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.5, ease: E }, 0.05);
      rise("#PX-title", 0.2);
      tl.fromTo("#PX-wheel", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.6, ease: E }, 0.7);
      tl.fromTo("#PX-wheel", { rotation: 0 }, { rotation: 4 * 360, duration: D - 1.4, ease: "none", transformOrigin: "50% 50%" }, 1.4);
      rise("#PX-count", 1.5, 20, 0.4);
      // un tour toutes les 0,6 s à partir de 2,0 s (les « tic » du compteur), piloté par un tween : sûr au saut
      const n = document.getElementById("PX-n"), s = document.getElementById("PX-s"), o = { v: 0 };
      const montre = () => { const k = Math.min(4, Math.floor(o.v + 1e-6)); n.textContent = String(k); s.textContent = k > 1 ? "s" : ""; };
      tl.fromTo(o, { v: 0 }, { v: 5, duration: 3.0, ease: "none", onUpdate: montre }, 1.4);
      montre();""")

# 03 — Transmission de la Vespa
ETAPES = [("Moteur", "piston → vilebrequin"), ("Variateur + courroie", "rapport automatique"),
          ("Embrayage centrifuge", "s’engage en accélérant"), ("Réducteur", "entraîne la roue arrière"),
          ("Roue", "rotation → déplacement")]
etapes_html = "\n".join(
    f'        <div class="PX-step" id="PX-s{k}"><span class="PX-num">{k + 1}</span><span class="PX-t">{a}</span><span class="PX-d">{b}</span></div>'
    for k, (a, b) in enumerate(ETAPES))
scene("03-transmission", """
    #PX-svg { position: absolute; left: 60px; top: 380px; width: 960px; height: 597px; }
    #PX-steps { position: absolute; left: 108px; top: 1010px; width: 864px; display: flex; flex-direction: column; gap: 10px; }
    .PX-step { height: 58px; display: flex; align-items: center; gap: 16px; padding: 0 20px; border-radius: 12px; background: #141D21; border: 1.5px solid #26343B; opacity: 0; }
    .PX-num { width: 36px; height: 36px; border-radius: 50%; background: #26343B; color: #E8EEEC; display: flex; align-items: center; justify-content: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 28px; flex: none; }
    .PX-t { font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 30px; white-space: nowrap; }
    .PX-d { font-family: "Inter", sans-serif; font-weight: 500; font-size: 28px; color: #93A4A7; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }""",
      eyebrow("Du moteur à la roue") + """
      <div id="PX-h2">Ce qui fait <span class="PX-hl">avancer</span> ta Vespa</div>
      <svg id="PX-svg" viewBox="0 0 900 560" width="960" height="597">
          """ + vespa_cote("PX-v", transparent=True) + """
          <!-- moteur : cylindre + piston + vilebrequin -->
          <g id="PX-p0"><rect x="372" y="300" width="70" height="92" rx="8" fill="#16252B" stroke="#93CDBB" stroke-width="4" transform="rotate(-28 407 346)" />
            <rect id="PX-piston" x="388" y="318" width="38" height="26" rx="4" fill="#93CDBB" transform="rotate(-28 407 346)" />
            <circle cx="392" cy="402" r="20" fill="#16252B" stroke="#93CDBB" stroke-width="4" /></g>
          <!-- variateur, courroie, poulie arrière -->
          <g id="PX-p1"><circle cx="372" cy="430" r="26" fill="none" stroke="#93CDBB" stroke-width="5" />
            <path d="M 372 404 L 270 410 M 372 456 L 270 470" stroke="#93CDBB" stroke-width="6" />
            <circle cx="270" cy="440" r="32" fill="none" stroke="#93CDBB" stroke-width="5" /></g>
          <!-- embrayage centrifuge (cloche) -->
          <g id="PX-p2"><circle cx="270" cy="440" r="44" fill="none" stroke="#93CDBB" stroke-width="4" stroke-dasharray="10 8" /></g>
          <!-- réducteur : pignons -->
          <g id="PX-p3"><circle cx="247" cy="452" r="18" fill="#16252B" stroke="#93CDBB" stroke-width="4" /><circle cx="262" cy="432" r="10" fill="#93CDBB" /></g>
          <!-- flèche de la transmission -->
          <path id="PX-flow" d="M 392 402 L 372 430 L 270 440 L 247 452" fill="none" stroke="#F4A62A" stroke-width="7" stroke-linecap="round" stroke-dasharray="14 12" style="opacity: 0" />
          <path id="PX-move" d="M 120 530 L 330 530" fill="none" stroke="#F4A62A" stroke-width="7" stroke-linecap="round" />
          <path id="PX-moveHead" d="M 312 516 L 336 530 L 312 544" fill="none" stroke="#F4A62A" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <div id="PX-steps">
""" + etapes_html + """
      </div>""",
      INTRO_JS + """
      tl.fromTo("#PX-svg", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, ease: E }, 0.3);

      const parts = ["#PX-p0", "#PX-p1", "#PX-p2", "#PX-p3", "#PX-v-roueAR"];
      parts.forEach((p) => tl.set(p, { opacity: 0.35 }, 0));
      const T = [0.6, 3.0, 5.4, 7.8, 10.2];
      T.forEach((t, i) => {
        tl.fromTo("#PX-s" + i, { opacity: 0, x: -20 }, { opacity: 1, x: 0, borderColor: "#F4A62A", duration: 0.35, ease: E }, t);
        tl.to("#PX-s" + i + " .PX-num", { backgroundColor: "#F4A62A", color: "#0D1316", duration: 0.3 }, t);
        tl.to(parts[i], { opacity: 1, duration: 0.3 }, t);
        if (i > 0) { tl.to("#PX-s" + (i - 1), { opacity: 0.7, borderColor: "#26343B", duration: 0.3 }, t); tl.to("#PX-s" + (i - 1) + " .PX-num", { backgroundColor: "#3E525C", color: "#E8EEEC", duration: 0.3 }, t); }
      });
      tl.fromTo("#PX-piston", { y: 0 }, { y: 10, duration: 0.12, ease: "sine.inOut", repeat: 24, yoyo: true }, 0.6);
      tl.to("#PX-flow", { opacity: 1, duration: 0.3 }, 3.0);
      tl.fromTo("#PX-flow", { strokeDashoffset: 0 }, { strokeDashoffset: -260, duration: D - 3.0, ease: "none" }, 3.0);
      tl.fromTo("#PX-v-rAR", { rotation: 0 }, { rotation: 720, duration: D - 7.8, ease: "power1.in", svgOrigin: "235 452" }, 7.8);
      tl.fromTo("#PX-v-rAV", { rotation: 0 }, { rotation: 540, duration: D - 10.2, ease: "power1.in", svgOrigin: "700 452" }, 10.2);
      tl.fromTo(["#PX-move", "#PX-moveHead"], { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.5, ease: E }, 10.4);""")

# 04 — Le capteur de la roue avant
import math
dents = "".join(
    f'<rect x="{500 + 140 * math.cos(k * math.pi / 15) - 7:.1f}" y="{270 + 140 * math.sin(k * math.pi / 15) - 7:.1f}" width="14" height="14" rx="2" fill="#93CDBB" transform="rotate({k * 12} {500 + 140 * math.cos(k * math.pi / 15):.1f} {270 + 140 * math.sin(k * math.pi / 15):.1f})" />'
    for k in range(30))
scene("04-capteur", """
    #PX-svg { position: absolute; left: 40px; top: 330px; width: 1000px; height: 1040px; }""",
      eyebrow("Le capteur") + """
      <div id="PX-h2">Il compte les tours de la <span class="PX-hl">roue avant</span></div>
      <svg id="PX-svg" viewBox="0 0 1000 1040" width="1000" height="1040">
        <g id="PX-wheelIn"><g id="PX-wheel">""" + roue(500, 270, 230, 0.68, "PX-w", rayons=5).replace('<g id="PX-w">', '<g>') + f"""<g id="PX-teeth">{dents}</g></g></g>
        <rect id="PX-sensor" x="680" y="96" width="70" height="44" rx="10" fill="#F4A62A" />
        <text x="715" y="76" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="600" font-size="28" fill="#F4A62A">capteur</text>
        <path id="PX-cable" d="M 750 118 C 900 140 900 560 680 590" fill="none" stroke="#3E525C" stroke-width="6" />
        <circle id="PX-pulse" cx="750" cy="118" r="12" fill="#F4A62A" />
        <rect x="320" y="550" width="360" height="96" rx="14" fill="#141D21" stroke="#26343B" stroke-width="3" />
        <text x="500" y="612" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="600" font-size="38" fill="#E8EEEC">Calculateur</text>
        <path id="PX-arrow2" d="M 500 654 L 500 716" stroke="#F4A62A" stroke-width="6" stroke-linecap="round" />
        <path id="PX-arrow2h" d="M 484 700 L 500 720 L 516 700" fill="none" stroke="#F4A62A" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />
        <g id="PX-gauge">{jauge("PX-g", 500, 920, 160)}</g>
      </svg>""",
      INTRO_JS + """
      tl.fromTo("#PX-wheelIn", { opacity: 0, scale: 0.92 }, { opacity: 1, scale: 1, duration: 0.6, ease: E, svgOrigin: "500 270" }, 0.3);
      tl.fromTo("#PX-wheel", { rotation: 0 }, { rotation: 300, duration: D - 0.3, ease: "none", svgOrigin: "500 270" }, 0.3);
      tl.fromTo("#PX-sensor", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.8)", svgOrigin: "715 118" }, 0.7);
      tl.set("#PX-pulse", { opacity: 0 }, 0);
      [1.1, 1.5, 1.9, 2.3].forEach((t) => {
        tl.fromTo("#PX-pulse", { opacity: 1, attr: { cx: 750, cy: 118 } }, { attr: { cx: 680, cy: 590 }, duration: 0.34, ease: "none", immediateRender: false }, t);
        tl.to("#PX-pulse", { opacity: 0, duration: 0.04 }, t + 0.34);
      });
      tl.fromTo("#PX-gauge", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: E }, 2.8);
      tl.fromTo(["#PX-arrow2", "#PX-arrow2h"], { opacity: 0 }, { opacity: 1, duration: 0.3 }, 3.1);
      tl.fromTo("#PX-g-needle", { rotation: -120 }, { rotation: """ + f"{angle_aiguille(60):.1f}" + """, duration: 1.2, ease: "power2.out" }, 3.3);""")

# 05 — Le calcul (analyse avec la figure)
scene("05-calcul", """
    #PX-code { position: absolute; left: 640px; top: 400px; width: 332px; }
    #PX-code .PX-big { font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; font-size: 62px; color: #F4A62A; letter-spacing: -0.01em; }
    #PX-code .PX-chip { margin-top: 12px; padding: 8px 16px; border-radius: 100px; background: rgba(244, 166, 42, 0.08); font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 500; font-size: 28px; color: #F4A62A; white-space: nowrap; width: fit-content; }
    #PX-code .PX-chip b { font-weight: 700; }
    #PX-formula { left: 108px; top: 820px; width: 864px; padding: 26px 30px; }
    .PX-l { font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 31px; line-height: 1.5; white-space: nowrap; }
    .PX-l.PX-muted { color: #93A4A7; font-weight: 500; }
    .PX-l .PX-res { color: #F4A62A; font-weight: 700; }
    .PX-l .PX-new { color: #F25C54; font-weight: 700; }
    #PX-result { position: absolute; left: 108px; top: 1150px; width: 864px; padding: 22px 30px; border-radius: 12px; background: rgba(244, 166, 42, 0.08); border-left: 6px solid #F4A62A; }
    #PX-result .PX-k { font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 28px; letter-spacing: 0.08em; text-transform: uppercase; color: #F4A62A; }
    #PX-result .PX-t { margin-top: 6px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 34px; line-height: 1.25; }
    #PX-result .PX-big { color: #F25C54; font-weight: 700; font-size: 44px; }""",
      eyebrow("Comment le compteur calcule") + """
      <div id="PX-h2">Vitesse affichée = tours × <span class="PX-hl">circonférence d’origine</span></div>
""" + figure("PX-figure", 108, 400, 500, ring=True, tag="roue lue par le compteur", tag_dy=-60) + """
      <div id="PX-code">
        <div class="PX-big">120/70-12</div>
        <div class="PX-chip"><b>120</b> largeur (mm)</div>
        <div class="PX-chip"><b>70</b> série (% largeur)</div>
        <div class="PX-chip"><b>12</b> jante (pouces)</div>
        <div class="PX-chip" id="PX-chip13"><b>13</b> pouces après</div>
      </div>
      <div id="PX-formula" class="PX-card">
        <div class="PX-l" id="PX-l1">Diamètre = jante × 25,4 + 2 × flanc</div>
        <div class="PX-l PX-muted" id="PX-l2">flanc = 120 × 70 / 100 = 84 mm</div>
        <div class="PX-l" id="PX-l3">12″ : 304,8 mm + 168 = <span class="PX-res">472,8 mm</span> → 1,485 m</div>
        <div class="PX-l" id="PX-l4">13″ : 330,2 mm + 168 = <span class="PX-new">498,2 mm</span> → 1,565 m</div>
      </div>
      <div id="PX-result">
        <div class="PX-k">Vitesse réelle = affichée × (nouveau / origine)</div>
        <div class="PX-t">498,2 / 472,8 = <span class="PX-big">1,054</span> → <span class="PX-big">+5,4 %</span></div>
      </div>""",
      INTRO_JS + """
      tl.fromTo("#PX-figure", { opacity: 0, scale: 0.95 }, { opacity: 1, scale: 1, duration: 0.7, ease: E }, 0.3);
      tl.fromTo("#PX-figure-ring", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)" }, 0.8);
      tl.fromTo("#PX-figure-tag", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, 1.1);
      rise("#PX-code .PX-big", 2.7, 20, 0.45);
      gsap.utils.toArray("#PX-code .PX-chip").slice(0, 3).forEach((el, i) => rise(el, 3.0 + i * 0.15, 14, 0.4));
      rise("#PX-formula", 2.8, 24, 0.5);
      rise("#PX-l1", 2.9, 12, 0.4);
      rise("#PX-l2", 3.9, 12, 0.4);
      rise("#PX-l3", 4.9, 12, 0.4);
      rise("#PX-chip13", 6.3, 14, 0.4);
      rise("#PX-l4", 6.5, 12, 0.4);
      rise("#PX-result", 8.8, 30, 0.6);""")

# 06 — Comparaison 12″ / 13″ (un tour sur une règle)
S = 400  # px par mètre
R12, R13 = 0.4728 / 2 * S * 0.98, 0.4982 / 2 * S * 0.98
C12, C13 = math.pi * 2 * R12, math.pi * 2 * R13
X0 = 150


def regle(y):
    ticks = "".join(
        f'<line x1="{X0 + k * S / 4:.1f}" y1="{y}" x2="{X0 + k * S / 4:.1f}" y2="{y + (26 if k % 4 == 0 else 14)}" stroke="#3E525C" stroke-width="3" />'
        + (f'<text x="{X0 + k * S / 4:.1f}" y="{y + 56}" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="500" font-size="28" fill="#6E8186">{k // 4} m</text>' if k % 4 == 0 else "")
        for k in range(9))
    return f'<line x1="{X0 - 30}" y1="{y}" x2="{X0 + 2 * S + 30}" y2="{y}" stroke="#3E525C" stroke-width="3" />' + ticks


scene("06-comparaison", f"""
    #PX-svg {{ position: absolute; left: 0; top: 330px; width: 1080px; height: 880px; }}
    #PX-result {{ position: absolute; left: 108px; top: 1180px; width: 864px; padding: 22px 30px; border-radius: 12px; background: rgba(244, 166, 42, 0.08); border-left: 6px solid #F4A62A;
      font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 38px; line-height: 1.25; }}
    #PX-result .PX-big {{ color: #F25C54; font-weight: 700; }}""",
      eyebrow("Petite roue, grande roue") + f"""
      <div id="PX-h2">Un tour de roue… <span class="PX-hl">pas la même distance</span></div>
      <svg id="PX-svg" viewBox="0 0 1080 880" width="1080" height="880">
        <text x="108" y="70" font-family="Space Grotesk, Inter, sans-serif" font-weight="600" font-size="34" fill="#E8EEEC">12 pouces · 120/70-12</text>
        {regle(140 + 2 * R12)}
        <g id="PX-w12">{roue(X0, round(140 + R12, 1), round(R12, 1), 0.64, "PX-r12")}</g>
        <line id="PX-end12" x1="{X0 + C12:.1f}" y1="{120 + 2 * R12:.1f}" x2="{X0 + C12:.1f}" y2="{170 + 2 * R12:.1f}" stroke="#F4A62A" stroke-width="5" />
        <text id="PX-lab12" x="{X0 + C12:.1f}" y="{128:.1f}" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="700" font-size="40" fill="#F4A62A">1,485 m</text>
        <text x="108" y="{470:.1f}" font-family="Space Grotesk, Inter, sans-serif" font-weight="600" font-size="34" fill="#E8EEEC">13 pouces · 120/70-13</text>
        {regle(540 + 2 * R13)}
        <g id="PX-w13">{roue(X0, round(540 + R13, 1), round(R13, 1), 0.66, "PX-r13")}</g>
        <line id="PX-end13" x1="{X0 + C13:.1f}" y1="{520 + 2 * R13:.1f}" x2="{X0 + C13:.1f}" y2="{570 + 2 * R13:.1f}" stroke="#F25C54" stroke-width="5" />
        <text id="PX-lab13" x="{X0 + C13:.1f}" y="{528:.1f}" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="700" font-size="40" fill="#F25C54">1,565 m</text>
        <g id="PX-diff"><line x1="{X0 + C12:.1f}" y1="{838:.1f}" x2="{X0 + C13:.1f}" y2="{838:.1f}" stroke="#F25C54" stroke-width="5" />
          <text x="{X0 + (C12 + C13) / 2:.1f}" y="{824:.1f}" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="700" font-size="34" fill="#F25C54">+8 cm</text></g>
        <g id="PX-c12"><rect x="470" y="36" width="250" height="50" rx="25" fill="#141D21" stroke="#26343B" stroke-width="2" /><text x="595" y="71" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="600" font-size="28" fill="#93A4A7">compteur : 1 tour</text></g>
        <g id="PX-c13"><rect x="470" y="436" width="250" height="50" rx="25" fill="#141D21" stroke="#26343B" stroke-width="2" /><text x="595" y="471" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif" font-weight="600" font-size="28" fill="#93A4A7">compteur : 1 tour</text></g>
      </svg>
      <div id="PX-result">+8 cm à chaque tour : tu roules <span class="PX-big">plus vite</span> qu’affiché.</div>""",
      INTRO_JS + f"""
      tl.fromTo("#PX-svg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: E }}, 0.2);
      tl.set(["#PX-end12", "#PX-lab12", "#PX-end13", "#PX-lab13", "#PX-diff", "#PX-c12", "#PX-c13"], {{ opacity: 0 }}, 0);
      tl.fromTo("#PX-w12", {{ x: 0 }}, {{ x: {C12:.1f}, duration: 2.4, ease: "power1.inOut" }}, 0.4);
      tl.fromTo("#PX-r12", {{ rotation: 0 }}, {{ rotation: 360, duration: 2.4, ease: "power1.inOut", svgOrigin: "{X0} {140 + R12:.1f}" }}, 0.4);
      tl.fromTo("#PX-w13", {{ x: 0 }}, {{ x: {C13:.1f}, duration: 2.4, ease: "power1.inOut" }}, 0.4);
      tl.fromTo("#PX-r13", {{ rotation: 0 }}, {{ rotation: 360, duration: 2.4, ease: "power1.inOut", svgOrigin: "{X0} {540 + R13:.1f}" }}, 0.4);
      tl.to(["#PX-end12", "#PX-lab12", "#PX-end13", "#PX-lab13"], {{ opacity: 1, duration: 0.4 }}, 2.8);
      pop("#PX-diff", 3.0);
      tl.to(["#PX-c12", "#PX-c13"], {{ opacity: 1, duration: 0.4 }}, 3.8);
      tl.fromTo(["#PX-c12 rect", "#PX-c13 rect"], {{ attr: {{ stroke: "#26343B" }} }}, {{ attr: {{ stroke: "#F4A62A" }}, duration: 0.3, yoyo: true, repeat: 3 }}, 4.2);
      rise("#PX-result", 5.5, 30, 0.6);""")

# 07 — Sur la route (figure + compteur à 60 puis 100, et le radar à chaque fois)
scene("07-serein", f"""
    #PX-h2b {{ position: absolute; left: 108px; top: 214px; width: 864px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 54px; line-height: 1.12; letter-spacing: -0.02em; }}
    #PX-gaugebox {{ left: 108px; top: 1090px; width: 420px; height: 270px; }}
    #PX-gsvg {{ position: absolute; left: 0; top: 0; width: 420px; height: 270px; }}
    #PX-radar {{ left: 552px; top: 1090px; width: 420px; height: 270px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-color: #F25C54; overflow: visible; }}
    #PX-radar .PX-k {{ font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 28px; letter-spacing: 0.08em; text-transform: uppercase; color: #F25C54; }}
    #PX-vals {{ position: relative; width: 100%; height: 104px; margin-top: 8px; }}
    #PX-radar .PX-v {{ position: absolute; left: 0; right: 0; top: 0; text-align: center; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; font-size: 96px; color: #F25C54; line-height: 1.05; }}
    #PX-radar .PX-v small {{ font-size: 36px; margin-left: 6px; }}
    #PX-pulse2 {{ position: absolute; inset: -1.5px; border-radius: 14px; pointer-events: none; }}""",
      eyebrow("Sur la route") + """
      <div id="PX-h2">Compteur : <span class="PX-hl">60 km/h</span>. Tu es serein.</div>
      <div id="PX-h2b">Et à <span class="PX-hl">100 km/h</span> au compteur ?</div>
""" + figure("PX-figure", 108, 390, 864, ring=False) + f"""
      <div id="PX-gaugebox" class="PX-card"><svg id="PX-gsvg" viewBox="0 0 420 270" width="420" height="270">{jauge("PX-g", 210, 180, 140)}</svg></div>
      <div id="PX-radar" class="PX-card"><div class="PX-k">Radar</div>
        <div id="PX-vals"><div class="PX-v" id="PX-v63">63<small>km/h</small></div><div class="PX-v" id="PX-v105">105<small>km/h</small></div></div>
        <div id="PX-pulse2"></div></div>""",
      INTRO_JS + f"""
      tl.fromTo("#PX-figure", {{ opacity: 0, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.7, ease: E }}, 0.3);
      tl.fromTo("#PX-figure img", {{ x: -20, scale: 1.04 }}, {{ x: 20, scale: 1.04, duration: D, ease: "none" }}, 0);
      rise("#PX-gaugebox", 1.0, 24, 0.5);
      // aiguille : 0 → 60 (1,2 → 2,8 s), puis 60 → 100 (5,8 → 7,0 s) ; un seul tween proxy, rotation CSS autour du centre
      const aig = document.getElementById("PX-g-needle"), A60 = {angle_aiguille(60):.1f}, A100 = {angle_aiguille(100):.1f};
      const sortie = (x) => 1 - (1 - x) * (1 - x), dedans = (x) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);
      const angle = (t) => t < 1.2 ? -120 : t < 2.8 ? -120 + (A60 + 120) * sortie((t - 1.2) / 1.6)
        : t < 5.8 ? A60 : t < 7.0 ? A60 + (A100 - A60) * dedans((t - 5.8) / 1.2) : A100;
      const pa = {{ t: 0 }}, trace = () => {{ aig.style.transform = "rotate(" + angle(pa.t).toFixed(2) + "deg)"; }};
      tl.fromTo(pa, {{ t: 0 }}, {{ t: D, duration: D, ease: "none", onUpdate: trace }}, 0);
      trace();
      // 60 au compteur → le radar voit 63
      tl.set("#PX-radar", {{ opacity: 0 }}, 0);
      tl.set("#PX-v105", {{ opacity: 0 }}, 0);
      pop("#PX-radar", 3.2, 0.35);
      tl.fromTo("#PX-radar", {{ boxShadow: "0 0 0 0 rgba(242,92,84,0.6)" }}, {{ boxShadow: "0 0 0 24px rgba(242,92,84,0)", duration: 0.8, ease: "power2.out" }}, 3.3);
      tl.fromTo("#PX-v63", {{ opacity: 1 }}, {{ opacity: 0.4, duration: 0.22, yoyo: true, repeat: 3 }}, 3.8);
      // 100 au compteur → le radar voit 105
      tl.to("#PX-h2", {{ opacity: 0, y: -16, duration: 0.35, ease: "power2.in" }}, 5.3);
      rise("#PX-h2b", 5.6);
      tl.to("#PX-v63", {{ opacity: 0, y: -20, duration: 0.25, ease: "power2.in" }}, 6.8);
      tl.fromTo("#PX-v105", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.8)" }}, 7.0);
      tl.fromTo("#PX-pulse2", {{ boxShadow: "0 0 0 0 rgba(242,92,84,0.6)" }}, {{ boxShadow: "0 0 0 28px rgba(242,92,84,0)", duration: 0.8, ease: "power2.out" }}, 7.05);""")

# 09 — Tableau (analyse avec la figure)
import importlib.util
spec = importlib.util.spec_from_file_location("calculs", ROOT / "tools/calculs.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
lignes = []
for k, (pneu, dia, ecart, v60, v100) in enumerate(C.tableau()):
    v = float(v60.replace(",", "."))
    cls = "PX-up" if v > 60.05 else ("PX-down" if v < 59.95 else "PX-eq")
    chip = ' <span class="PX-chip">origine</span>' if pneu == "120/70-12" else (' <span class="PX-me">ta Vespa</span>' if pneu == "120/70-13" else "")
    rowcls = " PX-ref" if pneu == "120/70-13" else ""
    ecart_aff = "—" if ecart.startswith("0,0") else ecart
    lignes.append(f'        <div class="PX-row{rowcls}" id="PX-r{k}"><div class="PX-c1">{pneu}{chip}</div><div class="PX-c2">{dia}</div>'
                  f'<div class="PX-c3 {cls}">{ecart_aff}</div><div class="PX-c4 {cls}">{v60}</div><div class="PX-c5 {cls}">{v100}</div></div>')
scene("09-tableau", """
    #PX-h2 { width: 520px; }
    #PX-sub { position: absolute; left: 108px; top: 350px; width: 520px; font-family: "Inter", sans-serif; font-weight: 500; font-size: 28px; line-height: 1.3; color: #93A4A7; }
    #PX-table { position: absolute; left: 108px; top: 470px; width: 864px; }
    .PX-row { height: 82px; display: flex; align-items: center; border-bottom: 1.5px solid #26343B; font-family: "Space Grotesk", "Inter", sans-serif; font-size: 30px; font-weight: 500; }
    .PX-head { height: 56px; font-size: 28px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: #93A4A7; border-bottom: 2px solid #3E525C; }
    .PX-ref { background: rgba(244, 166, 42, 0.1); border-radius: 10px; }
    .PX-c1 { width: 300px; padding-left: 14px; display: flex; align-items: center; gap: 8px; font-weight: 600; white-space: nowrap; }
    .PX-c2 { width: 164px; text-align: right; white-space: nowrap; }
    .PX-c3 { width: 124px; text-align: right; white-space: nowrap; }
    .PX-c4 { width: 132px; text-align: right; font-weight: 700; }
    .PX-c5 { width: 144px; text-align: right; font-weight: 700; padding-right: 14px; }
    .PX-chip { padding: 3px 12px; border-radius: 100px; background: rgba(244, 166, 42, 0.1); color: #F4A62A; font-size: 28px; font-weight: 600; }
    .PX-me { padding: 3px 12px; border-radius: 100px; background: #F4A62A; color: #0D1316; font-size: 28px; font-weight: 600; }
    .PX-up { color: #F25C54; }
    .PX-down { color: #3CC98F; }
    .PX-eq { color: #E8EEEC; }
    #PX-foot { position: absolute; left: 108px; top: 1110px; width: 864px; font-family: "Inter", sans-serif; font-weight: 500; font-size: 28px; line-height: 1.35; color: #93A4A7; }""",
      eyebrow("Tableau récapitulatif") + """
      <div id="PX-h2">Compteur : <span class="PX-hl">60</span> et <span class="PX-hl">100 km/h</span></div>
      <div id="PX-sub">Vitesse réelle (km/h) selon le pneu avant, référence 120/70-12</div>
""" + figure("PX-figure", 652, 170, 320, ring=True) + """
      <div id="PX-table">
        <div class="PX-row PX-head"><div class="PX-c1">Pneu avant</div><div class="PX-c2">Diamètre</div><div class="PX-c3">Écart</div><div class="PX-c4">À 60</div><div class="PX-c5">À 100</div></div>
""" + "\n".join(lignes) + """
      </div>
      <div id="PX-foot">Calcul pour la roue avant, celle que lit le compteur. Vérifie les dimensions homologuées pour ta Vespa.</div>""",
      INTRO_JS + """
      rise("#PX-sub", 0.3, 16, 0.4);
      tl.fromTo("#PX-figure", { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: 0.6, ease: E }, 0.3);
      rise("#PX-table .PX-head", 0.7, 12, 0.4);
      // colonne « à 60 » ligne par ligne, puis la colonne « à 100 » d'un coup
      gsap.utils.toArray("#PX-table .PX-c5").forEach((el) => tl.set(el, { opacity: 0 }, 0));
      for (let i = 0; i < 7; i++) rise("#PX-r" + i, 1.0 + 0.6 * i, 16, 0.4);
      tl.fromTo("#PX-r5", { backgroundColor: "rgba(244,166,42,0.1)" }, { backgroundColor: "rgba(244,166,42,0.28)", duration: 0.4, yoyo: true, repeat: 3 }, 4.5);
      rise("#PX-foot", 5.4, 16, 0.5);
      tl.to(".PX-head .PX-c5", { opacity: 1, duration: 0.3 }, 6.8);
      for (let i = 0; i < 7; i++) if (i !== 5) tl.to("#PX-r" + i + " .PX-c5", { opacity: 1, duration: 0.3 }, 6.9 + 0.06 * i);
      tl.fromTo("#PX-r5 .PX-c5", { opacity: 0, scale: 1.5 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.8)", transformOrigin: "100% 50%" }, 7.4);""")

# 10 — Carburant (analyse avec la figure)
scene("10-carburant", """
    #PX-odo { position: absolute; left: 140px; top: 650px; display: flex; gap: 14px; }
    .PX-odo { padding: 10px 20px; border-radius: 12px; background: rgba(13, 19, 22, 0.86); border: 1.5px solid #26343B; font-family: "Space Grotesk", "Inter", sans-serif; }
    .PX-odo .PX-k { font-size: 28px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #93A4A7; }
    .PX-odo .PX-v { font-size: 46px; font-weight: 700; color: #E8EEEC; line-height: 1.05; }
    #PX-odoReel .PX-v { color: #F25C54; }
    .PX-box { position: absolute; left: 108px; width: 864px; padding: 20px 28px; }
    .PX-box .PX-k { font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 28px; letter-spacing: 0.08em; text-transform: uppercase; color: #F4A62A; }
    .PX-box .PX-t { margin-top: 6px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 34px; line-height: 1.28; }
    .PX-box .PX-n { margin-top: 4px; font-family: "Inter", sans-serif; font-weight: 500; font-size: 28px; color: #93A4A7; }
    .PX-strike { color: #93A4A7; text-decoration: line-through; text-decoration-thickness: 3px; }
    .PX-red { color: #F25C54; font-weight: 700; }
    .PX-green { color: #3CC98F; font-weight: 700; }""",
      eyebrow("Et ton carburant ?") + """
      <div id="PX-h2"><span class="PX-hl">145 MAD</span> pour 229 km… au compteur</div>
""" + figure("PX-figure", 108, 360, 864, h=380, ring=False) + """
      <div id="PX-odo">
        <div class="PX-odo" id="PX-odoCpt"><div class="PX-k">Compteur</div><div class="PX-v"><span id="PX-km">0</span> km</div></div>
        <div class="PX-odo" id="PX-odoReel"><div class="PX-k">Réel</div><div class="PX-v">241,3 km</div></div>
      </div>
      <div class="PX-box PX-card" id="PX-b1" style="top: 770px">
        <div class="PX-k">Distance réelle</div>
        <div class="PX-t">229 × 1,054 = <span class="PX-red">241,3 km</span></div>
        <div class="PX-n">12,3 km roulés que ton compteur n’a pas comptés</div>
      </div>
      <div class="PX-box PX-card" id="PX-b2" style="top: 960px">
        <div class="PX-k">Coût aux 100 km</div>
        <div class="PX-t"><span class="PX-strike">63,3 MAD</span> → <span class="PX-green">60,1 MAD</span> réels</div>
        <div class="PX-n">145 / 241,3 km = 0,60 MAD/km, et non 0,63 MAD/km</div>
      </div>
      <div class="PX-box PX-card" id="PX-b3" style="top: 1150px">
        <div class="PX-k">Entretien</div>
        <div class="PX-t">1 000 km affichés = <span class="PX-red">1 054 km</span> roulés</div>
        <div class="PX-n">Vidanges et révisions arrivent en retard</div>
      </div>""",
      INTRO_JS + """
      tl.fromTo("#PX-figure", { opacity: 0, scale: 0.95 }, { opacity: 1, scale: 1, duration: 0.7, ease: E }, 0.3);
      tl.fromTo("#PX-figure img", { scale: 1.12, x: -30 }, { scale: 1.12, x: 30, duration: D, ease: "none" }, 0);
      rise("#PX-odoCpt", 0.6, 14, 0.4);
      const km = document.getElementById("PX-km"), o = { v: 0 };
      tl.fromTo(o, { v: 0 }, { v: 229, duration: 2.0, ease: "power2.out", onUpdate: () => { km.textContent = String(Math.round(o.v)); } }, 0.8);
      tl.set("#PX-odoReel", { opacity: 0 }, 0);
      pop("#PX-odoReel", 3.3);
      rise("#PX-b1", 3.1, 24, 0.5);
      rise("#PX-b2", 6.2, 24, 0.5);
      rise("#PX-b3", 9.2, 24, 0.5);""")

# 11 — Conclusion
CONSEILS = ["Respecte les tailles homologuées pour ta Vespa.", "Vérifie ta vitesse au GPS après un changement de jantes.",
            "Fais recalibrer ton compteur… ou corrige tes calculs de 5,4 %."]
cons_html = "\n".join(
    f'      <div class="PX-tip PX-card" id="PX-t{k}" style="top: {380 + k * 190}px"><span class="PX-num">{k + 1}</span><span>{c}</span></div>'
    for k, c in enumerate(CONSEILS))
scene("11-conclusion", """
    .PX-tip { left: 108px; width: 864px; height: 160px; display: flex; align-items: center; gap: 26px; padding: 0 32px;
      font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 600; font-size: 38px; line-height: 1.22; }
    .PX-num { width: 64px; height: 64px; flex: none; border-radius: 50%; background: #F4A62A; color: #0D1316; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 34px; }
    #PX-final { position: absolute; left: 108px; top: 1010px; width: 864px; font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; font-size: 72px; line-height: 1.08; letter-spacing: -0.02em; }""",
      eyebrow("Trois réflexes") + "\n" + cons_html + """
      <div id="PX-final">Ton compteur compte des tours, <span class="PX-hl">le radar mesure la réalité.</span></div>
""" + figure("PX-figure", 108, 1300, 864, h=360, ring=True, tag="13″", pos_y=0.75) + """""",
      """      tl.fromTo("#PX-eyebrow", { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.5, ease: E }, 0.05);
      rise("#PX-t0", 0.4, 30, 0.5);
      rise("#PX-t1", 1.9, 30, 0.5);
      rise("#PX-t2", 3.4, 30, 0.5);
      rise("#PX-final", 5.0, 30, 0.7);
      tl.fromTo("#PX-figure", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8, ease: E }, 5.3);
      tl.fromTo("#PX-figure img", { scale: 1.1 }, { scale: 1.18, duration: D - 5.3, ease: "none" }, 5.3);""")
print("scènes écrites")
