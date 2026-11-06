# M0 : garde-fous et squelette du dépôt (document de niveau 2)

*   **Auteur :** Thomas (thom.bruyer)
*   **Statut :** Approved
*   **Date :** 2026-10-31, révisé le 2026-11-01 après les étapes 5 à 9 de la revue EGM
*   **Niveau 1 :** [architecture-niveau-1.md](./architecture-niveau-1.md) (§10, §11 ligne M0, Non-Functional Requirements)

Les titres de niveau 2, le statut, les mots Given / When / Then et les intitulés du gabarit du plan (sous-titres, Type / Scope, Proposed Changes, Create / Modify / Delete) suivent le gabarit de conception d'EGM, en anglais, pour que les outils de revue s'y retrouvent. Tout le reste est en français.

**Conventions de renvoi.** « Technical Plan, point N » désigne une partie du Technical Plan de ce document. « Plan détaillé, point N » désigne un point du Detailed Implementation Plan de ce document. Un renvoi au niveau 1 le dit toujours (« niveau 1, §10 »).

**Notation `!`.** Dans la session Claude Code, une commande précédée de `!` est tapée et lancée par le propriétaire lui-même, en mode shell. Elle n'est pas lancée par l'agent de code. Ce n'est pas la négation du shell.

--------------------------------------------------------------------------------

## Overview

M0 est le premier jalon. Il ne contient aucune règle du jeu. Il crée le dépôt GitHub public du projet et y met en place les garde-fous du document de niveau 1, **avant** que la première ligne de code du jeu soit écrite :
- le dépôt, avec un commit initial qui contient tous les documents existants ;
- le blocage des secrets par GitHub, activé avant le push initial ;
- la protection de la branche `main`, appliquée aussi aux administrateurs ;
- les interdictions de Claude Code : règles `deny` et hook ;
- le refus des secrets avant chaque commit et en CI ;
- le contrôle de garde, qui signale toute modification d'un chemin protégé et refuse qu'on ajoute un scénario « en attente » hors d'une pull request de scénarios ;
- la CI, avec les contrôles obligatoires de M0, qui tourne sur un projet Python vide ;
- les choix que le niveau 1 renvoie à M0 : outil des scénarios en français, marquage des scénarios en attente, format des termes interdits, identifiant des définitions d'étapes.

Une fois M0 livré, les règles de `CLAUDE.md` sur la fusion, le push et les secrets ne reposent plus seulement sur l'agent de code.

### Écarts au niveau 1

Le niveau 1 a le statut Approved et fait foi. Ce document s'en écarte sur six points, tous décidés par le propriétaire et couverts par la revue EGM de ce document :
- **E1 à E3 ont été décidés le 2026-10-31.** Ils relèvent de la règle du niveau 1 selon laquelle les décisions du 2026-10-31 restent dans le niveau 1, sans ADR (niveau 1, plan détaillé, règle de précédence).
- **E4 à E6 ont été décidés le 2026-11-01.** Ils passent par l'ADR `docs/adr/0001-ecarts-m0.md` (plan détaillé, point 27), que le propriétaire accepte avant le commit initial.

Le plan détaillé reporte les six écarts dans le niveau 1 et dans `CLAUDE.md` avant le commit initial.

| Écart | Niveau 1 | Ce document | Report |
| :-- | :-- | :-- | :-- |
| E1. Amorçage | une seule exception : le commit initial, poussé par l'agent de code | trois commandes d'amorçage (blocage des secrets, push initial, protection de `main`), lancées par l'agent de code, chacune refermée par l'état de GitHub (Technical Plan, point 3) | plan détaillé, points 31 et 32 |
| E2. Filtre du push et des réglages | règles `deny` | hook Claude Code, seul à savoir tester une condition (Technical Plan, point 6) ; les règles `deny` interdisent en plus l'édition de `.claude/` et de `.git/hooks/` | plan détaillé, points 31 et 32 |
| E3. Termes interdits | fichiers exclus : la liste, la RFC, `docs/revues/` | plus `docs/designs/architecture-niveau-1.md` et ce document, qui citent les termes pour définir la règle | plan détaillé, points 30 et 32 |
| E4. Rapports de revue | `docs/revues/` n'est pas protégé | `docs/revues/` devient un chemin protégé : les rapports et le compte rendu de M0 passent par une pull request protégée | ADR 0001 ; plan détaillé, points 31 et 32 |
| E5. Contrôles de M0 | linter, typage, `gitleaks`, garde, termes interdits | plus `tests-outillage` (tests du hook et des scripts) et `en-attente` (Technical Plan, point 5) | ADR 0001 ; plan détaillé, point 32 |
| E6. Liste des chemins protégés | une liste dans §10 | la liste qui fait foi est `.github/chemins-proteges.txt` (Technical Plan, point 8). Elle ajoute `tests/outillage/`, les fichiers de configuration des outils, `.gitleaks.toml`, `.pre-commit-config.yaml` et `.python-version`. `CLAUDE.md` et le niveau 1 y renvoient | ADR 0001 ; plan détaillé, points 31 et 32 |

## The Problem

Aujourd'hui, toutes les règles de `CLAUDE.md` reposent sur la discipline de l'agent de code. Aucun mécanisme n'est en place : pas de dépôt GitHub, pas de CI, pas de protection de branche, pas de filtre de commandes. `CLAUDE.md` le dit lui-même.

Trois raisons obligent à régler ce point avant tout code du jeu :

1. **L'agent de code agit avec le compte GitHub du propriétaire.** GitHub ne distingue pas l'agent de code du propriétaire. Sans protection explicite, l'agent peut fusionner, pousser sur `main` ou modifier les réglages, et rien ne l'arrête.
2. **Le dépôt sera public.** Un secret poussé une seule fois est exposé, même s'il est retiré ensuite. La protection doit précéder le premier push.
3. **Les contrôles de M1 et des jalons suivants s'appuient sur ceux de M0.** Le rejeu, la mutation, les contrats d'imports et la suite canari ne servent à rien si une pull request rouge peut être fusionnée, ou si la configuration de la CI peut changer sans être signalée.

**Ce que M0 ne protège pas.** M0 protège contre les erreurs et rend les écarts visibles. Il ne protège pas contre un contournement délibéré, et c'est le risque accepté par le propriétaire (niveau 1, §10). En particulier :
- une pull request qui modifie `.github/` peut affaiblir ses propres contrôles obligatoires, par exemple en faisant sauter une tâche. Le contrôle de garde le signale, mais rien ne l'empêche ;
- un script lancé par l'agent de code échappe au hook.

## Goals

Chaque objectif reprend un élément du critère de sortie de M0 (niveau 1, §11) ou une exigence du niveau 1. Chacun a sa vérification et un essai du Technical Plan, point 12.

1. **Le dépôt public existe et contient les documents.** Le commit initial contient `CLAUDE.md`, `docs/` et la configuration de M0.
   *Vérification :* `gh repo view EZPK/4X --json visibility` renvoie `PUBLIC` ; `git log --first-parent origin/main` commence par le commit initial ; un push direct sur `main` est refusé par GitHub (essai E2).
2. **Une pull request rouge ne peut pas être fusionnée, même par un administrateur.**
   *Vérification :* le propriétaire tente de fusionner une pull request d'essai dont un contrôle échoue, avec ses droits d'administrateur. GitHub refuse, et c'est bien GitHub qui refuse, pas Claude Code (essai E3).
3. **Claude Code refuse les commandes interdites** de `CLAUDE.md` : fusion, y compris `--admin` et `--auto` ; push vers `main` ; push forcé ; contournement du hook pre-commit ; écriture des réglages du dépôt ; édition de `.claude/` et de `.git/hooks/`. Les trois commandes d'amorçage (Technical Plan, point 3) ne sont acceptées que tant que leur condition tient.
   *Vérification :* l'essai E4 lance chaque catégorie de commande et les trois secondes tentatives d'amorçage, et cite chaque refus. Les variantes de chaque catégorie sont couvertes par les tests du hook.
4. **Un secret est arrêté avant de devenir public, et la CI détecte ceux qui passent.** Trois barrières :
   - le hook pre-commit (`gitleaks`) refuse le commit ;
   - le blocage des secrets de GitHub refuse le push, s'il est disponible ;
   - la CI (`gitleaks`) fait échouer la pull request. Elle détecte après publication, et une détection en CI impose de révoquer le secret.

   À M0, `gitleaks` détecte les formats de jetons connus et la valeur d'essai du projet. Les règles sur les adresses réseau et sur les variables d'environnement du projet arrivent à M4, avec ces adresses et ces variables. Les graines du monde en ligne ne se reconnaissent à aucun motif : elles restent couvertes par `.gitignore` et par la règle de `CLAUDE.md`.
   *Vérification :* essais E5 et E6.
5. **Une pull request qui touche un chemin protégé est signalée.**
   *Vérification :* une pull request d'essai qui modifie `CLAUDE.md` reçoit l'étiquette « fichiers protégés modifiés », et la liste des fichiers protégés modifiés apparaît en tête de sa description et dans le résumé de la tâche (essai E7).
6. **Un scénario ne peut pas être mis « en attente » pour cacher une régression.**
   *Vérification :* une pull request d'essai qui ajoute une entrée à `tests/scenarios/en_attente.txt` sans modifier de `.feature` fait échouer la tâche `en-attente` (essai E8).
7. **La CI tourne et passe sur le projet vide.** Les tâches de `ci.yml` (`lint`, `typage`, `gitleaks`, `termes-interdits`, `tests-outillage`) sont vertes sur `main`. Les tâches `garde` et `en-attente`, qui ne tournent que sur les pull requests, sont vertes sur une pull request d'essai sans défaut.
   *Vérification :* essai E1, puis l'état de `garde` et `en-attente` sur la pull request de l'essai E7 ; une pull request qui ajoute un terme interdit fait échouer `termes-interdits` (essai E9).
8. **Aucun runner auto-hébergé.**
   *Vérification :* `gh api repos/EZPK/4X/actions/runners` renvoie `total_count: 0` (essai E10).
9. **La feuille de route est copiée dans les jalons GitHub, et les choix renvoyés à M0 sont tranchés.**
   *Vérification :* les jalons M0 à M6 existent et renvoient à `docs/feuille-de-route.md` (essai E10). Chaque choix a sa décision et sa raison au Technical Plan, point 1, et le glossaire est mis à jour par le plan détaillé, point 29.

## Non-Goals

*   **Aucun code du jeu,** aucun scénario de jeu, aucune règle. Le squelette Python ne contient que ce qu'il faut pour que le linter et le typage aient quelque chose à vérifier.
*   **Les contrôles de M1 et suivants :**
    - à M1 : tests et scénarios obligatoires, rejeu, tests de propriétés (`hypothesis`), contrats d'imports obligatoires, mutation, suite canari ;
    - à M2 : panneau de métriques ;
    - à M3 : captures et vidéo du client ;
    - à M4 : verdicts d'entraînement.

    M0 fixe seulement le moyen de marquer les scénarios en attente, que M1 utilisera. Les contrats d'imports sont lancés à M0 sans être obligatoires.
*   **Les règles `gitleaks` propres au projet sur les adresses IPv4 privées et sur les variables `FOURX_`.** Elles arrivent à M4, quand l'adresse du serveur MLflow et les premières variables du projet existeront. À M0, elles ne détecteraient rien, sinon ce document et les rapports de revue, qui citent ces plages.
*   **La catégorie « références régénérées » du contrôle de garde.** Les empreintes de référence n'existent qu'à partir de M1, qui fixera leur chemin et la catégorie.
*   **Le compte GitHub séparé pour l'agent de code** (alternative G du niveau 1), écarté par le propriétaire.
*   **La mise en place du PC d'entraînement et de MLflow** (M4).
*   **Une preuve vidéo.** Au niveau 1, la vidéo arrive avec le client, à M3. À M0, les preuves sont les liens vers la CI et les sorties de commandes, rassemblées dans le compte rendu de M0.

## Open Questions

*   **Réglages GitHub d'un dépôt public gratuit :** la protection appliquée aux administrateurs et le blocage des secrets au push sont-ils disponibles ? On le vérifie juste après l'amorçage (Technical Plan, point 4), car le critère de sortie en dépend.
*   **Comportement de Claude Code, à vérifier contre la version installée avant d'écrire le hook :**
    - la syntaxe des motifs `deny`, et l'appel du hook par `$CLAUDE_PROJECT_DIR` ;
    - le fait qu'un hook `PreToolUse` ne bloque que sur le code de sortie 2 ;
    - le moment où un nouveau `.claude/settings.json` prend effet dans la session en cours ;
    - le fait que les commandes lancées par le propriétaire avec `!` ne passent ni par les règles `deny` ni par le hook. C'est vérifié par une commande sans danger avant les essais. Si ce n'est pas le cas, le propriétaire lance ses essais dans un terminal hors de Claude Code.

## Critical User Journeys (CUJs)

Ces parcours détaillent, pour M0, le CUJ 3 du niveau 1 (« un agent de code livre une fonctionnalité, jalon M0 et suivants »). M0 en livre la protection de `main`, le contrôle de garde et l'interdiction de fusion par l'agent. Les scénarios en français deviennent obligatoires à M1.

### CUJ 1 : l'amorçage

