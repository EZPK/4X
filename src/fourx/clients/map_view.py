"""La vue de la carte : projection, zoom, déplacement, système sous le pointeur, grille de cases.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter (vue de la carte) et
point 13 (interface). Fonctions pures, testées sans Textual ; `MapCanvas` (frames.py) ne fait que
peindre la grille que rend `render`.

Une case de caractère porte deux pixels, l'un au-dessus de l'autre (caractère `▀` : l'avant-plan
est le pixel du haut, le fond celui du bas). Au zoom 1, le carré [0, 1] × [0, 1] occupe toute la
hauteur de la carte, à deux pixels par ligne, et il est centré en largeur. Ordre de dessin :
liens, route, systèmes, vaisseaux, étiquettes.
"""

import math
from dataclasses import dataclass, replace

from fourx.clients.model import ClientModel
from fourx.clients.texts import systeme
from fourx.policies.geometry import distances
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OwnShipView

ZOOMS = (1.0, 1.5, 2.0, 3.0, 4.0)
ZOOM_DES_ETIQUETTES = 2.0
POINTS_DE_SUSPENSION = "…"

Position = tuple[float, float]
Positions = dict[int, Position]


@dataclass(frozen=True)
class View:
    zoom_index: int
    center: tuple[float, float]
    width: int
    height: int


@dataclass(frozen=True)
class Cell:
    char: str
    fg: str
    bg: str


VIDE = Cell(" ", "texte", "fond")


def initial_view(width: int, height: int) -> View:
    """La vue initiale : zoom 1, centrée."""
    return View(zoom_index=0, center=(0.5, 0.5), width=width, height=height)


def _echelle(view: View) -> float:
    """Pixels par unité du carré."""
    return 2 * view.height * ZOOMS[view.zoom_index]


def to_pixels(view: View, position: Position) -> Position:
    """La position en pixels dans la carte (x vers la droite, y vers le bas, deux par ligne)."""
    s = _echelle(view)
    return (
        (position[0] - view.center[0]) * s + view.width / 2,
        (position[1] - view.center[1]) * s + view.height,
    )


def _arrondi(valeur: float) -> int:
    return math.floor(valeur + 0.5)


def anchor(view: View, position: Position) -> tuple[int, int]:
    """La case d'ancrage : la colonne arrondie du x en pixels, la ligne ⌊y en pixels ÷ 2⌋."""
    x, y = to_pixels(view, position)
    return _arrondi(x), math.floor(y / 2)


def _pixel(view: View, position: Position) -> tuple[int, int]:
    x, y = to_pixels(view, position)
    return _arrondi(x), math.floor(y)


def _point_de_la_case(view: View, colonne: int, ligne: int) -> Position:
    """Le point du carré au centre de la case."""
    s = _echelle(view)
    return (
        (colonne - view.width / 2) / s + view.center[0],
        (2 * ligne + 1 - view.height) / s + view.center[1],
    )


def _dans_le_carre(centre: Position) -> Position:
    return min(max(centre[0], 0.0), 1.0), min(max(centre[1], 0.0), 1.0)


def zoom(view: View, step: int, anchor: tuple[int, int] | None) -> View:
    """Le niveau de zoom suivant (step = 1) ou précédent (step = −1) ; aux bornes, la vue ne change
    pas. Autour d'une case (la molette), le point sous cette case y reste ; sans case (le clavier),
    autour du centre de la vue."""
    rang = min(max(view.zoom_index + step, 0), len(ZOOMS) - 1)
    if rang == view.zoom_index:
        return view
    nouvelle = replace(view, zoom_index=rang)
    if anchor is None:
        return nouvelle
    colonne, ligne = anchor
    point = _point_de_la_case(view, colonne, ligne)
    s = _echelle(nouvelle)
    centre = (
        point[0] - (colonne - view.width / 2) / s,
        point[1] - (2 * ligne + 1 - view.height) / s,
    )
    return replace(nouvelle, center=_dans_le_carre(centre))


def pan(view: View, dx: int, dy: int) -> View:
    """Déplace la vue de dx colonnes et dy lignes ; le centre de la vue reste dans le carré."""
    s = _echelle(view)
    centre = (view.center[0] + dx / s, view.center[1] + 2 * dy / s)
    return replace(view, center=_dans_le_carre(centre))


def center_on(view: View, position: Position) -> View:
    """Recentre la vue sur une position (touche c : le vaisseau)."""
    return replace(view, center=_dans_le_carre(position))


