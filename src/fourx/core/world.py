"""Génération du monde au tick 0 (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 2).

Trois systèmes reliés en chaîne dans l'ordre de leurs identifiants. Le tirage borné sur
(graine du monde, tick 0, entité 0, motif « carte ») donne le rang, dans l'ordre
lexicographique, d'une des six permutations de (system_1, system_2, system_3) : dans l'ordre,
le système de la station, du gisement de ore_a et du gisement de ore_b.
"""

from fourx.core.keyed_random import keyed_below
from fourx.core.ledger import ledger_vide
from fourx.core.state import Deposit, LastTick, State, Station, System
from fourx.core.tunables import Tunables

SYSTEMES = (1, 2, 3)
PERMUTATIONS = ((1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1))
MOTIF_CARTE = "carte"


def generate(world_seed: int, tunables: Tunables) -> State:
    """L'état du tick 0 : la carte, les gisements pleins, la station, aucun acteur."""
    station, gisement_a, gisement_b = PERMUTATIONS[
        keyed_below(world_seed, 0, 0, MOTIF_CARTE, len(PERMUTATIONS))
    ]
    systemes = tuple(
        System(id=s, neighbors=tuple(v for v in (s - 1, s + 1) if v in SYSTEMES)) for s in SYSTEMES
    )
    gisements = (
        Deposit(id=1, system_id=gisement_a, ore_id=1, stock=tunables.deposit_stock),
        Deposit(id=2, system_id=gisement_b, ore_id=2, stock=tunables.deposit_stock),
    )
    return State(
        tick=0,
        systems=systemes,
        deposits=gisements,
        stations=(Station(id=1, system_id=station, ore_prices=tunables.ore_prices),),
        actors=(),
        ships=(),
        ledger=ledger_vide(),
        last_tick=LastTick(events=(), results=()),
    )


def label(table: str, id: int) -> str:  # noqa: A002
    """Libellé neutre : system_1, deposit_2, station_1, actor_1, ship_1 ; minerai : ore_a, ore_b."""
    if table == "ore":
        return "ore_" + chr(ord("a") + id - 1)
    return f"{table}_{id}"
