"""Tests du paquet schema (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 5 et 13)."""

import msgspec
import msgspec.json
import pytest

from fourx.schema import events, ids, observation, orders, protocol, types, visibility
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.ledger import AccountKind, LedgerEntry, Reason
from fourx.schema.orders import (
    ORDER_QUOTA_PER_TICK,
    CreateCharacter,
    Mine,
    Move,
    Order,
    OrderCategory,
    Sell,
    SubmittedOrder,
    identite,
    validate_orders,
)
from fourx.schema.results import RefusalCode


def soumis(
    actor: int,
    number: int,
    sender: int | None = None,
    category: OrderCategory = OrderCategory.PLAYER,
    policy_id: str | None = None,
) -> SubmittedOrder:
    return SubmittedOrder(
        tick=3,
        sender_actor_id=actor if sender is None else sender,
        order=Order(
            actor_id=actor,
            number=number,
            category=category,
            policy_id=policy_id,
            policy_version=None,
            command=Mine(ship_id=1, ore_id=1),
        ),
        reception_refusal=None,
    )


def test_bornes_64_bits() -> None:
    assert types.MIN_INT64 == -(2**63) and types.MAX_INT64 == 2**63 - 1
    with pytest.raises(msgspec.ValidationError):
        msgspec.convert({"actor_id": 0, "tick": 1, "number": 1}, ids.OrderId)
    with pytest.raises(msgspec.ValidationError):
        msgspec.convert({"actor_id": 1, "tick": 2**63, "number": 1}, ids.OrderId)
    assert msgspec.convert({"actor_id": 1, "tick": -(2**63), "number": 0}, ids.OrderId).tick == -(
        2**63
    )


def test_valeurs_des_enumerations() -> None:
    assert [k.value for k in ActorKind] == ["human", "ai_player", "npc"]
    assert [a.value for a in Activity] == ["idle", "en_route", "mining"]
    assert [c.value for c in OrderCategory] == ["player", "system", "admin"]
    assert [r.value for r in Reason] == ["ore_sale", "sale_tax"]
    assert [k.value for k in AccountKind] == [
        "issuance",
        "destruction",
        "escrow",
        "personal_wallet",
        "corporation_wallet",
    ]
    assert [v.value for v in visibility.Visibility] == ["public", "corporation", "private", "admin"]
    assert len(RefusalCode) == 18
    assert all(code.value == code.name.lower() for code in RefusalCode)


def test_visible_et_classe_de() -> None:
    meta = visibility.visible(visibility.Visibility.PRIVATE)
    assert meta.extra == {"visibility": "private"}
    assert visibility.classe_de(meta.extra) is visibility.Visibility.PRIVATE
    assert visibility.classe_de(None) is None
    assert visibility.classe_de({}) is None
    assert visibility.classe_de({"autre": 1}) is None


def test_commandes_et_identite() -> None:
    assert (
        msgspec.json.encode(Move(ship_id=1, target_system_id=3))
        == b'{"type":"move","ship_id":1,"target_system_id":3}'
    )
    assert (
        msgspec.json.encode(CreateCharacter(actor_kind=ActorKind.NPC))
        == b'{"type":"create_character","actor_kind":"npc"}'
    )
    ordre = Order(
        actor_id=2,
        number=5,
        category=OrderCategory.PLAYER,
        policy_id=None,
        policy_version=None,
        command=Sell(ship_id=1, ore_id=2, quantity=3),
    )
    decode = msgspec.json.decode(msgspec.json.encode(ordre), type=Order)
    assert decode == ordre and isinstance(decode.command, Sell)
    s = SubmittedOrder(
        tick=4, sender_actor_id=2, order=ordre, reception_refusal=RefusalCode.QUOTA_EXCEEDED
    )
    assert identite(s) == ids.OrderId(actor_id=2, tick=4, number=5)
    assert orders.OrderId is ids.OrderId


def test_validation_ordre_valide() -> None:
    assert validate_orders((soumis(1, 1),)) == (None,)
    assert validate_orders(()) == ()


