"""« La vitesse au volant » : les 8 scènes (Manim Community Edition).

Une classe par scène ; rendre.py les rend puis les assemble. Aucune valeur
physique n'est écrite ici : tout vient de physique.py, mis en mots par
textes.py à partir de textes_<langue>.json. Chaque scène note l'instant de
ses répliques (self.dire) pour caler voix off et sous-titres.
"""

import json
import os
import re
from pathlib import Path

import numpy as np
from manim import *  # noqa: F403

import physique as P
import style as S
from composants import (
    AxesTexte,
    NombreTexte,
    Repere,
    T,
    aiguille,
    barriere,
    cote,
    damier,
    dans_cadre,
    degrade,
    enfant,
    immeuble,
    jauge,
    pastille,
    placer_vehicule,
    route,
    texte,
    vehicule,
)
from textes import DOSSIER, VERSION, valeurs

PORTRAIT = config.pixel_height > config.pixel_width
if PORTRAIT:
    config.frame_width, config.frame_height = S.HAUTEUR_PAYSAGE, S.LARGEUR_PAYSAGE
else:
    config.frame_width, config.frame_height = S.LARGEUR_PAYSAGE, S.HAUTEUR_PAYSAGE
config.background_color = S.FOND
W, H = config.frame_width, config.frame_height
XMAX, YMAX = W / 2 - S.MARGE, H / 2 - S.MARGE
V = valeurs(T)
SIGNATURE = DOSSIER / "assets" / "signature.png"
COURT = VERSION == "courte"  # version de 90 s
FONDU = 0.5 if COURT else S.FONDU


def selon(longue, courte):
    """Valeur (durée, instant, réplique…) selon la version rendue."""
    return courte if COURT else longue


