"""Lecture d'une cargaison.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 7 et 13. Aucune logique de
décision : le PNJ et le client la réutilisent.
"""


def most_abundant(cargo: tuple[int, ...]) -> tuple[int, int] | None:
    """Le minerai le plus abondant (identifiant à partir de 1) et sa quantité ; à quantités
    égales, le plus petit identifiant ; None si la cargaison est vide."""
    if sum(cargo) <= 0:
        return None
    rang, quantite = max(enumerate(cargo), key=lambda e: (e[1], -e[0]))
    return rang + 1, quantite
