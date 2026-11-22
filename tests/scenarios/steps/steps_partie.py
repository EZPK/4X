"""Définitions d'étapes du volet B de M1, réécrites par l'amendement 1.

Document : docs/designs/niveau-2-m1-noyau.md, plan détaillé, points 20 et 23 ter ; interfaces du
Technical Plan, point 13 ; mode sans horloge du Technical Plan, point 6 ; génération du monde du
Technical Plan, point 2.

Chemin protégé. Les étapes sont écrites avant le code : elles n'importent le code de `fourx`
qu'à l'intérieur des fonctions, par `importlib`. Elles passent par le serveur en mémoire
(`Game`, mode sans horloge) et le protocole : les ordres partent par un point de connexion
(`Game.connect(...).submit`) et entrent au tick suivant ; les mises à jour du tick sont reçues
par un client synchrone attaché (`Game.attach`), qui ne renvoie aucun ordre. Le journal des
événements est lu dans le fichier `events.jsonl` du dossier de la partie.

Elles ne supposent pas la carte : elles lisent la géométrie dans l'observation (distances en sauts
par un parcours en largeur sur les voisins, par identifiant croissant ; à distance égale, le plus
petit identifiant de système).

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
  (`scripted_miner.decide`) ;
- réglages de test : ceux de `tunables.toml` (`load_tunables`), sauf `jump_ticks` = 5 et
  `mining_rate` = 10 ; une graine « première dont … » est la plus petite, de 1 à 1000, dont
  `world.generate(graine, réglages)` donne le monde demandé ; la condition du cycle (gisement
  conseillé) se calcule sur l'état généré et les réglages, sans le code testé ;
- un trajet de d sauts accepté au tick T arrive au tick T + d × `jump_ticks` − 1 ; un minage
  accepté au tick T extrait dès ce tick (Technical Plan, point 7 bis, durées affichées).
"""

import importlib
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any

import msgspec
import pytest
from pytest_bdd import given, parsers, then, when

LIMITE_DE_TICKS = 20_000
LIMITE_DE_GRAINES = 1000


def importer(nom: str) -> Any:
    """Importe un module du jeu au moment de l'appel."""
    return importlib.import_module(nom)


def rang_minerai(libelle: str) -> int:
    """ore_a → 1, ore_b → 2."""
    assert libelle.startswith("ore_") and len(libelle) == 5, libelle
    return ord(libelle[4]) - ord("a") + 1


def distances(systemes: Any, depart: int) -> dict[int, int]:
    """Distances en sauts depuis `depart`, sur des systèmes qui portent `id` et `neighbors`."""
    voisins = {s.id: sorted(s.neighbors) for s in systemes}
    resultat = {depart: 0}
    file = [depart]
    while file:
        courant = file.pop(0)
        for v in voisins[courant]:
            if v not in resultat:
                resultat[v] = resultat[courant] + 1
                file.append(v)
    return resultat


def plus_proche(dist: dict[int, int], systemes: list[int]) -> int:
    """Le système le plus proche, à distance égale le plus petit identifiant."""
    accessibles = [s for s in systemes if s in dist]
    assert accessibles, systemes
    return min(accessibles, key=lambda s: (dist[s], s))


