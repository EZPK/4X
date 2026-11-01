"""Traduction des motifs de chemins du projet (niveau 2 de M0, Technical Plan, point 8).

`**` désigne zéro ou plusieurs dossiers, `*` une suite de caractères sans `/`, et tout
autre caractère se lit tel quel. Ne dépend d'aucune version particulière de Python.
"""

import re
from pathlib import Path


def _en_regex(motif: str) -> str:
    morceaux: list[str] = []
    i = 0
    while i < len(motif):
        if motif.startswith("**/", i):
            morceaux.append("(?:.*/)?")
            i += 3
        elif motif.startswith("/**", i) and i + 3 == len(motif):
            morceaux.append("(?:/.*)?")
            i += 3
        elif motif.startswith("**", i):
            morceaux.append(".*")
            i += 2
        elif motif[i] == "*":
            morceaux.append("[^/]*")
            i += 1
        else:
            morceaux.append(re.escape(motif[i]))
            i += 1
    return "".join(morceaux)


def correspond(chemin: str, motif: str) -> bool:
    """Dit si `chemin` (relatif à la racine du dépôt, séparé par `/`) correspond à `motif`."""
    return re.fullmatch(_en_regex(motif), chemin) is not None


def lire_motifs(lignes: list[str]) -> list[str]:
    """Garde les motifs d'une liste de lignes, sans les lignes vides ni les commentaires `#`."""
    motifs: list[str] = []
    for ligne in lignes:
        propre = ligne.strip()
        if propre and not propre.startswith("#"):
            motifs.append(propre)
    return motifs


def lire_fichier_motifs(chemin: Path) -> list[str]:
    return lire_motifs(chemin.read_text(encoding="utf-8").splitlines())


def est_couvert(chemin: str, motifs: list[str]) -> bool:
    return any(correspond(chemin, motif) for motif in motifs)
