"""Configuration commune de tous les tests.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 7.

Chemin protégé. Le profil hypothesis « ci » rend les tests de propriétés reproductibles,
en CI comme sous mutmut, pour que le score de mutation de la base et celui de la tête
soient comparables.
"""

import os

import pytest
from hypothesis import settings

settings.register_profile("ci", derandomize=True, database=None, deadline=None)
settings.load_profile("ci")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Saute les tests marqués « mesure », sauf si FOURX_MESURE=1."""
    if os.environ.get("FOURX_MESURE") == "1":
        return
    saut = pytest.mark.skip(reason="indicateur avancé : lancer avec FOURX_MESURE=1")
    for item in items:
        if item.get_closest_marker("mesure") is not None:
            item.add_marker(saut)
