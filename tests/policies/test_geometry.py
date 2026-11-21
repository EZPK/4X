"""Tests de `policies/geometry.py` (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 7 et
13 ; plan détaillé, point 23 quater)."""

from fourx.policies.geometry import distances
from fourx.schema.observation import SystemView


def test_distances_en_sauts() -> None:
    systemes = (
        SystemView(id=1, neighbors=(2, 3)),
        SystemView(id=2, neighbors=(1, 4)),
        SystemView(id=3, neighbors=(1, 4)),
        SystemView(id=4, neighbors=(2, 3, 5)),
        SystemView(id=5, neighbors=(4,)),
    )
    assert distances(systemes, 1) == {1: 0, 2: 1, 3: 1, 4: 2, 5: 3}
    assert distances(systemes, 5) == {5: 0, 4: 1, 2: 2, 3: 2, 1: 3}


def test_systeme_isole() -> None:
    assert distances((SystemView(id=1, neighbors=()),), 1) == {1: 0}
