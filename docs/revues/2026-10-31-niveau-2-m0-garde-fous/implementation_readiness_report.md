# Rapport de revue Goldfish : étape 9 (test de préparation à l'implémentation), tour 1

**Cible :** /home/ezpk/Projects/4X/docs/designs/niveau-2-m0-garde-fous.md (l. 557 à 811, « Detailed Implementation Plan » et « Verification Plan »). Les l. 1 à 556 (la spécification) servent de référence.
**Date :** 2026-11-01
**Standard :** /home/ezpk/.claude/plugins/cache/egm/egm/0.1.0/resources/document_standards/implementation-readiness-standard.md (pour egm-implementation-readiness et egm-codebase-details) ; persona seul pour egm-style.

## État des relecteurs

| Relecteur | État | Constats bruts (Blocker / Major / Nit) |
| --- | --- | --- |
| `egm-implementation-readiness` | terminé, au premier essai | 0 / 14 / 11 |
| `egm-codebase-details` | terminé, au premier essai | 0 / 15 / 11 |
| `egm-style` | terminé, au premier essai | 0 / 10 / 13 (son en-tête annonçait 9 Major, mais il en liste 10) |

Après dédoublonnage : **0 Blocker, 24 Major, 19 Nit.** Quand plusieurs relecteurs signalent le même point, il porte la sévérité la plus haute qu'ils lui ont donnée.

Quatre faits textuels ont été revérifiés par le synthétiseur dans les fichiers :
- l'entrée « contrôle obligatoire » est déjà à la l. 151 de /home/ezpk/Projects/4X/docs/glossaire.md ;
- M0 est marqué « à écrire » à la l. 7 de /home/ezpk/Projects/4X/docs/feuille-de-route.md ;
- la règle d'arrêt est à la l. 11 de /home/ezpk/Projects/4X/CLAUDE.md ;
- les plages IPv4 privées sont citées à la l. 129 de /home/ezpk/Projects/4X/docs/revues/2026-10-31-niveau-2-m0-garde-fous/critic_report_tour2.md.

Les relecteurs n'ont lancé aucun outil. Leurs affirmations sur le comportement de `uv`, `import-linter`, `gitleaks`, `pre-commit`, `gh` et des runners de GitHub viennent de leurs connaissances. Le constat indique le degré de confiance du relecteur quand il l'a donné.

## Verdict

Le plan n'est pas prêt pour l'implémentation. Voici les réponses aux quatre questions posées.

1. **Peut-on l'exécuter fichier par fichier sans prendre de décision importante ?** Non. Plusieurs choix restent à l'exécutant :
   - les entrées et sorties des trois scripts ;
   - le contenu des quatre fichiers de configuration, de `.gitleaks.toml` et de `.pre-commit-config.yaml` ;
   - le système de construction et la politique de versions des dépendances Python ;
   - les actions GitHub à utiliser ;
   - la disposition des tests ;
   - le texte exact des règles de `CLAUDE.md` et du niveau 1.
2. **Chaque fichier touché est-il listé, avec quoi et pourquoi ?** Non. Il manque :
   - `docs/feuille-de-route.md` et le changement de statut de ce document ;
   - l'ADR qu'exigent E4 et E5 (point déjà accepté) ;
   - le module qui relie les scénarios à pytest ;
   - `.claude/settings.local.json`, absent du `.gitignore`.
3. **Chaque étape a-t-elle ses préconditions au moment où elle arrive ?** Pas toujours :
   - le hook est activé avant que ses tests aient tourné ;
   - le document est encore Proposed, alors que `CLAUDE.md` ordonne de s'arrêter dans ce cas ;
   - les résultats de la phase 0 n'ont nulle part où être écrits ;
   - le point 26 renvoie à une procédure qui n'existe pas ;
   - la vérification de `!` n'a pas d'étape.
4. **Le Verification Plan peut-il passer ?** Pas tel qu'il est écrit, même en mettant à part les points déjà acceptés :
   - `pytest` échoue à cause du commentaire de `en_attente.txt` ;
   - `lint-imports` échoue faute de `[build-system]` ;
   - la tâche `gitleaks` échoue sur le push initial ;
   - `gitleaks git` ne s'applique pas à un index sans commit ;
   - `pre-commit run --all-files` peut être vert sans rien prouver.

## Points déjà acceptés : effet sur le plan tel qu'il est écrit (non comptés)

Ces points ne sont pas de nouveaux constats. Les relecteurs indiquent où le plan échoue à cause d'eux, et deux d'entre eux élargissent le correctif prévu.
- **Règle `gitleaks` sur les IPv4 privées (egm-structural-2-2).** Elle détecte ce document (l. 323), mais aussi /home/ezpk/Projects/4X/docs/revues/2026-10-31-niveau-2-m0-garde-fous/critic_report_tour2.md (l. 129, vérifié). Ce fichier entre lui aussi dans le commit initial. Corriger la l. 323 ne suffit donc pas : il faut exclure le chemin `docs/revues/**` (ou un équivalent), ou reporter la règle. Sinon, `gitleaks` échoue au point 31 (l. 762) et au point 34 (l. 770).
- **`garde` et `en-attente` sur `main` (egm-structural-2-1).** L'essai E1, que lance le point 39 (l. 781), ne peut pas passer.
- **Pull request obligatoire (egm-design-2-7).** La l. 658 écrit `required_pull_request_reviews: null`, et l'essai E2 ne prouve donc rien. La copie de référence du hook doit suivre la correction (voir egm-codebase-details-1-6).
- **ADR pour E4 et E5 (egm-structural-2-4).** Aucun fichier `docs/adr/NNNN-….md (Create)` n'est prévu, ni aucune mise à jour d'un index d'ADR. L'ADR doit venir avant le point 29.
- **`fnmatch` et `**` (egm-design-2-6).** La correction proposée, `PurePosixPath.full_match`, demande Python 3.13 au moins. Le `python3` du runner est en 3.12 : voir egm-codebase-details-1-4.
- **Étape 8, constats non retenus :**
  - N-3 : `gitleaks` n'est pas installé, et aucune étape ne l'installe. Le point 31 et la l. 807 échouent ;
  - N-4 : le hook est appelé par un chemin relatif (l. 716) ;
  - N-5 : le hook est actif avant `git init` (l. 760).
