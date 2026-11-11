"""Observation d'un acteur (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 5 et 13).

Les vues reprennent les noms des champs de données de l'état. `wallet_balance` reprend le
solde (`balance`) du portefeuille personnel de l'acteur, `action_budget` celui de l'acteur.
"""

import msgspec

from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Event
from fourx.schema.results import OrderResult
from fourx.schema.types import Id, Int64


class SystemView(msgspec.Struct, frozen=True):
    id: Id
    neighbors: tuple[Id, ...]


class DepositView(msgspec.Struct, frozen=True):
    id: Id
    system_id: Id
    ore_id: Id
    stock: Int64


class StationView(msgspec.Struct, frozen=True):
    id: Id
    system_id: Id
    ore_prices: tuple[Int64, ...]


class ActorView(msgspec.Struct, frozen=True):
    id: Id
    kind: ActorKind


class OwnShipView(msgspec.Struct, frozen=True):
    id: Id
    owner_id: Id
    system_id: Id
    capacity: Int64
    activity: Activity
    route: tuple[Id, ...]
    ticks_to_next_jump: Int64
    cargo: tuple[Int64, ...]
    mining_ore_id: Id | None
    mined_since_start: Int64


class OtherShipView(msgspec.Struct, frozen=True):
    id: Id
    owner_id: Id
    system_id: Id
    capacity: Int64


class Observation(msgspec.Struct, frozen=True):
    tick: Int64
    actor_id: Id
    systems: tuple[SystemView, ...]
    deposits: tuple[DepositView, ...]
    stations: tuple[StationView, ...]
    actors: tuple[ActorView, ...]
    own_ships: tuple[OwnShipView, ...]
    other_ships: tuple[OtherShipView, ...]
    wallet_balance: Int64
    action_budget: Int64
    events: tuple[Event, ...]
    results: tuple[OrderResult, ...]
