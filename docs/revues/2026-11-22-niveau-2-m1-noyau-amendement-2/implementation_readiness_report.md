# Étape 6 — Préparation à l'implémentation (amendement 2)

**Cible :** `docs/designs/niveau-2-m1-noyau.md` : les passages de l'amendement 2, c'est-à-dire le Technical Plan, points 7 ter (l. 577-614) et 13 (l. 880-887), les objectifs 12 (réécrit), 17 à 19 (l. 169, 178-183), et les points 23 septies à 23 decies (l. 1514-1550). Pièce liée : `docs/adr/0006-client-retro-8-bits.md`.
**Standard appliqué :** `(plugin EGM) distributions/claude/resources/document_standards/implementation-readiness-standard.md`. Règle « zéro décision » : liste des fichiers, étapes exécutables, plan de test.
**Mode :** REVIEW, sans contexte, lecture seule. J'ai lu tous les fichiers demandés.

## Verdict

**Pas prêt.** Un développeur ne peut pas implémenter 23 octies et 23 nonies sans deviner :
- **3 bloquants :** deux données affichées que l'observation ne contient pas, et une disposition par forces dont la garantie centrale n'a pas d'algorithme.
- **12 majeurs.**
- **8 détails.**

Le point 23 octies est le plus exposé. C'est une pull request de scénarios protégée, écrite avant le code : elle a besoin de sorties observables fixées (`Step`, `help_pages`), et le texte ne les donne pas.

**Ce qui est vérifié et tient :**
- **Types cités :** `SystemView`, `Observation`, `ClientModel`, `public_tunables`, `distances`, `most_abundant` existent (`src/fourx/schema/observation.py:15-78`, `src/fourx/clients/model.py:52`).
- **Version de Textual :** 8.2.8, comme le cite l'ADR 0006 (`uv.lock:1041-1042`, `pyproject.toml:7`).
- **Contrats d'imports :** ils permettent à `clients` d'importer `schema`, `policies` et Textual (`.importlinter:48-56`).
- **Déterminisme statique :** le test ne lit que `src/fourx/core` (`tests/core/test_determinisme_statique.py:12,129`). Les flottants de `force_layout` sont donc permis.
- **Sites par système :** au plus une station et un gisement par système (`src/fourx/core/world.py:58-66`, `_placer` retire le système choisi). Le singulier « son gisement, sa station » est donc juste.
- **Scénarios avant le code :** les étapes importent le code à l'intérieur des fonctions (`tests/scenarios/steps/steps_ecrans.py:7-8`). Un scénario neuf échoue proprement sur le code de l'amendement 1 et peut aller dans `en_attente.txt`.
- **Suppression de `map_layout.py` :** `mutation.py` ne compte pas un fichier supprimé comme un échec (`.github/scripts/mutation.py:144-145, 185-189`).

---

## Bloquants

### B1. La barre du haut affiche la graine, que le client ne reçoit pas
- **Passage :** l. 583, « En haut, une barre : tick, durée de jeu estimée, solde, graine ».
- **Problème :**
  - `Observation` n'a aucun champ de graine (`src/fourx/schema/observation.py:65-78`).
  - `FourxApp(connection, actor_id, set_speed)` ne la reçoit pas non plus (`src/fourx/clients/textual_app.py:59-64` ; Technical Plan 13, l. 867).
  - Le Technical Plan, point 6, l. 512, l'interdit : « Ils restent hors de l'écran de jeu : le client ne reçoit du jeu que l'observation (niveau 1, §5 ; ADR 0003) ».
  - 7 ter dit aussi « Rien ne change dans le protocole, l'observation » (l. 579).
  - Pour l'afficher, il faudrait changer `FourxApp` et `__main__.py`, que 23 nonies ne liste pas, et rompre une règle en vigueur.
- **Proposition :** retirer la graine de la barre. Ou bien, si le propriétaire la veut, l'écrire comme une seconde exception locale (paramètre `world_seed` de `FourxApp`, passé par `__main__.py`, retiré à M3). Il faut alors amender l. 512, l. 867 et la liste des fichiers de 23 nonies.

