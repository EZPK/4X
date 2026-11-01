"""Tests de `.github/scripts/en_attente.py` (plan détaillé, point 26)."""

from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

ENTETE = "# Une entrée par ligne.\n"
SANS_FEATURE = '{"filename": "tests/scenarios/en_attente.txt", "previous_filename": null}\n'
AVEC_FEATURE = (
    SANS_FEATURE + '{"filename": "tests/scenarios/a.feature", "previous_filename": null}\n'
)


@pytest.fixture
def lancer(
    charger_script: Callable[[str], ModuleType], tmp_path: Path
) -> Callable[[str, str, str], int]:
    module = charger_script(".github/scripts/en_attente.py")

    def lancer(avant: str, apres: str, fichiers: str) -> int:
        chemins = []
        for nom, contenu in (("avant", avant), ("apres", apres), ("fichiers", fichiers)):
            chemin = tmp_path / nom
            chemin.write_text(contenu, encoding="utf-8")
            chemins += [f"--{nom}", str(chemin)]
        return int(module.principal(chemins))

    return lancer


def test_ajout_sans_feature_refuse(
    lancer: Callable[[str, str, str], int], capsys: pytest.CaptureFixture[str]
) -> None:
    assert lancer(ENTETE, ENTETE + "a.feature::Titre\n", SANS_FEATURE) == 1
    assert "entrée ajoutée : a.feature::Titre" in capsys.readouterr().out


def test_ajout_avec_feature_permis(lancer: Callable[[str, str, str], int]) -> None:
    assert lancer(ENTETE, ENTETE + "a.feature::Titre\n", AVEC_FEATURE) == 0


def test_ajout_avec_feature_renomme_permis(lancer: Callable[[str, str, str], int]) -> None:
    renomme = SANS_FEATURE + '{"filename": "b.txt", "previous_filename": "a.feature"}\n'
    assert lancer(ENTETE, ENTETE + "a.feature::Titre\n", renomme) == 0


def test_retrait_permis(lancer: Callable[[str, str, str], int]) -> None:
    assert lancer(ENTETE + "a.feature::Titre\n", ENTETE, SANS_FEATURE) == 0


def test_commentaire_modifie_n_est_pas_un_ajout(lancer: Callable[[str, str, str], int]) -> None:
    assert lancer(ENTETE, "# Un autre commentaire.\n\n   \n", SANS_FEATURE) == 0


def test_espaces_normalises(lancer: Callable[[str, str, str], int]) -> None:
    assert lancer("a.feature::Titre\n", "   a.feature::Titre   \n", SANS_FEATURE) == 0


@pytest.mark.parametrize(
    ("avant", "apres", "attendu"),
    [("", "a.feature::Titre\n", 1), ("a.feature::Titre\n", "", 0), ("", "", 0)],
)
def test_fichier_absent_dans_une_version(
    lancer: Callable[[str, str, str], int], avant: str, apres: str, attendu: int
) -> None:
    assert lancer(avant, apres, SANS_FEATURE) == attendu


def test_erreur_d_entree(lancer: Callable[[str, str, str], int]) -> None:
    assert lancer("", "", "pas du json\n") == 2
