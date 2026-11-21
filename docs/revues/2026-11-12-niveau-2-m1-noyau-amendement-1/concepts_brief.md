# Brief de concept, tour 2 : amendement du noyau de M1 (écran unique, et le temps comme ressource)

**Auteur :** EZPK
**Date :** 2026-11-11
**Mode :** BRAINSTORM, tour 2. Six angles de revue sans contexte : conception, détails du code, simplicité (zoom-out), compréhension, préparation à l'implémentation, structure. Les six revues ont abouti. Aucune n'a exécuté de code : les constats viennent de la lecture du code, et les chiffres d'un calcul à la main.
**Remplace :** le brief du tour 1, écrit sur l'hypothèse « document séparé, quatre onglets, tick plus long sans changer les règles ». Ce que le tour 1 a établi et qui reste vrai est repris ici. Les options qu'il a écartées figurent dans « Alternatives Weighed ».

---

## Overview

La partie de test du 2026-11-11 donne le verdict « intéressant, pas encore fun ». Le fun est attendu de mécaniques futures. Le propriétaire relève quatre gênes :
- le rythme est trop rapide ;
- l'affichage est confus : carte en simple liste, emplacement des minerais peu clair, historique qui défile, état du vaisseau trop dense ;
- les touches sont peu claires ;
- un refus de minage est resté incompris.

Il veut un jeu plus lent, stratégique et réfléchi, où le temps est une ressource.

Le concept révisé, confirmé par le propriétaire après le tour 1, est **un amendement du document approuvé** docs/designs/niveau-2-m1-noyau.md. Il est livré avant le volet C et couvre deux sujets :
1. **Un seul écran** au rendu « 8 bits », façon tableur : texte, tableaux, cadres, peu ou pas de couleurs. Il montre :
   - l'emplacement des minerais ;
   - la durée restante des trajets et du minage ;
   - les ordres en attente ;
   - des refus en français construits par le client, qui disent où aller ;
   - des alertes de fin de tâche à acquitter par une touche ;
   - une file de vente côté client, un minerai par tick, le plus abondant d'abord ;
   - une table des touches fixée par le document.

   Les noms retenus sont « Historique » et « Station ».
2. **Le temps devient une ressource dès M1.** Le concept propose `jump_ticks` = 400, soit 20 minutes par saut avec une période nominale de 3 s. Le minage prend du temps ; la vente et le déchargement restent instantanés. L'observation reçoit une vue des constantes publiques, ce qui fait passer `PROTOCOL_VERSION` à 2. Un moyen d'accélérer l'univers hors ligne est prévu.

**Ce que disent les six revues, en bref :**
- Le moment est bon : aucune référence du volet C n'existe, et `RULES_REVISION` vaut 0. Changer les réglages ne coûte donc aucune régénération.
- Le sujet 2 se réduit presque à des réglages. `rules_version` change seul, par l'empreinte des réglages, et `step` ne change pas, à une condition : la durée de minage voulue doit tenir dans la limite des entiers (100 ticks au plus avec une soute de 100).
- Passer à 400 ticks par saut casse pourtant quatre choses, que l'amendement doit traiter de front :
  - les fourchettes économiques du volet C, mesurées par fenêtres de 1 000 ticks ;
  - deux scénarios protégés de `partie.feature`, et la durée de la CI et de la mutation ;
  - la limite des entiers sur la durée du minage ;
  - la signature `observe(état, acteur)`, écrite au niveau 1.
- Trois questions de procédure et de jeu restent à trancher par le propriétaire :
  - **la procédure :** l'effet de l'amendement sur le statut de M1, avec le risque de geler tout le jalon ;
  - **l'ancrage en temps réel :** « 20 minutes » n'est pas une règle ;
  - **le jeu avec un seul vaisseau :** plus de 99 % du temps se passe en trajet, et un choix devient dominant.

---

## Analysis

### 1. Ce qui existe déjà (vérifié dans le code)

| Besoin | État actuel | Source |
| :-- | :-- | :-- |
| Emplacement des minerais | Déjà public : `DepositView` porte `system_id`, `ore_id` et `stock`. | src/fourx/schema/observation.py:20-24 |
| Prix de la station | Dans `StationView.ore_prices`, jamais affichés | src/fourx/schema/observation.py:27-30 |
| État de mon vaisseau | `activity`, `route`, `ticks_to_next_jump`, `cargo`, `capacity` | src/fourx/schema/observation.py:38-48 |
| Période | `--periode` (float, 1.0 par défaut) transmis à `Game(period_s=1.0)`. Hors des réglages. `Game.run` relit `self.period_s` à chaque tour, après avoir dormi une période. | src/fourx/__main__.py:53-55, src/fourx/server/game.py:60 et :158-162 |
| `rules_version` | `rules-<RULES_REVISION>+<blake2b de l'encodage MessagePack de Tunables>` : il change seul quand un réglage change. `RULES_REVISION` = 0 passe à 1 à la première création des références. | src/fourx/core/version.py:15-23 |
| Réglages actuels | `jump_ticks` = 5, `mining_rate` = 10, `cargo_capacity` = 100, `ore_prices` = [10, 15], `tax_rate_bp` = 1000, `deposit_stock` = 20000, `regen_ticks` = 1000, `budget_regen` = 1, `budget_max` = 10 | src/fourx/core/tunables.toml:3-11 |
| Protection | `tunables.toml` n'est **pas** un chemin protégé. Le document, les scénarios, leurs étapes et `setup.cfg` le sont. | .github/chemins-proteges.txt:1-29 |
| Carte | Une chaîne system_1, system_2, system_3. La graine choisit une des six permutations (station, gisement de ore_a, gisement de ore_b). Graine 1 : station dans system_1, ore_a dans system_2, ore_b dans system_3. | src/fourx/core/world.py:14-29, tests/scenarios/partie.feature:4 |

L'observation n'entre ni dans les empreintes ni dans les instantanés : les deux portent sur `State` seul. Enrichir l'observation ne touche donc pas les références.

### 2. Défauts confirmés dans le code actuel