*   **Given** : le dossier de travail contient `CLAUDE.md`, `docs/` et la configuration de M0 dans un commit local ; aucun dépôt GitHub n'existe.
*   **When** : le propriétaire demande explicitement à l'agent de code de créer le dépôt.
*   **Then** :
    - le dépôt public est créé ;
    - le blocage des secrets est activé ;
    - le commit initial est poussé sur `main` ;
    - la protection de `main` est appliquée ;
    - une seconde tentative de chacune de ces commandes est refusée par le hook.

### CUJ 2 : une pull request rouge

*   **Given** : une pull request d'essai dont un contrôle obligatoire échoue.
*   **When** : le propriétaire tente de la fusionner avec `! gh pr merge <n> --admin`.
*   **Then** : GitHub refuse la fusion, avec un message qui cite la protection de branche.

### CUJ 3 : l'agent de code tente une commande interdite

*   **Given** : une pull request d'essai ouverte, aux contrôles **verts**.
*   **When** : l'agent de code lance `gh pr merge`, avec ou sans `--admin` ou `--auto`, puis chacune des autres commandes interdites de l'essai E4.
*   **Then** : Claude Code refuse chaque commande avant de l'exécuter, avec un message qui cite la règle de `CLAUDE.md`.

### CUJ 4 : un faux secret

*   **Given** : deux faux secrets :
    - un jeton au format des jetons GitHub (`ghp_…`) ;
    - une valeur au format de la règle d'essai propre au projet (`FOURX_ESSAI_SECRET_…`).

    Aucun des deux ne donne accès à quoi que ce soit.
*   **When** :
    1. le propriétaire tente de committer chacun d'eux ;
    2. il les committe avec `! git commit --no-verify`, ce qui contourne le hook pre-commit ;
    3. il les pousse sur une branche `essai/…`.
*   **Then** :
    - le hook pre-commit refuse les deux commits ;
    - le blocage de GitHub refuse le push du jeton `ghp_…`. S'il ne le refuse pas, le compte rendu note « blocage non démontré » ;
    - la valeur d'essai, que GitHub ne connaît pas, arrive dans une pull request, où la tâche `gitleaks` échoue.

    Les faux secrets ne sont fusionnés dans aucune branche, mais restent lisibles dans la pull request fermée.

### CUJ 5 : une pull request qui touche un chemin protégé

*   **Given** : une pull request d'essai qui modifie `CLAUDE.md`.
*   **When** : la pull request est ouverte, puis sa description est réécrite.
*   **Then** :
    - le contrôle de garde pose l'étiquette « fichiers protégés modifiés » ;
    - il écrit la liste des fichiers protégés modifiés en tête de la description et dans le résumé de sa tâche ;
    - il rétablit la liste après la réécriture de la description.

### CUJ 6 : un scénario mis en attente pour cacher une régression

*   **Given** : une pull request d'essai qui ajoute une entrée à `tests/scenarios/en_attente.txt` sans toucher à aucun `.feature`.
*   **When** : la CI tourne.
*   **Then** : la tâche `en-attente` échoue et cite l'entrée ajoutée.

## Technical Plan (Architecture)

### 1. Décisions prises pour M0

| Sujet | Décision | Origine et raison |
| :-- | :-- | :-- |
| Dépôt | `EZPK/4X`, public | choix du propriétaire |
| Licence | aucune : tous droits réservés, ce que dit le `README.md`. Le sujet reviendra avant toute contribution extérieure ou tout client tiers, que le protocole rend possibles | choix du propriétaire |
| Python | 3.15, dans `.python-version` et `pyproject.toml` (`requires-python = ">=3.15,<3.16"`) | choix du propriétaire. Outils vérifiés sous 3.15 le 2026-10-31 (mypy 2.4.1, ruff 0.17.3, pytest 9.2.0, pytest-bdd 9.0.1, mutmut 3.8.1, import-linter 2.15, pre-commit 4.7.0, msgspec 0.22.0), puis le 2026-11-01 dans les versions que retient la règle des 14 jours (ruff 0.17.1, mypy 2.4.0, pytest 9.1.1, pytest-bdd 9.0.0, import-linter 2.15, pre-commit 4.7.0) |
| Versions épinglées | la version épinglée de chaque outil, dépendance Python ou action est la dernière publiée depuis au moins 14 jours (`exclude-newer` pour les dépendances Python) ; elle est notée, avec sa somme de contrôle SHA-256 ou son SHA de commit, dans le compte rendu de M0 | choix de ce document : une version trop récente n'a pas eu le temps de révéler ses défauts |
| Gestion des dépendances | `uv`, avec `uv.lock` versionné ; la CI lance `uv sync --locked` | niveau 1, §2 |
| Linter | `ruff check` et `ruff format --check` | choix de ce document : un seul outil pour le style et la mise en forme |
| Typage strict | `mypy --strict`, sur `src/`, `tests/`, `.github/scripts/` et `.claude/hooks/` | choix du propriétaire |
| Configuration des outils | fichiers séparés et protégés : `ruff.toml`, `mypy.ini`, `pytest.ini`, `.importlinter`. `pyproject.toml` et `uv.lock` ne sont pas protégés | pour qu'une pull request de fonctionnalité puisse ajouter une dépendance sans toucher un chemin protégé (niveau 1, §10) |
| Scénarios en français | `pytest-bdd`, `# language: fr` | choix du propriétaire. Un scénario en français a été testé avec pytest-bdd 9.0.1, et `pytest` sait exiger qu'un scénario en attente échoue (`xfail` strict) |
| Identifiant des définitions d'étapes | `steps`, dossier `tests/scenarios/steps/` | mot anglais attendu par la convention de langue, et usage courant de `pytest-bdd` |
| Format des termes interdits | un terme par ligne, sous le titre `## Termes` (Technical Plan, point 9) | simple à lire pour le propriétaire et pour le script |
| Paquet racine du code | `fourx`. Les identifiants des paquets du niveau 1 restent `core`, `schema`, etc. ; leur chemin d'import est `fourx.core`, `fourx.schema`, etc. | contrainte technique : `4X` commence par un chiffre, ce qu'un nom de paquet Python interdit ; un nom racine évite les conflits avec d'autres paquets nommés `tools` ou `schema` |
| Actions GitHub | chaque action tierce est épinglée par le SHA de son commit | un tag git peut être déplacé vers un autre commit, un SHA ne peut pas l'être |

### 2. Ce que M0 met en place

```text
  agent de code (Claude Code)
     │  commande ou édition
     ▼
  ┌────────────────────────────────────────────────┐
  │ .claude/settings.json : règles deny            │  fusion, push forcé, édition
  │ .claude/hooks/garde_commandes.py (PreToolUse)  │  de .claude/, réglages
  └────────────────────────────────────────────────┘
     │  commit
     ▼
  ┌────────────────────────────────────────────────┐
  │ hook pre-commit : gitleaks (+ .gitleaks.toml)  │  refuse un secret
  └────────────────────────────────────────────────┘
     │  push d'une branche, puis pull request
     ▼
  ┌────────────────────────────────────────────────┐
  │ GitHub : blocage des secrets (si disponible)   │
  │ ci.yml : lint · typage · gitleaks              │
  │          · termes-interdits · tests-outillage  │
  │ garde.yml (version de main) : garde            │  étiquette, liste
  │          · en-attente                          │  des chemins protégés
  └────────────────────────────────────────────────┘
     │  contrôles verts
     ▼
  ┌────────────────────────────────────────────────┐
  │ protection de main, appliquée aux admins :     │
  │   pull request obligatoire, contrôles exigés,  │
  │   pas de push forcé ni de suppression          │
  └────────────────────────────────────────────────┘
     │
     ▼
  fusion par le propriétaire seul
```

### 3. L'amorçage

Comme le prévoit le niveau 1, l'agent de code pousse lui-même le commit initial, à la demande explicite du propriétaire. Le propriétaire a choisi, le 2026-10-31, que l'agent de code applique aussi les deux réglages du dépôt (écart E1). Les trois **commandes d'amorçage** sont, dans cet ordre :
1. l'activation du blocage des secrets, avant tout push, pour que le commit initial soit lui-même protégé ;
2. le push initial ;
3. la protection de `main`, qui exige que `main` existe.

Le hook Claude Code les reconnaît par égalité exacte de la commande. Il n'autorise chacune que si sa condition d'état tient et si le fichier envoyé est identique à la copie de référence que contient le hook. Chaque exception se referme donc d'elle-même après sa première exécution.

| Commande d'amorçage | Autorisée seulement si | Après la première exécution |
| :-- | :-- | :-- |
| `gh api -X PATCH repos/EZPK/4X --input .github/securite-depot.json` | `security_and_analysis.secret_scanning_push_protection.status` n'est pas `enabled`, la lecture ayant réussi ; et le JSON de `.github/securite-depot.json` est identique à la copie de référence du hook | le blocage est actif : refus. Si GitHub ne propose pas cette fonction, la lecture le montre, et le hook refuse aussi |
| `git push -u origin main` | `git ls-remote --heads origin main` réussit (code de sortie 0) et ne renvoie rien | `main` existe : refus par le hook, puis par la protection de GitHub |
| `gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json` | la lecture de la protection renvoie 404 avec le message `Branch not protected`, tout autre 404 étant refusé ; et le JSON de `.github/protection-main.json` est identique à la copie de référence du hook | une protection existe : refus |

Juste avant le push initial, l'agent de code lance `gitleaks git` sur le commit initial. Le résultat attendu est : aucune fuite.

**Qui lance chaque étape :**

| Action | Qui | Comment |
| :-- | :-- | :-- |
| Préparer tous les fichiers de M0 en local, puis le commit initial | agent de code | sans dépôt GitHub, donc sans pull request (niveau 1, §10, circuit des documents de niveau 2) |
| Créer le dépôt public | agent de code, à la demande explicite du propriétaire | `gh repo create EZPK/4X --public --source .` (sans `--push`) ; le hook n'autorise `gh repo create` que tant que le dépôt n'existe pas |
| Les trois commandes d'amorçage, dans l'ordre | agent de code, à la demande explicite du propriétaire | voir le tableau ci-dessus |
| Créer les étiquettes du garde | agent de code | `gh api` en écriture sur `labels`, route autorisée |
| Vérifier les réglages obtenus | agent de code | `gh api` en lecture seule (Technical Plan, point 4) |
| Créer les jalons GitHub, vérifier l'absence de runner | agent de code | `gh api` sur `milestones`, route autorisée, et lecture de `actions/runners` |
| Mener les essais | agent de code, et le propriétaire pour trois d'entre eux | Technical Plan, point 12 |

Trois essais reviennent au propriétaire : la fusion en administrateur, le commit sans hook pre-commit et le push direct sur `main`. Les règles de l'agent de code lui interdisent ces trois commandes.

### 4. La vérification des réglages GitHub, juste après l'amorçage

La documentation consultée ne confirme pas que l'application de la protection aux administrateurs et le blocage des secrets au push soient disponibles sur un dépôt public gratuit (voir Additional Resources). Juste après les trois commandes d'amorçage, l'agent de code lit et cite dans le compte rendu de M0 :
- `gh api repos/EZPK/4X/branches/main/protection` : il vérifie `enforce_admins.enabled`, `allow_force_pushes.enabled` et `allow_deletions.enabled`, ainsi que la liste des contrôles exigés ;
- `gh api repos/EZPK/4X` : il vérifie `security_and_analysis.secret_scanning.status` et `secret_scanning_push_protection.status` ;
- `gh api repos/EZPK/4X/actions/permissions/workflow` : il vérifie le jeton des workflows en lecture seule, et l'interdiction aux Actions d'approuver des pull requests.

Puis, sur la première pull request d'essai, il vérifie que chaque contrôle exigé correspond à une tâche réellement lancée, avec le même nom, et que les états des tâches de `garde.yml` (déclenchées par `pull_request_target`) sont bien rattachés au commit de tête de la pull request. Sinon, plus aucune fusion ne serait possible.

**Si un réglage manque ou diffère,** l'agent de code s'arrête et le signale au propriétaire :
- **Application aux administrateurs indisponible.** Solutions, dans cet ordre :
  1. un ensemble de règles (ruleset), que l'agent de code écrit alors dans `.github/ruleset-main.json` (liste de contournement vide, mêmes exigences que `protection-main.json`) et que le propriétaire applique avec `!` ;
  2. un abonnement payant ;
  3. un critère de sortie réduit, consigné comme risque accepté.

  Le propriétaire choisit.
- **Blocage des secrets au push indisponible.** Le hook pre-commit et la tâche `gitleaks` de la CI restent en place, et le manque est consigné. L'objectif 4 reste atteignable, sans la barrière du push.
- **Nom de contrôle exigé faux.** La procédure de reprise du Technical Plan, point 13, s'applique.

### 5. La protection de `main` et les contrôles obligatoires

Une **tâche** est une tâche (job) de GitHub Actions. Un **contrôle obligatoire** est une tâche que la protection de `main` exige avant la fusion (required status check). À M0, les contrôles obligatoires sont :
- dans `ci.yml` : `lint`, `typage`, `gitleaks`, `termes-interdits`, `tests-outillage` ;
- dans `garde.yml` : `garde` et `en-attente`.

Les tâches `garde` et `en-attente` ne tournent que sur les pull requests : elles sont exigées pour fusionner une pull request, et n'apparaissent pas sur les commits de `main`. La tâche `imports`, qui lance `lint-imports`, tourne aussi, mais n'est pas obligatoire avant M1. À M1, la tâche `tests-outillage` devient `tests` : elle couvrira l'outillage, les scénarios et les tests de propriétés.

