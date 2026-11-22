"""Tests de la palette (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter)."""

import re

import pytest

from fourx.clients.palette import (
    CONTRAST_PAIRS,
    GRAPHIC_PAIRS,
    PALETTE,
    contrast_ratio,
    luminance,
)


def test_seize_roles_seize_valeurs_distinctes() -> None:
    assert len(PALETTE) == 16
    assert len(set(PALETTE.values())) == 16
    assert all(re.fullmatch(r"#[0-9A-F]{6}", v) for v in PALETTE.values())


def test_luminance_et_contraste_sur_des_valeurs_connues() -> None:
    assert luminance("#FFFFFF") == pytest.approx(1.0)
    assert luminance("#000000") == pytest.approx(0.0)
    assert luminance("#808080") == pytest.approx(0.21586050)
    assert luminance("#FF0000") == pytest.approx(0.2126)
    assert luminance("#00FF00") == pytest.approx(0.7152)
    assert luminance("#0000FF") == pytest.approx(0.0722)
    assert luminance("#0A0A0A") == pytest.approx(0.00303527)  # sous le coude de 0,04045
    assert contrast_ratio("ombre", "ombre") == pytest.approx(1.0)
    assert contrast_ratio("texte", "ombre") == contrast_ratio("ombre", "texte")
    assert contrast_ratio("texte", "ombre") == pytest.approx(17.78, abs=0.01)


def test_les_couples_de_texte_sont_ceux_du_point_7_ter() -> None:
    textes: tuple[str, ...] = ("texte", "texte_attenue", "accent", "ore_a", "ore_b", "succes")
    textes += ("alerte", "vaisseau", "station")
    attendus = {(t, f) for f in ("fond", "cadre") for t in textes}
    attendus |= {("texte", "cadre_clair"), ("texte_attenue", "cadre_clair")}
    attendus |= {("fond", e) for e in ("station", "alerte", "accent", "succes", "vaisseau")}
    assert set(CONTRAST_PAIRS) == attendus
    assert len(CONTRAST_PAIRS) == len(attendus)
    assert set(GRAPHIC_PAIRS) == {
        ("trait_fort", "fond"),
        ("trait_faible", "fond"),
        ("accent", "cadre"),
        ("trait_faible", "cadre"),
    }


@pytest.mark.parametrize(("texte", "fond"), CONTRAST_PAIRS)
def test_contraste_du_texte_au_moins_4_5(texte: str, fond: str) -> None:
    assert contrast_ratio(texte, fond) >= 4.5


@pytest.mark.parametrize(("trait", "fond"), GRAPHIC_PAIRS)
def test_contraste_des_traits_au_moins_3(trait: str, fond: str) -> None:
    assert contrast_ratio(trait, fond) >= 3.0
