"""Tests de fourx.clients.texts (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 bis ;
plan détaillé, point 23 quinquies, table des refus).

Carte de tests/aide_observation.py : chaîne system_1 – system_2 – system_3, station S1 dans
system_1, gisement de ore_a dans system_2, de ore_b dans system_3.
"""

import msgspec
import pytest

from fourx.clients.texts import duration_text, refusal_text
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.ids import OrderId
from fourx.schema.observation import DepositView, Observation, StationView, SystemView
from fourx.schema.orders import Command, CreateCharacter, Mine, Move, Sell
from fourx.schema.results import OrderResult, RefusalCode
from tests.aide_observation import ACTEUR, navire, observation


def refus(code: RefusalCode) -> OrderResult:
    return OrderResult(
        recipient_actor_id=ACTEUR,
        order_id=OrderId(actor_id=ACTEUR, tick=7, number=1),
        accepted=False,
        refusal=code,
        text=code.value,
        budget_left=9,
    )


@pytest.mark.parametrize(
    ("code", "attendu"),
    [
        (RefusalCode.UNKNOWN_SHIP, "vaisseau inconnu"),
        (RefusalCode.NOT_OWNER, "ce vaisseau n'est pas le vôtre"),
        (RefusalCode.UNKNOWN_SYSTEM, "système inconnu"),
        (RefusalCode.QUANTITY_NOT_POSITIVE, "quantité nulle ou négative"),
        (RefusalCode.NO_ACTION_LEFT, "plus d'action disponible ce tick"),
        (RefusalCode.SUPERSEDED, "remplacé par un autre ordre du même tick"),
        (RefusalCode.INVALID_FORMAT, "ordre mal formé"),
        (RefusalCode.DUPLICATE_NUMBER, "numéro d'ordre déjà utilisé"),
        (RefusalCode.QUOTA_EXCEEDED, "trop d'ordres ce tick"),
        (RefusalCode.ACTOR_MISMATCH, "ordre au nom d'un autre personnage"),
        (RefusalCode.FORBIDDEN_CATEGORY, "catégorie d'ordre interdite"),
    ],
)
def test_refus_sans_donnee(code: RefusalCode, attendu: str) -> None:
    obs = observation((navire(system=1),))
    assert refusal_text(refus(code), Move(ship_id=1, target_system_id=2), obs) == attendu


def test_creation_de_personnage_refusee_sans_donnee() -> None:
    obs = observation((navire(system=1),))
    commande = CreateCharacter(actor_kind=ActorKind.HUMAN)
    assert refusal_text(refus(RefusalCode.FORBIDDEN_CATEGORY), commande, obs) == (
        "catégorie d'ordre interdite"
    )
    with pytest.raises(ValueError, match="^refus SHIP_EN_ROUTE inattendu pour une création"):
        refusal_text(refus(RefusalCode.SHIP_EN_ROUTE), commande, obs)


def test_vaisseau_en_route() -> None:
    """Le saut en cours (3 ticks) puis un saut complet (5 ticks) vers system_3."""
    en_route = msgspec.structs.replace(
        navire(system=1, activity=Activity.EN_ROUTE, route=(2, 3)), ticks_to_next_jump=3
    )
    obs = observation((en_route,))
    texte = refusal_text(refus(RefusalCode.SHIP_EN_ROUTE), Mine(ship_id=1, ore_id=1), obs)
    assert texte == "vaisseau en route : arrivée dans 8 ticks"


def test_deja_dans_le_systeme() -> None:
    obs = observation((navire(system=2),))
    texte = refusal_text(refus(RefusalCode.ALREADY_THERE), Move(ship_id=1, target_system_id=2), obs)
    assert texte == "déjà dans system_2"


@pytest.mark.parametrize(
    ("systeme", "ore_id", "attendu"),
    [
        (1, 1, "pas de gisement de ore_a ici ; le plus proche est dans system_2 (1 saut)"),
        (1, 2, "pas de gisement de ore_b ici ; le plus proche est dans system_3 (2 sauts)"),
        (3, 1, "pas de gisement de ore_a ici ; le plus proche est dans system_2 (1 saut)"),
    ],
)
def test_pas_de_gisement_ici(systeme: int, ore_id: int, attendu: str) -> None:
    obs = observation((navire(system=systeme),))
    commande = Mine(ship_id=1, ore_id=ore_id)
    assert refusal_text(refus(RefusalCode.NO_DEPOSIT_FOR_ORE), commande, obs) == attendu


