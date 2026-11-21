"""Tests de la politique `scripted_miner`, version 2 (docs/designs/niveau-2-m1-noyau.md,
Technical Plan, point 7 ; plan détaillé, point 23 quater)."""

import msgspec
import pytest

from fourx.core.observe import observe
from fourx.core.state import State
from fourx.policies.scripted_miner import POLICY_ID, POLICY_VERSION, decide, mettre_a_jour
from fourx.schema.actors import Activity
from fourx.schema.observation import DepositView, Observation, OwnShipView, SystemView
from fourx.schema.orders import Command, Mine, Move, OrderCategory, Sell, SubmittedOrder
from tests.aide_monde import REGLAGES, avancer, monde, vaisseau
from tests.aide_observation import ACTEUR, navire, observation


def commandes(obs: Observation, vus: frozenset[int] = frozenset()) -> list[Command]:
    return [o.command for o in decide(obs, vus)[0]]


@pytest.mark.parametrize(
    ("vue", "attendu"),
    [
        # Cargaison vide à la station : aller au minerai le mieux payé (ore_b, system_3).
        (navire(system=1), [Move(ship_id=1, target_system_id=3)]),
        # Arrivé au gisement : miner.
        (navire(system=3), [Mine(ship_id=1, ore_id=2)]),
        # Déjà en minage : aucun nouvel ordre.
        (navire(system=3, activity=Activity.MINING, cargo=(0, 40)), []),
        # En route : aucun ordre.
        (navire(system=2, activity=Activity.EN_ROUTE, route=(3,)), []),
        # Cargaison pleine loin de la station : aller à la station qui paie le mieux.
        (navire(system=3, cargo=(0, 100)), [Move(ship_id=1, target_system_id=1)]),
        # Cargaison pleine à la station : vendre.
        (navire(system=1, cargo=(0, 100)), [Sell(ship_id=1, ore_id=2, quantity=100)]),
        # Cargaison mêlée à la station : le plus abondant d'abord.
        (navire(system=1, cargo=(30, 70)), [Sell(ship_id=1, ore_id=2, quantity=70)]),
        # Reste de cargaison à la station : tout vendre avant de repartir.
        (navire(system=1, cargo=(30, 0)), [Sell(ship_id=1, ore_id=1, quantity=30)]),
        # Égalité de quantités : le minerai de plus petit identifiant.
        (navire(system=1, cargo=(50, 50)), [Sell(ship_id=1, ore_id=1, quantity=50)]),
        # Une seule unité à la station : la vendre aussi.
        (navire(system=1, cargo=(1, 0)), [Sell(ship_id=1, ore_id=1, quantity=1)]),
        # Pleine, en minage dans le système de la station : attendre la fin du minage.
        (navire(system=1, activity=Activity.MINING, cargo=(100, 0)), []),
        # Cargaison partielle loin de la station : continuer à miner.
        (navire(system=3, cargo=(0, 40)), [Mine(ship_id=1, ore_id=2)]),
    ],
)
def test_activite_voulue(vue: OwnShipView, attendu: list[Command]) -> None:
    assert commandes(observation((vue,))) == attendu


def test_gisement_le_mieux_paye_vide() -> None:
    obs = observation((navire(system=1),), stocks=(20000, 0))
    assert commandes(obs) == [Move(ship_id=1, target_system_id=2)]


def test_gisement_d_une_seule_unite_non_vide() -> None:
    obs = observation((navire(system=1),), stocks=(20000, 1))
    assert commandes(obs) == [Move(ship_id=1, target_system_id=3)]


def test_tous_les_gisements_vus_vides_l_ensemble_se_vide() -> None:
    """Tous les gisements sont vus vides : l'ensemble se vide, et le vaisseau recommence à
    chercher, au minerai le mieux payé."""
    obs = observation((navire(system=2),), stocks=(0, 0))
    ordres, vus = decide(obs, frozenset())
    assert vus == frozenset()
    assert [o.command for o in ordres] == [Move(ship_id=1, target_system_id=3)]


def test_egalite_de_prix_plus_petit_minerai() -> None:
    obs = observation((navire(system=1),), prix=(15, 15))
    assert commandes(obs) == [Move(ship_id=1, target_system_id=2)]


def test_champs_de_l_ordre() -> None:
    obs = observation((navire(1, system=1), navire(2, system=3, activity=Activity.MINING)), tick=7)
    (seul,) = decide(obs)[0]
    assert seul.actor_id == ACTEUR
    assert seul.number == 700
    assert seul.category is OrderCategory.PLAYER
    assert (seul.policy_id, seul.policy_version) == (POLICY_ID, POLICY_VERSION)
    assert (POLICY_ID, POLICY_VERSION) == ("scripted_miner", 2)


