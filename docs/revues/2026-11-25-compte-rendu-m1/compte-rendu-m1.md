# Compte rendu de M1 : noyau déterministe et tranche 0

*   **Document suivi :** `docs/designs/niveau-2-m1-noyau.md` (Approved, amendements 1 et 2 compris), plan détaillé, points 1 à 33.
*   **Date du compte rendu :** 2026-11-25. Les travaux de M1 vont du 2026-11-08 (approbation du document) au 2026-11-25.
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
- Les 12 contrôles sont exigés par la protection de `main`. Chacun des cinq essais E1 à E5 a fait rougir le contrôle visé, et la fusion, tentée en administrateur, a été refusée (objectif 8). Pour E3, le refus est déduit : son message n'a pas été vu.
- La tâche de nuit, lancée à la main, réussit : 6 canaris attrapés sur 6, mutation complète du noyau au-dessus du plancher, protection de `main` en place.

**Ce qui n'est pas encore démontré, ou pas entièrement.**
- **Le rejeu sur le PC d'entraînement** (objectif 2, « sur les deux machines ») : **reporté** par le propriétaire le 2026-11-25 ; le rejeu est fait sur le portable et en CI (section 5). C'est le seul élément du critère de sortie de M1 sans preuve complète, et, selon le document de M1, il empêche la livraison tant qu'il manque.
- **Le message de refus de GitHub pour l'essai E3** n'a pas été consigné (section 3).
- **Les objectifs 18 et 19** n'ont pas de verdict séparé du propriétaire, alors que le plan le prend comme preuve ; leurs tests sont verts (section 7).
- **L'essai en 256 couleurs** n'a pas été fait (section 7).

Le propriétaire décide si ces réserves empêchent de déclarer M1 livré (section 10).

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
| Palier 5 : compte rendu | 32, 32 bis | n° 48 à 52 (essais, fermées) et celle-ci | essais E1 à E5, ce compte rendu |

**Hors du plan.** La pull request n° 34 (soute de 2 000) a été fermée sans fusion : la soute est entrée par la n° 33. La n° 37 ajoute le `Makefile` (`make jouer`, version stable). Les n° 46 et 47 réécrivent `README.md`.

Les détails de chaque pull request (revue EGM, mesures, liens CI) sont dans sa description.

## 3. Les essais

### 3.1 Les contrôles obligatoires (point 32 bis)

Chaque pull request d'essai part de `main` (`7361aac`), applique le bug volontaire du canari correspondant (`.github/canaris/`), et a été fermée sans fusion par le propriétaire, branche supprimée. Le propriétaire a tenté chaque fusion par `! gh pr merge <n> --admin --squash`, une fois le contrôle visé rouge.

