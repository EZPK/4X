"""La vue de la carte : projection, zoom, déplacement, système sous le pointeur, grille de cases.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter (vue de la carte) et
point 13 (interface). Fonctions pures, testées sans Textual ; `MapCanvas` (frames.py) ne fait que
peindre la grille que rend `render`.

Le rendu suit la maquette validée : chaque système est un petit cadre (┌──┐ │12│ └──┘), plein à
portée, en tirets hors de portée ; l'étiquette de sa station (S1) en violet à droite du cadre ; son
gisement et son stock dessous (◆20000, ou ◆? hors de portée). Les liens sont tracés point par
point en caractères Braille (2 × 4 points par case), ce qui permet un trait fin à n'importe quel
angle : plein à portée, pointillé et atténué hors de portée ; la route du vaisseau est en jaune.
Au zoom 1, le carré [0, 1] × [0, 1] couvre toute la carte ; la position d'un système est le coin
en haut à gauche de son cadre. Ordre de dessin : liens, route, systèmes, étiquettes, vaisseau en
route.
"""

import math
from dataclasses import dataclass, replace

from fourx.clients.model import ClientModel
from fourx.clients.texts import minerai, systeme
from fourx.policies.geometry import distances
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OwnShipView

ZOOMS = (1.0, 1.5, 2.0, 3.0, 4.0)
ZOOM_DES_ETIQUETTES = 2.0
POINTS_DE_SUSPENSION = "…"
LARGEUR_CADRE = 4
HAUTEUR_CADRE = 3

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


def to_cells(view: View, position: Position) -> Position:
    """La position en cases de la carte (colonne, ligne), en flottants ; au zoom 1, le carré
    couvre toute la carte."""
    z = ZOOMS[view.zoom_index]
    return (
        (position[0] - view.center[0]) * view.width * z + view.width / 2,
        (position[1] - view.center[1]) * view.height * z + view.height / 2,
    )


def anchor(view: View, position: Position) -> tuple[int, int]:
    """La case d'ancrage : le coin en haut à gauche du cadre du système."""
    colonne, ligne = to_cells(view, position)
    return math.floor(colonne), math.floor(ligne)


