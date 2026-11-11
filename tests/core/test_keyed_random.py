"""Tests de fourx.core.keyed_random (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 4).

Les valeurs attendues sont figées : une implémentation en Rust doit les reproduire.
"""

import pytest

from fourx.core.keyed_random import cle, keyed_below, keyed_draw


def test_encodage_canonique_de_la_cle() -> None:
    attendu = (
        "0100000000000000"  # graine 1
        "0200000000000000"  # tick 2
        "0300000000000000"  # entité 3
        "0200000000000000"  # longueur du motif
        "6162"  # « ab » en UTF-8
        "0400000000000000"  # essai 4
    )
    assert cle(1, 2, 3, "ab", 4).hex() == attendu


def test_entiers_signes_et_motif_utf8() -> None:
    encode = cle(-1, 0, 0, "é")
    assert encode[:8] == b"\xff" * 8
    assert encode[24:32] == (2).to_bytes(8, "little")
    assert encode[32:34] == "é".encode()


@pytest.mark.parametrize(
    ("arguments", "attendu"),
    [
        ((0, 0, 0, "carte"), 11920751339527598322),
        ((1, 1, 1, "minage"), 16781641023821713541),
        ((1, 1, 2, "minage"), 3516060242461741786),
        ((-5, 7, 3, "é"), 2714147288712901879),
    ],
)
def test_valeurs_figees(arguments: tuple[int, int, int, str], attendu: int) -> None:
    assert keyed_draw(*arguments) == attendu


def test_essai_change_le_tirage() -> None:
    assert keyed_draw(1, 1, 1, "minage", 0) == keyed_draw(1, 1, 1, "minage")
    assert keyed_draw(1, 1, 1, "minage", 1) != keyed_draw(1, 1, 1, "minage", 0)


def test_tirage_sur_64_bits() -> None:
    valeurs = [keyed_draw(g, 0, 0, "x") for g in range(200)]
    assert all(0 <= v < 2**64 for v in valeurs)
    assert max(valeurs) >= 2**63


def test_tirage_borne() -> None:
    assert keyed_below(1, 0, 0, "carte", 6) == 0
    assert keyed_below(42, 0, 0, "carte", 6) == 4
    valeurs = {keyed_below(g, 0, 0, "carte", 6) for g in range(300)}
    assert valeurs == set(range(6))
    assert keyed_below(9, 9, 9, "x", 1) == 0


def test_tirage_borne_rejette_au_dela_du_plus_grand_multiple() -> None:
    n = 2**63 + 1
    graine = next(g for g in range(1000) if keyed_draw(g, 0, 0, "r") >= 2**64 - (2**64 % n))
    attendu = next(
        v % n
        for e in range(1, 100)
        if (v := keyed_draw(graine, 0, 0, "r", e)) < 2**64 - (2**64 % n)
    )
    assert keyed_below(graine, 0, 0, "r", n) == attendu


@pytest.mark.parametrize("n", [0, -3])
def test_tirage_borne_refuse_n_non_positif(n: int) -> None:
    with pytest.raises(ValueError):
        keyed_below(1, 0, 0, "x", n)