La protection de `main` est la protection de branche classique de GitHub :
- les contrôles obligatoires ci-dessus, et la branche doit être à jour avant la fusion ;
- `enforce_admins` activé ;
- pull request obligatoire, sans approbation requise (`required_approving_review_count: 0`), puisque l'auteur des pull requests est le propriétaire lui-même ;
- pas de push forcé, pas de suppression de la branche.

Le contenu exact de la requête est versionné dans `.github/protection-main.json`, un chemin protégé. L'agent de code l'applique par la troisième commande d'amorçage.

### 6. Les interdictions de Claude Code

**Les règles `deny` de `.claude/settings.json`** refusent par motif :
- `gh pr merge` ;
- `git push` avec `--force`, `-f`, `--force-with-lease`, `--mirror`, `--all` ou `--delete` ;
- toute commande qui contient `--no-verify` ;
- `gh repo edit`, `gh repo delete`, `gh repo archive`, `gh repo rename` ;
- l'outil Edit sur `/.claude/**` et `/.git/hooks/**`, où le `/` initial désigne la racine du projet. Selon la documentation de Claude Code 2.1.306, une règle `Write(...)` sur un chemin ne s'applique à rien, alors qu'une règle `Edit(...)` couvre aussi les écritures faites par des commandes Bash (redirections, `tee`, `sed`). Sans cette règle, l'agent de code pourrait désactiver ses propres garde-fous en éditant le hook. En contrepartie, toute modification future de `.claude/` demande au propriétaire de lever la règle localement, de faire la modification, puis de la remettre. Le changement passe ensuite par une pull request protégée.

Aucun serveur MCP GitHub n'est configuré dans le projet. Si un l'était un jour, ses outils d'écriture seraient ajoutés aux règles `deny`.

**Le hook `PreToolUse`** (`.claude/hooks/garde_commandes.py`) est déclaré sur l'outil Bash, avec `"timeout": 30` et `"onFailure": "block"` : sans cette option, un hook qui dépasse son délai ne bloque pas la commande (documentation de Claude Code 2.1.306). Il est lancé par `python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/garde_commandes.py"`, pour ne pas dépendre du dossier courant, et n'utilise que la bibliothèque standard de Python. Il suit ces règles :
- **Il refuse en cas de doute.** Tout son code est enveloppé : une erreur interne, une entrée JSON inattendue ou une commande `git` ou `gh` qu'il ne sait pas analyser donnent un refus (code de sortie 2), avec un message en français qui cite la règle de `CLAUDE.md`.
- **Les commandes d'amorçage** sont reconnues par égalité exacte de la chaîne de commande, et autorisées sous les conditions du Technical Plan, point 3.
- **Pour le reste,** les motifs interdits sont cherchés dans toute la chaîne brute, sans découpage, de sorte qu'un enchaînement (`&&`, `||`, `;`, `|`, `$(…)`, sous-shell, `bash -c`, `eval`) ne les cache pas. Un faux positif ne donne qu'un refus.
- **Écritures sur GitHub, en liste blanche :**
  - `gh api` en lecture pure (sans `-X` ni `--method` autre que `GET`, et sans `-f`, `-F`, `--field`, `--raw-field` ni `--input`) est autorisé ;
  - en écriture, `gh api` n'est autorisé que sur les routes `issues`, `milestones`, `labels`, `pulls` (création, description, et fermeture par `state=closed`) et les commentaires, et en `DELETE` sur `git/refs/heads/essai/…`, pour supprimer les branches d'essai ;
  - les sous-commandes `gh` de lecture `gh pr view`, `gh pr list`, `gh pr checks`, `gh run list` et `gh run view` sont autorisées ;
  - `gh pr create` n'est autorisé qu'avec `--body-file`, et `git commit` qu'avec `-m` sans motif interdit ou avec `-F` ;
  - `gh api graphql` est refusé ;
  - `gh repo` n'est autorisé qu'en `view`, et en `create` tant que le dépôt n'existe pas ;
  - `gh pr edit --remove-label` est refusé pour les étiquettes du garde.
- **`git push` :** le hook détermine la branche cible réelle (refspec, sinon branche suivie) et refuse `main` hors de l'amorçage, y compris sous les formes `HEAD:main`, `x:refs/heads/main` et `:main`. Il refuse aussi un push sans refspec, ou vers `HEAD` ou `@`, quand le dépôt visé peut être un autre que celui du dossier courant (voir « Dépôt visé ailleurs »).
- **Contournement du hook pre-commit :** il refuse `git commit -n`, `SKIP=…`, `core.hooksPath` et `pre-commit uninstall`. Il refuse aussi `git commit` si le hook `pre-commit` du dossier git commun (`git rev-parse --git-common-dir`, sous-dossier `hooks/`) est absent, non exécutable ou n'appelle pas `pre-commit`, ou si un autre dossier de hooks est configuré, car un nouveau clone n'a pas ce hook (depuis la pull request #9 ; avant, il cherchait `.git/hooks/pre-commit` du dossier de travail, ce qui refusait tout commit depuis un worktree lié). Cette recherche demande git 2.31 au minimum (option `--path-format=absolute` de `git rev-parse`) : avec un git plus ancien, `rev-parse` recopie l'option inconnue dans sa sortie, qui n'est alors pas un chemin valide (un échec de `rev-parse` donnerait aussi un refus), et tout `git commit` lancé par Claude Code est refusé, avec un message qui annonce un hook absent.
- **Dépôt visé ailleurs** (ajouté le 2026-11-06 ; avant, seul un `cd`, `pushd` ou `popd` du premier niveau de la commande était vu) : le hook vérifie le hook pre-commit du dépôt du dossier courant. Pour une commande qui contient `git`, `gh` ou `git-`, après les motifs bruts et avant l'analyse des commandes git et gh, il parcourt donc toute la commande, sous-chaînes comprises (au-delà de trois niveaux de sous-chaînes, la commande est refusée). S'il y trouve `cd`, `pushd` ou `popd`, un jeton qui contient `GIT_` suivi d'une lettre, d'un chiffre ou de `_`, un `env` suivi d'une option, `--directory`, `--project`, `-execdir`, `-okdir`, ou `foreach` dans un segment qui contient `submodule`, il considère que git peut viser un autre dépôt : il refuse alors `git commit`, comme avec `git -C`, `--git-dir`, `--work-tree` ou `--namespace`, et `git push` sans refspec ou vers `HEAD` ou `@`. Il refuse aussi : tout appel à git dans une commande qui contient `GIT_CONFIG` ; un alias défini par `git -c alias.…` ou `--config-env=alias.…` ; tout segment où le mot `config` est suivi de `alias.`, quelle que soit la casse (motif brut, qui refuse aussi la lecture d'un alias) ; `git -c …` ou `--config-env=…` avec `git commit` ou `git push` ; une option globale de git inconnue suivie, plus loin, de `commit`, de `push` ou d'un argument qui contient `alias.` (`--help`, `-h` et `--version` passent) ; `git-commit` et `git-push` lancés directement. C'est un refus en cas de doute : un message de commit qui cite l'une de ces formes est refusé avec `-m`, et passe avec `-F`.
- **Contournements connus (limite acceptée).** Le hook ne filtre que le texte des commandes. Ces formes, relevées par les revues de 2026-11-06, passent encore : un alias ou un dossier de hooks écrit directement dans un fichier de configuration (`.git/config`, `~/.gitconfig`), y compris dans la même commande, ou chargé par `-c include.path=…` ; une configuration lue ailleurs par `HOME=…` ou `XDG_CONFIG_HOME=…` ; des motifs bruts coupés par des guillemets (`S""KIP=`, `core."hooksPath"`) ; un nom de variable construit (`GIT_$x`, `$'…'`) ; git lancé par une variable, une substitution ou une copie du binaire (`$(command -v git)`, `$g`) ; un commit créé sans `git commit` (`commit-tree`, `cherry-pick`, `revert`) ; un script ; un alias déjà configuré dans le dépôt ; un outil qui change de dossier sans option visible ou par une option autre que celles citées. Ce ne sont pas des fautes d'inattention. Le filet reste `gitleaks` en CI, le blocage des secrets par GitHub au push, et la protection de `main`.

Le hook ne voit pas ce que fait un script lancé par l'agent : c'est la limite écrite dans `CLAUDE.md`. Ses tests (`tests/outillage/test_garde_commandes.py`) couvrent chaque catégorie et chaque variante citée ici, l'erreur interne, l'analyse impossible, et les trois commandes d'amorçage avec un état de GitHub simulé : condition vraie, condition fausse, lecture en échec et fichier modifié.

### 7. Les secrets

- **`.gitignore`** part du modèle Python de référence de GitHub. On y ajoute :
  - partout : `.env*` sauf `.env.example`, `*.key`, `*.pem`, `*.p12`, `*.parquet`, `*.duckdb`, `*.ckpt`, `*.pt` ;
  - à la racine seulement : `/data/`, `/models/`, `/mlruns/`, `/mlartifacts/`, `/snapshots/`, `/logs/` et `/config/monde-en-ligne/`. Ancrés à la racine, ces motifs n'ignorent pas les futurs fichiers de référence placés dans `tests/`.
- **`.env.example`** ne contient qu'un commentaire : les variables d'environnement du projet y seront listées, sans valeur, à mesure que les jalons les créent. Le premier sera M4 (adresse du serveur MLflow).
- **`.gitleaks.toml`** étend la configuration par défaut (`[extend] useDefault = true`) et n'ajoute qu'une règle propre au projet : la règle d'essai `FOURX_ESSAI_SECRET_[A-Z0-9]{32}`, que GitHub ne connaît pas. La valeur d'essai est **tirée au hasard** : une suite régulière comme `ABCDEFGH…` est écartée par la configuration par défaut, ce qui a été vérifié le 2026-11-01 avec `gitleaks` 8.30.1. Les règles sur les adresses IPv4 privées et sur les variables `FOURX_` arrivent à M4 (Non-Goals).
- **Un seul binaire `gitleaks`,** la version 8.30.1, épinglée avec sa somme de contrôle SHA-256, sert au hook pre-commit (hook local de `pre-commit`) et à la CI.
- **En CI,** la tâche `gitleaks` analyse les commits de la pull request ou du push.
- **Côté GitHub,** le blocage au push est activé en premier pendant l'amorçage.

### 8. Le contrôle de garde

**`.github/chemins-proteges.txt`** contient un motif par ligne. Les motifs sont traduits par une fonction de `garde.py`, testée et indépendante de la version de Python : `**` désigne zéro ou plusieurs dossiers, `*` une suite de caractères sans `/`, et tout autre caractère se lit tel quel. Les lignes vides et les lignes qui commencent par `#` sont ignorées. À M0, la liste complète est :

```text
.github/**
CLAUDE.md
.claude/**
docs/designs/**
docs/adr/**
docs/glossaire.md
docs/feuille-de-route.md
docs/noms-valides.md
docs/termes-interdits.md
docs/revues/**
tests/scenarios/**/*.feature
tests/scenarios/steps/**
tests/scenarios/conftest.py
tests/scenarios/test_scenarios.py
tests/outillage/**
ruff.toml
mypy.ini
pytest.ini
.importlinter
.pre-commit-config.yaml
.gitleaks.toml
.python-version
```

Le fichier `tests/scenarios/en_attente.txt` n'est couvert par aucun motif. Il est contrôlé par la tâche `en-attente`.

**`.github/workflows/garde.yml`** se déclenche sur `pull_request_target`, pour les événements `opened`, `synchronize`, `reopened` et `edited`. Ses règles :
- il ne récupère que la version de `main`, jamais le code de la branche ;
- ses droits se limitent à `contents: read` et `pull-requests: write` ;
- aucune expression `${{ github.event.* }}` n'apparaît dans un `run:` ;
- le workflow lit la liste des fichiers modifiés par l'API, de façon paginée et avec l'ancien nom de chaque fichier renommé, et la passe aux scripts dans un fichier, à raison d'un objet JSON par ligne (`previous_filename` vaut `null` sans renommage) ; il fournit le jeton `GH_TOKEN` à `gh`. Les scripts lisent les données de la pull request dans `$GITHUB_EVENT_PATH` et ne font aucun appel réseau ;
- aucun cache ni artefact n'est partagé avec les workflows `pull_request`.

**La tâche `garde`** fait trois choses :
- elle lit les étiquettes déjà présentes dans `$GITHUB_EVENT_PATH`, et décide de poser l'étiquette « fichiers protégés modifiés », de la retirer, ou de ne rien faire : on ne retire une étiquette que si elle est présente ;
- elle écrit la liste de ces fichiers, échappée (code en ligne, caractères spéciaux neutralisés), dans un bloc en tête de la description, entre `<!-- garde:debut -->` et `<!-- garde:fin -->` ;
- elle copie cette liste dans le résumé de la tâche (`$GITHUB_STEP_SUMMARY`), que l'auteur de la pull request ne peut pas modifier.

Le bloc du garde vient en premier. Le résumé de la revue EGM, que l'agent de code écrit, vient ensuite. Si la description est réécrite, l'événement `edited` relance le garde, qui remet le bloc en tête.

