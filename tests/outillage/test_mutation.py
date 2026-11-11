"""Tests de `.github/scripts/mutation.py`.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 10.

Aucun de ces tests ne lance mutmut : ils portent sur le choix des fichiers, la lecture des
résultats, le calcul du score et la comparaison à la base.
"""

from collections import Counter
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def mutation(charger_script: Callable[[str], ModuleType]) -> ModuleType:
    return charger_script(".github/scripts/mutation.py")


NOYAU = ["src/fourx/core/__init__.py", "src/fourx/core/arith.py", "src/fourx/core/step.py"]
FORMATS = ["src/fourx/schema/__init__.py", "src/fourx/schema/orders.py"]
EXCLUS = ["src/fourx/__main__.py", "src/fourx/clients/textual_app.py"]

RESULTATS = """\
    fourx.core.arith.x_div_trunc__mutmut_1: killed
    fourx.core.arith.x_div_trunc__mutmut_2: survived
    fourx.core.arith.x_div_trunc__mutmut_3: timeout
    fourx.core.arith.x_rem_trunc__mutmut_1: no tests
    fourx.core.arith.x_rem_trunc__mutmut_2: skipped
    fourx.core.step.xǁStepǁrun__mutmut_1: killed
    fourx.core.x_helper__mutmut_1: not checked
    autre.module.x_f__mutmut_1: killed
"""


def test_table_tool_mutmut_refusee(mutation: ModuleType) -> None:
    mutation.refuser_table_pyproject('[project]\nname = "fourx"\n[tool.uv]\nexclude-newer = "x"\n')
    with pytest.raises(mutation.ErreurEntree):
        mutation.refuser_table_pyproject("[tool.mutmut]\ndo_not_mutate = ['src/fourx/core/*']\n")


def test_lecture_de_do_not_mutate(mutation: ModuleType, racine: Path) -> None:
    texte = "[mutmut]\ndo_not_mutate =\n    src/a.py\n    src/b.py\n"
    assert mutation.lire_do_not_mutate(texte) == ["src/a.py", "src/b.py"]
    assert mutation.lire_do_not_mutate("[mutmut]\nsource_paths = src\n") == []
    assert mutation.lire_do_not_mutate((racine / "setup.cfg").read_text(encoding="utf-8")) == EXCLUS


@pytest.mark.parametrize(
    ("chemin", "module"),
    [
        ("src/fourx/core/arith.py", "fourx.core.arith"),
        ("src/fourx/core/__init__.py", "fourx.core"),
        ("src/fourx/tools/replay.py", "fourx.tools.replay"),
    ],
)
def test_module_de(mutation: ModuleType, chemin: str, module: str) -> None:
    assert mutation.module_de(chemin) == module


def choisir(
    mutation: ModuleType,
    modifies: list[str],
    tout_core: bool = False,
    plancher_partout: bool = False,
) -> list[str]:
    return mutation.choisir_fichiers(  # type: ignore[no-any-return]
        modifies, EXCLUS, NOYAU, FORMATS, tout_core, plancher_partout
    )


def test_fichiers_modifies_seulement_sous_src_fourx(mutation: ModuleType) -> None:
    modifies = [
        "src/fourx/server/game.py",
        "README.md",
        "tests/core/test_step.py",
        "src/fourx/x.txt",
    ]
    assert choisir(mutation, modifies) == ["src/fourx/server/game.py"]


def test_fichiers_exclus_par_do_not_mutate(mutation: ModuleType) -> None:
    assert choisir(mutation, ["src/fourx/__main__.py", "src/fourx/clients/textual_app.py"]) == []


def test_aucun_fichier(mutation: ModuleType) -> None:
    assert choisir(mutation, []) == []


def test_definitions_d_etapes_modifiees_ajoutent_tout_le_noyau(mutation: ModuleType) -> None:
    assert choisir(mutation, ["tests/scenarios/steps/steps_noyau.py"]) == NOYAU


def test_tout_core(mutation: ModuleType) -> None:
    assert choisir(mutation, ["src/fourx/server/game.py"], tout_core=True) == sorted(
        [*NOYAU, "src/fourx/server/game.py"]
    )


def test_plancher_partout_ajoute_noyau_et_formats(mutation: ModuleType) -> None:
    assert choisir(mutation, [], tout_core=True, plancher_partout=True) == sorted(
        [*NOYAU, *FORMATS]
    )


def test_lecture_des_resultats(mutation: ModuleType) -> None:
    modules = ["fourx.core", "fourx.core.arith", "fourx.core.step"]
    par_module = mutation.lire_resultats(RESULTATS, modules)
    assert par_module["fourx.core.arith"] == Counter(
        {"killed": 1, "survived": 1, "timeout": 1, "no tests": 1, "skipped": 1}
    )
    assert par_module["fourx.core.step"] == Counter({"killed": 1})
    assert par_module["fourx.core"] == Counter({"not checked": 1})


def test_score(mutation: ModuleType) -> None:
    arith = Counter({"killed": 1, "survived": 1, "timeout": 1, "no tests": 1, "skipped": 1})
    assert mutation.score(arith) == 2 / 4
    assert mutation.score(Counter({"not checked": 1})) == 0.0
    assert mutation.score(Counter()) is None
    assert mutation.score(Counter({"skipped": 3})) is None


