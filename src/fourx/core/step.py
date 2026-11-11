"""La fonction `step` (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 2, 3 et 5 ;
niveau 1, §2).

Chronologie du tick : examen des ordres soumis (par actor_id croissant puis numéro croissant),
puis les phases dans leur suite fixe. Aucun état n'est modifié en place : chaque étape produit
de nouvelles tables à partir des précédentes.
"""

import enum

import msgspec.structs

from fourx.core.arith import mul_div_ceil, rem_trunc
from fourx.core.keyed_random import keyed_draw
from fourx.core.ledger import DESTRUCTION_ACCOUNT_ID, ISSUANCE_ACCOUNT_ID, ouvrir, post
from fourx.core.state import Actor, Deposit, LastTick, Ship, State, Station
from fourx.core.tunables import Tunables
from fourx.core.version import rules_version
from fourx.schema.actors import Activity
from fourx.schema.events import (
    CLASSES,
    EVENT_SCHEMA_VERSION,
    Arrived,
    CharacterCreated,
    Departed,
    DepositRegenerated,
    Event,
    LedgerEntryRecorded,
    MiningEnded,
    MiningStarted,
    OrderRefused,
    Payload,
    Sale,
)
from fourx.schema.ledger import AccountKind, LedgerEntry, Reason
from fourx.schema.orders import (
    CreateCharacter,
    Mine,
    Move,
    OrderCategory,
    Sell,
    SubmittedOrder,
    identite,
)
from fourx.schema.results import OrderResult, RefusalCode

MOTIF_MINAGE = "minage"
DIX_MILLE = 10_000


class Phase(enum.Enum):
    MOVEMENT = "movement"
    MINING = "mining"
    TRADE = "trade"
    COMBAT = "combat"
    SETTLEMENT = "settlement"


class _Tick:
    """Tables de travail d'un tick ; elles redeviennent des tuples triés à la fin de `step`."""

    def __init__(self, state: State, world_seed: int, tunables: Tunables) -> None:
        self.tick = state.tick + 1
        self.world_seed = world_seed
        self.tunables = tunables
        self.rules_version = rules_version(tunables)
        self.systems = {s.id: s for s in state.systems}
        self.deposits = {d.id: d for d in state.deposits}
        self.stations = state.stations
        self.actors = {a.id: a for a in state.actors}
        self.ships = {s.id: s for s in state.ships}
        self.ledger = msgspec.structs.replace(state.ledger, tick_entries=())
        self.events: list[Event] = []
        self.results: list[OrderResult] = []
        self.ventes: list[tuple[SubmittedOrder, Sell]] = []

    def emettre(
        self,
        payload: Payload,
        actor_id: int | None,
        cause: SubmittedOrder | None = None,
    ) -> None:
        acteur = self.actors.get(actor_id) if actor_id is not None else None
        ordre = cause.order if cause is not None else None
        self.events.append(
            Event(
                tick=self.tick,
                seq=len(self.events),
                event_schema_version=EVENT_SCHEMA_VERSION,
                rules_version=self.rules_version,
                actor_id=actor_id,
                actor_kind=acteur.kind if acteur is not None else None,
                policy_id=ordre.policy_id if ordre is not None else None,
                policy_version=ordre.policy_version if ordre is not None else None,
                causation_id=identite(cause) if cause is not None else None,
                visibility=CLASSES[type(payload)],
                payload=payload,
            )
        )

    def passer(
        self, entry: LedgerEntry, actor_id: int | None, cause: SubmittedOrder | None = None
    ) -> None:
        self.ledger = post(self.ledger, entry)
        self.emettre(LedgerEntryRecorded(entry=entry), actor_id, cause)

    def station(self) -> Station:
        return self.stations[0]

    def gisement(self, system_id: int, ore_id: int) -> Deposit | None:
        for d in sorted(self.deposits.values(), key=lambda g: g.id):
            if d.system_id == system_id and d.ore_id == ore_id:
                return d
        return None

    def portefeuille(self, actor_id: int) -> int:
        for c in self.ledger.accounts:
            if c.kind is AccountKind.PERSONAL_WALLET and c.owner_id == actor_id:
                return c.id
        raise KeyError(actor_id)

    def budget(self, actor_id: int) -> int:
        acteur = self.actors.get(actor_id)
        return acteur.action_budget if acteur is not None else 0


def plus_court_chemin(
    voisins: dict[int, tuple[int, ...]], depart: int, arrivee: int
) -> tuple[int, ...]:
    """Parcours en largeur, voisins par identifiant croissant ; la route exclut le départ."""
    precedent: dict[int, int] = {depart: depart}
    file = [depart]
    while file:
        courant = file.pop(0)
        if courant == arrivee:
            break
        for voisin in sorted(voisins[courant]):
            if voisin in voisins and voisin not in precedent:
                precedent[voisin] = courant
                file.append(voisin)
    route: list[int] = []
    noeud = arrivee
    while noeud != depart:
        route.append(noeud)
        noeud = precedent[noeud]
    return tuple(reversed(route))


