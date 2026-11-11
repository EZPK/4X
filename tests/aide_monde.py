"""Aide aux tests du noyau : construction d'états explicites et avance de ticks."""

from fourx.core.ledger import Account, Ledger, ledger_vide
from fourx.core.state import Actor, Deposit, LastTick, Ship, State, Station, System
from fourx.core.step import step
from fourx.core.tunables import Tunables
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Event
from fourx.schema.ledger import AccountKind
from fourx.schema.orders import Command, Order, OrderCategory, SubmittedOrder
from fourx.schema.results import RefusalCode

GRAINE = 1
REGLAGES = Tunables(
    jump_ticks=5,
    mining_rate=10,
    cargo_capacity=100,
    ore_prices=(10, 15),
    tax_rate_bp=1000,
    deposit_stock=20000,
    regen_ticks=1000,
    budget_regen=1,
    budget_max=10,
)


def vaisseau(
    ident: int,
    owner: int,
    system: int,
    cargo: tuple[int, ...] = (0, 0),
    capacity: int = 100,
) -> Ship:
    return Ship(
        id=ident,
        owner_id=owner,
        system_id=system,
        capacity=capacity,
        activity=Activity.IDLE,
        route=(),
        ticks_to_next_jump=0,
        cargo=cargo,
        mining_ore_id=None,
        mined_since_start=0,
    )


def monde(
    vaisseaux: tuple[Ship, ...] = (),
    budgets: dict[int, int] | None = None,
    stocks: tuple[int, int] = (20000, 20000),
    reglages: Tunables = REGLAGES,
) -> State:
    """Station dans system_1, gisement de ore_a dans system_2, de ore_b dans system_3."""
    proprietaires = sorted({v.owner_id for v in vaisseaux} | set(budgets or {}))
    budgets = budgets or {}
    ledger = ledger_vide()
    comptes = ledger.accounts + tuple(
        Account(id=2 + a, kind=AccountKind.PERSONAL_WALLET, owner_id=a, balance=0)
        for a in proprietaires
    )
    return State(
        tick=0,
        systems=(
            System(id=1, neighbors=(2,)),
            System(id=2, neighbors=(1, 3)),
            System(id=3, neighbors=(2,)),
        ),
        deposits=(
            Deposit(id=1, system_id=2, ore_id=1, stock=stocks[0]),
            Deposit(id=2, system_id=3, ore_id=2, stock=stocks[1]),
        ),
        stations=(Station(id=1, system_id=1, ore_prices=reglages.ore_prices),),
        actors=tuple(
            Actor(id=a, kind=ActorKind.HUMAN, action_budget=budgets.get(a, reglages.budget_max))
            for a in proprietaires
        ),
        ships=tuple(sorted(vaisseaux, key=lambda v: v.id)),
        ledger=Ledger(
            accounts=comptes,
            tick_entries=(),
            issued_by_reason=ledger.issued_by_reason,
            destroyed_by_reason=ledger.destroyed_by_reason,
        ),
        last_tick=LastTick(events=(), results=()),
    )


def ordre(
    state: State,
    actor: int,
    number: int,
    commande: Command,
    sender: int | None = -1,
    category: OrderCategory = OrderCategory.PLAYER,
    refus: RefusalCode | None = None,
    policy_id: str | None = None,
) -> SubmittedOrder:
    """Un ordre soumis pour le prochain tick ; par défaut, envoyé par l'acteur lui-même."""
    return SubmittedOrder(
        tick=state.tick + 1,
        sender_actor_id=actor if sender == -1 else sender,
        order=Order(
            actor_id=actor,
            number=number,
            category=category,
            policy_id=policy_id,
            policy_version=None if policy_id is None else 1,
            command=commande,
        ),
        reception_refusal=refus,
    )


def avancer(
    state: State,
    ordres: tuple[SubmittedOrder, ...] = (),
    n: int = 1,
    reglages: Tunables = REGLAGES,
    graine: int = GRAINE,
) -> tuple[State, list[Event]]:
    """Joue n ticks ; les ordres entrent au premier. Renvoie l'état et tous les événements."""
    tous: list[Event] = []
    for i in range(n):
        state, evenements = step(state, ordres if i == 0 else (), graine, reglages)
        tous.extend(evenements)
    return state, tous
