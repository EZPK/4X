# Résolution des constats des étapes 8 et 9

*   **Document :** `docs/designs/niveau-2-m1-noyau.md`, réécrit le 2026-11-06, puis corrigé le 2026-11-08 après la relecture finale (956 lignes).
*   **Rapports traités :** `zoom_out_intermediaire_report.md` (étape 8, préfixe É8), `implementation_readiness_report.md` (étape 9, préfixes R, T, Y).
*   **Mandat :** le propriétaire a délégué les choix techniques à l'agent de code (« tranche toi-même ») ; les choix nouveaux sont inscrits au Technical Plan, point 1, avec la mention « proposition de l'agent de code ».

## Vérifications faites par l'agent de code (2026-11-06, hors du dépôt)

Sorties de commandes, qui ne valent pas preuve de CI.

| Point vérifié | Commande | Résultat |
| :-- | :-- | :-- |
| Route publique de la protection (É8 M1, T-M5) | `curl -s https://api.github.com/repos/EZPK/4X/branches/main`, sans jeton | `protected` vrai, `enforcement_level` = `everyone`, contexts = `lint`, `typage`, `gitleaks`, `termes-interdits`, `tests-outillage`, `garde`, `en-attente` |
| Clés de configuration de `mutmut` 3.8.0 (R-M3, T-M4, T-N1) | lecture de `mutmut/configuration.py` installé sous Python 3.15.2 | `source_paths`, `only_mutate` (motifs de fichiers, en configuration seulement), `do_not_mutate`, `also_copy`, `pytest_add_cli_args`, `pytest_add_cli_args_test_selection` existent ; `paths_to_mutate` est déprécié. Le relecteur T se trompait sur `source_paths` et `only_mutate` |
| Filtrage et scores de `mutmut` 3.8.0 | `mutmut run --help`, lecture de `__main__.py`, essai sur un petit projet | `mutmut run [MUTANT_NAMES]` filtre par motifs `fnmatch` ; `export-cicd-stats` ne donne que des totaux ; `mutmut results --all true` donne une ligne `module.x_fonction__mutmut_N: statut` par mutant ; la formule du badge est (tués + délais dépassés) / (total − ignorés) |
| Code instrumenté par `mutmut` (T-M3) | lecture de `mutants/src/demo/m.py` après `mutmut run` | import `from mutmut.mutation.trampoline import ...` ajouté, et un mutant `a / 2` : le test de déterminisme statique doit être exclu de la mutation. Constat confirmé |
| Métadonnées de visibilité (É8 Nit 9, R-M1, T-N5, Y-M13) | `msgspec.inspect.type_info` sur un `Struct` à champ `Annotated[int, msgspec.Meta(ge, le, extra={...})]`, `msgspec` 0.22.0 | le champ revient comme `Metadata`, avec `extra` = `{'visibility': 'private'}` et les bornes |
| Date de `hypothesis` 6.170.2 (nouveau constat) | `uv pip install hypothesis==6.170.2` avec la date limite du projet | refusé : publié le 2026-10-19 à 04 h 17 UTC, après `exclude-newer` = 2026-10-19 ; l'en-tête du plan est corrigé |
| Copie de référence de la protection (T-B1) | lecture de `tests/outillage/test_garde_commandes.py`, lignes 679 à 685 | le test compare `.github/protection-main.json` à `hook.REFERENCE_PROTECTION`. Constat confirmé |
| Conftest du profil `hypothesis` (É8 B1, R-B4) | lecture du document et de `tests/` | `tests/proprietes/conftest.py` protégé au palier 2 mais créé au volet A ; pas de `tests/conftest.py`. Constat confirmé |

Script de contrôle du document révisé : bornes recalculées identiques (84 000 à 153 000 ; 8 400 à 15 300 ; 75 600 à 137 700 ; 10 200 unités au plus par fenêtre), tableaux réguliers, renvois « plan détaillé, point N » et « Technical Plan, point N » existants, aucun terme interdit, aucun chemin personnel.

## Blockers

