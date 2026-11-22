"""La prochaine étape : un conseil au joueur, calculé sur le modèle client.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 ter (prochaine étape) et
point 13 (interface). Fonction pure : elle ne lit que `ClientModel` (observation, alertes, ordres
envoyés, gisements vus vides) et n'envoie jamais d'ordre. La première règle qui s'applique donne
l'étape :

0. aucune observation encore ; 0 bis. aucun vaisseau du joueur ;
1. une alerte attend ; 2. des ordres envoyés attendent leur résultat ;
3. en route ; 4. en minage ;
5. à l'arrêt, cargaison pleine, ou non vide dans le système d'une station : la vente ;
6. à l'arrêt, sinon : le cycle au meilleur gain par tick.

Les gains par tick se comparent en entiers, par produits croisés (a ÷ b > c ÷ d si a × d > c × b).
Seuls comptent les stations et les gisements qu'atteint `distances` depuis le vaisseau.
"""

import functools
from dataclasses import dataclass

from fourx.clients.model import ClientModel, decrire, plafond
from fourx.clients.texts import duration_text, minerai, sauts, station, systeme
from fourx.policies.geometry import distances
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OwnShipView
from fourx.schema.orders import Command, Mine, Move


@dataclass(frozen=True)
class Step:
    title: str
    detail: str
    keys: tuple[str, ...]
    command: Command | None


def _meilleur_gain(gain_a: int, duree_a: int, gain_b: int, duree_b: int) -> int:
    """1 si gain_a ÷ duree_a > gain_b ÷ duree_b, −1 si plus petit, 0 à égalité."""
    gauche, droite = gain_a * duree_b, gain_b * duree_a
    return (gauche > droite) - (gauche < droite)


def best_sale(
    observation: Observation, system_id: int, cargo: tuple[int, ...]
) -> tuple[int, int, int] | None:
    """La station où vendre la cargaison depuis le système : le plus grand V ÷ (t + 1), où V est
    la valeur de la cargaison au prix brut de la station et t la durée du trajet ; à égalité, la
    plus proche, puis le plus petit identifiant. Rend (station, V, t), ou None si aucune station
    n'est atteinte."""
    dist = distances(observation.systems, system_id)
    saut = observation.public_tunables.jump_ticks
    retenue: tuple[int, int, int] | None = None
    for s in observation.stations:
        if s.system_id not in dist:
            continue
        valeur = sum(q * p for q, p in zip(cargo, s.ore_prices, strict=True))
        trajet = dist[s.system_id] * saut
        if retenue is None:
            retenue = (s.id, valeur, trajet)
            continue
        ordre = _meilleur_gain(valeur, trajet + 1, retenue[1], retenue[2] + 1)
        if ordre > 0 or (ordre == 0 and (trajet, s.id) < (retenue[2], retenue[0])):
            retenue = (s.id, valeur, trajet)
    return retenue


def _systeme_de_station(observation: Observation, ident: int) -> int:
    return next(s.system_id for s in observation.stations if s.id == ident)


def _autre_vaisseau_ici(observation: Observation, navire: OwnShipView) -> bool:
    return any(v.system_id == navire.system_id for v in observation.other_ships)


def _vente(observation: Observation, navire: OwnShipView) -> Step:
    """Règle 5 : vendre ici, ou aller vendre à la station retenue par `best_sale`."""
    retenue = best_sale(observation, navire.system_id, navire.cargo)
    if retenue is None:
        return Step("Aucune station accessible", "", (), None)
    ident, valeur, trajet = retenue
    cible = _systeme_de_station(observation, ident)
    if cible == navire.system_id:
        return Step("Vendre la cargaison ici", f"valeur avant taxe : {valeur}", ("v",), None)
    n = distances(observation.systems, navire.system_id)[cible]
    return Step(
        f"Aller vendre à {station(ident)}",
        f"{sauts(n)}, {duration_text(trajet)} ; valeur avant taxe : {valeur}",
        ("d",),
        Move(ship_id=navire.id, target_system_id=cible),
    )


@dataclass(frozen=True)
class _Candidat:
    gain: int
    duree: int
    gisement: int | None  # None : la vente directe
    quantite: int = 0
    station: int = 0


def _comparer(a: _Candidat, b: _Candidat) -> int:
    """Négatif si a passe avant b : plus grand gain par tick, puis plus petite durée, puis la
    vente directe, puis le plus petit identifiant de gisement."""
    ordre = _meilleur_gain(a.gain, a.duree, b.gain, b.duree)
    if ordre:
        return -ordre
    cle_a = (a.duree, a.gisement is not None, a.gisement or 0)
    cle_b = (b.duree, b.gisement is not None, b.gisement or 0)
    return (cle_a > cle_b) - (cle_a < cle_b)


