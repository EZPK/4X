"""Vérifications des workflows par lecture du texte.

Niveau 2 de M0, plan détaillé, point 26 ; niveau 2 de M1, plan détaillé, point 13.
"""

import re
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
WORKFLOWS = RACINE / ".github/workflows"
OBLIGATOIRES = {
    "lint",
    "typage",
    "gitleaks",
    "termes-interdits",
    "tests-outillage",
    "garde",
    "en-attente",
}
# Tâches de M1, obligatoires à partir du palier 4 (niveau 2 de M1, plan détaillé, point 31) :
# elles suivent dès le palier 2 la règle « pas de clé name ni de strategy ».
NOUVELLES_M1 = {"tests", "rejeu", "proprietes", "mutation"}


def blocs_run(texte: str) -> list[str]:
    """Le contenu de chaque `run:`, sur une ligne ou en bloc indenté."""
    lignes = texte.splitlines()
    blocs: list[str] = []
    for i, ligne in enumerate(lignes):
        trouve = re.match(r"^(\s*)(?:- )?run:(.*)$", ligne)
        if not trouve:
            continue
        retrait = len(trouve.group(1))
        bloc = [trouve.group(2)]
        for suite in lignes[i + 1 :]:
            if suite.strip() and len(suite) - len(suite.lstrip()) <= retrait:
                break
            bloc.append(suite)
        blocs.append("\n".join(bloc))
    return blocs


def taches(texte: str) -> dict[str, list[str]]:
    """Les clés directes de chaque tâche sous `jobs:` (retrait de 2 puis 4 espaces)."""
    resultat: dict[str, list[str]] = {}
    dans_jobs = False
    courante: str | None = None
    for ligne in texte.splitlines():
        if re.match(r"^\S", ligne):
            dans_jobs = ligne.startswith("jobs:")
            courante = None
        elif dans_jobs and (tache := re.match(r"^  ([\w-]+):\s*$", ligne)):
            courante = tache.group(1)
            resultat[courante] = []
        elif courante and (cle := re.match(r"^    ([\w-]+):", ligne)):
            resultat[courante].append(cle.group(1))
    return resultat


def textes() -> dict[str, str]:
    return {f.name: f.read_text(encoding="utf-8") for f in sorted(WORKFLOWS.glob("*.yml"))}


def test_les_deux_workflows_existent() -> None:
    assert set(textes()) == {"ci.yml", "garde.yml"}


def test_aucun_run_ne_contient_d_expression_github_event() -> None:
    for nom, texte in textes().items():
        blocs = blocs_run(texte)
        assert blocs, nom
        for bloc in blocs:
            assert "${{ github.event." not in bloc, nom
            assert "${{github.event." not in bloc, nom


def test_garde_ne_recupere_que_la_branche_de_base() -> None:
    texte = textes()["garde.yml"]
    assert "pull_request_target:" in texte
    assert re.search(r"^\s+pull_request:", texte, re.MULTILINE) is None
    refs = re.findall(r"^\s*ref:\s*(.+)$", texte, re.MULTILINE)
    assert refs == ["${{ github.base_ref }}", "${{ github.base_ref }}"]
    assert texte.count("actions/checkout@") == 2
    for interdit in (
        "head.sha }}",
        "head.ref }}",
        "refs/pull/",
        "actions/cache",
        "upload-artifact",
    ):
        assert interdit not in texte
    assert "persist-credentials: false" in texte


def test_aucune_tache_obligatoire_n_a_de_nom() -> None:
    trouvees: set[str] = set()
    for nom, texte in textes().items():
        for tache, cles in taches(texte).items():
            if tache in OBLIGATOIRES:
                trouvees.add(tache)
                assert "name" not in cles, f"{nom} : {tache}"
                assert "strategy" not in cles, f"{nom} : {tache}"
    assert trouvees == OBLIGATOIRES


def test_actions_epinglees_par_sha() -> None:
    for nom, texte in textes().items():
        for action in re.findall(r"uses:\s*(\S+)", texte):
            assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", action), f"{nom} : {action}"


def test_nouvelles_taches_de_m1_sans_nom_ni_strategie() -> None:
    cles = taches(textes()["ci.yml"])
    assert NOUVELLES_M1 <= set(cles)
    for tache in NOUVELLES_M1:
        assert "name" not in cles[tache], tache
        assert "strategy" not in cles[tache], tache


def test_rejeu_sous_deux_pythonhashseed_puis_divergence() -> None:
    texte = textes()["ci.yml"]
    assert "PYTHONHASHSEED=0 uv run pytest -m rejeu" in texte
    assert "PYTHONHASHSEED=1 uv run pytest -m rejeu" in texte
    assert "python -m fourx.tools.divergence" in texte


def test_tests_outillage_lance_encore_toute_la_suite() -> None:
    blocs = [b.strip() for b in blocs_run(textes()["ci.yml"])]
    assert "uv run pytest" in blocs
