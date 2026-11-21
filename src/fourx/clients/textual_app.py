"""Le client Textual : l'écran unique.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 bis (disposition, touches)
et point 6 (fonction de rappel de vitesse) ; plan détaillé, point 23 quinquies. `FourxApp` ne
garde que l'affichage, la saisie en cours et les touches ; l'état du client est dans
`ClientModel`, et chaque cadre de `frames.py` le lit. Le client ne connaît que `schema` et
`policies` (niveau 1, §1) : en mode développement, il reçoit une simple fonction `set_speed`.

Touches (AZERTY, sans Majuscule) : d déplacer, m miner, v vendre, q quitter ; Entrée acquitte
l'alerte affichée, sinon confirme la saisie ; Échap annule. En mode développement : p pause ou
reprise, a / r accélérer / ralentir (×1, ×10, ×100), Espace avancer jusqu'à la prochaine alerte.
"""

from collections.abc import Callable

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical

from fourx.clients.frames import (
    BarreEtat,
    CadreAlerte,
    CadreCarte,
    CadreDestinations,
    CadreHistorique,
    CadreStations,
    CadreVaisseau,
    destinations,
)
from fourx.clients.model import ClientModel
from fourx.clients.texts import minerai, systeme
from fourx.schema.orders import Command, Mine, Move
from fourx.schema.protocol import Connection, TickUpdate

PALIERS = (1, 10, 100)
QUITTER = "Quitter termine la partie (pas de reprise avant M5). Entrée pour confirmer."
AIDE = "sans effet ici · d déplacer · m miner · v vendre · q quitter"
AIDE_DEV = AIDE + " · dev : p a r ␣"
AIDE_LISTE = "destination : ↑ ↓ choisir · Entrée confirmer · Échap annuler"


