"""Les cadres de l'écran rétro : un widget Textual par cadre.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 7 bis et 7 ter (cadres,
palette, aide). Chaque cadre lit `ClientModel` et ne connaît pas les autres : on peut en ajouter,
en retirer ou les réarranger sans toucher au reste. Le texte de chaque cadre vient d'une fonction
de ce module, en couleurs de `PALETTE` ; le widget ne fait que l'afficher. Aucun cadre ne prend le
focus : toutes les touches vont à `FourxApp`. La carte (`MapCanvas`) peint la grille de
`map_view.render`, et prévient `FourxApp` d'un clic ou d'un survol par un message.
"""

import time

from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget
from textual.widgets import Static

from fourx.clients.force_layout import force_layout
from fourx.clients.guide import next_step
from fourx.clients.map_view import (
    ZOOMS,
    Cell,
    View,
    in_range,
    initial_view,
    pan,
    render,
    system_at,
    zoom,
)
from fourx.clients.model import ClientModel, HistoryKind, decrire
from fourx.clients.palette import PALETTE
from fourx.clients.texts import duration_text, help_pages, minerai, station, systeme
from fourx.policies.geometry import distances
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OwnShipView

ATTENTE = "En attente du premier tick…"
LARGEUR_BARRE = 20
NOMS_DES_TOUCHES = {"enter": "Entrée", "escape": "Échap", "space": "Espace"}
COULEURS_DE_L_HISTORIQUE = {
    HistoryKind.ORDER: "accent",
    HistoryKind.SALE: "succes",
    HistoryKind.ALERT: "vaisseau",
    HistoryKind.REFUSAL: "alerte",
}


def couleur(role: str) -> str:
    return PALETTE[role]


def texte_entete_carte(model: ClientModel, vue: View) -> Text:
    """L'en-tête de la carte : le nombre de systèmes, combien sont à portée, le zoom, et les
    gestes."""
    obs = model.observation
    texte = Text(" ")
    if obs is not None:
        portee = len(in_range(obs, model.vaisseau()))
        texte.append(f"{len(obs.systems)} systèmes", style=couleur("texte"))
        texte.append(f" · {portee} à portée", style=couleur("texte"))
    zoom_affiche = f"{ZOOMS[vue.zoom_index]:g}".replace(".", ",")
    texte.append(f" · zoom ×{zoom_affiche}", style=couleur("accent"))
    texte.append("   molette, glisser, clic : y aller", style=couleur("texte_attenue"))
    return texte


def texte_legende_carte() -> Text:
    """La légende des symboles de la carte."""
    texte = Text(" ")
    morceaux = [
        ("S1", f"{couleur('fond')} on {couleur('station')}", " station  "),
        ("◆", couleur("ore_a"), " ore_a  "),
        ("◆", couleur("ore_b"), " ore_b  "),
        ("▲", couleur("vaisseau"), " toi  "),
        ("⠒⠒⠒", couleur("trait_fort"), " à portée  "),
        ("⠂⠐⠂", couleur("trait_faible"), " loin, stock ?"),
    ]
    for symbole, style, libelle in morceaux:
        texte.append(symbole, style=style)
        texte.append(libelle, style=couleur("texte_attenue"))
    return texte


def texte_bulle(model: ClientModel, ident: int) -> str:
    """La bulle d'un système survolé : son libellé, ses sites, le stock (ou « ? »), et la distance
    en sauts, en ticks et en ≈ minutes depuis le vaisseau (pendant un saut, depuis `route[0]`,
    plus `ticks_to_next_jump`) ; « déjà ici » sur le système du vaisseau."""
    obs = model.observation
    if obs is None:
        return ATTENTE
    lignes = [systeme(ident)]
    sites = [
        f"{station(st.id)} (a {st.ore_prices[0]}, b {st.ore_prices[1]})"
        for st in obs.stations
        if st.system_id == ident
    ]
    sites += [
        f"gisement de {minerai(d.ore_id)}, stock {'?' if d.stock is None else d.stock}"
        for d in obs.deposits
        if d.system_id == ident
    ]
    lignes += sites or ["aucun site"]
    navire = model.vaisseau()
    if navire is None:
        return "\n".join(lignes)
    saut = obs.public_tunables.jump_ticks
    en_route = navire.activity is Activity.EN_ROUTE and bool(navire.route)
    if en_route:
        depart, deja = navire.route[0], navire.ticks_to_next_jump
    else:
        depart, deja = navire.system_id, 0
    if not en_route and ident == navire.system_id:
        lignes.append("déjà ici")
        return "\n".join(lignes)
    n = distances(obs.systems, depart).get(ident)
    if n is None:
        lignes.append("inaccessible")
    else:
        texte = f"{n} saut" + ("" if n == 1 else "s")
        lignes.append(f"{texte}, {duration_text(deja + n * saut)}")
    return "\n".join(lignes)