def test_numeros_par_rang_de_vaisseau() -> None:
    obs = observation((navire(1, system=1), navire(2, system=3)), tick=3)
    assert [o.number for o in decide(obs)[0]] == [300, 301]


# --- Mémoire des gisements vus vides, sur une chaîne de cinq systèmes


def chaine(systeme: int, gisements: tuple[DepositView, ...]) -> Observation:
    """Une chaîne 1–2–3–4–5, la station dans system_1 (ore_a 10, ore_b 15)."""
    systemes = tuple(
        SystemView(id=s, neighbors=tuple(v for v in (s - 1, s + 1) if 1 <= v <= 5))
        for s in range(1, 6)
    )
    return msgspec.structs.replace(
        observation((navire(system=systeme),)), systems=systemes, deposits=gisements
    )


def test_deux_gisements_proches_vides_le_vaisseau_va_plus_loin() -> None:
    """Les deux gisements de ore_b les plus proches sont vides : le vaisseau va miner le
    troisième, et ne revient pas vers un gisement vu vide devenu inconnu hors de portée."""
    obs = chaine(
        2,
        (
            DepositView(id=2, system_id=2, ore_id=2, stock=0),
            DepositView(id=4, system_id=3, ore_id=2, stock=0),
            DepositView(id=6, system_id=5, ore_id=2, stock=None),
            DepositView(id=1, system_id=1, ore_id=1, stock=20000),
        ),
    )
    ordres, vus = decide(obs, frozenset())
    assert vus == frozenset({2, 4})
    assert [o.command for o in ordres] == [Move(ship_id=1, target_system_id=5)]
    plus_loin = chaine(
        4,
        (
            DepositView(id=2, system_id=2, ore_id=2, stock=None),
            DepositView(id=4, system_id=3, ore_id=2, stock=0),
            DepositView(id=6, system_id=5, ore_id=2, stock=None),
            DepositView(id=1, system_id=1, ore_id=1, stock=None),
        ),
    )
    assert commandes(plus_loin, vus) == [Move(ship_id=1, target_system_id=5)]


def test_un_seul_gisement_vide_le_vaisseau_va_miner_l_autre() -> None:
    obs = chaine(
        3,
        (
            DepositView(id=2, system_id=3, ore_id=2, stock=0),
            DepositView(id=4, system_id=5, ore_id=2, stock=None),
            DepositView(id=1, system_id=1, ore_id=1, stock=None),
        ),
    )
    assert commandes(obs) == [Move(ship_id=1, target_system_id=5)]


def test_un_gisement_revu_plein_sort_de_l_ensemble() -> None:
    obs = chaine(2, (DepositView(id=2, system_id=2, ore_id=2, stock=100),))
    assert mettre_a_jour(obs, frozenset({2, 9})) == frozenset({9})


def test_l_ensemble_se_vide_quand_il_contient_tous_les_gisements() -> None:
    """Le dernier gisement vu vide complète l'ensemble : il se vide, et seuls les gisements vus
    vides à l'instant y rentrent."""
    obs = chaine(
        5,
        (
            DepositView(id=2, system_id=2, ore_id=2, stock=None),
            DepositView(id=6, system_id=5, ore_id=2, stock=0),
        ),
    )
    assert mettre_a_jour(obs, frozenset({2})) == frozenset({6})


# --- Sur le noyau


def _soumettre(state: State, obs_tick: int) -> tuple[SubmittedOrder, ...]:
    return tuple(
        SubmittedOrder(
            tick=obs_tick + 1, sender_actor_id=o.actor_id, order=o, reception_refusal=None
        )
        for o in decide(observe(state, ACTEUR, REGLAGES))[0]
    )


def test_aucun_ordre_pendant_dix_ticks_de_minage() -> None:
    state = monde((vaisseau(1, ACTEUR, system=3, capacity=200),))
    state, _ = avancer(state, _soumettre(state, state.tick))
    for _ in range(10):
        obs = observe(state, ACTEUR, REGLAGES)
        assert obs.own_ships[0].activity is Activity.MINING
        assert decide(obs)[0] == ()
        state, _ = avancer(state)
    # Le minage commence au tick de l'ordre : 1 + 10 ticks de minage.
    assert state.ships[0].cargo[1] == 11 * REGLAGES.mining_rate


def test_un_cycle_complet_rapporte() -> None:
    """Depuis la station, cargaison vide : aller, miner, revenir et vendre en moins de 40 ticks."""
    state = monde((vaisseau(1, ACTEUR, system=1),))
    for _ in range(40):
        state, _ = avancer(state, _soumettre(state, state.tick))
    obs = observe(state, ACTEUR, REGLAGES)
    assert obs.wallet_balance > 0
    assert sum(obs.own_ships[0].cargo) < REGLAGES.cargo_capacity
