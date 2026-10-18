"""Briques visuelles : textes Pango (aucun LaTeX), compteurs, axes,
voitures, silhouette d'enfant, immeuble, cotes, jauge."""

import textwrap

import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    MEDIUM,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    Arc,
    Axes,
    Circle,
    DashedLine,
    DecimalNumber,
    DoubleArrow,
    Ellipse,
    Line,
    MarkupText,
    NumberLine,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Text,
    VGroup,
    ManimColor,
    interpolate_color,
)

import style as S
from textes import Textes

T = Textes()


def melange(c1, c2, a):
    """Couleur entre c1 (a = 0) et c2 (a = 1)."""
    return interpolate_color(ManimColor(c1), ManimColor(c2), float(np.clip(a, 0, 1)))


def degrade(p):
    """Vert → jaune → rouge pour p de 0 à 1."""
    return melange(S.VERT, S.JAUNE, p * 2) if p < 0.5 else melange(S.JAUNE, S.ROUGE, p * 2 - 1)


# --- Textes -------------------------------------------------------------------


def _echapper(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _markup(s, graisse, taille):
    return MarkupText(_echapper(s) or " ", font=T.police, weight=graisse, font_size=taille)


def _couper(paragraphe, taille, graisse, largeur):
    """Coupe un paragraphe en lignes équilibrées qui tiennent dans `largeur`."""
    brut = paragraphe.replace("*", "")
    total = _markup(brut, graisse, taille).width if brut.strip() else 0
    if total <= largeur:
        return [paragraphe]
    n_lignes = int(np.ceil(total / largeur))
    while True:
        cible = int(np.ceil(len(paragraphe) / n_lignes)) + 2
        for n in range(cible, len(paragraphe) + 1):
            lignes = textwrap.wrap(paragraphe, n, break_long_words=False)
            if len(lignes) <= n_lignes:
                break
        if all(_markup(l.replace("*", ""), graisse, taille).width <= largeur for l in lignes):
            return lignes
        n_lignes += 1


def texte(
    s,
    taille=S.TEXTE,
    couleur=S.BLANC,
    graisse=BOLD,
    accents=(S.JAUNE,),
    largeur=None,
    alignement="centre",
    interligne=0.32,
):
    """Texte multi-ligne. *mot* = mot coloré (couleurs `accents` dans l'ordre),
    \\n = retour à la ligne, `largeur` = coupure automatique."""
    lignes = []
    for paragraphe in s.split("\n"):
        lignes += _couper(paragraphe, taille, graisse, largeur) if largeur else [paragraphe]

    groupe = VGroup()
    dedans, k = False, -1
    for ligne in lignes:
        markup = ""
        for i, morceau in enumerate(ligne.split("*")):
            if i > 0:
                dedans = not dedans
                k += dedans
            if not morceau:
                continue
            if dedans:
                c = accents[k % len(accents)]
                markup += f'<span foreground="{c}">{_echapper(morceau)}</span>'
            else:
                markup += _echapper(morceau)
        groupe.add(
            MarkupText(
                markup or " ", font=T.police, weight=graisse, font_size=taille, color=couleur
            )
        )
    if T.rtl and alignement != "centre":
        alignement = "gauche" if alignement == "droite" else "droite"
    bord = {"centre": ORIGIN, "gauche": LEFT, "droite": RIGHT}[alignement]
    groupe.arrange(DOWN, buff=interligne * taille / 48, aligned_edge=bord)
    return groupe


class NombreTexte(DecimalNumber):
    """DecimalNumber dont les chiffres sont un Text Pango (pas de LaTeX), avec
    le séparateur décimal de la langue et des chiffres à chasse fixe (ils ne
    sautent pas quand la valeur change). `formateur` : valeur → chaîne."""

    def __init__(self, number=0, num_decimal_places=0, formateur=None, graisse=BOLD, **kw):
        self.formateur = formateur
        self.graisse = graisse
        kw.setdefault("mob_class", Text)
        super().__init__(number, num_decimal_places=num_decimal_places, **kw)

    def _get_num_string(self, number):
        if self.formateur:
            return self.formateur(number)
        return T.nombre(number, self.num_decimal_places, self.include_sign)

    def _set_submobjects_from_number(self, number):
        self.number = number
        self.submobjects = []
        chaine = _echapper(self._get_num_string(number))
        mob = MarkupText(
            f'<span font_features="tnum">{chaine}</span>',
            font=T.police,
            weight=self.graisse,
            font_size=self._font_size,
        )
        self.add(*mob.submobjects)
        self.move_to(ORIGIN)
        self.initial_height = self.height


class AxeTexte(NumberLine):
    """NumberLine dont les graduations sont des NombreTexte (Text Pango)."""

    def __init__(self, *args, couleur_nombres=S.GRIS, **kw):
        self.couleur_nombres = couleur_nombres
        kw.setdefault("label_constructor", Text)
        super().__init__(*args, **kw)

    def get_number_mobject(
        self, x, direction=None, buff=None, font_size=None, label_constructor=None, **cfg
    ):
        cfg = {**self.decimal_number_config, **cfg}
        n = NombreTexte(
            x,
            num_decimal_places=cfg.get("num_decimal_places", 0),
            font_size=font_size or self.font_size,
            graisse=MEDIUM,
            color=self.couleur_nombres,
        )
        n.next_to(
            self.number_to_point(x),
            self.label_direction if direction is None else direction,
            buff=self.line_to_number_buff if buff is None else buff,
        )
        return n


class AxesTexte(Axes):
    """Axes construits avec AxeTexte."""

    def _create_axis(self, range_terms, axis_config, length):
        axis_config["length"] = length
        axe = AxeTexte(range_terms, **axis_config)
        axe.shift(-axe.number_to_point(self._origin_shift([axe.x_min, axe.x_max])))
        return axe


def pastille(s, couleur, taille=S.PETIT, fond=S.PANNEAU):
    """Étiquette arrondie (ex. « 40 km/h »)."""
    t = texte(s, taille=taille, couleur=couleur)
    cadre = RoundedRectangle(
        width=t.width + 0.5,
        height=t.height + 0.32,
        corner_radius=0.18,
        fill_color=fond,
        fill_opacity=1,
        stroke_color=couleur,
        stroke_width=3,
    ).move_to(t)
    return VGroup(cadre, t)


# --- Repère d'une route (paysage : vers la droite, portrait : vers le haut) --


class Repere:
    """s = distance le long de la route (m), lat = décalage en travers (unités)."""

    def __init__(self, origine, vertical, echelle):
        self.o = np.array(origine, dtype=float)
        self.vertical = vertical
        self.u = UP if vertical else RIGHT
        self.n = LEFT if vertical else UP
        self.angle = PI / 2 if vertical else 0
        self.k = echelle

    def p(self, s=0.0, lat=0.0):
        return self.o + self.u * s * self.k + self.n * lat


# --- Objets ---------------------------------------------------------------------


def _rect(l, h, c, r=0.0, **kw):
    if r:
        return RoundedRectangle(
            width=l, height=h, corner_radius=r, fill_color=c, fill_opacity=1, stroke_width=0, **kw
        )
    return Rectangle(width=l, height=h, fill_color=c, fill_opacity=1, stroke_width=0, **kw)


class Voiture(VGroup):
    """Voiture vue de dessus, avant vers +x, longueur L (unités)."""

    def __init__(self, couleur, L=1.6):
        super().__init__()
        self.L = L
        sombre = melange(couleur, "#000000", 0.35)
        roues = VGroup(
            *[
                _rect(0.2 * L, 0.07 * L, "#07090d", r=0.02 * L).move_to(
                    [sx * 0.29 * L, sy * 0.225 * L, 0]
                )
                for sx in (-1, 1)
                for sy in (-1, 1)
            ]
        )
        caisse = _rect(L, 0.46 * L, couleur, r=0.11 * L).set_stroke("#05070a", width=3)
        retros = VGroup(
            *[
                Ellipse(width=0.07 * L, height=0.05 * L, fill_color=sombre, fill_opacity=1, stroke_width=0).move_to(
                    [0.12 * L, sy * 0.245 * L, 0]
                )
                for sy in (-1, 1)
            ]
        )
        toit = _rect(0.3 * L, 0.36 * L, sombre, r=0.04 * L).shift(LEFT * 0.05 * L)
        pare_brise = Polygon(
            [0.10 * L, 0.18 * L, 0],
            [0.25 * L, 0.15 * L, 0],
            [0.25 * L, -0.15 * L, 0],
            [0.10 * L, -0.18 * L, 0],
            fill_color=S.VITRE,
            fill_opacity=1,
            stroke_width=0,
        )
        lunette = Polygon(
            [-0.20 * L, 0.18 * L, 0],
            [-0.31 * L, 0.15 * L, 0],
            [-0.31 * L, -0.15 * L, 0],
            [-0.20 * L, -0.18 * L, 0],
            fill_color=S.VITRE,
            fill_opacity=1,
            stroke_width=0,
        )
        phares = VGroup(
            *[_rect(0.035 * L, 0.09 * L, "#fff4cc", r=0.01 * L).move_to([0.475 * L, sy * 0.15 * L, 0]) for sy in (-1, 1)]
        )
        self.feux = VGroup(
            *[_rect(0.03 * L, 0.09 * L, "#6b0f17", r=0.01 * L).move_to([-0.48 * L, sy * 0.15 * L, 0]) for sy in (-1, 1)]
        )
        self.add(roues, retros, caisse, toit, pare_brise, lunette, phares, self.feux)

    def freine(self, oui=True):
        self.feux.set_fill("#ff2a2a" if oui else "#6b0f17")
        return self


def placer_voiture(voiture, repere, s):
    """Place l'avant de la voiture à s mètres sur le repère."""
    voiture.move_to(repere.p(s) - repere.u * voiture.L / 2)


def enfant(h=1.0, couleur=S.JAUNE):
    """Silhouette d'enfant (pictogramme), pieds en bas, hauteur h."""
    c = dict(fill_color=couleur, fill_opacity=1, stroke_width=0)
    tete = Circle(radius=0.12 * h, **c).move_to([0, 0.87 * h, 0])
    corps = RoundedRectangle(width=0.32 * h, height=0.36 * h, corner_radius=0.08 * h, **c).move_to([0, 0.55 * h, 0])
    bras = VGroup(
        *[
            RoundedRectangle(width=0.08 * h, height=0.32 * h, corner_radius=0.04 * h, **c)
            .rotate(sx * 0.45)
            .move_to([sx * 0.22 * h, 0.55 * h, 0])
            for sx in (-1, 1)
        ]
    )
    jambes = VGroup(
        *[
            RoundedRectangle(width=0.11 * h, height=0.4 * h, corner_radius=0.05 * h, **c).move_to(
                [sx * 0.08 * h, 0.2 * h, 0]
            )
            for sx in (-1, 1)
        ]
    )
    g = VGroup(jambes, bras, corps, tete)
    g.shift(-g.get_bottom())
    return g


def barriere(longueur, epaisseur, n=6):
    """Barrière rayée rouge et blanc, posée en travers (verticale)."""
    bandes = VGroup(
        *[
            _rect(epaisseur, longueur / n, S.ROUGE if i % 2 else S.BLANC)
            for i in range(n)
        ]
    ).arrange(DOWN, buff=0)
    return bandes


def route(longueur, largeur, vertical=False, pointilles=True):
    """Route vue de dessus, centrée sur l'origine."""
    fond = _rect(longueur, largeur, S.ROUTE)
    bords = VGroup(
        *[
            Line([-longueur / 2, sy * largeur / 2 * 0.9, 0], [longueur / 2, sy * largeur / 2 * 0.9, 0], stroke_color=S.MARQUAGE, stroke_width=3, stroke_opacity=0.7)
            for sy in (-1, 1)
        ]
    )
    g = VGroup(fond, bords)
    if pointilles:
        g.add(
            DashedLine(
                [-longueur / 2, 0, 0],
                [longueur / 2, 0, 0],
                dash_length=0.35,
                dashed_ratio=0.5,
                stroke_color=S.MARQUAGE,
                stroke_width=2,
                stroke_opacity=0.25,
            )
        )
    if vertical:
        g.rotate(PI / 2)
    return g


def immeuble(niveaux, h_niveau, largeur=2.2):
    """Immeuble vu de face, `niveaux` niveaux (RDC = 0), sol en y = 0.
    `.niveaux[i]` = rangée de fenêtres du niveau i."""
    g = VGroup()
    corps = Rectangle(
        width=largeur, height=niveaux * h_niveau, fill_color=S.PANNEAU, fill_opacity=1, stroke_color=S.GRIS_FONCE, stroke_width=3
    ).move_to([0, niveaux * h_niveau / 2, 0])
    g.niveaux = VGroup()
    for i in range(niveaux):
        rang = VGroup(
            *[
                _rect(largeur * 0.18, h_niveau * 0.5, S.GRIS_FONCE).move_to(
                    [x * largeur * 0.28, (i + 0.5) * h_niveau, 0]
                )
                for x in (-1, 0, 1)
            ]
        )
        g.niveaux.add(rang)
    sol = Line([-largeur, 0, 0], [largeur, 0, 0], stroke_color=S.GRIS, stroke_width=4)
    g.add(corps, g.niveaux, sol)
    return g


def cote(a, b, s, couleur=S.BLANC, cote_vers=DOWN, taille=S.PETIT, decalage=0.32):
    """Cote de dimension entre les points a et b, texte du côté `cote_vers`."""
    a, b = np.array(a), np.array(b)
    u = (b - a) / max(np.linalg.norm(b - a), 1e-6)
    n = np.array([-u[1], u[0], 0])
    fleche = DoubleArrow(
        a, b, buff=0, stroke_width=3, color=couleur, tip_length=0.16, max_tip_length_to_length_ratio=0.3
    )
    traits = VGroup(
        *[Line(p - n * 0.18, p + n * 0.18, stroke_width=3, color=couleur) for p in (a, b)]
    )
    t = texte(s, taille=taille, couleur=couleur)
    t.next_to((a + b) / 2, cote_vers, buff=decalage * 0.5)
    return VGroup(fleche, traits, t)


def jauge(rayon=2.0, n=40):
    """Compteur de vitesse sans chiffres : arc vert → rouge."""
    debut, fin = 210 * PI / 180, -30 * PI / 180
    arcs = VGroup()
    for i in range(n):
        a0 = debut + (fin - debut) * i / n
        a1 = debut + (fin - debut) * (i + 1) / n
        x = i / (n - 1)
        arcs.add(Arc(radius=rayon, start_angle=a0, angle=a1 - a0, stroke_color=degrade(x), stroke_width=22))
    graduations = VGroup()
    for i in range(11):
        a = debut + (fin - debut) * i / 10
        d = np.array([np.cos(a), np.sin(a), 0])
        graduations.add(
            Line(d * rayon * 0.78, d * rayon * 0.88, stroke_color=S.GRIS, stroke_width=4)
        )
    centre = Circle(radius=0.14, fill_color=S.BLANC, fill_opacity=1, stroke_width=0)
    g = VGroup(arcs, graduations, centre)
    g.debut, g.fin, g.rayon = debut, fin, rayon
    return g


def aiguille(j, p):
    """Aiguille de la jauge j pour une proportion p (0 → 1)."""
    a = j.debut + (j.fin - j.debut) * p
    d = np.array([np.cos(a), np.sin(a), 0])
    n = np.array([-d[1], d[0], 0])
    c0 = j[2].get_center()
    couleur = degrade(p)
    return Polygon(
        c0 + n * 0.08,
        c0 + d * j.rayon * 0.92,
        c0 - n * 0.08,
        c0 - d * 0.25,
        fill_color=couleur,
        fill_opacity=1,
        stroke_width=0,
    )


def damier(hauteur, n=6):
    """Ligne d'arrivée à damier, posée en travers de la route."""
    c = hauteur / n
    return VGroup(
        *[
            _rect(c, c, S.BLANC if (i + j) % 2 else "#111111").move_to([(i - 0.5) * c, (j - (n - 1) / 2) * c, 0])
            for i in range(2)
            for j in range(n)
        ]
    )


def dans_cadre(m, largeur, hauteur, marge=S.MARGE):
    """Décale m pour qu'il reste dans le cadre."""
    dx = max(0, -largeur / 2 + marge - m.get_left()[0]) - max(0, m.get_right()[0] - largeur / 2 + marge)
    dy = max(0, -hauteur / 2 + marge - m.get_bottom()[1]) - max(0, m.get_top()[1] - hauteur / 2 + marge)
    return m.shift([dx, dy, 0])
