"""Tests de l'écran rétro par le pilote de Textual, en 120 × 36 (docs/designs/niveau-2-m1-noyau.md,
Technical Plan, points 7 bis et 7 ter ; objectif 12 ; plan détaillé, points 23 quinquies et
23 nonies). L'aide s'ouvre au lancement : les tests la ferment avant d'agir, sauf ceux de l'aide.

Les observations sont fabriquées, à des ticks éloignés : la carte de tests/aide_observation.py
(chaîne system_1 – system_2 – system_3, S1 dans system_1, ore_a dans system_2, ore_b dans
system_3), et un monde généré de 12 systèmes pour la lisibilité de chaque état du vaisseau.
"""

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

import msgspec
import pytest
from textual import events
from textual.pilot import Pilot
from textual.widgets import Static

from fourx.clients.frames import (
    ATTENTE,
    MapCanvas,
    barre,
    destinations,
    texte_barre,
    texte_bulle,
    texte_destinations,
    texte_etape,
    texte_historique,
    texte_stations,
    texte_touches,
    texte_vaisseau,
)
from fourx.clients.map_view import ZOOMS, anchor, ship_position, to_pixels
from fourx.clients.model import ClientModel
from fourx.clients.palette import PALETTE
from fourx.clients.textual_app import (
    AIDE,
    AIDE_DEV,
    AIDE_LISTE,
    AIDE_OUVERTE,
    QUITTER,
    FourxApp,
    message_petite_fenetre,
)
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Arrived, Event, Payload, Sale
from fourx.schema.ids import OrderId
from fourx.schema.observation import Observation, StationView, SystemView
from fourx.schema.orders import Command, Mine, Move, OrderCategory, Sell
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate
from fourx.schema.results import OrderResult, RefusalCode
from fourx.schema.visibility import Visibility
from fourx.server.game import Game
from fourx.server.tunables_loader import load_tunables
from tests.aide_observation import ACTEUR, navire, observation

TAILLE = (120, 36)


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


def place(app: FourxApp, ident: str) -> tuple[int, int, int, int]:
    region = app.query_one(ident).region
    return (region.x, region.y, region.width, region.height)


def commandes(connexion: ConnexionFactice) -> list[list[Command]]:
    return [[o.command for o in m.orders] for m in connexion.soumis]


Scenario = Callable[[FourxApp, Pilot[None], ConnexionFactice], Awaitable[None]]


async def piloter(
    obs: Observation | None,
    scenario: Scenario,
    set_speed: Callable[[int | None], None] | None,
    taille: tuple[int, int],
    fermer_l_aide: bool,
) -> ConnexionFactice:
    connexion = ConnexionFactice()
    app = FourxApp(connexion, ACTEUR, set_speed)
    async with app.run_test(size=taille) as pilot:
        if obs is not None:
            await connexion.file.put(mise_a_jour(obs))
        await pilot.pause()
        if fermer_l_aide:
            await pilot.press("escape")
        await scenario(app, pilot, connexion)
        await pilot.pause()
    return connexion


def jouer(
    obs: Observation | None,
    scenario: Scenario,
    set_speed: Callable[[int | None], None] | None = None,
    taille: tuple[int, int] = TAILLE,
    fermer_l_aide: bool = True,
) -> ConnexionFactice:
    return asyncio.run(piloter(obs, scenario, set_speed, taille, fermer_l_aide))


def a_tick(obs: Observation, tick: int) -> Observation:
    return msgspec.structs.replace(obs, tick=tick)


# --- Les touches du tableau


def test_d_ouvre_la_liste_des_destinations_et_entree_confirme() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("d")
        assert app.query_one("#destinations").display
        assert not app.query_one("#stations").display
        # La prochaine étape conseille d'aller miner à system_2 : la liste s'ouvre sur sa ligne.
        assert lire(app, "#destinations").startswith("system_2 : 1 saut")
        assert AIDE_LISTE in lire(app, "#barre")
        await pilot.press("down", "down", "down", "up")
        assert lire(app, "#destinations").splitlines()[0] == (
            "system_2 : 1 saut, 5 ticks (≈ 15 s à 3 s)"
        )
        await pilot.press("enter")
        assert not app.query_one("#destinations").display
        assert app.query_one("#stations").display

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
        await pilot.press("y")
        assert AIDE_LISTE in lire(app, "#barre")
        await pilot.press("escape")
        assert not app.query_one("#destinations").display

    assert jouer(observation((navire(system=1),)), scenario).soumis == []


