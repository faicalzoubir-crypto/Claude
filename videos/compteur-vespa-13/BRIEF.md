---
workflow: faceless-explainer
flow: automation
storyboard: no
message: "Avec une roue avant de 13 pouces au lieu de 12, ta Vespa roule 5,4 % plus vite que le compteur ne l'affiche, et elle a parcouru plus de kilomètres qu'il n'en a comptés."
destination: social
aspect: 1080x1920
language: fr
audience: "Grand public, pilotes de scooter"
length: 90s
angle: concept
narration: no
---

## Intent

Version Vespa du film `videos/compteur-roue-radar` (« Pourquoi ton compteur peut te mentir », Ford Fiesta, 16:9), avec les chiffres de l'utilisateur :

- roue avant passée de **120/70-12** à **120/70-13** (le compteur de la Vespa lit la roue avant) ;
- **145 MAD** de carburant pour **229 km**, lus au compteur, donc déjà avec la roue de 13 pouces ;
- la figure fournie (Vespa 3D menthe) est utilisée dans les analyses. À la demande de l'utilisateur (« Make the scooter looks standing »),
  elle est rendue **debout** : même modèle 3D que la scène de glissade (`videos/glissade-vespa-asr`), sans inclinaison
  (`tools/figure-vespa/` → `assets/images/vespa-3d.jpg` ; `node tools/figure-vespa/rendu.mjs <sortie.png> "w=2238&h=1742&cam=4.1,1.6,2.5&tgt=0.05,0.6,0.85&fov=27"`
  affiche aussi la position de la roue avant, reportée dans `AV` de `tools/scenes.py`).

Format vertical 9:16, en français, **sans voix off**, sous-titres incrustés, musique et bruitages.

Révision « Remove the part that the police man explain the case and make the video only 90sec, change the music » :

- la scène du contrôle (bulles du policier) est supprimée ; le radar à 63 km/h reste dans la scène « Sur la route »,
  avec le sous-titre « Mais le radar mesure ta vraie vitesse : 63 km/h » ;
- **90,0 s** : 10 scènes (5 + 5,5 + 13 + 6 + 14 + 9,5 + 7 + 11 + 14 + 9,5 s, fondus de 0,5 s), sous-titres raccourcis ;
- nouvelle musique (`tools/music.py`) : groove lo-fi (piano électrique FM, nappe, basse ronde, batterie feutrée
  avec swing, réverbération, motif de kalimba par moments), pause avant le radar puis impact, accord final de Dm9.
  Même identité de marque (90 BPM, ré mineur, Dm – B♭ – F – C) ; l'ancienne version (nappe + arpège en sinus) était agaçante.

Ajout « You did it for 60 km per hour now add for 100 km per hour » : la scène « Sur la route » (10 s) passe à 100 au
compteur (radar 105 km/h, 105,4 réels) après 60 (radar 63) ; le tableau gagne une colonne « à 100 » ; durée toujours
90,0 s (calcul et carburant raccourcis à 12,5 s) ; second accent musical sur le radar à 105.

## Chiffres

Tous les chiffres viennent de `tools/calculs.py` (`python3 tools/calculs.py` les affiche, `--verifier` contrôle qu'ils sont tous présents dans les scènes).

| | 120/70-12 (origine) | 120/70-13 (actuelle) |
|---|---|---|
| Diamètre = jante × 25,4 + 2 × 120 × 70 / 100 | 472,8 mm | 498,2 mm |
| Circonférence | 1,485 m | 1,565 m |

- Rapport 498,2 / 472,8 = 1,054, soit **+5,4 %**, environ 8 cm de plus à chaque tour de roue.
- Compteur 60 km/h → **63,2 km/h** réels (le radar lit 63).
- Compteur 100 km/h → **105,4 km/h** réels (le radar lit 105).
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
python3 tools/normaliser.py livrables/compteur-vespa-13.mp4   # son à −14 LUFS
```

Charte : `brand/BRAND.md` (fond `#0D1316` + grille, ambre `#F4A62A`, objets menthe `#93CDBB`, Space Grotesk + Inter).
