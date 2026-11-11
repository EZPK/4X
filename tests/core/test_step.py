"""Tests de fourx.core.step.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 2, 3 et 5.
"""

import msgspec.structs
import pytest

from fourx.core.keyed_random import keyed_draw
from fourx.core.state import Ship, State
from fourx.core.step import Phase, plus_court_chemin, step
from fourx.core.version import rules_version
from fourx.schema.actors import Activity, ActorKind
from fourx.schema.events import (
    EVENT_SCHEMA_VERSION,
    Arrived,
    CharacterCreated,
    Departed,
    DepositRegenerated,
    LedgerEntryRecorded,
    MiningEnded,
    MiningStarted,
    OrderRefused,
    Sale,
)
from fourx.schema.ids import OrderId
from fourx.schema.ledger import Reason
from fourx.schema.orders import CreateCharacter, Mine, Move, OrderCategory, Sell
from fourx.schema.results import RefusalCode
from fourx.schema.visibility import Visibility
from tests.aide_monde import GRAINE, REGLAGES, avancer, monde, ordre, vaisseau


def refus(state: State, numero: int, acteur: int = 1) -> RefusalCode | None:
    resultats = [
        r
        for r in state.last_tick.results
        if r.order_id.number == numero and r.order_id.actor_id == acteur
    ]
    assert len(resultats) == 1
    return resultats[0].refusal


def test_phases() -> None:
    assert [p.value for p in Phase] == ["movement", "mining", "trade", "combat", "settlement"]


def test_tick_avance_et_etat_non_modifie() -> None:
    depart = monde((vaisseau(1, 1, 2),))
    copie = depart
    apres, evenements = step(depart, (), GRAINE, REGLAGES)
    assert apres.tick == 1
    assert depart is copie and depart.tick == 0
    assert evenements == ()
    assert apres.last_tick.events == () and apres.last_tick.results == ()


def test_plus_court_chemin() -> None:
    voisins = {1: (2,), 2: (3, 1), 3: (2,)}
    assert plus_court_chemin(voisins, 1, 3) == (2, 3)
    assert plus_court_chemin(voisins, 3, 1) == (2, 1)
    assert plus_court_chemin(voisins, 1, 2) == (2,)
    assert plus_court_chemin({1: (2, 3), 2: (4,), 3: (4,), 4: ()}, 1, 4) == (2, 4)


def test_deplacement_en_deux_sauts() -> None:
    etat = monde((vaisseau(1, 1, 1),))
    etat, evenements = avancer(etat, (ordre(etat, 1, 1, Move(ship_id=1, target_system_id=3)),), 4)
    navire = etat.ships[0]
    assert (navire.system_id, navire.activity, navire.route, navire.ticks_to_next_jump) == (
        1,
        Activity.EN_ROUTE,
        (2, 3),
        1,
    )
    assert etat.actors[0].action_budget == 10  # 10 − 1, puis + 1 par tick, plafonné à 10
    etat, suite = avancer(etat, (), 1)
    assert (etat.ships[0].system_id, etat.ships[0].route, etat.ships[0].ticks_to_next_jump) == (
        2,
        (3,),
        5,
    )
    assert [type(e.payload) for e in suite] == [Departed, Arrived]
    assert suite[0].payload == Departed(ship_id=1, system_id=1)
    assert suite[1].payload == Arrived(ship_id=1, system_id=2)
    assert all(e.visibility is Visibility.PUBLIC and e.actor_id == 1 for e in suite)
    etat, _ = avancer(etat, (), 5)
    assert (etat.ships[0].system_id, etat.ships[0].activity, etat.ships[0].ticks_to_next_jump) == (
        3,
        Activity.IDLE,
        0,
    )
    assert evenements == []


def test_minage_jusqu_a_cargaison_pleine() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    etat, evenements = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),), 1)
    assert etat.ships[0].cargo == (10, 0)
    assert etat.ships[0].mined_since_start == 10
    assert etat.ships[0].mining_ore_id == 1
    assert evenements[0].payload == MiningStarted(ship_id=1, ore_id=1, rate=10)
    etat, suite = avancer(etat, (), 9)
    navire = etat.ships[0]
    assert (navire.cargo, navire.activity, navire.mined_since_start, navire.mining_ore_id) == (
        (100, 0),
        Activity.IDLE,
        0,
        None,
    )
    assert etat.deposits[0].stock == 19900
    assert [e.payload for e in suite] == [MiningEnded(ship_id=1, quantity=100)]