Si aucun chemin protégé n'est modifié, la tâche retire l'étiquette et le bloc s'ils existent. Une description vide est traitée comme un texte vide. La tâche réussit dès qu'elle a terminé son analyse et appliqué ou retiré l'étiquette et le bloc. Elle n'échoue qu'en cas d'erreur technique : lecture de l'API, écriture de l'étiquette ou de la description.

**La tâche `en-attente`** compare `tests/scenarios/en_attente.txt` à sa version sur `main`. Elle échoue si la pull request ajoute une entrée sans modifier aucun fichier `.feature`. Les retraits sont toujours permis.

### 9. Les termes interdits

- **Format de `docs/termes-interdits.md` :** les termes sont les lignes non vides comprises entre le titre `## Termes` et le titre suivant, ou la fin du fichier. Un terme par ligne, sans puce.
- **Recherche :** sans tenir compte de la casse, par mots entiers. Un terme est trouvé seulement s'il n'est ni précédé ni suivi d'une lettre, d'un chiffre ou d'un souligné, au sens de `str.isalnum()` de Python, lettres accentuées comprises. Le tiret fait partie du terme : `null-sec` est cherché tel quel, et `ISK` n'est pas trouvé dans `disk`.
- **Portée :**
  - tous les fichiers suivis par git (un fichier listé mais absent du disque est ignoré) ;
  - le titre et la description de la pull request ;
  - les messages de ses commits ;
  - le nom de la branche.
- **Fichiers exclus :** `docs/termes-interdits.md`, `docs/designs/mmo-gestion-spatiale-ia.md`, `docs/revues/**`, `docs/designs/architecture-niveau-1.md` et ce document (écart E3). Cette liste est écrite dans `docs/termes-interdits.md`, sous le titre `## Fichiers exclus`, un motif par ligne dans la syntaxe de `chemins-proteges.txt` (Technical Plan, point 8), et le script la lit. La traduction des motifs est partagée par `garde.py` et `termes_interdits.py`, dans le module `.github/scripts/motifs.py`.
- **Exception :** une pull request qui ne modifie que `docs/termes-interdits.md` est dispensée de la vérification de sa description et de ses messages de commit, qui citent presque forcément le terme ajouté.
- **Script :** `.github/scripts/termes_interdits.py`. Il reçoit le chemin de la liste en argument. Il affiche chaque occurrence avec son fichier ou son texte, sa ligne et le terme, et renvoie le code 1 s'il en trouve une. Ses tests lui passent des termes inventés, écrits dans un dossier temporaire. Aucun terme de la vraie liste n'apparaît dans un fichier suivi et non exclu.

### 10. Les scénarios et leur marque « en attente »

- **Emplacement :**
  - les scénarios, chemin protégé : `tests/scenarios/*.feature` ;
  - les définitions d'étapes, chemin protégé : `tests/scenarios/steps/` ;
  - la configuration commune, chemin protégé : `tests/scenarios/conftest.py` ;
  - le module qui charge les scénarios, chemin protégé : `tests/scenarios/test_scenarios.py`. Il est créé à M1 avec le premier scénario, parce que `pytest-bdd` échoue à la collecte (`NoScenariosFound`) quand il ne trouve aucun scénario, ce qui a été vérifié le 2026-11-01.
- **Marque « en attente » :**
  - `tests/scenarios/en_attente.txt` liste une entrée par ligne, sous la forme `<fichier>.feature::<titre du scénario>`, où le chemin est relatif à `tests/scenarios/`. Les lignes vides et celles qui commencent par `#` sont ignorées ;
  - `conftest.py` marque chaque entrée « doit échouer » (`pytest.mark.xfail(strict=True)`). Un scénario en attente qui réussit fait donc échouer la CI ;
  - une entrée qui ne correspond à aucun scénario fait échouer la session pytest ;
  - deux scénarios d'un même fichier ne peuvent pas avoir le même titre, et la session échoue si c'est le cas ;
  - une entrée qui désigne un plan de scénario (`Plan du Scénario`) met en attente tous ses exemples ;
  - une entrée ne peut être ajoutée que par une pull request qui modifie un `.feature` (Technical Plan, point 8, tâche `en-attente`).
- **À M0,** aucun scénario de jeu n'existe. Le mécanisme est vérifié par les tests de l'outillage : ils lancent une session pytest imbriquée (`pytester`), avec une copie de `conftest.py`, un scénario d'exemple en français et leur propre liste en attente.

### 11. Le squelette du projet

