"""Tests de fourx.clients.map_view (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter,
vue de la carte ; plan détaillé, point 23 decies).

Carte de tests/aide_observation.py : chaîne system_1 – system_2 – system_3, S1 dans system_1,
ore_a dans system_2, ore_b dans system_3 ; jump_ticks 5. Les positions sont fixées à la main :
system_1 en (0,1 ; 0,4), system_2 en (0,4 ; 0,4), system_3 en (0,7 ; 0,4). Sur une carte de
70 × 23 au zoom 1, une colonne vaut x × 70 et une ligne y × 23 : les cadres ont leur coin en
haut à gauche en (7, 9), (28, 9) et (49, 9), et leur centre en (8,5 ; 10), (29,5 ; 10), (50,5 ; 10).
"""

import msgspec
import pytest

from fourx.clients.map_view import (
    VIDE,
    ZOOMS,
    Cell,
    View,
    _points,
    anchor,
    case_du_point,
    center_on,
    in_range,
    initial_view,
    pan,
    render,
    ship_position,
    system_at,
    to_cells,
    zoom,
)
from fourx.clients.model import ClientModel
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OtherShipView
from fourx.schema.protocol import PROTOCOL_VERSION, TickUpdate
from tests.aide_observation import ACTEUR, navire, observation

POSITIONS = {1: (0.1, 0.4), 2: (0.4, 0.4), 3: (0.7, 0.4)}
VUE = initial_view(70, 23)


def modele_de(obs: Observation) -> ClientModel:
    modele = ClientModel(ACTEUR)
    modele.on_update(TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs))
    return modele


def texte(grille: tuple[tuple[Cell, ...], ...], ligne: int, debut: int, fin: int) -> str:
    return "".join(c.char for c in grille[ligne][debut:fin])


def a_l_arret() -> ClientModel:
    return modele_de(observation((navire(system=1),)))


# --- Projection, zoom, déplacement


def test_projection_et_cases_d_ancrage() -> None:
    assert VUE == View(zoom_index=0, center=(0.5, 0.5), width=70, height=23)
    assert to_cells(VUE, (0.0, 0.0)) == (0.0, 0.0)  # le carré couvre toute la carte
    assert to_cells(VUE, (1.0, 1.0)) == (70.0, 23.0)
    assert to_cells(VUE, (0.5, 0.5)) == (35.0, 11.5)
    assert [anchor(VUE, POSITIONS[i]) for i in (1, 2, 3)] == [(7, 9), (28, 9), (49, 9)]


def test_zoom_autour_du_centre_et_bornes() -> None:
    assert zoom(VUE, 1, None) == View(1, (0.5, 0.5), 70, 23)
    assert zoom(VUE, -1, None) is VUE
    au_bout = View(len(ZOOMS) - 1, (0.5, 0.5), 70, 23)
    assert zoom(au_bout, 1, None) is au_bout


def test_zoom_autour_d_une_case_garde_le_point_sous_la_case() -> None:
    point = ((10.5 - 35) / 70 + 0.5, (5.5 - 11.5) / 23 + 0.5)  # centre de la case (10, 5)
    apres = zoom(VUE, 1, (10, 5))
    assert apres.zoom_index == 1
    assert to_cells(apres, point) == pytest.approx((10.5, 5.5))
    loin = zoom(View(0, (0.0, 0.0), 70, 23), 1, (0, 0))
    assert 0 <= loin.center[0] <= 1 and 0 <= loin.center[1] <= 1


def test_pan_deplace_en_colonnes_et_en_lignes_et_reste_dans_le_carre() -> None:
    assert pan(VUE, 7, 2).center == pytest.approx((0.6, 0.5 + 2 / 23))
    assert pan(VUE, 1000, -1000).center == (1.0, 0.0)
    assert center_on(VUE, (1.4, -0.2)).center == (1.0, 0.0)
    assert center_on(VUE, (0.3, 0.6)).center == (0.3, 0.6)


