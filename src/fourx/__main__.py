"""Point de départ du jeu : `python -m fourx [--graine N] [--periode S] [--runs DOSSIER]`.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 1 et 6 ; plan détaillé,
points 22 et 23 quater. Ce module, à la racine du paquet, est le seul qui relie le serveur en
mémoire et le client. La graine et le dossier de la partie s'affichent au lancement, et de
nouveau à la fermeture du client, puisque Textual efface l'affichage du lancement.
"""

import argparse
import asyncio
import contextlib
import secrets
from pathlib import Path

from fourx.clients.npc_host import NpcHost
from fourx.clients.textual_app import FourxApp
from fourx.core.tunables import Tunables
from fourx.core.world import npc_count
from fourx.policies.scripted_miner import decide
from fourx.schema.actors import ActorKind
from fourx.schema.protocol import NOMINAL_TICK_PERIOD_S, Connection
from fourx.server.game import Game
from fourx.server.tunables_loader import load_tunables


async def relayer(connexion: Connection, hote: NpcHost) -> None:
    """Transmet chaque mise à jour du tick à l'hôte des PNJ, et ses ordres au serveur."""
    while True:
        reponse = hote.on_update(await connexion.next_update())
        if reponse is not None:
            connexion.submit(reponse)


def creer_pnj(game: Game, graine: int, tunables: Tunables) -> tuple[int, ...]:
    """Crée les `npc_count(graine, réglages)` PNJ de la partie ; rend leurs identifiants."""
    return tuple(game.create_character(ActorKind.NPC) for _ in range(npc_count(graine, tunables)))


def annoncer(graine: int, dossier: Path) -> None:
    print(f"Graine du monde : {graine}")
    print(f"Dossier de la partie : {dossier}")


async def jouer(graine: int, periode: float, runs_dir: Path) -> None:
    tunables = load_tunables()
    game = Game(runs_dir, graine, tunables, period_s=periode)
    annoncer(graine, game.run_dir)
    humain = game.create_character(ActorKind.HUMAN)
    pnj = creer_pnj(game, graine, tunables)
    taches = [asyncio.create_task(game.run())]
    taches += [
        asyncio.create_task(relayer(game.connect(ident), NpcHost(ident, decide))) for ident in pnj
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
        annoncer(graine, game.run_dir)


def principal() -> None:
    analyseur = argparse.ArgumentParser(prog="python -m fourx", description="4X — tranche 0")
    analyseur.add_argument("--graine", type=int, default=None, help="graine du monde")
    analyseur.add_argument(
        "--periode",
        type=float,
        default=NOMINAL_TICK_PERIOD_S,
        help="durée d'un tick, en secondes, fixée pour toute la partie",
    )
    analyseur.add_argument("--runs", type=Path, default=Path("runs"), help="dossier des parties")
    options = analyseur.parse_args()
    graine = options.graine if options.graine is not None else secrets.randbelow(2**31)
    asyncio.run(jouer(graine, options.periode, options.runs))


if __name__ == "__main__":
    principal()
