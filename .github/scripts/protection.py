"""Vérifie chaque nuit que la protection de `main` est en place.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, points 30 bis et 31 bis (tâche
`protection` du workflow de nuit).

Lit https://api.github.com/repos/EZPK/4X/branches/main, avec le jeton `GITHUB_TOKEN` en lecture
seule s'il est défini (il évite la limite des lectures sans jeton), et échoue si `protected` est
faux, si `enforcement_level` n'est pas `everyone`, ou si la liste des contrôles exigés diffère de
celle de `.github/protection-main.json`. Bibliothèque standard seulement.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
URL = "https://api.github.com/repos/EZPK/4X/branches/main"
REFERENCE = RACINE / ".github" / "protection-main.json"


def controles_attendus(reference: Path = REFERENCE) -> list[str]:
    donnees = json.loads(reference.read_text(encoding="utf-8"))
    return list(donnees["required_status_checks"]["contexts"])


def verifier(reponse: dict[str, object], attendus: list[str]) -> list[str]:
    """Les écarts de la branche lue à la protection attendue ; vide si elle est en place."""
    erreurs: list[str] = []
    if reponse.get("protected") is not True:
        erreurs.append("main n'est pas protégée")
    protection = reponse.get("protection")
    controles = protection.get("required_status_checks") if isinstance(protection, dict) else None
    if not isinstance(controles, dict):
        erreurs.append("aucun contrôle exigé")
        return erreurs
    niveau = controles.get("enforcement_level")
    if niveau != "everyone":
        erreurs.append(f"enforcement_level vaut {niveau!r} au lieu de 'everyone'")
    lus = controles.get("contexts")
    if not isinstance(lus, list) or sorted(map(str, lus)) != sorted(attendus):
        erreurs.append(f"contrôles exigés {lus!r} au lieu de {sorted(attendus)!r}")
    return erreurs


def lire(url: str = URL) -> dict[str, object]:
    requete = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    jeton = os.environ.get("GITHUB_TOKEN")
    if jeton:
        requete.add_header("Authorization", f"Bearer {jeton}")
    with urllib.request.urlopen(requete, timeout=30) as reponse:  # noqa: S310 (URL fixe)
        donnees = json.load(reponse)
    if not isinstance(donnees, dict):
        raise ValueError("réponse inattendue de l'API")
    return donnees


def main() -> int:
    erreurs = verifier(lire(), controles_attendus())
    for erreur in erreurs:
        print(f"Protection de main : {erreur}")
    if not erreurs:
        print("Protection de main en place.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
