"""Les cadres de l'écran unique : un widget Textual par cadre.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 bis. Chaque cadre lit
`ClientModel` et ne connaît pas les autres : on peut en ajouter, en retirer ou les réarranger
sans toucher au reste. Le texte de chaque cadre vient d'une fonction de ce module ; le widget ne
fait que l'afficher. Aucun cadre ne prend le focus : toutes les touches vont à `FourxApp`.
"""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from fourx.clients.map_layout import layout
from fourx.clients.model import ClientModel, decrire
from fourx.clients.texts import duration_text, minerai, station, systeme
from fourx.policies.geometry import distances
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation

ATTENTE = "En attente du premier tick…"
ACTIVITES = {
    Activity.IDLE: "à l'arrêt",
    Activity.EN_ROUTE: "en route",
    Activity.MINING: "en minage",
}


def texte_carte(model: ClientModel) -> str:
    """La carte de `layout`, puis la ligne des vaisseaux : le joueur (@), les vaisseaux proches
    (o), par système."""
    obs = model.observation
    if obs is None:
        return ATTENTE
    propres = " ".join(f"[{v.system_id}]" for v in obs.own_ships) or "aucun"
    autres = " ".join(
        f"[{v.system_id}]" for v in sorted(obs.other_ships, key=lambda v: (v.system_id, v.id))
    )
    ligne = f"@ joueur : {propres}   o vaisseaux proches : {autres or 'aucun'}"
    return "\n".join([*layout(obs), "", ligne])


def deux_lignes(debut: str, ticks: int) -> list[str]:
    """« arrivée dans 62 ticks », puis l'estimation « (≈ 3 min 6 s à 3 s) » sur sa ligne."""
    duree, estimation = duration_text(ticks).split(" (", 1)
    return [f"{debut} {duree}", f"({estimation}"]


def texte_vaisseau(model: ClientModel) -> str:
    """Où est le vaisseau, ce qu'il fait, les ticks restants, la cargaison, les ordres envoyés."""
    navire = model.vaisseau()
    if model.observation is None or navire is None:
        return ATTENTE
    lignes = [f"{systeme(navire.system_id)}  {ACTIVITES[navire.activity]}"]
    restants = model.remaining_ticks()
    if navire.activity is Activity.EN_ROUTE:
        lignes.append(f"vers {systeme(navire.route[-1])}")
        if restants is not None:
            lignes += deux_lignes("arrivée dans", restants)
    elif navire.activity is Activity.MINING:
        if navire.mining_ore_id is not None:
            lignes.append(f"mine {minerai(navire.mining_ore_id)}")
        if restants is not None:
            lignes += deux_lignes("fin dans", restants)
    lignes.append(f"cargaison {sum(navire.cargo)}/{navire.capacity}")
    lignes.append("  ".join(f"{minerai(rang + 1)} {q}" for rang, q in enumerate(navire.cargo)))
    envoyes = [decrire(c) for _, c in model.pending]
    lignes.append("ordre envoyé : " + ("; ".join(envoyes) if envoyes else "aucun"))
    return "\n".join(lignes)


def texte_stations(model: ClientModel) -> str:
    """Chaque station, son système et son prix de rachat de chaque minerai."""
    obs = model.observation
    if obs is None:
        return ATTENTE
    lignes = []
    for s in obs.stations:
        prix = "  ".join(f"{chr(ord('a') + rang)} {p}" for rang, p in enumerate(s.ore_prices))
        lignes.append(f"{station(s.id)} sys {s.system_id}  {prix}")
    return "\n".join(lignes)


def texte_historique(model: ClientModel, hauteur: int) -> str:
    """Les dernières lignes de l'historique, la plus récente en bas."""
    lignes = model.history[-hauteur:] if hauteur > 0 else model.history
    return "\n".join(lignes)


def texte_alerte(model: ClientModel) -> str:
    """La plus ancienne alerte non acquittée, et le nombre d'alertes qui suivent."""
    if not model.alerts:
        return ""
    texte = f"t{model.alerts[0].tick} {model.alerts[0].text} · Entrée : acquitter"
    if len(model.alerts) > 1:
        texte += f" ({len(model.alerts) - 1} de plus)"
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


def texte_barre(model: ClientModel, vitesse: str | None, aide: str) -> str:
    """Première ligne : tick, solde, en mode développement la vitesse demandée, et les touches ;
    seconde ligne : l'aide ou l'invite de la saisie en cours."""
    obs = model.observation
    morceaux = [
        f"Tick {obs.tick}" if obs else "Tick —",
        f"Solde {obs.wallet_balance}" if obs else "Solde —",
    ]
    if vitesse is not None:
        morceaux.append(f"dev {vitesse}")
    morceaux.append("d m v q" + (" · dev : p a r ␣" if vitesse is not None else ""))
    return " " + " │ ".join(morceaux) + "\n " + aide


class Cadre(Static):
    """Un cadre de texte brut, sans balisage, qui ne prend pas le focus."""

    can_focus = False

    def __init__(self, titre: str, ident: str) -> None:
        super().__init__(ATTENTE, markup=False, id=ident)
        self.border_title = titre


class CadreCarte(VerticalScroll):
    """Le cadre Carte défile verticalement si la carte dépasse sa hauteur."""

    can_focus = False

    def __init__(self) -> None:
        super().__init__(id="carte")
        self.border_title = "Carte"

    def compose(self) -> ComposeResult:
        yield Static(ATTENTE, markup=False, id="carte-texte")

    def montrer(self, model: ClientModel) -> None:
        self.query_one("#carte-texte", Static).update(texte_carte(model))


class CadreVaisseau(Cadre):
    def __init__(self) -> None:
        super().__init__("Vaisseau", "vaisseau")

    def montrer(self, model: ClientModel) -> None:
        self.update(texte_vaisseau(model))


class CadreStations(Cadre):
    def __init__(self) -> None:
        super().__init__("Stations", "stations")

    def montrer(self, model: ClientModel) -> None:
        self.update(texte_stations(model))


class CadreHistorique(Cadre):
    def __init__(self) -> None:
        super().__init__("Historique", "historique")

    def montrer(self, model: ClientModel) -> None:
        self.update(texte_historique(model, self.content_region.height))


class CadreAlerte(Cadre):
    """En vidéo inverse au-dessus de l'historique, seulement quand une alerte attend."""

    def __init__(self) -> None:
        super().__init__("Alerte", "alerte")

    def montrer(self, model: ClientModel) -> None:
        self.update(texte_alerte(model))
        self.display = bool(model.alerts)


class CadreDestinations(Cadre):
    """La liste des destinations, à la place de l'historique pendant la saisie."""

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