- **Tour 2, constats acceptés :**
  - egm-structural-2-16 : « dans l'ordre » (l. 781) bloque à E4, qui a besoin de la pull request de E7 ;
  - egm-design-2-2 : `gh pr create`, `gh pr edit --body` et la suppression de branche ne sont pas autorisés par la liste blanche, et le hook les refuse.

## Constats classés

### A. Le Verification Plan échoue tel qu'il est écrit

#### egm-implementation-readiness-1-1 : le commentaire de `en_attente.txt` fait échouer pytest. Sévérité : Major
- **Relecteurs :** implementation-readiness (M9), codebase-details (M4), style (M3).
- **Lignes :** 695, comparée à 397-399 et 645.
- **Problème :** le point 22 met dans `en_attente.txt` « une ligne de commentaire qui explique le format ». La spécification parle d'« une entrée par ligne », ne définit aucun commentaire, et fait échouer la session quand une entrée ne correspond à aucun scénario.
- **Raison :** appliquée à la lettre, la règle traite le commentaire comme une entrée. `uv run pytest` (l. 763, l. 800) et `tests-outillage` sur `main` (E1) sont alors rouges. De son côté, `en_attente.py` compterait une modification du commentaire comme un ajout.
- **Correction :** au Technical Plan, point 10, et aux points 15 et 22, écrire : « les lignes vides et celles qui commencent par `#` sont ignorées par `conftest.py` et par `en_attente.py` ». Ajouter un test pour chacun au point 23.

#### egm-codebase-details-1-1 : sans `[build-system]`, `fourx` n'est pas installé et `lint-imports` échoue. Sévérité : Major
- **Relecteurs :** codebase-details (M2), implementation-readiness (M6).
- **Lignes :** 587-590, 599, 681, 805.
- **Problème :**
  - Le point 6 ne fixe ni `[build-system]` ni la forme du groupe de développement.
  - Sans système de construction, `uv sync` n'installe pas le projet (confiance haute).
  - `import-linter` ne trouve pas `fourx` sous `src/` (confiance moyenne à haute).
  - `uv sync --locked` n'installe le groupe par défaut que s'il s'appelle `dev`, dans `[dependency-groups]`.