def test_m_avec_un_gisement_demande_confirmation() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("m")
        assert "miner ore_b dans system_3 ? Entrée confirmer · Échap annuler" in lire(app, "#barre")
        await pilot.press("y")
        assert "Entrée confirmer le minage · Échap annuler" in lire(app, "#barre")
        await pilot.press("escape", "m", "enter")

    connexion = jouer(observation((navire(system=3),)), scenario)
    assert commandes(connexion) == [[Mine(ship_id=1, ore_id=2)]]


def test_m_sans_gisement_choisit_le_minerai() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("m")
        assert "pas de gisement ici : quel minerai ? a ou b (Échap annule)" in lire(app, "#barre")
        await pilot.press("y")
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
        await pilot.press("y")
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
        assert lire(app, "#etape").splitlines() == [
            "arrivée : system_3",
            "Entrée : acquitter",
            "Touche : Entrée",
        ]
        await pilot.press("m", "enter")
        assert "arrivée" not in lire(app, "#etape")
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
        await pilot.press("y")
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
        canevas = app.query_one(MapCanvas)
        for s in obs.systems:
            colonne, ligne = anchor(canevas.vue, canevas.positions[s.id])
            pastille = canevas.grille[ligne][colonne].char + canevas.grille[ligne][colonne + 1].char
            # En route, le vaisseau est peint sur le lien, par-dessus une pastille s'il y passe.
            assert pastille == f"{s.id:>2}" or (etat == "route" and "▲" in pastille)
        stations = lire(app, "#stations-texte").replace("★", "")
        for st in obs.stations:
            assert (
                f"S{st.id} system_{st.system_id}  a {st.ore_prices[0]}  b {st.ore_prices[1]}"
                in stations
            )
        assert "Tick 7840" in lire(app, "#barre")

    jouer(obs, scenario)


# --- Les textes des cadres


def test_texte_vaisseau_de_chaque_etat() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_vaisseau(modele).plain == ATTENTE
    modele.on_update(mise_a_jour(observation((navire(system=1, cargo=(30, 70)),))))
    assert texte_vaisseau(modele).plain.splitlines() == [
        "system_1  à l'arrêt",
        "aucun trajet ni minage en cours",
        "cargaison : ore_a 30  ore_b 70",
        "ordre envoyé : aucun",
        "activité  ░░░░░░░░░░░░░░░░░░░░",
        "cargaison ████████████████████ 100/100",
    ]
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    modele.on_update(mise_a_jour(observation((en_route,))))
    modele.send(Mine(ship_id=1, ore_id=2))
    modele.send(Move(ship_id=1, target_system_id=1))
    assert texte_vaisseau(modele).plain.splitlines() == [
        "system_1  en route vers system_3",
        "arrivée dans 7 ticks (≈ 21 s à 3 s)",
        "cargaison : ore_a 0  ore_b 0",
        "ordre envoyé : miner ore_b ; déplacer vers system_1",
        "saut      ████████████░░░░░░░░",  # 3 ticks sur 5
        "cargaison ░░░░░░░░░░░░░░░░░░░░ 0/100",
    ]
    en_minage = msgspec.structs.replace(
        navire(system=3, activity=Activity.MINING, cargo=(0, 38)),
        mining_ore_id=2,
        mined_since_start=38,
    )
    modele.on_update(mise_a_jour(observation((en_minage,), stocks=(20000, 50))))
    assert texte_vaisseau(modele).plain.splitlines() == [
        "system_3  en minage de ore_b",
        "fin dans 5 ticks (≈ 15 s à 3 s)",
        "cargaison : ore_a 0  ore_b 38",
        "ordre envoyé : miner ore_b ; déplacer vers system_1",  # toujours sans résultat
        "minage    ████████░░░░░░░░░░░░",  # 38 sur 38 + 50 : le stock borne le reste
        "cargaison ███████░░░░░░░░░░░░░ 38/100",
    ]


def test_barre_de_progression() -> None:
    assert barre(0, 5) == "░" * 20
    assert barre(5, 5) == "█" * 20
    assert barre(1, 3) == "█" * 6 + "░" * 14
    assert barre(9, 5) == "█" * 20
    assert barre(0, 0) == "░" * 20


