"""Contrôle de mutation de M1 (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 10 ;
plan détaillé, point 9).

Chemin protégé, bibliothèque standard seulement.

Usages :
- sur une pull request : mutation.py --base <commit> --tete <commit> [--tout-core]
- la nuit : mutation.py --tout-core --plancher-partout

Codes de sortie : 0 contrôle réussi, 1 contrôle en échec, 2 erreur d'entrée.

--tete ne sert qu'à lister les fichiers modifiés : la tête mutée est la copie de travail du
dépôt où le script est lancé (en CI, le commit de fusion ; pour la suite canari, le dépôt
temporaire où le bug volontaire est commité).
"""

import argparse
import ast
import configparser
import os
import subprocess
import sys
import tempfile
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motifs import est_couvert  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SOURCES = "src/fourx/"
NOYAU = "src/fourx/core/"
FORMATS = "src/fourx/schema/"
ETAPES = "tests/scenarios/steps/"
PLANCHER = 0.8
STATUTS_TUES = frozenset({"killed", "timeout"})
STATUTS_IGNORES = frozenset({"skipped"})


class ErreurEntree(Exception):
    pass


def refuser_table_pyproject(texte: str) -> None:
    """Une table [tool.mutmut] dans pyproject.toml masquerait la configuration protégée."""
    donnees = tomllib.loads(texte)
    outils = donnees.get("tool")
    if isinstance(outils, dict) and "mutmut" in outils:
        raise ErreurEntree("pyproject.toml contient une table [tool.mutmut] : interdit")


def lire_do_not_mutate(texte: str) -> list[str]:
    configuration = configparser.ConfigParser()
    configuration.read_string(texte)
    if not configuration.has_option("mutmut", "do_not_mutate"):
        return []
    return [
        ligne.strip()
        for ligne in configuration.get("mutmut", "do_not_mutate").splitlines()
        if ligne.strip()
    ]


def module_de(chemin: str) -> str:
    """src/fourx/core/arith.py → fourx.core.arith ; src/fourx/core/__init__.py → fourx.core."""
    relatif = chemin.removeprefix("src/").removesuffix(".py")
    parties = relatif.split("/")
    if parties[-1] == "__init__":
        parties = parties[:-1]
    return ".".join(parties)


def choisir_fichiers(
    modifies: list[str],
    exclus: list[str],
    tous_noyau: list[str],
    tous_formats: list[str],
    tout_core: bool,
    plancher_partout: bool,
) -> list[str]:
    """Les fichiers à muter, triés, sans doublon."""
    choisis = {c for c in modifies if c.startswith(SOURCES) and c.endswith(".py")}
    if tout_core or any(c.startswith(ETAPES) for c in modifies):
        choisis |= set(tous_noyau)
    if plancher_partout:
        choisis |= set(tous_noyau) | set(tous_formats)
    return sorted(c for c in choisis if not est_couvert(c, exclus))


def a_des_fonctions(source: str) -> bool:
    """mutmut ne mute que des fonctions : un fichier sans fonction n'a aucun mutant."""
    return any(
        isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef))
        for noeud in ast.walk(ast.parse(source))
    )


def lire_resultats(texte: str, modules: list[str]) -> dict[str, Counter[str]]:
    """Lit la sortie de `mutmut results --all true` : une ligne `nom: statut` par mutant."""
    par_module: dict[str, Counter[str]] = {m: Counter() for m in modules}
    for ligne in texte.splitlines():
        if ": " not in ligne:
            continue
        nom, statut = (morceau.strip() for morceau in ligne.rsplit(": ", 1))
        candidats = [m for m in modules if nom.startswith((m + ".x_", m + ".xǁ"))]
        if candidats:
            par_module[max(candidats, key=len)][statut] += 1
    return par_module


def score(statuts: Counter[str]) -> float | None:
    """(tués + délais dépassés) / (total − ignorés) ; None s'il n'y a aucun mutant compté."""
    total = sum(statuts.values()) - sum(statuts[s] for s in STATUTS_IGNORES)
    if total <= 0:
        return None
    return sum(statuts[s] for s in STATUTS_TUES) / total


@dataclass(frozen=True)
class Ligne:
    fichier: str
    tete: float | None
    base: float | None
    echec: str


def comparer(
    fichiers: list[str],
    scores_tete: dict[str, float | None],
    scores_base: dict[str, float | None],
    presents_base: set[str],
    plancher_partout: bool,
) -> list[Ligne]:
    lignes: list[Ligne] = []
    for fichier in fichiers:
        tete = scores_tete.get(fichier)
        base = scores_base.get(fichier)
        echec = ""
        soumis_au_plancher = fichier.startswith((NOYAU, FORMATS)) and (
            plancher_partout or base is None
        )
        if tete is None:
            echec = ""
        elif base is not None and not plancher_partout and tete < base:
            echec = "score inférieur à la base"
        elif soumis_au_plancher and tete < PLANCHER:
            echec = f"score inférieur à {PLANCHER:.0%}"
        lignes.append(Ligne(fichier, tete, base, echec))
    return lignes