- `pyproject.toml` : le projet `fourx`, ses dépendances de développement (`ruff`, `mypy`, `pytest`, `pytest-bdd`, `import-linter`, `pre-commit`), sans dépendance d'exécution à M0. `hypothesis` arrive à M1.
- `ruff.toml`, `mypy.ini` (strict, sur `src/`, `tests/`, `.github/scripts/` et `.claude/hooks/`), `pytest.ini` et `.importlinter` (contrats d'imports du tableau des paquets du niveau 1, §1).
- `src/fourx/` : les sept sous-paquets, chacun avec un `__init__.py` vide, et `py.typed`.
- Les tests chargent les scripts de `.github/scripts/` et `.claude/hooks/` par `importlib`, à partir de leur chemin.
- `README.md` présente le projet en quelques lignes, renvoie à `CLAUDE.md` et aux documents, et indique « Tous droits réservés, aucune licence ».

### 12. Les essais du critère de sortie

Chaque essai se fait sur une branche `essai/…`. Les essais se jouent dans cet ordre : E1, E2, E3, E7, E4, E5, E6, E8, E9, E10, car E4 a besoin de la pull request verte de E7. Une seule pull request d'essai est ouverte à la fois. L'agent de code la ferme **sans fusion** (`gh api -X PATCH repos/EZPK/4X/pulls/<n> -f state=closed`), puis supprime sa branche. Le lien ou la sortie de chaque essai va dans le compte rendu de M0. Pour les commandes du propriétaire, le compte rendu cite le message de refus et son origine.

| Essai | Qui | Branche et type | Résultat attendu |
| :-- | :-- | :-- | :-- |
| E1. CI de `main` | agent de code | aucune | les tâches de `ci.yml` sont vertes sur le commit initial, y compris `gitleaks` sur tout l'historique d'un premier push |
| E2. Push direct sur `main` | **propriétaire** | `essai/push-direct` (un commit sans danger), aucune pull request | `! git push origin HEAD:main` est refusé par GitHub, avec un message qui cite la protection de branche |
| E3. Pull request rouge | agent de code ouvre, **propriétaire** tente | `essai/controle-rouge`, un fichier qui enfreint une règle de `ruff` ; pull request de fonctionnalité | la tâche `lint` échoue ; `! gh pr merge <n> --admin` est refusé par GitHub, avec un message qui cite les contrôles exigés |
| E4. Interdictions de Claude Code | agent de code | sur la pull request **verte** de l'essai E7 | refusés par Claude Code, chacun avec son message :<br>– `gh pr merge`, `--admin` et `--auto` ;<br>– `git push origin main` et `git push origin HEAD:main` ;<br>– `git push --force` vers `essai/chemin-protege` ;<br>– `git commit --no-verify` et `git commit -n` ;<br>– `gh api -X PUT …/protection` hors amorçage ;<br>– `gh repo edit` ;<br>– une édition de `.claude/settings.json` ;<br>– une seconde tentative de chacune des trois commandes d'amorçage |
| E5. Faux jeton GitHub | **propriétaire** | `essai/faux-secret-github` ; aucune pull request si le push est refusé | le hook pre-commit refuse le commit ; `! git commit --no-verify`, puis `! git push -u origin essai/faux-secret-github` : le blocage de GitHub refuse le push, sinon le compte rendu note « blocage non démontré » et la branche est supprimée |
| E6. Valeur d'essai du projet, tirée au hasard | **propriétaire** commit et push, agent de code ouvre la pull request | `essai/faux-secret-projet` ; pull request de fonctionnalité | le hook pre-commit refuse le commit ; après `! git commit --no-verify` et push, la tâche `gitleaks` de la pull request échoue sur la règle `FOURX_ESSAI_SECRET_` |
| E7. Chemin protégé | agent de code | `essai/chemin-protege`, une ligne ajoutée à `CLAUDE.md` ; pull request protégée | étiquette « fichiers protégés modifiés », bloc de liste en tête de la description et dans le résumé de la tâche ; après réécriture de la description par `gh api -X PATCH repos/EZPK/4X/pulls/<n> -F body=@<fichier>`, le bloc est rétabli |
| E8. Scénario en attente | agent de code | `essai/en-attente`, une entrée ajoutée à `en_attente.txt` ; pull request de fonctionnalité | la tâche `en-attente` échoue et cite l'entrée |
| E9. Terme interdit | agent de code | `essai/terme-interdit`, un terme de la liste dans un fichier de `src/` ; pull request de fonctionnalité | la tâche `termes-interdits` échoue et cite le fichier et la ligne |
| E10. Runners et jalons | agent de code | aucune | `gh api repos/EZPK/4X/actions/runners` renvoie `total_count: 0` ; `gh api repos/EZPK/4X/milestones` liste M0 à M6 |

Les faux secrets ne donnent accès à rien. Ils ne sont fusionnés dans aucune branche, mais restent lisibles dans la pull request fermée de l'essai E6, et dans la référence `refs/pull/…` que GitHub garde.

### 13. La procédure de reprise

Si la version de `garde.yml` sur `main` est cassée, ou si un nom de contrôle exigé ne correspond à aucune tâche, plus aucune fusion n'est possible. L'agent de code ne peut pas réparer, car l'exception de protection est fermée. La procédure, réservée au propriétaire, se fait par l'interface de GitHub :
1. retirer `enforce_admins` dans les réglages de la protection de `main` ;
2. fusionner la pull request qui répare ;
3. remettre `enforce_admins` ;
4. demander à l'agent de code de relire la protection (Technical Plan, point 4) et de consigner l'incident.

## Alternatives Considered

### Alternative A : `behave` pour les scénarios

*   **Avantages :** un lanceur conçu pour les scénarios, et des définitions d'étapes séparées du reste.
*   **Inconvénients :** un second lanceur en CI ; aucun moyen direct d'exiger qu'un scénario en attente échoue ; la mutation ne voit pas les scénarios.
*   **Raison du rejet :** la marque « en attente » doit faire échouer la CI si un scénario réussit par accident, ce que `pytest` fait directement (`xfail` strict). Retenu : `pytest-bdd`, choix du propriétaire.

### Alternative B : `pyright` ou `basedpyright` en mode strict

*   **Avantages :** plus rapide, mêmes diagnostics dans l'éditeur et en CI.
*   **Inconvénients :** règles plus nombreuses, donc probablement plus d'exceptions sur `msgspec` et `pytest-bdd` ; `pyright` passe par Node.js.
*   **Raison du rejet :** choix du propriétaire. mypy 2.4.1 a été vérifié sous Python 3.15 avec `msgspec`. Retenu : `mypy --strict`.

### Alternative C : une licence MIT ou AGPL-3.0

*   **Avantages :** les contributions et les clients tiers deviennent légalement possibles. L'AGPL-3.0 obligerait aussi un serveur modifié à publier ses modifications.
*   **Inconvénients :** il est difficile de revenir sur une licence ouverte une fois que d'autres ont contribué.
*   **Raison du rejet :** le propriétaire préfère garder tous les droits tant qu'il n'y a ni contributeur ni client tiers. Retenu : aucune licence. Le sujet reviendra (Future Improvements).

### Alternative D : Python 3.13 ou 3.14

*   **Avantages :** des versions plus éprouvées, avec moins de risque qu'un outil ou une bibliothèque d'entraînement ne suive pas.
*   **Inconvénients :** il faudra monter de version plus tôt.
*   **Raison du rejet :** choix du propriétaire. Les outils de M0 ont été vérifiés sous 3.15, la version déjà installée. Retenu : Python 3.15. Le risque qui reste porte sur le PC d'entraînement (Risks & Mitigations).

### Alternative E : le propriétaire lance lui-même les commandes de création et de réglage

*   **Avantages :** aucune exception dans le hook, et le propriétaire voit chaque réglage au moment où il est appliqué.
*   **Inconvénients :** trois commandes à lancer par le propriétaire, avec `!`.
*   **Raison du rejet :** le niveau 1 prévoit le push initial par l'agent de code, et le propriétaire a choisi d'étendre cette exception aux deux réglages (écart E1). Retenu : trois exceptions d'amorçage dans le hook, chacune refermée par l'état de GitHub et liée au contenu exact de son fichier.

### Alternative F : un ensemble de règles (ruleset) au lieu de la protection de branche classique

*   **Avantages :** le mécanisme plus récent de GitHub, avec une liste de contournement explicite.
*   **Inconvénients :** sa disponibilité sur un dépôt public gratuit n'est pas mieux vérifiée, et il est moins documenté pour les agents de code.
*   **Raison du rejet :** la protection classique couvre les besoins de M0 avec `enforce_admins`. Retenu : la protection classique. Le ruleset est la première solution de rechange (Technical Plan, point 4), appliquée par le propriétaire.

### Alternative G : l'action GitHub officielle de `gitleaks`

*   **Avantages :** moins de configuration.
*   **Inconvénients :** une dépendance de plus à épingler, avec des conditions d'utilisation qui varient selon le type de compte.
*   **Raison du rejet :** le binaire épinglé, dont la somme de contrôle est vérifiée, sert à la fois au hook pre-commit et à la CI. Retenu : le binaire épinglé.

### Alternative H : marquer les scénarios en attente par une étiquette dans le fichier `.feature`

*   **Avantages :** la marque est à côté du scénario, et c'est l'usage habituel de Gherkin.
*   **Inconvénients :** les fichiers `.feature` sont des chemins protégés. La pull request de fonctionnalité, qui ne doit toucher aucun chemin protégé, ne pourrait pas retirer la marque.
*   **Raison du rejet :** le circuit des pull requests du niveau 1 l'interdit. Retenu : une liste hors des chemins protégés, dont les ajouts sont contrôlés par la tâche `en-attente`.

### Alternative I : des paquets de premier niveau sans racine (`core`, `schema`…)

*   **Avantages :** des imports plus courts.
*   **Inconvénients :** des noms aussi génériques peuvent entrer en conflit avec d'autres paquets installés, comme `tools` ou `schema`.
*   **Raison du rejet :** un conflit de noms de paquets casse les imports de façon difficile à diagnostiquer. Retenu : `fourx.<paquet>`.

### Alternative J : l'action `actions/labeler` pour l'étiquetage

*   **Avantages :** une action maintenue par GitHub, qui étiquette selon des motifs de chemins sans récupérer le code de la branche.
*   **Inconvénients :** elle n'écrit pas le bloc de liste, ne lit pas `en_attente.txt` et ne remet pas le bloc après une réécriture de la description. Il faudrait quand même un script, avec deux mécanismes pour un seul contrôle.
*   **Raison du rejet :** un seul script testé est plus simple qu'une action et un script qui doivent rester d'accord. Retenu : `garde.py`.

### Alternative K : la configuration des outils dans `pyproject.toml`

*   **Avantages :** un seul fichier de configuration.
*   **Inconvénients :** ce fichier deviendrait un chemin protégé, et toute nouvelle dépendance toucherait un chemin protégé.
*   **Raison du rejet :** le niveau 1 interdit à la pull request de fonctionnalité de toucher un chemin protégé. Retenu : un fichier de configuration par outil.

--------------------------------------------------------------------------------

## Non-Functional Requirements

*   **Sécurité :**
    - Aucun secret dans le commit initial : `gitleaks git` est lancé sur ce commit juste avant le push, et le blocage des secrets de GitHub est déjà actif.
    - Le contrôle de garde n'exécute jamais le code d'une pull request.
    - Aucune expression `${{ github.event.* }}` dans un `run:` d'un workflow : les données passent par `$GITHUB_EVENT_PATH` ou par des variables d'environnement.
    - Les actions GitHub tierces sont épinglées par SHA de commit.
    - Le jeton des workflows est en lecture seule par défaut, et les Actions ne peuvent pas approuver de pull request.
    - Aucun runner auto-hébergé.
*   **Visibilité publique :** les essais restent visibles dans l'historique des pull requests fermées. Les faux secrets ne donnent accès à rien.
*   **Coût :** la CI tourne sur les runners hébergés par GitHub, gratuits pour un dépôt public.

## Risks & Mitigations

| Risque | Effet | Signal | Parade |
| :-- | :-- | :-- | :-- |
| L'application de la protection aux administrateurs est indisponible | Le critère « même par un administrateur » ne peut pas être atteint | `enforce_admins.enabled` faux après l'amorçage | Arrêt, puis décision du propriétaire, dans l'ordre : ruleset, abonnement, critère réduit (Technical Plan, point 4) |
| Le blocage des secrets au push est indisponible | Une barrière de moins | `secret_scanning_push_protection` absent | Hook pre-commit et `gitleaks` en CI restent en place ; le manque est consigné |
| Le hook plante ou ne sait pas analyser une commande | Une commande interdite passerait | Tests « erreur interne » et « analyse impossible » | Le hook refuse en cas de doute (code de sortie 2) ; le comportement des codes de sortie est vérifié contre la version installée (Open Questions) |
| Une variante de commande interdite n'est pas prévue | L'agent de code lance une commande interdite | Tests du hook | Recherche dans toute la chaîne brute, liste blanche pour les écritures GitHub, refus en cas de doute |
| Un script, ou un outil autre que Bash, échappe au hook | Une fusion, un push ou un réglage passe | Historique des fusions ; étiquette du garde | Règles `deny` sur Edit pour `/.claude/**` et `.git/hooks/**`, doublées dans les réglages utilisateur pour le dépôt principal et les worktrees liés rangés sous `.worktrees/` (ADR 0002) ; outils MCP d'écriture refusés s'ils apparaissent ; le reste est le risque accepté du niveau 1 |
| Une exception d'amorçage se rouvre (protection retirée) | L'agent de code pourrait réappliquer une protection | Lecture de la protection au Technical Plan, point 4 ; à partir de M1, un contrôle après fusion relit la protection chaque nuit | Les copies de référence du hook n'autorisent que le contenu prévu ; la suppression de `main` est interdite ; un retrait de la protection, par l'interface ou par un script, reste possible : risque accepté du niveau 1 |
| Une pull request affaiblit ses propres contrôles (`.github/` modifié) | Une pull request rouge paraît verte | Étiquette « fichiers protégés modifiés » | Lecture par le propriétaire et revue EGM obligatoire (niveau 1, §10) ; risque accepté |
| Un scénario est mis en attente pour cacher une régression | Une régression passe la CI | Tâche `en-attente` | Les ajouts ne sont permis que par une pull request qui modifie un `.feature` |
| Le garde de `main` est cassé, ou un nom de contrôle exigé est faux | Plus aucune fusion possible | Une pull request qui attend un contrôle qui ne vient jamais | Vérification des noms sur la première pull request d'essai ; procédure de reprise du propriétaire (Technical Plan, point 13) |
| Injection par le titre, la description ou un nom de fichier dans `garde.yml` | Exécution de code avec un jeton en écriture | Revue de `garde.yml` ; test avec un nom de fichier hostile | Aucune expression `${{ github.event.* }}` dans un `run:`, données lues par les scripts, noms échappés |
| Un nouveau clone n'a pas le hook pre-commit | Un secret n'est arrêté qu'en CI, après publication | Le hook Claude Code refuse `git commit` sans hook pre-commit | Installation par `uv run pre-commit install`, vérifiée par le hook |
| Un faux positif du contrôle des termes interdits | Une pull request légitime bloquée | CI rouge sur un mot courant | Recherche par mots entiers ; liste tenue par le propriétaire |
| Python 3.15 n'est pas pris en charge par une bibliothèque d'entraînement sur le PC d'entraînement | Blocage à M4 | Installation à M4 | Vérification dès le début de M4 ; changement de version de Python, décidé par le propriétaire, si nécessaire |
| Absence de licence sur un dépôt public | Les contributions extérieures et les clients tiers ne sont pas légalement possibles | Une demande de contribution | Choisir une licence avant toute ouverture (Future Improvements) |

## Additional Resources

*   [Document de niveau 1](./architecture-niveau-1.md) : §10 (garde-fous), §11 (critère de sortie de M0), Non-Functional Requirements.
*   Documentation GitHub consultée le 2026-10-31, sans confirmation de disponibilité sur un dépôt public gratuit :
    - [changelog sur l'option « Do not allow bypassing the above settings »](https://github.blog/changelog/2022-08-18-bypass-branch-protections-with-a-new-permission/) ;
    - [activation du blocage des secrets au push](https://docs.github.com/en/enterprise-cloud@latest/code-security/secret-scanning/enabling-secret-scanning-features/enabling-push-protection-for-your-repository).
*   [Version 8.30.1 de `gitleaks`](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1), publiée le 2026-03-21. Vérifié le 2026-11-01 : somme de contrôle du binaire Linux, analyse d'un index sans commit (`git --pre-commit --staged`), écart d'une valeur d'essai trop régulière par la configuration par défaut.

## Future Improvements

*   **Une licence,** avant toute contribution extérieure ou tout client tiers.
*   **Un ensemble de règles (ruleset)** à la place de la protection classique, si celle-ci ne suffit pas.
*   **Un compte GitHub séparé pour l'agent de code** (niveau 1, §10), si la confiance baisse.
*   **Un contrôle après fusion qui relit la protection de `main` chaque nuit,** à partir de M1.

--------------------------------------------------------------------------------

## Detailed Implementation Plan

Le plan s'exécute dans l'ordre des points. Chaque phase dit, en tête, l'état qu'elle laisse. Une étape marquée **propriétaire** est faite ou décidée par le propriétaire. Les commandes qu'il lance lui-même sont précédées de `!`, ou tapées dans un terminal hors de Claude Code si le point 2 l'impose.

**Notes de travail.** Tant que le compte rendu de M0 n'existe pas, l'agent de code note chaque résultat (versions, sommes de contrôle, sorties de commandes, réponses du propriétaire) dans `notes-m0.md`, à la racine du dossier. Ce fichier est ignoré par git (point 7). Il est recopié dans le compte rendu au point 47.

**Messages et descriptions.** Toute description de pull request est écrite dans un fichier et passée par `--body-file`. Tout message de commit qui cite une commande est passé par `git commit -F <fichier>`. Le hook cherche les motifs interdits dans toute la commande : un texte cité en ligne pourrait être refusé.

### Phase 0 : décision et vérifications préalables

À la fin de cette phase, le document est approuvé, les quatre points sur Claude Code des Open Questions sont vérifiés, les versions sont choisies, et `gitleaks` est installé. Aucun fichier du dépôt n'existe encore, à part `notes-m0.md` et les deux fichiers modifiés au point 1.

#### 1. Action — approbation (propriétaire)

*   **Type / Scope :** circuit des documents de niveau 2 (niveau 1, §10).
*   **Proposed Changes :** le propriétaire valide ce document. Sur sa demande explicite, l'agent de code :
    - remplace dans ce document `*   **Statut :** Proposed` par `*   **Statut :** Approved` ;
    - remplace dans `docs/feuille-de-route.md` la ligne M0, colonne statut, `à écrire` par `approuvé`.

    Sans cette étape, `CLAUDE.md` impose à l'agent de code de s'arrêter. Les deux fichiers entrent dans le commit initial.

#### 2. Action — vérifications sur Claude Code

*   **Type / Scope :** vérification contre la documentation de la version installée de Claude Code. Le numéro de version et la page consultée sont notés.
*   **Proposed Changes :** cinq points sont vérifiés et notés :
    1. la syntaxe des motifs `deny` pour Bash, Edit et Write ;
    2. un hook `PreToolUse` ne bloque que sur le code de sortie 2 ;
    3. la variable `CLAUDE_PROJECT_DIR` est fournie au hook ;
    4. un nouveau `.claude/settings.json` prend effet soit dans la session en cours, soit seulement dans une nouvelle session ;
    5. les commandes lancées avec `!` ne passent ni par les règles `deny` ni par le hook.

    **Si le point 4 donne « nouvelle session seulement »,** le propriétaire ferme la session après le point 35 et en ouvre une nouvelle, qui reprend au point 36. Attendu dans la nouvelle session : la commande du point 36 est refusée.

    **Si le point 5 donne « les commandes `!` passent par le hook »,** toutes les étapes **propriétaire** des phases 2 à 4 se font dans un terminal hors de Claude Code.

    **Si un point contredit ce document** (par exemple, le code de sortie qui bloque n'est pas 2), l'agent de code s'arrête et le signale au propriétaire.

#### 3. Action — versions épinglées

*   **Type / Scope :** règle du Technical Plan, point 1.
*   **Proposed Changes :** l'agent de code note dans `notes-m0.md` :
    - `gitleaks` 8.30.1, publiée le 2026-03-21, somme de contrôle SHA-256 de `gitleaks_8.30.1_linux_x64.tar.gz` : `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` (vérifiée le 2026-11-01) ;
    - pour `actions/checkout` et `astral-sh/setup-uv` : la dernière version publiée depuis au moins 14 jours, lue avec `gh api repos/actions/checkout/releases` et `gh api repos/astral-sh/setup-uv/releases`, puis le SHA de son commit, lu avec `gh api repos/<organisation>/<action>/commits/<tag> --jq .sha` (vérifié le 2026-11-01 sur `actions/checkout`) ;
    - la date d'exécution moins 14 jours, qui devient `exclude-newer` ;
    - la version de `uv` installée, publiée depuis au moins 14 jours (uv 0.11.16, publiée le 2026-05-21), qui donne `required-version = ">=0.11.16"`.

    **Si `uv lock` (point 12) échoue à cause de `exclude-newer`,** l'agent de code s'arrête et le signale au propriétaire. Il ne déplace ni la date ni une borne de lui-même.

#### 4. Action — installation locale de `gitleaks`

*   **Type / Scope :** outil local, hors du dépôt.
*   **Proposed Changes :**
    - `gh release download v8.30.1 -R gitleaks/gitleaks -p gitleaks_8.30.1_linux_x64.tar.gz -p gitleaks_8.30.1_checksums.txt` dans un dossier temporaire ;
    - vérifier que `sha256sum gitleaks_8.30.1_linux_x64.tar.gz` est égale à la somme du point 3 ;
    - extraire `gitleaks` dans `~/.local/bin/` ;
    - `gitleaks version` doit afficher `8.30.1`.

    Le `README.md` (point 14) reprend ces étapes pour un nouveau clone.

#### 5. `notes-m0.md` (Create)

*   **Type / Scope :** notes de travail, ignorées par git.
*   **Proposed Changes :** les résultats des points 2 à 4, puis de chaque étape.

### Phase 1 : préparation locale (aucun dépôt GitHub)

À la fin de cette phase, le dossier est un dépôt git local sur la branche `main`, avec un commit initial vérifié, et le hook Claude Code est actif. Rien n'est poussé.

#### 6. Action — `git init -b main`

*   **Type / Scope :** git.
*   **Proposed Changes :** `git init -b main`, parce que la configuration git de la machine crée une branche `master` par défaut. Ce point vient en premier, pour que le hook trouve un dépôt quand il sera actif.

#### 7. `.gitignore` (Create)

*   **Type / Scope :** configuration git, hors des chemins protégés.
*   **Proposed Changes :**
    - le contenu de `https://github.com/github/gitignore/blob/main/Python.gitignore`, avec le SHA du commit lu noté dans les notes ;
    - puis, sous un commentaire `# Projet 4X` :
      - partout : `.env*`, `!.env.example`, `*.key`, `*.pem`, `*.p12`, `*.parquet`, `*.duckdb`, `*.ckpt`, `*.pt` ;
      - pour Claude Code : `.claude/settings.local.json` ;
      - à la racine : `/notes-m0.md`, `/data/`, `/models/`, `/mlruns/`, `/mlartifacts/`, `/snapshots/`, `/logs/` et `/config/monde-en-ligne/`.

#### 8. `.env.example` (Create)

*   **Type / Scope :** documentation des variables d'environnement.
*   **Proposed Changes :** une seule ligne : `# Variables d'environnement du projet, sans valeur. Elles sont ajoutées par les jalons qui les créent (la première à M4 : adresse du serveur MLflow).`

#### 9. `.python-version` (Create)

*   **Type / Scope :** configuration de `uv`, chemin protégé.
*   **Proposed Changes :** `3.15`.

#### 10. `pyproject.toml` (Create)

*   **Type / Scope :** projet Python, hors des chemins protégés.
*   **Proposed Changes :**
    - `[project]` : `name = "fourx"`, `version = "0.0.0"`, `requires-python = ">=3.15,<3.16"`, sans dépendance ;
    - `[build-system]` : `requires = ["uv_build>=0.9,<0.12"]` et `build-backend = "uv_build"`. Vérifié le 2026-11-01 : avec ce système, `lint-imports` trouve `fourx` ;
    - `[dependency-groups]` : `dev = ["ruff>=0.17.1", "mypy>=2.4.0", "pytest>=9.1.1", "pytest-bdd>=9.0.0", "import-linter>=2.15", "pre-commit>=4.7.0"]`. Ce sont les versions que retient la règle des 14 jours au 2026-11-01, vérifiées le même jour sous Python 3.15 (scénario en français, `mypy --strict`, `ruff`) ;
    - `[tool.uv]` : `exclude-newer` (point 3) et `required-version = ">=0.11.16"`.

#### 11. `ruff.toml`, `mypy.ini`, `pytest.ini`, `.importlinter` (Create)

*   **Type / Scope :** configuration des outils, chemins protégés.
*   **Proposed Changes :**
    - **`ruff.toml` :** `target-version = "py315"` (ou la cible la plus récente que `ruff` accepte, notée dans les notes), `line-length = 100`, `[lint] select = ["E", "F", "W", "I", "B", "UP"]`. L'essai E3 enfreint la règle `F401` (import inutilisé).
    - **`mypy.ini` :** `[mypy]` avec `python_version = 3.15`, `strict = True`, `mypy_path = src`, `explicit_package_bases = True`, `files = src, tests, .github/scripts, .claude/hooks`.
    - **`pytest.ini` :** `[pytest]` avec `testpaths = tests`, `addopts = -p pytester --import-mode=importlib`, `bdd_features_base_dir = tests/scenarios`.
    - **`.importlinter` :** `root_package = fourx`, puis un contrat `forbidden` par paquet, qui interdit tout import hors de ceux permis par le niveau 1, §1 :
      - `schema` n'importe aucun autre paquet ;
      - `core` n'importe que `schema` ;
      - `policies` n'importe que `schema` ;
      - `server` n'importe que `core` et `schema` ;
      - `clients` n'importe que `schema` et `policies` ;
      - `training` n'importe que `core`, `schema` et `policies` ;
      - `tools` n'importe que `core`, `schema` et `server`.

#### 12. `uv.lock` (Create)

*   **Type / Scope :** verrou des dépendances, hors des chemins protégés.
*   **Proposed Changes :** généré par `uv lock`, jamais édité à la main.

#### 13. `src/fourx/` (Create)

*   **Type / Scope :** squelette des paquets.
*   **Proposed Changes :** `src/fourx/__init__.py` et `src/fourx/py.typed`, puis un `__init__.py` vide dans chacun des sous-paquets `schema`, `core`, `policies`, `server`, `clients`, `training`, `tools`.

#### 14. `README.md` (Create)

*   **Type / Scope :** présentation du dépôt.
*   **Proposed Changes :** dans cet ordre :
    - « Jeu de gestion spatiale en ASCII, avec des joueurs IA entraînés hors ligne. »
    - « Pour commencer : `CLAUDE.md`, `docs/feuille-de-route.md` et `docs/designs/architecture-niveau-1.md`. »
    - « Installation d'un clone : `uv sync --locked`, puis `uv run pre-commit install`. `gitleaks` 8.30.1 doit être dans le `PATH` : voir `docs/designs/niveau-2-m0-garde-fous.md`, plan détaillé, point 4. »
    - « Tous droits réservés. Aucune licence n'accorde de droit de réutilisation de ce code. »

#### 15. `.gitleaks.toml` (Create)

*   **Type / Scope :** règles de `gitleaks`, chemin protégé.
*   **Proposed Changes :** exactement :

    ```toml
    [extend]
    useDefault = true

    [[rules]]
    id = "fourx-essai-secret"
    description = "Valeur d'essai du projet (essai E6)"
    regex = '''FOURX_ESSAI_SECRET_[A-Z0-9]{32}'''
    ```

#### 16. `.pre-commit-config.yaml` (Create)

*   **Type / Scope :** hooks git locaux, chemin protégé.
*   **Proposed Changes :** exactement :

    ```yaml
    repos:
      - repo: local
        hooks:
          - id: gitleaks
            name: gitleaks (fichiers indexés)
            entry: gitleaks git --pre-commit --staged --redact --config .gitleaks.toml
            language: unsupported
            pass_filenames: false
    ```

    `language: unsupported` est le nom que donne `pre-commit` 4.7.0 aux commandes déjà installées (vérifié le 2026-11-01).

#### 17. `.github/scripts/motifs.py` et `.github/scripts/termes_interdits.py` (Create)

*   **Type / Scope :** scripts du contrôle des termes interdits, chemins protégés, bibliothèque standard seulement.
*   **Proposed Changes :**
    - **`motifs.py`** contient la seule traduction des motifs du projet (Technical Plan, point 8) : une fonction `correspond(chemin, motif)`. `garde.py` et `termes_interdits.py` l'importent par le chemin de leur propre dossier.
    - **`termes_interdits.py` — appel :** `python termes_interdits.py --liste docs/termes-interdits.md [--evenement FICHIER] [--fichiers FICHIER] [--messages FICHIER]`.
    - **Entrées :**
      - `--liste` : la liste des termes, sous `## Termes`, et des fichiers exclus, sous `## Fichiers exclus` ;
      - `--evenement` : le JSON de `$GITHUB_EVENT_PATH`. S'il contient une clé `pull_request`, le titre, la description et le nom de la branche en sont lus ; sinon, ils ne sont pas analysés ;
      - `--fichiers` : la liste des fichiers modifiés par la pull request, un par ligne. Elle ne sert qu'à l'exception ci-dessous ;
      - `--messages` : les messages de commit, séparés par un caractère NUL.
    - **Analyse :** toujours tous les fichiers suivis (`git ls-files`), sauf les fichiers exclus. Un fichier listé mais absent du disque est ignoré.
    - **Exception :** si `--fichiers` ne contient que `docs/termes-interdits.md`, le titre, la description et les messages ne sont pas analysés.
    - **Sortie :** une ligne par occurrence, `<fichier ou texte>:<ligne>: terme « <terme> »`. Code 1 s'il y en a au moins une, 0 sinon, 2 sur une erreur d'entrée.

#### 18. `.github/scripts/garde.py` (Create)

*   **Type / Scope :** logique du contrôle de garde, chemin protégé, bibliothèque standard seulement, aucun appel réseau.
*   **Proposed Changes :**
    - **Appel :** `python garde.py --chemins .github/chemins-proteges.txt --fichiers FICHIER --evenement FICHIER --sortie FICHIER`.
    - **Entrées :**
      - `--fichiers` : un objet JSON par ligne, `{"filename": …, "previous_filename": …}`, où `previous_filename` vaut `null` sans renommage ;
      - `--evenement` : le JSON de `$GITHUB_EVENT_PATH`, d'où sont lues la description (`null` vaut texte vide) et les étiquettes déjà présentes.
    - **Traitement :**
      - un fichier est protégé si `filename` **ou** `previous_filename` correspond à un motif (`motifs.py`) ;
      - le bloc est remplacé entre ses marqueurs, ou ajouté en tête, sans jamais être dupliqué. Sans chemin protégé, il est retiré ;
      - chaque nom de fichier est écrit en code en ligne. Un accent grave y est remplacé par `\u0060`, et un retour à la ligne par `\n`.
    - **Sortie :** un JSON `{"etiquette": "poser" | "retirer" | "rien", "description": "…", "resume": "…"}`. `retirer` n'est rendu que si l'étiquette est présente. Code 0, ou 2 sur une erreur d'entrée.

#### 19. `.github/scripts/en_attente.py` (Create)

*   **Type / Scope :** logique de la tâche `en-attente`, chemin protégé, bibliothèque standard seulement.
*   **Proposed Changes :**
    - **Appel :** `python en_attente.py --avant FICHIER --apres FICHIER --fichiers FICHIER`.
    - **Entrées :** les deux versions de `tests/scenarios/en_attente.txt`, et la liste des fichiers modifiés (même format qu'au point 18). Un fichier vide vaut une liste vide.
    - **Traitement :** les lignes sont normalisées (espaces retirés en début et en fin ; lignes vides et `#` ignorées).
    - **Sortie :** la liste des entrées ajoutées. Code 1 si des entrées sont ajoutées et qu'aucun fichier `.feature` n'est modifié, 0 sinon, 2 sur une erreur d'entrée.

#### 20. `.github/chemins-proteges.txt` (Create)

*   **Type / Scope :** liste des chemins protégés, chemin protégé (écart E6).
*   **Proposed Changes :** exactement la liste du Technical Plan, point 8.

#### 21. `.github/protection-main.json` (Create)

*   **Type / Scope :** corps de la requête de protection de `main`, chemin protégé.
*   **Proposed Changes :** exactement :

    ```json
    {
      "required_status_checks": {
        "strict": true,
        "contexts": ["lint", "typage", "gitleaks", "termes-interdits", "tests-outillage", "garde", "en-attente"]
      },
      "enforce_admins": true,
      "required_pull_request_reviews": {"required_approving_review_count": 0},
      "restrictions": null,
      "allow_force_pushes": false,
      "allow_deletions": false
    }
    ```

#### 22. `.github/securite-depot.json` (Create)

*   **Type / Scope :** corps de la requête qui active l'analyse des secrets et le blocage des secrets au push, chemin protégé.
*   **Proposed Changes :** exactement :

    ```json
    {"security_and_analysis": {"secret_scanning": {"status": "enabled"}, "secret_scanning_push_protection": {"status": "enabled"}}}
    ```

    Le jeton des workflows et l'approbation par les Actions sont lus au point 43. S'ils diffèrent, le propriétaire les corrige dans l'interface.

#### 23. `.github/workflows/ci.yml` (Create)

*   **Type / Scope :** CI, chemin protégé. Déclenchée sur `pull_request` et sur `push` vers `main`.
*   **Proposed Changes :**
    - `permissions: contents: read` ;
    - aucune tâche obligatoire n'a de clé `name:` ni de matrice : le nom du contrôle est l'identifiant de la tâche ;
    - aucune expression `${{ github.event.* }}` dans un `run:`. Les SHA sont passés par `env:` : `BASE` et `HEAD` (`github.event.pull_request.base.sha` et `.head.sha`), `BEFORE` et `AFTER` (`github.event.before` et `github.event.after`).
    - **Chaque tâche commence par les mêmes étapes :**
      - `actions/checkout`, épinglée par SHA, avec `persist-credentials: false`, et `fetch-depth: 0` pour `gitleaks` et `termes-interdits` ;
      - `astral-sh/setup-uv`, épinglée par SHA, avec `enable-cache: false` ;
      - `uv python install`, qui lit `.python-version` ;
      - `uv sync --locked`.
    - **L'intervalle de commits** vaut `$BASE...$HEAD` pour une pull request, et `$BEFORE..$AFTER` pour un push. Si `BEFORE` vaut le SHA nul (premier push), c'est tout l'historique de `$AFTER`.
    - **Puis, selon la tâche :**
      - `lint` : `uv run ruff check .` et `uv run ruff format --check .` ;
      - `typage` : `uv run mypy` ;
      - `gitleaks` : `curl -sSfLO https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz`, vérification par `sha256sum -c` avec la somme du point 3, extraction, puis `./gitleaks git --redact --config .gitleaks.toml --log-opts="<intervalle>" .` ;
      - `termes-interdits` :
        - pour une pull request : `git diff --name-only "$BASE...$HEAD"` dans un fichier, `git log --format=%B%x00 "$BASE...$HEAD"` dans un autre, puis le script du point 17 avec `--evenement "$GITHUB_EVENT_PATH" --fichiers … --messages …` ;
        - pour un push : `git log --format=%B%x00` sur l'intervalle du push, puis le script avec `--messages` seulement ;
      - `tests-outillage` : `uv run pytest` ;
      - `imports` (non obligatoire) : `uv run lint-imports`.

#### 24. `.github/workflows/garde.yml` (Create)

*   **Type / Scope :** contrôle de garde, chemin protégé. Déclenché sur `pull_request_target` (`opened`, `synchronize`, `reopened`, `edited`).
*   **Proposed Changes :**
    - `permissions: contents: read, pull-requests: write` ;
    - au niveau de chaque tâche, `env: GH_TOKEN: ${{ github.token }}`. Ce n'est pas une expression `github.event.*`, et `gh` en a besoin ;
    - `actions/checkout` sur la branche de base seulement, avec `persist-credentials: false` ;
    - Python installé par `astral-sh/setup-uv` (`enable-cache: false`) et `uv python install` ;
    - aucun cache, aucun artefact, aucune expression `${{ github.event.* }}` dans un `run:` ;
    - le numéro `N` et le SHA de tête `HEAD_SHA` de la pull request sont lus dans `$GITHUB_EVENT_PATH` par une commande `python -c`, jamais insérés dans le YAML.
    - **Tâche `garde` :**
      - `gh api --paginate "repos/EZPK/4X/pulls/$N/files" --jq '.[] | {filename, previous_filename}'` dans un fichier : un objet par ligne, ce qui reste valide sur plusieurs pages (vérifié le 2026-11-01) ;
      - `uv run --no-project python .github/scripts/garde.py …` ;
      - selon la sortie :
        - `poser` : `gh api -X POST "repos/EZPK/4X/issues/$N/labels" -f "labels[]=fichiers protégés modifiés"` ;
        - `retirer` : `gh api -X DELETE "repos/EZPK/4X/issues/$N/labels/<nom encodé>"`, où le nom est encodé par `urllib.parse.quote` ;
        - `rien` : aucun appel ;
      - puis la description par `gh api -X PATCH "repos/EZPK/4X/pulls/$N" -F body=@<fichier>`, et le résumé ajouté à `$GITHUB_STEP_SUMMARY`.
    - **Tâche `en-attente` :**
      - la version de `main` de `en_attente.txt` est lue dans le dossier récupéré ;
      - celle de la pull request est lue par `gh api -H "Accept: application/vnd.github.raw+json" "repos/EZPK/4X/contents/tests/scenarios/en_attente.txt?ref=$HEAD_SHA"`, sans récupérer le code de la branche. Seule une erreur « HTTP 404 » vaut un fichier vide ; toute autre erreur fait échouer la tâche (comportement de `gh` vérifié le 2026-11-01) ;
      - la liste des fichiers modifiés est lue comme pour `garde` ;
      - puis `uv run --no-project python .github/scripts/en_attente.py …`.

#### 25. `tests/scenarios/` (Create)

*   **Type / Scope :** emplacement des scénarios de M1 et des jalons suivants.
*   **Proposed Changes :**
    - `conftest.py` (chemin protégé) : le mécanisme du Technical Plan, point 10, qui ignore les lignes vides et `#` ;
    - `steps/__init__.py` (chemin protégé) : vide ;
    - `en_attente.txt` (hors des chemins protégés) : une seule ligne, `# Une entrée par ligne : <fichier>.feature::<titre du scénario>. Voir docs/designs/niveau-2-m0-garde-fous.md, Technical Plan, point 10.`

    `test_scenarios.py`, qui appelle `scenarios(".")`, **n'est pas créé à M0** : sans aucun `.feature`, `pytest-bdd` 9.0.1 lève `NoScenariosFound` et la collecte échoue (vérifié le 2026-11-01). Le niveau 2 de M1 le crée avec le premier scénario. Son chemin est déjà protégé (point 20).

#### 26. `tests/outillage/` (Create)

*   **Type / Scope :** tests de l'outillage de M0, chemin protégé.
*   **Proposed Changes :** les fichiers et leurs cas. Chaque catégorie et chaque variante a au moins un test.
    - `__init__.py` : vide.
    - `conftest.py` : `collect_ignore = ["exemple"]`, et une fixture qui charge un script par `importlib.util.spec_from_file_location` à partir de son chemin.
    - **`test_garde_commandes.py`** couvre :
      - chaque catégorie et chaque variante du Technical Plan, point 6 ;
      - l'erreur interne et l'analyse impossible ;
      - les trois commandes d'amorçage dans quatre états simulés : condition vraie, condition fausse, lecture en échec, fichier modifié ;
      - l'égalité des deux copies de référence avec `.github/securite-depot.json` et `.github/protection-main.json`, comparées après `json.load`.
    - **`test_termes_interdits.py`** couvre aussi : les exclusions lues sous `## Fichiers exclus`, un fichier listé mais absent du disque, un événement de push sans `pull_request`. Il couvre :
      - un terme trouvé, en majuscules et en minuscules ;
      - un terme inclus dans un mot plus long, qui n'est pas trouvé ;
      - un terme à tiret ;
      - la frontière à une lettre accentuée ;
      - un fichier exclu, ignoré ;
      - la portée : titre, description, messages et nom de branche ;
      - l'exception de la pull request qui ne modifie que la liste ;
      - les codes de sortie 0, 1 et 2.

      Tous les termes sont inventés et écrits dans `tmp_path`.
    - **`test_garde.py`** couvre :
      - la traduction des motifs (`**` à zéro, un et plusieurs dossiers ; `*` sans `/`) ;
      - les lignes vides et `#` de la liste ;
      - un chemin protégé modifié ou renommé (`previous_filename`) ;
      - un fichier ordinaire ;
      - la décision `poser`, `retirer` (étiquette présente dans l'événement) ou `rien` (étiquette absente) ;
      - plusieurs objets JSON par ligne, `previous_filename` à `null` ;
      - le retrait du bloc sans chemin protégé ;
      - le bloc remplacé et jamais dupliqué ;
      - une description vide ;
      - un nom de fichier hostile échappé ;
      - le contenu du résumé.
    - **`test_en_attente.py`** couvre :
      - un ajout sans `.feature`, refusé ;
      - un ajout avec `.feature`, permis ;
      - un retrait, permis ;
      - un commentaire modifié, qui n'est pas un ajout ;
      - un fichier absent dans l'une des versions.
    - **`test_conftest_scenarios.py`** fait tourner une session imbriquée (`pytester`). Il recopie `tests/scenarios/conftest.py` par `pytester.makeconftest(...)`, le scénario d'exemple de `exemple/`, et une liste en attente écrite par chaque test. Il couvre :
      - un scénario en attente qui échoue : la session imbriquée passe ;
      - un scénario en attente qui réussit : elle échoue ;
      - une entrée sans scénario : elle échoue ;
      - un titre en double : elle échoue ;
      - un plan de scénario en attente : tous ses exemples sont marqués ;
      - les lignes vides et `#`, ignorées.
    - **`test_workflows.py`** vérifie par lecture du texte :
      - qu'aucun `run:` de `.github/workflows/*.yml` ne contient `${{ github.event.` ;
      - que `garde.yml` ne récupère que la branche de base ;
      - qu'aucune tâche obligatoire n'a de `name:`.
    - **`exemple/exemple.feature` et `exemple/steps_exemple.py`** : un scénario en français (« Étant donné un compteur à 0, Quand on l'augmente de 1, Alors il vaut 1 ») et ses étapes, sans terme interdit.

#### 27. `docs/adr/0001-ecarts-m0.md` (Create) et `docs/adr/README.md` (Modify)

*   **Type / Scope :** ADR, chemin protégé.
*   **Proposed Changes :**
    - l'ADR suit le modèle de `docs/adr/README.md` :
      - numéro 0001, titre « Écarts du niveau 2 de M0 décidés le 2026-11-01 » ;
      - statut « proposée » ;
      - date 2026-11-01, décideur : le propriétaire ;
      - contexte, options et décision pour E4, E5 et E6 (Overview, tableau des écarts) ;
      - section du niveau 1 modifiée : §10 ;
    - l'index du `README.md` reçoit la ligne `0001 — Écarts du niveau 2 de M0 décidés le 2026-11-01 — proposée`.

#### 28. Action — acceptation de l'ADR (propriétaire)

*   **Type / Scope :** décision.
*   **Proposed Changes :** le propriétaire accepte l'ADR et change **lui-même** son statut en « acceptée », dans l'ADR et dans l'index de `docs/adr/README.md`, avec son éditeur. `CLAUDE.md` et le niveau 1 interdisent à l'agent de code d'écrire « acceptée ». Les points 31 et 32 n'ont lieu qu'après cette étape.

#### 29. `docs/glossaire.md` (Modify)

*   **Type / Scope :** glossaire, chemin protégé.
*   **Proposed Changes :**
    - **La phrase entière** « Chaque définition reprend ou résume la phrase du `[document de niveau 1](designs/architecture-niveau-1.md)` qui définit le terme. En cas d'écart, le document de niveau 1 fait foi. » devient :

      « Chaque définition reprend ou résume la phrase qui définit le terme, dans le `[document de niveau 1](designs/architecture-niveau-1.md)` ou dans le document de niveau 2 qui introduit le terme. En cas d'écart, le document de niveau 1 fait foi. »
    - **Dans la phrase de la colonne « identifiant du code »,** « l'identifiant fixé par le document de niveau 1 s'il en fixe un » devient « l'identifiant fixé par le document de niveau 1, ou par un document de niveau 2, s'il en fixe un ».
    - **Tableau « Projet » :**
      - « définition d'étapes » : l'identifiant devient `steps`, la définition « Code de test qui donne son sens à une phrase de scénario ; dossier `tests/scenarios/steps/`. », et un lien vers ce document (Technical Plan, point 1) **s'ajoute** au lien §10 ;
      - « scénario en attente » : la définition devient « Scénario dont le code n'existe pas encore, listé dans `tests/scenarios/en_attente.txt`. La CI exige qu'il échoue, et un ajout exige une pull request qui modifie un `.feature` (tâche `en-attente`). », et un lien vers le Technical Plan, point 10, **s'ajoute** au lien §10 ;
      - « contrôle obligatoire » : la définition devient « Tâche (job GitHub Actions) que la protection de `main` exige avant la fusion (required status check). », et un lien vers le Technical Plan, point 5, **s'ajoute** au lien §10 ;
      - nouvelles lignes, après « contrôle après fusion » :
        - `| tâche | — | Tâche (job) de GitHub Actions. | [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#5-la-protection-de-main-et-les-contrôles-obligatoires) |` ;
        - `| commande d'amorçage | — | L'une des trois commandes de création du dépôt de M0 (blocage des secrets, push initial, protection de main), que le hook n'autorise qu'une fois. | [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#3-lamorçage) |`.
    - **Tableau « Paquets »,** nouvelle première ligne : `| paquet racine | fourx | Paquet qui contient les paquets du niveau 1 ; l'identifiant core s'importe par fourx.core. | [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#1-décisions-prises-pour-m0) |`.

#### 30. `docs/termes-interdits.md` (Modify)

*   **Type / Scope :** liste des termes interdits, chemin protégé.
*   **Proposed Changes :**
    - **Le paragraphe entier** qui commence par « Format provisoire » devient exactement :

      > Format : les termes sont les lignes non vides comprises entre le titre « ## Termes » et le titre suivant, un par ligne, sans puce. Les fichiers exclus sont les lignes non vides sous le titre « ## Fichiers exclus », un motif par ligne, dans la syntaxe de `.github/chemins-proteges.txt`. La recherche ne tient pas compte de la casse et se fait par mots entiers : un terme n'est trouvé que s'il n'est ni précédé ni suivi d'une lettre (accents compris), d'un chiffre ou d'un souligné. Le tiret fait partie du terme. Une pull request qui ne modifie que ce fichier est dispensée de la vérification de sa description et de ses messages de commit.
    - **À la fin du fichier,** après les termes :

      ```text
      ## Fichiers exclus

      docs/termes-interdits.md
      docs/designs/mmo-gestion-spatiale-ia.md
      docs/revues/**
      docs/designs/architecture-niveau-1.md
      docs/designs/niveau-2-m0-garde-fous.md
      ```

#### 31. `CLAUDE.md` (Modify)

*   **Type / Scope :** règles de travail de l'agent de code, chemin protégé. Ce point précède le point 32, qui recopie son résultat.
*   **Proposed Changes :** chaque remplacement porte sur la **puce entière**, lien final compris. Le texte donné est la puce complète après remplacement.
    - **La puce entière** qui commence par « - Pousser vers `main`, forcer un push » devient :

      « - Pousser vers `main`, forcer un push, utiliser `--no-verify`. Seule exception : le push initial de `main`, l'une des trois commandes d'amorçage de M0, une seule fois et à la demande explicite du propriétaire (`docs/designs/niveau-2-m0-garde-fous.md`, Technical Plan, point 3) (`[§10](docs/designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia)`). »
    - **La puce entière** qui commence par « - Modifier la protection de branche » devient :

      « - Modifier la protection de branche, les ensembles de règles (rulesets) ou les réglages du dépôt. Seules exceptions : l'activation du blocage des secrets et l'application de la protection de `main`, deux des trois commandes d'amorçage de M0, chacune une seule fois et à la demande explicite du propriétaire (`docs/designs/niveau-2-m0-garde-fous.md`, Technical Plan, point 3) (`[§10](docs/designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia)`). »
    - **Juste après la puce entière** qui commence par « - le hook Claude Code et les règles `deny` de `.claude/settings.json` filtrent », ajouter la puce, au même retrait :

      « - les règles `deny` interdisent aussi à l'agent de code d'éditer `.claude/` et `.git/hooks/`. Pour modifier `.claude/`, le propriétaire lève la règle dans sa copie locale, fait ou demande la modification, remet la règle, puis la modification passe par une pull request protégée ; »
    - **La puce entière** qui commence par « - Chemins protégés : » devient :

      « - Chemins protégés : la liste qui fait foi est `.github/chemins-proteges.txt`. Elle comprend notamment `.github/`, `CLAUDE.md`, `.claude/`, `docs/designs/`, `docs/adr/`, `docs/glossaire.md`, `docs/feuille-de-route.md`, `docs/noms-valides.md`, `docs/termes-interdits.md`, `docs/revues/`, les scénarios et leurs définitions d'étapes, les tests de l'outillage et la configuration des outils. »
    - **La puce entière** qui commence par « - Le dépôt est créé au début de M0. » (trois phrases) devient :

      « - Le dépôt est créé au début de M0. Le commit initial contient tous les documents existants. L'agent de code applique les trois commandes d'amorçage de M0 (blocage des secrets, push initial, protection de `main`), chacune à la demande explicite du propriétaire et une seule fois. Ce sont les seules exceptions aux interdictions de pousser vers `main` et de modifier les réglages. »

#### 32. `docs/designs/architecture-niveau-1.md` (Modify)

*   **Type / Scope :** document de niveau 1, chemin protégé.
*   **Proposed Changes :** chaque remplacement porte sur la puce ou la ligne entière.
    - **§10, interdictions dans les permissions de Claude Code :**
      - « - pousser vers `main` ; » devient « - pousser vers `main` (filtré par le hook Claude Code, qui autorise une fois le push initial de M0) ; » (E2) ;
      - « - modifier la protection de branche, les ensembles de règles (rulesets) ou les réglages du dépôt. » devient « - modifier la protection de branche, les ensembles de règles (rulesets) ou les réglages du dépôt (filtré par le hook Claude Code, qui autorise une fois l'activation du blocage des secrets et l'application de la protection de M0) ; » (E1, E2) ;
      - ajouter la puce « - éditer `.claude/` et `.git/hooks/` (règles `Edit`, qui couvrent aussi les écritures par Bash). » (E2).
    - **§10, circuit des documents de niveau 2 :** la puce entière qui commence par « Le dépôt est créé au début de M0. » devient : « Le dépôt est créé au début de M0. Le **commit initial** contient tous les documents existants. L'agent de code applique les trois commandes d'amorçage de M0 (blocage des secrets, push initial, protection de `main`), chacune à la demande explicite du propriétaire et une seule fois ; ce sont les seules exceptions aux interdictions de pousser vers `main` et de modifier les réglages (voir `docs/designs/niveau-2-m0-garde-fous.md`, Technical Plan, point 3). » (E1).
    - **§10, chemins protégés :** la dernière puce, « - `docs/feuille-de-route.md`, `docs/noms-valides.md` et `docs/termes-interdits.md`. », devient « - `docs/feuille-de-route.md`, `docs/noms-valides.md` et `docs/termes-interdits.md` ; », suivie de « - `docs/revues/`. » et de la phrase « La liste qui fait foi est `.github/chemins-proteges.txt` (niveau 2 de M0). » (E4, E6).
    - **§10, contrôles obligatoires, ligne M0 :** à la fin de la seconde cellule de la ligne entière, on ajoute « , tests de l'outillage (`tests-outillage`), contrôle des ajouts à la liste des scénarios en attente (`en-attente`) » (E5).
    - **Niveau 1, plan détaillé, point 4 (`docs/termes-interdits.md`) :** « cette liste, `docs/designs/mmo-gestion-spatiale-ia.md` et `docs/revues/` » devient « cette liste, `docs/designs/mmo-gestion-spatiale-ia.md`, `docs/revues/`, `docs/designs/architecture-niveau-1.md` et `docs/designs/niveau-2-m0-garde-fous.md` » (E3).
    - **Niveau 1, plan détaillé, point 6 (`CLAUDE.md`) :** le texte imposé est remplacé par le contenu de `CLAUDE.md` issu du point 31, chaque ligne non vide précédée de `    > ` et chaque ligne vide remplacée par `    >`. Le script de comparaison déjà utilisé pendant la revue (texte extrait du bloc cité, comparé octet pour octet à `CLAUDE.md`) doit répondre « identique ».

#### 33. `.claude/hooks/garde_commandes.py` (Create)

*   **Type / Scope :** hook Claude Code, chemin protégé, bibliothèque standard seulement.
*   **Proposed Changes :** les règles du Technical Plan, point 6, et les copies de référence des deux fichiers JSON des points 21 et 22, comparées après `json.load`.

#### 34. Action — tests du hook avant son activation

*   **Type / Scope :** contrôle.
*   **Proposed Changes :**
    - `uv sync --locked` ;
    - `uv run pytest tests/outillage/test_garde_commandes.py` ;
    - `uv run ruff check .claude/hooks` ;
    - `uv run mypy .claude/hooks/garde_commandes.py` ;
    - puis `echo '{"tool_name":"Bash","tool_input":{"command":"gh pr merge 1"}}' | python3 -I .claude/hooks/garde_commandes.py ; echo $?`, qui doit afficher un message de refus et `2` ;
    - et la même chose avec `"command":"ls"`, qui doit afficher `0`.

    Tout doit être vert avant le point 35.

#### 35. `.claude/settings.json` (Create)

*   **Type / Scope :** permissions et hooks de Claude Code, chemin protégé. C'est le dernier fichier de `.claude/` écrit par l'agent de code.
*   **Proposed Changes :** les règles `deny` du Technical Plan, point 6, dans la syntaxe vérifiée au point 2, et le hook `PreToolUse` sur l'outil Bash, avec `"timeout": 30`, `"onFailure": "block"` et la commande `python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/garde_commandes.py"`.

    **Reprise si le hook est cassé :** le propriétaire renomme `.claude/settings.json` en `.claude/settings.json.hors-service` hors de Claude Code, l'agent de code corrige, puis le propriétaire le remet en place.

#### 36. Action — vérification du hook actif

*   **Type / Scope :** contrôle (agent de code ; dans une nouvelle session si le point 2 l'impose).
*   **Proposed Changes :** l'agent de code lance `git commit -n --allow-empty --dry-run -m test`, qui est sans effet dans tous les cas. Attendu : refus par le hook, avec le message qui cite le contournement du hook pre-commit. Le refus est noté.

#### 37. Action — commit initial

*   **Type / Scope :** git.
*   **Proposed Changes :** dans cet ordre :
    1. `uv sync --locked` ;
    2. `uv run pre-commit install` ;
    3. `git add -A` ;
    4. `git status --short`, comparé à la liste des fichiers des points 1, 7 à 33 et 35, plus `CLAUDE.md` et les fichiers de `docs/` déjà présents. `notes-m0.md` et `tests/scenarios/test_scenarios.py` ne doivent pas y figurer ;
    5. `git diff --cached`, relu ;
    6. `gitleaks git --pre-commit --staged --redact --config .gitleaks.toml .`, qui ne doit rien trouver ;
    7. `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run pytest`, `uv run lint-imports`, et `uv run python .github/scripts/termes_interdits.py --liste docs/termes-interdits.md` (qui analyse les fichiers indexés, puisque `git ls-files` les voit), tous verts ;
    8. `git commit -F <fichier>`, avec le message « M0 : documents et garde-fous initiaux ».

    Si un contrôle trouve quelque chose, l'agent de code s'arrête et le propriétaire décide. `garde` et `en-attente` ne tournent que sur une pull request : ils sont vérifiés à la phase 4.

### Phase 2 : création du dépôt et amorçage

À la fin de cette phase, le dépôt public existe, `main` est poussée et protégée, et les réglages sont lus. Chacun des points 38 à 41 demande une demande explicite du propriétaire.

38. **Agent de code, à la demande du propriétaire :** `gh repo create EZPK/4X --public --source .`.
39. **Agent de code, à la demande du propriétaire :** première commande d'amorçage, l'activation du blocage des secrets (Technical Plan, point 3).
40. **Agent de code, à la demande du propriétaire :** `gitleaks git --redact --config .gitleaks.toml .` sur le commit initial, puis la deuxième commande d'amorçage, le push initial.
41. **Agent de code, à la demande du propriétaire :** troisième commande d'amorçage, la protection de `main`.
42. **Agent de code :** `gh api -X POST repos/EZPK/4X/labels -f name="fichiers protégés modifiés" -f color=d93f0b -f description="Le contrôle de garde a trouvé un chemin protégé modifié"`.
43. **Agent de code :** lecture des réglages (Technical Plan, point 4), puis une seconde tentative de chacune des trois commandes d'amorçage, qui doit être refusée par le hook. Ces secondes tentatives sont des essais demandés explicitement par le propriétaire avec la phase 2 : l'agent de code les lance une par une et attend un refus. **Si un réglage manque ou diffère,** s'arrêter et le signaler au propriétaire.

### Phase 3 : jalons GitHub

44. **Agent de code :** sept commandes séparées, une par jalon, de M0 à M6. Pour M0 : `gh api -X POST repos/EZPK/4X/milestones -f title="M0" -f description="Critère de sortie et document de niveau 2 : voir docs/feuille-de-route.md, ligne M0."`, puis la même avec `M1`, et ainsi de suite.

### Phase 4 : essais du critère de sortie

**Autorisation des essais.** Les essais E4 et E9, et les commandes interdites qu'ils contiennent, sont demandés explicitement par le propriétaire au début de cette phase. L'agent de code lance chaque commande interdite une par une et attend un refus. Si une commande n'est pas refusée, il s'arrête et le signale au propriétaire. Le terme de l'essai E9 n'est écrit que dans un fichier de la branche `essai/terme-interdit`, jamais dans le titre, le nom de branche ou un message, et cette branche n'est jamais fusionnée.

45. **Propriétaire :** `! git commit -n --allow-empty --dry-run -m test`. Attendu : la commande s'exécute sans message du hook. Sinon, les étapes **propriétaire** suivantes se font dans un terminal hors de Claude Code (point 2).
46. **Agent de code et propriétaire :** les essais E1 à E10 du Technical Plan, point 12, dans l'ordre E1, E2, E3, E7, E4, E5, E6, E8, E9, E10. Sur la première pull request d'essai (E3), l'agent de code vérifie aussi que chaque contrôle exigé correspond à une tâche lancée (Technical Plan, point 4). Chaque pull request d'essai est fermée par `gh api -X PATCH repos/EZPK/4X/pulls/<n> -f state=closed`, puis sa branche est supprimée par `gh api -X DELETE repos/EZPK/4X/git/refs/heads/essai/<nom>`, et sa branche locale par `git branch -D essai/<nom>`.

### Phase 5 : compte rendu et livraison

#### 47. `docs/revues/2026-10-31-niveau-2-m0-garde-fous/compte-rendu-m0.md` (Create)

*   **Type / Scope :** compte rendu de M0, chemin protégé. L'agent de code le rédige à partir de `notes-m0.md` et l'ajoute par une pull request protégée.
*   **Proposed Changes :**
    - les résultats de la phase 0 ;
    - les versions, sommes de contrôle et SHA épinglés ;
    - les lectures des réglages GitHub ;
    - pour chaque essai : le lien ou la sortie, le message de refus et son origine ;
    - un tableau qui associe chaque objectif à un essai réussi ou à une décision consignée.

    Aucun faux secret n'y est recopié : les sorties de `gitleaks` sont produites avec `--redact`.

#### 48. `docs/feuille-de-route.md` (Modify)

*   **Type / Scope :** feuille de route, chemin protégé.
*   **Proposed Changes :** le propriétaire déclare M0 « livré ». Sur sa demande, par une pull request protégée, l'agent de code passe M0 de `approuvé` à `livré` et remplace « Jalon en cours : M0 » par « Jalon en cours : M1 ».

### Verification Plan

*   **Installation :** `uv sync --locked` sans erreur.
*   **Tests :** `uv run pytest`, tous verts.
*   **Analyse statique :**
    - `uv run ruff check .` et `uv run ruff format --check .` ;
    - `uv run mypy` ;
    - `uv run lint-imports` ;
    - `uv run python .github/scripts/termes_interdits.py --liste docs/termes-interdits.md` ;
    - `gitleaks dir --redact --config .gitleaks.toml .` sur tout le dossier, `notes-m0.md` compris, en plus de l'analyse de l'index faite au point 37.
*   **Couverture :** chaque cas listé au point 26 a son test.
*   **Essais réels :** E1 à E10, consignés dans le compte rendu de M0.
*   **Critère de sortie :** chaque élément de la ligne M0 du niveau 1, §11, et chaque objectif de ce document correspondent à un essai réussi ou à une décision consignée du compte rendu.
