"""Registre en partie double (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 3).

L'état garde les soldes, les écritures du tick en cours et des compteurs cumulés d'émission et
de destruction par motif ; l'historique des écritures ne vit que dans les événements.
"""

from typing import Annotated

import msgspec
import msgspec.structs

from fourx.schema.ledger import AccountKind, LedgerEntry, Reason
from fourx.schema.types import Id, Int64
from fourx.schema.visibility import Visibility, visible

ADMIN = visible(Visibility.ADMIN)
PRIVATE = visible(Visibility.PRIVATE)

ISSUANCE_ACCOUNT_ID = 1
DESTRUCTION_ACCOUNT_ID = 2
MASSE_MONETAIRE = (AccountKind.PERSONAL_WALLET, AccountKind.CORPORATION_WALLET, AccountKind.ESCROW)


class Account(msgspec.Struct, frozen=True):
    id: Annotated[Id, ADMIN]
    kind: Annotated[AccountKind, ADMIN]
    owner_id: Annotated[Id | None, ADMIN]
    balance: Annotated[Int64, PRIVATE]


class Ledger(msgspec.Struct, frozen=True):
    accounts: Annotated[tuple[Account, ...], ADMIN]
    tick_entries: Annotated[tuple[LedgerEntry, ...], ADMIN]
    # Compteurs indexés dans l'ordre de déclaration de Reason.
    issued_by_reason: Annotated[tuple[Int64, ...], ADMIN]
    destroyed_by_reason: Annotated[tuple[Int64, ...], ADMIN]


def ledger_vide() -> Ledger:
    """Le registre d'un monde neuf : compte d'émission (1) et compte de destruction (2)."""
    zeros = (0,) * len(Reason)
    return Ledger(
        accounts=(
            Account(id=ISSUANCE_ACCOUNT_ID, kind=AccountKind.ISSUANCE, owner_id=None, balance=0),
            Account(
                id=DESTRUCTION_ACCOUNT_ID, kind=AccountKind.DESTRUCTION, owner_id=None, balance=0
            ),
        ),
        tick_entries=(),
        issued_by_reason=zeros,
        destroyed_by_reason=zeros,
    )


def money_supply(ledger: Ledger) -> int:
    """Somme des portefeuilles personnels, des portefeuilles de corporation et des séquestres."""
    return sum(c.balance for c in ledger.accounts if c.kind in MASSE_MONETAIRE)


def compte(ledger: Ledger, account_id: int) -> Account:
    for c in ledger.accounts:
        if c.id == account_id:
            return c
    raise KeyError(account_id)


def ouvrir(ledger: Ledger, kind: AccountKind, owner_id: int) -> tuple[Ledger, int]:
    """Ouvre un compte au prochain identifiant libre ; renvoie le registre et l'identifiant."""
    nouveau = max(c.id for c in ledger.accounts) + 1
    compte_neuf = Account(id=nouveau, kind=kind, owner_id=owner_id, balance=0)
    return msgspec.structs.replace(ledger, accounts=(*ledger.accounts, compte_neuf)), nouveau


def _ajoute(compteurs: tuple[int, ...], reason: Reason, montant: int) -> tuple[int, ...]:
    rang = list(Reason).index(reason)
    return tuple(v + montant if i == rang else v for i, v in enumerate(compteurs))


def post(ledger: Ledger, entry: LedgerEntry) -> Ledger:
    """Passe une écriture : débite un compte, crédite l'autre, et tient les compteurs."""
    if entry.amount <= 0:
        raise ValueError("une écriture porte un montant positif")
    if entry.debit_account_id == entry.credit_account_id:
        raise ValueError("une écriture relie deux comptes différents")
    debit = compte(ledger, entry.debit_account_id)
    credit = compte(ledger, entry.credit_account_id)
    comptes = tuple(
        msgspec.structs.replace(c, balance=c.balance - entry.amount)
        if c.id == debit.id
        else msgspec.structs.replace(c, balance=c.balance + entry.amount)
        if c.id == credit.id
        else c
        for c in ledger.accounts
    )
    emis = ledger.issued_by_reason
    detruit = ledger.destroyed_by_reason
    if debit.kind is AccountKind.ISSUANCE:
        emis = _ajoute(emis, entry.reason, entry.amount)
    if credit.kind is AccountKind.DESTRUCTION:
        detruit = _ajoute(detruit, entry.reason, entry.amount)
    return Ledger(
        accounts=comptes,
        tick_entries=(*ledger.tick_entries, entry),
        issued_by_reason=emis,
        destroyed_by_reason=detruit,
    )