### B2. Le Marché « rappelle la taxe », que l'observation ne contient pas
- **Passage :** l. 607, « la taxe est rappelée ».
- **Problème :**
  - Le taux (`tax_rate_bp`, `src/fourx/core/tunables.toml:9`) n'est pas dans `PublicTunablesView` (`src/fourx/schema/observation.py:58-62`).
  - `Sale` ne porte que le montant (`src/fourx/schema/events.py:53-59`), et seulement dans l'observation du tick de la vente.
  - L'objectif 14 dit que la taxe passe par l'événement de vente, et sa vérification exige qu'« aucun autre réglage n'apparaisse dans l'observation ».
  - Avant la première vente, le client ne peut donc rien rappeler.
- **Proposition :** au choix, avec la décision écrite :
  - (a) supprimer « la taxe est rappelée » ;
  - (b) afficher « taxe de la dernière vente : N », lue dans l'historique ;
  - (c) ajouter `tax_rate_bp` aux réglages publics, ce qui demande une nouvelle ADR et `PROTOCOL_VERSION` 3, contre le « rien ne change » de l. 579.

### B3. La disposition par forces : aucun paramètre fixé, et une garantie sans algorithme
- **Passage :** l. 585, « répulsion en 1/d², un ressort de longueur fixe […] un faible rappel vers le centre, avec un pas qui décroît […] Deux systèmes sont toujours à une distance d'au moins 0,08 ».
- **Problème :**
  - **Constantes absentes :** constante de répulsion, longueur et raideur du ressort, force du rappel, pas initial et loi de décroissance, rayon, centre, angle de départ et sens du cercle.
  - **Mise dans [0, 1]² non dite :** rien ne dit si l'on recadre sur la boîte englobante (ce qui déforme le rapport d'aspect) ou si l'on applique une échelle uniforme avec marge.
  - **Garantie de 0,08 sans mécanisme :** l'algorithme décrit ne garantit pas une distance minimale. Aucune passe de correction n'est prescrite, et le texte ne dit pas quoi faire si un test de propriétés trouve une graine fautive.
  - Le développeur devrait donc concevoir puis régler l'algorithme jusqu'à ce que les tests passent : c'est une décision de conception.
- **Preuve :** aucune fonction de ce type dans le code. `src/fourx/clients/map_layout.py:23-37` est un placement en colonnes, sans rapport.
- **Proposition :**
  - fixer les constantes, par exemple `K_REP`, `L0`, `K_RESSORT`, `K_CENTRE`, `PAS0` et décroissance linéaire jusqu'à 0 sur 300 itérations, centre (0,5 ; 0,5), rayon 0,4, angle de départ et sens ;
  - fixer la normalisation : échelle uniforme dans [0,05 ; 0,95]² ;
  - ajouter une passe finale déterministe qui écarte chaque paire sous 0,08, par identifiants croissants, avec un nombre de passes borné, puis renormaliser ;
  - ou bien ramener la garantie à « vérifiée sur les graines 1 à N » et dire ce qui se passe en cas d'échec.

---

## Majeurs

### M1. `Step` : aucune sortie observable fixée ; ni `test_guide.py` ni le scénario du cycle ne peuvent s'écrire
- **Passages :** l. 595-603 et l. 881 (`Step(title, detail, keys)`) ; l. 1532 (« la prochaine étape suit un cycle joué ») ; l. 1545 (`test_guide.py`, « les sept règles »).
- **Problème :**
  - Aucun titre ni détail n'est donné mot pour mot.
  - Le format de `keys` n'est pas dit : nom de touche Textual (`"enter"`, `"d"`) ou libellé (`"Entrée"`) ?
  - Les touches des règles 2 et 3 ne sont pas données (vide ? `c` ?).
  - Le scénario protégé, écrit avant le code, ne sait donc pas quoi affirmer à chaque étape du cycle.
  - Il doit en outre acquitter les alertes : la règle 1 l'emporte à chaque arrivée et à chaque fin de minage (`model.py:149-151`, `207`, `216`). La suite attendue n'est pas donnée.