def comparer(
    mutation: ModuleType,
    fichiers: list[str],
    tete: dict[str, float | None],
    base: dict[str, float | None],
    presents_base: set[str],
    plancher_partout: bool = False,
) -> dict[str, str]:
    lignes = mutation.comparer(fichiers, tete, base, presents_base, plancher_partout)
    return {ligne.fichier: ligne.echec for ligne in lignes}


def test_score_inferieur_a_la_base(mutation: ModuleType) -> None:
    fichier = "src/fourx/core/arith.py"
    echecs = comparer(mutation, [fichier], {fichier: 0.9}, {fichier: 0.95}, {fichier})
    assert echecs[fichier] == "score inférieur à la base"
    echecs = comparer(mutation, [fichier], {fichier: 0.95}, {fichier: 0.95}, {fichier})
    assert echecs[fichier] == ""


def test_fichier_nouveau_du_noyau_sous_le_plancher(mutation: ModuleType) -> None:
    fichier = "src/fourx/core/arith.py"
    assert (
        comparer(mutation, [fichier], {fichier: 0.79}, {}, set())[fichier]
        == "score inférieur à 80%"
    )
    assert comparer(mutation, [fichier], {fichier: 0.8}, {}, set())[fichier] == ""


def test_fichier_nouveau_hors_noyau_et_formats_sans_plancher(mutation: ModuleType) -> None:
    fichier = "src/fourx/server/game.py"
    assert comparer(mutation, [fichier], {fichier: 0.1}, {}, set())[fichier] == ""


def test_fichier_sans_mutant_ne_fait_pas_echouer(mutation: ModuleType) -> None:
    fichier = "src/fourx/core/__init__.py"
    assert comparer(mutation, [fichier], {fichier: None}, {}, set())[fichier] == ""


def test_fichier_supprime_dans_la_tete(mutation: ModuleType) -> None:
    fichier = "src/fourx/core/ancien.py"
    assert comparer(mutation, [fichier], {}, {fichier: 0.9}, {fichier})[fichier] == ""


def test_plancher_partout(mutation: ModuleType) -> None:
    noyau, serveur = "src/fourx/core/step.py", "src/fourx/server/game.py"
    echecs = comparer(mutation, [noyau, serveur], {noyau: 0.5, serveur: 0.5}, {}, set(), True)
    assert echecs == {noyau: "score inférieur à 80%", serveur: ""}


def test_tableau(mutation: ModuleType) -> None:
    lignes = mutation.comparer(
        ["src/fourx/core/arith.py"], {"src/fourx/core/arith.py": 0.5}, {}, set(), False
    )
    texte = mutation.tableau(lignes)
    assert "| `src/fourx/core/arith.py` | 50.0% | — | score inférieur à 80% |" in texte


def test_base_et_tete_obligatoires_sans_plancher_partout(mutation: ModuleType) -> None:
    assert mutation.principal([]) == 2
    assert mutation.principal(["--base", "abc"]) == 2


def test_fichier_sans_fonction_n_a_aucun_mutant(mutation: ModuleType) -> None:
    assert not mutation.a_des_fonctions('"""Paquet."""\n')
    assert not mutation.a_des_fonctions("X = 1\n")
    assert mutation.a_des_fonctions("def f() -> int:\n    return 1\n")
    assert mutation.a_des_fonctions("class A:\n    def m(self) -> None:\n        pass\n")


def test_pytest_ini_copie_dans_la_copie_de_travail(racine: Path) -> None:
    texte = (racine / "setup.cfg").read_text(encoding="utf-8")
    assert "also_copy =\n    pytest.ini\n" in texte


def test_fichier_present_dans_la_base_sans_score_soumis_au_plancher(mutation: ModuleType) -> None:
    fichier = "src/fourx/core/state.py"
    echecs = comparer(mutation, [fichier], {fichier: 0.5}, {fichier: None}, {fichier})
    assert echecs[fichier] == "score inférieur à 80%"


def test_sous_module_commencant_par_x_non_compte(mutation: ModuleType) -> None:
    texte = "    fourx.core.xtra.x_f__mutmut_1: survived\n    fourx.core.x_g__mutmut_1: killed\n"
    par_module = mutation.lire_resultats(texte, ["fourx.core"])
    assert par_module["fourx.core"] == Counter({"killed": 1})


def test_resultats_illisibles_font_echouer(
    mutation: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "src/fourx/core").mkdir(parents=True)
    (tmp_path / "src/fourx/core/arith.py").write_text("def f() -> int:\n    return 1\n")

    class Resultat:
        def __init__(self, sortie: str, code: int = 0) -> None:
            self.stdout, self.stderr, self.returncode = sortie, "", code

    def faux_run(commande: list[str], **_: object) -> Resultat:
        return Resultat("format inconnu\n") if "results" in commande else Resultat("")

    monkeypatch.setattr(mutation.subprocess, "run", faux_run)
    with pytest.raises(mutation.ErreurEntree, match="aucun résultat"):
        mutation.muter(tmp_path, ["src/fourx/core/arith.py"])

    def faux_run_en_echec(commande: list[str], **_: object) -> Resultat:
        return Resultat("", 1) if "results" in commande else Resultat("")

    monkeypatch.setattr(mutation.subprocess, "run", faux_run_en_echec)
    with pytest.raises(mutation.ErreurEntree, match="mutmut results a échoué"):
        mutation.muter(tmp_path, ["src/fourx/core/arith.py"])
