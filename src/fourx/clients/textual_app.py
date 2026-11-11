"""Le client Textual minimal.

Document : docs/designs/niveau-2-m1-noyau.md,
Technical Plan, point 7 ; plan détaillé, point 22.

Affiche la carte en ASCII, l'état du vaisseau, le solde du portefeuille et l'historique des
résultats d'ordre et des ventes. Touches : `d` puis le numéro d'un système (déplacer), `m` puis
la lettre d'un minerai (miner), `v` (vendre toute la cargaison : un ordre par minerai),
`q` (quitter).
Le client ne connaît que `schema` (niveau 1, §1).
"""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.widgets import Footer, RichLog, Static

from fourx.schema.actors import Activity
from fourx.schema.events import MiningEnded, Sale
from fourx.schema.observation import Observation
from fourx.schema.orders import Command, Mine, Move, Order, OrderCategory, Sell
from fourx.schema.protocol import PROTOCOL_VERSION, Connection, SubmitOrders

ACTIVITES = {
    Activity.IDLE: "à l'arrêt",
    Activity.EN_ROUTE: "en route",
    Activity.MINING: "en minage",
}


def lettre(ore_id: int) -> str:
    return chr(ord("a") + ore_id - 1)


def carte(observation: Observation) -> str:
    """Une ligne par système : sites, vaisseau du propriétaire (@) et autres vaisseaux (o)."""
    lignes = []
    for systeme in observation.systems:
        sites = ["station" for s in observation.stations if s.system_id == systeme.id]
        sites += [
            f"gisement ore_{lettre(d.ore_id)} ({d.stock})"
            for d in observation.deposits
            if d.system_id == systeme.id
        ]
        vaisseaux = "@" * sum(1 for v in observation.own_ships if v.system_id == systeme.id)
        vaisseaux += "o" * sum(1 for v in observation.other_ships if v.system_id == systeme.id)
        lignes.append(f"[{systeme.id}] system_{systeme.id:<3} {vaisseaux:<4} {', '.join(sites)}")
    return "\n".join(lignes)


def etat(observation: Observation) -> str:
    lignes = [f"Tick {observation.tick}   Portefeuille : {observation.wallet_balance}"]
    for v in observation.own_ships:
        route = " → ".join(f"system_{s}" for s in v.route) or "—"
        cargaison = ", ".join(f"ore_{lettre(i + 1)} : {q}" for i, q in enumerate(v.cargo))
        lignes.append(
            f"Vaisseau {v.id} : system_{v.system_id}, {ACTIVITES[v.activity]}, route {route}"
        )
        lignes.append(f"Cargaison ({sum(v.cargo)}/{v.capacity}) : {cargaison}")
    lignes.append(f"Actions restantes : {observation.action_budget}")
    return "\n".join(lignes)


def historique(observation: Observation) -> list[str]:
    lignes = []
    for r in observation.results:
        issue = "accepté" if r.accepted else f"refusé ({r.text})"
        lignes.append(f"t{observation.tick} ordre {r.order_id.number} : {issue}")
    for e in observation.events:
        if isinstance(e.payload, Sale):
            p = e.payload
            lignes.append(
                f"t{observation.tick} vente : {p.quantity} ore_{lettre(p.ore_id)} à {p.price}, "
                f"payé {p.payment}, taxe {p.tax}"
            )
        elif isinstance(e.payload, MiningEnded) and e.actor_id == observation.actor_id:
            lignes.append(f"t{observation.tick} fin de minage : {e.payload.quantity} unités")
    return lignes


class FourxApp(App[None]):
    TITLE = "4X — tranche 0"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("d", "deplacer", "Déplacer"),
        Binding("m", "miner", "Miner"),
        Binding("v", "vendre", "Vendre"),
        Binding("q", "quit", "Quitter"),
    ]

    def __init__(self, connection: Connection, actor_id: int) -> None:
        super().__init__()
        self.connection = connection
        self.actor_id = actor_id
        self.observation: Observation | None = None
        self.attente: str | None = None
        self.numero = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("En attente du premier tick…", id="carte")
            yield Static("", id="etat")
            yield Static("", id="aide")
            yield RichLog(id="historique", max_lines=200)
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self.recevoir(), exclusive=True)

    async def recevoir(self) -> None:
        while True:
            update = await self.connection.next_update()
            self.afficher(update.observation)

    def afficher(self, observation: Observation) -> None:
        self.observation = observation
        self.query_one("#carte", Static).update(carte(observation))
        self.query_one("#etat", Static).update(etat(observation))
        log = self.query_one("#historique", RichLog)
        for ligne in historique(observation):
            log.write(ligne)

    def envoyer(self, *commandes: Command) -> None:
        """Un message pour toutes les commandes, chacune avec le numéro d'ordre suivant."""
        ordres = []
        for commande in commandes:
            self.numero += 1
            ordres.append(
                Order(
                    actor_id=self.actor_id,
                    number=self.numero,
                    category=OrderCategory.PLAYER,
                    policy_id=None,
                    policy_version=None,
                    command=commande,
                )
            )
        self.connection.submit(
            SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=tuple(ordres))
        )

    def vaisseau(self) -> int | None:
        if self.observation is None or not self.observation.own_ships:
            return None
        return self.observation.own_ships[0].id

    def aide(self, texte: str) -> None:
        self.query_one("#aide", Static).update(texte)

    def action_deplacer(self) -> None:
        self.attente = "deplacer"
        self.aide("Déplacer vers quel système ? (1, 2 ou 3)")

    def action_miner(self) -> None:
        self.attente = "miner"
        self.aide("Miner quel minerai ? (a ou b)")

    def action_vendre(self) -> None:
        navire = self.vaisseau()
        if navire is None or self.observation is None:
            return
        ventes = [
            Sell(ship_id=navire, ore_id=rang + 1, quantity=quantite)
            for rang, quantite in enumerate(self.observation.own_ships[0].cargo)
            if quantite > 0
        ]
        if ventes:
            self.envoyer(*ventes)
            detail = ", ".join(f"{v.quantity} ore_{lettre(v.ore_id)}" for v in ventes)
            self.aide(f"Vente envoyée : {detail}.")

    def on_key(self, event: object) -> None:
        touche = getattr(event, "character", None)
        navire = self.vaisseau()
        if self.attente is None or touche is None or navire is None:
            return
        if self.attente == "deplacer" and touche.isdigit():
            self.envoyer(Move(ship_id=navire, target_system_id=int(touche)))
            self.aide(f"Déplacement vers system_{touche} envoyé.")
            self.attente = None
        elif self.attente == "miner" and touche in "ab":
            self.envoyer(Mine(ship_id=navire, ore_id=ord(touche) - ord("a") + 1))
            self.aide(f"Minage de ore_{touche} envoyé.")
            self.attente = None
