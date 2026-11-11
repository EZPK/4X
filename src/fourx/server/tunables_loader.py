"""Lecture des réglages du paquet.

Document : docs/designs/niveau-2-m1-noyau.md,
Technical Plan, point 2 ; plan détaillé, point 21.
Les bornes de `Tunables` sont vérifiées au décodage.
"""

import importlib.resources

import msgspec.toml

from fourx.core.tunables import Tunables


def load_tunables() -> Tunables:
    """Les réglages de M1, lus dans fourx/core/tunables.toml."""
    donnees = importlib.resources.files("fourx.core").joinpath("tunables.toml").read_bytes()
    return msgspec.toml.decode(donnees, type=Tunables)