def etoile(gisements: tuple[DepositView, ...]) -> Observation:
    """system_1 au centre, relié à system_2, system_3 et system_4 ; la station dans system_1."""
    return msgspec.structs.replace(
        observation((navire(system=1),)),
        systems=(
            SystemView(id=1, neighbors=(2, 3, 4)),
            SystemView(id=2, neighbors=(1,)),
            SystemView(id=3, neighbors=(1,)),
            SystemView(id=4, neighbors=(1,)),
        ),
        deposits=gisements,
    )


def test_a_distance_egale_le_systeme_de_plus_petit_identifiant() -> None:
    obs = etoile(
        (
            DepositView(id=1, system_id=4, ore_id=1, stock=5),
            DepositView(id=2, system_id=3, ore_id=1, stock=5),
        )
    )
    texte = refusal_text(refus(RefusalCode.NO_DEPOSIT_FOR_ORE), Mine(ship_id=1, ore_id=1), obs)
    assert texte == "pas de gisement de ore_a ici ; le plus proche est dans system_3 (1 saut)"


def test_aucun_gisement_accessible_du_minerai() -> None:
    obs = msgspec.structs.replace(observation((navire(system=1),)), deposits=())
    texte = refusal_text(refus(RefusalCode.NO_DEPOSIT_FOR_ORE), Mine(ship_id=1, ore_id=2), obs)
    assert texte == "pas de gisement de ore_b ici"


def test_gisement_vide_nomme_le_plus_proche_qui_n_est_pas_connu_comme_vide() -> None:
    """Ici, system_1 est vide ; system_2 est connu vide ; system_3, hors de portée, est inconnu ;
    system_4 a du stock."""
    obs = etoile(
        (
            DepositView(id=1, system_id=1, ore_id=1, stock=0),
            DepositView(id=2, system_id=2, ore_id=1, stock=0),
            DepositView(id=3, system_id=3, ore_id=1, stock=None),
            DepositView(id=4, system_id=4, ore_id=1, stock=7),
            DepositView(id=5, system_id=2, ore_id=2, stock=9),
        )
    )
    texte = refusal_text(refus(RefusalCode.DEPOSIT_EMPTY), Mine(ship_id=1, ore_id=1), obs)
    assert texte == (
        "gisement vide ; le plus proche gisement de ore_a qui n'est pas connu comme vide "
        "est dans system_3 (1 saut)"
    )


def test_gisement_vide_et_tous_les_autres_connus_vides() -> None:
    obs = etoile(
        (
            DepositView(id=1, system_id=1, ore_id=1, stock=0),
            DepositView(id=2, system_id=2, ore_id=1, stock=0),
            DepositView(id=3, system_id=3, ore_id=2, stock=40),
        )
    )
    texte = refusal_text(refus(RefusalCode.DEPOSIT_EMPTY), Mine(ship_id=1, ore_id=1), obs)
    assert texte == "gisement vide ; tous les gisements de ore_a connus sont vides"


def deux_stations(systeme: int) -> Observation:
    """S1 dans system_1, S2 dans system_3 : à égale distance de system_2."""
    return msgspec.structs.replace(
        observation((navire(system=systeme, cargo=(0, 100)),)),
        stations=(
            StationView(id=2, system_id=3, ore_prices=(12, 12)),
            StationView(id=1, system_id=1, ore_prices=(10, 15)),
        ),
    )


def test_cargaison_pleine_nomme_la_station_la_plus_proche() -> None:
    obs = deux_stations(3)
    texte = refusal_text(refus(RefusalCode.CARGO_FULL), Mine(ship_id=1, ore_id=2), obs)
    assert texte == "cargaison pleine : allez vendre ; la station la plus proche est S2 (0 sauts)"
    obs = deux_stations(2)
    texte = refusal_text(refus(RefusalCode.CARGO_FULL), Mine(ship_id=1, ore_id=2), obs)
    assert texte == "cargaison pleine : allez vendre ; la station la plus proche est S1 (1 saut)"