- **La vente perd le second minerai.** `action_vendre` envoie un `Sell` par minerai dans un seul message (src/fourx/clients/textual_app.py:159-171). `step` n'examine qu'un ordre par vaisseau et par tick, et refuse les autres en `SUPERSEDED` (src/fourx/core/step.py:294-315). Le concept dit ce défaut confirmé par exécution, et les revues le confirment à la lecture. Le test tests/clients/test_textual_app.py:117-121 fige ce comportement.
- **Les refus s'affichent en codes anglais.** `step` écrit `text=code.value` (src/fourx/core/step.py:288). Ce texte entre dans l'empreinte `last_tick`, d'où le consensus : construire le message dans le client.
- **Toute suite rapide d'ordres** produit des `SUPERSEDED`, pas seulement la vente. Le client ne garde pas de table numéro d'ordre → commande : seul `self.numero` existe (src/fourx/clients/textual_app.py:124-141).
- **Les chiffres demandent Majuscule sur un clavier AZERTY.** Le choix de destination attend `isdigit()`, et accepte même 0 (src/fourx/clients/textual_app.py:178). Sur AZERTY sans Majuscule, la rangée du haut donne `&`, `é`, `"`. Cela peut expliquer une partie de la plainte « touches peu claires ». La disposition du clavier du propriétaire n'est pas connue.
- **La graine est imprimée puis effacée par Textual** (src/fourx/__main__.py:59). La période n'est enregistrée nulle part.

### 3. Effets des longues durées (sujet 2)

**3.1 Calculs exacts** (lecture de src/fourx/core/step.py:249-263, :328-342, :357-379)
- Trajet :
  - un `Move` accepté au tick T fait sauter le vaisseau au tick T + J − 1, puis tous les J ticks ;
  - durée restante = `ticks_to_next_jump + (len(route) − 1) × jump_ticks` ;
  - tick d'arrivée = `obs.tick + ticks_to_next_jump + (len(route) − 1) × jump_ticks`.
- Minage :
  - il commence au tick d'acceptation ;
  - durée restante = `ceil(capacité libre / mining_rate)` ;
  - c'est une borne seulement : le minage finit plus tôt si le gisement se vide ou s'il est partagé.
- Cycle du PNJ :
  - durée = `4J + M + 4` pour un gisement à deux sauts (formule du noyau, docs/designs/niveau-2-m1-noyau.md:856) ;
  - avec J = 400 et M = 10, cela donne 1 614 ticks ;
  - première vente du PNJ avec la graine 1 au tick 1 612 (`4J + M + 2`).
- « Environ 1 600 ticks » ne vaut que pour un gisement à deux sauts. Si la station est dans system_2, chaque aller-retour fait environ 800 ticks.
- À 3 s par tick, un aller-retour dure environ 40 min vers ore_a et environ 80 min vers ore_b. Ces calculs ont été faits à la main par les revues : ils sont à refaire par script.

**3.2 Le minage est entier : bloquant si la durée voulue dépasse 100 ticks**
- `mining_rate` est un entier d'au moins 1 (src/fourx/core/tunables.py:12 et :22). Avec `cargo_capacity` = 100, remplir une cargaison prend au plus 100 ticks, soit 5 min à 3 s.
- Au-delà, deux leviers :
  - **changer l'échelle des unités**, par exemple une capacité de 4 000. Seuls les réglages changent. Il faut revoir `ore_prices`, `deposit_stock`, les montants du scénario CUJ 1 (1 500 / 150 / 1 350) et les bornes ;
  - **ajouter un réglage ou un compteur de cycles de minage.** Cela change `step`, `Tunables` (dans des étapes protégées), le sens de `MiningStarted.rate`, et peut-être `State`, les empreintes et `snapshot_schema_version`.
- Conception et préparation recommandent le changement d'échelle, ou une durée qui tient dans 100 ticks.

**3.3 Le volet C ne vérifierait plus rien (bloquant, unanime)**
- Avec un cycle de 810 à 1 614 ticks, une fenêtre de 1 000 ticks contient 0 ou 1 vente par PNJ : la borne basse tombe à 0.
- Les 100 000 ticks sont fixés par le niveau 1 (docs/designs/architecture-niveau-1.md:49 et :498). La largeur des fenêtres relève, elle, du niveau 2.
- Passages du noyau touchés : objectif 5 (:64), Technical Plan point 1 (:119), §9 (:297-301), §10 (:308), `window_stats(..., window=1000)` (:494), justification de `regen_ticks` (:765), point 27 bornes et calcul (:848-859).
- Calcul de la revue de préparation pour W = 10 000, J = 400 et un minage de 10 ticks, refait à la main, à refaire par script :
  - de 5 à 14 ventes par PNJ et par fenêtre ;
  - pour deux PNJ : émission de 15 000 à 42 000, taxe de 1 500 à 4 200, croissance de 13 500 à 37 800 ;
  - 9 fenêtres vérifiées ; `regen_ticks` = 1 000 divise W.

  La revue de conception propose W = 20 000.
- Le coût du rejeu ne change pas, puisqu'on garde 100 000 ticks. Le journal maigrit, et la partie de référence exerce moins de règles par minute de CI.

**3.4 Scénarios, tests, mutation**
- `partie.feature` lit les vrais réglages (`load_tunables()`, tests/scenarios/steps/steps_partie.py:151). Deux scénarios cassent :
  - le CUJ 1, durées codées en dur (tests/scenarios/partie.feature:11-31), qui échoue à :17 ;
  - « le PNJ vend en 100 ticks » (:56-59).
- `noyau.feature` ne casse pas, car ses étapes figent `REGLAGES_M1` (tests/scenarios/steps/steps_noyau.py:29-39). Mais « les réglages de M1 » (tests/scenarios/noyau.feature:9) devient faux.
- `tests/aide_monde.py` (`REGLAGES`) n'est relié à `tunables.toml` par aucun test : la dérive sera silencieuse.
- Un scénario en attente doit échouer (`xfail(strict=True)`, tests/scenarios/conftest.py:70-71). Un scénario vrai avec les anciennes et les nouvelles valeurs ne peut donc pas être marqué en attente. Les nouveaux scénarios doivent distinguer l'ancienne règle de la nouvelle, par exemple « après 400 ticks, le vaisseau est dans system_2, en route ».
- Durée : avec les vrais réglages, le CUJ 1 joue environ 1 620 ticks à travers `Game`. Chaque tick coûte un `step`, les empreintes, un commit SQLite et un `observe` par client. Ce coût est payé pour chaque mutant de `core`, avec une limite de 30 min par tâche (docs/designs/niveau-2-m1-noyau.md:561).
- Autres tests qui cassent :
  - si `PROTOCOL_VERSION` passe à 2 : tests/core/test_versions.py:20 et tests/schema/test_schema.py:202-219 ;
  - si `Observation` reçoit un champ : tests/aide_observation.py:53 ;
  - si le défaut de `Game(period_s=1.0)` change : tests/server/test_partie.py:46 ;
  - le test du PNJ « moins de 40 ticks » (tests/policies/test_scripted_miner.py:108-115) tourne sur les réglages de test.
