# Étape 8 — prise de recul intermédiaire

*   **Document :** `docs/designs/niveau-2-m1-noyau.md`, version révisée du 2026-11-06 (765 lignes), après la résolution des étapes 5 à 7 (`resolution_etapes_5-7.md`).
*   **Date :** 2026-11-06.
*   **Relecteur :** `egm-zoom-out`, sans contexte, standard `zoom-out-standard`. Contexte lu : niveau 1 (§1 à §7, §10, §11, alternative R), niveau 2 de M0 (lignes 286, 541, 564), `CLAUDE.md` (circuit des pull requests), `.github/chemins-proteges.txt`, `.github/workflows/ci.yml`, `pytest.ini`, `.importlinter`. Interrompu une fois par la limite d'usage, puis repris là où il s'était arrêté.
*   **Vérification de l'agent de code :** B1 relu aux lignes 472, 487 et 615 : `tests/proprietes/conftest.py` est déclaré protégé au palier 2, mais créé au point 19 (pull request de fonctionnalité du volet A), et `pytest.ini` choisit le profil dès le palier 2. Il n'existe pas de `tests/conftest.py` dans le dépôt. Constat confirmé.
*   **Verdict du relecteur :** le document reste le plus petit M1 compatible avec le niveau 1 : la révision n'a pas ajouté de fonction spéculative. Il n'est pas encore exécutable sans décision ouverte, à cause du conflit sur le conftest de `hypothesis` (B1), et la nouvelle partie de référence, les formats et les contrôles qui l'entourent demandent sept corrections ciblées.

## Constats

### B1 : le profil `hypothesis` est un chemin protégé, créé dans une pull request de fonctionnalité
- **Lignes :** 472 (point 4), 487 (point 7), 615 (point 19).
- **Description :**
  - le point 4 (palier 2) ajoute `tests/proprietes/conftest.py` aux chemins protégés ;
  - ce fichier n'est créé qu'au point 19, dans la pull request de fonctionnalité du volet A ;
  - or une pull request de fonctionnalité ne touche aucun chemin protégé, sauf `tests/references/` (`CLAUDE.md` ; document, ligne 676) ;
  - en plus, `pytest.ini` active `--hypothesis-profile=ci` dès le palier 2, avant que le profil existe.
- **Effet probable (à vérifier) :** le plugin `hypothesis` charge le profil à la configuration. Or `tests/proprietes/conftest.py` n'est pas un conftest initial : il ne se charge pas quand la tâche obligatoire `tests-outillage` lance `pytest tests/outillage`. Cette tâche passerait donc au rouge dès le palier 2.
- **Raison :** le document se veut exécutable par un agent sans décision ouverte (ligne 40). Ici, l'agent doit choisir entre violer le circuit des pull requests et ne pas livrer.
- **Correction :** enregistrer le profil dans `tests/conftest.py`, créé au palier 2 dans la pull request protégée, avec `pytest.ini`. Ce conftest racine est chargé par toutes les commandes. Protéger ce chemin au point 4, à la place de `tests/proprietes/conftest.py`, et retirer le conftest du point 19.

### M1 : le report de la relecture de nuit de la protection repose sur une raison non vérifiée
- **Lignes :** 85, 128, 432.
- **Description :**
  - le document de M0 (approuvé, lignes 541 et 564) fait de cette relecture la parade du risque « une exception d'amorçage se rouvre » ;
  - le report repose sur « à vérifier » ;
  - la relecture manuelle unique du point 31 ne remplace pas une relecture chaque nuit ;
  - le jalon qui reprendra le contrôle est laissé au propriétaire (ligne 85), alors que la ligne 92 dit qu'il n'y a aucune question ouverte ;
  - les lignes 85 et 432 donnent deux conditions de reprise différentes (le choix d'un jalon, puis le choix d'un jeton).
- **Raison :** c'est une réduction silencieuse d'une parade approuvée. Elle est peut-être évitable : selon le relecteur, la route `GET /repos/{owner}/{repo}/branches/main` renvoie, sans droit d'administration, `protection.required_status_checks.contexts` et `enforcement_level` (`everyone` quand les administrateurs sont inclus). Ce point est à vérifier.
- **Correction :**
  - vérifier cette route ;
  - si elle suffit : une tâche `protection` dans `nuit.yml`, sans secret, qui compare ces champs à `.github/protection-main.json` ;
  - sinon : garder le report, en faire une question ouverte avec une seule condition de reprise, et noter dans le plan l'écart avec M0. Y noter aussi l'écart sur `tests-outillage`, qui « devient `tests` » selon M0, ligne 286.

### M2 : les refus de la réception sont journalisés, mais un ordre illisible ne peut pas l'être
- **Lignes :** 123, 161, 254, 575, 636.
- **Description :**
  - `RefusalCode` contient « format invalide ». Un message non décodable n'a ni `actor_id`, ni numéro, ni place dans l'ordre (acteur, numéro) de `step` ;
  - le journal doit en outre porter un champ « code de la réception » que `step` croit sans le revérifier : c'est un second chemin de validation dans un format persistant.
