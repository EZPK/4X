"""Enregistrement des événements v0.

Document : docs/designs/niveau-2-m1-noyau.md,
Technical Plan, points 5 et 6 ; plan détaillé, point 21.
Une ligne JSON msgspec par `Event` ; le fichier est à jour après chaque tick.
"""

from pathlib import Path

import msgspec.json

from fourx.schema.events import Event


class EventsWriter:
    def __init__(self, path: Path) -> None:
        self._fichier = path.open("ab")
        self._encodeur = msgspec.json.Encoder()

    def write(self, events: tuple[Event, ...]) -> None:
        for event in events:
            self._fichier.write(self._encodeur.encode(event) + b"\n")
        self._fichier.flush()

    def close(self) -> None:
        self._fichier.close()
