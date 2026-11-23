"""Les grandeurs de l'économie par fenêtre de ticks (docs/designs/niveau-2-m1-noyau.md, Technical
Plan, points 9 et 13).

Une seule fonction, `window_stats`, les calcule à partir des événements v0 : l'émission par motif
(écritures débitées du compte d'émission), la destruction par motif (écritures créditées au
compte de destruction), la croissance de la masse monétaire et la masse monétaire en fin de
fenêtre. Le registre ne connaît que ces deux comptes hors de la masse monétaire : la masse
monétaire vaut donc l'émission cumulée moins la destruction cumulée.
"""

from collections.abc import Iterable

import msgspec

from fourx.core.ledger import DESTRUCTION_ACCOUNT_ID, ISSUANCE_ACCOUNT_ID
from fourx.schema.events import Event, LedgerEntryRecorded
from fourx.schema.ledger import Reason
from fourx.schema.types import Int64

MOTIFS = tuple(Reason)


class WindowStats(msgspec.Struct, frozen=True):
    """Les grandeurs d'une fenêtre ; les compteurs par motif suivent l'ordre de `Reason`."""

    first_tick: Int64
    issued_by_reason: tuple[Int64, ...]
    destroyed_by_reason: tuple[Int64, ...]
    money_supply_growth: Int64
    money_supply_end: Int64


def window_stats(events: Iterable[Event], window: int = 10_000) -> tuple[WindowStats, ...]:
    """Les fenêtres des ticks 1 à `window`, `window` + 1 à 2 × `window`…, jusqu'à celle du
    dernier tick des événements, fenêtres sans écriture comprises ; aucune sans événement."""
    if window <= 0:
        raise ValueError("une fenêtre compte au moins un tick")
    emis: dict[int, list[int]] = {}
    detruit: dict[int, list[int]] = {}
    dernier = 0
    for event in events:
        dernier = max(dernier, event.tick)
        if not isinstance(event.payload, LedgerEntryRecorded):
            continue
        entree = event.payload.entry
        rang = (event.tick - 1) // window
        motif = MOTIFS.index(entree.reason)
        if entree.debit_account_id == ISSUANCE_ACCOUNT_ID:
            emis.setdefault(rang, [0] * len(MOTIFS))[motif] += entree.amount
        if entree.credit_account_id == DESTRUCTION_ACCOUNT_ID:
            detruit.setdefault(rang, [0] * len(MOTIFS))[motif] += entree.amount
    fenetres: list[WindowStats] = []
    masse = 0
    zeros = [0] * len(MOTIFS)
    for rang in range(-(-dernier // window)):
        e = emis.get(rang, zeros)
        d = detruit.get(rang, zeros)
        croissance = sum(e) - sum(d)
        masse += croissance
        fenetres.append(
            WindowStats(
                first_tick=rang * window + 1,
                issued_by_reason=tuple(e),
                destroyed_by_reason=tuple(d),
                money_supply_growth=croissance,
                money_supply_end=masse,
            )
        )
    return tuple(fenetres)
