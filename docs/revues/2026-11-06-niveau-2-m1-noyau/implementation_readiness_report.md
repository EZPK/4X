# Étape 9 — préparation à l'implémentation

*   **Document :** `docs/designs/niveau-2-m1-noyau.md`, version révisée du 2026-11-06 (765 lignes), relue **sans** les corrections de l'étape 8 (le propriétaire a choisi de passer à l'étape 9 directement).
*   **Date :** 2026-11-06.
*   **Relecteurs :** trois relecteurs sans contexte, en parallèle, avec le standard `implementation-readiness-standard` :
    - `egm-implementation-readiness` (préfixe **R**), qui a lu le niveau 1, le glossaire, `CLAUDE.md`, `chemins-proteges.txt` et la CI existante (`ci.yml`, `garde.yml`, `garde.py`, `en_attente.py`, `pytest.ini`, `mypy.ini`, `pyproject.toml`, `.importlinter`, `protection-main.json`, `tests/scenarios/conftest.py`, `tests/outillage/test_workflows.py`) ;
    - `egm-codebase-details` (préfixe **T**), qui a confronté le document au dépôt entier (y compris le hook `.claude/hooks/garde_commandes.py`, en lecture) et à ce qu'il sait des outils. Il signale que `mutmut` 3.8.0, `msgspec` 0.22.0, `textual` 8.2.8, `hypothesis` 6.170.2, `marimo` 0.25.2 et `duckdb` 1.5.6 sont plus récents que ce qu'il connaît de façon fiable, et qu'aucun n'est dans `uv.lock` : ses affirmations sur leur fonctionnement interne sont marquées « à vérifier » ;
    - `egm-style` (préfixe **Y**).
*   **Renvois :** « É8 » vise `zoom_out_intermediaire_report.md`.
*   **Vérification de l'agent de code :** T-B1 relu dans `tests/outillage/test_garde_commandes.py`, lignes 679 à 685 : `test_copies_de_reference_egales_aux_fichiers` exige que `.github/protection-main.json` soit égal à `hook.REFERENCE_PROTECTION`. Constat confirmé.
*   **Verdict :** le plan n'est pas prêt. Un agent de code sans mémoire ne peut pas livrer le palier 3 (scénarios qui ne passent pas la CI, interfaces non fixées), ni le palier 4 (copie de référence de la protection dans un fichier que seul le propriétaire peut modifier).

## Synthèse

| Relecteur | Blocker | Major | Nit |
|---|---|---|---|
| Préparation (R) | 5 | 16 | 10 |
| Exactitude technique (T) | 1 | 14 | 12 |
| Style (Y) | 0 | 16 | 21 |
| **Total brut** | **6** | **46** | **43** |

