# REVIEW — reconstitution-accident-moto

Vidéo verticale 1080×1920, 25 s, 30 fps : `livrables/reconstitution-accident-moto.mp4`.

## Choix créatifs

- **Un seul monde en mètres** (`assets/kinematics.js`) : route, voies, terre-plein et deux-roues sont les mêmes dans
  tous les plans ; la caméra plonge, suit, zoome sur le contact, puis prend du recul. Aucun autre véhicule.
- **Cinématique cohérente** à partir des données (35 / 55 km/h, 20 m) : freinage du scooter 7,5 m/s² (arrêt en 6,3 m),
  réaction du motard B 1,0 s, freinage ≈ 7,2 m/s² (0,74 g), contact à ≈ 28 km/h, glissade de la BMW ≈ 8 m, motard
  à ≈ 5 m du contact sur la bordure du terre-plein, derrière la moto. `node tools/verifier.mjs` affiche tout.
- **Honnêteté du temps** : avec 20 m d'écart, tout se joue en ≈ 2 s réelles ; le film montre donc l'action à ×0,5 et
  le ralenti à ×0,1, indiqué à l'écran (« سرعة العرض ×0.5 », « حركة بطيئة ×0.1 »).
- **Clairement une simulation** : badge « محاكاة توضيحية » permanent, plan dessiné (pas de photo), « القيم والسرعات
  تقديرية » sous la carte d'étape, mention « ليست لقطات حقيقية » sur la fiche finale. Motard au sol schématique, sans
  blessure.
- **Voie non autorisée au scooter** (demande de l'auteur) : pendant l'étape 1 (3,6 → 6,5 s), la voie de gauche est
  surlignée en rouge (`#F25C54`, couleur « danger » de la charte) avec l'encadré « صاحب الدراجة الصغيرة / ليس له الحق في
  ذلك الممر » ; la même phrase est une ligne « ! » de la fiche de synthèse. Phrase de l'auteur, telle quelle : l'article
  du code de la route n'est pas cité. La mesure des 20 m passe à 6,35 → 7,75 s.
- **Nom de la rue** (demande de l'auteur) : « شارع فاس ». Sens de circulation (chaussée de droite, vers le haut) : « باتجاه
  طريق مراكش » ; sens opposé (chaussée de gauche, vers le bas) : « باتجاه شارع تادارت ». Étiquettes fléchées posées sur
  chaque chaussée à la fin de la plongée (1,6 → 3,75 s) et sur la vue d'ensemble (dès 16,45 s) ; « شارع فاس » dans le
  carton titre ; « شارع فاس · باتجاه طريق مراكش » sous le titre de la fiche de synthèse.
- Les numéros d'étape « 1) … 5) » sont rendus comme des pastilles ambre + texte (calques séparés, modifiables).
- Valeurs approchées écrites « حوالي » (environ) : le signe « ~ » se place à droite du nombre en arabe et prête à confusion.
- Musique de la charte (90 BPM, ré mineur), sans batterie : elle se retire avant le contact, impact grave étouffé au
  contact, accord final de Dm9 sous la fiche. Clics discrets à l'arrivée des étapes, souffle sur la plongée.

## Non fait / à fournir

- **Les références envoyées (vue satellite, photos de la BMW) ne sont pas arrivées dans la session** : le plan aérien est
  dessiné. Avec la vraie image, il faut la caler sur le repère (échelle px/m, orientation, position du nez de bordure).
- **Couleur du scooter** non précisée : menthe `#93CDBB` (couleur « objet » de la charte), à changer dans `compositions/world.html`.
- **Avatar présentateur arabe** (optionnel) : demande une connexion HeyGen (crédits) ; la voix locale (Kokoro) n'a pas d'arabe.

## Vérifié

- `npx hyperframes check` : 0 erreur. Avertissements gardés : fichier `world.html` long (une seule prise continue) ;
  étiquettes de la vue d'ensemble positionnées hors champ tant qu'elles sont invisibles.
- Regardé : `snapshot --review` (plans, coutures, téléphone) et des zooms sur les étiquettes (ordre droite-à-gauche).
- Son : mesuré avec `hyperframes audio` après normalisation (`tools/normaliser.py`) : −14 LUFS intégrés, crête vraie −1,8 dBTP,
  aucun écrêtage, aucun silence ; clics détectés à l'arrivée des étapes (3,15 / 9,03 / 12,18 s…). **Pas écouté.**
- Rendu : `npx hyperframes@0.9.19 render . -o livrables/reconstitution-accident-moto.mp4 --fps 30` (1 min 44 s), puis
  `python3 tools/normaliser.py livrables/reconstitution-accident-moto.mp4`. Images du MP4 vérifiées (0,5 / 5,5 / 11,5 / 14,2 / 18,6 / 22,5 s).

## Plan le plus faible

- 3–7 s : avec ≈ 31 m entre les deux deux-roues, ils sont petits à l'écran ; des cercles de repérage et les étiquettes
  A / B portent la lecture. La moto couchée vue de dessus reste une stylisation.
