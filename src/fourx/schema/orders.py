"""Ordres et validation sans état.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 2, 5 et 13.
"""

import enum

import msgspec

from fourx.schema.actors import ActorKind
from fourx.schema.ids import OrderId
from fourx.schema.results import RefusalCode
from fourx.schema.types import Id, Int64

__all__ = [
    "ORDER_QUOTA_PER_TICK",
    "Command",
    "CreateCharacter",
    "Mine",
    "Move",
    "Order",
    "OrderCategory",
    "OrderId",
    "Sell",
    "SubmittedOrder",
    "identite",
    "validate_orders",
]

ORDER_QUOTA_PER_TICK = 5
POLICY_ID_MAX = 64


class OrderCategory(enum.Enum):
    PLAYER = "player"
    SYSTEM = "system"
    ADMIN = "admin"


class Move(msgspec.Struct, frozen=True, tag="move"):
    ship_id: Id
    target_system_id: Id


class Mine(msgspec.Struct, frozen=True, tag="mine"):
    ship_id: Id
    ore_id: Id


class Sell(msgspec.Struct, frozen=True, tag="sell"):
    ship_id: Id
    ore_id: Id
    quantity: Int64


class CreateCharacter(msgspec.Struct, frozen=True, tag="create_character"):
    actor_kind: ActorKind


Command = Move | Mine | Sell | CreateCharacter


class Order(msgspec.Struct, frozen=True):
    actor_id: Id
    number: Int64
    category: OrderCategory
    policy_id: str | None
    policy_version: Int64 | None
    command: Command


class SubmittedOrder(msgspec.Struct, frozen=True):
    """Un ordre tel que le journal et `step` le reçoivent ; sender_actor_id None : le serveur."""

    tick: Int64
    sender_actor_id: Id | None
    order: Order
    reception_refusal: RefusalCode | None


def identite(soumis: SubmittedOrder) -> OrderId:
    return OrderId(actor_id=soumis.order.actor_id, tick=soumis.tick, number=soumis.order.number)


def validate_orders(orders: tuple[SubmittedOrder, ...]) -> tuple[RefusalCode | None, ...]:
    """Validation sans état des ordres d'un point de connexion pour un tick.

    Contrôles, dans cet ordre (le premier qui s'applique donne le code) : format, numéro
    répété, quota, ordre au nom d'un autre acteur, catégorie autre que « joueur ».
    Les numéros répétés et le quota se comptent par acteur du point de connexion.
    """
    vus: dict[tuple[Id | None, int], int] = {}
    rangs: dict[int, int] = {}
    par_emetteur: dict[Id | None, list[tuple[int, int]]] = {}
    for indice, soumis in enumerate(orders):
        par_emetteur.setdefault(soumis.sender_actor_id, []).append((soumis.order.number, indice))
    for liste in par_emetteur.values():
        for rang, (_, indice) in enumerate(sorted(liste)):
            rangs[indice] = rang
    codes: list[RefusalCode | None] = []
    for indice, soumis in enumerate(orders):
        ordre = soumis.order
        cle = (soumis.sender_actor_id, ordre.number)
        if ordre.number < 0 or (
            ordre.policy_id is not None and len(ordre.policy_id) > POLICY_ID_MAX
        ):
            codes.append(RefusalCode.INVALID_FORMAT)
        elif cle in vus:
            codes.append(RefusalCode.DUPLICATE_NUMBER)
        elif rangs[indice] >= ORDER_QUOTA_PER_TICK:
            codes.append(RefusalCode.QUOTA_EXCEEDED)
        elif ordre.actor_id != soumis.sender_actor_id:
            codes.append(RefusalCode.ACTOR_MISMATCH)
        elif ordre.category is not OrderCategory.PLAYER:
            codes.append(RefusalCode.FORBIDDEN_CATEGORY)
        else:
            codes.append(None)
        vus.setdefault(cle, indice)
    return tuple(codes)
