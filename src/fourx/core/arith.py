"""Arithmétique entière du noyau (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 4).

Seul module du noyau qui emploie `//` et `%`. La division et le reste sont tronqués vers zéro,
comme en Rust : div_trunc(-7, 2) = -3 et rem_trunc(-7, 2) = -1, avec
a = b × div_trunc(a, b) + rem_trunc(a, b). Une division par zéro lève ZeroDivisionError.
"""


def div_trunc(a: int, b: int) -> int:
    """Quotient tronqué vers zéro."""
    quotient = abs(a) // abs(b)
    # a ^ b est négatif exactement quand a et b sont de signes opposés.
    return -quotient if (a ^ b) < 0 else quotient


def rem_trunc(a: int, b: int) -> int:
    """Reste du quotient tronqué vers zéro ; il a le signe de `a`."""
    return a - b * div_trunc(a, b)


def mul_div_trunc(a: int, b: int, c: int) -> int:
    """a × b / c en une seule opération, tronqué vers zéro."""
    return div_trunc(a * b, c)


def mul_div_ceil(a: int, b: int, c: int) -> int:
    """a × b / c arrondi vers le haut, pour des nombres positifs ou nuls (taxe)."""
    if a < 0 or b < 0 or c <= 0:
        raise ValueError("mul_div_ceil attend a et b positifs ou nuls et c positif")
    return -((-(a * b)) // c)
