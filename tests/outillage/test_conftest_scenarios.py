"""Tests du mécanisme « en attente » de `tests/scenarios/conftest.py` (plan détaillé, point 26).

Chaque test lance une session pytest imbriquée avec une copie de `conftest.py`, le scénario
d'exemple de `exemple/` et sa propre liste en attente.
"""

from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
EXEMPLE = Path(__file__).resolve().parent / "exemple"
TITRE = "Augmenter le compteur"


def preparer(pytester: pytest.Pytester, en_attente: str, feature: str | None = None) -> None:
    pytester.makeconftest((RACINE / "tests/scenarios/conftest.py").read_text(encoding="utf-8"))
    texte = feature or (EXEMPLE / "exemple.feature").read_text(encoding="utf-8")
    (pytester.path / "exemple.feature").write_text(texte, encoding="utf-8")
    etapes = (EXEMPLE / "steps_exemple.py").read_text(encoding="utf-8")
    pytester.makepyfile(
        test_exemple=etapes + '\nfrom pytest_bdd import scenarios\n\nscenarios("exemple.feature")\n'
    )
    (pytester.path / "en_attente.txt").write_text(en_attente, encoding="utf-8")


def feature_qui_echoue() -> str:
    texte = (EXEMPLE / "exemple.feature").read_text(encoding="utf-8")
    return texte.replace("Alors il vaut 1", "Alors il vaut 2")


def test_sans_entree_le_scenario_passe(pytester: pytest.Pytester) -> None:
    preparer(pytester, "")
    pytester.runpytest().assert_outcomes(passed=1)


def test_scenario_en_attente_qui_echoue(pytester: pytest.Pytester) -> None:
    preparer(pytester, f"exemple.feature::{TITRE}\n", feature_qui_echoue())
    resultat = pytester.runpytest()
    resultat.assert_outcomes(xfailed=1)
    assert resultat.ret == pytest.ExitCode.OK


def test_scenario_en_attente_qui_reussit(pytester: pytest.Pytester) -> None:
    preparer(pytester, f"exemple.feature::{TITRE}\n")
    resultat = pytester.runpytest()
    resultat.assert_outcomes(failed=1)
    assert resultat.ret == pytest.ExitCode.TESTS_FAILED


def test_entree_sans_scenario(pytester: pytest.Pytester) -> None:
    preparer(pytester, "exemple.feature::Titre inconnu\n")
    resultat = pytester.runpytest()
    assert resultat.ret == pytest.ExitCode.USAGE_ERROR
    resultat.stderr.fnmatch_lines(["*aucun scénario exemple.feature::Titre inconnu*"])


def test_entree_dans_un_fichier_inconnu(pytester: pytest.Pytester) -> None:
    preparer(pytester, f"autre.feature::{TITRE}\n")
    assert pytester.runpytest().ret == pytest.ExitCode.USAGE_ERROR


def test_titre_en_double(pytester: pytest.Pytester) -> None:
    texte = (EXEMPLE / "exemple.feature").read_text(encoding="utf-8")
    scenario = texte[texte.index("  Scénario:") :]
    preparer(pytester, "", texte + "\n" + scenario)
    resultat = pytester.runpytest()
    assert resultat.ret == pytest.ExitCode.USAGE_ERROR
    resultat.stderr.fnmatch_lines(["*titre de scénario en double*"])


def test_plan_de_scenario_en_attente(pytester: pytest.Pytester) -> None:
    plan = """# language: fr
Fonctionnalité: Compteur d'exemple

  Plan du Scénario: Augmenter le compteur
    Étant donné un compteur à <depart>
    Quand on l'augmente de 1
    Alors il vaut 0

    Exemples:
      | depart |
      | 0      |
      | 5      |
"""
    preparer(pytester, f"exemple.feature::{TITRE}\n", plan)
    resultat = pytester.runpytest()
    resultat.assert_outcomes(xfailed=2)
    assert resultat.ret == pytest.ExitCode.OK


def test_lignes_vides_et_commentaires_ignores(pytester: pytest.Pytester) -> None:
    preparer(pytester, f"# commentaire\n\n   \n# exemple.feature::{TITRE}\n")
    pytester.runpytest().assert_outcomes(passed=1)


def test_espaces_autour_de_l_entree(pytester: pytest.Pytester) -> None:
    preparer(pytester, f"   exemple.feature::{TITRE}   \n", feature_qui_echoue())
    pytester.runpytest().assert_outcomes(xfailed=1)
