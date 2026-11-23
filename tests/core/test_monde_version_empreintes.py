"""Tests de fourx.core.world, version, fingerprints et snapshot (docs/designs/niveau-2-m1-noyau.md,
Technical Plan, points 2, 4, 6 et 8)."""

import os
import subprocess
import sys

import msgspec
import msgspec.structs
import pytest

from fourx.core import version
from fourx.core.fingerprints import Fingerprints, empreinte, fingerprints
from fourx.core.keyed_random import keyed_below
from fourx.core.snapshot import SNAPSHOT_SCHEMA_VERSION, Snapshot, decode, encode
from fourx.core.world import generate, label, npc_count
from fourx.schema.actors import ActorKind
from fourx.schema.orders import CreateCharacter, Mine, OrderCategory
from tests.aide_monde import REGLAGES, avancer, monde, ordre, vaisseau


def test_generation_graine_1() -> None:
    """Le monde de la graine 1 avec les réglages de test (essai du 2026-11-15, hors du dépôt)."""
    etat = generate(1, REGLAGES)
    assert etat.tick == 0
    assert len(etat.systems) == 11
    assert [(s.id, s.system_id, s.ore_prices) for s in etat.stations] == [
        (1, 2, (10, 15)),
        (2, 4, (12, 12)),
    ]
    assert [(d.id, d.system_id, d.ore_id) for d in etat.deposits] == [
        (1, 5, 1),
        (2, 7, 2),
        (3, 11, 1),
        (4, 4, 2),
        (5, 1, 1),
        (6, 3, 2),
    ]
    assert all(d.stock == REGLAGES.deposit_stock for d in etat.deposits)
    assert npc_count(1, REGLAGES) == 5
    assert etat.actors == () and etat.ships == ()
    assert [c.id for c in etat.ledger.accounts] == [1, 2]
    assert etat.last_tick.events == () and etat.last_tick.results == ()


def _connexe(etat: object) -> bool:
    systemes = {s.id: s.neighbors for s in etat.systems}  # type: ignore[attr-defined]
    vus = {1}
    file = [1]
    while file:
        for v in systemes[file.pop()]:
            if v not in vus:
                vus.add(v)
                file.append(v)
    return vus == set(systemes)


@pytest.mark.parametrize("graine", [1, 2, 3, 42, 1000, 123_456])
def test_generation_dans_les_fourchettes(graine: int) -> None:
    etat = generate(graine, REGLAGES)
    assert REGLAGES.systems_min <= len(etat.systems) <= REGLAGES.systems_max
    assert REGLAGES.stations_min <= len(etat.stations) <= REGLAGES.stations_max
    assert REGLAGES.deposits_min <= len(etat.deposits) <= REGLAGES.deposits_max
    assert REGLAGES.npc_min <= npc_count(graine, REGLAGES) <= REGLAGES.npc_max
    assert [s.id for s in etat.systems] == list(range(1, len(etat.systems) + 1))
    assert _connexe(etat)
    for s in etat.systems:
        assert list(s.neighbors) == sorted(s.neighbors)
        assert len(s.neighbors) <= REGLAGES.max_neighbors
        assert s.id not in s.neighbors
        for v in s.neighbors:
            assert s.id in etat.systems[v - 1].neighbors
    assert len({s.system_id for s in etat.stations}) == len(etat.stations)
    assert len({d.system_id for d in etat.deposits}) == len(etat.deposits)
    for station in etat.stations:
        assert station.ore_prices == REGLAGES.station_ore_prices[station.id - 1]
    for minerai in (1, 2):
        assert sum(1 for d in etat.deposits if d.ore_id == minerai) >= 2
    assert generate(graine, REGLAGES) == etat


def test_generation_sous_deux_pythonhashseed() -> None:
    """La même graine donne le même monde sous deux valeurs de PYTHONHASHSEED."""
    programme = (
        "import msgspec;"
        "from fourx.core.world import generate;"
        "from tests.aide_monde import REGLAGES;"
        "print(msgspec.json.encode([generate(g, REGLAGES) for g in (1, 2, 3, 42)]).decode())"
    )
    sorties = [
        subprocess.run(
            [sys.executable, "-c", programme],
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONHASHSEED": valeur},
        ).stdout
        for valeur in ("0", "1")
    ]
    assert sorties[0] == sorties[1] and sorties[0]


def test_tirages_de_la_generation() -> None:
    """La taille du monde vient du tirage (entité 0, motif « world_size »)."""
    for graine in (1, 2, 3):
        taille = REGLAGES.systems_min + keyed_below(
            graine, 0, 0, "world_size", REGLAGES.systems_max - REGLAGES.systems_min + 1
        )
        assert len(generate(graine, REGLAGES).systems) == taille


def test_voisins_de_la_graine_1() -> None:
    assert [s.neighbors for s in generate(1, REGLAGES).systems] == [
        (2, 3, 4, 5),
        (1, 3, 11),
        (1, 2, 11),
        (1, 6, 8),
        (1, 10),
        (4, 7, 8, 9),
        (6,),
        (4, 6),
        (6,),
        (5,),
        (2, 3),
    ]


def _tirage(graine: int, motif: str, bas: int, haut: int) -> int:
    """Un nombre « entre bas et haut » de la génération : entité 0, tick 0."""
    return bas + keyed_below(graine, 0, 0, motif, haut - bas + 1)


@pytest.mark.parametrize("graine", [1, 2, 3, 42])
def test_liens_en_plus_tires(graine: int) -> None:
    """Un arbre de N − 1 liens, plus le nombre de liens tiré entre 1 et extra_links_max."""
    etat = generate(graine, REGLAGES)
    liens = sum(len(s.neighbors) for s in etat.systems) // 2
    en_plus = _tirage(graine, "extra_link_count", 1, REGLAGES.extra_links_max)
    assert liens == len(etat.systems) - 1 + en_plus


