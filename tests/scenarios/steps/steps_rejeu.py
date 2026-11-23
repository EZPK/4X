"""Définitions d'étapes du volet C de M1 : le rejeu et l'outil de divergence.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 24 ; Technical Plan, point 8
(rejeu, divergence) et point 13 (interfaces de `tools`) ; CUJ 4 du niveau 1.

Chemin protégé. Les étapes sont écrites avant le code : elles n'importent le code de `fourx`
qu'à l'intérieur des fonctions, par `importlib`. Elles réutilisent la partie du serveur en mémoire
des étapes du volet B (fixture `serveur`, `tests/scenarios/steps/steps_partie.py`).

Conventions que ces étapes figent :
- le dossier d'une partie contient `snapshot.msgpack` (instantané initial, `core.snapshot`),
  `orders.sqlite` (journal des ordres, `server.order_log.OrderLog`) et `events.jsonl` ; le journal
  des ordres a une entrée par tick joué, du tick 1 au dernier ;
- `replay_orders(initial, orders_by_tick, world_seed, tunables)` renvoie les empreintes de chaque
  tick rejoué, dans l'ordre des ticks, et les événements de tous ces ticks, dans l'ordre où `step`
  les produit ; `orders_by_tick[i]` est le tuple des ordres soumis du tick i + 1 ;
- un fichier d'empreintes a une ligne par tick, l'encodage JSON msgspec de `Fingerprints`, dans
  l'ordre des ticks ;
- `python -m fourx.tools.replay <dossier>` lit les réglages de `tunables.toml`, rejoue la partie
  et finit avec le code 0 si les empreintes concordent avec celles du journal des ordres ;
- `python -m fourx.tools.divergence <A> <B>` accepte un dossier de partie (empreintes de son
  journal des ordres) ou un fichier d'empreintes ; il affiche « tick <n> : <composants> », les
  composants séparés par « , » dans l'ordre des champs de `Fingerprints`, et finit avec le code 1,
  ou affiche « aucune divergence » et finit avec le code 0 ;
- `first_divergence(a, b)` renvoie le premier tick (champ `tick` des empreintes) où a et b
  diffèrent, avec les noms des champs qui diffèrent, ou None.
"""

import importlib
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import msgspec
import pytest
from pytest_bdd import parsers, then, when

from tests.scenarios.steps.steps_partie import Serveur

RACINE = Path(__file__).resolve().parents[3]


def importer(nom: str) -> Any:
    return importlib.import_module(nom)


@dataclass
class Rejeu:
    arretee: bool = False
    empreintes: tuple[Any, ...] = ()
    evenements: tuple[Any, ...] = ()
    fichier: Path | None = None
    sortie: subprocess.CompletedProcess[str] | None = None
    rejoues: list[tuple[Any, ...]] = field(default_factory=list)


@pytest.fixture
def rejeu() -> Rejeu:
    return Rejeu()


def dossier_de_partie(serveur: Serveur) -> Path:
    dossiers = sorted(p for p in serveur.dossier.iterdir() if p.is_dir())
    assert len(dossiers) == 1, dossiers
    return dossiers[0]


def arreter(serveur: Serveur, rejeu: Rejeu) -> None:
    """Arrête la partie une seule fois : ses fichiers sont complets et fermés."""
    if not rejeu.arretee:
        serveur.jeu.close()
        rejeu.arretee = True


