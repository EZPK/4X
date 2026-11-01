# Compte rendu de M0 : garde-fous et squelette du dépôt

*   **Document suivi :** `docs/designs/niveau-2-m0-garde-fous.md` (Approved), plan détaillé, points 1 à 47.
*   **Date des travaux :** 2026-11-01.
*   **Rédigé par :** l'agent de code, à partir de ses notes de travail (`notes-m0.md`, non versionné), puis corrigé après une revue EGM sans contexte (deux relecteurs : exactitude, lecture naïve).
*   **Statut de M0 :** `approuvé` dans `docs/feuille-de-route.md`. Seul le propriétaire peut le déclarer `livré` (point 48).

Aucun faux secret n'est recopié ici. Les sorties de `gitleaks` ont été produites avec `--redact`, et la valeur du terme interdit de l'essai E9 est masquée.

**Conventions.**
- « Point N » renvoie au plan détaillé du document de M0 ; « Technical Plan, point N » renvoie à sa partie technique.
- Une commande précédée de `!` est tapée par le propriétaire lui-même dans le prompt de Claude Code. Elle s'exécute sans passer par l'agent de code, ni par le hook Claude Code (section 6.4).
- La « valeur d'essai du projet » est un faux secret au format `FOURX_ESSAI_SECRET_` suivi de caractères tirés au hasard, reconnu par la seule règle `gitleaks` propre au projet (`fourx-essai-secret`).

## 1. Résultat en bref

**Ce qui marche.**
- La protection de `main` refuse le push direct et la fusion d'une pull request rouge, même pour un administrateur (E2, E3).
- Le hook Claude Code refuse toutes les commandes interdites essayées, et la règle `deny` refuse l'édition de `.claude/` (E4).
- Le hook pre-commit refuse les deux faux secrets (E5, E6). La CI détecte la valeur d'essai (E6), refuse un ajout injustifié à la liste des scénarios en attente (E8) et un terme interdit (E9).
- Le contrôle de garde étiquette une pull request qui touche un chemin protégé et met la liste en tête de sa description (E7).
- Aucun runner auto-hébergé ; jalons M0 à M6 créés (E10).

**Ce qui n'est pas démontré.**
- **Le blocage des secrets de GitHub** n'a pas arrêté le faux jeton GitHub de E5 : résultat consigné « blocage non démontré », comme le plan le prévoit. La CI n'a pas vu ce jeton non plus, car il a été poussé sans pull request (section 6.2).
- **Le résumé de la tâche `garde`** de E7 n'a pas pu être lu par l'agent de code : vous devez le vérifier à l'œil.
- **Les règles `deny` sur Bash** n'ont jamais été vues agir seules : le hook a refusé chaque commande avant elles. Seule la règle `deny` sur l'édition de `.claude/` est démontrée.
- **Les trois exceptions d'amorçage du hook** n'ont jamais été vues accepter une commande : elles ne sont vérifiées que par les tests du hook.

Sur les dix essais du plan (E1 à E10), huit donnent tout le résultat attendu. E7 le donne sauf le résumé de la tâche, à vérifier. E5 est partiel.

**Ce que vous devez faire :** voir la section 9.

Les écarts au plan, les réserves et les choix de réalisation sont décrits à la section 6.

## 2. Phase 0 : décision et vérifications préalables