- **Proposition :** fixer, pour chaque règle, `title`, le gabarit de `detail` et `keys`, en noms de touches Textual. Écrire la suite attendue du scénario, par exemple : règle 7 `("d",)` → règle 2 `()` → règle 1 `("enter",)` → règle 6 `("m",)` → règle 3 `()` → règle 1 → règle 5 `("d",)` → règle 2 → règle 1 → règle 4 `("v",)`. Dire où `Step` est défini (`clients/guide.py`, `@dataclass(frozen=True)`).

### M2. `next_step` : cas limites et départages non traités
- **Passages :** l. 595-603 ; objectif 18, l. 180.
- **Problème :**
  - `observation is None`, ou aucun vaisseau (`model.vaisseau()` peut rendre `None`, `model.py:77-81`) : que rendre ?
  - Un ordre envoyé sans résultat (`model.pending`) : la règle 7 conseille alors de renvoyer le même ordre.
  - Règle 4 : le texte ne dit pas de quel minerai sont « le prix d'ici et le meilleur prix ailleurs » quand la cargaison est mêlée.
  - Règles 5 et 7 : aucun départage, ni à prix égal ni à distance égale. La règle 7 n'a pas de repli quand tous les gisements du minerai le mieux payé sont connus vides, ni quand aucun ne convient. La politique du PNJ, elle, en a (l. 525).
  - Règle 3 : « soute pleine dans n ticks » alors que `remaining_ticks` peut annoncer la fin par stock épuisé (`model.py:137-146`).
  - L'objectif 18 promet « sa durée », que les règles 4 et 6 ne donnent pas.
  - `next_step(observation, model)` est redondant avec `model.observation` et contredit « à partir de l'observation seule » (l. 180).
- **Proposition :**
  - ajouter une règle 0 (« en attente du premier tick ») et une règle « ordre envoyé : attendre le résultat » ;
  - reprendre les départages du PNJ (l. 524-525) : plus proche en sauts, puis plus petit identifiant, et repli sur l'autre minerai, puis « aucun gisement connu non vide » ;
  - règle 4 : le minerai le plus abondant (`most_abundant`) ;
  - réduire la signature à `next_step(model: ClientModel) -> Step`.

