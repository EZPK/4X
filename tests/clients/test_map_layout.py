"""Tests de fourx.clients.map_layout (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 7 bis, « Mise en page de la carte » et « Sortie de `layout` »)."""

import re

import msgspec
import pytest

from fourx.clients.map_layout import LARGEUR, layout, rangs
from fourx.core.observe import observe
from fourx.core.world import generate
from fourx.schema.observation import DepositView, Observation, StationView, SystemView
from fourx.server.tunables_loader import load_tunables
from tests.aide_observation import observation


def carte(
    voisins: dict[int, tuple[int, ...]],
    stations: tuple[StationView, ...] = (),
    gisements: tuple[DepositView, ...] = (),
) -> Observation:
    return msgspec.structs.replace(
        observation(),
        systems=tuple(SystemView(id=s, neighbors=v) for s, v in sorted(voisins.items())),
        stations=stations,
        deposits=gisements,
    )


def symetrique(liens: list[tuple[int, int]], n: int) -> dict[int, tuple[int, ...]]:
    voisins: dict[int, list[int]] = {s: [] for s in range(1, n + 1)}
    for a, b in liens:
        voisins[a].append(b)
        voisins[b].append(a)
    return {s: tuple(sorted(v)) for s, v in voisins.items()}


def test_sortie_d_une_petite_carte() -> None:
    """1–2–3 en ligne (tracés), 1–4 et 3–4 écrits ; S1 et un gisement de ore_b dans system_2."""
    obs = carte(
        symetrique([(1, 2), (2, 3), (1, 4), (3, 4)], 4),
        stations=(StationView(id=1, system_id=2, ore_prices=(10, 15)),),
        gisements=(
            DepositView(id=1, system_id=2, ore_id=2, stock=None),
            DepositView(id=2, system_id=4, ore_id=1, stock=None),
        ),
    )
    assert layout(obs) == [
        "[1]─────[2]S1b──[3]",
        "        [4]a",
        "liens : 1–4, 3–4",
    ]


def test_rang_du_parent_sinon_premier_rang_libre_en_dessous() -> None:
    """2 et 3 ont pour parent 1 : 2 prend le rang 0, 3 le rang 1 ; 4 a pour parent 3 (son seul
    voisin de la colonne 1) et prend son rang ; 5, enfant de 2, prend le rang 0."""
    obs = carte(symetrique([(1, 2), (1, 3), (3, 4), (2, 5)], 5))
    colonnes, rang = rangs(obs)
    assert colonnes == {1: 0, 2: 1, 3: 1, 4: 2, 5: 2}
    assert rang == {1: 0, 2: 0, 3: 1, 4: 1, 5: 0}
    assert layout(obs) == [
        "[1]─────[2]─────[5]",
        "        [3]─────[4]",
        "liens : 1–3",
    ]


def test_parent_de_plus_petit_identifiant_et_rang_pris() -> None:
    """4 a deux voisins dans la colonne 1, 2 et 3 : son parent est 2, de plus petit identifiant,
    et il prend son rang 0. 5, enfant de 2 aussi, trouve le rang 0 pris et descend au rang 1."""
    obs = carte(symetrique([(1, 2), (1, 3), (2, 4), (3, 4), (2, 5)], 5))
    _, rang = rangs(obs)
    assert rang == {1: 0, 2: 0, 3: 1, 4: 0, 5: 1}


def test_lien_dans_une_meme_colonne_ecrit() -> None:
    obs = carte(symetrique([(1, 2), (1, 3), (2, 3)], 3))
    assert layout(obs)[-1] == "liens : 1–3, 2–3"


def test_une_chaine_de_douze_passe_sur_deux_bandes() -> None:
    obs = carte(symetrique([(k, k + 1) for k in range(1, 12)], 12))
    assert layout(obs) == [
        "[1]─────[2]─────[3]─────[4]─────[5]─────[6]",
        "",
        "[7]─────[8]─────[9]─────[10]────[11]────[12]",
        "liens : 6–7",
    ]


def test_ligne_des_liens_coupee_a_la_largeur() -> None:
    """Une étoile de 12 systèmes : 1–2 est tracé, les 10 autres liens sont écrits, sur plusieurs
    lignes coupées après une virgule."""
    obs = carte(symetrique([(1, k) for k in range(2, 13)], 12))
    lignes = layout(obs)
    debut = next(i for i, ligne in enumerate(lignes) if ligne.startswith("liens : "))
    suite = lignes[debut:]
    assert suite == [
        "liens : 1–3, 1–4, 1–5, 1–6, 1–7, 1–8, 1–9, 1–10,",
        "1–11, 1–12",
    ]
    assert lire(lignes)[2] == [(1, k) for k in range(3, 13)]


def test_aucun_lien_ecrit_aucune_ligne_de_liens() -> None:
    obs = carte(symetrique([(1, 2)], 2))
    assert layout(obs) == ["[1]─────[2]"]


def lire(lignes: list[str]) -> tuple[list[int], list[tuple[int, int]], list[tuple[int, int]]]:
    """Comme les étapes des scénarios : cases, liens tracés, liens écrits."""
    debut = next((i for i, ligne in enumerate(lignes) if ligne.startswith("liens : ")), len(lignes))
    cases: list[int] = []
    traces: list[tuple[int, int]] = []
    for ligne in lignes[:debut]:
        trouves = list(re.finditer(r"\[(\d+)\][^\[]*", ligne))
        cases += [int(t.group(1)) for t in trouves]
        for gauche, droite in zip(trouves, trouves[1:], strict=False):
            if gauche.group(0).endswith("─") and gauche.end() == droite.start():
                a, b = int(gauche.group(1)), int(droite.group(1))
                traces.append((min(a, b), max(a, b)))
    texte = "".join(ligne.strip() for ligne in lignes[debut:])[len("liens :") :]
    ecrits = [
        (min(int(a), int(b)), max(int(a), int(b))) for a, b in re.findall(r"(\d+)–(\d+)", texte)
    ]
    return cases, traces, ecrits


@pytest.mark.parametrize("max_neighbors", [2, 3, 4])
def test_chaque_systeme_et_chaque_lien_une_fois_sur_de_nombreuses_graines(
    max_neighbors: int,
) -> None:
    reglages = msgspec.structs.replace(load_tunables(), max_neighbors=max_neighbors)
    for graine in range(1, 151):
        obs = observe(generate(graine, reglages), 1, reglages)
        lignes = layout(obs)
        cases, traces, ecrits = lire(lignes)
        attendus = {(min(s.id, v), max(s.id, v)) for s in obs.systems for v in s.neighbors}
        assert sorted(cases) == sorted(s.id for s in obs.systems), graine
        tous = traces + ecrits
        assert len(tous) == len(set(tous)), graine
        assert set(tous) == attendus, graine
        assert all(len(ligne) <= LARGEUR for ligne in lignes), graine