- La réception ne lit jamais `protocol_version`. `steps_partie.py:38` (`PROTOCOLE = 1`) continuera donc d'envoyer 1 sans erreur.

**3.5 Le jeu avec un seul vaisseau (risque à signaler, sans rouvrir la décision)**
- Plus de 99 % d'un cycle se passe en trajet, et aucun ordre n'est possible en route : tout ordre est refusé avec `SHIP_EN_ROUTE` (src/fourx/core/step.py:160-161). Il reste une décision par trajet.
- Aucune annulation n'existe. Une erreur de touche engage le vaisseau pour 20 à 40 minutes.
- Un choix devient dominant. Aujourd'hui, ore_a et ore_b rapportent environ 50 par tick chacun. Avec J = 400, ore_a voisin rapporte environ 1,23 par tick et ore_b à deux sauts environ 0,93. Le PNJ choisit le mieux payé quelle que soit la distance (src/fourx/policies/scripted_miner.py:39) : il devient sous-optimal.
- Deux réglages perdent leur sens :
  - `regen_ticks` = 1 000 est plus court qu'un aller-retour, donc l'épuisement des gisements ne pèse jamais ;
  - le budget d'actions (une action regagnée par tick, plafond 10) ne limite plus personne.
- Pour M4, des épisodes de milliers de ticks faits surtout d'attente donnent des récompenses rares. La métrique « pour 1 000 ticks » du niveau 1 (docs/designs/architecture-niveau-1.md:355) devient presque toujours nulle.

**3.6 Le temps réel n'est pas une règle**
- Les règles ne connaissent que des ticks. « 20 minutes » n'est vrai qu'à 3 s par tick. Or le code et le noyau disent 1 s (docs/designs/niveau-2-m1-noyau.md:269), et le niveau 1 évoque 5 s (docs/designs/architecture-niveau-1.md:89).
- Le client ne connaît pas la période. L'observation ne peut pas la porter, car ce n'est pas une donnée du jeu. Un champ dans `TickUpdate` serait un autre canal, interdit (docs/designs/architecture-niveau-1.md:310).
- À la période nominale, valider la boucle (objectif 11, docs/designs/niveau-2-m1-noyau.md:76) demanderait plusieurs heures, surtout d'attente. Les « 20 minutes » ne seront donc pas validées en M1.
- `asyncio.sleep` s'appuie sur une horloge monotone. Sous Linux, cette horloge ne compte probablement pas la veille : l'univers se figerait quand le portable est en veille. C'est à vérifier.

### 4. Effets de l'écran unique et du modèle client (sujet 1)

**4.1 Pendant un saut, l'écran ment**
- `system_id` reste le système de départ pendant tout le saut.
- `Departed` et `Arrived` sont émis ensemble, au tick du saut (src/fourx/core/step.py:333-334).
- `OtherShipView` ne porte ni activité ni route (src/fourx/schema/observation.py:51-55). Le PNJ paraît donc immobile pendant 20 minutes, puis saute d'un coup.
- Le document doit donner une maquette de l'état « en route », et dire explicitement qu'on ne voit pas si un autre vaisseau est en route.

**4.2 Les alertes reposent sur une sémantique d'événements piégeuse**
- `Arrived` est public et émis à chaque saut. Filtre : mon vaisseau, route vide.
- `MiningEnded` est aussi émis quand un autre ordre interrompt le minage. Sa cause se déduit de `causation_id` (src/fourx/core/step.py:189-202).
- La file de vente produit un `Sale` par tick. Il faut une seule alerte, en fin de file, avec le total net.
- Les refus apparaissent à la fois dans `OrderRefused` et dans `OrderResult` : une seule source, sinon l'alerte est doublée.
- `DepositRegenerated` est émis même quand le gisement est plein : c'est du bruit.
- Le signal n'est pas défini (visuel, sonore avec `bell`), ni la touche d'acquittement. « N'importe quelle touche » risque une action non voulue. L'empilement des alertes pendant une absence n'est pas défini non plus.

**4.3 La file de vente et les ordres en attente forment une petite machine à états**
- Les revues convergent vers un modèle client pur, séparé de `FourxApp`, testé sans Textual et couvert par la mutation (`textual_app.py` en est exclu, setup.cfg:17-19). Ses règles :
  - au plus un ordre en vol par vaisseau, c'est-à-dire envoyé et sans résultat vu ;
  - l'indicateur d'attente s'efface au résultat qui porte le même numéro d'ordre, pas à un tick supposé ;
  - « vendre » est un mode : chaque `Sell` est recalculé sur la dernière cargaison, comme le PNJ (src/fourx/policies/scripted_miner.py:30-33) ;
  - la vente suivante part seulement après le résultat de la précédente ;
  - un ordre manuel ou un refus vide la file.
- Écrit comme `SyncClient`, ce modèle s'attache par `Game.attach` et joue par `Game.advance` (src/fourx/server/game.py:114-116 et :153-156). On teste ainsi un saut de 400 ticks sans attendre.
- La logique « le plus abondant d'abord » existe dans `_commande`, fonction privée du PNJ. On peut l'extraire en fonction publique (`clients` peut importer `policies`).

**4.4 Quitter met fin à la partie**
- La fermeture du client annule l'horloge et ferme la partie (src/fourx/__main__.py:39-47). Il n'y a aucune reprise avant M5.
- `q` quitte sans confirmation. Une fausse manœuvre perd une boucle de 80 minutes.

**4.5 Termes ambigus ou en collision avec le glossaire**
- **« 8 bits » et « façon tableur ».** Le premier évoque des pixels colorés, le second une grille sobre. Il faut une maquette 80 × 24, le jeu de caractères et une règle de mise en valeur sans couleur.
- **« Ordre en attente ».** Il a deux sens (ordre envoyé, vente prévue). « En attente » désigne déjà les scénarios (docs/glossaire.md:150).
- **« Historique ».** Il frôle « historique public » (docs/glossaire.md:69). Préciser « Historique (cadre du client) ».
- **« Vaisseau de départ ».** Il se lit « vaisseau qui part ». Écrire « 20 minutes par saut ».
- **« Soute ».** Ni le code ni le glossaire n'emploient ce mot, qui disent « cargaison » et « capacité ».
- **« Constantes publiques ».** Le glossaire dit « réglages » (docs/glossaire.md:67). Proposer « réglages publics ».
- **« Hors ligne ».** Le mot entre en collision avec « départ hors ligne » et « monde en ligne ». Définir « partie locale ».
- **« Solde » et « Portefeuille ».** Le client dit « Portefeuille ». Choisir un seul mot. Aucun nom de monnaie n'est validé.
- **EVE Online.** Son vocabulaire est interdit (docs/termes-interdits.md:3 et :11-13) : ne rien en reprendre.

