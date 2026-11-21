"""Définitions d'étapes de l'écran unique (amendement 1 de M1).

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 23 ter ; Technical Plan,
point 7 bis (modèle client, mise en page de la carte, refus en français, alertes, durées) et
point 13 (interfaces de `clients/model.py`, `clients/map_layout.py`, `clients/texts.py`).

Chemin protégé. Les étapes sont écrites avant le code : elles n'importent le code de `fourx`
qu'à l'intérieur des fonctions. Elles réutilisent le serveur en mémoire et les étapes de
`steps_partie.py` : quand le propriétaire est joué par le modèle client, ses ordres partent par
`ClientModel.send` et `ClientModel.sell_all`, et ses observations sont lues dans
`ClientModel.observation`.

Conventions que ces étapes figent :
- `ClientModel(actor_id)` est attaché au serveur par `Game.attach`, comme client synchrone ; le
  message que rend `on_update` (la vente suivante de la file) entre au tick suivant ;
- `send(command)` et `sell_all()` rendent le message `SubmitOrders` à soumettre par la connexion
  de l'acteur ; le modèle numérote les ordres ;
- `remaining_ticks()` est le nombre de ticks que le serveur joue, après la mise à jour courante,
  jusqu'à l'arrivée ou jusqu'à la cargaison pleine ;
- `refusal_text(result, command, observation)` rend le texte du Technical Plan, point 7 bis
  (« 1 saut », « n sauts ») ; pour un refus qui nomme un gisement, le lieu nommé est son système
  et, à distance égale, c'est le système de plus petit identifiant ; l'historique du modèle
  contient ce texte ;
- `Alert.text` vaut « arrivée : system_k » ou « fin de minage : ore_x q/capacité » ;
- `layout(observation)` suit la « sortie de `layout` » du Technical Plan, point 7 bis ; la ligne
  « liens : » peut être coupée n'importe où, et ses suites sont lues bout à bout ;
- le refus sur un gisement vide se joue sur les réglages de test « aux gisements vides »
  (`deposit_stock` = 0), faute de pouvoir vider un gisement de 20 000 unités dans un scénario.
"""

import re
from typing import Any

from pytest_bdd import given, parsers, then, when

from tests.scenarios.steps.steps_partie import LIMITE_DE_TICKS, Serveur, importer, plus_proche


def libelle_minerai(ore_id: int) -> str:
    return "ore_" + chr(ord("a") + ore_id - 1)


def sauts(n: int) -> str:
    return f"{n} saut" if n == 1 else f"{n} sauts"


def jouer_et_compter(serveur: Serveur, condition: Any) -> int:
    """Joue tick par tick jusqu'à la condition ; rend le nombre de ticks joués."""
    joues = 0
    while not condition():
        serveur.jeu.advance(1)
        joues += 1
        assert joues <= LIMITE_DE_TICKS, "condition non atteinte"
    return joues


# --- Étant donné


@given("le propriétaire joué par le modèle client")
def proprietaire_modele(serveur: Serveur) -> None:
    model = importer("fourx.clients.model")
    ident = serveur.creer("propriétaire", "HUMAN")
    modele = model.ClientModel(ident)
    serveur.jeu.attach(ident, modele)
    serveur.modeles["propriétaire"] = modele
    serveur.connexions["propriétaire"] = serveur.jeu.connect(ident)


# --- Quand


@when(
    "le propriétaire ordonne à son vaisseau de miner un minerai "
    "qui n'a pas de gisement dans son système"
)
def miner_sans_gisement(serveur: Serveur) -> None:
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    observation = serveur.derniere("propriétaire")
    ici = {d.ore_id for d in observation.deposits if d.system_id == navire.system_id}
    ore_id = min({1, 2} - ici)
    serveur.envoyer("propriétaire", orders.Mine(ship_id=navire.id, ore_id=ore_id))


@when("le propriétaire vend toute sa cargaison par le modèle client")
def vendre_par_le_modele(serveur: Serveur) -> None:
    message = serveur.modeles["propriétaire"].sell_all()
    assert message is not None, "aucune vente mise en file"
    serveur.connexions["propriétaire"].submit(message)


