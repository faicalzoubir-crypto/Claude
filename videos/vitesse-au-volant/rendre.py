#!/usr/bin/env python3
"""Rend la vidéo de bout en bout :
tests → scènes (en parallèle) → assemblage → voix off et sous-titres.

    python rendre.py                       # brouillon (960×540, 15 i/s) dans build/brouillon/
    python rendre.py --final               # 1920×1080, 30 i/s → video_vitesse.mp4
    python rendre.py --final --vertical    # 1080×1920 → video_vitesse_vertical.mp4
    python rendre.py --scenes S4Paradoxe   # aperçu d'une ou plusieurs scènes
    python rendre.py --final --langue ar   # textes_ar.json → video_vitesse_ar.mp4
    python rendre.py --final --court       # version de 90 s → video_vitesse_90s.mp4
"""

import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent
SCENES = [
    "S1Accroche",
    "S2Ville",
    "S3Autoroute",
    "S4Paradoxe",
    "S5Schema",
    "S6Graphique",
    "S7Experiences",
    "S8Conclusion",
]
QUALITES = {"brouillon": (960, 540, 15), "final": (1920, 1080, 30)}
CARACTERES_PAR_SECONDE = 15  # débit de lecture visé pour la voix off
DUREE_MAX_COURTE = 90.0  # s, limite des Reels
LIGNE_SRT = 42  # caractères par ligne de sous-titre (2 lignes maximum)


def lancer_tests():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=DOSSIER)
    if r.returncode:
        sys.exit("Les tests échouent : rendu annulé.")


def rendre_scene(nom, largeur, hauteur, fps, media, reperes, langue, version):
    # Un dossier media par scène : les processus parallèles ne doivent pas
    # partager le cache des textes (fichiers SVG écrits à la volée).
    media = media / nom
    env = {**os.environ, "VITESSE_REPERES": str(reperes), "VITESSE_LANGUE": langue, "VITESSE_VERSION": version}
    cmd = [
        sys.executable, "-m", "manim", "render", "scenes.py", nom,
        "-r", f"{largeur},{hauteur}", "--fps", str(fps),
        "--media_dir", str(media), "--disable_caching",
        "--progress_bar", "none", "-v", "WARNING",
    ]
    debut = time.time()
    r = subprocess.run(cmd, cwd=DOSSIER, env=env, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{nom} : échec du rendu\n{r.stdout[-4000:]}\n{r.stderr[-4000:]}")
    sortie = chemin_scene(media.parent, nom, hauteur, fps)
    print(f"  ✓ {nom} ({time.time() - debut:.0f} s)", flush=True)
    return sortie


def chemin_scene(media, nom, hauteur, fps):
    return media / nom / "videos" / "scenes" / f"{hauteur}p{fps}" / f"{nom}.mp4"


def assembler(fichiers, sortie):
    liste = sortie.with_suffix(".txt")
    liste.write_text("".join(f"file '{Path(f).resolve()}'\n" for f in fichiers), encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(liste),
         "-c", "copy", "-movflags", "+faststart", str(sortie)],
        check=True,
    )
    liste.unlink()


def loudnorm(entree, sortie, cible=-14.0, crete=-1.5):
    """Normalisation EBU R128 en deux passes (gain linéaire si possible)."""
    filtre = f"loudnorm=I={cible}:TP={crete}:LRA=11"
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(entree), "-af", filtre + ":print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    m = json.loads(r.stderr[r.stderr.rindex("{") :])
    mesures = (
        f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
        f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(entree), "-af", filtre + mesures,
         "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(sortie)],
        check=True,
    )


def mixer_musique(video, durees, reperes, piste):
    """Ajoute la musique à la vidéo : assets/musique.* si présent, sinon la
    musique générée par musique.py, calée sur les événements des scènes."""
    import musique

    total = sum(durees.values())
    brut = piste.with_suffix(".brut.wav")
    perso = sorted((DOSSIER / "assets").glob("musique.*")) if (DOSSIER / "assets").is_dir() else []
    if perso:
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", str(perso[0]), "-t", f"{total:.3f}",
             "-af", f"afade=t=out:st={max(total - 2.5, 0):.3f}:d=2.5", "-ar", "48000", str(brut)],
            check=True,
        )
    else:
        musique.ecrire(musique.scenes_depuis(reperes, durees), brut)
    loudnorm(brut, piste)
    brut.unlink()
    avec_son = video.with_name(video.stem + ".son.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(piste), "-map", "0:v", "-map", "1:a",
         "-c", "copy", "-shortest", "-movflags", "+faststart", str(avec_son)],
        check=True,
    )
    avec_son.replace(video)
    return "assets/" + perso[0].name if perso else "musique.py"