def test_pas_de_station_ici() -> None:
    obs = observation((navire(system=3, cargo=(0, 10)),))
    commande = Sell(ship_id=1, ore_id=2, quantity=10)
    assert refusal_text(refus(RefusalCode.NOT_AT_STATION), commande, obs) == (
        "pas de station ici ; la plus proche est S1, dans system_1 (2 sauts)"
    )
    obs = deux_stations(2)
    assert refusal_text(refus(RefusalCode.NOT_AT_STATION), commande, obs) == (
        "pas de station ici ; la plus proche est S1, dans system_1 (1 saut)"
    )


def test_aucune_station_accessible() -> None:
    obs = msgspec.structs.replace(observation((navire(system=3),)), stations=())
    with pytest.raises(ValueError, match="^aucune station accessible depuis le vaisseau$"):
        refusal_text(refus(RefusalCode.NOT_AT_STATION), Sell(ship_id=1, ore_id=1, quantity=1), obs)


def test_quantite_superieure_a_la_cargaison() -> None:
    obs = observation((navire(system=1, cargo=(30, 4)),))
    commande = Sell(ship_id=1, ore_id=2, quantity=10)
    texte = refusal_text(refus(RefusalCode.QUANTITY_EXCEEDS_CARGO), commande, obs)
    assert texte == "quantité supérieure à la cargaison (4 à bord)"


@pytest.mark.parametrize(
    ("code", "commande"),
    [
        (RefusalCode.ALREADY_THERE, Mine(ship_id=1, ore_id=1)),
        (RefusalCode.NO_DEPOSIT_FOR_ORE, Move(ship_id=1, target_system_id=2)),
        (RefusalCode.DEPOSIT_EMPTY, Sell(ship_id=1, ore_id=1, quantity=1)),
        (RefusalCode.QUANTITY_EXCEEDS_CARGO, Mine(ship_id=1, ore_id=1)),
        (RefusalCode.QUANTITY_EXCEEDS_CARGO, Sell(ship_id=1, ore_id=3, quantity=1)),
        (RefusalCode.QUANTITY_EXCEEDS_CARGO, Sell(ship_id=1, ore_id=0, quantity=1)),
    ],
)
def test_refus_sans_rapport_avec_la_commande(code: RefusalCode, commande: Command) -> None:
    obs = observation((navire(system=1),))
    with pytest.raises(ValueError, match=f"^refus {code.name} inattendu pour la commande "):
        refusal_text(refus(code), commande, obs)


def test_refus_d_un_vaisseau_absent_ou_ordre_accepte() -> None:
    obs = observation((navire(system=1),))
    with pytest.raises(ValueError, match="^vaisseau 9 absent de l'observation$"):
        refusal_text(refus(RefusalCode.CARGO_FULL), Mine(ship_id=9, ore_id=1), obs)
    accepte = msgspec.structs.replace(refus(RefusalCode.CARGO_FULL), accepted=True, refusal=None)
    with pytest.raises(ValueError, match="^refusal_text attend un ordre refusé$"):
        refusal_text(accepte, Mine(ship_id=1, ore_id=1), obs)


def test_chaque_code_a_un_texte() -> None:
    """Aucun code de RefusalCode n'est oublié : chacun a son cas dans les tests ci-dessus."""
    assert len(RefusalCode) == 18


@pytest.mark.parametrize(
    ("ticks", "attendu"),
    [
        (400, "400 ticks (≈ 20 min à 3 s)"),
        (62, "62 ticks (≈ 3 min 6 s à 3 s)"),
        (1, "1 tick (≈ 3 s à 3 s)"),
        (0, "0 ticks (≈ 0 s à 3 s)"),
        (20, "20 ticks (≈ 1 min à 3 s)"),
        (1200, "1200 ticks (≈ 1 h à 3 s)"),
        (1221, "1221 ticks (≈ 1 h 1 min 3 s à 3 s)"),
        (1201, "1201 ticks (≈ 1 h 3 s à 3 s)"),
    ],
)
def test_durees(ticks: int, attendu: str) -> None:
    assert duration_text(ticks) == attendu
