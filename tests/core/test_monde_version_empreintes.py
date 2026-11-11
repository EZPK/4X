"""Tests de fourx.core.world, version, fingerprints et snapshot (docs/designs/niveau-2-m1-noyau.md,
Technical Plan, points 2, 4, 6 et 8)."""

import msgspec
import msgspec.structs
import pytest

from fourx.core import version
from fourx.core.fingerprints import Fingerprints, empreinte, fingerprints
from fourx.core.keyed_random import keyed_below
from fourx.core.snapshot import SNAPSHOT_SCHEMA_VERSION, Snapshot, decode, encode
from fourx.core.world import PERMUTATIONS, generate, label
from fourx.schema.actors import ActorKind
from fourx.schema.orders import CreateCharacter, Mine, OrderCategory
from tests.aide_monde import REGLAGES, avancer, monde, ordre, vaisseau


def test_generation_graine_1() -> None:
    etat = generate(1, REGLAGES)
    assert etat.tick == 0
    assert [(s.id, s.neighbors) for s in etat.systems] == [(1, (2,)), (2, (1, 3)), (3, (2,))]
    assert [(d.id, d.ore_id, d.system_id, d.stock) for d in etat.deposits] == [
        (1, 1, 2, 20000),
        (2, 2, 3, 20000),
    ]
    assert [(s.id, s.system_id, s.ore_prices) for s in etat.stations] == [(1, 1, (10, 15))]
    assert etat.actors == () and etat.ships == ()
    assert [c.id for c in etat.ledger.accounts] == [1, 2]
    assert etat.last_tick.events == () and etat.last_tick.results == ()


@pytest.mark.parametrize("graine", [1, 2, 3, 42, 1000])
def test_placement_des_sites_par_tirage(graine: int) -> None:
    etat = generate(graine, REGLAGES)
    attendu = PERMUTATIONS[keyed_below(graine, 0, 0, "carte", 6)]
    assert (
        etat.stations[0].system_id,
        etat.deposits[0].system_id,
        etat.deposits[1].system_id,
    ) == attendu
    assert sorted(attendu) == [1, 2, 3]


def test_les_six_permutations() -> None:
    assert len(set(PERMUTATIONS)) == 6
    assert list(PERMUTATIONS) == sorted(PERMUTATIONS)
    rangs = {keyed_below(g, 0, 0, "carte", 6) for g in range(200)}
    assert rangs == set(range(6))


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
        ("ore_prices", (10, 0)),
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
    assert version.RULES_REVISION == 0
    empreinte_reglages = version.tunables_fingerprint(REGLAGES)
    assert len(empreinte_reglages) == 16
    assert version.rules_version(REGLAGES) == f"rules-0+{empreinte_reglages}"
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
