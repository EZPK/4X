"""Instantané (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 6 ; niveau 1, §3).

L'instantané porte ses versions ; le serveur fournit le commit et l'indicateur
« dossier de travail modifié », que le noyau ne peut pas lire.
"""

import msgspec
import msgspec.msgpack

from fourx.core.state import State
from fourx.schema.types import Int64

SNAPSHOT_SCHEMA_VERSION = 1


class Snapshot(msgspec.Struct, frozen=True):
    snapshot_schema_version: Int64
    rules_version: str
    world_seed: Int64
    commit: str
    worktree_dirty: bool
    state: State


_DECODEUR = msgspec.msgpack.Decoder(Snapshot)


def encode(snapshot: Snapshot) -> bytes:
    return msgspec.msgpack.encode(snapshot)


def decode(donnees: bytes) -> Snapshot:
    return _DECODEUR.decode(donnees)
