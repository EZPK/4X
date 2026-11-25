"""La suite canari : des bugs volontaires que les contrôles doivent attraper.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, points 29 et 30 bis (tâche `canari`
du workflow de nuit).

Chaque canari est un fichier JSON de `.github/canaris/` : le contrôle visé, et une liste de
modifications. Une modification désigne un fichier, une ancre et un texte :
- `debut_de_fonction` (`fonction`) : le texte est inséré avant la première instruction du corps
  de la fonction nommée (après sa docstring), au retrait de ce corps ;
- `fin_du_module` : le texte est ajouté à la fin du fichier ;
- `expression` (`fonction`, `appel`, `contient`) : dans la fonction nommée, l'appel à `appel`
  (texte de la fonction appelée, par exemple `t.passer`) dont le texte source contient `contient`
  est remplacé par le texte ; l'ancre doit désigner exactement un appel. Si cet appel forme à lui
  seul une instruction, le texte peut être une instruction.

Les ancres sont trouvées par l'analyse de la syntaxe (module `ast`), pas par un patch de lignes, et
le fichier modifié doit encore se lire. Pour chaque canari, le script clone le dépôt dans un
dossier temporaire, applique les modifications, les enregistre dans un commit du clone, lance la
commande du contrôle visé (celles du plan détaillé, point 8) et échoue si cette commande réussit.

Bibliothèque standard seulement.
"""

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DOSSIER = RACINE / ".github" / "canaris"
PYTEST_TESTS = (
    'uv run pytest -m "not rejeu and not proprietes and not lent and not mesure" '
    "--ignore=tests/outillage"
)
COMMANDES = {
    "tests": PYTEST_TESTS,
    "imports": "uv run lint-imports",
    "proprietes": "uv run pytest -m proprietes",
    "rejeu": (
        "PYTHONHASHSEED=0 uv run pytest -m rejeu"
        " && PYTHONHASHSEED=1 uv run pytest -m rejeu"
        " && uv run python -m fourx.tools.divergence"
        " runs/rejeu-0/fingerprints.jsonl runs/rejeu-1/fingerprints.jsonl"
        " && uv run pytest -m lent"
    ),
    "mutation": "uv run python .github/scripts/mutation.py --base {base} --tete {tete}",
}
IDENTITE = ["-c", "user.name=canari", "-c", "user.email=canari@invalid"]


class ErreurCanari(Exception):
    """Un canari mal formé, ou une ancre introuvable."""


@dataclass(frozen=True)
class Modification:
    fichier: str
    ancre: dict[str, str]
    texte: str


@dataclass(frozen=True)
class Canari:
    nom: str
    description: str
    controle: str
    modifications: tuple[Modification, ...]


def lire(chemin: Path) -> Canari:
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    if donnees.get("controle") not in COMMANDES:
        raise ErreurCanari(f"{chemin.name} : contrôle inconnu {donnees.get('controle')!r}")
    modifications = tuple(
        Modification(fichier=m["fichier"], ancre=dict(m["ancre"]), texte=m["texte"])
        for m in donnees["modifications"]
    )
    if not modifications:
        raise ErreurCanari(f"{chemin.name} : aucune modification")
    return Canari(
        nom=chemin.stem,
        description=donnees["description"],
        controle=donnees["controle"],
        modifications=modifications,
    )


def lire_tous(dossier: Path = DOSSIER) -> tuple[Canari, ...]:
    return tuple(lire(chemin) for chemin in sorted(dossier.glob("*.json")))


def _decalages(source: str) -> list[int]:
    """Position, dans `source`, du début de chaque ligne (la ligne 1 au rang 0)."""
    debuts = [0, 0]
    for ligne in source.splitlines(keepends=True):
        debuts.append(debuts[-1] + len(ligne))
    return debuts


def _position(source: str, ligne: int, colonne: int) -> int:
    """Position dans `source` d'une ligne (à partir de 1) et d'une colonne en octets UTF-8."""
    debut = _decalages(source)[ligne]
    texte_de_ligne = source[debut:].splitlines(keepends=True)[0] if source[debut:] else ""
    return debut + len(texte_de_ligne.encode("utf-8")[:colonne].decode("utf-8"))


def _fonction(arbre: ast.Module, nom: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.FunctionDef | ast.AsyncFunctionDef) and noeud.name == nom:
            return noeud
    raise ErreurCanari(f"fonction {nom!r} introuvable")


def _indenter(texte: str, retrait: int) -> str:
    marge = " " * retrait
    return "\n".join(marge + ligne if ligne else "" for ligne in texte.splitlines())


