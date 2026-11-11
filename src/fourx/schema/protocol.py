"""Messages du protocole (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 5, 6 et 13)."""

from typing import Protocol

import msgspec

from fourx.schema.observation import Observation
from fourx.schema.orders import Order
from fourx.schema.types import Int64

PROTOCOL_VERSION = 1


class SubmitOrders(msgspec.Struct, frozen=True):
    protocol_version: Int64
    orders: tuple[Order, ...]


class TickUpdate(msgspec.Struct, frozen=True):
    protocol_version: Int64
    observation: Observation


class Connection(Protocol):
    """Point de connexion d'un client ; le serveur le réalise par une paire de files asyncio."""

    def submit(self, message: SubmitOrders) -> None: ...

    async def next_update(self) -> TickUpdate: ...


class SyncClient(Protocol):
    """Client appelé de façon synchrone par le mode sans horloge du serveur."""

    def on_update(self, update: TickUpdate) -> SubmitOrders | None: ...
