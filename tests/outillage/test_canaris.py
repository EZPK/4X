"""Tests de la suite canari, sur un petit module d'exemple et non sur `main`.

Niveau 2 de M1, plan détaillé, point 30. Que chaque canari s'applique à `main` et y soit attrapé est
vérifié par la tâche de nuit elle-même (point 30 bis).
"""

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

SOURCE = '''"""Module d'exemple."""


def calcul(a: int, b: int) -> int:
    """Docstring."""
    total = ajoute(a, b)
    return double(total, "x")


def sans_docstring(a: int) -> int:
    return ajoute(a, ajoute(a, 1))
'''


@pytest.fixture
def canaris(charger_script: Callable[[str], ModuleType]) -> ModuleType:
    return charger_script(".github/scripts/canaris.py")


def modification(canaris: ModuleType, ancre: dict[str, str], texte: str) -> object:
    return canaris.Modification(fichier="exemple.py", ancre=ancre, texte=texte)


def test_debut_de_fonction_apres_la_docstring(canaris: ModuleType) -> None:
    m = modification(canaris, {"type": "debut_de_fonction", "fonction": "calcul"}, "x = 1\ny = 2")
    resultat = canaris.appliquer(SOURCE, m)
    assert '    """Docstring."""\n    x = 1\n    y = 2\n    total = ajoute(a, b)\n' in resultat


def test_debut_de_fonction_sans_docstring(canaris: ModuleType) -> None:
    m = modification(
        canaris, {"type": "debut_de_fonction", "fonction": "sans_docstring"}, "z = 0.5"
    )
    resultat = canaris.appliquer(SOURCE, m)
    assert "-> int:\n    z = 0.5\n    return ajoute(a, ajoute(a, 1))\n" in resultat


def test_fin_du_module(canaris: ModuleType) -> None:
    m = modification(canaris, {"type": "fin_du_module"}, "import os  # canari")
    assert canaris.appliquer(SOURCE, m) == SOURCE + "import os  # canari\n"


def test_expression_remplace_le_seul_appel_designe(canaris: ModuleType) -> None:
    ancre = {"type": "expression", "fonction": "calcul", "appel": "double", "contient": '"x"'}
    resultat = canaris.appliquer(SOURCE, modification(canaris, ancre, "hash(total)"))
    assert "    return hash(total)\n" in resultat
    assert "total = ajoute(a, b)" in resultat


def test_expression_peut_etre_remplacee_par_une_instruction(canaris: ModuleType) -> None:
    source = "def f(t):\n    t.passer(1, 2)\n    return t\n"
    ancre = {"type": "expression", "fonction": "f", "appel": "t.passer", "contient": "2"}
    resultat = canaris.appliquer(source, modification(canaris, ancre, "t.compte = 3"))
    assert resultat == "def f(t):\n    t.compte = 3\n    return t\n"


def test_colonnes_apres_des_caracteres_accentues(canaris: ModuleType) -> None:
    source = 'def f(é):\n    return g("é", é) + g("à", 1)\n'
    ancre = {"type": "expression", "fonction": "f", "appel": "g", "contient": '"à"'}
    resultat = canaris.appliquer(source, modification(canaris, ancre, "0"))
    assert resultat == 'def f(é):\n    return g("é", é) + 0\n'


@pytest.mark.parametrize(
    ("ancre", "message"),
    [
        ({"type": "debut_de_fonction", "fonction": "absente"}, "fonction 'absente' introuvable"),
        (
            {"type": "expression", "fonction": "calcul", "appel": "triple", "contient": "a"},
            "0 appels à 'triple'",
        ),
        (
            {
                "type": "expression",
                "fonction": "sans_docstring",
                "appel": "ajoute",
                "contient": "a",
            },
            "2 appels à 'ajoute'",
        ),
        ({"type": "milieu"}, "ancre inconnue"),
    ],
)
def test_ancre_manquante_ou_ambigue(
    canaris: ModuleType, ancre: dict[str, str], message: str
) -> None:
    with pytest.raises(canaris.ErreurCanari, match=message):
        canaris.appliquer(SOURCE, modification(canaris, ancre, "0"))


def test_resultat_illisible(canaris: ModuleType) -> None:
    m = modification(canaris, {"type": "fin_du_module"}, "def (")
    with pytest.raises(canaris.ErreurCanari, match="ne se lit plus"):
        canaris.appliquer(SOURCE, m)


def ecrire_canari(
    dossier: Path, nom: str, controle: str, modifications: list[object], attendu: str = "VU"
) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    contenu = {
        "description": "d",
        "controle": controle,
        "attendu": attendu,
        "modifications": modifications,
    }
    (dossier / f"{nom}.json").write_text(json.dumps(contenu), encoding="utf-8")


def test_lire_refuse_une_cle_manquante_ou_un_motif_vide(
    canaris: ModuleType, tmp_path: Path
) -> None:
    dossier = tmp_path / "c"
    dossier.mkdir()
    (dossier / "x.json").write_text(
        json.dumps({"controle": "tests", "attendu": "a", "modifications": []}), encoding="utf-8"
    )
    with pytest.raises(canaris.ErreurCanari, match="x.json : clé manquante 'description'"):
        canaris.lire_tous(dossier)
    ancre = {"type": "fin_du_module"}
    ecrire_canari(
        tmp_path / "d", "x", "tests", [{"fichier": "f", "ancre": ancre, "texte": "t"}], ""
    )
    with pytest.raises(canaris.ErreurCanari, match="motif attendu vide"):
        canaris.lire_tous(tmp_path / "d")


