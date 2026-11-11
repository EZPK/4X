"""Tests du client Textual par son pilote de test (docs/designs/niveau-2-m1-noyau.md, Technical
Plan, point 7 ; plan détaillé, point 23)."""

import asyncio
from collections.abc import Awaitable, Callable

from textual.pilot import Pilot
from textual.widgets import RichLog, Static

from fourx.clients.textual_app import FourxApp, carte, etat, historique
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Event, MiningEnded, Sale
from fourx.schema.ids import OrderId
from fourx.schema.observation import Observation
from fourx.schema.orders import Command, Mine, Move, OrderCategory, Sell
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate
from fourx.schema.results import OrderResult, RefusalCode
from fourx.schema.visibility import Visibility
from tests.aide_observation import ACTEUR, navire, observation


class ConnexionFactice:
    """Point de connexion de test : garde les messages soumis, rend les mises à jour en file."""

    def __init__(self) -> None:
        self.soumis: list[SubmitOrders] = []
        self.file: asyncio.Queue[TickUpdate] = asyncio.Queue()

    def submit(self, message: SubmitOrders) -> None:
        self.soumis.append(message)

    async def next_update(self) -> TickUpdate:
        return await self.file.get()


def evenement(payload: Sale | MiningEnded) -> Event:
    return Event(
        tick=7,
        seq=0,
        event_schema_version=0,
        rules_version="rules-0+abc",
        actor_id=ACTEUR,
        actor_kind=ActorKind.HUMAN,
        policy_id=None,
        policy_version=None,
        causation_id=None,
        visibility=Visibility.PRIVATE,
        payload=payload,
    )


def resultat(numero: int, refus: RefusalCode | None, texte: str) -> OrderResult:
    return OrderResult(
        recipient_actor_id=ACTEUR,
        order_id=OrderId(actor_id=ACTEUR, tick=7, number=numero),
        accepted=refus is None,
        refusal=refus,
        text=texte,
        budget_left=9,
    )


def texte(app: FourxApp, ident: str) -> str:
    return str(app.query_one(ident, Static).content)


def commandes(connexion: ConnexionFactice) -> list[list[Command]]:
    return [[o.command for o in m.orders] for m in connexion.soumis]


Scenario = Callable[[FourxApp, Pilot[None]], Awaitable[None]]


async def demarrer(obs: Observation, scenario: Scenario) -> ConnexionFactice:
    connexion = ConnexionFactice()
    app = FourxApp(connexion, ACTEUR)
    async with app.run_test() as pilot:
        await connexion.file.put(TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs))
        await pilot.pause()
        await scenario(app, pilot)
    return connexion


def test_affichage_d_une_mise_a_jour() -> None:
    obs = observation(
        (navire(system=2, cargo=(30, 0)),),
        solde=1234,
        evenements=(
            evenement(Sale(ship_id=1, ore_id=1, quantity=30, price=10, payment=270, tax=30)),
        ),
        resultats=(resultat(3, RefusalCode.CARGO_FULL, "cargaison pleine"),),
    )

    async def scenario(app: FourxApp, pilot: Pilot[None]) -> None:
        assert app.observation == obs
        assert "Portefeuille : 1234" in texte(app, "#etat")
        assert "[2] system_2   @" in texte(app, "#carte")
        lignes = [ligne.text for ligne in app.query_one("#historique", RichLog).lines]
        assert any("ordre 3 : refusé (cargaison pleine)" in ligne for ligne in lignes)
        assert any("vente : 30 ore_a à 10, payé 270, taxe 30" in ligne for ligne in lignes)

    assert asyncio.run(demarrer(obs, scenario)).soumis == []


def test_ordres_au_clavier() -> None:
    obs = observation((navire(system=1, cargo=(30, 70)),))

    async def scenario(app: FourxApp, pilot: Pilot[None]) -> None:
        await pilot.press("d", "3")
        await pilot.press("m", "b")
        await pilot.press("v")
        # Une touche sans commande en attente n'envoie rien.
        await pilot.press("3")
        await pilot.pause()

    connexion = asyncio.run(demarrer(obs, scenario))
    assert commandes(connexion) == [
        [Move(ship_id=1, target_system_id=3)],
        [Mine(ship_id=1, ore_id=2)],
        [Sell(ship_id=1, ore_id=1, quantity=30), Sell(ship_id=1, ore_id=2, quantity=70)],
    ]
    ordres = [o for m in connexion.soumis for o in m.orders]
    assert [o.number for o in ordres] == [1, 2, 3, 4]
    assert all(o.actor_id == ACTEUR and o.category is OrderCategory.PLAYER for o in ordres)
    assert all(o.policy_id is None for o in ordres)
    assert all(m.protocol_version == PROTOCOL_VERSION for m in connexion.soumis)


def test_aucun_ordre_avant_le_premier_tick() -> None:
    async def jouer() -> ConnexionFactice:
        connexion = ConnexionFactice()
        app = FourxApp(connexion, ACTEUR)
        async with app.run_test() as pilot:
            assert texte(app, "#carte") == "En attente du premier tick…"
            await pilot.press("d", "2", "v")
            await pilot.pause()
        return connexion

    assert asyncio.run(jouer()).soumis == []


def test_vendre_cargaison_vide_n_envoie_rien() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None]) -> None:
        await pilot.press("v")
        await pilot.pause()

    assert asyncio.run(demarrer(observation((navire(),)), scenario)).soumis == []


def test_fonctions_d_affichage() -> None:
    obs = observation(
        (navire(system=2, activity=Activity.EN_ROUTE, route=(3,), cargo=(0, 40)),),
        tick=12,
        evenements=(evenement(MiningEnded(ship_id=1, quantity=40)),),
        resultats=(resultat(1, None, "accepté"),),
    )
    assert carte(obs).splitlines() == [
        "[1] system_1        station",
        "[2] system_2   @    gisement ore_a (20000)",
        "[3] system_3        gisement ore_b (20000)",
    ]
    assert etat(obs).splitlines() == [
        "Tick 12   Portefeuille : 0",
        "Vaisseau 1 : system_2, en route, route system_3",
        "Cargaison (40/100) : ore_a : 0, ore_b : 40",
        "Actions restantes : 10",
    ]
    assert historique(obs) == ["t12 ordre 1 : accepté", "t12 fin de minage : 40 unités"]