class SceneVitesse(Scene):
    ID = ""

    def setup(self):
        self.reperes = []
        self.evenements = []

    def e(self, cle, scene=None, **kw):
        """Texte écran de la scène, valeurs insérées."""
        scene = scene or self.ID
        return T.ecran(f"{scene.rstrip('b')}.{cle}", **{**V[scene], **kw})

    def dire(self, cle, scene=None):
        """Début d'une réplique de narration (voix off + sous-titre)."""
        self.reperes.append(
            {"scene": scene or self.ID, "cle": cle, "t": round(self.renderer.time, 3)}
        )

    def marquer(self, nom):
        """Moment clé pour la musique (départ, choc, carton…)."""
        self.evenements.append({"nom": nom, "t": round(self.renderer.time, 3)})

    def maintenant(self):
        return self.renderer.time

    def jusqua(self, t):
        """Attend jusqu'à l'instant t de la scène."""
        if t - self.maintenant() > 1 / config.frame_rate:
            self.wait(t - self.maintenant())

    def derouler(self, tracker, cible, duree, reperes=()):
        """Fait avancer `tracker` linéairement jusqu'à `cible` en `duree` s,
        en lançant les répliques (instant de scène, clé) au passage."""
        debut, v0 = self.maintenant(), tracker.get_value()
        pente = (cible - v0) / duree
        for t, cle in sorted(reperes):
            if t > self.maintenant() + 1e-3 and t < debut + duree:
                self.play(
                    tracker.animate.set_value(v0 + pente * (t - debut)),
                    run_time=t - self.maintenant(),
                    rate_func=linear,
                )
            self.dire(cle)
        reste = debut + duree - self.maintenant()
        if reste > 1e-3:
            self.play(tracker.animate.set_value(cible), run_time=reste, rate_func=linear)
        tracker.set_value(cible)

    def titre(self, s):
        return texte(s, taille=S.TITRE, largeur=2 * XMAX).to_edge(UP, buff=S.MARGE)

    def vider(self, run_time=FONDU):
        for m in self.mobjects:
            m.clear_updaters()
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)

    def tear_down(self):
        dossier = Path(os.environ.get("VITESSE_REPERES", DOSSIER / "build" / "reperes"))
        dossier.mkdir(parents=True, exist_ok=True)
        (dossier / f"{type(self).__name__}.json").write_text(
            json.dumps(
                {"duree": round(self.renderer.time, 3), "reperes": self.reperes, "evenements": self.evenements},
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )


# --- 1. Accroche --------------------------------------------------------------


class S1Accroche(SceneVitesse):
    ID = "s1"

    def construct(self):
        j = jauge(rayon=2.0 if PORTRAIT else 1.85)
        l1 = texte(self.e("ligne1"), taille=S.TITRE + (4 if PORTRAIT else 16), largeur=2 * XMAX)
        l2 = texte(self.e("ligne2"), taille=S.TEXTE + 6, graisse=SEMIBOLD, largeur=2 * XMAX)
        VGroup(j, l1, l2).arrange(DOWN, buff=0.6 if PORTRAIT else 0.45).move_to(ORIGIN)
        p = ValueTracker(0.0)
        aig = always_redraw(lambda: aiguille(j, p.get_value()))

        self.dire("accroche")
        self.play(FadeIn(j, scale=0.92), FadeIn(aig), run_time=selon(0.6, 0.4))
        self.marquer("aiguille")
        self.play(
            p.animate.set_value(0.95),
            FadeIn(l1, shift=UP * 0.3),
            run_time=selon(2.2, 1.4),
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.jusqua(selon(3.6, 1.9))
        self.marquer("question")
        self.play(FadeIn(l2, shift=UP * 0.3), run_time=selon(0.9, 0.6))
        self.jusqua(selon(6.4, 2.6))
        if not COURT:
            self.dire("calcul")
        self.play(Circumscribe(l2, color=S.JAUNE, buff=0.2, time_width=0.5), run_time=selon(1.6, 1.2))
        self.jusqua(selon(9.2, 4.5))
        self.vider()


# --- 2 et 3. Courses ------------------------------------------------------------


class SceneCourse(SceneVitesse):
    COURSE = None

    def course(self, t_depart, reperes_course, arrivees=("rapide", "lente")):
        """Deux voitures sur le même trajet, chronos accélérés. Renvoie les
        objets affichés (hors titre) et le titre."""
        c = self.COURSE
        k = P.SECONDES_REELLES_PAR_SECONDE_VIDEO[VERSION]
        titre = self.titre(self.e("titre"))
        sous = texte(self.e("trajet"), taille=S.TEXTE - 6, couleur=S.GRIS, graisse=MEDIUM)
        sous.next_to(titre, DOWN, buff=0.22)

        pastilles = [pastille(T.vitesse(v), coul, taille=S.TEXTE - 2) for v, coul in ((c.lente, S.VERT), (c.rapide, S.ROUGE))]
        l_chrono = NombreTexte(0, formateur=T.chrono, font_size=S.CHIFFRE - 34).width + 0.4
        if PORTRAIT:
            x0, x1, ys, lv, larg = -XMAX, XMAX, (2.3, -1.3), 1.15, 1.15
        else:
            x0 = -XMAX + max(p.width for p in pastilles) + 0.25
            x1 = XMAX - l_chrono - 0.3
            ys, lv, larg = (0.75, -1.25), 1.35, 1.2
        lv *= S.ECHELLE_ICONE[P.VEHICULE]
        x_dep, x_arr = x0 + lv + 0.2, x1 - 0.45
        temps = ValueTracker(0.0)  # secondes réelles
        voies, chronos = VGroup(), []
        for pas, couleur, y, t_fin in (
            (pastilles[0], S.VERT, ys[0], c.t_lente),
            (pastilles[1], S.ROUGE, ys[1], c.t_rapide),
        ):
            r = route(x1 - x0, larg).move_to([(x0 + x1) / 2, y, 0])
            depart = Line(
                [x_dep, y - larg * 0.45, 0], [x_dep, y + larg * 0.45, 0], stroke_color=S.MARQUAGE, stroke_width=4
            )
            arrivee = damier(larg * 0.9).move_to([x_arr + 0.1, y, 0])
            voiture = vehicule(couleur, lv)

            def suivre(m, y=y, t_fin=t_fin):
                f = min(1.0, temps.get_value() / t_fin)
                m.move_to([x_dep + f * (x_arr - x_dep) - lv / 2, y, 0])

            voiture.add_updater(suivre)
            suivre(voiture)
            chrono = NombreTexte(0, formateur=T.chrono, font_size=S.CHIFFRE - 34)
            cadre = SurroundingRectangle(
                chrono, buff=0.2, corner_radius=0.16, stroke_color=S.GRIS_FONCE, stroke_width=3,
                fill_color=S.PANNEAU, fill_opacity=1,
            )
            boite = VGroup(cadre, chrono)
            if PORTRAIT:
                pas.next_to(r, UP, buff=0.22).align_to(r, LEFT)
                boite.next_to(r, UP, buff=0.22).align_to(r, RIGHT)
            else:
                pas.next_to(r, LEFT, buff=0.22)
                boite.next_to(r, RIGHT, buff=0.3)
            chrono.add_updater(lambda m, t_fin=t_fin: m.set_value(min(temps.get_value(), t_fin)))
            voies.add(VGroup(r, depart, arrivee, pas, boite, voiture))
            chronos.append((boite, couleur, t_fin))

        accelere = texte(self.e("accelere"), taille=S.PETIT, couleur=S.GRIS, graisse=MEDIUM)
        gain = texte(self.e("gain"), taille=S.TITRE + 10)
        if PORTRAIT:
            accelere.move_to([0, -3.4, 0])
            gain.move_to([0, -4.6, 0])
        else:
            accelere.next_to(voies, DOWN, buff=0.45)
            gain.next_to(voies, DOWN, buff=0.55)

        self.dire("trajet")
        self.play(FadeIn(titre, shift=DOWN * 0.2), FadeIn(sous), run_time=selon(0.7, 0.45))
        self.play(LaggedStart(*[FadeIn(v, shift=RIGHT * 0.3) for v in voies], lag_ratio=0.35), run_time=selon(1.3, 0.6))
        for t, cle in [r for r in reperes_course if r[0] < t_depart]:
            self.jusqua(t)
            self.dire(cle)
        reperes_course = [r for r in reperes_course if r[0] >= t_depart]
        self.jusqua(t_depart - 0.6)
        self.play(FadeIn(accelere), run_time=selon(0.5, 0.3))
        self.jusqua(t_depart)

        # Course : le tracker avance en secondes réelles, k fois plus vite.
        (b_lente, c_lente, _), (b_rapide, c_rapide, _) = chronos
        self.marquer("depart")
        self.derouler(temps, c.t_rapide, c.t_rapide / k, reperes_course)
        self.marquer("arrivee_rapide")
        if arrivees[0]:
            self.dire(arrivees[0])
        b_rapide[1].clear_updaters()
        b_rapide[1].set_value(c.t_rapide)
        self.play(
            AnimationGroup(
                temps.animate(rate_func=linear).set_value(c.t_lente),
                b_rapide[0].animate(run_time=0.3).set_stroke(c_rapide, width=6),
                Indicate(b_rapide[1], scale_factor=1.15, color=c_rapide, run_time=selon(0.8, 0.6)),
            ),
            run_time=(c.t_lente - c.t_rapide) / k,
        )
        self.marquer("arrivee_lente")
        if arrivees[1]:
            self.dire(arrivees[1])
        b_lente[1].clear_updaters()
        b_lente[1].set_value(c.t_lente)
        for v in voies:
            v[-1].clear_updaters()
        self.play(
            b_lente[0].animate.set_stroke(c_lente, width=6),
            Indicate(b_lente[1], scale_factor=1.15, color=c_lente),
            run_time=selon(0.8, 0.6),
        )
        if not COURT:
            self.wait(0.6)
        self.marquer("gain")
        self.dire("gain")
        self.play(FadeOut(accelere), FadeIn(gain, scale=0.8), run_time=selon(0.7, 0.5))
        return VGroup(sous, voies, gain), titre


class S2Ville(SceneCourse):
    ID = "s2"
    COURSE = P.COURSE_VILLE

    def construct(self):
        self.course(
            t_depart=selon(5.0, 1.2),
            reperes_course=selon([(3.2, "vitesses"), (6.6, "accelere")], [(3.6, "accelere")]),
            arrivees=selon(("rapide", "lente"), (None, None)),
        )
        self.jusqua(selon(24.2, 10.9))
        self.vider()


class S3Autoroute(SceneCourse):
    ID = "s3"
    COURSE = P.COURSE_AUTOROUTE

    def construct(self):
        objets, titre = self.course(
            t_depart=selon(4.6, 1.2), reperes_course=[], arrivees=selon(("temps", None), (None, None))
        )
        if COURT:  # le bilan passe dans la scène suivante
            self.jusqua(8.6)
            self.vider()
            return
        self.jusqua(14.8)
        lignes = VGroup(
            texte(self.e("bilan_ville"), taille=S.TEXTE + 4, largeur=2 * XMAX, accents=(S.VERT,)),
            texte(self.e("bilan_autoroute"), taille=S.TEXTE + 4, largeur=2 * XMAX, accents=(S.ROUGE,)),
        ).arrange(DOWN, buff=0.7 if PORTRAIT else 0.55)
        lignes.move_to(DOWN * 0.3)
        nouveau_titre = self.titre(self.e("bilan_titre"))
        self.marquer("bilan")
        self.play(FadeOut(objets, shift=DOWN * 0.3), Transform(titre, nouveau_titre), run_time=0.7)
        self.dire("paradoxe")
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in lignes], lag_ratio=0.5), run_time=1.6)
        self.jusqua(18.5)
        self.play(Indicate(lignes[0], scale_factor=1.06, color=S.JAUNE), run_time=1.2)
        self.jusqua(24.2)
        self.vider()


