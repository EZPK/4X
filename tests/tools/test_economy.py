"""Tests des grandeurs de l'économie par fenêtre (docs/designs/niveau-2-m1-noyau.md, Technical
Plan, points 9 et 13)."""

from pathlib import Path

import msgspec
import msgspec.structs
import pytest

from fourx.__main__ import creer_pnj
from fourx.clients.npc_host import NpcHost
from fourx.core.ledger import money_supply
from fourx.policies.scripted_miner import decide
from fourx.schema.events import Arrived, Event, LedgerEntryRecorded, Sale
from fourx.schema.ledger import LedgerEntry, Reason
from fourx.schema.visibility import Visibility
from fourx.server.game import Game
from fourx.server.tunables_loader import load_tunables
from fourx.tools.economy import WindowStats, window_stats

EMISSION, DESTRUCTION, PORTEFEUILLE_A, PORTEFEUILLE_B = 1, 2, 3, 4


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


def ecriture(tick: int, debit: int, credit: int, montant: int, motif: Reason) -> Event:
    entree = LedgerEntry(
        debit_account_id=debit, credit_account_id=credit, amount=montant, reason=motif, cause=None
    )
    return evenement(tick, LedgerEntryRecorded(entry=entree))


def vente(tick: int, paiement: int, taxe: int) -> list[Event]:
    return [
        ecriture(tick, EMISSION, PORTEFEUILLE_A, paiement, Reason.ORE_SALE),
        ecriture(tick, PORTEFEUILLE_A, DESTRUCTION, taxe, Reason.SALE_TAX),
    ]


def test_fenetres_de_dix_mille_ticks_par_defaut() -> None:
    fenetre, suivante = window_stats([*vente(10_000, 1500, 150), *vente(10_001, 30, 3)])
    assert suivante.first_tick == 10_001
    assert suivante.issued_by_reason == (30, 0)
    assert fenetre == WindowStats(
        first_tick=1,
        issued_by_reason=(1500, 0),
        destroyed_by_reason=(0, 150),
        money_supply_growth=1350,
        money_supply_end=1350,
    )


def test_bornes_des_fenetres_fenetre_vide_et_masse_cumulee() -> None:
    evenements = [*vente(3, 100, 10), *vente(4, 200, 20), *vente(10, 50, 5), *vente(31, 400, 40)]
    fenetres = window_stats(evenements, window=10)
    assert [f.first_tick for f in fenetres] == [1, 11, 21, 31]
    assert [f.issued_by_reason for f in fenetres] == [(350, 0), (0, 0), (0, 0), (400, 0)]
    assert [f.destroyed_by_reason for f in fenetres] == [(0, 35), (0, 0), (0, 0), (0, 40)]
    assert [f.money_supply_growth for f in fenetres] == [315, 0, 0, 360]
    assert [f.money_supply_end for f in fenetres] == [315, 315, 315, 675]


def test_un_virement_entre_portefeuilles_ne_compte_ni_en_emission_ni_en_destruction() -> None:
    virement = ecriture(2, PORTEFEUILLE_A, PORTEFEUILLE_B, 70, Reason.ORE_SALE)
    (fenetre,) = window_stats([virement], window=10)
    assert (fenetre.issued_by_reason, fenetre.destroyed_by_reason) == ((0, 0), (0, 0))
    assert (fenetre.money_supply_growth, fenetre.money_supply_end) == (0, 0)


def test_la_derniere_fenetre_est_celle_du_dernier_evenement_quel_qu_il_soit() -> None:
    arrivee = evenement(25, Arrived(ship_id=1, system_id=2))
    fenetres = window_stats([*vente(1, 10, 1), arrivee], window=10)
    assert [f.first_tick for f in fenetres] == [1, 11, 21]
    assert fenetres[-1].money_supply_end == 9


def test_ordre_des_evenements_indifferent() -> None:
    evenements = [*vente(15, 100, 10), *vente(2, 30, 3)]
    assert window_stats(evenements, window=10) == window_stats(evenements[::-1], window=10)


def test_aucun_evenement_aucune_fenetre() -> None:
    assert window_stats([], window=10) == ()


def test_une_fenetre_compte_au_moins_un_tick() -> None:
    with pytest.raises(ValueError, match="^une fenêtre compte au moins un tick$"):
        window_stats(vente(1, 10, 1), window=0)
    fenetres = window_stats([*vente(1, 10, 1), *vente(2, 20, 2)], window=1)
    assert [(f.first_tick, f.money_supply_end) for f in fenetres] == [(1, 9), (2, 27)]


def test_concorde_avec_le_registre_d_une_partie_jouee(tmp_path: Path) -> None:
    """Sur une partie jouée par les PNJ (réglages courts), les sommes des fenêtres sont les
    compteurs cumulés du registre, et la masse finale est la masse monétaire de l'état."""
    tunables = msgspec.structs.replace(load_tunables(), jump_ticks=5, mining_rate=50)
    jeu = Game(tmp_path, world_seed=1, tunables=tunables)
    for ident in creer_pnj(jeu, 1, tunables):
        jeu.attach(ident, NpcHost(ident, decide))
    jeu.advance(1_500)
    jeu.close()
    decodeur = msgspec.json.Decoder(Event)
    lignes = (jeu.run_dir / "events.jsonl").read_bytes().splitlines()
    evenements = [decodeur.decode(ligne) for ligne in lignes if ligne.strip()]
    assert any(isinstance(e.payload, Sale) for e in evenements)
    fenetres = window_stats(evenements, window=500)
    registre = jeu.state.ledger
    emis = tuple(sum(f.issued_by_reason[i] for f in fenetres) for i in range(len(Reason)))
    detruit = tuple(sum(f.destroyed_by_reason[i] for f in fenetres) for i in range(len(Reason)))
    assert emis == registre.issued_by_reason
    assert detruit == registre.destroyed_by_reason
    assert fenetres[-1].money_supply_end == money_supply(registre)