def _candidats(
    model: ClientModel, observation: Observation, navire: OwnShipView
) -> list[_Candidat]:
    reglages = observation.public_tunables
    dist = distances(observation.systems, navire.system_id)
    libre = navire.capacity - sum(navire.cargo)
    candidats = []
    for g in observation.deposits:
        if g.system_id not in dist or g.stock == 0 or g.id in model.seen_empty:
            continue
        quantite = libre if g.stock is None else min(libre, g.stock)
        prevue = tuple(
            q + (quantite if rang + 1 == g.ore_id else 0) for rang, q in enumerate(navire.cargo)
        )
        retenue = best_sale(observation, g.system_id, prevue)
        if retenue is None:
            continue
        ident, valeur, trajet = retenue
        duree = (
            dist[g.system_id] * reglages.jump_ticks
            + plafond(quantite, reglages.mining_rate)
            + trajet
        )
        candidats.append(_Candidat(valeur, duree, g.id, quantite, ident))
    if sum(navire.cargo) > 0:
        directe = best_sale(observation, navire.system_id, navire.cargo)
        if directe is not None:
            candidats.append(_Candidat(directe[1], directe[2] + 1, None))
    return candidats


def _cycle(model: ClientModel, observation: Observation, navire: OwnShipView) -> Step:
    """Règle 6 : le cycle au meilleur gain par tick, ou la vente directe."""
    candidats = _candidats(model, observation, navire)
    if not candidats:
        return Step(
            "Aucun gisement connu disponible",
            "tous les gisements connus sont vides : attendre leur régénération",
            (),
            None,
        )
    choisi = min(candidats, key=functools.cmp_to_key(_comparer))
    if choisi.gisement is None:
        return _vente(observation, navire)
    gisement = next(d for d in observation.deposits if d.id == choisi.gisement)
    reglages = observation.public_tunables
    if gisement.system_id == navire.system_id:
        fin = duration_text(plafond(choisi.quantite, reglages.mining_rate))
        borne = "au plus " if _autre_vaisseau_ici(observation, navire) else ""
        lieu = _systeme_de_station(observation, choisi.station)
        if lieu == navire.system_id:
            suite = "puis vendre ici"
        else:
            n = distances(observation.systems, navire.system_id)[lieu]
            suite = f"puis vendre à {station(choisi.station)} ({sauts(n)})"
        return Step(
            f"Miner {minerai(gisement.ore_id)} ici",
            f"fin du minage dans {borne}{fin} ; {suite}",
            ("m",),
            Mine(ship_id=navire.id, ore_id=gisement.ore_id),
        )
    n = distances(observation.systems, navire.system_id)[gisement.system_id]
    detail = (
        f"{sauts(n)}, {duration_text(n * reglages.jump_ticks)} ; "
        f"cycle complet estimé : {duration_text(choisi.duree)}"
    )
    if gisement.stock is None:
        detail += " (stock inconnu)"
    return Step(
        f"Aller miner {minerai(gisement.ore_id)} à {systeme(gisement.system_id)}",
        detail,
        ("d",),
        Move(ship_id=navire.id, target_system_id=gisement.system_id),
    )


def next_step(model: ClientModel) -> Step:
    """La prochaine étape conseillée (Technical Plan, point 7 ter, règles 0 à 6)."""
    observation = model.observation
    if observation is None:
        return Step("En attente du premier tick", "", (), None)
    navire = model.vaisseau()
    if navire is None:
        return Step("Aucun vaisseau", "", (), None)
    if model.alerts:
        autres = len(model.alerts) - 1
        titre = model.alerts[0].text + (f" (+{autres})" if autres else "")
        return Step(titre, "Entrée : acquitter", ("enter",), None)
    if model.pending:
        ordres = " ; ".join(decrire(c) for _, c in model.pending)
        return Step(f"Ordre envoyé : {ordres}", "résultat au prochain tick", (), None)
    restants = model.remaining_ticks()
    if navire.activity is Activity.EN_ROUTE:
        detail = "" if restants is None else f"arrivée dans {duration_text(restants)}"
        return Step(f"En route vers {systeme(navire.route[-1])}", detail, (), None)
    if navire.activity is Activity.MINING:
        borne = "au plus " if _autre_vaisseau_ici(observation, navire) else ""
        duree = "" if restants is None else duration_text(restants)
        nom = "" if navire.mining_ore_id is None else minerai(navire.mining_ore_id)
        return Step(
            f"Minage de {nom}",
            f"fin du minage dans {borne}{duree} : cargaison pleine ou gisement vide",
            (),
            None,
        )
    charge = sum(navire.cargo)
    dans_une_station = any(s.system_id == navire.system_id for s in observation.stations)
    if charge >= navire.capacity or (charge > 0 and dans_une_station):
        return _vente(observation, navire)
    return _cycle(model, observation, navire)