- **Raison :** `uv run lint-imports` (l. 805) échoue, et le point 31 (« tous verts ») aussi. Choisir le backend de construction revient à choisir une dépendance, et le standard ne laisse pas ce choix à l'exécutant.
- **Correction :** au point 6, fixer `[build-system]` (`uv_build` ou `hatchling`, l'un des deux nommé) et `[dependency-groups] dev = [...]`.

#### egm-implementation-readiness-1-2 : la tâche `gitleaks` de la CI échoue au push initial. Sévérité : Major
- **Relecteurs :** implementation-readiness (M5), codebase-details (M6).
- **Lignes :** 672-681 (point 20), 770, 781 (E1) ; spécification l. 327.
- **Problème :**
  - « Les commits de la pull request ou du push » n'est traduit en aucune commande.
  - `actions/checkout` ne récupère qu'un commit par défaut.
  - Au premier push sur `main`, comme sur toute nouvelle branche, `github.event.before` vaut 40 zéros, et l'intervalle `avant..après` est invalide.
  - Le même manque touche les messages de commit que lit `termes-interdits`.
- **Raison :** E1 ne peut pas être vert sans une décision de l'exécutant.
- **Correction :**
  - `fetch-depth: 0` ;
  - SHA de base et de tête passés par `env:` ;
  - pour une pull request : `gitleaks git --redact --log-opts="$BASE..$HEAD"` ;
  - pour un push : `"$BEFORE..$AFTER"`, ou tout l'historique si `BEFORE` vaut le SHA nul.
  
  Ajouter ce cas aux attendus de E1.

#### egm-implementation-readiness-1-3 : le commit initial n'est pas une suite de commandes exécutable. Sévérité : Major
- **Relecteurs :** implementation-readiness (M13), codebase-details (M8, M7 en partie), style (N8, N9).
- **Lignes :** 756-764, 770.
- **Problème :**
  - Il n'y a aucun `git add`, aucune liste des fichiers attendus et aucune relecture `git diff --cached`, que `CLAUDE.md` impose pourtant.
  - « `gitleaks git` sur les fichiers indexés » ne fonctionne pas sans `--staged`, car il n'existe encore aucun commit (confiance haute).
  - `termes_interdits.py` parcourt les fichiers suivis : avant le `git add`, il n'y en a aucun, et le contrôle passe sans rien vérifier.
  - « Tous les contrôles de la CI lancés en local » est impossible pour `garde` et `en-attente`.
  - Rien ne dit quoi faire si un contrôle trouve quelque chose dans les documents existants.
- **Raison :** l'objectif 1 (contenu du commit initial) et l'exigence « aucun secret dans le commit initial » reposent sur cette étape.
- **Correction :** une liste numérotée :
  1. `git init -b main` ;
  2. `uv sync --locked` ;
  3. `uv run pre-commit install` ;
  4. `git add -A` ;
  5. `git status --short`, comparé à une liste attendue ;
  6. `gitleaks git --staged --redact` ;
  7. les commandes des l. 799 à 807 ;
  8. `git commit -m "…"`.
  
  Si un contrôle trouve quelque chose, on s'arrête et le propriétaire décide.

#### egm-codebase-details-1-2 : `.pre-commit-config.yaml` n'est pas donné, et `pre-commit run --all-files` ne prouve rien. Sévérité : Major
- **Relecteurs :** codebase-details (M7).
- **Lignes :** 624-627, 807.
- **Problème :**
  - Le YAML n'est pas donné.
  - Un hook local en `gitleaks git --staged`, avec `pass_filenames: false`, n'analyse que l'index, même lancé par `--all-files`. La vérification de la l. 807 est donc verte sans rien prouver.
  - Depuis pre-commit 4.4, `language: system` porte un autre nom, `unsupported` (confiance moyenne). Il faut choisir.
- **Raison :** c'est la première barrière contre les secrets, et la seule qui agit avant la publication.
- **Correction :** écrire le fichier exact (`repo: local`, `id`, `entry`, `language`, `pass_filenames: false`). Pour vérifier tout le dépôt, utiliser `gitleaks dir .`, ou `gitleaks git` après le commit.

### B. Ordre des étapes et préconditions

#### egm-implementation-readiness-1-4 : le statut du document et de la feuille de route n'est réglé avant aucune étape. Sévérité : Major
- **Relecteurs :** implementation-readiness (M1), codebase-details (M14).
- **Lignes :** 4, 559-570, 756-764, 795 ; /home/ezpk/Projects/4X/docs/feuille-de-route.md l. 7 ; /home/ezpk/Projects/4X/CLAUDE.md l. 11.
- **Problème :**
  - Le document est Proposed, et M0 est « à écrire ».
  - L'étape 4 de `CLAUDE.md` ordonne à l'agent de s'arrêter tant que le statut n'est pas « approuvé ».
  - Aucun point ne prévoit ce passage, et `docs/feuille-de-route.md` ne figure pas parmi les fichiers modifiés.
  - Après le point 35, ces deux fichiers sont protégés : les changer demanderait une pull request protégée.
- **Raison :** un exécutant qui suit `CLAUDE.md` s'arrête avant la phase 1. S'il continue, le commit initial publie un document Proposed.
- **Correction :**
  - Ajouter une étape du propriétaire avant le point 3 : le document passe à Approved, et M0 à « approuvé ».
  - Ajouter un point `docs/feuille-de-route.md (Modify)`, inclus dans le commit initial.
  - En phase 5, prévoir le passage à « livré » et à « Jalon en cours : M1 » par une pull request protégée.

#### egm-implementation-readiness-1-5 : le hook est activé avant d'avoir été testé, et rien n'est prévu s'il est cassé. Sévérité : Major
- **Relecteurs :** implementation-readiness (M2).
- **Lignes :** 698-721, 761-763.
- **Problème :**
  - Les tests du hook sont écrits au point 23, le hook est activé au point 25, et les tests ne tournent qu'au point 31.
  - Le hook refuse tout en cas d'erreur interne (l. 302), et la règle `deny` sur `.claude/**` est déjà active à ce moment-là.
- **Raison :** un défaut du hook (import, chemin, lecture du JSON) bloque toutes les commandes Bash, y compris `uv run pytest`. L'agent de code ne peut plus le corriger.
- **Correction :**
  - Avant le point 25, lancer : `uv sync`, `uv run pytest tests/outillage/test_garde_commandes.py`, `uv run ruff check .claude/hooks` et `uv run mypy .claude/hooks/garde_commandes.py`, puis le hook à la main avec un JSON `PreToolUse` d'exemple. Attendu : tout vert, et le code de sortie attendu pour le hook.
  - Ajouter une reprise : le propriétaire renomme ou corrige `.claude/settings.json` hors de Claude Code.

#### egm-implementation-readiness-1-6 : la « procédure notée en phase 0 » n'existe pas. Sévérité : Major
- **Relecteurs :** implementation-readiness (M3), style (M5).
- **Lignes :** 565, 721 ; spécification l. 105.
- **Problème :** le point 26 renvoie à une procédure qu'aucun point ne décrit : le point 1 se contente de vérifier et de noter. Le pronom « on » ne désigne personne.
- **Raison :** c'est la seule solution de secours si le garde-fou central n'est pas actif. L'exécutant devrait choisir seul : redémarrer la session, passer par le menu des hooks ou continuer.
- **Correction :** décrire la procédure au point 1, avec ses deux branches. Par exemple : « si le hook ne prend effet qu'au démarrage, le propriétaire ferme la session et en ouvre une nouvelle, qui reprend au point 26 ». Donner un attendu observable pour chaque branche. Au point 26, nommer qui agit.

#### egm-implementation-readiness-1-7 : la vérification que `!` échappe au hook n'a pas d'étape. Sévérité : Major
- **Relecteurs :** implementation-readiness (M4), style (M6).
- **Lignes :** 559, 565, 779-781 ; spécification l. 106.
- **Problème :**
  - La spécification prévoit une commande sans danger, lancée par le propriétaire avant les essais. Aucune étape ne la contient.
  - Le point 1 parle des « quatre points des Open Questions ». Or cette section a deux puces, et la seconde contient quatre sous-points.
- **Raison :** E2, E3, E5 et E6 en dépendent. Si `!` passe par le hook, le refus de E2 vient du hook et non de GitHub, et l'essai ne prouve plus rien.
- **Correction :**
  - Ajouter un point du propriétaire en tête de la phase 4 : une commande sans danger que le hook refuserait. Attendu : elle s'exécute, sans message du hook. Sinon, tous les essais du propriétaire se font dans un terminal hors de Claude Code.
  - Au point 1, écrire « les quatre points sur Claude Code des Open Questions ».

#### egm-style-1-1 : rien ne dit où les résultats sont gardés entre la phase 0 et la phase 5. Sévérité : Major
- **Relecteurs :** style (M4), implementation-readiness (N1), codebase-details (N5).
- **Lignes :** 563, 565, 566, 721, 785-789.
- **Problème :**
  - La l. 563 dit à la fois « rien n'est écrit dans le projet » et « les résultats vont dans le compte rendu ». Or le compte rendu est un fichier du projet, créé au point 40.
  - « Noter » et « citer » ne disent pas où.
- **Raison :** l'agent de code n'a pas de mémoire d'une session à l'autre. Si le compte rendu est écrit dès la phase 0, `git add -A` le met dans le commit initial, et le point 40 devient un Modify.
- **Correction :** nommer un emplacement provisoire, hors du dépôt ou ignoré par `.gitignore`. Ou bien créer le compte rendu en phase 1, dans le commit initial, et faire du point 40 un Modify.

#### egm-style-1-2 : on ne sait pas si chaque commande d'amorçage exige sa propre demande du propriétaire. Sévérité : Major
- **Relecteurs :** style (M9).
- **Lignes :** 768-771, comparées à 247 et 751.
- **Problème :** seul le point 32 porte la mention « à la demande explicite du propriétaire ». Le point 30, lui, écrit dans `CLAUDE.md` « à la demande explicite du propriétaire, chacune une seule fois ».
- **Raison :** c'est la condition humaine qui encadre les seules exceptions aux interdictions de `CLAUDE.md`.
- **Correction :** porter la mention sur les points 33 à 35, ou écrire en tête de la phase 2 « une demande du propriétaire couvre les points 32 à 35 ».

### C. Décisions laissées à l'exécutant

#### egm-implementation-readiness-1-8 : les entrées et sorties des trois scripts et de leurs étapes de workflow ne sont pas fixées. Sévérité : Major
- **Relecteurs :** implementation-readiness (M8), codebase-details (M5), style (M8).
- **Lignes :** 629-645, 672-688, 806 ; spécification l. 363, 379-388.
- **Problème :**
  - **`termes_interdits.py` :**
    - Ses entrées n'incluent pas la liste des fichiers modifiés, dont l'exception de la l. 387 a besoin. Le fichier d'événement ne la contient pas.
    - Ni la forme des arguments, ni le format du fichier des messages de commit, ni la commande qui le produit ne sont donnés.
    - Pour un push, rien ne dit quels messages vérifier.
    - On ne sait pas si la liste des fichiers exclus est écrite dans le script ou lue dans `docs/termes-interdits.md`.
    - « Lettre » n'est pas défini : ASCII ou Unicode (« concordé »).
    - Le point 20 et la l. 806 ne passent qu'un argument.
    - Dans « il en lit », « en » n'a pas d'antécédent clair.
  - **`garde.py` :**
    - Il calcule la nouvelle description, mais ne reçoit pas la description actuelle.
    - Le format de ses entrées et sorties n'est pas donné.
    - Les règles d'échappement ne sont pas fixées (que faire d'un accent grave dans un nom de fichier ?).
    - Le format du bloc et la commande `gh` qui écrit le corps manquent.
    - Rien ne renvoie au Technical Plan, point 8.
  - **`en_attente.py` :** ni les arguments, ni la normalisation des lignes, ni le cas d'un fichier absent dans l'une des versions. Le point 21 ne lui transmet pas la liste des fichiers modifiés.
  - **Contradiction :** la l. 363 confie l'appel à l'API aux scripts, la l. 640 le confie au workflow.
