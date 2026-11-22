"""Tests de fourx.clients.guide (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter,
prochaine étape ; plan détaillé, point 23 nonies).

Carte de tests/aide_observation.py : chaîne system_1 – system_2 – system_3, station S1 dans
system_1 (prix a 10, b 15), gisement 1 de ore_a dans system_2, gisement 2 de ore_b dans system_3 ;
jump_ticks 5, mining_rate 10, capacité 100. Les observations sont fabriquées : la visibilité du
stock n'y suit pas toujours la proximité, ce qui ne change rien à une fonction pure.
"""

import dataclasses

import msgspec
import pytest

from fourx.clients.guide import Step, best_sale, next_step
from fourx.clients.model import ClientModel
from fourx.schema.actors import Activity
from fourx.schema.events import Arrived
from fourx.schema.observation import (
    DepositView,
    Observation,
    OtherShipView,
    OwnShipView,
    StationView,
    SystemView,
)
from fourx.schema.orders import Mine, Move
from fourx.schema.protocol import PROTOCOL_VERSION, TickUpdate
from tests.aide_observation import ACTEUR, navire, observation
from tests.clients.test_model import evenement


def modele_de(obs: Observation) -> ClientModel:
    modele = ClientModel(ACTEUR)
    modele.on_update(TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs))
    return modele


def etape(obs: Observation) -> Step:
    return next_step(modele_de(obs))


def avec_autre_vaisseau(obs: Observation, systeme: int) -> Observation:
    autre = OtherShipView(id=9, owner_id=2, system_id=systeme, capacity=100)
    return msgspec.structs.replace(obs, other_ships=(autre,))


def deux_stations(obs: Observation, s1: tuple[int, int], s2: tuple[int, int]) -> Observation:
    """S1 dans system_1 et S2 dans system_3, aux prix donnés."""
    stations = (
        StationView(id=1, system_id=1, ore_prices=s1),
        StationView(id=2, system_id=3, ore_prices=s2),
    )
    return msgspec.structs.replace(obs, stations=stations)


# --- Règles 0 à 4


def test_regle_0_aucune_observation() -> None:
    assert next_step(ClientModel(ACTEUR)) == Step("En attente du premier tick", "", (), None)


def test_regle_0_bis_aucun_vaisseau() -> None:
    assert etape(observation(())) == Step("Aucun vaisseau", "", (), None)


def test_regle_1_une_alerte_puis_plusieurs() -> None:
    modele = ClientModel(ACTEUR)
    for systeme, tick in ((2, 7), (3, 8)):
        obs = msgspec.structs.replace(
            observation(
                (navire(system=systeme),),
                evenements=(evenement(Arrived(ship_id=1, system_id=systeme)),),
            ),
            tick=tick,
        )
        modele.on_update(TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs))
    assert next_step(modele) == Step(
        "arrivée : system_2 (+1)", "Entrée : acquitter", ("enter",), None
    )
    modele.acknowledge()
    assert next_step(modele) == Step("arrivée : system_3", "Entrée : acquitter", ("enter",), None)


def test_regle_2_des_ordres_attendent_leur_resultat() -> None:
    modele = modele_de(observation((navire(system=1),)))
    modele.send(Mine(ship_id=1, ore_id=2))
    modele.send(Move(ship_id=1, target_system_id=3))
    assert next_step(modele) == Step(
        "Ordre envoyé : miner ore_b ; déplacer vers system_3",
        "résultat au prochain tick",
        (),
        None,
    )


def test_regle_3_en_route() -> None:
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    assert etape(observation((en_route,))) == Step(
        "En route vers system_3", "arrivée dans 7 ticks (≈ 21 s à 3 s)", (), None
    )


def test_regle_4_en_minage_et_au_plus_avec_un_autre_vaisseau() -> None:
    en_minage = msgspec.structs.replace(
        navire(system=3, activity=Activity.MINING, cargo=(0, 38)), mining_ore_id=2
    )
    obs = observation((en_minage,))
    assert etape(obs) == Step(
        "Minage de ore_b",
        "fin du minage dans 7 ticks (≈ 21 s à 3 s) : cargaison pleine ou gisement vide",
        (),
        None,
    )
    assert etape(avec_autre_vaisseau(obs, 3)).detail == (
        "fin du minage dans au plus 7 ticks (≈ 21 s à 3 s) : cargaison pleine ou gisement vide"
    )
    assert etape(avec_autre_vaisseau(obs, 2)).detail.startswith("fin du minage dans 7 ticks")


