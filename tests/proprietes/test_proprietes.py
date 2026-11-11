"""Tests de propriétés sur des parties générées (docs/designs/niveau-2-m1-noyau.md, plan détaillé,
point 19). Profil hypothesis « ci » : sans hasard ni délai (tests/conftest.py)."""

from typing import Any

import msgspec
import msgspec.structs
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from fourx.core.fingerprints import fingerprints
from fourx.core.ledger import money_supply
from fourx.core.observe import classes, observe
from fourx.core.state import Actor, Deposit, Ship, State, Station, System
from fourx.core.step import step
from fourx.core.tunables import Tunables
from fourx.schema.actors import Activity
from fourx.schema.events import MiningEnded, Sale
from fourx.schema.ledger import AccountKind
from fourx.schema.observation import (
    ActorView,
    DepositView,
    OtherShipView,
    OwnShipView,
    StationView,
    SystemView,
)
from fourx.schema.orders import Mine, Move, Sell, SubmittedOrder
from fourx.schema.results import RefusalCode
from fourx.schema.types import MAX_INT64, MIN_INT64
from fourx.schema.visibility import Visibility
from tests.aide_monde import REGLAGES, monde, ordre, vaisseau

pytestmark = pytest.mark.proprietes

commandes = st.one_of(
    st.builds(Move, ship_id=st.integers(1, 4), target_system_id=st.integers(1, 4)),
    st.builds(Mine, ship_id=st.integers(1, 4), ore_id=st.integers(1, 3)),
    st.builds(
        Sell, ship_id=st.integers(1, 4), ore_id=st.integers(1, 3), quantity=st.integers(-2, 120)
    ),
)
tour = st.lists(st.tuples(st.integers(1, 3), st.integers(0, 6), commandes), max_size=6)
partie = st.tuples(
    st.integers(0, 2**32),
    st.integers(0, 40),
    st.integers(2, 12),
    st.lists(tour, min_size=1, max_size=25),
)


def jouer(
    graine: int, stock: int, regen: int, tours: list[list[Any]]
) -> list[tuple[State, State, tuple[Any, ...]]]:
    reglages = msgspec.structs.replace(
        REGLAGES, deposit_stock=stock, regen_ticks=regen, jump_ticks=2
    )
    etat = monde(
        (
            vaisseau(1, 1, 2),
            vaisseau(2, 2, 2),
            vaisseau(3, 3, 3, cargo=(5, 5)),
            vaisseau(4, 1, 1, cargo=(50, 0)),
        ),
        stocks=(stock, stock),
        reglages=reglages,
    )
    ticks = []
    for ordres_du_tour in tours:
        soumis = tuple(ordre(etat, a, n, c) for a, n, c in ordres_du_tour)
        apres, evenements = step(etat, soumis, graine, reglages)
        ticks.append((etat, apres, evenements))
        etat = apres
    return ticks


@settings(max_examples=60)
@given(partie)
def test_invariants_apres_chaque_tick(p: tuple[int, int, int, list[list[Any]]]) -> None:
    extrait_fin = vendu = 0
    initial = None
    for avant, apres, evenements in jouer(*p):
        if initial is None:
            initial = sum(sum(v.cargo) for v in avant.ships)
        comptes = apres.ledger.accounts
        assert sum(c.balance for c in comptes) == 0
        emis = sum(apres.ledger.issued_by_reason) - sum(avant.ledger.issued_by_reason)
        detruit = sum(apres.ledger.destroyed_by_reason) - sum(avant.ledger.destroyed_by_reason)
        assert emis == sum(e.amount for e in apres.ledger.tick_entries if e.debit_account_id == 1)
        assert detruit == sum(
            e.amount for e in apres.ledger.tick_entries if e.credit_account_id == 2
        )
        assert money_supply(apres.ledger) == money_supply(avant.ledger) + emis - detruit
        assert all(q >= 0 for v in apres.ships for q in v.cargo)
        assert all(sum(v.cargo) <= v.capacity for v in apres.ships)
        assert all(d.stock >= 0 for d in apres.deposits)
        assert all(0 <= a.action_budget <= 10 for a in apres.actors)
        extrait_fin += sum(
            e.payload.quantity for e in evenements if isinstance(e.payload, MiningEnded)
        )
        vendu += sum(e.payload.quantity for e in evenements if isinstance(e.payload, Sale))
        en_cours = sum(v.mined_since_start for v in apres.ships if v.activity is Activity.MINING)
        assert initial + extrait_fin + en_cours == sum(sum(v.cargo) for v in apres.ships) + vendu
        assert [e.seq for e in evenements] == list(range(len(evenements)))


