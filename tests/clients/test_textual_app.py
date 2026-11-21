"""Tests de l'écran unique par le pilote de Textual, en 80 × 24 (docs/designs/niveau-2-m1-noyau.md,
Technical Plan, point 7 bis ; objectif 12 ; plan détaillé, point 23 quinquies).

Les observations sont fabriquées, à des ticks éloignés : la carte de tests/aide_observation.py
(chaîne system_1 – system_2 – system_3, S1 dans system_1, ore_a dans system_2, ore_b dans
system_3), et un monde généré de 12 systèmes pour la lisibilité de chaque état du vaisseau.
"""

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

import msgspec
import pytest
from textual.pilot import Pilot
from textual.widgets import Static

from fourx.clients.frames import (
    ATTENTE,
    destinations,
    deux_lignes,
    texte_alerte,
    texte_barre,
    texte_carte,
    texte_destinations,
    texte_historique,
    texte_stations,
    texte_vaisseau,
)
from fourx.clients.model import ClientModel
from fourx.clients.textual_app import AIDE, AIDE_DEV, AIDE_LISTE, QUITTER, FourxApp
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Arrived, Event, Payload
from fourx.schema.ids import OrderId
from fourx.schema.observation import Observation, OtherShipView, SystemView
from fourx.schema.orders import Command, Mine, Move, OrderCategory, Sell
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate
from fourx.schema.results import OrderResult, RefusalCode
from fourx.schema.visibility import Visibility
from fourx.server.game import Game
from fourx.server.tunables_loader import load_tunables
from tests.aide_observation import ACTEUR, navire, observation

TAILLE = (80, 24)


class ConnexionFactice:
    """Point de connexion de test : garde les messages soumis, rend les mises à jour en file."""

    def __init__(self) -> None:
        self.soumis: list[SubmitOrders] = []
        self.file: asyncio.Queue[TickUpdate] = asyncio.Queue()

    def submit(self, message: SubmitOrders) -> None:
        self.soumis.append(message)

    async def next_update(self) -> TickUpdate:
        return await self.file.get()


def mise_a_jour(obs: Observation) -> TickUpdate:
    return TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs)


def evenement(charge: Payload) -> Event:
    return Event(
        tick=840,
        seq=0,
        event_schema_version=0,
        rules_version="r",
        actor_id=ACTEUR,
        actor_kind=ActorKind.HUMAN,
        policy_id=None,
        policy_version=None,
        causation_id=None,
        visibility=Visibility.PRIVATE,
        payload=charge,
    )


def resultat(numero: int, refus: RefusalCode | None = None) -> OrderResult:
    return OrderResult(
        recipient_actor_id=ACTEUR,
        order_id=OrderId(actor_id=ACTEUR, tick=840, number=numero),
        accepted=refus is None,
        refusal=refus,
        text="texte de step",
        budget_left=9,
    )


def lire(app: FourxApp, ident: str) -> str:
    return str(app.query_one(ident, Static).content)


def commandes(connexion: ConnexionFactice) -> list[list[Command]]:
    return [[o.command for o in m.orders] for m in connexion.soumis]


Scenario = Callable[[FourxApp, Pilot[None], ConnexionFactice], Awaitable[None]]


async def piloter(
    obs: Observation | None,
    scenario: Scenario,
    set_speed: Callable[[int | None], None] | None = None,
) -> ConnexionFactice:
    connexion = ConnexionFactice()
    app = FourxApp(connexion, ACTEUR, set_speed)
    async with app.run_test(size=TAILLE) as pilot:
        if obs is not None:
            await connexion.file.put(mise_a_jour(obs))
        await pilot.pause()
        await scenario(app, pilot, connexion)
        await pilot.pause()
    return connexion


def jouer(
    obs: Observation | None,
    scenario: Scenario,
    set_speed: Callable[[int | None], None] | None = None,
) -> ConnexionFactice:
    return asyncio.run(piloter(obs, scenario, set_speed))


def a_tick(obs: Observation, tick: int) -> Observation:
    return msgspec.structs.replace(obs, tick=tick)


# --- Les touches du tableau


