"""Tests de fourx.clients.model (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 7 bis
et 13 ; plan détaillé, point 23 quinquies).

Deux parties : des observations fabriquées (tests/aide_observation.py : chaîne system_1 –
system_2 – system_3, station S1 dans system_1, ore_a dans system_2, ore_b dans system_3), puis le
modèle joué comme client synchrone par `Game.advance`, sur un monde généré.
"""

from pathlib import Path

import msgspec
import pytest

from fourx.clients.model import (
    Alert,
    AlertKind,
    ClientModel,
    HistoryEntry,
    HistoryKind,
    decrire,
)
from fourx.policies.geometry import distances
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import Arrived, Event, MiningEnded, MiningStarted, Payload, Sale
from fourx.schema.ids import OrderId
from fourx.schema.observation import Observation
from fourx.schema.orders import CreateCharacter, Mine, Move, OrderCategory, Sell
from fourx.schema.protocol import PROTOCOL_VERSION, SubmitOrders, TickUpdate
from fourx.schema.results import OrderResult, RefusalCode
from fourx.schema.visibility import Visibility
from fourx.server.game import Game
from fourx.server.tunables_loader import load_tunables
from tests.aide_observation import ACTEUR, navire, observation


def mise_a_jour(obs: Observation) -> TickUpdate:
    return TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs)


def resultat(numero: int, refus: RefusalCode | None = None) -> OrderResult:
    return OrderResult(
        recipient_actor_id=ACTEUR,
        order_id=OrderId(actor_id=ACTEUR, tick=7, number=numero),
        accepted=refus is None,
        refusal=refus,
        text="texte de step",
        budget_left=9,
    )


def evenement(charge: Payload, cause: OrderId | None = None, acteur: int = ACTEUR) -> Event:
    return Event(
        tick=7,
        seq=0,
        event_schema_version=0,
        rules_version="r",
        actor_id=acteur,
        actor_kind=ActorKind.HUMAN,
        policy_id=None,
        policy_version=None,
        causation_id=cause,
        visibility=Visibility.PRIVATE,
        payload=charge,
    )


def commandes(message: SubmitOrders | None) -> list[object]:
    assert message is not None
    return [o.command for o in message.orders]


# --- Ordres envoyés et numéros


def test_send_numerote_et_garde_l_ordre_jusqu_a_son_resultat() -> None:
    modele = ClientModel(ACTEUR)
    premier = modele.send(Move(ship_id=1, target_system_id=3))
    second = modele.send(Mine(ship_id=1, ore_id=1))
    ordres = [o for m in (premier, second) for o in m.orders]
    assert [o.number for o in ordres] == [1, 2]
    assert all(o.actor_id == ACTEUR and o.category is OrderCategory.PLAYER for o in ordres)
    assert all(o.policy_id is None and o.policy_version is None for o in ordres)
    assert premier.protocol_version == PROTOCOL_VERSION
    assert modele.pending == (
        (1, Move(ship_id=1, target_system_id=3)),
        (2, Mine(ship_id=1, ore_id=1)),
    )
    obs = observation((navire(system=1),), resultats=(resultat(2), resultat(9)))
    assert modele.on_update(mise_a_jour(obs)) is None
    assert list(modele.pending) == [(1, Move(ship_id=1, target_system_id=3))]
    assert modele.history == (
        HistoryEntry(7, HistoryKind.ORDER, "ordre « miner ore_a » : accepté"),
    )
    assert modele.observation == obs


def test_un_refus_est_traduit_dans_l_historique() -> None:
    modele = ClientModel(ACTEUR)
    modele.send(Mine(ship_id=1, ore_id=2))
    modele.on_update(
        mise_a_jour(
            observation(
                (navire(system=1),), resultats=(resultat(1, RefusalCode.NO_DEPOSIT_FOR_ORE),)
            )
        )
    )
    assert modele.history == (
        HistoryEntry(
            7,
            HistoryKind.REFUSAL,
            "ordre « miner ore_b » : refusé : pas de gisement de ore_b ici ; le plus proche est "
            "dans system_3 (2 sauts)",
        ),
    )
    assert modele.pending == ()


@pytest.mark.parametrize(
    ("commande", "attendu"),
    [
        (Move(ship_id=1, target_system_id=9), "déplacer vers system_9"),
        (Mine(ship_id=1, ore_id=2), "miner ore_b"),
        (Sell(ship_id=1, ore_id=1, quantity=30), "vendre 30 ore_a"),
        (CreateCharacter(actor_kind=ActorKind.NPC), "créer un personnage npc"),
    ],
)
def test_decrire(commande: object, attendu: str) -> None:
    assert decrire(commande) == attendu  # type: ignore[arg-type]


# --- File de vente


