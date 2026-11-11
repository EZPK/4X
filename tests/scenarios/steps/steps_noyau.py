"""Définitions d'étapes du volet A de M1.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 15.

Chemin protégé. Les étapes sont écrites avant le code : elles n'importent le code de `fourx`
qu'à l'intérieur des fonctions, par `importlib`, pour qu'un module encore absent fasse
échouer le scénario sans casser `mypy` ni la collecte. Elles emploient les noms du
Technical Plan, point 13, et appliquent `step` directement, sans serveur.

Conventions que ces étapes figent :
- un ordre soumis porte le tick que `step` va produire, le tick de l'état plus un : cela découle
  du Technical Plan, point 6 (ordres de création journalisés pour le tick 1, instantané au tick 0,
  appliqués par le premier `step`) ;
- le tirage du départage porte ce même tick produit : le document ne le précise pas (à confirmer
  par le propriétaire avec la pull request de scénarios) ;
- le compte débité d'une écriture est celui d'où part l'argent (« émission → portefeuille ») ;
- après `step`, `ledger.tick_entries` contient les écritures du tick produit.
"""

import importlib
import re
from dataclasses import dataclass, field
from typing import Any

import pytest
from pytest_bdd import given, parsers, then, when

GRAINE = 1
REGLAGES_M1: dict[str, Any] = {
    "jump_ticks": 5,
    "mining_rate": 10,
    "cargo_capacity": 100,
    "ore_prices": (10, 15),
    "tax_rate_bp": 1000,
    "deposit_stock": 20000,
    "regen_ticks": 1000,
    "budget_regen": 1,
    "budget_max": 10,
}


def m(nom: str) -> Any:
    """Importe un module du jeu au moment de l'appel."""
    return importlib.import_module(nom)


def numero(libelle: str) -> int:
    """system_3 → 3, ship_1 → 1, actor_2 → 2."""
    trouve = re.fullmatch(r"[a-z]+_(\d+)", libelle)
    assert trouve is not None, libelle
    return int(trouve.group(1))


def minerai(libelle: str) -> int:
    """ore_a → 1, ore_b → 2 (lettre de rang de l'identifiant)."""
    trouve = re.fullmatch(r"ore_([a-z])", libelle)
    assert trouve is not None, libelle
    return ord(trouve.group(1)) - ord("a") + 1


