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
# Les répliques déjà écrites en grand dans l'image (question, bulles, conseils, phrase finale)
# ne sont pas incrustées, mais restent dans le .srt.
SCENES = [
    ("01-question", 6.5, None, [
        (0.4, 6.1, "J’ai passé ma Vespa de 12 à 13 pouces… mon compteur affiche-t-il toujours la vraie vitesse ?", False),
    ], [(0.0, "whoosh-soft", 0.35)]),
    ("02-titre", 7.0, "fondu", [
        (0.4, 2.2, "Réponse courte : non.", True),
        (2.4, 6.6, "Ton compteur ne mesure pas ta vitesse… il compte des tours de roue.", True),
    ], [(2.6, "tick", 0.4), (3.2, "tick", 0.25), (3.8, "tick", 0.25), (4.4, "tick", 0.25)]),
    ("03-transmission", 17.5, "glisse", [
        (0.6, 3.9, "Tout part du moteur : le piston fait tourner le vilebrequin.", True),
        (4.1, 7.6, "Le variateur et sa courroie changent le rapport tout seuls.", True),
        (7.8, 11.1, "L’embrayage centrifuge relie le moteur dès que tu accélères.", True),
        (11.3, 14.4, "Le réducteur fait tourner la roue arrière…", True),
        (14.6, 17.0, "… qui transforme la rotation en déplacement.", True),
    ], [(0.6, "click", 0.35), (4.1, "click", 0.35), (7.8, "click", 0.35), (11.3, "click", 0.35), (14.6, "click", 0.35), (17.0, "whoosh-soft", 0.3)]),
    ("04-capteur", 7.5, "zoom", [
        (0.4, 3.8, "Sur ta Vespa, un capteur compte les tours de la roue avant…", True),
        (4.0, 7.0, "… et envoie l’info au calculateur, puis au compteur.", True),
    ], [(1.4, "blip", 0.3), (1.9, "blip", 0.3), (2.4, "blip", 0.3), (2.9, "blip", 0.3), (5.6, "chime", 0.3)]),
    ("05-calcul", 18.0, "fondu", [
        (0.4, 3.6, "Le compteur multiplie ces tours par la circonférence d’origine.", True),
        (3.8, 8.6, "Pneu avant d’origine, 120/70-12 : 472,8 mm de diamètre, soit 1,485 m par tour.", True),
        (8.8, 12.8, "En 13 pouces, 120/70-13 : 498,2 mm, soit 1,565 m par tour.", True),
        (13.0, 17.5, "Tout est multiplié par 1,054 : tu roules 5,4 % plus vite qu’affiché.", True),
    ], [(4.0, "tick", 0.35), (6.4, "tick", 0.35), (9.0, "tick", 0.35), (11.0, "tick", 0.35), (13.2, "ding", 0.35)]),
    ("06-comparaison", 12.0, "glisse", [
        (0.4, 4.8, "Chaque roue fait un tour : la 13 pouces va 8 cm plus loin.", True),
        (5.0, 8.4, "Mais le compteur compte « un tour »… dans les deux cas.", True),
        (8.6, 11.5, "Roue plus grande : tu roules plus vite qu’affiché.", True),
    ], [(0.3, "roll", 0.3), (3.0, "ding", 0.35)]),
    ("07-serein", 6.5, "fondu", [
        (0.4, 4.4, "Jantes de 13 montées. Le compteur indique 60 : tu es serein.", True),
    ], [(2.6, "tick", 0.4), (4.8, "radar-beep", 0.45)]),
    ("08-controle", 19.0, None, [
        (0.8, 5.6, "« Bonjour, vous rouliez à 63 km/h dans une zone limitée à 60. »", False),
        (6.0, 9.6, "« Impossible ! Mon compteur indiquait exactement 60 ! »", False),
        (10.0, 18.6, "« Votre compteur est réglé pour des roues de 12 pouces. En 13, chaque tour vous fait parcourir "
                     "plus de distance. Le radar, lui, mesure votre vitesse réelle. »", False),
    ], [(0.0, "siren-chirp", 0.35)]),
    ("09-tableau", 13.5, "fondu", [
        (0.4, 5.6, "Pour 60 au compteur : 58,2 en vrai avec un 110/70-12…", True),
        (5.8, 9.4, "… 63,2 avec ton 120/70-13…", True),
        (9.6, 13.0, "… et 65 avec un 130/70-13.", True),
    ], [(1.2 + 0.75 * i, "tick", 0.25) for i in range(7)]),
    ("10-carburant", 17.0, "glisse", [
        (0.4, 4.2, "Ton plein : 145 MAD pour 229 km… lus au compteur.", True),
        (4.4, 9.0, "En vrai : 229 × 1,054 = 241,3 km. 12,3 km jamais comptés.", True),
        (9.2, 13.0, "Ton essence coûte 60,1 MAD aux 100 km, pas 63,3.", True),
        (13.2, 16.6, "Et ton entretien prend du retard : 1 000 km affichés = 1 054 km roulés.", True),
    ], [(4.6, "tick", 0.35), (9.4, "tick", 0.35), (13.4, "ding", 0.35)]),
    ("11-conclusion", 12.5, "fondu", [
        (0.3, 2.4, "Trois réflexes : respecte les tailles homologuées pour ta Vespa,", False),
        (2.5, 4.4, "vérifie ta vitesse au GPS après un changement de jantes,", False),
        (4.5, 6.9, "et fais recalibrer ton compteur… ou corrige tes calculs de 5,4 %.", False),
        (7.0, 12.3, "Ton compteur compte des tours, le radar mesure la réalité.", False),
    ], [(0.5, "tick", 0.35), (2.5, "tick", 0.35), (4.5, "tick", 0.35), (7.0, "chime", 0.3)]),
]

SFX_DUREES = {"whoosh-soft": 0.7, "tick": 0.06, "click": 0.08, "blip": 0.09, "chime": 1.6, "ding": 1.1,
              "roll": 2.4, "radar-beep": 0.31, "siren-chirp": 0.9}


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
        else:  # fondu enchaîné (et entrée sans transition pour le contrôle : cut sur la sirène)
            if kind is None:
                js.append(f'tl.set("#el-{a}", {{ opacity: 0 }}, {t + CHEVAUCHEMENT});')
                continue
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