def test_d_ouvre_la_liste_des_destinations_et_entree_confirme() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("d")
        assert app.query_one("#destinations").display
        assert not app.query_one("#historique").display
        assert lire(app, "#destinations").startswith("system_1 : 0 sauts")
        assert AIDE_LISTE in lire(app, "#barre")
        await pilot.press("down", "down", "down", "up")
        assert lire(app, "#destinations").splitlines()[0] == (
            "system_2 : 1 saut, 5 ticks (≈ 15 s à 3 s)"
        )
        await pilot.press("enter")
        assert not app.query_one("#destinations").display
        assert app.query_one("#historique").display

    connexion = jouer(a_tick(observation((navire(system=1),)), 2400), scenario)
    assert commandes(connexion) == [[Move(ship_id=1, target_system_id=2)]]
    ordre = connexion.soumis[0].orders[0]
    assert ordre.number == 1 and ordre.actor_id == ACTEUR
    assert ordre.category is OrderCategory.PLAYER


def test_echap_annule_la_liste_et_les_bornes_de_la_liste() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("d", "up", "up")
        assert "> [1] system_1" in lire(app, "#destinations")
        await pilot.press("down", "down", "down", "down")
        assert "> [3] system_3" in lire(app, "#destinations")
        await pilot.press("x")
        assert AIDE_LISTE in lire(app, "#barre")
        await pilot.press("escape")
        assert not app.query_one("#destinations").display

    assert jouer(observation((navire(system=1),)), scenario).soumis == []


def test_m_avec_un_gisement_demande_confirmation() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("m")
        assert "miner ore_b dans system_3 ? Entrée confirmer · Échap annuler" in lire(app, "#barre")
        await pilot.press("x")
        assert "Entrée confirmer le minage · Échap annuler" in lire(app, "#barre")
        await pilot.press("escape", "m", "enter")

    connexion = jouer(observation((navire(system=3),)), scenario)
    assert commandes(connexion) == [[Mine(ship_id=1, ore_id=2)]]


def test_m_sans_gisement_choisit_le_minerai() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("m")
        assert "pas de gisement ici : quel minerai ? a ou b (Échap annule)" in lire(app, "#barre")
        await pilot.press("x")
        assert "quel minerai ? a ou b (Échap annule)" in lire(app, "#barre")
        await pilot.press("a", "m", "b", "m", "escape")

    connexion = jouer(observation((navire(system=1),)), scenario)
    assert commandes(connexion) == [[Mine(ship_id=1, ore_id=1)], [Mine(ship_id=1, ore_id=2)]]


def test_v_vend_toute_la_cargaison_une_vente_apres_l_autre() -> None:
    plein = observation((navire(system=1, cargo=(30, 70)),), tick=12000)

    async def scenario(app: FourxApp, pilot: Pilot[None], connexion: ConnexionFactice) -> None:
        await pilot.press("v")
        assert "ordre envoyé : vendre 70 ore_b" in lire(app, "#vaisseau")
        vendu = observation(
            (navire(system=1, cargo=(30, 0)),), tick=12001, resultats=(resultat(1),)
        )
        await connexion.file.put(mise_a_jour(vendu))
        await pilot.pause()
        assert "ordre envoyé : vendre 30 ore_a" in lire(app, "#vaisseau")

    connexion = jouer(plein, scenario)
    assert commandes(connexion) == [
        [Sell(ship_id=1, ore_id=2, quantity=70)],
        [Sell(ship_id=1, ore_id=1, quantity=30)],
    ]


def test_v_cargaison_vide() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("v")
        assert "cargaison vide : rien à vendre" in lire(app, "#barre")

    assert jouer(observation((navire(system=1),)), scenario).soumis == []


def test_q_demande_confirmation_puis_quitte() -> None:
    sorties: list[bool] = []

    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("q")
        assert QUITTER in lire(app, "#barre")
        await pilot.press("x")
        assert QUITTER in lire(app, "#barre")
        await pilot.press("escape")
        assert QUITTER not in lire(app, "#barre")
        sorties.append(app.is_running)
        await pilot.press("q", "enter")
        await pilot.pause()
        sorties.append(app.is_running)

    jouer(observation((navire(system=1),)), scenario)
    assert sorties == [True, False]


