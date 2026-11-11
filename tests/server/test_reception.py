"""Tests de la réception (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 6 ; plan
détaillé, point 23)."""

from fourx.schema.orders import Move, Order, OrderCategory
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders
from fourx.schema.results import RefusalCode
from fourx.server.reception import Reception


def ordre(numero: int, acteur: int = 4, categorie: OrderCategory = OrderCategory.PLAYER) -> Order:
    return Order(
        actor_id=acteur,
        number=numero,
        category=categorie,
        policy_id=None,
        policy_version=None,
        command=Move(ship_id=1, target_system_id=2),
    )


def message(*ordres: Order) -> SubmitOrders:
    return SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=ordres)


def test_lie_l_acteur_du_point_de_connexion_et_le_tick() -> None:
    (soumis,) = Reception().receive(4, (message(ordre(1)),), tick=12)
    assert soumis.tick == 12
    assert soumis.sender_actor_id == 4
    assert soumis.order == ordre(1)
    assert soumis.reception_refusal is None


def test_deux_messages_du_meme_tick_comptes_ensemble() -> None:
    """Quota et numéros répétés se comptent sur l'ensemble des messages du tick."""
    messages = (message(ordre(1), ordre(2), ordre(3)), message(ordre(3), ordre(4), ordre(5)))
    soumis = Reception().receive(4, messages, tick=1)
    assert [s.order.number for s in soumis] == [1, 2, 3, 3, 4, 5]
    assert [s.reception_refusal for s in soumis] == [
        None,
        None,
        None,
        RefusalCode.DUPLICATE_NUMBER,
        None,
        RefusalCode.QUOTA_EXCEEDED,
    ]


def test_ordre_au_nom_d_un_autre_acteur_et_categorie() -> None:
    soumis = Reception().receive(
        4, (message(ordre(1, acteur=5), ordre(2, categorie=OrderCategory.ADMIN)),), tick=1
    )
    assert [s.reception_refusal for s in soumis] == [
        RefusalCode.ACTOR_MISMATCH,
        RefusalCode.FORBIDDEN_CATEGORY,
    ]
    assert all(s.sender_actor_id == 4 for s in soumis)


def test_aucun_message() -> None:
    assert Reception().receive(4, (), tick=1) == ()
