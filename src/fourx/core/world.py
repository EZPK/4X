"""Génération du monde au tick 0 (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 2).

Chaque tirage est keyed_below(graine, 0, entité, motif, n), avec l'entité et le motif de chaque
étape ; deux tirages n'ont jamais la même clé. Un nombre tiré « entre a et b » vaut
a + keyed_below(…, b − a + 1). Chaque liste de candidats est triée par identifiant avant le
tirage, et les voisins de chaque système sont triés par identifiant croissant.
"""

from fourx.core.keyed_random import keyed_below
from fourx.core.ledger import ledger_vide
from fourx.core.state import Deposit, LastTick, State, Station, System
from fourx.core.tunables import Tunables

MOTIF_TAILLE = "world_size"
MOTIF_ARBRE = "tree"
MOTIF_NOMBRE_DE_LIENS = "extra_link_count"
MOTIF_LIENS = "extra_links"
MOTIF_NOMBRE_DE_STATIONS = "station_count"
MOTIF_STATIONS = "stations"
MOTIF_NOMBRE_DE_GISEMENTS = "deposit_count"
MOTIF_GISEMENTS = "deposits"
MOTIF_NOMBRE_DE_PNJ = "npc_count"


def _entre(world_seed: int, entite: int, motif: str, bas: int, haut: int) -> int:
    """Un nombre tiré entre bas et haut, bornes comprises."""
    return bas + keyed_below(world_seed, 0, entite, motif, haut - bas + 1)


def _graphe(world_seed: int, tunables: Tunables) -> dict[int, list[int]]:
    """Les systèmes 1 à N et leurs voisins : un arbre, puis des liens qui créent des boucles."""
    n = _entre(world_seed, 0, MOTIF_TAILLE, tunables.systems_min, tunables.systems_max)
    voisins: dict[int, list[int]] = {1: []}
    for k in range(2, n + 1):
        candidats = [s for s in sorted(voisins) if len(voisins[s]) < tunables.max_neighbors]
        parent = candidats[keyed_below(world_seed, 0, k, MOTIF_ARBRE, len(candidats))]
        voisins[k] = [parent]
        voisins[parent].append(k)
    nombre = _entre(world_seed, 0, MOTIF_NOMBRE_DE_LIENS, 1, tunables.extra_links_max)
    for i in range(1, nombre + 1):
        paires = [
            (a, b)
            for a in sorted(voisins)
            for b in sorted(voisins)
            if a < b
            and b not in voisins[a]
            and len(voisins[a]) < tunables.max_neighbors
            and len(voisins[b]) < tunables.max_neighbors
        ]
        if not paires:
            break
        a, b = paires[keyed_below(world_seed, 0, i, MOTIF_LIENS, len(paires))]
        voisins[a].append(b)
        voisins[b].append(a)
    return voisins


def _placer(world_seed: int, motif: str, nombre: int, systemes: list[int]) -> list[int]:
    """Le système de chaque site i (i = 1 à nombre), tiré parmi les systèmes encore libres."""
    libres = list(systemes)
    places: list[int] = []
    for i in range(1, nombre + 1):
        choisi = libres[keyed_below(world_seed, 0, i, motif, len(libres))]
        places.append(choisi)
        libres.remove(choisi)
    return places


def generate(world_seed: int, tunables: Tunables) -> State:
    """L'état du tick 0 : la carte, les gisements pleins, les stations, aucun acteur."""
    voisins = _graphe(world_seed, tunables)
    systemes = sorted(voisins)
    nombre_de_stations = _entre(
        world_seed, 0, MOTIF_NOMBRE_DE_STATIONS, tunables.stations_min, tunables.stations_max
    )
    nombre_de_gisements = _entre(
        world_seed, 0, MOTIF_NOMBRE_DE_GISEMENTS, tunables.deposits_min, tunables.deposits_max
    )
    lieux_des_stations = _placer(world_seed, MOTIF_STATIONS, nombre_de_stations, systemes)
    lieux_des_gisements = _placer(world_seed, MOTIF_GISEMENTS, nombre_de_gisements, systemes)
    stations = tuple(
        Station(id=i, system_id=s, ore_prices=tunables.station_ore_prices[i - 1])
        for i, s in enumerate(lieux_des_stations, start=1)
    )
    gisements = tuple(
        Deposit(
            id=i,
            system_id=s,
            ore_id=1 if (i & 1) == 1 else 2,
            stock=tunables.deposit_stock,
        )
        for i, s in enumerate(lieux_des_gisements, start=1)
    )
    return State(
        tick=0,
        systems=tuple(System(id=s, neighbors=tuple(sorted(voisins[s]))) for s in systemes),
        deposits=gisements,
        stations=stations,
        actors=(),
        ships=(),
        ledger=ledger_vide(),
        last_tick=LastTick(events=(), results=()),
    )


def npc_count(world_seed: int, tunables: Tunables) -> int:
    """Le nombre de PNJ de la partie, tiré de la graine du monde (ce n'est pas un champ de
    l'état : `__main__.py` crée les PNJ par des ordres d'administration au tick 1)."""
    return _entre(world_seed, 0, MOTIF_NOMBRE_DE_PNJ, tunables.npc_min, tunables.npc_max)


def label(table: str, id: int) -> str:  # noqa: A002
    """Libellé neutre : system_1, deposit_2, station_1, actor_1, ship_1 ; minerai : ore_a, ore_b."""
    if table == "ore":
        return "ore_" + chr(ord("a") + id - 1)
    return f"{table}_{id}"
