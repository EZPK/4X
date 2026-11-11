"""Résultats d'ordre et codes de refus.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 13.
"""

import enum

import msgspec

from fourx.schema.ids import OrderId
from fourx.schema.types import Id, Int64


class RefusalCode(enum.Enum):
    UNKNOWN_SHIP = "unknown_ship"
    NOT_OWNER = "not_owner"
    SHIP_EN_ROUTE = "ship_en_route"
    UNKNOWN_SYSTEM = "unknown_system"
    ALREADY_THERE = "already_there"
    NO_DEPOSIT_FOR_ORE = "no_deposit_for_ore"
    DEPOSIT_EMPTY = "deposit_empty"
    CARGO_FULL = "cargo_full"
    NOT_AT_STATION = "not_at_station"
    QUANTITY_NOT_POSITIVE = "quantity_not_positive"
    QUANTITY_EXCEEDS_CARGO = "quantity_exceeds_cargo"
    NO_ACTION_LEFT = "no_action_left"
    SUPERSEDED = "superseded"
    INVALID_FORMAT = "invalid_format"
    DUPLICATE_NUMBER = "duplicate_number"
    QUOTA_EXCEEDED = "quota_exceeded"
    ACTOR_MISMATCH = "actor_mismatch"
    FORBIDDEN_CATEGORY = "forbidden_category"


class OrderResult(msgspec.Struct, frozen=True):
    recipient_actor_id: Id | None
    order_id: OrderId
    accepted: bool
    refusal: RefusalCode | None
    text: str
    budget_left: Int64
