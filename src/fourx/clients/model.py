"""Le modèle du client, sans Textual.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 7 bis (architecture du
client, ordres envoyés, alertes, durées) et 13 (interface de `ClientModel`). `ClientModel` garde
la dernière observation, les ordres envoyés sans résultat (numéro → commande), la file de vente,
les alertes non acquittées et l'historique. Il reçoit une mise à jour et rend le message à
envoyer, s'il y en a un : la vente suivante de la file. Il implémente `SyncClient` : attaché au
serveur en mode sans horloge, le message qu'il rend entre au tick suivant ; en mode avec
horloge, `FourxApp` le soumet par sa connexion.
"""

import enum
from dataclasses import dataclass

from fourx.clients.texts import minerai, refusal_text, systeme, ticks_de_trajet
from fourx.policies.cargo import most_abundant
from fourx.schema.actors import Activity
from fourx.schema.events import Arrived, MiningEnded, MiningStarted, Sale
from fourx.schema.observation import Observation, OwnShipView
from fourx.schema.orders import Command, Mine, Move, Order, OrderCategory, Sell
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate


class AlertKind(enum.Enum):
    ARRIVED = "arrived"
    MINING_ENDED = "mining_ended"


@dataclass(frozen=True)
class Alert:
    kind: AlertKind
    tick: int
    text: str


def decrire(command: Command) -> str:
    """Le contenu d'un ordre, tel que l'historique et le cadre Vaisseau le nomment."""
    if isinstance(command, Move):
        return f"déplacer vers {systeme(command.target_system_id)}"
    if isinstance(command, Mine):
        return f"miner {minerai(command.ore_id)}"
    if isinstance(command, Sell):
        return f"vendre {command.quantity} {minerai(command.ore_id)}"
    return f"créer un personnage {command.actor_kind.value}"