@dataclass
class Partie:
    reglages: dict[str, Any] = field(default_factory=lambda: dict(REGLAGES_M1))
    systemes: list[int] = field(default_factory=list)
    station: int = 0
    # minerai → [id, système, stock] ; stock None : deposit_stock des réglages
    gisements: dict[int, list[int | None]] = field(default_factory=dict)
    acteurs: dict[int, int | None] = field(default_factory=dict)  # acteur → budget (None : maximum)
    vaisseaux: dict[int, list[Any]] = field(
        default_factory=dict
    )  # vaisseau → [acteur, système, cargaison]
    etat: Any = None
    tunables: Any = None
    initial: Any = None
    attente: list[Any] = field(default_factory=list)
    journal: list[tuple[Any, ...]] = field(default_factory=list)
    resultats: list[Any] = field(default_factory=list)
    evenements: list[Any] = field(default_factory=list)
    numeros: dict[int, int] = field(default_factory=dict)
    cargaison_initiale: int = 0

    def construire(self) -> None:
        """Construit l'état initial à partir de ce que les étapes « Étant donné » ont décrit."""
        if self.etat is not None:
            return
        tunables_mod = m("fourx.core.tunables")
        state = m("fourx.core.state")
        ledger = m("fourx.core.ledger")
        actors = m("fourx.schema.actors")
        schema_ledger = m("fourx.schema.ledger")
        self.tunables = tunables_mod.Tunables(**self.reglages)
        systemes = tuple(
            state.System(
                id=s,
                neighbors=tuple(v for v in (s - 1, s + 1) if v in self.systemes),
            )
            for s in self.systemes
        )
        gisements = tuple(
            state.Deposit(
                id=g[0],
                system_id=g[1],
                ore_id=o,
                stock=self.reglages["deposit_stock"] if g[2] is None else g[2],
            )
            for o, g in sorted(self.gisements.items())
        )
        stations = (
            state.Station(
                id=1, system_id=self.station, ore_prices=tuple(self.reglages["ore_prices"])
            ),
        )
        acteurs = tuple(
            state.Actor(
                id=a,
                kind=actors.ActorKind.HUMAN,
                action_budget=self.reglages["budget_max"] if b is None else b,
            )
            for a, b in sorted(self.acteurs.items())
        )
        vaisseaux = tuple(
            state.Ship(
                id=v,
                owner_id=d[0],
                system_id=d[1],
                capacity=self.reglages["cargo_capacity"],
                activity=actors.Activity.IDLE,
                route=(),
                ticks_to_next_jump=0,
                cargo=tuple(d[2]),
                mining_ore_id=None,
                mined_since_start=0,
            )
            for v, d in sorted(self.vaisseaux.items())
        )
        self.cargaison_initiale = sum(sum(d[2]) for d in self.vaisseaux.values())
        raisons = len(schema_ledger.Reason)
        comptes = [
            ledger.Account(id=1, kind=schema_ledger.AccountKind.ISSUANCE, owner_id=None, balance=0),
            ledger.Account(
                id=2, kind=schema_ledger.AccountKind.DESTRUCTION, owner_id=None, balance=0
            ),
        ] + [
            ledger.Account(
                id=2 + a, kind=schema_ledger.AccountKind.PERSONAL_WALLET, owner_id=a, balance=0
            )
            for a in sorted(self.acteurs)
        ]
        self.etat = state.State(
            tick=0,
            systems=systemes,
            deposits=gisements,
            stations=stations,
            actors=acteurs,
            ships=vaisseaux,
            ledger=ledger.Ledger(
                accounts=tuple(comptes),
                tick_entries=(),
                issued_by_reason=(0,) * raisons,
                destroyed_by_reason=(0,) * raisons,
            ),
            last_tick=state.LastTick(events=(), results=()),
        )
        self.initial = self.etat

    def ordonner(self, acteur: int, commande: Any, num: int | None) -> None:
        self.construire()
        orders = m("fourx.schema.orders")
        if num is None:
            num = self.numeros.get(acteur, 0) + 1
        self.numeros[acteur] = num
        ordre = orders.Order(
            actor_id=acteur,
            number=num,
            category=orders.OrderCategory.PLAYER,
            policy_id=None,
            policy_version=None,
            command=commande,
        )
        self.attente.append(
            orders.SubmittedOrder(
                tick=self.etat.tick + 1, sender_actor_id=acteur, order=ordre, reception_refusal=None
            )
        )

    def avancer(self, n: int) -> None:
        self.construire()
        step = m("fourx.core.step")
        for _ in range(n):
            ordres = tuple(self.attente)
            self.attente = []
            avant = self.etat
            self.etat, evenements = step.step(avant, ordres, GRAINE, self.tunables)
            self.journal.append(ordres)
            self.evenements.extend(evenements)
            self.resultats.extend(self.etat.last_tick.results)
            verifier_invariants(self, avant, self.etat)

    def vaisseau(self, libelle: str) -> Any:
        return next(v for v in self.etat.ships if v.id == numero(libelle))

    def gisement(self, libelle: str) -> Any:
        return next(g for g in self.etat.deposits if g.ore_id == minerai(libelle))

    def portefeuille(self, acteur: int) -> Any:
        kinds = m("fourx.schema.ledger").AccountKind
        return next(
            c
            for c in self.etat.ledger.accounts
            if c.kind == kinds.PERSONAL_WALLET and c.owner_id == acteur
        )

    def ecritures(self) -> list[Any]:
        events = m("fourx.schema.events")
        return [
            e.payload.entry
            for e in self.evenements
            if isinstance(e.payload, events.LedgerEntryRecorded)
        ]