- **Raison :** chaque script et son workflow décrivent une même interface à deux endroits, et cette interface n'est définie nulle part.
- **Correction :**
  - Pour chaque script : la ligne de commande exacte, le format de chaque entrée et de chaque sortie, et les codes de sortie.
  - Pour chaque tâche : les étapes, et les commandes `gh` et `git diff --name-only` exactes.
  - Fixer une source unique pour les exclusions, et la classe de caractères des mots entiers.
  - Aligner la l. 363 sur la l. 640.

#### egm-implementation-readiness-1-9 : le contenu de `ruff.toml`, `mypy.ini`, `pytest.ini` et `.importlinter` est laissé à l'exécutant. Sévérité : Major
- **Relecteurs :** implementation-readiness (M10), codebase-details (M3, N8).
- **Lignes :** 592-599.
- **Problème :**
  - **`ruff.toml` :** ni `select`, ni `line-length`, ni `target-version`. L'essai E3 dépend pourtant d'une règle de `ruff`.
  - **`mypy.ini` :** ni `files`, ni `mypy_path = src`, ni `explicit_package_bases`, ni `python_version`. Des dossiers sans `__init__.py` produisent l'erreur « Duplicate module named ».
  - **`pytest.ini` :** ni `addopts` (`-p pytester`), ni `testpaths`, ni le mode d'import.
  - **`.importlinter` :** le type de contrat (`forbidden`, `layers`, `independence`) n'est pas choisi. Le tableau du niveau 1, §1, n'est pas une pile de couches stricte.
- **Raison :** ce sont des décisions durables. Ces fichiers sont protégés : une fois `main` protégée, chaque correction passera par une pull request protégée.
- **Correction :** donner le contenu exact des quatre fichiers, ou au moins chaque clé et sa valeur. Pour `.importlinter`, écrire un contrat `forbidden` par paquet, déduit du niveau 1, §1.