# --- 4. Le paradoxe ---------------------------------------------------------------


class S4Paradoxe(SceneVitesse):
    ID = "s4"

    def construct(self):
        spk = P.secondes_par_km
        vs = P.VITESSES_GRAPHIQUE
        pas_v = vs[1] - vs[0]
        pas_y = 30 if spk(vs[0]) > 60 else 10
        y_max = np.ceil(spk(vs[0]) / pas_y) * pas_y
        titre = self.titre(self.e("titre"))
        formule = texte(self.e("formule"), taille=S.PETIT, couleur=S.GRIS, graisse=MEDIUM)
        formule.next_to(titre, DOWN, buff=0.18)

        axes = AxesTexte(
            x_range=[vs[0], vs[-1], pas_v],
            y_range=[0, y_max, pas_y],
            x_length=6.8 if PORTRAIT else 6.4,
            y_length=5.0 if PORTRAIT else 4.7,
            axis_config=dict(include_tip=False, color=S.GRIS, stroke_width=3, font_size=S.AXE),
            x_axis_config=dict(include_numbers=True, numbers_to_include=list(vs[1::2])),
            y_axis_config=dict(
                include_numbers=True, numbers_to_include=list(np.arange(pas_y, y_max + 1, pas_y))
            ),
        )
        if PORTRAIT:
            axes.move_to([0.45, 1.2, 0])
        else:
            axes.move_to([-3.6, -0.45, 0])
        lab_x = texte(self.e("axe_x"), taille=S.AXE - 2, couleur=S.GRIS, graisse=MEDIUM)
        lab_x.next_to(axes.x_axis, DOWN, buff=0.55).align_to(axes.x_axis, RIGHT)
        lab_y = texte(self.e("axe_y"), taille=S.AXE - 2, couleur=S.GRIS, graisse=MEDIUM)
        lab_y.next_to(axes.y_axis, UP, buff=0.2).align_to(axes.y_axis, LEFT).shift(LEFT * 0.4)
        grille = VGroup(
            *[
                DashedLine(axes.c2p(vs[0], y), axes.c2p(vs[-1], y), stroke_color=S.GRIS_FONCE, stroke_width=1.5, dash_length=0.08)
                for y in np.arange(pas_y, y_max + 1, pas_y)
            ]
        )
        courbe = axes.plot(spk, x_range=[vs[0], vs[-1]], stroke_width=7)
        courbe.set_stroke(color=[S.ROUGE, S.JAUNE, S.VERT])  # dégradé dans l'ordre inverse des points

        def marche(v1, v2):
            p1, p2 = axes.c2p(v1, spk(v1)), axes.c2p(v2, spk(v2))
            coin = axes.c2p(v2, spk(v1))
            fr = lambda v: (v - vs[0]) / (vs[-1] - vs[0])  # noqa: E731
            points = VGroup(
                Dot(p1, radius=0.11, color=degrade(fr(v1))), Dot(p2, radius=0.11, color=degrade(fr(v2)))
            )
            horiz = DashedLine(p1, coin, stroke_color=S.BLANC, stroke_width=3, dash_length=0.1)
            dv = texte(T.format("vitesse", v=T.nombre(v2 - v1, signe=True)), taille=S.AXE - 4, couleur=S.BLANC, graisse=MEDIUM)
            dv.next_to(horiz, UP, buff=0.12).align_to(horiz, LEFT)
            fleche = Arrow(coin, p2, buff=0, color=S.JAUNE, stroke_width=7, max_tip_length_to_length_ratio=0.35, max_stroke_width_to_length_ratio=12)
            return points, horiz, dv, fleche

        def bloc(v1, v2):
            haut = texte(T.format("intervalle", a=T.nombre(v1), b=T.vitesse(v2)), taille=S.PETIT, couleur=S.GRIS, graisse=MEDIUM)
            bas = texte(T.s_par_km(spk(v2) - spk(v1)), taille=S.CHIFFRE - 36, couleur=S.JAUNE)
            if PORTRAIT:
                return VGroup(haut, bas).arrange(DOWN, buff=0.12)
            return VGroup(haut, bas).arrange(RIGHT, buff=0.35)

        (va, vb), (vc, vd) = P.VITESSES_VILLE, P.VITESSES_AUTOROUTE
        m1, m2 = marche(va, vb), marche(vc, vd)
        b1, b2 = bloc(va, vb), bloc(vc, vd)
        message = texte(self.e("message"), taille=S.TEXTE - 6, largeur=2 * XMAX if PORTRAIT else 6.9, interligne=0.25)
        note = texte(self.e("note"), taille=S.PETIT - 4, couleur=S.GRIS, graisse=MEDIUM, largeur=2 * XMAX if PORTRAIT else 6.9)
        if PORTRAIT:
            VGroup(b1, b2).arrange(RIGHT, buff=0.8).move_to([0, -3.4, 0])
            message.move_to([0, -5.15, 0])
            note.next_to(message, DOWN, buff=0.4)
        else:
            formule.move_to([3.95, 2.8, 0])
            col = VGroup(b1, b2).arrange(DOWN, buff=0.35)
            for b in col:
                b.align_to(col, RIGHT)
            col.move_to([3.95, 1.45, 0])
            message.move_to([3.95, -1.0, 0])
            note.next_to(message, DOWN, buff=0.4)

        self.dire("pourquoi")
        self.play(FadeIn(titre, shift=DOWN * 0.2), FadeIn(formule), run_time=selon(0.8, 0.5))
        self.play(Create(axes), FadeIn(lab_x), FadeIn(lab_y), FadeIn(grille), run_time=selon(1.4, 0.8))
        self.play(Create(courbe), run_time=selon(2.0, 1.0))
        for (m, b, t, cle) in ((m1, b1, selon(4.6, 2.4), "ville"), (m2, b2, selon(9.0, 3.9), "autoroute")):
            self.jusqua(t)
            self.marquer("marche")
            if not COURT:
                self.dire(cle)
            self.play(FadeIn(m[0], scale=0.5), run_time=selon(0.5, 0.3))
            self.play(Create(m[1]), FadeIn(m[2]), run_time=selon(0.7, 0.4))
            self.play(GrowArrow(m[3]), FadeIn(b, shift=LEFT * 0.3), run_time=selon(0.8, 0.5))
        self.jusqua(selon(13.0, 5.3))
        self.marquer("message")
        self.dire("message")
        self.play(FadeIn(message, shift=UP * 0.2), run_time=selon(0.8, 0.5))
        if not COURT:
            self.jusqua(18.2)
            self.dire("note")
            self.play(FadeIn(note), run_time=0.8)
        self.jusqua(selon(24.2, 11.0))
        self.vider()