# --- Alors


def refus_traduit(serveur: Serveur, code: str) -> str:
    texts = importer("fourx.clients.texts")
    refusal = importer("fourx.schema.results").RefusalCode
    observation = serveur.derniere("propriétaire")
    ordre = serveur.derniers_ordres["propriétaire"]
    trouves = [r for r in observation.results if r.order_id.number == ordre.number]
    assert len(trouves) == 1, trouves
    assert not trouves[0].accepted and trouves[0].refusal == refusal[code], trouves[0]
    serveur.refus = str(texts.refusal_text(trouves[0], ordre.command, observation))
    return serveur.refus


@then(
    "le refus traduit dit qu'il n'y a pas de gisement de ce minerai ici, "
    "et nomme le système du plus proche avec sa distance en sauts"
)
def refus_sans_gisement(serveur: Serveur) -> None:
    ore_id = serveur.derniers_ordres["propriétaire"].command.ore_id
    dist = serveur.dist("propriétaire")
    observation = serveur.derniere("propriétaire")
    systemes = [d.system_id for d in observation.deposits if d.ore_id == ore_id]
    cible = plus_proche(dist, systemes)
    attendu = (
        f"pas de gisement de {libelle_minerai(ore_id)} ici ; le plus proche est dans "
        f"system_{cible} ({sauts(dist[cible])})"
    )
    assert refus_traduit(serveur, "NO_DEPOSIT_FOR_ORE") == attendu


@then(
    "le refus traduit dit que le gisement est vide, "
    "et nomme le plus proche gisement du même minerai qui n'est pas connu comme vide"
)
def refus_gisement_vide(serveur: Serveur) -> None:
    observation = serveur.derniere("propriétaire")
    navire = serveur.vaisseau("propriétaire")
    ici = next(d for d in observation.deposits if d.system_id == navire.system_id)
    candidats = [
        d.system_id
        for d in observation.deposits
        if d.ore_id == ici.ore_id and d.id != ici.id and (d.stock is None or d.stock > 0)
    ]
    assert candidats, "aucun gisement du même minerai hors de portée : la graine ne convient pas"
    dist = serveur.dist("propriétaire")
    cible = plus_proche(dist, candidats)
    attendu = (
        f"gisement vide ; le plus proche gisement de {libelle_minerai(ici.ore_id)} qui n'est pas "
        f"connu comme vide est dans system_{cible} ({sauts(dist[cible])})"
    )
    assert refus_traduit(serveur, "DEPOSIT_EMPTY") == attendu


@then("l'historique du modèle client contient ce refus traduit")
def historique_refus(serveur: Serveur) -> None:
    assert serveur.refus
    assert any(serveur.refus in ligne for ligne in serveur.modeles["propriétaire"].history)


@then(
    parsers.re(
        r"les ticks restants annoncés par le modèle client sont ceux que le serveur joue ensuite "
        r"jusqu'(?P<fin>à l'arrivée|à la cargaison pleine)"
    )
)
def ticks_restants(serveur: Serveur, fin: str) -> None:
    actors = importer("fourx.schema.actors")
    annonces = serveur.modeles["propriétaire"].remaining_ticks()
    assert annonces is not None and annonces > 0, annonces
    if fin == "à l'arrivée":
        cible = serveur.cibles["propriétaire"]

        def atteint() -> bool:
            navire = serveur.vaisseau("propriétaire")
            return bool(navire.system_id == cible and navire.activity == actors.Activity.IDLE)

    else:

        def atteint() -> bool:
            navire = serveur.vaisseau("propriétaire")
            return bool(sum(navire.cargo) >= navire.capacity)

    assert jouer_et_compter(serveur, atteint) == annonces