def appliquer(source: str, modification: Modification) -> str:
    """Le texte de `source` après la modification ; lève ErreurCanari si l'ancre manque ou si le
    résultat ne se lit plus."""
    arbre = ast.parse(source)
    genre = modification.ancre.get("type")
    if genre == "fin_du_module":
        resultat = source.rstrip("\n") + "\n" + modification.texte + "\n"
    elif genre == "debut_de_fonction":
        fonction = _fonction(arbre, modification.ancre["fonction"])
        corps = fonction.body
        premiere = corps[0]
        if (
            isinstance(premiere, ast.Expr)
            and isinstance(premiere.value, ast.Constant)
            and isinstance(premiere.value.value, str)
            and len(corps) > 1
        ):
            premiere = corps[1]
        debut = _position(source, premiere.lineno, 0)
        insertion = _indenter(modification.texte, premiere.col_offset) + "\n"
        resultat = source[:debut] + insertion + source[debut:]
    elif genre == "expression":
        fonction = _fonction(arbre, modification.ancre["fonction"])
        appel, motif = modification.ancre["appel"], modification.ancre["contient"]
        trouvees = [
            noeud
            for noeud in ast.walk(fonction)
            if isinstance(noeud, ast.Call)
            and ast.get_source_segment(source, noeud.func) == appel
            and motif in (ast.get_source_segment(source, noeud) or "")
        ]
        if len(trouvees) != 1:
            raise ErreurCanari(
                f"{len(trouvees)} appels à {appel!r} contenant {motif!r} dans {fonction.name!r}"
                " (il en faut exactement un)"
            )
        trouvee = trouvees[0]
        if trouvee.end_lineno is None or trouvee.end_col_offset is None:
            raise ErreurCanari(f"position de l'appel à {appel!r} inconnue")
        debut = _position(source, trouvee.lineno, trouvee.col_offset)
        fin = _position(source, trouvee.end_lineno, trouvee.end_col_offset)
        resultat = source[:debut] + modification.texte + source[fin:]
    else:
        raise ErreurCanari(f"ancre inconnue : {modification.ancre}")
    try:
        ast.parse(resultat)
    except SyntaxError as erreur:
        raise ErreurCanari(f"{modification.fichier} ne se lit plus : {erreur}") from erreur
    return resultat


def appliquer_canari(racine: Path, canari: Canari) -> None:
    for modification in canari.modifications:
        chemin = racine / modification.fichier
        if not chemin.is_file():
            raise ErreurCanari(f"{canari.nom} : fichier {modification.fichier} introuvable")
        chemin.write_text(
            appliquer(chemin.read_text(encoding="utf-8"), modification), encoding="utf-8"
        )


def git(dossier: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *IDENTITE, *arguments],
        cwd=dossier,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def essayer(canari: Canari, depot: Path, commandes: dict[str, str]) -> tuple[bool, str]:
    """Clone `depot`, applique le canari, l'enregistre et lance la commande du contrôle visé.
    Rend (attrapé, compte rendu) : attrapé si la commande échoue."""
    with tempfile.TemporaryDirectory(prefix=f"canari-{canari.nom}-") as temporaire:
        copie = Path(temporaire) / "depot"
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(depot), str(copie)],
            check=True,
            capture_output=True,
        )
        base = git(copie, "rev-parse", "HEAD")
        appliquer_canari(copie, canari)
        git(copie, "commit", "--quiet", "--all", "--message", f"canari {canari.nom}")
        tete = git(copie, "rev-parse", "HEAD")
        commande = commandes[canari.controle].format(base=base, tete=tete)
        resultat = subprocess.run(
            ["bash", "-c", commande], cwd=copie, capture_output=True, text=True, check=False
        )
    attrape = resultat.returncode != 0
    fin = (resultat.stdout + resultat.stderr).strip().splitlines()[-5:]
    compte_rendu = f"{canari.nom} → {canari.controle} : code {resultat.returncode}"
    if not attrape:
        compte_rendu += " — NON ATTRAPÉ\n    " + "\n    ".join(fin)
    return attrape, compte_rendu


def main(argv: list[str] | None = None, commandes: dict[str, str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description="Suite canari de M1")
    analyseur.add_argument("--depot", type=Path, default=RACINE)
    analyseur.add_argument("--canaris", type=Path, default=DOSSIER)
    analyseur.add_argument("--seulement", action="append", default=[], metavar="NOM")
    options = analyseur.parse_args(argv)
    try:
        canaris = lire_tous(options.canaris)
        if options.seulement:
            inconnus = set(options.seulement) - {c.nom for c in canaris}
            if inconnus:
                raise ErreurCanari(f"canaris inconnus : {sorted(inconnus)}")
            canaris = tuple(c for c in canaris if c.nom in options.seulement)
        if not canaris:
            raise ErreurCanari("aucun canari")
        echecs = 0
        for canari in canaris:
            attrape, compte_rendu = essayer(canari, options.depot, commandes or COMMANDES)
            print(compte_rendu, flush=True)
            echecs += not attrape
    except (ErreurCanari, subprocess.CalledProcessError) as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 2
    print(f"{len(canaris) - echecs} canaris attrapés sur {len(canaris)}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
