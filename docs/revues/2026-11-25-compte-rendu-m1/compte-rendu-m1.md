# Compte rendu de M1 : noyau déterministe et tranche 0

*   **Document suivi :** `docs/designs/niveau-2-m1-noyau.md` (Approved, amendements 1 et 2 compris), plan détaillé, points 1 à 33.
*   **Date du compte rendu :** 2026-11-25. Les travaux de M1 vont du 2026-11-08 (approbation du document) au 2026-11-25.
*   **Rédigé par :** l'agent de code, à partir des pull requests, des contrôles CI et des décisions du propriétaire prises en session.
*   **Statut de M1 :** `approuvé` dans `docs/feuille-de-route.md`. Seul le propriétaire peut le déclarer `livré` (point 33).

**Conventions.**
- « Point N » renvoie au plan détaillé du document de M1 ; « Technical Plan, point N » à sa partie technique ; « objectif N » à sa liste d'objectifs.
- Une commande précédée de `!` est tapée par le propriétaire dans le prompt de Claude Code. Elle ne passe ni par l'agent de code, ni par le hook Claude Code.
- **Preuve CI de référence.** La pull request n° 47 ne modifie que `README.md` par rapport à `main` (`7361aac`) ; son run CI `45666609367`, sur `01062e0`, porte donc sur le code livré. Ses tâches sont citées ci-dessous comme « CI du code livré ».
- Une mesure « locale » a été faite hors CI, sur le portable de développement ; elle ne vaut pas preuve au sens de `CLAUDE.md`, mais le document de M1 en demande la publication.

## 1. Résultat en bref

**Ce qui marche.**
- Le propriétaire joue la tranche 0 de bout en bout dans le client rétro : il extrait, transporte et vend (objectif 1). Il a validé la boucle de jeu (objectif 11).
- La partie de référence (graine 1, 5 PNJ, 100 000 ticks) se rejoue avec les mêmes empreintes sous `PYTHONHASHSEED=0` et `1`, et l'outil de divergence localise un écart au tick et au composant près (objectifs 2 et 3).
- L'économie reste dans ses fourchettes sur les dix fenêtres de 10 000 ticks, et les trois invariants de conservation tiennent à chaque tick (objectifs 4 et 5).
- Les 12 contrôles sont exigés par la protection de `main`. Chacun des cinq essais E1 à E5 a fait rougir le contrôle visé, et GitHub a refusé la fusion, même tentée en administrateur (objectif 8).
- La tâche de nuit, lancée à la main, réussit : 6 canaris attrapés sur 6, mutation complète du noyau au-dessus du plancher, protection de `main` en place.

**Ce qui n'est pas encore démontré.**
- **Le rejeu sur le PC d'entraînement** (objectif 2, « sur les deux machines ») : **en attente** de la sortie que le propriétaire doit coller (section 5).
- **Le message de refus de GitHub pour l'essai E3** n'a pas été consigné : la commande a été lancée hors de la session (section 3).
- **La graine des deux parties d'essai** n'a pas été consignée, ni l'essai en 256 couleurs (section 7).

## 2. Ce qui a été livré

| Palier ou volet | Points | Pull requests | Contenu |
| :-- | :-- | :-- | :-- |
| Palier 1 : décision et documents | 1 à 4 | n° 15 et 16 | document de niveau 2 et sa revue EGM, approbation, glossaire, chemins protégés |
| Palier 2 : outillage de M1 | 5 à 14 | n° 17 | mutation, nouvelles tâches de CI, garde |
| Volet A : noyau et formats | 15 à 19 | n° 18 et 19 | `schema`, `core` (`step`, `observe`, registre, générateur à clé), invariants |
| Volet B : serveur, client, PNJ | 20 à 23 | n° 20 à 22 | serveur en mémoire, journal, instantanés, client Textual, `scripted_miner` |
| Volet B bis : écran unique (amendement 1) | 23 bis à 23 sexies | n° 23 à 27 (ADR 0003 à 0005) | monde de 8 à 12 systèmes, durées, visibilité par proximité, mode développement |
| Volet B ter : écran rétro (amendement 2) | 23 septies à 23 undecies | n° 28 à 33, 35, 36, 38 à 41 (ADR 0006 et 0007) | palette 8 bits, carte par forces en Braille, prochaine étape, aide |
| Volet C : rejeu, divergence, économie | 24 à 28 bis | n° 42 à 44 | `tools` (rejeu, divergence, économie), partie de référence, fourchettes, `RULES_REVISION` = 1 |
| Palier 4 : contrôles obligatoires | 29 à 31 ter | n° 45 | suite canari, `nuit.yml`, 12 contrôles exigés, hook mis à jour |
| Palier 5 : compte rendu | 32, 32 bis | n° 48 à 52 (essais, fermées) et celle-ci | essais E1 à E5, ce compte rendu |

