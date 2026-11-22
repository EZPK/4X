"""Tests de fourx.clients.map_view (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter,
vue de la carte ; plan détaillé, point 23 decies).

Carte de tests/aide_observation.py : chaîne system_1 – system_2 – system_3, S1 dans system_1,
ore_a dans system_2, ore_b dans system_3 ; jump_ticks 5. Les positions sont fixées à la main :
system_1 en (0,2 ; 0,5), system_2 en (0,5 ; 0,5), system_3 en (0,8 ; 0,5). En 72 × 27 au zoom 1,
l'échelle vaut 54 pixels par unité : les cases d'ancrage sont (20, 13), (36, 13) et (52, 13).
"""

import msgspec
import pytest

from fourx.clients.map_view import (
    VIDE,
    ZOOMS,
    Cell,
    View,
    anchor,
    center_on,
    in_range,
    initial_view,
    pan,
    render,
    ship_position,
    system_at,
    to_pixels,
    zoom,
)
from fourx.clients.model import ClientModel
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OtherShipView
from fourx.schema.protocol import PROTOCOL_VERSION, TickUpdate
from tests.aide_observation import ACTEUR, navire, observation

POSITIONS = {1: (0.2, 0.5), 2: (0.5, 0.5), 3: (0.8, 0.5)}
VUE = initial_view(72, 27)


def modele_de(obs: Observation) -> ClientModel:
    modele = ClientModel(ACTEUR)
    modele.on_update(TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs))
    return modele


def texte(grille: tuple[tuple[Cell, ...], ...], ligne: int, debut: int, fin: int) -> str:
    return "".join(c.char for c in grille[ligne][debut:fin])


# --- Projection, zoom, déplacement


def test_projection_et_cases_d_ancrage() -> None:
    assert VUE == View(zoom_index=0, center=(0.5, 0.5), width=72, height=27)
    assert to_pixels(VUE, (0.5, 0.5)) == (36.0, 27.0)
    assert to_pixels(VUE, (0.0, 0.0)) == (9.0, 0.0)  # le carré occupe toute la hauteur
    assert to_pixels(VUE, (1.0, 1.0)) == (63.0, 54.0)
    assert [anchor(VUE, POSITIONS[i]) for i in (1, 2, 3)] == [(20, 13), (36, 13), (52, 13)]
    assert anchor(VUE, (0.5, 0.49)) == (36, 13)  # ⌊26,46 ÷ 2⌋
    assert anchor(VUE, (0.5, 0.48)) == (36, 12)  # ⌊25,92 ÷ 2⌋


def test_zoom_autour_du_centre_et_bornes() -> None:
    avant = zoom(VUE, 1, None)
    assert avant == View(1, (0.5, 0.5), 72, 27)
    assert zoom(VUE, -1, None) is VUE
    au_bout = View(len(ZOOMS) - 1, (0.5, 0.5), 72, 27)
    assert zoom(au_bout, 1, None) is au_bout


def test_zoom_autour_d_une_case_garde_le_point_sous_la_case() -> None:
    case = (10, 5)
    point = ((10 - 36) / 54 + 0.5, (11 - 27) / 54 + 0.5)  # centre de la case
    apres = zoom(VUE, 1, case)
    assert apres.zoom_index == 1
    assert to_pixels(apres, point) == pytest.approx((10, 11))
    # Le centre reste dans le carré, même autour d'une case du bord.
    loin = zoom(View(0, (0.0, 0.0), 72, 27), 1, (0, 0))
    assert 0 <= loin.center[0] <= 1 and 0 <= loin.center[1] <= 1


def test_pan_deplace_en_colonnes_et_en_lignes_et_reste_dans_le_carre() -> None:
    assert pan(VUE, 5, 3).center == pytest.approx((0.5 + 5 / 54, 0.5 + 6 / 54))
    assert pan(VUE, 1000, -1000).center == (1.0, 0.0)
    assert center_on(VUE, (1.4, -0.2)).center == (1.0, 0.0)
    assert center_on(VUE, (0.3, 0.6)).center == (0.3, 0.6)