# --- 5. Schéma de la distance d'arrêt --------------------------------------------


class S5Schema(SceneVitesse):
    ID = "s5"

    def construct(self):
        v1, v2 = P.VITESSE_SCHEMA, P.VITESSE_SCHEMA_BIS
        s_obs = P.distance_arret(v2) * 1.05  # barrière juste après l'arrêt le plus long
        larg = 1.5
        titre = self.titre(self.e("titre"))
        if PORTRAIT:
            o = np.array([0.0, -4.4, 0])
            haut = titre.get_bottom()[1] - 0.4
            rep = Repere(o, True, (haut - 0.6 - o[1]) / s_obs)
            s_min, s_max = (-H / 2 - o[1]) / rep.k, (haut - o[1]) / rep.k
        else:
            o = np.array([-5.6, 0.25, 0])
            rep = Repere(o, False, (XMAX - 0.5 - o[0]) / s_obs)
            s_min, s_max = (-W / 2 - o[0]) / rep.k, (W / 2 - o[0]) / rep.k
        lm = max(P.LONGUEUR_VEHICULE * rep.k, S.TAILLE_MIN_VEHICULE * S.ECHELLE_ICONE[P.VEHICULE]) / rep.k  # longueur dessinée (m)
        a, b = rep.p(s_min), rep.p(s_max)
        r = route(np.linalg.norm(b - a), larg, vertical=PORTRAIT).move_to((a + b) / 2)
        obs = barriere(larg * 0.85, 0.22).rotate(rep.angle).move_to(rep.p(s_obs) + rep.u * 0.15)
        ligne_danger = DashedLine(
            rep.p(0, larg / 2 + 0.15), rep.p(0, -larg / 2 - 0.15), stroke_color=S.JAUNE, stroke_width=4, dash_length=0.12
        )
        danger = pastille(self.e("danger"), S.JAUNE, taille=S.PETIT)
        if PORTRAIT:
            danger.next_to(rep.p(-lm, 0), DOWN, buff=0.45)
        else:
            danger.next_to(rep.p(0, larg / 2), UP, buff=1.0)
        dans_cadre(danger, W, H)
        ralenti = texte(self.e("ralenti"), taille=S.PETIT - 4, couleur=S.GRIS, graisse=MEDIUM)
        ralenti.to_corner(DL if PORTRAIT else DR, buff=S.MARGE)
        formule = texte(self.e("formule"), taille=S.TEXTE - 4, accents=(S.ORANGE, S.ROUGE), largeur=2 * XMAX)
        formule.to_edge(DOWN, buff=S.MARGE + 0.1)

        t = ValueTracker(-selon(1.2, 0.8))  # s après la perception du danger
        etat = {"v": v1}
        voiture = vehicule(S.NEUTRE, lm * rep.k).rotate(rep.angle)

        def s_voiture():
            tt = t.get_value()
            return P.ms(etat["v"]) * tt if tt < 0 else P.position_freinage(etat["v"], tt)

        def suivre(m):
            placer_vehicule(m, rep, s_voiture())
            m.freine(t.get_value() > P.TEMPS_REACTION)

        voiture.add_updater(suivre)
        suivre(voiture)

        def zone(sa, sb, couleur):
            if sb - sa < 1e-3:
                return VectorizedPoint(rep.p(sa))
            return Polygon(
                rep.p(sa, larg * 0.42), rep.p(sb, larg * 0.42), rep.p(sb, -larg * 0.42), rep.p(sa, -larg * 0.42),
                fill_color=couleur, fill_opacity=0.72, stroke_width=0,
            )

        def dr():
            return P.distance_reaction(etat["v"])

        z_r = always_redraw(lambda: zone(0, max(0, min(s_voiture(), dr())), S.ORANGE))
        z_f = always_redraw(lambda: zone(dr(), max(dr(), s_voiture()), S.ROUGE))
        compteur = NombreTexte(v1, formateur=T.vitesse, font_size=S.PETIT + 4)

        def suivre_compteur(m):
            m.set_value(P.vitesse_freinage(etat["v"], max(0.0, t.get_value())))
            m.next_to(rep.p(s_voiture() - lm / 2, larg / 2), rep.n, buff=0.2)

        compteur.add_updater(suivre_compteur)
        suivre_compteur(compteur)

        def etiquettes(v):
            """Noms des zones avec leurs cotes, puis la cote totale."""
            d_r, d_f, d_a = P.distance_reaction(v), P.distance_freinage(v), P.distance_arret(v)
            if PORTRAIT:
                # Zones et longueurs à droite de la route, total à gauche.
                lat = -larg / 2 - 0.35
                c_r = cote(rep.p(0, lat), rep.p(d_r, lat), "", S.ORANGE)
                c_f = cote(rep.p(d_r, lat), rep.p(d_a, lat), "", S.ROUGE)
                n_r = texte(f"{self.e('reaction')}\n{T.metres(d_r)}", taille=S.PETIT - 4, couleur=S.ORANGE, alignement="gauche")
                n_f = texte(f"{self.e('freinage')}\n{T.metres(d_f)}", taille=S.PETIT - 4, couleur=S.ROUGE, alignement="gauche")
                n_r.next_to(rep.p(d_r / 2, lat), RIGHT, buff=0.3)
                n_f.next_to(rep.p((d_r + d_a) / 2, lat), RIGHT, buff=0.3)
                lat_t = larg / 2 + 0.35
                c_t = cote(rep.p(0, lat_t), rep.p(d_a, lat_t), "", S.BLANC)
                n_t = texte(re.sub(r":\s*", ":\n", self.e("total", d=T.metres(d_a)), count=1), taille=S.TEXTE - 6, alignement="droite")
                n_t.next_to(rep.p(d_a / 2, lat_t), LEFT, buff=0.3)
                return VGroup(n_r, n_f), VGroup(c_r, c_f), VGroup(c_t, n_t)
            n_r = texte(self.e("reaction"), taille=S.PETIT - 2, couleur=S.ORANGE)
            n_f = texte(self.e("freinage"), taille=S.PETIT - 2, couleur=S.ROUGE)
            n_r.next_to(rep.p(d_r / 2, larg / 2), UP, buff=0.22)
            n_f.next_to(rep.p((d_r + d_a) / 2, larg / 2), UP, buff=0.22)
            lat = -larg / 2 - 0.4
            c_r = cote(rep.p(0, lat), rep.p(d_r, lat), T.metres(d_r), S.ORANGE)
            c_f = cote(rep.p(d_r, lat), rep.p(d_a, lat), T.metres(d_f), S.ROUGE)
            lat_t = lat - 1.15
            c_t = cote(rep.p(0, lat_t), rep.p(d_a, lat_t), self.e("total", d=T.metres(d_a)), S.BLANC, taille=S.TEXTE - 4)
            return VGroup(n_r, n_f), VGroup(c_r, c_f), c_t

        # Mise en place
        self.dire("prix")
        self.play(FadeIn(titre, shift=DOWN * 0.2), run_time=selon(0.7, 0.5))
        self.play(FadeIn(r), FadeIn(obs), run_time=selon(0.8, 0.5))
        self.add(z_r, z_f, voiture, compteur)
        self.jusqua(selon(2.6, 1.0))
        # Approche à vitesse réelle, puis arrêt sur image : danger !
        self.marquer("approche")
        self.derouler(t, 0.0, -t.get_value())
        self.marquer("danger")
        if not COURT:
            self.dire("danger")
        self.play(Create(ligne_danger), FadeIn(danger, scale=0.7), run_time=selon(0.5, 0.3))
        self.jusqua(selon(5.8, 2.6))
        # Réaction (ralenti ×4, ou ×2 en version courte) puis freinage (ralenti ×1,5 ou ×1,2).
        self.play(FadeIn(ralenti), run_time=0.3)
        self.dire("reaction")
        self.marquer("reaction")
        self.derouler(t, P.TEMPS_REACTION, selon(4.0, 2.0) * P.TEMPS_REACTION)
        self.marquer("freinage")
        if not COURT:
            self.dire("freinage")
        self.derouler(t, P.TEMPS_REACTION + P.duree_freinage(v1), selon(1.5, 1.2) * P.duree_freinage(v1))
        self.marquer("arret")
        self.play(FadeOut(ralenti), FadeOut(compteur), run_time=selon(0.4, 0.3))
        noms, cotes, total = etiquettes(v1)
        self.marquer("bilan")
        self.dire("bilan")
        self.play(FadeIn(noms), LaggedStart(*[FadeIn(c) for c in cotes], lag_ratio=0.4), run_time=selon(1.0, 0.7))
        self.play(FadeIn(total, shift=-rep.n * 0.2), run_time=selon(0.6, 0.4))
        if PORTRAIT:
            self.play(FadeOut(danger), run_time=0.3)
        self.play(FadeIn(formule, shift=UP * 0.2), run_time=selon(0.7, 0.5))
        if COURT:  # pas de reprise à la seconde vitesse
            self.jusqua(10.9)
            self.vider()
            return
        self.jusqua(19.4)

        # Même chose à v2, en temps réel.
        et_a = texte(self.e("et_a"), taille=S.TEXTE, couleur=S.JAUNE).move_to(formule)
        self.play(FadeOut(noms), FadeOut(cotes), FadeOut(total), FadeOut(formule), FadeIn(et_a), run_time=0.6)
        etat["v"] = v2
        t.set_value(-0.6)
        compteur.set_value(v2)
        suivre_compteur(compteur)
        self.play(FadeIn(compteur), run_time=0.2)
        self.marquer("reprise")
        self.derouler(t, P.TEMPS_REACTION + P.duree_freinage(v2), 0.6 + P.TEMPS_REACTION + P.duree_freinage(v2))
        self.marquer("arret")
        noms, cotes, total = etiquettes(v2)
        self.dire("et_a")
        self.play(FadeOut(compteur), FadeIn(noms), FadeIn(cotes), run_time=0.7)
        self.play(FadeIn(total, shift=-rep.n * 0.2), run_time=0.6)
        self.jusqua(27.4)
        self.vider()


