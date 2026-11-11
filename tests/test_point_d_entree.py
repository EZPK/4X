"""Tests du point de départ `python -m fourx` (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 7 ; plan détaillé, point 22) : en mode avec horloge, une tâche transmet les mises à jour à
l'hôte des PNJ par sa connexion."""

import asyncio
import contextlib
from pathlib import Path

from fourx.__main__ import relayer
from fourx.clients.npc_host import NpcHost
from fourx.policies.scripted_miner import POLICY_ID, decide
from fourx.schema.actors import ActorKind
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