def test_texte_stations_meilleurs_prix_et_gisements() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_stations(modele).plain == ATTENTE
    modele.on_update(mise_a_jour(observation((navire(system=1),), stocks=(20000, None))))
    assert texte_stations(modele).plain.splitlines() == [
        "S1 system_1  a 10★  b 15★",
        "ore_a : system_2 (20000)",
        "ore_b : system_3 (?)",
    ]
    deux = msgspec.structs.replace(
        observation((navire(system=1),)),
        stations=(
            StationView(id=1, system_id=1, ore_prices=(10, 15)),
            StationView(id=2, system_id=3, ore_prices=(20, 15)),
        ),
    )
    modele.on_update(mise_a_jour(deux))
    lignes = texte_stations(modele).plain.splitlines()
    assert lignes[:2] == ["S1 system_1  a 10  b 15★", "S2 system_3  a 20★  b 15★"]


def test_texte_historique_les_quatre_dernieres_et_leurs_couleurs() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_historique(modele).plain == ""
    for tick in range(1, 6):
        obs = observation(
            (navire(system=2),),
            tick=tick,
            evenements=(evenement(Arrived(ship_id=1, system_id=2)),),
        )
        modele.on_update(mise_a_jour(obs))
    assert texte_historique(modele).plain.splitlines() == [
        f"t{tick} arrivée : system_2" for tick in range(2, 6)
    ]
    vente = evenement(Sale(ship_id=1, ore_id=2, quantity=10, price=15, payment=150, tax=15))
    modele.on_update(mise_a_jour(observation((navire(system=1),), tick=6, evenements=(vente,))))
    texte = texte_historique(modele, 1)
    assert texte.plain == "t6 vente : 10 ore_b à 15, paiement 150, taxe 15"
    etiquette = next(s for s in texte.spans if s.start == 0)
    assert PALETTE["succes"].lower() in str(etiquette.style).lower()


def test_texte_etape() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_etape(modele).plain == "En attente du premier tick"
    modele.on_update(mise_a_jour(observation((navire(system=1),))))
    assert texte_etape(modele).plain.splitlines() == [
        "Aller miner ore_a à system_2",
        "1 saut, 5 ticks (≈ 15 s à 3 s) ; cycle complet estimé : 20 ticks (≈ 1 min à 3 s)",
        "Touche : d",
    ]
    arrive = observation(
        (navire(system=3),), tick=840, evenements=(evenement(Arrived(ship_id=1, system_id=3)),)
    )
    modele.on_update(mise_a_jour(arrive))
    texte = texte_etape(modele)
    assert texte.plain.splitlines()[0] == "arrivée : system_3"
    assert PALETTE["vaisseau"].lower() in str(texte.style).lower()


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
    assert texte_barre(modele, None, "").plain == " Tick — │ Solde —\n "
    modele.on_update(mise_a_jour(observation((navire(),), tick=840, solde=1500)))
    assert texte_barre(modele, "×10", "aide").plain == (
        " Tick 840 (≈ 42 min à 3 s) │ Solde 1500 │ dev ×10\n aide"
    )


def test_texte_touches() -> None:
    assert texte_touches(None, False) == " d déplacer · m miner · v vendre · h aide · q quitter"
    assert texte_touches("destination", False) == " ↑↓ choisir · Entrée confirmer · Échap annuler"
    assert texte_touches("miner", False) == " Entrée confirmer · Échap annuler"
    assert texte_touches("quitter", False) == " Entrée confirmer · Échap annuler"
    assert texte_touches("minerai", False) == " a ou b : minerai · Échap annuler"
    assert texte_touches(None, True) == " ↑↓ défiler · Entrée, Échap ou h fermer"
    assert texte_touches("destination", True) == texte_touches(None, True)


# --- Disposition de l'écran (Technical Plan, point 7 ter)


def test_disposition_en_120_x_36() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert place(app, "#barre") == (0, 0, 120, 2)
        assert place(app, "#carte") == (0, 2, 72, 27)
        assert place(app, "#etape") == (73, 2, 47, 7)
        assert place(app, "#vaisseau") == (73, 9, 47, 8)
        assert place(app, "#stations") == (73, 17, 47, 12)
        assert place(app, "#historique") == (0, 29, 120, 6)
        assert place(app, "#touches") == (0, 35, 120, 1)
        assert lire(app, "#touches") == " d déplacer · m miner · v vendre · h aide · q quitter"
        await pilot.press("d")
        assert place(app, "#destinations") == (73, 17, 47, 12)
        assert lire(app, "#touches") == " ↑↓ choisir · Entrée confirmer · Échap annuler"

    jouer(observation((navire(system=1),)), scenario)