def test_vendre_toute_la_cargaison_une_vente_apres_l_autre() -> None:
    modele = ClientModel(ACTEUR)
    assert modele.sell_all() is None
    modele.on_update(mise_a_jour(observation((navire(system=1, cargo=(30, 70)),))))
    assert commandes(modele.sell_all()) == [Sell(ship_id=1, ore_id=2, quantity=70)]
    vendu = observation((navire(system=1, cargo=(30, 0)),), resultats=(resultat(1),))
    suivant = modele.on_update(mise_a_jour(vendu))
    assert commandes(suivant) == [Sell(ship_id=1, ore_id=1, quantity=30)]
    assert suivant is not None and suivant.orders[0].number == 2
    fini = observation((navire(system=1),), resultats=(resultat(2),))
    assert modele.on_update(mise_a_jour(fini)) is None
    assert modele.pending == ()


def test_a_quantites_egales_le_plus_petit_minerai_d_abord() -> None:
    modele = ClientModel(ACTEUR)
    modele.on_update(mise_a_jour(observation((navire(system=1, cargo=(50, 50)),))))
    assert commandes(modele.sell_all()) == [Sell(ship_id=1, ore_id=1, quantity=50)]


def test_cargaison_vide_aucune_vente() -> None:
    modele = ClientModel(ACTEUR)
    modele.on_update(mise_a_jour(observation((navire(system=1),))))
    assert modele.sell_all() is None
    assert modele.pending == ()


def test_le_refus_d_une_vente_de_la_file_vide_la_file() -> None:
    modele = ClientModel(ACTEUR)
    modele.on_update(mise_a_jour(observation((navire(system=3, cargo=(30, 70)),))))
    modele.sell_all()
    refuse = observation(
        (navire(system=3, cargo=(30, 70)),), resultats=(resultat(1, RefusalCode.NOT_AT_STATION),)
    )
    assert modele.on_update(mise_a_jour(refuse)) is None
    assert modele.on_update(mise_a_jour(observation((navire(system=3, cargo=(30, 70)),)))) is None


def test_un_autre_ordre_du_joueur_vide_la_file() -> None:
    modele = ClientModel(ACTEUR)
    modele.on_update(mise_a_jour(observation((navire(system=1, cargo=(30, 70)),))))
    modele.sell_all()
    modele.send(Move(ship_id=1, target_system_id=2))
    accepte = observation((navire(system=1, cargo=(30, 0)),), resultats=(resultat(1), resultat(2)))
    assert modele.on_update(mise_a_jour(accepte)) is None


def test_un_resultat_d_un_autre_ordre_ne_fait_pas_partir_la_vente_suivante() -> None:
    modele = ClientModel(ACTEUR)
    modele.on_update(mise_a_jour(observation((navire(system=1, cargo=(30, 70)),))))
    modele.send(Move(ship_id=1, target_system_id=2))
    modele.sell_all()
    autre = observation((navire(system=1, cargo=(30, 70)),), resultats=(resultat(1),))
    assert modele.on_update(mise_a_jour(autre)) is None
    vendu = observation((navire(system=1, cargo=(30, 0)),), resultats=(resultat(2),))
    assert commandes(modele.on_update(mise_a_jour(vendu))) == [
        Sell(ship_id=1, ore_id=1, quantity=30)
    ]


def test_sans_vaisseau_aucune_vente_ni_duree() -> None:
    modele = ClientModel(ACTEUR)
    assert modele.remaining_ticks() is None
    modele.on_update(mise_a_jour(observation(())))
    assert modele.sell_all() is None
    assert modele.remaining_ticks() is None


# --- Historique des ventes et alertes


def test_une_vente_dans_l_historique() -> None:
    modele = ClientModel(ACTEUR)
    vente = evenement(Sale(ship_id=1, ore_id=2, quantity=100, price=15, payment=1500, tax=150))
    autre = evenement(Sale(ship_id=2, ore_id=2, quantity=5, price=15, payment=75, tax=8), acteur=2)
    modele.on_update(mise_a_jour(observation((navire(system=1),), evenements=(vente, autre))))
    assert modele.history == (
        HistoryEntry(7, HistoryKind.SALE, "vente : 100 ore_b à 15, paiement 1500, taxe 150"),
    )


def test_alerte_d_arrivee_seulement_quand_la_route_est_vide() -> None:
    modele = ClientModel(ACTEUR)
    intermediaire = observation(
        (navire(system=2, activity=Activity.EN_ROUTE, route=(3,)),),
        evenements=(evenement(Arrived(ship_id=1, system_id=2)),),
    )
    modele.on_update(mise_a_jour(intermediaire))
    assert modele.alerts == ()
    arrive = observation(
        (navire(system=3),), evenements=(evenement(Arrived(ship_id=1, system_id=3)),)
    )
    modele.on_update(mise_a_jour(arrive))
    assert list(modele.alerts) == [Alert(kind=AlertKind.ARRIVED, tick=7, text="arrivée : system_3")]
    assert modele.history == (HistoryEntry(7, HistoryKind.ALERT, "arrivée : system_3"),)