def verifier_invariants(partie: Partie, avant: Any, apres: Any) -> None:
    """Les trois invariants du niveau 1, §4 (Technical Plan, point 3), après un tick."""
    ledger = m("fourx.core.ledger")
    events = m("fourx.schema.events")
    actors = m("fourx.schema.actors")
    kinds = m("fourx.schema.ledger").AccountKind
    comptes = apres.ledger.accounts
    assert sum(c.balance for c in comptes) == 0, "partie double"
    emission = {c.id for c in comptes if c.kind == kinds.ISSUANCE}
    destruction = {c.id for c in comptes if c.kind == kinds.DESTRUCTION}
    emis = sum(apres.ledger.issued_by_reason) - sum(avant.ledger.issued_by_reason)
    detruit = sum(apres.ledger.destroyed_by_reason) - sum(avant.ledger.destroyed_by_reason)
    ecrit_emis = sum(e.amount for e in apres.ledger.tick_entries if e.debit_account_id in emission)
    ecrit_detruit = sum(
        e.amount for e in apres.ledger.tick_entries if e.credit_account_id in destruction
    )
    assert emis == ecrit_emis, "compteur d'émission et écritures du tick différents"
    assert detruit == ecrit_detruit, "compteur de destruction et écritures du tick différents"
    masse_kinds = (kinds.PERSONAL_WALLET, kinds.CORPORATION_WALLET, kinds.ESCROW)
    masse = sum(c.balance for c in comptes if c.kind in masse_kinds)
    assert ledger.money_supply(apres.ledger) == masse, "money_supply contraire à sa définition"
    assert masse == ledger.money_supply(avant.ledger) + emis - detruit, "invariant 2"
    for v in apres.ships:
        assert all(q >= 0 for q in v.cargo), "cargaison négative"
    for g in apres.deposits:
        assert g.stock >= 0, "stock négatif"
    fin = sum(
        e.payload.quantity for e in partie.evenements if isinstance(e.payload, events.MiningEnded)
    )
    en_cours = sum(v.mined_since_start for v in apres.ships if v.activity == actors.Activity.MINING)
    vendu = sum(e.payload.quantity for e in partie.evenements if isinstance(e.payload, events.Sale))
    cargaison = sum(sum(v.cargo) for v in apres.ships)
    assert partie.cargaison_initiale + fin + en_cours == cargaison + vendu, "biens non conservés"


@pytest.fixture
def partie() -> Partie:
    return Partie()


# --- Étant donné


@given("les réglages de M1")
def reglages_m1(partie: Partie) -> None:
    partie.reglages = dict(REGLAGES_M1)


@given(
    parsers.re(
        r"une carte de trois systèmes en chaîne, la station dans (?P<s>system_\d+), "
        r"le gisement de ore_a dans (?P<a>system_\d+) et celui de ore_b dans (?P<b>system_\d+)"
    )
)
def carte(partie: Partie, s: str, a: str, b: str) -> None:
    partie.systemes = [1, 2, 3]
    partie.station = numero(s)
    partie.gisements = {1: [1, numero(a), None], 2: [2, numero(b), None]}


@given(
    parsers.re(
        r"(?P<acteur>actor_\d+) et son vaisseau (?P<vaisseau>ship_\d+) dans (?P<systeme>system_\d+)"
    )
)
def acteur_et_vaisseau(partie: Partie, acteur: str, vaisseau: str, systeme: str) -> None:
    partie.acteurs[numero(acteur)] = None
    partie.vaisseaux[numero(vaisseau)] = [numero(acteur), numero(systeme), [0, 0]]


@given(
    parsers.re(
        r"(?P<acteur>actor_\d+) et son vaisseau (?P<vaisseau>ship_\d+) "
        r"dans (?P<systeme>system_\d+), "
        r"avec (?P<q>\d+) unités de (?P<ore>ore_[a-z]) en cargaison"
    )
)
def acteur_et_vaisseau_charge(
    partie: Partie, acteur: str, vaisseau: str, systeme: str, q: str, ore: str
) -> None:
    cargaison = [0, 0]
    cargaison[minerai(ore) - 1] = int(q)
    partie.acteurs[numero(acteur)] = None
    partie.vaisseaux[numero(vaisseau)] = [numero(acteur), numero(systeme), cargaison]


@given(parsers.re(r"le gisement de (?P<ore>ore_[a-z]) contient (?P<n>\d+) unités"))
def gisement_donne(partie: Partie, ore: str, n: str) -> None:
    partie.gisements[minerai(ore)][2] = int(n)


@given(
    parsers.re(
        r"une régénération des gisements tous les (?P<n>\d+) ticks, jusqu'à (?P<s>\d+) unités"
    )
)
def regeneration(partie: Partie, n: str, s: str) -> None:
    partie.reglages["regen_ticks"] = int(n)
    partie.reglages["deposit_stock"] = int(s)


@given(parsers.re(r"(?P<acteur>actor_\d+) n'a plus aucune action"))
def sans_action(partie: Partie, acteur: str) -> None:
    partie.acteurs[numero(acteur)] = 0


# --- Quand


@when(
    parsers.re(
        r"(?P<acteur>actor_\d+) ordonne à (?P<vaisseau>ship_\d+) "
        r"d'aller dans (?P<systeme>system_\d+)"
    )
)
def ordre_deplacer(partie: Partie, acteur: str, vaisseau: str, systeme: str) -> None:
    orders = m("fourx.schema.orders")
    commande = orders.Move(ship_id=numero(vaisseau), target_system_id=numero(systeme))
    partie.ordonner(numero(acteur), commande, None)


