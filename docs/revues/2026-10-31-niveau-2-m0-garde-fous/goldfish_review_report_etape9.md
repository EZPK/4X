# Goldfish Annotated Review Report : document de M0, étape 9

Status: resolved (2026-11-01, « auto accept » : plan détaillé réécrit, spécification retouchée ; copie de la version précédente gardée hors du dépôt)

**Target:** `docs/designs/niveau-2-m0-garde-fous.md`, plan détaillé (l. 557 à la fin). S'y ajoutent les retouches de la spécification qu'imposent les points déjà acceptés, à corriger avant l'implémentation.

**Constats traités :**
- les 43 constats de [implementation_readiness_report.md](./implementation_readiness_report.md) : 24 majeurs et 19 mineurs ;
- les cinq points « à régler par l'implémentation » de [critic_report_tour2.md](./critic_report_tour2.md) ;
- les mineurs N-3, N-4 et N-5 de l'étape 8.

**Bilan :** 41 constats reçoivent une correction. Le constat 1-18 n'en reçoit qu'en partie, et le constat 1-9 (cd) est écarté. Aucun n'est contesté ni remonté au propriétaire.

**Proposition :** réécrire le plan détaillé en entier, et retoucher la spécification sur les points acceptés. Le document ne change de statut que par la décision du propriétaire (constat 1-4).

## Faits vérifiés le 2026-11-01

Ces faits ont été vérifiés par des commandes, hors du projet. Ils remplacent les affirmations non vérifiées des relecteurs.

| Fait | Résultat |
| :-- | :-- |
| Version de `gitleaks` à épingler (dernière publiée depuis au moins 14 jours, soit avant le 2026-10-18) | **8.30.1**, publiée le 2026-03-21. Somme de contrôle SHA-256 de `gitleaks_8.30.1_linux_x64.tar.gz` : `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`, identique à celle publiée |
| `gitleaks git --pre-commit --staged` sur un index sans aucun commit | fonctionne : il détecte une fuite indexée (code 1) et passe sur un index propre (code 0) |
| Règle propre au projet avec `[extend] useDefault = true` | fonctionne, **mais** une valeur trop régulière (`…ABCDEFGHIJKLMNOPQRSTUVWXYZ012345`) est écartée par la configuration par défaut. Une valeur tirée au hasard est détectée. La valeur d'essai doit donc être tirée au hasard |
| Faux jeton `ghp_` + 36 caractères aléatoires | détecté par la configuration par défaut de `gitleaks` |
| Langages de hook de `pre-commit` 4.7.0 | `system` n'existe plus, on écrit `unsupported` |
| `uv_build`, `[dependency-groups] dev`, `[tool.uv] exclude-newer`, `uv sync --locked` (uv 0.11.16) puis `lint-imports` | `fourx` est trouvé sous `src/`, et un contrat `forbidden` est appliqué (« 1 kept, 0 broken ») |

## Choix contenus dans les corrections

Ils ne remettent pas en cause une décision du propriétaire, mais en tirent les conséquences.

1. **Motifs des chemins protégés : une traduction propre au projet.** On n'utilise ni `fnmatch` ni `full_match`, mais une petite fonction de `garde.py`, testée : `**` désigne zéro ou plusieurs dossiers, `*` tout sauf `/`. Elle ne dépend d'aucune version de Python (point accepté egm-design-2-6, et constat 1-4 cd).
2. **`garde` et `en-attente` ne tournent que sur les pull requests.** Ce sont des contrôles obligatoires de pull request. L'essai E1 vérifie sur `main` les seules tâches de `ci.yml` (point accepté egm-structural-2-1).
3. **Les règles `gitleaks` sur les adresses IP privées et sur les variables `FOURX_` sont reportées à M4,** comme l'a recommandé l'étape 8. M0 ne garde que la règle d'essai. Ce document et les rapports de revue ne se détectent donc plus eux-mêmes (point accepté egm-structural-2-2 et constat 1-12). Le Goal 4 est ajusté.
4. **La pull request obligatoire sans approbation :** `required_pull_request_reviews` avec `required_approving_review_count: 0` (point accepté egm-design-2-7).
5. **Une ADR `0001` pour les écarts E4 et E5,** décidés le 2026-11-01. L'agent de code la rédige au statut « proposée », et le propriétaire l'accepte avant le commit initial (point accepté egm-structural-2-4).
6. **Les résultats en cours de route vont dans `notes-m0.md`,** à la racine, ignoré par git. Ils sont recopiés dans le compte rendu en phase 5 (constat 1-1 style).
7. **Le Python de la CI et du garde est installé par `uv` à partir de `.python-version`, sans cache.** Les scripts de `garde.yml` tournent sous ce même Python 3.15 (constats 1-4 cd et 1-13).

