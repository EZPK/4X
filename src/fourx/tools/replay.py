"""Le rejeu (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 8 et 13).

`replay_orders` part d'un état initial et des ordres soumis de chaque tick, applique `step` tick
par tick, et rend les empreintes et les événements de chaque tick. La commande rejoue un dossier
de partie (instantané initial et journal des ordres) sur les réglages de `tunables.toml`.
"""

import argparse
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

import msgspec

from fourx.core import snapshot
from fourx.core.fingerprints import Fingerprints, fingerprints
from fourx.core.state import State
from fourx.core.step import step
from fourx.core.tunables import Tunables
from fourx.core.version import rules_version
from fourx.schema.events import Event
from fourx.schema.orders import SubmittedOrder
from fourx.server.order_log import OrderLog
from fourx.server.tunables_loader import load_tunables
from fourx.tools.divergence import first_divergence, texte


def replay_orders(
    initial: State,
    orders_by_tick: Iterable[tuple[SubmittedOrder, ...]],
    world_seed: int,
    tunables: Tunables,
) -> tuple[tuple[Fingerprints, ...], tuple[Event, ...]]:
    etat = initial
    empreintes: list[Fingerprints] = []
    evenements: list[Event] = []
    for ordres in orders_by_tick:
        etat, produits = step(etat, ordres, world_seed, tunables)
        empreintes.append(fingerprints(etat))
        evenements.extend(produits)
    return tuple(empreintes), tuple(evenements)


def main(argv: Sequence[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(prog="python -m fourx.tools.replay")
    parseur.add_argument("dossier", type=Path, help="dossier de partie")
    parseur.add_argument("--export-fingerprints", type=Path, metavar="FICHIER")
    arguments = parseur.parse_args(argv)
    tunables = load_tunables()
    initial = snapshot.decode((arguments.dossier / "snapshot.msgpack").read_bytes())
    if initial.rules_version != rules_version(tunables):
        print(
            f"règles différentes : partie {initial.rules_version}, "
            f"tunables.toml {rules_version(tunables)}"
        )
        return 1
    journal = OrderLog(arguments.dossier / "orders.sqlite")
    try:
        ordres, enregistrees = journal.orders_by_tick(), journal.fingerprints_by_tick()
    finally:
        journal.close()
    empreintes, _ = replay_orders(initial.state, ordres, initial.world_seed, tunables)
    if arguments.export_fingerprints is not None:
        arguments.export_fingerprints.write_bytes(
            b"".join(msgspec.json.encode(e) + b"\n" for e in empreintes)
        )
    divergence = first_divergence(enregistrees, empreintes)
    print(texte(divergence))
    return 0 if divergence is None else 1


if __name__ == "__main__":
    sys.exit(main())