def test_systeme_sous_le_pointeur_le_cadre_entier() -> None:
    assert system_at(VUE, POSITIONS, 7, 9) == 1
    assert system_at(VUE, POSITIONS, 10, 11) == 1
    assert system_at(VUE, POSITIONS, 11, 10) is None
    assert system_at(VUE, POSITIONS, 7, 12) is None
    assert system_at(VUE, POSITIONS, 50, 10) == 3


def test_les_points_braille_d_un_trait() -> None:
    # Le trait de (0, 0) à (5, 2), en points : Bresenham, dans l'ordre.
    assert _points((0.0, 0.0), (5.0, 2.0)) == [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]
    assert _points((3.0, 3.0), (3.0, 3.0)) == [(3, 3)]
    assert case_du_point((5, 9)) == (2, 2)  # 2 points par colonne, 4 par ligne


# --- Portée et position du vaisseau


def test_portee_et_position_du_vaisseau() -> None:
    obs = observation((navire(system=1),))
    assert in_range(obs, obs.own_ships[0]) == frozenset({1, 2})
    assert in_range(obs, None) == frozenset()
    assert ship_position(a_l_arret(), POSITIONS) == (0.1, 0.4)
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    # Fraction 1 − 2 ÷ 5 = 0,6 du lien system_1 – system_2.
    position = ship_position(modele_de(observation((en_route,))), POSITIONS)
    assert position == pytest.approx((0.28, 0.4))
    assert ship_position(modele_de(observation(())), POSITIONS) is None


# --- La grille


def test_grille_vide_sans_observation() -> None:
    grille = render(VUE, POSITIONS, ClientModel(ACTEUR), None)
    assert len(grille) == 23 and all(len(ligne) == 70 for ligne in grille)
    assert all(c == VIDE for ligne in grille for c in ligne)


def test_cadres_a_portee_et_loin() -> None:
    grille = render(VUE, POSITIONS, a_l_arret(), None)
    # system_2, à portée : cadre plein, numéro sur cadre_clair.
    assert texte(grille, 9, 28, 32) == "┌──┐" and grille[9][28].fg == "texte"
    assert texte(grille, 10, 28, 32) == "│ 2│"
    assert grille[10][30] == Cell("2", "texte", "cadre_clair")
    assert texte(grille, 11, 28, 32) == "└──┘"
    # system_3, hors de portée : cadre en tirets, atténué.
    assert texte(grille, 9, 49, 53) == "┌┄┄┐" and grille[9][49].fg == "texte_attenue"
    assert texte(grille, 10, 49, 53) == "┆ 3┆"
    assert grille[10][51] == Cell("3", "texte_attenue", "fond")


def test_station_gisement_et_stock() -> None:
    grille = render(VUE, POSITIONS, a_l_arret(), None)
    assert grille[9][11:13] == (Cell("S", "fond", "station"), Cell("1", "fond", "station"))
    assert grille[12][28] == Cell("◆", "ore_a", "fond")
    assert texte(grille, 12, 29, 34) == "20000" and grille[12][29].fg == "texte"
    inconnus = modele_de(observation((navire(system=1),), stocks=(None, None)))
    grille_inconnue = render(VUE, POSITIONS, inconnus, None)
    assert texte(grille_inconnue, 12, 28, 30) == "◆?"
    assert grille_inconnue[12][29].fg == "texte_attenue"


def test_le_vaisseau_a_l_arret_dans_la_bordure_de_son_cadre() -> None:
    grille = render(VUE, POSITIONS, a_l_arret(), None)
    assert grille[9][8] == Cell("▲", "vaisseau", "fond")
    assert texte(grille, 9, 7, 11) == "┌▲─┐"


def test_liens_traits_fins_a_portee_points_sinon() -> None:
    grille = render(VUE, POSITIONS, a_l_arret(), None)
    # Centres en points : (18, 42), (60, 42), (102, 42) ; la rangée 42 % 4 = 2 des cases.
    assert grille[10][20] == Cell("⠤", "trait_fort", "fond")  # system_1 – system_2, plein
    # system_2 – system_3, un point sur trois depuis (60, 42) : le point 81 est le rang 21.
    assert grille[10][40] == Cell("⠠", "trait_faible", "fond")
    assert grille[10][41] == VIDE
    assert grille[10][8].char == " " and grille[10][8].bg == "cadre_clair"  # le cadre couvre