def _refus_d_etat(t: _Tick, soumis: SubmittedOrder) -> RefusalCode | None:
    """Contrôles du tableau des ordres, dans l'ordre des colonnes ; puis le budget."""
    ordre = soumis.order
    commande = ordre.command
    if not isinstance(commande, (Move, Mine, Sell)):
        return RefusalCode.FORBIDDEN_CATEGORY
    vaisseau = t.ships.get(commande.ship_id)
    if vaisseau is None:
        return RefusalCode.UNKNOWN_SHIP
    if vaisseau.owner_id != ordre.actor_id:
        return RefusalCode.NOT_OWNER
    if vaisseau.activity is Activity.EN_ROUTE:
        return RefusalCode.SHIP_EN_ROUTE
    if isinstance(commande, Move):
        if commande.target_system_id not in t.systems:
            return RefusalCode.UNKNOWN_SYSTEM
        if commande.target_system_id == vaisseau.system_id:
            return RefusalCode.ALREADY_THERE
    elif isinstance(commande, Mine):
        gisement = t.gisement(vaisseau.system_id, commande.ore_id)
        if gisement is None:
            return RefusalCode.NO_DEPOSIT_FOR_ORE
        if gisement.stock == 0:
            return RefusalCode.DEPOSIT_EMPTY
        if sum(vaisseau.cargo) >= vaisseau.capacity:
            return RefusalCode.CARGO_FULL
    else:
        if vaisseau.system_id != t.station().system_id:
            return RefusalCode.NOT_AT_STATION
        if commande.quantity <= 0:
            return RefusalCode.QUANTITY_NOT_POSITIVE
        rang = commande.ore_id - 1
        en_cargaison = vaisseau.cargo[rang] if 0 <= rang < len(vaisseau.cargo) else 0
        if commande.quantity > en_cargaison:
            return RefusalCode.QUANTITY_EXCEEDS_CARGO
    if t.budget(ordre.actor_id) <= 0:
        return RefusalCode.NO_ACTION_LEFT
    return None


def _arreter_minage(t: _Tick, vaisseau: Ship, cause: SubmittedOrder | None = None) -> Ship:
    """Arrête un minage en cours : événement « fin de minage », vaisseau à l'arrêt.

    `cause` est l'ordre qui remplace le minage, ou None quand les règles l'arrêtent."""
    if vaisseau.activity is not Activity.MINING:
        return vaisseau
    t.emettre(
        MiningEnded(ship_id=vaisseau.id, quantity=vaisseau.mined_since_start),
        vaisseau.owner_id,
        cause,
    )
    return msgspec.structs.replace(
        vaisseau, activity=Activity.IDLE, mining_ore_id=None, mined_since_start=0
    )


def _creer_personnage(t: _Tick, soumis: SubmittedOrder, commande: CreateCharacter) -> None:
    actor_id = max(t.actors, default=0) + 1
    ship_id = max(t.ships, default=0) + 1
    t.actors[actor_id] = Actor(
        id=actor_id, kind=commande.actor_kind, action_budget=t.tunables.budget_max
    )
    t.ledger, _ = ouvrir(t.ledger, AccountKind.PERSONAL_WALLET, actor_id)
    t.ships[ship_id] = Ship(
        id=ship_id,
        owner_id=actor_id,
        system_id=t.station().system_id,
        capacity=t.tunables.cargo_capacity,
        activity=Activity.IDLE,
        route=(),
        ticks_to_next_jump=0,
        cargo=(0,) * len(t.tunables.ore_prices),
        mining_ore_id=None,
        mined_since_start=0,
    )
    t.emettre(
        CharacterCreated(actor_id=actor_id, actor_kind=commande.actor_kind, ship_id=ship_id),
        actor_id,
        soumis,
    )
    t.results.append(
        OrderResult(
            recipient_actor_id=soumis.sender_actor_id,
            order_id=identite(soumis),
            accepted=True,
            refusal=None,
            text="personnage créé",
            budget_left=t.tunables.budget_max,
        )
    )


