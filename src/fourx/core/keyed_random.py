"""Générateur à clé (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 4 ; niveau 1, §2).

La clé est (graine du monde, tick, entité, motif du tirage, numéro d'essai). Chaque entier
est encodé sur 8 octets, signé, petit-boutiste ; le motif est encodé en UTF-8, précédé de sa
longueur sur 8 octets. Le tirage est BLAKE2b avec un condensé de 8 octets, lu comme un entier
non signé petit-boutiste. Ajouter un tirage ne décale pas les autres.
"""

import hashlib

from fourx.core.arith import div_trunc, rem_trunc

ETENDUE = 2**64


def _entier(valeur: int) -> bytes:
    return valeur.to_bytes(8, "little", signed=True)


def cle(world_seed: int, tick: int, entity: int, motif: str, attempt: int = 0) -> bytes:
    """Encodage canonique de la clé d'un tirage."""
    texte = motif.encode("utf-8")
    return (
        _entier(world_seed)
        + _entier(tick)
        + _entier(entity)
        + _entier(len(texte))
        + texte
        + _entier(attempt)
    )


def keyed_draw(world_seed: int, tick: int, entity: int, motif: str, attempt: int = 0) -> int:
    """Un tirage de 64 bits, de 0 à 2^64 − 1."""
    condense = hashlib.blake2b(cle(world_seed, tick, entity, motif, attempt), digest_size=8)
    return int.from_bytes(condense.digest(), "little")


def keyed_below(world_seed: int, tick: int, entity: int, motif: str, n: int) -> int:
    """Un tirage de 0 à n − 1, sans biais : les valeurs au-delà du plus grand multiple de n
    sont rejetées, et le tirage recommence avec le numéro d'essai suivant."""
    if n <= 0:
        raise ValueError("keyed_below attend n positif")
    limite = div_trunc(ETENDUE, n) * n
    essai = 0
    while True:
        valeur = keyed_draw(world_seed, tick, entity, motif, essai)
        if valeur < limite:
            return rem_trunc(valeur, n)
        essai += 1
