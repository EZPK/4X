# Compte rendu de M1 : noyau déterministe et tranche 0

*   **Document suivi :** `docs/designs/niveau-2-m1-noyau.md` (Approved, amendements 1 et 2 compris), plan détaillé, points 1 à 33.
*   **Date du compte rendu :** 2026-11-25 ; complété le même jour pour les réserves 2 à 4, puis le 2026-11-26 pour le rejeu sur le PC d'entraînement (sections 5 et 9) et la décision du propriétaire sur l'objectif 18 (section 10). Les travaux de M1 vont du 2026-11-08 (approbation du document) au 2026-11-25.
*   **Rédigé par :** l'agent de code, à partir des pull requests, des contrôles CI, des dossiers de partie et des décisions du propriétaire prises en session ; corrigé après une revue EGM sans contexte (exactitude technique).
*   **Statut de M1 :** `approuvé` dans `docs/feuille-de-route.md`. Seul le propriétaire peut le déclarer `livré` (point 33).

**Conventions.**
- « Point N » renvoie au plan détaillé du document de M1 ; « Technical Plan, point N » à sa partie technique ; « objectif N » à sa liste d'objectifs.
- Une commande précédée de `!` est tapée par le propriétaire dans le prompt de Claude Code. Elle ne passe ni par l'agent de code, ni par le hook Claude Code.
- **CI du code livré :** le run [`45679948773`](https://github.com/EZPK/4X/actions/runs/45679948773) de `ci.yml`, déclenché par le push sur `main` au commit `7361aac` (fusion de la pull request n° 47). Le garde et la tâche `en-attente` ne tournent que sur les pull requests : pour eux, la preuve est le run [`45666609595`](https://github.com/EZPK/4X/actions/runs/45666609595) de la pull request n° 47, dont la seule différence avec sa base est `README.md`.
- Une mesure « locale » a été faite hors CI, sur le portable de développement ; elle ne vaut pas preuve au sens de `CLAUDE.md`, mais le document de M1 en demande la publication.
- La colonne « Réserve » de la section 8 renvoie aux points de la section 9.

## 1. Résultat en bref

**Ce qui marche.**
- Le propriétaire joue la tranche 0 de bout en bout dans le client rétro : il extrait, transporte et vend (objectif 1). Il a validé la boucle de jeu (objectif 11).
- La partie de référence (graine 1, 5 PNJ, 100 000 ticks) se rejoue avec les mêmes empreintes sous `PYTHONHASHSEED=0` et `1`, et l'outil de divergence localise un écart au tick et au composant près (objectifs 2 et 3).
- L'économie reste dans ses fourchettes sur les dix fenêtres de 10 000 ticks, et les trois invariants de conservation tiennent à chaque tick (objectifs 4 et 5).
- Les 12 contrôles sont exigés par la protection de `main`. Chacun des cinq essais E1 à E5 a fait rougir le contrôle visé, et la fusion, tentée en administrateur, a été refusée (objectif 8). L'essai E3 a été refait pour consigner le message de refus (section 3.1).
- Le propriétaire a rendu un verdict sur chacun des objectifs 17 à 19 : favorable sur la carte (17) et sur l'aide (19), **défavorable sur la prochaine étape (18)** (section 7). Ce verdict ne bloque pas la livraison (point 23 undecies). L'écran se lit avec un rendu forcé en 256 couleurs.
- La tâche de nuit, lancée à la main, réussit : 6 canaris attrapés sur 6, mutation complète du noyau au-dessus du plancher, protection de `main` en place.

**Ce qui n'est pas encore démontré, ou pas entièrement.**
- Rien, depuis le 2026-11-26. Le rejeu sur le PC d'entraînement est fait : ses fichiers d'empreintes de chaque tick sont identiques au bit près à ceux du portable (section 5).

Les réserves 1 à 4 de la première version de ce compte rendu sont levées (section 9). Le propriétaire a reporté la décision sur la suite du verdict défavorable sur l'objectif 18 (section 10).

## 2. Ce qui a été livré

| Palier ou volet | Points | Pull requests | Contenu |
| :-- | :-- | :-- | :-- |
| Palier 1 : décision et documents | 1 à 3 bis | n° 15 et 16 | document de niveau 2 et sa revue EGM, approbation, glossaire, chemins protégés |
| Palier 2 : outillage de M1 | 4 à 14 | n° 17 | mutation, nouvelles tâches de CI, garde |
| Volet A : noyau et formats | 15 à 19 | n° 18 et 19 | `schema`, `core` (`step`, `observe`, registre, générateur à clé), invariants |
| Volet B : serveur, client, PNJ | 20 à 23 | n° 20 à 22 | serveur en mémoire, journal, instantanés, client Textual, `scripted_miner` |
| Volet B bis : écran unique (amendement 1) | 23 bis à 23 sexies | n° 23 à 27 (ADR 0003 à 0005) | monde de 8 à 12 systèmes, durées, visibilité par proximité, mode développement |
| Volet B ter : écran rétro (amendement 2) | 23 septies à 23 undecies | n° 28 à 33, 35, 36, 38 à 41 (ADR 0006 et 0007) | palette 8 bits, carte par forces en Braille, prochaine étape, aide |
| Volet C : rejeu, divergence, économie | 24 à 28 bis | n° 42 à 44 | `tools` (rejeu, divergence, économie), partie de référence, fourchettes, `RULES_REVISION` = 1 |
| Palier 4 : contrôles obligatoires | 29 à 31 ter | n° 45 | suite canari, `nuit.yml`, 12 contrôles exigés, hook mis à jour |
| Palier 5 : compte rendu | 32, 32 bis | n° 48 à 52 et 55 (essais, fermées), n° 53, 54 et celle-ci | essais E1 à E5, ce compte rendu |

**Hors du plan.** La pull request n° 34 (soute de 2 000) a été fermée sans fusion : la soute est entrée par la n° 33. La n° 37 ajoute le `Makefile` (`make jouer`, version stable). Les n° 46 et 47 réécrivent `README.md`.

Les détails de chaque pull request (revue EGM, mesures, liens CI) sont dans sa description.

## 3. Les essais

### 3.1 Les contrôles obligatoires (point 32 bis)

Les pull requests d'essai n° 48 à 52 partent de `main` (`7361aac`). Chacune applique le bug volontaire du canari correspondant (`.github/canaris/`), et a été fermée sans fusion par le propriétaire, branche supprimée. Le propriétaire a tenté chaque fusion par `! gh pr merge <n> --admin --squash`, une fois le contrôle visé rouge.

L'essai E3 a été refait le 2026-11-25, parce que le message de refus de la première tentative n'avait pas été vu. La pull request n° 55 part de `main` au commit `73759f9`, dont le code est celui de `7361aac` (`git diff --stat 7361aac 73759f9` ne montre que ce compte rendu), et applique le même bug ; sa tête est le commit `2a900f4`, et `mergeStateStatus` valait `BLOCKED`. Le propriétaire a tenté la fusion par une commande `!` dans la session, où le message s'est affiché, puis a fermé la pull request sans fusion et supprimé la branche.

| Essai | Pull request | Contrôle visé : lien et message | Autres contrôles rouges | Refus de GitHub |
| :-- | :-- | :-- | :-- | :-- |
| E1. Nombre flottant dans `step` | [n° 48](https://github.com/EZPK/4X/pull/48) | [`tests`](https://github.com/EZPK/4X/actions/runs/45680098110/job/139438041980) : « src/fourx/core/step.py:456: nombre flottant » | `mutation` (`step.py` 98,1 % contre 98,4 % à la base) | « GraphQL: 2 of 12 required status checks are failing. (mergePullRequest) » |
| E2. Taille du monde par `hash()` | [n° 49](https://github.com/EZPK/4X/pull/49) | [`rejeu`](https://github.com/EZPK/4X/actions/runs/45682045025/job/139444836180), dès `PYTHONHASHSEED=0` : « le rejeu diverge de la référence : tick 1000 : systems, deposits, stations, ships » | `tests` (« world.py:32: usage de hash »), `lint` (ligne trop longue), `mutation` (un test du monde casse) | « GraphQL: 4 of 12 required status checks are failing. (mergePullRequest) » |
| E3. Portefeuille d'un autre acteur dans l'observation | [n° 50](https://github.com/EZPK/4X/pull/50) | [`proprietes`](https://github.com/EZPK/4X/actions/runs/45683109808/job/139448521061) : « test_visibilite_des_observations - AssertionError: assert 0 == 9 » | `tests` (`test_observation_d_un_acteur` et deux autres), `mutation` | message non vu : la commande a été lancée hors de la session ; essai refait (ligne suivante) |
| E3 refait | [n° 55](https://github.com/EZPK/4X/pull/55) | [`proprietes`](https://github.com/EZPK/4X/actions/runs/45696834071/job/139496325895) : « test_visibilite_des_observations - AssertionError: assert 0 == 9 » | [`tests`](https://github.com/EZPK/4X/actions/runs/45696834071/job/139496325806) (`test_observation_d_un_acteur` : « assert 0 == 135 », et les deux mêmes autres), [`mutation`](https://github.com/EZPK/4X/actions/runs/45696834071/job/139496325959) | « GraphQL: 3 of 12 required status checks are failing. (mergePullRequest) » |
| E4. `core` importe `server` | [n° 51](https://github.com/EZPK/4X/pull/51) | [`imports`](https://github.com/EZPK/4X/actions/runs/45683810794/job/139450979813) : « Contracts: 6 kept, 1 broken. fourx.core is not allowed to import fourx.server » | `tests` (contrôle statique du déterminisme) | « GraphQL: 2 of 12 required status checks are failing. (mergePullRequest) » |
| E5. Fonction non vérifiée dans `arith.py` | [n° 52](https://github.com/EZPK/4X/pull/52) | [`mutation`](https://github.com/EZPK/4X/actions/runs/45685558738/job/139457119299) : `arith.py` 92,3 % contre 100,0 % à la base, « score inférieur à la base » | aucun | « GraphQL: Required status check "mutation" is failing. (mergePullRequest) » |

**Lecture.** Chaque bug est attrapé par le contrôle visé. Plusieurs le sont aussi par d'autres contrôles : c'est sans conséquence sur l'essai, et montre que les contrôles se recouvrent en partie.

### 3.2 La suite canari, la tâche de nuit et la protection

- **La suite canari échoue quand un contrôle laisse passer son bug.** En local, sur `60c30f7`, la commande du contrôle `imports` remplacée par `true` : « core-importe-server → imports : code 0 — NON ATTRAPÉ (« fourx.server » absent de la sortie) », « 0 canaris attrapés sur 1 », code de sortie 1. En CI, `tests/outillage/test_canaris.py` vérifie aussi les cas attrapé et non attrapé, dans [`tests-outillage`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518438).
- **Lancement manuel de `nuit.yml`** par le propriétaire (`! gh workflow run nuit.yml --ref main`), run [`45686800721`](https://github.com/EZPK/4X/actions/runs/45686800721) sur `7361aac`, réussi :

  | Tâche | Résultat | Durée |
  | :-- | :-- | :-- |
  | [`canari`](https://github.com/EZPK/4X/actions/runs/45686800721/job/139461429823) | « 6 canaris attrapés sur 6 » | 5 min 55 s |
  | [`mutation-complete`](https://github.com/EZPK/4X/actions/runs/45686800721/job/139461430279) | tous les fichiers de `core` et `schema` au-dessus du plancher de 80 % (section 6.4) | 8 min 12 s |
  | [`protection`](https://github.com/EZPK/4X/actions/runs/45686800721/job/139461429955) | « Protection de main en place. » | 20 s |

- **Protection de `main`**, appliquée par le propriétaire après la fusion de la pull request n° 45 (`! gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json`), puis relue par l'agent de code avec `gh api repos/EZPK/4X/branches/main/protection` : 12 contrôles exigés (`lint`, `typage`, `gitleaks`, `termes-interdits`, `tests-outillage`, `garde`, `en-attente`, `tests`, `rejeu`, `proprietes`, `imports`, `mutation`), `strict` = `true`, `enforce_admins` = `true`, `allow_force_pushes` = `false`, `allow_deletions` = `false`.

### 3.3 L'essai de la veille (point 23 quater)

Fait le 2026-11-21 par l'agent de code sur le portable, partie à la période nominale (3 s), tick relevé à l'écran (pull request n° 26). La veille n'a duré qu'environ 15 s au lieu de cinq minutes (réveil précoce) :

| Moment | Tick affiché |
| :-- | --: |
| juste avant la veille | 18 |
| au réveil, 17 s plus tard | 20 |
| 6 s après le réveil | 21 |
| 26 s après le réveil | 28 |

Sans arrêt, le tick aurait été vers 23 ou 24 au réveil : l'univers s'est figé pendant la veille, puis a repris à un tick toutes les 3 s, sans rattraper les ticks manqués. Le propriétaire a jugé l'essai complet de cinq minutes inutile : le jeu tournera ensuite sur un serveur qui ne s'arrête pas.

## 4. CI du code livré

Run [`45679948773`](https://github.com/EZPK/4X/actions/runs/45679948773), push sur `main` au commit `7361aac`, tous en `success` :

| Tâche | Lien | Durée |
| :-- | :-- | :-- |
| `tests` (tests et scénarios) | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592) | 46 s |
| `rejeu` (deux `PYTHONHASHSEED`, divergence, `-m lent`) | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162) | 1 min 33 s |
| `proprietes` | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518288) | 24 s |
| `imports` | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518406) | 21 s |
| `tests-outillage` | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518438) | 21 s |
| `lint` | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518270) | 26 s |
| `typage` | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518294) | 25 s |
| `gitleaks` | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518169) | 18 s |
| `termes-interdits` | [job](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518273) | 24 s |
| `mutation` | sautée sur un push : elle ne tourne que sur les pull requests | — |
| `garde` (pull request n° 47) | [job](https://github.com/EZPK/4X/actions/runs/45666609595/job/139390344816) | 18 s |
| `en-attente` (pull request n° 47) | [job](https://github.com/EZPK/4X/actions/runs/45666609595/job/139390343849) | 9 s |

**Durée de la mutation sur une pull request** (elle ne mute que les fichiers modifiés, scénarios compris) :
- la plus longue, une pull request de scénarios, qui mute tout `core` : 11 min 53 s ([n° 42](https://github.com/EZPK/4X/actions/runs/45095695275/job/137434879654)) ;
- l'essai E4 : 6 min 52 s ; l'essai E1 (`step.py`) : 4 min 35 s ; la pull request n° 44 (`version.py`) : 2 min 23 s.

Aucune tâche n'approche le seuil de 30 minutes du point 28 bis.

**Scénarios en attente.** `tests/scenarios/en_attente.txt` ne contient plus aucune entrée sur `main` : tous les scénarios de `noyau.feature`, `partie.feature`, `ecrans.feature` et `rejeu.feature` passent dans `tests`.

## 5. Le rejeu sur les deux machines

**Portable de développement : fait.** Le 2026-11-25, par l'agent de code, depuis `main` au commit `f5d5073` (fusion de ce compte rendu, code identique à `7361aac`), sous Linux x86_64 avec Python 3.15.2. Sortie locale, qui ne vaut pas preuve au sens de `CLAUDE.md` ; la même tâche passe en CI (section 4).

Sortie réduite à la dernière ligne de chaque commande :

```text
$ git rev-parse --short HEAD
f5d5073
$ uv sync --locked
Checked 46 packages
$ PYTHONHASHSEED=0 uv run pytest -m rejeu
1 passed, 1055 deselected in 3.94s
$ PYTHONHASHSEED=1 uv run pytest -m rejeu
1 passed, 1055 deselected in 3.87s
$ uv run python -m fourx.tools.divergence runs/rejeu-0/fingerprints.jsonl runs/rejeu-1/fingerprints.jsonl
aucune divergence
```

Chaque passe compare, tous les 1 000 ticks, les empreintes du rejeu à celles de `tests/references/rules-1/reference.json`, et écrit les empreintes de chaque tick (100 000 lignes).

**PC d'entraînement : fait.** Le 2026-11-26, par l'agent de code, à la demande du propriétaire (écart, section 9, point 8), par SSH depuis le portable, dans un clone neuf du dépôt, sous Linux x86_64 (WSL2). Comme sur le portable, la sortie est locale et ne vaut pas preuve au sens de `CLAUDE.md`. Aucune adresse ni aucun identifiant de la machine n'entre dans le dépôt.

Préparation :
- `uv` mis à jour en 0.13.10, la version que la CI a prise le 2026-11-25 : `ci.yml` ne la fixe pas, et le projet exige 0.11.16 au moins ;
- Python 3.15.2 installé par `uv`, comme en CI. Le premier essai avait pris un Python 3.15.0b1 déjà présent sur la machine, sur lequel la construction de `pyyaml` (dépendance de `pre-commit`) plantait (SIGSEGV).

Sortie réduite à la dernière ligne de chaque commande :

```text
$ git rev-parse --short HEAD
3360680
$ uv sync --locked
Checked 46 packages in 43ms
$ uv run python --version
Python 3.15.2
$ PYTHONHASHSEED=0 uv run pytest -m rejeu
1 passed, 1055 deselected in 4.51s
$ PYTHONHASHSEED=1 uv run pytest -m rejeu
1 passed, 1055 deselected in 3.23s
$ uv run python -m fourx.tools.divergence runs/rejeu-0/fingerprints.jsonl runs/rejeu-1/fingerprints.jsonl
aucune divergence
```

Le code de `3360680` est celui de `7361aac` : `git diff --name-only 7361aac 3360680` ne montre que ce compte rendu.

**Comparaison des deux machines, tick par tick.** Au-delà des points de contrôle tous les 1 000 ticks, les fichiers d'empreintes de chaque tick (100 000 lignes) sont identiques au bit près sur les deux machines. `sha256sum runs/rejeu-0/fingerprints.jsonl runs/rejeu-1/fingerprints.jsonl` donne la même valeur pour les quatre fichiers, `0c59aec543c846c09e9818a39153f213de7495efb311722057555599778ea86d` : sur le PC d'entraînement, et sur le portable, relancé le 2026-11-26 (`uv` 0.11.16, Python 3.15.2) au commit `21478ca`, dont le code est celui de `3360680`. La sortie du portable : « 1 passed, 1055 deselected in 10.60s » pour `PYTHONHASHSEED=1`.

## 6. Économie, mesures et mutation

### 6.1 Fourchettes sur 100 000 ticks (objectif 5, point 27)

Relevés de l'outil de régénération sur la partie de référence (pull request n° 44), vérifiés en CI par `tests/economie/test_fourchettes.py` (tâche [`rejeu`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162), étape `-m lent`).

Bornes : N = 5 PNJ, p_max = 15, d_min = 0, C_min = 2 000 ticks, b' = 6 cycles par fenêtre ; émission `ORE_SALE` par fenêtre dans ]0 ; 900 000].

| Fenêtre (premier tick) | Émission | Destruction | Croissance | Masse en fin |
| --: | --: | --: | --: | --: |
| 1 | 462 000 | 46 200 | 415 800 | 415 800 |
| 10 001 | 461 880 | 46 193 | 415 687 | 831 487 |
| 20 001 | 450 000 | 45 000 | 405 000 | 1 236 487 |
| 30 001 | 390 000 | 39 000 | 351 000 | 1 587 487 |
| 40 001 | 300 000 | 30 000 | 270 000 | 1 857 487 |
| 50 001 | 570 000 | 57 000 | 513 000 | 2 370 487 |
| 60 001 | 475 260 | 47 530 | 427 730 | 2 798 217 |
| 70 001 | 450 000 | 45 000 | 405 000 | 3 203 217 |
| 80 001 | 390 000 | 39 000 | 351 000 | 3 554 217 |
| 90 001 | 300 000 | 30 000 | 270 000 | 3 824 217 |

- Chaque fenêtre compte au moins une vente, et son émission reste sous le plafond de 900 000 (au plus 570 000).
- La destruction est égale à la somme des taxes, et la croissance à l'émission moins la destruction.
- Gisements vidés : `deposit_4`, 4 fois (premier au tick 14 165) ; `deposit_6`, 6 fois (premier au tick 9 471). Un seul départage par tirage à clé : `deposit_6`, au tick 9 471.
- Taille de `tests/references/rules-1/` : 172 748 octets.

### 6.2 Indicateur avancé (objectif 9, Technical Plan, point 11)

Mesure locale, `FOURX_MESURE=1 uv run pytest -m mesure -s`, sur un monde de 12 systèmes et 30 PNJ, pendant 2 000 ticks (pull request n° 44) :

| Mesure | Ticks par seconde |
| :-- | --: |
| `step` seul | 9 699 |
| `observe` (30 observations par tick) | 424 |
| les deux | 406 |

Ces chiffres ne déclenchent rien (niveau 1, §2). Ils montrent que `observe`, appelée une fois par acteur, coûte bien plus que `step`.

### 6.3 Carte et écran (point 28 bis)

Mesures de la pull request n° 33 :
- **Disposition sur les graines 1 à 2 000** (test `lent` de la tâche `rejeu` ; 143 s en local) : aucun recouvrement ; au zoom 1, sur un canevas de 70 × 23 et sur un de 100 × 30, chaque case d'un système est dans la grille, sans case commune ni voisine avec un autre système ; le filet de sécurité déplace 45 systèmes au total ; croisements de liens : 0,76 par monde en moyenne, 7 au plus, et 52 % des mondes en ont au moins un.
- **Temps de rendu** (local, script hors du dépôt : vrai serveur, graine 1, un PNJ, 2 000 ticks, grille et peinture à chaque mise à jour d'une carte de 70 × 23 cases, la taille de la carte dans un terminal de 120 × 36) : moyenne 7,0 ms, maximum 71 ms, sous les seuils de 30 ms et de 100 ms. Le palier de vitesse de la mesure n'est pas noté dans la pull request.

Mesure de la pull request n° 27 (amendement 1), au palier ×100, sur la graine 1, pendant 20 000 ticks : débordement de « avancer jusqu'à la prochaine alerte » de 0 tick au plus ; files du propriétaire et des PNJ toujours vides ; aucun ordre de PNJ refusé.

### 6.4 Mutation complète du noyau

Tâche `mutation-complete` du run de nuit [`45686800721`](https://github.com/EZPK/4X/actions/runs/45686800721/job/139461430279), sur `7361aac` :

| Fichier | Score |
| :-- | --: |
| `core/arith.py`, `fingerprints.py`, `observe.py`, `snapshot.py`, `tunables.py`, `version.py`, `world.py` | 100 % |
| `core/step.py` | 98,4 % |
| `core/ledger.py` | 94,3 % |
| `core/keyed_random.py` | 91,4 % |
| `schema/events.py`, `visibility.py` | 100 % |
| `schema/orders.py` | 95,2 % |

Tous les fichiers dépassent le plancher de 80 %. Les fichiers sans mutant n'ont pas de score (Technical Plan, point 10) : `core/state.py`, et dans `schema` : `actors.py`, `ids.py`, `ledger.py`, `observation.py`, `protocol.py`, `results.py`, `types.py`. Ces scores sont ceux que la pull request n° 44 avait mesurés en local sur `8b3a5fd`.

## 7. Les parties d'essai et les décisions du propriétaire

La graine, les vitesses et les ticks viennent des dossiers de partie écrits par le jeu (`runs/<horodatage>/` : `snapshot.msgpack`, `speed.jsonl`, `events.jsonl`). L'agent de code a identifié la partie de chaque essai par son commit, son heure et la présence d'une vente du joueur humain. La durée réelle est estimée en multipliant chaque tick par la période en vigueur, sans compter les pauses.

| | Écran unique (point 23 sexies) | Écran rétro (point 23 undecies) |
| :-- | :-- | :-- |
| Partie | dossier `20261121-232115-914607` (2026-11-21, 23 h 21 UTC), commit `b24d06c` (fusion de la pull request n° 27) | dossier `20261122-182118-899706` (2026-11-22, 18 h 21 UTC), version stable `f25e557` (après les pull requests n° 33 et 37) |
| Graine | 1 172 393 351 | 1 |
| Premier cycle | minage au tick 1 173 dans le système d'une station, sans saut ; vente de 100 `ore_a` au tick 1 417 | quatre sauts, minage de 2 000 `ore_b` du tick 1 622 au tick 3 621, deux sauts, vente au tick 4 426 (paiement 24 000, taxe 2 400) |
| Vitesses jouées | ×1 (44 ticks), ×10 (2), ×100 (1 371) ; durée estimée 2 min 54 s | ×1 (1 980 ticks), ×10 (6), ×100 (2 440) ; durée estimée 100 min. Le propriétaire l'estimait à environ 1 h |
| Saut complet à la période nominale (3 s) | aucun | deux : ticks 807 à 1 206 et 1 207 à 1 606, 20 minutes chacun |
| Terminal | non consigné | foot, dans le multiplexeur herdr ; police JetBrainsMono Nerd Font, corps 8 ; `TERM` = `xterm-256color`, `COLORTERM` = `truecolor` ; au moins 120 × 36 (le jeu s'affichait), environ 160 colonnes d'après la capture. Rendu forcé en 256 couleurs le 2026-11-25 (voir après le tableau) : 212 × 57 |
| Verdict sur la lisibilité (objectif 12) | **non atteint** : « l'écran est visible, mais l'interface est vraiment pas claire. L'information n'est pas hiérarchisée. » Suite : ADR 0006 et amendement 2 | **favorable** : « beaucoup mieux maintenant […] pour le moment, c'est pas mal » ; la carte en Braille est « nettement mieux » (objectif 17). Verdicts sur les objectifs 18 et 19 rendus le 2026-11-25 (voir après le tableau) |
| Autres retours | ASCII abandonné au profit d'un style rétro 8 bits | la route déjà parcourue ne doit plus être jaune (corrigé par les pull requests n° 38 et 41) ; il reste difficile de savoir où aller vendre |

**Rendu forcé en 256 couleurs et verdicts sur les objectifs 18 et 19 (2026-11-25).**
- **Lancement.** Le propriétaire a lancé le jeu dans foot, sous herdr (police de la configuration de foot : JetBrainsMono Nerd Font, corps 8), avec `stty size && env -u COLORTERM TERM=xterm-256color TEXTUAL_COLOR_SYSTEM=256 uv run python -m fourx --graine 1 --dev`. Avec Rich 15.0.0 et Textual 8.2.8 (versions du lockfile), sans `COLORTERM` et avec `TERM` = `xterm-256color`, la console détecte `256` ; Textual lui passe `TEXTUAL_COLOR_SYSTEM`. foot reste un terminal truecolor : c'est la sortie du jeu qui est forcée en 256 couleurs, pas le terminal qui est limité. L'agent de code a relu l'environnement des deux processus du jeu encore ouverts, sur trois lancements (le premier était fermé) : `TERM=xterm-256color`, `TEXTUAL_COLOR_SYSTEM=256`, pas de `COLORTERM`.
- **Taille du terminal.** `stty size`, tapé par le propriétaire dans la même fenêtre : « 57 212 » (lignes, colonnes), soit 212 colonnes × 57 lignes.
- **Parties.** Dossiers `20261125-203910-477253`, `20261125-203931-554780` et `20261125-204207-081798`, graine 1, période de 3 s sans changement de vitesse. Ce sont des parties courtes, pour regarder l'écran ; aucun cycle complet n'y est consigné. Le cycle complet de l'écran rétro est celui du 2026-11-22.
- **Rendu forcé en 256 couleurs :** « Bien lisible ».
- **Objectif 19 (l'aide explique les mécaniques) : favorable.** « la touche H fonctionne bien » ; à la question « l'aide explique-t-elle les mécaniques ? » : « oui ».
- **Objectif 18 (l'écran dit quoi faire ensuite) : défavorable.** « Non, le cadre, prochaine étape ne m'a pas trop aidé. Déjà, il parle beaucoup trop de tics, etc. Ça n'a pas trop d'intérêt pour le joueur. Ça, c'est plus des mécaniques internes et pour le debug. […] En plus, c'est pas très bien mis en forme. » Sur les messages en haut de l'écran : « il y a des informations qui apparaissent pour valider ou non des choses, mais c'est pas trop mis en avance, on voit pas trop que c'est là que ça se passe ». Sur le principe : « la prochaine étape, ça sera plutôt au joueur à la déterminer et pas tellement à lui suggérer. Après, il doit pouvoir suivre ce qu'il est en train de faire, là où il en est dans la tâche qu'il cherche à accomplir ».

**Validation de la boucle de jeu (objectif 11).**
- 2026-11-22, après la partie de l'écran unique : « considère que je valide la boucle de jeu actuelle, mais garde en tête qu'il va falloir l'étoffer ».
- 2026-11-25, en session, après la partie de l'écran rétro et la livraison du palier 4 : « oui je valide la boucle de jeu ».

La condition de l'amendement 1 (un cycle en accéléré, et au moins un saut complet à la période nominale) est remplie par la partie de l'écran rétro.

Le verdict sur l'écran rétro ne bloque pas la livraison de M1 (décision du propriétaire, 2026-11-22). Les besoins d'écran exprimés après la partie (informations sur les systèmes, onglets, inventaire de la soute, vente sélective) sont pour une prochaine conception. S'y ajoutent ceux du 2026-11-25 : durées présentées autrement qu'en ticks, messages de validation et de refus mis en avant, et suivi de la tâche en cours à la place d'une étape suggérée.

## 8. Objectifs et critère de sortie

Liens : [`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592), [`rejeu`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162), [`proprietes`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518288), [`imports`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518406) et [`tests-outillage`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518438) du code livré.

| Objectif du document de M1 | Preuve | État | Réserve |
| :-- | :-- | :-- | :-- |
| 1. Le propriétaire joue la tranche 0 de bout en bout | scénario « Le propriétaire extrait ore_b, le ramène à la station qui le paie le mieux et le vend » ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) ; parties d'essai (section 7) | atteint | — |
| 2. Une partie se rejoue à l'identique | [`rejeu`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162) : deux `PYTHONHASHSEED`, divergence « aucune » ; scénario « Une partie jouée à travers le serveur se rejoue avec les mêmes empreintes à chaque tick, refus compris » ; E2 | atteint en CI, sur le portable et sur le PC d'entraînement | — |
| 3. Un rejeu qui diverge est localisé | scénario « L'outil de divergence signale au tick 50, composant ledger, une partie dont le registre est modifié au tick 50 » ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) ; E2 localise au tick 1 000 et aux composants | atteint | — |
| 4. L'argent et les biens se conservent | `test_invariants_apres_chaque_tick` ([`proprietes`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518288)) ; vérification après chaque tick des scénarios du noyau ; canari `vente-sans-taxe-ecrite` attrapé (section 3.2) | atteint | — |
| 5. L'économie reste dans ses fourchettes sur 100 000 ticks | section 6.1 ; `test_fourchettes.py` ([`rejeu`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162)) | atteint | — |
| 6. Tous les acteurs passent par la même porte | `test_visibilite_des_observations` ([`proprietes`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518288)) ; scénarios « Un ordre au nom d'un autre acteur est refusé par la réception », « Un ordre d'administration soumis par un client est refusé par la réception » et « On ne voit un autre vaisseau, et le stock d'un gisement, qu'à proximité » ; contrats « clients » et « policies » sans import de `core` ([`imports`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518406)) ; E3 | atteint | — |
| 7. Tout ce qui persiste ou circule porte un numéro de version | `tests/core/test_versions.py`, `tests/server/test_versions_journal.py` ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) ; le garde lit `RULES_REVISION` (`.github/scripts/garde.py`) | atteint | — |
| 8. Les contrôles de M1 deviennent obligatoires | protection de `main` relue (section 3.2) ; E1 à E5 ; run de nuit ; `test_canaris.py` ([`tests-outillage`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518438)) | atteint | — |
| 9. L'indicateur avancé est mesuré | section 6.2 (local) | atteint | — |
| 10. Les identifiants du glossaire sont fixés | `grep -c "à fixer au niveau 2 de M1" docs/glossaire.md` → 0 ; Technical Plan, point 12 | atteint | — |
| 11. Le propriétaire valide la boucle de jeu | section 7 : validations du 2026-11-22 et du 2026-11-25 ; graine, paliers et saut à la période nominale relevés dans le dossier de partie | atteint | — |
| 12. Le propriétaire lit l'écran sans se perdre | section 7 : non à l'écran unique, favorable à l'écran rétro ; tests du pilote de Textual ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) ; retour du 2026-11-25 : les messages de validation et de refus, en haut de l'écran, sont peu mis en avant (section 7) | verdict favorable consigné (2026-11-22) | — |
| 13. Le temps est une ressource, et les durées sont des règles | scénario « Les durées lues dans l'observation sont celles du jeu, sur les vrais réglages » | atteint | — |
| 14. Le joueur connaît les durées par l'observation seule | ADR 0003 ; `test_reglages_publics_et_aucun_autre` (`tests/core/test_observe.py`) ; scénarios « Les ticks restants d'un trajet annoncés par le modèle client sont ceux du jeu » et « … d'un minage … » | atteint | — |
| 15. L'univers s'accélère en mode développement | `test_rejeu_exact_d_une_partie_jouee_en_accelere` et `test_speed_jsonl_en_tete_periode_initiale_et_changements` (`tests/server/test_partie.py`) ; mesure de débordement (section 6.3) | atteint | — |
| 16. Le monde est plus grand, et sa taille vient de la graine | ADR 0004 ; `test_generation_sous_deux_pythonhashseed` (`tests/core/test_monde_version_empreintes.py`) ; `world.py` muté à 100 % | atteint | — |
| 17. La carte montre tous les systèmes à la fois | scénario « La disposition de la carte place chaque système une fois, dans le carré, sans recouvrement, et la même à chaque appel » ; section 6.3 ; verdict « nettement mieux » | verdict favorable consigné | — |
| 18. L'écran dit quoi faire ensuite | scénario « La prochaine étape suit un cycle joué : aller miner, miner, aller vendre, vendre » ; verdict du propriétaire (section 7) | **verdict défavorable consigné** ; tests verts | — |
| 19. Les mécaniques sont expliquées dans le jeu | scénario « L'aide donne les durées lues dans l'observation » ; tests de l'aide ; verdict du propriétaire (section 7) | verdict favorable consigné | — |

| Élément du critère de sortie de M1 (niveau 1, §11) | Preuve | État |
| :-- | :-- | :-- |
| Le CUJ 1 passe | objectif 1 | atteint |
| Le CUJ 4 passe | objectif 3 | atteint |
| Sur 100 000 ticks, la masse monétaire, l'émission et la destruction par motif restent dans les fourchettes | objectif 5 | atteint |
| Le rejeu est identique sur les deux machines | objectif 2 ; section 5 | atteint : portable et PC d'entraînement, empreintes identiques au bit près |
| Le propriétaire valide la boucle de jeu | objectif 11 | atteint |

## 9. Écarts, réserves et incidents

1. **Rejeu sur le PC d'entraînement reporté : levée le 2026-11-26.** Le rejeu est fait sur le PC d'entraînement, sans divergence, et ses empreintes sont identiques à celles du portable (section 5).
2. **Message de refus de E3 non consigné : levée le 2026-11-25.** L'essai a été refait (pull request n° 55) et le message est consigné (section 3.1).
3. **Essai en 256 couleurs non fait, et taille du terminal non mesurée exactement : levée pour l'essai du 2026-11-25.** Rendu forcé en 256 couleurs « Bien lisible », sur 212 × 57, police consignée (section 7). La taille du terminal de la partie du 2026-11-22 (cycle complet, verdicts sur les objectifs 12 et 17) reste approximative : environ 160 colonnes.
4. **Objectifs 18 et 19 sans verdict séparé : levée le 2026-11-25.** Verdict favorable sur l'objectif 19, défavorable sur l'objectif 18 (section 7). Le plan prend comme preuve le verdict consigné, favorable ou non (Verification Plan, critère de sortie).
5. **Le hook refuse `gh workflow run` et `gh pr close` à l'agent de code.** Le propriétaire a lancé la tâche de nuit et fermé les pull requests d'essai lui-même.
6. **Incident de la pull request n° 46 (`README.md`).** Elle a été fusionnée sur son premier commit, avant que GitHub n'ait pris en compte les deux suivants ; la pull request n° 47 a rétabli la version voulue. Depuis, l'agent de code vérifie que la tête de la pull request est son dernier commit avant de la dire prête.
7. **Point 27 corrigé au palier 4.** Ses deux calculs dataient d'avant la soute de 2 000 ; ils ont été refaits (10 800 ticks ; 900 000) dans la pull request n° 45.
8. **Rejeu sur le PC d'entraînement lancé par l'agent de code.** Le document de M1 prévoit que le propriétaire le lance, parce que seul le propriétaire avait accès à cette machine (Verification Plan). Les 2026-11-25 et 2026-11-26, le propriétaire a fait installer un accès SSH au PC, puis a demandé à l'agent de code d'agir : « prends controle du PC, demande moi les ID si nécssaire ». L'agent de code a lancé les commandes prévues, sans autre changement que la préparation décrite en section 5. L'adresse et les identifiants de la machine restent hors du dépôt.

## 10. Ce qui reste à faire

1. **Rejeu sur le PC d'entraînement : fait** le 2026-11-26 (section 5).
2. **Suite du verdict défavorable sur l'objectif 18 : décision reportée par le propriétaire.** Le point 23 undecies prévoit qu'au plus une pull request de fonctionnalité de correction suive dans M1 ; au-delà, la condition de révision de l'ADR 0006 s'applique. Les raisons données (durées en ticks, mise en forme, principe d'une étape suggérée, messages peu mis en avant) ne sont pas propres au terminal, et le rendu forcé en 256 couleurs a été jugé « Bien lisible » : selon cette condition, c'est la conception de l'écran (document de M1, Technical Plan, point 7 ter) qui est reprise, sans réexaminer l'ADR 0006. Les retours du propriétaire remettent en cause le principe d'une étape suggérée, au profit du suivi de la tâche en cours : c'est un changement de conception, plus qu'une correction. Le verdict ne bloque pas la livraison de M1. **Le propriétaire, 2026-11-26 :** « Pour le point 2, on décidera plus tard quand on fera le cadre modulaire. » *Lecture de l'agent de code, non confirmée par le propriétaire :* « le cadre modulaire » désigne la proposition de rendre les cadres du client interchangeables, faite en session et pas encore écrite dans le dépôt ; sa conception reprendrait le point 7 ter ; si M1 est déclaré livré avant cette décision, le point 23 undecies ne permet plus de pull request de correction dans M1.
3. **Propriétaire :** décider si M1 passe à `livré` (point 33). Sur sa demande, l'agent de code met alors à jour `docs/feuille-de-route.md` dans une pull request protégée : M1 `livré`, « Jalon en cours » : M2.
