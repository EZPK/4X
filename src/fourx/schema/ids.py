"""Identité d'un ordre (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 5 et 13).

Dans un module à part pour que `orders` et `results` ne s'importent pas l'un l'autre ;
`fourx.schema.orders` la réexporte.
"""

import msgspec

from fourx.schema.types import Id, Int64


class OrderId(msgspec.Struct, frozen=True):
    actor_id: Id
    tick: Int64
    number: Int64