def taxe(montant: int, tax_rate_bp: int) -> int:
    """Taxe arrondie vers le haut (Technical Plan, point 3)."""
    return -(-montant * tax_rate_bp // 10_000)


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
    graine: int = 1
    tunables: Any = None
    acteurs: dict[str, int] = field(default_factory=dict)
    enregistreurs: dict[str, Enregistreur] = field(default_factory=dict)
    modeles: dict[str, Any] = field(default_factory=dict)
    connexions: dict[str, Any] = field(default_factory=dict)
    numeros: dict[str, int] = field(default_factory=dict)
    soumis: dict[str, list[int]] = field(default_factory=dict)
    cibles: dict[str, int] = field(default_factory=dict)
    vente: dict[str, int] = field(default_factory=dict)
    debut: dict[str, int] = field(default_factory=dict)
    fin: dict[str, int] = field(default_factory=dict)
    derniers_ordres: dict[str, Any] = field(default_factory=dict)
    refus: str = ""
    touches: list[tuple[str, ...]] = field(default_factory=list)

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
        if nom in self.modeles:
            observation = self.modeles[nom].observation
            assert observation is not None, f"aucune mise à jour reçue par le modèle de {nom}"
            return observation
        mises_a_jour = self.enregistreurs[nom].mises_a_jour
        assert mises_a_jour, f"aucune mise à jour reçue par {nom}"
        return mises_a_jour[-1].observation

    def vaisseau(self, nom: str) -> Any:
        propres = self.derniere(nom).own_ships
        assert len(propres) == 1, propres
        return propres[0]

    def dist(self, nom: str) -> dict[int, int]:
        return distances(self.derniere(nom).systems, self.vaisseau(nom).system_id)

    def soumettre(self, nom: str, ordres: list[Any]) -> None:
        protocol = importer("fourx.schema.protocol")
        self.connexions[nom].submit(
            protocol.SubmitOrders(protocol_version=protocol.PROTOCOL_VERSION, orders=tuple(ordres))
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

    def envoyer(self, nom: str, commande: Any) -> None:
        """Envoie une commande au nom de `nom` : par son modèle client s'il en a un."""
        if nom in self.modeles:
            message = self.modeles[nom].send(commande)
            self.derniers_ordres[nom] = message.orders[0]
            self.connexions[nom].submit(message)
        else:
            ordre = self.ordre(nom, commande)
            self.derniers_ordres[nom] = ordre
            self.soumettre(nom, [ordre])

    def aller(self, nom: str, cible: int) -> None:
        """Retient la destination ; envoie le déplacement si le vaisseau n'y est pas déjà."""
        orders = importer("fourx.schema.orders")
        navire = self.vaisseau(nom)
        self.cibles[nom] = cible
        if navire.system_id != cible:
            self.envoyer(nom, orders.Move(ship_id=navire.id, target_system_id=cible))

    def jouer_jusqua(self, condition: Any) -> None:
        for _ in range(LIMITE_DE_TICKS):
            if condition():
                return
            self.jeu.advance(1)
        raise AssertionError(f"condition non atteinte en {LIMITE_DE_TICKS} ticks")

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


def reglages_de(nom: str) -> Any:
    tunables_loader = importer("fourx.server.tunables_loader")
    reels = tunables_loader.load_tunables()
    if nom == "de tunables.toml":
        return reels
    changements: dict[str, int] = {"jump_ticks": 5, "mining_rate": 10}
    if nom == "de test à 12 systèmes":
        changements |= {"systems_min": 12, "systems_max": 12}
    elif nom == "de test aux gisements vides":
        changements |= {"deposit_stock": 0}
    else:
        assert nom == "de test", nom
    return msgspec.structs.replace(reels, **changements)


def plafond(a: int, b: int) -> int:
    return -(-a // b)


def meilleure_vente(
    etat: Any, depuis: dict[int, int], ore_id: int, quantite: int, jump_ticks: int
) -> tuple[int, int, int]:
    """`best_sale` (Technical Plan, point 7 ter) pour une cargaison d'un seul minerai : la station
    de plus grand V ÷ (t + 1), puis la plus proche, puis le plus petit identifiant ; rend
    (station, V, t). `depuis` : les distances en sauts depuis le système de départ."""
    candidats = [
        (s.id, quantite * s.ore_prices[ore_id - 1], depuis[s.system_id] * jump_ticks)
        for s in etat.stations
        if s.system_id in depuis
    ]
    return min(candidats, key=lambda c: (-Fraction(c[1], c[2] + 1), c[2], c[0]))


def conseil_du_plan(etat: Any, x: int, tunables: Any) -> int:
    """Le gisement conseillé depuis le système x, cargaison vide, selon la formule du plan
    détaillé, point 23 octies : le couple (gisement g, station s) de plus grand G ÷ T, puis de
    plus petit T, puis de plus petit identifiant de gisement, puis de station."""
    cap, saut = tunables.cargo_capacity, tunables.jump_ticks
    depuis_x = distances(etat.systems, x)
    couples = []
    for g in etat.deposits:
        if g.system_id not in depuis_x:
            continue
        depuis_g = distances(etat.systems, g.system_id)
        for s in etat.stations:
            if s.system_id not in depuis_g:
                continue
            gain = cap * s.ore_prices[g.ore_id - 1]
            duree = saut * (depuis_x[g.system_id] + depuis_g[s.system_id]) + plafond(
                cap, tunables.mining_rate
            )
            couples.append((-Fraction(gain, duree), duree, g.id, s.id))
    return int(min(couples)[2])


def conseil_de_la_regle_6(etat: Any, x: int, tunables: Any) -> int:
    """Le gisement conseillé depuis le système x, cargaison vide, selon la règle 6 du Technical
    Plan, point 7 ter : la station de chaque gisement est celle de `best_sale` depuis son système ;
    plus grand G ÷ T, puis plus petit T, puis plus petit identifiant de gisement."""
    cap, saut = tunables.cargo_capacity, tunables.jump_ticks
    depuis_x = distances(etat.systems, x)
    candidats = []
    for g in etat.deposits:
        if g.system_id not in depuis_x:
            continue
        depuis_g = distances(etat.systems, g.system_id)
        _, gain, trajet = meilleure_vente(etat, depuis_g, g.ore_id, cap, saut)
        duree = saut * depuis_x[g.system_id] + plafond(cap, tunables.mining_rate) + trajet
        candidats.append((-Fraction(gain, duree), duree, g.id))
    return int(min(candidats)[2])


def cycle_convient(etat: Any, tunables: Any) -> bool:
    """Condition de graine du scénario du cycle (plan détaillé, point 23 octies). Avec les réglages
    de test, le stock initial de chaque gisement dépasse la capacité et aucun autre vaisseau ne
    mine : la quantité minée est `cargo_capacity` pour tout gisement. Par prudence, la graine doit
    aussi donner le même gisement par la règle 6 telle quelle, depuis les deux systèmes : la
    formule du plan prend la station du meilleur cycle, la règle 6 celle de `best_sale`, et les
    deux peuvent différer."""
    assert all(d.stock >= tunables.cargo_capacity for d in etat.deposits), "stock trop petit"
    depart = next(s for s in etat.stations if s.id == 1).system_id
    g0 = conseil_du_plan(etat, depart, tunables)
    if conseil_de_la_regle_6(etat, depart, tunables) != g0:
        return False
    gisement = next(d for d in etat.deposits if d.id == g0)
    if gisement.system_id in {s.system_id for s in etat.stations}:
        return False
    if not (
        conseil_du_plan(etat, gisement.system_id, tunables) == g0
        and conseil_de_la_regle_6(etat, gisement.system_id, tunables) == g0
    ):
        return False
    # La vente finale (« v ») : la station retenue depuis le gisement l'emporte encore une fois
    # sur place, ce que les prix de tunables.toml donnent, mais que rien d'autre ne vérifie.
    cap, saut = tunables.cargo_capacity, tunables.jump_ticks
    depuis_g0 = distances(etat.systems, gisement.system_id)
    station, _, _ = meilleure_vente(etat, depuis_g0, gisement.ore_id, cap, saut)
    ici = next(s for s in etat.stations if s.id == station).system_id
    depuis_ici = distances(etat.systems, ici)
    return meilleure_vente(etat, depuis_ici, gisement.ore_id, cap, saut)[0] == station


def monde_convient(etat: Any, condition: str, tunables: Any) -> bool:
    if condition == (
        "le gisement conseillé depuis la station 1 n'est pas dans le système d'une station,"
        " et le reste depuis son propre système"
    ):
        return cycle_convient(etat, tunables)
    if condition == "une station et un gisement partagent un système":
        return bool({s.system_id for s in etat.stations} & {d.system_id for d in etat.deposits})
    station_1 = next(s for s in etat.stations if s.id == 1)
    dist = distances(etat.systems, station_1.system_id)
    if condition == "un système est à deux sauts de la station 1":
        return 2 in dist.values()
    if condition == (
        "un système est à deux sauts de la station 1, un gisement à"
        " deux sauts ou plus, et un autre à un saut ou moins"
    ):
        loins = [d for d in etat.deposits if dist[d.system_id] >= 2]
        proches = [d for d in etat.deposits if dist[d.system_id] <= 1]
        return 2 in dist.values() and bool(loins) and bool(proches)
    assert condition == (
        "le gisement le plus proche de la station 1 a un gisement"
        " du même minerai à deux sauts ou plus de lui"
    ), condition
    gisements = [d.system_id for d in etat.deposits]
    proche = plus_proche(dist, gisements)
    vise = next(d for d in etat.deposits if d.system_id == proche)
    depuis = distances(etat.systems, proche)
    return any(
        d.ore_id == vise.ore_id and d.id != vise.id and depuis[d.system_id] >= 2
        for d in etat.deposits
    )


@given(
    parsers.re(
        r"une partie du serveur en mémoire sur les réglages "
        r"(?P<reglages>de test|de test à 12 systèmes|de test aux gisements vides"
        r"|de tunables\.toml), "
        r"(?:graine (?P<graine>\d+)|sur la première graine dont (?P<condition>.+)), sans horloge"
    )
)
def partie_serveur(
    serveur: Serveur, reglages: str, graine: str | None, condition: str | None
) -> None:
    game = importer("fourx.server.game")
    world = importer("fourx.core.world")
    serveur.tunables = reglages_de(reglages)
    if condition is None:
        assert graine is not None
        serveur.graine = int(graine)
    else:
        trouvees = (
            g
            for g in range(1, LIMITE_DE_GRAINES + 1)
            if monde_convient(world.generate(g, serveur.tunables), condition, serveur.tunables)
        )
        choisie = next(trouvees, None)
        assert choisie is not None, f"aucune graine de 1 à {LIMITE_DE_GRAINES} : {condition}"
        serveur.graine = choisie
    serveur.dossier.mkdir(parents=True, exist_ok=True)
    serveur.jeu = game.Game(serveur.dossier, serveur.graine, serveur.tunables)


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

QUI = r"(?P<qui>le propriétaire|l'autre acteur)"


def nom_de(qui: str) -> str:
    return "propriétaire" if qui == "le propriétaire" else "autre"


@when(parsers.re(r"le serveur joue (?P<n>\d+) ticks?"))
def serveur_joue(serveur: Serveur, n: str) -> None:
    serveur.jeu.advance(int(n))


@when(
    parsers.re(QUI + r" envoie son vaisseau vers le gisement de (?P<ore>ore_[a-z]) le plus proche")
)
def vers_gisement_du_minerai(serveur: Serveur, qui: str, ore: str) -> None:
    nom = nom_de(qui)
    systemes = [
        d.system_id for d in serveur.derniere(nom).deposits if d.ore_id == rang_minerai(ore)
    ]
    serveur.aller(nom, plus_proche(serveur.dist(nom), systemes))


@when(parsers.re(QUI + r" envoie son vaisseau vers le gisement le plus proche"))
def vers_gisement(serveur: Serveur, qui: str) -> None:
    nom = nom_de(qui)
    systemes = [d.system_id for d in serveur.derniere(nom).deposits]
    serveur.aller(nom, plus_proche(serveur.dist(nom), systemes))


@when(
    parsers.re(
        r"le propriétaire envoie son vaisseau vers la station qui paie le mieux (?P<ore>ore_[a-z])"
    )
)
def vers_meilleure_station(serveur: Serveur, ore: str) -> None:
    """Règle 2 du PNJ (Technical Plan, point 7) : le meilleur prix, puis la plus proche, puis le
    plus petit identifiant."""
    rang = rang_minerai(ore)
    dist = serveur.dist("propriétaire")
    station = min(
        serveur.derniere("propriétaire").stations,
        key=lambda s: (-s.ore_prices[rang - 1], dist[s.system_id], s.id),
    )
    serveur.aller("propriétaire", station.system_id)


@when(parsers.re(r"le propriétaire envoie son vaisseau vers la station (?P<n>\d+)"))
def vers_station(serveur: Serveur, n: str) -> None:
    stations = [s for s in serveur.derniere("propriétaire").stations if s.id == int(n)]
    assert len(stations) == 1, stations
    serveur.aller("propriétaire", stations[0].system_id)


@when(parsers.re(QUI + r" envoie son vaisseau vers un système voisin"))
def vers_voisin(serveur: Serveur, qui: str) -> None:
    nom = nom_de(qui)
    dist = serveur.dist(nom)
    serveur.aller(nom, min(s for s, d in dist.items() if d == 1))


@when(parsers.re(QUI + r" envoie son vaisseau vers un système à deux sauts du sien"))
def vers_deux_sauts(serveur: Serveur, qui: str) -> None:
    nom = nom_de(qui)
    dist = serveur.dist(nom)
    serveur.aller(nom, min(s for s, d in dist.items() if d == 2))


@when(
    parsers.re(
        r"l'autre acteur envoie son vaisseau vers un système (?P<ecart>à deux sauts|voisin) "
        r"de celui du propriétaire"
    )
)
def vers_ecart_du_proprietaire(serveur: Serveur, ecart: str) -> None:
    sauts = 2 if ecart == "à deux sauts" else 1
    dist = serveur.dist("propriétaire")
    serveur.aller("autre", min(s for s, d in dist.items() if d == sauts))


@when(
    "le propriétaire envoie son vaisseau vers le plus proche système qui a une station et un "
    "gisement"
)
def vers_colocalisation(serveur: Serveur) -> None:
    observation = serveur.derniere("propriétaire")
    communs = {s.system_id for s in observation.stations} & {
        d.system_id for d in observation.deposits
    }
    serveur.aller("propriétaire", plus_proche(serveur.dist("propriétaire"), sorted(communs)))


def dernier_ordre_accepte(serveur: Serveur, nom: str) -> bool:
    """La dernière mise à jour de `nom` porte le résultat accepté de son dernier ordre."""
    ordre = serveur.derniers_ordres.get(nom)
    if ordre is None:
        return False
    return any(
        r.order_id.number == ordre.number and r.accepted for r in serveur.derniere(nom).results
    )


@when(
    parsers.re(
        r"le serveur joue jusqu'à l'arrivée du vaisseau (?P<de>du propriétaire|de l'autre acteur)"
    )
)
def jusqua_arrivee(serveur: Serveur, de: str) -> None:
    actors = importer("fourx.schema.actors")
    nom = "propriétaire" if de == "du propriétaire" else "autre"
    cible = serveur.cibles[nom]

    def arrive() -> bool:
        navire = serveur.vaisseau(nom)
        if nom not in serveur.debut and dernier_ordre_accepte(serveur, nom):
            serveur.debut[nom] = serveur.derniere(nom).tick
        return bool(navire.system_id == cible and navire.activity == actors.Activity.IDLE)

    serveur.debut.pop(nom, None)
    serveur.jouer_jusqua(arrive)
    serveur.fin[nom] = serveur.derniere(nom).tick


@when(parsers.re(r"le propriétaire ordonne à son vaisseau de miner (?P<ore>ore_[a-z])"))
def miner(serveur: Serveur, ore: str) -> None:
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    serveur.envoyer("propriétaire", orders.Mine(ship_id=navire.id, ore_id=rang_minerai(ore)))


@when("le propriétaire ordonne à son vaisseau de miner le gisement de son système")
def miner_ici(serveur: Serveur) -> None:
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    ici = [d for d in serveur.derniere("propriétaire").deposits if d.system_id == navire.system_id]
    assert len(ici) == 1, ici
    serveur.envoyer("propriétaire", orders.Mine(ship_id=navire.id, ore_id=ici[0].ore_id))


@when("le serveur joue jusqu'à ce que la cargaison du propriétaire soit pleine")
def jusqua_pleine(serveur: Serveur) -> None:
    nom = "propriétaire"

    def pleine() -> bool:
        navire = serveur.vaisseau(nom)
        if "minage" not in serveur.debut and dernier_ordre_accepte(serveur, nom):
            serveur.debut["minage"] = serveur.derniere(nom).tick
        return bool(sum(navire.cargo) >= navire.capacity)

    serveur.debut.pop("minage", None)
    serveur.jouer_jusqua(pleine)
    serveur.fin["minage"] = serveur.derniere(nom).tick


@when("le propriétaire ordonne à son vaisseau de vendre toute sa cargaison")
def vendre_tout(serveur: Serveur) -> None:
    """Une cargaison d'un seul minerai : une seule vente."""
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    charges = [(rang + 1, q) for rang, q in enumerate(navire.cargo) if q > 0]
    assert len(charges) == 1, navire.cargo
    ore_id, quantite = charges[0]
    serveur.vente = {"ore_id": ore_id, "quantite": quantite}
    serveur.envoyer(
        "propriétaire", orders.Sell(ship_id=navire.id, ore_id=ore_id, quantity=quantite)
    )


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


def voisin_du_proprietaire(serveur: Serveur) -> int:
    dist = serveur.dist("propriétaire")
    return min(s for s, d in dist.items() if d == 1)


@when(
    "le propriétaire soumet, en son propre nom, un ordre d'administration d'aller dans "
    "un système voisin"
)
def ordre_d_administration(serveur: Serveur) -> None:
    """Un déplacement de catégorie « administration » : `step` l'accepterait s'il passait,
    seule la réception peut le refuser."""
    orders = importer("fourx.schema.orders")
    navire = serveur.vaisseau("propriétaire")
    commande = orders.Move(ship_id=navire.id, target_system_id=voisin_du_proprietaire(serveur))
    serveur.soumettre("propriétaire", [serveur.ordre("propriétaire", commande, categorie="ADMIN")])


@when(
    parsers.re(
        r"le propriétaire soumet dans le même tick (?P<n>\d+) ordres d'aller dans "
        r"un système voisin, numérotés de 1 à (?P<dernier>\d+)"
    )
)
def plusieurs_ordres(serveur: Serveur, n: str, dernier: str) -> None:
    orders = importer("fourx.schema.orders")
    assert int(n) == int(dernier)
    navire = serveur.vaisseau("propriétaire")
    commande = orders.Move(ship_id=navire.id, target_system_id=voisin_du_proprietaire(serveur))
    # Envoyés du plus grand au plus petit numéro : la réception doit garder les plus petits
    # numéros, pas les premiers arrivés.
    ordres = [serveur.ordre("propriétaire", commande, num=k) for k in range(int(n), 0, -1)]
    serveur.soumettre("propriétaire", ordres)


# --- Alors


@then(parsers.re(r"le monde de la partie a au moins (?P<n>\d+) systèmes"))
def monde_assez_grand(serveur: Serveur, n: str) -> None:
    world = importer("fourx.core.world")
    assert len(world.generate(serveur.graine, serveur.tunables).systems) >= int(n)


@then(
    "la dernière mise à jour du propriétaire montre dans ses réglages publics le jump_ticks et "
    "le mining_rate de tunables.toml"
)
def reglages_publics(serveur: Serveur) -> None:
    publics = serveur.derniere("propriétaire").public_tunables
    assert (publics.jump_ticks, publics.mining_rate) == (
        serveur.tunables.jump_ticks,
        serveur.tunables.mining_rate,
    )


@then("le trajet du propriétaire a duré jump_ticks ticks")
def duree_trajet(serveur: Serveur) -> None:
    assert serveur.fin["propriétaire"] - serveur.debut["propriétaire"] + 1 == (
        serveur.tunables.jump_ticks
    )


@then("le minage du propriétaire a duré cargo_capacity ÷ mining_rate ticks")
def duree_minage(serveur: Serveur) -> None:
    attendu = -(-serveur.tunables.cargo_capacity // serveur.tunables.mining_rate)
    assert serveur.fin["minage"] - serveur.debut["minage"] + 1 == attendu


def vente_du_proprietaire(serveur: Serveur) -> Any:
    events = importer("fourx.schema.events")
    ventes = [
        e.payload
        for e in serveur.derniere("propriétaire").events
        if isinstance(e.payload, events.Sale)
    ]
    assert len(ventes) == 1, ventes
    return ventes[0]


@then(
    "la dernière mise à jour du propriétaire montre la vente de sa cargaison au prix de la station "
    "de son système"
)
def vente_au_prix_de_la_station(serveur: Serveur) -> None:
    observation = serveur.derniere("propriétaire")
    ici = serveur.vaisseau("propriétaire").system_id
    stations = [s for s in observation.stations if s.system_id == ici]
    assert len(stations) == 1, stations
    prix = stations[0].ore_prices[serveur.vente["ore_id"] - 1]
    vente = vente_du_proprietaire(serveur)
    paiement = serveur.vente["quantite"] * prix
    assert (vente.ore_id, vente.quantity, vente.price, vente.payment, vente.tax) == (
        serveur.vente["ore_id"],
        serveur.vente["quantite"],
        prix,
        paiement,
        taxe(paiement, serveur.tunables.tax_rate_bp),
    )


@then(
    "la dernière mise à jour du propriétaire montre un portefeuille égal au paiement moins la taxe"
)
def portefeuille(serveur: Serveur) -> None:
    vente = vente_du_proprietaire(serveur)
    assert serveur.derniere("propriétaire").wallet_balance == vente.payment - vente.tax


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


@then("le journal des événements contient l'écriture de vente et l'écriture de taxe de cette vente")
def journal_ecritures(serveur: Serveur) -> None:
    events = importer("fourx.schema.events")
    raison = importer("fourx.schema.ledger").Reason
    vente = vente_du_proprietaire(serveur)
    ecritures = [
        e.payload.entry
        for e in serveur.evenements()
        if isinstance(e.payload, events.LedgerEntryRecorded)
    ]
    assert any(e.reason == raison.ORE_SALE and e.amount == vente.payment for e in ecritures)
    assert any(e.reason == raison.SALE_TAX and e.amount == vente.tax for e in ecritures)


@then("la dernière mise à jour du propriétaire ne montre pas le vaisseau de l'autre acteur")
def autre_invisible(serveur: Serveur) -> None:
    autre = serveur.vaisseau("autre").id
    assert all(v.id != autre for v in serveur.derniere("propriétaire").other_ships)


@then(
    "la dernière mise à jour du propriétaire montre comme inconnu le stock de chaque gisement à "
    "deux sauts ou plus, et connu celui des autres"
)
def stock_selon_la_portee(serveur: Serveur) -> None:
    dist = serveur.dist("propriétaire")
    gisements = serveur.derniere("propriétaire").deposits
    assert any(dist[d.system_id] >= 2 for d in gisements), "aucun gisement à deux sauts ou plus"
    assert any(dist[d.system_id] <= 1 for d in gisements), "aucun gisement à un saut ou moins"
    for d in gisements:
        if dist[d.system_id] >= 2:
            assert d.stock is None, d
        else:
            assert d.stock is not None, d


@then(
    "la dernière mise à jour du propriétaire montre le vaisseau de l'autre acteur dans son système"
)
def autre_visible(serveur: Serveur) -> None:
    autre = serveur.vaisseau("autre")
    vus = [v for v in serveur.derniere("propriétaire").other_ships if v.id == autre.id]
    assert len(vus) == 1, vus
    assert (vus[0].owner_id, vus[0].system_id) == (serveur.acteurs["autre"], autre.system_id)
    assert not hasattr(vus[0], "activity")


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
    "la dernière mise à jour du propriétaire montre son vaisseau dans son système de départ, "
    "à l'arrêt"
)
def dans_son_systeme_de_depart(serveur: Serveur) -> None:
    """Le propriétaire, créé le premier, part de la station de plus petit identifiant
    (Technical Plan, point 2, système de départ)."""
    actors = importer("fourx.schema.actors")
    observation = serveur.derniere("propriétaire")
    depart = min(observation.stations, key=lambda s: s.id).system_id
    navire = serveur.vaisseau("propriétaire")
    assert (navire.system_id, navire.activity) == (depart, actors.Activity.IDLE)


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
