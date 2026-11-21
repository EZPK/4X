"""Tests des contrôles croisés des réglages (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 2, amendement 1).

Chaque contrôle est essayé à sa limite, acceptée, puis juste au-delà, refusée avec son message.
"""

from typing import Any

import msgspec
import pytest

from fourx.core.tunables import Tunables
from tests.aide_monde import REGLAGES


def reglages(**changes: Any) -> Tunables:
    """REGLAGES avec quelques champs changés, en repassant par __post_init__."""
    return Tunables(**{**msgspec.structs.asdict(REGLAGES), **changes})


def test_les_reglages_de_test_sont_acceptes() -> None:
    assert reglages() == REGLAGES


@pytest.mark.parametrize(
    ("bas", "haut"),
    [
        ("systems_min", "systems_max"),
        ("deposits_min", "deposits_max"),
        ("stations_min", "stations_max"),
        ("npc_min", "npc_max"),
    ],
)
def test_un_minimum_ne_depasse_pas_son_maximum(bas: str, haut: str) -> None:
    maximum = getattr(REGLAGES, haut)
    assert getattr(reglages(**{bas: maximum}), bas) == maximum
    with pytest.raises(ValueError, match=f"^{bas} dépasse {haut}$"):
        reglages(**{bas: maximum + 1})


def test_une_ligne_de_prix_par_station_possible() -> None:
    lignes = REGLAGES.station_ore_prices
    assert len(lignes) == REGLAGES.stations_max
    assert reglages(station_ore_prices=(*lignes, (1, 1))).station_ore_prices[3] == (1, 1)
    with pytest.raises(ValueError, match="^station_ore_prices a moins de stations_max lignes$"):
        reglages(station_ore_prices=lignes[:2])


@pytest.mark.parametrize("ligne", [(10,), (10, 15, 20)])
def test_un_prix_par_minerai_dans_chaque_ligne(ligne: tuple[int, ...]) -> None:
    lignes = (*REGLAGES.station_ore_prices[:2], ligne)
    with pytest.raises(
        ValueError, match="^chaque ligne de station_ore_prices a un prix par minerai$"
    ):
        reglages(station_ore_prices=lignes)


def test_au_moins_deux_gisements_par_minerai() -> None:
    assert reglages(deposits_min=4).deposits_min == 4
    with pytest.raises(
        ValueError, match=r"^deposits_min est inférieur à 4 \(deux gisements par minerai\)$"
    ):
        reglages(deposits_min=3)


def test_assez_de_systemes_pour_les_gisements() -> None:
    assert reglages(systems_min=6).systems_min == REGLAGES.deposits_max
    with pytest.raises(
        ValueError, match="^systems_min est inférieur à deposits_max ou à stations_max$"
    ):
        reglages(systems_min=5)


def test_assez_de_systemes_pour_les_stations() -> None:
    """Gisements bornés à 4 : seul le nombre de stations peut dépasser systems_min."""
    peu = {"deposits_max": 4, "systems_min": 4}
    lignes = ((1, 1),) * 5
    assert reglages(**peu, stations_max=4, station_ore_prices=lignes).stations_max == 4
    with pytest.raises(
        ValueError, match="^systems_min est inférieur à deposits_max ou à stations_max$"
    ):
        reglages(**peu, stations_max=5, station_ore_prices=lignes)


def test_au_moins_deux_voisins_par_systeme() -> None:
    assert reglages(max_neighbors=2).max_neighbors == 2
    with pytest.raises(ValueError, match="^max_neighbors est inférieur à 2$"):
        reglages(max_neighbors=1)