def system_at(view: View, positions: Positions, x: int, y: int) -> int | None:
    """Le système dont la pastille (deux cases à partir de la case d'ancrage) couvre la case."""
    for ident in sorted(positions):
        colonne, ligne = anchor(view, positions[ident])
        if ligne == y and colonne <= x <= colonne + 1:
            return ident
    return None


def in_range(observation: Observation, navire: OwnShipView | None) -> frozenset[int]:
    """Les systèmes à portée : celui du vaisseau du joueur et ses voisins."""
    if navire is None:
        return frozenset()
    dist = distances(observation.systems, navire.system_id)
    return frozenset(s for s, d in dist.items() if d <= 1)


def ship_position(model: ClientModel, positions: Positions) -> Position | None:
    """La position du vaisseau du joueur : son système, ou, pendant un saut, le point du lien de
    `system_id` à `route[0]` à la fraction 1 − ticks_to_next_jump ÷ jump_ticks."""
    navire = model.vaisseau()
    obs = model.observation
    if navire is None or obs is None or navire.system_id not in positions:
        return None
    depart = positions[navire.system_id]
    if navire.activity is not Activity.EN_ROUTE or not navire.route:
        return depart
    arrivee = positions.get(navire.route[0])
    if arrivee is None:
        return depart
    fraction = 1 - navire.ticks_to_next_jump / obs.public_tunables.jump_ticks
    return (
        depart[0] + fraction * (arrivee[0] - depart[0]),
        depart[1] + fraction * (arrivee[1] - depart[1]),
    )


