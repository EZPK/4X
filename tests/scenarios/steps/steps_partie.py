"""Définitions d'étapes du volet B de M1.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 20 ; interfaces du Technical
Plan, point 13 ; mode sans horloge du Technical Plan, point 6.

Chemin protégé. Les étapes sont écrites avant le code : elles n'importent le code de `fourx`
qu'à l'intérieur des fonctions, par `importlib`. Elles passent par le serveur en mémoire
(`Game`, mode sans horloge) et le protocole : les ordres partent par un point de connexion
(`Game.connect(...).submit`) et entrent au tick suivant ; les mises à jour du tick sont reçues
par un client synchrone attaché (`Game.attach`), qui ne renvoie aucun ordre. Le journal des
événements est lu dans le fichier `events.jsonl` du dossier de la partie.

Conventions que ces étapes figent :
- `Game(runs_dir, world_seed, tunables)` crée le dossier de la partie sous `runs_dir` ;
- `create_character(kind)` renvoie l'identifiant du nouvel acteur, créé au tick suivant ;
- `attach(actor_id, client)` peut être appelé avant le tick où l'acteur est créé ; le client
  synchrone attaché reçoit alors chaque mise à jour du tick de cet acteur, dans l'ordre des ticks ;
- une seule connexion par acteur (`connect`), qui peut coexister avec un client attaché pour le
  même acteur ;
- en mode sans horloge, `advance` prend aussi, au début de chaque tick, les ordres soumis par les
  connexions depuis le tick précédent, comme l'horloge ;
- chaque ligne de `events.jsonl` est l'encodage JSON msgspec d'un `Event`, et le fichier est à
  jour quand `advance` rend la main ;
- `NpcHost(actor_id, policy)` reçoit la fonction de décision de la politique
  (`scripted_miner.decide`).
"""

import importlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import msgspec
import pytest
from pytest_bdd import given, parsers, then, when

PROTOCOLE = 1


def importer(nom: str) -> Any:
    """Importe un module du jeu au moment de l'appel."""
    return importlib.import_module(nom)


def systeme(libelle: str) -> int:
    trouve = re.fullmatch(r"system_(\d+)", libelle)
    assert trouve is not None, libelle
    return int(trouve.group(1))


def rang_minerai(libelle: str) -> int:
    trouve = re.fullmatch(r"ore_([a-z])", libelle)
    assert trouve is not None, libelle
    return ord(trouve.group(1)) - ord("a") + 1


class Enregistreur:
    """Client synchrone qui garde chaque mise à jour du tick et ne renvoie aucun ordre."""

    def __init__(self) -> None:
        self.mises_a_jour: list[Any] = []

    def on_update(self, update: Any) -> Any:
        self.mises_a_jour.append(update)
        return None


@dataclass
class Serveur:
    dossier: Path
    jeu: Any = None
    acteurs: dict[str, int] = field(default_factory=dict)
    enregistreurs: dict[str, Enregistreur] = field(default_factory=dict)
    connexions: dict[str, Any] = field(default_factory=dict)
    numeros: dict[str, int] = field(default_factory=dict)
    soumis: dict[str, list[int]] = field(default_factory=dict)

    def creer(self, nom: str, kind: str) -> int:
        actors = importer("fourx.schema.actors")
        ident = int(self.jeu.create_character(actors.ActorKind[kind]))
        self.acteurs[nom] = ident
        return ident

    def ecouter(self, nom: str) -> None:
        enregistreur = Enregistreur()
        self.jeu.attach(self.acteurs[nom], enregistreur)
        self.enregistreurs[nom] = enregistreur
        self.connexions[nom] = self.jeu.connect(self.acteurs[nom])

    def derniere(self, nom: str) -> Any:
        mises_a_jour = self.enregistreurs[nom].mises_a_jour
        assert mises_a_jour, f"aucune mise à jour reçue par {nom}"
        return mises_a_jour[-1].observation

    def vaisseau(self, nom: str) -> Any:
        propres = self.derniere(nom).own_ships
        assert len(propres) == 1, propres
        return propres[0]

    def soumettre(self, nom: str, ordres: list[Any]) -> None:
        protocol = importer("fourx.schema.protocol")
        self.connexions[nom].submit(
            protocol.SubmitOrders(protocol_version=PROTOCOLE, orders=tuple(ordres))
        )

    def ordre(
        self,
        nom: str,
        commande: Any,
        actor_id: int | None = None,
        categorie: str = "PLAYER",
        num: int | None = None,
    ) -> Any:
        orders = importer("fourx.schema.orders")
        if num is None:
            num = self.numeros.get(nom, 0) + 1
        self.numeros[nom] = num
        self.soumis.setdefault(nom, []).append(num)
        return orders.Order(
            actor_id=self.acteurs[nom] if actor_id is None else actor_id,
            number=num,
            category=orders.OrderCategory[categorie],
            policy_id=None,
            policy_version=None,
            command=commande,
        )

    def evenements(self) -> list[Any]:
        events = importer("fourx.schema.events")
        fichiers = sorted(self.dossier.glob("*/events.jsonl"))
        assert len(fichiers) == 1, fichiers
        decodeur = msgspec.json.Decoder(events.Event)
        lignes = fichiers[0].read_text(encoding="utf-8").splitlines()
        return [decodeur.decode(ligne) for ligne in lignes if ligne.strip()]