def test_systeme_sous_le_pointeur() -> None:
    assert system_at(VUE, POSITIONS, 20, 13) == 1
    assert system_at(VUE, POSITIONS, 21, 13) == 1
    assert system_at(VUE, POSITIONS, 22, 13) is None
    assert system_at(VUE, POSITIONS, 20, 12) is None
    assert system_at(VUE, POSITIONS, 52, 13) == 3


# --- Portée et position du vaisseau


def test_portee_et_position_du_vaisseau() -> None:
    obs = observation((navire(system=1),))
    assert in_range(obs, obs.own_ships[0]) == frozenset({1, 2})
    assert in_range(obs, None) == frozenset()
    assert ship_position(modele_de(obs), POSITIONS) == (0.2, 0.5)
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    # Fraction 1 − 2 ÷ 5 = 0,6 du lien system_1 – system_2.
    assert ship_position(modele_de(observation((en_route,))), POSITIONS) == pytest.approx(
        (0.38, 0.5)
    )
    assert ship_position(modele_de(observation(())), POSITIONS) is None


# --- La grille


def test_grille_vide_sans_observation() -> None:
    grille = render(VUE, POSITIONS, ClientModel(ACTEUR), None)
    assert len(grille) == 27 and all(len(ligne) == 72 for ligne in grille)
    assert all(c == VIDE for ligne in grille for c in ligne)


def test_pastilles_gisements_et_vaisseau() -> None:
    grille = render(VUE, POSITIONS, modele_de(observation((navire(system=1),))), None)
    # Pastilles : station (system_1), à portée (system_2), hors de portée (system_3).
    assert grille[13][20:22] == (Cell(" ", "fond", "station"), Cell("1", "fond", "station"))
    assert grille[13][36:38] == (
        Cell(" ", "texte", "cadre_clair"),
        Cell("2", "texte", "cadre_clair"),
    )
    assert grille[13][52:54] == (
        Cell(" ", "texte_attenue", "fond"),
        Cell("3", "texte_attenue", "fond"),
    )
    # Gisements, juste après la pastille.
    assert grille[13][38:40] == (Cell("◆", "ore_a", "fond"), Cell("a", "ore_a", "fond"))
    assert grille[13][54:56] == (Cell("◆", "ore_b", "fond"), Cell("b", "ore_b", "fond"))
    # Le vaisseau du joueur, sur la ligne au-dessus de sa pastille.
    assert grille[12][20] == Cell("▲", "vaisseau", "fond")


def test_liens_pleins_a_portee_un_pixel_sur_deux_sinon() -> None:
    grille = render(VUE, POSITIONS, modele_de(observation((navire(system=1),))), None)
    # Le lien system_1 – system_2 (à portée) passe par le pixel du bas de la ligne 13.
    assert grille[13][28] == Cell("▀", "fond", "trait_fort")
    assert grille[13][29] == Cell("▀", "fond", "trait_fort")
    # system_2 – system_3 : un pixel sur deux à partir de (36, 27).
    assert grille[13][44] == Cell("▀", "fond", "trait_faible")
    assert grille[13][45] == VIDE


def test_route_trois_pixels_sur_quatre_et_vaisseau_sur_le_lien() -> None:
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    grille = render(VUE, POSITIONS, modele_de(observation((en_route,))), None)
    assert grille[13][24] == Cell("▀", "fond", "vaisseau")  # rang 4 de la route
    assert grille[13][23] == Cell("▀", "fond", "trait_fort")  # rang 3 : le lien dessous
    assert grille[13][48] == Cell("▀", "fond", "vaisseau")  # route jusqu'à system_3 (rang 12)
    assert grille[13][30] == Cell("▲", "vaisseau", "fond")  # 0,6 du lien : x = 29,52
    assert grille[12][20] != Cell("▲", "vaisseau", "fond")