class FourxApp(App[None]):
    TITLE = "4X — tranche 0"
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen { layout: vertical; }
    #corps { height: 1fr; }
    #gauche { width: 53; }
    #droite { width: 1fr; }
    #carte { height: 12; border: solid $foreground; }
    #alerte { height: auto; text-style: reverse; border: solid $foreground; display: none; }
    #historique, #destinations { height: 1fr; border: solid $foreground; }
    #destinations { display: none; }
    #vaisseau { height: 10; border: solid $foreground; }
    #stations { height: 1fr; border: solid $foreground; }
    #barre { height: 2; }
    """

    def __init__(
        self,
        connection: Connection,
        actor_id: int,
        set_speed: Callable[[int | None], None] | None = None,
    ) -> None:
        super().__init__()
        self.connection = connection
        self.model = ClientModel(actor_id)
        self.set_speed = set_speed
        self.saisie: str | None = None
        self.choix = 0
        self.minerai_a_miner: int | None = None
        self.aide = ""
        self.palier = 1
        self.en_pause = False
        self.en_avance = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="corps"):
            with Vertical(id="gauche"):
                yield CadreCarte()
                yield CadreAlerte()
                yield CadreHistorique()
                yield CadreDestinations()
            with Vertical(id="droite"):
                yield CadreVaisseau()
                yield CadreStations()
        yield BarreEtat()

    def on_mount(self) -> None:
        self.rafraichir()
        self.run_worker(self.recevoir(), exclusive=True)

    async def recevoir(self) -> None:
        while True:
            self.recevoir_mise_a_jour(await self.connection.next_update())

    def recevoir_mise_a_jour(self, update: TickUpdate) -> None:
        """Passe la mise à jour au modèle, soumet sa réponse ; pendant l'avance jusqu'à la
        prochaine alerte, une nouvelle alerte remet la vitesse à ×1."""
        avant = len(self.model.alerts)
        reponse = self.model.on_update(update)
        if reponse is not None:
            self.connection.submit(reponse)
        if self.en_avance and len(self.model.alerts) > avant:
            self.en_avance = False
            self.palier = 1
            self.vitesse(1)
        self.rafraichir()

    # --- Affichage

    def libelle_vitesse(self) -> str | None:
        if self.set_speed is None:
            return None
        if self.en_pause:
            return "pause"
        if self.en_avance:
            return "×100 jusqu'à l'alerte"
        return f"×{self.palier}"

    def rafraichir(self) -> None:
        self.query_one(CadreCarte).montrer(self.model)
        self.query_one(CadreVaisseau).montrer(self.model)
        self.query_one(CadreStations).montrer(self.model)
        self.query_one(CadreAlerte).montrer(self.model)
        self.query_one(CadreHistorique).montrer(self.model)
        liste = self.query_one(CadreDestinations)
        en_liste = self.saisie == "destination"
        liste.display = en_liste
        self.query_one(CadreHistorique).display = not en_liste
        if en_liste:
            liste.montrer(self.model, self.choix)
        self.query_one(BarreEtat).montrer(self.model, self.libelle_vitesse(), self.aide)

    # --- Ordres

    def envoyer(self, command: Command) -> None:
        self.connection.submit(self.model.send(command))

    def vitesse(self, facteur: int | None) -> None:
        if self.set_speed is not None:
            self.set_speed(facteur)

    # --- Touches

    def on_key(self, event: events.Key) -> None:
        event.stop()
        self.aide = ""
        self.touche(event.key)
        self.rafraichir()

    def touche(self, touche: str) -> None:
        if touche == "enter" and self.model.alerts:
            self.model.acknowledge()
            return
        if self.saisie is not None:
            self.dans_la_saisie(touche)
        elif touche in ("d", "m", "v", "q"):
            self.commande(touche)
        elif self.set_speed is not None and touche in ("p", "a", "r", "space"):
            self.developpement(touche)
        else:
            self.aide = AIDE_DEV if self.set_speed is not None else AIDE

    def commande(self, touche: str) -> None:
        if touche == "q":
            self.saisie = "quitter"
            self.aide = QUITTER
            return
        navire = self.model.vaisseau()
        obs = self.model.observation
        if navire is None or obs is None:
            self.aide = "en attente du premier tick"
            return
        if touche == "d":
            self.saisie = "destination"
            self.aide = AIDE_LISTE
            self.choix = next(i for i, s in enumerate(obs.systems) if s.id == navire.system_id)
        elif touche == "m":
            ici = [d for d in obs.deposits if d.system_id == navire.system_id]
            if ici:
                self.saisie = "miner"
                self.minerai_a_miner = ici[0].ore_id
                self.aide = (
                    f"miner {minerai(ici[0].ore_id)} dans {systeme(navire.system_id)} ? "
                    "Entrée confirmer · Échap annuler"
                )
            else:
                self.saisie = "minerai"
                self.aide = "pas de gisement ici : quel minerai ? a ou b (Échap annule)"
        else:
            message = self.model.sell_all()
            if message is None:
                self.aide = "cargaison vide : rien à vendre"
            else:
                self.connection.submit(message)

    def dans_la_saisie(self, touche: str) -> None:
        if touche == "escape":
            self.saisie = None
            return
        navire = self.model.vaisseau()
        obs = self.model.observation
        if self.saisie == "quitter":
            if touche == "enter":
                self.exit()
            else:
                self.aide = QUITTER
        elif navire is None or obs is None:
            self.saisie = None
        elif self.saisie == "destination":
            lignes = destinations(obs, navire.system_id)
            self.aide = AIDE_LISTE
            if touche == "up":
                self.choix = max(self.choix - 1, 0)
            elif touche == "down":
                self.choix = min(self.choix + 1, len(lignes) - 1)
            elif touche == "enter":
                self.saisie = None
                self.aide = ""
                self.envoyer(Move(ship_id=navire.id, target_system_id=lignes[self.choix][0]))
        elif self.saisie == "miner":
            if touche == "enter" and self.minerai_a_miner is not None:
                self.saisie = None
                self.envoyer(Mine(ship_id=navire.id, ore_id=self.minerai_a_miner))
            else:
                self.aide = "Entrée confirmer le minage · Échap annuler"
        elif self.saisie == "minerai":
            if touche in ("a", "b"):
                self.saisie = None
                self.envoyer(Mine(ship_id=navire.id, ore_id=ord(touche) - ord("a") + 1))
            else:
                self.aide = "quel minerai ? a ou b (Échap annule)"

    def developpement(self, touche: str) -> None:
        if touche == "p":
            self.en_avance = False
            self.en_pause = not self.en_pause
            self.vitesse(None if self.en_pause else self.palier)
            return
        if touche == "space":
            if self.model.alerts:
                self.aide = "acquittez d'abord l'alerte (Entrée)"
                return
            self.en_pause = False
            self.en_avance = True
            self.vitesse(100)
            return
        rang = PALIERS.index(100 if self.en_avance else self.palier)
        voulu = rang + 1 if touche == "a" else rang - 1
        if not 0 <= voulu < len(PALIERS):
            if not self.en_avance:
                self.aide = "déjà au palier le plus " + ("rapide" if touche == "a" else "lent")
                return
            voulu = rang
        self.en_avance = False
        self.palier = PALIERS[voulu]
        if not self.en_pause:
            self.vitesse(self.palier)