def test_quitter_avant_le_premier_tick() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert lire(app, "#vaisseau") == ATTENTE
        await pilot.press("d", "m", "v")
        assert "en attente du premier tick" in lire(app, "#barre")
        await pilot.press("q", "enter")

    assert jouer(None, scenario).soumis == []


def test_entree_acquitte_l_alerte_sans_rien_confirmer() -> None:
    arrive = observation(
        (navire(system=3),), tick=840, evenements=(evenement(Arrived(ship_id=1, system_id=3)),)
    )

    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert app.query_one("#alerte").display
        assert lire(app, "#alerte") == "t840 arrivée : system_3 · Entrée : acquitter"
        await pilot.press("m", "enter")
        assert not app.query_one("#alerte").display
        assert "t840 arrivée : system_3" in lire(app, "#historique")
        await pilot.press("enter")

    connexion = jouer(arrive, scenario)
    assert commandes(connexion) == [[Mine(ship_id=1, ore_id=2)]]


def test_touche_sans_effet_ligne_d_aide() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("p")
        assert AIDE in lire(app, "#barre") and "dev" not in lire(app, "#barre")
        await pilot.press("space", "a", "r")
        assert AIDE in lire(app, "#barre")

    assert jouer(observation((navire(system=1),)), scenario).soumis == []


def test_un_refus_traduit_dans_l_historique() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], connexion: ConnexionFactice) -> None:
        await pilot.press("v")
        refuse = observation(
            (navire(system=3, cargo=(0, 40)),),
            tick=5000,
            resultats=(resultat(1, RefusalCode.NOT_AT_STATION),),
        )
        await connexion.file.put(mise_a_jour(refuse))
        await pilot.pause()
        assert (
            "t5000 ordre « vendre 40 ore_b » : refusé : pas de station ici ; la plus proche est "
            "S1, dans system_1 (2 sauts)"
        ) in lire(app, "#historique").replace("\n", " ")
        assert "ordre envoyé : aucun" in lire(app, "#vaisseau")

    jouer(observation((navire(system=3, cargo=(0, 40)),)), scenario)


# --- Mode développement


def test_vitesse_en_mode_developpement() -> None:
    appels: list[int | None] = []

    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert "dev ×1" in lire(app, "#barre")
        await pilot.press("r")
        assert "déjà au palier le plus lent" in lire(app, "#barre")
        await pilot.press("a", "a")
        assert "dev ×100" in lire(app, "#barre")
        await pilot.press("a")
        assert "déjà au palier le plus rapide" in lire(app, "#barre")
        await pilot.press("r", "p")
        assert "dev pause" in lire(app, "#barre")
        await pilot.press("r")
        assert "dev pause" in lire(app, "#barre")
        await pilot.press("p")
        assert "dev ×1" in lire(app, "#barre")
        await pilot.press("x")
        assert AIDE_DEV in lire(app, "#barre")

    jouer(observation((navire(system=1),)), scenario, appels.append)
    assert appels == [10, 100, 10, None, 1]


def test_avancer_jusqu_a_la_prochaine_alerte() -> None:
    appels: list[int | None] = []
    en_route = observation((navire(system=2, activity=Activity.EN_ROUTE, route=(3,)),), tick=900)

    async def scenario(app: FourxApp, pilot: Pilot[None], connexion: ConnexionFactice) -> None:
        await pilot.press("space")
        assert "dev ×100 jusqu'à l'alerte" in lire(app, "#barre")
        arrive = observation(
            (navire(system=3),), tick=1300, evenements=(evenement(Arrived(ship_id=1, system_id=3)),)
        )
        await connexion.file.put(mise_a_jour(arrive))
        await pilot.pause()
        assert "dev ×1" in lire(app, "#barre")
        await pilot.press("space")
        assert "acquittez d'abord l'alerte (Entrée)" in lire(app, "#barre")
        await pilot.press("enter", "space", "r")
        assert "dev ×10" in lire(app, "#barre")
        await pilot.press("space", "a")
        assert "dev ×100" in lire(app, "#barre")
        assert "jusqu'à l'alerte" not in lire(app, "#barre")
        await pilot.press("p", "space")
        assert "dev ×100 jusqu'à l'alerte" in lire(app, "#barre")
        await pilot.press("p")
        assert "dev pause" in lire(app, "#barre")

    jouer(en_route, scenario, appels.append)
    assert appels == [100, 1, 100, 10, 100, 100, None, 100, None]


