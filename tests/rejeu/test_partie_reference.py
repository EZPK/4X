"""Tests de l'outil de régénération, sur des parties courtes (docs/designs/niveau-2-m1-noyau.md,
plan détaillé, point 27). La partie de référence elle-même n'est jouée qu'à la régénération."""

from pathlib import Path

import msgspec
import msgspec.structs
import pytest

from fourx.core.fingerprints import Fingerprints
from fourx.core.version import RULES_REVISION, rules_version
from fourx.core.world import generate
from fourx.server.order_log import OrderLog, import_jsonl
from fourx.server.tunables_loader import load_tunables
from tests.rejeu import partie_reference
from tests.rejeu.partie_reference import (
    Epuisement,
    Reference,
    jouer,
    lire_reference,
    rapport_de_differences,
    relever_epuisement,
    releves,
    texte_de_l_epuisement,
)

COURTS = {"jump_ticks": 5, "mining_rate": 50}


def empreinte(tick: int, ledger: str = "l") -> Fingerprints:
    return Fingerprints(
        tick=tick,
        systems="s",
        deposits="d",
        stations="st",
        actors="a",
        ships="sh",
        ledger=ledger,
        last_tick="t",
    )


def test_releves_tous_les_mille_ticks_et_au_dernier() -> None:
    suite = [empreinte(t) for t in range(1, 2_501)]
    assert [e.tick for e in releves(suite)] == [1_000, 2_000, 2_500]
    assert [e.tick for e in releves(suite[:2_000])] == [1_000, 2_000]
    assert releves([]) == ()


def test_rapport_sans_revision_precedente() -> None:
    nouvelle = Reference(rules_version="rules-1+x", fingerprints=(empreinte(1_000),))
    assert rapport_de_differences(None, nouvelle, 7, 123) == (
        f"Rapport de différences : aucune → rules-{RULES_REVISION}\n"
        "- révision précédente : aucune (première création des références)\n"
        "- rules_version : rules-1+x\n"
        "- ordres soumis : 7\n"
        "- relevés d'empreintes : 1\n"
        "- taille du dossier : 123 octets"
    )


def test_rapport_avec_revision_precedente(tmp_path: Path) -> None:
    precedente = tmp_path / "rules-0"
    precedente.mkdir()
    ancienne = Reference(rules_version="rules-0+x", fingerprints=(empreinte(1_000),))
    (precedente / "reference.json").write_bytes(msgspec.json.encode(ancienne))
    (precedente / "orders.jsonl").write_bytes(b"{}\n{}\n{}\n")
    nouvelle = Reference(rules_version="rules-1+y", fingerprints=(empreinte(1_000, "autre"),))
    taille = sum(f.stat().st_size for f in precedente.iterdir())
    rapport = rapport_de_differences(precedente, nouvelle, 5, 999).splitlines()
    assert rapport == [
        f"Rapport de différences : rules-0 → rules-{RULES_REVISION}",
        "- rules_version : rules-0+x → rules-1+y",
        "- ordres soumis : 2 → 5",
        "- premier relevé d'empreintes qui diffère : tick 1000 : ledger",
        f"- taille du dossier : {taille} → 999 octets",
    ]


def test_texte_de_l_epuisement() -> None:
    assert texte_de_l_epuisement(Epuisement()) == "Gisements vidés : aucun\nDépartages : aucun"
    releve = Epuisement(vides={6: [9, 12], 4: [20]}, departages={6: [9]})
    assert texte_de_l_epuisement(releve) == (
        "Gisements vidés : deposit_4 : 1 fois (premier au tick 20) ; "
        "deposit_6 : 2 fois (premier au tick 9)\n"
        "Départages : deposit_6 : 1 fois (premier au tick 9)"
    )


def test_releve_des_gisements_vides_et_des_departages(tmp_path: Path) -> None:
    """Gisements petits : les PNJ les vident. Chaque départage relevé tombe sur un tick où le
    gisement se vide (la demande dépassait le stock)."""
    tunables = msgspec.structs.replace(load_tunables(), deposit_stock=120, **COURTS)
    run_dir = jouer(tmp_path, tunables, ticks=600)
    journal = OrderLog(run_dir / "orders.sqlite")
    ordres = journal.orders_by_tick()
    journal.close()
    releve = relever_epuisement(generate(1, tunables), ordres, tunables)
    assert releve.vides
    assert releve.departages
    for gisement, ticks in releve.departages.items():
        assert set(ticks) <= set(releve.vides[gisement])


def preparer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, erreurs: list[str]
) -> tuple[Path, list[str]]:
    """Références dans un dossier temporaire, partie de 300 ticks, écarts imposés."""
    references = tmp_path / "references"
    monkeypatch.setattr(partie_reference, "REFERENCES", references)
    monkeypatch.setattr(partie_reference, "TICKS", 300)
    jouer_court = partie_reference.jouer
    monkeypatch.setattr(
        partie_reference,
        "jouer",
        lambda d, t: jouer_court(d, msgspec.structs.replace(t, **COURTS), 300),
    )
    monkeypatch.setattr(partie_reference, "ecarts", lambda *_: ((), erreurs))
    affiches: list[str] = []
    return references, affiches


def test_la_regeneration_refuse_d_ecrire_hors_des_bornes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    references, affiches = preparer(monkeypatch, tmp_path, ["fenêtre 1-10000 : aucune vente"])
    (references / "rules-0").mkdir(parents=True)
    with pytest.raises(AssertionError, match="références non écrites\nfenêtre 1-10000"):
        partie_reference.regenerer(tmp_path / "runs", load_tunables(), affiches.append)
    assert sorted(p.name for p in references.iterdir()) == ["rules-0"]


def test_la_regeneration_remplace_l_ancienne_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    references, affiches = preparer(monkeypatch, tmp_path, [])
    ancienne = references / "rules-0"
    ancienne.mkdir(parents=True)
    (ancienne / "reference.json").write_bytes(
        msgspec.json.encode(Reference(rules_version="rules-0+x", fingerprints=()))
    )
    (ancienne / "orders.jsonl").write_bytes(b"{}\n")
    tunables = load_tunables()
    partie_reference.regenerer(tmp_path / "runs", tunables, affiches.append)
    nouvelle = references / f"rules-{RULES_REVISION}"
    assert sorted(p.name for p in references.iterdir()) == [nouvelle.name]
    assert sorted(p.name for p in nouvelle.iterdir()) == ["orders.jsonl", "reference.json"]
    reference = lire_reference(nouvelle)
    courts = msgspec.structs.replace(tunables, **COURTS)
    assert reference.rules_version == rules_version(courts)
    assert [e.tick for e in reference.fingerprints] == [300]
    en_tete, ordres = import_jsonl(nouvelle / "orders.jsonl")
    assert (en_tete.world_seed, en_tete.last_tick, len(ordres)) == (1, 300, 300)
    assert any(a.startswith("Bornes : ") for a in affiches)
    assert any(
        a.startswith(f"Rapport de différences : rules-0 → rules-{RULES_REVISION}") for a in affiches
    )
    assert any(a.startswith("Gisements vidés : ") for a in affiches)