@when(
    parsers.re(
        r"(?P<acteur>actor_\d+) ordonne à (?P<vaisseau>ship_\d+) de miner (?P<ore>ore_[a-z])"
        r"(?:, avec le numéro (?P<num>\d+))?"
    )
)
def ordre_miner(partie: Partie, acteur: str, vaisseau: str, ore: str, num: str | None) -> None:
    orders = m("fourx.schema.orders")
    commande = orders.Mine(ship_id=numero(vaisseau), ore_id=minerai(ore))
    partie.ordonner(numero(acteur), commande, None if num is None else int(num))


@when(
    parsers.re(
        r"(?P<acteur>actor_\d+) ordonne à (?P<vaisseau>ship_\d+) de vendre (?P<q>\d+) unités de "
        r"(?P<ore>ore_[a-z])(?:, avec le numéro (?P<num>\d+))?"
    )
)
def ordre_vendre(
    partie: Partie, acteur: str, vaisseau: str, q: str, ore: str, num: str | None
) -> None:
    orders = m("fourx.schema.orders")
    commande = orders.Sell(ship_id=numero(vaisseau), ore_id=minerai(ore), quantity=int(q))
    partie.ordonner(numero(acteur), commande, None if num is None else int(num))


@when(parsers.re(r"(?P<n>\d+) ticks? pass(?:e|ent)"))
def ticks_passent(partie: Partie, n: str) -> None:
    partie.avancer(int(n))


# --- Alors


@then(parsers.re(r"(?P<vaisseau>ship_\d+) n'est pas encore dans (?P<systeme>system_\d+)"))
def pas_encore_dans(partie: Partie, vaisseau: str, systeme: str) -> None:
    assert partie.vaisseau(vaisseau).system_id != numero(systeme)


@then(parsers.re(r"(?P<vaisseau>ship_\d+) est dans (?P<systeme>system_\d+)"))
def est_dans(partie: Partie, vaisseau: str, systeme: str) -> None:
    assert partie.vaisseau(vaisseau).system_id == numero(systeme)


@then(parsers.re(r"(?P<vaisseau>ship_\d+) est en route"))
def en_route(partie: Partie, vaisseau: str) -> None:
    actors = m("fourx.schema.actors")
    assert partie.vaisseau(vaisseau).activity == actors.Activity.EN_ROUTE


@then(
    parsers.re(
        r"(?P<vaisseau>ship_\d+) a quitté (?P<q1>system_\d+) puis (?P<q2>system_\d+), "
        r"et est arrivé dans (?P<a1>system_\d+) puis (?P<a2>system_\d+)"
    )
)
def departs_et_arrivees(partie: Partie, vaisseau: str, q1: str, q2: str, a1: str, a2: str) -> None:
    events = m("fourx.schema.events")
    ident = numero(vaisseau)
    quittes = [
        e.payload.system_id
        for e in partie.evenements
        if isinstance(e.payload, events.Departed) and e.payload.ship_id == ident
    ]
    atteints = [
        e.payload.system_id
        for e in partie.evenements
        if isinstance(e.payload, events.Arrived) and e.payload.ship_id == ident
    ]
    assert quittes == [numero(q1), numero(q2)]
    assert atteints == [numero(a1), numero(a2)]


@then(parsers.re(r"une fin de minage de (?P<vaisseau>ship_\d+) porte (?P<q>\d+) unités"))
def fin_de_minage(partie: Partie, vaisseau: str, q: str) -> None:
    events = m("fourx.schema.events")
    assert any(
        isinstance(e.payload, events.MiningEnded)
        and e.payload.ship_id == numero(vaisseau)
        and e.payload.quantity == int(q)
        for e in partie.evenements
    )


@then(parsers.re(r"(?P<vaisseau>ship_\d+) est à l'arrêt"))
def a_l_arret(partie: Partie, vaisseau: str) -> None:
    actors = m("fourx.schema.actors")
    assert partie.vaisseau(vaisseau).activity == actors.Activity.IDLE


@then(
    parsers.re(
        r"la cargaison de (?P<vaisseau>ship_\d+) contient (?P<q>\d+) unités de (?P<ore>ore_[a-z])"
    )
)
def cargaison(partie: Partie, vaisseau: str, q: str, ore: str) -> None:
    assert partie.vaisseau(vaisseau).cargo[minerai(ore) - 1] == int(q)


@then(parsers.re(r"le gisement de (?P<ore>ore_[a-z]) contient (?P<n>\d+) unités"))
def gisement_vaut(partie: Partie, ore: str, n: str) -> None:
    assert partie.gisement(ore).stock == int(n)


