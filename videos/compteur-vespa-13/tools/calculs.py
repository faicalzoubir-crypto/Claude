#!/usr/bin/env python3
"""Calculs de la vidéo « Vespa : de 12 à 13 pouces » — source unique des chiffres.

    python3 tools/calculs.py            # affiche tous les chiffres de la vidéo
    python3 tools/calculs.py --verifier # vérifie que les scènes affichent ces chiffres

Formules (reprises de la vidéo d'origine) :
  Diamètre = (jante en pouces × 25,4) + 2 × (largeur × série / 100)
  Vitesse réelle = vitesse affichée × (diamètre nouveau / diamètre d'origine)
Le compteur d'une Vespa lit la roue avant : seul le pneu avant compte.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ORIGINE = (120, 70, 12)  # pneu avant d'origine : 120/70-12
NOUVEAU = (120, 70, 13)  # après le passage en 13 pouces : 120/70-13
CARBURANT_MAD = 145      # plein payé
KM_COMPTEUR = 229        # distance lue au compteur avec les roues de 13
VITESSE_CONTROLE = 100   # compteur au passage devant le radar
VITESSES_TABLEAU = 100
PNEUS_TABLEAU = [(110, 70, 12), (120, 70, 12), (130, 70, 12), (110, 70, 13), (130, 60, 13), (120, 70, 13), (130, 70, 13)]


def diametre(p):
    largeur, serie, jante = p
    return jante * 25.4 + 2 * largeur * serie / 100


def fr(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


D0, D1 = diametre(ORIGINE), diametre(NOUVEAU)
RAPPORT = D1 / D0
C0, C1 = math.pi * D0 / 1000, math.pi * D1 / 1000
KM_REELS = KM_COMPTEUR * RAPPORT

CHIFFRES = {
    "diamètre 12": fr(D0) + " mm",
    "diamètre 13": fr(D1) + " mm",
    "flanc": fr(ORIGINE[0] * ORIGINE[1] / 100, 0) + " mm",
    "jante 12": fr(12 * 25.4) + " mm",
    "jante 13": fr(13 * 25.4) + " mm",
    "circonférence 12": fr(C0, 3) + " m",
    "circonférence 13": fr(C1, 3) + " m",
    "écart par tour": fr((C1 - C0) * 100, 0) + " cm",
    "rapport": fr(RAPPORT, 3),
    "écart %": "+" + fr((RAPPORT - 1) * 100) + " %",
    "vitesse réelle à 100": fr(VITESSE_CONTROLE * RAPPORT) + " km/h",
    "radar": fr(VITESSE_CONTROLE * RAPPORT, 0) + " km/h",
    "km réels": fr(KM_REELS) + " km",
    "km non comptés": fr(KM_REELS - KM_COMPTEUR) + " km",
    "MAD/100 km compteur": fr(CARBURANT_MAD / KM_COMPTEUR * 100) + " MAD",
    "MAD/100 km réels": fr(CARBURANT_MAD / KM_REELS * 100) + " MAD",
    "MAD/km compteur": fr(CARBURANT_MAD / KM_COMPTEUR, 2) + " MAD",
    "MAD/km réel": fr(CARBURANT_MAD / KM_REELS, 2) + " MAD",
    "1000 km compteur": f"{1000 * RAPPORT:,.0f}".replace(",", "\u202f") + " km",
}


def tableau():
    lignes = []
    for p in PNEUS_TABLEAU:
        d = diametre(p)
        ecart = (d / D0 - 1) * 100
        signe = "+" if ecart > 0.05 else ("−" if ecart < -0.05 else "")
        lignes.append((f"{p[0]}/{p[1]}-{p[2]}", fr(d) + " mm", signe + fr(abs(ecart)) + " %",
                       fr(VITESSES_TABLEAU * d / D0) + " km/h"))
    return lignes


if __name__ == "__main__":
    for k, v in CHIFFRES.items():
        print(f"{k:22s} {v}")
    print()
    for l in tableau():
        print("  ".join(f"{c:>12s}" for c in l))
    if "--verifier" in sys.argv:
        textes = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "compositions").rglob("*.html"))
        # la ligne de référence affiche « — » plutôt que « 0,0 % »
        attendus = list(CHIFFRES.values()) + [c for l in tableau() for c in l if c != "0,0 %"]
        manquants = [c for c in attendus if c.replace(" ", " ") not in textes and c not in textes]
        print("\nChiffres absents des scènes :", manquants or "aucun")
        sys.exit(1 if manquants else 0)
