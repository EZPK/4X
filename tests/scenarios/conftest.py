"""Scénarios en attente (docs/designs/niveau-2-m0-garde-fous.md, Technical Plan, point 10).

Chaque entrée de `en_attente.txt` est marquée « doit échouer » (`xfail(strict=True)`).
La session échoue sur une entrée sans scénario et sur un titre en double dans un même fichier.
"""

from pathlib import Path

import pytest
from pytest_bdd.gherkin_parser import Child, get_gherkin_document
from pytest_bdd.scenario import scenario_wrapper_template_registry

DOSSIER = Path(__file__).resolve().parent
LISTE = DOSSIER / "en_attente.txt"


def lire_en_attente() -> set[tuple[str, str]]:
    entrees: set[tuple[str, str]] = set()
    if not LISTE.is_file():
        return entrees
    for ligne in LISTE.read_text(encoding="utf-8").splitlines():
        propre = ligne.strip()
        if not propre or propre.startswith("#"):
            continue
        fichier, separateur, titre = propre.partition("::")
        if not separateur:
            raise pytest.UsageError(f"en_attente.txt : entrée sans « :: » : {propre}")
        entrees.add((fichier.strip(), titre.strip()))
    return entrees


def _titres(enfants: list[Child]) -> list[str]:
    titres: list[str] = []
    for enfant in enfants:
        if enfant.scenario is not None:
            titres.append(enfant.scenario.name)
        elif enfant.rule is not None:
            titres += _titres(enfant.rule.children)
    return titres


def lire_scenarios() -> dict[str, list[str]]:
    """Titres des scénarios de chaque `.feature`, lus dans le Gherkin, doublons compris."""
    scenarios: dict[str, list[str]] = {}
    for chemin in sorted(DOSSIER.rglob("*.feature")):
        document = get_gherkin_document(str(chemin))
        scenarios[chemin.relative_to(DOSSIER).as_posix()] = _titres(document.feature.children)
    return scenarios


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    scenarios = lire_scenarios()
    for fichier, titres in scenarios.items():
        doubles = sorted({titre for titre in titres if titres.count(titre) > 1})
        if doubles:
            raise pytest.UsageError(f"{fichier} : titre de scénario en double : {doubles}")
    en_attente = lire_en_attente()
    for fichier, titre in sorted(en_attente):
        if titre not in scenarios.get(fichier, []):
            raise pytest.UsageError(f"en_attente.txt : aucun scénario {fichier}::{titre}")
    for item in items:
        if not isinstance(item, pytest.Function):
            continue
        modele = scenario_wrapper_template_registry.get(item.obj)
        if modele is None:
            continue
        chemin = Path(modele.feature.filename).resolve()
        if not chemin.is_relative_to(DOSSIER):
            continue
        if (chemin.relative_to(DOSSIER).as_posix(), modele.name) in en_attente:
            item.add_marker(pytest.mark.xfail(strict=True, reason="scénario en attente"))
