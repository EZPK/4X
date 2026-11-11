"""La partie du serveur en mémoire.

Document : docs/designs/niveau-2-m1-noyau.md,
Technical Plan, points 6 et 13 ; plan détaillé, point 21.

Une seule boucle asyncio : l'horloge (`run`) joue un tick à chaque période. Le mode sans horloge
(`advance`) joue un nombre donné de ticks, de façon synchrone. À chaque tick :
1. les ordres des connexions et des clients synchrones, reçus depuis le tick précédent, passent
   par la réception, un appel par acteur ; les ordres d'administration du serveur s'y ajoutent ;
2. `step` produit le nouvel état ; le journal et les événements sont enregistrés ;
3. chaque connexion et chaque client synchrone reçoit sa mise à jour du tick ; les ordres qu'un
   client synchrone renvoie entrent au tick suivant.
"""

import asyncio
from datetime import UTC, datetime
from pathlib import Path

from fourx.core import snapshot
from fourx.core.fingerprints import fingerprints
from fourx.core.observe import observe
from fourx.core.state import State
from fourx.core.step import step
from fourx.core.tunables import Tunables
from fourx.core.version import rules_version
from fourx.core.world import generate
from fourx.schema.actors import ActorKind
from fourx.schema.orders import CreateCharacter, Order, OrderCategory, SubmittedOrder
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, SyncClient, TickUpdate
from fourx.server.events_writer import EventsWriter
from fourx.server.order_log import OrderLog, lire_commit
from fourx.server.reception import Reception

RACINE_DEPOT = Path(__file__).resolve().parents[3]


class Connexion:
    """Point de connexion en mémoire d'un acteur : une paire de files asyncio."""

    def __init__(self, actor_id: int) -> None:
        self.actor_id = actor_id
        self.ordres: asyncio.Queue[SubmitOrders] = asyncio.Queue()
        self.mises_a_jour: asyncio.Queue[TickUpdate] = asyncio.Queue()

    def submit(self, message: SubmitOrders) -> None:
        self.ordres.put_nowait(message)

    async def next_update(self) -> TickUpdate:
        return await self.mises_a_jour.get()

    def vider_ordres(self) -> list[SubmitOrders]:
        messages: list[SubmitOrders] = []
        while not self.ordres.empty():
            messages.append(self.ordres.get_nowait())
        return messages


class Game:
    def __init__(
        self, runs_dir: Path, world_seed: int, tunables: Tunables, period_s: float = 1.0
    ) -> None:
        self.world_seed = world_seed
        self.tunables = tunables
        self.period_s = period_s
        horodatage = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        self.run_dir = runs_dir / horodatage
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.state: State = generate(world_seed, tunables)
        version = rules_version(tunables)
        commit, modifie = lire_commit(RACINE_DEPOT)
        instantane = snapshot.Snapshot(
            snapshot_schema_version=snapshot.SNAPSHOT_SCHEMA_VERSION,
            rules_version=version,
            world_seed=world_seed,
            commit=commit,
            worktree_dirty=modifie,
            state=self.state,
        )
        (self.run_dir / "snapshot.msgpack").write_bytes(snapshot.encode(instantane))
        self.journal = OrderLog.create(
            self.run_dir / "orders.sqlite", version, world_seed, commit, modifie
        )
        self.evenements = EventsWriter(self.run_dir / "events.jsonl")
        self.reception = Reception()
        self.connexions: dict[int, Connexion] = {}
        self.clients: list[tuple[int, SyncClient]] = []
        self._administration: list[Order] = []
        self._renvoyes: dict[int, list[SubmitOrders]] = {}

    def create_character(self, kind: ActorKind) -> int:
        """Journalise la création d'un personnage pour le prochain tick.

        Renvoie l'identifiant que recevra l'acteur (le plus grand identifiant connu plus un)."""
        deja = [a.id for a in self.state.actors] + [o.actor_id for o in self._administration]
        actor_id = max(deja, default=0) + 1
        self._administration.append(
            Order(
                actor_id=actor_id,
                number=0,
                category=OrderCategory.ADMIN,
                policy_id=None,
                policy_version=None,
                command=CreateCharacter(actor_kind=kind),
            )
        )
        return actor_id

    def connect(self, actor_id: int) -> Connexion:
        """Le point de connexion de l'acteur ; une seule connexion par acteur."""
        if actor_id not in self.connexions:
            self.connexions[actor_id] = Connexion(actor_id)
        return self.connexions[actor_id]

    def attach(self, actor_id: int, client: SyncClient) -> None:
        """Attache un client synchrone, appelé après chaque tick avec la mise à jour de l'acteur."""
        self.clients.append((actor_id, client))

    def _ordres_du_tick(self, tick: int) -> tuple[SubmittedOrder, ...]:
        administration = tuple(
            SubmittedOrder(tick=tick, sender_actor_id=None, order=o, reception_refusal=None)
            for o in self._administration
        )
        self._administration = []
        messages: dict[int, list[SubmitOrders]] = {a: list(m) for a, m in self._renvoyes.items()}
        self._renvoyes = {}
        for actor_id in sorted(self.connexions):
            messages.setdefault(actor_id, []).extend(self.connexions[actor_id].vider_ordres())
        joueurs = tuple(
            soumis
            for actor_id in sorted(messages)
            if messages[actor_id]
            for soumis in self.reception.receive(actor_id, tuple(messages[actor_id]), tick)
        )
        return administration + joueurs

    def _un_tick(self) -> None:
        ordres = self._ordres_du_tick(self.state.tick + 1)
        self.state, evenements = step(self.state, ordres, self.world_seed, self.tunables)
        self.journal.append(ordres, fingerprints(self.state))
        self.evenements.write(evenements)
        for actor_id in sorted(self.connexions):
            self.connexions[actor_id].mises_a_jour.put_nowait(self._mise_a_jour(actor_id))
        for actor_id, client in self.clients:
            reponse = client.on_update(self._mise_a_jour(actor_id))
            if reponse is not None:
                self._renvoyes.setdefault(actor_id, []).append(reponse)

    def _mise_a_jour(self, actor_id: int) -> TickUpdate:
        return TickUpdate(
            protocol_version=PROTOCOL_VERSION, observation=observe(self.state, actor_id)
        )

    def advance(self, n: int) -> None:
        """Mode sans horloge : joue n ticks, de façon synchrone."""
        for _ in range(n):
            self._un_tick()

    async def run(self) -> None:
        """Mode avec horloge : un tick à chaque période, jusqu'à l'annulation de la tâche."""
        while True:
            await asyncio.sleep(self.period_s)
            self._un_tick()

    def close(self) -> None:
        self.journal.close()
        self.evenements.close()
