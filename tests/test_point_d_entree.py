"""Tests du point de départ `python -m fourx` (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 7 ; plan détaillé, point 22) : en mode avec horloge, une tâche transmet les mises à jour à
l'hôte des PNJ par sa connexion."""

import asyncio
import contextlib
from pathlib import Path

from fourx.__main__ import analyser, creer_pnj, fonction_de_vitesse, relayer
from fourx.clients.npc_host import NpcHost
from fourx.core.world import npc_count
from fourx.policies.scripted_miner import POLICY_ID, decide
from fourx.schema.actors import ActorKind
from fourx.schema.protocol import NOMINAL_TICK_PERIOD_S
from fourx.server.game import Game
from fourx.server.order_log import OrderLog
from fourx.server.tunables_loader import load_tunables


def test_relais_des_ordres_du_pnj(tmp_path: Path) -> None:
    async def jouer() -> tuple[Path, int]:
        partie = Game(tmp_path, world_seed=3, tunables=load_tunables(), period_s=0.001)
        pnj = partie.create_character(ActorKind.NPC)
        humain = partie.create_character(ActorKind.HUMAN)
        temoin = partie.connect(humain)
        taches = [
            asyncio.create_task(partie.run()),
            asyncio.create_task(relayer(partie.connect(pnj), NpcHost(pnj, decide))),
        ]
        try:
            while (await temoin.next_update()).observation.tick < 3:
                pass
        finally:
            for tache in taches:
                tache.cancel()
            for tache in taches:
                with contextlib.suppress(asyncio.CancelledError):
                    await tache
            partie.close()
        return partie.run_dir, pnj

    dossier, pnj = asyncio.run(jouer())
    log = OrderLog(dossier / "orders.sqlite")
    du_pnj = [s for ordres in log.orders_by_tick() for s in ordres if s.sender_actor_id == pnj]
    log.close()
    # L'ordre décidé sur la mise à jour du tick 1 entre au tick 2.
    assert du_pnj
    assert du_pnj[0].tick == 2
    assert all(s.order.policy_id == POLICY_ID and s.reception_refusal is None for s in du_pnj)


def test_plusieurs_pnj(tmp_path: Path) -> None:
    """`creer_pnj` crée les npc_count(graine, réglages) PNJ de la partie."""
    reglages = load_tunables()
    partie = Game(tmp_path, world_seed=3, tunables=reglages)
    humain = partie.create_character(ActorKind.HUMAN)
    pnj = creer_pnj(partie, 3, reglages)
    partie.advance(1)
    partie.close()
    assert len(pnj) == npc_count(3, reglages) >= reglages.npc_min
    assert pnj == tuple(range(humain + 1, humain + 1 + len(pnj)))
    assert [a.kind for a in partie.state.actors if a.id in pnj] == [ActorKind.NPC] * len(pnj)


def test_options_de_lancement() -> None:
    defaut = analyser([])
    assert (defaut.graine, defaut.periode, defaut.runs, defaut.dev) == (
        None,
        NOMINAL_TICK_PERIOD_S,
        Path("runs"),
        False,
    )
    options = analyser(["--dev", "--graine", "7", "--periode", "0.5", "--runs", "ailleurs"])
    assert (options.graine, options.periode, options.runs, options.dev) == (
        7,
        0.5,
        Path("ailleurs"),
        True,
    )


def test_la_fonction_de_vitesse_divise_la_periode_de_lancement(tmp_path: Path) -> None:
    """Le client choisit un palier ; Game.set_period reçoit des secondes, ou None en pause."""
    partie = Game(tmp_path, world_seed=3, tunables=load_tunables(), period_s=3.0)
    set_speed = fonction_de_vitesse(partie, 3.0)
    vues: list[float | None] = []
    for facteur in (10, 100, None, 1):
        set_speed(facteur)
        vues.append(partie.period_s)
    partie.close()
    assert vues == [0.3, 0.03, None, 3.0]