def test_disposition_en_100_x_30_la_carte_et_les_stations_retrecissent() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert place(app, "#carte") == (0, 2, 52, 21)
        assert place(app, "#etape") == (53, 2, 47, 7)
        assert place(app, "#vaisseau") == (53, 9, 47, 8)
        assert place(app, "#stations") == (53, 17, 47, 6)
        assert place(app, "#historique") == (0, 23, 100, 6)
        assert not app.query_one("#petite").display

    jouer(observation((navire(system=1),)), scenario, taille=(100, 30))


@pytest.mark.parametrize("taille", [(99, 30), (100, 29)])
def test_petite_fenetre_un_message_et_seule_q_agit(taille: tuple[int, int]) -> None:
    sorties: list[bool] = []

    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert app.query_one("#petite").display
        assert not app.query_one("#ecran").display
        assert not app.query_one("#aide").display
        assert lire(app, "#petite") == message_petite_fenetre(*taille)
        assert lire(app, "#petite") == (
            "Agrandis la fenêtre : 100 colonnes × 30 lignes au moins "
            f"(actuellement {taille[0]} × {taille[1]})."
        )
        await pilot.press("d", "enter", "m", "v")
        await pilot.press("q")
        assert QUITTER in lire(app, "#petite")
        await pilot.press("escape")
        assert QUITTER not in lire(app, "#petite")
        sorties.append(app.is_running)
        await pilot.press("q", "enter")
        await pilot.pause()
        sorties.append(app.is_running)

    connexion = jouer(observation((navire(system=1, cargo=(0, 50)),)), scenario, taille=taille)
    assert connexion.soumis == [] and sorties == [True, False]


def test_la_fenetre_agrandie_retrouve_l_ecran() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.resize_terminal(90, 25)
        await pilot.pause()
        assert app.query_one("#petite").display
        assert lire(app, "#petite") == message_petite_fenetre(90, 25)
        await pilot.resize_terminal(120, 36)
        await pilot.pause()
        assert not app.query_one("#petite").display
        assert app.query_one("#ecran").display

    jouer(observation((navire(system=1),)), scenario)


# --- L'aide (Technical Plan, point 7 ter)


def test_l_aide_s_ouvre_au_lancement_centree_avec_son_ombre() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert app.query_one("#aide").display and app.query_one("#ombre").display
        assert place(app, "#aide") == (15, 4, 90, 28)
        assert place(app, "#ombre") == (17, 5, 90, 28)
        texte = lire(app, "#aide-texte").splitlines()
        assert texte[0] == "COMMENT JOUER"
        assert texte[2].endswith("prend 10 ticks (≈ 30 s à 3 s).")
        assert texte[-1] == "Entrée, Échap ou h : fermer"
        assert lire(app, "#touches") == " ↑↓ défiler · Entrée, Échap ou h fermer"
        await pilot.press("escape")
        assert not app.query_one("#aide").display and not app.query_one("#ombre").display

    jouer(observation((navire(system=1),)), scenario, fermer_l_aide=False)


def test_l_aide_avant_le_premier_tick() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert "(connue au premier tick)" in lire(app, "#aide-texte")

    jouer(None, scenario, fermer_l_aide=False)


def test_les_touches_de_l_aide() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("d")
        assert AIDE_OUVERTE in lire(app, "#barre")
        assert app.saisie is None and app.aide_ouverte
        await pilot.press("up", "down", "down")
        assert AIDE_OUVERTE not in lire(app, "#barre") and app.aide_ouverte
        assert app.query_one("#aide").scroll_y == 2  # l'aide dépasse sa hauteur et défile
        await pilot.press("up")
        assert app.query_one("#aide").scroll_y == 1
        await pilot.press("h")
        assert not app.aide_ouverte
        await pilot.press("h")
        assert app.aide_ouverte
        assert app.query_one("#aide").scroll_y == 0  # rouverte en haut
        await pilot.press("enter")
        assert not app.aide_ouverte
        await pilot.press("d", "h")
        assert app.aide_ouverte and app.saisie is None
        assert not app.query_one("#destinations").display
        await pilot.press("q")
        assert not app.aide_ouverte and app.saisie == "quitter"
        assert QUITTER in lire(app, "#barre")
        await pilot.press("escape")
        assert app.saisie is None

    connexion = jouer(observation((navire(system=1),)), scenario, fermer_l_aide=False)
    assert connexion.soumis == []


