"""L'hôte des PNJ.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 6, 7 et 13 ; plan détaillé,
point 22. Il fait jouer une politique pour un acteur PNJ par le même protocole que le client.
"""

from collections.abc import Callable

from fourx.schema.observation import Observation
from fourx.schema.orders import Order
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate

Politique = Callable[[Observation], tuple[Order, ...]]


class NpcHost:
    def __init__(self, actor_id: int, policy: Politique) -> None:
        self.actor_id = actor_id
        self.policy = policy

    def on_update(self, update: TickUpdate) -> SubmitOrders | None:
        ordres = self.policy(update.observation)
        if not ordres:
            return None
        return SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=ordres)