### 5. Procédure documentaire

**5.1 Statut pendant la revue de l'amendement (bloquant, signalé par quatre revues)**
- Un document approuvé ne change que par une nouvelle revue (docs/designs/architecture-niveau-1.md:448).
- Si le statut Proposed ou « en revue » est fusionné sur `main`, CLAUDE.md impose de s'arrêter, et tout M1 gèle, y compris la correction des défauts.
- Si le statut reste « approuvé » sur `main`, rien n'empêche d'ouvrir la pull request de scénarios du volet C, puisque protégée et scénarios sont deux types distincts.
- Le précédent du point 1 du plan détaillé (docs/designs/niveau-2-m1-noyau.md:620 et :629) fait changer le statut sur la branche seulement.

**5.2 ADR pour `observe` (bloquant selon la structure, à trancher selon la conception et la préparation)**
- Le niveau 1 fixe `observe(état, acteur)`, qui « ne renvoie que les champs visibles » de l'état (docs/designs/architecture-niveau-1.md:308). Le glossaire écrit la même chose (docs/glossaire.md:41). Le noyau ajoute « les vues reprennent les noms des champs de l'état » (:225).
- Une vue construite à partir de `Tunables` sort de ces trois règles. Le README des ADR exige une ADR pour tout changement d'une interface du niveau 1. L'agent de code ne peut la rédiger qu'au statut « proposée ».

**5.3 Numérotation et marquage**
- Une trentaine de fichiers de tests, et presque tous les modules, citent des points du noyau, par exemple « point 7 » ou « point 17 ».
- Règle proposée : ajouter sans jamais renuméroter.
  - Objectifs 12 et 13 à la suite.
  - Un §7 bis pour l'écran unique.
  - Le temps écrit dans les §2 et §6.
  - Un volet « B bis » de points 23 bis, 23 ter, etc., entre les points 23 et 24.
  - Un tableau des amendements dans le préambule.
  - La marque « (amendement 1) » au niveau du titre ou du point modifié.
- La section Open Questions revit pendant la revue, et doit être vide avant le retour à Approved.

**5.4 Rangement**
- Les rapports vont dans `docs/revues/<date>-niveau-2-m1-noyau-amendement-1/`, avec un `README.md`.
- Ce brief ne doit pas rester à la racine du worktree : il va dans ce dossier, ou il est supprimé.

**5.5 Le code et le document divergent déjà**
- Le point 22 annonce `python -m fourx [--graine N]`, alors que le code a aussi `--periode` et `--runs`.
- Le §13 écrit `Game(..., period_s: float = 1.0)`.

---

## Goals vs. Non-Goals

### Objectifs de l'amendement

1. **Règles en ticks, temps réel en conséquence.**
   - Une phrase fait foi : « les durées des règles sont en ticks ; les minutes ne sont qu'une estimation d'affichage ».
   - La période nominale est écrite à un seul endroit (§6), avec sa valeur et sa raison.
   - « 20 min » y figure comme cible dérivée (`jump_ticks` × période).
2. **Valeurs fixées et confirmées** par le propriétaire, dans un tableau « réglage : valeur actuelle → nouvelle valeur → effet sur `step`, tests et scénarios ». Il couvre `jump_ticks`, la durée de minage et son levier, `regen_ticks`, `deposit_stock`, `ore_prices` si on rééquilibre, la période nominale, la taille des fenêtres et les bornes. La formule de calcul des bornes est écrite et appliquée aux réglages.
3. **Versions sans surprise.**
   - `rules_version` change seul et `RULES_REVISION` reste à 0, écrit noir sur blanc.
   - `PROTOCOL_VERSION` passe à 2, sans contrôle à la réception en M1.
4. **Réglages publics dans l'observation.**
   - Une liste fermée, chaque champ justifié par un affichage.
   - La signature d'`observe`.
   - La visibilité déclarée champ par champ sur `Tunables`.
   - Un test qui prouve que l'annotation ne change ni l'encodage ni `tunables_fingerprint`.
   - L'extension du test « aucun champ caché ».
   - Une règle de bascule : quand une durée dépendra d'un vaisseau ou d'un lien, elle passera dans la vue de l'entité.
5. **Écran unique lisible sur 80 × 24.**
   - Des maquettes en texte pour chaque état : à l'arrêt, en route, en minage, saisie, confirmation, alerte, file de vente.
   - Une table « information affichée → source → formule → unité ».
   - Une chronologie commentée d'un cycle complet.
6. **Refus compréhensibles.**
   - Une table des 18 `RefusalCode` (src/fourx/schema/results.py:14-32) → texte français → donnée utilisée.
   - Les refus liés à un lieu nomment le système, et ceux liés au temps nomment le tick.
   - L'ordre est désigné par son contenu, jamais par son numéro.
7. **Alertes fiables.** Une table « événement et filtre → texte → signal → acquittement ». Une alerte par fin de tâche de mon vaisseau, des ventes regroupées, des refus inclus, un empilement défini, une copie dans l'Historique et une touche d'acquittement sans autre effet.
8. **Clavier sans ambiguïté.**
   - Une table des touches par mode.
   - Une confirmation avant tout ordre coûteux : un déplacement, avec sauts, ticks et ≈ minutes ; un ordre qui interrompt un minage.
   - Échap pour annuler, un retour visible sur une touche invalide.
   - Une saisie compatible AZERTY.
   - `q` confirmé, avec le message « quitter termine la partie ».
9. **Modèle client pur.** Il porte la file de vente, les ordres en vol, les alertes et l'Historique. Il est muté, joué en `SyncClient` dans les tests, et sa table de transitions est écrite.
10. **Accélération hors ligne bornée.** Qui la commande, par quel geste, comment elle s'affiche, ce qu'elle laisse intact (ticks, ordres, journal), et pourquoi ce n'est pas l'alternative C.
11. **Observabilité.**
    - La graine, la période (et la vitesse), et le dossier de la partie affichés en permanence.
    - La période initiale et chaque changement enregistrés dans un fichier du dossier de la partie, distinct de `OrderLog`.
