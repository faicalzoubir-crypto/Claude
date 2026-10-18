"""Valeurs de contrôle (sol sec, réaction 1 s), à ±0,2 près."""

import pytest

import physique as P

TOL = 0.2


@pytest.mark.parametrize(
    "v, da",
    [(40, 19.9), (50, 27.7), (80, 57.5), (120, 112.7)],
)
def test_distance_arret(v, da):
    assert P.distance_arret(v) == pytest.approx(da, abs=TOL)


def test_distance_arret_somme_reaction_freinage():
    for v in P.VITESSES_GRAPHIQUE:
        for sol in P.DECELERATION:
            assert P.distance_arret(v, sol) == pytest.approx(
                P.distance_reaction(v) + P.distance_freinage(v, sol)
            )


def test_impact_ville():
    d = P.distance_arret(40)
    assert P.vitesse_impact(50, d) == pytest.approx(37.5, abs=TOL)
    assert P.EXPERIENCE_VILLE.v_impact == pytest.approx(37.5, abs=TOL)


def test_impact_autoroute():
    d = P.distance_arret(80)
    assert P.vitesse_impact(120, d) == pytest.approx(100.1, abs=TOL)
    assert P.EXPERIENCE_AUTOROUTE.v_impact == pytest.approx(100.1, abs=TOL)


def test_pas_d_impact_si_la_voiture_s_arrete():
    assert P.vitesse_impact(40, P.distance_arret(40) + 0.01) == 0
    assert P.EXPERIENCE_VILLE.lente == 40
    assert P.vitesse_impact(40, P.EXPERIENCE_VILLE.d_obstacle) == pytest.approx(
        0, abs=0.5
    )


def test_obstacle_dans_la_distance_de_reaction():
    # Choc à pleine vitesse : aucun freinage n'a commencé.
    assert P.vitesse_impact(50, 5) == pytest.approx(50)


def test_chute_equivalente():
    a, b = P.EXPERIENCE_VILLE, P.EXPERIENCE_AUTOROUTE
    assert a.h_chute == pytest.approx(5.5, abs=TOL)
    assert a.etage == 2
    assert b.h_chute == pytest.approx(39.4, abs=TOL)
    assert b.etage == 13


def test_gains_de_temps():
    assert P.COURSE_VILLE.t_lente == pytest.approx(15 * 60)
    assert P.COURSE_VILLE.t_rapide == pytest.approx(12 * 60)
    assert P.COURSE_VILLE.gain == pytest.approx(3 * 60)
    assert P.COURSE_AUTOROUTE.gain == pytest.approx(2 * 60 + 30)
    # Le paradoxe : +10 km/h en ville fait gagner plus que +40 sur autoroute.
    assert P.COURSE_VILLE.gain > P.COURSE_AUTOROUTE.gain


def test_secondes_par_km():
    assert P.secondes_par_km(40) - P.secondes_par_km(50) == pytest.approx(18)
    assert P.secondes_par_km(80) - P.secondes_par_km(120) == pytest.approx(15)


def test_freinage_quadruple_quand_la_vitesse_double():
    v1, v2 = P.VITESSES_CARRE
    assert P.distance_freinage(v1) == pytest.approx(9, abs=0.5)
    assert P.distance_freinage(v2) == pytest.approx(35, abs=0.5)
    assert P.distance_freinage(v2) / P.distance_freinage(v1) == pytest.approx(
        (v2 / v1) ** 2
    )


def test_sol_mouille_plus_long():
    for v in P.VITESSES_GRAPHIQUE:
        assert P.distance_arret(v, "mouille") > P.distance_arret(v, "sec")


def test_mouvement_coherent_avec_les_distances():
    for v in (40, 50, 80, 120):
        assert P.position_freinage(v, P.TEMPS_REACTION) == pytest.approx(
            P.distance_reaction(v)
        )
        assert P.position_freinage(v, 1e3) == pytest.approx(P.distance_arret(v))
        assert P.vitesse_freinage(v, 1e3) == 0
    exp = P.EXPERIENCE_VILLE
    assert P.position_freinage(exp.rapide, exp.t_impact) == pytest.approx(
        exp.d_obstacle
    )
    assert P.vitesse_freinage(exp.rapide, exp.t_impact) == pytest.approx(
        exp.v_impact
    )
