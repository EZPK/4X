"""Types du registre partagés avec les clients (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
points 3 et 13). `LedgerEntry` vit ici parce que `schema` n'importe pas `core`."""

import enum

import msgspec

from fourx.schema.ids import OrderId
from fourx.schema.types import Id, Int64


class AccountKind(enum.Enum):
    ISSUANCE = "issuance"
    DESTRUCTION = "destruction"
    ESCROW = "escrow"
    PERSONAL_WALLET = "personal_wallet"
    CORPORATION_WALLET = "corporation_wallet"


class Reason(enum.Enum):
    ORE_SALE = "ore_sale"
    SALE_TAX = "sale_tax"


class LedgerEntry(msgspec.Struct, frozen=True):
    """Le compte débité est celui d'où part l'argent ; le compte crédité le reçoit."""

    debit_account_id: Id
    credit_account_id: Id
    amount: Int64
    reason: Reason
    cause: OrderId | None