@settings(max_examples=40)
@given(partie)
def test_deux_executions_memes_empreintes(p: tuple[int, int, int, list[list[Any]]]) -> None:
    premiere = [fingerprints(apres) for _, apres, _ in jouer(*p)]
    seconde = [fingerprints(apres) for _, apres, _ in jouer(*p)]
    assert premiere == seconde


def entiers(valeur: Any) -> list[int]:
    if isinstance(valeur, bool):
        return []
    if isinstance(valeur, int):
        return [valeur]
    if isinstance(valeur, tuple):
        return [i for v in valeur for i in entiers(v)]
    if isinstance(valeur, msgspec.Struct):
        return [i for f in valeur.__struct_fields__ for i in entiers(getattr(valeur, f))]
    return []


@settings(max_examples=30)
@given(partie)
def test_entiers_sur_64_bits(p: tuple[int, int, int, list[list[Any]]]) -> None:
    for _, apres, _ in jouer(*p):
        assert all(MIN_INT64 <= i <= MAX_INT64 for i in entiers(apres))


SOURCES = {
    SystemView: System,
    DepositView: Deposit,
    StationView: Station,
    ActorView: Actor,
    OwnShipView: Ship,
    OtherShipView: Ship,
}


@settings(max_examples=30)
@given(partie)
def test_visibilite_des_observations(p: tuple[int, int, int, list[list[Any]]]) -> None:
    for _, apres, _ in jouer(*p):
        for acteur in (1, 2, 3):
            obs = observe(apres, acteur)
            for liste in (
                obs.systems,
                obs.deposits,
                obs.stations,
                obs.actors,
                obs.own_ships,
                obs.other_ships,
            ):
                for v in liste:
                    source = classes(SOURCES[type(v)])
                    detient = isinstance(v, OwnShipView)
                    for champ in v.__struct_fields__:
                        classe = source[champ]
                        assert classe is Visibility.PUBLIC or (
                            classe is Visibility.PRIVATE and detient
                        )
            assert all(v.owner_id == acteur for v in obs.own_ships)
            assert all(v.owner_id != acteur for v in obs.other_ships)
            portefeuille = next(
                c
                for c in apres.ledger.accounts
                if c.kind is AccountKind.PERSONAL_WALLET and c.owner_id == acteur
            )
            assert obs.wallet_balance == portefeuille.balance
            assert all(
                e.visibility is Visibility.PUBLIC
                or (e.visibility is Visibility.PRIVATE and e.actor_id == acteur)
                for e in obs.events
            )
            assert all(r.recipient_actor_id == acteur for r in obs.results)


@settings(max_examples=30)
@given(
    st.lists(
        st.tuples(st.integers(1, 3), st.integers(0, 6), commandes),
        max_size=8,
        unique_by=lambda o: (o[0], o[1]),
    )
)
def test_chaque_ordre_recoit_un_resultat(ordres_bruts: list[Any]) -> None:
    etat = monde((vaisseau(1, 1, 2), vaisseau(2, 2, 1, cargo=(0, 10))))
    soumis: tuple[SubmittedOrder, ...] = tuple(ordre(etat, a, n, c) for a, n, c in ordres_bruts)
    apres, _ = step(etat, soumis, 1, REGLAGES)
    assert len(apres.last_tick.results) == len(soumis)
    for r in apres.last_tick.results:
        assert r.accepted == (r.refusal is None)
        assert r.refusal is None or isinstance(r.refusal, RefusalCode)
    acceptes = {
        (r.order_id.actor_id, r.order_id.number) for r in apres.last_tick.results if r.accepted
    }
    vus = [
        (s.order.actor_id, s.order.command.ship_id)
        for s in soumis
        if (s.order.actor_id, s.order.number) in acceptes
        and isinstance(s.order.command, (Move, Mine, Sell))
    ]
    assert len(vus) == len(set(vus))


def test_reglages_valides() -> None:
    assert isinstance(REGLAGES, Tunables)