def plafond(a: int, b: int) -> int:
    """⌈a ÷ b⌉ pour des entiers positifs."""
    return -(-a // b)


class ClientModel:
    def __init__(self, actor_id: int) -> None:
        self.actor_id = actor_id
        self.observation: Observation | None = None
        self._numero = 0
        self._envoyes: dict[int, Command] = {}
        self._file: list[Sell] = []
        self._vente_en_cours: int | None = None
        self._alertes: list[Alert] = []
        self._historique: list[str] = []

    @property
    def pending(self) -> tuple[tuple[int, Command], ...]:
        """Les ordres envoyés qui attendent leur résultat, par numéro croissant."""
        return tuple(sorted(self._envoyes.items()))

    @property
    def alerts(self) -> tuple[Alert, ...]:
        """Les alertes non acquittées, la plus ancienne d'abord."""
        return tuple(self._alertes)

    @property
    def history(self) -> tuple[str, ...]:
        return tuple(self._historique)

    def vaisseau(self) -> OwnShipView | None:
        """Le vaisseau du joueur : chaque personnage en a un à M1."""
        if self.observation is None or not self.observation.own_ships:
            return None
        return self.observation.own_ships[0]

    def _message(self, command: Command) -> SubmitOrders:
        self._numero += 1
        self._envoyes[self._numero] = command
        ordre = Order(
            actor_id=self.actor_id,
            number=self._numero,
            category=OrderCategory.PLAYER,
            policy_id=None,
            policy_version=None,
            command=command,
        )
        return SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=(ordre,))

    def send(self, command: Command) -> SubmitOrders:
        """Un ordre du joueur ; il vide la file de vente."""
        self._file = []
        self._vente_en_cours = None
        return self._message(command)

    def sell_all(self) -> SubmitOrders | None:
        """Une vente par minerai, le plus abondant d'abord (à quantités égales, le plus petit
        identifiant) ; la première part tout de suite, chaque suivante après le résultat de la
        précédente. None si la cargaison est vide."""
        navire = self.vaisseau()
        if navire is None:
            return None
        ventes = sorted(
            (
                Sell(ship_id=navire.id, ore_id=rang + 1, quantity=q)
                for rang, q in enumerate(navire.cargo)
                if q > 0
            ),
            key=lambda v: (-v.quantity, v.ore_id),
        )
        if not ventes:
            return None
        message = self.send(ventes[0])
        self._file = ventes[1:]
        self._vente_en_cours = self._numero
        return message

    def acknowledge(self) -> None:
        """Retire l'alerte la plus ancienne."""
        if self._alertes:
            self._alertes.pop(0)

    def remaining_ticks(self) -> int | None:
        """Ticks restants du trajet ou du minage en cours ; None à l'arrêt."""
        navire = self.vaisseau()
        if navire is None or self.observation is None:
            return None
        reglages = self.observation.public_tunables
        if navire.activity is Activity.EN_ROUTE:
            return ticks_de_trajet(navire, reglages.jump_ticks)
        if navire.activity is Activity.MINING:
            libre = plafond(navire.capacity - sum(navire.cargo), reglages.mining_rate)
            stocks = [
                d.stock
                for d in self.observation.deposits
                if d.system_id == navire.system_id
                and d.ore_id == navire.mining_ore_id
                and d.stock is not None
            ]
            return min([libre] + [plafond(s, reglages.mining_rate) for s in stocks])
        return None

    def _alerter(self, kind: AlertKind, tick: int, text: str) -> None:
        self._alertes.append(Alert(kind=kind, tick=tick, text=text))
        self._historique.append(f"t{tick} {text}")

    def _minerai_mine(
        self, observation: Observation, precedente: Observation | None, navire: OwnShipView
    ) -> int:
        """Le minerai d'un minage qui vient de finir : celui du minage commencé dans ce même
        tick, sinon celui de l'observation précédente, sinon le plus abondant de la cargaison."""
        for e in observation.events:
            if isinstance(e.payload, MiningStarted) and e.payload.ship_id == navire.id:
                return e.payload.ore_id
        if precedente is not None:
            for v in precedente.own_ships:
                if v.id == navire.id and v.mining_ore_id is not None:
                    return v.mining_ore_id
        abondant = most_abundant(navire.cargo)
        if abondant is None:
            raise ValueError(
                "fin de minage d'un vaisseau à la cargaison vide et au minerai inconnu"
            )
        return abondant[0]

    def on_update(self, update: TickUpdate) -> SubmitOrders | None:
        observation = update.observation
        precedente = self.observation
        self.observation = observation
        tick = observation.tick
        reponse: SubmitOrders | None = None
        for resultat in observation.results:
            command = self._envoyes.pop(resultat.order_id.number, None)
            if command is None:
                continue
            if resultat.accepted:
                self._historique.append(f"t{tick} ordre « {decrire(command)} » : accepté")
            else:
                texte = refusal_text(resultat, command, observation)
                self._historique.append(f"t{tick} ordre « {decrire(command)} » : refusé : {texte}")
            if resultat.order_id.number == self._vente_en_cours:
                self._vente_en_cours = None
                if resultat.accepted and self._file:
                    reponse = self._message(self._file.pop(0))
                    self._vente_en_cours = self._numero
                else:
                    self._file = []
        propres = {v.id: v for v in observation.own_ships}
        for e in observation.events:
            charge = e.payload
            if isinstance(charge, Sale) and charge.ship_id in propres:
                self._historique.append(
                    f"t{tick} vente : {charge.quantity} {minerai(charge.ore_id)} à {charge.price}, "
                    f"paiement {charge.payment}, taxe {charge.tax}"
                )
            elif (
                isinstance(charge, Arrived)
                and charge.ship_id in propres
                and not propres[charge.ship_id].route
            ):
                self._alerter(AlertKind.ARRIVED, tick, f"arrivée : {systeme(charge.system_id)}")
            elif (
                isinstance(charge, MiningEnded)
                and charge.ship_id in propres
                and e.causation_id is None
            ):
                navire = propres[charge.ship_id]
                ore_id = self._minerai_mine(observation, precedente, navire)
                texte = f"fin de minage : {minerai(ore_id)} {sum(navire.cargo)}/{navire.capacity}"
                self._alerter(AlertKind.MINING_ENDED, tick, texte)
        return reponse
