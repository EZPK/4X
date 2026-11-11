"""Tests de l'hôte des PNJ (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ; plan
détaillé, point 23)."""

from fourx.clients.npc_host import NpcHost
from fourx.policies.scripted_miner import decide
from fourx.schema.observation import Observation
from fourx.schema.orders import Move, Order, OrderCategory
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate
from tests.aide_observation import navire, observation


def mise_a_jour(obs: Observation) -> TickUpdate:
    return TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs)


def test_transmet_l_observation_et_renvoie_les_ordres() -> None:
    vues: list[Observation] = []
    ordre = Order(
        actor_id=1,
        number=5,
        category=OrderCategory.PLAYER,
        policy_id="essai",
        policy_version=1,
        command=Move(ship_id=1, target_system_id=2),
    )

    def politique(obs: Observation) -> tuple[Order, ...]:
        vues.append(obs)
        return (ordre,)

    obs = observation((navire(),))
    hote = NpcHost(1, politique)
    assert hote.actor_id == 1
    reponse = hote.on_update(mise_a_jour(obs))
    assert vues == [obs]
    assert reponse == SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=(ordre,))


def test_aucun_ordre_aucun_message() -> None:
    hote = NpcHost(1, lambda obs: ())
    assert hote.on_update(mise_a_jour(observation((navire(),)))) is None


def test_avec_la_politique_scriptee() -> None:
    obs = observation((navire(system=1),))
    reponse = NpcHost(1, decide).on_update(mise_a_jour(obs))
    assert reponse is not None
    assert reponse.orders == decide(obs)
