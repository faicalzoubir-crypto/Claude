"""Charte graphique : couleurs, tailles de texte, cadre.

Vert = lent / sûr, rouge = rapide / danger, orange = réaction.
"""

FOND = "#0b0f17"
PANNEAU = "#151b26"
BLANC = "#f4f6fa"
GRIS = "#8e98aa"
GRIS_FONCE = "#3a4352"
ROUTE = "#252b35"
MARQUAGE = "#d5dbe4"
VERT = "#2fd47c"
ROUGE = "#ff4b5c"
ORANGE = "#ff9f1c"
JAUNE = "#ffd23f"
BLEU = "#4dabf7"
VITRE = "#1a2430"
NEUTRE = "#cfd6e0"  # véhicule du schéma (ni lent ni rapide)
TAILLE_MIN_VEHICULE = 0.9  # unités : longueur dessinée minimale d'un véhicule à l'échelle
ECHELLE_ICONE = {"moto": 1.45, "voiture": 1.0}  # une moto, plus fine, est dessinée plus grande

# Tailles de police (le cadre fait 16 × 9 unités en paysage, 9 × 16 en
# portrait : 1 unité = 120 px dans les deux cas).
TITRE = 60
TEXTE = 44
PETIT = 32
AXE = 30
CHIFFRE = 96
ENORME = 140

# Cadre logique
LARGEUR_PAYSAGE, HAUTEUR_PAYSAGE = 16, 9
MARGE = 0.55

# Durées communes
FONDU = 0.8
