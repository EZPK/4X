"""La vue de la carte : projection, zoom, déplacement, système sous le pointeur, grille de cases.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter (vue de la carte) et
point 13 (interface). Fonctions pures, testées sans Textual ; `MapCanvas` (frames.py) ne fait que
peindre la grille que rend `render`.

Le rendu suit la maquette validée : chaque système est un petit cadre (┌──┐ │12│ └──┘), plein à
portée, en tirets hors de portée ; l'étiquette de sa station (S1) en violet à droite du cadre ; son
gisement et son stock dessous (◆20000, ou ◆? hors de portée). Les liens sont des traits fins
d'un seul tenant (─ │ ╱ ╲), atténués et en tirets (┄ ┆) hors de portée ; la route du vaisseau est
en jaune. Au zoom 1,
le carré [0, 1] × [0, 1] couvre toute la carte ; la position d'un système est le coin en haut à
gauche de son cadre. Ordre de dessin : liens, route, systèmes, étiquettes, vaisseau en route.
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


def _centre_du_cadre(view: View, position: Position) -> Position:
    colonne, ligne = to_cells(view, position)
    return colonne + LARGEUR_CADRE / 2 - 0.5, ligne + HAUTEUR_CADRE / 2 - 0.5


def _trace(a: Position, b: Position) -> list[tuple[int, int]]:
    """Les cases d'un trait de a à b, dans l'ordre, sans doublon."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    pas = max(math.ceil(max(abs(dx), abs(dy))), 1)
    cases: list[tuple[int, int]] = []
    for i in range(pas + 1):
        case = (math.floor(a[0] + dx * i / pas + 0.5), math.floor(a[1] + dy * i / pas + 0.5))
        if not cases or cases[-1] != case:
            cases.append(case)
    return cases


def trait(dx: float, dy: float, gras: bool = False) -> str:
    """Le caractère d'un trait selon sa pente à l'écran (une case est deux fois plus haute que
    large) : ─ │ ╲ ╱, ou ━ ┃ pour un trait gras."""
    pente = math.inf if dx == 0 else 2 * dy / dx
    if abs(pente) < 0.5:
        return "━" if gras else "─"
    if abs(pente) > 2:
        return "┃" if gras else "│"
    return "╲" if pente > 0 else "╱"


TIRETS = {"─": "┄", "│": "┆"}
GRAS = {"─": "━", "│": "┃"}


def caractere_local(
    precedente: tuple[int, int] | None,
    case: tuple[int, int],
    pente: tuple[float, float],
    plein: bool = True,
    gras: bool = False,
) -> str:
    """Le caractère d'une case d'un lien. Un lien qui paraît diagonal à l'écran est tracé en ╲ ou
    ╱ ; un lien plutôt horizontal (ou vertical) en ─ (ou │), avec ╲ ou ╱ sur chaque case où il
    change de ligne (ou de colonne), d'après son pas depuis la case précédente. Hors de portée, les
    traits droits passent en tirets (┄ ┆) ; pour la route, en gras (━ ┃)."""
    char = trait(*pente)
    if char in "─│" and precedente is not None:
        dx, dy = case[0] - precedente[0], case[1] - precedente[1]
        if dx != 0 and dy != 0:
            char = "╲" if dx * dy > 0 else "╱"
    if gras:
        return GRAS.get(char, char)
    if not plein:
        return TIRETS.get(char, char)
    return char


class _Grille:
    """La grille en cours de dessin : les traits, puis les cases de texte (« occupées »)."""

    def __init__(self, view: View) -> None:
        self.view = view
        self.traits: dict[tuple[int, int], Cell] = {}
        self.cases: dict[tuple[int, int], Cell] = {}

    def dedans(self, colonne: int, ligne: int) -> bool:
        return 0 <= colonne < self.view.width and 0 <= ligne < self.view.height

    def tracer(self, a: Position, b: Position, plein: bool, role: str, gras: bool = False) -> None:
        """Un lien d'un seul tenant : chaque case prend le caractère de son pas local (─ │ ╲ ╱),
        en tirets (┄ ┆) pour un lien hors de portée, en gras (━ ┃) pour la route."""
        cases = _trace(a, b)
        pente = (b[0] - a[0], b[1] - a[1])
        for rang, case in enumerate(cases):
            if self.dedans(*case):
                precedente = cases[rang - 1] if rang > 0 else None
                char = caractere_local(precedente, case, pente, plein, gras)
                self.traits[case] = Cell(char, role, "fond")

    def ecrire(self, colonne: int, ligne: int, char: str, fg: str, bg: str = "fond") -> None:
        if self.dedans(colonne, ligne):
            self.cases[(colonne, ligne)] = Cell(char, fg, bg)

    def occupee(self, colonne: int, ligne: int) -> bool:
        return not self.dedans(colonne, ligne) or (colonne, ligne) in self.cases

    def mot(self, colonne: int, ligne: int, mot: str, fg: str, bg: str = "fond") -> None:
        for decalage, char in enumerate(mot):
            self.ecrire(colonne + decalage, ligne, char, fg, bg)

    def rendre(self) -> tuple[tuple[Cell, ...], ...]:
        return tuple(
            tuple(
                self.cases.get((colonne, ligne)) or self.traits.get((colonne, ligne)) or VIDE
                for colonne in range(self.view.width)
            )
            for ligne in range(self.view.height)
        )


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
                grille.ecrire(curseur - 1, ligne, " ", "texte")
            grille.mot(curseur, ligne, mot, fg)
            curseur += len(mot) + 1
            continue
        if curseur < limite:
            grille.ecrire(curseur, ligne, POINTS_DE_SUSPENSION, "texte_attenue")
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
    # Liens : traits fins entre deux systèmes à portée, points sinon.
    for s in sorted(obs.systems, key=lambda s: s.id):
        for v in sorted(s.neighbors):
            if v > s.id and s.id in centres and v in centres:
                plein = s.id in portee and v in portee
                role = "trait_fort" if plein else "trait_faible"
                grille.tracer(centres[s.id], centres[v], plein, role)
    # Route du vaisseau, en jaune.
    if navire is not None and navire.route:
        etapes = [navire.system_id, *navire.route]
        for a, b in zip(etapes, etapes[1:], strict=False):
            if a in centres and b in centres:
                grille.tracer(centres[a], centres[b], True, "vaisseau", gras=True)
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
        colonne_f, ligne_f = _centre_du_cadre(view, position)
        ici = (math.floor(colonne_f + 0.5), math.floor(ligne_f + 0.5))
        cases = [ici]
        if navire.system_id in centres and navire.route[0] in centres:
            trace = _trace(centres[navire.system_id], centres[navire.route[0]])
            rang = min(
                range(len(trace)),
                key=lambda k: (trace[k][0] - ici[0]) ** 2 + (trace[k][1] - ici[1]) ** 2,
            )
            cases = trace[rang:] + trace[:rang][::-1]
        libre = next((c for c in cases if not grille.occupee(*c)), ici)
        grille.ecrire(libre[0], libre[1], "▲", "vaisseau")
    return grille.rendre()