def _segment(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    """Les pixels d'un segment, de a à b (tracé de Bresenham)."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    erreur = dx + dy
    points = []
    while True:
        points.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return points
        double = 2 * erreur
        if double >= dy:
            erreur += dy
            x0 += sx
        if double <= dx:
            erreur += dx
            y0 += sy


class _Grille:
    """La grille en cours de dessin : les pixels des traits, puis les cases de texte."""

    def __init__(self, view: View) -> None:
        self.view = view
        self.pixels: dict[tuple[int, int], str] = {}
        self.cases: dict[tuple[int, int], Cell] = {}

    def trait(
        self, a: tuple[int, int], b: tuple[int, int], role: str, motif: int, plein: int
    ) -> None:
        """Les pixels d'un segment dont le rang modulo `motif` est inférieur à `plein`."""
        for rang, point in enumerate(_segment(a, b)):
            if rang % motif < plein:
                self.pixels[point] = role

    def ecrire(self, colonne: int, ligne: int, char: str, fg: str, bg: str = "fond") -> None:
        if 0 <= colonne < self.view.width and 0 <= ligne < self.view.height:
            self.cases[(colonne, ligne)] = Cell(char, fg, bg)

    def occupee(self, colonne: int, ligne: int) -> bool:
        hors = not (0 <= colonne < self.view.width and 0 <= ligne < self.view.height)
        return hors or (colonne, ligne) in self.cases

    def mot(self, colonne: int, ligne: int, mot: str, fg: str) -> None:
        for decalage, char in enumerate(mot):
            self.ecrire(colonne + decalage, ligne, char, fg)

    def rendre(self) -> tuple[tuple[Cell, ...], ...]:
        lignes = []
        for ligne in range(self.view.height):
            cases = []
            for colonne in range(self.view.width):
                case = self.cases.get((colonne, ligne))
                if case is None:
                    haut = self.pixels.get((colonne, 2 * ligne))
                    bas = self.pixels.get((colonne, 2 * ligne + 1))
                    case = (
                        VIDE
                        if haut is None and bas is None
                        else Cell("▀", haut or "fond", bas or "fond")
                    )
                cases.append(case)
            lignes.append(tuple(cases))
        return tuple(lignes)


def _etiquette(grille: _Grille, colonne: int, ligne: int, mots: list[tuple[str, str]]) -> None:
    """Une ligne d'étiquette : des mots entiers, séparés d'une espace ; un mot qui ne tient pas
    avant la première case occupée est remplacé par « … », et les suivants ne sont pas écrits."""
    curseur = colonne
    for mot, fg in mots:
        limite = curseur
        while not grille.occupee(limite, ligne):
            limite += 1
        if curseur + len(mot) <= limite:
            if curseur > colonne:
                grille.ecrire(curseur - 1, ligne, " ", "texte")  # l'espace qui sépare les mots
            grille.mot(curseur, ligne, mot, fg)
            curseur += len(mot) + 1
            continue
        if curseur < limite:
            grille.ecrire(curseur, ligne, POINTS_DE_SUSPENSION, "texte_attenue")
        return


def render(
    view: View, positions: Positions, model: ClientModel, hovered: int | None
) -> tuple[tuple[Cell, ...], ...]:
    """La grille de cases que `MapCanvas` peint, `view.height` lignes de `view.width` cases."""
    grille = _Grille(view)
    obs = model.observation
    if obs is None:
        return grille.rendre()
    navire = model.vaisseau()
    portee = in_range(obs, navire)
    places = {i: p for i, p in positions.items() if any(s.id == i for s in obs.systems)}
    # Liens : pleins entre deux systèmes à portée, un pixel sur deux sinon.
    for s in sorted(obs.systems, key=lambda s: s.id):
        for v in sorted(s.neighbors):
            if v > s.id and s.id in places and v in places:
                plein = s.id in portee and v in portee
                grille.trait(
                    _pixel(view, places[s.id]),
                    _pixel(view, places[v]),
                    "trait_fort" if plein else "trait_faible",
                    motif=1 if plein else 2,
                    plein=1,
                )
    # Route : trois pixels sur quatre.
    if navire is not None and navire.route:
        etapes = [navire.system_id, *navire.route]
        for a, b in zip(etapes, etapes[1:], strict=False):
            if a in places and b in places:
                grille.trait(_pixel(view, places[a]), _pixel(view, places[b]), "vaisseau", 4, 3)
    # Systèmes : la pastille, puis le gisement.
    stations = {st.system_id for st in obs.stations}
    for ident in sorted(places):
        colonne, ligne = anchor(view, places[ident])
        if ident == hovered:
            fg, bg = "fond", "accent"
        elif ident in stations:
            fg, bg = "fond", "station"
        elif ident in portee:
            fg, bg = "texte", "cadre_clair"
        else:
            fg, bg = "texte_attenue", "fond"
        for decalage, char in enumerate(f"{ident:>2}"[-2:]):
            grille.ecrire(colonne + decalage, ligne, char, fg, bg)
        gisements = sorted((d for d in obs.deposits if d.system_id == ident), key=lambda d: d.id)
        for rang, d in enumerate(gisements):
            lettre = chr(ord("a") + d.ore_id - 1)
            grille.ecrire(colonne + 2 + 2 * rang, ligne, "◆", f"ore_{lettre}")
            grille.ecrire(colonne + 3 + 2 * rang, ligne, lettre, f"ore_{lettre}")
    # Vaisseaux, sur la ligne au-dessus de la pastille.
    au_dessus: set[int] = set()
    position = ship_position(model, places)
    if navire is not None and position is not None:
        if navire.activity is Activity.EN_ROUTE and navire.route:
            x, y = to_pixels(view, position)
            grille.ecrire(_arrondi(x), math.floor(y / 2), "▲", "vaisseau")
        else:
            colonne, ligne = anchor(view, places[navire.system_id])
            grille.ecrire(colonne, ligne - 1, "▲", "vaisseau")
            au_dessus.add(navire.system_id)
    proches: dict[int, int] = {}
    for autre in obs.other_ships:
        proches[autre.system_id] = proches.get(autre.system_id, 0) + 1
    for ident in sorted(proches):
        if ident not in places:
            continue
        colonne, ligne = anchor(view, places[ident])
        debut = colonne + (1 if ident in au_dessus else 0)
        nombre = proches[ident]
        grille.mot(debut, ligne - 1, "▲" + (str(nombre) if nombre > 1 else ""), "texte_attenue")
    # Étiquettes, à partir du zoom 2.
    if ZOOMS[view.zoom_index] >= ZOOM_DES_ETIQUETTES:
        for ident in sorted(places):
            colonne, ligne = anchor(view, places[ident])
            gisements = sorted(
                (d for d in obs.deposits if d.system_id == ident), key=lambda d: d.id
            )
            debut = colonne + 2 + 2 * len(gisements) + 1
            lignes: list[list[tuple[str, str]]] = [[(systeme(ident), "texte")]]
            for st in sorted(obs.stations, key=lambda st: st.id):
                if st.system_id == ident:
                    mots = [(f"S{st.id}", "station")]
                    mots += [
                        (f"{chr(ord('a') + rang)}{prix}", f"ore_{chr(ord('a') + rang)}")
                        for rang, prix in enumerate(st.ore_prices)
                    ]
                    lignes.append(mots)
            for d in gisements:
                lignes.append([("?" if d.stock is None else str(d.stock), "texte_attenue")])
            for rang, mots in enumerate(lignes[:3]):
                _etiquette(grille, debut, ligne + rang, mots)
    return grille.rendre()
