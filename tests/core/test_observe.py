"""Tests de fourx.core.observe et des classes de visibilité de l'état.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 5.
"""

import pytest

from fourx.core.ledger import Account, Ledger
from fourx.core.observe import classes, observe, vue
from fourx.core.state import Actor, Deposit, Ship, Station, System
from fourx.schema.observation import OtherShipView, OwnShipView
from fourx.schema.orders import Mine, Sell
from fourx.schema.visibility import Visibility
from tests.aide_monde import avancer, monde, ordre, vaisseau


def test_chaque_champ_d_entite_a_une_classe() -> None:
    for entite in (System, Deposit, Station, Actor, Ship, Account, Ledger):
        assert all(c is not None for c in classes(entite).values()), entite


def test_classes_attendues() -> None:
    assert classes(Ship) == {
        "id": Visibility.PUBLIC,
        "owner_id": Visibility.PUBLIC,
        "system_id": Visibility.PUBLIC,
        "capacity": Visibility.PUBLIC,
        "activity": Visibility.PRIVATE,
        "route": Visibility.PRIVATE,
        "ticks_to_next_jump": Visibility.PRIVATE,
        "cargo": Visibility.PRIVATE,
        "mining_ore_id": Visibility.PRIVATE,
        "mined_since_start": Visibility.PRIVATE,
    }
    assert classes(Actor) == {
        "id": Visibility.PUBLIC,
        "kind": Visibility.PUBLIC,
        "action_budget": Visibility.PRIVATE,
    }
    assert classes(Account)["balance"] is Visibility.PRIVATE
    assert classes(Account)["owner_id"] is Visibility.ADMIN
    assert set(classes(Station).values()) == {Visibility.PUBLIC}
    assert set(classes(Ledger).values()) == {Visibility.ADMIN}


def test_vue_refuse_un_champ_prive_d_un_autre() -> None:
    navire = vaisseau(1, 2, 1)
    assert vue(navire, OtherShipView, False) == OtherShipView(
        id=1, owner_id=2, system_id=1, capacity=100
    )
    with pytest.raises(ValueError):
        vue(navire, OwnShipView, False)
    assert vue(navire, OwnShipView, True).cargo == (0, 0)


def test_observation_d_un_acteur() -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(0, 10)), vaisseau(2, 2, 2)))
    etat, _ = avancer(
        etat,
        (
            ordre(etat, 1, 1, Sell(ship_id=1, ore_id=2, quantity=10)),
            ordre(etat, 2, 1, Mine(ship_id=2, ore_id=1)),
            ordre(etat, 2, 2, Mine(ship_id=9, ore_id=1)),
        ),
    )
    obs = observe(etat, 1)
    assert obs.tick == 1 and obs.actor_id == 1
    assert [v.id for v in obs.own_ships] == [1]
    assert [v.id for v in obs.other_ships] == [2]
    assert obs.wallet_balance == 135
    assert obs.action_budget == 10
    assert [s.id for s in obs.systems] == [1, 2, 3]
    assert [d.stock for d in obs.deposits] == [19990, 20000]
    assert obs.stations[0].ore_prices == (10, 15)
    assert [a.id for a in obs.actors] == [1, 2]
    types = [type(e.payload).__name__ for e in obs.events]
    assert types == ["Sale"]
    assert [r.order_id.actor_id for r in obs.results] == [1]
    autre = observe(etat, 2)
    assert [type(e.payload).__name__ for e in autre.events] == ["MiningStarted", "OrderRefused"]
    assert len(autre.results) == 2
    assert autre.wallet_balance == 0


def test_observation_d_un_inconnu() -> None:
    etat = monde((vaisseau(1, 1, 1),))
    obs = observe(etat, 9)
    assert obs.wallet_balance == 0 and obs.action_budget == 0
    assert obs.own_ships == () and len(obs.other_ships) == 1
