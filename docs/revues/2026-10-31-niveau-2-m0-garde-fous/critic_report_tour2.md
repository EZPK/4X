# Rapport de revue critique (étape 7, tour 2)

**Cible :** /home/ezpk/Projects/4X/docs/designs/niveau-2-m0-garde-fous.md (lignes 1 à 556, avant « ## Detailed Implementation Plan » à la ligne 557)
**Date :** 2026-11-01
**Tour :** 2, la seule re-vérification autorisée
**Standard :** /home/ezpk/.claude/plugins/cache/egm/egm/0.1.0/resources/document_standards/feature-spec-standard.md (egm-design, egm-structural) ; persona seule (egm-style)
**Contexte fourni aux relecteurs :** /home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md, /home/ezpk/Projects/4X/CLAUDE.md, /home/ezpk/Projects/4X/docs/glossaire.md, /home/ezpk/Projects/4X/docs/termes-interdits.md, /home/ezpk/Projects/4X/docs/feuille-de-route.md
**Tour 1 :** /home/ezpk/Projects/4X/docs/revues/2026-10-31-niveau-2-m0-garde-fous/critic_report.md
**Résolution appliquée :** /home/ezpk/Projects/4X/docs/revues/2026-10-31-niveau-2-m0-garde-fous/goldfish_review_report.md

Les décisions du propriétaire inscrites dans le document n'ont pas été remises en cause. La section « Écarts au niveau 1 » annonce des reports dans le niveau 1 et dans `CLAUDE.md`. Ces fichiers ne sont volontairement pas encore à jour, et ce décalage n'est pas compté comme un défaut. Les deux constats écartés en partie au tour 1 (le séparateur de egm-structural-1-13, le mot « jouer » de egm-style-1-14) n'ont pas été rouverts.

## État des relecteurs

| Relecteur | État | Constats bruts (avant fusion) |
| --- | --- | --- |
| `egm-design` | completed | 8 Major, 4 Nit (12) |
| `egm-structural` | completed | 6 Major, 18 Nit (24) |
| `egm-style` | completed | 9 Major, 21 Nit (30), plus une remarque sans défaut |

Les trois relecteurs ont répondu au premier essai. Aucune relance n'a été nécessaire. Le filtre du système a signalé dans deux rapports un motif « settings-json ». C'est un faux positif : les rapports citent le fichier `.claude/settings.json` du document, sans aucune consigne adressée au synthétiseur.

## Méthode de fusion

- Quand plusieurs relecteurs signalent le même défaut, il n'y a qu'un constat. Son identifiant vient du relecteur dont la formulation sert de base, et les autres sont cités dans « Signalé aussi par ».
- La sévérité retenue est la plus haute parmi celles proposées.
- Un défaut qui n'est que le reste d'un constat du tour 1 partiellement résolu reste rattaché à ce constat, dans la partie 1. Il n'est pas compté comme nouveau.
- Le synthétiseur a relu dans la cible les citations des constats Major. Il a vérifié la règle de précédence du niveau 1 (/home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md, l. 670 et 754) pour egm-structural-2-4.

--------------------------------------------------------------------------------

## 1. Statut des constats du tour 1

**Bilan :** 51 constats. 37 résolus, 14 partiellement résolus, aucun non résolu.

### Constats egm-design-1-* (vérifiés par egm-design)

| Constat | Statut | Ce qui manque |
| --- | --- | --- |
| egm-design-1-1 (en attente) | partiellement résolu | Le cas du tour 1 est fermé (l. 375). Une pull request mixte reste possible : voir egm-design-2-4. |
| egm-design-1-2 (hook qui plante) | partiellement résolu | L'enveloppe `try/except` (l. 302) ne couvre pas trois cas qui donnent un code autre que 2 : `python3` absent (code 127), erreur de syntaxe à la lecture du fichier (code 1, avant le `try`), délai du hook dépassé pendant les lectures réseau des conditions d'amorçage. Il faut un délai interne plus court que celui de Claude Code, avec refus, une vérification de la version de `python3` en phase 0, et le délai dans les Open Questions (l. 102-106) et au risque de la l. 528. |
| egm-design-1-3 (variantes du hook) | partiellement résolu | Liste blanche et branche cible incomplètes : voir egm-design-2-2 et egm-design-2-3. |
| egm-design-1-4 (outils hors Bash) | partiellement résolu | Edit, Write et MCP sont traités (l. 297, 299). L'outil Bash peut toujours écrire dans `.claude/` : voir egm-design-2-1. |
| egm-design-1-5 (garde bloquant) | résolu | l. 262, 272, 432-438, 534 |
| egm-design-1-6 (signal du garde) | partiellement résolu | (a) Rien ne dit que `termes-interdits`, dans `ci.yml`, se relance sur `edited` (l. 360 ne vaut que pour `garde.yml`), alors que la résolution l'annonçait (signalé aussi par egm-structural, son N18). (b) `labeled` et `unlabeled` manquent aux déclencheurs. (c) L'étiquette reste retirable par la route `issues` (egm-design-2-2). (d) Une réécriture de la description peut être perdue (egm-design-2-8). |
| egm-design-1-7 (injection) | résolu | l. 363, 368, 515, 535 |
| egm-design-1-8 (contrôles neutralisés) | résolu | l. 52-53, 532 |
| egm-design-1-9 (ordre de l'amorçage) | résolu | l. 66-69, 226-229, 239, 328 |
| egm-design-1-10 (règles `gitleaks`) | partiellement résolu | La l. 71 promet la détection des « adresses réseau du projet » et des « valeurs des variables d'environnement du projet ». Les règles (l. 323-324) ne voient que les IPv4 privées et les variables `FOURX_`. Aucune règle n'impose ce préfixe, et la première variable annoncée (l. 321, adresse MLflow) s'appelle d'habitude `MLFLOW_TRACKING_URI`. Les noms d'hôte et la plage 100.64.0.0/10 ne sont pas couverts. Il faut poser la règle du préfixe, élargir les règles ou ramener la l. 71 à ce qui est détecté (signalé aussi par egm-style, son N6). |
| egm-design-1-11 (hook pre-commit d'un clone) | résolu | l. 312, 536. Le bit d'exécution n'est pas vérifié : voir egm-design-2-1. |
| egm-design-1-12 (termes auto-bloquants) | résolu | l. 386-388 |
| egm-design-1-13 (`pyproject.toml` protégé) | résolu | l. 181, 349-352, 506. La correction ouvre un nouveau trou : voir egm-design-2-5. |
| egm-design-1-14 (absent ou lecture en échec) | résolu | l. 235-237. Le cas de la 1re commande est traité en egm-style-2-2. |
| egm-design-1-15 (catégorie `references`) | résolu | l. 94 |
| egm-design-1-16 (titres des scénarios) | partiellement résolu | Les doublons sont traités (l. 400). Le plan de scénario (l. 401) ne l'est pas : si certains exemples passent, `strict` fait échouer la CI. Dire que la pull request de fonctionnalité doit faire passer tous les exemples d'un coup, ou permettre une entrée par exemple. |
| egm-design-1-17 (typage des scripts) | résolu | l. 180, 408, 410 |
| egm-design-1-18 (réglages et préalables) | partiellement résolu | Jeton des workflows, étiquettes et `--locked` traités (l. 178, 248, 260, 517). L'approbation des workflows lancés depuis un fork n'est ni tranchée ni écartée. |

### Constats egm-structural-1-* (vérifiés par egm-structural)

| Constat | Statut | Ce qui manque |
| --- | --- | --- |
| egm-structural-1-1 (3e exception, contenu du fichier) | résolu | l. 226-237, 64. Défaut de rédaction restant : egm-structural-2-5. |
| egm-structural-1-2 (qui applique la protection) | résolu | l. 226, 288 |
| egm-structural-1-3 (Goal 3 et essais) | partiellement résolu | E4 (l. 422) ne teste pas l'édition de `.git/hooks/`, que le Goal 3 annonce (l. 64-65). Voir aussi egm-structural-2-3. |
| egm-structural-1-4 (Goal 1 sans essai) | partiellement résolu | Le push direct est exercé (E2, l. 420). Les lectures du Goal 1 (l. 61 : `gh repo view … visibility`, `git log --first-parent origin/main`) et le contenu du commit initial (l. 60) ne sont dans aucun essai, alors que la résolution annonçait un « essai de lecture ». « Commence par le commit initial » est faux à la lettre : `git log` affiche le plus récent en premier. |
| egm-structural-1-5 (`!` non défini) | résolu | l. 12, 106, 420-423 |
| egm-structural-1-6 (solutions de rechange) | résolu | l. 265-270, 476, 526 |
| egm-structural-1-7 (écarts au niveau 1) | résolu sur la forme | l. 30-40, 470. La justification par la date est fausse : voir egm-structural-2-4. |
| egm-structural-1-8 (renvois « point N ») | résolu | l. 9-10 ; tous les renvois des l. 1-556 pointent au bon endroit |
| egm-structural-1-9 (raisons manquantes) | résolu | l. 179, 182-184 |
| egm-structural-1-10 (Goal 8 double) | partiellement résolu | E10 (l. 428) vérifie que les jalons M0 à M6 existent, pas qu'ils « renvoient à `docs/feuille-de-route.md` » (l. 82). |
| egm-structural-1-11 (Open Questions, puces) | partiellement résolu | Les Open Questions sont propres (l. 101-106). Les puces de premier niveau restent mélangées : `-` aux l. 19-26, 53-54, 258, 318 ; `*   ` aux l. 86, 101, 114, 512. Écrire une règle, ou n'en garder qu'un. |
| egm-structural-1-12 (sections du gabarit) | résolu | l. 541-553. Un lien est discutable : egm-structural-2-15. |
| egm-structural-1-13 (mise en forme) | résolu pour la partie acceptée | l. 8, 241 ; le séparateur, écarté, n'est pas rouvert |
| egm-structural-1-14 (CUJ 3 du niveau 1) | résolu | l. 110 |
| egm-structural-1-15 (type des pull requests d'essai) | résolu | l. 415-428 |
| egm-structural-1-16 (risques manquants) | résolu | l. 175, 538, 539 |

### Constats egm-style-1-* (vérifiés par egm-style)

| Constat | Statut | Ce qui manque |
| --- | --- | --- |
| egm-style-1-1 (faux secret) | résolu | l. 66-72, 135-151, 423-424. Une imprécision nouvelle : egm-structural-2-8. |
| egm-style-1-2 (« avant tout le reste ») | résolu | l. 101, 249, 255, 257 |
| egm-style-1-3 (tâches requises) | résolu | l. 40, 77, 276-280 |
| egm-style-1-4 (« obligatoire » et « requis ») | partiellement résolu | « Contrôle requis » a disparu, mais « contrôle exigé » le remplace aux l. 216, 258, 262, 272, 421, 434 et 534, à côté de « contrôle obligatoire » (l. 77, 276, 283). Écrire « contrôle obligatoire » partout. |
| egm-style-1-5 (compte rendu de M0) | partiellement résolu | Les mentions des l. 39, 97, 177, 257 et 415 ne disent ni ce qu'est le compte rendu, ni où il est, ni qui le rédige. La définition n'est qu'aux l. 785-787, dans le plan détaillé. La donner à la première mention de la spécification. |
| egm-style-1-6 (réussite du garde) | résolu | l. 373 |
| egm-style-1-7 (alternative B) | résolu | l. 452. Reste une affirmation sans source à la l. 451 : egm-style-2-9. |
| egm-style-1-8 (exception qui se rouvre) | résolu | l. 531. Un décalage avec la l. 553 : egm-structural-2-11. |
| egm-style-1-9 à egm-style-1-13 | résolus | l. 48, 114, « pull request d'essai » partout, l. 186, 177, 326, 185, 493-494 |
| egm-style-1-14 (tournures familières) | résolu pour la partie acceptée | l. 206, 251, 421 ; « jouer », écarté, n'est pas rouvert |
| egm-style-1-15 (« à juste titre ») | résolu | l. 253. Le décompte est faux : egm-style-2-1. |
| egm-style-1-16 (formats des listes) | résolu | l. 379, 380, 397-402 |
| egm-style-1-17 (points divers) | résolu | l. 82, 95, 446-506, 520 |

--------------------------------------------------------------------------------

## 2. Nouveaux constats

### Bilan après fusion

| Sévérité | Nombre |
| --- | --- |
| Blocker | 0 |
| Major | 15 |
| Nit | 23 |
| **Total** | **38** |

Aucun nouveau Blocker. Quinze nouveaux Major.

## Major

### egm-structural-2-1 : `garde` et `en-attente` ne peuvent pas être verts sur `main`

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style` (Major)
- **Lignes :** 77, 419, comparées à 360
- **Problème :** le Goal 7 exige que les sept contrôles obligatoires soient « tous présents et verts sur `main` », `garde` et `en-attente` compris. L'essai E1 attend : « tous les contrôles obligatoires sont verts sur le commit initial ». Or `garde.yml` ne se déclenche que sur `pull_request_target` (l. 360). Ces deux tâches ne tournent donc jamais sur un commit de `main`.
- **Raison :** un objectif du critère de sortie et son essai ne peuvent pas être atteints tels qu'ils sont écrits.
- **Correction proposée :** l. 77 et 419 : « les tâches de `ci.yml` sont vertes sur `main` ; `garde` et `en-attente` sont vertes sur la première pull request d'essai » (cette vérification existe déjà à la l. 262). Ou bien ajouter à `garde.yml` un déclencheur sur `main` et le dire à la l. 360.

### egm-structural-2-2 : la règle `gitleaks` des IPv4 privées détecte ce document, et l'attendu « aucune fuite » ne peut pas tenir

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style` (Major)
- **Lignes :** 323, comparée à 239, 513 et 419
- **Problème :** la l. 323 écrit en clair « 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 », dans un fichier du commit initial. La l. 239 attend pourtant « aucune fuite » de `gitleaks git` sur ce commit, et la l. 513 et l'essai E1 supposent une tâche `gitleaks` verte. Aucune exclusion n'est prévue pour `gitleaks`, alors que le contrôle des termes interdits en a une (l. 386). La même question se pose pour la règle `FOURX_` face aux documents qui la décrivent, et pour `.gitleaks.toml` lui-même.
- **Raison :** l'amorçage s'arrêterait à l'étape de la l. 239, avant le push initial.
- **Correction proposée :** décrire les plages sans adresse littérale (« les plages privées de la RFC 1918 »), ou prévoir une liste d'exclusion dans `.gitleaks.toml` (ce document, `.gitleaks.toml`, les tests des règles) et la nommer au Technical Plan, point 7, comme la l. 386 le fait pour les termes.

### egm-design-2-6 : `fnmatch` ne connaît pas `**`, et les scénarios à la racine de `tests/scenarios/` ne seraient pas protégés

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural` (Major) et `egm-style` (Major)
- **Lignes :** 332, 345, 393
- **Problème :** « Les motifs suivent la syntaxe de `fnmatch` de Python, où `**` désigne n'importe quel nombre de dossiers ». `fnmatch` ne donne aucun sens particulier à `**`, et son `*` traverse déjà les `/`. Avec `fnmatch`, `tests/scenarios/**/*.feature` exige un `/` de plus après `tests/scenarios/` : `tests/scenarios/exemple.feature` ne correspond pas. Or la l. 393 place justement les scénarios dans `tests/scenarios/*.feature`.
- **Raison :** le chemin protégé le plus important à partir de M1 serait ouvert sans aucun signal, et le Goal 5 manqué pour les scénarios. Deux sections disent deux choses différentes sur un même chemin.
- **Correction proposée :** nommer une fonction qui reconnaît `**` (par exemple `PurePosixPath.full_match`, où `**` compte aussi zéro dossier), ou ajouter le motif `tests/scenarios/*.feature`. Aligner les l. 345 et 393. Ajouter les tests `tests/scenarios/a.feature` et `tests/scenarios/x/a.feature`.

### egm-design-2-1 : l'outil Bash peut réécrire `.claude/` et `.git/hooks/`

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 64, 297, 312, 530
- **Problème :** le Goal 3 promet le refus de l'« édition de `.claude/` et de `.git/hooks/` ». Le seul mécanisme prévu est la règle `deny` sur Edit et Write (l. 297). Des commandes Bash directes passent : `sed -i`, `cat >`, `cp`, `git checkout <branche> -- .claude/`, `git restore`, `git stash pop`, `git apply`, `chmod -x .git/hooks/pre-commit`. Ce dernier cas échappe aussi à la vérification de la l. 312, qui regarde si le fichier existe et appelle `pre-commit`, pas s'il est exécutable. Ce sont des commandes directes, pas des scripts : elles ne relèvent pas du risque accepté (l. 54).
- **Raison :** le hook lit ses propres fichiers sur le disque. Les réécrire par Bash désactive tous les garde-fous côté Claude Code. La parade de la l. 530 ne couvre que deux outils.
- **Correction proposée :** le hook refuse toute commande Bash qui cite `.claude/` ou `.git/hooks`, sauf les lectures (`cat`, `ls`, `git diff`, `git log`, `git show`). La vérification de la l. 312 inclut le bit d'exécution. Le cas restant (passer sur une branche qui modifie `.claude/` active la version de cette branche) va au tableau des risques.

### egm-design-2-2 : la liste blanche des écritures GitHub laisse retirer l'étiquette du garde, ne dit rien des autres commandes `gh`, et bloque les gestes des essais

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural` (Major) et `egm-style` (Major)
- **Lignes :** 294, 305-310, 360, 371, 415, 425
- **Problème :**
  - La route `issues` est autorisée en écriture (l. 307). Or `DELETE …/issues/<n>/labels/<nom>`, `PUT …/issues/<n>/labels` et `PATCH …/issues/<n>` avec `labels` retirent l'étiquette d'une pull request, ce qui contourne la l. 310. La route `labels` permet aussi `DELETE` et `PATCH` sur `labels/<nom>`. Le garde ne se relance pas sur `unlabeled` (l. 360).
  - La règle de correspondance des routes n'est pas donnée (préfixe ou route exacte). Si « `pulls` (création) » est un préfixe, `PUT …/pulls/<n>/merge`, qui fusionne, passe. Les routes de « commentaires », les URL absolues, les `..` et les gabarits `{owner}` ne sont pas traités.
  - La politique ne couvre que `gh api` et `gh repo`. Rien n'est dit de `gh pr create`, `gh pr close`, `gh pr edit --body` (utilisé par E7, l. 425), `gh label create` ou `gh label delete`, `gh issue edit --remove-label`, `gh workflow disable`, `gh secret set`, `gh variable set`. Selon la l. 302, une commande `gh` que le hook ne sait pas analyser est refusée : soit les essais sont bloqués, soit des écritures non listées passent.
  - La l. 415 demande de supprimer la branche de chaque essai, sans dire qui le fait. `git push --delete` est refusé par les règles `deny` (l. 294), et `DELETE …/git/refs` n'est pas une route autorisée.
- **Raison :** le Goal 5 et le niveau 1 (§10) font de l'étiquette le signal principal du propriétaire. Une liste blanche dont les entrées permettent l'action interdite n'en est pas une, et le texte demande à l'agent une action que ses propres règles lui interdisent.
- **Correction proposée :** donner les routes autorisées par méthode et par chemin exact (`POST issues`, `POST issues/<n>/comments`, `POST pulls`, `POST labels`, `POST` et `PATCH` sur `milestones`) ; refuser toute écriture sur `issues/<n>/labels`, les `PATCH issues/<n>` qui contiennent `labels`, et `DELETE` ou `PATCH` sur `labels/*`. Lister les sous-commandes `gh` autorisées (par exemple `pr create`, `pr view`, `pr checks`, `pr close`, `pr edit` sans retrait d'une étiquette du garde, `issue create`, `issue comment`, `run view`) et refuser les autres. Ajouter `labeled` et `unlabeled` aux déclencheurs de `garde.yml`. À la l. 415, dire qui supprime les branches et par quelle commande (le propriétaire avec `!`, ou `gh pr close --delete-branch` si elle est autorisée).

### egm-design-2-3 : la branche cible de `git push` est lue avant l'exécution, pas pendant

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 304, 311, 312
- **Problème :** « le hook détermine la branche cible réelle (refspec, sinon branche suivie) » (l. 311). Il lit l'état au moment où le hook tourne. Or la l. 304 accepte les enchaînements : `git switch main && git push` est évalué depuis la branche d'essai, donc autorisé. D'autres formes ne sont pas citées : `git push origin HEAD`, `@`, `+x:main`, une URL à la place de `origin`, `push.default=matching`, `remote.pushDefault`. Les options courtes combinées (`git commit -an`, `-nm "…"`) échappent à la recherche de `git commit -n` (l. 312).
- **Raison :** en temps normal, GitHub refuse un push sur `main` (voir toutefois egm-design-2-7). Dans le cas du « critère réduit » (l. 268), le hook est la seule barrière. La l. 311 annonce une détermination qu'une analyse sans exécution ne peut pas garantir.
- **Correction proposée :** liste blanche pour `git push` : seulement `git push [-u] origin <nom>` ou `<nom>:<nom>`, avec `<nom>` différent de `main`, sans enchaînement dans la même commande ; tout le reste est refusé, `git push` sans argument compris. Pour `git commit`, refuser tout groupe d'options courtes qui contient `n`. Ajouter ces cas aux tests.

### egm-design-2-4 : le Goal 6 se contourne par une pull request mixte

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-style` (Nit)
- **Lignes :** 24, 75-76, 375, 402, 533
- **Problème :** la tâche `en-attente` accepte un ajout dès qu'un `.feature` quelconque est modifié (l. 375). Une pull request qui contient le code qui casse le scénario X, une retouche sans portée d'un `.feature` et l'ajout de X à `en_attente.txt` passe au vert. Seule l'étiquette « fichiers protégés modifiés » apparaît, et elle est normale pour toute pull request de scénarios. Rien n'impose la séparation des types de pull request du niveau 1. Le Goal 6 dit pourtant « ne peut pas », et la l. 24 parle d'un refus « hors d'une pull request de scénarios », ce qui n'est pas le mécanisme décrit.
- **Raison :** c'est le contournement que le niveau 1 (§10) demande d'interdire : « on ne puisse pas utiliser la marque pour cacher une régression ».
- **Correction proposée :** l'une ou l'autre de ces règles, ou les deux : une entrée ajoutée doit désigner un scénario nouveau ou modifié dans les `.feature` de la pull request (comparaison avec `main`) ; la tâche échoue si une pull request modifie à la fois un `.feature` et un fichier de `src/`. À défaut, affaiblir le Goal 6 et la l. 24, et inscrire le cas au tableau des risques.

### egm-design-2-5 : la configuration chargée par dossier échappe aux chemins protégés

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 181, 334-356, 506
- **Problème :** séparer la configuration de `pyproject.toml` (correction de egm-design-1-13) suppose que les outils ne lisent que les fichiers protégés. Ce n'est pas le cas :
  - `ruff` préfère `.ruff.toml` à `ruff.toml` dans le même dossier, et applique la configuration la plus proche de chaque fichier source. Une pull request de fonctionnalité qui ajoute `.ruff.toml` à la racine, ou `src/fourx/core/ruff.toml`, remplace la configuration protégée sans toucher un chemin protégé ;
  - `pytest` charge tout `conftest.py` de la racine ou de `tests/`, et seul `tests/scenarios/conftest.py` est protégé. Un `tests/conftest.py` peut marquer tous les échecs comme attendus ;
  - `pyproject.toml` n'est pas protégé, et une dépendance ajoutée peut charger d'elle-même un greffon `pytest` (entry points) qui agit de la même façon.
- **Raison :** le niveau 1 protège « la configuration des tests, du linter, du typage ». Ces voies la contournent sans aucun signal.
- **Correction proposée :** en CI, passer la configuration explicitement : `ruff --config ruff.toml`, `mypy --config-file mypy.ini`, `pytest -c pytest.ini` avec `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` et `-p pytest_bdd`. Ajouter `**/conftest.py`, `**/.ruff.toml` et `**/ruff.toml` aux chemins protégés. Inscrire au tableau des risques les désactivations écrites dans le code (`# noqa`, `# type: ignore`, `# mypy: ignore-errors`).

### egm-design-2-7 : « pull request obligatoire » n'est pas garanti par la protection décrite

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 61, 216, 258, 282-286, 420
- **Problème :** le schéma (l. 216) et le niveau 1 (§10) annoncent « pull request obligatoire ». La liste des l. 282-286 ne le reprend pas, et dit « aucune approbation requise ». Dans la protection classique de GitHub, l'exigence d'une pull request passe par le champ `required_pull_request_reviews`. La lecture naturelle de « aucune approbation » est de le mettre à `null`, ce qui retire l'exigence : il ne reste que les contrôles obligatoires. Un commit déjà vert, comme la tête d'une pull request à jour, pourrait alors être poussé directement sur `main`. L'essai E2 pousse un commit qui n'a passé aucun contrôle : il serait refusé pour une autre raison, et le Goal 1 paraîtrait démontré à tort. Le Technical Plan, point 4 (l. 258) ne relit pas ce champ.
- **Raison :** une garantie du schéma et du niveau 1 n'est pas dans la liste qui fait foi pour l'exécutant, et l'essai qui devrait la prouver ne peut pas distinguer les deux causes de refus.
- **Correction proposée :** écrire que la pull request est exigée par `required_pull_request_reviews` avec `required_approving_review_count: 0`. Relire ce champ au point 4. À l'essai E2, pousser aussi la tête verte d'une pull request d'essai, et attendre le refus.

### egm-design-2-8 : deux exécutions du garde peuvent effacer une description plus récente

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 363, 368-371
- **Problème :** les scripts lisent la description dans `$GITHUB_EVENT_PATH`, c'est-à-dire telle qu'elle était au moment de l'événement. Aucun groupe `concurrency` n'est prévu. Enchaînement courant : l'agent pousse un commit (`synchronize`), puis écrit le résumé EGM (`edited`). Si l'exécution liée au push finit en dernier, elle réécrit l'ancienne description avec le bloc en tête, et le résumé EGM disparaît ou revient à une version périmée.
- **Raison :** le résumé EGM est ce que lit le propriétaire avant de fusionner une pull request protégée.
- **Correction proposée :** `concurrency: garde-<numéro de la pull request>` avec `cancel-in-progress: true`, et relecture de la description par l'API juste avant de l'écrire.

### egm-structural-2-3 : le Goal 3 confie les variantes aux tests du hook, alors que plusieurs catégories ne dépendent que des règles `deny`

- **Sévérité :** Major
- **Lentille :** `egm-structural`
- **Lignes :** 65, 292-297, 302-314, 422
- **Problème :** l. 65 : « Les variantes de chaque catégorie sont couvertes par les tests du hook ». Or `gh pr merge`, `--force-with-lease`, `--mirror`, `--all`, `--delete`, `--no-verify`, `gh repo archive`, `rename` et `delete`, et l'édition de `.claude/**` et `.git/hooks/**` ne figurent que dans les règles `deny` (l. 292-297). Les règles du hook (l. 302-312) ne les reprennent pas. « Les motifs interdits » de la l. 304 ne sont pas définis. Un test du hook ne peut pas vérifier une règle `deny`, dont la syntaxe est encore une question ouverte (l. 103). E4 ne teste qu'une variante par catégorie.
- **Raison :** la vérification annoncée par le Goal 3 ne correspond à aucun mécanisme pour ces variantes.
- **Correction proposée :** dire au Technical Plan, point 6 que le hook reprend toute la liste des règles `deny` qui portent sur Bash, et la tester. Ou bien ajouter à E4 une tentative par variante couverte seulement par une règle `deny`, `.git/hooks/` compris. Corriger la l. 65 en conséquence.

### egm-structural-2-4 : la dispense d'ADR repose sur une date que le document contredit

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style` (Major)
- **Lignes :** 32, comparée à 5
- **Problème :** l. 32 : « Tous ont été décidés par le propriétaire le 2026-10-31 […]. Ils relèvent donc de la règle du niveau 1 selon laquelle les décisions du 2026-10-31 restent dans le niveau 1, sans ADR ». Or la l. 5 date la révision du 2026-11-01. Le rapport de résolution présente E4 (`docs/revues/` protégé) comme « un écart de plus », contenu dans les corrections de la revue. La tâche `en-attente` de E5 vient aussi d'une correction (egm-design-1-1). La règle de précédence du niveau 1 (/home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md, l. 670 et 754) ne dispense d'ADR que les décisions du 2026-10-31. Une ADR enregistre toute décision prise après cette date qui change un choix du niveau 1.
- **Raison :** l'affirmation est factuellement inexacte et porte un raisonnement. Une session neuve qui compare la l. 5 et la l. 32 peut conclure qu'une ADR est requise pour E4 et E5. Le choix lui-même n'est pas en cause, seulement sa justification.
- **Correction proposée :** dater correctement : E1 à E3 décidés le 2026-10-31, E4 et E5 acceptés le 2026-11-01 pendant la revue EGM. Puis citer la base qui dispense d'ADR (à faire confirmer par le propriétaire), ou prévoir l'ADR. Autre possibilité : le propriétaire confirme que ces décisions datent bien du 2026-10-31.

### egm-style-2-1 : le nombre d'essais confiés au propriétaire est faux

- **Sévérité :** Major
- **Lentille :** `egm-style` ; signalé aussi par `egm-structural` (Nit)
- **Lignes :** 251, 253, comparées à 420-424
- **Problème :** « le propriétaire pour trois d'entre eux » et « Trois essais reviennent au propriétaire : la fusion en administrateur, le commit sans hook pre-commit et le push direct sur `main` ». Le tableau du Technical Plan, point 12 en confie quatre au propriétaire : E2, E3, E5 et E6. Le commit sans hook revient dans E5 et dans E6.
- **Raison :** un exécutant qui se fie au point 3 oubliera un essai.
- **Correction proposée :** « Quatre essais (E2, E3, E5, E6) reviennent au propriétaire. Ils portent sur trois commandes que les règles de l'agent de code lui interdisent : … ». Corriger aussi la l. 251.

### egm-style-2-2 : la condition de la commande `PATCH` contredit le résultat annoncé

- **Sévérité :** Major
- **Lentille :** `egm-style` ; signalé aussi par `egm-structural` (Nit) et `egm-design` (Nit)
- **Lignes :** 235, 247, 271, 513
- **Problème :** la condition est que `secret_scanning_push_protection.status` « n'est pas `enabled`, la lecture ayant réussi ». La colonne de droite dit pourtant : « Si GitHub ne propose pas cette fonction, la lecture le montre, et le hook refuse aussi ». Si la fonction n'existe pas, le statut est absent ou différent de `enabled` : la condition reste vraie, et l'exception ne se referme jamais. Le document ne dit pas non plus si un refus « déjà actif » (possible par défaut sur un dépôt public récent) permet de continuer vers le push, ni si un refus « indisponible » arrête l'agent. La l. 513 affirme sans condition que le blocage « est déjà actif », alors que la l. 271 prévoit son absence.
- **Raison :** contradiction sur la fermeture d'une exception d'amorçage, mécanisme central du Technical Plan, point 3.
- **Correction proposée :** autoriser seulement si le statut vaut `disabled` ; un statut absent ou toute autre valeur donne un refus. Dire qu'un refus pour « déjà actif » est un succès et que l'agent continue, et qu'un refus pour « indisponible » l'arrête jusqu'à la décision du propriétaire. Ajouter « s'il est disponible » à la l. 513.

### egm-style-2-3 : « contrôle de garde » et « le garde » ont plusieurs sens, dont un contraire au glossaire

- **Sévérité :** Major
- **Lentille :** `egm-style` ; signalé aussi par `egm-structural` (deux Nit)
- **Lignes :** 24, 40, 53, 94, 248, 310, 366-375, 534
- **Problème :**
  - La l. 24 dit que le contrôle de garde « refuse qu'on ajoute un scénario « en attente » ». Le glossaire le définit comme un contrôle qui signale, et le document confie ce refus à une tâche distincte, `en-attente` (l. 40, 358, 375).
  - « Le garde », au masculin et non défini, désigne tantôt la tâche `garde` (l. 371), tantôt la version de `garde.yml` sur `main` (l. 534).
  - « Les étiquettes du garde » (l. 248, 310) est au pluriel et n'est jamais nommé, alors que M0 n'en définit qu'une, « fichiers protégés modifiés », et que la catégorie des références est reportée à M1 (l. 94).
- **Raison :** le même terme sert pour un contrôle qui signale et pour un contrôle qui bloque, alors que le glossaire fait référence. L'objet des règles des l. 248 et 310 reste flou.
- **Correction proposée :** l. 24 en deux puces : « le contrôle de garde (tâche `garde`), qui signale toute modification d'un chemin protégé » et « la tâche `en-attente`, qui refuse… ». Remplacer « le garde » par « la tâche `garde` » ou « `garde.yml` » selon le cas. Nommer l'étiquette, au singulier, aux l. 248 et 310.

## Nits

### egm-design-2-9 : aucune procédure pour faire évoluer les contrôles obligatoires

- **Lentille :** `egm-design`
- **Lignes :** 280, 288, 434-438, 531
- **Problème :** à M1, `tests-outillage` devient `tests` (l. 280). Si la pull request renomme la tâche avant que la protection change, plus rien ne fusionne. L'agent ne peut pas réappliquer la protection (exception fermée, copie de référence figée). Il ne reste que la procédure de reprise, prévue pour les incidents.
- **Correction proposée :** écrire la procédure courante : ajouter la nouvelle tâche sans retirer l'ancienne ; le propriétaire applique la nouvelle protection avec `!` après la fusion ; puis retirer l'ancienne tâche. Préciser que la copie de référence du hook ne sert qu'à l'amorçage.

### egm-design-2-10 : la levée temporaire de la règle `deny` peut être commitée par erreur

- **Lentille :** `egm-design`
- **Lignes :** 297
- **Problème :** modifier `.claude/` demande d'éditer `.claude/settings.json`, qui est suivi par git. Une version où la règle est levée peut être commitée, et rien ne le détecte : l'étiquette est normale pour ce type de pull request.
- **Correction proposée :** un test de `tests-outillage` vérifie que `settings.json` contient les règles `deny` attendues et la déclaration du hook.

### egm-design-2-11 : le compte rendu pourrait recopier les faux secrets

- **Lentille :** `egm-design`
- **Lignes :** 415, 423-424, 430
- **Problème :** le compte rendu cite la sortie de chaque essai, et `gitleaks` affiche le secret trouvé sauf avec `--redact`. Recopier ces sorties mettrait le faux `ghp_…` dans le compte rendu, dont la pull request serait alors refusée par les trois barrières.
- **Correction proposée :** lancer `gitleaks` avec `--redact` partout, et interdire de recopier les faux secrets dans le compte rendu.

### egm-structural-2-5 : « le fichier envoyé » ne vaut que pour deux commandes d'amorçage sur trois

- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 231, 236
- **Correction proposée :** « …et, pour les deux commandes `gh api`, si le fichier envoyé est identique à la copie de référence… ».

### egm-structural-2-6 : `gh repo create` est une quatrième exception conditionnelle, sans condition décrite ni test

- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 121, 246, 309, 314, 422, 470
- **Problème :** au CUJ 1, « une seconde tentative de chacune de ces commandes » couvre quatre commandes, création du dépôt comprise. Le Goal 3, E4, les tests et l'alternative E (« trois exceptions d'amorçage ») n'en couvrent que trois. `gh repo create` n'est autorisé que « tant que le dépôt n'existe pas » (l. 246, 309), mais le tableau du Technical Plan, point 3 ne dit pas comment l'existence du dépôt est lue, ni ce qui se passe si la lecture échoue.
- **Correction proposée :** ajouter `gh repo create` au tableau du point 3, aux tests et à E4, ou restreindre la formulation du CUJ 1. Aligner la l. 470.

### egm-structural-2-7 : le message de refus attendu n'est pas le même au CUJ 2 et à l'essai E3

- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 127, 421
- **Problème :** le CUJ 2 attend un message « qui cite la protection de branche », E3 un message « qui cite les contrôles exigés ».
- **Correction proposée :** choisir un seul attendu.

### egm-structural-2-8 : où restent les faux secrets, et qui ouvre les pull requests de E5 et E6

- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 145, 149, 151, 423-424, 430
- **Problème :** la l. 151 dit que les faux secrets « restent lisibles dans la pull request fermée ». Le jeton `ghp_` n'arrive jamais dans une pull request : il est refusé au push, ou poussé sans pull request si le blocage n'est pas démontré, et le nettoyage de sa branche n'est alors pas prévu. Personne n'ouvre la pull request de E6. Le CUJ 4 parle d'« une branche `essai/…` », alors que E5 et E6 en utilisent deux.
- **Correction proposée :** l. 151 : « La valeur d'essai n'est fusionnée dans aucune branche, mais reste lisible dans la pull request fermée », aligné sur la l. 430. Dire qui ouvre la pull request de E6, et que faire de la branche de E5 si son push passe.

### egm-structural-2-9 : la ligne E2 du tableau des écarts omet les règles `deny` Edit et Write

- **Lentille :** `egm-structural`
- **Lignes :** 37, comparée à 297
- **Correction proposée :** citer dans la ligne E2 (ou dans une ligne à part) les règles `deny` sur `.claude/**` et `.git/hooks/**`, puisque le plan les reporte sous cet écart.

### egm-structural-2-10 : les règles `gitleaks` propres au projet n'ont ni test ni essai

- **Lentille :** `egm-structural`
- **Lignes :** 71-72, 322-325
- **Problème :** la vérification du Goal 4 se limite aux essais E5 et E6, qui n'exercent que `ghp_` et `FOURX_ESSAI_SECRET_`. Aucun test de `tests/outillage/` ne porte sur les règles IPv4 et `FOURX_` de `.gitleaks.toml`.
- **Correction proposée :** un test par règle propre au projet, ou retirer cette promesse du Goal (voir aussi le reste de egm-design-1-10).

### egm-structural-2-11 : on ne sait pas si le contrôle de nuit de la protection est décidé

- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 531, 553
- **Problème :** le tableau des risques présente comme acquis « à partir de M1, un contrôle après fusion relit la protection chaque nuit ». Les Future Improvements en font une amélioration possible, et le tableau des contrôles après fusion du niveau 1 (§10) ne le contient pas.
- **Correction proposée :** écrire la même chose aux deux endroits, par exemple « proposé pour M1, à décider au niveau 2 de M1 ».

### egm-structural-2-12 : rien n'est prévu si le réglage du jeton des workflows diffère

- **Lentille :** `egm-structural`
- **Lignes :** 260, 264-272
- **Correction proposée :** ajouter à la liste « Si un réglage manque ou diffère » le cas du jeton des workflows et de l'approbation par les Actions, par exemple « le propriétaire le corrige par l'interface ».

### egm-structural-2-13 : le risque d'injection de consignes par le contenu du dépôt public n'est pas repris

- **Lentille :** `egm-structural`
- **Lignes :** 522-539
- **Problème :** le niveau 1 (Risks & Mitigations) rattache à M0 le risque « Injection de consignes dans l'agent de code par du contenu du dépôt public ». Ce document rend le dépôt public sans reprendre ce risque ni y renvoyer.
- **Correction proposée :** ajouter une ligne, ou un renvoi au niveau 1.

### egm-structural-2-14 : les outils des invariants de déterminisme ne sont ni choisis ni reportés

- **Lentille :** `egm-structural`
- **Lignes :** 26, 84-97
- **Problème :** le niveau 1 (§2, « Invariants de déterminisme ») dit que « les outils exacts sont choisis dans les documents de niveau 2 de M0 et M1 ». La liste des choix renvoyés à M0 (l. 26) et les Non-Goals n'en parlent pas.
- **Correction proposée :** dire qu'ils sont reportés à M1, ou en choisir une partie ici.

### egm-structural-2-15 : le lien sur le blocage des secrets pointe vers la documentation « enterprise-cloud »

- **Lentille :** `egm-structural`
- **Lignes :** 546, comparée à 101
- **Correction proposée :** lier la version générale de la documentation GitHub, ou dire pourquoi celle-ci a été choisie.

### egm-structural-2-16 : l'ordre des essais E4 et E7 n'est pas dit

- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 415, 422, 425
- **Problème :** E4 se fait « sur la pull request verte de l'essai E7 », alors qu'une seule pull request d'essai est ouverte à la fois et que le tableau place E4 avant E7. Un exécutant qui suit l'ordre du tableau bloque à E4.
- **Correction proposée :** déplacer E4 après E7, ou écrire « E4 se joue pendant que la pull request de E7 est ouverte, avant sa fermeture ».

### egm-structural-2-17 : si la règle `deny` de fusion ne marche pas, E4 fusionne une modification de `CLAUDE.md`

- **Lentille :** `egm-structural`
- **Lignes :** 422, 425, 522-539
- **Problème :** E4 tente `gh pr merge` sur la pull request verte de E7, qui modifie `CLAUDE.md`. Si la règle `deny` est défaillante, la fusion réussit. Aucune ligne du tableau des risques ne couvre ce cas.
- **Correction proposée :** utiliser pour E4 une modification sans effet, ou faire précéder E4 d'une vérification sans danger de la règle `deny`.

### egm-style-2-4 : « les trois secondes tentatives d'amorçage » se lit comme une durée

- **Lentille :** `egm-style`
- **Lignes :** 65
- **Correction proposée :** « la seconde tentative de chacune des trois commandes d'amorçage », comme à la l. 422.

### egm-style-2-5 : on ne sait pas d'où vient le message de refus au CUJ 3

- **Lentille :** `egm-style`
- **Lignes :** 133, 293, 302
- **Problème :** le CUJ 3 promet pour chaque commande « un message qui cite la règle de `CLAUDE.md` ». `gh pr merge` est refusé par une règle `deny`, qui affiche le message de Claude Code. Seuls les messages du hook citent `CLAUDE.md` (l. 302).
- **Correction proposée :** « avec le message de la règle `deny`, ou celui du hook, qui cite la règle de `CLAUDE.md` ».

### egm-style-2-6 : on ne sait pas qui modifie `.claude/` une fois la règle levée

- **Lentille :** `egm-style`
- **Lignes :** 297
- **Correction proposée :** dans « demande au propriétaire de lever la règle localement, de faire la modification, puis de la remettre », dire si la modification est faite par le propriétaire ou par l'agent de code.

### egm-style-2-7 : « sans `-X` ni `--method` autre que `GET` » est ambigu

- **Lentille :** `egm-style`
- **Lignes :** 306
- **Correction proposée :** « avec la méthode `GET`, explicite ou implicite, et sans `-f`… ».

### egm-style-2-8 : deux imprécisions dans la règle des versions épinglées

- **Lentille :** `egm-style`
- **Lignes :** 177, comparée à 186
- **Correction proposée :** « la plus récente des versions publiées il y a au moins 14 jours » ; « avec sa somme de contrôle SHA-256, ou le SHA de son commit pour une action ».

### egm-style-2-9 : deux affirmations sans source dans les alternatives

- **Lentille :** `egm-style`
- **Lignes :** 451, 475
- **Problème :** « probablement plus d'exceptions » est une conjecture ; « moins documenté pour les agents de code » est sans source, du même type que egm-style-1-7.
- **Correction proposée :** retirer ces phrases, ou dire sur quoi elles s'appuient.

### egm-style-2-10 : formulations à reprendre

- **Lentille :** `egm-style`
- **Lignes et corrections :**
  - l. 434 : « l'exception de protection est fermée » peut se lire « l'exception à la protection ». Écrire « la commande d'amorçage de la protection est refermée ».
  - l. 363 : « la liste des fichiers modifiés par l'API » se lit « les fichiers que l'API a modifiés ». Écrire « et obtiennent par l'API la liste des fichiers modifiés ».
  - l. 276 : « Une tâche est une tâche (job) de GitHub Actions » est circulaire. Écrire « Une tâche désigne un job de GitHub Actions ».
  - l. 302 : « Tout son code est enveloppé » est vague. Écrire « Tout son code est placé dans un bloc qui intercepte toute exception ».
  - l. 175 : « que le protocole rend possibles » couvre aussi les contributions extérieures. Écrire « …ou tout client tiers, que le protocole rend possible ».
  - l. 321 : « Le premier sera M4 » : « premier » n'a pas d'antécédent. Écrire « Le premier jalon qui en crée une sera M4 ».
  - l. 38 : « la RFC » n'est pas reliée à son fichier. Écrire « la RFC (`docs/designs/mmo-gestion-spatiale-ia.md`) », comme à la l. 386.

--------------------------------------------------------------------------------

## Remarque sans défaut

egm-style note que la l. 380 contient deux termes interdits (`null-sec`, `ISK`). Ce document est exclu du contrôle par l'écart E3 (l. 38, 386), décision du propriétaire. Ce n'est pas un défaut. Aucun autre terme de la liste n'apparaît dans les lignes 1 à 556.

## Correspondance des constats bruts

| Identifiant | egm-design | egm-structural | egm-style |
| --- | --- | --- | --- |
| egm-structural-2-1 | | M1 | N2 |
| egm-structural-2-2 | | M2 | N9 |
| egm-design-2-6 | N6 | M3 | N5 |
| egm-design-2-1 | N1 | | |
| egm-design-2-2 | N2 | M5 | N3 |
| egm-design-2-3 | N3 | | |
| egm-design-2-4 | N4 | | N16 |
| egm-design-2-5 | N5 | | |
| egm-design-2-7 | N7 | | |
| egm-design-2-8 | N8 | | |
| egm-structural-2-3 | | M4 | |
| egm-structural-2-4 | | M6 | N8 |
| egm-style-2-1 | | N4 | N1 |
| egm-style-2-2 | N10 | N9 | N4 |
| egm-style-2-3 | | N6, N12 | N7, N25 |
| egm-design-2-9 | N9 | | |
| egm-design-2-10 | N11 | | |
| egm-design-2-11 | N12 | | |
| egm-structural-2-5 | | N1 | N15 |
| egm-structural-2-6 | | N2 | N11 |
| egm-structural-2-7 | | N3 | N13 |
| egm-structural-2-8 | | N5 | N12 |
| egm-structural-2-9 | | N7 | |
| egm-structural-2-10 | | N8 | |
| egm-structural-2-11 | | N10 | N28 |
| egm-structural-2-12 | | N11 | |
| egm-structural-2-13 | | N13 | |
| egm-structural-2-14 | | N14 | |
| egm-structural-2-15 | | N15 | |
| egm-structural-2-16 | | N16 | N30 |
| egm-structural-2-17 | | N17 | |
| egm-style-2-4 | | | N10 |
| egm-style-2-5 | | | N14 |
| egm-style-2-6 | | | N20 |
| egm-style-2-7 | | | N22 |
| egm-style-2-8 | | | N23 |
| egm-style-2-9 | | | N27 |
| egm-style-2-10 | | | N17, N18, N19, N21, N24, N26, N29 |
| statut egm-design-1-6 (partie a) | | N18 | |
| statut egm-design-1-10 | | | N6 |
| remarque sans défaut | | | N31 |

Les 66 constats bruts (12 + 24 + 30) et la remarque N31 de egm-style se retrouvent tous dans ce tableau.

---

## Décision du propriétaire (2026-11-01) : constats acceptés en l'état

La limite de relecture de l'étape 7 est atteinte. Le propriétaire a choisi d'accepter le document en l'état et de passer à l'étape 8.

**Constats qui restent ouverts, et deviennent des risques acceptés :**
- les 14 constats du tour 1 réglés seulement en partie :
  - egm-design-1-1, 1-2, 1-3, 1-4, 1-6, 1-10, 1-16 et 1-18 ;
  - egm-structural-1-3, 1-4, 1-10 et 1-11 ;
  - egm-style-1-4 et 1-5 ;
- les 15 nouveaux majeurs et les 23 nouveaux mineurs de ce rapport.

**Points que l'implémentation devra régler, faute de quoi elle échouera :**
- egm-design-2-6 : `fnmatch` ne gère pas `**`, et les `.feature` ne seraient pas protégés ;
- egm-structural-2-1 : `garde` et `en-attente` ne tournent pas sur `main` ;
- egm-structural-2-2 : la règle `gitleaks` sur les adresses IP privées attrape ce document ;
- egm-design-2-7 : la pull request obligatoire n'est pas exigée par `protection-main.json` ;
- egm-structural-2-4 : les écarts E4 et E5, décidés le 2026-11-01, demandent une ADR selon le niveau 1.