def test_l_arrivee_d_un_autre_vaisseau_n_alerte_pas() -> None:
    modele = ClientModel(ACTEUR)
    obs = observation(
        (navire(system=1),), evenements=(evenement(Arrived(ship_id=2, system_id=2), acteur=2),)
    )
    modele.on_update(mise_a_jour(obs))
    assert modele.alerts == () and modele.history == ()


def test_alerte_de_fin_de_minage_avec_le_minerai_de_l_observation_precedente() -> None:
    modele = ClientModel(ACTEUR)
    en_minage = msgspec.structs.replace(
        navire(system=3, activity=Activity.MINING, cargo=(0, 90)), mining_ore_id=2
    )
    modele.on_update(mise_a_jour(observation((en_minage,))))
    fini = observation(
        (navire(system=3, cargo=(0, 100)),),
        evenements=(evenement(MiningEnded(ship_id=1, quantity=100)),),
    )
    modele.on_update(mise_a_jour(fini))
    assert modele.alerts == (
        Alert(kind=AlertKind.MINING_ENDED, tick=7, text="fin de minage : ore_b 100/100"),
    )
    assert modele.history == (HistoryEntry(7, HistoryKind.ALERT, "fin de minage : ore_b 100/100"),)


def test_minage_commence_et_fini_dans_le_meme_tick() -> None:
    """Le minerai vient de l'événement de début de minage ; la cargaison mêlée donne le total."""
    modele = ClientModel(ACTEUR)
    fini = observation(
        (navire(system=2, cargo=(95, 5)),),
        evenements=(
            evenement(MiningStarted(ship_id=1, ore_id=1, rate=10)),
            evenement(MiningEnded(ship_id=1, quantity=5)),
        ),
    )
    modele.on_update(mise_a_jour(fini))
    assert [a.text for a in modele.alerts] == ["fin de minage : ore_a 100/100"]


def test_minerai_inconnu_le_plus_abondant_de_la_cargaison() -> None:
    modele = ClientModel(ACTEUR)
    fini = observation(
        (navire(system=2, cargo=(30, 70)),),
        evenements=(evenement(MiningEnded(ship_id=1, quantity=5)),),
    )
    modele.on_update(mise_a_jour(fini))
    assert [a.text for a in modele.alerts] == ["fin de minage : ore_b 100/100"]


def test_minerai_inconnu_et_cargaison_vide() -> None:
    modele = ClientModel(ACTEUR)
    fini = observation(
        (navire(system=2),), evenements=(evenement(MiningEnded(ship_id=1, quantity=0)),)
    )
    with pytest.raises(ValueError, match="^fin de minage d'un vaisseau à la cargaison vide"):
        modele.on_update(mise_a_jour(fini))


def test_un_minage_interrompu_par_un_ordre_n_alerte_pas() -> None:
    modele = ClientModel(ACTEUR)
    cause = OrderId(actor_id=ACTEUR, tick=7, number=3)
    obs = observation(
        (navire(system=2, cargo=(40, 0)),),
        evenements=(evenement(MiningEnded(ship_id=1, quantity=40), cause),),
    )
    modele.on_update(mise_a_jour(obs))
    assert modele.alerts == () and modele.history == ()


def test_les_alertes_forment_une_file_acquittee_par_la_plus_ancienne() -> None:
    modele = ClientModel(ACTEUR)
    modele.acknowledge()
    for systeme, tick in ((2, 7), (3, 8)):
        obs = msgspec.structs.replace(
            observation(
                (navire(system=systeme),),
                evenements=(evenement(Arrived(ship_id=1, system_id=systeme)),),
            ),
            tick=tick,
        )
        modele.on_update(mise_a_jour(obs))
    assert [a.text for a in modele.alerts] == ["arrivée : system_2", "arrivée : system_3"]
    modele.acknowledge()
    assert modele.alerts == (Alert(kind=AlertKind.ARRIVED, tick=8, text="arrivée : system_3"),)
    modele.acknowledge()
    assert list(modele.alerts) == []
    assert modele.history == (
        HistoryEntry(7, HistoryKind.ALERT, "arrivée : system_2"),
        HistoryEntry(8, HistoryKind.ALERT, "arrivée : system_3"),
    )


# --- Ticks restants


def test_ticks_restants_d_un_trajet() -> None:
    modele = ClientModel(ACTEUR)
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=2
    )
    modele.on_update(mise_a_jour(observation((en_route,))))
    assert modele.remaining_ticks() == 2 + 5


