"""Tests des bornes de l'économie (docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 27)."""

import msgspec
import msgspec.structs
import pytest

from fourx.core.world import generate
from fourx.schema.events import Event, LedgerEntryRecorded, Sale
from fourx.schema.ledger import LedgerEntry, Reason
from fourx.schema.visibility import Visibility
from fourx.server.tunables_loader import load_tunables
from tests.economie.bornes import Bornes, bornes, distances, ecarts, taxe


def evenement(tick: int, payload: object) -> Event:
    return Event(
        tick=tick,
        seq=0,
        event_schema_version=0,
        rules_version="r",
        actor_id=None,
        actor_kind=None,
        policy_id=None,
        policy_version=None,
        causation_id=None,
        visibility=Visibility.ADMIN,
        payload=payload,  # type: ignore[arg-type]
    )


def vente(tick: int, paiement: int, taxe_ecrite: int) -> list[Event]:
    """Une vente : l'événement Sale, l'écriture d'émission et l'écriture de taxe."""

    def ecriture(debit: int, credit: int, montant: int, motif: Reason) -> Event:
        entree = LedgerEntry(
            debit_account_id=debit,
            credit_account_id=credit,
            amount=montant,
            reason=motif,
            cause=None,
        )
        return evenement(tick, LedgerEntryRecorded(entry=entree))

    return [
        evenement(
            tick,
            Sale(
                ship_id=1, ore_id=2, quantity=1, price=paiement, payment=paiement, tax=taxe_ecrite
            ),
        ),
        ecriture(1, 3, paiement, Reason.ORE_SALE),
        ecriture(3, 2, taxe_ecrite, Reason.SALE_TAX),
    ]


LIMITES = Bornes(
    fenetre=10,
    n_pnj=1,
    p_max=15,
    d_min=0,
    duree_minimale_d_un_cycle=5,
    cycles_max_par_fenetre=3,
    emission_max=1000,
)


def test_taxe_arrondie_vers_le_haut() -> None:
    assert taxe(1500, 1000) == 150
    assert taxe(1501, 1000) == 151
    assert taxe(1, 1) == 1
    assert taxe(0, 1000) == 0


def test_distances_en_sauts() -> None:
    etat = generate(1, load_tunables())
    dist = distances(etat, etat.systems[0].id)
    assert dist[etat.systems[0].id] == 0
    assert set(dist) == {s.id for s in etat.systems}
    for s in etat.systems:
        for v in s.neighbors:
            assert abs(dist[s.id] - dist[v]) <= 1


def test_bornes_de_la_graine_1() -> None:
    """Graine 1 : une station et un gisement partagent un système (d_min = 0), p_max = 15 ;
    C_min = 2 × 0 × 400 + 2000 ÷ 1 = 2 000 ; b' = ⌈10 000 ÷ 2 000⌉ + 1 = 6 ;
    émission max = 5 × 6 × 2 000 × 15 = 900 000 pour 5 PNJ."""
    tunables = load_tunables()
    assert (tunables.jump_ticks, tunables.cargo_capacity, tunables.mining_rate) == (400, 2000, 1)
    assert bornes(generate(1, tunables), 5, tunables) == Bornes(
        fenetre=10_000,
        n_pnj=5,
        p_max=15,
        d_min=0,
        duree_minimale_d_un_cycle=2000,
        cycles_max_par_fenetre=6,
        emission_max=900_000,
    )


def test_bornes_avec_trajet_et_minage_arrondi() -> None:
    """Sur la première graine sans colocalisation, C_min compte l'aller-retour ; M arrondi vers le
    bas (2 000 ÷ 3 = 666)."""
    tunables = msgspec.structs.replace(load_tunables(), mining_rate=3)
    graine, etat, limites = next(
        (g, e, b)
        for g in range(1, 200)
        if (b := bornes(e := generate(g, tunables), 2, tunables)).d_min > 0
    )
    assert graine > 1
    c_min = 2 * limites.d_min * 400 + 666
    assert limites.duree_minimale_d_un_cycle == c_min
    assert limites.cycles_max_par_fenetre == -(-10_000 // c_min) + 1
    p_max = max(p for s in etat.stations for p in s.ore_prices)
    assert limites.emission_max == 2 * limites.cycles_max_par_fenetre * 2000 * p_max


def test_un_cycle_dure_au_moins_un_tick() -> None:
    tunables = msgspec.structs.replace(load_tunables(), mining_rate=5000)
    with pytest.raises(ValueError, match="au moins un tick"):
        bornes(generate(1, tunables), 1, tunables)


def test_aucun_ecart() -> None:
    evenements = [*vente(2, 150, 15), *vente(12, 100, 10)]
    fenetres, erreurs = ecarts(evenements, LIMITES, 1000, 2)
    assert erreurs == []
    assert [f.first_tick for f in fenetres] == [1, 11]


def test_ecarts_releves() -> None:
    evenements = [
        *vente(2, 1200, 120),  # au-dessus de l'émission max
        *vente(12, 100, 9),  # taxe écrite 9, attendue 10
        evenement(25, LedgerEntryRecorded(entry=LedgerEntry(1, 3, 5, Reason.SALE_TAX, None))),
    ]
    _, erreurs = ecarts(evenements, LIMITES, 1000, 4)
    assert erreurs == [
        "3 fenêtres au lieu de 4",
        "fenêtre 1-10 : émission 1200 au-dessus de 1000",
        "fenêtre 1-10 : croissance 1080 hors de [0, émission max]",
        "fenêtre 11-20 : destruction 9, taxes des ventes 10",
        "fenêtre 21-30 : aucune vente",
    ]