def test_route_en_jaune_et_vaisseau_sur_son_lien() -> None:
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    grille = render(VUE, POSITIONS, modele_de(observation((en_route,))), None)
    assert grille[10][15] == Cell("⠤", "vaisseau", "fond")
    assert grille[10][40] == Cell("⠤", "vaisseau", "fond")  # la route couvre le lien lointain
    assert grille[10][21] == Cell("▲", "vaisseau", "fond")  # 8,5 + 0,6 × 21 = 21,1
    assert grille[9][8].char == "─"  # plus de ▲ dans la bordure du cadre


def test_le_vaisseau_en_route_ne_cache_ni_cadre_ni_etiquette() -> None:
    # Le saut vient de commencer : la case de sa fraction est dans le cadre de départ.
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2,)), ticks_to_next_jump=5
    )
    grille = render(VUE, POSITIONS, modele_de(observation((en_route,))), None)
    assert texte(grille, 10, 7, 11) == "│ 1│"
    assert grille[10][11] == Cell("▲", "vaisseau", "fond")  # première case libre du trait


def test_vaisseaux_proches_dans_la_bordure_du_bas() -> None:
    autres = (
        OtherShipView(id=7, owner_id=2, system_id=2, capacity=100),
        OtherShipView(id=8, owner_id=3, system_id=2, capacity=100),
        OtherShipView(id=9, owner_id=3, system_id=1, capacity=100),
    )
    obs = msgspec.structs.replace(observation((navire(system=1),)), other_ships=autres)
    grille = render(VUE, POSITIONS, modele_de(obs), None)
    assert texte(grille, 11, 28, 32) == "└▲2┘" and grille[11][29].fg == "texte_attenue"
    assert texte(grille, 11, 7, 11) == "└▲─┘"


def test_le_systeme_survole() -> None:
    grille = render(VUE, POSITIONS, a_l_arret(), 3)
    assert grille[9][49].fg == "accent" and grille[9][50].fg == "accent"
    assert grille[10][51] == Cell("3", "fond", "accent")


def test_etiquettes_a_partir_du_zoom_2() -> None:
    modele = a_l_arret()
    sans = render(zoom(VUE, 1, None), POSITIONS, modele, None)
    assert not any("system_" in "".join(c.char for c in ligne) for ligne in sans)
    vue = View(2, (0.5, 0.5), 70, 23)  # une colonne vaut (x − 0,5) × 140 + 35
    positions = {1: (0.3, 0.45), 2: (0.5, 0.45), 3: (0.6932, 0.45)}
    grille = render(vue, positions, modele, None)
    # system_1 en (7, 9), S1 en 11 et 12, ses prix à partir de 14 ; le libellé en 12.
    assert texte(grille, 9, 11, 21) == "S1 a10 b15"
    assert grille[9][14].fg == "ore_a" and grille[9][18].fg == "ore_b"
    assert texte(grille, 10, 12, 20) == "system_1"
    # system_2 en (35, 9) : le libellé en 40, le minerai et le stock sous le cadre.
    assert texte(grille, 10, 40, 48) == "system_2"
    assert texte(grille, 12, 35, 47) == "◆ore_a 20000"
    # system_3 en (62, 9) : 3 cases avant le bord, « system_3 » ne tient pas.
    assert texte(grille, 10, 67, 70) == "…  "


def test_un_mot_ne_coupe_jamais_un_nombre() -> None:
    vue = View(2, (0.5, 0.5), 70, 23)
    # Le cadre de system_2 occupe la colonne 19 de la ligne 9 : « b15 » n'y tient pas.
    positions = {1: (0.3, 0.45), 2: (0.3858, 0.424), 3: (0.9, 0.9)}
    grille = render(vue, positions, a_l_arret(), None)
    assert texte(grille, 9, 14, 17) == "a10"
    assert grille[9][18] == Cell("…", "texte_attenue", "fond")
    assert "b" not in texte(grille, 9, 14, 19)