12. **Volet C redimensionné dans l'amendement lui-même.** Taille des fenêtres, bornes recalculées et justification de `regen_ticks`. Ce n'est pas renvoyé au volet C.
13. **Critère « lisible »** distinct de la validation de la boucle (objectif 11). L'amendement dit à quelle période se joue la séance de validation.

### Non-objectifs

- La souris, les thèmes, le mode rejeu du client (M3), le tutoriel.
- Plusieurs vaisseaux, des types de vaisseaux, des distances variables.
- **Les dommages.** Aucune conception en M1, au plus une ligne dans « Future Improvements ».
- Un marché ou des prix variables (M6).
- Un ordre « arrêter » ou un changement de route en vol : ce serait un changement des règles.
- Une reprise de partie avant M5. On peut la noter en « Future Improvements », car elle serait peu coûteuse par `replay_orders` après le volet C.
- La période ou une accélération passant par le protocole ou par `TickUpdate`.
- Augmenter `RULES_REVISION`.
- Le fun, attendu de mécaniques futures.

---

## Alternatives Weighed

### Écartées au tour 1 (raisons conservées)

| Option | Raison du rejet |
| :-- | :-- |
| **Document séparé `niveau-2-m1-ecrans.md`** | La feuille de route n'a qu'une cellule et un statut par jalon, et `CLAUDE.md` parle du document du jalon au singulier. Il aurait fallu changer le circuit, et deux textes auraient fait foi. Le propriétaire a choisi l'amendement. |
| **Quatre onglets et une barre d'état** | Les onglets cachent de l'information, alors que le joueur rate des événements. L'onglet Station n'aurait montré que deux prix. Les touches 1 à 4 entraient en conflit avec le choix de la destination. Le propriétaire a choisi l'écran unique. |
| **Un tick plus long seulement, sans changer les règles** | Le PNJ reste aussi rapide en ticks, et l'ennui menace plus que la réflexion. Le propriétaire a choisi le temps comme ressource, par les réglages. |
| **Aucune donnée nouvelle** (distances en sauts, débit lu dans `MiningStarted.rate`) | Pas de durée avant le premier départ. Déduire `jump_ticks` de `ticks_to_next_jump` est fragile. Le propriétaire a accepté l'enrichissement de l'observation. |
| **Un champ dans `TickUpdate` hors de l'observation, ou un message d'accueil** | « Il n'y a pas d'autre canal vers le joueur » (docs/designs/architecture-niveau-1.md:310). Les joueurs IA en seraient privés. |
| **Refus construits par `step`** | Le texte entre dans l'empreinte `last_tick` et casse tests/core/test_step.py:298. Après le volet C, chaque retouche d'un libellé coûterait une régénération des références. |
| **Champ structuré dans `OrderResult`** | Change `schema`, l'instantané et le protocole sans nécessité. |
| **Alertes par `App.notify`** | Disparaissent au bout d'un délai réel, utilisent des couleurs, et le test dépend de l'horloge. |
| **Alertes par comparaison de deux observations successives** | Casse dès qu'une mise à jour manque, ce qui arrivera avec les reconnexions de M3. On s'appuie sur les événements. |
| **Une vente par appui, minerai choisi par lettre** | Le propriétaire a choisi la file côté client. |
| **Tables dérivées (durées, distances) calculées dans `core`** | Casse « vues = champs de l'état » et alourdit `observe`. Le calcul se fait dans le client, avec un test croisé. |

### Écartées ou mises en réserve au tour 2

| Option | Raison |
| :-- | :-- |
| **Garder des fenêtres de 1 000 ticks** | 0 ou 1 vente par fenêtre : la borne basse tombe à 0 et le test ne prouve plus rien. |
| **Allonger la partie de référence à 1 000 000 de ticks** | Environ 10 fois plus de temps de rejeu, et un fichier d'empreintes de chaque tick d'environ 300 Mo. Élargir les fenêtres suffit, et les 100 000 ticks du niveau 1 restent intacts. |
| **Descendre sous 100 000 ticks** | Fixé par le niveau 1 : il faudrait une ADR, sans bénéfice. |
| **Cycles de minage (compteur dans `Ship`) ou nouveau réglage « ticks par lot »** | Change `step`, `Tunables` dans des étapes protégées, le sens de `MiningStarted.rate`, et peut-être `State` et `snapshot_schema_version`. Préférer une durée qui tient dans `cargo_capacity` ticks, ou un changement d'échelle des unités. |
| **Copier les réglages publics dans `State` à la génération** (précédent `ore_prices`) | **En réserve, comme repli si l'ADR est refusée.** Évite l'ADR, et ne coûte presque rien tant que les références n'existent pas. Mais elle change `State`, les empreintes et l'instantané, contre la décision « sans toucher les empreintes ni les instantanés ». Le document doit la noter avec ce coût réel. |
| **Accélération par un message de protocole** | C'est l'alternative C, déjà rejetée (docs/designs/niveau-2-m1-noyau.md:515-519). |
| **Accélération par `Game.advance(n)` appelé depuis l'interface** | Bloque la boucle de Textual, envoie n mises à jour d'un coup, et mélange les deux modes. |
| **Un fichier de réglages « de développement » présenté comme accélération** | C'est un changement de règles, avec un autre `rules_version`. Acceptable seulement comme option distincte (`--reglages`), avec les réglages enregistrés dans le dossier de la partie. |
| **La période transmise au client dans l'observation ou dans `TickUpdate`** | Ce n'est pas une donnée du jeu, et ce serait un autre canal. |
| **Afficher seulement des minutes** | Le client ne connaît pas la période, qui change avec l'accélération. Les ticks restent l'information principale, avec une estimation marquée « ≈ ». |
| **Augmenter `RULES_REVISION`** | Rendrait fausse la règle du volet C, « de 0 à 1 à la première création des références ». |
| **Scénarios de partie entièrement sur les vrais réglages** | Chaque essai de réglage repasserait par une pull request de scénarios protégée, et la CI et la mutation s'allongent. Préférer des réglages de test explicites, plus un seul scénario sur les vraies valeurs. |
| **Livrer l'écran et les durées en un seul bloc** | Retarde la correction de défauts déjà confirmés (vente, refus). Voir le découpage plus bas. |

---