### M3. L'aide : contenu non fixé ; durée du minage hors de `public_tunables` ; aide ouverte avant le premier tick
- **Passages :** l. 610 ; objectif 19, l. 182-183 ; l. 1532 (« l'aide donne les durées des réglages publics ») ; l. 883.
- **Problème :**
  - Aucun texte n'est donné, ni le nombre de lignes par page.
  - La durée de « miner » (remplir la soute) vaut `capacity ÷ mining_rate`, or `capacity` est dans `OwnShipView` et non dans `public_tunables` (`observation.py:42, 58-62`).
  - L'aide s'ouvre « au lancement », mais `on_mount` tourne avant toute observation (`textual_app.py:89-91` ; `frames.py:20`, `ATTENTE`). `help_pages(observation: Observation)` n'accepte pas `None`.
  - Le scénario ne sait pas quoi affirmer : `duration_text(jump_ticks)` ? `duration_text(capacity // mining_rate)` ?
- **Proposition :**
  - donner le texte des deux pages, ou au minimum les lignes contractuelles, par exemple « transporter : un saut dure {duration_text(jump_ticks)} » et « miner : remplir une soute vide prend {duration_text(⌈capacity ÷ mining_rate⌉)} » ;
  - dire d'où vient `capacity` ;
  - passer la signature à `help_pages(observation: Observation | None)`, avec un texte sans durées tant qu'aucune observation n'est arrivée ;
  - fixer l'assertion du scénario.

### M4. Mutation : le score de `texts.py` ne doit pas baisser, et les textes de l'aide le feront baisser
- **Passages :** l. 1541 (`texts.py` (Modify) : `help_pages`) ; l. 1545 (« test_texts.py (aide, durées) »).
- **Problème :**
  - `texts.py` est déjà muté. Le contrôle échoue si son score baisse par rapport au commit de base (`.github/scripts/mutation.py:146-147`).
  - mutmut mute les chaînes littérales. Des pages d'aide testées seulement sur leurs durées laisseraient survivre tous les mutants de texte, et la pull request 23 nonies échouerait.
  - L'usage du dépôt est d'affirmer les textes mot pour mot (`tests/clients/test_texts.py:69, 114, 151`).
- **Proposition :** fixer les textes de l'aide dans le document (voir M3) et exiger que `test_texts.py` compare les pages en entier. Ou bien loger l'aide dans un module neuf, sans score de base, ce qui change l. 883.

### M5. La logique de la carte tombe dans `frames.py`, exclu de la mutation
- **Passages :** l. 587-593 et l. 1542 (`MapView` dans `frames.py`) ; l. 579 (« Les modules purs nouveaux sont testés sans Textual et mutés »).
- **Problème :**
  - `frames.py` est dans `do_not_mutate` (`setup.cfg:17-20`, recopié dans `tests/outillage/test_mutation.py:24-27`).
  - Or `MapView` porte de la vraie logique : projection [0,1]² vers les pixels, bornes du zoom, déplacement de la vue, recherche du système sous le curseur pour le survol et le clic, fraction du saut, portée et halo, choix des ★ du Marché, barres de progression.
  - Le texte ne dit pas de l'extraire. Elle échapperait donc à la mutation, ce qui va contre l'intention de 7 ter.
- **Proposition :** ajouter un module pur et muté, par exemple `clients/map_view.py`, avec ses signatures (projection, `hit_test`, `zoom_suivant`, `grille(...)`, qui rend des cases (caractère, avant-plan, arrière-plan)). `frames.py` ne ferait plus que peindre. Aucun changement de `setup.cfg` n'est alors nécessaire. S'il en fallait un, ce serait dans 23 octies, chemin protégé (`.github/chemins-proteges.txt:26`).

### M6. La vérification automatique de l'objectif 12 n'est plus testable telle qu'écrite
- **Passage :** l. 169, « au besoin après défilement du cadre Carte : le test lit le contenu du cadre ».
- **Problème :**
  - La carte ne défile plus : elle se zoome et se déplace.
  - Le test actuel lit `#carte-texte` et cherche `[id]` (`tests/clients/test_textual_app.py:409-411`). Une toile en demi-blocs n'a pas de « contenu » textuel exploitable.
  - « Où se trouve chaque minerai » n'est donné, au zoom ×1, que par la couleur d'un losange (l. 589), que le test ne peut pas lire en texte.
- **Proposition :** dire comment le test lit la carte, par exemple par la `grille(...)` pure de M5, avec le style de chaque case ; ou affirmer à partir du zoom ×2, où les noms et les sites s'écrivent. Réécrire l. 169 en conséquence.

### M7. Le Journal veut des étiquettes par type, et l'historique n'est fait que de chaînes
- **Passage :** l. 608, « une étiquette colorée par type (ordre, vente, alerte, refus) ».
- **Problème :**
  - `ClientModel.history` est un `tuple[str, ...]` sans type (`model.py:61, 74-75, 151, 183, 186, 198`).
  - Il faudrait soit relire les chaînes (fragile), soit changer l'interface de `ClientModel`. Celle-ci est fixée au Technical Plan 13, l. 876, que l'amendement 2 ne touche pas, et `model.py` n'est pas dans la liste de 23 nonies.
- **Proposition :** décider. Par exemple : `history: tuple[HistoryEntry, ...]`, avec `HistoryEntry(tick: int, kind: Literal["ordre","vente","alerte","refus"], text: str)`. Il faut alors amender l. 876, ajouter `model.py` et `test_model.py` à 23 nonies, et vérifier l'étape `historique_refus` (`steps_ecrans.py:148-151`, qui fait `in ligne` sur des chaînes), un chemin protégé que 23 octies devrait alors adapter.

### M8. Disposition : la place des cadres existants n'est pas reprise
- **Passages :** l. 583 ; l. 887 (« barre d'état, alerte ») ; l. 1543.
- **Problème :** la nouvelle disposition ne place que la barre du haut, la carte, Prochaine étape, Vaisseau, Marché, le Journal et la barre des touches. Elle ne dit pas :
  - où va le cadre Alerte (aujourd'hui au-dessus de l'historique, `textual_app.py:51, 80-81`) ;
  - où va la liste des destinations, qui remplace aujourd'hui l'historique (`textual_app.py:127-132`). Avec un Journal de quatre lignes, la fenêtre de la liste ne montrerait que trois lignes (`frames.py:132`) ;
  - où va la ligne d'aide ou d'invite (`AIDE`, `AIDE_LISTE`, `QUITTER`), aujourd'hui seconde ligne de `#barre` (`frames.py:142-153`). Le texte parle à la fois d'une « barre » en haut et d'une « barre des touches » en bas.
  - Les identifiants des widgets, sur lesquels les tests s'appuient (`#stations`, `#historique`, `#barre`), ne sont pas fixés non plus.
- **Proposition :** une maquette en texte, ou un tableau, qui donne pour chaque widget son identifiant, sa position et sa taille en 120 × 36, avec la place de l'alerte, de la liste des destinations et de la ligne d'invite.

### M9. Le clic sur un système renvoie à une « confirmation » qui n'existe pas
- **Passage :** l. 593, « la confirmation du déplacement s'ouvre, comme après `d` et le choix de ce système ».
- **Problème :**
  - Après `d`, Entrée envoie l'ordre directement, sans étape de confirmation (`textual_app.py:211-221`).
  - Le texte ne traite pas : le clic sur le système du vaisseau (refus `ALREADY_THERE`), le clic pendant une saisie ouverte ou pendant que l'aide est affichée, le clic pendant un saut (refus `SHIP_EN_ROUTE`), ni le seuil qui distingue un clic d'un glisser (bouton gauche dans les deux cas, l. 592).
- **Proposition :**
  - « le clic ouvre la liste des destinations (`saisie = "destination"`), la ligne de ce système choisie ; Entrée confirme » ;
  - le clic est ignoré si une saisie ou l'aide est ouverte ;
  - un glisser commence après un déplacement d'au moins une case entre `MouseDown` et `MouseUp`.

### M10. L'aide : son rôle de saisie et la priorité des touches ne sont pas dits
- **Passages :** l. 610 (« Entrée la ferme, et les flèches changent de page ») ; l. 612 (les flèches déplacent la vue quand aucune saisie n'est ouverte).
- **Problème :**
  - Entrée acquitte d'abord une alerte, avant toute saisie (`textual_app.py:153-155`). Avec l'aide ouverte et une alerte en attente, Entrée acquitte au lieu de fermer.
  - Le texte ne dit pas si l'aide compte comme une saisie (flèches : page ou vue ?), quelles flèches changent de page, ni si l'on boucle.
  - Il ne dit pas non plus si `h` referme l'aide, si Échap la ferme, ni si `d`, `m`, `v` ou `q` agissent pendant qu'elle est ouverte.
  - Il ne dit pas si l'aide est un `ModalScreen` de Textual, auquel cas `App.on_key` ne reçoit plus les touches, ou un widget superposé.
  - Enfin, les tests existants (`test_textual_app.py:134-418`) appuient sur des touches dès le lancement : le texte ne dit pas qu'ils doivent d'abord fermer l'aide.
- **Proposition :** fixer une table : l'aide est une saisie `"aide"` ; Entrée et Échap la ferment, avant les alertes ; ← → changent de page sans boucler ; `h` la referme ; toute autre touche affiche la ligne d'aide. Fixer aussi le type de widget, et le fait que chaque test ferme l'aide avant d'agir.

### M11. Zoom, vue, mini-carte et étiquettes : des valeurs non fixées
- **Passages :** l. 591-592.
- **Problème :**
  - **Pas du zoom :** par pas de 1,25 depuis ×1, on n'atteint ni ×2 ni ×4 (1,95 puis 2,44 ; 3,81 puis 4,77). Faut-il borner à 4 ? Le seuil « à partir de ×2 » tombe donc à 2,44.
  - **Vue :** le texte ne fixe ni le point d'ancrage du zoom (curseur ou centre), ni le pas des flèches, ni les bornes du déplacement, ni la vue initiale.
  - **Projection :** il ne fixe pas le rapport d'aspect (une case fait environ deux demi-pixels de haut), donc pas la projection du carré [0,1]² sur une carte d'environ 70 × 30 cases.
  - **Mini-carte :** taille et position non dites.
  - **Étiquettes :** il ne dit pas comment éviter qu'elles se chevauchent au zoom ×2 (« system_12 », station, prix, gisement, stock, sur 0,08 × 2 × 70 ≈ 11 colonnes).
  - **Dessin :** motif des pointillés et des tirets, ordre de dessin (liens, route, systèmes, vaisseaux, étiquettes), forme du halo et de la pastille.
- **Proposition :**
  - une table `ZOOMS = (1.0, 1.25, 1.6, 2.0, 2.5, 3.2, 4.0)` ;
  - zoom centré sur le curseur, ou sur le centre de la vue au clavier ;
  - pas de vue de 10 % de la zone visible, vue bornée au carré, vue initiale centrée à ×1 ;
  - projection à échelle uniforme ;
  - mini-carte de 12 × 6 cases en bas à droite ;
  - au zoom ×2, étiquettes tronquées à la place libre ;
  - ou bien dire explicitement que ces choix visuels sont laissés au développeur et validés à la partie d'essai (23 decies).

### M12. Le temps de rendu et le plan de vérification ne sont pas suivis
- **Passages :** l. 614 et l. 1150 (« mesuré au plan détaillé, point 28 bis ») ; Verification Plan, l. 1710 et 1712.
- **Problème :**
  - Le point 28 bis (l. 1607-1612) n'a aucun ajout de l'amendement 2 : ni méthode, ni graine, ni palier, ni seuil, ni conduite en cas de dépassement.
  - Le Verification Plan cite encore `map_layout.py` muté (l. 1710) et des mesures de « part des liens tracés et hauteur de la carte » publiées au compte rendu (l. 1712), impossibles une fois `map_layout.py` supprimé (l. 1544).
  - L'amendement 2 n'y ajoute rien pour ses propres tests.
- **Proposition :** ajouter une puce « Proposed Changes (amendement 2, ajout) » au point 28 bis (mesure du rendu au palier ×100, script, seuil et signalement), et un bloc « (amendement 2) » au Verification Plan, qui remplace l. 1710 et 1712 : modules mutés, mesures de la disposition (distance minimale observée) publiées au compte rendu.

---

## Détails

- **D1. Portée calculée par le client** (l. 588-589, liens pleins et halo).
  - *Problème :* `core.observe.portee` existe (`src/fourx/core/observe.py:92-98`), mais `clients` ne peut pas importer `core` (`.importlinter:52-53`). Le texte ne dit pas où la recalculer.
  - *Proposition :* `portee(systems, systemes_propres) -> frozenset[int]` dans `policies/geometry.py`, à ajouter à 23 nonies avec son test, ou dans `clients/map_view.py`.
- **D2. Vaisseau pendant un saut** (l. 590).
  - *Problème :* le lien suivi n'est pas nommé.
  - *Preuve :* pendant un saut, `system_id` reste le système de départ et `route[0]` est le suivant (`src/fourx/core/step.py:255-256, 331-344`).
  - *Proposition :* écrire « le long du lien `system_id` → `route[0]` », avec la fraction donnée ; dire aussi ce que fait `c` pendant un saut.
- **D3. Titres des scénarios** (l. 1532-1534).
  - *Problème :* `en_attente.txt` attend des titres exacts (`tests/scenarios/conftest.py:57-60`). Les deux scénarios neufs n'ont pas de titre, et le titre réécrit est donné en minuscule. « Toujours les mêmes » : deux appels dans le même processus, ou deux sous-processus sous `PYTHONHASHSEED` ?
  - *Proposition :* donner les trois titres exacts et la méthode. L'étape `carte_complete` (`steps_ecrans.py:245-275`) disparaît.
- **D4. Tests de propriétés de la disposition** (l. 1545).
  - *Problème :* rien n'est fixé : réglages (8 à 12 systèmes de `tunables.toml`, ou 12 imposés), `max_examples`, conversion `core.state.System` → `SystemView`. Ces tests tournent aussi sous mutmut : la marque `proprietes` n'est pas exclue (`setup.cfg:9-10`).
  - *Proposition :* fixer ces trois points et borner le coût.
- **D5. Déterminisme des flottants.**
  - *Problème :* le texte ne dit pas que l'invariant ne vaut que pour `core` et que la disposition n'entre dans aucune empreinte.
  - *Proposition :* l'écrire, et interdire aux tests de comparer des positions à des valeurs flottantes écrites en dur entre machines.
- **D6. Palette** (l. 581-582).
  - *Problème :*
    - les clés de `PALETTE` ne sont pas données (« panneau clair » ? `panel_light` ?) ;
    - « chaque couple texte et fond employé » n'est pas énuméré, et la couleur des systèmes et vaisseaux « atténués » n'est pas nommée. Si c'est « trait fort » `#5A6796` sur le fond `#0B0E1A`, le contraste fait environ 3,5:1 (mon calcul), sous 4,5:1 ;
    - « lisible en 256 couleurs » n'est vérifié par rien ;
    - si `palette.py` ne contient qu'une constante, il n'a aucun mutant et n'aura pas de score (`mutation.py:92-97`), ce qui est acceptable.
  - *Proposition :* fixer les clés, la liste des couples testés et la couleur des éléments atténués.
- **D7. Marché et Vaisseau** (l. 606-607).
  - *Problème :* ★ en cas d'égalité de prix ? Largeur et glyphes des barres de progression : ▀ et ▄ sont des moitiés haute et basse, pas gauche et droite.
  - *Proposition :* « ★ sur chaque station à égalité » ; une largeur fixe et des glyphes précis.
- **D8. Valeurs encore libres.**
  - *Problème :* le texte de l'écran « agrandir la fenêtre » (l. 583) et le comportement des touches sous 100 × 30 ; la « durée de jeu estimée » de la barre (l. 583), sans formule ; la condition « la carte n'est redessinée que si… » (l. 614), sans critère vérifiable, l'observation changeant à chaque tick ; des passages devenus caducs mais non marqués : risque l. 1138 (« rang du parent »), l. 535 (« stations, historique ») et alternative AE l. 1093.
  - *Proposition :* donner le texte et le comportement de la petite fenêtre ; une formule pour la durée, par exemple `duration_text(tick)` sans la partie ticks ; la clé de cache de la carte (zoom, vue, taille, `observation.tick`) ; marquer les passages caducs comme remplacés.

---

## Fichiers à créer, modifier ou supprimer : ce qui manque à 23 nonies

- **Manquent si B1 et M7 sont tranchés comme proposé :** `src/fourx/__main__.py`, `src/fourx/clients/model.py`, `tests/clients/test_model.py`, `tests/test_point_d_entree.py`.
- **Manque si M5 est retenu :** le module pur de la carte, avec son test.
- **Manque si D1 est retenu :** `src/fourx/policies/geometry.py` et `tests/policies/test_geometry.py`.
- **`frames.py` :** il faut lui retirer l'import de `map_layout` (`src/fourx/clients/frames.py:13`). Ce n'est pas dit, mais cela découle de la suppression.
- **Documents :** le point 28 bis et le Verification Plan (M12) devraient être amendés dans 23 septies.

## Fichiers lus

- **Document et ADR :** `docs/designs/niveau-2-m1-noyau.md`, `docs/adr/0006-client-retro-8-bits.md`.
- **Client :** `src/fourx/clients/{model,map_layout,texts,frames,textual_app}.py`.
- **Formats et noyau :** `src/fourx/schema/{observation,events}.py`, `src/fourx/core/{world,step,observe}.py`, `src/fourx/core/tunables.toml`.
- **Scénarios :** `tests/scenarios/ecrans.feature`, `tests/scenarios/steps/steps_ecrans.py`, `tests/scenarios/conftest.py`.
- **Tests :** `tests/clients/test_textual_app.py`, `tests/clients/test_texts.py`, `tests/proprietes/test_proprietes.py`, `tests/core/test_determinisme_statique.py`, `tests/outillage/test_mutation.py`.
- **Configuration et outillage :** `setup.cfg`, `.importlinter`, `.github/chemins-proteges.txt`, `.github/scripts/mutation.py`, `pyproject.toml`, `uv.lock`.

Aucun fichier n'a été modifié.
