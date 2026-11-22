"""Tests de fourx.clients.force_layout (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 7 ter, disposition de la carte ; plan détaillé, point 23 decies).

Les étapes sont testées une à une sur de petits graphes, et comparées par `pytest.approx` : la
disposition calcule en flottants. Le test des graines 1 à 2 000 porte la marque `lent` seule : il
est hors de la mutation, et la tâche `rejeu` le lance ; il écrit les croisements de liens dans sa
sortie (`-s`), pour le compte rendu de M1.
"""

import math

import pytest

from fourx.clients.force_layout import (
    CARTE_MINIMALE,
    HAUTEUR_BOITE,
    LARGEUR_BOITE,
    RECTANGLE_UTILE,
    Positions,
    force_layout,
    initial_layers,
    normalize,
    recouvrement,
    relax,
    separate,
    snap_overlaps,
)
from fourx.clients.map_view import (
    HAUTEUR_CADRE,
    LARGEUR_CADRE,
    _cases_du_trait,
    _centre_du_cadre,
    anchor,
    initial_view,
)
from fourx.core import world
from fourx.core.observe import observe
from fourx.schema.observation import SystemView
from fourx.server.tunables_loader import load_tunables
from tests.aide_carte import verifier_carte

X0, Y0, X1, Y1 = RECTANGLE_UTILE


def chaine(n: int) -> tuple[SystemView, ...]:
    return tuple(
        SystemView(id=i, neighbors=tuple(v for v in (i - 1, i + 1) if 1 <= v <= n))
        for i in range(1, n + 1)
    )


def systemes_de(graine: int) -> tuple[SystemView, ...]:
    reglages = load_tunables()
    return observe(world.generate(graine, reglages), 1, reglages).systems


def verifier(positions: Positions, systemes: tuple[SystemView, ...]) -> None:
    """Chaque système une fois, toute sa boîte dans le carré, aucun recouvrement."""
    assert sorted(positions) == sorted(s.id for s in systemes)
    for x, y in positions.values():
        assert X0 - 1e-9 <= x <= X1 + 1e-9 and Y0 - 1e-9 <= y <= Y1 + 1e-9
        assert x + LARGEUR_BOITE <= 1 + 1e-9 and y + HAUTEUR_BOITE <= 1 + 1e-9
    idents = sorted(positions)
    for rang, a in enumerate(idents):
        for b in idents[rang + 1 :]:
            assert not recouvrement(positions[a], positions[b]), (a, b, positions)


# --- 1. Départ en couches


def test_couches_par_distance_sur_des_cercles() -> None:
    # Étoile : 1 au centre, 2 et 3 à un saut ; 4 à deux sauts ; 5 isolé (dernière couche).
    systemes = (
        SystemView(id=1, neighbors=(2, 3)),
        SystemView(id=2, neighbors=(1, 4)),
        SystemView(id=3, neighbors=(1,)),
        SystemView(id=4, neighbors=(2,)),
        SystemView(id=5, neighbors=()),
    )
    positions = initial_layers(systemes)
    assert positions[1] == (0.0, 0.0)
    assert positions[2] == pytest.approx((math.cos(0.5), math.sin(0.5)))
    assert positions[3] == pytest.approx((math.cos(0.5 + math.pi), math.sin(0.5 + math.pi)))
    assert positions[4] == pytest.approx((2 * math.cos(1.0), 2 * math.sin(1.0)))
    assert positions[5] == pytest.approx((3 * math.cos(1.5), 3 * math.sin(1.5)))
    assert initial_layers(()) == {}


# --- 2. Les forces


def test_relax_deux_voisins_trouvent_l_equilibre_et_les_forces_sont_symetriques() -> None:
    systemes = chaine(2)
    positions = relax(systemes, {1: (-1.5, 0.0), 2: (1.5, 0.0)})
    (x1, y1), (x2, y2) = positions[1], positions[2]
    assert y1 == pytest.approx(0.0) and y2 == pytest.approx(0.0)
    assert x1 == pytest.approx(-x2)  # symétrie autour de l'origine
    # Équilibre : répulsion 1 ÷ d² = ressort (d − 1) + rappel ; d se resserre depuis 3.
    assert 1.0 < x2 - x1 < 3.0


