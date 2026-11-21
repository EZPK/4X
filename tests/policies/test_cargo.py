"""Tests de `policies/cargo.py` (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 7 et
13 ; plan détaillé, point 23 quater)."""

from fourx.policies.cargo import most_abundant


def test_minerai_le_plus_abondant() -> None:
    assert most_abundant((30, 70)) == (2, 70)
    assert most_abundant((70, 30)) == (1, 70)


def test_egalite_plus_petit_identifiant() -> None:
    assert most_abundant((50, 50)) == (1, 50)


def test_cargaison_vide() -> None:
    assert most_abundant((0, 0)) is None
