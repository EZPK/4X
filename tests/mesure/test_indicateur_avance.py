"""L'indicateur avancé (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 11 ; plan détaillé,
point 27). Marque `mesure`, lancé à la main :

    FOURX_MESURE=1 uv run pytest -m mesure -s

Mesure les ticks par seconde de `step` et de `observe` (une observation par acteur et par tick),
sans serveur, sur un monde généré de 12 systèmes (`systems_min` = `systems_max` = 12, réglages de
mesure hors de `tunables.toml`) et 30 PNJ créés par des ordres d'administration. Les ordres des PNJ
sont calculés hors du temps mesuré (hôte des PNJ, politique `scripted_miner`, réception). Le test
affiche le résultat ; rien ne dépend de sa valeur.
"""

import time

import msgspec
import pytest

from fourx.clients.npc_host import NpcHost
from fourx.core.observe import observe
from fourx.core.step import step
from fourx.core.world import generate
from fourx.policies.scripted_miner import decide
from fourx.schema.actors import ActorKind
from fourx.schema.orders import CreateCharacter, Order, OrderCategory, SubmittedOrder
from fourx.schema.protocol import PROTOCOL_VERSION, TickUpdate
from fourx.server.reception import Reception
from fourx.server.tunables_loader import load_tunables

GRAINE = 1
N_PNJ = 30
TICKS = 2_000


@pytest.mark.mesure
def test_ticks_par_seconde_de_step_et_observe() -> None:
    tunables = msgspec.structs.replace(load_tunables(), systems_min=12, systems_max=12)
    etat = generate(GRAINE, tunables)
    assert len(etat.systems) == 12
    creations = tuple(
        SubmittedOrder(
            tick=1,
            sender_actor_id=None,
            order=Order(
                actor_id=k,
                number=0,
                category=OrderCategory.ADMIN,
                policy_id=None,
                policy_version=None,
                command=CreateCharacter(actor_kind=ActorKind.NPC),
            ),
            reception_refusal=None,
        )
        for k in range(1, N_PNJ + 1)
    )
    etat, _ = step(etat, creations, GRAINE, tunables)
    assert len(etat.ships) == N_PNJ
    hotes = {a.id: NpcHost(a.id, decide) for a in etat.actors}
    reception = Reception()
    duree_step = duree_observe = 0.0
    for _ in range(TICKS):
        debut = time.perf_counter()
        observations = {ident: observe(etat, ident, tunables) for ident in sorted(hotes)}
        duree_observe += time.perf_counter() - debut
        soumis: list[SubmittedOrder] = []
        for ident in sorted(hotes):
            message = hotes[ident].on_update(
                TickUpdate(protocol_version=PROTOCOL_VERSION, observation=observations[ident])
            )
            if message is not None:
                soumis += reception.receive(ident, (message,), etat.tick + 1)
        debut = time.perf_counter()
        etat, _ = step(etat, tuple(soumis), GRAINE, tunables)
        duree_step += time.perf_counter() - debut
    print(
        f"\nIndicateur avancé : 12 systèmes, {N_PNJ} PNJ, {TICKS} ticks\n"
        f"- step seul : {TICKS / duree_step:.0f} ticks/s\n"
        f"- observe ({N_PNJ} observations par tick) : {TICKS / duree_observe:.0f} ticks/s\n"
        f"- step et observe : {TICKS / (duree_step + duree_observe):.0f} ticks/s"
    )
