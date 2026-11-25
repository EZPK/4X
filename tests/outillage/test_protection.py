"""Tests du script de la tâche `protection` du workflow de nuit, sur une réponse d'exemple.

Niveau 2 de M1, plan détaillé, points 30 bis et 31 bis.
"""

import copy
import json
from collections.abc import Callable
from types import ModuleType

import pytest

ATTENDUS = ["lint", "tests", "rejeu"]
REPONSE: dict[str, object] = {
    "name": "main",
    "protected": True,
    "protection": {
        "enabled": True,
        "required_status_checks": {
            "enforcement_level": "everyone",
            "contexts": ["rejeu", "lint", "tests"],
            "checks": [],
        },
    },
}


@pytest.fixture
def protection(charger_script: Callable[[str], ModuleType]) -> ModuleType:
    return charger_script(".github/scripts/protection.py")


def test_protection_en_place(protection: ModuleType) -> None:
    assert protection.verifier(REPONSE, ATTENDUS) == []


def test_branche_non_protegee(protection: ModuleType) -> None:
    reponse = {"name": "main", "protected": False}
    assert protection.verifier(reponse, ATTENDUS) == [
        "main n'est pas protégée",
        "aucun contrôle exigé",
    ]


def test_niveau_et_controles_differents(protection: ModuleType) -> None:
    reponse = copy.deepcopy(REPONSE)
    controles = reponse["protection"]["required_status_checks"]  # type: ignore[index]
    controles["enforcement_level"] = "non_admins"
    controles["contexts"] = ["lint", "tests"]
    assert protection.verifier(reponse, ATTENDUS) == [
        "enforcement_level vaut 'non_admins' au lieu de 'everyone'",
        "contrôles exigés ['lint', 'tests'] au lieu de ['lint', 'rejeu', 'tests']",
    ]


def test_controles_attendus_lus_dans_la_reference(protection: ModuleType) -> None:
    with open(protection.REFERENCE, encoding="utf-8") as fichier:
        reference = json.load(fichier)
    assert protection.controles_attendus() == reference["required_status_checks"]["contexts"]


def test_main_lit_l_api_avec_le_jeton(
    protection: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    vus: list[str | None] = []

    class Reponse:
        def __enter__(self) -> Reponse:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(REPONSE).encode()

    def ouvrir(requete: object, timeout: int) -> Reponse:
        vus.append(requete.get_header("Authorization"))  # type: ignore[attr-defined]
        assert requete.full_url == protection.URL  # type: ignore[attr-defined]
        assert timeout == 30
        return Reponse()

    monkeypatch.setattr(protection.urllib.request, "urlopen", ouvrir)
    monkeypatch.setattr(protection, "controles_attendus", lambda: ATTENDUS)
    monkeypatch.setenv("GITHUB_TOKEN", "jeton-de-test")
    assert protection.main() == 0
    assert vus == ["Bearer jeton-de-test"]
    assert capsys.readouterr().out == "Protection de main en place.\n"
    monkeypatch.setattr(protection, "controles_attendus", lambda: ["autre"])
    assert protection.main() == 1
    assert "contrôles exigés" in capsys.readouterr().out