def _point_de_la_case(view: View, colonne: int, ligne: int) -> Position:
    """Le point du carré au centre de la case."""
    z = ZOOMS[view.zoom_index]
    return (
        (colonne + 0.5 - view.width / 2) / (view.width * z) + view.center[0],
        (ligne + 0.5 - view.height / 2) / (view.height * z) + view.center[1],
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
    z = ZOOMS[rang]
    centre = (
        point[0] - (colonne + 0.5 - view.width / 2) / (view.width * z),
        point[1] - (ligne + 0.5 - view.height / 2) / (view.height * z),
    )
    return replace(nouvelle, center=_dans_le_carre(centre))


def pan(view: View, dx: int, dy: int) -> View:
    """Déplace la vue de dx colonnes et dy lignes ; le centre de la vue reste dans le carré."""
    z = ZOOMS[view.zoom_index]
    centre = (view.center[0] + dx / (view.width * z), view.center[1] + dy / (view.height * z))
    return replace(view, center=_dans_le_carre(centre))


def center_on(view: View, position: Position) -> View:
    """Recentre la vue sur une position (touche c : le vaisseau)."""
    return replace(view, center=_dans_le_carre(position))


def system_at(view: View, positions: Positions, x: int, y: int) -> int | None:
    """Le système dont le cadre couvre la case."""
    for ident in sorted(positions):
        colonne, ligne = anchor(view, positions[ident])
        if colonne <= x < colonne + LARGEUR_CADRE and ligne <= y < ligne + HAUTEUR_CADRE:
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


# Les points d'une case Braille : (colonne du point, ligne du point) → bit du caractère U+2800.
BITS_BRAILLE = {
    (0, 0): 0x01,
    (0, 1): 0x02,
    (0, 2): 0x04,
    (1, 0): 0x08,
    (1, 1): 0x10,
    (1, 2): 0x20,
    (0, 3): 0x40,
    (1, 3): 0x80,
}
POINTS_PAR_CASE = (2, 4)
PRIORITE = {"trait_faible": 1, "trait_fort": 2, "vaisseau": 3}
POINTILLE = 3  # hors de portée, un point sur trois


def _centre_du_cadre(view: View, position: Position) -> Position:
    """Le centre du cadre d'un système, en points Braille."""
    colonne, ligne = anchor(view, position)
    return (
        (colonne + LARGEUR_CADRE / 2) * POINTS_PAR_CASE[0],
        (ligne + HAUTEUR_CADRE / 2) * POINTS_PAR_CASE[1],
    )


def _points(a: Position, b: Position) -> list[tuple[int, int]]:
    """Les points Braille d'un trait de a à b, dans l'ordre (tracé de Bresenham). La boucle est
    bornée par |dx| + |dy| + 1 points, le plus long tracé possible : aucune erreur ne peut la
    faire tourner sans fin."""
    x0, y0 = math.floor(a[0]), math.floor(a[1])
    x1, y1 = math.floor(b[0]), math.floor(b[1])
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    erreur = dx + dy
    points = []
    for _ in range(dx - dy + 1):
        points.append((x0, y0))
        if (x0, y0) == (x1, y1):
            break
        double = 2 * erreur
        if double >= dy:
            erreur += dy
            x0 += sx
        if double <= dx:
            erreur += dx
            y0 += sy
    return points


def case_du_point(point: tuple[int, int]) -> tuple[int, int]:
    return point[0] // POINTS_PAR_CASE[0], point[1] // POINTS_PAR_CASE[1]


def _cases_du_trait(a: Position, b: Position) -> list[tuple[int, int]]:
    """Les cases que traverse un trait, dans l'ordre, sans doublon."""
    cases: list[tuple[int, int]] = []
    for point in _points(a, b):
        case = case_du_point(point)
        if not cases or cases[-1] != case:
            cases.append(case)
    return cases


class _Grille:
    """La grille en cours de dessin : les traits, puis les cases de texte (« occupées »)."""

    def __init__(self, view: View) -> None:
        self.view = view
        self.braille: dict[tuple[int, int], tuple[int, str]] = {}
        self.cases: dict[tuple[int, int], Cell] = {}

    def dedans(self, colonne: int, ligne: int) -> bool:
        return 0 <= colonne < self.view.width and 0 <= ligne < self.view.height

    def tracer(self, a: Position, b: Position, plein: bool, role: str, depuis: float = 0.0) -> None:
        """Un lien, point par point : tous les points s'il est plein, un sur trois sinon ; à partir
        de la fraction `depuis` du trait seulement (0 : tout le trait). Une case traversée par
        plusieurs liens prend la couleur du plus important (route, puis lien à portée, puis lien
        lointain)."""
        points = _points(a, b)
        premier = round(min(max(depuis, 0.0), 1.0) * (len(points) - 1))
        for rang, point in enumerate(points):
            if rang < premier or (not plein and rang % POINTILLE):
                continue
            case = case_du_point(point)
            if not self.dedans(*case):
                continue
            bit = BITS_BRAILLE[(point[0] % POINTS_PAR_CASE[0], point[1] % POINTS_PAR_CASE[1])]
            bits, ancien = self.braille.get(case, (0, role))
            garde = ancien if PRIORITE[ancien] > PRIORITE[role] else role
            self.braille[case] = (bits | bit, garde)

    def ecrire(self, colonne: int, ligne: int, char: str, fg: str, bg: str = "fond") -> None:
        if self.dedans(colonne, ligne):
            self.cases[(colonne, ligne)] = Cell(char, fg, bg)

    def occupee(self, colonne: int, ligne: int) -> bool:
        return not self.dedans(colonne, ligne) or (colonne, ligne) in self.cases

    def mot(self, colonne: int, ligne: int, mot: str, fg: str, bg: str = "fond") -> None:
        for decalage, char in enumerate(mot):
            self.ecrire(colonne + decalage, ligne, char, fg, bg)

    def _braille(self, colonne: int, ligne: int) -> Cell:
        if (colonne, ligne) not in self.braille:
            return VIDE
        bits, role = self.braille[(colonne, ligne)]
        return Cell(chr(0x2800 + bits), role, "fond")

    def rendre(self) -> tuple[tuple[Cell, ...], ...]:
        return tuple(
            tuple(
                self.cases.get((colonne, ligne)) or self._braille(colonne, ligne)
                for colonne in range(self.view.width)
            )
            for ligne in range(self.view.height)
        )


def _etiquette(grille: _Grille, colonne: int, ligne: int, mots: list[tuple[str, str]]) -> None:
    """Une ligne d'étiquette : des mots entiers, séparés d'une espace qui doit elle aussi tomber sur
    une case libre ; un mot qui ne tient pas avant la première case occupée est remplacé par « … »
    (s'il reste une case libre), et les suivants ne sont pas écrits."""
    curseur = colonne
    for mot, fg in mots:
        debut = curseur - 1 if curseur > colonne else curseur  # l'espace qui le sépare compris
        # La première case occupée ; hors de la carte, toute case l'est.
        cases = range(debut, grille.view.width + 1)
        limite = next((c for c in cases if grille.occupee(c, ligne)), debut)
        if curseur + len(mot) <= limite:
            if debut < curseur:
                grille.ecrire(debut, ligne, " ", "texte")
            grille.mot(curseur, ligne, mot, fg)
            curseur += len(mot) + 1
            continue
        place = curseur if curseur < limite else debut
        if place < limite:
            grille.ecrire(place, ligne, POINTS_DE_SUSPENSION, "texte_attenue")
        return


def _cadre(grille: _Grille, colonne: int, ligne: int, ident: int, style: str) -> None:
    """Le cadre d'un système : plein (« portee »), en tirets (« loin ») ou survolé."""
    loin = style == "loin"
    bord = {"survol": "accent", "portee": "texte", "loin": "texte_attenue"}[style]
    horizontal, vertical = ("┄", "┆") if loin else ("─", "│")
    grille.mot(colonne, ligne, "┌" + horizontal * 2 + "┐", bord)
    grille.ecrire(colonne, ligne + 1, vertical, bord)
    grille.ecrire(colonne + 3, ligne + 1, vertical, bord)
    grille.mot(colonne, ligne + 2, "└" + horizontal * 2 + "┘", bord)
    fg, bg = {
        "survol": ("fond", "accent"),
        "portee": ("texte", "cadre_clair"),
        "loin": ("texte_attenue", "fond"),
    }[style]
    grille.mot(colonne + 1, ligne + 1, f"{ident:>2}"[-2:], fg, bg)


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
    centres = {i: _centre_du_cadre(view, p) for i, p in places.items()}
    # Liens : pleins entre deux systèmes à portée, pointillés sinon.
    for s in sorted(obs.systems, key=lambda s: s.id):
        for v in sorted(s.neighbors):
            if v > s.id and s.id in centres and v in centres:
                plein = s.id in portee and v in portee
                role = "trait_fort" if plein else "trait_faible"
                grille.tracer(centres[s.id], centres[v], plein, role)
    # Route du vaisseau, en jaune : seulement ce qui reste à parcourir. Elle suit exactement les
    # points de ses liens ; pendant un saut, les points du lien en cours déjà parcourus (avant la
    # fraction 1 − ticks_to_next_jump ÷ jump_ticks) gardent le tracé du lien.
    if navire is not None and navire.route:
        etapes = [navire.system_id, *navire.route]
        fait = 0.0
        if navire.activity is Activity.EN_ROUTE:
            fait = 1 - navire.ticks_to_next_jump / obs.public_tunables.jump_ticks
        for rang, (a, b) in enumerate(zip(etapes, etapes[1:], strict=False)):
            if a in centres and b in centres:
                depuis = fait if rang == 0 else 0.0
                grille.tracer(centres[a], centres[b], True, "vaisseau", depuis)
    # Systèmes : cadre, station, gisement et stock, vaisseaux.
    proches: dict[int, int] = {}
    for autre in obs.other_ships:
        proches[autre.system_id] = proches.get(autre.system_id, 0) + 1
    en_route = navire is not None and navire.activity is Activity.EN_ROUTE and bool(navire.route)
    zoome = ZOOMS[view.zoom_index] >= ZOOM_DES_ETIQUETTES
    for ident in sorted(places):
        colonne, ligne = anchor(view, places[ident])
        style = "survol" if ident == hovered else ("portee" if ident in portee else "loin")
        _cadre(grille, colonne, ligne, ident, style)
        for st in sorted(obs.stations, key=lambda st: st.id):
            if st.system_id == ident:
                grille.mot(colonne + LARGEUR_CADRE, ligne, f"S{st.id}", "fond", "station")
        if navire is not None and not en_route and navire.system_id == ident:
            grille.ecrire(colonne + 1, ligne, "▲", "vaisseau")
        if proches.get(ident):
            nombre = proches[ident]
            autres = "▲" + (str(nombre) if nombre > 1 else "")
            grille.mot(colonne + 1, ligne + 2, autres, "texte_attenue")
        gisements = sorted((d for d in obs.deposits if d.system_id == ident), key=lambda d: d.id)
        for d in gisements:
            lettre = chr(ord("a") + d.ore_id - 1)
            grille.ecrire(colonne, ligne + HAUTEUR_CADRE, "◆", f"ore_{lettre}")
            debut = colonne + 1
            if zoome:
                nom = minerai(d.ore_id) + " "
                grille.mot(debut, ligne + HAUTEUR_CADRE, nom, f"ore_{lettre}")
                debut += len(nom)
            role = "texte_attenue" if d.stock is None else "texte"
            stock = "?" if d.stock is None else str(d.stock)
            grille.mot(debut, ligne + HAUTEUR_CADRE, stock, role)
    # Étiquettes, à partir du zoom 2 : le libellé, et les prix de la station.
    if zoome:
        for ident in sorted(places):
            colonne, ligne = anchor(view, places[ident])
            _etiquette(grille, colonne + LARGEUR_CADRE + 1, ligne + 1, [(systeme(ident), "texte")])
            for st in sorted(obs.stations, key=lambda st: st.id):
                if st.system_id == ident:
                    mots = [
                        (f"{chr(ord('a') + rang)}{prix}", f"ore_{chr(ord('a') + rang)}")
                        for rang, prix in enumerate(st.ore_prices)
                    ]
                    _etiquette(grille, colonne + LARGEUR_CADRE + 3, ligne, mots)
    # Le vaisseau en route, sur son lien : à la case de sa fraction, ou à la première case libre
    # qui la suit sur le trait (il ne cache ni un cadre ni une étiquette).
    position = ship_position(model, places)
    if en_route and navire is not None and position is not None:
        x, y = _centre_du_cadre(view, position)
        ici = case_du_point((math.floor(x), math.floor(y)))
        cases = [ici]
        if navire.system_id in centres and navire.route[0] in centres:
            trace = _cases_du_trait(centres[navire.system_id], centres[navire.route[0]])
            rang = min(
                range(len(trace)),
                key=lambda k: (trace[k][0] - ici[0]) ** 2 + (trace[k][1] - ici[1]) ** 2,
            )
            cases = trace[rang:] + trace[:rang][::-1]
        libre = next((c for c in cases if not grille.occupee(*c)), ici)
        grille.ecrire(libre[0], libre[1], "▲", "vaisseau")
    return grille.rendre()
