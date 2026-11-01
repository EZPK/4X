"""Logique du contrôle de garde.

Niveau 2 de M0 : Technical Plan, point 8 ; plan détaillé, point 18.

Aucun appel réseau : le workflow fournit les données et applique le résultat.
Codes de sortie : 0 analyse faite, 2 erreur d'entrée.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motifs import est_couvert, lire_fichier_motifs  # noqa: E402

ETIQUETTE = "fichiers protégés modifiés"
DEBUT = "<!-- garde:debut -->"
FIN = "<!-- garde:fin -->"


class ErreurEntree(Exception):
    pass


def lire_fichiers_modifies(texte: str) -> list[tuple[str, str | None]]:
    """Lit un objet JSON par ligne : {"filename": …, "previous_filename": … ou null}."""
    fichiers: list[tuple[str, str | None]] = []
    for numero, ligne in enumerate(texte.splitlines(), start=1):
        if not ligne.strip():
            continue
        try:
            objet = json.loads(ligne)
        except json.JSONDecodeError as erreur:
            raise ErreurEntree(f"ligne {numero} : JSON invalide") from erreur
        if not isinstance(objet, dict) or not isinstance(objet.get("filename"), str):
            raise ErreurEntree(f"ligne {numero} : champ filename manquant")
        ancien = objet.get("previous_filename")
        fichiers.append((objet["filename"], ancien if isinstance(ancien, str) else None))
    return fichiers


def echapper(nom: str) -> str:
    return "`" + nom.replace("`", "\\u0060").replace("\n", "\\n").replace("\r", "\\r") + "`"


def retirer_bloc(description: str) -> str:
    """Retire chaque bloc du garde, pour qu'il n'y en ait jamais deux."""
    while True:
        debut = description.find(DEBUT)
        fin = description.find(FIN, debut + 1)
        if debut == -1 or fin == -1:
            return description
        description = (description[:debut] + description[fin + len(FIN) :]).lstrip("\n")


def construire_bloc(proteges: list[str]) -> str:
    lignes = [DEBUT, "**Fichiers protégés modifiés (contrôle de garde) :**", ""]
    lignes += [f"- {echapper(nom)}" for nom in proteges]
    lignes.append(FIN)
    return "\n".join(lignes)


def analyser(
    motifs: list[str], fichiers: list[tuple[str, str | None]], evenement: dict[str, Any]
) -> dict[str, str]:
    pull_request = evenement.get("pull_request")
    if not isinstance(pull_request, dict):
        raise ErreurEntree("l'événement ne contient pas de pull request")
    description = str(pull_request.get("body") or "")
    presentes = {
        str(etiquette.get("name"))
        for etiquette in pull_request.get("labels") or []
        if isinstance(etiquette, dict)
    }
    proteges: list[str] = []
    for nom, ancien in fichiers:
        if est_couvert(nom, motifs) or (ancien is not None and est_couvert(ancien, motifs)):
            if nom not in proteges:
                proteges.append(nom)
    sans_bloc = retirer_bloc(description)
    if proteges:
        nouvelle = construire_bloc(proteges) + ("\n\n" + sans_bloc if sans_bloc else "\n")
        decision = "rien" if ETIQUETTE in presentes else "poser"
        resume = construire_bloc(proteges)
    else:
        nouvelle = sans_bloc
        decision = "retirer" if ETIQUETTE in presentes else "rien"
        resume = "Aucun chemin protégé modifié."
    return {"etiquette": decision, "description": nouvelle, "resume": resume}


def principal(arguments: list[str]) -> int:
    analyseur = argparse.ArgumentParser(description="Contrôle de garde")
    analyseur.add_argument("--chemins", required=True)
    analyseur.add_argument("--fichiers", required=True)
    analyseur.add_argument("--evenement", required=True)
    analyseur.add_argument("--sortie", required=True)
    options = analyseur.parse_args(arguments)
    try:
        motifs = lire_fichier_motifs(Path(options.chemins))
        fichiers = lire_fichiers_modifies(Path(options.fichiers).read_text(encoding="utf-8"))
        evenement = json.loads(Path(options.evenement).read_text(encoding="utf-8"))
        if not isinstance(evenement, dict):
            raise ErreurEntree("événement invalide")
        resultat = analyser(motifs, fichiers, evenement)
        Path(options.sortie).write_text(json.dumps(resultat, ensure_ascii=False), encoding="utf-8")
    except (ErreurEntree, OSError, json.JSONDecodeError) as erreur:
        print(f"erreur d'entrée : {erreur}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
