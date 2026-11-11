"""Champs de version du journal des ordres soumis et des fichiers d'une partie
(docs/designs/niveau-2-m1-noyau.md, objectif 7 ; plan détaillé, point 23)."""

import os
import re
import subprocess
from pathlib import Path

from fourx.core import snapshot
from fourx.core.version import rules_version
from fourx.server.game import RACINE_DEPOT, Game
from fourx.server.order_log import INCONNU, ORDER_LOG_SCHEMA_VERSION, OrderLog, lire_commit
from fourx.server.tunables_loader import load_tunables


def git(dossier: Path, *arguments: str) -> str:
    """git isolé de la configuration de la machine (aucun hook, aucun réglage utilisateur)."""
    env = os.environ | {
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.invalid",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.invalid",
    }
    return subprocess.run(
        ["git", *arguments], cwd=dossier, env=env, check=True, capture_output=True, text=True
    ).stdout.strip()


def test_version_du_journal() -> None:
    assert ORDER_LOG_SCHEMA_VERSION == 1


def test_lire_commit_hors_depot(tmp_path: Path) -> None:
    assert lire_commit(tmp_path) == (INCONNU, False)


def test_lire_commit_et_indicateur(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    git(tmp_path, "commit", "-q", "--allow-empty", "-m", "vide")
    sha, modifie = lire_commit(tmp_path)
    assert re.fullmatch(r"[0-9a-f]{40}", sha)
    assert sha == git(tmp_path, "rev-parse", "HEAD")
    assert modifie is False
    (tmp_path / "nouveau.txt").write_text("x", encoding="utf-8")
    assert lire_commit(tmp_path) == (sha, True)


def test_la_partie_ecrit_les_versions(tmp_path: Path) -> None:
    reglages = load_tunables()
    jeu = Game(tmp_path, world_seed=9, tunables=reglages)
    jeu.close()
    commit, modifie = lire_commit(RACINE_DEPOT)
    log = OrderLog(jeu.run_dir / "orders.sqlite")
    assert log.meta() == {
        "order_log_schema_version": str(ORDER_LOG_SCHEMA_VERSION),
        "rules_version": rules_version(reglages),
        "world_seed": "9",
        "commit": commit,
        "worktree_dirty": "1" if modifie else "0",
    }
    log.close()
    instantane = snapshot.decode((jeu.run_dir / "snapshot.msgpack").read_bytes())
    assert instantane.snapshot_schema_version == snapshot.SNAPSHOT_SCHEMA_VERSION
    assert instantane.rules_version == rules_version(reglages)
    assert (instantane.world_seed, instantane.commit) == (9, commit)
    assert instantane.worktree_dirty is modifie
    assert instantane.state.tick == 0