- **Raison :** le cas limite n'est pas couvert, et la solution est plus large que nécessaire.
- **Correction (plus simple) :**
  - la réception ne fait que décoder et lier le point de connexion à son acteur. Les ordres décodés vont au journal, bruts, avec l'acteur du point de connexion ;
  - `step` appelle lui-même `validate_orders` (dans `schema`, pure), puis fait la validation d'état. Le rejeu reproduit ainsi les refus sans champ ajouté ;
  - pour un message non décodable, dire explicitement ce qu'il devient : un refus attribué à l'acteur du point de connexion, avec un numéro réservé, ou un abandon, accepté à M1.

### M3 : en mode sans horloge, rien ne dit comment le PNJ répond
- **Lignes :** 126, 252, 639, 683, 694.
- **Description :**
  - le mode sans horloge est synchrone ;
  - or la partie de référence fait jouer les PNJ « par le protocole », c'est-à-dire par des `asyncio.Queue`, en mode sans horloge ;
  - rien ne dit comment l'hôte des PNJ reçoit la mise à jour et renvoie ses ordres entre deux ticks synchrones ;
  - pourtant, les bornes économiques supposent exactement un tick de délai par décision.
- **Raison :** c'est un trou d'interface qui touche directement les références et les fourchettes.
- **Correction :** fixer qu'en mode sans horloge, après chaque mise à jour, le serveur appelle une méthode synchrone de chaque client en mémoire (par exemple `NpcHost.respond(TickUpdate) -> SubmitOrders`), et que ces ordres entrent au tick suivant.

### M4 : les empreintes de référence ne sont gardées que tous les 1 000 ticks
- **Lignes :** 48, 677, 684 ; niveau 1, §2 et CUJ 4.
- **Description :**
  - l'objectif 2 promet « les mêmes empreintes, tick par tick », mais `reference.json` ne garde les empreintes que tous les 1 000 ticks ;
  - quand `test_rejeu` échoue en CI, la référence n'est pas un dossier de partie : `divergence.py` ne peut pas la lire, et la localisation s'arrête à une fenêtre de 1 000 ticks ;
  - le scénario du CUJ 4 (ligne 662) ne couvre qu'une partie fabriquée pour le test.
- **Correction :**
  - dans la tâche `rejeu`, comparer aussi, tick par tick, les empreintes des deux rejeux faits sous `PYTHONHASHSEED=0` et `1`. C'est la vraie preuve demandée par le niveau 1, et `divergence.py` sait déjà comparer deux suites ;
  - comparer à la référence aux points d'échantillonnage ;
  - écrire dans l'objectif 2 que la référence est comparée tous les 1 000 ticks, et donner la commande qui localise ensuite le tick exact, rejeu contre rejeu.

### M5 : la partie de référence crée un second format de journal et un second chemin de rejeu
- **Lignes :** 125, 273, 677, 684.
- **Description :**
  - `ordres.jsonl` est un deuxième format du journal des ordres, à côté de `OrderLog` en SQLite, sans `order_log_schema_version`. Cela contredit l'objectif 7 et le niveau 1, §7 ;
  - `test_rejeu.py` réimplémente le rejeu au lieu de réutiliser `tools/replay.py`, et part « de l'état généré par la graine 1 » au lieu d'un instantané ;
  - la rétention des dossiers `rules-<révision>/` n'est pas dite. Estimation du relecteur : environ 30 000 ordres sur 100 000 ticks, soit quelques Mo par révision gardée dans le dépôt.
- **Raison :** la proposition (rejouer par `step` seul) est bonne, mais elle duplique un format et un outil.
- **Correction :**
  - enregistrer la référence au format d'un dossier de partie : instantané initial, plus le journal ou un export versionné de celui-ci ;
  - la rejouer avec `fourx.tools.replay` ;
  - dire qu'une régénération remplace le dossier de la révision précédente (l'historique git le garde), sauf si le niveau 1, §7 (« rangées par `rules_version` »), impose de les garder. Dans ce cas, le dire et chiffrer la taille.

### M6 : l'instantané ne porte pas toutes ses versions
- **Lignes :** 256, 599, 609 ; niveau 1, §3.
- **Description :** le niveau 1 exige que l'instantané porte `snapshot_schema_version`, `rules_version` et l'empreinte du commit. Le document ne donne que `snapshot_schema_version`, et `test_versions.py` ne vérifie qu'« un champ de version ».
- **Raison :** c'est une exigence du niveau 1, sur un format persistant.
- **Correction :** ajouter `rules_version`, le SHA du commit et l'indicateur « dossier de travail modifié » à `Snapshot`. Le serveur les fournit, puisque le noyau n'appelle pas git. Les faire vérifier par `test_versions.py`.