# --- 6. Graphique ---------------------------------------------------------------------


class S6Graphique(SceneVitesse):
    ID = "s6"

    def construct(self):
        vs = P.VITESSES_GRAPHIQUE
        pas_v = vs[1] - vs[0]
        d_max_brut = max(P.distance_arret(v, "mouille") for v in vs)
        pas_d = next(p for p in (10, 20, 25, 30, 40, 50, 100) if d_max_brut / p <= 6)
        d_max = np.ceil(d_max_brut / pas_d) * pas_d
        titre = self.titre(self.e("titre"))

        plage_v = [vs[0] - pas_v * 0.75, vs[-1] + pas_v * 0.75, pas_v]
        plage_d = [0, d_max, pas_d]
        cfg_v = dict(include_numbers=True, numbers_to_include=list(vs), include_ticks=False)
        cfg_d = dict(include_numbers=True, numbers_to_include=list(np.arange(pas_d, d_max + 1, pas_d)))
        commun = dict(include_tip=False, color=S.GRIS, stroke_width=3, font_size=S.AXE)
        if PORTRAIT:
            axes = AxesTexte(x_range=plage_d, y_range=plage_v, x_length=6.5, y_length=7.4,
                             axis_config=commun, x_axis_config=cfg_d, y_axis_config=cfg_v)
            axes.move_to([0.5, 0.3, 0])

            def pt(v, d):
                return axes.c2p(d, v)
        else:
            axes = AxesTexte(x_range=plage_v, y_range=plage_d, x_length=11.6, y_length=4.6,
                             axis_config=commun, x_axis_config=cfg_v, y_axis_config=cfg_d)
            axes.move_to([-0.25, -0.55, 0])

            def pt(v, d):
                return axes.c2p(v, d)

        axe_d = axes.x_axis if PORTRAIT else axes.y_axis
        axe_v = axes.y_axis if PORTRAIT else axes.x_axis
        lab_v = texte(self.e("axe_x"), taille=S.AXE - 2, couleur=S.GRIS, graisse=MEDIUM)
        lab_d = texte(self.e("axe_y"), taille=S.AXE - 2, couleur=S.GRIS, graisse=MEDIUM)
        if PORTRAIT:
            lab_v.next_to(axe_v, UP, buff=0.25).align_to(axe_v, LEFT).shift(LEFT * 0.5)
            lab_d.next_to(axe_d, DOWN, buff=0.6).align_to(axe_d, RIGHT)
        else:
            lab_v.next_to(axe_v, DOWN, buff=0.62).align_to(axe_v, RIGHT)
            lab_d.next_to(axe_d, UP, buff=0.2).align_to(axe_d, LEFT).shift(LEFT * 0.4)
        grille = VGroup(
            *[
                DashedLine(pt(plage_v[0], d), pt(plage_v[1], d), stroke_color=S.GRIS_FONCE, stroke_width=1.5, dash_length=0.08)
                for d in np.arange(pas_d, d_max + 1, pas_d)
            ]
        )

        lb = pas_v * 0.62

        def barre(v, d0, d1, couleur):
            a, b = pt(v - lb / 2, d0), pt(v + lb / 2, max(d1, d0 + 1e-3))
            return Rectangle(
                width=abs(b[0] - a[0]), height=abs(b[1] - a[1]), fill_color=couleur, fill_opacity=1, stroke_width=0
            ).move_to((a + b) / 2)

        bord = LEFT if PORTRAIT else DOWN
        barres = {}
        for v in vs:
            d_r, d_a = P.distance_reaction(v), P.distance_arret(v)
            barres[v] = VGroup(barre(v, 0, d_r, S.ORANGE), barre(v, d_r, d_a, S.ROUGE))

        taille_leg = S.PETIT - (6 if PORTRAIT else 2)
        legende_buff = 0.3 if PORTRAIT else 0.6

        def legende_case(couleur, s):
            c = Square(0.3, fill_color=couleur, fill_opacity=1, stroke_width=0)
            return VGroup(c, texte(s, taille=taille_leg, graisse=MEDIUM)).arrange(RIGHT, buff=0.16)

        sol = pastille(self.e("sol_sec"), S.BLANC, taille=taille_leg)
        legende = VGroup(legende_case(S.ORANGE, self.e("reaction")), legende_case(S.ROUGE, self.e("freinage")), sol)
        legende.arrange(RIGHT, buff=legende_buff).next_to(titre, DOWN, buff=0.3)
        if legende.width > 2 * XMAX:
            legende.arrange_in_grid(rows=2, buff=(0.5, 0.25)).next_to(titre, DOWN, buff=0.3)

        # Mise en avant : la vitesse double, le freinage quadruple.
        v_bas, v_haut = P.VITESSES_CARRE
        valeurs_df = VGroup()
        for v in (v_bas, v_haut):
            df = P.distance_freinage(v)
            lab = texte(T.metres(df, 0), taille=S.TEXTE, couleur=S.ROUGE)
            lab.next_to(barres[v][1], RIGHT if PORTRAIT else UP, buff=0.15)
            valeurs_df.add(lab)
        carre = texte(self.e("carre"), taille=S.TEXTE + 4, accents=(S.JAUNE, S.ROUGE), largeur=2 * XMAX)
        explication = texte(self.e("carre_explication"), taille=S.PETIT, couleur=S.GRIS, graisse=MEDIUM, largeur=2 * XMAX)
        bloc = VGroup(carre, explication).arrange(DOWN, buff=0.25)
        if PORTRAIT:
            bloc.next_to(lab_d, DOWN, buff=0.45).set_x(0)
        else:
            bloc.move_to(pt(vs[0] + pas_v * 3.2, d_max * 0.78))
            bloc.align_to(pt(vs[0], 0), LEFT).shift(RIGHT * 0.3)
        lien = CurvedArrow(
            valeurs_df[0].get_corner(UR if not PORTRAIT else DR) + (RIGHT * 0.1 if not PORTRAIT else DOWN * 0.05),
            valeurs_df[1].get_left() + LEFT * 0.1,
            angle=-PI / 3 if not PORTRAIT else PI / 3,
            color=S.JAUNE,
            stroke_width=4,
            tip_length=0.2,
        )

        self.dire(selon("graphique", "carre"))
        self.play(FadeIn(titre, shift=DOWN * 0.2), FadeIn(legende), run_time=selon(0.8, 0.5))
        self.play(Create(axes), FadeIn(grille), FadeIn(lab_v), FadeIn(lab_d), run_time=selon(1.2, 0.6))
        self.marquer("barres")
        self.play(
            LaggedStart(
                *[Succession(GrowFromEdge(barres[v][0], bord, run_time=0.35), GrowFromEdge(barres[v][1], bord, run_time=0.45)) for v in vs],
                lag_ratio=0.25,
            ),
            run_time=selon(3.4, 1.8),
        )
        self.jusqua(selon(5.8, 2.9))
        self.marquer("carre")
        if not COURT:
            self.dire("carre")
        autres = VGroup(*[barres[v] for v in vs if v not in (v_bas, v_haut)])
        self.play(autres.animate.set_opacity(0.22), run_time=selon(0.6, 0.4))
        self.play(LaggedStart(*[FadeIn(l, scale=0.7) for l in valeurs_df], lag_ratio=0.6), run_time=selon(1.2, 0.7))
        self.play(Create(lien), run_time=selon(0.6, 0.4))
        if COURT:
            self.play(FadeIn(bloc, shift=UP * 0.2), run_time=0.5)
        else:
            self.play(FadeIn(carre, shift=UP * 0.2), run_time=0.7)
            self.jusqua(12.8)
            self.dire("explication")
            self.play(FadeIn(explication), run_time=0.6)
        self.jusqua(selon(16.0, 5.6))
        self.play(
            FadeOut(valeurs_df), FadeOut(lien), FadeOut(bloc), autres.animate.set_opacity(1), run_time=selon(0.7, 0.5)
        )

        # Sol mouillé : le freinage s'allonge, l'ancien total reste marqué.
        sol_m = pastille(self.e("sol_mouille"), S.BLEU, taille=taille_leg)
        nouvelle = VGroup(legende[0].copy(), legende[1].copy(), sol_m).arrange(RIGHT, buff=legende_buff)
        nouvelle.move_to(legende)
        repere_sec = VGroup()
        anims = []
        for v in vs:
            d_r, d_a, d_m = P.distance_reaction(v), P.distance_arret(v), P.distance_arret(v, "mouille")
            a, b = pt(v - lb / 2 - pas_v * 0.06, d_a), pt(v + lb / 2 + pas_v * 0.06, d_a)
            repere_sec.add(Line(a, b, stroke_color=S.BLANC, stroke_width=5))
            anims.append(Transform(barres[v][1], barre(v, d_r, d_m, S.ROUGE)))
        repere_sec.set_z_index(2)
        self.dire("mouille")
        self.marquer("mouille")
        self.play(
            legende[0].animate.move_to(nouvelle[0]),
            legende[1].animate.move_to(nouvelle[1]),
            Transform(sol, sol_m),
            run_time=selon(0.6, 0.4),
        )
        self.add(repere_sec)
        self.play(LaggedStart(*anims, lag_ratio=0.12), run_time=selon(2.2, 1.4))
        self.jusqua(selon(24.2, 9.9))
        self.vider()