## Key Decisions & Staging for Next Steps

### Décisions du propriétaire (2026-11-12)

Ces décisions tranchent les options listées plus bas, qui restent pour mémoire.

1. **Statut :** Proposed et « en revue » sur la branche de la pull request protégée seulement, puis retour à Approved et « approuvé » avant la fusion. Aucune pull request du volet C avant la livraison de l'amendement (pull requests protégée, de scénarios et de fonctionnalité).
2. **Saut :** `jump_ticks = 400`, soit 20 minutes à la période nominale de 3 s.
3. **Minage :** en principe, sa durée dépendra du vaisseau (son laser de minage, débit) et de la capacité de sa cargaison ; ni l'un ni l'autre ne varie en M1 (un seul type de vaisseau). En M1 : `mining_rate = 1` avec `cargo_capacity = 100`, soit 100 ticks (5 minutes à 3 s) pour remplir une cargaison, sans changement d'échelle des unités. La durée de remplissage se lit déjà comme capacité ÷ débit, ce qui prépare les lasers et cargaisons variables des jalons suivants.
4. **Période nominale :** 3 s, écrite à un seul endroit ; premier tick joué dès le lancement.
5. **Validation de la boucle de M1 :** en accéléré.
6. **Économie :** fenêtres de 10 000 ticks sur les 100 000 ticks du niveau 1 ; `regen_ticks` et le budget d'actions réajustés par l'amendement.
7. **Réglages publics (révisé le 2026-11-12) :** la première version de cette décision (un champ dans `TickUpdate`) contredisait le niveau 1 : « Il n'y a pas d'autre canal vers le joueur » (architecture-niveau-1.md, ligne 310). Décision révisée : `observe(état, acteur, réglages)` ajoute à l'observation une vue des réglages publics. Une ADR 0003, rédigée au statut « proposée » et acceptée par le propriétaire, change l'interface du niveau 1 (ligne 308) et le glossaire. `State`, `step`, les empreintes et les instantanés ne changent pas ; `PROTOCOL_VERSION` passe à 2. Écarté : copier les valeurs sur les entités de l'état (vaisseau, station), et un second canal assumé par ADR. Limite connue : quand ces valeurs deviendront propres à chaque vaisseau (laser, vitesse), elles passeront dans la vue du vaisseau.
8. **Liste des réglages publics :** `jump_ticks`, `mining_rate`, `cargo_capacity`, `tax_rate_bp`.
9. **Accélération hors ligne :** `--periode` au lancement, plus, en cours de partie, des paliers de vitesse, une pause et « avancer jusqu'à la prochaine alerte », hors ligne seulement, par un rappel passé par `__main__.py` à une méthode de `Game`, hors protocole.
10. **Prix :** statu quo en M1 (ore_a 10, ore_b 15). Plus tard, les prix seront fixés par le marché, selon la nature du minerai et la demande, et non selon la distance : un minerai lointain n'est pas forcément plus cher. Le PNJ qui vise le minerai le mieux payé joue moins bien qu'il ne pourrait (ore_a rapporte 1,23 par tick, ore_b 0,93, chiffres vérifiés par simulation : cycle ore_b de 1 611 ticks). C'est accepté et écrit comme tel. Le mode d'attache du PNJ en mode avec horloge (tâche de relais ou `SyncClient`) reste à fixer par l'amendement.
11. **Clavier :** le propriétaire tape en AZERTY. Aucune commande ne doit demander Majuscule ; les chiffres de la rangée du haut ne conviennent donc pas tels quels. Confirmation avant de quitter, puisque quitter met fin à la partie.
12. **Scénarios :** réglages de test explicites, plus un seul scénario sur les vraies valeurs.
13. **Vocabulaire :** l'amendement fixe les nouveaux termes du glossaire (historique, ordre en attente, nom de l'argent, alerte, période nominale…).
14. **Défaut de la touche `v` :** corrigé sans attendre l'amendement, par une petite pull request de fonctionnalité : retour à « vendre le minerai le plus abondant », avec un test qui vérifie le résultat dans `step`. La vente en file arrivera avec l'amendement.

