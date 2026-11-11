"""Réglages des règles (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 2 et 13).

Les valeurs de M1 sont dans tunables.toml, donnée du paquet lue par le serveur.
"""

from typing import Annotated

import msgspec

from fourx.schema.types import MAX_INT64

Positif = Annotated[int, msgspec.Meta(ge=1, le=MAX_INT64)]
Naturel = Annotated[int, msgspec.Meta(ge=0, le=MAX_INT64)]
PointsDeBase = Annotated[int, msgspec.Meta(ge=0, le=10_000)]


class Tunables(msgspec.Struct, frozen=True):
    """Bornes vérifiées au décodage de tunables.toml (une division par zéro ou un prix nul
    ferait échouer step)."""

    jump_ticks: Positif
    mining_rate: Positif
    cargo_capacity: Positif
    ore_prices: tuple[Positif, ...]  # indexé par identifiant de minerai moins un
    tax_rate_bp: PointsDeBase  # taux de taxe en points de base
    deposit_stock: Naturel
    regen_ticks: Positif
    budget_regen: Naturel
    budget_max: Naturel
