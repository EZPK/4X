"""Tout entier de l'état et de l'instantané tient sur 64 bits signés.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 18.
"""

from typing import Any

import msgspec

from fourx.core import snapshot, version
from fourx.core.state import State
from fourx.core.world import generate
from fourx.schema.actors import ActorKind
from fourx.schema.orders import CreateCharacter, Mine, Move, OrderCategory, Sell
from fourx.schema.types import MAX_INT64, MIN_INT64
from tests.aide_monde import REGLAGES, avancer, ordre


def entiers(valeur: Any) -> list[int]:
    if isinstance(valeur, bool):
        return []
    if isinstance(valeur, int):
        return [valeur]
    if isinstance(valeur, (tuple, list)):
        return [i for v in valeur for i in entiers(v)]
    if isinstance(valeur, msgspec.Struct):
        return [i for f in valeur.__struct_fields__ for i in entiers(getattr(valeur, f))]
    return []


def verifier(etat: State) -> None:
    assert all(MIN_INT64 <= i <= MAX_INT64 for i in entiers(etat))
    instantane = snapshot.Snapshot(
        snapshot_schema_version=1,
        rules_version=version.rules_version(REGLAGES),
        world_seed=1,
        commit="x",
        worktree_dirty=True,
        state=etat,
    )
    assert snapshot.decode(snapshot.encode(instantane)) == instantane


def test_partie_generee() -> None:
    etat = generate(7, REGLAGES)
    verifier(etat)
    creation = ordre(
        etat,
        1,
        1,
        CreateCharacter(actor_kind=ActorKind.HUMAN),
        sender=None,
        category=OrderCategory.ADMIN,
    )
    etat, _ = avancer(etat, (creation,))
    verifier(etat)
    gisement_a = etat.deposits[0].system_id
    for commande in (
        Move(ship_id=1, target_system_id=gisement_a),
        Mine(ship_id=1, ore_id=1),
        Move(ship_id=1, target_system_id=etat.stations[0].system_id),
        Sell(ship_id=1, ore_id=1, quantity=100),
    ):
        etat, _ = avancer(etat, (ordre(etat, 1, etat.tick, commande),), 1)
        verifier(etat)
        etat, _ = avancer(etat, (), 12)
        verifier(etat)


def test_borne_refusee_a_l_encodage() -> None:
    import pytest

    from fourx.core.ledger import Account
    from fourx.schema.ledger import AccountKind

    trop = msgspec.msgpack.encode(
        {"id": 1, "kind": AccountKind.ISSUANCE.value, "owner_id": None, "balance": MAX_INT64 + 1}
    )
    with pytest.raises(msgspec.ValidationError):
        msgspec.msgpack.decode(trop, type=Account)
