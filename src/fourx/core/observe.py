"""La fonction `observe`.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 5 ; niveau 1, §5.

`observe` lit tout dans l'état, et les réglages qu'il reçoit (ADR 0003). Les vues reprennent
les champs de données de l'état dont la classe de visibilité, relue dans les métadonnées msgspec,
est visible pour l'acteur : publique ; privée et détenue par lui ; de proximité (ADR 0005) et
détenue par lui, ou à portée. La *portée* d'un acteur est l'ensemble des systèmes de ses
vaisseaux et de leurs voisins, dans l'état reçu. Hors de portée, un vaisseau d'autrui disparaît
de l'observation, et un champ de proximité d'une entité publique (le stock d'un gisement) vaut
None. Les événements du dernier tick suivent la classe de leur type ; le système de référence
d'un événement de proximité est celui de sa charge utile, ou, pour un événement de gisement,
le système du gisement.
"""

from typing import Any

import msgspec
import msgspec.inspect

from fourx.core.ledger import Ledger
from fourx.core.state import State
from fourx.core.tunables import Tunables
from fourx.schema.events import Arrived, Departed, DepositRegenerated, Event
from fourx.schema.ledger import AccountKind
from fourx.schema.observation import (
    ActorView,
    DepositView,
    Observation,
    OtherShipView,
    OwnShipView,
    PublicTunablesView,
    StationView,
    SystemView,
)
from fourx.schema.visibility import Visibility, classe_de


def classes(type_entite: type[Any]) -> dict[str, Visibility | None]:
    """Classe de visibilité de chaque champ de données d'un type d'entité de l'état."""
    info = msgspec.inspect.type_info(type_entite)
    resultat: dict[str, Visibility | None] = {}
    for champ in info.fields:  # type: ignore[attr-defined]
        meta = champ.type
        resultat[champ.name] = classe_de(
            meta.extra if isinstance(meta, msgspec.inspect.Metadata) else None
        )
    return resultat


_PLANS: dict[tuple[type[Any], type[Any]], tuple[tuple[str, Visibility | None], ...]] = {}


def plan(type_entite: type[Any], type_vue: type[Any]) -> tuple[tuple[str, Visibility | None], ...]:
    """Les champs d'une vue et leur classe de visibilité dans l'état.

    Les métadonnées d'un type ne changent pas : le plan est relu une fois par couple de types,
    et non à chaque vue (msgspec.inspect est lent : 2 000 ticks prenaient plus de 30 s)."""
    cle = (type_entite, type_vue)
    if cle not in _PLANS:
        visibles = classes(type_entite)
        _PLANS[cle] = tuple(
            (champ.name, visibles[champ.name]) for champ in msgspec.structs.fields(type_vue)
        )
    return _PLANS[cle]


PUBLIQUE = (Visibility.PUBLIC,)
"""Classes visibles d'une entité hors de portée, ou d'un type sans champ de proximité."""
A_PORTEE = (Visibility.PUBLIC, Visibility.NEARBY)
"""Classes visibles d'une entité d'autrui à portée."""
DETENUE = (Visibility.PUBLIC, Visibility.NEARBY, Visibility.PRIVATE)
"""Classes visibles d'une entité détenue par l'acteur."""


def vue(entite: Any, type_vue: type[Any], visibles: tuple[Visibility, ...]) -> Any:
    """Construit une vue en ne copiant que les champs dont la classe est dans `visibles`.

    Un champ de proximité hors de portée vaut None ; tout autre champ invisible pour l'acteur
    lève une erreur."""
    valeurs: dict[str, Any] = {}
    for nom, classe in plan(type(entite), type_vue):
        if classe in visibles:
            valeurs[nom] = getattr(entite, nom)
        elif classe is Visibility.NEARBY:
            valeurs[nom] = None
        else:
            raise ValueError(f"champ {nom} invisible pour cet acteur")
    return type_vue(**valeurs)


def portee(state: State, actor_id: int) -> tuple[int, ...]:
    """Les systèmes des vaisseaux de l'acteur et leurs voisins, triés par identifiant."""
    voisins = {s.id: s.neighbors for s in state.systems}
    propres = [v.system_id for v in state.ships if v.owner_id == actor_id]
    return tuple(
        sorted(s.id for s in state.systems if any(s.id == p or s.id in voisins[p] for p in propres))
    )


def systeme_de_reference(state: State, evenement: Event) -> int:
    """Le système de référence d'un événement de proximité (Technical Plan, point 5)."""
    charge = evenement.payload
    if isinstance(charge, DepositRegenerated):
        return next(d.system_id for d in state.deposits if d.id == charge.deposit_id)
    if isinstance(charge, Departed | Arrived):
        return charge.system_id
    raise ValueError(f"événement de proximité sans système de référence : {type(charge).__name__}")


def _visible(state: State, evenement: Event, actor_id: int, systemes: tuple[int, ...]) -> bool:
    if evenement.visibility is Visibility.PUBLIC:
        return True
    if evenement.visibility is Visibility.PRIVATE:
        return evenement.actor_id == actor_id
    if evenement.visibility is Visibility.NEARBY:
        return systeme_de_reference(state, evenement) in systemes
    return False


def _solde(ledger: Ledger, actor_id: int) -> int:
    for c in ledger.accounts:
        if c.kind is AccountKind.PERSONAL_WALLET and c.owner_id == actor_id:
            return c.balance
    return 0


def observe(state: State, actor_id: int, tunables: Tunables) -> Observation:
    acteur = next((a for a in state.actors if a.id == actor_id), None)
    systemes = portee(state, actor_id)
    evenements = tuple(e for e in state.last_tick.events if _visible(state, e, actor_id, systemes))
    return Observation(
        tick=state.tick,
        actor_id=actor_id,
        systems=tuple(vue(s, SystemView, PUBLIQUE) for s in state.systems),
        deposits=tuple(
            vue(d, DepositView, A_PORTEE if d.system_id in systemes else PUBLIQUE)
            for d in state.deposits
        ),
        stations=tuple(vue(s, StationView, PUBLIQUE) for s in state.stations),
        actors=tuple(vue(a, ActorView, PUBLIQUE) for a in state.actors),
        own_ships=tuple(
            vue(v, OwnShipView, DETENUE) for v in state.ships if v.owner_id == actor_id
        ),
        other_ships=tuple(
            vue(v, OtherShipView, A_PORTEE)
            for v in state.ships
            if v.owner_id != actor_id and v.system_id in systemes
        ),
        wallet_balance=_solde(state.ledger, actor_id + 1),
        action_budget=acteur.action_budget if acteur is not None else 0,
        events=evenements,
        results=tuple(r for r in state.last_tick.results if r.recipient_actor_id == actor_id),
        public_tunables=PublicTunablesView(
            jump_ticks=tunables.jump_ticks, mining_rate=tunables.mining_rate
        ),
    )