def test_vaisseaux_proches_et_leur_nombre() -> None:
    autres = (
        OtherShipView(id=7, owner_id=2, system_id=2, capacity=100),
        OtherShipView(id=8, owner_id=3, system_id=2, capacity=100),
        OtherShipView(id=9, owner_id=3, system_id=1, capacity=100),
    )
    obs = msgspec.structs.replace(observation((navire(system=1),)), other_ships=autres)
    grille = render(VUE, POSITIONS, modele_de(obs), None)
    assert grille[12][36:38] == (
        Cell("▲", "texte_attenue", "fond"),
        Cell("2", "texte_attenue", "fond"),
    )
    assert grille[12][20:22] == (Cell("▲", "vaisseau", "fond"), Cell("▲", "texte_attenue", "fond"))
    assert grille[12][22] == VIDE


def test_le_systeme_survole() -> None:
    grille = render(VUE, POSITIONS, modele_de(observation((navire(system=1),))), 3)
    assert grille[13][53] == Cell("3", "fond", "accent")
    survole_station = render(VUE, POSITIONS, modele_de(observation((navire(system=1),))), 1)
    assert survole_station[13][21] == Cell("1", "fond", "accent")


def test_ordre_de_dessin_les_systemes_couvrent_les_liens() -> None:
    grille = render(VUE, POSITIONS, modele_de(observation((navire(system=1),))), None)
    # Le lien system_1 – system_2 part de la case d'ancrage de system_1 : la pastille la couvre.
    assert grille[13][20].bg == "station" and grille[13][21].bg == "station"


def test_etiquettes_a_partir_du_zoom_2_par_mots_entiers() -> None:
    modele = modele_de(observation((navire(system=1),)))
    assert all(
        c.char in " ▀◆ab▲123"
        for ligne in render(zoom(VUE, 1, None), POSITIONS, modele, None)
        for c in ligne
    )
    vue = View(2, (0.5, 0.5), 72, 27)  # 108 pixels par unité
    positions = {1: (0.2, 0.5), 2: (0.5, 0.5), 3: (0.74, 0.5)}
    grille = render(vue, positions, modele, None)
    # system_1 en colonne 4, sans gisement : étiquettes à partir de la colonne 7.
    assert texte(grille, 13, 7, 15) == "system_1"
    assert texte(grille, 14, 7, 17) == "S1 a10 b15"
    assert grille[14][7].fg == "station" and grille[14][10].fg == "ore_a"
    # system_2 en colonne 36, gisement en 38 et 39 : étiquettes à partir de 41.
    assert texte(grille, 13, 41, 49) == "system_2"
    assert texte(grille, 14, 41, 46) == "20000"
    # system_3 en colonne 62, gisement en 64 et 65 : 5 cases avant le bord.
    assert texte(grille, 13, 67, 72) == "…    "  # « system_3 » ne tient pas
    assert texte(grille, 14, 67, 72) == "20000"  # tient tout juste


def test_un_mot_ne_coupe_jamais_un_nombre() -> None:
    modele = modele_de(observation((navire(system=1),), prix=(10, 15)))
    vue = View(2, (0.5, 0.5), 72, 27)
    # system_1 en colonne 4 ; system_2 placé pour occuper la ligne 14 à partir de la colonne 14.
    positions = {1: (0.2, 0.5), 2: (0.2 + 10 / 108, 0.5 + 2 / 108), 3: (0.9, 0.2)}
    grille = render(vue, positions, modele, None)
    # « b15 » ne tient pas avant la pastille de system_2 (colonne 14) : ni écrit, ni coupé.
    assert texte(grille, 14, 7, 13) == "S1 a10"
    assert texte(grille, 14, 14, 16) == " 2"
    assert "b" not in texte(grille, 14, 7, 14)
