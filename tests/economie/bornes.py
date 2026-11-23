"""Les bornes larges de l'économie de la partie de référence (docs/designs/niveau-2-m1-noyau.md,
plan détaillé, point 27, amendement 1 ; Technical Plan, point 9).

Elles se calculent à partir de l'état initial, du nombre de PNJ et des réglages, sans lire la
partie ni dépendre de la politique du PNJ. Notations du plan : W = 10 000 ; N, le nombre de PNJ ;
J = `jump_ticks` ; M = `cargo_capacity` ÷ `mining_rate` ; Q = `cargo_capacity` ; p_max, le plus
grand prix de rachat des stations ; d_min, la plus petite distance en sauts entre une station et un
gisement ; C_min = 2 × d_min × J + M ; b' = ⌈W ÷ C_min⌉ + 1. Borne haute de l'émission par
fenêtre : N × b' × Q × p_max.

M est arrondi vers le bas : C_min reste une durée minimale, et la borne haute ne peut que grandir.
"""

from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass

from fourx.core.state import State
from fourx.core.tunables import Tunables
from fourx.schema.events import Event, Sale
from fourx.schema.ledger import Reason
from fourx.tools.economy import MOTIFS, WindowStats, window_stats

FENETRE = 10_000


@dataclass(frozen=True)
class Bornes:
    fenetre: int
    n_pnj: int
    p_max: int
    d_min: int
    duree_minimale_d_un_cycle: int
    cycles_max_par_fenetre: int
    emission_max: int


def distances(etat: State, depart: int) -> dict[int, int]:
    """Distances en sauts depuis `depart`, par un parcours en largeur sur les voisins."""
    voisins = {s.id: s.neighbors for s in etat.systems}
    vues = {depart: 0}
    file = deque([depart])
    while file:
        courant = file.popleft()
        for suivant in voisins[courant]:
            if suivant not in vues:
                vues[suivant] = vues[courant] + 1
                file.append(suivant)
    return vues


def bornes(etat_initial: State, n_pnj: int, tunables: Tunables) -> Bornes:
    p_max = max(p for station in etat_initial.stations for p in station.ore_prices)
    gisements = {g.system_id for g in etat_initial.deposits}
    d_min = min(
        d
        for station in etat_initial.stations
        for systeme, d in distances(etat_initial, station.system_id).items()
        if systeme in gisements
    )
    minage = tunables.cargo_capacity // tunables.mining_rate
    c_min = 2 * d_min * tunables.jump_ticks + minage
    if c_min <= 0:
        raise ValueError("un cycle dure au moins un tick")
    b_prime = -(-FENETRE // c_min) + 1
    return Bornes(
        fenetre=FENETRE,
        n_pnj=n_pnj,
        p_max=p_max,
        d_min=d_min,
        duree_minimale_d_un_cycle=c_min,
        cycles_max_par_fenetre=b_prime,
        emission_max=n_pnj * b_prime * tunables.cargo_capacity * p_max,
    )


def taxe(paiement: int, tax_rate_bp: int) -> int:
    """La taxe d'une vente, arrondie vers le haut (Technical Plan, point 3)."""
    return -(-paiement * tax_rate_bp // 10_000)


def ecarts(
    evenements: Sequence[Event], limites: Bornes, tax_rate_bp: int, n_fenetres: int
) -> tuple[tuple[WindowStats, ...], list[str]]:
    """Les fenêtres de la partie et la liste de leurs écarts aux bornes (vide si aucun) :
    émission ORE_SALE strictement positive et au plus `emission_max` ; destruction SALE_TAX égale
    à la somme des taxes des ventes de la fenêtre, arrondies vers le haut ; croissance de la masse
    monétaire entre 0 et `emission_max` (`window_stats` la calcule déjà comme l'émission moins la
    destruction : l'invariant 2 n'est pas revérifié ici, `step` le garde à chaque tick)."""
    fenetres = window_stats(evenements, limites.fenetre)
    vente, taxe_de_vente = MOTIFS.index(Reason.ORE_SALE), MOTIFS.index(Reason.SALE_TAX)
    taxes: dict[int, int] = {}
    for e in evenements:
        if isinstance(e.payload, Sale):
            rang = (e.tick - 1) // limites.fenetre
            taxes[rang] = taxes.get(rang, 0) + taxe(e.payload.payment, tax_rate_bp)
    erreurs: list[str] = []
    if len(fenetres) != n_fenetres:
        erreurs.append(f"{len(fenetres)} fenêtres au lieu de {n_fenetres}")
    for rang, f in enumerate(fenetres):
        nom = f"fenêtre {f.first_tick}-{f.first_tick + limites.fenetre - 1}"
        emis = f.issued_by_reason[vente]
        detruit = f.destroyed_by_reason[taxe_de_vente]
        if emis <= 0:
            erreurs.append(f"{nom} : aucune vente")
        if emis > limites.emission_max:
            erreurs.append(f"{nom} : émission {emis} au-dessus de {limites.emission_max}")
        if detruit != taxes.get(rang, 0):
            erreurs.append(f"{nom} : destruction {detruit}, taxes des ventes {taxes.get(rang, 0)}")
        if not 0 <= f.money_supply_growth <= limites.emission_max:
            erreurs.append(f"{nom} : croissance {f.money_supply_growth} hors de [0, émission max]")
    return fenetres, erreurs
