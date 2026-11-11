"""Tests de fourx.core.ledger (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 3)."""

import pytest

from fourx.core.ledger import (
    DESTRUCTION_ACCOUNT_ID,
    ISSUANCE_ACCOUNT_ID,
    Account,
    Ledger,
    compte,
    ledger_vide,
    money_supply,
    ouvrir,
    post,
)
from fourx.schema.ledger import AccountKind, LedgerEntry, Reason


def registre() -> Ledger:
    ledger, _ = ouvrir(ledger_vide(), AccountKind.PERSONAL_WALLET, 1)
    return ledger


def test_registre_vide() -> None:
    ledger = ledger_vide()
    assert [(c.id, c.kind) for c in ledger.accounts] == [
        (ISSUANCE_ACCOUNT_ID, AccountKind.ISSUANCE),
        (DESTRUCTION_ACCOUNT_ID, AccountKind.DESTRUCTION),
    ]
    assert ISSUANCE_ACCOUNT_ID == 1 and DESTRUCTION_ACCOUNT_ID == 2
    assert ledger.issued_by_reason == (0, 0) == ledger.destroyed_by_reason
    assert ledger.tick_entries == ()
    assert all(c.balance == 0 and c.owner_id is None for c in ledger.accounts)


def test_ouvrir_un_compte() -> None:
    ledger, ident = ouvrir(ledger_vide(), AccountKind.PERSONAL_WALLET, 7)
    assert ident == 3
    assert ledger.accounts[-1] == Account(
        id=3, kind=AccountKind.PERSONAL_WALLET, owner_id=7, balance=0
    )
    ledger, ident = ouvrir(ledger, AccountKind.PERSONAL_WALLET, 8)
    assert ident == 4


def test_vente_et_taxe() -> None:
    ledger = registre()
    vente = LedgerEntry(
        debit_account_id=1, credit_account_id=3, amount=1500, reason=Reason.ORE_SALE, cause=None
    )
    taxe = LedgerEntry(
        debit_account_id=3, credit_account_id=2, amount=150, reason=Reason.SALE_TAX, cause=None
    )
    ledger = post(post(ledger, vente), taxe)
    assert [c.balance for c in ledger.accounts] == [-1500, 150, 1350]
    assert sum(c.balance for c in ledger.accounts) == 0
    assert ledger.issued_by_reason == (1500, 0)
    assert ledger.destroyed_by_reason == (0, 150)
    assert ledger.tick_entries == (vente, taxe)
    assert money_supply(ledger) == 1350


def test_ecriture_entre_portefeuilles_sans_compteur() -> None:
    ledger, _ = ouvrir(registre(), AccountKind.PERSONAL_WALLET, 2)
    ledger = post(
        ledger,
        LedgerEntry(
            debit_account_id=1, credit_account_id=3, amount=10, reason=Reason.ORE_SALE, cause=None
        ),
    )
    ledger = post(
        ledger,
        LedgerEntry(
            debit_account_id=3, credit_account_id=4, amount=4, reason=Reason.ORE_SALE, cause=None
        ),
    )
    assert ledger.issued_by_reason == (10, 0)
    assert ledger.destroyed_by_reason == (0, 0)
    assert compte(ledger, 3).balance == 6 and compte(ledger, 4).balance == 4
    assert money_supply(ledger) == 10


def test_masse_monetaire_compte_corporations_et_sequestres() -> None:
    ledger = Ledger(
        accounts=(
            Account(id=1, kind=AccountKind.ISSUANCE, owner_id=None, balance=-60),
            Account(id=2, kind=AccountKind.DESTRUCTION, owner_id=None, balance=5),
            Account(id=3, kind=AccountKind.PERSONAL_WALLET, owner_id=1, balance=10),
            Account(id=4, kind=AccountKind.CORPORATION_WALLET, owner_id=1, balance=20),
            Account(id=5, kind=AccountKind.ESCROW, owner_id=1, balance=25),
        ),
        tick_entries=(),
        issued_by_reason=(0, 0),
        destroyed_by_reason=(0, 0),
    )
    assert money_supply(ledger) == 55


@pytest.mark.parametrize(("debit", "credit", "montant"), [(1, 3, 0), (1, 3, -5), (3, 3, 5)])
def test_ecriture_invalide(debit: int, credit: int, montant: int) -> None:
    with pytest.raises(ValueError):
        post(
            registre(),
            LedgerEntry(
                debit_account_id=debit,
                credit_account_id=credit,
                amount=montant,
                reason=Reason.ORE_SALE,
                cause=None,
            ),
        )


def test_compte_inconnu() -> None:
    with pytest.raises(KeyError):
        compte(registre(), 99)
