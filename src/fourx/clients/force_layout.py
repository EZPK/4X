"""La disposition de la carte par forces : les systèmes se repoussent, les liens les retiennent.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter (disposition de la
carte) et point 13 (interface). Fonctions pures, sans tirage aléatoire : les mêmes systèmes donnent
les mêmes positions. La disposition ne dépend que du graphe, qui ne change pas pendant la partie :
elle est calculée une fois. Elle calcule en flottants et n'entre dans aucune empreinte (les
invariants de déterminisme ne valent que pour `core`).

Les positions sont dans le carré [0, 1] × [0, 1], axe des y vers le bas. Cinq étapes :
1. `initial_layers` : départ en couches, par distance en sauts depuis le plus petit identifiant ;
2. `relax` : 300 itérations de répulsion, de ressorts et de rappel vers l'origine ;
3. `normalize` : une échelle par axe : les positions remplissent le rectangle utile R ;
4. `separate` : les boîtes des systèmes (7 × 5 cases d'une carte de 70 × 23, à partir du coin
   en haut à gauche du cadre, vers la droite et vers le bas) sont
   écartées jusqu'à ne plus se recouvrir, en au plus 100 passes ;
5. `snap_overlaps` : un système encore en recouvrement va au point libre le plus proche d'un
   quadrillage au quart de boîte.
"""

import math
from collections.abc import Iterable

from fourx.policies.geometry import distances
from fourx.schema.observation import SystemView

Position = tuple[float, float]
Positions = dict[int, Position]

ITERATIONS = 300
PAS_INITIAL = 0.1
DISTANCE_MINIMALE = 0.01
RAPPEL = 0.05
# La boîte d'un système, dans la plus petite carte (70 × 23 cases, terminal de 120 × 36) :
# 7 colonnes (cadre de 4, étiquette de station de 2, une de marge) et 5 lignes (cadre de 3,
# gisement et stock, une de marge), à partir du coin en haut à gauche du cadre, plus une
# demi-case de réserve dans chaque sens, pour que l'arrondi aux cases garde la case de marge.
CARTE_MINIMALE = (70, 23)
LARGEUR_BOITE = 7.5 / CARTE_MINIMALE[0]
HAUTEUR_BOITE = 5.5 / CARTE_MINIMALE[1]
RECTANGLE_UTILE = (0.0, 0.0, 1 - LARGEUR_BOITE, 1 - HAUTEUR_BOITE)
PASSES_MAXIMALES = 100
QUART = 4
TOLERANCE = 1e-9


def initial_layers(systems: tuple[SystemView, ...]) -> Positions:
    """La couche k (distance k depuis le plus petit identifiant) est répartie régulièrement sur un
    cercle de rayon k, par identifiants croissants, à partir de l'angle 0,5 × k, dans le sens
    trigonométrique ; les systèmes non atteints forment une dernière couche."""
    if not systems:
        return {}
    depart = min(s.id for s in systems)
    dist = distances(systems, depart)
    derniere = max(dist.values()) + 1
    couches: dict[int, list[int]] = {}
    for s in sorted(systems, key=lambda s: s.id):
        couches.setdefault(dist.get(s.id, derniere), []).append(s.id)
    positions: Positions = {}
    for k, membres in couches.items():
        for rang, ident in enumerate(membres):
            if k == 0:
                positions[ident] = (0.0, 0.0)
                continue
            angle = 0.5 * k + 2 * math.pi * rang / len(membres)
            positions[ident] = (k * math.cos(angle), k * math.sin(angle))
    return positions


def _unitaire(dx: float, dy: float) -> tuple[float, float, float]:
    """Le vecteur unitaire de (dx, dy) et sa norme ; (1, 0) si le vecteur est nul."""
    d = math.hypot(dx, dy)
    if d == 0:
        return 1.0, 0.0, 0.0
    return dx / d, dy / d, d


def relax(systems: tuple[SystemView, ...], positions: Positions) -> Positions:
    """300 itérations : répulsion 1 ÷ d² de chaque autre système (d bornée à 0,01), ressort
    (d − 1) vers chaque voisin, rappel −0,05 × p vers l'origine ; chaque système se déplace dans la
    direction de sa force, d'au plus le pas 0,1 × (1 − i ÷ 300). Tous se déplacent ensemble."""
    idents = sorted(positions)
    voisins = {s.id: tuple(v for v in s.neighbors if v in positions) for s in systems}
    courantes = dict(positions)
    for i in range(ITERATIONS):
        pas = PAS_INITIAL * (1 - i / ITERATIONS)
        suivantes: Positions = {}
        for a in idents:
            xa, ya = courantes[a]
            fx, fy = -RAPPEL * xa, -RAPPEL * ya
            for b in idents:
                if b == a:
                    continue
                ux, uy, d = _unitaire(xa - courantes[b][0], ya - courantes[b][1])
                repulsion = 1 / max(d, DISTANCE_MINIMALE) ** 2
                fx += repulsion * ux
                fy += repulsion * uy
            for v in voisins.get(a, ()):
                ux, uy, d = _unitaire(courantes[v][0] - xa, courantes[v][1] - ya)
                fx += (d - 1) * ux
                fy += (d - 1) * uy
            ux, uy, norme = _unitaire(fx, fy)
            longueur = min(norme, pas)
            suivantes[a] = (xa + longueur * ux, ya + longueur * uy) if norme else (xa, ya)
        courantes = suivantes
    return courantes