def test_entree_ferme_l_aide_avant_l_alerte() -> None:
    arrive = observation(
        (navire(system=3),), tick=840, evenements=(evenement(Arrived(ship_id=1, system_id=3)),)
    )

    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("enter")
        assert not app.aide_ouverte
        assert len(app.model.alerts) == 1
        assert lire(app, "#etape").startswith("arrivée : system_3")
        await pilot.press("enter")
        assert len(app.model.alerts) == 0

    jouer(arrive, scenario, fermer_l_aide=False)


def test_les_touches_du_mode_developpement_restent_actives_dans_l_aide() -> None:
    appels: list[int | None] = []

    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert "Mode développement" in lire(app, "#aide-texte")
        await pilot.press("a", "p")
        assert app.aide_ouverte
        assert "dev pause" in lire(app, "#barre")

    jouer(observation((navire(system=1),)), scenario, appels.append, fermer_l_aide=False)
    assert appels == [10, None]


def test_le_cadre_prochaine_etape_suit_le_modele() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        assert lire(app, "#etape").splitlines()[0] == "Aller miner ore_a à system_2"
        await pilot.press("d", "enter")
        assert lire(app, "#etape").splitlines()[0] == "Ordre envoyé : déplacer vers system_2"

    jouer(observation((navire(system=1),)), scenario)


# --- La carte rétro (Technical Plan, point 7 ter, vue de la carte)


def souris(
    classe: type[events.MouseEvent], canevas: MapCanvas, x: int, y: int, bouton: int = 0
) -> events.MouseEvent:
    region = canevas.region
    return classe(canevas, x, y, 0, 0, bouton, False, False, False, region.x + x, region.y + y)


def test_d_ouvre_la_liste_sur_le_vaisseau_sans_conseil_de_deplacement() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        await pilot.press("d")  # conseil : miner ici, dans system_2
        assert lire(app, "#destinations").startswith("system_2 : 0 sauts")

    jouer(observation((navire(system=2),)), scenario)


def test_z_x_zooment_et_les_bornes_affichent_la_ligne_d_aide() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        canevas = app.query_one(MapCanvas)
        assert canevas.vue.zoom_index == 0 and canevas.vue.center == (0.5, 0.5)
        await pilot.press("x")
        assert AIDE in lire(app, "#barre") and canevas.vue.zoom_index == 0
        await pilot.press("z", "z")
        assert canevas.vue.zoom_index == 2 and canevas.vue.center == (0.5, 0.5)
        await pilot.press("z", "z")
        assert canevas.vue.zoom_index == len(ZOOMS) - 1
        await pilot.press("z")
        assert AIDE in lire(app, "#barre")
        await pilot.press("x")
        assert canevas.vue.zoom_index == len(ZOOMS) - 2

    jouer(observation((navire(system=1),)), scenario)


