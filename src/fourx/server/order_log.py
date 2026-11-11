"""Journal des ordres soumis.

Document : docs/designs/niveau-2-m1-noyau.md,
Technical Plan, points 6 et 8 ; plan détaillé, point 21.

Base SQLite `orders.sqlite` en mode WAL (`synchronous=NORMAL` avant M5), deux tables :
- `meta` (clé, valeur) : order_log_schema_version, rules_version, world_seed, commit,
  worktree_dirty ;
- `ticks` : tick (clé primaire), orders (MessagePack du tuple des ordres soumis), fingerprints
  (MessagePack de `Fingerprints`).
Il s'exporte et s'importe en JSONL versionné : une ligne d'en-tête (les valeurs de `meta` et le
dernier tick), puis un ordre soumis par ligne.
"""

import sqlite3
import subprocess
from pathlib import Path

import msgspec
import msgspec.json
import msgspec.msgpack

from fourx.core.fingerprints import Fingerprints
from fourx.schema.orders import SubmittedOrder

ORDER_LOG_SCHEMA_VERSION = 1
INCONNU = "inconnu"


class EnTete(msgspec.Struct, frozen=True):
    order_log_schema_version: int
    rules_version: str
    world_seed: int
    commit: str
    worktree_dirty: bool
    last_tick: int


def lire_commit(dossier: Path) -> tuple[str, bool]:
    """L'identifiant (SHA) du commit et l'indicateur « dossier de travail modifié »."""
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=dossier, capture_output=True, text=True, check=True
        ).stdout.strip()
        etat = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=dossier,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except OSError, subprocess.CalledProcessError:
        return INCONNU, False
    return sha, bool(etat.strip())


class OrderLog:
    def __init__(self, path: Path) -> None:
        self._connexion = sqlite3.connect(path)
        self._connexion.execute("PRAGMA journal_mode=WAL")
        self._connexion.execute("PRAGMA synchronous=NORMAL")

    @classmethod
    def create(
        cls, path: Path, rules_version: str, world_seed: int, commit: str, worktree_dirty: bool
    ) -> OrderLog:
        journal = cls(path)
        with journal._connexion:
            journal._connexion.execute("CREATE TABLE meta (cle TEXT PRIMARY KEY, valeur TEXT)")
            journal._connexion.execute(
                "CREATE TABLE ticks (tick INTEGER PRIMARY KEY, orders BLOB, fingerprints BLOB)"
            )
            journal._connexion.executemany(
                "INSERT INTO meta VALUES (?, ?)",
                [
                    ("order_log_schema_version", str(ORDER_LOG_SCHEMA_VERSION)),
                    ("rules_version", rules_version),
                    ("world_seed", str(world_seed)),
                    ("commit", commit),
                    ("worktree_dirty", "1" if worktree_dirty else "0"),
                ],
            )
        return journal

    def meta(self) -> dict[str, str]:
        return dict(self._connexion.execute("SELECT cle, valeur FROM meta").fetchall())

    def append(self, orders: tuple[SubmittedOrder, ...], fingerprints: Fingerprints) -> None:
        with self._connexion:
            self._connexion.execute(
                "INSERT INTO ticks VALUES (?, ?, ?)",
                (
                    fingerprints.tick,
                    msgspec.msgpack.encode(orders),
                    msgspec.msgpack.encode(fingerprints),
                ),
            )

    def orders_by_tick(self) -> tuple[tuple[SubmittedOrder, ...], ...]:
        decodeur = msgspec.msgpack.Decoder(tuple[SubmittedOrder, ...])
        lignes = self._connexion.execute("SELECT orders FROM ticks ORDER BY tick").fetchall()
        return tuple(decodeur.decode(ligne[0]) for ligne in lignes)

    def fingerprints_by_tick(self) -> tuple[Fingerprints, ...]:
        decodeur = msgspec.msgpack.Decoder(Fingerprints)
        lignes = self._connexion.execute("SELECT fingerprints FROM ticks ORDER BY tick").fetchall()
        return tuple(decodeur.decode(ligne[0]) for ligne in lignes)

    def en_tete(self) -> EnTete:
        meta = self.meta()
        dernier = self._connexion.execute("SELECT MAX(tick) FROM ticks").fetchone()[0]
        return EnTete(
            order_log_schema_version=int(meta["order_log_schema_version"]),
            rules_version=meta["rules_version"],
            world_seed=int(meta["world_seed"]),
            commit=meta["commit"],
            worktree_dirty=meta["worktree_dirty"] == "1",
            last_tick=0 if dernier is None else int(dernier),
        )

    def export_jsonl(self, path: Path) -> None:
        lignes = [msgspec.json.encode(self.en_tete())]
        lignes += [msgspec.json.encode(o) for ordres in self.orders_by_tick() for o in ordres]
        path.write_bytes(b"\n".join(lignes) + b"\n")

    def close(self) -> None:
        self._connexion.close()


def import_jsonl(path: Path) -> tuple[EnTete, tuple[tuple[SubmittedOrder, ...], ...]]:
    """L'en-tête et les ordres par tick, du tick 1 au dernier tick, ticks sans ordre compris."""
    lignes = [ligne for ligne in path.read_bytes().splitlines() if ligne.strip()]
    en_tete = msgspec.json.decode(lignes[0], type=EnTete)
    decodeur = msgspec.json.Decoder(SubmittedOrder)
    par_tick: list[list[SubmittedOrder]] = [[] for _ in range(en_tete.last_tick)]
    for ligne in lignes[1:]:
        soumis = decodeur.decode(ligne)
        par_tick[soumis.tick - 1].append(soumis)
    return en_tete, tuple(tuple(t) for t in par_tick)