@then(
    parsers.re(
        r"le registre contient une écriture de vente de (?P<montant>\d+) "
        r"vers le portefeuille de (?P<acteur>actor_\d+)"
    )
)
def ecriture_vente(partie: Partie, montant: str, acteur: str) -> None:
    raison = m("fourx.schema.ledger").Reason
    portefeuille = partie.portefeuille(numero(acteur)).id
    assert any(
        e.reason == raison.ORE_SALE
        and e.amount == int(montant)
        and e.debit_account_id == 1
        and e.credit_account_id == portefeuille
        for e in partie.ecritures()
    )


@then(
    parsers.re(
        r"le registre contient une écriture de taxe de (?P<montant>\d+) "
        r"depuis le portefeuille de (?P<acteur>actor_\d+)"
    )
)
def ecriture_taxe(partie: Partie, montant: str, acteur: str) -> None:
    raison = m("fourx.schema.ledger").Reason
    portefeuille = partie.portefeuille(numero(acteur)).id
    assert any(
        e.reason == raison.SALE_TAX
        and e.amount == int(montant)
        and e.debit_account_id == portefeuille
        and e.credit_account_id == 2
        for e in partie.ecritures()
    )


@then(parsers.re(r"le portefeuille de (?P<acteur>actor_\d+) vaut (?P<montant>\d+)"))
def portefeuille_vaut(partie: Partie, acteur: str, montant: str) -> None:
    assert partie.portefeuille(numero(acteur)).balance == int(montant)


@then(
    parsers.re(
        r"le vaisseau au plus petit tirage à clé reçoit (?P<a>\d+) unités de (?P<ore>ore_[a-z]) "
        r"et l'autre (?P<b>\d+)"
    )
)
def departage(partie: Partie, a: str, ore: str, b: str) -> None:
    keyed_random = m("fourx.core.keyed_random")
    tick = partie.initial.tick + 1
    ordre = sorted(
        (keyed_random.keyed_draw(GRAINE, tick, v.id, "minage"), v.id) for v in partie.etat.ships
    )
    premier, second = (partie.vaisseau(f"ship_{i}") for _, i in ordre)
    assert premier.cargo[minerai(ore) - 1] == int(a)
    assert second.cargo[minerai(ore) - 1] == int(b)
    # Une graine qui donne l'ordre inverse : le résultat doit s'inverser aussi, pour qu'un
    # classement par identifiant, sans tirage, ne puisse pas passer ce scénario.
    step = m("fourx.core.step")
    ids = [i for _, i in ordre]
    inverse = next(
        g
        for g in range(2, 10_000)
        if [i for _, i in sorted((keyed_random.keyed_draw(g, tick, v, "minage"), v) for v in ids)]
        == ids[::-1]
    )
    etat, _ = step.step(partie.initial, partie.journal[0], inverse, partie.tunables)
    recus = {v.id: v.cargo[minerai(ore) - 1] for v in etat.ships}
    assert recus[ids[-1]] == int(a)
    assert recus[ids[0]] == int(b)


@then("la même partie rejouée donne les mêmes empreintes")
def rejouee(partie: Partie) -> None:
    step = m("fourx.core.step")
    fingerprints = m("fourx.core.fingerprints")
    etat = partie.initial
    for ordres in partie.journal:
        etat, _ = step.step(etat, ordres, GRAINE, partie.tunables)
    assert fingerprints.fingerprints(etat) == fingerprints.fingerprints(partie.etat)


def resultat(partie: Partie, acteur: str, num: str) -> Any:
    trouves = [
        r
        for r in partie.resultats
        if r.order_id.actor_id == numero(acteur) and r.order_id.number == int(num)
    ]
    assert len(trouves) == 1, trouves
    return trouves[0]


@then(parsers.re(r"l'ordre numéro (?P<num>\d+) de (?P<acteur>actor_\d+) est accepté"))
def ordre_accepte(partie: Partie, num: str, acteur: str) -> None:
    r = resultat(partie, acteur, num)
    assert r.accepted and r.refusal is None


@then(
    parsers.re(
        r"l'ordre numéro (?P<num>\d+) de (?P<acteur>actor_\d+) "
        r"est refusé avec le code (?P<code>[A-Z_]+)"
    )
)
def ordre_refuse(partie: Partie, num: str, acteur: str, code: str) -> None:
    refusal = m("fourx.schema.results").RefusalCode
    r = resultat(partie, acteur, num)
    assert not r.accepted
    assert r.refusal == refusal[code]