def test_les_fleches_deplacent_la_vue_et_c_la_recentre() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        canevas = app.query_one(MapCanvas)
        await pilot.press("z", "right", "down")
        echelle = 2 * canevas.vue.height * ZOOMS[1]
        assert canevas.vue.center == pytest.approx(
            (0.5 + (72 // 10) / echelle, 0.5 + 2 * (27 // 10) / echelle)
        )
        await pilot.press("left", "up")
        assert canevas.vue.center == pytest.approx((0.5, 0.5))
        await pilot.press("c")
        assert canevas.vue.center == ship_position(app.model, canevas.positions)

    jouer(observation((navire(system=1),)), scenario)


def test_dans_une_saisie_les_touches_de_la_carte_sont_sans_effet() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        canevas = app.query_one(MapCanvas)
        await pilot.press("d", "left", "z", "c")
        assert canevas.vue.zoom_index == 0 and canevas.vue.center == (0.5, 0.5)
        assert AIDE_LISTE in lire(app, "#barre")

    jouer(observation((navire(system=1),)), scenario)


def test_la_molette_zoome_autour_du_pointeur() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        canevas = app.query_one(MapCanvas)
        avant = canevas.vue
        canevas.post_message(souris(events.MouseScrollUp, canevas, 10, 5))
        await pilot.pause()
        apres = canevas.vue
        assert apres.zoom_index == 1
        # Le point sous la case (10, 5) y reste.
        point = (
            (10 - avant.width / 2) / (2 * avant.height) + avant.center[0],
            (11 - avant.height) / (2 * avant.height) + avant.center[1],
        )
        x, y = to_pixels(apres, point)
        assert (x, y) == pytest.approx((10, 11))
        canevas.post_message(souris(events.MouseScrollDown, canevas, 10, 5))
        await pilot.pause()
        assert canevas.vue.zoom_index == 0

    jouer(observation((navire(system=1),)), scenario)


def test_le_glisser_deplace_la_vue_sans_cliquer() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        canevas = app.query_one(MapCanvas)
        await pilot.press("z")
        depart = canevas.vue.center
        canevas.post_message(souris(events.MouseDown, canevas, 30, 10, bouton=1))
        canevas.post_message(souris(events.MouseMove, canevas, 34, 12, bouton=1))
        canevas.post_message(souris(events.MouseUp, canevas, 34, 12, bouton=1))
        await pilot.pause()
        echelle = 2 * canevas.vue.height * ZOOMS[1]
        assert canevas.vue.center == pytest.approx(
            (depart[0] - 4 / echelle, depart[1] - 4 / echelle)
        )
        assert app.saisie is None

    jouer(observation((navire(system=1),)), scenario)


def test_le_survol_montre_la_bulle_et_le_clic_ouvre_la_liste() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        canevas = app.query_one(MapCanvas)
        colonne, ligne = anchor(canevas.vue, canevas.positions[3])
        await pilot.hover(MapCanvas, offset=(colonne, ligne))
        await pilot.pause()
        bulle = app.query_one("#bulle")
        assert bulle.display
        assert lire(app, "#bulle") == texte_bulle(app.model, 3)
        assert lire(app, "#bulle").splitlines() == [
            "system_3",
            "gisement de ore_b, stock 20000",
            "2 sauts, 10 ticks (≈ 30 s à 3 s)",
        ]
        assert canevas.grille[ligne][colonne].bg == "accent"
        await pilot.click(MapCanvas, offset=(colonne + 1, ligne))
        assert app.saisie == "destination"
        assert lire(app, "#destinations").startswith("system_3 : 2 sauts")
        await pilot.press("escape")
        colonne, ligne = anchor(canevas.vue, canevas.positions[1])
        await pilot.click(MapCanvas, offset=(colonne, ligne))
        assert app.saisie is None
        assert "déjà dans system_1" in lire(app, "#barre")

    jouer(observation((navire(system=1),)), scenario)


def test_le_clic_est_ignore_pendant_l_aide_et_une_saisie() -> None:
    async def scenario(app: FourxApp, pilot: Pilot[None], _: ConnexionFactice) -> None:
        canevas = app.query_one(MapCanvas)
        colonne, ligne = anchor(canevas.vue, canevas.positions[3])
        canevas.post_message(MapCanvas.Clic(3))
        await pilot.pause()
        assert app.aide_ouverte and app.saisie is None
        await pilot.press("escape", "m")
        canevas.post_message(MapCanvas.Clic(3))
        await pilot.pause()
        assert app.saisie == "minerai"
        assert (colonne, ligne) == anchor(canevas.vue, canevas.positions[3])

    jouer(observation((navire(system=1),)), scenario, fermer_l_aide=False)


def test_texte_bulle() -> None:
    modele = ClientModel(ACTEUR)
    assert texte_bulle(modele, 1) == ATTENTE
    modele.on_update(mise_a_jour(observation((navire(system=1),), stocks=(20000, None))))
    assert texte_bulle(modele, 1).splitlines() == ["system_1", "S1 (a 10, b 15)", "déjà ici"]
    assert texte_bulle(modele, 3).splitlines() == [
        "system_3",
        "gisement de ore_b, stock ?",
        "2 sauts, 10 ticks (≈ 30 s à 3 s)",
    ]
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    modele.on_update(mise_a_jour(observation((en_route,))))
    assert texte_bulle(modele, 1).splitlines()[-1] == "1 saut, 7 ticks (≈ 21 s à 3 s)"
    assert texte_bulle(modele, 2).splitlines()[-1] == "0 sauts, 2 ticks (≈ 6 s à 3 s)"
    assert texte_bulle(modele, 3).splitlines()[-1] == "1 saut, 7 ticks (≈ 21 s à 3 s)"


def test_rien_de_l_application_n_importe_le_serveur() -> None:
    """Le client reçoit une simple fonction de vitesse, ou rien (Technical Plan, point 6)."""
    source = Path(__file__).resolve().parents[2] / "src" / "fourx" / "clients" / "textual_app.py"
    assert "fourx.server" not in source.read_text(encoding="utf-8")
