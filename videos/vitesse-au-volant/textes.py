"""Textes de la vidéo (textes_<langue>.json) et mise en forme des nombres.

`valeurs(T)` calcule, scène par scène, toutes les valeurs à insérer dans les
textes à partir de physique.py : c'est le seul pont entre le modèle et ce
qui est affiché ou dit.
"""

import json
import os
import re
from pathlib import Path

import physique as P

DOSSIER = Path(__file__).resolve().parent
LANGUE = os.environ.get("VITESSE_LANGUE", "fr")

ESPACE_FINE = " "
ESPACE_INSECABLE = " "


class Textes:
    def __init__(self, langue=LANGUE):
        self.langue = langue
        chemin = DOSSIER / f"textes_{langue}.json"
        self.data = json.loads(chemin.read_text(encoding="utf-8"))
        self.police = self.data["police"]
        self.rtl = self.data.get("direction") == "rtl"
        self._n = self.data["nombres"]
        self._f = self.data["formats"]
        # Chiffres optionnels (ex. « ٠١٢٣٤٥٦٧٨٩ » pour une version arabe).
        chiffres = self._n.get("chiffres")
        self._chiffres = str.maketrans("0123456789", chiffres) if chiffres else None

    def _chiffres_locaux(self, s):
        return s.translate(self._chiffres) if self._chiffres else s

    # --- Nombres et unités --------------------------------------------------

    def nombre(self, x, decimales=0, signe=False):
        arrondi = round(x, decimales)
        s = f"{abs(arrondi):,.{decimales}f}"
        s = s.replace(",", "\0").replace(".", self._n["decimale"])
        s = s.replace("\0", self._n["milliers"])
        if arrondi < 0:
            s = self._n["moins"] + s
        elif signe and arrondi > 0:
            s = self._n["plus"] + s
        return self._chiffres_locaux(s)

    def format(self, nom, **valeurs):
        # Les modèles ne contiennent aucun chiffre : ceux du résultat viennent
        # des valeurs (y compris les {s:02d} du chrono).
        return self._chiffres_locaux(self._f[nom].format(**valeurs))

    def vitesse(self, v):
        return self.format("vitesse", v=self.nombre(v))

    def metres(self, d, decimales=1):
        return self.format("metres", d=self.nombre(d, decimales))

    def km(self, d):
        return self.format("km", d=self.nombre(d))

    def secondes(self, s, decimales=0):
        return self.format("secondes", s=self.nombre(s, decimales))

    def duree(self, secondes):
        """Durée en « 12 min » ou « 2 min 30 »."""
        m, s = divmod(round(secondes), 60)
        if s == 0:
            return self.format("minutes", m=self.nombre(m))
        return self.format("minutes_secondes", m=self.nombre(m), s=s)

    def chrono(self, secondes):
        m, s = divmod(int(secondes + 1e-6), 60)
        return self.format("chrono", m=m, s=s)

    def s_par_km(self, s, signe=False):
        return self.format("s_par_km", s=self.nombre(s, signe=signe))

    def facteur(self, k):
        return self.format("facteur", k=self.nombre(k))

    def ordinal(self, n):
        nom = "ordinal_premier" if n == 1 else "ordinal"
        return self.format(nom, n=self.nombre(n))

    def hauteur(self, h):
        """5,5 m sous 10 m, sinon arrondi au mètre (39 m)."""
        return self.metres(h, 1 if h < 10 else 0)

    # --- Textes -------------------------------------------------------------

    def typo(self, s):
        """Espaces insécables de la typographie française."""
        if not self.data.get("typographie_fr"):
            return s
        s = re.sub(r" ([?!;])", ESPACE_FINE + r"\1", s)
        s = re.sub(r" ([:»])", ESPACE_INSECABLE + r"\1", s)
        return re.sub(r"« ", "«" + ESPACE_INSECABLE, s)

    def ecran(self, cle, **valeurs):
        scene, nom = cle.split(".")
        return self.typo(self.data["ecran"][scene][nom].format(**valeurs))

    def narration(self, scene, cle, **valeurs):
        return self.typo(self.data["narration"][scene][cle].format(**valeurs))


def valeurs(T):
    """Valeurs mises en forme pour chaque scène (clés des {accolades})."""
    n = T.nombre
    cv, ca = P.COURSE_VILLE, P.COURSE_AUTOROUTE
    ev, ea = P.EXPERIENCE_VILLE, P.EXPERIENCE_AUTOROUTE
    v_bas, v_haut = P.VITESSES_CARRE
    df_bas, df_haut = P.distance_freinage(v_bas), P.distance_freinage(v_haut)
    vs, vb = P.VITESSE_SCHEMA, P.VITESSE_SCHEMA_BIS

    def course(c):
        return dict(
            d=T.km(c.d_km),
            d_nombre=n(c.d_km),
            v1=n(c.lente),
            v2=n(c.rapide),
            t1=T.duree(c.t_lente),
            t2=T.duree(c.t_rapide),
            gain=T.duree(c.gain),
            video=T.secondes(1),
            reel=T.duree(P.SECONDES_REELLES_PAR_SECONDE_VIDEO),
        )

    def experience(e):
        return dict(
            v1=n(e.lente),
            v2=n(e.rapide),
            d=T.metres(e.d_obstacle),
            vi=n(e.v_impact),
            v=T.vitesse(e.v_impact),
            h=T.hauteur(e.h_chute),
            ordinal=T.ordinal(e.etage),
            etage=T.ordinal(e.etage),
        )

    bilan = dict(
        dv_ville=n(cv.rapide - cv.lente),
        dv_autoroute=n(ca.rapide - ca.lente),
        gain_ville=T.duree(cv.gain),
        gain_autoroute=T.duree(ca.gain),
    )
    return {
        "s1": {},
        "s2": course(cv),
        "s3": {**course(ca), **bilan},
        "s4": dict(
            sph=n(P.SECONDES_PAR_HEURE),
            v1=n(cv.lente),
            v2=n(cv.rapide),
            v3=n(ca.lente),
            v4=n(ca.rapide),
            g_ville=n(P.secondes_par_km(cv.lente) - P.secondes_par_km(cv.rapide)),
            g_autoroute=n(
                P.secondes_par_km(ca.lente) - P.secondes_par_km(ca.rapide)
            ),
        ),
        "s5": dict(
            tr=T.secondes(P.TEMPS_REACTION),
            v=n(vs),
            dr=T.metres(P.distance_reaction(vs)),
            df=T.metres(P.distance_freinage(vs)),
            da=T.metres(P.distance_arret(vs)),
            d=T.metres(P.distance_arret(vs)),  # « Arrêt : {d} », remplacé par la scène
            v_bis=n(vb),
            da_bis=T.metres(P.distance_arret(vb)),
        ),
        "s6": dict(
            tr=T.secondes(P.TEMPS_REACTION),
            vmin=n(min(P.VITESSES_GRAPHIQUE)),
            vmax=n(max(P.VITESSES_GRAPHIQUE)),
            v1=n(v_bas),
            v2=n(v_haut),
            df1=T.metres(df_bas, 0),
            df2=T.metres(df_haut, 0),
            kv=T.facteur(v_haut / v_bas),
            kf=T.facteur(df_haut / df_bas),
        ),
        "s7": experience(ev),
        "s7b": experience(ea),
        "s8": {},
    }
