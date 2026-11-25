# 4X

Jeu de gestion spatiale multijoueur, joué dans le terminal au style rétro 8 bits. Humains, joueurs IA et personnages scriptés y partagent le même monde et les mêmes règles.

> **État :** en développement, jalon M1 sur 7 (M0 à M6). Une première version jouable existe, hors ligne et en solo : miner, transporter, vendre.

## Le jeu

### L'idée

On dirige des vaisseaux miniers dans un univers fait de systèmes reliés entre eux. On extrait du minerai, on le transporte et on le vend, puis, à terme, on s'organise en corporations qui se disputent les ressources, le marché et les routes.

- **Un rythme lent et stratégique.** Le temps est une ressource : un saut entre deux systèmes ou une cargaison à miner prend du temps réel, et le monde avance même quand on ne fait rien. On grandit avec plus de vaisseaux, pas avec des actions plus rapides.
- **Des joueurs IA à égalité.** Des réseaux de neurones, entraînés hors ligne sur une carte graphique, joueront comme les humains, à partir du jalon M4. Ils reçoivent la même observation, envoient les mêmes ordres et subissent les mêmes refus. Dans le jeu, ils seront toujours signalés comme IA.
- **Une économie tenue en comptabilité.** Tout l'argent passe par un registre en partie double, en nombres entiers. Aujourd'hui, il est créé quand une station rachète du minerai, et détruit par la taxe sur la vente. Plus tard viendront les contrats, les primes et les frais. La conservation de l'argent est vérifiée à chaque tick.
- **Un monde rejouable.** Toute la simulation tient dans une seule fonction déterministe, `step`. Une partie rejouée depuis son journal d'ordres redonne exactement le même état, tick après tick.
- **À terme, un monde persistant.** Un serveur qui tourne en continu, où les joueurs IA peuvent continuer de faire vivre une corporation pendant que les humains sont absents.

### Ce qui est jouable aujourd'hui (tranche 0)

Un petit monde hors ligne, généré à partir d'une graine :
- 8 à 12 systèmes reliés en graphe, et 4 à 6 gisements ;
- deux minerais ;
- 2 à 3 stations, qui rachètent chaque minerai à leur propre prix fixe ;
- d'autres mineurs, pilotés par des scripts.

On choisit un minerai, on envoie son vaisseau le miner, on le ramène à une station et on vend la cargaison. La vente est taxée. Un cadre « Prochaine étape » guide la première partie.

Un vaisseau voit la carte entière, les gisements et les prix. En revanche, il ne voit les autres vaisseaux et le stock des gisements que dans son système et les systèmes voisins.

### Ce qui n'est pas prévu

- Des noms, un lore et un univers inventés au fil du code. Seuls les noms validés par le propriétaire entrent dans le jeu (`docs/noms-valides.md`).
- Des personnages conversationnels, des clients tiers ou un client navigateur avant la fin de la feuille de route.

## Installation

### Prérequis

