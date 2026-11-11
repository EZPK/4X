"""La fonction `observe`.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 5 ; niveau 1, §5.

`observe` lit tout dans l'état. Les vues reprennent les champs de données de l'état dont la
classe de visibilité, relue dans les métadonnées msgspec, est visible pour l'acteur : publique,
ou privée et détenue par lui. Les événements du dernier tick suivent la classe de leur type.
"""

from typing import Any

import msgspec
import msgspec.inspect

from fourx.core.ledger import Ledger
from fourx.core.state import State
from fourx.schema.ledger import AccountKind
from fourx.schema.observation import (
    ActorView,
    DepositView,
    Observation,
    OtherShipView,
    OwnShipView,
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


def vue(entite: Any, type_vue: type[Any], detient: bool) -> Any:
    """Construit une vue en ne copiant que les champs visibles.

    Un champ invisible pour l'acteur lève une erreur."""
    visibles = classes(type(entite))
    valeurs: dict[str, Any] = {}
    for champ in msgspec.structs.fields(type_vue):
        classe = visibles[champ.name]
        if classe is not Visibility.PUBLIC and not (classe is Visibility.PRIVATE and detient):
            raise ValueError(f"champ {champ.name} invisible pour cet acteur")
        valeurs[champ.name] = getattr(entite, champ.name)
    return type_vue(**valeurs)


def _solde(ledger: Ledger, actor_id: int) -> int:
    for c in ledger.accounts:
        if c.kind is AccountKind.PERSONAL_WALLET and c.owner_id == actor_id:
            return c.balance
    return 0


def observe(state: State, actor_id: int) -> Observation:
    acteur = next((a for a in state.actors if a.id == actor_id), None)
    evenements = tuple(
        e
        for e in state.last_tick.events
        if e.visibility is Visibility.PUBLIC
        or (e.visibility is Visibility.PRIVATE and e.actor_id == actor_id)
    )
    return Observation(
        tick=state.tick,
        actor_id=actor_id,
        systems=tuple(vue(s, SystemView, False) for s in state.systems),
        deposits=tuple(vue(d, DepositView, False) for d in state.deposits),
        stations=tuple(vue(s, StationView, False) for s in state.stations),
        actors=tuple(vue(a, ActorView, False) for a in state.actors),
        own_ships=tuple(vue(v, OwnShipView, True) for v in state.ships if v.owner_id == actor_id),
        other_ships=tuple(
            vue(v, OtherShipView, False) for v in state.ships if v.owner_id != actor_id
        ),
        wallet_balance=_solde(state.ledger, actor_id),
        action_budget=acteur.action_budget if acteur is not None else 0,
        events=evenements,
        results=tuple(r for r in state.last_tick.results if r.recipient_actor_id == actor_id),
    )
