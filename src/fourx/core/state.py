"""État du monde (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 2, 4, 5 et 13).

Chaque champ de données d'une entité déclare sa classe de visibilité. Les tables sont des
tuples triés par identifiant croissant ; aucun dictionnaire ni ensemble n'apparaît dans l'état.
"""

from typing import Annotated

import msgspec

from fourx.core.ledger import Ledger
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Event
from fourx.schema.results import OrderResult
from fourx.schema.types import Id, Int64
from fourx.schema.visibility import Visibility, visible

PUBLIC = visible(Visibility.PUBLIC)
PRIVATE = visible(Visibility.PRIVATE)


class System(msgspec.Struct, frozen=True):
    id: Annotated[Id, PUBLIC]
    neighbors: Annotated[tuple[Id, ...], PUBLIC]


class Deposit(msgspec.Struct, frozen=True):
    id: Annotated[Id, PUBLIC]
    system_id: Annotated[Id, PUBLIC]
    ore_id: Annotated[Id, PUBLIC]
    stock: Annotated[Int64, PUBLIC]


class Station(msgspec.Struct, frozen=True):
    id: Annotated[Id, PUBLIC]
    system_id: Annotated[Id, PUBLIC]
    ore_prices: Annotated[tuple[Int64, ...], PUBLIC]


class Actor(msgspec.Struct, frozen=True):
    id: Annotated[Id, PUBLIC]
    kind: Annotated[ActorKind, PUBLIC]
    action_budget: Annotated[Int64, PRIVATE]


class Ship(msgspec.Struct, frozen=True):
    id: Annotated[Id, PUBLIC]
    owner_id: Annotated[Id, PUBLIC]
    system_id: Annotated[Id, PUBLIC]
    capacity: Annotated[Int64, PUBLIC]
    activity: Annotated[Activity, PRIVATE]
    route: Annotated[tuple[Id, ...], PRIVATE]
    ticks_to_next_jump: Annotated[Int64, PRIVATE]
    cargo: Annotated[tuple[Int64, ...], PRIVATE]
    mining_ore_id: Annotated[Id | None, PRIVATE]
    mined_since_start: Annotated[Int64, PRIVATE]


class LastTick(msgspec.Struct, frozen=True):
    events: tuple[Event, ...]
    results: tuple[OrderResult, ...]


class State(msgspec.Struct, frozen=True):
    tick: Int64
    systems: tuple[System, ...]
    deposits: tuple[Deposit, ...]
    stations: tuple[Station, ...]
    actors: tuple[Actor, ...]
    ships: tuple[Ship, ...]
    ledger: Ledger
    last_tick: LastTick
