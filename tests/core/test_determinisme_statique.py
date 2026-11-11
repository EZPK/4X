"""Vérifications mécaniques du déterminisme du noyau (docs/designs/niveau-2-m1-noyau.md,
Technical Plan, point 4 ; plan détaillé, point 7 bis).

Chemin protégé. L'analyse porte sur les sources de src/fourx/core/ trouvées depuis la racine
du dépôt, jamais sur une copie instrumentée (mutmut l'exclut, setup.cfg).
"""

import ast
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
NOYAU = RACINE / "src" / "fourx" / "core"

IMPORTS_PERMIS = frozenset(
    {
        "__future__",
        "enum",
        "typing",
        "hashlib",
        "msgspec",
        "msgspec.structs",
        "msgspec.msgpack",
        "msgspec.inspect",
    }
)
PREFIXES_PERMIS = ("fourx.schema", "fourx.core")
FONCTIONS_INTERDITES = frozenset(
    {
        "float",
        "hash",
        "id",
        "divmod",
        "pow",
        "round",
        "open",
        "input",
        "vars",
        "globals",
        "eval",
        "exec",
        "compile",
        "__import__",
        "set",
        "frozenset",
    }
)
OPERATEURS_DIVISION = {ast.Div: "/", ast.FloorDiv: "//", ast.Mod: "%"}
EXEMPTION_ARITH = frozenset({ast.FloorDiv, ast.Mod})


def _import_permis(nom: str) -> bool:
    if nom in IMPORTS_PERMIS:
        return True
    return any(nom == p or nom.startswith(p + ".") for p in PREFIXES_PERMIS)


def _paquet(nom_fichier: str) -> str:
    """Paquet d'un fichier du noyau : src/fourx/core/a/b.py → fourx.core.a."""
    parties = Path(nom_fichier).parent.parts
    if "core" not in parties:
        return "fourx.core"
    return ".".join(("fourx", *parties[parties.index("core") :]))


def _absolu(noeud: ast.ImportFrom, paquet: str) -> str:
    """Nom absolu du module d'un import, relatif ou non."""
    if noeud.level == 0:
        return noeud.module or ""
    base = paquet.split(".")
    base = base[: len(base) - (noeud.level - 1)]
    return ".".join([*base, noeud.module] if noeud.module else base)


def violations(source: str, nom_fichier: str) -> list[str]:
    """Liste les violations des invariants de déterminisme dans une source du noyau."""
    arbre = ast.parse(source, filename=nom_fichier)
    exempte = Path(nom_fichier).name == "arith.py" and Path(nom_fichier).parent.name == "core"
    paquet = _paquet(nom_fichier)
    appelees = {
        id(n.func)
        for n in ast.walk(arbre)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    trouvees: list[tuple[int, int, str]] = []

    def signaler(noeud: ast.AST, message: str) -> None:
        ligne = getattr(noeud, "lineno", 0)
        trouvees.append(
            (ligne, getattr(noeud, "col_offset", 0), f"{nom_fichier}:{ligne}: {message}")
        )

    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Constant) and isinstance(noeud.value, (float, complex)):
            signaler(noeud, "nombre flottant")
        elif isinstance(noeud, (ast.BinOp, ast.AugAssign)):
            operateur = type(noeud.op)
            if operateur in OPERATEURS_DIVISION and not (exempte and operateur in EXEMPTION_ARITH):
                signaler(noeud, f"opérateur {OPERATEURS_DIVISION[operateur]}")
            elif operateur is ast.Pow:
                exposant = noeud.right if isinstance(noeud, ast.BinOp) else noeud.value
                if not (
                    isinstance(exposant, ast.Constant)
                    and type(exposant.value) is int
                    and exposant.value >= 0
                ):
                    signaler(noeud, "** sans exposant littéral positif ou nul")
        elif isinstance(noeud, (ast.Set, ast.SetComp)):
            signaler(noeud, "ensemble")
        elif isinstance(noeud, ast.Name):
            if noeud.id == "__builtins__":
                signaler(noeud, "usage de __builtins__")
            elif noeud.id in FONCTIONS_INTERDITES:
                if noeud.id != "id" or id(noeud) in appelees:
                    signaler(noeud, f"usage de {noeud.id}")
        elif isinstance(noeud, ast.Import):
            for alias in noeud.names:
                if not _import_permis(alias.name):
                    signaler(noeud, f"import interdit : {alias.name}")
        elif isinstance(noeud, ast.ImportFrom):
            module = _absolu(noeud, paquet)
            if not _import_permis(module) and not all(
                _import_permis(f"{module}.{alias.name}") for alias in noeud.names
            ):
                signaler(noeud, f"import interdit : {module}")
    return [message for _, _, message in sorted(trouvees)]