@then(
    "le journal des événements montre deux ventes du propriétaire, d'un minerai chacune, "
    "sur deux ticks qui se suivent, la plus grosse d'abord"
)
def deux_ventes(serveur: Serveur) -> None:
    events = importer("fourx.schema.events")
    proprietaire = serveur.acteurs["propriétaire"]
    ventes = [
        e
        for e in serveur.evenements()
        if isinstance(e.payload, events.Sale) and e.actor_id == proprietaire
    ]
    assert len(ventes) == 2, ventes
    premiere, seconde = ventes
    assert seconde.tick == premiere.tick + 1, (premiere.tick, seconde.tick)
    assert premiere.payload.ore_id != seconde.payload.ore_id
    assert premiere.payload.quantity >= seconde.payload.quantity > 0


def alertes(serveur: Serveur, genre: str) -> list[Any]:
    model = importer("fourx.clients.model")
    modele = serveur.modeles["propriétaire"]
    return [a for a in modele.alerts if a.kind == model.AlertKind[genre]]


@then(
    "le modèle client a une seule alerte d'arrivée, levée au tick de l'arrivée, "
    "qui nomme le système atteint"
)
def alerte_arrivee(serveur: Serveur) -> None:
    trouvees = alertes(serveur, "ARRIVED")
    assert len(trouvees) == 1, trouvees
    cible = serveur.cibles["propriétaire"]
    attendu = (serveur.fin["propriétaire"], f"arrivée : system_{cible}")
    assert (trouvees[0].tick, trouvees[0].text) == attendu


@then(
    "le modèle client a une seule alerte de fin de minage, "
    "qui donne le minerai et la cargaison pleine"
)
def alerte_fin_de_minage(serveur: Serveur) -> None:
    trouvees = alertes(serveur, "MINING_ENDED")
    assert len(trouvees) == 1, trouvees
    navire = serveur.vaisseau("propriétaire")
    ore_id = next(rang + 1 for rang, q in enumerate(navire.cargo) if q > 0)
    attendu = f"fin de minage : {libelle_minerai(ore_id)} {navire.capacity}/{navire.capacity}"
    assert trouvees[0].text == attendu


@then("le modèle client n'a aucune alerte de fin de minage")
def aucune_alerte_de_minage(serveur: Serveur) -> None:
    events = importer("fourx.schema.events")
    navire = serveur.vaisseau("propriétaire")
    interrompus = [
        e
        for e in serveur.evenements()
        if isinstance(e.payload, events.MiningEnded)
        and e.payload.ship_id == navire.id
        and e.causation_id is not None
    ]
    assert interrompus, "aucun minage interrompu par un ordre : le scénario ne vérifie rien"
    assert alertes(serveur, "MINING_ENDED") == []


@then(
    "la carte du modèle client contient chaque système une fois, "
    "et chaque lien une fois, tracé ou écrit"
)
def carte_complete(serveur: Serveur) -> None:
    map_layout = importer("fourx.clients.map_layout")
    observation = serveur.derniere("propriétaire")
    lignes = list(map_layout.layout(observation))
    debut_liens = next(
        (i for i, ligne in enumerate(lignes) if ligne.startswith("liens : ")), len(lignes)
    )
    cases: list[int] = []
    traces: list[tuple[int, int]] = []
    for ligne in lignes[:debut_liens]:
        trouves = list(re.finditer(r"\[(\d+)\][^\[]*", ligne))
        cases += [int(t.group(1)) for t in trouves]
        for gauche, droite in zip(trouves, trouves[1:], strict=False):
            if gauche.group(0).endswith("─") and gauche.end() == droite.start():
                a, b = int(gauche.group(1)), int(droite.group(1))
                traces.append((min(a, b), max(a, b)))
    texte_liens = "".join(ligne.strip() for ligne in lignes[debut_liens:])[len("liens :") :]
    ecrits = [
        (min(int(a), int(b)), max(int(a), int(b)))
        for a, b in re.findall(r"(\d+)–(\d+)", texte_liens)
    ]
    attendus = {(min(s.id, v), max(s.id, v)) for s in observation.systems for v in s.neighbors}
    assert len(observation.systems) == 12, len(observation.systems)
    assert sorted(cases) == sorted(s.id for s in observation.systems), cases
    tous = traces + ecrits
    assert len(tous) == len(set(tous)), tous
    assert set(tous) == attendus, (sorted(set(tous) ^ attendus), traces, ecrits)