| Constat | Issue |
| :-- | :-- |
| T-B1 (copie de référence de la protection dans le hook) | Point 31 ter : le propriétaire met à jour `REFERENCE_PROTECTION` au palier 4, selon la procédure de `CLAUDE.md` ; ligne au Technical Plan, point 1 |
| R-B1, T-M8 (scénarios qui cassent `mypy` et la collecte) | Règles pour les définitions d'étapes (palier 3) : import de `fourx` dans les fonctions d'étape par `importlib.import_module` ; `test_scenarios.py` fixé ; `pythonpath = .` (point 7, corrigé après la relecture finale) |
| R-B2 (interfaces non définies) | Nouveau Technical Plan, point 13 : types, champs, signatures, libellés, codes de refus, types d'événements, composants des empreintes, commandes |
| R-B3 (fichiers non protégés dans une pull request protégée) | `pyproject.toml`, `uv.lock` et `.gitignore` protégés au palier 1 (point 3 bis) ; ligne au Technical Plan, point 1, avec la conséquence (une dépendance passe par une pull request protégée) |
| R-B4, É8 B1, T-M2, T-M12 (profil `hypothesis`) | `tests/conftest.py` racine au palier 2, protégé, `derandomize=True, database=None, deadline=None` (point 7) |
| R-B5, É8 M2, T-M13 (contrat de `step`) | Type `SubmittedOrder` ; `step` refait `validate_orders` (plus de code de la réception dans le journal) ; `rules_version` calculé par le noyau à partir de `Tunables` ; attribution des identifiants ; schéma SQLite et export JSONL (point 21) ; message illisible impossible à M1, renvoyé à M3 (Non-Goals) |

## Majors

- **É8 M1, T-M5 :** relecture de nuit de la protection livrée à M1 par la route publique (point 30 bis, `protection.py`), engagement de M0 tenu ; `strict`, `allow_force_pushes`, `allow_deletions` relus à la main au point 31.
- **É8 M3, R-M10 :** mode sans horloge décrit (Technical Plan, point 6 : `Game.advance`, `SyncClient.on_update`, ordres au tick suivant) ; `__main__.py` avec `asyncio.run` et `app.run_async()`.
- **É8 M4, R-M4, T-M6, Y-M4 :** comparaison tick par tick entre les deux rejeux sous deux `PYTHONHASHSEED` (tâche `rejeu`, trois étapes), et aux références tous les 1 000 ticks ; objectif 2 réécrit.
- **É8 M5, T-M9 :** référence au format d'export versionné du journal des ordres soumis ; une seule fonction de rejeu (`replay_orders`) ; état initial régénéré par la graine ; un seul dossier de révision gardé, taille mesurée au point 28 bis.
- **É8 M6, R-M16 :** `Snapshot` porte `rules_version`, la graine, le commit et l'indicateur ; vérifié par `test_versions.py`.
- **É8 M7, R-M11, R-M12, T-M11 :** montée de révision contrôlée par `garde.py` (base + 1, depuis `main`, sans exécuter la branche) ; `RULES_REVISION` = 0 au volet A, 1 au volet C ; `tests/rejeu/**`, `tests/economie/**` et `test_determinisme_statique.py` protégés (point 4).
- **R-M2 :** priorité des codes de refus (ordre des colonnes), propriété du vaisseau pour tous les ordres, placement des sites, moment d'émission de chaque événement, numéro répété, limite de taille.
- **R-M3, T-M4 :** `mutation.py` spécifié (arguments, filtrage par motifs de noms de mutants, `mutmut results --all true`, formule, fichier sans mutant, base dans un `git worktree`), d'après la lecture du code de 3.8.0.
- **T-M3 :** test de déterminisme statique et `tests/outillage` exclus de la mutation (point 5).
- **R-M5 :** `nuit.yml` créé au palier 4 (point 30 bis).
- **R-M6 :** vérification de version du journal déplacée dans `tests/server/test_versions_journal.py`.
- **R-M7 :** bugs volontaires ancrés par l'analyse de la syntaxe ; `test_canaris.py` sur un module d'exemple ; risque ajouté.
- **R-M8, T-N7, Y-M14 :** versions épinglées en `==`, pytest plafonné, `exclude-newer` fixé à la date de la pull request moins 14 jours ; constat nouveau sur la date de `hypothesis`.
- **R-M9, T-M7 :** pas de greffon asynchrone ; `asyncio.run` dans des tests synchrones.
- **R-M13 :** `tests/schema/`.
- **R-M14 :** essais E1 à E5 (point 32 bis).
- **R-M15, É8 Nit 4 :** mesure de durée sur chaque pull request du palier 3 (point 28 bis).
- **T-M1 :** compte de `test_vraie_liste_des_chemins_proteges` mis à jour (25 au palier 1, 29 au palier 2, 31 au palier 4, après la relecture finale).
- **T-M10 :** sortie de `garde.py` en liste d'étiquettes ; refus du retrait de la nouvelle étiquette ajouté au hook au palier 4 (point 31 ter) ; risque accepté entre les paliers 2 et 4.
- **T-M14 :** `tests-outillage` inchangée jusqu'au palier 4, puis limitée (point 31 bis) ; l'échec attendu des scénarios en attente reste dans un contrôle obligatoire.
- **Style, Y-M1 à Y-M16 :** « acteur détenteur » ; « régénération d'un gisement » et « régénération des références », « outil de régénération » seul ; « journal enregistré de la partie de référence » ; colonne « Tâche » au Technical Plan, point 10 ; « croissance de la masse monétaire » ; « score du commit de base, fichier par fichier » ; paire de `asyncio.Queue` ; tirage borné et BLAKE2b précisés ; partage d'un gisement ; sens de tri ; `Int64` ; libellés neutres ; identifiants des réglages (`cargo_capacity`, `ore_prices`, `tax_rate_bp`, `deposit_stock`) ; les deux « à vérifier » résolus par essai.