def tableau(lignes: list[Ligne]) -> str:
    def pourcent(valeur: float | None) -> str:
        return "—" if valeur is None else f"{valeur:.1%}"

    sortie = [
        "| Fichier | Score de la tête | Score de la base | Échec |",
        "| :-- | --: | --: | :-- |",
    ]
    for ligne in lignes:
        sortie.append(
            f"| `{ligne.fichier}` | {pourcent(ligne.tete)} | {pourcent(ligne.base)} "
            f"| {ligne.echec or '—'} |"
        )
    return "\n".join(sortie)


def git(*arguments: str, dossier: Path = RACINE) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=dossier, check=True, capture_output=True, text=True
    ).stdout


def lister(dossier: Path, prefixe: str) -> list[str]:
    racine = dossier / prefixe
    if not racine.is_dir():
        return []
    return sorted(str(p.relative_to(dossier)) for p in racine.rglob("*.py"))


def muter(dossier: Path, fichiers: list[str]) -> dict[str, float | None]:
    """Lance mutmut dans `dossier` sur les fichiers donnés et renvoie le score de chacun."""
    presents = [
        f
        for f in fichiers
        if (dossier / f).is_file() and a_des_fonctions((dossier / f).read_text(encoding="utf-8"))
    ]
    modules = [module_de(f) for f in presents]
    if not modules:
        return {}
    motifs = [motif for m in modules for motif in (f"{m}.x_*", f"{m}.xǁ*")]
    lancement = subprocess.run(
        ["uv", "run", "--locked", "mutmut", "run", *motifs],
        cwd=dossier,
        capture_output=True,
        text=True,
    )
    if lancement.returncode != 0 and "nothing matches" not in lancement.stdout + lancement.stderr:
        print(lancement.stdout[-4000:], lancement.stderr[-4000:], sep="\n", file=sys.stderr)
        raise ErreurEntree(f"mutmut run a échoué dans {dossier}")
    lecture = subprocess.run(
        ["uv", "run", "--locked", "mutmut", "results", "--all", "true"],
        cwd=dossier,
        capture_output=True,
        text=True,
    )
    if lecture.returncode != 0:
        print(lecture.stdout[-4000:], lecture.stderr[-4000:], sep="\n", file=sys.stderr)
        raise ErreurEntree(f"mutmut results a échoué dans {dossier}")
    par_module = lire_resultats(lecture.stdout, modules)
    if not any(par_module.values()):
        raise ErreurEntree("aucun résultat de mutmut lu pour des fichiers qui ont des fonctions")
    return {f: score(par_module[m]) for f, m in zip(presents, modules, strict=True)}


def principal(arguments: list[str]) -> int:
    analyseur = argparse.ArgumentParser(description="Contrôle de mutation de M1")
    analyseur.add_argument("--base")
    analyseur.add_argument("--tete")
    analyseur.add_argument("--tout-core", action="store_true")
    analyseur.add_argument("--plancher-partout", action="store_true")
    options = analyseur.parse_args(arguments)
    try:
        if not options.plancher_partout and not (options.base and options.tete):
            raise ErreurEntree("--base et --tete sont obligatoires sans --plancher-partout")
        refuser_table_pyproject((RACINE / "pyproject.toml").read_text(encoding="utf-8"))
        exclus = lire_do_not_mutate((RACINE / "setup.cfg").read_text(encoding="utf-8"))
        modifies = (
            []
            if options.plancher_partout
            else [
                nom
                for nom in git(
                    "-c",
                    "core.quotePath=false",
                    "diff",
                    "--name-only",
                    "-z",
                    f"{options.base}...{options.tete}",
                ).split("\0")
                if nom
            ]
        )
        fichiers = choisir_fichiers(
            modifies,
            exclus,
            lister(RACINE, NOYAU),
            lister(RACINE, FORMATS),
            options.tout_core,
            options.plancher_partout,
        )
        if not fichiers:
            print("Aucun fichier à muter : le contrôle réussit.")
            return 0
        scores_tete = muter(RACINE, fichiers)
        scores_base: dict[str, float | None] = {}
        presents_base: set[str] = set()
        if not options.plancher_partout:
            with tempfile.TemporaryDirectory() as temporaire:
                copie = Path(temporaire) / "base"
                git("worktree", "add", "--detach", str(copie), options.base)
                try:
                    synchro = subprocess.run(
                        ["uv", "sync", "--locked"], cwd=copie, capture_output=True, text=True
                    )
                    if synchro.returncode != 0:
                        print(
                            synchro.stdout[-4000:],
                            synchro.stderr[-4000:],
                            sep="\n",
                            file=sys.stderr,
                        )
                        raise ErreurEntree("uv sync a échoué sur la base")
                    presents_base = {f for f in fichiers if (copie / f).is_file()}
                    scores_base = muter(copie, sorted(presents_base))
                finally:
                    git("worktree", "remove", "--force", str(copie))
        lignes = comparer(
            fichiers, scores_tete, scores_base, presents_base, options.plancher_partout
        )
    except (
        ErreurEntree,
        OSError,
        subprocess.CalledProcessError,
        tomllib.TOMLDecodeError,
    ) as erreur:
        print(f"erreur d'entrée : {erreur}", file=sys.stderr)
        return 2
    rapport = tableau(lignes)
    print(rapport)
    resume = os.environ.get("GITHUB_STEP_SUMMARY")
    if resume:
        with open(resume, "a", encoding="utf-8") as fichier:
            fichier.write("## Mutation\n\n" + rapport + "\n")
    return 1 if any(ligne.echec for ligne in lignes) else 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
