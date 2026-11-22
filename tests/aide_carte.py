"""Vérification de la carte d'un monde généré (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 7 ter, disposition de la carte) : utilisée sur 50 graines (marque `proprietes`) et sur les
graines 1 à 2 000 (marque `lent`).

Les systèmes passent par `observe(generate(graine, réglages), 1, réglages).systems`. Pour dessiner
la ligne des vaisseaux, l'observation reçoit, par `msgspec.structs.replace`, un vaisseau du joueur
et deux autres vaisseaux dans chaque système (« ▲2 »), et le modèle la reçoit par `on_update`.
"""

import msgspec

from fourx.clients.force_layout import force_layout, recouvrement
from fourx.clients.map_view import VIDE, View, anchor, render
from fourx.clients.model import ClientModel
from fourx.core import world
from fourx.core.observe import observe
from fourx.schema.actors import Activity
from fourx.schema.observation import Observation, OtherShipView, OwnShipView
from fourx.schema.protocol import PROTOCOL_VERSION, TickUpdate
from fourx.server.tunables_loader import load_tunables

TAILLES = ((72, 27), (52, 21))


def observation_chargee(graine: int) -> Observation:
    reglages = load_tunables()
    obs = observe(world.generate(graine, reglages), 1, reglages)
    depart = obs.systems[0].id
    joueur = OwnShipView(
        id=1,
        owner_id=obs.actor_id,
        system_id=depart,
        capacity=100,
        activity=Activity.IDLE,
        route=(),
        ticks_to_next_jump=0,
        cargo=(0, 0),
        mining_ore_id=None,
        mined_since_start=0,
    )
    autres = tuple(
        OtherShipView(id=100 + 2 * rang + k, owner_id=99, system_id=s.id, capacity=100)
        for rang, s in enumerate(obs.systems)
        for k in range(2)
    )
    return msgspec.structs.replace(obs, own_ships=(joueur,), other_ships=autres)


def empreintes(
    vue: View, positions: dict[int, tuple[float, float]], obs: Observation
) -> dict[int, set[tuple[int, int]]]:
    """Les cases que chaque système occupe au zoom 1 : pastille, gisement, ligne des vaisseaux."""
    joueur = obs.own_ships[0].system_id
    cases: dict[int, set[tuple[int, int]]] = {}
    for s in obs.systems:
        colonne, ligne = anchor(vue, positions[s.id])
        siennes = {(colonne, ligne), (colonne + 1, ligne)}
        gisements = [d for d in obs.deposits if d.system_id == s.id]
        for rang in range(len(gisements)):
            siennes |= {(colonne + 2 + 2 * rang, ligne), (colonne + 3 + 2 * rang, ligne)}
        debut = colonne
        if s.id == joueur:
            siennes.add((colonne, ligne - 1))
            debut += 1
        siennes |= {(debut, ligne - 1), (debut + 1, ligne - 1)}  # « ▲2 »
        cases[s.id] = siennes
    return cases


def verifier_carte(graine: int) -> None:
    obs = observation_chargee(graine)
    positions = force_layout(obs.systems)
    assert positions == force_layout(obs.systems)
    assert sorted(positions) == sorted(s.id for s in obs.systems)
    idents = sorted(positions)
    for rang, a in enumerate(idents):
        assert 0 <= positions[a][0] <= 1 and 0 <= positions[a][1] <= 1
        for b in idents[rang + 1 :]:
            assert not recouvrement(positions[a], positions[b]), (graine, a, b)
    modele = ClientModel(obs.actor_id)
    modele.on_update(TickUpdate(protocol_version=PROTOCOL_VERSION, observation=obs))
    for largeur, hauteur in TAILLES:
        vue = View(0, (0.5, 0.5), largeur, hauteur)
        grille = render(vue, positions, modele, None)
        cases = empreintes(vue, positions, obs)
        for ident, siennes in cases.items():
            for colonne, ligne in siennes:
                assert 0 <= colonne < largeur and 0 <= ligne < hauteur, (graine, largeur, ident)
                assert grille[ligne][colonne] != VIDE, (graine, largeur, ident, colonne, ligne)
        for rang, a in enumerate(idents):
            for b in idents[rang + 1 :]:
                ecart = min(
                    max(abs(ca - cb), abs(la - lb)) for ca, la in cases[a] for cb, lb in cases[b]
                )
                # Ni case commune (écart 0), ni cases voisines (écart 1).
                assert ecart >= 2, (graine, largeur, a, b)