## Nits

Appliqués : É8 Nit 1 (seuil limité à `core` et `schema`, revu au point 28 bis), Nit 2 (plus petit numéro, comme le quota), Nit 3 (`Connection` en `typing.Protocol`), Nit 5 (« plus un »), Nit 6 (empreinte des réglages calculée par le noyau), Nit 7 (journal des corporations en Future Improvements), Nit 8 (DuckDB justifié par le niveau 1, §9) ; R-N1 à R-N9 ; T-N2, T-N3, T-N4, T-N6, T-N8, T-N10, T-N11, T-N12 ; Y-N1 à Y-N21 pour l'essentiel (dont `Deposit` au lieu de `Field`, « site » défini, « minerai entreposé », « intervalle » des paliers).

Écartés :
- **T-N1** (`paths_to_mutate`) : contredit par la lecture du code de 3.8.0 (`source_paths` est la clé, `paths_to_mutate` est déprécié).
- **T-N9** (`rich` déjà figé) : sans action ; la résolution du palier 2 le dira.
- **Y-N13, en partie** : quelques jugements gardés quand ils portent une raison (« où les mutants équivalents sont rares »).

## À confirmer par le propriétaire au passage à Approved

Les lignes « proposition de l'agent de code » du Technical Plan, point 1 : arrondi de la taxe, seuil de mutation, résultats d'ordre, ordres d'un même tick, partie de référence, concurrence, tâche `tests-outillage`, relecture de la protection, fichiers de configuration du dépôt protégés, copie de référence de la protection dans le hook (action du propriétaire au palier 4).

## Relecture finale de la pull request n° 15 (2026-11-08)

Relecteur `egm-design`, sans contexte, sur le commit b712f97 : 2 bloquants, 7 majeurs, 14 mineurs ; 17 corrections des bilans contrôlées (11 justes, 6 incomplètes) ; bornes recalculées exactes ; aucun terme interdit, secret ni identifiant de machine. Corrections appliquées par un script de 53 remplacements exacts (hors du dépôt) :

