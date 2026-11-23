"""Le rejeu de la partie de référence (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 8 ;
plan détaillé, point 27). Marque `rejeu` : tâche `rejeu` de la CI, sous PYTHONHASHSEED=0 puis 1.

Importe le journal enregistré de la révision courante des règles, régénère l'état initial par
`world.generate(1, réglages)`, rejoue par `replay_orders`, compare `rules_version` et les
empreintes tous les 1 000 ticks à `reference.json`, et écrit les empreintes de chaque tick dans
`runs/rejeu-<PYTHONHASHSEED>/fingerprints.jsonl` (`runs/rejeu-aleatoire/` si la variable n'est
pas définie), que la tâche `rejeu` compare entre elles par l'outil de divergence.

Avec FOURX_REGENERER_REFERENCES=1, ce test est l'outil de régénération (`partie_reference.py`).
"""

import os
from pathlib import Path

import msgspec
import pytest

from fourx.core.version import rules_version
from fourx.core.world import generate
from fourx.server.order_log import import_jsonl
from fourx.server.tunables_loader import load_tunables
from fourx.tools.divergence import first_divergence, texte
from fourx.tools.replay import replay_orders
from tests.rejeu.partie_reference import (
    GRAINE,
    RACINE,
    TICKS,
    dossier_de_revision,
    lire_reference,
    regenerer,
    releves,
)


def dossier_des_empreintes() -> Path:
    graine = os.environ.get("PYTHONHASHSEED")
    return RACINE / "runs" / f"rejeu-{graine if graine is not None else 'aleatoire'}"


@pytest.mark.rejeu
def test_rejeu_de_la_partie_de_reference(tmp_path: Path) -> None:
    tunables = load_tunables()
    if os.environ.get("FOURX_REGENERER_REFERENCES") == "1":
        regenerer(tmp_path, tunables, print)
        return
    dossier = dossier_de_revision()
    reference = lire_reference(dossier)
    en_tete, ordres = import_jsonl(dossier / "orders.jsonl")
    assert reference.rules_version == rules_version(tunables), (
        "les règles ont changé : régénérer les références "
        "(FOURX_REGENERER_REFERENCES=1, et RULES_REVISION augmenté de un)"
    )
    assert en_tete.rules_version == reference.rules_version
    assert (en_tete.world_seed, en_tete.last_tick, len(ordres)) == (GRAINE, TICKS, TICKS)
    empreintes, _ = replay_orders(generate(GRAINE, tunables), ordres, GRAINE, tunables)
    sortie = dossier_des_empreintes()
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "fingerprints.jsonl").write_bytes(
        b"".join(msgspec.json.encode(e) + b"\n" for e in empreintes)
    )
    assert [e.tick for e in empreintes] == list(range(1, TICKS + 1))
    divergence = first_divergence(reference.fingerprints, releves(empreintes))
    assert divergence is None, f"le rejeu diverge de la référence : {texte(divergence)}"
