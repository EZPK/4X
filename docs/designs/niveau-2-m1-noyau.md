# M1 : noyau déterministe et tranche 0 (document de niveau 2)

*   **Auteur :** Thomas (thom.bruyer)
*   **Statut :** Proposed
*   **Date :** 2026-11-02 ; mis à jour le 2026-11-06 (décisions du propriétaire sur le contenu du jeu ; corrections de la revue EGM, étapes 5 à 9)
*   **Niveau 1 :** [architecture-niveau-1.md](./architecture-niveau-1.md) (CUJ 1, CUJ 4, §1 à §7, §10, §11 ligne M1)
*   **Intentions reprises :** [RFC du brainstorm](./mmo-gestion-spatiale-ia.md), jalon « M1 – Tranche 0 ». Le niveau 1 fait foi en cas d'écart.

Les titres de section (`##`), le statut et les intitulés du gabarit du plan (sous-titres, Type / Scope, Proposed Changes, Create / Modify / Delete) suivent le gabarit de conception d'EGM, en anglais, pour que les outils de revue s'y retrouvent. Tout le reste est en français.

**Chemins protégés nouveaux.** Un fichier nouveau ajouté à `.github/chemins-proteges.txt` dans la pull request protégée qui le crée compte comme protégé dans cette pull request. Un fichier qui existe déjà sans être protégé doit être protégé par une pull request antérieure avant d'être modifié dans une pull request protégée (d'où le plan détaillé, point 3 bis).

**Conventions de renvoi.** « Technical Plan, point N » désigne une section du Technical Plan de ce document. « Plan détaillé, point N » désigne un point du Detailed Implementation Plan de ce document. Un « point N » sans préfixe renvoie à la même partie du document que le passage qui le cite. Un renvoi au niveau 1 le dit toujours (« niveau 1, §2 »).

**Autres conventions.**
- Un *CUJ* (Critical User Journey) est un parcours utilisateur critique du niveau 1 ; M1 reprend le CUJ 1 et le CUJ 4 sans les adapter, et les scénarios du plan détaillé, points 20 et 24, les traduisent.
- « Par `!` » veut dire que le propriétaire tape la commande dans Claude Code en la préfixant de `!`, ce qui l'exécute dans la session sous son propre nom.
- Un *site* est une station ou un gisement. Un *gisement* est l'entité du jeu où l'on mine ; « champ » ne désigne que les champs de données.
- Les deux machines sont l'*ordinateur portable* du propriétaire et le *PC d'entraînement*.

--------------------------------------------------------------------------------

## Overview

M1 est le premier jalon qui contient des règles du jeu. Il construit la *tranche 0* : un petit monde hors ligne, généré à partir d'une graine, où le propriétaire peut extraire du minerai, le transporter jusqu'à une station et le vendre à prix fixes (niveau 1, CUJ 1).

Tout tourne dans un seul processus, sur l'ordinateur portable. M1 livre six livrables, qui dépendent les uns des autres :
1. **le noyau** (`core`) : l'état du monde, la fonction `step`, la fonction `observe` et le registre comptable, avec les invariants de déterminisme du niveau 1, §2 ;
2. **les règles de la tranche 0** : déplacement sur une carte en graphe, minage dans des gisements finis qui se régénèrent, vente à la station, taxe ;
3. **les formats** (`schema`) : ordres, résultats d'ordre, observations, événements v0 et messages du protocole, chacun avec son numéro de version ;
4. **le serveur en mémoire** (`server`) : la boucle des ticks, la réception des ordres, le journal des ordres soumis, les instantanés et l'enregistrement des événements v0 ;
5. **le client Textual minimal** (`clients`), relié au serveur dans le même processus, et un PNJ (`policies`) qui joue la même boucle que le propriétaire ;
6. **l'outillage de vérification** (`tools` et CI) : l'outil de divergence, le test de rejeu, et les contrôles obligatoires de M1 (niveau 1, §10).

M1 fixe aussi les identifiants que le glossaire marque « à fixer au niveau 2 de M1 ».

## The Problem

Le niveau 1 fixe les interfaces et les invariants, mais aucun code ne les met encore en œuvre. Tant qu'un premier noyau n'existe pas, trois choses restent inconnues :
- **si les invariants tiennent sur un vrai tick.** Le déterminisme, la conservation de l'argent et des biens et la visibilité par champ de données n'ont été vérifiés que sur papier, et sur un banc d'essai simplifié (niveau 1, §2) ;
- **si la boucle de jeu fonctionne.** Extraire, transporter et vendre doit former une boucle que le propriétaire a envie de rejouer. C'est un jugement subjectif, que le niveau 1 assume ;
- **comment l'économie évolue sur la durée.** Sur 100 000 ticks, la masse monétaire, l'émission et la destruction doivent rester dans des fourchettes connues. Sans cela, on ne saura pas si une dérive future vient d'une règle ou d'un joueur IA.

Tous les jalons suivants reposent sur ce noyau. L'entraînement (M4) fait tourner `step` dans de nombreux processus en parallèle, le serveur persistant (M5) rejoue son journal, l'observabilité (M2) lit ses événements. Une erreur de format ou de déterminisme laissée à M1 se paierait plus tard en migrations, ou en joueurs IA entraînés sur un monde faux.

Le jalon est large : six livrables, et cinq contrôles obligatoires de plus (dont `imports`, qui tourne déjà sans être obligatoire). Le risque principal est donc l'exécution, pas la conception. Un agent de code sans mémoire doit pouvoir livrer chaque livrable à partir de ce document seul, sans décision ouverte : les noms et les signatures sont au Technical Plan, point 13.

## Goals

Chaque objectif est vérifiable par un contrôle automatique, ou validé explicitement par le propriétaire quand le document le dit.

1. **Le propriétaire joue la tranche 0 de bout en bout** (niveau 1, CUJ 1). Dans le client Textual, il choisit un minerai, envoie un vaisseau l'extraire, le ramène à la station et vend sa cargaison. Le client affiche le trajet, la cargaison et le paiement.
   *Vérification :* un scénario en français, joué par la CI à travers le protocole en mémoire, sans le client Textual ; une capture du client n'est pas exigée avant M3.
2. **Une partie se rejoue à l'identique.**
   - En CI, le journal enregistré de la partie de référence (100 000 ticks) est rejoué sous `PYTHONHASHSEED=0` puis `1` ; les deux rejeux sont comparés **tick par tick** par l'outil de divergence, et chacun est comparé aux empreintes de référence **tous les 1 000 ticks**.
   - Les empreintes de référence sont produites sur l'ordinateur portable (plan détaillé, point 27) : un rejeu réussi en CI prouve donc aussi l'égalité avec l'ordinateur portable.
   - Sur le PC d'entraînement, le propriétaire lance la même commande (Verification Plan) ; sa sortie est citée dans le compte rendu de M1.

   *Vérification :* la tâche `rejeu` en CI, et la sortie citée dans le compte rendu.
3. **Un rejeu qui diverge est localisé** (niveau 1, CUJ 4). L'outil de divergence indique le premier tick qui diverge et les composants de l'état concernés.
   *Vérification :* un scénario qui modifie volontairement un composant à un tick donné et vérifie que l'outil nomme ce tick et ce composant.
4. **L'argent et les biens se conservent.** Les trois invariants du niveau 1, §4 (Technical Plan, point 3), sont vérifiés à chaque tick.
   *Vérification :* une assertion à chaque tick dans les tests et les scénarios, et des tests de propriétés sur des parties générées.
5. **L'économie reste dans ses fourchettes sur 100 000 ticks.** Sur la partie de référence, l'émission par motif, la destruction par motif et la croissance de la masse monétaire, par fenêtre de 1 000 ticks, restent dans les bornes du plan détaillé, point 27. Les prix sont fixes à ce jalon.
   *Vérification :* un test lancé en CI, qui calcule ces grandeurs à partir des événements v0 avec la fonction du plan détaillé, point 25, et un notebook marimo qui affiche les mêmes grandeurs, calculées par la même fonction, pour le propriétaire.
6. **Tous les acteurs passent par la même porte.** Le client Textual et le PNJ reçoivent leurs observations de la seule fonction `observe`, et leurs ordres passent par la même réception, puis par `step`. Aucun champ de données caché n'apparaît dans une observation.
   *Vérification :* des tests de propriétés sur la visibilité ; les contrats d'imports interdisent à `clients` et `policies` d'importer `core`.
7. **Tout ce qui persiste ou circule porte un numéro de version.** Le journal des ordres soumis, les instantanés, les événements, le protocole et les règles portent leurs champs de version (niveau 1, §3 et §7).
   *Vérification :* `tests/core/test_versions.py` et `tests/server/test_versions_journal.py` (plan détaillé, points 18 et 23) ; le contrôle de garde exige que `RULES_REVISION` augmente de un quand les références changent.
8. **Les contrôles de M1 deviennent obligatoires** (niveau 1, §10) : tests et scénarios ; rejeu sous deux `PYTHONHASHSEED` ; tests de propriétés ; contrats d'imports ; mutation sur les fichiers modifiés, scénarios compris (Technical Plan, point 10), avec un score jamais inférieur à celui du commit de base de la pull request. La suite canari et la mutation complète du noyau tournent chaque nuit sur `main`.
   *Vérification :* les cinq contrôles figurent dans la protection de `main` ; les essais du plan détaillé, point 32 bis, montrent qu'une pull request en échec sur chacun d'eux est refusée ; la suite canari échoue si l'un de ses bugs volontaires n'est pas attrapé.
9. **L'indicateur avancé est mesuré.** Les ticks par seconde de `step` et `observe`, sur un monde de la taille de ceux de l'entraînement, sont mesurés et publiés. Ils ne déclenchent rien (niveau 1, §2).
   *Vérification :* la mesure figure dans le compte rendu de M1, avec la commande qui l'a produite.
10. **Les identifiants du glossaire sont fixés.** Chaque terme marqué « à fixer au niveau 2 de M1 » reçoit son identifiant du code, et le glossaire est mis à jour.
    *Vérification :* plus aucune entrée du glossaire ne porte « à fixer au niveau 2 de M1 ».
11. **Le propriétaire valide la boucle de jeu.** Après avoir joué, il déclare que la boucle extraire, transporter, vendre lui convient. C'est une validation subjective, assumée par le niveau 1, §11.
    *Vérification :* sa décision, consignée dans le compte rendu de M1.

## Non-Goals

*   **Le marché entre joueurs, les corporations, les permissions, le combat et les pirates.** Ils arrivent à M6. La phase « combat » existe dans l'ordre des phases du tick (niveau 1, §2), mais reste vide à M1.
*   **La perte de vaisseau.** Aucun vaisseau n'est détruit à M1 (Technical Plan, point 1).
*   **Les prix variables.** La station rachète chaque minerai à un prix fixe.
*   **Le transport WebSocket, les comptes et l'authentification par jeton.** Ils arrivent à M3. À M1, le client et le serveur partagent un processus, et les messages circulent déjà typés : un message illisible ne peut pas exister. M3 fixera son traitement.
*   **Le serveur persistant, les migrations testées, `synchronous=FULL` et la reprise après plantage.** Ils arrivent à M5. Avant M5, un changement incompatible de format fait monter sa version, et les données sont régénérées (niveau 1, §7).
*   **Les événements v1, Parquet et la page d'accueil.** Ils arrivent à M2. Les événements v0 sont des fichiers JSONL jetables.
*   **L'environnement d'entraînement, l'encodeur, le décodeur, `obs_spec_version` et `action_spec_version`.** Ils arrivent à M4.
*   **La télémétrie technique.** Elle arrive à M5.
*   **Le scénario « dix premières minutes d'un joueur », les captures du client et la vidéo.** Ils arrivent à M3.
*   **L'assurance, le gouvernement, les banques et les institutions** (niveau 1, Non-Goals).
*   **L'univers du jeu et les noms propres.** Aucun nom de lieu, de minerai ou de vaisseau n'est inventé : `docs/noms-valides.md` est vide.
*   **Rust.** Le passage n'est envisagé que si le déclencheur du niveau 1, §2, est atteint, et il ne peut pas l'être avant M4.

## Open Questions

Ces questions sont posées au propriétaire une à une pendant la rédaction. Une question tranchée quitte cette liste et rejoint le Technical Plan.

Aucune question ouverte. Les lignes du Technical Plan, point 1, marquées « proposition de l'agent de code » attendent la confirmation du propriétaire au passage à Approved.

--------------------------------------------------------------------------------

## Technical Plan (Architecture)

### 1. Décisions prises pour M1

**Règle de rédaction (propriétaire, 2026-11-02).** M1 fait le minimum possible **dans le cadre déjà fixé** par le niveau 1. Ce document ne réduit aucune exigence du niveau 1, n'en ajoute aucune sauf le seuil de mutation ci-dessous, et ne redéfinit rien : chaque contrôle obligatoire de M1 est livré. Quand une question de contenu du jeu a plusieurs réponses, la plus petite qui respecte le niveau 1 est retenue.

**Décisions sur le contenu du jeu (propriétaire, 2026-11-06).** Après la rédaction, pendant la revue de l'univers et de la conception du jeu (documents hors de `main`), le propriétaire a tranché quatre points du contenu de la tranche 0. Ils priment sur la règle du minimum et figurent dans le tableau ci-dessous (lignes datées du 2026-11-06, sans autre mention). Aucun ne change le niveau 1.

**Propositions de l'agent de code (2026-11-06).** Pendant la revue EGM de ce document, le propriétaire a délégué à l'agent de code les choix techniques que la revue a fait apparaître. Ces lignes portent la mention « proposition de l'agent de code » et attendent la confirmation du propriétaire au passage à Approved.