def test_relax_un_pas_borne_le_deplacement() -> None:
    # Deux systèmes confondus, sans lien : la répulsion est bornée par d ≥ 0,01, et le pas
    # total de 300 itérations vaut au plus Σ 0,1 × (1 − i ÷ 300) = 15,05.
    positions = relax((SystemView(1, ()), SystemView(2, ())), {1: (0.0, 0.0), 2: (0.0, 0.0)})
    for x, y in positions.values():
        assert math.hypot(x, y) <= 15.05 + 1e-9
    assert positions[1][0] > 0 and positions[2][0] > 0  # direction (1, 0) pour des confondus


def test_relax_ne_change_pas_un_systeme_seul_a_l_origine() -> None:
    assert relax((SystemView(1, ()),), {1: (0.0, 0.0)}) == {1: (0.0, 0.0)}


# --- 3. Normalisation


def test_normalize_remplit_le_rectangle_utile_sur_chaque_axe() -> None:
    positions = normalize({1: (-1.0, 0.0), 2: (1.0, 0.5), 3: (0.0, 1.0)})
    assert positions[1] == pytest.approx((X0, Y0))
    assert positions[2] == pytest.approx((X1, (Y0 + Y1) / 2))
    assert positions[3] == pytest.approx(((X0 + X1) / 2, Y1))


def test_normalize_un_axe_plat_et_un_point_seul_vont_au_milieu() -> None:
    plat = normalize({1: (0.0, 2.0), 2: (4.0, 2.0)})
    assert plat[1] == pytest.approx((X0, (Y0 + Y1) / 2))
    assert plat[2] == pytest.approx((X1, (Y0 + Y1) / 2))
    assert normalize({7: (3.0, 3.0)}) == {7: pytest.approx(((X0 + X1) / 2, (Y0 + Y1) / 2))}
    assert normalize({}) == {}


# --- 4. Séparation


def test_separate_ecarte_sur_l_axe_du_plus_petit_deplacement() -> None:
    # Écart horizontal 0,06, vertical 0,02 : il manque moins sur l'axe horizontal.
    positions = separate({1: (0.4, 0.5), 2: (0.46, 0.52)})
    manque = LARGEUR_BOITE - 0.06
    assert manque < HAUTEUR_BOITE - 0.02
    assert positions[1] == pytest.approx((0.4 - manque / 2, 0.5))
    assert positions[2] == pytest.approx((0.46 + manque / 2, 0.52))
    assert not recouvrement(positions[1], positions[2])


def test_separate_a_egalite_le_plus_petit_identifiant_va_a_gauche() -> None:
    positions = separate({1: (0.4, 0.5), 2: (0.4, 0.5)})
    assert positions[1] == pytest.approx((0.4 - LARGEUR_BOITE / 2, 0.5))
    assert positions[2] == pytest.approx((0.4 + LARGEUR_BOITE / 2, 0.5))


def test_separate_un_bord_laisse_le_reste_du_deplacement_a_l_autre() -> None:
    # 1 contre le bord gauche de R : il ne peut pas reculer ; 2 prend tout le déplacement.
    positions = separate({1: (X0, 0.5), 2: (X0 + 0.05, 0.5)})
    assert positions[1] == pytest.approx((X0, 0.5))
    assert positions[2] == pytest.approx((X0 + LARGEUR_BOITE, 0.5))


def test_separate_ramene_dans_r_et_laisse_des_boites_disjointes() -> None:
    positions = separate({1: (-1.0, 2.0), 2: (0.5, 0.5)})
    assert positions[1] == pytest.approx((X0, Y1))
    assert positions[2] == pytest.approx((0.5, 0.5))


# --- 5. Filet de sécurité


