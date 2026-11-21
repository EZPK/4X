"""Textes du client : refus en français et durées.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 bis (refus en français,
durées affichées) ; plan détaillé, point 23 quinquies (table des refus). Fonctions pures : elles
ne lisent que le résultat d'ordre, la commande refusée, que le modèle client garde sous le numéro
de l'ordre, et l'observation. Le texte de `OrderResult`, construit par `step`, n'est pas repris.
"""

from fourx.policies.geometry import distances
from fourx.schema.observation import Observation, OwnShipView
from fourx.schema.orders import Command, CreateCharacter, Mine, Move, Sell
from fourx.schema.protocol import NOMINAL_TICK_PERIOD_S
from fourx.schema.results import OrderResult, RefusalCode

TEXTES_FIXES = {
    RefusalCode.UNKNOWN_SHIP: "vaisseau inconnu",
    RefusalCode.NOT_OWNER: "ce vaisseau n'est pas le vôtre",
    RefusalCode.UNKNOWN_SYSTEM: "système inconnu",
    RefusalCode.QUANTITY_NOT_POSITIVE: "quantité nulle ou négative",
    RefusalCode.NO_ACTION_LEFT: "plus d'action disponible ce tick",
    RefusalCode.SUPERSEDED: "remplacé par un autre ordre du même tick",
    RefusalCode.INVALID_FORMAT: "ordre mal formé",
    RefusalCode.DUPLICATE_NUMBER: "numéro d'ordre déjà utilisé",
    RefusalCode.QUOTA_EXCEEDED: "trop d'ordres ce tick",
    RefusalCode.ACTOR_MISMATCH: "ordre au nom d'un autre personnage",
    RefusalCode.FORBIDDEN_CATEGORY: "catégorie d'ordre interdite",
}


def systeme(ident: int) -> str:
    return f"system_{ident}"


def minerai(ore_id: int) -> str:
    return "ore_" + chr(ord("a") + ore_id - 1)


def station(ident: int) -> str:
    """Libellé court d'une station : S1 pour station_1."""
    return f"S{ident}"


def sauts(n: int) -> str:
    return "1 saut" if n == 1 else f"{n} sauts"


def ticks_de_trajet(navire: OwnShipView, jump_ticks: int) -> int:
    """Ticks restants d'un trajet : le saut en cours, puis un saut complet par système restant."""
    return navire.ticks_to_next_jump + (len(navire.route) - 1) * jump_ticks


def duration_text(ticks: int) -> str:
    """« 400 ticks (≈ 20 min à 3 s) » : estimation à la période nominale, sans les unités nulles."""
    secondes = round(ticks * NOMINAL_TICK_PERIOD_S)
    heures, reste = divmod(secondes, 3600)
    minutes, secondes = divmod(reste, 60)
    morceaux = [
        f"{valeur} {unite}"
        for valeur, unite in ((heures, "h"), (minutes, "min"), (secondes, "s"))
        if valeur
    ]
    estimation = " ".join(morceaux) or "0 s"
    unite = "tick" if ticks == 1 else "ticks"
    return f"{ticks} {unite} (≈ {estimation} à {NOMINAL_TICK_PERIOD_S:g} s)"


def _navire(observation: Observation, command: Move | Mine | Sell) -> OwnShipView | None:
    return next((v for v in observation.own_ships if v.id == command.ship_id), None)


def _plus_proche(dist: dict[int, int], lieux: list[tuple[int, int]]) -> tuple[int, int] | None:
    """Parmi des lieux (identifiant, système), le plus proche en sauts, puis le plus petit
    identifiant ; None si aucun n'est accessible."""
    accessibles = [(dist[s], ident, s) for ident, s in lieux if s in dist]
    if not accessibles:
        return None
    _, ident, s = min(accessibles)
    return ident, s


def _sans_gisement(observation: Observation, ore_id: int, dist: dict[int, int]) -> str:
    debut = f"pas de gisement de {minerai(ore_id)} ici"
    lieux = [(d.system_id, d.system_id) for d in observation.deposits if d.ore_id == ore_id]
    trouve = _plus_proche(dist, lieux)
    if trouve is None:
        return debut
    return f"{debut} ; le plus proche est dans {systeme(trouve[1])} ({sauts(dist[trouve[1]])})"


def _gisement_vide(observation: Observation, ore_id: int, ici: int, dist: dict[int, int]) -> str:
    lieux = [
        (d.system_id, d.system_id)
        for d in observation.deposits
        if d.ore_id == ore_id and d.system_id != ici and (d.stock is None or d.stock > 0)
    ]
    trouve = _plus_proche(dist, lieux)
    if trouve is None:
        return f"gisement vide ; tous les gisements de {minerai(ore_id)} connus sont vides"
    return (
        f"gisement vide ; le plus proche gisement de {minerai(ore_id)} qui n'est pas connu "
        f"comme vide est dans {systeme(trouve[1])} ({sauts(dist[trouve[1]])})"
    )


def _station_la_plus_proche(observation: Observation, dist: dict[int, int]) -> tuple[int, int]:
    trouve = _plus_proche(dist, [(s.id, s.system_id) for s in observation.stations])
    if trouve is None:
        raise ValueError("aucune station accessible depuis le vaisseau")
    return trouve


def refusal_text(result: OrderResult, command: Command, observation: Observation) -> str:
    """Le refus en français ; pour un refus lié à un lieu, où aller (Technical Plan, 7 bis)."""
    code = result.refusal
    if code is None:
        raise ValueError("refusal_text attend un ordre refusé")
    if code in TEXTES_FIXES:
        return TEXTES_FIXES[code]
    if isinstance(command, CreateCharacter):
        raise ValueError(f"refus {code.name} inattendu pour une création de personnage")
    navire = _navire(observation, command)
    if navire is None:
        raise ValueError(f"vaisseau {command.ship_id} absent de l'observation")
    dist = distances(observation.systems, navire.system_id)
    if code is RefusalCode.SHIP_EN_ROUTE:
        ticks = ticks_de_trajet(navire, observation.public_tunables.jump_ticks)
        return f"vaisseau en route : arrivée dans {ticks} ticks"
    if code is RefusalCode.ALREADY_THERE and isinstance(command, Move):
        return f"déjà dans {systeme(command.target_system_id)}"
    if code is RefusalCode.NO_DEPOSIT_FOR_ORE and isinstance(command, Mine):
        return _sans_gisement(observation, command.ore_id, dist)
    if code is RefusalCode.DEPOSIT_EMPTY and isinstance(command, Mine):
        return _gisement_vide(observation, command.ore_id, navire.system_id, dist)
    if code is RefusalCode.CARGO_FULL:
        ident, lieu = _station_la_plus_proche(observation, dist)
        return (
            "cargaison pleine : allez vendre ; la station la plus proche est "
            f"{station(ident)} ({sauts(dist[lieu])})"
        )
    if code is RefusalCode.NOT_AT_STATION:
        ident, lieu = _station_la_plus_proche(observation, dist)
        return (
            f"pas de station ici ; la plus proche est {station(ident)}, "
            f"dans {systeme(lieu)} ({sauts(dist[lieu])})"
        )
    if (
        code is RefusalCode.QUANTITY_EXCEEDS_CARGO
        and isinstance(command, Sell)
        and 1 <= command.ore_id <= len(navire.cargo)
    ):
        a_bord = navire.cargo[command.ore_id - 1]
        return f"quantité supérieure à la cargaison ({a_bord} à bord)"
    raise ValueError(f"refus {code.name} inattendu pour la commande {type(command).__name__}")