#### egm-implementation-readiness-1-10 : la disposition des tests de l'outillage n'est pas fixée, et la collecte peut casser. Sévérité : Major
- **Relecteurs :** implementation-readiness (M11), codebase-details (M3).
- **Lignes :** 698-706 ; spécification l. 403.
- **Problème :**
  - On ne sait pas si la « copie de `conftest.py` » est un fichier versionné (qui peut s'écarter de l'original sans que personne le voie) ou une copie faite pendant le test.
  - On ne sait pas comment `exemple/` échappe à la collecte de la session principale.
  - Les fichiers de `exemple/` ne sont pas nommés, et l'emplacement des `__init__.py` n'est pas dit.
  - La liste en attente propre à la session imbriquée (l. 403) n'apparaît pas au point 23.
- **Raison :** un module d'étapes ou un `conftest.py` en double fait échouer mypy (modules en double) ou pytest (conflit d'import). Le scénario d'exemple pourrait aussi tourner comme un vrai test.
- **Correction :**
  - Pendant le test : `pytester.makeconftest(Path("tests/scenarios/conftest.py").read_text())`.
  - Des noms de fichiers fixés pour `exemple/`.
  - `norecursedirs` ou `collect_ignore` pour `exemple/`.
  - Une liste en attente écrite par chaque test.
  - La liste des `__init__.py`.

#### egm-implementation-readiness-1-11 : le texte imposé de `CLAUDE.md`, du niveau 1 et de `termes-interdits.md` n'est pas donné. Sévérité : Major
- **Relecteurs :** implementation-readiness (M12, N7), codebase-details (M13), style (N10).
- **Lignes :** 577-580, 731-754.
- **Problème :**
  - Le niveau 1 (plan détaillé, point 6) impose « exactement » le texte de `CLAUDE.md`, et le point 29 veut qu'il soit mis à jour « à l'identique du point 30 ». Or le point 30 ne donne que des intentions, et il vient après le point 29.
  - Le point 30 attribue « les trois commandes d'amorçage » à chacune des deux règles. Pourtant, chaque règle ne concerne qu'une partie de ces commandes : le push initial pour la première, le `PATCH` et le `PUT` pour la seconde.
  - Le paragraphe définitif de `termes-interdits.md` et le commentaire de `.env.example` ne sont pas donnés non plus.
- **Raison :** l'agent de code rédigerait lui-même ses propres règles de travail, dans un chemin protégé et dans un document Approved.
- **Correction :** donner les phrases nouvelles mot pour mot, avant et après, pour `CLAUDE.md`, le niveau 1 §10 et `termes-interdits.md`. Nommer l'exception propre à chaque règle. Faire passer le point 30 avant le point 29, ou écrire « recopier le texte final du point 30 ».

#### egm-implementation-readiness-1-12 : les règles propres au projet dans `.gitleaks.toml` n'ont ni motif ni exclusion. Sévérité : Major
- **Relecteurs :** implementation-readiness (M14).
- **Lignes :** 619-622 ; spécification l. 139, 322-325, 424.
- **Problème :**
  - Le point 11 ne donne ni l'identifiant, ni le motif, ni la liste d'exclusion des trois règles.
  - Rien ne dit ce qui « suit » `FOURX_` (`=`, `:`, `export`, YAML ?) ni ce qu'est une « valeur non vide ».
  - Ce document et le rapport du tour 2 citent la règle `FOURX_`. Le cas est distinct du constat accepté sur les adresses IP.
- **Raison :** ce sont des choix de conception, et une règle mal faite fait échouer le commit initial.
- **Correction :** donner le fichier exact : `[extend] useDefault = true`, puis chaque `[[rules]]` avec son `id`, son `regex` et son `[rules.allowlist]`. Exclure au minimum `.env.example`, ce document, `.gitleaks.toml` et `docs/revues/**`.

#### egm-implementation-readiness-1-13 : la CI ne nomme pas ses actions et ne dit pas comment elle installe `uv` et Python 3.15. Sévérité : Major
- **Relecteurs :** implementation-readiness (M7), codebase-details (M1, en partie).
- **Lignes :** 566, 672-688.
- **Problème :**
  - Le point 2 épingle « chaque action tierce », mais aucune n'est nommée.
  - Rien ne dit comment `uv` et Python 3.15 arrivent sur le runner, ni si les actions de GitHub elles-mêmes sont épinglées.
  - La suite des étapes de chaque tâche n'est pas donnée.
- **Raison :** choisir une dépendance revient à l'exécutant, ce que le standard interdit.
- **Correction :**
  - Nommer les actions (`actions/checkout`, `astral-sh/setup-uv`…), toutes épinglées par SHA, avec la version de `uv`.
  - Écrire « Python installé par `uv` à partir de `.python-version` ».
  - Donner les étapes de chaque tâche.

#### egm-codebase-details-1-3 : la règle des 14 jours ne s'applique pas aux dépendances Python. Sévérité : Major
- **Relecteurs :** codebase-details (M1), implementation-readiness (M6), style (M7).
- **Lignes :** 566, 587-590, 601-604 ; spécification l. 176-177.
- **Problème :**
  - La l. 177 fixe la version épinglée de « chaque outil ou action ». Le point 2 ne l'applique qu'à `gitleaks` et aux actions.
  - Le point 6 ne met aucune borne aux dépendances, et le point 8 lance `uv lock`, qui prend la dernière version publiée.
- **Raison :** le plan contredit la spécification, et l'exécutant ne sait pas laquelle des deux suivre.
- **Correction :**
  - Au point 6 : `[tool.uv] exclude-newer = "<date du jour moins 14 jours>"`, des bornes basses égales aux versions vérifiées (l. 176), et `required-version` pour `uv`.
  - Noter dans le compte rendu la date et les versions obtenues.
  - Ou bien restreindre la l. 177 aux binaires et aux actions.

