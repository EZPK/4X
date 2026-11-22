"""Le client Textual : l'écran rétro.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 bis (touches, ordres,
alertes) et point 7 ter (disposition 120 × 36, palette, carte, prochaine étape, aide), point 6
(fonction de rappel de vitesse) ; plan détaillé, points 23 nonies et 23 decies. `FourxApp` ne
garde que l'affichage, la saisie en cours et les touches ; l'état du client est dans
`ClientModel`, et chaque cadre de `frames.py` le lit. Le client ne connaît que `schema` et
`policies` (niveau 1, §1) : en mode développement, il reçoit une simple fonction `set_speed`.

Touches (AZERTY, sans Majuscule) : d déplacer, m miner, v vendre, h aide, q quitter ; z / x zoom
avant et arrière, c recentrer sur le vaisseau, flèches déplacer la carte (hors saisie) ; Entrée
acquitte l'alerte affichée, sinon confirme la saisie ; Échap annule. À la souris : molette, glisser,
survol (bulle) et clic sur un système (liste des destinations ouverte sur sa ligne). En mode
développement : p pause ou reprise, a / r accélérer / ralentir (×1, ×10, ×100), Espace avancer
jusqu'à la prochaine alerte. L'aide s'ouvre au lancement : c'est une saisie, un widget
superposé, et non un écran modal, pour que `FourxApp` reçoive toujours les touches. En dessous de
120 × 36, seul un message s'affiche, et seule la touche q agit.
"""

from collections.abc import Callable

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from fourx.clients.frames import (
    BarreEtat,
    BarreTouches,
    Bulle,
    CadreAide,
    CadreCarte,
    CadreDestinations,
    CadreEtape,
    CadreHistorique,
    CadreStations,
    CadreVaisseau,
    MapCanvas,
    destinations,
    texte_bulle,
)
from fourx.clients.guide import next_step
from fourx.clients.map_view import center_on, pan, ship_position, zoom
from fourx.clients.model import ClientModel
from fourx.clients.palette import PALETTE
from fourx.clients.texts import minerai, systeme
from fourx.schema.orders import Command, Mine, Move
from fourx.schema.protocol import Connection, TickUpdate

PALIERS = (1, 10, 100)
TAILLE_MINIMALE = (120, 36)
TAILLE_AIDE = (90, 28)
QUITTER = "Quitter termine la partie (pas de reprise avant M5). Entrée pour confirmer."
AIDE = "sans effet ici · d déplacer · m miner · v vendre · h aide · q quitter"
AIDE_DEV = AIDE + " · dev : p a r ␣"
AIDE_LISTE = "destination : ↑ ↓ choisir · Entrée confirmer · Échap annuler"
AIDE_OUVERTE = "aide ouverte : Entrée, Échap ou h pour la fermer · ↑ ↓ pour la faire défiler"
TOUCHES_DEV = ("p", "a", "r", "space")
TOUCHES_CARTE = ("z", "x", "c", "left", "right", "up", "down")
TAILLE_BULLE = (40, 7)


def message_petite_fenetre(largeur: int, hauteur: int) -> str:
    return (
        f"Agrandis la fenêtre : {TAILLE_MINIMALE[0]} colonnes × {TAILLE_MINIMALE[1]} lignes au "
        f"moins (actuellement {largeur} × {hauteur})."
    )


def feuille_de_style() -> str:
    p = PALETTE
    return f"""
    Screen {{ layers: base ombre aide; background: {p["fond"]}; color: {p["texte"]}; }}
    #ecran {{ height: 100%; }}
    #petite {{ display: none; padding: 1 2; color: {p["texte"]}; }}
    #barre {{ height: 2; background: {p["fond"]}; }}
    #corps {{ height: 1fr; }}
    #carte {{
        width: 1fr;
        background: {p["fond"]};
        color: {p["texte"]};
        border: round {p["trait"]};
        border-title-color: {p["texte_attenue"]};
    }}
    #carte-entete, #carte-legende {{ height: 1; background: {p["fond"]}; }}
    #carte-canevas {{ height: 1fr; }}
    #droite {{ width: 47; margin-left: 1; }}
    .cadre {{
        background: {p["cadre"]};
        border: round {p["trait"]};
        border-title-color: {p["texte_attenue"]};
        padding: 0 1;
    }}
    #etape {{ height: 7; border: round {p["accent"]}; border-title-color: {p["accent"]}; }}
    #vaisseau {{ height: 8; }}
    #stations, #destinations {{ height: 1fr; }}
    #destinations {{ display: none; }}
    #historique {{ height: 6; }}
    #touches {{ height: 1; background: {p["cadre_clair"]}; color: {p["texte"]}; }}
    #aide, #ombre {{
        position: absolute;
        width: {TAILLE_AIDE[0]};
        height: {TAILLE_AIDE[1]};
    }}
    #aide {{ layer: aide; border: round {p["accent"]}; }}
    #bulle {{
        position: absolute;
        layer: ombre;
        display: none;
        width: {TAILLE_BULLE[0]};
        height: {TAILLE_BULLE[1]};
        background: {p["cadre"]};
        color: {p["texte"]};
        border: round {p["accent"]};
        padding: 0 1;
    }}
    #ombre {{ layer: ombre; background: {p["ombre"]}; }}
    """


