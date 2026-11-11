"""Aide aux tests de `policies` et `clients` : observations construites à la main.

Même carte que tests/aide_monde.py : la station dans system_1, le gisement de ore_a (id 1) dans
system_2, celui de ore_b (id 2) dans system_3 ; ore_a payé 10, ore_b payé 15.
"""

from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Event
from fourx.schema.observation import (
    ActorView,
    DepositView,
    Observation,
    OwnShipView,
    StationView,
    SystemView,
)
from fourx.schema.results import OrderResult

ACTEUR = 1


def navire(
    ident: int = 1,
    system: int = 1,
    activity: Activity = Activity.IDLE,
    cargo: tuple[int, int] = (0, 0),
    capacity: int = 100,
    route: tuple[int, ...] = (),
) -> OwnShipView:
    return OwnShipView(
        id=ident,
        owner_id=ACTEUR,
        system_id=system,
        capacity=capacity,
        activity=activity,
        route=route,
        ticks_to_next_jump=5 if route else 0,
        cargo=cargo,
        mining_ore_id=None,
        mined_since_start=0,
    )


def observation(
    navires: tuple[OwnShipView, ...] = (),
    tick: int = 7,
    stocks: tuple[int, int] = (20000, 20000),
    prix: tuple[int, int] = (10, 15),
    solde: int = 0,
    evenements: tuple[Event, ...] = (),
    resultats: tuple[OrderResult, ...] = (),
) -> Observation:
    return Observation(
        tick=tick,
        actor_id=ACTEUR,
        systems=(
            SystemView(id=1, neighbors=(2,)),
            SystemView(id=2, neighbors=(1, 3)),
            SystemView(id=3, neighbors=(2,)),
        ),
        deposits=(
            DepositView(id=1, system_id=2, ore_id=1, stock=stocks[0]),
            DepositView(id=2, system_id=3, ore_id=2, stock=stocks[1]),
        ),
        stations=(StationView(id=1, system_id=1, ore_prices=prix),),
        actors=(ActorView(id=ACTEUR, kind=ActorKind.HUMAN),),
        own_ships=navires,
        other_ships=(),
        wallet_balance=solde,
        action_budget=10,
        events=evenements,
        results=resultats,
    )
