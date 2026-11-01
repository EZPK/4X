"""Tests de `.github/scripts/motifs.py` et `.github/scripts/garde.py` (plan détaillé, point 26)."""

import json
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ETIQUETTE = "fichiers protégés modifiés"


@pytest.fixture
def motifs(charger_script: Callable[[str], ModuleType]) -> ModuleType:
    return charger_script(".github/scripts/motifs.py")


@pytest.fixture
def garde(charger_script: Callable[[str], ModuleType]) -> ModuleType:
    return charger_script(".github/scripts/garde.py")


def evenement(body: str | None = "", etiquettes: list[str] | None = None) -> dict[str, Any]:
    return {"pull_request": {"body": body, "labels": [{"name": nom} for nom in etiquettes or []]}}


@pytest.mark.parametrize(
    ("chemin", "motif", "attendu"),
    [
        ("tests/scenarios/a.feature", "tests/scenarios/**/*.feature", True),
        ("tests/scenarios/x/a.feature", "tests/scenarios/**/*.feature", True),
        ("tests/scenarios/x/y/z/a.feature", "tests/scenarios/**/*.feature", True),
        ("tests/scenarios/a.py", "tests/scenarios/**/*.feature", False),
        (".github/workflows/ci.yml", ".github/**", True),
        (".github", ".github/**", True),
        (".githubx/a", ".github/**", False),
        ("docs/glossaire.md", "docs/*.md", True),
        ("docs/designs/a.md", "docs/*.md", False),
        ("CLAUDE.md", "CLAUDE.md", True),
        ("CLAUDEXmd", "CLAUDE.md", False),
        ("src/CLAUDE.md", "CLAUDE.md", False),
    ],
)
def test_traduction_des_motifs(motifs: ModuleType, chemin: str, motif: str, attendu: bool) -> None:
    assert motifs.correspond(chemin, motif) is attendu


def test_lignes_vides_et_commentaires_ignores(motifs: ModuleType) -> None:
    assert motifs.lire_motifs(["", "  ", "# commentaire", "  a/**  ", "b.txt"]) == ["a/**", "b.txt"]


def test_vraie_liste_des_chemins_proteges(motifs: ModuleType, racine: Path) -> None:
    liste = motifs.lire_fichier_motifs(racine / ".github/chemins-proteges.txt")
    assert len(liste) == 22
    assert motifs.est_couvert(".github/workflows/garde.yml", liste)
    assert motifs.est_couvert("tests/scenarios/steps/etapes.py", liste)
    assert not motifs.est_couvert("tests/scenarios/en_attente.txt", liste)
    assert not motifs.est_couvert("src/fourx/core/__init__.py", liste)


def test_plusieurs_objets_et_previous_filename_null(garde: ModuleType) -> None:
    texte = (
        '{"filename": "a.py", "previous_filename": null}\n'
        "\n"
        '{"filename": "b.py", "previous_filename": "c.py"}\n'
    )
    assert garde.lire_fichiers_modifies(texte) == [("a.py", None), ("b.py", "c.py")]


@pytest.mark.parametrize("ligne", ["pas du json", '{"previous_filename": null}', "[1, 2]"])
def test_ligne_invalide(garde: ModuleType, ligne: str) -> None:
    with pytest.raises(garde.ErreurEntree):
        garde.lire_fichiers_modifies(ligne)


def test_chemin_protege_modifie_pose_l_etiquette(garde: ModuleType) -> None:
    resultat = garde.analyser(["CLAUDE.md"], [("CLAUDE.md", None)], evenement("texte"))
    assert resultat["etiquette"] == "poser"
    assert resultat["description"].startswith(garde.DEBUT)
    assert resultat["description"].endswith("\n\ntexte")


def test_chemin_protege_renomme(garde: ModuleType) -> None:
    resultat = garde.analyser(["CLAUDE.md"], [("ailleurs.md", "CLAUDE.md")], evenement())
    assert resultat["etiquette"] == "poser"
    assert "`ailleurs.md`" in resultat["description"]


def test_etiquette_deja_presente_rien(garde: ModuleType) -> None:
    resultat = garde.analyser(["CLAUDE.md"], [("CLAUDE.md", None)], evenement("", [ETIQUETTE]))
    assert resultat["etiquette"] == "rien"