# --- Chaque état du vaisseau, sur un monde de 12 systèmes (objectif 12)


@pytest.fixture(scope="module")
def monde_12(tmp_path_factory: pytest.TempPathFactory) -> Observation:
    reglages = msgspec.structs.replace(load_tunables(), systems_min=12, systems_max=12)
    partie = Game(tmp_path_factory.mktemp("runs"), world_seed=1, tunables=reglages)
    ident = partie.create_character(ActorKind.HUMAN)
    modele = ClientModel(ident)
    partie.attach(ident, modele)
    partie.advance(1)
    partie.close()
    assert modele.observation is not None
    return msgspec.structs.replace(modele.observation, actor_id=ACTEUR)


def vaisseau_12(obs: Observation, **champs: object) -> Observation:
    ancien = obs.own_ships[0]
    return msgspec.structs.replace(
        obs, own_ships=(msgspec.structs.replace(ancien, owner_id=ACTEUR, **champs),)
    )


@pytest.mark.parametrize("etat", ["arrêt", "route", "minage"])
def test_chaque_etat_du_vaisseau_se_lit_dans_son_cadre(monde_12: Observation, etat: str) -> None:
    depart = monde_12.own_ships[0].system_id
    gisement = next(d for d in monde_12.deposits if d.system_id != depart)
    if etat == "arrêt":
        obs = vaisseau_12(monde_12)
    elif etat == "route":
        obs = vaisseau_12(
            monde_12, activity=Activity.EN_ROUTE, route=(gisement.system_id,), ticks_to_next_jump=62
        )
    else:
        obs = vaisseau_12(
            monde_12,
            system_id=gisement.system_id,
            activity=Activity.MINING,
            mining_ore_id=gisement.ore_id,
            cargo=(38, 0) if gisement.ore_id == 1 else (0, 38),
        )
    obs = a_tick(obs, 7840)

    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("d", "enter")
        vaisseau = lire(app, "#vaisseau")
        navire_ = obs.own_ships[0]
        assert f"system_{navire_.system_id}" in vaisseau
        assert {"arrêt": "à l'arrêt", "route": "en route", "minage": "en minage"}[etat] in vaisseau
        if etat == "route":
            assert f"vers system_{gisement.system_id}" in vaisseau
            assert "arrivée dans 62 ticks" in vaisseau
        if etat == "minage":
            taux = obs.public_tunables.mining_rate
            assert f"fin dans {-(-62 // taux)} ticks" in vaisseau  # 62 unités libres
        assert "ordre envoyé : déplacer vers system_" in vaisseau
        carte = lire(app, "#carte-texte")
        for s in obs.systems:
            assert f"[{s.id}]" in carte
        stations = lire(app, "#stations")
        for st in obs.stations:
            assert (
                f"S{st.id} sys {st.system_id}  a {st.ore_prices[0]}  b {st.ore_prices[1]}"
                in stations
            )
        assert "Tick 7840" in lire(app, "#barre")

    jouer(obs, scenario)


# --- Les textes des cadres


def test_texte_carte_et_ligne_des_vaisseaux() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_carte(modele) == ATTENTE
    autres = (
        OtherShipView(id=7, owner_id=2, system_id=3, capacity=100),
        OtherShipView(id=5, owner_id=3, system_id=2, capacity=100),
    )
    obs = msgspec.structs.replace(observation((navire(system=2),)), other_ships=autres)
    modele.on_update(mise_a_jour(obs))
    assert texte_carte(modele).splitlines() == [
        "[1]S1───[2]a────[3]b",
        "",
        "@ joueur : [2]   o vaisseaux proches : [2] [3]",
    ]
    seul = ClientModel(ACTEUR)
    seul.on_update(mise_a_jour(observation(())))
    assert texte_carte(seul).splitlines()[-1] == "@ joueur : aucun   o vaisseaux proches : aucun"