def journal_des_ordres(serveur: Serveur) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Les ordres soumis et les empreintes de chaque tick, lus dans `orders.sqlite`."""
    order_log = importer("fourx.server.order_log")
    journal = order_log.OrderLog(dossier_de_partie(serveur) / "orders.sqlite")
    try:
        return journal.orders_by_tick(), journal.fingerprints_by_tick()
    finally:
        journal.close()


def instantane(serveur: Serveur) -> Any:
    snapshot = importer("fourx.core.snapshot")
    return snapshot.decode((dossier_de_partie(serveur) / "snapshot.msgpack").read_bytes())


def lancer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", *args], cwd=RACINE, capture_output=True, text=True, check=False
    )


# --- Quand


@when("le propriétaire envoie son vaisseau vers le système où il se trouve")
def vers_son_systeme(serveur: Serveur) -> None:
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    serveur.envoyer(
        "propriétaire", orders.Move(ship_id=navire.id, target_system_id=navire.system_id)
    )


@when(
    "on rejoue la partie par replay_orders depuis son instantané initial et son journal des ordres"
)
def rejouer(serveur: Serveur, rejeu: Rejeu) -> None:
    replay = importer("fourx.tools.replay")
    arreter(serveur, rejeu)
    initial = instantane(serveur)
    ordres, _ = journal_des_ordres(serveur)
    rejeu.empreintes, rejeu.evenements = replay.replay_orders(
        initial.state, ordres, initial.world_seed, serveur.tunables
    )


@when(
    parsers.re(
        r"on rejoue la partie par step depuis son instantané initial et son journal des ordres, "
        r"(?P<quoi>en modifiant son registre au tick (?P<tick>\d+)|sans modification)"
    )
)
def rejouer_par_step(
    serveur: Serveur, rejeu: Rejeu, tmp_path: Path, quoi: str, tick: str | None
) -> None:
    """Rejoue tick par tick avec `step`. Au tick demandé, après `step`, le compteur d'émission du
    premier motif du registre augmente de un : seul le registre change, à partir de ce tick."""
    step = importer("fourx.core.step")
    fingerprints = importer("fourx.core.fingerprints")
    arreter(serveur, rejeu)
    initial = instantane(serveur)
    ordres, _ = journal_des_ordres(serveur)
    etat = initial.state
    empreintes = []
    for soumis in ordres:
        etat, _ = step.step(etat, soumis, initial.world_seed, serveur.tunables)
        if tick is not None and etat.tick == int(tick):
            registre = etat.ledger
            emis = (registre.issued_by_reason[0] + 1, *registre.issued_by_reason[1:])
            registre = msgspec.structs.replace(registre, issued_by_reason=emis)
            etat = msgspec.structs.replace(etat, ledger=registre)
        empreintes.append(fingerprints.fingerprints(etat))
    rejeu.empreintes = tuple(empreintes)
    rejeu.fichier = tmp_path / f"empreintes-{len(rejeu.rejoues)}.jsonl"
    rejeu.fichier.write_bytes(b"".join(msgspec.json.encode(e) + b"\n" for e in empreintes))
    rejeu.rejoues.append(rejeu.empreintes)


@when(
    "on lance l'outil de divergence sur le dossier de la partie et le fichier d'empreintes "
    "de ce rejeu"
)
def lancer_divergence(serveur: Serveur, rejeu: Rejeu) -> None:
    assert rejeu.fichier is not None
    rejeu.sortie = lancer(
        "fourx.tools.divergence", str(dossier_de_partie(serveur)), str(rejeu.fichier)
    )


# --- Alors


@then(
    parsers.re(
        r"le journal des ordres de la partie contient un ordre refusé par la réception "
        r"avec le code (?P<code>[A-Z_]+)"
    )
)
def refus_de_reception(serveur: Serveur, code: str) -> None:
    results = importer("fourx.schema.results")
    ordres, _ = journal_des_ordres(serveur)
    refus = [s.reception_refusal for tick in ordres for s in tick]
    assert results.RefusalCode[code] in refus, refus


@then(
    parsers.re(r"le journal des événements contient un ordre refusé avec le code (?P<code>[A-Z_]+)")
)
def refus_dans_les_evenements(serveur: Serveur, code: str) -> None:
    events = importer("fourx.schema.events")
    results = importer("fourx.schema.results")
    refus = [
        e.payload.refusal
        for e in serveur.evenements()
        if isinstance(e.payload, events.OrderRefused)
    ]
    assert results.RefusalCode[code] in refus, refus


@then(
    "le rejeu donne les empreintes du journal des ordres à chaque tick, du tick 1 au dernier "
    "tick joué"
)
def memes_empreintes(serveur: Serveur, rejeu: Rejeu) -> None:
    _, attendues = journal_des_ordres(serveur)
    dernier = serveur.jeu.state.tick
    assert [e.tick for e in attendues] == list(range(1, dernier + 1))
    assert len(rejeu.empreintes) == len(attendues)
    for obtenue, attendue in zip(rejeu.empreintes, attendues, strict=True):
        assert obtenue == attendue, f"tick {attendue.tick}"


@then("le rejeu donne les événements du journal des événements, dans le même ordre")
def memes_evenements(serveur: Serveur, rejeu: Rejeu) -> None:
    attendus = serveur.evenements()
    assert attendus
    assert list(rejeu.evenements) == attendus


@then("l'outil de rejeu, lancé sur le dossier de la partie, finit avec le code 0")
def outil_de_rejeu(serveur: Serveur) -> None:
    sortie = lancer("fourx.tools.replay", str(dossier_de_partie(serveur)))
    assert sortie.returncode == 0, sortie.stdout + sortie.stderr


@then(
    parsers.re(
        r"l'outil de divergence affiche « (?P<texte>[^»]+) » et finit avec le code (?P<code>\d)"
    )
)
def sortie_divergence(rejeu: Rejeu, texte: str, code: str) -> None:
    assert rejeu.sortie is not None
    lignes = [ligne.strip() for ligne in rejeu.sortie.stdout.splitlines()]
    assert texte in lignes, rejeu.sortie.stdout + rejeu.sortie.stderr
    assert rejeu.sortie.returncode == int(code), rejeu.sortie.stderr


@then(
    parsers.re(
        r"first_divergence, sur les empreintes du journal des ordres et celles de ce rejeu, "
        r"(?:renvoie le tick (?P<tick>\d+) et le seul composant (?P<composant>[a-z_]+)"
        r"|ne renvoie rien)"
    )
)
def premiere_divergence(
    serveur: Serveur, rejeu: Rejeu, tick: str | None, composant: str | None
) -> None:
    divergence = importer("fourx.tools.divergence")
    _, attendues = journal_des_ordres(serveur)
    resultat = divergence.first_divergence(attendues, rejeu.empreintes)
    if tick is None:
        assert resultat is None, resultat
    else:
        assert resultat == (int(tick), (composant,)), resultat