#### egm-codebase-details-1-4 : `garde.yml` ne fixe ni la version de Python, ni le cache, ni les droits de git. Sévérité : Major
- **Relecteurs :** codebase-details (M10).
- **Lignes :** 683-688 ; spécification l. 360-364.
- **Problème :**
  - Rien ne dit quel Python lance `garde.py` et `en_attente.py`. Le `python3` de `ubuntu-24.04` est en 3.12 (confiance haute pour cette image, moyenne pour `ubuntu-latest`).
  - Le cache de `astral-sh/setup-uv` est actif par défaut (confiance moyenne), ce qui contredit « aucun cache ».
  - `persist-credentials: false` n'est pas demandé.
- **Raison :** le typage vise 3.15, et la correction acceptée de `fnmatch` (`full_match`, Python 3.13 au moins) ferait planter le garde sur `main`. Plus aucune fusion ne serait alors possible.
- **Correction :** `actions/setup-python` épinglée par SHA, avec `python-version-file: .python-version`, sans cache ni `uv`. Pour `actions/checkout`, `persist-credentials: false`.

#### egm-codebase-details-1-5 : la liste des fichiers de `garde.yml` est paginée, et les renommages échappent au garde. Sévérité : Major
- **Relecteurs :** codebase-details (M9).
- **Lignes :** 638, 687 ; spécification l. 363 et objectif 5.
- **Problème :**
  - `GET pulls/{n}/files` renvoie 30 fichiers par défaut (confiance haute).
  - Pour un renommage, l'ancien nom est dans `previous_filename`. Un `git mv CLAUDE.md notes.md` n'est donc pas signalé si le script ne regarde que `filename`.
- **Raison :** dans ces deux cas, une modification d'un chemin protégé passe sans étiquette.
- **Correction :** `gh api --paginate …/pulls/$N/files` au point 21. Tester `filename` et `previous_filename` au point 14, et ajouter les deux cas à `test_garde.py`.

#### egm-codebase-details-1-6 : rien ne vérifie que les copies de référence du hook restent identiques aux fichiers JSON. Sévérité : Major
- **Relecteurs :** codebase-details (M11), implementation-readiness (N4).
- **Lignes :** 711, 716 ; spécification l. 231-237.
- **Problème :**
  - Le point 24 exige des copies « identiques », mais aucun test ne le vérifie.
  - « Identique » n'est pas défini : mêmes octets, ou même JSON une fois lu ?
  - Un écart n'apparaît qu'aux points 33 et 35. À ce moment, la règle `deny` sur `.claude/**` est déjà active.
- **Raison :** l'amorçage serait bloqué sans que l'agent de code puisse corriger le hook. La correction acceptée de `protection-main.json` rend cet écart probable.
- **Correction :** comparer le JSON une fois lu (`json.load`), et ajouter à `test_garde_commandes.py` un test qui compare chaque copie au fichier de `.github/`.

### D. Cohérence avec la spécification et les documents liés

#### egm-codebase-details-1-7 : « contrôle obligatoire » existe déjà dans le glossaire, et l'en-tête du glossaire ne prévoit pas d'entrée venue d'un niveau 2. Sévérité : Major
- **Relecteurs :** codebase-details (M12), style (M2, N11), implementation-readiness (N6).
- **Lignes :** 723-729 ; /home/ezpk/Projects/4X/docs/glossaire.md l. 8, l. 10 et l. 151.
- **Problème :**
  - Le point 27 présente « contrôle obligatoire » comme une nouvelle entrée. Elle existe déjà (l. 151), avec une définition différente de celle du Technical Plan, point 5.
  - Les l. 8 et 10 du glossaire font venir chaque définition et chaque identifiant du niveau 1.
  - « Un lien vers ce document » est moins précis que la règle du glossaire, qui lie une section.
- **Raison :** la règle « chaque terme a une seule entrée » serait enfreinte, ou deux définitions se contrediraient.
- **Correction :**
  - Faire de « contrôle obligatoire » un Modify de l'entrée existante.
  - Donner le texte exact des entrées.
  - Ajouter au point 27 la retouche des l. 8 et 10.
  - Lier chaque entrée à la section qui définit le terme.

#### egm-codebase-details-1-8 : la couverture annoncée par le Verification Plan dépasse les tests prévus. Sévérité : Major
- **Relecteurs :** codebase-details (M15), style (M10), implementation-readiness (N5).
- **Lignes :** 701-706, comparées à 808, 332, 379-385, 401.
- **Problème :** la l. 808 annonce un test pour chaque règle des points 8, 9 et 10. Le point 23 n'en prévoit pas pour :
  - les lignes vides et `#` de `chemins-proteges.txt` ;
  - le résumé `$GITHUB_STEP_SUMMARY` ;
  - une pull request qui ne touche plus aucun chemin protégé. Rien ne dit non plus ce que fait `garde` dans ce cas : retirer l'étiquette et le bloc, ou non ;
  - la casse, la frontière « chiffre ou souligné », et la portée sur le titre, la description, les messages de commit et le nom de branche ;
  - le « Plan du Scénario » ;
  - les règles du workflow (pas de `${{ github.event.* }}` dans un `run:`, droits, cache). La bibliothèque standard ne lit pas le YAML.
- **Raison :** suivre le point 23 à la lettre ne satisfait pas la l. 808, et une revue ne peut pas dire lequel des deux fait foi.
- **Correction :** compléter le point 23, dont un test texte sur `.github/workflows/*.yml`, et fixer le comportement de `garde` sans chemin protégé. Ou bien réduire l'annonce de la l. 808.