class FourxApp(App[None]):
    TITLE = "4X — tranche 0"
    ENABLE_COMMAND_PALETTE = False
    CSS = feuille_de_style()

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
        self.aide_ouverte = True
        self.petite_fenetre = False
        self.taille = (0, 0)
        self.choix = 0
        self.minerai_a_miner: int | None = None
        self.aide = ""
        self.palier = 1
        self.en_pause = False
        self.en_avance = False

    def compose(self) -> ComposeResult:
        yield Static("", markup=False, id="petite")
        with Vertical(id="ecran"):
            yield BarreEtat()
            with Horizontal(id="corps"):
                yield CadreCarte()
                with Vertical(id="droite"):
                    yield CadreEtape()
                    yield CadreVaisseau()
                    yield CadreStations()
                    yield CadreDestinations()
            yield CadreHistorique()
            yield BarreTouches()
        yield Static("", id="ombre")
        yield CadreAide()
        yield Bulle()

    def on_mount(self) -> None:
        for ident in ("#etape", "#vaisseau", "#stations", "#destinations", "#historique", "#aide"):
            self.query_one(ident).add_class("cadre")
        self.placer(self.size.width, self.size.height)
        self.rafraichir()
        self.run_worker(self.recevoir(), exclusive=True)

    def on_resize(self, event: events.Resize) -> None:
        self.placer(event.size.width, event.size.height)
        self.rafraichir()

    def placer(self, largeur: int, hauteur: int) -> None:
        """Centre l'aide et son ombre ; en dessous de 120 × 36, n'affiche que le message."""
        self.taille = (largeur, hauteur)
        self.petite_fenetre = largeur < TAILLE_MINIMALE[0] or hauteur < TAILLE_MINIMALE[1]
        x = max((largeur - TAILLE_AIDE[0]) // 2, 0)
        y = max((hauteur - TAILLE_AIDE[1]) // 2, 0)
        self.query_one("#aide").styles.offset = (x, y)
        self.query_one("#ombre").styles.offset = (x + 2, y + 1)

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
        petite = self.query_one("#petite", Static)
        petite.display = self.petite_fenetre
        self.query_one("#ecran").display = not self.petite_fenetre
        aide_visible = self.aide_ouverte and not self.petite_fenetre
        self.query_one(CadreAide).display = aide_visible
        self.query_one("#ombre").display = aide_visible
        if self.petite_fenetre:
            message = message_petite_fenetre(*self.taille)
            petite.update(message + ("\n\n" + QUITTER if self.saisie == "quitter" else ""))
            return
        self.query_one(CadreCarte).montrer(self.model)
        self.query_one(CadreEtape).montrer(self.model)
        self.query_one(CadreVaisseau).montrer(self.model)
        self.query_one(CadreHistorique).montrer(self.model)
        en_liste = self.saisie == "destination"
        liste = self.query_one(CadreDestinations)
        liste.display = en_liste
        stations = self.query_one(CadreStations)
        stations.display = not en_liste
        if en_liste:
            liste.montrer(self.model, self.choix)
        else:
            stations.montrer(self.model)
        if aide_visible:
            self.query_one(CadreAide).montrer(self.model, self.set_speed is not None)
        self.query_one(BarreEtat).montrer(self.model, self.libelle_vitesse(), self.aide)
        self.query_one(BarreTouches).montrer(self.saisie, self.aide_ouverte)

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
        if self.petite_fenetre:
            self.dans_la_petite_fenetre(event.key)
        elif self.aide_ouverte:
            self.dans_l_aide(event.key)
        else:
            self.touche(event.key)
        self.rafraichir()

    def dans_la_petite_fenetre(self, touche: str) -> None:
        """Seule q agit, avec sa confirmation."""
        if self.saisie == "quitter":
            if touche == "enter":
                self.exit()
            elif touche == "escape":
                self.saisie = None
        elif touche == "q":
            self.saisie = "quitter"

    def dans_l_aide(self, touche: str) -> None:
        if touche in ("enter", "escape", "h"):
            self.aide_ouverte = False
        elif touche in ("up", "down"):
            cadre = self.query_one(CadreAide)
            if touche == "up":
                cadre.scroll_up(animate=False)
            else:
                cadre.scroll_down(animate=False)
        elif touche == "q":
            self.aide_ouverte = False
            self.saisie = "quitter"
            self.aide = QUITTER
        elif self.set_speed is not None and touche in TOUCHES_DEV:
            self.developpement(touche)
        else:
            self.aide = AIDE_OUVERTE

    def touche(self, touche: str) -> None:
        if touche == "h":
            self.saisie = None
            self.aide_ouverte = True
            self.query_one(CadreAide).scroll_home(animate=False)
            return
        if touche == "enter" and self.model.alerts:
            self.model.acknowledge()
            return
        if self.saisie is not None:
            self.dans_la_saisie(touche)
        elif touche in TOUCHES_CARTE:
            self.carte(touche)
        elif touche in ("d", "m", "v", "q"):
            self.commande(touche)
        elif self.set_speed is not None and touche in TOUCHES_DEV:
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
            conseil = next_step(self.model).command
            cible = conseil.target_system_id if isinstance(conseil, Move) else navire.system_id
            self.ouvrir_la_liste(cible)
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

    def ouvrir_la_liste(self, cible: int) -> None:
        """Ouvre la liste des destinations sur la ligne du système `cible`."""
        obs = self.model.observation
        if obs is None:
            return
        self.saisie = "destination"
        self.aide = AIDE_LISTE
        self.choix = next((i for i, s in enumerate(obs.systems) if s.id == cible), 0)

    def carte(self, touche: str) -> None:
        """z / x : zoom avant et arrière autour du centre ; c : recentrer sur le vaisseau ;
        flèches : déplacer la vue d'un dixième de la zone visible."""
        canevas = self.query_one(MapCanvas)
        vue = canevas.vue
        if touche in ("z", "x"):
            nouvelle = zoom(vue, 1 if touche == "z" else -1, None)
        elif touche == "c":
            position = ship_position(self.model, canevas.positions)
            if position is None:
                self.aide = "en attente du premier tick"
                return
            nouvelle = center_on(vue, position)
        else:
            dx = max(vue.width // 10, 1)
            dy = max(vue.height // 10, 1)
            decalages = {"left": (-dx, 0), "right": (dx, 0), "up": (0, -dy), "down": (0, dy)}
            nouvelle = pan(vue, *decalages[touche])
        if nouvelle == vue:
            self.aide = AIDE_DEV if self.set_speed is not None else AIDE
            return
        canevas.changer_vue(nouvelle)

    def on_map_canvas_clic(self, message: MapCanvas.Clic) -> None:
        """Un clic sur un système : la liste des destinations s'ouvre sur sa ligne ; ignoré
        pendant une saisie ou quand l'aide est ouverte."""
        navire = self.model.vaisseau()
        if self.saisie is not None or self.aide_ouverte or self.petite_fenetre or navire is None:
            return
        self.aide = ""
        if message.ident == navire.system_id:
            self.aide = f"déjà dans {systeme(message.ident)}"
        else:
            self.ouvrir_la_liste(message.ident)
        self.rafraichir()

    def on_map_canvas_survol(self, message: MapCanvas.Survol) -> None:
        """La bulle : deux cases à droite et en dessous du pointeur ; à gauche ou au-dessus près
        des bords."""
        bulle = self.query_one(Bulle)
        if message.ident is None or self.aide_ouverte:
            bulle.display = False
            return
        largeur, hauteur = self.taille
        x, y = message.x + 2, message.y + 2
        if x + TAILLE_BULLE[0] > largeur:
            x = max(message.x - 2 - TAILLE_BULLE[0], 0)
        if y + TAILLE_BULLE[1] > hauteur:
            y = max(message.y - 2 - TAILLE_BULLE[1], 0)
        bulle.styles.offset = (x, y)
        bulle.update(texte_bulle(self.model, message.ident))
        bulle.display = True

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
