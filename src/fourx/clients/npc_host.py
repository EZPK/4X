"""L'hôte des PNJ.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 6, 7 et 13 ; plan détaillé,
point 22. Il fait jouer une politique pour un acteur PNJ par le même protocole que le client.
Il garde la seule mémoire de la politique, l'ensemble des gisements vus vides, et la lui repasse
à chaque décision (amendement 1). Vu du niveau 1, §1, le joueur PNJ est l'hôte et sa politique
ensemble : il reçoit une observation et rend des ordres.
"""

from collections.abc import Callable

from fourx.schema.observation import Observation
from fourx.schema.orders import Order
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate

Politique = Callable[[Observation, frozenset[int]], tuple[tuple[Order, ...], frozenset[int]]]


class NpcHost:
    def __init__(self, actor_id: int, policy: Politique) -> None:
        self.actor_id = actor_id
        self.policy = policy
        self.seen_empty: frozenset[int] = frozenset()

    def on_update(self, update: TickUpdate) -> SubmitOrders | None:
        ordres, self.seen_empty = self.policy(update.observation, self.seen_empty)
        if not ordres:
            return None
        return SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=ordres)