#### egm-style-1-3 : « plan détaillé, point 4 / point 6 » contredit la convention de renvoi du document. Sévérité : Major
- **Relecteurs :** style (M1).
- **Lignes :** 744-745, comparées à la l. 10.
- **Problème :** au point 29, ces renvois visent le plan détaillé du niveau 1. Or la l. 10 réserve « plan détaillé, point N » à ce document. Lus à la lettre, ils envoient vers `.env.example` (point 4) et `pyproject.toml` (point 6).
- **Raison :** l'exécutant risque de modifier la mauvaise section d'un document protégé.
- **Correction :** écrire « niveau 1, plan détaillé, point 4 (`docs/termes-interdits.md`) » et « niveau 1, plan détaillé, point 6 (`CLAUDE.md`) ».

### E. Nits

#### egm-style-1-4 : l'introduction annonce une marque qui n'est jamais employée. Sévérité : Nit
- **Lignes :** 559, 106.
- **Problème :** aucune étape n'est marquée **propriétaire**. « Terminal séparé » ne reprend pas « terminal hors de Claude Code ». « État stable » n'est pas défini, et le mot « état » a déjà un autre sens dans le glossaire.
- **Correction :** marquer les étapes concernées, ou retirer la phrase. Reprendre la formule de la l. 106. Décrire l'état attendu en tête de chaque phase.

#### egm-style-1-5 : les étapes n'ont pas toutes la même forme. Sévérité : Nit
- **Lignes :** 565-566, 718-721, 756-764, 768-781.
- **Problème :** certaines phases sont des listes numérotées, d'autres des titres `####`. Les points 26 et 31 ne sont pas des fichiers, mais portent « Proposed Changes ».
- **Correction :** des titres `####` pour les fichiers, une liste numérotée pour les actions, et l'intitulé « Action » pour les points 26 et 31.

#### egm-style-1-6 : la mention « chemin protégé » n'est pas systématique. Sévérité : Nit
- **Lignes :** 584, 631-715.
- **Problème :** elle manque aux points 5, 13 à 21, 24 et 25. Le point 22 mêle des fichiers protégés et `en_attente.txt`, qui ne l'est pas.
- **Correction :** l'ajouter partout où elle s'applique, et préciser fichier par fichier au point 22.

#### egm-style-1-7 : plusieurs renvois sont mal formés. Sévérité : Nit
- **Lignes :** 687, 688, 711, 745.
- **Problème :**
  - À la l. 711, l'ordre est inversé : `protection-main.json` est au point 17, `securite-depot.json` au point 18.
  - Le préfixe « plan détaillé » manque aux l. 711 et 745.
  - « Lance le plan détaillé, point 14 » se lit comme « lancer un plan ».
- **Correction :** « … `protection-main.json` (plan détaillé, point 17) et `securite-depot.json` (plan détaillé, point 18) » ; « lance `garde.py` (plan détaillé, point 14) ».

#### egm-style-1-8 : le texte du `README.md` diffère de celui de la spécification. Sévérité : Nit
- **Lignes :** 617, comparée à 411 et 175.
- **Problème :** il y a deux textes cités. « Peut être lu, mais pas réutilisé » est imprécis en droit : les conditions de GitHub permettent la copie par fork.
- **Correction :** un seul texte, au point 10, avec un renvoi à la l. 411. Par exemple : « Aucune licence n'accorde de droit de réutilisation ».

#### egm-style-1-9 : les termes du point 18 ne reprennent pas ceux du Technical Plan. Sévérité : Nit
- **Lignes :** 664-665.
- **Problème :** « la sécurité du dépôt » ne reprend pas « blocage des secrets ». « Il est lu au Technical Plan, point 4 » ne se dit pas : on ne lit pas un réglage dans un document.
- **Correction :** « l'analyse des secrets et le blocage des secrets au push » ; « lu à la vérification des réglages (plan détaillé, point 37) ».

#### egm-style-1-10 : le point 37 écrit « manque », la spécification « manque ou diffère ». Sévérité : Nit
- **Lignes :** 773, comparée à 264.
- **Correction :** « Si un réglage manque ou diffère ».

#### egm-style-1-11 : plusieurs formulations sont vagues ou se lisent de deux façons. Sévérité : Nit
- **Lignes :** 596, 638, 645, 703.
- **Problème :**
  - 596 : « règles de lint » ne dit pas lesquelles ;
  - 638 : « calcule l'étiquette », alors que l'étiquette est fixe ;
  - 645 : « compare » porte à la fois sur les deux versions et sur la liste des fichiers ;
  - 703 : « terme dans un mot non trouvé » se lit de deux façons.
- **Correction :**
  - 638 : « décide si l'étiquette … s'applique » ;
  - 645 : « reçoit deux versions … et la liste des fichiers modifiés » ;
  - 703 : « terme inclus dans un mot plus long : non trouvé ».

#### egm-style-1-12 : les conventions de langue et de nommage sont mal tenues. Sévérité : Nit
- **Lignes :** 580, 695, 705, 713, 799, 810.
- **Problème :**
  - La langue des commentaires de `.env.example` et de `en_attente.txt` n'est pas dite.
  - « Compilation/Build » et « Create, en dernier dans `.claude/` » mêlent les deux langues.
  - `test_en_attente.py` teste aussi `conftest.py`, ce que son nom ne dit pas.
  - La l. 810 rattache chaque objectif à un essai. Or la seconde moitié de l'objectif 9 se vérifie par une décision consignée, et non par un essai.
- **Correction :** fixer la langue des deux commentaires. Créer un fichier de test à part pour `conftest.py`. Écrire à la l. 810 « à un essai réussi ou à une décision consignée ».

