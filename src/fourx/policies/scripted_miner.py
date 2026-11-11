"""La politique du PNJ de M1, référence scriptée du glossaire.

Document : docs/designs/niveau-2-m1-noyau.md,
Technical Plan, point 7 ; plan détaillé, point 22.

Activité voulue :
- à la station, hors minage, cargaison non vide : tout vendre, un minerai par tick, le plus
  abondant d'abord ;
- cargaison pleine ailleurs : aller à la station ;
- sinon : parmi les gisements non vides, aller à celui dont le minerai est le mieux payé, puis
  miner ;
- tous les gisements vides : rester à l'arrêt.
La politique n'émet un ordre que si l'activité observée diffère de l'activité voulue. Elle ne
garde aucune mémoire d'un tick à l'autre : « tout vendre » se lit sur la cargaison restante.
"""

from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OwnShipView
from fourx.schema.orders import Command, Mine, Move, Order, OrderCategory, Sell

POLICY_ID = "scripted_miner"
POLICY_VERSION = 1


def _commande(observation: Observation, navire: OwnShipView) -> Command | None:
    if navire.activity is Activity.EN_ROUTE:
        return None
    station = observation.stations[0]
    a_la_station = navire.system_id == station.system_id
    if a_la_station and sum(navire.cargo) > 0 and navire.activity is not Activity.MINING:
        # max garde le premier maximum : à quantités égales, le plus petit identifiant de minerai.
        rang, quantite = max(enumerate(navire.cargo), key=lambda e: e[1])
        return Sell(ship_id=navire.id, ore_id=rang + 1, quantity=quantite)
    if sum(navire.cargo) >= navire.capacity:
        return None if a_la_station else Move(ship_id=navire.id, target_system_id=station.system_id)
    non_vides = [d for d in observation.deposits if d.stock > 0]
    if not non_vides:
        return None
    cible = max(non_vides, key=lambda d: (station.ore_prices[d.ore_id - 1], -d.id))
    if navire.system_id != cible.system_id:
        return Move(ship_id=navire.id, target_system_id=cible.system_id)
    if navire.activity is Activity.MINING:
        return None
    return Mine(ship_id=navire.id, ore_id=cible.ore_id)


def decide(observation: Observation) -> tuple[Order, ...]:
    """Les ordres du PNJ pour le prochain tick ; numéro d'ordre : tick observé × 100 + rang."""
    ordres: list[Order] = []
    for rang, navire in enumerate(observation.own_ships):
        commande = _commande(observation, navire)
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
    return tuple(ordres)