def test_positions_comme_ast_malgre_un_saut_de_page(canaris: ModuleType) -> None:
    # str.splitlines couperait aussi sur \f ; ast ne compte que \n, \r et \r\n.
    source = 'x = "\f"  # saut de page\ndef f(a):\n    return g(a)\n'
    ancre = {"type": "expression", "fonction": "f", "appel": "g", "contient": "a"}
    resultat = canaris.appliquer(source, modification(canaris, ancre, "h(a)"))
    assert resultat == 'x = "\f"  # saut de page\ndef f(a):\n    return h(a)\n'


def test_lire_refuse_un_controle_inconnu_ou_sans_modification(
    canaris: ModuleType, tmp_path: Path
) -> None:
    ecrire_canari(tmp_path / "a", "x", "lint", [])
    with pytest.raises(canaris.ErreurCanari, match="contrôle inconnu 'lint'"):
        canaris.lire_tous(tmp_path / "a")
    ecrire_canari(tmp_path / "b", "x", "tests", [])
    with pytest.raises(canaris.ErreurCanari, match="aucune modification"):
        canaris.lire_tous(tmp_path / "b")


def test_les_canaris_du_depot_se_lisent(canaris: ModuleType) -> None:
    lus = canaris.lire_tous()
    assert sorted(c.controle for c in lus) == [
        "imports",
        "mutation",
        "proprietes",
        "rejeu",
        "tests",
        "tests",
    ]


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un petit dépôt git : exemple.py et un canari qui insère un flottant dans `calcul`."""
    racine = tmp_path / "depot"
    racine.mkdir()
    (racine / "exemple.py").write_text(SOURCE, encoding="utf-8")
    identite = ["-c", "user.name=t", "-c", "user.email=t@invalid"]
    for arguments in (["init", "--quiet"], ["add", "."], ["commit", "--quiet", "-m", "départ"]):
        subprocess.run(["git", *identite, *arguments], cwd=racine, check=True)
    ancre = {"type": "debut_de_fonction", "fonction": "calcul"}
    ecrire_canari(
        tmp_path / "canaris",
        "flottant",
        "tests",
        [{"fichier": "exemple.py", "ancre": ancre, "texte": "z = 0.5"}],
    )
    return racine


def options(depot: Path) -> list[str]:
    return ["--depot", str(depot), "--canaris", str(depot.parent / "canaris")]


def test_un_canari_attrape(
    canaris: ModuleType, depot: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # La commande échoue, avec le motif, si le flottant a été inséré et enregistré dans le clone.
    commande = {
        "tests": "grep -q 'z = 0.5' exemple.py && git log -1 --format=%s | grep -q canari"
        " && echo 'erreur : VU ici' && false"
    }
    assert canaris.main(options(depot), commande) == 0
    sortie = capsys.readouterr().out
    assert "flottant → tests : code 1, « VU » trouvé\n    erreur : VU ici" in sortie
    assert "1 canaris attrapés sur 1" in sortie
    assert (depot / "exemple.py").read_text(encoding="utf-8") == SOURCE  # le dépôt est intact


def test_un_canari_non_attrape_fait_echouer(
    canaris: ModuleType, depot: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert canaris.main(options(depot), {"tests": "echo rien vu"}) == 1
    sortie = capsys.readouterr().out
    assert "flottant → tests : code 0 — NON ATTRAPÉ (« VU » absent de la sortie)" in sortie
    assert "rien vu" in sortie
    assert "0 canaris attrapés sur 1" in sortie


@pytest.mark.parametrize(
    ("commande", "raison"),
    [
        ("echo panne sans rapport; false", "code 1 — NON ATTRAPÉ (« VU » absent de la sortie)"),
        ("echo VU; exit 2", "code 2 — NON ATTRAPÉ (motif attendu trouvé)"),
    ],
)
def test_une_panne_sans_rapport_ne_compte_pas_comme_attrapee(
    canaris: ModuleType,
    depot: Path,
    capsys: pytest.CaptureFixture[str],
    commande: str,
    raison: str,
) -> None:
    assert canaris.main(options(depot), {"tests": commande}) == 1
    assert f"flottant → tests : {raison}" in capsys.readouterr().out


def test_base_et_tete_passees_a_la_commande(
    canaris: ModuleType, depot: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=depot, capture_output=True, text=True, check=True
    ).stdout.strip()
    commande = {
        "tests": f'test "{{base}}" = "{base}" && test "{{tete}}" != "{base}" && echo VU && false'
    }
    assert canaris.main(options(depot), commande) == 0
    assert "1 canaris attrapés sur 1" in capsys.readouterr().out


def test_canari_inconnu_ou_ancre_manquante(
    canaris: ModuleType, depot: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert canaris.main([*options(depot), "--seulement", "autre"], {"tests": "false"}) == 2
    assert "canaris inconnus : ['autre']" in capsys.readouterr().err
    ancre = {"type": "debut_de_fonction", "fonction": "absente"}
    ecrire_canari(
        depot.parent / "canaris",
        "flottant",
        "tests",
        [{"fichier": "exemple.py", "ancre": ancre, "texte": "z = 0.5"}],
    )
    assert canaris.main(options(depot), {"tests": "false"}) == 2
    assert "fonction 'absente' introuvable" in capsys.readouterr().err
