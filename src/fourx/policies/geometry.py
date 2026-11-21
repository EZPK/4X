"""Distances en sauts sur la carte de l'observation.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 7 et 13. Aucune logique de
décision : le PNJ et le client la réutilisent.
"""

from fourx.schema.observation import SystemView


def distances(systems: tuple[SystemView, ...], start: int) -> dict[int, int]:
    """Distance en sauts de chaque système accessible depuis `start`, par un parcours en largeur
    sur les voisins, par identifiant croissant."""
    voisins = {s.id: sorted(s.neighbors) for s in systems}
    resultat = {start: 0}
    file = [start]
    while file:
        courant = file.pop(0)
        for voisin in voisins.get(courant, []):
            if voisin not in resultat:
                resultat[voisin] = resultat[courant] + 1
                file.append(voisin)
    return resultat