def texte_etape(model: ClientModel) -> Text:
    """La prochaine étape : son titre (en couleur `vaisseau` pour une alerte), son détail et ses
    touches, par leur nom français."""
    etape = next_step(model)
    alerte = etape.keys == ("enter",) and bool(model.alerts)
    texte = Text(etape.title, style=f"bold {couleur('vaisseau' if alerte else 'texte')}")
    if etape.detail:
        texte.append("\n" + etape.detail, style=couleur("texte_attenue"))
    if etape.keys:
        noms = " ".join(NOMS_DES_TOUCHES.get(k, k) for k in etape.keys)
        texte.append("\nTouche : ", style=couleur("texte_attenue"))
        texte.append(noms, style=f"bold {couleur('accent')}")
    return texte


def barre(fait: int, total: int) -> str:
    """Une barre de progression de 20 cases : █ fait, ░ à faire."""
    pleines = 0 if total <= 0 else min(fait * LARGEUR_BARRE // total, LARGEUR_BARRE)
    return "█" * pleines + "░" * (LARGEUR_BARRE - pleines)


def _progres(model: ClientModel, navire: OwnShipView) -> tuple[str, int, int]:
    """Le libellé, le fait et le total de la barre du saut ou du minage en cours."""
    obs = model.observation
    assert obs is not None
    reglages = obs.public_tunables
    if navire.activity is Activity.EN_ROUTE:
        return "saut", reglages.jump_ticks - navire.ticks_to_next_jump, reglages.jump_ticks
    if navire.activity is Activity.MINING:
        restant = navire.capacity - sum(navire.cargo)
        for d in obs.deposits:
            if (
                d.system_id == navire.system_id
                and d.ore_id == navire.mining_ore_id
                and d.stock is not None
            ):
                restant = min(restant, d.stock)
        return "minage", navire.mined_since_start, navire.mined_since_start + restant
    return "activité", 0, 1


def texte_vaisseau(model: ClientModel) -> Text:
    """État, route, durée restante, cargaison, ordre envoyé, puis les deux barres de progression :
    le saut ou le minage en cours, et le remplissage de la cargaison."""
    navire = model.vaisseau()
    if model.observation is None or navire is None:
        return Text(ATTENTE)
    restants = model.remaining_ticks()
    if navire.activity is Activity.EN_ROUTE:
        etat = f"en route vers {systeme(navire.route[-1])}"
        suite = "" if restants is None else f"arrivée dans {duration_text(restants)}"
    elif navire.activity is Activity.MINING:
        nom = "" if navire.mining_ore_id is None else f" de {minerai(navire.mining_ore_id)}"
        etat = f"en minage{nom}"
        suite = "" if restants is None else f"fin dans {duration_text(restants)}"
    else:
        etat, suite = "à l'arrêt", "aucun trajet ni minage en cours"
    texte = Text(systeme(navire.system_id), style=f"bold {couleur('texte')}")
    texte.append(f"  {etat}\n", style=couleur("texte"))
    texte.append(suite + "\n", style=couleur("texte_attenue"))
    texte.append("cargaison : ", style=couleur("texte_attenue"))
    for rang, q in enumerate(navire.cargo):
        if rang:
            texte.append("  ")
        texte.append(f"{minerai(rang + 1)} {q}", style=couleur(f"ore_{chr(ord('a') + rang)}"))
    envoyes = [decrire(c) for _, c in model.pending]
    texte.append("\nordre envoyé : " + (" ; ".join(envoyes) if envoyes else "aucun") + "\n")
    libelle, fait, total = _progres(model, navire)
    texte.append(f"{libelle:<10}", style=couleur("texte_attenue"))
    _ajouter_barre(texte, fait, total)
    texte.append("\ncargaison ", style=couleur("texte_attenue"))
    _ajouter_barre(texte, sum(navire.cargo), navire.capacity)
    texte.append(f" {sum(navire.cargo)}/{navire.capacity}", style=couleur("texte"))
    return texte


def _ajouter_barre(texte: Text, fait: int, total: int) -> None:
    trace = barre(fait, total)
    pleines = trace.count("█")
    texte.append(trace[:pleines], style=couleur("accent"))
    texte.append(trace[pleines:], style=couleur("trait_faible"))


def texte_stations(model: ClientModel) -> Text:
    """Une ligne par station, le meilleur prix de chaque minerai marqué ★ (toutes les stations à
    égalité le sont) ; puis, par minerai, les systèmes de ses gisements et leur stock, « ? » hors
    de portée."""
    obs = model.observation
    if obs is None:
        return Text(ATTENTE)
    meilleurs = [max((s.ore_prices[rang] for s in obs.stations), default=0) for rang in range(2)]
    texte = Text()
    for s in obs.stations:
        texte.append(f"{station(s.id)} ", style=f"bold {couleur('station')}")
        texte.append(systeme(s.system_id), style=couleur("texte"))
        for rang, prix in enumerate(s.ore_prices):
            lettre = chr(ord("a") + rang)
            texte.append(f"  {lettre} {prix}", style=couleur(f"ore_{lettre}"))
            if prix == meilleurs[rang]:
                texte.append("★", style=couleur("succes"))
        texte.append("\n")
    for rang in range(2):
        lieux = [
            f"{systeme(d.system_id)} ({'?' if d.stock is None else d.stock})"
            for d in obs.deposits
            if d.ore_id == rang + 1
        ]
        texte.append(f"{minerai(rang + 1)} : ", style=couleur(f"ore_{chr(ord('a') + rang)}"))
        texte.append(", ".join(lieux) or "aucun gisement", style=couleur("texte"))
        if rang == 0:
            texte.append("\n")
    return texte


def texte_historique(model: ClientModel, nombre: int = 4) -> Text:
    """Les dernières entrées de l'historique, la plus récente en bas, chacune « t[tick] [texte] »,
    l'étiquette colorée selon son type."""
    texte = Text()
    for rang, entree in enumerate(model.history[-nombre:]):
        if rang:
            texte.append("\n")
        texte.append(
            f"t{entree.tick}", style=f"bold {couleur(COULEURS_DE_L_HISTORIQUE[entree.kind])}"
        )
        texte.append(f" {entree.text}", style=couleur("texte"))
    return texte


def destinations(observation: Observation, depart: int) -> list[tuple[int, str]]:
    """Chaque système, avec ses sites ; le stock des gisements proches, « ? » pour les autres."""
    lignes = []
    dist = distances(observation.systems, depart)
    for s in observation.systems:
        sites = [station(st.id) for st in observation.stations if st.system_id == s.id]
        sites += [
            f"{minerai(d.ore_id)} ({'?' if d.stock is None else d.stock})"
            for d in observation.deposits
            if d.system_id == s.id
        ]
        sauts = dist.get(s.id)
        loin = "?" if sauts is None else f"{sauts} saut" + ("" if sauts == 1 else "s")
        lignes.append((s.id, f"[{s.id}] {systeme(s.id)}  {loin}  {' '.join(sites)}".rstrip()))
    return lignes


def texte_destinations(model: ClientModel, choix: int, hauteur: int) -> str:
    """Pour la ligne choisie, sauts, ticks et ≈ minutes ; puis la liste des destinations, dont
    une fenêtre de `hauteur` − 1 lignes suit la ligne choisie (toute la liste si la hauteur
    n'est pas encore connue)."""
    obs = model.observation
    navire = model.vaisseau()
    if obs is None or navire is None:
        return ATTENTE
    lignes = destinations(obs, navire.system_id)
    cible = lignes[choix][0]
    sauts = distances(obs.systems, navire.system_id).get(cible)
    if sauts is None:
        tete = f"{systeme(cible)} : inaccessible"
    else:
        cout = duration_text(sauts * obs.public_tunables.jump_ticks)
        tete = f"{systeme(cible)} : {sauts} saut{'' if sauts == 1 else 's'}, {cout}"
    place = max(hauteur - 1, 1) if hauteur > 0 else len(lignes)
    premier = min(max(choix - place // 2, 0), max(len(lignes) - place, 0))
    fenetre = [
        ("> " if i == choix else "  ") + ligne
        for i, (_, ligne) in enumerate(lignes)
        if premier <= i < premier + place
    ]
    return "\n".join([tete, *fenetre])


def texte_barre(model: ClientModel, vitesse: str | None, aide: str) -> Text:
    """Ligne 1 : tick, durée de jeu estimée, solde ; en mode développement, la vitesse demandée.
    Ligne 2 : la ligne d'aide d'une touche sans effet, ou l'invite de la saisie en cours."""
    obs = model.observation
    texte = Text(" ")
    if obs is None:
        texte.append("Tick —", style=f"bold {couleur('texte')}")
        texte.append(" │ Solde —", style=couleur("texte"))
    else:
        estimation = "(" + duration_text(obs.tick).split(" (", 1)[1]
        texte.append(f"Tick {obs.tick}", style=f"bold {couleur('texte')}")
        texte.append(f" {estimation}", style=couleur("texte_attenue"))
        texte.append(" │ ", style=couleur("texte_attenue"))
        texte.append(f"Solde {obs.wallet_balance}", style=f"bold {couleur('succes')}")
    if vitesse is not None:
        texte.append(" │ ", style=couleur("texte_attenue"))
        texte.append(f"dev {vitesse}", style=couleur("vaisseau"))
    texte.append("\n " + aide, style=couleur("accent"))
    return texte


def texte_touches(saisie: str | None, aide_ouverte: bool) -> str:
    """Les touches utiles dans la saisie en cours."""
    if aide_ouverte:
        return " ↑↓ défiler · Entrée, Échap ou h fermer"
    if saisie == "destination":
        return " ↑↓ choisir · Entrée confirmer · Échap annuler"
    if saisie in ("miner", "quitter"):
        return " Entrée confirmer · Échap annuler"
    if saisie == "minerai":
        return " a ou b : minerai · Échap annuler"
    return " d déplacer · m miner · v vendre · h aide · q quitter"


def texte_aide(model: ClientModel, dev: bool) -> Text:
    """L'aide « Comment jouer », son titre en couleur `accent`."""
    lignes = help_pages(model.observation, dev)
    texte = Text(lignes[0], style=f"bold {couleur('accent')}")
    for ligne in lignes[1:]:
        texte.append("\n" + ligne, style=couleur("texte"))
    return texte


class Cadre(Static):
    """Un cadre de texte, sans balisage, qui ne prend pas le focus."""

    can_focus = False

    def __init__(self, titre: str, ident: str) -> None:
        super().__init__(ATTENTE, markup=False, id=ident)
        self.border_title = titre


class MapCanvas(Widget):
    """La carte rétro : peint la grille de `map_view.render`, en demi-blocs et en couleurs de la
    palette. La molette zoome autour du pointeur, le glisser déplace la vue, le survol montre la
    bulle, le clic choisit une destination. La grille n'est recalculée que si l'une de ses entrées
    change ; les mises à jour du tick sont plafonnées à 10 dessins par seconde."""

    can_focus = False
    INTERVALLE = 0.1

    class Clic(Message):
        def __init__(self, ident: int) -> None:
            super().__init__()
            self.ident = ident

    class Survol(Message):
        def __init__(self, ident: int | None, x: int, y: int) -> None:
            super().__init__()
            self.ident = ident
            self.x = x
            self.y = y

    class Vue(Message):
        """La vue a changé (zoom, déplacement) : l'en-tête de la carte se met à jour."""

    def __init__(self) -> None:
        super().__init__(id="carte-canevas")
        self.model: ClientModel | None = None
        self.positions: dict[int, tuple[float, float]] = {}
        self._graphe: tuple[tuple[int, tuple[int, ...]], ...] = ()
        self.vue: View = initial_view(1, 1)
        self.survol: int | None = None
        self.grille: tuple[tuple[Cell, ...], ...] = ()
        self._cle: object = None
        self._appui: tuple[int, int] | None = None
        self._vue_a_l_appui: View | None = None
        self._glisse = False
        self._dernier_dessin = 0.0
        self._attente = False

    # --- Données

    def montrer(self, model: ClientModel) -> None:
        """Une mise à jour du modèle : dessinée tout de suite, ou au plus tard dans 0,1 s."""
        self.model = model
        obs = model.observation
        if obs is not None:
            graphe = tuple((s.id, tuple(sorted(s.neighbors))) for s in obs.systems)
            if graphe != self._graphe:
                self._graphe = graphe
                self.positions = force_layout(obs.systems)
        attente = self.INTERVALLE - (time.monotonic() - self._dernier_dessin)
        if attente <= 0:
            self.dessiner()
        elif not self._attente:
            self._attente = True
            self.set_timer(attente, self._dessiner_en_retard)

    def _dessiner_en_retard(self) -> None:
        self._attente = False
        self.dessiner()

    def _entrees(self) -> object:
        """Les entrées de la grille : vue, survol, vaisseau, vaisseaux visibles, stocks."""
        obs = self.model.observation if self.model is not None else None
        if obs is None:
            return (self.vue, self.survol)
        return (
            self.vue,
            self.survol,
            tuple(obs.own_ships),
            tuple(sorted((v.system_id, v.id) for v in obs.other_ships)),
            tuple((d.id, d.stock) for d in obs.deposits),
            tuple(obs.stations),
        )

    def dessiner(self) -> None:
        self._dernier_dessin = time.monotonic()
        if self.model is None:
            return
        cle = self._entrees()
        if cle == self._cle:
            return
        self._cle = cle
        self.grille = render(self.vue, self.positions, self.model, self.survol)
        self.refresh()

    def changer_vue(self, vue: View) -> None:
        self.vue = vue
        self.dessiner()
        self.post_message(self.Vue())

    def on_resize(self, event: events.Resize) -> None:
        self.vue = View(self.vue.zoom_index, self.vue.center, event.size.width, event.size.height)
        self.dessiner()

    # --- Peinture

    def render_line(self, y: int) -> Strip:
        if y >= len(self.grille):
            return Strip.blank(self.size.width, Style(bgcolor=PALETTE["fond"]))
        segments: list[Segment] = []
        for case in self.grille[y]:
            style = Style(color=PALETTE[case.fg], bgcolor=PALETTE[case.bg])
            if segments and segments[-1].style == style:
                segments[-1] = Segment(segments[-1].text + case.char, style)
            else:
                segments.append(Segment(case.char, style))
        return Strip(segments)

    # --- Souris

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        event.stop()
        self.changer_vue(zoom(self.vue, 1, (event.x, event.y)))

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        event.stop()
        self.changer_vue(zoom(self.vue, -1, (event.x, event.y)))

    def on_mouse_down(self, event: events.MouseDown) -> None:
        event.stop()
        if event.button == 1:
            self._appui = (event.x, event.y)
            self._vue_a_l_appui = self.vue
            self._glisse = False

    def on_mouse_move(self, event: events.MouseMove) -> None:
        event.stop()
        if event.button == 1 and self._appui is not None and self._vue_a_l_appui is not None:
            # Le contenu suit le pointeur depuis l'appui, dès qu'il a bougé d'une case.
            dx = int(event.x) - self._appui[0]
            dy = int(event.y) - self._appui[1]
            if dx or dy:
                self._glisse = True
            self.changer_vue(pan(self._vue_a_l_appui, -dx, -dy))
            return
        survol = system_at(self.vue, self.positions, event.x, event.y)
        if survol != self.survol:
            self.survol = survol
            self.dessiner()
        self.post_message(self.Survol(survol, event.screen_x, event.screen_y))

    def on_mouse_up(self, event: events.MouseUp) -> None:
        event.stop()
        if self._appui is not None and not self._glisse:
            ident = system_at(self.vue, self.positions, event.x, event.y)
            if ident is not None:
                self.post_message(self.Clic(ident))
        self._appui = None
        self._vue_a_l_appui = None
        self._glisse = False

    def on_leave(self, event: events.Leave) -> None:
        if self.survol is not None:
            self.survol = None
            self.dessiner()
        self.post_message(self.Survol(None, 0, 0))


class CadreCarte(Vertical):
    """Le cadre de la carte : l'en-tête, le canevas et la légende."""

    can_focus = False

    def __init__(self) -> None:
        super().__init__(id="carte")
        self.border_title = "Carte"
        self.model: ClientModel | None = None

    def compose(self) -> ComposeResult:
        yield Static("", markup=False, id="carte-entete")
        yield MapCanvas()
        yield Static(texte_legende_carte(), markup=False, id="carte-legende")

    def montrer(self, model: ClientModel) -> None:
        self.model = model
        canevas = self.query_one(MapCanvas)
        canevas.montrer(model)
        self.query_one("#carte-entete", Static).update(texte_entete_carte(model, canevas.vue))

    def on_map_canvas_vue(self, message: MapCanvas.Vue) -> None:
        if self.model is not None:
            canevas = self.query_one(MapCanvas)
            entete = texte_entete_carte(self.model, canevas.vue)
            self.query_one("#carte-entete", Static).update(entete)


class Bulle(Static):
    """La bulle d'information d'un système survolé, 40 × 7, près du pointeur."""

    can_focus = False

    def __init__(self) -> None:
        super().__init__("", markup=False, id="bulle")


class CadreEtape(Cadre):
    def __init__(self) -> None:
        super().__init__("Prochaine étape", "etape")

    def montrer(self, model: ClientModel) -> None:
        self.update(texte_etape(model))


class CadreVaisseau(Cadre):
    def __init__(self) -> None:
        super().__init__("Vaisseau", "vaisseau")

    def montrer(self, model: ClientModel) -> None:
        self.update(texte_vaisseau(model))


class CadreStations(VerticalScroll):
    """Les prix et les gisements ; le cadre défile quand son contenu dépasse sa hauteur."""

    can_focus = False

    def __init__(self) -> None:
        super().__init__(id="stations")
        self.border_title = "Stations"

    def compose(self) -> ComposeResult:
        yield Static(ATTENTE, markup=False, id="stations-texte")

    def montrer(self, model: ClientModel) -> None:
        self.query_one("#stations-texte", Static).update(texte_stations(model))


class CadreHistorique(Cadre):
    def __init__(self) -> None:
        super().__init__("Historique", "historique")

    def montrer(self, model: ClientModel) -> None:
        self.update(texte_historique(model))


class CadreDestinations(Cadre):
    """La liste des destinations, à la place du cadre Stations pendant la saisie."""

    def __init__(self) -> None:
        super().__init__("Destinations", "destinations")

    def montrer(self, model: ClientModel, choix: int) -> None:
        self.update(texte_destinations(model, choix, self.content_region.height))


class BarreEtat(Static):
    can_focus = False

    def __init__(self) -> None:
        super().__init__("", markup=False, id="barre")

    def montrer(self, model: ClientModel, vitesse: str | None, aide: str) -> None:
        self.update(texte_barre(model, vitesse, aide))


class BarreTouches(Static):
    can_focus = False

    def __init__(self) -> None:
        super().__init__("", markup=False, id="touches")

    def montrer(self, saisie: str | None, aide_ouverte: bool) -> None:
        self.update(texte_touches(saisie, aide_ouverte))


class CadreAide(VerticalScroll):
    """L'aide « Comment jouer », superposée au centre de l'écran ; elle défile."""

    can_focus = False

    def __init__(self) -> None:
        super().__init__(id="aide")
        self.border_title = "Aide"

    def compose(self) -> ComposeResult:
        yield Static("", markup=False, id="aide-texte")

    def montrer(self, model: ClientModel, dev: bool) -> None:
        self.query_one("#aide-texte", Static).update(texte_aide(model, dev))