# --- Règle 5, la vente


def test_regle_5_cargaison_non_vide_dans_le_systeme_d_une_station() -> None:
    assert etape(observation((navire(system=1, cargo=(30, 0)),))) == Step(
        "Vendre la cargaison ici", "valeur avant taxe : 300", ("v",), None
    )


def test_regle_5_cargaison_pleine_ailleurs() -> None:
    assert etape(observation((navire(system=3, cargo=(0, 100)),))) == Step(
        "Aller vendre à S1",
        "2 sauts, 10 ticks (≈ 30 s à 3 s) ; valeur avant taxe : 1500",
        ("d",),
        Move(ship_id=1, target_system_id=1),
    )


# --- best_sale


def test_best_sale_le_plus_grand_gain_par_tick() -> None:
    obs = deux_stations(observation(), (10, 15), (20, 15))
    # Depuis system_1 : S1 vaut 1000 ÷ 1, S2 2000 ÷ 11 ; depuis system_2 : 1000 ÷ 6 et 2000 ÷ 6.
    assert best_sale(obs, 1, (100, 0)) == (1, 1000, 0)
    assert best_sale(obs, 2, (100, 0)) == (2, 2000, 5)
    assert best_sale(obs, 2, (30, 70)) == (2, 1650, 5)  # cargaison mêlée : 600 + 1050


def test_best_sale_a_egalite_la_plus_proche_puis_le_plus_petit_identifiant() -> None:
    # S1 dans system_3 à 11, S2 dans system_1 à 1 : depuis system_1, 110 ÷ 11 = 10 ÷ 1.
    stations = (
        StationView(id=1, system_id=3, ore_prices=(11, 15)),
        StationView(id=2, system_id=1, ore_prices=(1, 15)),
    )
    obs = msgspec.structs.replace(observation(), stations=stations)
    assert best_sale(obs, 1, (10, 0)) == (2, 10, 0)
    # Même gain, même distance depuis system_2 : le plus petit identifiant.
    pareilles = deux_stations(observation(), (10, 15), (10, 15))
    assert best_sale(pareilles, 2, (100, 0)) == (1, 1000, 5)


def test_best_sale_ignore_les_stations_inaccessibles() -> None:
    obs = msgspec.structs.replace(
        deux_stations(observation(), (10, 15), (99, 99)),
        systems=(
            SystemView(id=1, neighbors=(2,)),
            SystemView(id=2, neighbors=(1,)),
            SystemView(id=3, neighbors=()),
        ),
    )
    assert best_sale(obs, 2, (100, 0)) == (1, 1000, 5)
    seule = msgspec.structs.replace(obs, stations=obs.stations[1:])
    assert best_sale(seule, 1, (100, 0)) is None


# --- Règle 6, le cycle


def test_regle_6_egalite_de_gain_par_tick_le_plus_petit_cycle() -> None:
    # Depuis system_1 : gisement 1, 1000 ÷ (5 + 10 + 5) = 50 ;
    # gisement 2, 1500 ÷ (10 + 10 + 10) = 50.
    assert etape(observation((navire(system=1),))) == Step(
        "Aller miner ore_a à system_2",
        "1 saut, 5 ticks (≈ 15 s à 3 s) ; cycle complet estimé : 20 ticks (≈ 1 min à 3 s)",
        ("d",),
        Move(ship_id=1, target_system_id=2),
    )


def test_regle_6_miner_ici_et_au_plus() -> None:
    # Depuis system_2 : gisement 1, 1000 ÷ 15 ; gisement 2, 1500 ÷ 25.
    obs = observation((navire(system=2),))
    assert etape(obs) == Step(
        "Miner ore_a ici",
        "fin du minage dans 10 ticks (≈ 30 s à 3 s) ; puis vendre à S1 (1 saut)",
        ("m",),
        Mine(ship_id=1, ore_id=1),
    )
    assert etape(avec_autre_vaisseau(obs, 2)).detail == (
        "fin du minage dans au plus 10 ticks (≈ 30 s à 3 s) ; puis vendre à S1 (1 saut)"
    )