def _appliquer(t: _Tick, soumis: SubmittedOrder, commande: Move | Mine | Sell) -> None:
    ordre = soumis.order
    acteur = t.actors[ordre.actor_id]
    t.actors[acteur.id] = msgspec.structs.replace(acteur, action_budget=acteur.action_budget - 1)
    vaisseau = _arreter_minage(t, t.ships[commande.ship_id], soumis)
    if isinstance(commande, Move):
        voisins = {s.id: s.neighbors for s in t.systems.values()}
        route = plus_court_chemin(voisins, vaisseau.system_id, commande.target_system_id)
        vaisseau = msgspec.structs.replace(
            vaisseau,
            activity=Activity.EN_ROUTE,
            route=route,
            ticks_to_next_jump=t.tunables.jump_ticks,
        )
    elif isinstance(commande, Mine):
        vaisseau = msgspec.structs.replace(
            vaisseau, activity=Activity.MINING, mining_ore_id=commande.ore_id, mined_since_start=0
        )
        t.emettre(
            MiningStarted(ship_id=vaisseau.id, ore_id=commande.ore_id, rate=t.tunables.mining_rate),
            vaisseau.owner_id,
            soumis,
        )
    else:
        t.ventes.append((soumis, commande))
    t.ships[vaisseau.id] = vaisseau
    t.results.append(
        OrderResult(
            recipient_actor_id=soumis.sender_actor_id,
            order_id=identite(soumis),
            accepted=True,
            refusal=None,
            text="ordre accepté",
            budget_left=t.actors[acteur.id].action_budget,
        )
    )


def _refuser(t: _Tick, soumis: SubmittedOrder, code: RefusalCode) -> None:
    destinataire = soumis.sender_actor_id
    t.emettre(OrderRefused(order_id=identite(soumis), refusal=code), destinataire, soumis)
    t.results.append(
        OrderResult(
            recipient_actor_id=destinataire,
            order_id=identite(soumis),
            accepted=False,
            refusal=code,
            text=code.value,
            budget_left=t.budget(destinataire) if destinataire is not None else 0,
        )
    )


def _examiner(t: _Tick, orders: tuple[SubmittedOrder, ...]) -> None:
    # Un seul ordre examiné par (acteur, vaisseau) : le premier dans l'ordre (acteur, numéro),
    # donc celui de plus petit numéro ; les autres sont remplacés, même à numéro égal.
    examines: dict[tuple[int, int], int] = {}
    for soumis in sorted(orders, key=lambda s: (s.order.actor_id, s.order.number)):
        ordre = soumis.order
        commande = ordre.command
        if soumis.sender_actor_id is None:
            if ordre.category is OrderCategory.ADMIN and isinstance(commande, CreateCharacter):
                _creer_personnage(t, soumis, commande)
            else:
                _refuser(t, soumis, RefusalCode.FORBIDDEN_CATEGORY)
            continue
        if soumis.reception_refusal is not None:
            _refuser(t, soumis, soumis.reception_refusal)
            continue
        if isinstance(commande, (Move, Mine, Sell)):
            cle = (ordre.actor_id, commande.ship_id)
            if cle in examines:
                _refuser(t, soumis, RefusalCode.SUPERSEDED)
                continue
            examines[cle] = ordre.number
        code = _refus_d_etat(t, soumis)
        if code is not None:
            _refuser(t, soumis, code)
        elif isinstance(commande, (Move, Mine, Sell)):
            _appliquer(t, soumis, commande)


def _deplacement(t: _Tick) -> None:
    for ship_id in sorted(t.ships):
        vaisseau = t.ships[ship_id]
        if vaisseau.activity is not Activity.EN_ROUTE:
            continue
        restant = vaisseau.ticks_to_next_jump - 1
        if restant > 0:
            t.ships[ship_id] = msgspec.structs.replace(vaisseau, ticks_to_next_jump=restant)
            continue
        suivant = vaisseau.route[0]
        t.emettre(Departed(ship_id=ship_id, system_id=vaisseau.system_id), vaisseau.owner_id)
        t.emettre(Arrived(ship_id=ship_id, system_id=suivant), vaisseau.owner_id)
        route = vaisseau.route[1:]
        t.ships[ship_id] = msgspec.structs.replace(
            vaisseau,
            system_id=suivant,
            route=route,
            activity=Activity.EN_ROUTE if route else Activity.IDLE,
            ticks_to_next_jump=t.tunables.jump_ticks if route else 0,
        )


