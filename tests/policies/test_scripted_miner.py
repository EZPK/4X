"""Tests de la politique `scripted_miner` (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 7 ; plan détaillé, point 23)."""

import pytest

from fourx.core.observe import observe
from fourx.core.state import State
from fourx.policies.scripted_miner import POLICY_ID, POLICY_VERSION, decide
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OwnShipView
from fourx.schema.orders import Command, Mine, Move, OrderCategory, Sell, SubmittedOrder
from tests.aide_monde import REGLAGES, avancer, monde, vaisseau
from tests.aide_observation import ACTEUR, navire, observation


def commandes(obs: Observation) -> list[Command]:
    return [o.command for o in decide(obs)]


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
        # Cargaison pleine loin de la station : y aller.
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


def test_tous_les_gisements_vides() -> None:
    assert commandes(observation((navire(system=2),), stocks=(0, 0))) == []


def test_egalite_de_prix_plus_petit_gisement() -> None:
    obs = observation((navire(system=1),), prix=(15, 15))
    assert commandes(obs) == [Move(ship_id=1, target_system_id=2)]


def test_champs_de_l_ordre() -> None:
    obs = observation((navire(1, system=1), navire(2, system=3, activity=Activity.MINING)), tick=7)
    (seul,) = decide(obs)
    assert seul.actor_id == ACTEUR
    assert seul.number == 700
    assert seul.category is OrderCategory.PLAYER
    assert (seul.policy_id, seul.policy_version) == (POLICY_ID, POLICY_VERSION)
    assert (POLICY_ID, POLICY_VERSION) == ("scripted_miner", 1)


def test_numeros_par_rang_de_vaisseau() -> None:
    obs = observation((navire(1, system=1), navire(2, system=3)), tick=3)
    assert [o.number for o in decide(obs)] == [300, 301]


def _soumettre(state: State, obs_tick: int) -> tuple[SubmittedOrder, ...]:
    return tuple(
        SubmittedOrder(
            tick=obs_tick + 1, sender_actor_id=o.actor_id, order=o, reception_refusal=None
        )
        for o in decide(observe(state, ACTEUR))
    )


def test_aucun_ordre_pendant_dix_ticks_de_minage() -> None:
    state = monde((vaisseau(1, ACTEUR, system=3, capacity=200),))
    state, _ = avancer(state, _soumettre(state, state.tick))
    for _ in range(10):
        obs = observe(state, ACTEUR)
        assert obs.own_ships[0].activity is Activity.MINING
        assert decide(obs) == ()
        state, _ = avancer(state)
    # Le minage commence au tick de l'ordre : 1 + 10 ticks de minage.
    assert state.ships[0].cargo[1] == 11 * REGLAGES.mining_rate


def test_un_cycle_complet_rapporte() -> None:
    """Depuis la station, cargaison vide : aller, miner, revenir et vendre en moins de 40 ticks."""
    state = monde((vaisseau(1, ACTEUR, system=1),))
    for _ in range(40):
        state, _ = avancer(state, _soumettre(state, state.tick))
    obs = observe(state, ACTEUR)
    assert obs.wallet_balance > 0
    assert sum(obs.own_ships[0].cargo) < REGLAGES.cargo_capacity