def test_regle_6_miner_ici_puis_vendre_ici() -> None:
    gisements = (DepositView(id=1, system_id=1, ore_id=1, stock=20000),)
    obs = msgspec.structs.replace(observation((navire(system=1),)), deposits=gisements)
    assert etape(obs) == Step(
        "Miner ore_a ici",
        "fin du minage dans 10 ticks (≈ 30 s à 3 s) ; puis vendre ici",
        ("m",),
        Mine(ship_id=1, ore_id=1),
    )


def test_regle_6_le_stock_visible_borne_la_quantite() -> None:
    # Depuis system_2, stock 30 : gisement 1, 300 ÷ (0 + 3 + 5) ; gisement 2, 1500 ÷ 25.
    obs = observation((navire(system=2),), stocks=(30, 20000))
    assert etape(obs) == Step(
        "Aller miner ore_b à system_3",
        "1 saut, 5 ticks (≈ 15 s à 3 s) ; cycle complet estimé : 25 ticks (≈ 1 min 15 s à 3 s)",
        ("d",),
        Move(ship_id=1, target_system_id=3),
    )
    # Stock 80 : 800 ÷ (8 + 5) ≈ 61,5 l'emporte sur 60 ; le minage dure 8 ticks.
    assert etape(observation((navire(system=2),), stocks=(80, 20000))).detail == (
        "fin du minage dans 8 ticks (≈ 24 s à 3 s) ; puis vendre à S1 (1 saut)"
    )


def test_regle_6_stock_inconnu() -> None:
    obs = observation((navire(system=1),), stocks=(20000, None), prix=(10, 30))
    assert etape(obs).detail == (
        "2 sauts, 10 ticks (≈ 30 s à 3 s) ; cycle complet estimé : 30 ticks (≈ 1 min 30 s à 3 s)"
        " (stock inconnu)"
    )


def test_regle_6_un_gisement_vide_ou_vu_vide_est_ecarte() -> None:
    vide = observation((navire(system=1),), stocks=(0, 20000))
    assert etape(vide).title == "Aller miner ore_b à system_3"
    modele = modele_de(observation((navire(system=1),), stocks=(None, 20000)))
    assert next_step(modele).title == "Aller miner ore_a à system_2"
    modele.seen_empty = frozenset({1})
    assert next_step(modele).title == "Aller miner ore_b à system_3"


def test_regle_6_cargaison_melee() -> None:
    # Depuis system_2, cargaison (20, 30), 50 libres : gisement 1, 1150 ÷ 10 ;
    # gisement 2, 1400 ÷ 20 ; vente directe, 650 ÷ 6.
    assert etape(observation((navire(system=2, cargo=(20, 30)),))) == Step(
        "Miner ore_a ici",
        "fin du minage dans 5 ticks (≈ 15 s à 3 s) ; puis vendre à S1 (1 saut)",
        ("m",),
        Mine(ship_id=1, ore_id=1),
    )


def test_regle_6_cargaison_a_99_sur_100() -> None:
    # Gisement 1 : 1000 ÷ (0 + 1 + 5) ; vente directe : 990 ÷ (5 + 1).
    assert etape(observation((navire(system=2, cargo=(99, 0)),))) == Step(
        "Miner ore_a ici",
        "fin du minage dans 1 tick (≈ 3 s à 3 s) ; puis vendre à S1 (1 saut)",
        ("m",),
        Mine(ship_id=1, ore_id=1),
    )


def test_regle_6_vente_directe_a_egalite_avant_les_gisements() -> None:
    # Prix de ore_a à 0, cargaison (0, 90) dans system_2 : la vente directe vaut 900 ÷ (5 + 1) ;
    # le gisement 1, 900 ÷ (0 + 1 + 5) : même gain par tick, même durée, la vente passe avant.
    # Le gisement 2 vaut 1000 ÷ (5 + 1 + 10).
    obs = observation((navire(system=2, cargo=(0, 90)),), prix=(0, 10))
    assert etape(obs) == Step(
        "Aller vendre à S1",
        "1 saut, 5 ticks (≈ 15 s à 3 s) ; valeur avant taxe : 900",
        ("d",),
        Move(ship_id=1, target_system_id=1),
    )