## Prioritized Findings & AI Suggestions

| Constat | Gravité | Suggestion | Correction |
| :-- | :-- | :-- | :-- |
| ir-1-1 : le commentaire de `en_attente.txt` | Medium | PROPOSE FIX | Les lignes vides et `#` sont ignorées par `conftest.py` et par `en_attente.py`, et un test le vérifie |
| cd-1-1 : `[build-system]` absent | Medium | PROPOSE FIX | `uv_build`, `[dependency-groups] dev`, vérifiés |
| ir-1-2 : `gitleaks` au push initial | Medium | PROPOSE FIX | `fetch-depth: 0`. SHA passés par `env:`. Pull request : `--log-opts="$BASE..$HEAD"` ; push : `"$BEFORE..$AFTER"`, ou tout l'historique si `BEFORE` est nul |
| ir-1-3 : commit initial non exécutable | Medium | PROPOSE FIX | Une liste de commandes numérotée, avec la liste des fichiers attendus et l'arrêt en cas de trouvaille |
| cd-1-2 : `.pre-commit-config.yaml` absent, `--all-files` ne prouve rien | Medium | PROPOSE FIX | Le YAML exact (`repo: local`, `language: unsupported`, `pass_filenames: false`). La vérification de tout le dépôt se fait par `gitleaks dir .` |
| ir-1-4 : statut du document et de la feuille de route | Medium | PROPOSE FIX | Une étape du propriétaire en tête du plan : document Approved et M0 « approuvé » dans `docs/feuille-de-route.md`, inclus dans le commit initial. En phase 5, M0 passe à « livré » et le jalon en cours à M1, par une pull request protégée |
| ir-1-5 : hook activé avant d'être testé | Medium | PROPOSE FIX | Les tests du hook, `ruff`, `mypy`, puis un appel à la main avec un JSON d'exemple, **avant** l'écriture de `settings.json`. Reprise : le propriétaire renomme `.claude/settings.json` hors de Claude Code |
| ir-1-6 : procédure de la phase 0 inexistante | Medium | PROPOSE FIX | Deux branches décrites : hook actif tout de suite, ou nouvelle session ouverte par le propriétaire. Un attendu observable pour chacune |
| ir-1-7 : vérification de `!` sans étape | Medium | PROPOSE FIX | Étape du propriétaire en tête de la phase 4 : `! git commit -n --allow-empty --dry-run -m test`, qui doit s'exécuter sans message du hook. Sinon, terminal hors de Claude Code |
| style-1-1 : où garder les résultats | Medium | PROPOSE FIX | Choix 6 (`notes-m0.md`) |
| style-1-2 : une demande par commande d'amorçage ? | Medium | PROPOSE FIX | Une demande explicite du propriétaire pour chacune des quatre commandes de la phase 2 |
| ir-1-8 : entrées et sorties des scripts | Medium | PROPOSE FIX | Pour chaque script : ligne de commande, entrées, sorties et codes de sortie. Les exclusions sont lues dans `docs/termes-interdits.md` (source unique). Classe « lettre » = `str.isalnum()` de Python, accents compris. Les appels à l'API sont faits par le workflow, le script ne fait aucun appel réseau, et le Technical Plan, point 8, est aligné |
| ir-1-9 : contenu des fichiers de configuration | Medium | PROPOSE FIX | Chaque clé et sa valeur : `ruff.toml`, `mypy.ini`, `pytest.ini`, `.importlinter` (un contrat `forbidden` par paquet du niveau 1, §1) |
| ir-1-10 : disposition des tests | Medium | PROPOSE FIX | `pytester.makeconftest(…read_text())` ; fichiers de `exemple/` nommés ; `collect_ignore` ; liste en attente écrite par chaque test ; liste des `__init__.py` |
| ir-1-11 : texte imposé non donné | Medium | PROPOSE FIX | Les phrases exactes, avant et après, pour `CLAUDE.md`, le niveau 1, §10, et `termes-interdits.md`. Une exception nommée pour chaque règle. `CLAUDE.md` avant le niveau 1 |
| ir-1-12 : règles de `.gitleaks.toml` | Medium | PROPOSE FIX | Le fichier exact (choix 3) : `[extend] useDefault = true` et la seule règle d'essai, avec son motif |
| ir-1-13 : actions et installation de Python | Medium | PROPOSE FIX | `actions/checkout` et `astral-sh/setup-uv`, épinglées par SHA ; Python installé par `uv` à partir de `.python-version` ; étapes de chaque tâche |
| cd-1-3 : la règle des 14 jours et les dépendances Python | Medium | PROPOSE FIX | `exclude-newer` = date d'exécution moins 14 jours ; bornes basses égales aux versions vérifiées ; `required-version` pour `uv` |
| cd-1-4 : Python, cache et droits de git de `garde.yml` | Medium | PROPOSE FIX | Choix 7, avec `enable-cache: false` et `persist-credentials: false` |
| cd-1-5 : pagination et renommages | Medium | PROPOSE FIX | `gh api --paginate` ; `filename` et `previous_filename` testés |
| cd-1-6 : copies de référence du hook | Medium | PROPOSE FIX | Comparaison du JSON une fois lu, et un test qui compare chaque copie au fichier de `.github/` |
| cd-1-7 : « contrôle obligatoire » existe déjà dans le glossaire | Medium | PROPOSE FIX | Modify de l'entrée existante ; retouche des l. 8 et 10 du glossaire, qui admettent les termes d'un niveau 2 ; liens vers la section concernée |
| cd-1-8 : couverture annoncée trop large | Medium | PROPOSE FIX | Le point des tests reprend chaque règle des points 8, 9 et 10, plus un test texte sur les fichiers de workflow (pas de `${{ github.event.* }}` dans un `run:`). Sans chemin protégé, `garde` retire l'étiquette et le bloc |
| style-1-3 : « plan détaillé, point 4 / 6 » | Medium | PROPOSE FIX | « niveau 1, plan détaillé, point 4 (`docs/termes-interdits.md`) » |
| style-1-4 à 1-12 | Low | PROPOSE FIX | Marques « propriétaire » sur les étapes concernées ; titres `####` pour les fichiers et intitulé « Action » pour les actions ; mention « chemin protégé » partout ; renvois corrigés ; un seul texte de `README.md` ; termes du Technical Plan repris ; « manque ou diffère » ; formulations précisées ; commentaires en français ; fichier de test à part pour `conftest.py` ; « essai réussi ou décision consignée » |
| ir-1-14 : `settings.local.json`, modèle de `.gitignore` | Low | PROPOSE FIX | `.claude/settings.local.json` ignoré ; modèle cité par son URL, et SHA du commit noté dans les notes |
| ir-1-15 : commande d'essai du hook | Low | PROPOSE FIX | `git commit -n --allow-empty --dry-run -m test` : sans effet dans tous les cas, avec son message de refus attendu |
| ir-1-16 : chemins protégés absents de `CLAUDE.md` et du niveau 1 | Low | PROPOSE FIX | `CLAUDE.md` et le niveau 1 renvoient à `.github/chemins-proteges.txt`, qui fait foi ; l'écart est ajouté au tableau |
| ir-1-17 : étiquettes et jalons | Low | PROPOSE FIX | Commandes `gh api -X POST …/labels` et `…/milestones`, avec les titres et descriptions exacts |
| ir-1-18 : textes qui citent les essais | Low | PROPOSE FIX (en partie) | `--body-file` et `git commit -F` imposés pour les descriptions et messages. Les faux positifs restants sont acceptés, puisqu'ils ne donnent qu'un refus |
| ir-1-19 : forme de `required_status_checks` | Low | PROPOSE FIX | `contexts` ; aucune tâche obligatoire n'a de `name:` ni de matrice |
| cd-1-9 : `gh pr edit` dans Actions, description vide | Low | DECLINE (en partie) | `body: null` est traité. Le passage aux appels REST pour l'étiquette et la description est retenu, parce qu'il est aussi plus simple à tester. Le risque cité sur `projectCards` est jugé non vérifiable et n'entre pas dans le document |
| cd-1-10 : structure de `ruleset-main.json` | Low | PROPOSE FIX | Le fichier n'est écrit que si la solution de rechange est déclenchée (étape 8, N-2), avec sa structure et sa commande données à ce moment-là |
| cd-1-11 : `git push` sans `-u` à l'essai E5 | Low | PROPOSE FIX | `git push -u origin essai/faux-secret-github` |
| cd-1-12 : module qui appelle `scenarios()` | Low | PROPOSE FIX | `tests/scenarios/test_scenarios.py`, chemin protégé, qui charge tous les `.feature` |
| Étape 8, N-3, N-4 et N-5 | Low | PROPOSE FIX | Installation de `gitleaks` (version, somme, emplacement `~/.local/bin`) ; hook appelé par `$CLAUDE_PROJECT_DIR`, à vérifier en phase 0 ; `git init -b main` au début de la phase 1 |
| Tour 2 : egm-structural-2-16 et egm-design-2-2 | Low | PROPOSE FIX | Ordre des essais : E7 avant E4. La liste blanche autorise `gh pr create --body-file`, l'écriture de la description par l'API sur `pulls`, et la suppression des branches `essai/…` |
