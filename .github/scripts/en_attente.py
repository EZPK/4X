"""Logique de la tâche `en-attente`.

Niveau 2 de M0 : Technical Plan, point 8 ; plan détaillé, point 19.

Un ajout à la liste des scénarios en attente exige une pull request qui modifie un `.feature`.
Codes de sortie : 0 permis, 1 ajout refusé, 2 erreur d'entrée.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from garde import ErreurEntree, lire_fichiers_modifies  # noqa: E402
from motifs import lire_motifs  # noqa: E402


def entrees_ajoutees(avant: str, apres: str) -> list[str]:
    deja = set(lire_motifs(avant.splitlines()))
    return [entree for entree in lire_motifs(apres.splitlines()) if entree not in deja]


def feature_modifie(fichiers: list[tuple[str, str | None]]) -> bool:
    return any(
        nom.endswith(".feature") or (ancien is not None and ancien.endswith(".feature"))
        for nom, ancien in fichiers
    )


def principal(arguments: list[str]) -> int:
    analyseur = argparse.ArgumentParser(description="Contrôle des ajouts à en_attente.txt")
    analyseur.add_argument("--avant", required=True)
    analyseur.add_argument("--apres", required=True)
    analyseur.add_argument("--fichiers", required=True)
    options = analyseur.parse_args(arguments)
    try:
        avant = Path(options.avant).read_text(encoding="utf-8")
        apres = Path(options.apres).read_text(encoding="utf-8")
        fichiers = lire_fichiers_modifies(Path(options.fichiers).read_text(encoding="utf-8"))
    except (ErreurEntree, OSError) as erreur:
        print(f"erreur d'entrée : {erreur}", file=sys.stderr)
        return 2
    ajoutees = entrees_ajoutees(avant, apres)
    for entree in ajoutees:
        print(f"entrée ajoutée : {entree}")
    if ajoutees and not feature_modifie(fichiers):
        print("refus : un ajout exige une pull request qui modifie un fichier .feature")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