@pytest.fixture
def serveur(tmp_path: Path) -> Serveur:
    return Serveur(dossier=tmp_path / "runs")


# --- Étant donné


@given("une partie du serveur en mémoire, graine 1, avec les réglages de M1, sans horloge")
def partie_serveur(serveur: Serveur) -> None:
    game = importer("fourx.server.game")
    tunables_loader = importer("fourx.server.tunables_loader")
    serveur.dossier.mkdir(parents=True, exist_ok=True)
    serveur.jeu = game.Game(serveur.dossier, 1, tunables_loader.load_tunables())


@given("le propriétaire et un autre acteur, chacun avec son vaisseau")
def proprietaire_et_autre(serveur: Serveur) -> None:
    serveur.creer("propriétaire", "HUMAN")
    serveur.creer("autre", "HUMAN")
    serveur.ecouter("propriétaire")
    serveur.ecouter("autre")


@given("un PNJ joué par l'hôte des PNJ avec la politique scripted_miner")
def pnj(serveur: Serveur) -> None:
    npc_host = importer("fourx.clients.npc_host")
    scripted_miner = importer("fourx.policies.scripted_miner")
    ident = serveur.creer("PNJ", "NPC")
    serveur.jeu.attach(ident, npc_host.NpcHost(ident, scripted_miner.decide))


# --- Quand


@when(parsers.re(r"le serveur joue (?P<n>\d+) ticks?"))
def serveur_joue(serveur: Serveur, n: str) -> None:
    serveur.jeu.advance(int(n))


@when(parsers.re(r"le propriétaire envoie son vaisseau vers (?P<cible>system_\d+)"))
def envoyer(serveur: Serveur, cible: str) -> None:
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    commande = orders.Move(ship_id=navire.id, target_system_id=systeme(cible))
    serveur.soumettre("propriétaire", [serveur.ordre("propriétaire", commande)])


@when(parsers.re(r"le propriétaire ordonne à son vaisseau de miner (?P<ore>ore_[a-z])"))
def miner(serveur: Serveur, ore: str) -> None:
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    commande = orders.Mine(ship_id=navire.id, ore_id=rang_minerai(ore))
    serveur.soumettre("propriétaire", [serveur.ordre("propriétaire", commande)])


@when(
    parsers.re(
        r"le propriétaire ordonne à son vaisseau de vendre (?P<q>\d+) unités de (?P<ore>ore_[a-z])"
    )
)
def vendre(serveur: Serveur, q: str, ore: str) -> None:
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    commande = orders.Sell(ship_id=navire.id, ore_id=rang_minerai(ore), quantity=int(q))
    serveur.soumettre("propriétaire", [serveur.ordre("propriétaire", commande)])