def test_fichier_ordinaire_etiquette_absente_rien(garde: ModuleType) -> None:
    resultat = garde.analyser(["CLAUDE.md"], [("src/a.py", None)], evenement("texte", ["autre"]))
    assert resultat == {
        "etiquette": "rien",
        "description": "texte",
        "resume": "Aucun chemin protégé modifié.",
    }


def test_fichier_ordinaire_etiquette_presente_retirer(garde: ModuleType) -> None:
    resultat = garde.analyser(["CLAUDE.md"], [("src/a.py", None)], evenement("", [ETIQUETTE]))
    assert resultat["etiquette"] == "retirer"


def test_bloc_retire_sans_chemin_protege(garde: ModuleType) -> None:
    ancienne = garde.construire_bloc(["CLAUDE.md"]) + "\n\nrésumé EGM"
    resultat = garde.analyser(["CLAUDE.md"], [("src/a.py", None)], evenement(ancienne))
    assert resultat["description"] == "résumé EGM"


def test_bloc_remplace_jamais_duplique(garde: ModuleType) -> None:
    ancien = garde.construire_bloc(["vieux.md"])
    description = f"{ancien}\n\nrésumé EGM\n\n{ancien}"
    resultat = garde.analyser(["CLAUDE.md"], [("CLAUDE.md", None)], evenement(description))
    assert resultat["description"].count(garde.DEBUT) == 1
    assert resultat["description"].count(garde.FIN) == 1
    assert "vieux.md" not in resultat["description"]
    assert resultat["description"].startswith(garde.DEBUT)
    assert resultat["description"].endswith("résumé EGM\n\n")


@pytest.mark.parametrize("body", [None, ""])
def test_description_vide(garde: ModuleType, body: str | None) -> None:
    resultat = garde.analyser(["CLAUDE.md"], [("CLAUDE.md", None)], evenement(body))
    assert resultat["description"] == garde.construire_bloc(["CLAUDE.md"]) + "\n"
    resultat = garde.analyser(["CLAUDE.md"], [("a.py", None)], evenement(body))
    assert resultat["description"] == ""


def test_nom_hostile_echappe(garde: ModuleType) -> None:
    nom = "docs/adr/a`b\n<!-- garde:fin -->\r.md"
    bloc = garde.construire_bloc([nom])
    assert "`docs/adr/a\\u0060b\\n<!-- garde:fin -->\\r.md`" in bloc
    assert bloc.count("\n") == 4


def test_contenu_du_resume(garde: ModuleType) -> None:
    resultat = garde.analyser(
        ["CLAUDE.md", "docs/**"], [("CLAUDE.md", None), ("docs/a.md", None)], evenement("x")
    )
    assert resultat["resume"] == garde.construire_bloc(["CLAUDE.md", "docs/a.md"])
    assert "- `CLAUDE.md`" in resultat["resume"]
    assert "- `docs/a.md`" in resultat["resume"]


def test_principal_codes_de_sortie(garde: ModuleType, tmp_path: Path) -> None:
    chemins = tmp_path / "chemins.txt"
    chemins.write_text("# liste\nCLAUDE.md\n", encoding="utf-8")
    fichiers = tmp_path / "fichiers.jsonl"
    fichiers.write_text('{"filename": "CLAUDE.md", "previous_filename": null}\n', encoding="utf-8")
    evt = tmp_path / "evenement.json"
    evt.write_text(json.dumps(evenement("texte")), encoding="utf-8")
    sortie = tmp_path / "sortie.json"
    arguments = ["--chemins", str(chemins), "--fichiers", str(fichiers), "--evenement", str(evt)]
    assert garde.principal([*arguments, "--sortie", str(sortie)]) == 0
    assert json.loads(sortie.read_text(encoding="utf-8"))["etiquette"] == "poser"
    evt.write_text('{"push": true}', encoding="utf-8")
    assert garde.principal([*arguments, "--sortie", str(sortie)]) == 2
    fichiers.write_text("cassé\n", encoding="utf-8")
    assert garde.principal([*arguments, "--sortie", str(sortie)]) == 2