- Linux. C'est la seule plateforme essayée à ce jour.
- `git`, `make` et [uv](https://docs.astral.sh/uv/). uv télécharge Python 3.15 s'il manque.
- Un terminal :
  - en couleurs 24 bits (truecolor) ;
  - d'au moins 120 colonnes × 36 lignes ;
  - avec une police qui dessine les caractères Braille, qui servent à tracer les liens de la carte. Par exemple : JetBrainsMono Nerd Font.

### Jouer

```sh
git clone https://github.com/EZPK/4X.git
cd 4X
uv sync --locked
make jouer
```

- `make jouer` lance la dernière version stable : l'état de la branche `main` sur GitHub. Le jeu tourne depuis un dossier de travail à part (`.worktrees/stable`), remis à jour à chaque lancement ; la branche sur laquelle on travaille n'est jamais touchée.
- `make jouer-ici` lance la version du dossier courant.
- Options : `GRAINE=42` (graine du monde), `DEV=1` (mode développement : pause, accélération).
- `make` seul affiche l'aide.

### Les touches

| Touche | Action |
| :-- | :-- |
| `d` | déplacer le vaisseau (liste des destinations ; Entrée envoie, Échap annule). Un clic sur la carte marche aussi |
| `m` | miner le gisement du système |
| `v` | vendre toute la cargaison, dans le système d'une station |
| `z` / `x` | zoomer, dézoomer la carte |
| `c` | recentrer la carte sur son vaisseau |
| flèches | déplacer la carte |
| Entrée | confirmer, ou acquitter une alerte |
| Échap | annuler |
| `h` | ouvrir ou fermer l'aide |
| `q` | quitter |

En mode développement (`DEV=1`) :
- `p` met en pause ;
- `a` et `r` accélèrent ou ralentissent ;
- Espace avance jusqu'à la prochaine alerte.

## Développer

```sh
uv sync --locked
uv run pre-commit install
make tests
```

`gitleaks` 8.30.1 doit être dans le `PATH`, car le hook pre-commit refuse tout commit qui contient un secret. Voir `docs/designs/niveau-2-m0-garde-fous.md`, plan détaillé, point 4.

`make tests` lance les tests rapides. Trois groupes de tests plus longs se lancent à part :
- `uv run pytest -m rejeu` : le rejeu de la partie de référence sur 100 000 ticks ;
- `uv run pytest -m lent` : les fourchettes économiques et la disposition de la carte ;
- `uv run pytest -m proprietes` : les tests de propriétés.

### Organisation du code

Le code vit dans le paquet `fourx`, découpé en paquets aux imports contrôlés en CI :

| Paquet | Rôle |
| :-- | :-- |
| `schema` | Types des ordres, des observations et des événements ; validation et encodage |
| `core` | État du monde, `step`, `observe`, registre comptable. Strictement déterministe : ni nombre flottant, ni hasard non contrôlé, ni horloge |
| `policies` | Tout ce qui décide des ordres à partir d'une observation : scripts et, plus tard, réseaux entraînés |
| `server` | Boucle des ticks, transport, persistance |
| `clients` | Client Textual, hôte des personnages scriptés |
| `training` | Environnement d'entraînement des joueurs IA (à partir de M4) |
| `tools` | Serveur de rejeu, outil de divergence, statistiques économiques |

### Documents et règles du dépôt

Le code est écrit par un agent de code (Claude Code), selon des documents de conception validés par le propriétaire, qui est le seul à fusionner.

- `CLAUDE.md` : les règles de travail et le circuit des pull requests.
- `docs/designs/architecture-niveau-1.md` : l'architecture commune et le découpage en jalons.
- `docs/designs/niveau-2-*.md` : le plan détaillé de chaque jalon.
- `docs/adr/` : les décisions d'architecture.
- `docs/glossaire.md` : le vocabulaire, en français et dans le code.
- `docs/feuille-de-route.md` : l'état officiel des jalons. **Il fait foi** sur la feuille de route présumée ci-dessous.

La CI bloque la fusion de toute pull request dont un contrôle est rouge, y compris pour l'administrateur. Elle vérifie notamment :
- le lint, le typage, les secrets et les termes interdits ;
- les contrats d'imports ;
- les invariants de déterminisme et de conservation de l'argent ;
- le rejeu de référence, et un score de mutation sur le noyau.

Chaque nuit, une suite de bugs volontaires (les « canaris ») vérifie que chacun de ces contrôles attrape bien ce qu'il doit attraper.

## Feuille de route présumée

Chaque jalon a son propre document de conception et un critère de sortie mesurable. Seuls M0 et M1 ont aujourd'hui un document approuvé. Pour les jalons suivants, le tableau reprend le découpage de l'architecture (`docs/designs/architecture-niveau-1.md`, §11), et leur contenu peut encore changer.

| Jalon | Contenu | Critère de sortie | État |
| :-- | :-- | :-- | :-- |
| **M0** | Garde-fous et squelette du dépôt : protection de `main`, contrôle des chemins protégés, détection des secrets, CI | Une pull request rouge ne peut pas être fusionnée ; un faux secret est refusé | livré |
| **M1** | Noyau déterministe, tranche 0 jouable, client rétro, rejeu et outil de divergence | La boucle « miner, transporter, vendre » passe ; 100 000 ticks rejoués à l'identique ; l'économie reste dans ses fourchettes ; le propriétaire valide la boucle de jeu | en cours : code livré, compte rendu et validation à venir |
| **M2** | Observabilité : événements versionnés, stockage Parquet, page d'accueil de santé du projet | Chaque chiffre de jeu ou d'économie se recalcule à partir des événements | à concevoir |
| **M3** | Jeu en réseau : transport WebSocket entre client et serveur | Les dix premières minutes d'un joueur se jouent par WebSocket | à concevoir |
| **M4** | Premier joueur IA : environnement d'entraînement, mineur entraîné par renforcement, suivi dans MLflow | Le mineur entraîné bat d'au moins 10 % la référence scriptée, verdict statistique à l'appui | à concevoir |
| **M5** | Monde persistant : serveur en continu, migrations, déploiement des joueurs IA | Aucun ordre confirmé n'est perdu après un plantage ; un joueur IA est déployé avec ses garde-fous (mode observation, arrêt d'urgence) | à concevoir |
| **M6** | Jeu à plusieurs : marché entre joueurs, corporations et permissions, pirates scriptés | Une corporation à deux membres, un humain et un joueur IA, fonctionne | à concevoir |

**Au-delà de M6** (pistes, rien n'est décidé) :
- une économie plus riche : prix fixés par un marché, gouvernement, banques, assurance ;
- une carte plus vaste, pensée comme un graphe avec des carrefours et des passages obligés ;
- d'autres métiers pour les joueurs IA : transporteur, marchand ;
- un portage du noyau en Rust, si la vitesse de simulation l'exige ;
- des clients tiers branchés sur le protocole, et un client navigateur.

## Licence

Tous droits réservés. Aucune licence n'accorde de droit de réutilisation de ce code.