@when(
    parsers.re(
        r"le propriétaire soumet, au nom de l'autre acteur, l'ordre de miner (?P<ore>ore_[a-z])"
    )
)
def au_nom_d_un_autre(serveur: Serveur, ore: str) -> None:
    orders = importer("fourx.schema.orders")
    autre = serveur.vaisseau("autre")
    commande = orders.Mine(ship_id=autre.id, ore_id=rang_minerai(ore))
    ordre = serveur.ordre("propriétaire", commande, actor_id=serveur.acteurs["autre"])
    serveur.soumettre("propriétaire", [ordre])


@when(
    parsers.re(
        r"le propriétaire soumet, en son propre nom, un ordre d'administration d'aller dans "
        r"(?P<cible>system_\d+)"
    )
)
def ordre_d_administration(serveur: Serveur, cible: str) -> None:
    """Un déplacement de catégorie « administration » : `step` l'accepterait s'il passait,
    seule la réception peut le refuser."""
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    commande = orders.Move(ship_id=navire.id, target_system_id=systeme(cible))
    serveur.soumettre("propriétaire", [serveur.ordre("propriétaire", commande, categorie="ADMIN")])


@when(
    parsers.re(
        r"le propriétaire soumet dans le même tick (?P<n>\d+) ordres d'aller dans "
        r"(?P<cible>system_\d+), numérotés de 1 à (?P<dernier>\d+)"
    )
)
def plusieurs_ordres(serveur: Serveur, n: str, cible: str, dernier: str) -> None:
    orders = importer("fourx.schema.orders")
    assert int(n) == int(dernier)
    navire = serveur.vaisseau("propriétaire")
    commande = orders.Move(ship_id=navire.id, target_system_id=systeme(cible))
    # Envoyés du plus grand au plus petit numéro : la réception doit garder les plus petits
    # numéros, pas les premiers arrivés.
    ordres = [serveur.ordre("propriétaire", commande, num=k) for k in range(int(n), 0, -1)]
    serveur.soumettre("propriétaire", ordres)


# --- Alors


@then(
    parsers.re(
        r"la dernière mise à jour du propriétaire montre son vaisseau dans (?P<lieu>system_\d+)"
    )
)
def mise_a_jour_lieu(serveur: Serveur, lieu: str) -> None:
    assert serveur.vaisseau("propriétaire").system_id == systeme(lieu)


@then(
    parsers.re(
        r"la dernière mise à jour du propriétaire montre son vaisseau dans (?P<lieu>system_\d+), "
        r"(?P<activite>en route|à l'arrêt)"
    )
)
def mise_a_jour_lieu_et_activite(serveur: Serveur, lieu: str, activite: str) -> None:
    actors = importer("fourx.schema.actors")
    navire = serveur.vaisseau("propriétaire")
    attendue = actors.Activity.EN_ROUTE if activite == "en route" else actors.Activity.IDLE
    assert (navire.system_id, navire.activity) == (systeme(lieu), attendue)


@then(
    parsers.re(
        r"la dernière mise à jour du propriétaire montre (?P<q>\d+) unités de "
        r"(?P<ore>ore_[a-z]) en cargaison"
    )
)
def mise_a_jour_cargaison(serveur: Serveur, q: str, ore: str) -> None:
    assert serveur.vaisseau("propriétaire").cargo[rang_minerai(ore) - 1] == int(q)


@then(
    parsers.re(
        r"la dernière mise à jour du propriétaire montre une vente de (?P<q>\d+) unités de "
        r"(?P<ore>ore_[a-z]), payée (?P<paiement>\d+) et taxée (?P<taxe>\d+)"
    )
)
def mise_a_jour_vente(serveur: Serveur, q: str, ore: str, paiement: str, taxe: str) -> None:
    events = importer("fourx.schema.events")
    ventes = [
        e.payload
        for e in serveur.derniere("propriétaire").events
        if isinstance(e.payload, events.Sale)
    ]
    assert len(ventes) == 1, ventes
    vente = ventes[0]
    assert (vente.quantity, vente.ore_id, vente.payment, vente.tax) == (
        int(q),
        rang_minerai(ore),
        int(paiement),
        int(taxe),
    )