def test_texte_vaisseau_de_chaque_etat() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_vaisseau(modele) == ATTENTE
    modele.on_update(mise_a_jour(observation((navire(system=1, cargo=(30, 70)),))))
    assert texte_vaisseau(modele).splitlines() == [
        "system_1  à l'arrêt",
        "cargaison 100/100",
        "ore_a 30  ore_b 70",
        "ordre envoyé : aucun",
    ]
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    modele.on_update(mise_a_jour(observation((en_route,))))
    modele.send(Mine(ship_id=1, ore_id=2))
    modele.send(Move(ship_id=1, target_system_id=1))
    assert texte_vaisseau(modele).splitlines() == [
        "system_1  en route",
        "vers system_3",
        "arrivée dans 7 ticks",
        "(≈ 21 s à 3 s)",
        "cargaison 0/100",
        "ore_a 0  ore_b 0",
        "ordre envoyé : miner ore_b; déplacer vers system_1",
    ]
    en_minage = msgspec.structs.replace(
        navire(system=3, activity=Activity.MINING, cargo=(0, 38)), mining_ore_id=2
    )
    modele.on_update(mise_a_jour(observation((en_minage,))))
    assert texte_vaisseau(modele).splitlines()[:4] == [
        "system_3  en minage",
        "mine ore_b",
        "fin dans 7 ticks",
        "(≈ 21 s à 3 s)",
    ]


def test_texte_stations_historique_et_alerte() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_stations(modele) == ATTENTE
    assert texte_alerte(modele) == ""
    for systeme, tick in ((2, 840), (3, 1240)):
        obs = observation(
            (navire(system=systeme),),
            tick=tick,
            evenements=(evenement(Arrived(ship_id=1, system_id=systeme)),),
        )
        modele.on_update(mise_a_jour(obs))
    assert texte_stations(modele) == "S1 sys 1  a 10  b 15"
    assert texte_alerte(modele) == "t840 arrivée : system_2 · Entrée : acquitter (1 de plus)"
    assert texte_historique(modele, 1) == "t1240 arrivée : system_3"
    assert texte_historique(modele, 0) == "t840 arrivée : system_2\nt1240 arrivée : system_3"


def test_destinations_et_fenetre_de_la_liste() -> None:
    obs = observation((navire(system=1),), stocks=(20000, None))
    assert destinations(obs, 1) == [
        (1, "[1] system_1  0 sauts  S1"),
        (2, "[2] system_2  1 saut  ore_a (20000)"),
        (3, "[3] system_3  2 sauts  ore_b (?)"),
    ]
    modele = ClientModel(ACTEUR)
    assert texte_destinations(modele, 0, 5) == ATTENTE
    modele.on_update(mise_a_jour(obs))
    assert texte_destinations(modele, 2, 3).splitlines() == [
        "system_3 : 2 sauts, 10 ticks (≈ 30 s à 3 s)",
        "  [2] system_2  1 saut  ore_a (20000)",
        "> [3] system_3  2 sauts  ore_b (?)",
    ]
    assert len(texte_destinations(modele, 0, 0).splitlines()) == 4
    isole = msgspec.structs.replace(
        obs,
        systems=(
            SystemView(id=1, neighbors=(2,)),
            SystemView(id=2, neighbors=(1,)),
            SystemView(id=3, neighbors=()),
        ),
    )
    modele.on_update(mise_a_jour(isole))
    assert texte_destinations(modele, 2, 0).splitlines()[0] == "system_3 : inaccessible"
    assert destinations(isole, 1)[2] == (3, "[3] system_3  ?  ore_b (?)")


def test_texte_barre() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_barre(modele, None, "") == " Tick — │ Solde — │ d m v q\n "
    modele.on_update(mise_a_jour(observation((navire(),), tick=840, solde=1500)))
    assert texte_barre(modele, "×10", "aide") == (
        " Tick 840 │ Solde 1500 │ dev ×10 │ d m v q · dev : p a r ␣\n aide"
    )


def test_deux_lignes() -> None:
    assert deux_lignes("fin dans", 62) == ["fin dans 62 ticks", "(≈ 3 min 6 s à 3 s)"]


def test_rien_de_l_application_n_importe_le_serveur() -> None:
    """Le client reçoit une simple fonction de vitesse, ou rien (Technical Plan, point 6)."""
    source = Path(__file__).resolve().parents[2] / "src" / "fourx" / "clients" / "textual_app.py"
    assert "fourx.server" not in source.read_text(encoding="utf-8")