@pytest.mark.parametrize(
    ("cargo", "stock", "attendu"),
    [
        ((0, 40), 20000, 6),  # capacité libre 60 : 6 ticks à 10 par tick
        ((0, 35), 20000, 7),  # capacité libre 65 : arrondi au tick supérieur
        ((0, 40), 25, 3),  # le stock s'épuise d'abord
        ((0, 40), None, 6),  # stock inconnu : la capacité libre seule
    ],
)
def test_ticks_restants_d_un_minage(
    cargo: tuple[int, int], stock: int | None, attendu: int
) -> None:
    modele = ClientModel(ACTEUR)
    en_minage = msgspec.structs.replace(
        navire(system=3, activity=Activity.MINING, cargo=cargo), mining_ore_id=2
    )
    modele.on_update(mise_a_jour(observation((en_minage,), stocks=(5, stock))))
    assert modele.remaining_ticks() == attendu


def test_a_l_arret_aucun_tick_restant() -> None:
    modele = ClientModel(ACTEUR)
    modele.on_update(mise_a_jour(observation((navire(system=1),))))
    assert modele.remaining_ticks() is None


# --- Joué comme client synchrone par Game.advance


@pytest.fixture
def partie(tmp_path: Path) -> Game:
    reglages = msgspec.structs.replace(load_tunables(), jump_ticks=5, mining_rate=10)
    return Game(tmp_path, world_seed=1, tunables=reglages)


def test_trajet_de_jump_ticks_ticks_et_alerte_d_arrivee(partie: Game) -> None:
    ident = partie.create_character(ActorKind.HUMAN)
    modele = ClientModel(ident)
    partie.attach(ident, modele)
    connexion = partie.connect(ident)
    partie.advance(1)
    obs = modele.observation
    assert obs is not None
    depart = obs.own_ships[0]
    dist = distances(obs.systems, depart.system_id)
    cible = min(s for s, d in dist.items() if d == 1)
    connexion.submit(modele.send(Move(ship_id=depart.id, target_system_id=cible)))
    partie.advance(1)
    # Le tick où l'ordre est accepté compte déjà comme le premier tick du saut.
    annonce = modele.remaining_ticks()
    assert annonce == partie.tunables.jump_ticks - 1
    partie.advance(annonce - 1)
    assert not modele.alerts
    partie.advance(1)
    assert modele.observation is not None and modele.observation.own_ships[0].system_id == cible
    assert [a.text for a in modele.alerts] == [f"arrivée : system_{cible}"]
    assert modele.pending == ()
    partie.close()


def test_la_vente_suivante_entre_au_tick_suivant(partie: Game) -> None:
    """Deux minerais à bord, à la station : deux ventes sur deux ticks qui se suivent."""
    ident = partie.create_character(ActorKind.HUMAN)
    modele = ClientModel(ident)
    partie.attach(ident, modele)
    connexion = partie.connect(ident)
    partie.advance(1)
    navire_ = partie.state.ships[0]
    plein = msgspec.structs.replace(navire_, cargo=(30, 70))
    partie.state = msgspec.structs.replace(partie.state, ships=(plein,))
    partie.advance(1)
    message = modele.sell_all()
    assert message is not None
    connexion.submit(message)
    partie.advance(1)
    assert partie.state.ships[0].cargo == (30, 0)
    partie.advance(1)
    assert partie.state.ships[0].cargo == (0, 0)
    ventes = [e.text for e in modele.history if e.kind is HistoryKind.SALE]
    assert len(ventes) == 2 and "70 ore_b" in ventes[0] and "30 ore_a" in ventes[1]
    partie.close()


# --- Gisements vus vides (amendement 2, Technical Plan, point 7 ter)


def test_gisements_vus_vides_mis_a_jour_a_chaque_observation() -> None:
    modele = ClientModel(ACTEUR)
    assert modele.seen_empty == frozenset()
    modele.on_update(mise_a_jour(observation((navire(system=2),), stocks=(0, None))))
    assert modele.seen_empty == frozenset({1})
    modele.on_update(mise_a_jour(observation((navire(system=3),), stocks=(None, 500))))
    assert modele.seen_empty == frozenset({1})
    modele.on_update(mise_a_jour(observation((navire(system=2),), stocks=(30, None))))
    assert modele.seen_empty == frozenset()


def test_gisements_vus_vides_se_vident_quand_tous_y_sont() -> None:
    modele = ClientModel(ACTEUR)
    modele.on_update(mise_a_jour(observation((navire(system=2),), stocks=(0, None))))
    modele.on_update(mise_a_jour(observation((navire(system=3),), stocks=(None, 0))))
    assert modele.seen_empty == frozenset({2})  # l'ensemble repart des seuls vides visibles
    modele.on_update(mise_a_jour(observation((navire(system=2),), stocks=(0, 0))))
    assert modele.seen_empty == frozenset()