#### egm-implementation-readiness-1-14 : `.claude/settings.local.json` n'est pas ignoré, et la version du modèle de `.gitignore` n'est pas fixée. Sévérité : Nit
- **Relecteurs :** implementation-readiness (N2), codebase-details (N4).
- **Lignes :** 572-575.
- **Problème :** Claude Code écrit des autorisations locales dans `.claude/settings.local.json`, et `git add -A` les publierait. Le modèle Python de GitHub n'est fixé ni par une URL ni par un commit.
- **Correction :** ajouter `.claude/settings.local.json` au `.gitignore`, et citer l'URL et le commit du modèle.

#### egm-implementation-readiness-1-15 : la commande d'essai du point 26 n'est ni fixée ni sans danger dans tous les cas. Sévérité : Nit
- **Relecteurs :** implementation-readiness (N3), codebase-details (N6).
- **Lignes :** 718-721.
- **Problème :** « par exemple » laisse le choix à l'exécutant. Avant `git init`, le refus peut venir de la règle « hook pre-commit absent », et non de `-n`. Si l'ordre change, un hook inactif laisse passer un commit vide, qui deviendrait le premier commit.
- **Correction :** fixer la commande et le message de refus attendu. Choisir une commande sans effet dans tous les cas.

#### egm-implementation-readiness-1-16 : des chemins protégés manquent dans `CLAUDE.md`, dans le niveau 1 et dans le tableau des écarts. Sévérité : Nit
- **Relecteurs :** implementation-readiness (N8), codebase-details (N9).
- **Lignes :** 335-355, 742, 747-754 ; tableau des écarts, l. 34-40.
- **Problème :** `tests/outillage/**`, `.gitleaks.toml`, `.pre-commit-config.yaml` et `.python-version` sont protégés ici. Ils n'apparaissent ni dans le niveau 1, ni dans `CLAUDE.md`, ni comme écart. Le point 30 n'ajoute que `docs/revues/`.
- **Correction :** les ajouter, ou faire renvoyer `CLAUDE.md` et le niveau 1 à `.github/chemins-proteges.txt`. Les mentionner dans le tableau des écarts.

#### egm-implementation-readiness-1-17 : les commandes et les textes des étiquettes et des jalons ne sont pas donnés. Sévérité : Nit
- **Relecteurs :** implementation-readiness (N9), codebase-details (N7).
- **Lignes :** 772, 775-777.
- **Problème :** `gh label create` n'entre pas dans la liste blanche du hook (l. 305-310). Le titre et la description des jalons ne sont pas fixés, ce qui rend l'essai E10 difficile à vérifier.
- **Correction :** `gh api -X POST repos/EZPK/4X/labels -f name=… -f color=…`. Donner le titre (`M0`…) et la description exacte des jalons.

#### egm-implementation-readiness-1-18 : le hook refusera les textes qui citent les essais. Sévérité : Nit
- **Relecteurs :** implementation-readiness (N10).
- **Lignes :** 781-795 ; spécification l. 304.
- **Problème :** le hook cherche les motifs dans toute la chaîne de commande. Une description ou un message de commit qui cite « `gh pr merge` » ou « `--no-verify` » fait donc refuser `gh pr create --body …` ou `git commit -m …`.
- **Correction :** imposer `--body-file` et `git commit -F` pour ces textes.

#### egm-implementation-readiness-1-19 : la forme de `required_status_checks` n'est pas fixée. Sévérité : Nit
- **Relecteurs :** implementation-readiness (N11), codebase-details (N2).
- **Lignes :** 652-660, 672-688.
- **Problème :** le plan ne choisit pas entre `contexts` et `checks` (avec `app_id`). Le nom du contrôle n'est l'identifiant de la tâche que si la tâche n'a ni `name:` ni matrice.
- **Correction :** fixer la forme au point 17. Interdire `name:` et les matrices sur les sept tâches, aux points 20 et 21.

#### egm-codebase-details-1-9 : `gh pr edit` dans Actions et description vide. Sévérité : Nit
- **Lignes :** 636-640, 687.
- **Problème :** `gh pr edit` a déjà échoué sous `GITHUB_TOKEN`, sur la lecture de `projectCards` (confiance basse pour la version actuelle de `gh`). Le cas `body: null` (description vide) n'est pas traité.
- **Correction :** passer par des appels REST (`POST …/issues/$N/labels`, `PATCH …/pulls/$N`), et traiter `body: null` dans `garde.py`.

#### egm-codebase-details-1-10 : la structure et la commande de `ruleset-main.json` ne sont pas données. Sévérité : Nit
- **Lignes :** 667-670.
- **Correction :** donner la structure :
  - `target`, `enforcement: active`, `bypass_actors: []`, `conditions.ref_name` ;
  - les règles `deletion`, `non_fast_forward`, `pull_request` (0 approbation) et `required_status_checks`.
  
  Donner aussi la commande : `gh api -X POST repos/EZPK/4X/rulesets --input .github/ruleset-main.json`.

#### egm-codebase-details-1-11 : à l'essai E5, `git push` échoue sur une branche neuve. Sévérité : Nit
- **Lignes :** 423, joué par le point 39.
- **Problème :** `! git push` échoue faute de branche suivie.
- **Correction :** `git push -u origin essai/faux-secret-github`.

#### egm-codebase-details-1-12 : l'emplacement du module qui appelle `scenarios()` n'est pas fixé. Sévérité : Nit
- **Lignes :** 690-696.
- **Problème :** placé hors des chemins protégés, ce module permettrait de retirer tous les scénarios sans aucun signal.
- **Correction :** le fixer et le protéger, ou dire explicitement que le choix revient à M1.