| Question | Décision | Raison |
| :-- | :-- | :-- |
| Perte de vaisseau | aucune à M1 | le niveau 1 ne l'exige pas ; l'ajouter changerait l'invariant 3 du niveau 1, §4 |
| Noms et identifiants | dans l'état, chaque entité a un identifiant entier, propre à sa table, à partir de 1 ; les scénarios et le client affichent des libellés neutres tirés de l'identifiant (Technical Plan, point 13) | le niveau 1, §2, exige des tables indexées par un identifiant entier ; `docs/noms-valides.md` est vide ; les exemples de `CLAUDE.md` (`station_a`, `ore_1`) ne sont que des exemples |
| Taille de la tranche 0 | 3 systèmes, 2 minerais, 1 station, 1 vaisseau pour le propriétaire, 1 PNJ | le bas des fourchettes du niveau 1, CUJ 1 |
| Rythme du temps | une horloge du serveur fait avancer les ticks ; sa période est un paramètre du serveur, hors des règles | le niveau 1, §2, ordonne chaque tick autour de la réception des ordres (« reçus avant le début du tick T+1 »), ce qui suppose des ticks cadencés par le serveur ; voir l'alternative C |
| Preuve sur le PC d'entraînement | le propriétaire lance la commande de rejeu sur le PC d'entraînement, à la fin du jalon, et sa sortie va dans le compte rendu de M1 | seul le propriétaire a accès à cette machine ; aucune adresse ni aucun identifiant n'entre dans le dépôt |
| Fourchettes économiques | les fourchettes portent sur l'émission par motif, la destruction par motif et la croissance de la masse monétaire, **par fenêtre de 1 000 ticks** ; les bornes sont au plan détaillé, point 27 | à prix fixes, la station paie chaque vente par une émission et seule la taxe détruit de l'argent : la masse monétaire ne peut que croître, et seule sa croissance par fenêtre peut rester dans une fourchette ; par l'invariant 2, cette croissance vaut l'émission moins la destruction |
| Point de départ du jeu | un module à la racine du paquet, `fourx/__main__.py`, assemble le serveur en mémoire et le client | `clients` ne peut pas importer `server`, ni `server` importer `clients` (niveau 1, §1) ; seule la racine du paquet peut les relier, et les contrats d'imports ne la contraignent pas |
| Outil de mutation | `mutmut` 3.8.0 (choix du propriétaire) | essayé sous Python 3.15 avec pytest 9.1.1 le 2026-11-02 : fonctionne ; cassé par pytest 9.2.0, donc pytest est plafonné sous 9.2 et toute montée de pytest est vérifiée avec `mutmut` avant d'être acceptée |
| Mode rejeu du client | son identifiant est fixé ici ; il est construit à M3, avec la vidéo rendue depuis un rejeu | aucun critère de sortie de M1 ne l'exige ; l'outil de divergence suffit au CUJ 4 |
| Station (2026-11-06) | une structure du jeu, pas un personnage : sans `actor_id` ni portefeuille ; elle paie chaque vente par une émission | décision du propriétaire ; le niveau 1, CUJ 1, dit « station PNJ » : la formule désigne ici une structure dont le comportement est fixé par les règles, pas un acteur |
| Gisements (2026-11-06) | finis : chaque gisement a un stock, qui baisse au minage et revient à `deposit_stock` tous les `regen_ticks` ticks (régénération d'un gisement) | décision du propriétaire : un stock large, qui finit par se vider, oblige les mineurs, surtout quand ils viennent à plusieurs, à changer de gisement ; dans le monde en ligne, la régénération d'un gisement a lieu environ chaque semaine. À M1, avec les valeurs du plan détaillé, point 17, la partie de référence ne vide aucun gisement : le stock n'a aucun effet sur les fourchettes, et l'épuisement comme le départage sont vérifiés par les scénarios et les tests de propriétés |
| Visibilité de la vente (2026-11-06) | le vendeur voit sa vente, son paiement et sa taxe dans un événement privé ; les écritures du registre et les compteurs d'émission et de destruction relèvent de l'administration ; aucun acteur ne voit le portefeuille d'un autre | décision du propriétaire (personne ne voit le compte en banque d'un autre, ni l'argent créé par le jeu) ; le niveau 1, CUJ 1, exige que le client affiche le paiement |
| Argent de départ (2026-11-06) | aucun : tout portefeuille commence à zéro ; le vaisseau de départ est une dotation, sans écriture | décision du propriétaire |
| Arrondi de la taxe | vers le haut, au profit du compte de destruction | proposition de l'agent de code : arrondie vers zéro, une taxe s'annulerait sur des ventes découpées en petits lots |
| Seuil de mutation | le contrôle `mutation` échoue si un fichier nouveau de `core` ou de `schema` a moins de 80 % de mutants tués ; la mutation complète du noyau, de nuit, aussi ; le seuil est revu au plan détaillé, point 28 bis | proposition de l'agent de code, seule exigence ajoutée au niveau 1 : à M1, tous les fichiers sont nouveaux, donc la règle du niveau 1 (« jamais inférieur au score de `main` ») ne vérifie rien sans plancher ; il est limité à `core` et `schema`, où les mutants équivalents sont rares, et non au code d'entrées et de sorties |
| Résultats d'ordre | `State` garde les événements et les résultats d'ordre du dernier tick ; la réception applique la validation sans état (niveau 1, §2) ; un ordre qu'elle refuse est quand même journalisé, avec son code de refus, et `step` le refuse avec ce code, sans autre contrôle | proposition de l'agent de code, dans le cadre du niveau 1, §2 (la réception fait les contrôles sans état, `step` ceux qui dépendent de l'état) : `observe` ne lit que l'état et le joueur n'a pas d'autre canal que l'observation (niveau 1, §5) ; le refus de la réception doit donc passer par le journal, puis par `step`, pour arriver dans l'observation et être reproduit au rejeu |
| Ordres d'un même tick | un seul ordre examiné par vaisseau et par tick, celui de plus petit numéro, comme pour le quota ; les autres sont refusés (« ordre remplacé ») ; tout ordre sur un vaisseau en route est refusé | proposition de l'agent de code : sinon deux ventes validées contre le même état pourraient vendre plus que la cargaison (invariant 3) |
| Partie de référence | jouée une fois par deux PNJ à la régénération des références ; son journal des ordres soumis est exporté en JSONL versionné, avec ses empreintes, dans `tests/references/` ; le contrôle `rejeu` l'importe et le rejoue par `step` seul, avec l'outil de rejeu de `tools` | proposition de l'agent de code : sinon un changement du PNJ ou du serveur, sans changement de règle, changerait les empreintes et ferait monter `rules_version`, que M4 enregistre et que M5 compare au déploiement |
| Concurrence | une seule boucle `asyncio` : l'horloge est une tâche de cette boucle, à côté de Textual ; un mode sans horloge, synchrone, sert aux tests, aux outils et à la partie de référence | proposition de l'agent de code : Textual tourne déjà sur `asyncio`, et le transport WebSocket de M3 aussi |
| Tâche `tests-outillage` | inchangée jusqu'au palier 4 ; au palier 4, limitée à `tests/outillage`, quand la tâche `tests` devient obligatoire | proposition de l'agent de code : le document de M0 prévoyait que `tests-outillage` « devient `tests` » ; renommer un contrôle obligatoire bloquerait toute fusion entre la pull request qui le renomme et la commande de protection ; jusqu'au palier 4, `tests-outillage` lance toute la suite et garde l'échec attendu des scénarios en attente dans un contrôle obligatoire (niveau 2 de M0) |
| Relecture de la protection | une tâche de nuit relit la protection de `main` par la route `GET /repos/EZPK/4X/branches/main`, avec le `GITHUB_TOKEN` en lecture seule (palier 4) | proposition de l'agent de code, qui tient l'engagement du document de M0 : cette route ne demande aucun droit d'administration ; lue sans jeton le 2026-11-06, elle renvoie `protected`, `required_status_checks.enforcement_level` (`everyone`) et la liste des contrôles exigés ; `strict`, `allow_force_pushes` et `allow_deletions` n'y figurent pas et restent vérifiés à la main (plan détaillé, point 31) |
| Fichiers de configuration du dépôt | `pyproject.toml`, `uv.lock` et `.gitignore` deviennent des chemins protégés, au palier 1 | proposition de l'agent de code, qui revient sur l'alternative K du document de M0 (`pyproject.toml` non protégé) : la pull request protégée du palier 2 doit les modifier, or une pull request protégée ne contient que des chemins protégés (`CLAUDE.md`) ; une table `[tool.mutmut]` dans `pyproject.toml` masquerait aussi la configuration protégée de `setup.cfg`. Conséquence : toute nouvelle dépendance passe ensuite par une pull request protégée |
| Copie de référence de la protection dans le hook | au palier 4, le propriétaire met à jour `REFERENCE_PROTECTION` de `.claude/hooks/garde_commandes.py` avec la nouvelle liste des contrôles, selon la procédure de `CLAUDE.md` | proposition de l'agent de code : `tests/outillage/test_garde_commandes.py` exige que `.github/protection-main.json` soit égal à cette copie ; l'agent de code n'édite pas `.claude/` |

### 2. Les règles de la tranche 0

**La carte.** Trois systèmes, `system_1` à `system_3`, reliés en chaîne dans l'ordre de leurs identifiants. La graine du monde fixe le système de chaque site (plan détaillé, point 17, `world.py`) : la station, le gisement de `ore_a` et le gisement de `ore_b` sont chacun dans un système différent. Un saut vers un système voisin dure `jump_ticks` ticks. Chaque gisement a un stock : il commence à `deposit_stock` unités, baisse de ce qui est extrait, et revient à `deposit_stock` aux ticks multiples de `regen_ticks` (phase de règlement). Un gisement vide ne rend plus rien jusqu'à sa régénération.

**Le placement des sites.** Le tirage borné (Technical Plan, point 4) donne, pour (graine du monde, tick 0, entité 0, motif du tirage « carte »), un nombre de 0 à 5 : c'est le rang, dans l'ordre lexicographique, d'une des six permutations de (`system_1`, `system_2`, `system_3`) ; la permutation donne, dans l'ordre, le système de la station, du gisement de `ore_a` et du gisement de `ore_b`.

**Les entités** (types au Technical Plan, point 13).

| Entité | Champs de données principaux |
| :-- | :-- |
| système | identifiant, voisins |
| gisement | identifiant, système, minerai, stock |
| station | identifiant, système, prix de rachat de chaque minerai (copiés de `ore_prices` à la génération du monde ; une structure du jeu : ni acteur ni portefeuille) |
| acteur | identifiant (`id`, l'`actor_id` des formats), type d'acteur (`kind`, l'`actor_kind` des formats), budget d'actions |
| vaisseau | identifiant, acteur détenteur, système, activité (à l'arrêt, en route, en minage), route restante et ticks avant le prochain saut, cargaison par minerai, capacité |
| registre | comptes et leurs soldes, écritures du tick, compteurs cumulés d'émission et de destruction par motif (Technical Plan, point 3) |
| dernier tick | événements et résultats d'ordre produits par le dernier `step` |

**Les ordres.** Les codes de refus d'une ligne sont examinés de gauche à droite : le premier qui s'applique est retenu.

| Catégorie | Ordre | Effet | Refusé si (dans cet ordre) |
| :-- | :-- | :-- | :-- |
| joueur | déplacer un vaisseau vers un système | calcule le plus court chemin (parcours en largeur, voisins par identifiant croissant) et met le vaisseau en route | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, système inconnu, déjà sur place |
| joueur | miner un minerai | le vaisseau extrait à chaque tick, jusqu'à ce que la cargaison soit pleine ou que le gisement soit vide (il passe alors à l'arrêt), ou qu'un autre ordre remplace son activité | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, pas de gisement de ce minerai dans le système, gisement vide, cargaison pleine |
| joueur | vendre une quantité d'un minerai | la station rachète au prix fixe ; la taxe est prélevée ; le vaisseau passe à l'arrêt | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, vaisseau hors du système de la station, quantité nulle ou négative, quantité supérieure à la cargaison |
| administration | créer un personnage | crée l'acteur, son portefeuille personnel et un vaisseau vide, à l'arrêt, dans le système de la station | — (émis par le serveur seulement) |

- **Budget d'actions.** Un acteur commence avec `budget_max` actions. Chaque ordre de joueur accepté coûte une action ; un ordre refusé ne coûte rien. Un ordre qui passe tous les contrôles mais trouve le budget à zéro est refusé (« budget épuisé »).
- **Un ordre par vaisseau et par tick.** Si un acteur soumet plusieurs ordres sur le même vaisseau pour un tick, seul celui de plus petit numéro est examiné ; les autres sont refusés (« ordre remplacé »). Un ordre accepté remplace l'activité en cours du vaisseau dès l'examen, avant les phases du tick.
- **Ordres d'administration.** Le serveur les écrit directement dans le journal, sans passer par la réception, avec un acteur émetteur absent (`sender_actor_id` = `None`) et sans code de refus : ni validation sans état, ni quota, ni budget. `step` refuse (« catégorie interdite ») un ordre sans acteur émetteur qui n'est pas de la catégorie « administration ». L'acteur créé reçoit le prochain identifiant libre de la table des acteurs (le plus grand identifiant plus un) ; son vaisseau et son portefeuille font de même dans leur table. L'ordre porte comme `actor_id` l'identifiant que recevra l'acteur. Un client qui soumet, sous son propre `actor_id`, un ordre d'une autre catégorie que « joueur » voit son ordre refusé par la réception (« catégorie interdite »).
- La catégorie « système » existe dans les formats, mais aucun ordre système n'est émis à M1 : la déconnexion et le départ hors ligne arrivent avec les comptes, à M3.

**Le tick.** `step` suit la chronologie du niveau 1, §2 :
1. il examine chaque ordre soumis, par `actor_id` croissant puis par numéro croissant :
   - un ordre qui porte un code de refus de la réception (validation sans état, Technical Plan, point 5) est refusé avec ce code ;
   - puis un ordre par vaisseau, puis les contrôles du tableau, puis le budget.

   Chaque ordre reçoit un résultat ; un refus produit aussi un événement ;
2. il exécute les phases du tick, dans leur suite fixe :
   - **déplacement :** chaque vaisseau en route décompte son trajet ; à la fin d'un saut, il quitte son système (événement « départ ») et entre dans le suivant (événement « arrivée ») ; au bout de sa route, il passe à l'arrêt ;
   - **minage :** chaque vaisseau en minage extrait jusqu'à `mining_rate` unités, sans dépasser sa capacité libre ni le stock du gisement. Quand plusieurs vaisseaux minent le même gisement et que le stock ne suffit pas à tous, ils sont servis dans l'ordre du départage : chacun reçoit le minimum de `mining_rate`, de sa capacité libre et du stock restant ; un vaisseau servi après l'épuisement ne reçoit rien. Un vaisseau dont la cargaison devient pleine, ou dont le gisement est vide, passe à l'arrêt (événement « fin de minage ») ;
   - **commerce :** chaque vente acceptée retire le minerai de la cargaison et produit deux écritures (Technical Plan, point 3) ;
   - **combat :** vide à M1 ;
   - **règlement :** chaque acteur regagne `budget_regen` actions, sans dépasser `budget_max` ; aux ticks multiples de `regen_ticks`, chaque gisement revient à `deposit_stock` (événement « régénération d'un gisement »).

**Le départage.** La seule égalité possible à M1 est celle de plusieurs vaisseaux sur un gisement dont le stock ne suffit pas. Chaque vaisseau concerné reçoit un tirage à clé sur (graine du monde, tick, identifiant du vaisseau, motif du tirage « minage ») ; les vaisseaux sont servis par tirage croissant, puis par identifiant croissant en cas d'égalité des tirages. La station rachète sans limite : aucune vente n'est donc départagée.

**Les réglages.** Toutes les valeurs vivent dans `tunables.toml`, sous les noms du type `Tunables` (Technical Plan, point 13) : `jump_ticks`, `mining_rate`, `cargo_capacity`, `ore_prices`, `tax_rate_bp` (taux de taxe en points de base), `deposit_stock`, `regen_ticks`, `budget_regen`, `budget_max`. Leurs valeurs sont au plan détaillé, point 17. Le serveur lit ce fichier et passe les réglages à `step` ; le noyau ne lit aucun fichier. `world.generate` copie `ore_prices` dans la station : pendant la partie, le prix qui fait foi est celui de la station, et il est public, pour que le client et la politique le voient.

### 3. Le registre et les invariants

- **Comptes :** émission, destruction, et un portefeuille personnel par acteur. Les types séquestre et portefeuille de corporation existent dans les formats, sans compte ouvert à M1. Le compte d'émission a l'identifiant 1, celui de destruction l'identifiant 2 ; les portefeuilles suivent.
- **Une vente** de `q` unités au prix `p` produit deux écritures, causées par l'ordre de vente :
  - émission → portefeuille du vendeur, montant `q × p`, motif `ORE_SALE` ;
  - portefeuille du vendeur → destruction, montant `q × p × tax_rate_bp / 10 000` arrondi vers le haut (au profit du compte de destruction), motif `SALE_TAX`.
- **Argent de départ :** tout portefeuille commence à zéro. Le vaisseau est donné à la création du personnage, sans écriture : c'est une dotation du jeu, hors de l'invariant 3, qui ne compte que le minerai.
- **Ce que l'état garde :** les soldes des comptes, les écritures du tick en cours, et des compteurs cumulés d'émission et de destruction par motif. L'historique des écritures ne vit que dans les événements (événement « écriture du registre »), pour que l'état et ses empreintes ne grossissent pas avec le nombre de ticks.
- **Les trois invariants du niveau 1, §4,** vérifiés à chaque tick dans les tests :
  1. la somme de tous les comptes vaut zéro (partie double) ;
  2. la masse monétaire = sa valeur au tick précédent + l'émission du tick − la destruction du tick ;
  3. les biens se conservent : aucune quantité n'est négative, et le minerai extrait = le minerai stocké + transporté + vendu. À M1, aucun minerai n'est entreposé, donc : minerai extrait = minerai en cargaison + minerai vendu. Le stock d'un gisement n'y entre pas : le minerai n'est compté qu'une fois extrait, et la régénération d'un gisement ne le touche pas.

### 4. Le noyau et le déterminisme

- **L'état** est un enregistrement `msgspec.Struct` figé, qui contient une table par type d'entité. Une table est un tuple d'enregistrements figés, trié par identifiant croissant. Chaque phase du tick produit de nouvelles tables à partir des précédentes (`msgspec.structs.replace`) : c'est la stratégie de copie par défaut du niveau 1 (alternative R), confirmée ici. Aucun dictionnaire ni ensemble n'apparaît dans l'état. La graine du monde n'est pas dans l'état : elle est passée à `step` (niveau 1, §2), et elle est enregistrée dans l'instantané initial et dans le journal.
- **L'arithmétique** passe par un module du noyau, `arith.py` : division et reste tronqués vers zéro, comme en Rust, une multiplication suivie d'une division en une seule opération, et une division arrondie vers le haut. Hors de ce module, le code du noyau n'emploie jamais `/`, `//`, `%`, ni un nombre flottant.
- **Le générateur à clé :**
  - la clé est (graine du monde, tick, entité, motif du tirage, numéro d'essai) ; chaque entier est encodé sur 8 octets, signé, petit-boutiste ; le motif du tirage est encodé en UTF-8, précédé de sa longueur sur 8 octets ; les cinq morceaux sont mis bout à bout dans cet ordre ;
  - le tirage est `hashlib.blake2b(clé, digest_size=8)`, lu comme un entier non signé petit-boutiste (ce n'est pas le début d'un condensé de 64 octets) ;
  - le tirage borné à `n` valeurs pose `m = (2^64 div n) × n` ; une valeur `x ≥ m` est rejetée et le tirage recommence avec le numéro d'essai suivant ; sinon le résultat est `x mod n`. Il commence à l'essai 0. Ajouter un tirage ne décale donc pas les autres (niveau 1, §2).
- **Les empreintes** sont calculées par composant de l'état : `hashlib.blake2b(encodage, digest_size=16)` sur l'encodage MessagePack de `msgspec` du composant, le même que celui des instantanés, écrit en hexadécimal. Les composants sont les champs de `Fingerprints`, sauf `tick` (Technical Plan, point 13).
- **Les vérifications mécaniques** sont des tests, lancés par le contrôle « tests et scénarios ». Une analyse de la syntaxe des sources de `src/fourx/core/`, à la racine du dépôt, refuse :
  - les nombres flottants, les opérateurs `/`, `//`, `%` et leurs formes d'affectation, sauf dans `arith.py`, seule exemption, et seulement pour `//` et `%` ;
  - `**`, sauf avec un exposant littéral positif ou nul ;
  - les ensembles (`set`, `frozenset`) ;
  - les appels des fonctions intégrées `float`, `hash`, `id`, `divmod`, `pow`, `round`, `open`, `input`, `vars`, `globals`, `eval`, `exec`, `compile`, `__import__` (un champ ou un paramètre nommé `id` reste permis) ;
  - tout import hors d'une liste fermée : `__future__`, `enum`, `typing`, `hashlib`, `msgspec`, `msgspec.structs`, `msgspec.msgpack`, `msgspec.inspect`, `fourx.schema` et ses modules, `fourx.core` et ses modules.

  Les contrats d'imports de M0 restent en place.
- **Les entiers sur 64 bits :** chaque champ entier des types de `schema` et de `core` est déclaré `Int64` (Technical Plan, point 13), qui porte la borne ; un test vérifie à chaque tick, et à chaque encodage, que tout entier de l'état tient dans un entier signé de 64 bits ; les tests de propriétés le vérifient aussi sur des parties générées.

### 5. Les formats (`schema`)

- **Ordre :** `actor_id`, numéro choisi par l'acteur, catégorie, `policy_id` et `policy_version` (`None` pour un humain), et la commande, union typée des quatre ordres. L'identité d'un ordre est (`actor_id`, tick, numéro). Le journal et `step` reçoivent des **ordres soumis** : l'ordre, le tick auquel il entre, l'acteur du point de connexion qui l'a soumis (`None` pour un ordre d'administration écrit par le serveur), et le code de refus de la réception, s'il y en a un (Technical Plan, point 13).
- **Résultat d'ordre :** acteur destinataire (celui du point de connexion), identité de l'ordre, accepté ou code de refus, texte, budget restant (niveau 1, §5). Chaque ordre examiné par `step` reçoit un résultat.
- **Observation :** le tick, l'état visible pour l'acteur, les événements du dernier tick qui lui sont visibles, et ses résultats d'ordre. `observe` lit tout cela dans l'état (table « dernier tick »).
- **Visibilité.** Chaque champ de données des entités de l'état déclare sa classe de visibilité par `Annotated[T, msgspec.Meta(extra={"visibility": ...})]` ; `observe` relit ces métadonnées par `msgspec.inspect.type_info` (mécanisme essayé sur `msgspec` 0.22.0 le 2026-11-06 : la métadonnée revient comme `Metadata` avec son `extra`). Chaque type d'événement a une seule classe. « Privé » veut dire visible par le seul acteur qui détient l'entité. Les vues de l'observation reprennent les noms des champs de données de l'état. À M1 :
  - publics : les systèmes et leurs voisins, les sites, le minerai et le stock des gisements, les prix de rachat de la station, l'identifiant, le détenteur, le système et la capacité des vaisseaux, le `kind` de chaque acteur (`actor_kind`, niveau 1, §5) ;
  - privés : la cargaison, l'activité, la route, les ticks avant le prochain saut et le minage en cours d'un vaisseau, le budget d'actions, le solde (`balance`) du portefeuille personnel ;
  - administration : les écritures du registre, les comptes d'émission et de destruction, les compteurs cumulés.

  Un acteur attentif peut déduire une partie de l'activité d'un autre acteur (position publique, stock public, prix fixes) : c'est accepté à M1.
- **Événements v0** (`event_schema_version` = 0) : l'enveloppe du niveau 1, §6 : `tick` et `seq`, `event_schema_version` et `rules_version`, `actor_id` et `actor_kind`, `policy_id` et `policy_version`, `causation_id`, la classe de visibilité. `actor_id`, `actor_kind` et `causation_id` sont `None` pour un fait des règles (régénération d'un gisement). `causation_id` est l'identité de l'ordre qui a causé l'événement. `seq` croît avec la production dans le tick : examen des ordres, puis phases du tick dans leur suite fixe, puis, dans une phase, identifiants croissants. Les types sont des types `msgspec`, exportables en JSON Schema :

  | Type d'événement | Classe | Contenu | Émis |
  | :-- | :-- | :-- | :-- |
  | personnage créé | public | acteur, `actor_kind`, vaisseau | à l'examen de l'ordre |
  | ordre refusé | privé | identité de l'ordre, code de refus | à l'examen de l'ordre |
  | départ | public | vaisseau, système quitté | à chaque saut, en phase de déplacement |
  | arrivée | public | vaisseau, système atteint | à chaque saut, en phase de déplacement |
  | début de minage | privé | vaisseau, minerai, débit (`mining_rate`) | à l'examen de l'ordre « miner » accepté |
  | fin de minage | privé | vaisseau, quantité extraite depuis le début | quand le minage s'arrête, pour toute raison |
  | vente | privé | quantité, prix, paiement, taxe | en phase de commerce |
  | régénération d'un gisement | public | gisement, stock | en phase de règlement |
  | écriture du registre | administration | l'écriture | quand l'écriture est passée |

  Le montant d'une vente n'est jamais public ; l'événement de vente suffit au client (niveau 1, CUJ 1). Il n'y a jamais un événement par entité et par tick (niveau 1, §6).
- **Protocole** (`protocol_version` = 1) : deux messages. Le client envoie « soumettre des ordres » ; le serveur envoie, après chaque tick, une « mise à jour du tick » qui porte l'observation.
- **Validation sans état** (`validate_orders`, fonction pure) : format (numéro positif ou nul, `policy_id` d'au plus 64 caractères), numéro répété dans un tick (le second et les suivants sont refusés), quota d'ordres par acteur et par tick (`ORDER_QUOTA_PER_TICK`, valeur au plan détaillé, point 16 ; au-delà, les plus petits numéros sont gardés), ordre au nom d'un autre acteur que celui du point de connexion, catégorie autre que « joueur ». Les contrôles sont faits dans cet ordre, et le premier qui s'applique donne le code. Elle vit dans `schema` : la réception l'applique (niveau 1, §2), et, plus tard, l'entraînement l'appliquera de la même façon. Les ordres d'administration du serveur ne passent pas par elle.

### 6. Le serveur en mémoire

```text
  fourx/__main__.py  (assemble, lance asyncio.run)
        |
        v
  clients : client Textual ----+          +---- hôte des PNJ (politique scripted_miner)
                               | ordres   |
                               v          v
  server : réception (validation sans état, point de connexion) --> journal des ordres soumis (SQLite)
                               |
                               v
           horloge --> step (core) --> événements v0 (JSONL), empreintes (journal)
                               |
                               v
           observe (core) --> mise à jour du tick --> chaque client
```

- **La concurrence :** une seule boucle `asyncio`. L'horloge est une tâche de cette boucle. Chaque point de connexion est une paire de `asyncio.Queue` (ordres, mises à jour), derrière le protocole `Connection` de `schema`. Au début de chaque tick, l'horloge vide les files d'ordres : un ordre reçu avant ce moment entre dans ce tick (niveau 1, §2).
- **Le mode sans horloge** sert aux tests, aux outils et à la partie de référence. `Game.advance(n)` joue `n` ticks, de façon synchrone. À chaque tick : il prend les ordres soumis, appelle `step`, envoie la mise à jour à chaque client, puis appelle, pour chaque client synchrone attaché (`SyncClient`, Technical Plan, point 13), `on_update(mise à jour)` ; les ordres que cette méthode renvoie entrent au tick suivant. Une décision prend donc exactement un tick (plan détaillé, point 27, calcul des bornes).
- **L'horloge** déclenche un tick à chaque période. La période est un paramètre du serveur (1 seconde par défaut à M1), hors de `tunables.toml` et hors de `rules_version`.
- **La réception** lie chaque ordre reçu à l'acteur de son point de connexion et au tick où il entre, lui applique la validation sans état, puis le journalise avec son code de refus éventuel. `step` refuse un ordre qui porte un code, avec ce code, et adresse le résultat à l'acteur du point de connexion, par son observation.
- **Le journal des ordres soumis** est une base SQLite en mode WAL (`synchronous=NORMAL` avant M5), `orders.sqlite`, avec deux tables (schéma au plan détaillé, point 21). Il contient sa version (`order_log_schema_version` = 1), `rules_version`, la graine du monde, l'identifiant (SHA) du commit et un indicateur « dossier de travail modifié », les ordres soumis par tick et les empreintes de chaque tick. Il s'exporte et s'importe en JSONL versionné (plan détaillé, point 21).
- **Les fichiers d'une partie** sont rangés dans `runs/<AAAAMMJJ-HHMMSS-micro>/`, ignoré par git : `orders.sqlite`, `snapshot.msgpack` (instantané initial, tick 0, `snapshot_schema_version` = 1, avec `rules_version`, la graine, l'identifiant du commit et l'indicateur « dossier de travail modifié », fournis par le serveur) et `events.jsonl`.
- **Les personnages** sont créés par des ordres d'administration journalisés pour le tick 1, l'un pour le propriétaire, l'autre pour le PNJ ; l'instantané initial est l'état du tick 0, avant ces ordres, et le premier `step` les applique.

### 7. Le client Textual et le PNJ

- **Le client** affiche la carte en ASCII, l'état du vaisseau (système, route, activité, cargaison), le solde du portefeuille, et un historique des résultats d'ordre et des ventes, avec le paiement et la taxe. Le propriétaire donne ses ordres au clavier : `d` (déplacer, puis le numéro du système), `m` (miner, puis la lettre du minerai), `v` (vendre toute la cargaison), `q` (quitter). Le client ne connaît que `schema` (niveau 1, §1).
- **Le PNJ de M1** joue la politique `scripted_miner` de `policies`, la référence scriptée du glossaire. Elle décide de l'activité voulue :
  - si la cargaison est pleine : aller à la station, puis tout vendre ;
  - sinon : parmi les gisements non vides, aller à celui dont le minerai est le mieux payé, puis miner ;
  - si tous les gisements sont vides : rester à l'arrêt.

  Elle n'émet un ordre que si l'activité observée diffère de l'activité voulue : un vaisseau qui mine déjà ne reçoit pas de nouvel ordre « miner ». **L'hôte des PNJ** (`NpcHost`) la fait jouer par le même protocole que le client : il implémente `SyncClient` pour le mode sans horloge, et une tâche de `__main__.py` lui transmet les mises à jour en mode avec horloge.

### 8. Le rejeu, la divergence et les empreintes de référence

- **Le rejeu** part d'un état initial et d'une suite d'ordres soumis par tick, applique `step` tick par tick, et produit les empreintes et les événements de chaque tick. Une seule fonction de `tools` le fait (`replay_orders`, Technical Plan, point 13) ; elle sert à l'outil de rejeu d'un dossier de partie (état initial lu dans l'instantané), au contrôle `rejeu` et au test des fourchettes.
- **L'outil de divergence** (`tools`, niveau 1, CUJ 4) compare deux suites d'empreintes (deux dossiers de partie, ou deux fichiers d'empreintes), et indique le premier tick qui diffère et les composants concernés.
- **La partie de référence** est générée par la graine 1 et jouée par deux PNJ, à travers le serveur en mode sans horloge. Elle n'est jouée qu'à la régénération des références. On enregistre alors, dans `tests/references/rules-<révision>/` :
  - `orders.jsonl`, l'export versionné de son journal des ordres soumis (en-tête : les valeurs de la table `meta` du journal et le dernier tick ; puis un ordre soumis par ligne) ;
  - `reference.json`, son `rules_version` et les empreintes de chaque composant tous les 1 000 ticks et au dernier tick.

  L'état initial n'est pas enregistré : il est régénéré par `world.generate` à partir de la graine, ce qui vérifie aussi la génération du monde. Le contrôle `rejeu` n'a besoin que de `core`, de `schema`, de `tools` et de l'import JSONL de `server`. Un changement du PNJ, de l'hôte des PNJ ou du serveur ne touche donc pas les références ; un changement des règles ou des réglages les fait diverger, et oblige à les régénérer. Une régénération des références remplace le dossier de la révision précédente ; l'historique git le garde (environ 4 Mo par révision, à mesurer au plan détaillé, point 28 bis).
- **La régénération des références** se fait avec l'outil de régénération (plan détaillé, point 27), lancé sur l'ordinateur portable. Il assemble `server`, `clients` et `policies` ; or `tools` peut importer `server`, mais ni `clients` ni `policies` (niveau 1, §1). Il vit donc sous `tests/`, que les contrats d'imports ne contraignent pas (choix du propriétaire), et produit aussi un rapport de différences. Le dossier `tests/references/` devient un chemin protégé. Le contrôle de garde exige que `RULES_REVISION` augmente de un quand les références changent, et pose l'étiquette « références régénérées » sur la pull request (`CLAUDE.md`, circuit des pull requests).
- **`rules_version`** est formé du numéro de révision, tenu à la main dans le noyau (`RULES_REVISION`), et de l'empreinte des réglages (niveau 1, §3) : `"rules-<RULES_REVISION>+<empreinte>"`. Le noyau calcule l'empreinte sur l'encodage MessagePack de `Tunables` (et non sur les octets du fichier, pour qu'un commentaire ne la change pas) : `step` la connaît donc, et la met dans chaque événement.

### 9. L'économie sur 100 000 ticks

- Le contrôle `rejeu` lance aussi un test marqué `lent` : il rejoue le journal enregistré de la partie de référence par `replay_orders` et collecte ses événements v0.
- Une seule fonction de `tools` (`window_stats`) calcule, à partir des événements v0, par fenêtre de 1 000 ticks (ticks 1 à 1 000, 1 001 à 2 000…) : l'émission par motif, la destruction par motif, la croissance de la masse monétaire, et la masse monétaire en fin de fenêtre. Le test vérifie les trois premières grandeurs contre les bornes du plan détaillé, point 27, sur chaque fenêtre sauf la première, qui contient le départ à vide des vaisseaux.
- Un notebook marimo appelle la même fonction et affiche les mêmes grandeurs pour le propriétaire. Il lit aussi les événements avec DuckDB, pour les explorer, sans calcul propre : le niveau 1 (§9, « DuckDB + notebooks marimo » dès M1) fixe ces deux outils pour l'économie.

### 10. Les contrôles de CI de M1

| Contrôle (niveau 1, §10) | Tâche | Ce qu'elle lance | Obligatoire à partir de |
| :-- | :-- | :-- | :-- |
| tests et scénarios | `tests` | `pytest` : tests unitaires, scénarios en français, vérifications mécaniques du noyau | M1 |
| rejeu sous deux `PYTHONHASHSEED` | `rejeu` | le rejeu du journal enregistré de la partie de référence, 100 000 ticks, sous deux valeurs, comparé tick par tick entre les deux rejeux et tous les 1 000 ticks aux empreintes de référence ; puis le test `lent` des fourchettes économiques | M1 |
| tests de propriétés | `proprietes` | `hypothesis` : conservation, entiers sur 64 bits, visibilité, déterminisme, épuisement et départage, sur des parties générées | M1 |
| contrats d'imports | `imports` | `lint-imports` (tâche qui tourne déjà depuis M0 sans être obligatoire) | M1 |
| mutation | `mutation` | `mutmut` sur les fichiers modifiés par la pull request ; le score de chaque fichier ne doit pas être inférieur à celui du commit de base de la pull request, et un fichier nouveau de `core` ou de `schema` doit atteindre 80 % (Technical Plan, point 1) | M1 |

- **« Scénarios compris »** (niveau 1, §10) se lit ainsi : chaque mutant est soumis aux tests et aux scénarios, et une pull request qui modifie des définitions d'étapes (`tests/scenarios/steps/`) déclenche la mutation de tout `src/fourx/core/`, comparée au score du commit de base. Des définitions d'étapes affaiblies laissent survivre plus de mutants, et le contrôle échoue.
- **Le score d'un fichier** est (tués + délais dépassés) / (total − ignorés), calculé à partir de `mutmut results --all true` (une ligne `module.x_fonction__mutmut_N: statut` par mutant, regroupées par module). Les mutants « sans test » et « non vérifiés » comptent comme survivants ; c'est la formule de `mutmut` 3.8.0 pour son badge (`__main__.py`, commande `badge`). Un fichier sans aucun mutant n'a pas de score : il est cité dans le résumé de la tâche et ne la fait pas échouer.
- **Une mutation stable :** les tests `hypothesis` tournent avec un profil sans hasard (`derandomize=True`, sans base d'exemples, sans délai `deadline`), en CI comme sous `mutmut`, pour que le score de la base et celui de la tête soient comparables.
- **Rendre ces contrôles obligatoires** modifie `.github/protection-main.json`, par une pull request protégée, puis la protection de `main`. Appliquer la protection est une modification des réglages du dépôt : l'agent de code n'en a pas le droit (`CLAUDE.md`, « Ne jamais »). Le propriétaire lance lui-même la commande, par `!`.
- **Contrôles de nuit** (niveau 1, §10) : la suite canari, la mutation complète du noyau et la relecture de la protection tournent chaque nuit sur `main`, à partir du palier 4. La mutation complète échoue sous 80 % (Technical Plan, point 1). Avant M2, un échec se signale par la notification d'échec de GitHub Actions.
- **La suite canari** contient six bugs volontaires, chacun associé au contrôle qui doit l'attraper : deux pour `tests` (un nombre flottant dans le noyau ; une vente sans écriture de taxe), un pour `imports`, un pour `proprietes`, un pour `rejeu`, un pour `mutation` (plan détaillé, point 29). Chaque nuit, elle applique chaque bug à une copie de `main` et vérifie que le contrôle visé échoue.

### 11. L'indicateur avancé

Un test marqué `mesure`, sous `tests/` pour la même raison que l'outil de régénération (Technical Plan, point 8), mesure les ticks par seconde de `step` et de `observe` (une observation par acteur et par tick), sans serveur. Le monde a la taille de ceux de l'entraînement : le niveau 1, §8, dit « quelques dizaines d'entités », et M1 retient trois systèmes et 30 PNJ, un vaisseau chacun. Les ordres des PNJ sont calculés hors du temps mesuré. Le test affiche le résultat ; rien ne dépend de sa valeur.

### 12. Les identifiants fixés par M1

Ils remplacent « à fixer au niveau 2 de M1 » dans le glossaire.

| Terme | Identifiant du code |
| :-- | :-- |
| référence scriptée | `scripted_miner` (`policy_id`) |
| type d'acteur | `ActorKind` : `HUMAN`, `AI_PLAYER`, `NPC` |
| hôte des PNJ | `NpcHost` |
| observation | `Observation` |
| phase | `Phase` : `MOVEMENT`, `MINING`, `TRADE`, `COMBAT`, `SETTLEMENT` |
| réception | `Reception` |
| validation sans état | `validate_orders` |
| ordre | `Order` |
| catégorie d'ordre | `OrderCategory` : `PLAYER`, `SYSTEM`, `ADMIN` |
| journal des ordres soumis | `OrderLog` |
| code de refus | `RefusalCode` |
| résultat d'ordre | `OrderResult` |
| budget d'actions | `action_budget` |
| quota d'ordres | `ORDER_QUOTA_PER_TICK` (remplace le nom provisoire `K_ordres`) |
| mode rejeu | `replay_mode` |
| état | `State` |
| générateur à clé | `keyed_draw` |
| instantané | `Snapshot` |
| événement | `Event` |
| classe de visibilité | `Visibility` : `PUBLIC`, `CORPORATION`, `PRIVATE`, `ADMIN` |
| empreinte | `Fingerprints` (une valeur par composant) |
| empreinte de référence | `reference_fingerprints` |
| messages du protocole | `SubmitOrders`, `TickUpdate` |
| registre | `Ledger` |
| écriture | `LedgerEntry` |
| compte du registre | `Account`, de type `AccountKind` : `ISSUANCE`, `DESTRUCTION`, `ESCROW`, `PERSONAL_WALLET`, `CORPORATION_WALLET` |
| émission | `AccountKind.ISSUANCE` |
| destruction | `AccountKind.DESTRUCTION` |
| masse monétaire | `money_supply` |
| séquestre | `AccountKind.ESCROW` |
| motif | `Reason` : `ORE_SALE`, `SALE_TAX` (le « motif du tirage » d'un tirage à clé est une simple chaîne, pas un `Reason`) |

M1 ajoute aussi au glossaire le terme **gisement** (`Deposit`), et le terme **ordre soumis** (`SubmittedOrder`).

### 13. Les interfaces

Les définitions d'étapes des scénarios sont écrites avant le code et figent ces noms. Les types sont des `msgspec.Struct` figés (`frozen=True`) ; les champs sont donnés dans l'ordre d'encodage. Tout type dont `schema` a besoin (`Activity`, `LedgerEntry`) est défini dans `schema` et réutilisé par `core`, car `schema` n'importe pas `core` (contrat d'imports, niveau 1, §1). `Int64` est `Annotated[int, msgspec.Meta(ge=-2**63, le=2**63 - 1)]` ; `Id` est `Annotated[int, msgspec.Meta(ge=1, le=2**63 - 1)]` ; les deux sont définis dans `schema/types.py`. La classe de visibilité de chaque champ d'entité suit le Technical Plan, point 5 ; elle est déclarée par une fonction `visible(classe)` de `schema/visibility.py`, qui renvoie la métadonnée.

**Libellés neutres** (`core/world.py`, `label(table, id)`) : `system_<id>`, `deposit_<id>`, `station_<id>`, `actor_<id>`, `ship_<id>` ; minerai : `ore_` suivi de la lettre de rang `id` (1 → `ore_a`, 2 → `ore_b`).

**`schema`**

```text
visibility.py   Visibility(enum.Enum) ; visible(v: Visibility) -> msgspec.Meta
actors.py       ActorKind(enum.Enum) ; Activity(enum.Enum) : IDLE, EN_ROUTE, MINING
orders.py       OrderCategory(enum.Enum)
                Move(ship_id: Id, target_system_id: Id)             tag "move"
                Mine(ship_id: Id, ore_id: Id)                       tag "mine"
                Sell(ship_id: Id, ore_id: Id, quantity: Int64)      tag "sell"
                CreateCharacter(actor_kind: ActorKind)              tag "create_character"
                Command = Move | Mine | Sell | CreateCharacter
                Order(actor_id: Id, number: Int64, category: OrderCategory,
                      policy_id: str | None, policy_version: Int64 | None, command: Command)
                OrderId(actor_id: Id, tick: Int64, number: Int64)
                SubmittedOrder(tick: Int64, sender_actor_id: Id | None, order: Order,
                               reception_refusal: RefusalCode | None)   (sender_actor_id None : le serveur)
                ORDER_QUOTA_PER_TICK: int = 5
                validate_orders(orders: tuple[SubmittedOrder, ...]) -> tuple[RefusalCode | None, ...]
results.py      RefusalCode(enum.Enum) : UNKNOWN_SHIP, NOT_OWNER, SHIP_EN_ROUTE, UNKNOWN_SYSTEM,
                      ALREADY_THERE, NO_DEPOSIT_FOR_ORE, DEPOSIT_EMPTY, CARGO_FULL, NOT_AT_STATION,
                      QUANTITY_NOT_POSITIVE, QUANTITY_EXCEEDS_CARGO, NO_ACTION_LEFT, SUPERSEDED,
                      INVALID_FORMAT, DUPLICATE_NUMBER, QUOTA_EXCEEDED, ACTOR_MISMATCH, FORBIDDEN_CATEGORY
                OrderResult(recipient_actor_id: Id, order_id: OrderId, accepted: bool,
                            refusal: RefusalCode | None, text: str, budget_left: Int64)
ledger.py       AccountKind(enum.Enum) ; Reason(enum.Enum)
                LedgerEntry(debit_account_id, credit_account_id, amount, reason: Reason,
                            cause: OrderId | None)
events.py       EVENT_SCHEMA_VERSION = 0
                CharacterCreated(actor_id: Id, actor_kind: ActorKind, ship_id: Id)  tag "character_created"
                OrderRefused(order_id: OrderId, refusal: RefusalCode)             tag "order_refused"
                Departed(ship_id: Id, system_id: Id)                              tag "departed"
                Arrived(ship_id: Id, system_id: Id)                               tag "arrived"
                MiningStarted(ship_id: Id, ore_id: Id, rate: Int64)               tag "mining_started"
                MiningEnded(ship_id: Id, quantity: Int64)                         tag "mining_ended"
                Sale(ship_id: Id, ore_id: Id, quantity: Int64, price: Int64,
                     payment: Int64, tax: Int64)                                  tag "sale"
                DepositRegenerated(deposit_id: Id, stock: Int64)                  tag "deposit_regenerated"
                LedgerEntryRecorded(entry: LedgerEntry)                           tag "ledger_entry_recorded"
                Event(tick: Int64, seq: Int64, event_schema_version: Int64, rules_version: str,
                      actor_id: Id | None, actor_kind: ActorKind | None,
                      policy_id: str | None, policy_version: Int64 | None,
                      causation_id: OrderId | None, visibility: Visibility, payload: <union des neuf types>)
                event_json_schema() -> dict[str, object]
observation.py  SystemView, DepositView, StationView, ActorView (champs publics)
                OwnShipView (tous les champs de Ship, mêmes noms) ; OtherShipView (champs publics de Ship)
                (StationView reprend ore_prices ; wallet_balance est le balance du portefeuille personnel de l'acteur)
                Observation(tick: Int64, actor_id: Id, systems, deposits, stations, actors,
                            own_ships, other_ships, wallet_balance: Int64, action_budget: Int64,
                            events: tuple[Event, ...], results: tuple[OrderResult, ...])
protocol.py     PROTOCOL_VERSION = 1
                SubmitOrders(protocol_version: Int64, orders: tuple[Order, ...])
                TickUpdate(protocol_version: Int64, observation: Observation)
                Connection(typing.Protocol) : submit(message: SubmitOrders) -> None ;
                                              async next_update() -> TickUpdate
                SyncClient(typing.Protocol) : on_update(update: TickUpdate) -> SubmitOrders | None
```

**`core`**

```text
tunables.py     Tunables(jump_ticks, mining_rate, cargo_capacity: Int64, ore_prices: tuple[Int64, ...],
                         tax_rate_bp, deposit_stock, regen_ticks, budget_regen, budget_max: Int64)
                (ore_prices, comme Station.ore_prices et Ship.cargo, est indexé par identifiant de minerai moins un)
state.py        System(id, neighbors: tuple[Id, ...]) ; Deposit(id, system_id, ore_id, stock)
                Station(id, system_id, ore_prices: tuple[Int64, ...]) ; Actor(id, kind: ActorKind, action_budget)
                Ship(id, owner_id, system_id, capacity, activity: Activity, route: tuple[Id, ...],
                     ticks_to_next_jump, cargo: tuple[Int64, ...], mining_ore_id: Id | None,
                     mined_since_start)
                LastTick(events: tuple[Event, ...], results: tuple[OrderResult, ...])
                State(tick, systems, deposits, stations, actors, ships, ledger: Ledger, last_tick: LastTick)
ledger.py       Account(id, kind: AccountKind, owner_id: Id | None, balance)
                Ledger(accounts: tuple[Account, ...], tick_entries: tuple[LedgerEntry, ...],
                       issued_by_reason: tuple[Int64, ...], destroyed_by_reason: tuple[Int64, ...])
                (les compteurs sont indexés dans l'ordre de déclaration de Reason ; LedgerEntry vient de schema)
                money_supply(ledger) -> int ; post(ledger, entry) -> Ledger
arith.py        div_trunc(a, b), rem_trunc(a, b), mul_div_trunc(a, b, c), mul_div_ceil(a, b, c) -> int
keyed_random.py keyed_draw(world_seed, tick, entity, motif: str, attempt: int = 0) -> int
                keyed_below(world_seed, tick, entity, motif: str, n: int) -> int
world.py        generate(world_seed: int, tunables: Tunables) -> State ; label(table: str, id: int) -> str
step.py         Phase(enum.Enum)
                step(state, orders: tuple[SubmittedOrder, ...], world_seed: int, tunables: Tunables)
                    -> tuple[State, tuple[Event, ...]]
observe.py      observe(state: State, actor_id: int) -> Observation
fingerprints.py Fingerprints(tick: Int64, systems, deposits, stations, actors, ships, ledger, last_tick: str)
                (les composants sont tous ces champs sauf tick)
                fingerprints(state: State) -> Fingerprints
snapshot.py     SNAPSHOT_SCHEMA_VERSION = 1   (replay_mode, mode rejeu du client, n'est construit qu'à M3)
                Snapshot(snapshot_schema_version, rules_version: str, world_seed, commit: str,
                         worktree_dirty: bool, state: State) ; encode / decode (MessagePack)
version.py      RULES_REVISION: int ; tunables_fingerprint(t: Tunables) -> str ;
                rules_version(t: Tunables) -> str
```

**`server`, `clients`, `policies`, `tools`**

```text
server/tunables_loader.py  load_tunables() -> Tunables   (msgspec.toml.decode(..., type=Tunables))
server/reception.py        Reception.receive(sender_actor_id: int, message: SubmitOrders, tick: int)
                               (applique validate_orders et remplit reception_refusal)
                               -> tuple[SubmittedOrder, ...]
server/order_log.py        OrderLog.create(path, rules_version, world_seed, commit, worktree_dirty) ;
                           append(orders: tuple[SubmittedOrder, ...], fingerprints: Fingerprints) ;
                           orders_by_tick() -> tuple[tuple[SubmittedOrder, ...], ...] ;
                           export_jsonl(path) ; import_jsonl(path) -> en-tête et ordres par tick
                           (l'en-tête porte aussi le dernier tick de la partie)
server/game.py             Game(runs_dir: Path, world_seed: int, tunables: Tunables, period_s: float = 1.0)
                           (crée runs_dir/<AAAAMMJJ-HHMMSS-micro>/ ; les tests passent un dossier temporaire)
                           create_character(kind: ActorKind) -> int ; connect(actor_id) -> Connection ;
                           attach(actor_id, client: SyncClient) ; advance(n: int) -> None ;
                           async run() -> None
policies/scripted_miner.py decide(observation: Observation) -> tuple[Order, ...]
clients/npc_host.py        NpcHost(actor_id, policy) : on_update(update) -> SubmitOrders | None
clients/textual_app.py     FourxApp(textual.app.App)
tools/replay.py            replay_orders(initial: State, orders_by_tick, world_seed, tunables)
                               -> tuple[tuple[Fingerprints, ...], tuple[Event, ...]]
                           python -m fourx.tools.replay <dossier> [--export-fingerprints <fichier>]
                               (code de sortie 0 si les empreintes concordent, 1 sinon)
tools/divergence.py        first_divergence(a, b: Sequence[Fingerprints]) -> tuple[int, tuple[str, ...]] | None
                           (une suite d'empreintes de référence, reference_fingerprints, se compare de même)
                           python -m fourx.tools.divergence <A> <B>   (A et B : dossiers ou fichiers d'empreintes ;
                               affiche « tick <n> : <composants> », ou « aucune divergence » ; code 1 si divergence)
tools/economy.py           WindowStats(first_tick, issued_by_reason, destroyed_by_reason,
                                       money_supply_growth, money_supply_end)
                           window_stats(events: Iterable[Event], window: int = 1000) -> tuple[WindowStats, ...]
```

Les noms des composants affichés par l'outil de divergence sont ceux des champs de `Fingerprints` (`ledger` pour le registre).

## Alternatives Considered

Ces alternatives ont été pesées pendant la rédaction et la revue de ce document. Les alternatives d'architecture sont dans le niveau 1, et celles qui portent sur les règles du jeu dans la [RFC du brainstorm](./mmo-gestion-spatiale-ia.md).

### Alternative A : une perte de vaisseau dès M1 (accident en transit, ou usure et réparation)

*   **Avantages :** un enjeu au transport ; avec l'usure, une sortie d'argent qui aide les fourchettes économiques. La RFC plaçait la perte de vaisseau dans la tranche 0.
*   **Inconvénients :** il faut une règle d'achat de vaisseau, et la perte de la cargaison change l'invariant 3 du niveau 1, §4, donc une ADR.
*   **Raison du rejet :** le propriétaire a choisi le minimum dans le cadre du niveau 1, qui ne l'exige pas. Retenu : aucune perte à M1.

### Alternative B : réduire les contrôles de M1 par une ADR (reporter la mutation et la suite canari)

*   **Avantages :** un prototype jouable plus tôt ; l'outillage de vérification représente une grande part du jalon.
*   **Inconvénients :** des tests écrits par l'agent de code qui ne vérifient rien passeraient inaperçus, alors que le propriétaire ne lit pas le code.
*   **Raison du rejet :** le propriétaire veut le minimum **dans le cadre déjà fixé**, sans redéfinir le niveau 1. Retenu : tous les contrôles de M1 du niveau 1.

### Alternative C : des ticks avancés à la demande du joueur

*   **Avantages :** pas d'attente ; le propriétaire avance au rythme de sa lecture.
*   **Inconvénients :** le client devrait commander l'horloge par un message de protocole nouveau, qui n'aurait plus de sens dans un monde partagé.
*   **Raison du rejet :** hors du cadre du niveau 1, §2, qui ordonne le tick autour de la réception des ordres. Retenu : une horloge du serveur, dont la période est un paramètre.

### Alternative D : `cosmic-ray` 8.7.0 pour la mutation

*   **Avantages :** il lance une commande de test quelconque, ce qui l'isole mieux de pytest et de `pytest-bdd`.
*   **Inconvénients :** plus de configuration, et un script de rapport à écrire pour comparer le score à `main`.
*   **Raison du rejet :** choix du propriétaire, qui préfère moins de configuration au départ. Retenu : `mutmut` 3.8.0, avec le risque connu d'une casse à chaque montée de pytest.

### Alternative E : une copie de l'état à chaque modification

*   **Raison du rejet :** le niveau 1 (alternative R) retient par défaut une nouvelle table par phase du tick, et rien à M1 ne justifie d'en changer.

### Alternative F : la partie de référence à la racine du paquet, ou une suite d'ordres écrite à la main

*   **Avantages :** à la racine (`fourx/reference.py`), les outils se lancent par `python -m`, hors de pytest ; une suite d'ordres écrite à la main reste dans `tools`.
*   **Inconvénients :** la racine du paquet n'est surveillée par aucun contrat d'imports ; une suite d'ordres écrite à la main ne représente plus une vraie partie après un changement de règle, et doit être réécrite.
*   **Raison du rejet :** choix du propriétaire. Retenu : la partie de référence est jouée par des PNJ, l'outil de régénération et l'indicateur avancé vivent sous `tests/` et se lancent par pytest ; son journal est enregistré et rejoué (solution retenue à l'alternative H).

### Alternative G : des gisements inépuisables

*   **Avantages :** le minimum ; aucune égalité à départager à M1 ; c'était la version du premier brouillon.
*   **Inconvénients :** aucun mineur n'aurait de raison de changer de gisement, ni de se méfier des autres mineurs sur le même gisement.
*   **Raison du rejet :** décision du propriétaire du 2026-11-06 : les gisements sont finis et se régénèrent. Retenu : un stock par gisement, régénéré tous les `regen_ticks` ticks.

### Alternative H : rejouer la partie de référence avec ses PNJ à chaque contrôle

*   **Avantages :** pas de journal enregistré dans le dépôt ; le contrôle vérifie aussi le serveur et le PNJ.
*   **Inconvénients :** les empreintes de référence dépendent alors du PNJ, de l'hôte des PNJ et du serveur : un changement de l'un d'eux, sans changement de règle, oblige à monter `RULES_REVISION`. `rules_version` ne dirait plus si les règles ont changé, alors que M4 l'enregistre pour chaque entraînement et que M5 le compare au déploiement.
*   **Raison du rejet :** proposition de l'agent de code. Retenu : le journal de la partie de référence est exporté à la régénération des références, au format versionné du journal des ordres soumis, et le contrôle `rejeu` le rejoue par `step` seul. Le serveur et le PNJ restent vérifiés par les scénarios et par leurs tests.

### Alternative I : garder tout l'historique des écritures dans l'état

*   **Avantages :** l'état contient tout le registre, sans recours aux événements.
*   **Inconvénients :** l'empreinte du registre réencode tout l'historique à chaque tick, donc le coût total d'une partie croît comme le carré de son nombre de ticks ; chaque phase recopie l'historique, et l'instantané du monde en ligne grossirait sans limite à M5.
*   **Raison du rejet :** proposition de l'agent de code. Retenu : soldes, écritures du tick et compteurs cumulés dans l'état ; l'historique dans les événements (Technical Plan, point 3).

--------------------------------------------------------------------------------

## Non-Functional Requirements

*   **Secrets :** M1 n'introduit aucun secret. La relecture de nuit de la protection utilise une route publique, avec le `GITHUB_TOKEN` en lecture seule. Les graines des parties de test et de la partie de référence sont dans le dépôt : ce ne sont pas des graines du monde en ligne, qui n'existe qu'à M5. Les dossiers de parties (`runs/`) et de mutation (`mutants/`) sont ignorés par git.
*   **Performance :** l'indicateur avancé est mesuré (Technical Plan, point 11) ; il ne déclenche rien avant M4.
*   **Durée de la CI :** le rejeu de 100 000 ticks et la mutation n'ont pas encore de durée mesurée. Le plan détaillé, point 28 bis, les mesure sur chaque pull request du palier 3 ; au premier dépassement de 30 minutes par tâche, l'agent de code s'arrête et le signale au propriétaire avant de continuer.

## Risks & Mitigations

| Risque | Effet | Signal | Parade |
| :-- | :-- | :-- | :-- |
| Des définitions d'étapes ne vérifient pas ce que dit le scénario (niveau 1, risque daté M1) | Une fonctionnalité fausse passe pour validée | Mutation | Mutation de tout `core` quand des définitions d'étapes changent (Technical Plan, point 10) ; revue EGM sans contexte ; le risque résiduel est accepté (niveau 1) |
| Fuite d'un champ de données caché par `observe` (niveau 1, risque daté M1) | Avantage injuste, ou joueur IA entraîné sur une information invisible | Tests de propriétés | Classe de visibilité déclarée sur chaque champ, filtre générique, test générique entre vues et état (Technical Plan, point 5 ; plan détaillé, point 19) |
| Une montée de Python ou de `msgspec` change les empreintes (niveau 1, risque daté M1) | Faux échecs de rejeu, ou références recalculées à tort | Rejeu en CI | Versions épinglées dans `pyproject.toml` et figées par `uv.lock` ; une montée de `msgspec` est un changement d'encodage explicite, avec régénération des références et révision augmentée |
| Une montée de pytest casse `mutmut` | Le contrôle de mutation ne tourne plus | Tâche `mutation` en échec | pytest plafonné sous 9.2 ; toute montée de pytest est vérifiée avec `mutmut` avant d'être acceptée ; repli : alternative D |
| La mutation donne un score instable | Échecs au hasard d'un contrôle obligatoire | Score différent sur deux lancements du même commit | Profil `hypothesis` sans hasard et sans délai (Technical Plan, point 10) |
| Le code instrumenté par `mutmut` fausse un test | Tous les mutants passent pour tués, ou aucun | Lancement de contrôle de `mutmut` en échec | Le test de déterminisme statique et `tests/outillage` sont exclus de la mutation (plan détaillé, point 5) : `mutmut` 3.8.0 réécrit chaque fonction avec des imports ajoutés et des mutants qui emploient `/` (constaté le 2026-11-06) |
| La configuration de `mutmut` est contournée par une table `[tool.mutmut]` de `pyproject.toml` | Le contrôle de mutation est affaibli | `mutation.py` ; étiquette « fichiers protégés modifiés » | `pyproject.toml` est protégé, et `mutation.py` échoue si cette table existe (plan détaillé, point 9) |
| L'épuisement et le départage ne sont jamais exécutés par la partie de référence | Un défaut de départage échappe au contrôle `rejeu` | — | Scénarios et tests de propriétés à stock bas ; le bug volontaire de la suite canari vise le placement des sites, toujours exécuté |
| Une pull request de fonctionnalité casse un bug volontaire de la suite canari | Le contrôle de nuit `canari` échoue sans qu'un contrôle ne le signale avant la fusion | Tâche `canari` en échec | Les bugs volontaires sont ancrés sur des symboles (nom de fonction), pas sur des lignes ; la nuit suivante, l'agent de code corrige l'ancre par une pull request protégée |
| Les tâches de CI dépassent 30 minutes | Pull requests lentes, contrôle trop coûteux à garder | Mesure du plan détaillé, point 28 bis | Arrêt et signalement au propriétaire avant de continuer |
| Entre les paliers 2 et 4, une pull request en échec est fusionnée | Une régression entre dans `main` | Tâches en échec sur la pull request | Le propriétaire ne fusionne pas une pull request en échec ; l'intervalle se ferme au palier 4 |
| Entre les paliers 2 et 4, l'étiquette « références régénérées » est retirée | Une régénération des références passe sans attention particulière | Historique des étiquettes | Le contrôle de garde exige quand même la montée de révision ; le hook est mis à jour au palier 4 (plan détaillé, point 31 ter) ; risque accepté pendant cet intervalle |
| Entre le volet C et le palier 4, `tests/rejeu/**` et `tests/economie/**` ne sont pas protégés | Une pull request de fonctionnalité pourrait affaiblir le rejeu ou les fourchettes sans étiquette | Revue des pull requests par le propriétaire | Protection au palier 4 (plan détaillé, point 31 bis) ; risque accepté pendant cet intervalle, comme le niveau 1 l'accepte pour le code avant M1 |
| `duckdb` se compile depuis ses sources sous Python 3.15 | Chaque tâche de CI ralentit de plusieurs minutes | Durée de `uv sync` | Groupe `notebooks` que la CI n'installe pas (plan détaillé, point 14) |
| Le PC d'entraînement est indisponible à la fin du jalon | L'objectif 2 n'a pas de preuve sur le PC d'entraînement | Compte rendu incomplet | Le jalon n'est pas livré tant que la sortie manque ; aucune adresse ni aucun identifiant n'entre dans le dépôt |

## Additional Resources

*   [Niveau 1](./architecture-niveau-1.md), [RFC du brainstorm](./mmo-gestion-spatiale-ia.md), [glossaire](../glossaire.md), [document de M0](./niveau-2-m0-garde-fous.md).
*   Essais du 2026-11-02, hors du dépôt : `mutmut` 3.8.0 et `cosmic-ray` 8.7.0 sous Python 3.15 ; lecture du chargement de la configuration de `mutmut` 3.8.0 (`pyproject.toml` d'abord, sinon section `[mutmut]` de `setup.cfg`).
*   Essais du 2026-11-06, hors du dépôt, sous Python 3.15.2 : lecture du code de `mutmut` 3.8.0 (clés `source_paths`, `only_mutate`, `do_not_mutate`, `also_copy`, `pytest_add_cli_args` ; filtrage de `mutmut run` par motifs de noms de mutants ; `export-cicd-stats` ne donne que des totaux ; sortie de `mutmut results --all true`) et une mutation d'un petit projet ; métadonnées `msgspec.Meta(extra=...)` relues par `msgspec.inspect.type_info` sur `msgspec` 0.22.0 ; route `GET /repos/EZPK/4X/branches/main` lue sans jeton.
*   Rapports de la revue EGM de ce document : `docs/revues/2026-11-06-niveau-2-m1-noyau/`.

## Future Improvements

*   **Le mode rejeu du client Textual**, à M3, avec la vidéo rendue depuis un rejeu.
*   **Le journal public de chaque corporation** (niveau 1, §4), à M6 : il sera construit à partir des événements « écriture du registre », puisque l'état ne garde que les écritures du tick.
*   **Une seconde partie de référence, contrainte par le stock** (plusieurs PNJ sur un gisement, `deposit_stock` bas), si les scénarios et les tests de propriétés ne suffisent pas à couvrir l'épuisement et le départage.

--------------------------------------------------------------------------------

## Detailed Implementation Plan

**Ordre des pull requests.** `CLAUDE.md` impose une pull request de scénarios fusionnée avant chaque pull request de fonctionnalité, et une seule pull request de chaque type ouverte à la fois. M1 avance donc en cinq paliers :
1. décision et documents (pull request protégée) ;
2. outillage de M1 (pull request protégée) : les nouvelles tâches de CI tournent, sans être encore obligatoires ;
3. trois volets de jeu, chacun en deux pull requests : scénarios, puis fonctionnalité ;
4. contrôles obligatoires, contrôles de nuit et suite canari (pull request protégée), puis la commande de protection, lancée par le propriétaire ;
5. compte rendu et livraison.

Entre les paliers 2 et 4, les nouvelles tâches ne bloquent pas la fusion : le propriétaire ne fusionne pas une pull request dont l'une des nouvelles tâches est en échec. C'est le seul intervalle où cette règle ne repose que sur lui ; il se ferme au palier 4, parce qu'une tâche ne peut être rendue obligatoire qu'une fois que le code qu'elle vérifie existe. Pendant cet intervalle, une nouvelle tâche qui ne trouve encore aucun test (code de sortie 5 de pytest) réussit, et le dit (point 8) ; le palier 4 retire cette tolérance (point 31 bis).

**Versions.** Chaque nouvelle dépendance est la dernière version publiée il y a au moins 14 jours à la date de la pull request du palier 2 (règle du document de M0, Technical Plan, point 1). Essayées sous Python 3.15 : `msgspec` 0.22.0, `textual` 8.2.8, `hypothesis` 6.170.2, `marimo` 0.25.2, `mutmut` 3.8.0 (2026-11-02), `duckdb` 1.5.6 (compilé depuis ses sources, en plusieurs minutes, puis `select 42` essayé). `hypothesis` 6.170.2 a été publié le 2026-10-19 à 04 h 17 UTC : la date limite `exclude-newer` doit donc être postérieure (`uv` le refuse avec `exclude-newer` = 2026-10-19, constaté le 2026-11-06). Au palier 2, l'agent de code :
- fixe `exclude-newer` à la date de la pull request moins 14 jours ;
- relit les versions à cette date, et épingle chaque nouvelle dépendance en `==` dans `pyproject.toml` ;
- plafonne pytest : `pytest>=9.1.1,<9.2` ;
- si une version diffère de celles essayées, refait l'essai `mutmut` avant de l'adopter.

### Palier 1 : décision et documents (pull request protégée)

#### 1. `docs/designs/niveau-2-m1-noyau.md` (Create)

*   **Type / Scope :** ce document, chemin protégé.
*   **Proposed Changes :** le contenu de ce brouillon, au statut Proposed, puis la revue EGM complète (étapes 5 à 9 : prise de recul, test de compréhension, critique, prise de recul intermédiaire, préparation à l'implémentation) avec ses rapports dans `docs/revues/2026-11-06-niveau-2-m1-noyau/`. Le propriétaire décide du passage à Approved.

#### 2. `docs/feuille-de-route.md` (Modify)

*   **Type / Scope :** feuille de route, chemin protégé.
*   **Proposed Changes :** M1 passe à « en revue » avec la pull request du document, puis à « approuvé » sur décision explicite du propriétaire.

#### 3. `docs/glossaire.md` (Modify)

*   **Type / Scope :** glossaire, chemin protégé. Dans la pull request protégée du point 1, une fois le document approuvé.
*   **Proposed Changes :** chaque « à fixer au niveau 2 de M1 » est remplacé par l'identifiant du Technical Plan, point 12 ; `K_ordres` devient `ORDER_QUOTA_PER_TICK`, et la mention « nom provisoire » disparaît ; les entrées « gisement » (`Deposit`) et « ordre soumis » (`SubmittedOrder`) sont ajoutées . La colonne « Lien » renvoie à ce document pour les identifiants qu'il fixe.

#### 3 bis. `.github/chemins-proteges.txt` et `tests/outillage/test_garde.py` (Modify)

*   **Type / Scope :** liste des chemins protégés et son test, chemins protégés. Dans la pull request protégée du point 1.
*   **Proposed Changes :** ajouter `pyproject.toml`, `uv.lock` et `.gitignore` (Technical Plan, point 1) ; `test_vraie_liste_des_chemins_proteges` passe de 22 à 25 motifs et vérifie que ces trois fichiers sont couverts.

### Palier 2 : outillage de M1 (pull request protégée)

#### 4. `.github/chemins-proteges.txt` et `tests/outillage/test_garde.py` (Modify)

*   **Type / Scope :** liste des chemins protégés et son test.
*   **Proposed Changes :** ajouter `setup.cfg` (configuration de la mutation), `tests/conftest.py` (profil `hypothesis`), `tests/references/**` (journal enregistré et empreintes de référence) et `tests/core/test_determinisme_statique.py` (créé dans cette même pull request, point 7 bis) ; le compte attendu par `test_vraie_liste_des_chemins_proteges` passe à 29. `tests/rejeu/**` et `tests/economie/**` ne sont protégés qu'au palier 4 (point 31 bis), parce qu'ils sont créés par la pull request de fonctionnalité du volet C, qui n'a pas le droit de toucher un chemin protégé. Le notebook de `notebooks/` n'y entre pas : il affiche des chiffres, il ne contrôle rien.

#### 5. `setup.cfg` (Create)

*   **Type / Scope :** configuration de `mutmut`, chemin protégé. Un fichier à part, comme les autres outils (document de M0, alternative K).
*   **Proposed Changes :** section `[mutmut]`, une valeur par ligne pour les listes :
    - `source_paths` = `src/fourx` ;
    - `pytest_add_cli_args_test_selection` = `tests` ;
    - `pytest_add_cli_args` = `-m`, `not rejeu and not lent and not mesure`, `--ignore=tests/outillage`, `--ignore=tests/core/test_determinisme_statique.py` (le code instrumenté par `mutmut` contient des imports ajoutés et des `/` ; `tests/outillage` lit `.github/` et `.claude/`, absents de la copie de travail de `mutmut`) ;
    - `do_not_mutate` = `src/fourx/__main__.py`, `src/fourx/clients/textual_app.py` (interface, couverte par les scénarios à travers le protocole, pas par des assertions sur l'écran) ;
    - au premier lancement de `mutmut`, vérifier que `pytest.ini` (et donc `pythonpath = .`) est présent dans `mutants/` ; sinon ajouter `also_copy` = `pytest.ini`.

#### 6. `.gitignore` (Modify)

*   **Type / Scope :** fichiers ignorés, chemin protégé (point 3 bis).
*   **Proposed Changes :** ajouter `/runs/` (dossiers de parties) et `/mutants/` (copie de travail de `mutmut`).

#### 7. `pytest.ini` et `tests/conftest.py` (Modify, Create)

*   **Type / Scope :** configuration des tests, chemins protégés.
*   **Proposed Changes :**
    - `pytest.ini` : déclarer les marques `rejeu` (rejeu de 100 000 ticks), `proprietes` (tests `hypothesis`), `lent` (fourchettes économiques sur 100 000 ticks) et `mesure` (indicateur avancé) ; activer `--strict-markers` (aucune étiquette Gherkin n'est donc permise dans un `.feature`) ; ajouter `pythonpath = .`, pour que les tests importent leurs modules d'aide sous le nom que leur donne `mypy` (`tests.scenarios.steps.steps_noyau`, `tests.rejeu.partie_reference`) : essayé le 2026-11-08 sur un petit projet avec la configuration `mypy` et pytest du dépôt, `mypy` strict ne signale rien et pytest collecte les tests ;
    - `tests/conftest.py` : `settings.register_profile("ci", derandomize=True, database=None, deadline=None)` puis `settings.load_profile("ci")`. Ce conftest racine est chargé par toutes les commandes pytest, `tests/outillage` compris ; un test marqué `mesure` est sauté sauf si `FOURX_MESURE=1`.

#### 7 bis. `tests/core/test_determinisme_statique.py` (Create)

*   **Type / Scope :** test du contrôle `tests`, chemin protégé (point 4), créé au palier 2 : il passe sur un `core` encore vide.
*   **Proposed Changes :** l'analyse de la syntaxe du Technical Plan, point 4, sur les sources de `src/fourx/core/` trouvées depuis la racine du dépôt.

#### 8. `.github/workflows/ci.yml` (Modify)

*   **Type / Scope :** CI, chemin protégé.
*   **Proposed Changes :**
    - `tests-outillage` (tâche de M0, obligatoire) : inchangée jusqu'au palier 4 (Technical Plan, point 1) ;
    - quatre nouvelles tâches, dont le nom est celui de la colonne « Tâche » du Technical Plan, point 10, sans clé `name` et sans `strategy` :
      - `tests` : `uv run pytest -m "not rejeu and not proprietes and not lent and not mesure" --ignore=tests/outillage` ;
      - `rejeu` : trois étapes dans la même tâche : `PYTHONHASHSEED=0 uv run pytest -m rejeu` (qui écrit les empreintes de chaque tick dans `runs/rejeu-0/fingerprints.jsonl`), la même avec `PYTHONHASHSEED=1` (`runs/rejeu-1/`), puis `uv run python -m fourx.tools.divergence runs/rejeu-0/fingerprints.jsonl runs/rejeu-1/fingerprints.jsonl`, qui doit répondre « aucune divergence » ; puis `uv run pytest -m lent` (Technical Plan, point 9) ;
      - `proprietes` : `uv run pytest -m proprietes` ;
      - `mutation` : sur une pull request seulement, `uv run python .github/scripts/mutation.py --base "$BASE" --tete "$HEAD"` (variables déjà définies en tête de `ci.yml`), avec tout l'historique (`fetch-depth: 0`).
    - Jusqu'au palier 4, les commandes pytest des tâches `tests`, `rejeu` et `proprietes` acceptent le code de sortie 5 (aucun test trouvé) et l'écrivent dans le résumé de la tâche ; l'étape de divergence de `rejeu` est sautée, et le dit, tant que les deux fichiers d'empreintes n'existent pas (avant le volet C).

    La tâche `imports` existe déjà et ne change pas. Toutes les actions GitHub restent épinglées par SHA.

#### 9. `.github/scripts/mutation.py` (Create)

*   **Type / Scope :** script de CI, chemin protégé, bibliothèque standard seulement.
*   **Proposed Changes :** `mutation.py --base <commit> --tete <commit> [--tout-core]`, ou `mutation.py --tout-core --plancher-partout` (nuit) :
    - échoue si `pyproject.toml` contient une table `tool.mutmut` (lue avec `tomllib`) ;
    - liste les fichiers `.py` de `src/fourx/` modifiés entre la base et la tête, hors de ceux que `do_not_mutate` exclut (motifs lus par `.github/scripts/motifs.py`) ; si des fichiers de `tests/scenarios/steps/` sont modifiés, ou avec `--tout-core`, ajoute tous les fichiers de `src/fourx/core/` (Technical Plan, point 10) ; s'il n'y a aucun fichier, la tâche réussit et le dit ;
    - lance `mutmut run` avec, comme arguments, les motifs des noms de mutants de ces fichiers (`fourx.core.arith.*`, par exemple), puis lit `mutmut results --all true` et calcule le score de chaque fichier (Technical Plan, point 10) ;
    - fait de même sur le commit de base, dans un `git worktree` temporaire synchronisé par `uv sync --locked`, pour les mêmes fichiers qui y existent ; un fichier nouveau n'a pas de score de base ;
    - échoue si le score d'un fichier est inférieur à celui de la base, ou si un fichier nouveau de `core` ou de `schema` a un score inférieur à 80 % ; avec `--plancher-partout`, ajoute aussi tous les fichiers de `src/fourx/schema/`, ne calcule rien sur une base et applique les 80 % à chaque fichier de `core` et de `schema` ; écrit le tableau des scores dans le résumé de la tâche ;
    - la tête est un commit : pour un bug volontaire de la suite canari, `canaris.py` committe la copie de travail dans un dépôt temporaire avant d'appeler `mutation.py`.

#### 10. `tests/outillage/test_mutation.py` (Create)

*   **Type / Scope :** tests de l'outillage, chemin protégé.
*   **Proposed Changes :** avec la fixture `charger_script` de `tests/outillage/conftest.py`, sans lancer `mutmut` : le refus d'une table `tool.mutmut` ; le choix des fichiers (modifiés, exclus, nouveaux, supprimés, définitions d'étapes modifiées, `--tout-core`) ; la lecture d'une sortie de `mutmut results --all true` d'exemple ; le calcul du score (sans test, non vérifiés, délais dépassés, ignorés, fichier sans mutant) ; la comparaison à la base, le seuil de 80 % et `--plancher-partout`.

#### 11. `.github/workflows/garde.yml` et `.github/scripts/garde.py` (Modify)

*   **Type / Scope :** contrôle de garde, chemins protégés.
*   **Proposed Changes :**
    - la sortie de `garde.py` devient une liste d'étiquettes à poser ou retirer (aujourd'hui une seule décision `etiquette`) ; `garde.yml` les applique une à une ;
    - une pull request qui modifie un fichier de `tests/references/` reçoit en plus l'étiquette « références régénérées » (créée comme celle de M0, par `gh label create`, au premier besoin) ;
    - dans ce cas, `garde.yml` lit, dans la tête, `src/fourx/core/version.py` et la liste de `tests/references/` par `gh api -H "Accept: application/vnd.github.raw+json" repos/EZPK/4X/contents/<chemin>?ref=$HEAD_SHA` (`HEAD_SHA` pris dans le JSON de l'événement, comme la tâche `en-attente`, sans `${{ github.event.* }}` dans un `run:` ni nouveau `checkout`), à chaque exécution, avant que `garde.py` décide ; une réponse 404 (fichier ou dossier absent de la tête) donne un fichier vide ; les deux résultats sont passés à `garde.py` dans deux fichiers ; la base est lue dans la copie déjà récupérée. `garde.py` lit `RULES_REVISION` comme texte (expression régulière, sans importer le code de la branche) : la tâche `garde` échoue si la révision de la tête n'est pas celle de la base plus un, ou si le dossier `tests/references/rules-<révision de la tête>/` n'existe pas, ou si un autre dossier `rules-*` reste.

#### 12. `tests/outillage/test_garde.py` (Modify)

*   **Type / Scope :** tests de l'outillage, chemin protégé.
*   **Proposed Changes :** la nouvelle sortie de `garde.py` ; les cas de l'étiquette « références régénérées » (posée si `tests/references/` change, retirée sinon) ; les cas de la révision (base + 1 accepté ; égal, + 2, dossier manquant, ancien dossier restant refusés), à partir des deux fichiers fournis par `garde.yml` ; `test_workflows.py` vérifie que `garde.yml` reste sans `head.sha }}` ni troisième `checkout`.

#### 13. `tests/outillage/test_workflows.py` (Modify)

*   **Type / Scope :** tests de l'outillage, chemin protégé. Modifié au palier 2, puis au palier 4 (point 31 bis).
*   **Proposed Changes :** au palier 2 : la règle « pas de clé `name` ni de `strategy` » s'applique aussi aux nouvelles tâches de `ci.yml` ; la liste des tâches obligatoires, comparée à `.github/protection-main.json`, ne change pas encore.

#### 14. `pyproject.toml` et `uv.lock` (Modify)

*   **Type / Scope :** dépendances, chemins protégés (point 3 bis).
*   **Proposed Changes :** dépendances d'exécution `msgspec` et `textual` ; dépendances de développement `hypothesis` et `mutmut` ; pytest plafonné ; un groupe à part, `notebooks`, pour `marimo` et `duckdb`, que la CI n'installe pas (`uv sync` installe le groupe `dev` par défaut ; le propriétaire lance `uv sync --group notebooks`). `duckdb` 1.5.6 n'a pas de paquet précompilé pour Python 3.15 : il se compile depuis ses sources, en plusieurs minutes (constaté le 2026-11-02), ce qui ralentirait chaque tâche de CI pour un outil qu'aucun contrôle n'utilise. Versions et `exclude-newer` : en-tête de ce plan. Aucun greffon asynchrone : les tests asynchrones sont des tests synchrones qui appellent `asyncio.run(...)`.

### Palier 3 : les trois volets de jeu

Chaque volet a sa pull request de scénarios (fichiers `.feature` en français et définitions d'étapes, scénarios ajoutés à `tests/scenarios/en_attente.txt`), fusionnée par le propriétaire, puis sa pull request de fonctionnalité, qui écrit le code et retire les entrées de `en_attente.txt`.

**Règles pour les définitions d'étapes**, écrites avant le code :
- elles n'importent le code de `fourx` qu'à l'intérieur des fonctions d'étape, par `importlib.import_module(...)` (dont le résultat est typé `ModuleType`, ce que `mypy` accepte) : un module absent fait échouer le scénario, comme le mécanisme « en attente » l'attend, sans casser `mypy` ni la collecte ;
- elles emploient les noms du Technical Plan, point 13, et les libellés neutres (`system_1`, `ore_a`, `station_1`, `deposit_1`) ;
- `tests/scenarios/test_scenarios.py` (créé au point 15) contient `scenarios(".")` et importe chaque module d'étapes par `from tests.scenarios.steps.steps_<volet> import *  # noqa: F403` (`pythonpath = .`, point 7 ; `ruff` refuse sinon un `import *`).

**Volet A : le noyau, les règles et le registre**

#### 15. `tests/scenarios/noyau.feature` et `tests/scenarios/steps/steps_noyau.py` (Create)

*   **Type / Scope :** pull request de scénarios, chemins protégés.
*   **Proposed Changes :** scénarios appliqués directement à `step`, chacun sur un état construit par l'étape « Étant donné » (carte et sites explicites, sans dépendre de la graine) :
    - un vaisseau se déplace de `system_1` à `system_3` en deux sauts, en `2 × jump_ticks` ticks ;
    - un vaisseau mine `ore_a` jusqu'à remplir sa cargaison, puis passe à l'arrêt ;
    - une vente produit l'écriture de vente et celle de la taxe, et les trois invariants tiennent ;
    - une vente dont la taxe exacte tombe entre deux unités paie l'unité supérieure ;
    - un vaisseau mine un gisement jusqu'à le vider, puis s'arrête ; le gisement revient à `deposit_stock` au tick multiple de `regen_ticks` suivant ;
    - deux vaisseaux minent dans le même tick un gisement dont le stock ne suffit pas aux deux : le départage par tirage à clé décide qui reçoit le reste, et la même partie rejouée donne le même résultat ;
    - deux ventes du même vaisseau dans un tick : seule celle de plus petit numéro est examinée, l'autre est refusée (`SUPERSEDED`) ;
    - un ordre sur le vaisseau d'un autre acteur est refusé (`NOT_OWNER`) ;
    - une vente hors du système de la station est refusée (`NOT_AT_STATION`) ;
    - un ordre au-delà du budget d'actions est refusé (`NO_ACTION_LEFT`).

    Les étapes vérifient aussi les trois invariants après chaque tick. Le fichier `tests/scenarios/test_scenarios.py` est créé ici (document de M0, Technical Plan, point 10).

#### 16. `src/fourx/schema/` (Create)

*   **Type / Scope :** paquet `schema` (le fichier `__init__.py` existe déjà, vide, et ne change pas).
*   **Proposed Changes :** les modules du Technical Plan, point 13 : `types.py`, `visibility.py`, `actors.py`, `orders.py` (`ORDER_QUOTA_PER_TICK` = 5), `results.py`, `ledger.py`, `events.py`, `observation.py`, `protocol.py`.

#### 17. `src/fourx/core/` (Create)

*   **Type / Scope :** paquet `core` (le fichier `__init__.py` existe déjà, vide, et ne change pas).
*   **Proposed Changes :** les modules du Technical Plan, point 13 :
    - `arith.py`, seul module exempté de l'interdiction de `//` et `%` ;
    - `keyed_random.py` ;
    - `tunables.py` et `tunables.toml`. Valeurs de M1 : `jump_ticks` = 5, `mining_rate` = 10, `cargo_capacity` = 100, `ore_prices` = [10, 15], `tax_rate_bp` = 1 000 (10 %), `budget_regen` = 1, `budget_max` = 10, `deposit_stock` = 20 000, `regen_ticks` = 1 000. Ce fichier est une donnée du paquet, lue par le serveur.

      La régénération d'un gisement tous les 1 000 ticks est alignée sur les fenêtres des fourchettes économiques. Avec deux PNJ, au plus 10 200 unités sont extraites par fenêtre (point 27) : aucun gisement ne se vide, et les bornes du point 27 restent valables. Les valeurs du monde en ligne (stock plus large, régénération d'un gisement environ chaque semaine) seront fixées à M5 ;
    - `state.py`, `ledger.py`, `world.py` (génération et placement des sites, Technical Plan, point 2 ; libellés neutres), `step.py`, `observe.py`, `fingerprints.py`, `snapshot.py` ;
    - `version.py` : `RULES_REVISION` = 0 au volet A ; il passe à 1 avec la première création des références (point 26), selon la règle « plus un » du contrôle de garde.

#### 18. `tests/core/` et `tests/schema/` (Create)

*   **Type / Scope :** tests unitaires (contrôle `tests`).
*   **Proposed Changes :**
    - un fichier de test par module des points 16 et 17, dont `validate_orders`, l'export JSON Schema et les messages du protocole ; celui de `keyed_random.py` contient des valeurs attendues figées (clé connue → tirage connu), pour un portage en Rust ;
    - `tests/core/test_entiers_64_bits.py` : tout entier de l'état et de l'instantané tient dans un entier signé de 64 bits, après chaque tick d'une partie générée ;
    - `tests/core/test_versions.py` : l'instantané (`snapshot_schema_version`, `rules_version`, commit), les événements (`event_schema_version`, `rules_version`), les messages du protocole (`protocol_version`) et `rules_version` portent leurs champs de version (objectif 7).

#### 19. `tests/proprietes/` (Create)

*   **Type / Scope :** tests de propriétés (contrôle `proprietes`), marque `proprietes`.
*   **Proposed Changes :**
    - sur des parties générées par `hypothesis` (graine, réglages dont un `deposit_stock` bas et plusieurs vaisseaux sur un même gisement, suite d'ordres valides et invalides) : les trois invariants après chaque tick ; les entiers sur 64 bits ; deux exécutions de la même partie donnent les mêmes empreintes ;
    - visibilité : pour chaque champ de données de chaque vue d'une observation, le champ de même nom de l'entité d'état a une classe visible pour l'acteur (`wallet_balance` est apparié à `Account.balance` du portefeuille personnel, `action_budget` à `Actor.action_budget`) ; aucun champ privé ou d'administration d'un autre acteur n'apparaît.

**Volet B : le serveur, le client et le PNJ**

#### 20. `tests/scenarios/partie.feature` et `tests/scenarios/steps/steps_partie.py` (Create)

*   **Type / Scope :** pull request de scénarios, chemins protégés.
*   **Proposed Changes :** scénarios joués à travers le serveur en mémoire, en mode sans horloge, et le protocole, sans le client Textual :
    - **CUJ 1 :** le propriétaire choisit `ore_b`, envoie son vaisseau le miner, le ramène à la station et vend ; ses mises à jour du tick montrent le trajet, la cargaison, et le paiement et la taxe par l'événement de vente privé ; l'autre acteur ne voit ni le paiement ni la taxe ; le registre contient l'écriture de vente et celle de la taxe ;
    - un ordre soumis sous l'`actor_id` d'un autre acteur est refusé par la réception (`ACTOR_MISMATCH`), et le refus arrive dans l'observation de l'acteur qui l'a soumis ;
    - un ordre d'administration soumis par un client sous son propre `actor_id` est refusé par la réception (`FORBIDDEN_CATEGORY`) ;
    - au-delà de `ORDER_QUOTA_PER_TICK` ordres dans un tick, les plus petits numéros sont gardés (`QUOTA_EXCEEDED` pour les autres) ;
    - le PNJ vend au moins une cargaison en 100 ticks.

#### 21. `src/fourx/server/` (Create)

*   **Type / Scope :** paquet `server` (le fichier `__init__.py` existe déjà, vide).
*   **Proposed Changes :** les modules du Technical Plan, point 13 :
    - `tunables_loader.py` : lit `tunables.toml` (via `importlib.resources`) par `msgspec.toml.decode(..., type=Tunables)` ;
    - `reception.py` ;
    - `order_log.py` : base SQLite `orders.sqlite` en mode WAL, deux tables : `meta` (clé, valeur : `order_log_schema_version` = 1, `rules_version`, `world_seed`, `commit`, `worktree_dirty`) et `ticks` (`tick` entier, clé primaire ; `orders` : encodage MessagePack du tuple des ordres soumis ; `fingerprints` : encodage MessagePack de `Fingerprints`) ; le commit est lu par `git rev-parse HEAD` (« inconnu » hors d'un dépôt git) et l'indicateur par `git status --porcelain` non vide. Export JSONL : une ligne d'en-tête (les valeurs de `meta`, plus le dernier tick, c'est-à-dire le plus grand `tick` de la table `ticks`), puis un ordre soumis par ligne, en JSON `msgspec` ;
    - `events_writer.py` : enregistre les événements v0 en JSONL (`events.jsonl`) ;
    - `game.py` : la partie : création du dossier `runs/<AAAAMMJJ-HHMMSS-micro>/` (microsecondes, pour que deux parties de la même seconde ne se mêlent pas), instantané initial, ordres de création des personnages, horloge (tâche `asyncio`), boucle des ticks, envoi des mises à jour, et le mode sans horloge (Technical Plan, point 6).

#### 22. `src/fourx/policies/scripted_miner.py` et `src/fourx/clients/` (Create)

*   **Type / Scope :** paquets `policies` et `clients`.
*   **Proposed Changes :**
    - `scripted_miner.py` : la politique du Technical Plan, point 7, `policy_id` = `scripted_miner`, `policy_version` = 1 ;
    - `clients/npc_host.py` : `NpcHost` ;
    - `clients/textual_app.py` : `FourxApp`, l'application Textual du Technical Plan, point 7 ;
    - `src/fourx/__main__.py` : `python -m fourx [--graine N]` crée une partie (graine tirée au hasard par `__main__.py` si l'option manque, hors du noyau), un personnage humain et un PNJ, puis `asyncio.run(...)` lance la tâche de l'horloge, la tâche qui transmet les mises à jour à l'hôte des PNJ, et `await app.run_async()`.

#### 23. `tests/server/`, `tests/policies/`, `tests/clients/` (Create)

*   **Type / Scope :** tests unitaires.
*   **Proposed Changes :** réception ; journal (enregistrement, relecture, export et import JSONL) ; `tests/server/test_versions_journal.py` (`order_log_schema_version`, `rules_version`, commit et indicateur dans le journal ; objectif 7) ; sortie JSONL des événements ; boucle des ticks en mode sans horloge ; politique `scripted_miner` sur des observations construites à la main (dont : aucun ordre pendant 10 ticks de minage) ; hôte des PNJ. Le client Textual est testé par le pilote de test de Textual (`async with app.run_test() as pilot`, dans une fonction appelée par `asyncio.run`) : envoi d'un ordre au clavier et affichage d'une mise à jour.

**Volet C : le rejeu, la divergence et l'économie**

#### 24. `tests/scenarios/rejeu.feature` et `tests/scenarios/steps/steps_rejeu.py` (Create)

*   **Type / Scope :** pull request de scénarios, chemins protégés.
*   **Proposed Changes :**
    - une partie jouée à travers le serveur, puis rejouée depuis son instantané initial et son journal, donne les mêmes empreintes à chaque tick, refus compris ;
    - **CUJ 4 :** une partie dont le registre est modifié au tick 50 est signalée par l'outil de divergence au tick 50, composant `ledger`.

#### 25. `src/fourx/tools/` (Create)

*   **Type / Scope :** paquet `tools` (le fichier `__init__.py` existe déjà, vide).
*   **Proposed Changes :** les modules du Technical Plan, point 13 : `replay.py` (`replay_orders` et la commande), `divergence.py`, `economy.py` (`window_stats`).

    L'outil de régénération et l'indicateur avancé ne sont pas dans `tools`, qui ne peut pas importer `policies` ni `clients` (niveau 1, §1) : ils sont au point 27.

#### 26. `tests/references/rules-1/` (Create)

*   **Type / Scope :** références, chemin protégé (point 4). Produites par l'outil de régénération du point 27, dans la pull request de fonctionnalité du volet C : c'est le seul chemin protégé qu'une pull request de fonctionnalité peut modifier (`CLAUDE.md`, circuit des pull requests). La même pull request passe `RULES_REVISION` de 0 à 1.
*   **Proposed Changes :** `orders.jsonl` et `reference.json` (Technical Plan, point 8), pour la révision 1 des règles.

#### 27. `tests/rejeu/partie_reference.py`, `tests/rejeu/test_rejeu.py`, `tests/economie/test_fourchettes.py`, `tests/mesure/test_indicateur_avance.py` (Create)

*   **Type / Scope :** tests du contrôle `rejeu`, tests marqués `lent` et `mesure`, et outil de régénération lancé par pytest. Ils vivent sous `tests/` parce que l'outil de régénération assemble `server`, `clients` et `policies` (choix du propriétaire, Technical Plan, point 8). Le point 26 est produit par ce point.
*   **Proposed Changes :**
    - `partie_reference.py` : la partie de référence : graine 1, deux PNJ joués par l'hôte des PNJ, 100 000 ticks, serveur en mode sans horloge ;
    - `test_rejeu.py` (marque `rejeu`) : importe `tests/references/rules-<RULES_REVISION>/orders.jsonl`, régénère l'état initial par `world.generate(1, tunables)`, rejoue par `replay_orders`, compare `rules_version` et les empreintes tous les 1 000 ticks à `reference.json`, et écrit les empreintes de chaque tick dans `runs/rejeu-<PYTHONHASHSEED>/fingerprints.jsonl` (`runs/rejeu-aleatoire/` si la variable n'est pas définie, comme dans `tests-outillage` avant le palier 4 ; comparées entre elles par la tâche `rejeu`, point 8) ;
    - **outil de régénération :** `FOURX_REGENERER_REFERENCES=1 uv run pytest -m rejeu tests/rejeu/test_rejeu.py`, lancé sur l'ordinateur portable, joue la partie de référence, exporte son journal et ses empreintes dans `tests/references/rules-<RULES_REVISION>/` au lieu de comparer, supprime l'ancien dossier, et affiche le rapport de différences avec la révision précédente. C'est l'outil de régénération que cite `CLAUDE.md` ;
    - `test_fourchettes.py` (marque `lent`) : rejoue le journal enregistré de la partie de référence par `replay_orders`, calcule les grandeurs par `window_stats`, et vérifie, sur chaque fenêtre de 1 000 ticks sauf la première :
      - émission `ORE_SALE` entre 84 000 et 153 000 ;
      - destruction `SALE_TAX` entre 8 400 et 15 300, et égale à la somme des taxes de chaque vente, arrondies vers le haut ;
      - croissance de la masse monétaire entre 75 600 et 137 700 ;
    - `test_indicateur_avance.py` (marque `mesure`, lancé à la main par `FOURX_MESURE=1 uv run pytest -m mesure -s`) : mesure les ticks par seconde de `step` et `observe` sur trois systèmes et 30 PNJ, et affiche le résultat (Technical Plan, point 11).

    **Calcul des bornes** (fait avec un script le 2026-11-02, refait le 2026-11-06 ; à refaire si un réglage change) :
    - durée minimale d'un aller-retour : `2 × jump_ticks + cargo_capacity / mining_rate` = 20 ticks (gisement voisin de la station) ;
    - durée maximale : `4 × jump_ticks + cargo_capacity / mining_rate + 4` = 34 ticks (gisement à deux sauts, et un tick de délai à chacune des quatre décisions, Technical Plan, point 6) ;
    - ventes par PNJ et par fenêtre : au moins 28 (1 000 / 34, arrondi en dessous, moins une vente coupée par la fenêtre), au plus 51 (1 000 / 20, arrondi au-dessus, plus une) ;
    - chaque vente : 100 unités de `ore_b` à 15, soit 1 500 d'émission et 150 de taxe ;
    - deux PNJ : émission de 84 000 à 153 000, destruction de 8 400 à 15 300, croissance de la masse monétaire de 75 600 à 137 700.

#### 28. `notebooks/economie_m1.py` (Create)

*   **Type / Scope :** notebook marimo.
*   **Proposed Changes :** lit le fichier `events.jsonl` d'une partie, appelle `window_stats`, et affiche par fenêtre de 1 000 ticks la masse monétaire, sa croissance, l'émission et la destruction par motif. Il lit aussi les événements avec DuckDB pour les explorer, sans calculer lui-même ces grandeurs.

#### 28 bis. Action — mesure de durée et revue du seuil de mutation

*   **Type / Scope :** action de l'agent de code, sur chaque pull request du palier 3.
*   **Proposed Changes :** relever la durée des tâches `rejeu`, `mutation` et `tests-outillage` (qui lance toute la suite jusqu'au palier 4) dans la description de la pull request ; la mutation la plus longue est celle d'une pull request de scénarios, qui mute tout `core`. Au premier dépassement de 30 minutes, l'agent de code s'arrête et le signale au propriétaire. Sur la pull request de fonctionnalité du volet C, relever aussi la taille de `tests/references/rules-1/`, et les scores de mutation de `core` et `schema` : si l'un d'eux est sous 80 % malgré des tests complets (mutants équivalents), l'agent de code le signale au propriétaire, qui décide du seuil.

### Palier 4 : contrôles obligatoires, contrôles de nuit et suite canari (pull request protégée)

#### 29. `.github/canaris/` et `.github/scripts/canaris.py` (Create)

*   **Type / Scope :** suite canari, chemins protégés.
*   **Proposed Changes :** six bugs volontaires, chacun décrit par un fichier JSON : le contrôle visé, et une liste de modifications (fichier visé ; ancre : début du corps d'une fonction nommée, fin du module, ou expression nommée à remplacer ; texte inséré ou de remplacement). `canaris.py` applique chaque bug par l'analyse de la syntaxe (module `ast`), pas par un patch de lignes, puis lance la commande du contrôle visé, et échoue si cette commande réussit. Table contrôle → commande : celles du point 8.
    - un nombre flottant dans `step` (`core/step.py`) → `tests` ;
    - `core` qui importe `server` → `imports` ;
    - une vente sans écriture de taxe, mais avec le compteur cumulé de destruction augmenté → `tests` (invariants) ;
    - le portefeuille d'un autre acteur laissé dans une observation (`observe`) → `proprietes` ;
    - le placement des sites tiré par `hash()` d'une chaîne au lieu de `keyed_below` (`world.generate`) → `rejeu` (ce tirage a lieu dans chaque partie, et `hash()` d'une chaîne change avec `PYTHONHASHSEED`) ;
    - une fonction insérée à la fin de `core/arith.py` (ancre : le nom de module), et un appel inséré au début de `step` dont aucun test ne vérifie le résultat → `mutation` (`mutation.py --base main --tete <commit de la copie>` : le score de `arith.py` baisse par rapport à `main`).

#### 30. `tests/outillage/test_canaris.py` (Create)

*   **Type / Scope :** tests de l'outillage, chemin protégé.
*   **Proposed Changes :** avec la fixture `charger_script`, sur un petit module d'exemple et non sur `main` : l'application d'un bug par son ancre ; l'échec quand l'ancre manque ; l'échec quand un bug n'est pas attrapé (commande de contrôle remplacée par une commande qui réussit). Que chaque bug s'applique à `main` est vérifié par la tâche de nuit elle-même.

#### 30 bis. `.github/workflows/nuit.yml` (Create)

*   **Type / Scope :** contrôles après fusion, chemin protégé.
*   **Proposed Changes :** déclenché chaque nuit (`cron: "0 3 * * *"`, en UTC) et à la main, sur `main`. Trois tâches :
    - `canari` : `uv run python .github/scripts/canaris.py` ;
    - `mutation-complete` : `uv run python .github/scripts/mutation.py --tout-core --plancher-partout`, échec sous 80 % ;
    - `protection` : `uv run python .github/scripts/protection.py`, qui lit `https://api.github.com/repos/EZPK/4X/branches/main` avec le `GITHUB_TOKEN` en lecture seule (`permissions: contents: read`, aucun nouveau secret ; il évite la limite de 60 requêtes par heure des lectures sans jeton), et échoue si `protected` est faux, si `enforcement_level` n'est pas `everyone`, ou si la liste des contrôles exigés diffère de celle de `.github/protection-main.json`.

    Un échec envoie la notification de GitHub Actions au propriétaire.

#### 31. `.github/protection-main.json` (Modify)

*   **Type / Scope :** protection de `main`, chemin protégé.
*   **Proposed Changes :** ajouter aux contrôles exigés `tests`, `rejeu`, `proprietes`, `imports`, `mutation`. Après la fusion, **le propriétaire** lance `!gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json`. L'agent de code relit ensuite la protection par `gh api repos/EZPK/4X/branches/main/protection` et cite la liste des contrôles exigés, `strict`, `allow_force_pushes` et `allow_deletions`.

#### 31 bis. `.github/workflows/ci.yml`, `.github/chemins-proteges.txt`, `.github/scripts/protection.py`, `tests/outillage/test_garde.py` et `tests/outillage/test_workflows.py` (Modify, Create)

*   **Type / Scope :** CI et ses tests, chemins protégés, dans la même pull request que le point 31.
*   **Proposed Changes :**
    - `ci.yml` : retirer la tolérance du code de sortie 5 de pytest et le saut de l'étape de divergence (point 8) ; limiter `tests-outillage` à `uv run pytest tests/outillage` (Technical Plan, point 1) ;
    - `.github/chemins-proteges.txt` et `tests/outillage/test_garde.py` : ajouter `tests/rejeu/**` et `tests/economie/**` ; le compte attendu passe à 31 ;
    - `protection.py` : le script de la tâche `protection` (point 30 bis), bibliothèque standard seulement, et son test dans `tests/outillage/test_protection.py` sur une réponse d'exemple ;
    - `test_workflows.py` : trois workflows attendus (`ci.yml`, `garde.yml`, `nuit.yml`) ; la liste des tâches obligatoires ajoute `tests`, `rejeu`, `proprietes`, `imports` et `mutation`, en accord avec `.github/protection-main.json`.

#### 31 ter. `.claude/hooks/garde_commandes.py` et `tests/outillage/test_garde_commandes.py` (Modify) — propriétaire

*   **Type / Scope :** hook Claude Code, chemin protégé que l'agent de code n'édite pas. Dans la même pull request que le point 31.
*   **Proposed Changes :** selon la procédure de `CLAUDE.md` : **le propriétaire** lève la règle `deny` sur `.claude/` dans sa copie locale, fait ou demande la modification, puis remet la règle :
    - `REFERENCE_PROTECTION` reçoit la nouvelle liste des contrôles exigés, pour que `test_copies_de_reference_egales_aux_fichiers` reste vrai ;
    - le refus de `gh pr edit --remove-label` couvre aussi l'étiquette « références régénérées ».

    La protection de `main` existe déjà : l'exception d'amorçage reste refermée.

### Palier 5 : compte rendu et livraison

#### 32. `docs/revues/<AAAA-MM-JJ du compte rendu>-compte-rendu-m1/compte-rendu-m1.md` (Create)

*   **Type / Scope :** compte rendu de M1, chemin protégé, par une pull request protégée. Le dossier porte la date de création du compte rendu, et non celle de la revue du document.
*   **Proposed Changes :** pour chaque objectif, le lien vers le contrôle CI ou la sortie de commande qui le prouve ; les essais du point 32 bis ; la sortie du rejeu lancé par le propriétaire sur le PC d'entraînement, sans adresse ni identifiant ; la mesure de l'indicateur avancé ; la durée des tâches de CI ; la décision du propriétaire sur la boucle de jeu.

#### 32 bis. Action — essais des contrôles obligatoires

*   **Type / Scope :** action de l'agent de code, après la commande de protection du point 31, une pull request d'essai à la fois (une pull request de fonctionnalité), fermée sans fusion.
*   **Proposed Changes :**

    | Essai | Branche | Contenu | Attendu |
    | :-- | :-- | :-- | :-- |
    | E1 | `essai-tests` | le bug volontaire « nombre flottant dans `step` » | `tests` en échec, fusion refusée |
    | E2 | `essai-rejeu` | le bug volontaire « placement des sites par `hash()` » | `rejeu` en échec, fusion refusée |
    | E3 | `essai-proprietes` | le bug volontaire « portefeuille d'un autre acteur dans l'observation » | `proprietes` en échec, fusion refusée |
    | E4 | `essai-imports` | le bug volontaire « `core` importe `server` » | `imports` en échec, fusion refusée |
    | E5 | `essai-mutation` | le bug volontaire « fonction non vérifiée dans `arith.py` » | `mutation` en échec, fusion refusée |

    Pour chaque essai, le compte rendu cite le lien du contrôle en échec et le message de refus de fusion.

#### 33. `docs/feuille-de-route.md` (Modify)

*   **Type / Scope :** feuille de route, chemin protégé.
*   **Proposed Changes :** sur décision du propriétaire, M1 passe à « livré » et le champ « Jalon en cours » passe à M2.

### Verification Plan

*   **Installation :** `uv sync --locked`.
*   **Tests :** `uv run pytest tests/outillage`, puis `uv run pytest -m "not rejeu and not proprietes and not lent and not mesure" --ignore=tests/outillage`, puis `-m proprietes`, puis les trois étapes de la tâche `rejeu` (point 8), puis `-m lent`. L'indicateur avancé : `FOURX_MESURE=1 uv run pytest -m mesure -s`.
*   **Analyse statique :** `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run lint-imports`, et la tâche `termes-interdits` du document de M0.
*   **Mutation :** `uv run python .github/scripts/mutation.py --base <base> --tete <tête>` sur chaque pull request ; mutation complète du noyau de nuit, score d'au moins 80 %.
*   **Essais réels :**
    - les essais E1 à E5 (point 32 bis) ;
    - un lancement manuel de `nuit.yml`, qui doit réussir ;
    - un lancement de `canaris.py` où la commande d'un contrôle visé est remplacée par une commande qui réussit : le script doit échouer.
*   **PC d'entraînement :** depuis le commit livré, le propriétaire lance `uv sync --locked`, puis les deux premières étapes de la tâche `rejeu` (point 8) ; la sortie va dans le compte rendu.
*   **Critère de sortie :** chaque élément de la ligne M1 du niveau 1, §11, et chaque objectif de ce document correspondent à une preuve du compte rendu.

*Drafted with EGM*