| Constat | Correction |
| :-- | :-- |
| B1 : `tests/rejeu/**`, `tests/economie/**`, `test_determinisme_statique.py` protégés au palier 2 mais créés par des pull requests de fonctionnalité | `test_determinisme_statique.py` créé et protégé au palier 2 (point 7 bis, 29 motifs) ; `tests/rejeu/**` et `tests/economie/**` protégés au palier 4 (point 31 bis, 31 motifs) ; risque de l'intervalle ajouté |
| B2 : étape de divergence en échec avant le volet C | étape sautée, et dite, tant que les fichiers d'empreintes manquent ; tolérance retirée au point 31 bis |
| M1 : `schema` dépendrait de `core` | `Activity` et `LedgerEntry` définis dans `schema`, réutilisés par `core` |
| M2 : prix absents des observations | `world.generate` copie `ore_prices` dans la station ; prix publics, dans `StationView` |
| M3 : origine d'un ordre du serveur | `sender_actor_id` vaut `None` pour le serveur ; règle de catégorie dans `validate_orders` |
| M4 : mutation de nuit sans plancher | option `--plancher-partout`, utilisée par `nuit.yml`, testée au point 10 |
| M5 : lecture de la tête par le contrôle de garde | `garde.yml` lit la tête par `gh api .../contents/...?ref=$HEAD_SHA`, sans nouveau `checkout`, et passe deux fichiers à `garde.py` |
| M6 : imports des modules d'aide sous `mypy` | `pythonpath = .` et imports `tests.scenarios.steps...`, `tests.rejeu...` ; essayé le 2026-11-08 sur un petit projet avec la configuration du dépôt : `mypy` strict sans erreur, pytest collecte, le scénario échoue dans son étape comme attendu |
| M7 : rôle de la réception | d'abord déclaré comme écart au niveau 1, §2 ; remplacé après la relecture ciblée par une solution conforme au niveau 1 (voir ci-dessous) |
| N1 à N14 | appliqués : noms (`kind`, `balance`), indexation des tuples, `replay_mode` et `reference_fingerprints` situés, dernier tick dans l'export, `tick` hors des composants, import JSONL de `server`, dossier de partie à la microseconde, appels de fonctions intégrées seulement, ancre du bug volontaire `mutation`, alternative K de M0 signalée, durée de `tests-outillage` relevée, `GITHUB_TOKEN` en lecture seule pour la tâche `protection`, `economy.py`. N13 (`also_copy = pytest.ini`) : non appliqué, à confirmer par le premier lancement de `mutmut` au palier 2 |

## Relecture ciblée du commit 36e0249 (2026-11-08)

Relecteur `egm-design`, sans contexte : les dix corrections sont présentes, huit justes, deux incomplètes (M3, M7) ; 0 bloquant, 2 majeurs, 9 mineurs. Corrections appliquées par 25 remplacements exacts (hors du dépôt) :

| Constat | Correction |
| :-- | :-- |
| Major 1 : l'écart au niveau 1, §2, exigerait une ADR | écart retiré : la réception applique la validation sans état, comme le niveau 1, §2 ; un ordre qu'elle refuse est journalisé avec son code (`SubmittedOrder.reception_refusal`), et `step` le refuse avec ce code. Règle de rédaction du propriétaire rétablie ; glossaire inchangé sur ce point |
| Major 2 : ordres du serveur refusés par `ACTOR_MISMATCH` | les ordres du serveur ne passent plus par la validation sans état ; `step` refuse seulement un ordre sans émetteur qui n'est pas d'administration ; scénarios précisés (`actor_id` d'un autre acteur ; propre `actor_id` pour l'ordre d'administration) ; ordre des contrôles sans état écrit |
| Nit 1 | en-tête de l'export : valeurs de `meta` et dernier tick, aux deux endroits |
| Nit 2 | `id` et `kind` dans le tableau des entités ; appariement de `wallet_balance` et `action_budget` dans le test de visibilité |
| Nit 3 | `--plancher-partout` ajoute `src/fourx/schema/` |
| Nit 4 | format des bugs volontaires : liste de modifications, ancre « fin du module » |
| Nit 5 | `gh api` en `raw+json`, à chaque exécution, réponse 404 traitée |
| Nit 6 | `# noqa: F403` sur les `import *` des modules d'étapes |
| Nit 7 | vérification de `pytest.ini` dans `mutants/` écrite au point 5 ; ligne R-B1 de ce bilan corrigée |
| Nit 8 | règle des chemins protégés nouveaux écrite en tête du document |
| Nit 9 | `Int64` et `Id` dans `schema/types.py` |
