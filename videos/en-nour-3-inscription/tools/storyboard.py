"""Builds storyboard.html (self-contained: images and fonts inlined) from storyboard/frames/NN.png."""
import base64
import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FRAMES = sorted((ROOT / "storyboard" / "frames").glob("*.png"))


def b64img(p, w=540):
    im = Image.open(p).convert("RGB")
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=84)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def b64font(name):
    return "data:font/woff2;base64," + base64.b64encode((ROOT / "assets" / "fonts" / name).read_bytes()).decode()


CELLS = [
    ("01", "Accroche", "0,0–6,0 s", "<b>Le soleil ouvre, la caméra plonge.</b> Titre « Avant d'inscrire votre enfant, venez tout découvrir. » La caméra dévale tout l'escalier d'îlots (aperçu des 7 étapes).", "coupe d'ouverture"),
    ("01b", "Accroche · façade", "3,0–6,0 s", "<b>Atterrissage sur la façade réelle.</b> La famille longe le mur jaune, les portails s'ouvrent, le logo apparaît : « La visite guidée, pas à pas ».", "plongée → atterrissage"),
    ("02", "Étape 1 · Accueil", "6,0–12,2 s", "<b>Le soleil-guide emprunte le premier pont de lumière.</b> L'hôtesse salue (« Bienvenue ! »), les niveaux surgissent et « Primaire » est choisi, zoom sur le plan « La visite ».", "travelling ↗ pont 1"),
    ("03", "Étape 2 · Présentation", "12,2–19,0 s", "<b>Le directeur présente le projet pédagogique.</b> Les 4 étages de la maquette s'allument au rythme de « maternelle, primaire, collège, lycée ».", "travelling ↖ pont 2"),
    ("04", "Étape 3 · Infrastructures", "19,0–26,1 s", "<b>Une vraie visite guidée.</b> La caméra zoome sur la classe, le labo, la salle informatique, la cour puis les espaces communs, chaque lieu étiqueté au mot près.", "travelling ↗ pont 3"),
    ("05", "Étape 4 · Organisation", "26,1–32,9 s", "<b>Les 4 piliers en orbite.</b> Méthodes, suivi & évaluation, encadrement, communication école-parents apparaissent sur leur mot, autour d'une classe en cours.", "travelling ↖ pont 4"),
    ("06", "Étape 5 · Services", "32,9–40,0 s", "<b>Zoom dans l'application Ecole Plus.</b> Notifications Notes, Absences, Messages, puis panoramique vers les activités : sport, arts, musique.", "travelling ↗ pont 5"),
    ("07", "Étape 6 · Modalités", "40,0–46,8 s", "<b>Une liste qui se coche toute seule.</b> Admission, places, frais, documents, dossier : les 5 points se cochent pendant que les documents volent dans le dossier bleu.", "travelling ↖ pont 6"),
    ("08", "Étape 7 · Conclusion", "46,8–52,8 s", "<b>Questions, réponses, poignée de main.</b> Badge « Inscription finalisée », confettis aux couleurs du logo, la fille saute de joie.", "travelling ↗ pont 7"),
    ("09", "Appel à l'action", "52,8–60,3 s", "<b>Le soleil-guide rejoint le grand soleil.</b> Recul sur tout le parcours éclairé, carte logo, bouton « Réservez votre visite » qui pulse. Plan tenu environ 2 s.", "montée + recul"),
]


def main():
    assert len(FRAMES) == len(CELLS), (len(FRAMES), len(CELLS))
    cells = []
    for (num, name, time, note, seam), img in zip(CELLS, FRAMES):
        cells.append(f"""
      <article class="cell" id="frame-{num}">
        <div class="shot"><img src="{b64img(img)}" alt="Plan {num} — {name}" /></div>
        <div class="label"><span class="n">{num} · {name.upper()}</span><span class="t">{time}</span></div>
        <p class="note">{note}</p>
        <span class="seam">{seam}</span>
      </article>""")
    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Storyboard EN-NOUR 3</title>
