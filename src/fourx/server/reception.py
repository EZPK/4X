"""La réception des ordres.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 5 et 6 ; niveau 1, §2.

La réception lie chaque ordre reçu à l'acteur de son point de connexion et au tick où il entre,
applique la validation sans état à tous les ordres de ce point de connexion pour ce tick, puis
rend des ordres soumis portant leur code de refus éventuel. Elle ne refuse rien elle-même :
`step` rend le refus, et le journal garde l'ordre.
"""

import msgspec.structs

from fourx.schema.orders import SubmittedOrder, validate_orders
from fourx.schema.protocol import SubmitOrders


class Reception:
    def receive(
        self, sender_actor_id: int, messages: tuple[SubmitOrders, ...], tick: int
    ) -> tuple[SubmittedOrder, ...]:
        """Tous les messages d'un point de connexion pour un tick, en un seul appel."""
        soumis = tuple(
            SubmittedOrder(
                tick=tick, sender_actor_id=sender_actor_id, order=o, reception_refusal=None
            )
            for message in messages
            for o in message.orders
        )
        codes = validate_orders(soumis)
        return tuple(
            msgspec.structs.replace(s, reception_refusal=code)
            for s, code in zip(soumis, codes, strict=True)
        )