def _minage(t: _Tick) -> None:
    par_gisement: dict[int, list[Ship]] = {}
    for ship_id in sorted(t.ships):
        vaisseau = t.ships[ship_id]
        if vaisseau.activity is not Activity.MINING or vaisseau.mining_ore_id is None:
            continue
        gisement = t.gisement(vaisseau.system_id, vaisseau.mining_ore_id)
        if gisement is not None:
            par_gisement.setdefault(gisement.id, []).append(vaisseau)
    for deposit_id in sorted(par_gisement):
        gisement = t.deposits[deposit_id]
        vaisseaux = par_gisement[deposit_id]
        demandes = {v.id: min(t.tunables.mining_rate, v.capacity - sum(v.cargo)) for v in vaisseaux}
        if sum(demandes.values()) > gisement.stock:
            vaisseaux = sorted(
                vaisseaux,
                key=lambda v: (keyed_draw(t.world_seed, t.tick, v.id, MOTIF_MINAGE), v.id),
            )
        stock = gisement.stock
        for vaisseau in vaisseaux:
            recu = min(demandes[vaisseau.id], stock)
            stock -= recu
            rang = gisement.ore_id - 1
            cargaison = tuple(q + recu if i == rang else q for i, q in enumerate(vaisseau.cargo))
            vaisseau = msgspec.structs.replace(
                vaisseau, cargo=cargaison, mined_since_start=vaisseau.mined_since_start + recu
            )
            t.ships[vaisseau.id] = vaisseau
        t.deposits[deposit_id] = msgspec.structs.replace(gisement, stock=stock)
    for ship_id in sorted(v.id for vaisseaux in par_gisement.values() for v in vaisseaux):
        courant = t.ships[ship_id]
        gisement_courant = t.gisement(courant.system_id, courant.mining_ore_id or 0)
        vide = gisement_courant is None or gisement_courant.stock == 0
        if sum(courant.cargo) >= courant.capacity or vide:
            t.ships[ship_id] = _arreter_minage(t, courant)


def _commerce(t: _Tick) -> None:
    station = t.station()
    for soumis, vente in sorted(t.ventes, key=lambda v: v[1].ship_id):
        order_id = identite(soumis)
        vaisseau = t.ships[vente.ship_id]
        rang = vente.ore_id - 1
        prix = station.ore_prices[rang]
        paiement = vente.quantity * prix
        taxe = mul_div_ceil(paiement, t.tunables.tax_rate_bp, DIX_MILLE)
        cargaison = tuple(
            q - vente.quantity if i == rang else q for i, q in enumerate(vaisseau.cargo)
        )
        t.ships[vaisseau.id] = msgspec.structs.replace(vaisseau, cargo=cargaison)
        t.emettre(
            Sale(
                ship_id=vaisseau.id,
                ore_id=vente.ore_id,
                quantity=vente.quantity,
                price=prix,
                payment=paiement,
                tax=taxe,
            ),
            vaisseau.owner_id,
            soumis,
        )
        portefeuille = t.portefeuille(vaisseau.owner_id)
        t.passer(
            LedgerEntry(
                debit_account_id=ISSUANCE_ACCOUNT_ID,
                credit_account_id=portefeuille,
                amount=paiement,
                reason=Reason.ORE_SALE,
                cause=order_id,
            ),
            vaisseau.owner_id,
            soumis,
        )
        if taxe > 0:
            t.passer(
                LedgerEntry(
                    debit_account_id=portefeuille,
                    credit_account_id=DESTRUCTION_ACCOUNT_ID,
                    amount=taxe,
                    reason=Reason.SALE_TAX,
                    cause=order_id,
                ),
                vaisseau.owner_id,
                soumis,
            )


def _reglement(t: _Tick) -> None:
    for actor_id in sorted(t.actors):
        acteur = t.actors[actor_id]
        budget = min(t.tunables.budget_max, acteur.action_budget + t.tunables.budget_regen)
        t.actors[actor_id] = msgspec.structs.replace(acteur, action_budget=budget)
    if rem_trunc(t.tick, t.tunables.regen_ticks) == 0:
        for deposit_id in sorted(t.deposits):
            gisement = msgspec.structs.replace(
                t.deposits[deposit_id], stock=t.tunables.deposit_stock
            )
            t.deposits[deposit_id] = gisement
            t.emettre(DepositRegenerated(deposit_id=deposit_id, stock=gisement.stock), None)


def step(
    state: State, orders: tuple[SubmittedOrder, ...], world_seed: int, tunables: Tunables
) -> tuple[State, tuple[Event, ...]]:
    """Fait avancer le monde d'un tick ; seul point d'entrée des règles (niveau 1, §2)."""
    t = _Tick(state, world_seed, tunables)
    _examiner(t, orders)
    _deplacement(t)
    _minage(t)
    _commerce(t)
    # Phase de combat : vide à M1.
    _reglement(t)
    evenements = tuple(t.events)
    nouveau = State(
        tick=t.tick,
        systems=state.systems,
        deposits=tuple(t.deposits[i] for i in sorted(t.deposits)),
        stations=state.stations,
        actors=tuple(t.actors[i] for i in sorted(t.actors)),
        ships=tuple(t.ships[i] for i in sorted(t.ships)),
        ledger=t.ledger,
        last_tick=LastTick(events=evenements, results=tuple(t.results)),
    )
    return nouveau, evenements


__all__ = ["Phase", "step"]