def test_regle_6_la_vente_directe_l_emporte() -> None:
    # Cargaison (0, 60) : vente directe 600 ÷ 6 ; gisement 1, 600 ÷ (0 + 4 + 5) ;
    # gisement 2, 1000 ÷ (5 + 4 + 10).
    obs = observation((navire(system=2, cargo=(0, 60)),), prix=(0, 10))
    assert etape(obs).title == "Aller vendre à S1"


def test_regle_6_cargaison_non_vide_sans_gisement_candidat() -> None:
    obs = observation((navire(system=2, cargo=(50, 0)),), stocks=(0, 0))
    assert etape(obs) == Step(
        "Aller vendre à S1",
        "1 saut, 5 ticks (≈ 15 s à 3 s) ; valeur avant taxe : 500",
        ("d",),
        Move(ship_id=1, target_system_id=1),
    )


def test_regle_6_aucun_candidat() -> None:
    assert etape(observation((navire(system=2),), stocks=(0, 0))) == Step(
        "Aucun gisement connu disponible",
        "tous les gisements connus sont vides : attendre leur régénération",
        (),
        None,
    )


def test_regle_6_un_systeme_inaccessible_est_ignore() -> None:
    obs = msgspec.structs.replace(
        observation((navire(system=1),), prix=(10, 30)),
        systems=(
            SystemView(id=1, neighbors=(2,)),
            SystemView(id=2, neighbors=(1,)),
            SystemView(id=3, neighbors=()),
        ),
    )
    # Accessible, le gisement 2 l'emporterait (3000 ÷ 30 contre 1000 ÷ 20).
    assert etape(obs).title == "Aller miner ore_a à system_2"


def test_la_station_du_cycle_est_celle_de_la_vente_une_fois_la_cargaison_pleine() -> None:
    obs = deux_stations(observation((navire(system=2),)), (10, 15), (20, 15))
    assert etape(obs).detail.endswith("puis vendre à S2 (1 saut)")
    plein = deux_stations(observation((navire(system=2, cargo=(100, 0)),)), (10, 15), (20, 15))
    assert etape(plein).title == "Aller vendre à S2"


def chaine_de_quatre(depart: int) -> Observation:
    """system_1 – system_2 – system_3 – system_4 ; S1 dans system_1 (a 20, b 31) ; gisement 1 de
    ore_a dans system_3 (stock 20000), gisement 2 de ore_b dans system_2 (stock 50)."""
    return msgspec.structs.replace(
        observation((navire(system=depart),)),
        systems=(
            SystemView(id=1, neighbors=(2,)),
            SystemView(id=2, neighbors=(1, 3)),
            SystemView(id=3, neighbors=(2, 4)),
            SystemView(id=4, neighbors=(3,)),
        ),
        deposits=(
            DepositView(id=1, system_id=3, ore_id=1, stock=20000),
            DepositView(id=2, system_id=2, ore_id=2, stock=50),
        ),
        stations=(StationView(id=1, system_id=1, ore_prices=(20, 31)),),
    )


def test_un_gisement_cede_la_place_a_l_arrivee() -> None:
    # Depuis system_4 : gisement 1, 2000 ÷ (5 + 10 + 10) = 80 ; gisement 2, 1550 ÷ (10 + 5 + 5)
    # = 77,5. Depuis system_3, l'approche ne compte plus : 2000 ÷ 20 = 100 contre
    # 1550 ÷ (5 + 5 + 5) ≈ 103,3.
    assert etape(chaine_de_quatre(4)).title == "Aller miner ore_a à system_3"
    assert etape(chaine_de_quatre(3)).title == "Aller miner ore_b à system_2"


def test_step_est_gele() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        etape(observation(())).title = "autre"  # type: ignore[misc]


def test_un_vaisseau_d_un_autre_systeme_ne_compte_pas_pour_au_plus() -> None:
    autre: OwnShipView = navire(system=2)
    assert "au plus" not in etape(avec_autre_vaisseau(observation((autre,)), 3)).detail