@pytest.mark.parametrize("graine", [1, 2, 3, 4, 5, 42])
def test_nombres_tires_de_stations_de_gisements_et_de_pnj(graine: int) -> None:
    etat = generate(graine, REGLAGES)
    r = REGLAGES
    assert len(etat.stations) == _tirage(graine, "station_count", r.stations_min, r.stations_max)
    assert len(etat.deposits) == _tirage(graine, "deposit_count", r.deposits_min, r.deposits_max)
    assert npc_count(graine, r) == _tirage(graine, "npc_count", r.npc_min, r.npc_max)


def test_au_plus_deux_voisins_la_carte_est_un_cycle() -> None:
    """Avec deux voisins au plus, l'arbre est une chaîne et seul le lien entre ses deux bouts
    reste possible : la carte est un cycle, même quand plus d'un lien est tiré."""
    reglages = msgspec.structs.replace(REGLAGES, max_neighbors=2)
    graines = range(1, 13)
    assert any(_tirage(g, "extra_link_count", 1, reglages.extra_links_max) > 1 for g in graines)
    for graine in graines:
        etat = generate(graine, reglages)
        assert all(len(s.neighbors) == 2 for s in etat.systems), graine
        assert _connexe(etat)


def test_libelles() -> None:
    assert label("system", 3) == "system_3"
    assert label("deposit", 2) == "deposit_2"
    assert label("ore", 1) == "ore_a"
    assert label("ore", 2) == "ore_b"
    assert label("station", 1) == "station_1"
    assert label("actor", 4) == "actor_4"
    assert label("ship", 2) == "ship_2"
    assert label(table="ship", id=7) == "ship_7"


def test_reglages_bornes_au_decodage() -> None:
    from fourx.core.tunables import Tunables

    valides = msgspec.structs.asdict(REGLAGES)
    assert msgspec.convert(valides, Tunables) == REGLAGES
    for champ, valeur in (
        ("regen_ticks", 0),
        ("jump_ticks", 0),
        ("mining_rate", 0),
        ("cargo_capacity", 0),
        ("station_ore_prices", ((10, 0), (12, 12), (8, 18))),
        ("station_ore_prices", ((10, 15), (12, 12))),
        ("station_ore_prices", ((10, 15, 1), (12, 12), (8, 18))),
        ("systems_min", 13),
        ("deposits_min", 3),
        ("systems_min", 5),
        ("max_neighbors", 1),
        ("extra_links_max", 0),
        ("npc_min", 0),
        ("npc_min", 6),
        ("stations_min", 4),
        ("tax_rate_bp", 10_001),
        ("tax_rate_bp", -1),
        ("deposit_stock", -1),
        ("budget_regen", -1),
        ("budget_max", -1),
    ):
        with pytest.raises(msgspec.ValidationError):
            msgspec.convert({**valides, champ: valeur}, Tunables)
    assert msgspec.convert({**valides, "tax_rate_bp": 10_000}, Tunables).tax_rate_bp == 10_000
    assert msgspec.convert({**valides, "deposit_stock": 0}, Tunables).deposit_stock == 0


def test_rules_version() -> None:
    assert version.RULES_REVISION == 1
    empreinte_reglages = version.tunables_fingerprint(REGLAGES)
    assert len(empreinte_reglages) == 16
    assert version.rules_version(REGLAGES) == f"rules-1+{empreinte_reglages}"
    autres = msgspec.structs.replace(REGLAGES, tax_rate_bp=500)
    assert version.tunables_fingerprint(autres) != empreinte_reglages


def test_empreintes_par_composant() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    e = fingerprints(etat)
    assert e.tick == 0
    assert e.ships == empreinte(etat.ships)
    assert all(len(getattr(e, f)) == 32 for f in Fingerprints.__struct_fields__ if f != "tick")
    apres, _ = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),))
    f = fingerprints(apres)
    assert f.tick == 1
    assert (f.systems, f.stations) == (e.systems, e.stations)
    assert f.ships != e.ships and f.deposits != e.deposits and f.last_tick != e.last_tick
    assert f.actors == e.actors  # budget : −1 à l'ordre, +1 au règlement
    assert fingerprints(apres) == f


def test_empreinte_du_registre_change_avec_une_vente() -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(10, 0)),))
    from fourx.schema.orders import Sell

    apres, _ = avancer(etat, (ordre(etat, 1, 1, Sell(ship_id=1, ore_id=1, quantity=10)),))
    assert fingerprints(apres).ledger != fingerprints(etat).ledger


def test_instantane_aller_retour() -> None:
    etat = generate(1, REGLAGES)
    soumis = ordre(
        etat,
        1,
        1,
        CreateCharacter(actor_kind=ActorKind.HUMAN),
        sender=None,
        category=OrderCategory.ADMIN,
    )
    etat, _ = avancer(etat, (soumis,))
    instantane = Snapshot(
        snapshot_schema_version=SNAPSHOT_SCHEMA_VERSION,
        rules_version=version.rules_version(REGLAGES),
        world_seed=1,
        commit="0" * 40,
        worktree_dirty=False,
        state=etat,
    )
    donnees = encode(instantane)
    assert isinstance(donnees, bytes)
    assert decode(donnees) == instantane
    assert SNAPSHOT_SCHEMA_VERSION == 1
    with pytest.raises(msgspec.ValidationError):
        decode(msgspec.msgpack.encode({"snapshot_schema_version": 1}))