def test_minage_capacite_libre_limite_la_quantite() -> None:
    etat = monde((vaisseau(1, 1, 2, cargo=(0, 95)),))
    etat, _ = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),), 1)
    assert etat.ships[0].cargo == (5, 95)
    assert etat.ships[0].activity is Activity.IDLE
    assert etat.deposits[0].stock == 19995


def test_gisement_vide_puis_regeneration() -> None:
    reglages = msgspec.structs.replace(REGLAGES, regen_ticks=4, deposit_stock=25)
    etat = monde((vaisseau(1, 1, 2),), stocks=(25, 25), reglages=reglages)
    etat, _ = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),), 3, reglages=reglages)
    assert etat.ships[0].cargo == (25, 0)
    assert etat.deposits[0].stock == 0
    assert etat.ships[0].activity is Activity.IDLE
    etat, evenements = avancer(etat, (), 1, reglages=reglages)
    assert [d.stock for d in etat.deposits] == [25, 25]
    regen = [e for e in evenements if isinstance(e.payload, DepositRegenerated)]
    assert [e.payload for e in regen] == [
        DepositRegenerated(deposit_id=1, stock=25),
        DepositRegenerated(deposit_id=2, stock=25),
    ]
    assert all(
        e.actor_id is None and e.actor_kind is None and e.causation_id is None for e in regen
    )


def test_departage_par_tirage_a_cle() -> None:
    etat = monde((vaisseau(1, 1, 2), vaisseau(2, 2, 2)), stocks=(15, 20000))
    ordres = (
        ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),
        ordre(etat, 2, 1, Mine(ship_id=2, ore_id=1)),
    )
    for graine in range(1, 6):
        apres, _ = avancer(etat, ordres, 1, graine=graine)
        premier = min((1, 2), key=lambda i: (keyed_draw(graine, 1, i, "minage"), i))
        recus = {v.id: v.cargo[0] for v in apres.ships}
        assert recus[premier] == 10 and recus[3 - premier] == 5
        assert apres.deposits[0].stock == 0
        assert all(v.activity is Activity.IDLE for v in apres.ships)


def test_stock_suffisant_pas_de_departage() -> None:
    etat = monde((vaisseau(1, 1, 2), vaisseau(2, 2, 2)), stocks=(20, 20000))
    apres, _ = avancer(
        etat,
        (
            ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),
            ordre(etat, 2, 1, Mine(ship_id=2, ore_id=1)),
        ),
    )
    assert [v.cargo[0] for v in apres.ships] == [10, 10]
    assert apres.deposits[0].stock == 0


def test_vente_ecritures_evenements() -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(0, 3)),))
    soumis = ordre(etat, 1, 1, Sell(ship_id=1, ore_id=2, quantity=3), policy_id="p")
    etat, evenements = avancer(etat, (soumis,))
    assert etat.ships[0].cargo == (0, 0)
    assert [type(e.payload) for e in evenements] == [Sale, LedgerEntryRecorded, LedgerEntryRecorded]
    assert evenements[0].payload == Sale(
        ship_id=1, ore_id=2, quantity=3, price=15, payment=45, tax=5
    )
    vente, taxe = (e.payload.entry for e in evenements[1:])  # type: ignore[union-attr]
    cause = OrderId(actor_id=1, tick=1, number=1)
    assert (
        vente.debit_account_id,
        vente.credit_account_id,
        vente.amount,
        vente.reason,
        vente.cause,
    ) == (1, 3, 45, Reason.ORE_SALE, cause)
    assert (
        taxe.debit_account_id,
        taxe.credit_account_id,
        taxe.amount,
        taxe.reason,
        taxe.cause,
    ) == (3, 2, 5, Reason.SALE_TAX, cause)
    assert [c.balance for c in etat.ledger.accounts] == [-45, 5, 40]
    assert etat.ledger.tick_entries == (vente, taxe)
    assert [e.visibility for e in evenements] == [
        Visibility.PRIVATE,
        Visibility.ADMIN,
        Visibility.ADMIN,
    ]
    assert [e.seq for e in evenements] == [0, 1, 2]
    etat, _ = avancer(etat)
    assert etat.ledger.tick_entries == ()


