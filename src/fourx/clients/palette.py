"""La palette de l'écran rétro : seize couleurs, une par rôle.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter (palette). Ce sont des
valeurs RGB rendues en couleurs 24 bits, et non les seize couleurs ANSI du terminal. Les valeurs
sont retouchables sans amendement : les tests de contraste font foi. `CONTRAST_PAIRS` liste les
couples (texte, fond) employés, à 4,5 pour 1 au moins ; `GRAPHIC_PAIRS` les traits et les barres,
à 3 pour 1 au moins (WCAG 2.1).
"""

PALETTE: dict[str, str] = {
    "fond": "#0B0E1A",
    "cadre": "#121830",
    "cadre_clair": "#1B2444",
    "trait": "#2B3557",
    "trait_fort": "#7B89C2",
    "trait_faible": "#5E6A99",
    "texte_attenue": "#8B97C3",
    "texte": "#E8ECF8",
    "accent": "#3FD0E0",
    "ore_a": "#F2A33A",
    "ore_b": "#5AA0FF",
    "succes": "#5BD46A",
    "alerte": "#F0506E",
    "vaisseau": "#F5E14A",
    "station": "#A98BFF",
    "ombre": "#000000",
}

COULEURS_DE_TEXTE = (
    "texte",
    "texte_attenue",
    "accent",
    "ore_a",
    "ore_b",
    "succes",
    "alerte",
    "vaisseau",
    "station",
)

CONTRAST_PAIRS: tuple[tuple[str, str], ...] = (
    tuple((couleur, fond) for fond in ("fond", "cadre") for couleur in COULEURS_DE_TEXTE)
    + (("texte", "cadre_clair"), ("texte_attenue", "cadre_clair"))
    + tuple(
        ("fond", etiquette) for etiquette in ("station", "alerte", "accent", "succes", "vaisseau")
    )
)

GRAPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("trait_fort", "fond"),
    ("trait_faible", "fond"),
    ("accent", "cadre"),
    ("trait_faible", "cadre"),
)


def _lineaire(composante: int) -> float:
    c = composante / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(couleur: str) -> float:
    """Luminance relative d'une couleur « #RRGGBB » (WCAG 2.1)."""
    rouge, vert, bleu = (int(couleur[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _lineaire(rouge) + 0.7152 * _lineaire(vert) + 0.0722 * _lineaire(bleu)


def contrast_ratio(premier: str, second: str) -> float:
    """Rapport de contraste entre deux rôles de la palette (WCAG 2.1), de 1 à 21."""
    claire, sombre = sorted((luminance(PALETTE[premier]), luminance(PALETTE[second])), reverse=True)
    return (claire + 0.05) / (sombre + 0.05)