def test_le_noyau_respecte_les_invariants() -> None:
    sources = sorted(NOYAU.rglob("*.py"))
    assert sources, "src/fourx/core/ est introuvable"
    toutes = [
        v for chemin in sources for v in violations(chemin.read_text(encoding="utf-8"), str(chemin))
    ]
    assert toutes == []


def test_refuse_les_flottants_et_les_divisions() -> None:
    source = "x = 1.5\ny = 3 / 2\nz = 3 // 2\nw = 3 % 2\nx //= 2\n"
    messages = [v.split(": ", 1)[1] for v in violations(source, "core/step.py")]
    assert messages == [
        "nombre flottant",
        "opérateur /",
        "opérateur //",
        "opérateur %",
        "opérateur //",
    ]


def test_arith_peut_employer_division_entiere_et_reste_seulement() -> None:
    assert violations("a = 7 // 2\nb = 7 % 2\n", "core/arith.py") == []
    assert len(violations("a = 7 / 2\n", "core/arith.py")) == 1


def test_puissance_permise_seulement_avec_exposant_litteral_positif() -> None:
    assert violations("a = 2 ** 63\nb = x ** 0\n", "core/x.py") == []
    assert len(violations("a = 2 ** -1\n", "core/x.py")) == 1
    assert len(violations("a = 2 ** n\n", "core/x.py")) == 1
    assert len(violations("a = 2 ** 1.0\n", "core/x.py")) == 2


def test_refuse_les_ensembles_et_les_fonctions_interdites() -> None:
    source = (
        "a = {1, 2}\nb = {x for x in y}\nc = set()\nd = hash('s')\ne = id(a)\nf = divmod(1, 2)\n"
    )
    assert len(violations(source, "core/x.py")) == 6


def test_un_champ_nomme_id_reste_permis() -> None:
    source = "def label(table: str, id: int) -> str:\n    return table + str(id)\n\nx = obj.id\n"
    assert violations(source, "core/x.py") == []


def test_liste_fermee_des_imports() -> None:
    permis = (
        "import hashlib\nimport msgspec\nfrom msgspec import structs\nimport msgspec.msgpack\n"
        "from typing import Annotated\nfrom fourx.schema.orders import Order\nfrom . import arith\n"
        "from fourx.core.arith import div_trunc\n"
    )
    assert violations(permis, "core/x.py") == []
    for interdit in (
        "import random",
        "import time",
        "from datetime import date",
        "import os",
        "import math",
        "from fourx.server import game",
        "import decimal",
        "from mutmut.mutation.trampoline import wrap_in_trampoline",
    ):
        assert len(violations(interdit + "\n", "core/x.py")) == 1, interdit


def test_imports_relatifs_resolus() -> None:
    assert violations("from . import arith\nfrom .arith import div_trunc\n", "core/x.py") == []
    assert violations("from .. import schema\n", "core/x.py") == []
    assert len(violations("from .. import server\n", "core/x.py")) == 1
    assert len(violations("from ..tools import replay\n", "core/x.py")) == 1
    assert violations("from .. import arith\n", "src/fourx/core/sous/x.py") == []


def test_exemption_seulement_pour_core_arith() -> None:
    assert len(violations("a = 7 // 2\n", "src/fourx/core/sous/arith.py")) == 1
    assert violations("a = 7 // 2\n", "src/fourx/core/arith.py") == []


def test_appels_detournes_refuses() -> None:
    assert len(violations("f = float\n", "core/x.py")) == 1
    assert len(violations("x = __builtins__.round(1)\n", "core/x.py")) == 1
    assert len(violations("x = getattr(__builtins__, 'hash')\n", "core/x.py")) == 1