Les détails de chaque pull request (revue EGM, mesures, liens CI) sont dans sa description.

## 3. Les essais des contrôles obligatoires (point 32 bis)

Chaque pull request d'essai part de `main` (`7361aac`), applique le bug volontaire du canari correspondant (`.github/canaris/`), et a été fermée sans fusion par le propriétaire, branche supprimée. Le propriétaire a tenté chaque fusion par `! gh pr merge <n> --admin --squash`, une fois le contrôle visé rouge.

| Essai | Pull request | Contrôle visé : lien et message | Autres contrôles rouges | Refus de GitHub |
| :-- | :-- | :-- | :-- | :-- |
| E1. Nombre flottant dans `step` | [n° 48](https://github.com/EZPK/4X/pull/48) | [`tests`](https://github.com/EZPK/4X/actions/runs/45680098110/job/139438041980) : « src/fourx/core/step.py:456: nombre flottant » | `mutation` (`step.py` 98,1 % contre 98,4 % à la base) | « GraphQL: 2 of 12 required status checks are failing. (mergePullRequest) » |
| E2. Taille du monde par `hash()` | [n° 49](https://github.com/EZPK/4X/pull/49) | [`rejeu`](https://github.com/EZPK/4X/actions/runs/45682045025/job/139444836180), dès `PYTHONHASHSEED=0` : « le rejeu diverge de la référence : tick 1000 : systems, deposits, stations, ships » | `tests` (« world.py:32: usage de hash »), `lint` (ligne trop longue), `mutation` (un test du monde casse) | « GraphQL: 4 of 12 required status checks are failing. (mergePullRequest) » |
| E3. Portefeuille d'un autre acteur dans l'observation | [n° 50](https://github.com/EZPK/4X/pull/50) | [`proprietes`](https://github.com/EZPK/4X/actions/runs/45683109808/job/139448521061) : « test_visibilite_des_observations - AssertionError: assert 0 == 9 » | `tests` (`test_observation_d_un_acteur` et deux autres), `mutation` | **non consigné** : la commande a été lancée hors de la session ; `mergeStateStatus` = `BLOCKED` avant la tentative, et la pull request est fermée sans fusion |
| E4. `core` importe `server` | [n° 51](https://github.com/EZPK/4X/pull/51) | [`imports`](https://github.com/EZPK/4X/actions/runs/45683810794/job/139450979813) : « Contracts: 6 kept, 1 broken. fourx.core is not allowed to import fourx.server » | `tests` (contrôle statique du déterminisme) | « GraphQL: 2 of 12 required status checks are failing. (mergePullRequest) » |
| E5. Fonction non vérifiée dans `arith.py` | [n° 52](https://github.com/EZPK/4X/pull/52) | [`mutation`](https://github.com/EZPK/4X/actions/runs/45685558738/job/139457119299) : `arith.py` 92,3 % contre 100,0 % à la base, « score inférieur à la base » | aucun | « GraphQL: Required status check "mutation" is failing. (mergePullRequest) » |

**Lecture.** Chaque bug est attrapé par le contrôle visé. Plusieurs le sont aussi par d'autres contrôles : c'est sans conséquence sur l'essai, et montre que les contrôles se recouvrent en partie.

**Autres essais du plan de vérification.**
- **La suite canari échoue quand un contrôle laisse passer son bug.** En local, sur `60c30f7`, la commande du contrôle `imports` remplacée par `true` : « core-importe-server → imports : code 0 — NON ATTRAPÉ (« fourx.server » absent de la sortie) », « 0 canaris attrapés sur 1 », code de sortie 1.
- **Lancement manuel de `nuit.yml`** par le propriétaire (`! gh workflow run nuit.yml --ref main`), run [`45686800721`](https://github.com/EZPK/4X/actions/runs/45686800721) sur `7361aac`, réussi :

  | Tâche | Résultat | Durée |
  | :-- | :-- | :-- |
  | [`canari`](https://github.com/EZPK/4X/actions/runs/45686800721/job/139461429823) | « 6 canaris attrapés sur 6 » | 5 min 55 s |
  | [`mutation-complete`](https://github.com/EZPK/4X/actions/runs/45686800721/job/139461430279) | tous les fichiers de `core` et `schema` au-dessus du plancher de 80 % (section 6) | 8 min 12 s |
  | [`protection`](https://github.com/EZPK/4X/actions/runs/45686800721/job/139461429955) | « Protection de main en place. » | 20 s |

- **Protection de `main`**, appliquée par le propriétaire après la fusion de la pull request n° 45 (`! gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json`), puis relue par l'agent de code avec `gh api repos/EZPK/4X/branches/main/protection` : 12 contrôles exigés (`lint`, `typage`, `gitleaks`, `termes-interdits`, `tests-outillage`, `garde`, `en-attente`, `tests`, `rejeu`, `proprietes`, `imports`, `mutation`), `strict` = `true`, `enforce_admins` = `true`, `allow_force_pushes` = `false`, `allow_deletions` = `false`.

## 4. CI du code livré

Run [`45666609367`](https://github.com/EZPK/4X/actions/runs/45666609367) (et [`45666609595`](https://github.com/EZPK/4X/actions/runs/45666609595) pour le garde), tous en `success` :

| Tâche | Lien | Durée |
| :-- | :-- | :-- |
| `tests` (tests et scénarios) | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338904) | 46 s |
| `rejeu` (deux `PYTHONHASHSEED`, divergence, `-m lent`) | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338687) | 1 min 35 s |
| `proprietes` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338775) | 29 s |
| `imports` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338415) | 14 s |
| `mutation` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338650) | 20 s (aucun fichier muté) |
| `tests-outillage` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338511) | 22 s |
| `lint` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338731) | 18 s |
| `typage` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390337876) | 24 s |
| `gitleaks` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338776) | 23 s |
| `termes-interdits` | [job](https://github.com/EZPK/4X/actions/runs/45666609367/job/139390338926) | 16 s |
| `garde` | [job](https://github.com/EZPK/4X/actions/runs/45666609595/job/139390344816) | 18 s |
| `en-attente` | [job](https://github.com/EZPK/4X/actions/runs/45666609595/job/139390343849) | 9 s |

**Durée de la mutation sur une pull request qui touche le noyau.** Elle ne mute que les fichiers modifiés : 4 min 35 s pour l'essai E1 (`step.py`), 6 min 52 s pour l'essai E4, 2 min 23 s pour la pull request n° 44 (`version.py`). Aucune tâche n'approche le seuil de 30 minutes du point 28 bis.

**Scénarios en attente.** `tests/scenarios/en_attente.txt` ne contient plus aucune entrée sur `main` : tous les scénarios de `noyau.feature`, `partie.feature`, `ecrans.feature` et `rejeu.feature` passent dans `tests`.

## 5. Le rejeu sur le PC d'entraînement

*En attente.* Le propriétaire lance, depuis `main` à jour, sur le PC d'entraînement :

```
uv sync --locked
PYTHONHASHSEED=0 uv run pytest -m rejeu
PYTHONHASHSEED=1 uv run pytest -m rejeu
```

Sa sortie sera recopiée ici, sans adresse ni identifiant de la machine.

## 6. Économie, mesures et mutation

### 6.1 Fourchettes sur 100 000 ticks (objectif 5, point 27)

Relevés de l'outil de régénération sur la partie de référence (pull request n° 44), vérifiés en CI par `tests/economie/test_fourchettes.py` (tâche `rejeu`, étape `-m lent`).

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

### 6.3 Carte et écran (amendement 2, point 28 bis)

Mesures de la pull request n° 33 :
- **Disposition sur les graines 1 à 2 000** (test `lent`, dans la tâche `rejeu`) : aucun recouvrement ; au zoom 1, sur un canevas de 70 × 23 et sur un de 100 × 30, chaque case d'un système est dans la grille, sans case commune ni voisine avec un autre système ; le filet de sécurité déplace 45 systèmes au total ; croisements de liens : 0,76 par monde en moyenne, 7 au plus, dans 52 % des mondes.
- **Temps de rendu** (local, script hors du dépôt : vrai serveur, graine 1, 2 000 ticks, grille et peinture d'une carte de 70 × 23 à chaque mise à jour) : moyenne 7,0 ms, maximum 71 ms, sous les seuils de 30 ms et de 100 ms.

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

Tous les fichiers dépassent le plancher de 80 %. Ces scores sont ceux que la pull request n° 44 avait mesurés en local sur `8b3a5fd`.

## 7. Les parties d'essai et les décisions du propriétaire

| Partie ou décision | Date | Conditions | Verdict du propriétaire |
| :-- | :-- | :-- | :-- |
| Partie d'essai de l'écran unique (point 23 sexies) | 2026-11-22 | `main` après la pull request n° 27 ; graine et vitesses jouées non consignées | **lisibilité (objectif 12) : non atteinte** : « l'écran est visible, mais l'interface est vraiment pas claire. L'information n'est pas hiérarchisée. » **Boucle (objectif 11) : validée**, « mais garde en tête qu'il va falloir l'étoffer ». Suite : ADR 0006 et amendement 2 |
| Partie d'essai de l'écran rétro (point 23 undecies) | 2026-11-22 | version stable (`make jouer`, après les pull requests n° 33 et 37) ; terminal foot dans le multiplexeur herdr ; police JetBrainsMono Nerd Font, corps 8 ; `TERM` = `xterm-256color`, `COLORTERM` = `truecolor` ; taille d'au moins 120 × 36 (le jeu s'affichait), environ 160 colonnes d'après la capture ; graine non consignée ; essai en 256 couleurs non fait | **lisibilité (objectif 12) : favorable** : « beaucoup mieux maintenant […] pour le moment, c'est pas mal » ; la carte en Braille est « nettement mieux » (objectif 17). Premier cycle : environ 1 h (soute de 2 000, débit de 1 par tick). Retours : la route déjà parcourue ne doit plus être jaune (corrigé par les pull requests n° 38 et 41) ; il reste difficile de savoir où aller vendre. Aucun verdict séparé sur les objectifs 18 et 19 |
| Validation de la boucle de jeu (objectif 11) | 2026-11-25 | en session, après la livraison du palier 4 | « oui je valide la boucle de jeu » |

Le verdict sur l'écran rétro ne bloque pas la livraison de M1 (décision du propriétaire, 2026-11-22). Les besoins d'écran exprimés après la partie (informations sur les systèmes, onglets, inventaire de la soute, vente sélective) sont pour une prochaine conception.

## 8. Objectifs et critère de sortie

| Objectif du document de M1 | Preuve | État |
| :-- | :-- | :-- |
| 1. Le propriétaire joue la tranche 0 de bout en bout | scénario « Le propriétaire extrait ore_b, le ramène à la station qui le paie le mieux et le vend » (`partie.feature`), dans `tests` (section 4) ; parties d'essai (section 7) | atteint |
| 2. Une partie se rejoue à l'identique | `rejeu` (section 4) : deux `PYTHONHASHSEED`, divergence « aucune » ; scénario de `rejeu.feature` ; E2 | atteint sur le portable et en CI ; **PC d'entraînement en attente** (section 5) |
| 3. Un rejeu qui diverge est localisé | scénario « L'outil de divergence signale au tick 50, composant ledger… » (`rejeu.feature`), dans `tests` ; E2 localise au tick 1 000 et aux composants | atteint |
| 4. L'argent et les biens se conservent | `test_invariants_apres_chaque_tick` (`proprietes`) ; vérification après chaque tick des scénarios du noyau ; canari `vente-sans-taxe-ecrite` attrapé (section 3) | atteint |
| 5. L'économie reste dans ses fourchettes sur 100 000 ticks | section 6.1 ; `test_fourchettes.py` dans `rejeu` | atteint |
| 6. Tous les acteurs passent par la même porte | `test_visibilite_des_observations` (`proprietes`) ; scénarios « Un ordre au nom d'un autre acteur est refusé par la réception » et « Un ordre d'administration soumis par un client est refusé » ; E3 | atteint |
| 7. Tout ce qui persiste ou circule porte un numéro de version | `tests/core/test_versions.py`, `tests/server/test_versions_journal.py`, dans `tests` | atteint |
| 8. Les contrôles de M1 deviennent obligatoires | protection de `main` relue (section 3) ; E1 à E5 ; run de nuit | atteint, sauf le message de refus de E3 non consigné |
| 9. L'indicateur avancé est mesuré | section 6.2 (local) | atteint |
| 10. Les identifiants du glossaire sont fixés | `docs/glossaire.md` : plus aucun terme « à fixer au niveau 2 de M1 » ; Technical Plan, point 12 | atteint |
| 11. Le propriétaire valide la boucle de jeu | section 7 (2026-11-22, avec réserve ; 2026-11-25) | atteint |
| 12. Le propriétaire lit l'écran sans se perdre | section 7 : non à l'écran unique, favorable à l'écran rétro ; tests du pilote de Textual dans `tests` | verdict favorable consigné |
| 13. Le temps est une ressource, et les durées sont des règles | scénario « Les durées lues dans l'observation sont celles du jeu, sur les vrais réglages » | atteint |
| 14. Le joueur connaît les durées par l'observation seule | ADR 0003 ; scénarios des durées (`partie.feature`, `ecrans.feature`) | atteint |
| 15. L'univers s'accélère en mode développement | tests du client dans `tests` ; mesure de débordement (section 6.3) | atteint |
| 16. Le monde est plus grand, et sa taille vient de la graine | ADR 0004 ; `world.generate` muté à 100 % ; tests de génération sous deux `PYTHONHASHSEED` | atteint |
| 17. La carte montre tous les systèmes à la fois | scénario de la disposition (`ecrans.feature`) ; section 6.3 ; verdict « nettement mieux » | verdict favorable consigné |
| 18. L'écran dit quoi faire ensuite | scénario « La prochaine étape suit un cycle joué » | atteint par les tests ; pas de verdict séparé du propriétaire |
| 19. Les mécaniques sont expliquées dans le jeu | scénario « L'aide donne les durées lues dans l'observation » ; tests de l'aide | atteint par les tests ; pas de verdict séparé du propriétaire |

| Élément du critère de sortie de M1 (niveau 1, §11) | Preuve | État |
| :-- | :-- | :-- |
| Le CUJ 1 passe | objectif 1 | atteint |
| Le CUJ 4 passe | objectif 3 | atteint |
| Sur 100 000 ticks, la masse monétaire, l'émission et la destruction par motif restent dans les fourchettes | objectif 5 | atteint |
| Le rejeu est identique sur les deux machines | objectif 2 | **en attente du PC d'entraînement** |
| Le propriétaire valide la boucle de jeu | objectif 11 | atteint |

## 9. Écarts, réserves et incidents

1. **Rejeu sur le PC d'entraînement en attente** (section 5). Tant qu'il manque, un élément du critère de sortie n'est pas prouvé.
2. **Message de refus de E3 non consigné.** Le blocage est montré par `mergeStateStatus` = `BLOCKED` et par les quatre autres essais, mais le message de GitHub n'a pas été vu.
3. **Parties d'essai.** Les graines jouées ne sont pas consignées, l'essai en 256 couleurs n'a pas été fait, et la taille du terminal n'a pas été mesurée exactement. Les objectifs 18 et 19 n'ont pas de verdict séparé : le verdict favorable porte sur l'écran dans son ensemble.
4. **Le hook refuse `gh workflow run` et `gh pr close` à l'agent de code.** Le propriétaire a lancé la tâche de nuit et fermé les pull requests d'essai lui-même.
5. **Incident de la pull request n° 46 (`README.md`).** Elle a été fusionnée sur son premier commit, avant que GitHub n'ait pris en compte les deux suivants ; la pull request n° 47 a rétabli la version voulue. Depuis, l'agent de code vérifie que la tête de la pull request est son dernier commit avant de la dire prête.
6. **Point 27 corrigé au palier 4.** Ses deux calculs dataient d'avant la soute de 2 000 ; ils ont été refaits (10 800 ticks ; 900 000) dans la pull request n° 45.

## 10. Ce qui reste à faire

1. **Propriétaire :** lancer le rejeu sur le PC d'entraînement et coller sa sortie, recopiée en section 5 avant la fusion de cette pull request.
2. **Propriétaire :** relire ce compte rendu et fusionner sa pull request protégée.
3. **Propriétaire :** décider si M1 passe à `livré` (point 33). Sur sa demande, l'agent de code met alors à jour `docs/feuille-de-route.md` dans une pull request protégée : M1 `livré`, « Jalon en cours » : M2.
