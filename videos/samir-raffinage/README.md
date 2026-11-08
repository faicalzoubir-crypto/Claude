# « شحال غادي يسوى اللتر؟ » — la SAMIR et le prix de l'essence

Vidéo verticale en arabe (1080 × 1920, 30 i/s, 99 s, sous-titres incrustés) : un litre d'essence à
13,95 DH, ce qu'il contient (achat ≈ 46 %, taxes ≈ 38 %, transport et marges ≈ 16 %), ce qu'une
SAMIR relancée changerait (la marge de raffinage, ≈ 1,20 DH/L en temps normal, avant ses coûts) et ce
qu'elle apporte vraiment (sécurité d'approvisionnement). Storyline A de `STORYLINES.md`, cahier des
charges dans `SPEC.md`.

## Livrable

`livrables/samir-raffinage-99s.mp4`

## Chaîne de fabrication

| Étape | Commande | Produit |
|---|---|---|
| Voix arabe (Piper `ar_JO-kareem-medium`, tashkeel écrit à la main dans `script.json`) | `python3 tools/voice.py` | `assets/voice/*.wav`, `timing.json` |
| Calage sur la voix | `python3 tools/assemble.py` | `cues.js`, `index.html`, `compositions/captions.html` |
| Plans 3D tirés du modèle `refinery/samir-3d` | `python3 tools/render3d/build_film.py` puis `node tools/render3d/render.cjs` | `assets/footage/*.mp4/.jpg`, `footage-anchors.js` |
| Musique (identité de marque, 90 BPM ré mineur) et bruitages | `python3 tools/music.py` puis `python3 tools/assemble.py` | `assets/music/bed-voix.m4a`, `assets/sfx/*.wav` |
| Contrôle, rendu | `npx hyperframes check`, `npx hyperframes render` | |

`tools/render3d` a besoin de `npm i` (three 0.160.0) et du Chromium de Playwright (SwiftShader).
Les étiquettes posées sur les plans 3D suivent les points projetés image par image (`footage-anchors.js`).

## Sources des chiffres

- Structure du prix : Conseil de la concurrence (T4 2024), via Hespress, SNRT News, Le Matin.
- Prix de 13,95 DH/L : TelQuel, mars 2026.
- Arrêt en août 2015, liquidation en mars 2016 : MEED, Hespress.
- Marge de raffinage de 1,20 DH/L : exemple calculé (20 $/baril ÷ 159 L), marqué « مثال » à l'écran ;
  l'écart final de 0,5 à 2 DH/L est une estimation, marquée « تقدير ».
- Le modèle 3D est représentatif, pas le plan réel du site.
