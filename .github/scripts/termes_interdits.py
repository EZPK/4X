"""Contrôle des termes interdits.

Niveau 2 de M0 : Technical Plan, point 9 ; plan détaillé, point 17.

Codes de sortie : 0 aucune occurrence, 1 au moins une occurrence, 2 erreur d'entrée.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motifs import est_couvert, lire_motifs  # noqa: E402

LISTE_PAR_DEFAUT = "docs/termes-interdits.md"


class ErreurEntree(Exception):
    pass


def lire_sections(texte: str) -> dict[str, list[str]]:
    """Découpe le fichier de liste en sections `## Titre` -> lignes non vides."""
    sections: dict[str, list[str]] = {}
    courante: str | None = None
    for ligne in texte.splitlines():
        if ligne.startswith("## "):
            courante = ligne[3:].strip()
            sections[courante] = []
        elif ligne.startswith("#"):
            courante = None
        elif courante is not None and ligne.strip():
            sections[courante].append(ligne.strip())
    return sections


def _bord(texte: str, position: int) -> bool:
    if position < 0 or position >= len(texte):
        return True
    caractere = texte[position]
    return not (caractere.isalnum() or caractere == "_")


def occurrences(texte: str, terme: str) -> list[int]:
    """Numéros de ligne (à partir de 1) où `terme` apparaît comme mot entier, sans casse."""
    bas = texte.lower()
    cible = terme.lower()
    lignes: list[int] = []
    debut = bas.find(cible)
    while debut != -1:
        fin = debut + len(cible)
        if _bord(texte, debut - 1) and _bord(texte, fin):
            numero = texte.count("\n", 0, debut) + 1
            if numero not in lignes:
                lignes.append(numero)
        debut = bas.find(cible, debut + 1)
    return lignes


def fichiers_suivis() -> list[str]:
    sortie = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True, text=True
    ).stdout
    return [chemin for chemin in sortie.split("\0") if chemin]


def analyser_textes(textes: list[tuple[str, str]], termes: list[str]) -> list[str]:
    resultats: list[str] = []
    for nom, texte in textes:
        for terme in termes:
            for numero in occurrences(texte, terme):
                resultats.append(f"{nom}:{numero}: terme « {terme} »")
    return resultats


def analyser_fichiers(chemins: list[str], exclus: list[str], termes: list[str]) -> list[str]:
    textes: list[tuple[str, str]] = []
    for chemin in chemins:
        if est_couvert(chemin, exclus):
            continue
        fichier = Path(chemin)
        if not fichier.is_file():
            continue
        contenu = fichier.read_bytes()
        if b"\0" in contenu:
            continue
        textes.append((chemin, contenu.decode("utf-8", errors="replace")))
    return analyser_textes(textes, termes)


def lire_evenement(chemin: Path) -> list[tuple[str, str]]:
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erreur:
        raise ErreurEntree(f"événement illisible : {erreur}") from erreur
    pull_request = donnees.get("pull_request")
    if not isinstance(pull_request, dict):
        return []
    tete = pull_request.get("head") or {}
    return [
        ("titre de la pull request", str(pull_request.get("title") or "")),
        ("description de la pull request", str(pull_request.get("body") or "")),
        ("nom de la branche", str(tete.get("ref") or "")),
    ]


def principal(arguments: list[str]) -> int:
    analyseur = argparse.ArgumentParser(description="Contrôle des termes interdits")
    analyseur.add_argument("--liste", default=LISTE_PAR_DEFAUT)
    analyseur.add_argument("--evenement")
    analyseur.add_argument("--fichiers")
    analyseur.add_argument("--messages")
    options = analyseur.parse_args(arguments)
    try:
        try:
            sections = lire_sections(Path(options.liste).read_text(encoding="utf-8"))
        except OSError as erreur:
            raise ErreurEntree(f"liste illisible : {erreur}") from erreur
        termes = sections.get("Termes", [])
        exclus = lire_motifs(sections.get("Fichiers exclus", []))
        if not termes:
            raise ErreurEntree("aucun terme sous « ## Termes »")
        resultats = analyser_fichiers(fichiers_suivis(), exclus, termes)

        seule_la_liste = False
        if options.fichiers:
            modifies = lire_motifs(Path(options.fichiers).read_text(encoding="utf-8").splitlines())
            seule_la_liste = modifies == [LISTE_PAR_DEFAUT]
        textes: list[tuple[str, str]] = []
        if options.evenement:
            for nom, texte in lire_evenement(Path(options.evenement)):
                if seule_la_liste and nom != "nom de la branche":
                    continue
                textes.append((nom, texte))
        if options.messages and not seule_la_liste:
            brut = Path(options.messages).read_text(encoding="utf-8")
            for rang, message in enumerate(m for m in brut.split("\0") if m.strip()):
                textes.append((f"message de commit {rang + 1}", message))
        resultats += analyser_textes(textes, termes)
    except (ErreurEntree, OSError, subprocess.CalledProcessError) as erreur:
        print(f"erreur d'entrée : {erreur}", file=sys.stderr)
        return 2
    for ligne in resultats:
        print(ligne)
    return 1 if resultats else 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
