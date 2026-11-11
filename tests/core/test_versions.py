"""Champs de version de ce qui persiste ou circule (docs/designs/niveau-2-m1-noyau.md, objectif 7 ;
plan détaillé, point 18). La version du journal des ordres soumis est vérifiée au volet B."""

from fourx.core import snapshot, version
from fourx.schema import events, protocol


def test_champs_de_version() -> None:
    assert "snapshot_schema_version" in snapshot.Snapshot.__struct_fields__
    assert "rules_version" in snapshot.Snapshot.__struct_fields__
    assert "commit" in snapshot.Snapshot.__struct_fields__
    assert {"event_schema_version", "rules_version"} <= set(events.Event.__struct_fields__)
    assert "protocol_version" in protocol.SubmitOrders.__struct_fields__
    assert "protocol_version" in protocol.TickUpdate.__struct_fields__


def test_valeurs_de_version() -> None:
    assert snapshot.SNAPSHOT_SCHEMA_VERSION == 1
    assert events.EVENT_SCHEMA_VERSION == 0
    assert protocol.PROTOCOL_VERSION == 1
    assert version.RULES_REVISION == 0