Après le retrait des doublons (avec l'étape 8, et entre relecteurs) : **5 Blockers nouveaux** (R-B1, R-B2, R-B3 en partie, R-B5, T-B1), le sixième (R-B4) confirmant É8 B1.

## Blockers

### T-B1 : le palier 4 casse le contrôle obligatoire `tests-outillage`
- **Lignes :** 729 à 732 (point 31), 523 à 528 (point 11 bis), 295.
- **Constat :** le point 31 ajoute cinq contrôles à `.github/protection-main.json`. Or `test_copies_de_reference_egales_aux_fichiers` (`tests/outillage/test_garde_commandes.py`, lignes 679 à 685), lancé par `tests-outillage`, exige que ce fichier soit identique à la copie `REFERENCE_PROTECTION` du hook (`.claude/hooks/garde_commandes.py`, lignes 34 à 52).
- **Conséquence :** la pull request du palier 4 ne peut pas passer sans modifier `.claude/hooks/garde_commandes.py`, que les règles `deny` interdisent à l'agent de code d'éditer (`CLAUDE.md`). Le plan ne prévoit ni ce fichier, ni la procédure du propriétaire.
- **Correction :** un point « `.claude/hooks/garde_commandes.py` (Modify) » au palier 4, dans la même pull request protégée que le point 31 : le propriétaire lève la règle `deny`, fait ou demande la mise à jour de `REFERENCE_PROTECTION`, puis remet la règle (`CLAUDE.md`). Dire aussi que l'exception d'amorçage reste refermée (la protection existe déjà).

### R-B1 : les pull requests de scénarios ne peuvent pas passer la CI
- **Lignes :** 547, 551 à 566, 621 à 629, 657 à 662.
- **Constat :**
  - les définitions d'étapes sont écrites avant le code qu'elles appellent. Or `mypy.ini` est strict sur `tests/` : un import d'un module absent fait échouer `typage`, obligatoire depuis M0 ;
  - à l'exécution, un import au niveau du module lève `ImportError` pendant la collecte : c'est une erreur de session, pas l'échec attendu, et le mécanisme `xfail(strict=True)` de `tests/scenarios/conftest.py` (lignes 51 à 71) ne s'applique pas ;
  - avec `--import-mode=importlib` et sans `tests/__init__.py`, ni `test_scenarios.py` → `steps/steps_*.py`, ni `test_rejeu.py` → `partie_reference.py` ne s'importent directement (T-M8).
- **Raison :** aucune pull request de scénarios ne peut être fusionnée : tout le palier 3 est bloqué.
- **Correction :** fixer la convention : les étapes importent le code du projet à l'intérieur des fonctions d'étape, par un utilitaire typé `Any` (`importlib.import_module`) ; donner le texte de `test_scenarios.py` et le chargement des modules d'étapes et d'aide (`pythonpath = tests` au point 7, ou un chargement comme la fixture `charger_script` de `tests/outillage/conftest.py`).
- **Recoupe :** T-M8.

### R-B2 : les interfaces que les étapes protégées vont figer ne sont pas définies
- **Lignes :** 136 à 153, 207 à 232, 568 à 600, 631 à 648, 664 à 670.
- **Constat :** les définitions d'étapes sont des chemins protégés, écrites avant le code ; la pull request de fonctionnalité ne peut pas les corriger, donc elles figent l'interface. Le document ne fixe pas : les tables et champs de `State` et des entités ; les champs de `Tunables` (capacité, prix, taux de taxe ; Y-M12) ; les quatre commandes et leurs champs ; l'identification d'un minerai ; l'énumération de l'activité ; les membres de `RefusalCode` ; les noms des types d'événements ; les champs de `Observation`, des vues, de `OrderResult`, `SubmitOrders`, `TickUpdate` ; les composants de `Fingerprints` ; la clé d'un `Account` ; les signatures de `keyed_draw`, de la génération du monde, de `Reception`, de `game.py`, de `NpcHost` ; la sortie de l'outil de divergence (le scénario attend « registre »).
- **Raison :** chaque choix revient à l'agent, contre la ligne 40 ; et `CLAUDE.md` lui ordonne de s'arrêter quand un identifiant nécessaire n'est pas fixé.
- **Correction :** une section « Interfaces » : chaque type `msgspec` avec ses champs typés, chaque fonction publique avec sa signature.
- **Recoupe :** Y-M11 (libellés neutres), Y-M12 (réglages sans identifiant), R-N4, R-N7.

### R-B3 : des fichiers sont portés par une pull request qui n'en a pas le droit
- **Lignes :** 472, 479 à 482, 540 à 543, 611 à 615.
- **Constat :**
  - la pull request protégée du palier 2 contient `.gitignore`, `pyproject.toml` et `uv.lock`, qui ne sont pas dans `chemins-proteges.txt` ; or une pull request protégée « ne contient que des chemins protégés » (`CLAUDE.md`) ;
  - `tests/proprietes/conftest.py`, protégé au point 4, est créé au point 19, dans une pull request de fonctionnalité (même constat qu'É8 B1).
- **Correction :** pour la première partie, au choix : protéger ces trois fichiers au palier 1, ou les sortir dans une pull request de fonctionnalité d'outillage, ou acter l'exception par une ADR. Pour la seconde, voir R-B4.

### R-B4 : le profil `hypothesis` `ci` est demandé avant d'exister
- **Lignes :** 487, 615.
- **Recoupe :** É8 B1, T-M2, et R-B3 (seconde partie). Ajouts : `uv run pytest tests/outillage` et la copie de travail de `mutmut` ne chargent jamais `tests/proprietes/conftest.py` ; le profil doit aussi porter `deadline=None` (T-M12).
- **Correction :** `tests/conftest.py` racine, au palier 2, protégé : `settings.register_profile("ci", derandomize=True, database=None, deadline=None)` puis chargement ; retirer le conftest du point 19.

### R-B5 : le contrat de `step` est incomplet
- **Lignes :** 123, 157, 161, 207, 208, 216, 254, 255, 275, 637, 677.
- **Constat :**
  - `Order` n'a ni tick, ni acteur du point de connexion, ni code de refus de la réception, alors que `step` doit refuser « avec le code de la réception » et adresser le résultat à cet acteur ; le type exact du paramètre `orders` n'est pas défini (T-M13, É8 M2) ;
  - les formats de `ordres.jsonl` et du schéma SQLite de `OrderLog` (tables, colonnes) ne sont pas définis ;
  - l'enveloppe des événements porte `rules_version`, mais `step(state, orders, world_seed, tunables)` ne le reçoit pas ; « le serveur la passe au noyau » ne dit ni par quel paramètre, ni sous quel format ;
  - l'attribution de l'`actor_id` et de l'identifiant du vaisseau d'un personnage créé n'est pas fixée.
- **Raison :** c'est le contrat central du noyau, du journal et du rejeu, que M5 migrera.
- **Correction :** définir le type de l'ordre soumis (ordre, acteur du point de connexion, `RefusalCode | None`), la représentation de `rules_version` et la façon de la passer, la règle d'attribution des identifiants (prochain identifiant libre de la table), et les schémas du journal. La simplification d'É8 M2 (`step` appelle lui-même `validate_orders`) supprime le champ « code de la réception ».

## Majors

### Nouveaux

- **R-M2 : règles ambiguës qui changent les empreintes** (lignes 132, 148 à 153, 161 à 167, 216 à 228, 232) : priorité des codes de refus quand plusieurs conditions s'appliquent ; propriété du vaisseau vérifiée seulement pour « déplacer » ; algorithme de placement des sites (entité, borne, procédure) ; moment d'émission des événements (« départ » à chaque saut ou une fois par trajet) et donc `seq` ; lequel de deux numéros répétés est refusé ; valeur de la limite de « taille » de la validation sans état (niveau 1, §2). **Correction :** trancher chaque point au Technical Plan, points 2 et 5.
- **R-M3, T-M4 : l'outillage de mutation est sous-spécifié, et sans doute cassé en l'état** (lignes 291, 477, 503 à 511, 521, 720) :
  - `only_mutate` n'existe pas, à la connaissance du relecteur T, comme option ou clé de `mutmut` 3 ; le filtrage connu passe par les noms de mutants en argument de `mutmut run` (motifs `fourx.core.arith.*`). À vérifier sur 3.8.0 ;
  - `export-cicd-stats` donne des totaux globaux, pas des scores par fichier ;
  - la formule ignore `no_tests`, `timeout` et `suspicious` ; une fonction jamais appelée gonflerait le score ;
  - le cas de zéro mutant (volet A : `core` n'a que des `__init__.py`) n'est pas traité ;
  - le lancement sur le commit de base (copie, `uv sync`, tests de la base) n'est pas décrit ;
  - `tests/outillage` lit `.github/`, `docs/` et `.claude/`, absents de la copie de travail de `mutmut` sans `also_copy` ;
  - `mutation-complete` et l'interface de `mutation.py` pour `canaris.py` (base, tête) ne sont pas décrites.
  - **Correction :** vérifier sur `mutmut` 3.8.0 et fixer : les arguments de `mutation.py` (`--base`, `--tete`, en réutilisant `$BASE` et `$HEAD` de `ci.yml`, T-N8), la source des scores par fichier, la formule (`no_tests` compté comme survivant), la règle pour zéro mutant, `--ignore=tests/outillage` ou `also_copy`.
- **T-M3 : sous `mutmut`, le test de déterminisme statique lirait le code instrumenté** (lignes 607, 195 à 200, 477, 509) : `mutmut` 3 recopie sources et tests dans `mutants/` et réécrit chaque fonction en « trampoline », avec des imports ajoutés ; si le test trouve `src/fourx/core/` à partir de `__file__`, il refusera ces imports. **Correction :** l'exclure de la mutation, ou lui faire viser les sources de la racine du dépôt ; l'écrire au point 5. À vérifier sur 3.8.0.
- **R-M5 : `nuit.yml` est créé avant ce qu'il lance** (lignes 518 à 521, 711, 759) : `canaris.py` n'arrive qu'au palier 4 et `mutation-complete` tourne sur un `core` vide ; le contrôle échoue chaque nuit pendant le palier 3. **Correction :** créer `nuit.yml` au palier 4, et y avancer l'attente de trois workflows dans `test_workflows.py`.
- **R-M6 : `test_versions.py` ne peut pas passer à sa création** (ligne 609) : il vérifie la version du journal, dont `OrderLog` n'existe qu'au volet B. **Correction :** déplacer cette vérification dans `tests/server/` (point 23).
- **R-M7 : la suite canari peut bloquer toute fusion** (lignes 711 à 727) : si les bugs volontaires sont des patchs, `test_canaris.py` (dans `tests-outillage`, obligatoire) échoue dès qu'une pull request de fonctionnalité touche leur contexte, et aucune pull request ne peut corriger le patch protégé avant la fusion du code. **Correction :** exprimer les bugs comme des insertions ancrées sur des symboles stables (AST ou expression régulière), ou lancer ce test de nuit ; fixer la table « contrôle → commande ».
- **R-M8, T-N7, Y-M14 : les versions se contredisent** (lignes 115, 448, 543) : « versions de l'en-tête » et « `exclude-newer` avancé, versions relues » ; pytest n'est pas plafonné alors que 9.2.0 casse `mutmut`. **Correction :** épingler en `==` (`mutmut`, `msgspec`…), ajouter `pytest<9.2`, donner une valeur fixe à `exclude-newer`.
- **R-M9, T-M7 : les tests asynchrones n'ont pas d'outil** (lignes 543, 653) : `App.run_test()` est un gestionnaire de contexte asynchrone, l'horloge aussi ; aucun greffon n'est prévu. **Correction :** imposer `asyncio.run(...)` dans des tests synchrones, ou ajouter `pytest-asyncio` épinglé avec `asyncio_mode`.
- **R-M13 : le paquet `schema` n'a pas de tests unitaires** (lignes 568 à 581, 602 à 609, 650 à 653), alors que ses fichiers neufs doivent atteindre 80 %. **Correction :** `tests/schema/` au volet A.
- **R-M14 : les essais de l'objectif 8 ne sont pas décrits** (lignes 63, 64, 744, 758) : ni branche, ni contenu, ni type de pull request, ni ordre, alors qu'une seule pull request de chaque type peut être ouverte. **Correction :** une table comme les essais E1 à E8 de M0, réutilisant les bugs de la suite canari.
- **T-M1 : le point 4 casse `test_vraie_liste_des_chemins_proteges`** (`tests/outillage/test_garde.py`, ligne 55, qui exige exactement 22 motifs). **Correction :** au point 13, passer le compte au nouveau total et vérifier la couverture des nouveaux chemins.
- **T-M10 : la nouvelle étiquette est moins bien gardée que celle de M0** (lignes 530 à 538) : `garde.py` ne produit qu'une décision `etiquette` (lignes 18, 85 à 91) et `garde.yml` code son nom en dur (lignes 41 à 46) ; le hook ne refuse `gh pr edit --remove-label` que pour « fichiers protégés modifiés ». **Correction :** donner le format de sortie de `garde.py` ; ajouter `.claude/hooks/garde_commandes.py` (procédure de T-B1), ou accepter ce manque explicitement.
- **T-M14 : le palier 2 retire une exigence de M0 sans le dire** (lignes 493, 127, 446) : aujourd'hui, `tests-outillage` lance toute la suite (`ci.yml`, ligne 115), donc l'échec attendu des scénarios en attente fait partie d'un contrôle obligatoire ; limitée à `tests/outillage`, ce n'est plus le cas avant le palier 4. **Correction :** ne limiter `tests-outillage` qu'au palier 4, ou ajouter ce cas à la fenêtre des paliers 2 à 4 et aux risques.
- **R-M11 (en partie) : d'autres tests de contrôle restent hors des chemins protégés** (lignes 472, 607, 684 à 686) : `test_rejeu.py`, `test_determinisme_statique.py`, `test_fourchettes.py` portent des contrôles du niveau 1. **Correction :** les protéger. (La part sur `test_revision.py` recoupe É8 M7.)
- **Y-M1 : « propriétaire » au sens de détenteur d'un vaisseau** (lignes 142, 210) : « acteur détenteur ».
- **Y-M2 : « régénération » désigne deux mécanismes** (gisement, références), avec des synonymes (« recharge », « revient à son maximum ») et trois noms pour l'outil : qualifier toujours ; « outil de régénération » seul, comme `CLAUDE.md`.
- **Y-M3 : « journal » désigne deux artefacts** (`OrderLog`, `ordres.jsonl`) : réserver « journal des ordres soumis » à la base SQLite. (Disparaît si É8 M5 est appliqué.)
- **Y-M5 : noms des contrôles et des tâches** (lignes 195, 285 à 291, 297, 494, 604, 613, 681) : ajouter une colonne « Tâche » au tableau du Technical Plan, point 10.
- **Y-M6 : « masse monétaire » ou sa croissance par fenêtre** (lignes 57, 113, 280, 670, 702 contre 689) : un agent peut renvoyer le niveau, un autre la variation. Écrire « croissance de la masse monétaire par fenêtre » partout.
- **Y-M7 : score de référence de la mutation** (lignes 63, 122, 291, 508 à 511) : « score du commit de base de la pull request, fichier par fichier » partout.
- **Y-M8 : une file ou deux par point de connexion** (lignes 126, 252 contre 579) : « une paire de `asyncio.Queue` (ordres, mises à jour) ».
- **Y-M9, T-N6 : tirage borné et BLAKE2b sous-spécifiés** (lignes 190 à 194) : `digest_size=8` (différent des 8 premiers octets d'un condensé de 64) ; `m = (2**64 // n) × n`, rejet si `x ≥ m`, sinon `x mod n` ; taille du condensé des empreintes.
- **Y-M10 : partage d'un gisement** (ligne 164) : chaque vaisseau reçoit le minimum de `mining_rate`, de sa capacité libre et du stock restant ; un vaisseau servi après l'épuisement ne reçoit rien.
- **Y-M15 : sens de tri non dit** (lignes 161, 216) : « par `actor_id` croissant, puis par numéro croissant ».
- **Y-M16, R-N10 : forme de la borne sur 64 bits** (ligne 581) : `Annotated[int, Meta(ge=-2**63, le=2**63-1)]` ou une autre forme explicite.

### Qui recoupent l'étape 8

- **R-M1, T-N5, Y-M13** → É8 Nit 9 (mécanisme de visibilité « à vérifier ») ; ajouts : `msgspec.field` n'accepte pas de métadonnées, passer par `Annotated[..., Meta(extra=…)]` relu par `msgspec.inspect.type_info` ; classer chaque champ (capacité, détenteur, ticks avant saut, prix, voisins, type de compte) ; les vues reprennent les noms des champs de l'état ; la liste fermée d'imports doit couvrir `msgspec.structs`, `msgspec.inspect`, `msgspec.msgpack`.
- **R-M4, T-M6, Y-M4** → É8 M4 (empreintes tous les 1 000 ticks) ; ajout : stocker une empreinte par tick (petite), et faire accepter un dossier de références à `divergence.py`.
- **R-M10** → É8 M3 (mode sans horloge) ; ajout : `__main__.py` lance `asyncio.run()` qui démarre l'horloge puis `await app.run_async()`.
- **R-M12, T-M11** → É8 Nit 5 ; correction précisée : `RULES_REVISION = 0` au volet A, 1 au volet C, et `test_revision.py` exige « base + 1 », comme `CLAUDE.md`.
- **R-M15** → É8 Nit 4 ; ajout : la mutation de tout `core` ne se déclenche que sur une pull request qui modifie `steps/` : mesurer `mutation` sur la pull request de scénarios du volet C.
- **R-M16** → É8 M6 (champs de l'instantané).
- **T-M5** → É8 M1 ; le relecteur T confirme, de sa connaissance de l'API : `GET .../branches/{b}/protection` demande l'administration, mais `GET /repos/EZPK/4X/branches/main` se lit avec le jeton par défaut sur un dépôt public et donne `protection.required_status_checks.{enforcement_level, contexts}` (`strict`, `allow_force_pushes`, `allow_deletions` restent invisibles).
- **T-M9** → É8 M5 ; correction précisée : une fonction de `tools` (état initial, ordres par tick → empreintes et événements) appelée par `replay.py`, `test_rejeu.py`, `test_fourchettes.py`.
- **T-M12** → R-B4 (`deadline=None`).
- **T-M13** → R-B5.

## Nits

- **Préparation :** R-N1 (création de l'étiquette et clé de sortie de `garde.py`) ; R-N2, T-N2 (texte exact de `pytest_add_cli_args`, découpé par lignes) ; R-N3 (comment `test_workflows.py` sépare la règle « sans `name` » de la liste des contrôles) ; R-N4 (noms des fichiers d'une partie, format de `<date-heure>`, sorties de `replay` et `divergence`, signature de `economie.py`, bornes des fenêtres) ; R-N5, É8 M5 (anciens dossiers `rules-N`, lecture de `RULES_REVISION` sur `origin/main`) ; R-N6 (taille du condensé des empreintes) ; R-N7 (touches du client, options de `python -m fourx`) ; R-N8 (heure de la tâche de nuit) ; R-N9 (prix : la station dans l'état ou `Tunables` ?).
- **Technique :** T-N1 (clé `source_paths` : `paths_to_mutate` dans les versions connues ; une clé inconnue est ignorée sans erreur ; à vérifier) ; T-N3 (deux lancements de `rejeu` en deux étapes, sans matrice, que `test_workflows.py` refuse) ; T-N4 (les `__init__.py` des paquets existent déjà : « Create » vise les fichiers) ; T-N8 (réutiliser `$BASE`, `$HEAD`, la fixture `charger_script`, `.github/scripts/motifs.py`) ; T-N9 (`rich` 15.0.0 déjà figé dans `uv.lock`) ; T-N10 (avec `--strict-markers`, une étiquette Gherkin devient une marque non déclarée) ; T-N11 (commande exacte de régénération) ; T-N12 (`msgspec.toml.decode(..., type=Tunables)`).
- **Style :** Y-N1 à Y-N21 (titres de section, « six livrables », « ordinateur portable » et « PC d'entraînement », phrase sans verbe ligne 52, « contrôle obligatoire », exception de la ligne 100, antécédents, sujets grammaticaux, « commande », « scénario » au sens de monde de mesure, « prix fixes », variantes de termes, jugements non étayés, exemption de `/` dans `arith.py`, parenthèse de la ligne 274, phrase isolée ligne 169, « passe à l'arrêt » ligne 151, guillemets des codes, « fenêtre » des paliers, « site » non défini, « minerai entreposé », écarts mineurs, précisions manquantes ; `Field` se confond avec `msgspec.field`).

## Points vérifiés et conformes (relecteur T)

Code de sortie 5 de pytest (aussi quand `-m` désélectionne tout) ; `fetch-depth: 0` récupère `origin/main` ; `uv sync` installe `dev` par défaut ; ordre de lecture de la configuration de `mutmut` ; `derandomize` et `database=None` valides ; contrats d'imports conformes à `.importlinter` ; `tests-outillage` et `imports` conformes à `ci.yml` ; calcul des bornes du point 27 ; `exclude-newer` = 2026-10-19 ; identifiants « à fixer au niveau 2 de M1 » tous couverts ; fichiers « Modify » tous existants.

## Décompte

- Brut : 6 Blockers, 46 Majors, 43 Nits (95 constats).
- Après retrait des doublons : 5 Blockers nouveaux (T-B1, R-B1, R-B2, R-B3, R-B5) et R-B4 qui confirme É8 B1 ; 25 Majors nouveaux (28 constats bruts, fusionnés entre relecteurs) ; les 18 autres Majors recoupent l'étape 8 ou un autre relecteur.