15. **Disposition de l'écran unique :** modulaire. L'écran est fait de cadres indépendants (carte, vaisseau, station, historique, barre d'état, alertes) que l'on peut réarranger, ajouter ou retirer sans réécrire le reste. La disposition définitive n'est pas tranchée : l'amendement fixe une première disposition simple, sans la figer.
16. **Alertes en M1 :** deux seulement, la fin du minage et l'arrivée au point de destination voulu (fin de route, pas chaque saut). La table des alertes sera retravaillée plus tard (dommages, ventes, refus…).
17. **Touches (choix délégué à l'agent, pour un clavier AZERTY, sans Majuscule) :** les actions sont des lettres ; la destination se choisit dans une liste avec les flèches et Entrée, ce qui marche sur toute disposition de clavier ; le minerai par sa lettre (`a`, `b`). Proposition à fixer dans l'amendement : `d` déplacer, `m` miner, `v` vendre, `p` pause, `+` et `-` (ou `=` et `-`, à vérifier en AZERTY) pour la vitesse, Espace pour avancer jusqu'à la prochaine alerte, Échap pour annuler une saisie, `q` puis confirmation pour quitter.

18. **PNJ :** en M1, il reste simple : la politique `scripted_miner` garde sa règle (le minerai le mieux payé à l'unité), même si elle rapporte moins par heure avec les longues durées. C'est la référence scriptée, la base de comparaison des joueurs IA. Plus tard (non-objectif de M1), les PNJ prendront des décisions individuelles, voire collectives : par exemple miner un minerai moins rentable parce que leur corporation en a besoin (corporations prévues à M6).

19. **Tranche 0 agrandie (2026-11-12, pendant la rédaction).** « Sans rentrer dans l'excessif », le propriétaire veut plus de nœuds, plus d'endroits où miner, plus de vaisseaux qui bougent et plus de points de vente. Cela dépasse le CUJ 1 du niveau 1 (« 3 à 5 systèmes reliés en graphe ; deux minerais, et une station PNJ », architecture-niveau-1.md, lignes 102-103) : une ADR 0004, au statut « proposée », élargit ces fourchettes. La décision « Taille de la tranche 0 » du noyau (Technical Plan, point 1) est révisée par l'amendement.
20. **Taille tirée par la graine,** dans des fourchettes fixées par l'amendement : 8 à 12 systèmes en graphe, 4 à 6 gisements, 2 à 3 stations, 2 minerais (inchangé), 3 à 5 PNJ. Le haut de la fourchette demande une carte en graphe à l'écran. Les scénarios et les bornes d'économie doivent valoir pour toutes les tailles.
21. **Plus de vaisseaux qui bougent** = plus de PNJ, chacun avec un vaisseau. Plusieurs vaisseaux pour un même joueur (flotte) restent un non-objectif (hypothèse de l'agent, signalée au propriétaire).
22. **Prix propres à chaque station, fixés par réglage.** Le réglage des prix a autant de lignes que le maximum de stations (3) ; la station k prend la ligne k (règle mécanique, choisie par l'agent). Les prix restent fixes à M1.

23. **Graphe :** un arbre (chaque nouveau système se relie à un système déjà placé), puis quelques liens qui créent des boucles. Écartés : grille partielle, anneau plus cordes.
24. **Règle du PNJ (`scripted_miner`, version 2) :** il vise le minerai qui a le meilleur prix dans une station, mine au gisement non vide le plus proche de ce minerai, et vend à la station qui le paie le mieux. Écartés : « le plus proche », « gisement attitré ». Limite acceptée : les PNJ font le même choix et s'entassent.
25. **Attache du PNJ en mode avec horloge :** tâche de relais (code actuel). Écarté : client synchrone attaché. Limite acceptée : à vitesse élevée, une décision du PNJ peut entrer un ou plusieurs ticks plus tard qu'en mode sans horloge.
26. **Carte à l'écran :** mise en page calculée par le client (colonnes selon la distance en sauts, liens en traits, liens difficiles écrits en texte). Écartés : positions dans l'état, tableau sans dessin.
27. **Visibilité des autres vaisseaux par proximité :** on ne voit un autre vaisseau que s'il est dans le système d'un de ses vaisseaux ou dans un système voisin, et on n'en voit que le système où il est (pas son activité). Plus tard, des scanners porteront plus loin. La carte (systèmes, liens, gisements, stations) reste entièrement visible. Contredit le niveau 1 (ligne 308, classes de visibilité sans notion de distance) : ADR 0005, au statut « proposée ».

28. **Vitesse de l'univers, mode développement seul (2026-11-12, finalisation) :** les paliers, la pause et « avancer jusqu'à la prochaine alerte » n'existent qu'avec l'option `--dev`. En partie normale, l'univers tourne à la période nominale (ou à celle de `--periode`). Rappel : la vitesse de l'univers (secondes réelles par tick) n'est pas la vitesse du vaisseau (ticks par saut, une règle, plus tard propre à chaque vaisseau et à la distance). Idée notée pour plus tard : des événements pendant les trajets.

29. **Écarts de finalisation retenus (2026-11-12) :** `m` mine le gisement du système (un système a au plus un gisement, donc pas de lettre) ; le budget d'actions reste à 1 et 10 ; prix des stations [[10, 15], [12, 12], [8, 18]] ; d'un vaisseau proche, on voit l'identifiant, le propriétaire, le système et la capacité (pas l'activité). Ajouts acceptés : `NOMINAL_TICK_PERIOD_S` dans `schema/protocol.py`, les nouveaux réglages de fourchettes, `Departed` et `Arrived` en `NEARBY`, `Game.set_period`, `npc_count`, `plus_abondant`, bornes du point 27 en formule, scénarios du noyau en attente.

### Options examinées par les revues

1. **Statut pendant la revue de l'amendement.** Les revues recommandent :
   - Proposed et « en revue » sur la branche de la pull request protégée seulement, comme au point 1 du plan détaillé, puis retour à Approved et « approuvé » avant la fusion ;
   - une règle explicite dans le plan : aucune pull request du volet C tant que l'amendement et ses pull requests de scénarios et de fonctionnalité ne sont pas livrés.

   Option inverse : fusionner le statut sur `main`, ce qui gèle tout M1.
2. **`jump_ticks`** : confirmer 400, ou une autre valeur.
3. **Durée de minage et son levier** :
   - au plus 100 ticks, par `mining_rate` seul ;
   - ou au-delà, par un changement d'échelle des unités : capacité, prix, stock, montants des scénarios.
4. **Période nominale** (3 s proposées) et emplacement de son défaut : `--periode` seulement, ou aussi `Game`, ce qui casse tests/server/test_partie.py:46. Faut-il un premier tick immédiat ?
5. **Période de la séance de validation de la boucle** : par exemple accélérée, en sachant que les « 20 minutes » ne seront pas validées en M1.
6. **Taille des fenêtres économiques** : 10 000 ticks (bornes déjà esquissées) ou 20 000. Garder ou changer `regen_ticks`, et dire ce que devient le budget d'actions.
7. **ADR 0003 au statut « proposée »** pour `observe(state, actor_id, tunables)`. Repli : copie dans `State`.
8. **Liste fermée des réglages publics.**
   - Minimum : `jump_ticks` et `mining_rate`.
   - Selon l'affichage : `tax_rate_bp` (montant net), `regen_ticks` (prochaine régénération), `budget_regen` et `budget_max`.
   - À exclure : `ore_prices` et `cargo_capacity`, déjà observés par ailleurs.

   Nom du champ et du type de vue.
9. **Accélération hors ligne.** La revue de simplicité recommande de s'en tenir à `--periode` en M1. Les autres proposent un mécanisme minimal :
   - `Game` reçoit une méthode qui change la période et réveille la boucle tout de suite ;
   - `__main__.py`, seul lieu qui relie serveur et client, passe à `FourxApp` un rappel facultatif ;
   - rien dans le protocole, le journal ou `clients/`.

   À fixer :
   - les paliers (par exemple ×1, ×10, ×100) et une période plancher ;
   - la pause, qui est le même mécanisme à vitesse nulle ;
   - « avancer jusqu'à la prochaine alerte » ;
   - le retour à la vitesse nominale sur une alerte.
10. **PNJ.**
    - En mode avec horloge, l'attacher en `SyncClient` pour qu'une décision prenne toujours exactement un tick ? Aujourd'hui, ses ordres peuvent glisser à vitesse élevée.
    - Face au choix dominant : rééquilibrer `ore_prices` (sans code), écrire une politique attentive au temps (`policy_version` 2), ou garder le statu quo par écrit.
11. **Confirmation des ordres coûteux** et saisie de la destination : flèches et Entrée, lettres, ou chiffres AZERTY acceptés.
12. **Scénarios de partie** : réglages de test explicites, plus un scénario sur les vraies valeurs, ou vrais réglages partout.
13. **Mot pour l'argent** (« solde » ou « Portefeuille »), et termes du glossaire : période de l'horloge, période nominale, partie locale, accélération, ordre en vol, vente prévue, alerte, Historique (cadre du client), Station (cadre), réglages publics.

### Ce que l'amendement doit contenir

- **En-tête et préambule :**
  - la puce « Amendements » ;
  - le tableau des amendements (n°, date, objet, passages touchés, dossier de revue) ;
  - la convention « (amendement 1) » ;
  - la règle « ajouter sans renuméroter ».
- **The Problem :** un paragraphe sur la partie de test du 2026-11-11.
- **Goals :** les objectifs 12 (écran lisible) et 13 (le temps comme ressource). L'objectif 5 est réécrit (fenêtres).
- **Non-Goals :** la liste ci-dessus.
- **Open Questions :** rouverte pendant la revue, vide avant Approved.
- **Technical Plan :**
  - §1 : nouvelles lignes datées ;
  - §2 : réglages ;
  - §5 : `Observation`, réglages publics, `protocol_version` 2 ;
  - §6 : période nominale ;
  - §7 : une ligne de renvoi ;
  - nouveau §7 bis : écran unique, maquettes, tables des touches, des refus et des alertes, modèle client, accélération ;
  - §8 à §10 : fenêtres et bornes ;
  - §12 et §13 : identifiants et interfaces.
- **Alternatives Considered :** les tableaux ci-dessus, et une distinction explicite entre l'accélération locale et l'alternative C.
- **Risks & Mitigations :**
  - la durée des parties manuelles ;
  - l'accélération oubliée ;
  - la dérive entre `tunables.toml`, les tests et le document (option : un test qui compare) ;
  - la file de vente ;
  - le jeu d'attente avec un seul vaisseau ;
  - les conséquences pour M4 ;
  - la veille du portable ;
  - le disque à haute vitesse ;
  - la file de mises à jour sans limite (le client traite toutes les mises à jour mais ne redessine que la dernière).
- **Plan détaillé :**
  - les points 17 et 27 modifiés sur place ;
  - le point 28 bis à remesurer ;
  - une ligne de renvoi dans les points déjà livrés 5, 20, 22 et 23 ;
  - un nouveau volet B bis (points 23 bis et suivants) ;
  - la Verification Plan complétée.
- **Hors du noyau, dans la même pull request protégée :**
  - l'ADR 0003 et l'index des ADR ;
  - le niveau 1, ligne 308, si l'ADR est acceptée ;
  - le glossaire ;
  - `setup.cfg` (`do_not_mutate` pour les nouveaux modules purs du client) ;
  - la feuille de route, sur la branche seulement si la décision 1 suit la recommandation.

### Découpage et ordre de livraison

| Étape | Contenu | Contrainte |
| :-- | :-- | :-- |
| 0. Expérience gratuite | Rejouer avec `python -m fourx --periode 3` sur le client actuel | Tout de suite, pour mesurer la gêne due au seul rythme. Le défaut de vente reste présent. |
| 1. Pull request protégée | Amendement, rapports de revue EGM dans `docs/revues/<date>-niveau-2-m1-noyau-amendement-1/`, glossaire, ADR proposée, `setup.cfg` | Revue EGM complète sans contexte. Le résumé en français va en tête de la description. Fusion par le propriétaire seul. |
| 2. Pull request de scénarios | Réécriture de `partie.feature` avec des scénarios qui distinguent l'ancienne règle de la nouvelle, `ecrans.feature` et ses étapes, import dans `tests/scenarios/test_scenarios.py`, entrées dans `en_attente.txt` | Mesurer la durée de la CI et de la mutation (point 28 bis). |
| 3. Pull request de fonctionnalité, partie règles | `tunables.toml`, `schema/observation.py`, `schema/protocol.py`, `core/observe.py`, `server/game.py`, `__main__.py`, tests non protégés (tests/core/test_versions.py:20, tests/schema/test_schema.py:202, tests/aide_observation.py, tests/server/test_partie.py:46) | Avant le volet C, tant que les références n'existent pas. |
| 4. Pull request de fonctionnalité, partie client | Modèle client pur, écran unique, file de vente, refus, alertes, touches. Réécriture de tests/clients/test_textual_app.py avec `run_test(size=(80, 24))` et des observations fabriquées à des ticks éloignés | Dépend de l'étape 3 pour les durées. Une seule pull request de fonctionnalité ouverte à la fois. |
| 5. Partie d'essai du propriétaire | Verdict « client lisible » et validation de la boucle (objectif 11), à la période fixée par la décision 5 | **Avant la pull request de scénarios du volet C.** Après le volet C, toute retouche de `tunables.toml` impose de régénérer les références et d'augmenter `RULES_REVISION` de un. |
| 6. Volet C | Avec les fenêtres et les bornes de l'amendement | — |

La revue de simplicité propose une variante : livrer tout de suite la file de vente, les refus en français et l'indicateur d'ordre en attente, en client seul et sans attendre l'amendement. Elle s'appuie sur le point 7 actuel, « vendre toute la cargaison » (docs/designs/niveau-2-m1-noyau.md:277). **Le propriétaire doit dire** si cette correction anticipée est permise, compte tenu du statut choisi à la décision 1.

### Ce qui reste supposé

- Aucune revue n'a exécuté de code ni de test. Les listes de tests qui cassent et les numéros de ligne viennent de la lecture du code.
- Les chiffres ont été calculés à la main par les revues, contrairement à la règle « calculer avec un outil ». Ils sont à refaire par script avant d'entrer dans l'amendement : cycles de 810 et 1 614 ticks, première vente au tick 1 612, 5 à 14 ventes par fenêtre de 10 000 ticks, bornes 15 000 à 42 000, revenus par tick de 1,23 et 0,93.
- Le défaut de la vente est dit confirmé par exécution dans le concept. Les revues ne l'ont confirmé qu'à la lecture.
- Plusieurs points restent à vérifier :
  - le gel de l'univers pendant la veille du portable (horloge monotone de `asyncio`) ;
  - la relecture par `msgspec.inspect` d'une métadonnée de visibilité combinée aux `Meta(ge, le)` de `Tunables` ;
  - l'effet de l'AZERTY sur la partie du propriétaire.
- La gêne due au seul rythme n'a pas été mesurée : c'est le rôle de l'étape 0.