def normalize(positions: Positions) -> Positions:
    """La boîte englobante des positions remplit le rectangle utile R : une échelle par axe, pour
    que la carte occupe toute sa largeur et toute sa hauteur, comme la maquette validée ; sur un
    axe où toutes les positions sont égales, elles sont placées au milieu de R."""
    if not positions:
        return {}
    x0, y0, x1, y1 = RECTANGLE_UTILE
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]

    def axe(v: float, valeurs: list[float], debut: float, fin: float) -> float:
        bas, haut = min(valeurs), max(valeurs)
        if haut == bas:
            return (debut + fin) / 2
        return debut + (v - bas) * (fin - debut) / (haut - bas)

    return {i: (axe(x, xs, x0, x1), axe(y, ys, y0, y1)) for i, (x, y) in positions.items()}


def _borne(valeur: float, bas: float, haut: float) -> float:
    return min(max(valeur, bas), haut)


def _dans_r(position: Position) -> Position:
    x0, y0, x1, y1 = RECTANGLE_UTILE
    return _borne(position[0], x0, x1), _borne(position[1], y0, y1)


def _paires(idents: Iterable[int]) -> list[tuple[int, int]]:
    tries = sorted(idents)
    return [(a, b) for rang, a in enumerate(tries) for b in tries[rang + 1 :]]


def recouvrement(a: Position, b: Position) -> bool:
    """Deux boîtes se recouvrent si leurs écarts sur les deux axes sont inférieurs à leurs
    dimensions (à 1e-9 près : deux boîtes qui se touchent ne se recouvrent pas)."""
    return (
        abs(a[0] - b[0]) < LARGEUR_BOITE - TOLERANCE
        and abs(a[1] - b[1]) < HAUTEUR_BOITE - TOLERANCE
    )


def _ecarter(pa: Position, pb: Position) -> tuple[Position, Position]:
    """Écarte deux boîtes en recouvrement sur l'axe qui demande le plus petit déplacement
    (l'horizontal à égalité), chacune de la moitié ; une boîte arrêtée par un bord de R laisse le
    reste du déplacement à l'autre. À positions égales sur l'axe, la première recule (à gauche, ou
    en haut)."""
    manque_x = LARGEUR_BOITE - abs(pa[0] - pb[0])
    manque_y = HAUTEUR_BOITE - abs(pa[1] - pb[1])
    axe = 0 if manque_x <= manque_y else 1
    manque = manque_x if axe == 0 else manque_y
    x0, y0, x1, y1 = RECTANGLE_UTILE
    bas, haut = (x0, x1) if axe == 0 else (y0, y1)
    signe = 1.0 if pa[axe] > pb[axe] else -1.0
    va = _borne(pa[axe] + signe * manque / 2, bas, haut)
    vb = _borne(pb[axe] - signe * (manque - abs(va - pa[axe])), bas, haut)
    reste = manque - abs(va - pa[axe]) - abs(vb - pb[axe])
    if reste > 0:
        va = _borne(va + signe * reste, bas, haut)
    if axe == 0:
        return (va, pa[1]), (vb, pb[1])
    return (pa[0], va), (pb[0], vb)


def separate(positions: Positions) -> Positions:
    """Au plus 100 passes : chaque paire en recouvrement, par identifiants croissants, est écartée
    tout de suite (`_ecarter`), dans R. Une passe sans recouvrement arrête la séparation ; au-delà
    de 100 passes, les positions sont rendues telles quelles, pour `snap_overlaps`."""
    courantes = {i: _dans_r(p) for i, p in positions.items()}
    paires = _paires(courantes)
    for _ in range(PASSES_MAXIMALES):
        ecarte = False
        for a, b in paires:
            if recouvrement(courantes[a], courantes[b]):
                ecarte = True
                courantes[a], courantes[b] = _ecarter(courantes[a], courantes[b])
        if not ecarte:
            break
    return courantes


def _points_du_quadrillage() -> list[Position]:
    """Les points de R au pas d'un quart de boîte, de gauche à droite puis de haut en bas."""
    x0, y0, x1, y1 = RECTANGLE_UTILE
    pas_x, pas_y = LARGEUR_BOITE / QUART, HAUTEUR_BOITE / QUART
    colonnes = int((x1 - x0) / pas_x + TOLERANCE) + 1
    lignes = int((y1 - y0) / pas_y + TOLERANCE) + 1
    return [(x0 + i * pas_x, y0 + j * pas_y) for j in range(lignes) for i in range(colonnes)]


def snap_overlaps(positions: Positions) -> Positions:
    """Le filet de sécurité : par identifiants croissants, un système dont la boîte en recouvre
    encore une autre va au point du quadrillage (pas d'un quart de boîte) le plus proche dont la
    boîte n'en recouvre aucune (à distance égale, le plus haut, puis le plus à gauche). S'il n'y en
    a aucun, il reste où il est."""
    courantes = dict(positions)
    points = _points_du_quadrillage()
    for a in sorted(courantes):
        autres = [courantes[b] for b in sorted(courantes) if b != a]
        if not any(recouvrement(courantes[a], q) for q in autres):
            continue
        libres = [c for c in points if not any(recouvrement(c, q) for q in autres)]
        if libres:
            xa, ya = courantes[a]
            courantes[a] = min(
                libres, key=lambda c: ((c[0] - xa) ** 2 + (c[1] - ya) ** 2, c[1], c[0])
            )
    return courantes


def force_layout(systems: tuple[SystemView, ...]) -> Positions:
    """La position de chaque système dans le carré [0, 1] × [0, 1], axe des y vers le bas."""
    return snap_overlaps(separate(normalize(relax(systems, initial_layers(systems)))))