def test_vente_d_un_vaisseau_en_minage_arrete_le_minage() -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(0, 50)),))
    en_minage = msgspec.structs.replace(
        etat.ships[0], activity=Activity.MINING, mining_ore_id=2, mined_since_start=7
    )
    etat = msgspec.structs.replace(etat, ships=(en_minage,))
    etat, evenements = avancer(etat, (ordre(etat, 1, 1, Sell(ship_id=1, ore_id=2, quantity=50)),))
    assert evenements[0].payload == MiningEnded(ship_id=1, quantity=7)
    assert etat.ships[0].activity is Activity.IDLE
    assert etat.ships[0].mined_since_start == 0


def test_enveloppe_des_evenements() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    soumis = ordre(etat, 1, 4, Mine(ship_id=1, ore_id=1), policy_id="scripted_miner")
    _, evenements = avancer(etat, (soumis,))
    e = evenements[0]
    assert (e.tick, e.seq, e.event_schema_version, e.rules_version) == (
        1,
        0,
        EVENT_SCHEMA_VERSION,
        rules_version(REGLAGES),
    )
    assert (e.actor_id, e.actor_kind, e.policy_id, e.policy_version) == (
        1,
        ActorKind.HUMAN,
        "scripted_miner",
        1,
    )
    assert e.causation_id == OrderId(actor_id=1, tick=1, number=4)
    assert e.visibility is Visibility.PRIVATE


@pytest.mark.parametrize(
    ("vaisseaux", "acteur", "commande", "code"),
    [
        ((vaisseau(1, 1, 2),), 1, Mine(ship_id=9, ore_id=1), RefusalCode.UNKNOWN_SHIP),
        (
            (vaisseau(1, 1, 2), vaisseau(2, 2, 1)),
            2,
            Mine(ship_id=1, ore_id=1),
            RefusalCode.NOT_OWNER,
        ),
        ((vaisseau(1, 1, 1),), 1, Move(ship_id=1, target_system_id=9), RefusalCode.UNKNOWN_SYSTEM),
        ((vaisseau(1, 1, 1),), 1, Move(ship_id=1, target_system_id=1), RefusalCode.ALREADY_THERE),
        ((vaisseau(1, 1, 2),), 1, Mine(ship_id=1, ore_id=2), RefusalCode.NO_DEPOSIT_FOR_ORE),
        (
            (vaisseau(1, 1, 2, cargo=(60, 40)),),
            1,
            Mine(ship_id=1, ore_id=1),
            RefusalCode.CARGO_FULL,
        ),
        (
            (vaisseau(1, 1, 2, cargo=(5, 0)),),
            1,
            Sell(ship_id=1, ore_id=1, quantity=5),
            RefusalCode.NOT_AT_STATION,
        ),
        (
            (vaisseau(1, 1, 1, cargo=(5, 0)),),
            1,
            Sell(ship_id=1, ore_id=1, quantity=0),
            RefusalCode.QUANTITY_NOT_POSITIVE,
        ),
        (
            (vaisseau(1, 1, 1, cargo=(5, 0)),),
            1,
            Sell(ship_id=1, ore_id=1, quantity=-1),
            RefusalCode.QUANTITY_NOT_POSITIVE,
        ),
        (
            (vaisseau(1, 1, 1, cargo=(5, 0)),),
            1,
            Sell(ship_id=1, ore_id=1, quantity=6),
            RefusalCode.QUANTITY_EXCEEDS_CARGO,
        ),
        (
            (vaisseau(1, 1, 1, cargo=(5, 0)),),
            1,
            Sell(ship_id=1, ore_id=3, quantity=1),
            RefusalCode.QUANTITY_EXCEEDS_CARGO,
        ),
    ],
)
def test_codes_de_refus(
    vaisseaux: tuple[object, ...], acteur: int, commande: object, code: RefusalCode
) -> None:
    etat = monde(vaisseaux)  # type: ignore[arg-type]
    apres, evenements = avancer(etat, (ordre(etat, acteur, 1, commande),))  # type: ignore[arg-type]
    assert refus(apres, 1, acteur) is code
    resultat = apres.last_tick.results[0]
    assert not resultat.accepted and resultat.text == code.value
    assert resultat.recipient_actor_id == acteur
    assert resultat.budget_left == 10
    assert evenements[0].payload == OrderRefused(
        order_id=OrderId(actor_id=acteur, tick=1, number=1), refusal=code
    )
    assert evenements[0].visibility is Visibility.PRIVATE and evenements[0].actor_id == acteur
    assert apres.ships == etat.ships


