"""Tests du rejeu (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 8 et 13)."""

import sqlite3
from pathlib import Path

import msgspec
import msgspec.structs
import pytest

from fourx.core import snapshot
from fourx.core.fingerprints import Fingerprints, fingerprints
from fourx.core.state import State
from fourx.core.step import step
from fourx.core.tunables import Tunables
from fourx.core.version import rules_version
from fourx.core.world import generate
from fourx.schema.actors import ActorKind
from fourx.schema.events import Event
from fourx.schema.orders import Move, Order, OrderCategory, SubmittedOrder
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders
from fourx.server.game import Game
from fourx.server.order_log import OrderLog
from fourx.server.tunables_loader import load_tunables
from fourx.tools import replay
from fourx.tools.divergence import lire_empreintes
from fourx.tools.replay import main, replay_orders


def partie(dossier: Path, ticks: int = 12, **reglages: int) -> Game:
    """Une partie courte : un acteur qui part vers un système voisin, puis un refus."""
    tunables = msgspec.structs.replace(load_tunables(), **reglages)
    jeu = Game(dossier, world_seed=1, tunables=tunables)
    acteur = jeu.create_character(ActorKind.HUMAN)
    connexion = jeu.connect(acteur)
    jeu.advance(1)
    (navire,) = [s for s in jeu.state.ships if s.owner_id == acteur]
    voisin = next(v for s in jeu.state.systems if s.id == navire.system_id for v in s.neighbors)
    for numero, cible in ((1, voisin), (2, navire.system_id)):
        commande = Move(ship_id=navire.id, target_system_id=cible)
        ordre = Order(
            actor_id=acteur,
            number=numero,
            category=OrderCategory.PLAYER,
            policy_id=None,
            policy_version=None,
            command=commande,
        )
        connexion.submit(SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=(ordre,)))
        jeu.advance(1)
    jeu.advance(ticks - 3)
    jeu.close()
    return jeu


def ordres_et_empreintes(
    jeu: Game,
) -> tuple[tuple[tuple[SubmittedOrder, ...], ...], tuple[Fingerprints, ...]]:
    journal = OrderLog(jeu.run_dir / "orders.sqlite")
    try:
        return journal.orders_by_tick(), journal.fingerprints_by_tick()
    finally:
        journal.close()


def test_replay_orders_applique_step_tick_par_tick() -> None:
    tunables = load_tunables()
    initial = generate(2, tunables)
    empreintes, evenements = replay_orders(initial, ((), (), ()), 2, tunables)
    etat, attendus = initial, list[Event]()
    for _ in range(3):
        etat, produits = step(etat, (), 2, tunables)
        attendus.extend(produits)
    assert [e.tick for e in empreintes] == [1, 2, 3]
    assert empreintes[-1] == fingerprints(etat)
    assert list(evenements) == attendus


def test_replay_orders_sans_ordre() -> None:
    tunables = load_tunables()
    assert replay_orders(generate(1, tunables), (), 1, tunables) == ((), ())


def test_rejouer_une_partie_redonne_ses_empreintes_et_ses_evenements(tmp_path: Path) -> None:
    jeu = partie(tmp_path)
    ordres, attendues = ordres_et_empreintes(jeu)
    initial = snapshot.decode((jeu.run_dir / "snapshot.msgpack").read_bytes())
    empreintes, evenements = replay_orders(initial.state, ordres, 1, jeu.tunables)
    assert empreintes == attendues
    assert len(empreintes) == 12
    assert evenements


def test_commande_sans_divergence_et_export(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    jeu = partie(tmp_path / "runs")
    exportees = tmp_path / "exportees.jsonl"
    assert main([str(jeu.run_dir), "--export-fingerprints", str(exportees)]) == 0
    assert capsys.readouterr().out == "aucune divergence\n"
    assert lire_empreintes(exportees) == ordres_et_empreintes(jeu)[1]


def test_commande_sans_export(tmp_path: Path) -> None:
    jeu = partie(tmp_path / "runs")
    assert main([str(jeu.run_dir)]) == 0
    assert not list(tmp_path.glob("*.jsonl"))


def test_commande_avec_une_empreinte_alteree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    jeu = partie(tmp_path)
    _, empreintes = ordres_et_empreintes(jeu)
    alteree = msgspec.structs.replace(empreintes[6], ships="0" * 32)
    with sqlite3.connect(jeu.run_dir / "orders.sqlite") as base:
        base.execute(
            "UPDATE ticks SET fingerprints = ? WHERE tick = 7",
            (msgspec.msgpack.encode(alteree),),
        )
    assert main([str(jeu.run_dir)]) == 1
    assert capsys.readouterr().out == "tick 7 : ships\n"


def test_commande_sur_d_autres_regles(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    jeu = partie(tmp_path, jump_ticks=5)
    assert main([str(jeu.run_dir)]) == 1
    attendu = (
        f"règles différentes : partie {rules_version(jeu.tunables)}, "
        f"tunables.toml {rules_version(load_tunables())}\n"
    )
    assert capsys.readouterr().out == attendu


def test_la_graine_de_la_partie_est_transmise_a_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """La graine ne sert qu'au départage du minage, que ces parties courtes ne déclenchent pas :
    on vérifie donc qu'elle arrive à `step`, par replay_orders comme par la commande."""
    graines: list[object] = []

    def espion(etat: State, ordres: object, world_seed: int, tunables: Tunables) -> object:
        graines.append(world_seed)
        return step(etat, ordres, world_seed, tunables)  # type: ignore[arg-type]

    monkeypatch.setattr(replay, "step", espion)
    tunables = load_tunables()
    replay_orders(generate(2, tunables), ((), ()), 2, tunables)
    assert graines == [2, 2]
    graines.clear()
    jeu = Game(tmp_path, world_seed=3, tunables=tunables)
    jeu.advance(2)
    jeu.close()
    assert main([str(jeu.run_dir)]) == 0
    assert graines == [3, 3]