<style>
@font-face {{ font-family: "Baloo 2"; src: url("{b64font('Baloo2-var-latin.woff2')}") format("woff2"); font-weight: 400 800; }}
@font-face {{ font-family: "Quicksand"; src: url("{b64font('Quicksand-var-latin.woff2')}") format("woff2"); font-weight: 300 700; }}
:root {{ --sun:#F8B114; --blue:#2A91D1; --sky:#35B3E5; --deep:#165A8A; --ink:#1D3B57; --bg:#F4F8FC; --card:#FFFFFF; --muted:#5B7389; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0F1D2B; --card:#16293B; --ink:#E4EEF6; --deep:#8CC8F0; --muted:#9DB4C7; }} }}
:root[data-theme="dark"] {{ --bg:#0F1D2B; --card:#16293B; --ink:#E4EEF6; --deep:#8CC8F0; --muted:#9DB4C7; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--ink); font-family: "Quicksand", system-ui, sans-serif; padding: 32px 16px 64px; }}
header {{ max-width: 1200px; margin: 0 auto 28px; }}
h1 {{ font-family: "Baloo 2", system-ui, sans-serif; font-weight: 800; font-size: clamp(30px, 5vw, 52px); line-height: 1.05; color: var(--deep); }}
h1 small {{ font-size: 0.5em; color: var(--muted); font-weight: 700; margin-left: 8px; }}
.dek {{ margin-top: 10px; font-size: 18px; font-weight: 600; max-width: 820px; line-height: 1.45; }}
.tags {{ margin-top: 14px; display: flex; flex-wrap: wrap; gap: 8px; }}
.tag {{ background: var(--sun); color: #163A57; font-weight: 700; font-size: 14px; padding: 5px 12px; border-radius: 30px; }}
.tag.alt {{ background: var(--card); color: var(--deep); border: 1.5px solid var(--sky); }}
main {{ max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 22px; }}
.cell {{ background: var(--card); border-radius: 22px; padding: 12px 12px 16px; box-shadow: 0 6px 22px rgba(22,90,138,0.10); display: flex; flex-direction: column; gap: 10px; }}
.shot {{ aspect-ratio: 9 / 16; border-radius: 14px; overflow: hidden; background: #dbe9f4; }}
.shot img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.label {{ display: flex; justify-content: space-between; gap: 8px; font-family: "Baloo 2", sans-serif; font-weight: 800; font-size: 15px; color: var(--deep); letter-spacing: 0.02em; }}
.label .t {{ color: var(--muted); font-weight: 700; white-space: nowrap; }}
.note {{ font-size: 14.5px; line-height: 1.45; font-weight: 600; }}
.note b {{ color: var(--deep); }}
.seam {{ align-self: flex-start; font-size: 12.5px; font-weight: 700; color: var(--deep); border: 1.5px solid var(--sky); border-radius: 20px; padding: 3px 10px; }}
.wide {{ grid-column: 1 / -1; background: var(--card); border-radius: 22px; padding: 22px; box-shadow: 0 6px 22px rgba(22,90,138,0.10); }}
.wide h2 {{ font-family: "Baloo 2", sans-serif; font-weight: 800; font-size: 24px; color: var(--deep); margin-bottom: 12px; }}
.seammap {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-weight: 700; font-size: 14px; }}
.seammap .s {{ background: var(--bg); padding: 6px 10px; border-radius: 10px; }}
.seammap .a {{ color: var(--sun); font-weight: 800; }}
.tokens {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; font-size: 14.5px; line-height: 1.5; font-weight: 600; }}
.sw {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }}
.sw span {{ display: inline-flex; align-items: center; gap: 6px; font-size: 13px; }}
.sw i {{ width: 22px; height: 22px; border-radius: 6px; display: inline-block; border: 1px solid rgba(0,0,0,0.08); }}
ul {{ padding-left: 18px; }}
</style>
</head>
<body>
<header>
  <h1>EN-NOUR 3 — La visite guidée, pas à pas <small>v1</small></h1>
  <p class="dek">Cette vidéo dit aux parents que chez EN-NOUR 3, une visite guidée en 7 étapes (30 à 40 min) leur donne toutes les clés pour inscrire leur enfant en confiance, de la maternelle au lycée. Fil conducteur : <b>le chemin de lumière</b>, le soleil du logo qui guide la famille d'îlot en îlot.</p>
  <div class="tags"><span class="tag">1080 × 1920 · vertical</span><span class="tag">60,3 s</span><span class="tag">9 plans · 7 étapes</span><span class="tag alt">Voix off FR + sous-titres</span><span class="tag alt">3D isométrique</span></div>
</header>
<main>{''.join(cells)}
  <section class="wide">
    <h2>Enchaînements</h2>
    <div class="seammap"><span class="s">Soleil</span><span class="a">↓ plongée</span><span class="s">Façade</span><span class="a">↗ pont 1</span><span class="s">Accueil</span><span class="a">↖ pont 2</span><span class="s">Présentation</span><span class="a">↗ pont 3</span><span class="s">Infrastructures</span><span class="a">↖ pont 4</span><span class="s">Organisation</span><span class="a">↗ pont 5</span><span class="s">Services</span><span class="a">↖ pont 6</span><span class="s">Modalités</span><span class="a">↗ pont 7</span><span class="s">Conclusion</span><span class="a">↑ recul</span><span class="s">Appel à l'action</span></div>
  </section>
  <section class="wide">
    <h2>Charte et règles</h2>
    <div class="tokens">
      <div><b>Couleurs (du logo)</b>
        <div class="sw"><span><i style="background:#F8B114"></i>Or soleil</span><span><i style="background:#2A91D1"></i>Bleu</span><span><i style="background:#35B3E5"></i>Bleu ciel</span><span><i style="background:#165A8A"></i>Bleu profond (textes)</span><span><i style="background:#FBF3E4"></i>Crème</span></div>
      </div>
      <div><b>Typographies</b><br />Baloo 2 ExtraBold : titres, étapes, bouton<br />Quicksand Bold : points clés, sous-titres</div>
      <div><b>Interdits</b><ul><li>aucun chiffre inventé (frais, places)</li><li>Ecole Plus en rendu stylisé, jamais présenté comme une capture</li><li>pas d'effet de diaporama : chaque passage est un vrai mouvement de caméra</li></ul></div>
      <div><b>Encore ouvert</b><ul><li>musique de fond (morceau fourni, ou fond synthétisé)</li><li>coordonnées sous « Réservez votre visite »</li><li>capture réelle de l'application Ecole Plus (facultatif)</li></ul></div>
    </div>
  </section>
</main>
</body>
</html>
"""
    out = ROOT / "storyboard.html"
    out.write_text(html, encoding="utf-8")
    print(out, round(out.stat().st_size / 1024), "KB")


main()
