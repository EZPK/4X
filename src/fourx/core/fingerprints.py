"""Empreintes par composant de l'état (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 4).

BLAKE2b, condensé de 16 octets, sur l'encodage MessagePack de msgspec de chaque composant,
écrit en hexadécimal. Les composants sont tous les champs de Fingerprints sauf `tick`.
"""

import hashlib

import msgspec
import msgspec.msgpack

from fourx.core.state import State
from fourx.schema.types import Int64


class Fingerprints(msgspec.Struct, frozen=True):
    tick: Int64
    systems: str
    deposits: str
    stations: str
    actors: str
    ships: str
    ledger: str
    last_tick: str


def empreinte(valeur: object) -> str:
    return hashlib.blake2b(msgspec.msgpack.encode(valeur), digest_size=16).hexdigest()


def fingerprints(state: State) -> Fingerprints:
    return Fingerprints(
        tick=state.tick,
        systems=empreinte(state.systems),
        deposits=empreinte(state.deposits),
        stations=empreinte(state.stations),
        actors=empreinte(state.actors),
        ships=empreinte(state.ships),
        ledger=empreinte(state.ledger),
        last_tick=empreinte(state.last_tick),
    )
