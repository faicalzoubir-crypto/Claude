#!/usr/bin/env python3
"""Plan du film « Vespa : de 12 à 13 pouces » — source unique du minutage.

Durées des scènes, sous-titres (pas de voix off : ils portent le texte),
bruitages et transitions. Génère :
  index.html                    hôtes des scènes, sous-titres, musique, bruitages, transitions
  compositions/captions.html    piste de sous-titres incrustés
  livrables/compteur-vespa-13.srt
  tools/plan.json               débuts des scènes, pour tools/music.py

  python3 tools/construire.py
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
CHEVAUCHEMENT = 0.5  # chaque scène commence pendant le fondu de la précédente

# (id, durée, transition d'entrée, sous-titres [(début, fin, texte, à l'écran ?)], bruitages [(t, son, volume)])
# Les phrases déjà écrites en grand dans l'image (question, bandeau, conseils, phrase finale)
# ne sont pas incrustées, mais restent dans le .srt. Version 90 s, sans la scène du policier.
SCENES = [
    ("01-question", 5.0, None, [
        (0.3, 4.7, "J’ai passé ma Vespa de 12 à 13 pouces… mon compteur affiche-t-il toujours la vraie vitesse ?", False),
    ], [(0.0, "whoosh-soft", 0.35)]),
    ("02-titre", 5.5, "fondu", [
        (0.3, 1.7, "Réponse courte : non.", True),
        (1.9, 5.2, "Ton compteur ne mesure pas ta vitesse… il compte des tours de roue.", True),
    ], [(2.0, "tick", 0.4), (2.6, "tick", 0.25), (3.2, "tick", 0.25), (3.8, "tick", 0.25)]),
    ("03-transmission", 13.0, "glisse", [
        (0.6, 2.8, "Le piston fait tourner le vilebrequin.", True),
        (3.0, 5.2, "Variateur et courroie : le rapport change tout seul.", True),
        (5.4, 7.6, "L’embrayage centrifuge s’engage quand tu accélères.", True),
        (7.8, 10.0, "Le réducteur fait tourner la roue arrière…", True),
        (10.2, 12.6, "… qui transforme la rotation en déplacement.", True),
    ], [(0.6, "click", 0.35), (3.0, "click", 0.35), (5.4, "click", 0.35), (7.8, "click", 0.35), (10.2, "click", 0.35), (12.5, "whoosh-soft", 0.3)]),
    ("04-capteur", 6.0, "zoom", [
        (0.3, 3.0, "Un capteur compte les tours de la roue avant…", True),
        (3.1, 5.7, "… et le calculateur en déduit la vitesse affichée.", True),
    ], [(1.1, "blip", 0.3), (1.5, "blip", 0.3), (1.9, "blip", 0.3), (2.3, "blip", 0.3), (4.4, "chime", 0.3)]),
    ("05-calcul", 14.0, "fondu", [
        (0.3, 2.9, "Le compteur multiplie les tours par la circonférence d’origine.", True),
        (3.0, 6.9, "Pneu d’origine 120/70-12 : 472,8 mm, soit 1,485 m par tour.", True),
        (7.0, 10.1, "En 120/70-13 : 498,2 mm, soit 1,565 m par tour.", True),
        (10.2, 13.7, "Tout est multiplié par 1,054 : tu roules 5,4 % plus vite qu’affiché.", True),
    ], [(3.1, "tick", 0.35), (5.4, "tick", 0.35), (7.2, "tick", 0.35), (10.4, "ding", 0.35)]),
    ("06-comparaison", 9.5, "glisse", [
        (0.4, 3.7, "Chaque roue fait un tour : la 13 pouces va 8 cm plus loin.", True),
        (3.8, 6.2, "Mais le compteur compte « un tour »… dans les deux cas.", True),
        (6.3, 9.2, "Roue plus grande : tu roules plus vite qu’affiché.", False),
    ], [(0.3, "roll", 0.3), (3.0, "ding", 0.35)]),
    ("07-serein", 7.0, "fondu", [
        (0.3, 3.4, "Jantes de 13 montées. Le compteur indique 60 : tu es serein.", True),
        (3.6, 6.7, "Mais le radar mesure ta vraie vitesse : 63 km/h.", True),
    ], [(2.4, "tick", 0.4), (3.6, "radar-beep", 0.45)]),
    ("09-tableau", 11.0, "fondu", [
        (0.3, 4.2, "Pour 60 au compteur : 58,2 en vrai avec un 110/70-12…", True),
        (4.3, 7.4, "… 63,2 avec ton 120/70-13…", True),
        (7.5, 10.7, "… et 65 avec un 130/70-13.", True),
    ], [(1.0 + 0.6 * i, "tick", 0.25) for i in range(7)]),
    ("10-carburant", 14.0, "glisse", [
        (0.3, 3.3, "Ton plein : 145 MAD pour 229 km… lus au compteur.", True),
        (3.4, 6.9, "En vrai : 229 × 1,054 = 241,3 km. 12,3 km jamais comptés.", True),
        (7.0, 10.3, "Ton essence coûte 60,1 MAD aux 100 km, pas 63,3.", True),
        (10.4, 13.7, "Entretien : 1 000 km affichés = 1 054 km roulés.", True),
    ], [(3.6, "tick", 0.35), (7.2, "tick", 0.35), (10.6, "ding", 0.35)]),
    ("11-conclusion", 9.5, "fondu", [
        (0.3, 1.8, "Trois réflexes : respecte les tailles homologuées pour ta Vespa,", False),
        (1.9, 3.3, "vérifie ta vitesse au GPS après un changement de jantes,", False),
        (3.4, 4.9, "et fais recalibrer ton compteur… ou corrige tes calculs de 5,4 %.", False),
        (5.0, 9.3, "Ton compteur compte des tours, le radar mesure la réalité.", False),
    ], [(0.4, "tick", 0.35), (1.9, "tick", 0.35), (3.4, "tick", 0.35), (5.0, "chime", 0.3)]),
]

SFX_DUREES = {"whoosh-soft": 0.7, "tick": 0.06, "click": 0.08, "blip": 0.09, "chime": 1.6, "ding": 1.1,
              "roll": 2.4, "radar-beep": 0.31}


def debuts():
    t, out = 0.0, []
    for i, s in enumerate(SCENES):
        out.append(round(t, 3))
        t += s[1] - CHEVAUCHEMENT
    return out, round(out[-1] + SCENES[-1][1], 3)


def transitions(starts):
    js = []
    for i in range(1, len(SCENES)):
        a, b, t = SCENES[i - 1][0], SCENES[i][0], starts[i]
        kind = SCENES[i][2]
        if kind == "glisse":
            js.append(f'tl.to("#el-{a}", {{ x: -{W}, duration: 0.5, ease: "power3.inOut" }}, {t});')
            js.append(f'tl.fromTo("#el-{b}", {{ x: {W}, opacity: 1 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: "power3.inOut" }}, {t});')
        elif kind == "zoom":
            js.append(f'tl.to("#el-{a}", {{ scale: 2.2, opacity: 0, filter: "blur(8px)", duration: 0.4, ease: "power3.in" }}, {t});')
            js.append(f'tl.fromTo("#el-{b}", {{ scale: 0.6, opacity: 0, filter: "blur(8px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power3.out" }}, {t});')
        else:  # fondu enchaîné
            js.append(f'tl.to("#el-{a}", {{ opacity: 0, duration: 0.5, ease: "power2.inOut" }}, {t});')
            js.append(f'tl.fromTo("#el-{b}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "power2.inOut" }}, {t});')
    return "\n        ".join(js)


def index(starts, total):
    hotes = []
    for i, (sid, d, *_r) in enumerate(SCENES):
        hotes.append(f'''      <div id="el-{sid}" class="scene" data-track-kind="graphics"
        data-composition-id="{sid}" data-composition-src="compositions/frames/{sid}.html"
        data-start="{starts[i]}" data-duration="{d}" data-track-index="{i % 2}"></div>''')
    audios, n = [], 0
    for i, s in enumerate(SCENES):
        for t, son, vol in s[4]:
            audios.append(f'''      <audio id="el-sfx-{n}" src="assets/sfx/{son}.wav" data-start="{round(starts[i] + t, 3)}"
        data-duration="{SFX_DUREES[son]}" data-track-index="{20 + n}" data-volume="{vol}"></audio>''')
            n += 1
    return f'''<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #0D1316; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <!-- Généré par tools/construire.py : modifier le plan là-bas, puis relancer. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{chr(10).join(hotes)}

      <!-- sous-titres -->
      <div id="el-captions" class="scene" data-track-kind="captions" data-composition-id="captions"
        data-composition-src="compositions/captions.html" data-start="0" data-duration="{total}" data-track-index="2"></div>

      <!-- musique -->
      <audio id="el-bgm" src="assets/music/fond.m4a" data-start="0" data-duration="{total}" data-track-index="11" data-volume="0.5"></audio>

      <!-- bruitages -->
{chr(10).join(audios)}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
      (function () {{ var tl = window.__timelines["main"];
        {transitions(starts)}
        tl.to({{}}, {{ duration: {total} }}, 0); // ancre : durée du film
      }})();
    </script>
  </body>
</html>
'''


def sous_titres(starts, total):
    groupes = []
    for i, s in enumerate(SCENES):
        for t0, t1, txt, visible in s[3]:
            if visible:
                groupes.append((round(starts[i] + t0, 3), round(t1 - t0, 3), txt))
    divs = "\n".join(
        f'    <div id="cap-{k}" class="cap clip" data-start="{a}" data-duration="{d}" data-track-index="0"><span>{escape(t)}</span></div>'
        for k, (a, d, t) in enumerate(groupes))
    anims = "\n".join(
        f'      tl.fromTo("#cap-{k}", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.18, ease: "power2.out" }}, {a});\n'
        f'      tl.to("#cap-{k}", {{ opacity: 0, duration: 0.15, ease: "power2.in" }}, {round(a + d - 0.15, 3)});'
        for k, (a, d, t) in enumerate(groupes))
    return f'''<template>
  <script src="vendor/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: "Inter"; src: url("assets/fonts/Inter-SemiBold.woff2") format("woff2"); font-weight: 600; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    /* Bande des sous-titres : au-dessus de l'interface des Reels, dans la zone titre (80 %). */
    .cap {{ position: absolute; left: 108px; width: 864px; top: 1390px; height: 230px;
      display: flex; align-items: flex-end; justify-content: center; opacity: 0; }}
    .cap span {{ display: inline-block; max-width: 864px; padding: 14px 28px; border-radius: 14px;
      background: rgba(13, 19, 22, 0.82); border: 1.5px solid #26343B;
      font-family: "Inter", sans-serif; font-weight: 600; font-size: 44px; line-height: 1.28;
      color: #E8EEEC; text-align: center; }}
  </style>
  <!-- Généré par tools/construire.py. -->
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}" data-duration="{total}">
{divs}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{anims}
      tl.to({{}}, {{ duration: {total} }}, 0);
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
'''


def srt(starts):
    def ts(x):
        ms = round(x * 1000)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    out, n = [], 0
    for i, s in enumerate(SCENES):
        for t0, t1, txt, _ in s[3]:
            n += 1
            out += [str(n), f"{ts(starts[i] + t0)} --> {ts(starts[i] + t1)}", txt, ""]
    return "\n".join(out)


if __name__ == "__main__":
    starts, total = debuts()
    (ROOT / "index.html").write_text(index(starts, total), encoding="utf-8")
    (ROOT / "compositions/captions.html").write_text(sous_titres(starts, total), encoding="utf-8")
    (ROOT / "livrables").mkdir(exist_ok=True)
    (ROOT / "livrables/compteur-vespa-13.srt").write_text(srt(starts), encoding="utf-8")
    (ROOT / "tools/plan.json").write_text(json.dumps(
        {"total": total, "scenes": [{"id": s[0], "debut": starts[i], "duree": s[1]} for i, s in enumerate(SCENES)]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    m, sec = divmod(total, 60)
    print(f"{len(SCENES)} scènes, {int(m)} min {sec:04.1f} s")
    for i, s in enumerate(SCENES):
        print(f"  {s[0]:<16} {starts[i]:7.2f} s  +{s[1]} s")
