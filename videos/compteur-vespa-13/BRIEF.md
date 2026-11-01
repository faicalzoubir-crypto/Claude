---
workflow: faceless-explainer
flow: automation
storyboard: no
message: "Avec une roue avant de 13 pouces au lieu de 12, ta Vespa roule 5,4 % plus vite que le compteur ne l'affiche, et elle a parcouru plus de kilomètres qu'il n'en a comptés."
destination: social
aspect: 1080x1920
language: fr
audience: "Grand public, pilotes de scooter"
length: 132s
angle: concept
narration: no
---

## Intent

Version Vespa du film `videos/compteur-roue-radar` (« Pourquoi ton compteur peut te mentir », Ford Fiesta, 16:9), avec les chiffres de l'utilisateur :

- roue avant passée de **120/70-12** à **120/70-13** (le compteur de la Vespa lit la roue avant) ;
- **145 MAD** de carburant pour **229 km**, lus au compteur, donc déjà avec la roue de 13 pouces ;
- la figure fournie (Vespa 3D menthe, `assets/images/vespa-3d.jpg`) est utilisée dans les analyses.

Format vertical 9:16, en français, **sans voix off**, sous-titres incrustés, musique et bruitages.

## Chiffres

Tous les chiffres viennent de `tools/calculs.py` (`python3 tools/calculs.py` les affiche, `--verifier` contrôle qu'ils sont tous présents dans les scènes).

| | 120/70-12 (origine) | 120/70-13 (actuelle) |
|---|---|---|
| Diamètre = jante × 25,4 + 2 × 120 × 70 / 100 | 472,8 mm | 498,2 mm |
| Circonférence | 1,485 m | 1,565 m |

- Rapport 498,2 / 472,8 = 1,054, soit **+5,4 %**, environ 8 cm de plus à chaque tour de roue.
- Compteur 60 km/h → **63,2 km/h** réels (le radar lit 63).
- 229 km au compteur → **241,3 km** réels, donc 12,3 km non comptés.
- Carburant : 63,3 MAD/100 km selon le compteur, **60,1 MAD/100 km** en réalité (0,60 MAD/km au lieu de 0,63).
- Entretien : une vidange prévue à 1 000 km au compteur tombe à 1 054 km réels.

## Hypothèses (affichées ou dites dans le film)

- Le compteur était juste avec la roue d'origine, et il est entraîné par la roue avant.
- Les autres dimensions du tableau sont des calculs théoriques : vérifier l'homologation et la carte grise avant tout montage.

## Construction

```bash
python3 tools/construire.py   # plan, index.html, sous-titres (+ .srt), tools/plan.json
python3 tools/scenes.py       # les 11 scènes de compositions/frames/
python3 tools/music.py        # musique de marque (90 BPM, ré mineur) → assets/music/fond.m4a
python3 tools/calculs.py --verifier
npx --yes hyperframes@0.8.226 check
npx --yes hyperframes@0.8.226 render . -o livrables/compteur-vespa-13.mp4 --fps 30
```

Charte : `brand/BRAND.md` (fond `#0D1316` + grille, ambre `#F4A62A`, objets menthe `#93CDBB`, Space Grotesk + Inter).
