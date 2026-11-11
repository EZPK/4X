"""Événements v0.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 5 et 13 ; niveau 1, §6.
"""

from typing import Any

import msgspec
import msgspec.json

from fourx.schema.actors import ActorKind
from fourx.schema.ids import OrderId
from fourx.schema.ledger import LedgerEntry
from fourx.schema.results import RefusalCode
from fourx.schema.types import Id, Int64
from fourx.schema.visibility import Visibility

EVENT_SCHEMA_VERSION = 0


class CharacterCreated(msgspec.Struct, frozen=True, tag="character_created"):
    actor_id: Id
    actor_kind: ActorKind
    ship_id: Id


class OrderRefused(msgspec.Struct, frozen=True, tag="order_refused"):
    order_id: OrderId
    refusal: RefusalCode


class Departed(msgspec.Struct, frozen=True, tag="departed"):
    ship_id: Id
    system_id: Id


class Arrived(msgspec.Struct, frozen=True, tag="arrived"):
    ship_id: Id
    system_id: Id


class MiningStarted(msgspec.Struct, frozen=True, tag="mining_started"):
    ship_id: Id
    ore_id: Id
    rate: Int64


class MiningEnded(msgspec.Struct, frozen=True, tag="mining_ended"):
    ship_id: Id
    quantity: Int64


class Sale(msgspec.Struct, frozen=True, tag="sale"):
    ship_id: Id
    ore_id: Id
    quantity: Int64
    price: Int64
    payment: Int64
    tax: Int64


class DepositRegenerated(msgspec.Struct, frozen=True, tag="deposit_regenerated"):
    deposit_id: Id
    stock: Int64


class LedgerEntryRecorded(msgspec.Struct, frozen=True, tag="ledger_entry_recorded"):
    entry: LedgerEntry


Payload = (
    CharacterCreated
    | OrderRefused
    | Departed
    | Arrived
    | MiningStarted
    | MiningEnded
    | Sale
    | DepositRegenerated
    | LedgerEntryRecorded
)

# Une seule classe de visibilité par type d'événement (Technical Plan, point 5).
CLASSES: dict[type[Any], Visibility] = {
    CharacterCreated: Visibility.PUBLIC,
    OrderRefused: Visibility.PRIVATE,
    Departed: Visibility.PUBLIC,
    Arrived: Visibility.PUBLIC,
    MiningStarted: Visibility.PRIVATE,
    MiningEnded: Visibility.PRIVATE,
    Sale: Visibility.PRIVATE,
    DepositRegenerated: Visibility.PUBLIC,
    LedgerEntryRecorded: Visibility.ADMIN,
}


class Event(msgspec.Struct, frozen=True):
    tick: Int64
    seq: Int64
    event_schema_version: Int64
    rules_version: str
    actor_id: Id | None
    actor_kind: ActorKind | None
    policy_id: str | None
    policy_version: Int64 | None
    causation_id: OrderId | None
    visibility: Visibility
    payload: Payload


def event_json_schema() -> dict[str, object]:
    """Le JSON Schema des événements v0."""
    return msgspec.json.schema(Event)
