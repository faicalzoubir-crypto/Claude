"""Modèle physique et scénario chiffré de la vidéo.

Toutes les valeurs affichées dans la vidéo viennent d'ici : les scènes
n'écrivent aucun chiffre en dur. Changer un paramètre ci-dessous puis
relancer `python rendre.py` régénère la vidéo, la voix off et les
sous-titres.
"""

from dataclasses import dataclass

# --- Paramètres physiques (valeurs usuelles) -------------------------------

TEMPS_REACTION = 1.0  # s, temps de réaction du conducteur
DECELERATION = {  # m/s², freinage d'urgence
    "sec": 7.0,
    "mouille": 5.0,
}
G = 9.81  # m/s², pesanteur
HAUTEUR_ETAGE = 3.0  # m, hauteur d'un étage

# --- Scénario ---------------------------------------------------------------

DISTANCE_TRAJET_KM = 10  # trajet comparé dans les scènes 2 et 3
VITESSES_VILLE = (40, 50)  # km/h (lente, rapide)
VITESSES_AUTOROUTE = (80, 120)  # km/h (lente, rapide)
VITESSE_SCHEMA = 50  # km/h, schéma de la scène 5 ...
VITESSE_SCHEMA_BIS = 80  # ... puis la même chose à cette vitesse
VITESSES_GRAPHIQUE = tuple(range(30, 131, 10))  # km/h, barres de la scène 6
VITESSES_CARRE = (40, 80)  # km/h, exemple « vitesse ×2 → freinage ×4 »
SECONDES_REELLES_PAR_SECONDE_VIDEO = 60  # chronos accélérés (1 s = 1 min)

LONGUEUR_VOITURE = 4.2  # m, pour dessiner les voitures à l'échelle
SECONDES_PAR_HEURE = 3600
METRES_PAR_KM = 1000


# --- Formules ---------------------------------------------------------------


def ms(v_kmh):
    """km/h → m/s."""
    return v_kmh * METRES_PAR_KM / SECONDES_PAR_HEURE


def kmh(v_ms):
    """m/s → km/h."""
    return v_ms * SECONDES_PAR_HEURE / METRES_PAR_KM


def temps_trajet(d_km, v_kmh):
    """Temps de trajet t = d / v, en secondes."""
    return d_km / v_kmh * SECONDES_PAR_HEURE


def secondes_par_km(v_kmh):
    """Temps passé sur chaque kilomètre : 3600 / v, en secondes."""
    return SECONDES_PAR_HEURE / v_kmh


def distance_reaction(v_kmh, t_reaction=TEMPS_REACTION):
    """DR = v × t_reaction (v en m/s), en mètres."""
    return ms(v_kmh) * t_reaction


def distance_freinage(v_kmh, sol="sec"):
    """DF = v² / (2a), en mètres."""
    return ms(v_kmh) ** 2 / (2 * DECELERATION[sol])


def distance_arret(v_kmh, sol="sec"):
    """DA = DR + DF, en mètres."""
    return distance_reaction(v_kmh) + distance_freinage(v_kmh, sol)


def duree_freinage(v_kmh, sol="sec"):
    """Durée du freinage jusqu'à l'arrêt, en secondes."""
    return ms(v_kmh) / DECELERATION[sol]


def vitesse_impact(v_kmh, d_obstacle, sol="sec"):
    """Vitesse (km/h) en heurtant un obstacle surgi à d_obstacle mètres.

    v_i² = v² − 2a(D − DR), 0 si la voiture s'arrête avant.
    Si l'obstacle est plus près que la distance de réaction, le choc a lieu
    à pleine vitesse.
    """
    v = ms(v_kmh)
    freinage_dispo = max(0.0, d_obstacle - distance_reaction(v_kmh))
    vi2 = v**2 - 2 * DECELERATION[sol] * freinage_dispo
    return kmh(vi2**0.5) if vi2 > 0 else 0.0


def hauteur_chute(v_kmh):
    """Hauteur de chute libre donnant la même vitesse : h = v² / (2g)."""
    return ms(v_kmh) ** 2 / (2 * G)


def etage(h):
    """Étage équivalent à une hauteur h (1 étage ≈ HAUTEUR_ETAGE m)."""
    return round(h / HAUTEUR_ETAGE)


# --- Mouvement (pour animer les voitures) -----------------------------------


def position_freinage(v_kmh, t, sol="sec"):
    """Distance parcourue t secondes après avoir perçu le danger (réaction
    puis freinage jusqu'à l'arrêt)."""
    v = ms(v_kmh)
    a = DECELERATION[sol]
    if t <= TEMPS_REACTION:
        return v * t
    tf = min(t - TEMPS_REACTION, v / a)
    return v * TEMPS_REACTION + v * tf - a * tf**2 / 2


def vitesse_freinage(v_kmh, t, sol="sec"):
    """Vitesse (km/h) t secondes après avoir perçu le danger."""
    if t <= TEMPS_REACTION:
        return v_kmh
    return max(0.0, kmh(ms(v_kmh) - DECELERATION[sol] * (t - TEMPS_REACTION)))


def instant_position(v_kmh, d, sol="sec"):
    """Instant (s après la perception) où la voiture a parcouru d mètres.
    Renvoie None si elle s'arrête avant."""
    v = ms(v_kmh)
    a = DECELERATION[sol]
    dr = distance_reaction(v_kmh)
    if d <= dr:
        return d / v
    disc = v**2 - 2 * a * (d - dr)
    if disc < 0:
        return None
    return TEMPS_REACTION + (v - disc**0.5) / a


# --- Scénario chiffré -------------------------------------------------------


@dataclass(frozen=True)
class Course:
    """Deux voitures sur le même trajet (scènes 2 et 3)."""

    lente: float
    rapide: float
    d_km: float = DISTANCE_TRAJET_KM

    @property
    def t_lente(self):
        return temps_trajet(self.d_km, self.lente)

    @property
    def t_rapide(self):
        return temps_trajet(self.d_km, self.rapide)

    @property
    def gain(self):
        return self.t_lente - self.t_rapide


@dataclass(frozen=True)
class Experience:
    """Obstacle surgissant à la distance d'arrêt de la voiture lente."""

    lente: float
    rapide: float
    sol: str = "sec"

    @property
    def d_obstacle(self):
        return distance_arret(self.lente, self.sol)

    @property
    def v_impact(self):
        return vitesse_impact(self.rapide, self.d_obstacle, self.sol)

    @property
    def t_impact(self):
        return instant_position(self.rapide, self.d_obstacle, self.sol)

    @property
    def t_arret_lente(self):
        return TEMPS_REACTION + duree_freinage(self.lente, self.sol)

    @property
    def h_chute(self):
        return hauteur_chute(self.v_impact)

    @property
    def etage(self):
        return etage(self.h_chute)


COURSE_VILLE = Course(*VITESSES_VILLE)
COURSE_AUTOROUTE = Course(*VITESSES_AUTOROUTE)
EXPERIENCE_VILLE = Experience(*VITESSES_VILLE)
EXPERIENCE_AUTOROUTE = Experience(*VITESSES_AUTOROUTE)