# --- 7. Expériences simulées --------------------------------------------------------


class S7Experiences(SceneVitesse):
    ID = "s7"

    def experience(self, exp, nid, debut, repliques, temps):
        """Deux voitures passent au même point quand un obstacle surgit à la
        distance d'arrêt de la plus lente. `repliques` : événement → clé de
        narration ; `temps` : instants (relatifs à `debut`) des étapes."""
        dio = exp.d_obstacle
        lm = P.LONGUEUR_VEHICULE
        titre = self.titre(self.e("titre", scene=nid))
        larg, h_enfant = (1.2, 1.1) if PORTRAIT else (1.45, 1.25)
        visible = 0.4  # s d'approche de la voiture rapide visibles avant le danger
        avant = P.ms(exp.rapide) * visible + lm
        if PORTRAIT:
            bas, haut = -YMAX, titre.get_bottom()[1] - 0.45 - h_enfant
            k = (haut - bas) / (avant + dio)
            reps = [Repere([x, bas + avant * k, 0], True, k) for x in (-1.25, 1.25)]
            cotes_lab = [LEFT, RIGHT]  # compteurs à l'extérieur des deux voies
        else:
            gauche, droite = -XMAX, XMAX - 0.6
            k = (droite - gauche) / (avant + dio)
            reps = [Repere([gauche + avant * k, y, 0], False, k) for y in (1.2, -1.05)]
            cotes_lab = [UP, UP]
        lm = max(lm * k, S.TAILLE_MIN_VEHICULE * S.ECHELLE_ICONE[P.VEHICULE]) / k  # longueur dessinée (m), lisible même à petite échelle
        t = ValueTracker(-3 * visible)
        routes, zones, voitures, compteurs, enfants = VGroup(), VGroup(), [], [], VGroup()

        def evt(nom):
            if nom in repliques:
                self.dire(repliques[nom], scene=nid)

        for rep, vit, couleur, t_imp, dir_lab in zip(
            reps, (exp.lente, exp.rapide), (S.VERT, S.ROUGE), (None, exp.t_impact), cotes_lab
        ):
            if PORTRAIT:
                haut_route = titre.get_bottom()[1] - 0.25
                a, b = rep.p((-H / 2 - rep.o[1]) / k), rep.p((haut_route - rep.o[1]) / k)
            else:
                a, b = rep.p((-W / 2 - rep.o[0]) / k), rep.p((W / 2 - rep.o[0]) / k)
            routes.add(route(np.linalg.norm(b - a), larg, vertical=PORTRAIT).move_to((a + b) / 2))

            def sv(vit=vit, t_imp=t_imp):
                tt = t.get_value() if t_imp is None else min(t.get_value(), t_imp)
                return P.ms(vit) * tt if tt < 0 else P.position_freinage(vit, tt)

            def zone(sa, sb, c, rep=rep):
                if sb - sa < 1e-3:
                    return VectorizedPoint(rep.p(sa))
                return Polygon(
                    rep.p(sa, larg * 0.42), rep.p(sb, larg * 0.42), rep.p(sb, -larg * 0.42), rep.p(sa, -larg * 0.42),
                    fill_color=c, fill_opacity=0.72, stroke_width=0,
                )

            d_r = P.distance_reaction(vit)
            zones.add(
                always_redraw(lambda sv=sv, d_r=d_r, zone=zone: zone(0, max(0, min(sv(), d_r)), S.ORANGE)),
                always_redraw(lambda sv=sv, d_r=d_r, zone=zone: zone(d_r, max(d_r, sv()), S.ROUGE)),
            )
            voiture = vehicule(couleur, lm * k).rotate(rep.angle)

            def suivre(m, rep=rep, sv=sv):
                placer_vehicule(m, rep, sv())
                m.freine(t.get_value() > P.TEMPS_REACTION)

            voiture.add_updater(suivre)
            suivre(voiture)
            compteur = NombreTexte(vit, formateur=T.vitesse, font_size=S.PETIT if PORTRAIT else S.TEXTE - 6, color=couleur)

            def suivre_compteur(m, rep=rep, sv=sv, vit=vit, d=dir_lab):
                m.set_value(P.vitesse_freinage(vit, max(0.0, t.get_value())))
                bord = rep.p(sv() - lm / 2, larg / 2 if (d == UP).all() or (d == LEFT).all() else -larg / 2)
                m.next_to(bord, d, buff=0.15)

            compteur.add_updater(suivre_compteur)
            suivre_compteur(compteur)
            voitures.append(voiture)
            compteurs.append(compteur)
            e = enfant(h_enfant)
            if PORTRAIT:
                e.next_to(rep.p(dio), UP, buff=0.04)
            else:
                e.move_to(rep.p(dio)).align_to(rep.p(dio), LEFT).shift(RIGHT * 0.04)
            enfants.add(e)

        ligne = DashedLine(
            reps[0].p(0, larg / 2 + 0.2), reps[1].p(0, -larg / 2 - 0.2), stroke_color=S.JAUNE, stroke_width=4, dash_length=0.12
        )
        if PORTRAIT:
            x_mil = (reps[0].o[0] + reps[1].o[0]) / 2
            c_obs = cote([x_mil, reps[0].o[1], 0], [x_mil, reps[0].p(dio)[1], 0], "", S.JAUNE)
            lab = texte(self.e("obstacle", scene=nid), taille=S.PETIT - 2, couleur=S.JAUNE).next_to(ligne, DOWN, buff=0.35)
            c_obs.add(lab)
        else:
            lat = -larg / 2 - 0.35
            c_obs = cote(reps[1].p(0, lat), reps[1].p(dio, lat), self.e("obstacle", scene=nid), S.JAUNE)
        flash = Rectangle(width=W, height=H, fill_color=WHITE, fill_opacity=0, stroke_width=0)

        # 1. Mise en place, puis approche à vitesse réelle.
        self.marquer("partie")
        evt("debut")
        self.play(FadeIn(titre, shift=DOWN * 0.2), FadeIn(routes), run_time=selon(0.8, 0.5))
        self.add(zones, *voitures, *compteurs)
        self.jusqua(debut + temps["approche"])
        self.marquer("approche")
        self.derouler(t, 0.0, -t.get_value())
        # 2. L'obstacle surgit : arrêt sur image.
        self.marquer("gel")
        evt("gel")
        self.play(Create(ligne), LaggedStart(*[GrowFromEdge(e, DOWN) for e in enfants], lag_ratio=0.15), run_time=selon(0.5, 0.4))
        self.play(FadeIn(c_obs), run_time=selon(0.5, 0.3))
        self.jusqua(debut + temps["reprise"])
        # 3. Temps réel : la rapide heurte l'obstacle...
        self.marquer("reprise")
        self.derouler(t, exp.t_impact, exp.t_impact)
        self.marquer("impact")
        rouge, c_rouge = voitures[1], compteurs[1]
        rouge.clear_updaters()
        c_rouge.clear_updaters()
        c_rouge.set_value(exp.v_impact)
        c_rouge.generate_target()
        c_rouge.target.scale(1.2 if PORTRAIT else 1.35)
        dans_cadre(c_rouge.target, W, H)
        choc = reps[1].p(dio)
        duree_choc = 0.8
        self.play(
            AnimationGroup(
                t.animate(rate_func=linear).set_value(exp.t_impact + duree_choc),
                flash.animate(run_time=0.4, rate_func=there_and_back).set_fill(opacity=0.75),
                Flash(choc, color=WHITE, line_length=0.35, flash_radius=0.45, num_lines=14, run_time=0.5),
                MoveToTarget(c_rouge, run_time=0.5),
            ),
            run_time=duree_choc,
        )
        evt("choc")
        # ... la lente s'arrête juste à temps.
        self.derouler(t, exp.t_arret_lente, exp.t_arret_lente - exp.t_impact - duree_choc)
        vert, c_vert = voitures[0], compteurs[0]
        vert.clear_updaters()
        c_vert.clear_updaters()
        arret = pastille(self.e("arret", scene=nid), S.VERT, taille=S.PETIT - 2).move_to(c_vert)
        dans_cadre(arret, W, H)
        self.marquer("arret")
        evt("arret")
        self.play(ReplacementTransform(c_vert, arret), run_time=selon(0.5, 0.4))
        self.jusqua(debut + temps["equivalence"])

        # 4. Équivalence : chute du N-ième étage.
        self.marquer("equivalence")
        for m in self.mobjects:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects if m is not titre], run_time=selon(0.6, 0.4))
        imp = texte(self.e("impact", scene=nid), taille=S.TITRE + 6, accents=(S.ROUGE,))
        chute = texte(self.e("chute", scene=nid), taille=S.TEXTE + 4)
        bloc = VGroup(imp, chute).arrange(DOWN, buff=0.35)
        if PORTRAIT:
            bloc.next_to(titre, DOWN, buff=0.7)
            sol_y = -YMAX
            h_dispo = bloc.get_bottom()[1] - 0.7 - sol_y
            x_imm = -0.2
        else:
            bloc.move_to([-3.6, 0.2, 0])
            sol_y = -YMAX + 0.1
            h_dispo = titre.get_bottom()[1] - 0.45 - sol_y
            x_imm = 2.9
        h_niv = min(h_dispo / (exp.etage + 1), 0.9)
        imm = immeuble(exp.etage + 1, h_niv, largeur=2.0).shift([x_imm, sol_y, 0])
        y_chute = sol_y + exp.h_chute / P.HAUTEUR_ETAGE * h_niv
        x_f = x_imm - 1.55
        fleche = Arrow(
            [x_f, y_chute, 0], [x_f, sol_y, 0], buff=0, color=S.ROUGE, stroke_width=7,
            max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=10,
        )
        trait = DashedLine([x_f - 0.35, y_chute, 0], [x_imm - 1.0, y_chute, 0], stroke_color=S.ROUGE, stroke_width=3)
        h_lab = texte(T.hauteur(exp.h_chute), taille=S.TEXTE - 4, couleur=S.ROUGE).next_to(fleche, LEFT, buff=0.2)
        etage_lab = texte(self.e("etage", scene=nid), taille=S.TEXTE, couleur=S.JAUNE)
        etage_lab.next_to(imm[0], RIGHT, buff=0.35).set_y(imm.niveaux[-1].get_y())
        dans_cadre(etage_lab, W, H)
        evt("equivalence")
        self.play(FadeIn(imp, scale=0.85), run_time=selon(0.6, 0.4))
        if "chute" in temps:
            self.jusqua(debut + temps["chute"])
        evt("chute")
        self.play(FadeIn(chute, shift=UP * 0.2), run_time=selon(0.5, 0.4))
        self.play(
            LaggedStart(FadeIn(imm[0]), FadeIn(imm[2]), *[FadeIn(n) for n in imm.niveaux], lag_ratio=0.12),
            run_time=selon(0.6 + 0.12 * exp.etage, 0.9),
        )
        self.play(
            imm.niveaux[-1].animate.set_fill(S.JAUNE), FadeIn(etage_lab, shift=LEFT * 0.2), Create(trait),
            run_time=selon(0.6, 0.4),
        )
        self.play(GrowArrow(fleche), FadeIn(h_lab), run_time=selon(0.9, 0.6))
        self.jusqua(debut + temps["fin"] - FONDU)
        self.vider()

    def construct(self):
        self.experience(
            P.EXPERIENCE_VILLE, "s7", 0.0,
            repliques=selon(
                {"debut": "intro", "gel": "obstacle", "arret": "arret", "equivalence": "impact"},
                {"debut": "intro", "equivalence": "impact"},
            ),
            temps=selon(
                dict(approche=3.6, reprise=8.9, equivalence=12.9, fin=20.0),
                dict(approche=0.5, reprise=2.4, equivalence=5.4, fin=10.0),
            ),
        )
        debut = self.maintenant()
        self.experience(
            P.EXPERIENCE_AUTOROUTE, "s7b", debut,
            repliques={"debut": "intro", "choc": "impact", "chute": "chute"},
            temps=selon(
                dict(approche=2.0, reprise=4.4, equivalence=9.6, chute=10.6, fin=20.0),
                dict(approche=0.5, reprise=2.4, equivalence=7.0, chute=7.8, fin=11.0),
            ),
        )


