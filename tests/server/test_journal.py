"""Tests du journal des ordres soumis (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
points 6 et 8 ; plan détaillé, points 21 et 23)."""

import sqlite3
from pathlib import Path

import msgspec.json
import pytest

from fourx.core.fingerprints import Fingerprints, fingerprints
from fourx.core.state import State
from fourx.schema.orders import Mine, Move, SubmittedOrder
from fourx.schema.results import RefusalCode
from fourx.server.order_log import ORDER_LOG_SCHEMA_VERSION, EnTete, OrderLog, import_jsonl
from tests.aide_monde import avancer, monde, ordre, vaisseau


def partie() -> tuple[list[tuple[SubmittedOrder, ...]], list[Fingerprints]]:
    """Trois ticks : deux ordres au tick 1 (dont un refusé à la réception), aucun au tick 2."""
    state: State = monde((vaisseau(1, 1, system=1),))
    par_tick = [
        (
            ordre(state, 1, 1, Move(ship_id=1, target_system_id=2)),
            ordre(
                state, 1, 1, Move(ship_id=1, target_system_id=3), refus=RefusalCode.DUPLICATE_NUMBER
            ),
        ),
        (),
        (),
    ]
    empreintes = []
    for i in range(3):
        if i == 2:
            par_tick[2] = (ordre(state, 1, 2, Mine(ship_id=1, ore_id=1)),)
        state, _ = avancer(state, par_tick[i])
        empreintes.append(fingerprints(state))
    return par_tick, empreintes


def journal(chemin: Path) -> OrderLog:
    return OrderLog.create(chemin, "rules-0+abc", 42, "0123abcd", True)


def test_enregistrement_et_relecture(tmp_path: Path) -> None:
    par_tick, empreintes = partie()
    log = journal(tmp_path / "orders.sqlite")
    for ordres, emp in zip(par_tick, empreintes, strict=True):
        log.append(ordres, emp)
    log.close()
    relu = OrderLog(tmp_path / "orders.sqlite")
    assert relu.orders_by_tick() == tuple(par_tick)
    assert relu.fingerprints_by_tick() == tuple(empreintes)
    assert relu.en_tete() == EnTete(
        order_log_schema_version=ORDER_LOG_SCHEMA_VERSION,
        rules_version="rules-0+abc",
        world_seed=42,
        commit="0123abcd",
        worktree_dirty=True,
        last_tick=3,
    )
    relu.close()


def test_mode_wal_et_tables(tmp_path: Path) -> None:
    journal(tmp_path / "orders.sqlite").close()
    connexion = sqlite3.connect(tmp_path / "orders.sqlite")
    assert connexion.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    tables = {n for (n,) in connexion.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert tables == {"meta", "ticks"}
    connexion.close()


def test_journal_vide(tmp_path: Path) -> None:
    log = journal(tmp_path / "orders.sqlite")
    assert log.orders_by_tick() == ()
    assert log.en_tete().last_tick == 0
    log.export_jsonl(tmp_path / "orders.jsonl")
    en_tete, ordres = import_jsonl(tmp_path / "orders.jsonl")
    assert (en_tete.last_tick, ordres) == (0, ())
    log.close()


def test_un_tick_n_est_enregistre_qu_une_fois(tmp_path: Path) -> None:
    par_tick, empreintes = partie()
    log = journal(tmp_path / "orders.sqlite")
    log.append(par_tick[0], empreintes[0])
    with pytest.raises(sqlite3.IntegrityError):
        log.append(par_tick[0], empreintes[0])
    assert len(log.orders_by_tick()) == 1
    log.close()


def test_export_et_import_jsonl(tmp_path: Path) -> None:
    par_tick, empreintes = partie()
    log = journal(tmp_path / "orders.sqlite")
    for ordres, emp in zip(par_tick, empreintes, strict=True):
        log.append(ordres, emp)
    log.export_jsonl(tmp_path / "orders.jsonl")
    lignes = (tmp_path / "orders.jsonl").read_bytes().splitlines()
    assert len(lignes) == 1 + 3
    assert msgspec.json.decode(lignes[0], type=EnTete) == log.en_tete()
    en_tete, ordres_importes = import_jsonl(tmp_path / "orders.jsonl")
    assert en_tete == log.en_tete()
    # Le tick 2, sans ordre, est rendu vide à sa place.
    assert ordres_importes == tuple(par_tick)
    log.close()


def test_indicateur_dossier_non_modifie(tmp_path: Path) -> None:
    log = OrderLog.create(tmp_path / "orders.sqlite", "rules-0+abc", 42, "0123abcd", False)
    assert log.meta()["worktree_dirty"] == "0"
    assert log.en_tete().worktree_dirty is False
    log.close()