def duree_video(f):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout)


# --- Voix off et sous-titres -----------------------------------------------------


def horodatage(t, srt=False):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    if srt:
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return f"{m:02d}:{s:02d}.{ms // 100}"


def repliques(scenes, reperes, langue, version):
    """Liste des répliques : (début absolu, fin du créneau, scène, texte)."""
    sys.path.insert(0, str(DOSSIER))
    from textes import Textes, valeurs

    T = Textes(langue, version)
    V = valeurs(T)
    brut, debut = [], 0.0
    fins_scenes = []
    for nom, duree in scenes:
        info = json.loads((reperes / f"{nom}.json").read_text(encoding="utf-8"))
        for r in info["reperes"]:
            brut.append([debut + r["t"], r["scene"], T.narration(r["scene"], r["cle"], **V[r["scene"]])])
        debut += duree
        fins_scenes.append(debut)
    sortie = []
    for i, (t, scene, txt) in enumerate(brut):
        fin_scene = next(f for f in fins_scenes if f > t)
        suivant = brut[i + 1][0] if i + 1 < len(brut) else fin_scene
        sortie.append((t, min(suivant, fin_scene), scene, txt))
    return T, sortie


def ecrire_voix_off(T, lignes, duree_totale, chemin):
    noms = T.data["scenes"]
    out = [
        f"{noms['titre_video'].upper()} — voix off" + (" (version courte)" if T.version == "courte" else ""),
        f"Durée totale : {horodatage(duree_totale)}. Chaque réplique commence à l'instant indiqué ;",
        f"entre crochets, le temps disponible avant la suivante (débit visé ≈ {CARACTERES_PAR_SECONDE} caractères/s).",
        "",
    ]
    scene_courante = None
    for t, fin, scene, txt in lignes:
        if scene != scene_courante:
            scene_courante = scene
            debut_s = t
            fin_s = max(f for tt, f, sc, _ in lignes if sc == scene)
            out += ["", f"## {noms[scene]}  ({horodatage(debut_s)} – {horodatage(fin_s)})"]
        dispo = fin - t
        besoin = len(txt) / CARACTERES_PAR_SECONDE
        alerte = "  ⚠ serré" if besoin > dispo + 0.3 else ""
        out.append(f"{horodatage(t)}  [{dispo:4.1f} s]  {txt}{alerte}")
    chemin.write_text("\n".join(out) + "\n", encoding="utf-8")


def decouper(txt):
    """Coupe une réplique en blocs de 2 lignes de LIGNE_SRT caractères max."""
    lignes = textwrap.wrap(txt, LIGNE_SRT, break_long_words=False)
    if len(lignes) <= 2:
        return ["\n".join(lignes)]
    phrases = re.split(r"(?<=[.!?…:])\s+", txt)
    if len(phrases) > 1:
        blocs = []
        for p in phrases:
            blocs += decouper(p)
        return blocs
    milieu = len(lignes) // 2
    return decouper(" ".join(lignes[:milieu])) + decouper(" ".join(lignes[milieu:]))


def ecrire_srt(lignes, chemin):
    out, n = [], 0
    for t, fin, _, txt in lignes:
        lecture = len(txt) / CARACTERES_PAR_SECONDE
        fin = min(fin - 0.05, t + max(lecture + 1.2, 1.6))
        blocs = decouper(txt)
        total = sum(len(b) for b in blocs)
        debut = t
        for b in blocs:
            d = (fin - t) * len(b) / total
            n += 1
            out += [str(n), f"{horodatage(debut, True)} --> {horodatage(debut + d, True)}", b, ""]
            debut += d
    chemin.write_text("\n".join(out), encoding="utf-8")