| Essai | Pull request | Contrôle visé : lien et message | Autres contrôles rouges | Refus de GitHub |
| :-- | :-- | :-- | :-- | :-- |
| E1. Nombre flottant dans `step` | [n° 48](https://github.com/EZPK/4X/pull/48) | [`tests`](https://github.com/EZPK/4X/actions/runs/45680098110/job/139438041980) : « src/fourx/core/step.py:456: nombre flottant » | `mutation` (`step.py` 98,1 % contre 98,4 % à la base) | « GraphQL: 2 of 12 required status checks are failing. (mergePullRequest) » |
| E2. Taille du monde par `hash()` | [n° 49](https://github.com/EZPK/4X/pull/49) | [`rejeu`](https://github.com/EZPK/4X/actions/runs/45682045025/job/139444836180), dès `PYTHONHASHSEED=0` : « le rejeu diverge de la référence : tick 1000 : systems, deposits, stations, ships » | `tests` (« world.py:32: usage de hash »), `lint` (ligne trop longue), `mutation` (un test du monde casse) | « GraphQL: 4 of 12 required status checks are failing. (mergePullRequest) » |
| E3. Portefeuille d'un autre acteur dans l'observation | [n° 50](https://github.com/EZPK/4X/pull/50) | [`proprietes`](https://github.com/EZPK/4X/actions/runs/45683109808/job/139448521061) : « test_visibilite_des_observations - AssertionError: assert 0 == 9 » | `tests` (`test_observation_d_un_acteur` et deux autres), `mutation` | **refus déduit, message non vu** : la commande a été lancée hors de la session ; `mergeStateStatus` = `BLOCKED` avant la tentative, et la pull request est fermée sans fusion |
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

**PC d'entraînement : reporté.** L'agent de code n'a pas accès à cette machine. Le propriétaire a reporté ce rejeu le 2026-11-25 (« c'est compliqué maintenant tout de suite »). Il lancera les mêmes commandes depuis la racine d'un clone, au commit livré, en commençant par `git rev-parse --short HEAD` ; l'agent de code ajoutera leur sortie ici, sans adresse ni identifiant de la machine.

**Conséquence pour la livraison.** Le document de M1 (Risks & Mitigations, ligne « Le PC d'entraînement est indisponible à la fin du jalon ») prévoit que « le jalon n'est pas livré tant que la sortie manque ». Livrer M1 sans elle s'écarterait du document approuvé, et demanderait une décision explicite du propriétaire, consignée par un amendement.

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
| Terminal | non consigné | foot, dans le multiplexeur herdr ; police JetBrainsMono Nerd Font, corps 8 ; `TERM` = `xterm-256color`, `COLORTERM` = `truecolor` ; au moins 120 × 36 (le jeu s'affichait), environ 160 colonnes d'après la capture ; essai en 256 couleurs non fait |
| Verdict sur la lisibilité (objectif 12) | **non atteint** : « l'écran est visible, mais l'interface est vraiment pas claire. L'information n'est pas hiérarchisée. » Suite : ADR 0006 et amendement 2 | **favorable** : « beaucoup mieux maintenant […] pour le moment, c'est pas mal » ; la carte en Braille est « nettement mieux » (objectif 17). Aucun verdict séparé sur les objectifs 18 et 19 |
| Autres retours | ASCII abandonné au profit d'un style rétro 8 bits | la route déjà parcourue ne doit plus être jaune (corrigé par les pull requests n° 38 et 41) ; il reste difficile de savoir où aller vendre |

**Validation de la boucle de jeu (objectif 11).**
- 2026-11-22, après la partie de l'écran unique : « considère que je valide la boucle de jeu actuelle, mais garde en tête qu'il va falloir l'étoffer ».
- 2026-11-25, en session, après la partie de l'écran rétro et la livraison du palier 4 : « oui je valide la boucle de jeu ».

La condition de l'amendement 1 (un cycle en accéléré, et au moins un saut complet à la période nominale) est remplie par la partie de l'écran rétro.

Le verdict sur l'écran rétro ne bloque pas la livraison de M1 (décision du propriétaire, 2026-11-22). Les besoins d'écran exprimés après la partie (informations sur les systèmes, onglets, inventaire de la soute, vente sélective) sont pour une prochaine conception.

## 8. Objectifs et critère de sortie

Liens : [`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592), [`rejeu`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162), [`proprietes`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518288), [`imports`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518406) et [`tests-outillage`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518438) du code livré.

| Objectif du document de M1 | Preuve | État | Réserve |
| :-- | :-- | :-- | :-- |
| 1. Le propriétaire joue la tranche 0 de bout en bout | scénario « Le propriétaire extrait ore_b, le ramène à la station qui le paie le mieux et le vend » ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) ; parties d'essai (section 7) | atteint | — |
| 2. Une partie se rejoue à l'identique | [`rejeu`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162) : deux `PYTHONHASHSEED`, divergence « aucune » ; scénario « Une partie jouée à travers le serveur se rejoue avec les mêmes empreintes à chaque tick, refus compris » ; E2 | atteint en CI et sur le portable ; **PC d'entraînement reporté** | 1 |
| 3. Un rejeu qui diverge est localisé | scénario « L'outil de divergence signale au tick 50, composant ledger, une partie dont le registre est modifié au tick 50 » ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) ; E2 localise au tick 1 000 et aux composants | atteint | — |
| 4. L'argent et les biens se conservent | `test_invariants_apres_chaque_tick` ([`proprietes`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518288)) ; vérification après chaque tick des scénarios du noyau ; canari `vente-sans-taxe-ecrite` attrapé (section 3.2) | atteint | — |
| 5. L'économie reste dans ses fourchettes sur 100 000 ticks | section 6.1 ; `test_fourchettes.py` ([`rejeu`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518162)) | atteint | — |
| 6. Tous les acteurs passent par la même porte | `test_visibilite_des_observations` ([`proprietes`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518288)) ; scénarios « Un ordre au nom d'un autre acteur est refusé par la réception », « Un ordre d'administration soumis par un client est refusé par la réception » et « On ne voit un autre vaisseau, et le stock d'un gisement, qu'à proximité » ; contrats « clients » et « policies » sans import de `core` ([`imports`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518406)) ; E3 | atteint | — |
| 7. Tout ce qui persiste ou circule porte un numéro de version | `tests/core/test_versions.py`, `tests/server/test_versions_journal.py` ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) ; le garde lit `RULES_REVISION` (`.github/scripts/garde.py`) | atteint | — |
| 8. Les contrôles de M1 deviennent obligatoires | protection de `main` relue (section 3.2) ; E1 à E5 ; run de nuit ; `test_canaris.py` ([`tests-outillage`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437518438)) | atteint | 2 |
| 9. L'indicateur avancé est mesuré | section 6.2 (local) | atteint | — |
| 10. Les identifiants du glossaire sont fixés | `grep -c "à fixer au niveau 2 de M1" docs/glossaire.md` → 0 ; Technical Plan, point 12 | atteint | — |
| 11. Le propriétaire valide la boucle de jeu | section 7 : validations du 2026-11-22 et du 2026-11-25 ; graine, paliers et saut à la période nominale relevés dans le dossier de partie | atteint | — |
| 12. Le propriétaire lit l'écran sans se perdre | section 7 : non à l'écran unique, favorable à l'écran rétro ; tests du pilote de Textual ([`tests`](https://github.com/EZPK/4X/actions/runs/45679948773/job/139437517592)) | verdict favorable consigné | 3 |
| 13. Le temps est une ressource, et les durées sont des règles | scénario « Les durées lues dans l'observation sont celles du jeu, sur les vrais réglages » | atteint | — |
| 14. Le joueur connaît les durées par l'observation seule | ADR 0003 ; `test_reglages_publics_et_aucun_autre` (`tests/core/test_observe.py`) ; scénarios « Les ticks restants d'un trajet annoncés par le modèle client sont ceux du jeu » et « … d'un minage … » | atteint | — |
| 15. L'univers s'accélère en mode développement | `test_rejeu_exact_d_une_partie_jouee_en_accelere` et `test_speed_jsonl_en_tete_periode_initiale_et_changements` (`tests/server/test_partie.py`) ; mesure de débordement (section 6.3) | atteint | — |
| 16. Le monde est plus grand, et sa taille vient de la graine | ADR 0004 ; `test_generation_sous_deux_pythonhashseed` (`tests/core/test_monde_version_empreintes.py`) ; `world.py` muté à 100 % | atteint | — |
| 17. La carte montre tous les systèmes à la fois | scénario « La disposition de la carte place chaque système une fois, dans le carré, sans recouvrement, et la même à chaque appel » ; section 6.3 ; verdict « nettement mieux » | verdict favorable consigné | 3 |
| 18. L'écran dit quoi faire ensuite | scénario « La prochaine étape suit un cycle joué : aller miner, miner, aller vendre, vendre » | **verdict non rendu** ; tests verts | 4 |
| 19. Les mécaniques sont expliquées dans le jeu | scénario « L'aide donne les durées lues dans l'observation » ; tests de l'aide | **verdict non rendu** ; tests verts | 4 |

| Élément du critère de sortie de M1 (niveau 1, §11) | Preuve | État |
| :-- | :-- | :-- |
| Le CUJ 1 passe | objectif 1 | atteint |
| Le CUJ 4 passe | objectif 3 | atteint |
| Sur 100 000 ticks, la masse monétaire, l'émission et la destruction par motif restent dans les fourchettes | objectif 5 | atteint |
| Le rejeu est identique sur les deux machines | objectif 2 ; section 5 | portable : atteint ; **PC d'entraînement reporté** |
| Le propriétaire valide la boucle de jeu | objectif 11 | atteint |

## 9. Écarts, réserves et incidents

1. **Rejeu sur le PC d'entraînement reporté** (section 5) par le propriétaire, le 2026-11-25. Tant qu'il manque, un élément du critère de sortie n'est prouvé que sur le portable et en CI, et le document de M1 prévoit que le jalon n'est pas livré (section 5).
2. **Message de refus de E3 non consigné.** Le blocage est montré par `mergeStateStatus` = `BLOCKED` et par les quatre autres essais, mais le message de GitHub n'a pas été vu. L'essai peut être refait à peu de frais : rouvrir une pull request avec le même bug, et tenter la fusion par une commande `!`.
3. **Essai en 256 couleurs non fait**, et taille du terminal non mesurée exactement (point 23 undecies).
4. **Objectifs 18 et 19 sans verdict séparé.** Le verdict favorable porte sur l'écran dans son ensemble ; le plan prend comme preuve un verdict sur chacun de ces objectifs.
5. **Le hook refuse `gh workflow run` et `gh pr close` à l'agent de code.** Le propriétaire a lancé la tâche de nuit et fermé les pull requests d'essai lui-même.
6. **Incident de la pull request n° 46 (`README.md`).** Elle a été fusionnée sur son premier commit, avant que GitHub n'ait pris en compte les deux suivants ; la pull request n° 47 a rétabli la version voulue. Depuis, l'agent de code vérifie que la tête de la pull request est son dernier commit avant de la dire prête.
7. **Point 27 corrigé au palier 4.** Ses deux calculs dataient d'avant la soute de 2 000 ; ils ont été refaits (10 800 ticks ; 900 000) dans la pull request n° 45.

## 10. Ce qui reste à faire

1. **Propriétaire :** lancer le rejeu sur le PC d'entraînement et transmettre sa sortie, que l'agent de code ajoute en section 5. M1 n'est pas livré tant que cette sortie manque (document de M1, Risks & Mitigations). Livrer sans elle demande une décision explicite du propriétaire qui s'écarte du document approuvé, consignée par un amendement.
2. **Propriétaire :** décider, pour chacune des réserves 2 à 4, si elle empêche de déclarer M1 livré, ou s'il faut la lever d'abord : refaire l'essai E3, essayer un terminal en 256 couleurs, rendre un verdict sur les objectifs 18 et 19.
3. **Propriétaire :** décider si M1 passe à `livré` (point 33). Sur sa demande, l'agent de code met alors à jour `docs/feuille-de-route.md` dans une pull request protégée : M1 `livré`, « Jalon en cours » : M2.
