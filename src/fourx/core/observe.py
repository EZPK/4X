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


def vue(entite: Any, type_vue: type[Any], detient: bool, a_portee: bool = False) -> Any:
    """Construit une vue en ne copiant que les champs visibles.

    Un champ de proximité hors de portée vaut None ; tout autre champ invisible pour l'acteur
    lève une erreur."""
    visibles = classes(type(entite))
    valeurs: dict[str, Any] = {}
    for champ in msgspec.structs.fields(type_vue):
        classe = visibles[champ.name]
        if classe is Visibility.NEARBY and not (detient or a_portee):
            valeurs[champ.name] = None
            continue
        if (
            classe is not Visibility.PUBLIC
            and classe is not Visibility.NEARBY
            and not (classe is Visibility.PRIVATE and detient)
        ):
            raise ValueError(f"champ {champ.name} invisible pour cet acteur")
        valeurs[champ.name] = getattr(entite, champ.name)
    return type_vue(**valeurs)


def portee(state: State, actor_id: int) -> tuple[int, ...]:
    """Les systèmes des vaisseaux de l'acteur et leurs voisins, triés par identifiant."""
    voisins = {s.id: s.neighbors for s in state.systems}
    systemes: dict[int, None] = {}
    for v in state.ships:
        if v.owner_id == actor_id:
            systemes[v.system_id] = None
            for voisin in voisins[v.system_id]:
                systemes[voisin] = None
    return tuple(sorted(systemes))


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
        systems=tuple(vue(s, SystemView, False) for s in state.systems),
        deposits=tuple(vue(d, DepositView, False, d.system_id in systemes) for d in state.deposits),
        stations=tuple(vue(s, StationView, False) for s in state.stations),
        actors=tuple(vue(a, ActorView, False) for a in state.actors),
        own_ships=tuple(vue(v, OwnShipView, True) for v in state.ships if v.owner_id == actor_id),
        other_ships=tuple(
            vue(v, OtherShipView, False, True)
            for v in state.ships
            if v.owner_id != actor_id and v.system_id in systemes
        ),
        wallet_balance=_solde(state.ledger, actor_id),
        action_budget=acteur.action_budget if acteur is not None else 0,
        events=evenements,
        results=tuple(r for r in state.last_tick.results if r.recipient_actor_id == actor_id),
        public_tunables=PublicTunablesView(
            jump_ticks=tunables.jump_ticks, mining_rate=tunables.mining_rate
        ),
    )