@pytest.mark.parametrize("ore_id", [0, -1])
def test_vente_d_un_minerai_hors_bornes_refusee(ore_id: int) -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(5, 5)),))
    apres, _ = avancer(etat, (ordre(etat, 1, 1, Sell(ship_id=1, ore_id=ore_id, quantity=1)),))
    assert refus(apres, 1) is RefusalCode.QUANTITY_EXCEEDS_CARGO
    assert apres.ships[0].cargo == (5, 5)
    assert all(c.balance == 0 for c in apres.ledger.accounts)


def test_enveloppe_de_la_vente_et_de_ses_ecritures() -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(0, 3)),))
    soumis = ordre(etat, 1, 6, Sell(ship_id=1, ore_id=2, quantity=3), policy_id="p")
    _, evenements = avancer(etat, (soumis,))
    cause = OrderId(actor_id=1, tick=1, number=6)
    assert [e.causation_id for e in evenements] == [cause, cause, cause]
    assert [(e.policy_id, e.policy_version) for e in evenements] == [("p", 1)] * 3
    assert [e.actor_id for e in evenements] == [1, 1, 1]


def test_fin_de_minage_remplace_par_un_ordre_porte_cet_ordre() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    etat, _ = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),), 2)
    _, evenements = avancer(etat, (ordre(etat, 1, 2, Move(ship_id=1, target_system_id=1)),))
    fin = evenements[0]
    assert fin.payload == MiningEnded(ship_id=1, quantity=20)
    assert fin.causation_id == OrderId(actor_id=1, tick=3, number=2)


def test_fin_de_minage_par_les_regles_sans_cause() -> None:
    etat = monde((vaisseau(1, 1, 2, cargo=(0, 95)),))
    _, evenements = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),))
    fin = [e for e in evenements if isinstance(e.payload, MiningEnded)]
    assert len(fin) == 1 and fin[0].causation_id is None and fin[0].actor_id == 1


@pytest.mark.parametrize(
    ("vaisseaux", "budgets", "acteur", "commande", "code"),
    [
        # Vaisseau d'un autre acteur et en route : la colonne « autre acteur » passe avant.
        (
            (vaisseau(1, 1, 1),),
            {1: 10, 2: 10},
            2,
            Move(ship_id=1, target_system_id=3),
            RefusalCode.NOT_OWNER,
        ),
        # Système inconnu passe avant « déjà sur place ».
        (
            (vaisseau(1, 1, 1),),
            None,
            1,
            Move(ship_id=1, target_system_id=99),
            RefusalCode.UNKNOWN_SYSTEM,
        ),
        # Le budget se contrôle en dernier.
        ((vaisseau(1, 1, 2),), {1: 0}, 1, Mine(ship_id=9, ore_id=1), RefusalCode.UNKNOWN_SHIP),
        (
            (vaisseau(1, 1, 2),),
            {1: 0},
            1,
            Mine(ship_id=1, ore_id=2),
            RefusalCode.NO_DEPOSIT_FOR_ORE,
        ),
        # Hors de la station passe avant une quantité nulle.
        (
            (vaisseau(1, 1, 2),),
            None,
            1,
            Sell(ship_id=1, ore_id=1, quantity=0),
            RefusalCode.NOT_AT_STATION,
        ),
        # Quantité nulle passe avant « plus que la cargaison ».
        (
            (vaisseau(1, 1, 1),),
            None,
            1,
            Sell(ship_id=1, ore_id=1, quantity=0),
            RefusalCode.QUANTITY_NOT_POSITIVE,
        ),
    ],
)
def test_priorite_des_codes_de_refus(
    vaisseaux: tuple[Ship, ...],
    budgets: dict[int, int] | None,
    acteur: int,
    commande: Move | Mine | Sell,
    code: RefusalCode,
) -> None:
    etat = monde(vaisseaux, budgets=budgets)
    if acteur == 2 and code is RefusalCode.NOT_OWNER:
        etat, _ = avancer(etat, (ordre(etat, 1, 1, Move(ship_id=1, target_system_id=3)),))
    apres, _ = avancer(etat, (ordre(etat, acteur, 2, commande),))
    assert refus(apres, 2, acteur) is code