# --- Programme principal ---------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final", action="store_true", help="haute qualité (1080p, 30 i/s)")
    ap.add_argument("--vertical", action="store_true", help="format 1080×1920 (Reels, TikTok)")
    ap.add_argument("--langue", default="fr", help="utilise textes_<langue>.json")
    ap.add_argument("--court", action="store_true", help="version de 90 s (narration_courte)")
    ap.add_argument("--scenes", nargs="+", default=SCENES, help="scènes à rendre (aperçu)")
    ap.add_argument("--processus", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--sans-tests", action="store_true")
    ap.add_argument("--sans-rendu", action="store_true", help="réassemble les scènes déjà rendues")
    ap.add_argument("--sans-musique", action="store_true", help="vidéo muette")
    args = ap.parse_args()

    if not args.sans_tests:
        lancer_tests()
    qualite = "final" if args.final else "brouillon"
    largeur, hauteur, fps = QUALITES[qualite]
    if args.vertical:
        largeur, hauteur = hauteur, largeur
    version = "courte" if args.court else "longue"
    suffixe = (
        ("_90s" if args.court else "")
        + ("_vertical" if args.vertical else "")
        + ("" if args.langue == "fr" else f"_{args.langue}")
    )
    variante = qualite + suffixe
    build = DOSSIER / "build" / variante
    media, reperes = build / "media", build / "reperes"
    reperes.mkdir(parents=True, exist_ok=True)

    print(f"Rendu {variante} ({version}) : {largeur}×{hauteur}, {fps} i/s, {len(args.scenes)} scène(s)")
    ordre = sorted(args.scenes, key=lambda s: -SCENES.index(s) if s == "S7Experiences" else SCENES.index(s))
    if args.sans_rendu:
        fichiers = {n: chemin_scene(media, n, hauteur, fps) for n in SCENES}
    else:
        with cf.ThreadPoolExecutor(args.processus) as ex:
            futurs = {
                n: ex.submit(rendre_scene, n, largeur, hauteur, fps, media, reperes, args.langue, version) for n in ordre
            }
            fichiers = {n: f.result() for n, f in futurs.items()}

    if args.scenes != SCENES:
        for n in args.scenes:
            print(f"  {fichiers[n]}")
        return

    sortie_dir = DOSSIER if args.final else build
    video = sortie_dir / f"video_vitesse{suffixe}.mp4"
    assembler([fichiers[n] for n in SCENES], video)
    scenes = [(n, duree_video(fichiers[n])) for n in SCENES]
    T, lignes = repliques(scenes, reperes, args.langue, version)
    total = sum(d for _, d in scenes)
    # Le minutage ne dépend pas du format : la version verticale réutilise
    # la voix off et les sous-titres de la version paysage (copie dans build/).
    textes_dir = build if args.vertical else sortie_dir
    suffixe_textes = ("_90s" if args.court else "") + ("" if args.langue == "fr" else f"_{args.langue}")
    ecrire_voix_off(T, lignes, total, textes_dir / f"voix_off{suffixe_textes}.txt")
    ecrire_srt(lignes, textes_dir / f"sous_titres{suffixe_textes}.srt")
    if not args.sans_musique:
        source = mixer_musique(video, dict(scenes), reperes, textes_dir / f"musique{suffixe_textes}.m4a")
        print(f"Musique : {source}, normalisée à −14 LUFS")
    for n, d in scenes:
        print(f"  {n:<14} {d:5.1f} s")
    print(f"Vidéo : {video} ({horodatage(total)})")
    if args.court and total > DUREE_MAX_COURTE:
        print(f"⚠ La version courte dépasse {DUREE_MAX_COURTE:.0f} s : resserrez les temps (selon(...) dans scenes.py).")


if __name__ == "__main__":
    main()