@then(parsers.re(r"la dernière mise à jour du propriétaire montre un portefeuille de (?P<x>\d+)"))
def mise_a_jour_portefeuille(serveur: Serveur, x: str) -> None:
    assert serveur.derniere("propriétaire").wallet_balance == int(x)


@then("aucune mise à jour de l'autre acteur ne montre la vente du propriétaire")
def autre_ne_voit_pas(serveur: Serveur) -> None:
    events = importer("fourx.schema.events")
    visibility = importer("fourx.schema.visibility")
    proprietaire = serveur.acteurs["propriétaire"]
    ticks_autre = [m.observation.tick for m in serveur.enregistreurs["autre"].mises_a_jour]
    ticks_proprietaire = [
        m.observation.tick for m in serveur.enregistreurs["propriétaire"].mises_a_jour
    ]
    assert ticks_autre == ticks_proprietaire and ticks_autre, (ticks_autre, ticks_proprietaire)
    for maj in serveur.enregistreurs["autre"].mises_a_jour:
        for e in maj.observation.events:
            assert not isinstance(e.payload, (events.Sale, events.LedgerEntryRecorded))
            assert not (
                e.actor_id == proprietaire and e.visibility is visibility.Visibility.PRIVATE
            )


@then(
    parsers.re(
        r"le journal des événements contient une écriture de vente de (?P<vente>\d+) "
        r"et une écriture de taxe de (?P<taxe>\d+)"
    )
)
def journal_ecritures(serveur: Serveur, vente: str, taxe: str) -> None:
    events = importer("fourx.schema.events")
    raison = importer("fourx.schema.ledger").Reason
    ecritures = [
        e.payload.entry
        for e in serveur.evenements()
        if isinstance(e.payload, events.LedgerEntryRecorded)
    ]
    assert any(e.reason == raison.ORE_SALE and e.amount == int(vente) for e in ecritures)
    assert any(e.reason == raison.SALE_TAX and e.amount == int(taxe) for e in ecritures)


def resultats(serveur: Serveur, nom: str) -> list[Any]:
    return list(serveur.derniere(nom).results)


@then(
    parsers.re(
        r"la dernière mise à jour du propriétaire montre son ordre refusé avec le code "
        r"(?P<code>[A-Z_]+)"
    )
)
def ordre_refuse_a_la_reception(serveur: Serveur, code: str) -> None:
    refusal = importer("fourx.schema.results").RefusalCode
    numero = serveur.soumis["propriétaire"][-1]
    trouves = [r for r in resultats(serveur, "propriétaire") if r.order_id.number == numero]
    assert len(trouves) == 1, trouves
    assert not trouves[0].accepted
    assert trouves[0].refusal == refusal[code]


@then(
    parsers.re(
        r"les ordres (?P<a>\d+) et (?P<b>\d+) du propriétaire sont refusés avec le code "
        r"(?P<code>[A-Z_]+)"
    )
)
def ordres_refuses(serveur: Serveur, a: str, b: str, code: str) -> None:
    refusal = importer("fourx.schema.results").RefusalCode
    par_numero = {r.order_id.number: r for r in resultats(serveur, "propriétaire")}
    for numero in (int(a), int(b)):
        assert par_numero[numero].refusal == refusal[code]


@then(
    parsers.re(
        r"aucun des ordres (?P<a>\d+) à (?P<b>\d+) du propriétaire n'est refusé avec le code "
        r"(?P<code>[A-Z_]+)"
    )
)
def ordres_non_refuses(serveur: Serveur, a: str, b: str, code: str) -> None:
    refusal = importer("fourx.schema.results").RefusalCode
    par_numero = {r.order_id.number: r for r in resultats(serveur, "propriétaire")}
    for numero in range(int(a), int(b) + 1):
        assert par_numero[numero].refusal != refusal[code]


@then("le journal des événements contient au moins une vente du PNJ")
def vente_du_pnj(serveur: Serveur) -> None:
    events = importer("fourx.schema.events")
    pnj = serveur.acteurs["PNJ"]
    assert any(
        isinstance(e.payload, events.Sale) and e.actor_id == pnj for e in serveur.evenements()
    )
