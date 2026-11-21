"""Tests de fourx.core.observe et des classes de visibilité de l'état.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 5.
"""

import msgspec
import pytest

from fourx.core.ledger import Account, Ledger
from fourx.core.observe import classes, observe, portee, vue
from fourx.core.state import Actor, Deposit, LastTick, Ship, Station, System
from fourx.schema.events import CLASSES, Arrived, DepositRegenerated, Event
from fourx.schema.observation import DepositView, OtherShipView, OwnShipView
from fourx.schema.orders import Mine, Move, Sell
from fourx.schema.visibility import Visibility
from tests.aide_monde import REGLAGES, avancer, monde, ordre, vaisseau


def test_chaque_champ_d_entite_a_une_classe() -> None:
    for entite in (System, Deposit, Station, Actor, Ship, Account, Ledger):
        assert all(c is not None for c in classes(entite).values()), entite


def test_classes_attendues() -> None:
    assert classes(Ship) == {
        "id": Visibility.NEARBY,
        "owner_id": Visibility.NEARBY,
        "system_id": Visibility.NEARBY,
        "capacity": Visibility.NEARBY,
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
    assert classes(Deposit)["stock"] is Visibility.NEARBY
    assert {c for n, c in classes(Deposit).items() if n != "stock"} == {Visibility.PUBLIC}
    assert set(classes(Ledger).values()) == {Visibility.ADMIN}


def test_vue_refuse_un_champ_prive_d_un_autre() -> None:
    navire = vaisseau(1, 2, 1)
    assert vue(navire, OtherShipView, False, True) == OtherShipView(
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
    obs = observe(etat, 1, REGLAGES)
    assert obs.tick == 1 and obs.actor_id == 1
    assert [v.id for v in obs.own_ships] == [1]
    assert [v.id for v in obs.other_ships] == [2]
    assert obs.wallet_balance == 135
    assert obs.action_budget == 10
    assert [s.id for s in obs.systems] == [1, 2, 3]
    assert [d.stock for d in obs.deposits] == [19990, None]
    assert obs.stations[0].ore_prices == (10, 15)
    assert [a.id for a in obs.actors] == [1, 2]
    types = [type(e.payload).__name__ for e in obs.events]
    assert types == ["Sale"]
    assert [r.order_id.actor_id for r in obs.results] == [1]
    autre = observe(etat, 2, REGLAGES)
    assert [type(e.payload).__name__ for e in autre.events] == ["MiningStarted", "OrderRefused"]
    assert len(autre.results) == 2
    assert autre.wallet_balance == 0


def test_observation_d_un_inconnu() -> None:
    etat = monde((vaisseau(1, 1, 1),))
    obs = observe(etat, 9, REGLAGES)
    assert obs.wallet_balance == 0 and obs.action_budget == 0
    assert obs.own_ships == () and obs.other_ships == ()
    assert all(d.stock is None for d in obs.deposits)


def test_portee_systemes_des_vaisseaux_et_voisins() -> None:
    etat = monde((vaisseau(1, 1, 1), vaisseau(2, 2, 3)))
    assert portee(etat, 1) == (1, 2)
    assert portee(etat, 2) == (2, 3)
    assert portee(etat, 9) == ()


def test_vaisseau_d_autrui_et_stock_hors_de_portee() -> None:
    """Deux sauts plus loin, un vaisseau d'autrui disparaît, et le stock d'un gisement vaut None ;
    à un saut, le vaisseau apparaît, sans son activité, et le stock est connu."""
    etat = monde((vaisseau(1, 1, 1), vaisseau(2, 2, 3)))
    obs = observe(etat, 1, REGLAGES)
    assert obs.other_ships == ()
    assert [(d.id, d.stock) for d in obs.deposits] == [(1, 20000), (2, None)]
    etat = monde((vaisseau(1, 1, 1), vaisseau(2, 2, 2)))
    obs = observe(etat, 1, REGLAGES)
    assert obs.other_ships == (OtherShipView(id=2, owner_id=2, system_id=2, capacity=100),)
    assert not hasattr(obs.other_ships[0], "activity")


def test_evenements_de_proximite() -> None:
    """Un saut est visible à portée de son système ; la régénération d'un gisement, à portée du
    système du gisement."""
    etat = monde((vaisseau(1, 1, 1), vaisseau(2, 2, 3)), budgets={1: 10, 2: 10})
    etat, _ = avancer(etat, (ordre(etat, 2, 1, Move(ship_id=2, target_system_id=2)),), 5)
    assert etat.ships[1].system_id == 2
    arrivees = [e for e in etat.last_tick.events if isinstance(e.payload, Arrived)]
    assert arrivees and arrivees[0].visibility is Visibility.NEARBY
    vus = [type(e.payload) for e in observe(etat, 1, REGLAGES).events]
    assert Arrived in vus
    regen = Event(
        tick=etat.tick,
        seq=0,
        event_schema_version=0,
        rules_version="r",
        actor_id=None,
        actor_kind=None,
        policy_id=None,
        policy_version=None,
        causation_id=None,
        visibility=Visibility.NEARBY,
        payload=DepositRegenerated(deposit_id=2, stock=20000),
    )
    seul = monde((vaisseau(1, 1, 1),))
    seul = msgspec.structs.replace(seul, last_tick=LastTick(events=(regen,), results=()))
    assert observe(seul, 1, REGLAGES).events == ()
    loin = msgspec.structs.replace(seul, ships=(vaisseau(1, 1, 2),))
    assert observe(loin, 1, REGLAGES).events == (regen,)


def test_reglages_publics_et_aucun_autre() -> None:
    obs = observe(monde((vaisseau(1, 1, 1),)), 1, REGLAGES)
    assert (obs.public_tunables.jump_ticks, obs.public_tunables.mining_rate) == (5, 10)
    noms = set(obs.public_tunables.__struct_fields__)
    assert noms == {"jump_ticks", "mining_rate"}
    assert noms <= set(REGLAGES.__struct_fields__)


def test_tout_type_de_proximite_a_un_systeme_de_reference() -> None:
    for entite in (System, Deposit, Station, Actor, Ship):
        if Visibility.NEARBY in classes(entite).values():
            assert "system_id" in entite.__struct_fields__, entite
    for type_evenement, classe in CLASSES.items():
        if classe is Visibility.NEARBY:
            champs = set(type_evenement.__struct_fields__)
            assert "system_id" in champs or "deposit_id" in champs, type_evenement


def test_vue_d_un_gisement_hors_de_portee() -> None:
    gisement = Deposit(id=1, system_id=3, ore_id=1, stock=7)
    assert vue(gisement, DepositView, False, False).stock is None
    assert vue(gisement, DepositView, False, True).stock == 7