### M7 : le seul contrôle de la montée de révision vit hors des chemins protégés
- **Lignes :** 685, 274.
- **Description :**
  - `tests/rejeu/test_revision.py` est le seul mécanisme qui applique la règle du niveau 1, §3 (« un contrôle CI exige que ce numéro augmente ») ;
  - il n'est pas protégé. La pull request de fonctionnalité qui régénère les références a le droit de toucher `tests/references/`, et peut donc modifier ce test dans la même pull request sans que le garde le signale.
- **Raison :** il est mal placé. Les autres contrôles qui vérifient des règles, comme `mutation.py`, sont sous `.github/`.
- **Correction (en réutilisant l'existant) :** faire ce contrôle dans `garde.py`, qui tourne déjà depuis `main`, liste les fichiers modifiés et pose déjà l'étiquette « références régénérées » (point 12). Il lirait `RULES_REVISION` comme texte dans la base et dans la tête, sans exécuter le code de la branche. À défaut, protéger `tests/rejeu/` au palier 4.

### Nits
1. **Seuil de 80 %** (lignes 122, 291, 296, 511) : il est nécessaire pour que la mutation vérifie quelque chose à M1. Mais il s'applique sans fin à tout fichier nouveau, y compris le code d'entrées-sorties (`order_log.py` et ses appels à git, `game.py` et `asyncio`), où des mutants équivalents sont probables, et « revu après la première mesure » n'a ni responsable ni moment. **Correction :** limiter le seuil à `core` et `schema` (ou à la moyenne de la pull request), et rattacher sa revue à un point du plan, par exemple le point 28 bis.
2. **Deux conventions opposées pour le même numéro** (lignes 124, 156 et 232) : le quota garde les plus petits numéros (règle du niveau 1), la règle « un ordre par vaisseau » garde le plus grand. **Correction :** aligner sur le plus petit, ou justifier l'écart en une phrase.
3. **Point de connexion dans `schema`** (lignes 126, 579) : l'`asyncio.Queue` est un objet de transport, pas un message ; placée dans `schema`, qu'importe `core`, elle fait entrer `asyncio` dans ses dépendances, même si la liste fermée de la ligne 200 ne regarde que `core`. **Correction :** un `typing.Protocol` minimal dans `schema`, et les vraies files créées par `__main__.py`.
4. **Moment de la mesure de durée** (lignes 405, 706) : la durée de `mutation` est mesurée au volet C, alors que la première mutation lourde, celle de tout `core`, a lieu sur la pull request de fonctionnalité du volet A. **Correction :** mesurer à chaque pull request de fonctionnalité, et s'arrêter au premier dépassement.
5. **« Supérieur » ou « augmenté de un »** (ligne 685 ; `CLAUDE.md`) : `test_revision.py` exige un numéro « supérieur », `CLAUDE.md` dit « augmenté de un ». **Correction :** choisir l'une des deux règles et l'écrire partout.
6. **Dépendance cachée du rejeu** (lignes 273, 275, 635) : « le contrôle `rejeu` n'a besoin que de `core` et de `schema` », mais `rules_version` exige l'empreinte des réglages, calculée par `server/tunables_loader.py`. **Correction :** dire que le test importe aussi ce module, ou déplacer le calcul de cette empreinte dans `core`, qui reçoit déjà les réglages.
7. **Journal public des corporations** (lignes 180, 397 ; niveau 1, §4) : garder l'historique dans les événements engage M6 à construire ce journal à partir des événements. C'est raisonnable, mais ce n'est pas dit. **Correction :** une ligne dans Future Improvements, ou une note au niveau 1 par ADR si le propriétaire y tient.
8. **DuckDB dans le notebook** (lignes 281, 543, 702) : DuckDB n'y calcule rien (« pour les explorer »), au prix d'une compilation de plusieurs minutes et d'un groupe de dépendances à part. **Correction :** soit citer le niveau 1, §9 (« DuckDB + marimo », dès M1) comme seule raison, soit reporter DuckDB à M2 et n'utiliser que marimo.
9. **Mécanisme de visibilité non vérifié** (ligne 210) : l'objectif 6 repose sur « à vérifier contre `msgspec` 0.22.0 ». **Correction :** nommer le mécanisme vérifié (`msgspec.Meta(extra=...)`, lu par `msgspec.inspect`), ou prévoir le repli : une table des classes à côté de chaque `Struct`.

## Propositions de l'agent de code jugées nécessaires et proportionnées

Le relecteur ne voit rien de plus simple pour :
- l'arrondi de la taxe vers le haut ;
- les résultats d'ordre gardés dans `State` (hors du cas limite de M2) ;
- la tâche `tests-outillage` gardée telle quelle (écart avec M0 à noter, voir M1) ;
- le principe d'une partie de référence rejouée par `step` seul (hors des défauts du format, voir M5).

## Décompte

1 Blocker, 7 Major, 9 Nit.
