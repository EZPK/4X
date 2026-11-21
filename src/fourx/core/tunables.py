"""Réglages des règles (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 2 et 13).

Les valeurs de M1 sont dans tunables.toml, donnée du paquet lue par le serveur.
"""

from typing import Annotated

import msgspec

from fourx.schema.types import MAX_INT64

Positif = Annotated[int, msgspec.Meta(ge=1, le=MAX_INT64)]
Naturel = Annotated[int, msgspec.Meta(ge=0, le=MAX_INT64)]
PointsDeBase = Annotated[int, msgspec.Meta(ge=0, le=10_000)]


NOMBRE_DE_MINERAIS = 2
GISEMENTS_PAR_MINERAI = 2


class Tunables(msgspec.Struct, frozen=True):
    """Bornes vérifiées au décodage de tunables.toml (une division par zéro ou un prix nul
    ferait échouer step), puis contrôles croisés du Technical Plan, point 2 (amendement 1)."""

    jump_ticks: Positif
    mining_rate: Positif
    cargo_capacity: Positif
    # Une ligne par station : la station d'identifiant i prend la ligne i ; chaque ligne est
    # indexée par identifiant de minerai moins un.
    station_ore_prices: tuple[tuple[Positif, ...], ...]
    tax_rate_bp: PointsDeBase  # taux de taxe en points de base
    deposit_stock: Naturel
    regen_ticks: Positif
    budget_regen: Naturel
    budget_max: Naturel
    systems_min: Positif
    systems_max: Positif
    deposits_min: Positif
    deposits_max: Positif
    stations_min: Positif
    stations_max: Positif
    npc_min: Positif
    npc_max: Positif
    extra_links_max: Positif
    max_neighbors: Positif

    def __post_init__(self) -> None:
        for bas, haut in (
            ("systems_min", "systems_max"),
            ("deposits_min", "deposits_max"),
            ("stations_min", "stations_max"),
            ("npc_min", "npc_max"),
        ):
            if getattr(self, bas) > getattr(self, haut):
                raise ValueError(f"{bas} dépasse {haut}")
        if len(self.station_ore_prices) < self.stations_max:
            raise ValueError("station_ore_prices a moins de stations_max lignes")
        for ligne in self.station_ore_prices:
            if len(ligne) != NOMBRE_DE_MINERAIS:
                raise ValueError("chaque ligne de station_ore_prices a un prix par minerai")
        if self.deposits_min < NOMBRE_DE_MINERAIS * GISEMENTS_PAR_MINERAI:
            raise ValueError("deposits_min est inférieur à 4 (deux gisements par minerai)")
        if self.systems_min < self.deposits_max or self.systems_min < self.stations_max:
            raise ValueError("systems_min est inférieur à deposits_max ou à stations_max")
        if self.max_neighbors < 2:
            raise ValueError("max_neighbors est inférieur à 2")
