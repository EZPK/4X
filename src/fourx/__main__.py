"""Point de départ du jeu : `python -m fourx [--graine N]`.

Document : docs/designs/niveau-2-m1-noyau.md,
Technical Plan, points 1 et 6 ; plan détaillé, point 22.
Ce module, à la racine du paquet, est le seul qui relie le serveur en mémoire et le client.
"""

import argparse
import asyncio
import contextlib
import secrets
from pathlib import Path

from fourx.clients.npc_host import NpcHost
from fourx.clients.textual_app import FourxApp
from fourx.policies.scripted_miner import decide
from fourx.schema.actors import ActorKind
from fourx.schema.protocol import Connection
from fourx.server.game import Game
from fourx.server.tunables_loader import load_tunables


async def relayer(connexion: Connection, hote: NpcHost) -> None:
    """Transmet chaque mise à jour du tick à l'hôte des PNJ, et ses ordres au serveur."""
    while True:
        reponse = hote.on_update(await connexion.next_update())
        if reponse is not None:
            connexion.submit(reponse)


async def jouer(graine: int, periode: float, runs_dir: Path) -> None:
    game = Game(runs_dir, graine, load_tunables(), period_s=periode)
    humain = game.create_character(ActorKind.HUMAN)
    pnj = game.create_character(ActorKind.NPC)
    taches = [
        asyncio.create_task(game.run()),
        asyncio.create_task(relayer(game.connect(pnj), NpcHost(pnj, decide))),
    ]
    try:
        await FourxApp(game.connect(humain), humain).run_async()
    finally:
        for tache in taches:
            tache.cancel()
        for tache in taches:
            with contextlib.suppress(asyncio.CancelledError):
                await tache
        game.close()


def principal() -> None:
    analyseur = argparse.ArgumentParser(prog="python -m fourx", description="4X — tranche 0")
    analyseur.add_argument("--graine", type=int, default=None, help="graine du monde")
    analyseur.add_argument(
        "--periode", type=float, default=1.0, help="durée d'un tick, en secondes"
    )
    analyseur.add_argument("--runs", type=Path, default=Path("runs"), help="dossier des parties")
    options = analyseur.parse_args()
    graine = options.graine if options.graine is not None else secrets.randbelow(2**31)
    print(f"Graine du monde : {graine}")
    asyncio.run(jouer(graine, options.periode, options.runs))


if __name__ == "__main__":
    principal()