def test_ordre_sans_emetteur_avant_le_code_de_la_reception() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    soumis = ordre(
        etat, 1, 1, Mine(ship_id=1, ore_id=1), sender=None, refus=RefusalCode.QUOTA_EXCEEDED
    )
    apres, _ = avancer(etat, (soumis,))
    assert refus(apres, 1) is RefusalCode.FORBIDDEN_CATEGORY


def test_ordre_des_evenements_entre_les_phases() -> None:
    reglages = msgspec.structs.replace(REGLAGES, regen_ticks=6, jump_ticks=1)
    etat = monde(
        (
            vaisseau(1, 1, 1),
            vaisseau(2, 2, 2, cargo=(0, 95)),
            vaisseau(3, 3, 1, cargo=(0, 10)),
        ),
        reglages=reglages,
    )
    etat, _ = avancer(etat, (), 5, reglages=reglages)
    ordres = (
        ordre(etat, 1, 1, Move(ship_id=1, target_system_id=2)),
        ordre(etat, 1, 2, Mine(ship_id=9, ore_id=1)),
        ordre(etat, 2, 1, Mine(ship_id=2, ore_id=1)),
        ordre(etat, 3, 1, Sell(ship_id=3, ore_id=2, quantity=10)),
    )
    apres, evenements = avancer(etat, ordres, reglages=reglages)
    assert apres.tick == 6
    assert [type(e.payload).__name__ for e in evenements] == [
        "OrderRefused",  # examen : acteur 1, ordre 2
        "MiningStarted",  # examen : acteur 2
        "Departed",  # déplacement
        "Arrived",
        "MiningEnded",  # minage : cargaison pleine
        "Sale",  # commerce
        "LedgerEntryRecorded",
        "LedgerEntryRecorded",
        "DepositRegenerated",  # règlement
        "DepositRegenerated",
    ]
    assert [e.seq for e in evenements] == list(range(10))


def test_gisement_vide_refuse() -> None:
    etat = monde((vaisseau(1, 1, 2),), stocks=(0, 5))
    apres, _ = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),))
    assert refus(apres, 1) is RefusalCode.DEPOSIT_EMPTY


def test_vaisseau_en_route_refuse() -> None:
    etat = monde((vaisseau(1, 1, 1),))
    etat, _ = avancer(etat, (ordre(etat, 1, 1, Move(ship_id=1, target_system_id=3)),))
    apres, _ = avancer(etat, (ordre(etat, 1, 2, Move(ship_id=1, target_system_id=2)),))
    assert refus(apres, 2) is RefusalCode.SHIP_EN_ROUTE


def test_budget_epuise_et_regain() -> None:
    etat = monde((vaisseau(1, 1, 2),), budgets={1: 0})
    apres, _ = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1)),))
    assert refus(apres, 1) is RefusalCode.NO_ACTION_LEFT
    assert apres.last_tick.results[0].budget_left == 0
    assert apres.actors[0].action_budget == 1
    apres, _ = avancer(apres, (ordre(apres, 1, 2, Mine(ship_id=1, ore_id=1)),))
    assert apres.last_tick.results[0].accepted
    assert apres.last_tick.results[0].budget_left == 0
    assert apres.actors[0].action_budget == 1


def test_un_ordre_par_vaisseau_le_plus_petit_numero() -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(0, 100)),))
    apres, _ = avancer(
        etat,
        (
            ordre(etat, 1, 2, Sell(ship_id=1, ore_id=2, quantity=60)),
            ordre(etat, 1, 1, Sell(ship_id=1, ore_id=2, quantity=30)),
        ),
    )
    assert refus(apres, 1) is None
    assert refus(apres, 2) is RefusalCode.SUPERSEDED
    assert apres.ships[0].cargo == (0, 70)
    assert [r.order_id.number for r in apres.last_tick.results] == [1, 2]


