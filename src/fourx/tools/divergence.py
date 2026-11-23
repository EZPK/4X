"""L'outil de divergence (niveau 1, CUJ 4 ; docs/designs/niveau-2-m1-noyau.md, Technical Plan,
points 8 et 13).

Compare deux suites d'empreintes, lues dans un dossier de partie (journal des ordres) ou dans un
fichier d'empreintes (une ligne JSON de `Fingerprints` par tick), et indique le premier tick qui
diffère et les composants concernés.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import msgspec

from fourx.core.fingerprints import Fingerprints
from fourx.server.order_log import OrderLog

COMPOSANTS = tuple(f for f in Fingerprints.__struct_fields__ if f != "tick")


def first_divergence(
    a: Sequence[Fingerprints], b: Sequence[Fingerprints]
) -> tuple[int, tuple[str, ...]] | None:
    """Le premier tick où a et b diffèrent, et les composants qui diffèrent ; None si aucun.

    Un tick présent d'un seul côté diffère par tous ses composants."""
    for x, y in zip(a, b, strict=False):
        differents = tuple(c for c in COMPOSANTS if getattr(x, c) != getattr(y, c))
        if differents or x.tick != y.tick:
            return x.tick, differents
    if len(a) != len(b):
        return (a if len(a) > len(b) else b)[min(len(a), len(b))].tick, COMPOSANTS
    return None


def lire_empreintes(chemin: Path) -> tuple[Fingerprints, ...]:
    """Les empreintes d'un dossier de partie, ou d'un fichier d'empreintes."""
    if chemin.is_dir():
        journal = OrderLog(chemin / "orders.sqlite")
        try:
            return journal.fingerprints_by_tick()
        finally:
            journal.close()
    decodeur = msgspec.json.Decoder(Fingerprints)
    lignes = chemin.read_bytes().splitlines()
    return tuple(decodeur.decode(ligne) for ligne in lignes if ligne.strip())


def texte(divergence: tuple[int, tuple[str, ...]] | None) -> str:
    if divergence is None:
        return "aucune divergence"
    tick, composants = divergence
    return f"tick {tick} : {', '.join(composants)}"


def main(argv: Sequence[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(prog="python -m fourx.tools.divergence")
    parseur.add_argument("a", type=Path, help="dossier de partie ou fichier d'empreintes")
    parseur.add_argument("b", type=Path, help="dossier de partie ou fichier d'empreintes")
    arguments = parseur.parse_args(argv)
    divergence = first_divergence(lire_empreintes(arguments.a), lire_empreintes(arguments.b))
    print(texte(divergence))
    return 0 if divergence is None else 1


if __name__ == "__main__":
    sys.exit(main())
