"""Tests de fourx.core.arith (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 4)."""

import pytest

from fourx.core.arith import div_trunc, mul_div_ceil, mul_div_trunc, rem_trunc


@pytest.mark.parametrize(
    ("a", "b", "quotient", "reste"),
    [
        (7, 2, 3, 1),
        (-7, 2, -3, -1),
        (7, -2, -3, 1),
        (-7, -2, 3, -1),
        (6, 3, 2, 0),
        (-6, 3, -2, 0),
        (0, 5, 0, 0),
        (1, 3, 0, 1),
        (-1, 3, 0, -1),
        (5, 5, 1, 0),
        (-5, -5, 1, 0),
        (0, -3, 0, 0),
    ],
)
def test_division_et_reste_tronques_vers_zero(a: int, b: int, quotient: int, reste: int) -> None:
    assert div_trunc(a, b) == quotient
    assert rem_trunc(a, b) == reste
    assert b * div_trunc(a, b) + rem_trunc(a, b) == a


def test_division_par_zero() -> None:
    with pytest.raises(ZeroDivisionError):
        div_trunc(1, 0)
    with pytest.raises(ZeroDivisionError):
        rem_trunc(1, 0)


def test_mul_div_trunc() -> None:
    assert mul_div_trunc(7, 3, 2) == 10
    assert mul_div_trunc(-7, 3, 2) == -10
    assert mul_div_trunc(2**62, 4, 8) == 2**61


@pytest.mark.parametrize(
    ("a", "b", "c", "attendu"),
    [
        (45, 1000, 10000, 5),
        (1500, 1000, 10000, 150),
        (1, 1, 3, 1),
        (0, 7, 3, 0),
        (9, 1, 3, 3),
        (5, 0, 3, 0),
        (7, 1, 1, 7),
    ],
)
def test_mul_div_ceil(a: int, b: int, c: int, attendu: int) -> None:
    assert mul_div_ceil(a, b, c) == attendu


@pytest.mark.parametrize(("a", "b", "c"), [(-1, 1, 1), (1, -1, 1), (1, 1, 0), (1, 1, -2)])
def test_mul_div_ceil_refuse_les_negatifs(a: int, b: int, c: int) -> None:
    with pytest.raises(
        ValueError, match="^mul_div_ceil attend a et b positifs ou nuls et c positif$"
    ):
        mul_div_ceil(a, b, c)