# --- 8. Conclusion ------------------------------------------------------------------


class S8Conclusion(SceneVitesse):
    ID = "s8"

    def construct(self):
        l1 = texte(self.e("ligne1"), taille=S.TITRE + 10, largeur=2 * XMAX)
        l2 = texte(self.e("ligne2"), taille=S.TITRE + 4, accents=(S.ROUGE,), largeur=2 * XMAX)
        VGroup(l1, l2).arrange(DOWN, buff=0.9).move_to(ORIGIN)
        self.dire("secondes")
        self.play(FadeIn(l1, shift=UP * 0.3), run_time=selon(1.0, 0.6))
        self.jusqua(selon(3.6, 1.9))
        self.marquer("ligne2")
        self.dire("metres")
        self.play(FadeIn(l2, shift=UP * 0.3), run_time=selon(1.0, 0.6))
        self.jusqua(selon(8.8, 5.0))
        self.play(FadeOut(l1), FadeOut(l2), run_time=selon(0.8, 0.5))

        # Carton final : la jauge de l'accroche redescend dans le vert,
        # puis la signature si assets/signature.png existe.
        j = jauge(rayon=1.35)
        p = ValueTracker(0.95)
        aig = always_redraw(lambda: aiguille(j, p.get_value()))
        slogan = texte(self.e("carton"), taille=S.TITRE + 24, couleur=S.BLANC)
        self.marquer("carton")
        elements = [j, slogan]
        if SIGNATURE.exists():
            img = ImageMobject(str(SIGNATURE))
            img.scale_to_fit_height(1.5)
            if img.width > 2 * XMAX:
                img.scale_to_fit_width(2 * XMAX)
            elements.append(img)
        Group(*elements).arrange(DOWN, buff=0.6).move_to(ORIGIN)
        self.play(FadeIn(j), FadeIn(aig), FadeIn(slogan, scale=0.9), run_time=selon(0.8, 0.6))
        self.play(p.animate.set_value(0.12), run_time=selon(1.6, 1.0), rate_func=rate_functions.ease_in_out_cubic)
        if SIGNATURE.exists():
            self.play(FadeIn(elements[-1]), run_time=selon(0.8, 0.5))
        self.jusqua(selon(14.2, 7.6))
        self.vider()