def test_validation_format() -> None:
    assert validate_orders((soumis(1, -1),)) == (RefusalCode.INVALID_FORMAT,)
    assert validate_orders((soumis(1, 0, policy_id="p" * 64),)) == (None,)
    assert validate_orders((soumis(1, 0, policy_id="p" * 65),)) == (RefusalCode.INVALID_FORMAT,)


def test_validation_numero_repete() -> None:
    assert validate_orders((soumis(1, 2), soumis(1, 2), soumis(1, 2))) == (
        None,
        RefusalCode.DUPLICATE_NUMBER,
        RefusalCode.DUPLICATE_NUMBER,
    )
    assert validate_orders((soumis(1, 2), soumis(2, 2))) == (None, None)


def test_validation_quota_garde_les_plus_petits_numeros() -> None:
    assert ORDER_QUOTA_PER_TICK == 5
    lot = tuple(soumis(1, n) for n in (7, 1, 2, 3, 4, 5, 6))
    assert validate_orders(lot) == (
        RefusalCode.QUOTA_EXCEEDED,
        None,
        None,
        None,
        None,
        None,
        RefusalCode.QUOTA_EXCEEDED,
    )
    autres = tuple(soumis(1, n) for n in range(5)) + (soumis(2, 9),)
    assert validate_orders(autres)[-1] is None


def test_validation_acteur_et_categorie() -> None:
    assert validate_orders((soumis(2, 1, sender=1),)) == (RefusalCode.ACTOR_MISMATCH,)
    assert validate_orders((soumis(1, 1, category=OrderCategory.ADMIN),)) == (
        RefusalCode.FORBIDDEN_CATEGORY,
    )
    assert validate_orders((soumis(1, 1, category=OrderCategory.SYSTEM),)) == (
        RefusalCode.FORBIDDEN_CATEGORY,
    )
    assert validate_orders((soumis(2, -1, sender=1, category=OrderCategory.ADMIN),)) == (
        RefusalCode.INVALID_FORMAT,
    )


def test_evenements_classes_et_schema() -> None:
    assert len(events.CLASSES) == 9
    assert events.CLASSES[events.Sale] is visibility.Visibility.PRIVATE
    assert events.CLASSES[events.LedgerEntryRecorded] is visibility.Visibility.ADMIN
    assert events.CLASSES[events.Departed] is visibility.Visibility.PUBLIC
    publics = {t.__name__ for t, c in events.CLASSES.items() if c is visibility.Visibility.PUBLIC}
    assert publics == {"CharacterCreated", "Departed", "Arrived", "DepositRegenerated"}
    schema = events.event_json_schema()
    assert schema["$ref"] == "#/$defs/Event"
    definitions = schema["$defs"]
    assert isinstance(definitions, dict)
    assert {"Sale", "MiningEnded", "LedgerEntryRecorded", "LedgerEntry", "OrderId"} <= set(
        definitions
    )
    assert events.EVENT_SCHEMA_VERSION == 0


def test_evenement_aller_retour() -> None:
    e = events.Event(
        tick=1,
        seq=0,
        event_schema_version=0,
        rules_version="rules-0+x",
        actor_id=None,
        actor_kind=None,
        policy_id=None,
        policy_version=None,
        causation_id=None,
        visibility=visibility.Visibility.ADMIN,
        payload=events.LedgerEntryRecorded(
            entry=LedgerEntry(
                debit_account_id=1,
                credit_account_id=3,
                amount=5,
                reason=Reason.ORE_SALE,
                cause=None,
            )
        ),
    )
    assert msgspec.json.decode(msgspec.json.encode(e), type=events.Event) == e


def test_protocole() -> None:
    assert protocol.PROTOCOL_VERSION == 1
    message = protocol.SubmitOrders(protocol_version=1, orders=())
    assert msgspec.json.decode(msgspec.json.encode(message), type=protocol.SubmitOrders) == message
    obs = observation.Observation(
        tick=0,
        actor_id=1,
        systems=(),
        deposits=(),
        stations=(),
        actors=(),
        own_ships=(),
        other_ships=(),
        wallet_balance=0,
        action_budget=0,
        events=(),
        results=(),
    )
    maj = protocol.TickUpdate(protocol_version=1, observation=obs)
    assert msgspec.json.decode(msgspec.json.encode(maj), type=protocol.TickUpdate) == maj
