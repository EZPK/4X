"""La politique du PNJ de M1, référence scriptée du glossaire, en version 2.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 (amendement 1).

La politique reste une fonction pure. Sa seule mémoire, d'un tick à l'autre, est l'ensemble des
gisements que le vaisseau a vus vides : `decide` le reçoit et rend l'ensemble à jour, que l'hôte
des PNJ garde et lui repasse à la décision suivante. Avant de décider, `decide` le met à jour à
partir de l'observation : un gisement visible de stock nul y entre ; un gisement visible de stock
positif en sort ; quand tous les gisements du monde y sont, l'ensemble se vide.

Pour chaque vaisseau à l'arrêt ou en minage :
1. dans le système d'une station, hors minage, cargaison non vide : vendre le minerai le plus
   abondant (à quantités égales, le plus petit identifiant) ;
2. cargaison pleine, ailleurs : aller à la station qui paie le mieux le minerai le plus abondant
   de la cargaison (à prix égal, la plus proche en sauts, puis le plus petit identifiant) ;
3. sinon : viser le minerai qui a le meilleur prix, toutes stations confondues (à prix égal, le
   plus petit identifiant) ; aller au plus proche des gisements de ce minerai qui ne sont pas
   dans l'ensemble des gisements vus vides, en sauts puis par identifiant, puis miner ; si tous
   y sont, faire de même avec l'autre minerai ; si aucun gisement ne convient, rester à l'arrêt.
La politique n'émet un ordre que si l'activité voulue diffère de l'activité observée.
"""

from fourx.policies.cargo import most_abundant
from fourx.policies.geometry import distances
from fourx.schema.actors import Activity
from fourx.schema.observation import DepositView, Observation, OwnShipView
from fourx.schema.orders import Command, Mine, Move, Order, OrderCategory, Sell

POLICY_ID = "scripted_miner"
POLICY_VERSION = 2


def mettre_a_jour(observation: Observation, seen_empty: frozenset[int]) -> frozenset[int]:
    """L'ensemble des gisements vus vides, mis à jour à partir de l'observation."""
    vus = set(seen_empty)
    for d in observation.deposits:
        if d.stock == 0:
            vus.add(d.id)
        elif d.stock is not None:
            vus.discard(d.id)
    tous = {d.id for d in observation.deposits}
    if tous and vus >= tous:
        # Tous les gisements y sont : l'ensemble se vide, et seuls les gisements vus vides à
        # l'instant y rentrent (s'ils sont tous vus vides, l'ensemble reste vide).
        vus = {d.id for d in observation.deposits if d.stock == 0}
        if vus >= tous:
            vus = set()
    return frozenset(vus)


def _gisement_vise(
    observation: Observation, dist: dict[int, int], seen_empty: frozenset[int]
) -> DepositView | None:
    # Indices de prix, de 0 à nombre − 1 : le minerai d'indice i a l'identifiant i + 1.
    meilleurs = sorted(
        range(len(observation.stations[0].ore_prices)),
        key=lambda i: (-max(s.ore_prices[i] for s in observation.stations), i),
    )
    for indice in meilleurs:
        candidats = [
            d
            for d in observation.deposits
            if d.ore_id == indice + 1 and d.id not in seen_empty and d.system_id in dist
        ]
        if candidats:
            return min(candidats, key=lambda d: (dist[d.system_id], d.id))
    return None


def _commande(
    observation: Observation, navire: OwnShipView, seen_empty: frozenset[int]
) -> Command | None:
    if navire.activity is Activity.EN_ROUTE:
        return None
    dist = distances(observation.systems, navire.system_id)
    ici = [s for s in observation.stations if s.system_id == navire.system_id]
    abondant = most_abundant(navire.cargo)
    if ici and abondant is not None and navire.activity is not Activity.MINING:
        return Sell(ship_id=navire.id, ore_id=abondant[0], quantity=abondant[1])
    if sum(navire.cargo) >= navire.capacity and abondant is not None:
        ore_id = abondant[0]
        station = min(
            (s for s in observation.stations if s.system_id in dist),
            key=lambda s: (-s.ore_prices[ore_id - 1], dist[s.system_id], s.id),
        )
        if station.system_id == navire.system_id:
            return None
        return Move(ship_id=navire.id, target_system_id=station.system_id)
    cible = _gisement_vise(observation, dist, seen_empty)
    if cible is None:
        return None
    if navire.system_id != cible.system_id:
        return Move(ship_id=navire.id, target_system_id=cible.system_id)
    if navire.activity is Activity.MINING:
        return None
    return Mine(ship_id=navire.id, ore_id=cible.ore_id)


def decide(
    observation: Observation, seen_empty: frozenset[int] = frozenset()
) -> tuple[tuple[Order, ...], frozenset[int]]:
    """Les ordres du PNJ pour le prochain tick, et l'ensemble à jour des gisements vus vides ;
    numéro d'ordre : tick observé × 100 + rang du vaisseau."""
    vus = mettre_a_jour(observation, seen_empty)
    ordres: list[Order] = []
    for rang, navire in enumerate(observation.own_ships):
        commande = _commande(observation, navire, vus)
        if commande is not None:
            ordres.append(
                Order(
                    actor_id=observation.actor_id,
                    number=observation.tick * 100 + rang,
                    category=OrderCategory.PLAYER,
                    policy_id=POLICY_ID,
                    policy_version=POLICY_VERSION,
                    command=commande,
                )
            )
    return tuple(ordres), vus
