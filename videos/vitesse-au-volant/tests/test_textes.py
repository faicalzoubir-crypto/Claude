"""Les textes se remplissent tous avec les valeurs calculées, sans chiffre en dur."""

import json
import re

import pytest

from textes import DOSSIER, Textes, valeurs

LANGUES = sorted(p.stem.split("_", 1)[1] for p in DOSSIER.glob("textes_*.json"))


def chaines(d):
    if isinstance(d, str):
        yield d
    elif isinstance(d, dict):
        for k, v in d.items():
            if not k.startswith("_"):
                yield from chaines(v)
    elif isinstance(d, list):
        for v in d:
            yield from chaines(v)


@pytest.mark.parametrize("langue", LANGUES)
def test_tous_les_textes_se_remplissent(langue):
    T = Textes(langue)
    V = valeurs(T)
    for section in ("ecran", "narration"):
        for scene, textes in T.data[section].items():
            for cle in textes:
                if section == "ecran":
                    s = T.ecran(f"{scene}.{cle}", **V[scene])
                else:
                    s = T.narration(scene, cle, **V[scene])
                assert "{" not in s and "}" not in s, (scene, cle, s)


@pytest.mark.parametrize("langue", LANGUES)
def test_aucun_chiffre_en_dur(langue):
    data = json.loads((DOSSIER / f"textes_{langue}.json").read_text("utf-8"))
    for s in chaines({k: data[k] for k in ("ecran", "narration")}):
        sans_accolades = re.sub(r"\{[^}]*\}", "", s)
        assert not re.search(r"\d", sans_accolades), s


def test_nombres_a_la_francaise():
    T = Textes("fr")
    assert T.nombre(19.93, 1) == "19,9"
    assert T.nombre(3600) == "3 600"
    assert T.nombre(-18) == "−18"
    assert T.nombre(-0.01) == "0"
    assert T.duree(180) == "3 min"
    assert T.duree(150) == "2 min 30"
    assert T.chrono(12 * 60) == "12:00"
    assert T.chrono(7 * 60 + 30) == "07:30"
    assert T.ordinal(1) == "1er"
    assert T.ordinal(13) == "13e"
    assert T.hauteur(5.52) == "5,5 m"
    assert T.hauteur(39.4) == "39 m"


def test_valeurs_du_storyboard():
    T = Textes("fr")
    V = valeurs(T)
    assert V["s2"]["gain"] == "3 min"
    assert V["s3"]["gain"] == "2 min 30"
    assert (V["s4"]["g_ville"], V["s4"]["g_autoroute"]) == ("18", "15")
    assert (V["s6"]["df1"], V["s6"]["df2"], V["s6"]["kf"]) == ("9 m", "35 m", "×4")
    assert (V["s7"]["vi"], V["s7"]["h"], V["s7"]["etage"]) == ("37", "5,5 m", "2e")
    assert (V["s7b"]["vi"], V["s7b"]["h"], V["s7b"]["etage"]) == ("100", "39 m", "13e")


def test_chiffres_locaux():
    """Option « chiffres » de textes_XX.json (ici simulée sur le français)."""
    T = Textes("fr")
    T._chiffres = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    assert T.nombre(37.47) == "٣٧"
    assert T.chrono(7 * 60 + 30) == "٠٧:٣٠"
    assert T.duree(150) == "٢ min ٣٠"
