"""Tests de `.github/scripts/termes_interdits.py` (plan détaillé, point 26).

Tous les termes sont inventés et écrits dans `tmp_path`.
"""

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

LISTE = """# Termes interdits d'essai

## Termes

glorpex
méga-fluff

## Fichiers exclus

exclus/**
liste.md
"""


@pytest.fixture
def depot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], check=True)
    (tmp_path / "liste.md").write_text(LISTE, encoding="utf-8")
    return tmp_path


@pytest.fixture
def module(charger_script: Callable[[str], ModuleType]) -> ModuleType:
    return charger_script(".github/scripts/termes_interdits.py")


def suivre(depot: Path, fichiers: dict[str, str]) -> None:
    for nom, contenu in fichiers.items():
        chemin = depot / nom
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(contenu, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], check=True)


def lancer(
    module: ModuleType, capsys: pytest.CaptureFixture[str], *arguments: str
) -> tuple[int, list[str]]:
    code = module.principal(["--liste", "liste.md", *arguments])
    return int(code), capsys.readouterr().out.splitlines()


def evenement_pr(depot: Path, titre: str, corps: str | None, branche: str) -> str:
    chemin = depot.parent / "evenement.json"
    donnees = {"pull_request": {"title": titre, "body": corps, "head": {"ref": branche}}}
    chemin.write_text(json.dumps(donnees), encoding="utf-8")
    return str(chemin)


def test_aucun_terme_code_0(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "rien de spécial\n"})
    assert lancer(module, capsys) == (0, [])


def test_terme_trouve_majuscules_et_minuscules(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "ligne 1\nUn GLORPEX ici.\nun glorpex là\n"})
    code, sortie = lancer(module, capsys)
    assert code == 1
    assert sortie == ["a.md:2: terme « glorpex »", "a.md:3: terme « glorpex »"]


def test_terme_dans_un_mot_plus_long(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "glorpexes superglorpex glorpex_1 glorpex2\n"})
    assert lancer(module, capsys) == (0, [])


def test_terme_a_tiret(depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]) -> None:
    suivre(depot, {"a.md": "du Méga-Fluff\nméga fluff\nméga-fluffs\n"})
    assert lancer(module, capsys) == (1, ["a.md:1: terme « méga-fluff »"])


def test_frontiere_a_une_lettre_accentuee(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "églorpex glorpexé\n(glorpex)\n"})
    assert lancer(module, capsys) == (1, ["a.md:2: terme « glorpex »"])


def test_fichiers_exclus_ignores(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"exclus/x/a.md": "glorpex\n", "garde.md": "rien\n"})
    assert lancer(module, capsys) == (0, [])


def test_fichier_liste_mais_absent_du_disque(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "glorpex\n"})
    (depot / "a.md").unlink()
    assert lancer(module, capsys) == (0, [])


def test_fichier_non_suivi_ignore(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "rien\n"})
    (depot / "b.md").write_text("glorpex\n", encoding="utf-8")
    assert lancer(module, capsys) == (0, [])


def test_portee_titre_description_messages_branche(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "rien\n"})
    evenement = evenement_pr(depot, "Ajout glorpex", "ligne\nglorpex", "essai/glorpex")
    messages = depot.parent / "messages.txt"
    messages.write_text("premier\0second\nglorpex\n\0", encoding="utf-8")
    code, sortie = lancer(module, capsys, "--evenement", evenement, "--messages", str(messages))
    assert code == 1
    assert sortie == [
        "titre de la pull request:1: terme « glorpex »",
        "description de la pull request:2: terme « glorpex »",
        "nom de la branche:1: terme « glorpex »",
        "message de commit 2:2: terme « glorpex »",
    ]


def test_description_null(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "rien\n"})
    evenement = evenement_pr(depot, "titre", None, "essai/x")
    assert lancer(module, capsys, "--evenement", evenement) == (0, [])


def test_evenement_de_push_sans_pull_request(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "rien\n"})
    chemin = depot.parent / "push.json"
    chemin.write_text(json.dumps({"ref": "refs/heads/glorpex", "head_commit": {}}), "utf-8")
    assert lancer(module, capsys, "--evenement", str(chemin)) == (0, [])


def test_exception_pull_request_qui_ne_modifie_que_la_liste(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "rien\n"})
    evenement = evenement_pr(depot, "Ajout glorpex", "glorpex", "essai/liste")
    messages = depot.parent / "messages.txt"
    messages.write_text("Ajout de glorpex\0", encoding="utf-8")
    fichiers = depot.parent / "fichiers.txt"
    fichiers.write_text("docs/termes-interdits.md\n", encoding="utf-8")
    arguments = ["--evenement", evenement, "--messages", str(messages), "--fichiers", str(fichiers)]
    assert lancer(module, capsys, *arguments) == (0, [])
    fichiers.write_text("docs/termes-interdits.md\na.md\n", encoding="utf-8")
    code, sortie = lancer(module, capsys, *arguments)
    assert code == 1
    assert len(sortie) == 3


def test_exception_garde_le_nom_de_branche(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    suivre(depot, {"a.md": "rien\n"})
    evenement = evenement_pr(depot, "titre", "corps", "essai/glorpex")
    fichiers = depot.parent / "fichiers.txt"
    fichiers.write_text("docs/termes-interdits.md\n", encoding="utf-8")
    arguments = ["--evenement", evenement, "--fichiers", str(fichiers)]
    assert lancer(module, capsys, *arguments) == (1, ["nom de la branche:1: terme « glorpex »"])


@pytest.mark.parametrize(
    "contenu", [None, "# Sans section\n", "## Termes\n\n## Fichiers exclus\nx\n"]
)
def test_erreur_d_entree_code_2(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str], contenu: str | None
) -> None:
    liste = depot / "liste.md"
    if contenu is None:
        liste.unlink()
    else:
        liste.write_text(contenu, encoding="utf-8")
    assert lancer(module, capsys) == (2, [])


def test_evenement_illisible_code_2(
    depot: Path, module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    chemin = depot.parent / "casse.json"
    chemin.write_text("{", encoding="utf-8")
    assert lancer(module, capsys, "--evenement", str(chemin)) == (2, [])