def test_snap_overlaps_replace_au_point_libre_le_plus_proche() -> None:
    # 1 et 2 confondus : par identifiants croissants, 1 part au point libre le plus proche du
    # quadrillage (à droite : une largeur de boîte est plus courte qu'une hauteur) ; 2 reste.
    positions = snap_overlaps({1: (X0, Y0), 2: (X0, Y0)})
    assert positions[1] == pytest.approx((X0 + LARGEUR_BOITE, Y0))
    assert positions[2] == (X0, Y0)
    assert not recouvrement(positions[1], positions[2])


def test_snap_overlaps_ne_touche_pas_des_boites_disjointes() -> None:
    disjointes = {1: (X0, Y0), 2: (X1, Y1)}
    assert snap_overlaps(disjointes) == disjointes


# --- La disposition entière


def test_meme_resultat_a_chaque_appel_et_disposition_valide() -> None:
    systemes = systemes_de(1)
    positions = force_layout(systemes)
    assert positions == force_layout(systemes)
    verifier(positions, systemes)


def test_disposition_d_une_chaine_et_d_un_systeme_seul() -> None:
    verifier(force_layout(chaine(12)), chaine(12))
    assert force_layout((SystemView(1, ()),)) == {1: pytest.approx(((X0 + X1) / 2, (Y0 + Y1) / 2))}


def croisements(systemes: tuple[SystemView, ...], positions: Positions) -> int:
    """Les paires de liens qui se coupent, extrémités communes exclues."""
    liens = sorted({(min(s.id, v), max(s.id, v)) for s in systemes for v in s.neighbors})

    def cote(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    total = 0
    for rang, (a, b) in enumerate(liens):
        for c, d in liens[rang + 1 :]:
            if len({a, b, c, d}) < 4:
                continue
            pa, pb, pc, pd = positions[a], positions[b], positions[c], positions[d]
            if cote(pa, pb, pc) * cote(pa, pb, pd) < 0 and cote(pc, pd, pa) * cote(pc, pd, pb) < 0:
                total += 1
    return total


def test_croisements_d_un_carre_et_de_ses_diagonales() -> None:
    systemes = (
        SystemView(1, (2, 3)),
        SystemView(2, (1, 4)),
        SystemView(3, (1, 4)),
        SystemView(4, (2, 3)),
    )
    carre = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (0.0, 1.0), 4: (1.0, 1.0)}
    assert croisements(systemes, carre) == 0
    croise = {1: (0.0, 0.0), 2: (1.0, 1.0), 3: (1.0, 0.0), 4: (0.0, 1.0)}
    assert croisements(systemes, croise) == 1


def traversees(systemes: tuple[SystemView, ...], positions: Positions) -> int:
    """Les liens qui traversent le cadre d'un autre système, au zoom 1 sur la carte minimale."""
    vue = initial_view(*CARTE_MINIMALE)
    cadres = {}
    for s in systemes:
        colonne, ligne = anchor(vue, positions[s.id])
        cadres[s.id] = {
            (colonne + dx, ligne + dy) for dx in range(LARGEUR_CADRE) for dy in range(HAUTEUR_CADRE)
        }
    liens = sorted({(min(s.id, v), max(s.id, v)) for s in systemes for v in s.neighbors})
    total = 0
    for a, b in liens:
        trace = _cases_du_trait(
            _centre_du_cadre(vue, positions[a]), _centre_du_cadre(vue, positions[b])
        )
        if any(set(trace) & cadres[c] for c in cadres if c not in (a, b)):
            total += 1
    return total


@pytest.mark.lent
def test_les_graines_1_a_2000() -> None:
    comptes = []
    traverses = 0
    for graine in range(1, 2001):
        verifier_carte(graine)  # disposition, et grille au zoom 1 en 72 × 27 et 52 × 21
        systemes = systemes_de(graine)
        positions = force_layout(systemes)
        comptes.append(croisements(systemes, positions))
        traverses += traversees(systemes, positions)
    moyenne = sum(comptes) / len(comptes)
    part = sum(1 for c in comptes if c) / len(comptes)
    print(
        f"\ncroisements de liens sur les graines 1 à 2000 : moyenne {moyenne:.2f}, "
        f"maximum {max(comptes)}, part des mondes qui en ont {part:.0%} ; "
        f"liens qui traversent le cadre d'un autre système : {traverses}"
    )