- **Point 1 :** le propriétaire a approuvé le document de M0 (« j'approuve »). Son statut est passé à `Approved`, et M0 à `approuvé` dans la feuille de route.
- **Point 2 :** Claude Code 2.1.306 (`claude --version`). Vérifications faites le 2026-11-01 dans la documentation de code.claude.com (pages `permissions.md`, `hooks.md`, `settings.md`, `interactive-mode.md`), sans essai local :
  - **Règles `deny` :** syntaxe `Bash(gh pr merge *)`, où `*` couvre tout, espaces compris ; les règles `deny` passent avant les règles `allow`. **Écart :** une règle `Write(...)` sur un chemin ne s'applique à rien ; les règles d'édition s'écrivent `Edit(/.claude/**)` et `Edit(/.git/hooks/**)`. Un chemin qui commence par `/` est relatif au dossier du fichier de réglages.
  - **Hook `PreToolUse` :** le code de sortie 2 bloque ; les autres codes non nuls ne bloquent pas. **Écart :** un hook qui dépasse son délai ne bloque pas, sauf avec `"onFailure": "block"` (Claude Code 2.1.295 ou plus). Le hook est déclaré avec `"timeout": 30` et `"onFailure": "block"`, placés dans l'objet du hook, à côté de `type` et `command`, d'après la page des hooks relue avant l'écriture de `.claude/settings.json`.
  - **`CLAUDE_PROJECT_DIR`** est fourni au hook et utilisable dans sa commande, entre guillemets.
  - **Réglages modifiés en cours de session :** relus aussitôt, `permissions` et `hooks` compris. Le point 36 a donc été fait dans la même session, et le hook y a bien refusé une commande (section 4).
  - **Commandes `!` :** la documentation ne dit pas si elles passent par le hook. L'essai du point 45 a montré que non (section 6.4).

  Les deux écarts ont été signalés au propriétaire, qui a choisi « Ajuster et continuer » : le document de M0 a été corrigé sur ces deux points après son approbation, avant le commit initial.
- **Point 4 :** `gitleaks` 8.30.1, téléchargé dans un dossier temporaire, somme SHA-256 vérifiée, installé dans `~/.local/bin`.

## 3. Versions épinglées

| Élément | Version | Publiée le | Empreinte ou contrainte |
| :-- | :-- | :-- | :-- |
| `gitleaks` | 8.30.1 | 2026-03-21 | SHA-256 de `gitleaks_8.30.1_linux_x64.tar.gz` : `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` |
| `actions/checkout` | v7.0.1 | 2026-07-20 | commit `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `astral-sh/setup-uv` | v10.3.0 | 2026-10-09 | commit `1c37ad07a6a961277cf70c0d37d6f313000f5884` |
| `uv` | 0.11.16 | 2026-05-21 | contrainte `required-version = ">=0.11.16"` ; pas d'empreinte du binaire |
| modèle `.gitignore` | `github/gitignore`, `Python.gitignore` | — | commit `7705c2cd7cfe56c5b9b5c1000844a17f573cf5f1` |

Python installé : 3.15.0. Les dépendances de développement sont résolues avec `exclude-newer = "2026-10-18"` (2026-11-01 moins 14 jours) : ruff 0.17.1, mypy 2.4.0, pytest 9.1.1, pytest-bdd 9.0.0, import-linter 2.15, pre-commit 4.7.0. Leurs sommes de contrôle sont dans `uv.lock`, et `uv sync --locked` les vérifie. Le document de M0 cite `pytest-bdd` 9.0.1 au point 25 ; la version installée est 9.0.0, et le comportement cité (`NoScenariosFound` sans `.feature`) a été vérifié sur cette version.

## 4. Préparation locale et commit initial

- **Contrôles avant le commit initial (point 37) :**
  - `uv run ruff check .` et `uv run ruff format --check .` : verts ;
  - `uv run mypy` : « Success: no issues found in 24 source files » ;
  - `uv run pytest` : « 286 passed » ;
  - `uv run lint-imports` : « Contracts: 7 kept, 0 broken » ;
  - contrôle des termes interdits : code 0 ;
  - `gitleaks git --pre-commit --staged --redact --config .gitleaks.toml .` : « no leaks found ».
- **Relecture du contenu indexé :** 75 fichiers, 11 090 lignes. Les fichiers écrits pendant M0 ont été relus un par un. Dans l'ensemble, une recherche des adresses e-mail, adresses IP, jetons et mots de passe n'a trouvé que les plages d'adresses privées génériques citées dans un rapport de revue, et le préfixe `ghp_` cité dans les textes.
- **Hook Claude Code avant activation (point 34) :** `gh pr merge 1` donne un message de refus et le code 2 ; `ls` donne 0.
- **Hook actif (point 36) :** `git commit -n --allow-empty --dry-run -m test` est refusé : « git commit -n (CLAUDE.md, « Ne jamais » : utiliser --no-verify ; tout contournement du hook pre-commit est refusé) ».
- **Commit initial :** `544c2ac`, « M0 : documents et garde-fous initiaux », auteur `EZPK`, avec l'adresse e-mail choisie par le propriétaire. Le hook pre-commit a lancé `gitleaks` pendant le commit : « Passed ».
- **Analyse de l'historique avant le push (point 40) :** `gitleaks git --redact --config .gitleaks.toml .`, lancée par l'agent de code : « 1 commits scanned », « no leaks found », code 0.
- **Analyse finale du dossier de travail (plan de vérification) :** `gitleaks dir --redact --config .gitleaks.toml .` : « no leaks found ». Comme `gitleaks dir` saute les fichiers ignorés par git, `notes-m0.md` a été analysé à part : « no leaks found ».

## 5. Création du dépôt, amorçage et réglages GitHub

| Étape | Commande | Lancée par | Résultat |
| :-- | :-- | :-- | :-- |
| Point 38 | `gh repo create EZPK/4X --public --source .` | agent de code | accepté par le hook (dépôt absent) ; `https://github.com/EZPK/4X`, dépôt vide |
| Point 39, blocage des secrets | `gh api -X PATCH repos/EZPK/4X --input .github/securite-depot.json` | agent de code | refusée par le hook : « blocage des secrets déjà actif : exception refermée ». La lecture faite juste après la création du dépôt montrait déjà `secret_scanning_push_protection` à `enabled` ; la commande n'a donc jamais été exécutée |
| Point 40, push initial | `git push -u origin main` | **propriétaire**, par `!` | « * [new branch] main -> main » ; `main` distante = `544c2ac` |
| Point 41, protection de `main` | `gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json` | **propriétaire**, par `!` | protection créée, `enforce_admins.enabled` = `true` |
| Point 42 | création de l'étiquette « fichiers protégés modifiés » | agent de code | couleur `d93f0b` |
| Point 44 | sept créations de jalons, M0 à M6 | agent de code | numéros GitHub 1 à 7 |

**Lectures des réglages (point 43) :**
- `gh api repos/EZPK/4X/branches/main/protection` :
  - `enforce_admins` : true ;
  - `allow_force_pushes` : false ;
  - `allow_deletions` : false ;
  - `required_status_checks.strict` : true ;
  - contrôles exigés : `lint`, `typage`, `gitleaks`, `termes-interdits`, `tests-outillage`, `garde`, `en-attente` ;
  - approbations exigées : 0.

  Ces valeurs sont celles de `.github/protection-main.json` : la protection posée par la commande `!` du propriétaire est bien celle du plan.
- `gh api repos/EZPK/4X` : `secret_scanning` et `secret_scanning_push_protection` valent `enabled`.
- `gh api repos/EZPK/4X/actions/permissions/workflow` : `default_workflow_permissions` vaut `read`, `can_approve_pull_request_reviews` vaut `false`.

Les deux doutes du Technical Plan, point 4, sont levés : l'application de la protection aux administrateurs et le blocage des secrets au push sont disponibles sur ce dépôt public gratuit. Le second est disponible, mais l'essai E5 ne l'a pas vu agir (section 7).

**Nouvelles tentatives des trois commandes d'amorçage :** toutes refusées par le hook, avec « exception refermée » (« blocage des secrets déjà actif » ; « main existe déjà sur GitHub » ; « main est déjà protégée »). Elles ont été rejouées à l'essai E4, avec le même résultat.

**Contrôles exigés et tâches réelles (Technical Plan, point 4) :** sur la première pull request d'essai (n°1), les sept contrôles exigés existent comme tâches, sous le même nom, toutes rattachées au commit de tête `c7b587181e317c620811b6f7920cde4e6812a1e2`, y compris les deux tâches de `garde.yml`, lancées par `pull_request_target`.

## 6. Écarts au plan, réserves et choix de réalisation

### 6.1 Écarts au plan

1. **Push initial et protection de `main` lancés par le propriétaire.** Le plan confie les trois commandes d'amorçage à l'agent de code. Le mode automatique de Claude Code, réglé pour la session et non dans le dépôt, fait juger les commandes par un classificateur avant de les exécuter. Ce classificateur a refusé les deux dernières, avec les motifs « [Git Destructive] » pour le push et « [CI Bypass] » pour la protection. Il ne fait pas partie des garde-fous de M0, et peut refuser d'autres commandes à l'avenir. On suppose que le hook aurait accepté ces deux commandes, puisque leurs conditions étaient remplies (`main` absente de GitHub, puis non protégée) ; **ce n'est pas vérifié**. L'agent de code n'a pas contourné le refus ; le propriétaire a lancé les deux commandes lui-même par `!`, donc sans passer par le hook. La lecture des réglages (section 5) montre que le résultat est bien celui de `.github/protection-main.json`.
2. **Blocage des secrets déjà actif.** La première commande d'amorçage n'a jamais été exécutée : GitHub avait déjà activé le blocage sur ce dépôt public neuf, et le hook l'a refusée (section 5). Avec le point 1, aucune des trois exceptions d'amorçage du hook n'a été vue accepter une commande en réel ; ce chemin n'est vérifié que par `tests/outillage/test_garde_commandes.py`.
3. **Document de M0 corrigé après son approbation**, sur les deux écarts du point 2 (section 2), à la demande du propriétaire.
4. **Ordre des essais.** Le point 46 fixe E1, E2, E3, E7, E4, E5, E6, E8, E9, E10. L'ordre joué est E1, E2, E3, E7, E4, E8, E9, E10, E5, E6 : E5 et E6, où le propriétaire committe et pousse lui-même un faux secret, ont été joués à la suite, en dernier. La seule dépendance du plan (E4 après la pull request verte de E7) est respectée.
5. **Formes des commandes de E2 et E3.**
   - E2 : `! git push origin essai/push-direct:main` au lieu de `HEAD:main`. C'est la même cible, sans changer de branche.
   - E3 : `! gh pr merge 1 --admin --squash` au lieu de `--admin` seul, car `gh` exige une méthode de fusion hors mode interactif. Le premier essai, sans méthode, n'était pas parti vers GitHub.
6. **`pytest-bdd` 9.0.0 au lieu de 9.0.1** (section 3).

### 6.2 Réserves

1. **Résumé de la tâche `garde` non lu par l'agent de code.** L'API ne l'expose pas (`output.summary` vaut `null`), et la page publique du run ne l'affiche pas sans connexion. L'étape qui l'écrit a réussi. **Vérification à faire par le propriétaire :** ouvrir, connecté à GitHub, https://github.com/EZPK/4X/actions/runs/41289483420. C'est le run de `garde.yml` lancé à l'ouverture de la pull request 2 (E7). Sur la page de synthèse du run, sous la tâche `garde`, le résumé doit contenir la liste des fichiers protégés modifiés, avec `CLAUDE.md`. On peut aussi le vérifier sur la pull request qui ajoute ce compte rendu : elle touche `docs/revues/`, donc le résumé de sa tâche `garde` doit lister ce fichier.
2. **Faux jeton GitHub (E5).** GitHub a accepté le push. Cause probable, **non vérifiée** : un vrai jeton GitHub contient une somme de contrôle, qu'un jeton tiré au hasard n'a pas, et GitHub l'ignore alors. La lecture des alertes (`[]`), faite juste après la suppression de la branche, ne montre rien de plus.
3. **Secret poussé sur une branche sans pull request.** `ci.yml` ne tourne que sur les pull requests et sur les pushs vers `main`. Un secret poussé sur une autre branche, sans pull request, est donc publié sans que la CI le voie ; seuls le hook pre-commit et le blocage de GitHub le couvrent. C'est le cas de E5.
4. **Règles `deny` sur Bash non isolées.** Les règles `deny` sur `gh pr merge`, le push forcé, `--no-verify` et `gh repo edit` existent dans `.claude/settings.json`. À E4, le hook a refusé chaque commande, et aucune de ces règles n'a été vue agir seule. Pour les isoler, il faudrait mettre le hook hors service. Seule la règle `deny` sur l'édition de `.claude/` est démontrée.
5. **Faux positifs connus du hook Claude Code.** Ils refusent à tort, ce qui va dans le sens de la sécurité :
   - toute commande dont le texte contient `--no-verify` est refusée, même s'il s'agit d'un texte, par exemple un message de commit. C'est voulu : le motif est cherché dans toute la chaîne ;
   - `gh api … 2>&1` est refusé (« gh api avec deux points d'accès »), parce que le `2` de la redirection est pris pour un argument ;
   - un mot `gh` ou `git` passé en argument, comme dans `grep gh fichier`, est analysé comme une commande et peut être refusé.

   Les deux derniers sont à corriger après M0 (section 9).

### 6.3 Choix de réalisation non détaillés par le document

- **Le hook refuse aussi**, entre autres : `gh auth token`, `gh pr close` (la fermeture passe par l'API), `gh alias`, `gh extension`, `gh secret`, l'écriture par `gh api` avec `--input` hors amorçage, et `git commit` lancé dans un autre dossier. Un `git push` lancé dans un autre dossier n'est refusé que sans refspec explicite ou avec `HEAD` ; un push vers `main` est refusé dans tous les cas.
- **Un contrôle est réduit :** `ruff` n'analyse ni ne reformate le Markdown (`extend-exclude = ["*.md"]`), sinon `ruff format` aurait réécrit un rapport de revue protégé.
- **Titres de scénarios en double :** `tests/scenarios/conftest.py` relit les fichiers `.feature` pour les trouver, car `pytest-bdd` les écrase sans erreur. Le lien entre test et scénario passe par une structure interne de `pytest-bdd` (`scenario_wrapper_template_registry`), qu'une mise à jour peut changer, et que `test_conftest_scenarios.py` surveille.

### 6.4 Commandes `!` du propriétaire (point 45)

`! git commit -n --allow-empty --dry-run -m test` s'exécute sans message du hook. Les commandes `!` ne passent donc pas par le hook, et les essais du propriétaire ont été faits depuis le prompt de Claude Code.

## 7. Les essais du critère de sortie

Chaque pull request d'essai a été fermée sans fusion, et sa branche supprimée. À la fin, `main` est toujours au commit `544c2ac`, et aucune pull request n'est ouverte. L'ordre joué est décrit en section 6.1, point 4.

| Essai | Qui | Lien ou sortie | Refus et origine | Résultat |
| :-- | :-- | :-- | :-- | :-- |
| E1. CI de `main` | agent de code | https://github.com/EZPK/4X/actions/runs/41289002414 | — | réussi : `lint`, `typage`, `gitleaks` (tout l'historique du premier push), `termes-interdits`, `tests-outillage` et `imports` en `success` |
| E2. Push direct sur `main` | propriétaire | `! git push origin essai/push-direct:main` | **GitHub** : « GH006: Protected branch update failed for refs/heads/main. — Changes must be made through a pull request. — 7 of 7 required status checks are expected. … (protected branch hook declined) » | réussi |
| E3. Pull request rouge | agent de code ouvre, propriétaire tente | https://github.com/EZPK/4X/pull/1 ; `lint` en échec : https://github.com/EZPK/4X/actions/runs/41289224643/job/124796790678 ; `mergeStateStatus` = `BLOCKED` | **GitHub**, sur `! gh pr merge 1 --admin --squash` : « GraphQL: Required status check "lint" is failing. (mergePullRequest) » | réussi |
| E7. Chemin protégé | agent de code | https://github.com/EZPK/4X/pull/2 ; run de `garde` à l'ouverture : https://github.com/EZPK/4X/actions/runs/41289483420 ; tous les contrôles en `success` | — | réussi, **sauf le résumé de la tâche, à vérifier par le propriétaire** (section 6.2, point 1) : étiquette « fichiers protégés modifiés » ; bloc `<!-- garde:debut -->` … `CLAUDE.md` … `<!-- garde:fin -->` en tête de la description ; après réécriture de la description sans le bloc, l'événement `edited` a relancé le garde (run `41289572627`), qui a remis le bloc en tête |
| E4. Interdictions de Claude Code | agent de code, sur la pull request 2 verte | voir la liste sous ce tableau | **hook Claude Code** pour les commandes Bash ; **règle `deny`** pour l'édition de `.claude/settings.json` | réussi : tout est refusé. Après coup, `.claude/settings.json` est intact, la pull request 2 non fusionnée, et `main` inchangée |
| E8. Scénario en attente | agent de code | https://github.com/EZPK/4X/pull/3 ; https://github.com/EZPK/4X/actions/runs/41289723344/job/124798251668 | **CI**, tâche `en-attente` : « entrée ajoutée : essai.feature::Scénario d'essai E8 », « refus : un ajout exige une pull request qui modifie un fichier .feature ». La tâche `tests-outillage` échoue aussi, comme prévu au Technical Plan, point 10 (une entrée sans scénario fait échouer la session pytest) : « ERROR: en_attente.txt : aucun scénario essai.feature::Scénario d'essai E8 » | réussi |
| E9. Terme interdit | agent de code | https://github.com/EZPK/4X/pull/4 ; https://github.com/EZPK/4X/actions/runs/41289812337/job/124798526493 | **CI**, tâche `termes-interdits` : « src/fourx/essai_terme_interdit.py:3: terme « … » » (terme masqué ici) | réussi |
| E10. Runners et jalons | agent de code | `gh api repos/EZPK/4X/actions/runners` → `{"total_count":0}` ; `gh api repos/EZPK/4X/milestones --jq '.[] \| [.number, .title, .description] \| @tsv'` → sept lignes, de « 1 M0 Critère de sortie et document de niveau 2 : voir docs/feuille-de-route.md, ligne M0. » à « 7 M6 … ligne M6. » (description relue le 2026-11-01 pour ce compte rendu) | — | réussi |
| E5. Faux jeton GitHub | propriétaire | branche `essai/faux-secret-github`, faux jeton `ghp_` suivi de 36 caractères tirés au hasard, sans pull request | **hook pre-commit** : « gitleaks (fichiers indexés)….Failed », « leaks found: 1 ». Le commit qui contourne le hook (`70f8d00`), puis `! git push -u origin essai/faux-secret-github` : **accepté par GitHub** | partiel : **blocage non démontré** (section 6.2, points 2 et 3). Branche distante supprimée aussitôt ; `gh api repos/EZPK/4X/secret-scanning/alerts` → `[]` |
| E6. Valeur d'essai du projet | propriétaire commit et push, agent de code ouvre la pull request | https://github.com/EZPK/4X/pull/5 ; https://github.com/EZPK/4X/actions/runs/41290092466/job/124799357218 | **hook pre-commit** : « Failed », « leaks found: 1 ». Après le commit qui contourne le hook (`1cd81ef`) et le push : **CI**, tâche `gitleaks` en échec, « leaks found: 1 ». La règle déclenchée, lue en relançant `gitleaks` en local avec un rapport JSON masqué, est `fourx-essai-secret` (`essai-e6.txt`, ligne 2) | réussi |

**Commandes de l'essai E4.** Pendant l'essai, chaque commande Bash a été refusée par le hook Claude Code ; seul le motif court a été noté. Les messages complets ci-dessous ont été reproduits le 2026-11-01, pour ce compte rendu, en passant chaque commande au script du hook (`.claude/hooks/garde_commandes.py`) sans l'exécuter. Chaque message commence par « Refusé par le hook Claude Code : » et finit par la règle de `CLAUDE.md` citée, omise ici :
- `gh pr merge 2`, `gh pr merge 2 --admin`, `gh pr merge 2 --auto` : « fusion de pull request » ;
- `git push origin main` : « git push vers « main » » ;
- `git push origin HEAD:main` : « git push vers « HEAD:main » » ;
- `git push --force origin essai/chemin-protege` : « git push --force » ;
- `git commit --no-verify` : « option --no-verify » ;
- `git commit -n` : « git commit -n » ;
- `gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json --silent` : « gh api en écriture avec --input, hors amorçage » ;
- `gh repo edit EZPK/4X --description essai` : « modification du dépôt » ;
- les nouvelles tentatives des trois commandes d'amorçage : « exception refermée » (section 5).

L'édition de `.claude/settings.json` a été refusée par la règle `deny` : « File is in a directory that is denied by your permission settings. »

**Les faux secrets** ne donnent accès à rien, et n'ont été fusionnés dans aucune branche. La valeur d'essai de E6 reste lisible dans la pull request fermée n°5 (commit `1cd81ef`). Le jeton de E5 n'est dans aucune pull request, mais GitHub peut garder le commit `70f8d00` accessible par son SHA.

## 8. Objectifs et critère de sortie

| Objectif du document de M0 | Preuve | État |
| :-- | :-- | :-- |
| 1. Le dépôt public existe et contient les documents | `gh repo view EZPK/4X --json visibility` → `PUBLIC` ; `git log --first-parent origin/main` → `544c2ac M0 : documents et garde-fous initiaux` seul ; E2 | atteint |
| 2. Une pull request rouge ne peut pas être fusionnée, même par un administrateur | E3, refus de GitHub | atteint |
| 3. Claude Code refuse les commandes interdites | E4 ; 215 cas dans `tests/outillage/test_garde_commandes.py` | atteint par le hook ; règles `deny` sur Bash non isolées, exceptions d'amorçage non vues en réel (section 6.2, point 4 ; section 6.1, point 2) |
| 4. Un secret est arrêté avant de devenir public, et la CI détecte ceux qui passent | E5 et E6 : le hook pre-commit refuse les deux ; la CI détecte la valeur d'essai | atteint pour le hook pre-commit et la CI ; **blocage au push non démontré** ; secret poussé sans pull request non vu par la CI (section 6.2, points 2 et 3) |
| 5. Une pull request qui touche un chemin protégé est signalée | E7 | atteint, **sous réserve** de la vérification du résumé de la tâche par le propriétaire |
| 6. Un scénario ne peut pas être mis « en attente » pour cacher une régression | E8 | atteint |
| 7. La CI tourne et passe sur le projet vide | E1 ; `garde` et `en-attente` en `success` sur la pull request 2 (E7) ; E9 | atteint |
| 8. Aucun runner auto-hébergé | E10 | atteint |
| 9. La feuille de route est copiée dans les jalons GitHub, et les choix renvoyés à M0 sont tranchés | E10 (descriptions des jalons) ; Technical Plan, point 1 ; glossaire mis à jour (plan détaillé, point 29) ; ADR 0001 acceptée par le propriétaire | atteint |

| Élément du critère de sortie de M0 (niveau 1, §11) | Preuve | État |
| :-- | :-- | :-- |
| Une pull request qui touche un chemin protégé est étiquetée et signalée | E7 | atteint, sous réserve du résumé de la tâche |
| Une pull request rouge ne peut pas être fusionnée, même par une tentative en administrateur | E3 | atteint |
| `gh pr merge` est refusé par les permissions de Claude Code | E4 : le refus constaté vient du hook ; les règles `deny` `Bash(gh pr merge)` et `Bash(gh pr merge *)` sont aussi présentes dans `.claude/settings.json`, mais leur effet propre n'a pas été isolé | atteint par le hook ; règles `deny` non isolées |
| Un faux secret est refusé par le hook pre-commit et en CI | E5 et E6 (hook pre-commit), E6 (CI) | atteint |
| La CI tourne sur un projet vide | E1 | atteint |

## 9. Ce qui reste à faire

**Par le propriétaire, dans cet ordre :**
1. Vérifier le résumé de la tâche `garde` (section 6.2, point 1). S'il ne liste pas `CLAUDE.md`, l'objectif 5 n'est pas atteint : ne pas déclarer M0 livré.
2. Décider si le refus de `gh pr merge` par le hook suffit pour l'élément « refusé par les permissions de Claude Code » du critère de sortie, ou demander un essai qui isole les règles `deny` (section 6.2, point 4).
3. Prendre acte de « blocage au push non démontré » (E5) et du secret poussé sans pull request non vu par la CI, ou demander un autre essai ou un changement de `ci.yml` (section 6.2, points 2 et 3).
4. Dire si l'écart d'amorçage (section 6.1, point 1) doit être reporté dans `CLAUDE.md` ou le document de niveau 1, qui confient les trois commandes à l'agent de code.
5. Fusionner la pull request de ce compte rendu.
6. Déclarer M0 livré, ou non (point 48).

**Après M0, par une pull request protégée :** corriger les faux positifs `2>&1` et « mot `gh` ou `git` en argument » du hook (section 6.2, point 5). Le propriétaire lève localement la règle `deny` sur `.claude/`, l'agent de code fait la correction, puis le propriétaire remet la règle avant d'ouvrir la pull request.

**Preuve en vidéo :** pas de vidéo pour M0, conformément au document de M0 (Non-Goals) : la vidéo arrive avec le client, à M3. Les preuves sont les liens vers les contrôles et les sorties citées ici.