def test_meme_numero_sur_le_meme_vaisseau_le_second_est_remplace() -> None:
    etat = monde((vaisseau(1, 1, 1, cargo=(0, 100)),))
    apres, _ = avancer(
        etat,
        (
            ordre(etat, 1, 0, Sell(ship_id=1, ore_id=2, quantity=10)),
            ordre(etat, 1, 0, Sell(ship_id=1, ore_id=2, quantity=20)),
        ),
    )
    codes = [r.refusal for r in apres.last_tick.results]
    assert codes == [None, RefusalCode.SUPERSEDED]
    assert apres.ships[0].cargo == (0, 90)


def test_ordre_refuse_a_la_reception_ne_compte_pas_pour_le_vaisseau() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    apres, _ = avancer(
        etat,
        (
            ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1), refus=RefusalCode.QUOTA_EXCEEDED),
            ordre(etat, 1, 2, Mine(ship_id=1, ore_id=1)),
        ),
    )
    assert refus(apres, 1) is RefusalCode.QUOTA_EXCEEDED
    assert refus(apres, 2) is None
    assert apres.ships[0].activity is Activity.MINING


def test_creation_de_personnage() -> None:
    etat = monde()
    soumis = ordre(
        etat,
        1,
        1,
        CreateCharacter(actor_kind=ActorKind.NPC),
        sender=None,
        category=OrderCategory.ADMIN,
    )
    apres, evenements = avancer(etat, (soumis,))
    assert [(a.id, a.kind, a.action_budget) for a in apres.actors] == [(1, ActorKind.NPC, 10)]
    navire = apres.ships[0]
    assert (
        navire.id,
        navire.owner_id,
        navire.system_id,
        navire.capacity,
        navire.cargo,
        navire.activity,
    ) == (
        1,
        1,
        1,
        100,
        (0, 0),
        Activity.IDLE,
    )
    assert apres.ledger.accounts[-1].owner_id == 1
    assert evenements[0].payload == CharacterCreated(
        actor_id=1, actor_kind=ActorKind.NPC, ship_id=1
    )
    assert evenements[0].visibility is Visibility.PUBLIC
    assert evenements[0].actor_kind is ActorKind.NPC
    resultat = apres.last_tick.results[0]
    assert (resultat.recipient_actor_id, resultat.accepted, resultat.budget_left) == (
        None,
        True,
        10,
    )
    deux = ordre(
        apres,
        2,
        1,
        CreateCharacter(actor_kind=ActorKind.HUMAN),
        sender=None,
        category=OrderCategory.ADMIN,
    )
    apres, _ = avancer(apres, (deux,))
    assert [a.id for a in apres.actors] == [1, 2]
    assert [v.id for v in apres.ships] == [1, 2]


def test_ordre_sans_emetteur_qui_n_est_pas_d_administration() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    apres, _ = avancer(etat, (ordre(etat, 1, 1, Mine(ship_id=1, ore_id=1), sender=None),))
    assert refus(apres, 1) is RefusalCode.FORBIDDEN_CATEGORY
    assert apres.last_tick.results[0].budget_left == 0


def test_ordre_d_administration_soumis_par_un_client() -> None:
    etat = monde((vaisseau(1, 1, 2),))
    soumis = ordre(
        etat, 1, 1, CreateCharacter(actor_kind=ActorKind.HUMAN), category=OrderCategory.ADMIN
    )
    apres, _ = avancer(etat, (soumis,))
    assert refus(apres, 1) is RefusalCode.FORBIDDEN_CATEGORY


def test_ordres_examines_par_acteur_puis_numero() -> None:
    etat = monde((vaisseau(1, 1, 2), vaisseau(2, 2, 2)))
    apres, _ = avancer(
        etat,
        (
            ordre(etat, 2, 1, Mine(ship_id=2, ore_id=1)),
            ordre(etat, 1, 3, Mine(ship_id=9, ore_id=1)),
            ordre(etat, 1, 2, Mine(ship_id=1, ore_id=1)),
        ),
    )
    assert [(r.order_id.actor_id, r.order_id.number) for r in apres.last_tick.results] == [
        (1, 2),
        (1, 3),
        (2, 1),
    ]


def test_regain_de_budget_plafonne() -> None:
    etat = monde((vaisseau(1, 1, 2),), budgets={1: 9})
    apres, _ = avancer(etat, (), 3)
    assert apres.actors[0].action_budget == 10
