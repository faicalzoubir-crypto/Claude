# La vitesse au volant — vidéo pédagogique (Manim)

Vidéo animée en français, en deux versions : **3 min 13 s** et **90 s**
(format Reels / TikTok). Deux idées :

1. Rouler plus vite fait gagner peu de temps : sur 10 km, passer de 40 à 50 km/h
   fait gagner **3 min**, passer de 80 à 120 km/h seulement **2 min 30**.
2. Le prix de ce gain : la **distance d'arrêt** (schéma, graphique,
   expériences simulées).

Tout est généré en Python avec [Manim Community Edition](https://www.manim.community/),
sans LaTeX ni image externe.

## Livrables

| Fichier | Contenu |
|---|---|
| `video_vitesse_90s.mp4` | **Version courte** 1920 × 1080, 30 i/s, 1 min 28 s |
| `video_vitesse_90s_vertical.mp4` | Version courte en 1080 × 1920 (Reels, TikTok) |
| `voix_off_90s.txt`, `sous_titres_90s.srt` | Narration minutée et sous-titres de la version courte (valables pour les deux formats) |
| `video_vitesse.mp4` | Version longue 1920 × 1080, 30 i/s, 3 min 13 s |
| `video_vitesse_vertical.mp4` | Version longue en 1080 × 1920, même minutage |
| `voix_off.txt`, `sous_titres.srt` | Narration minutée et sous-titres de la version longue (valables pour les deux formats) |

La vidéo n'a pas de bande son : `voix_off.txt` sert de texte d'enregistrement
et les sous-titres peuvent être incrustés ou chargés à part.

## Organisation

| Fichier | Rôle |
|---|---|
| `physique.py` | Modèle physique et scénario chiffré : **tous** les chiffres de la vidéo viennent d'ici |
| `textes_fr.json` | **Tous** les textes : écran, narration, formats des nombres, police |
| `textes.py` | Charge le JSON, met en forme les nombres (« 19,9 m », « 2 min 30 », « 13e »), calcule les valeurs de chaque scène |
| `style.py` | Couleurs (vert = lent/sûr, rouge = rapide/danger, orange = réaction), tailles de texte |
| `composants.py` | Briques visuelles : textes, compteurs, axes, voitures, enfant, immeuble, cotes, jauge |
| `scenes.py` | Les 8 scènes (`S1Accroche` … `S8Conclusion`) |
| `rendre.py` | Tests → rendu des scènes en parallèle → assemblage → voix off et sous-titres |
| `tests/` | Valeurs de contrôle du modèle, textes complets et sans chiffre en dur |

## Installation

```bash
# Bibliothèques système (Debian / Ubuntu)
sudo apt install ffmpeg libpango1.0-dev libcairo2-dev pkg-config python3-dev

# Environnement Python
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

La police utilisée est **Inter** (réglable dans `textes_fr.json`, clé `police`) ;
si elle manque, Pango prend une police de remplacement.

> Pillow est limité à la version 11 : avec Pillow 13 (dernière version testée), Manim 0.22 plante
> dès qu'une image est affichée (la signature du carton final).

## Régénérer la vidéo

```bash
.venv/bin/python rendre.py                      # brouillon 960×540, 15 i/s → build/brouillon/
.venv/bin/python rendre.py --final              # 1920×1080, 30 i/s → video_vitesse.mp4, voix_off.txt, sous_titres.srt
.venv/bin/python rendre.py --final --vertical   # 1080×1920 → video_vitesse_vertical.mp4
.venv/bin/python rendre.py --final --court      # version de 90 s → video_vitesse_90s.mp4, voix_off_90s.txt, sous_titres_90s.srt
.venv/bin/python rendre.py --final --court --vertical   # → video_vitesse_90s_vertical.mp4
.venv/bin/python rendre.py --scenes S4Paradoxe  # aperçu d'une ou plusieurs scènes
.venv/bin/python rendre.py --sans-rendu         # réassemble les scènes déjà rendues
```

`rendre.py` lance d'abord les tests (`pytest`) et s'arrête s'ils échouent.
Le rendu final prend environ 1 min 30 s sur 4 cœurs ; le brouillon environ 30 s.

## Changer les paramètres

### Le modèle physique — `physique.py`

| Paramètre | Valeur | Effet |
|---|---|---|
| `TEMPS_REACTION` | 1,0 s | Distance de réaction DR = v × t |
| `DECELERATION` | sec 7 m/s², mouillé 5 m/s² | Distance de freinage DF = v² / 2a |
| `G`, `HAUTEUR_ETAGE` | 9,81 m/s², 3 m | Chute équivalente h = v_i² / 2g et étage |
| `DISTANCE_TRAJET_KM` | 10 km | Trajet des scènes 2 et 3 |
| `VITESSES_VILLE`, `VITESSES_AUTOROUTE` | (40, 50), (80, 120) | Courses (scènes 2-3), courbe (4), expériences (7) |
| `VITESSE_SCHEMA`, `VITESSE_SCHEMA_BIS` | 50, 80 km/h | Schéma de la scène 5 |
| `VITESSES_GRAPHIQUE` | 30 à 130 km/h | Barres de la scène 6 |
| `VITESSES_CARRE` | (40, 80) | Exemple « vitesse ×2 → freinage ×4 » |
| `SECONDES_REELLES_PAR_SECONDE_VIDEO` | longue 60, courte 120 | Accéléré des chronos (1 s de vidéo = 1 min, ou 2 min en 90 s) |
| `LONGUEUR_VOITURE` | 4,2 m | Voitures dessinées à l'échelle |

Les textes, la narration et les sous-titres se mettent à jour tout seuls. Seule
exception : si les nouveaux chiffres contredisent une phrase (par exemple si
la ville ne fait plus gagner plus de temps que l'autoroute), il faut aussi
relire la narration dans `textes_fr.json`. `tests/test_physique.py` vérifie les
valeurs de contrôle du cahier des charges ; adaptez-le si vous changez
volontairement le modèle.

### Les textes — `textes_fr.json`

- `ecran` : textes affichés (communs aux deux versions) ; `narration` : voix off et
  sous-titres de la version longue, une réplique par clé ; `narration_courte` : idem
  pour la version de 90 s, plus resserrée.
- `{accolades}` : valeurs calculées (ne pas les traduire). Aucun chiffre ne doit
  être écrit en dur (un test le vérifie).
- `*mot*` : mot mis en couleur ; `\n` : retour à la ligne forcé (sinon la coupure est automatique).
- `nombres` : séparateurs (virgule décimale, espace fine des milliers, signe moins).
- `formats` : « 12 min », « 2 min 30 », « 13e », « 00:00 », etc.

### Style et format

- Couleurs et tailles : `style.py`.
- Format : `--vertical` pour 1080 × 1920. Les scènes adaptent leur mise en page :
  routes verticales, graphique en barres horizontales, colonnes empilées.
- Qualité : `QUALITES` dans `rendre.py`.

### Rythme et voix off

Les durées et instants de chaque scène s'écrivent `selon(longue, courte)` dans
`scenes.py` : c'est là qu'on resserre ou détend une version sans toucher à
l'autre. En version courte, `rendre.py` prévient si la vidéo dépasse 90 s.

Chaque scène note l'instant où commence chaque réplique (`self.dire(...)` dans
`scenes.py`). `rendre.py` en tire `voix_off.txt` et `sous_titres.srt`, calés
sur l'image. Dans `voix_off.txt`, `⚠ serré` signale une réplique trop longue
pour son créneau (au débit de 15 caractères/s) : raccourcissez le texte ou
retardez la réplique suivante (`jusqua(...)`, dictionnaires `temps` des scènes).

### Carton final et signature

Déposez un logo ou une signature dans `assets/signature.png` (fond transparent
conseillé) puis relancez le rendu : il apparaît sous « Levez le pied. ».
Sans ce fichier, le carton affiche seulement la jauge et le slogan.

## Version arabe

1. Copier `textes_fr.json` en `textes_ar.json` et traduire les valeurs (pas les `{accolades}`).
2. Dans le nouveau fichier : `"langue": "ar"`, `"direction": "rtl"`,
   `"typographie_fr": false`, une police arabe dans `"police"` (ex. « Noto Sans Arabic »,
   à installer), et si besoin `"chiffres": "٠١٢٣٤٥٦٧٨٩"` dans `nombres` pour les
   chiffres arabes orientaux.
3. `.venv/bin/python -m pytest` vérifie que tous les textes se remplissent.
4. `.venv/bin/python rendre.py --final --langue ar` → `video_vitesse_ar.mp4`,
   `voix_off_ar.txt`, `sous_titres_ar.srt`.

Tous les textes passent par `MarkupText` (Pango), qui gère l'écriture de droite
à gauche et la liaison des lettres. Les schémas restent orientés de gauche à
droite.

## Choix techniques

- **Aucun LaTeX** : tous les textes sont des `Text` Pango (`MarkupText` pour la
  couleur des mots). Les compteurs animés sont des `NombreTexte`, un
  `DecimalNumber` qui dessine ses chiffres avec Text (virgule décimale, chiffres
  à chasse fixe). Les axes sont des `AxeTexte`, une `NumberLine` avec
  `label_constructor=Text` dont les graduations sont des `NombreTexte`.
- **Voitures, enfant, immeuble, jauge** : formes vectorielles simples (`composants.py`).
- **Mouvements physiques** : les voitures suivent exactement `position_freinage`
  (réaction à vitesse constante, puis décélération constante). Les compteurs de
  vitesse suivent `vitesse_freinage`.
- **Scène 5** : la réaction (×4) et le freinage (×1,5) sont montrés au ralenti,
  avec l'étiquette « Ralenti » ; la reprise à 80 km/h est en temps réel.
- **Scène 7** : arrêt sur image quand l'obstacle surgit, puis réaction et
  freinage en temps réel. L'obstacle est exactement à la distance d'arrêt de la
  voiture lente.

## Minutage

| Scène | Longue | Courte (90 s) |
|---|---|---|
| 1. Accroche | 10 s | 5 s |
| 2. En ville | 25 s | 11 s |
| 3. Sur autoroute (+ bilan en version longue) | 25 s | 9 s |
| 4. Le paradoxe | 25 s | 11,5 s |
| 5. Schéma de la distance d'arrêt (+ reprise à 80 km/h en version longue) | 28 s | 11,5 s |
| 6. Graphique | 25 s | 10,5 s |
| 7. Expériences simulées | 40 s | 21 s |
| 8. Conclusion et carton final | 15 s | 8 s |
| **Total** | **3 min 13 s** | **1 min 28 s** |

La version courte garde tous les visuels et tous les chiffres clés. Elle
retire le bilan chiffré de la scène 3 (la courbe de la scène 4 le montre), la
reprise à 80 km/h du schéma (le graphique la contient) et la note sur les feux.
Les ralentis du schéma y sont moins marqués (×2 et ×1,2).
