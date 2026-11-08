# Étape 6 — test de compréhension

*   **Document :** `docs/designs/niveau-2-m1-noyau.md` (636 lignes ; spécification : lignes 1 à 347 ; plan détaillé : lignes 348 à 636).
*   **Date :** 2026-11-06.
*   **Relecteur :** `egm-comprehension`, sans contexte. Il a d'abord lu le document seul, puis le glossaire et les passages utiles du niveau 1 (§1, §2, §4, §8, §10, alternative R). Aucun fichier modifié.
*   **Verdict :** le document se paraphrase sans trou, et le vocabulaire du projet est presque toujours défini dans le glossaire. En revanche, il contient une contradiction qui empêche d'atteindre l'objectif 8 (B1). Il contient aussi plusieurs écarts avec le niveau 1 (M1, M2, M3, M7, M12) et des points laissés ouverts (M6, M8, M9, M10, M11, M14). C'est contraire à la ligne 38, qui veut qu'un agent de code puisse livrer chaque partie « sans décision ouverte ».

## 1. Paraphrase du relecteur

**Ce que le document propose.** M1 est le premier jalon qui contient des règles du jeu. Il livre une « tranche 0 » jouable hors ligne, dans un seul processus. Le monde est généré à partir d'une graine : trois systèmes reliés en chaîne, deux minerais, chacun dans un seul champ, et une station qui rachète le minerai à prix fixe. Il y a deux acteurs : le propriétaire et un PNJ scripté. Le joueur déplace son vaisseau, mine jusqu'à remplir sa cargaison, revient à la station et vend. Chaque vente crée de l'argent (émission) et prélève une taxe de 10 % arrondie vers le haut (destruction). Les champs s'épuisent et retrouvent leur stock tous les 1 000 ticks.

Le noyau `core` est une fonction pure `step`, sans flottant, sans `/`, sans dictionnaire, avec un tirage aléatoire « à clé » par BLAKE2b et une empreinte par composant de l'état. Autour du noyau viennent :
- les formats versionnés (`schema`) ;
- un serveur en mémoire avec une horloge ;
- un journal SQLite des ordres et des événements JSONL ;
- un client Textual et un hôte de PNJ, qui passent par le même protocole et la même fonction `observe` ;
- un outil de rejeu et de divergence ;
- une partie de référence de 100 000 ticks, dont les empreintes sont figées sous `tests/references/`.

Enfin, cinq contrôles CI deviennent obligatoires (tests, rejeu sous deux `PYTHONHASHSEED`, propriétés, imports, mutation), et deux tâches tournent chaque nuit (suite canari, mutation complète du noyau). Le travail avance en cinq phases : documents, outillage, trois tranches de jeu (chacune en une PR de scénarios puis une PR de fonctionnalité), contrôles obligatoires, compte rendu.

**Pourquoi.** Les invariants du niveau 1 (déterminisme, conservation, visibilité) n'ont été vérifiés que sur papier. Tous les jalons suivants (M2, M4, M5) reposent sur ce noyau, donc une erreur de format ou de déterminisme laissée à M1 coûterait cher plus tard.

**Comment on saura que c'est fini.** Chacun des 11 objectifs a une preuve dans le compte rendu de M1 :
- scénario CUJ 1 vert ;
- rejeu identique en CI et sur le PC d'entraînement ;
- outil de divergence qui localise un défaut injecté ;
- invariants vérifiés à chaque tick ;
- émission et destruction par tranche dans les bornes du point 27 ;
- cinq contrôles exigés sur `main`, avec une PR rouge refusée par contrôle ;
- indicateur de ticks par seconde publié ;
- glossaire purgé des « à fixer au niveau 2 de M1 » ;
- validation subjective de la boucle par le propriétaire.

**Ce qui existe déjà, selon le document.** M0 a livré les garde-fous : chemins protégés, contrôle de garde, tâche `imports` non obligatoire, mécanisme des scénarios « en attente », protection de `main` décrite dans `.github/protection-main.json`. Aucun code de jeu n'existe encore. Le niveau 1 fixe les interfaces (`step`, `observe`, registre en partie double, enveloppe des événements, versions) et les règles d'import entre paquets.

Le relecteur a pu paraphraser chaque section. Aucun Blocker ne vient d'une section incompréhensible. Le Blocker ci-dessous est une contradiction interne.

## 2. Questions de compréhension

1. Les identifiants `system_1`, `ore_a`, `station_1` sont-ils des chaînes dans l'état, ou des libellés pour des identifiants entiers ? Le niveau 1 parle d'identifiants entiers. L'« ordre des identifiants » (lignes 138, 169) en dépend.
2. Le scénario de la ligne 455 suppose que la chaîne est `system_1`-`system_2`-`system_3`, mais la ligne 121 laisse la graine décider de cet ordre. Quelle graine les scénarios utilisent-ils ?
3. Comment un seul tirage clé sur (graine, tick, champ, « minage ») (ligne 154) ordonne-t-il plusieurs vaisseaux ?
4. Avec quel budget d'actions un acteur commence-t-il ? Les ordres d'administration coûtent-ils une action, passent-ils par le quota, et quel `actor_id` portent-ils ?
5. Quelle est la classe de visibilité des événements « personnage créé », « ordre refusé », « départ », « arrivée », « début de minage », « fin de minage » ?
6. Que font les tâches `rejeu` et `proprietes` entre la phase 2 et l'arrivée de leurs tests ? pytest renvoie le code 5 (aucun test collecté), donc la tâche est rouge.
7. Où vit la fonction de rejeu dont a besoin le scénario CUJ 1 de la tranche B (ligne 518), alors que `replay.py` n'arrive qu'à la tranche C (ligne 560) ?
8. D'où vient le seuil de 80 % de mutation ?
9. « Scénarios compris » (lignes 61, 235) : veut-on muter les définitions d'étapes, ou seulement utiliser les scénarios pour tuer les mutants ?
10. Qu'est-ce que la « liste des attrapés » (ligne 632) ?
11. Pourquoi exclure la première tranche de 1 000 ticks (ligne 577) ?
12. Comment le client apprend-il un refus prononcé à la réception (usurpation, quota), avant `step` ?
13. Que fait `test_revision.py` (ligne 576) lors de la première création, quand `main` n'a ni `RULES_REVISION` ni `tests/references/` ?

## 3. Constats

### Blocker

#### B1 : le canari « départage par `hash()` » ne peut pas être attrapé par `rejeu`
- **Lignes :** 154, 489, 574, 600 (et 62, 239).
- **Description :** la ligne 154 dit que la seule égalité possible à M1 est celle de plusieurs vaisseaux sur un champ dont le stock ne suffit pas. La ligne 489 dit qu'avec deux PNJ, « le stock ne limite pas les ventes de la partie de référence » (au plus 10 200 unités pour 20 000 en stock). La partie de référence (ligne 574) ne passe donc jamais par le départage. Or le canari de la ligne 600 (« un départage par `hash()` d'une chaîne → `rejeu` ») compte précisément sur cette partie pour être attrapé. Quand le stock suffit, l'ordre de service ne change pas l'état, donc les empreintes ne changent pas.
- **Raison :** tel qu'il est écrit, le canari passe sans être attrapé, la tâche `canari` est rouge chaque nuit, et l'objectif 8 (ligne 62) ne peut pas être atteint.
- **Correction :** choisir un tirage que la partie de référence exécute vraiment (par exemple la génération de la carte, ligne 121). Sinon, faire attraper ce canari par `proprietes`, avec une partie générée où le stock est rare. Dans les deux cas, justifier dans le texte que le contrôle visé exécute bien ce code.

### Major

#### M1 : contradiction sur les imports de `tools`
- **Ligne :** 218.
- **Description :** la ligne 218 dit que `server`, `clients` et `policies` sont des paquets « que `tools` ne peut pas importer ». Or le niveau 1, §1, et le glossaire autorisent `tools` à importer `server`. La ligne 563 du document ne cite d'ailleurs que `policies` et `clients`.
- **Correction :** retirer `server` de la phrase de la ligne 218.

#### M2 : « mutation, scénarios compris » ne correspond pas à la configuration
- **Lignes :** 61, 235, 388, 415.
- **Description :** le niveau 1, §10, exige que les définitions d'étapes soient mutées. Mais `source_paths` = `src/fourx` (ligne 388) et le script ne liste que les fichiers de `src/fourx/` (ligne 415). `tests/scenarios/steps/` n'est donc jamais muté.
- **Raison :** soit c'est une exigence du niveau 1 abandonnée en silence, ce que la ligne 97 interdit, soit le mot « compris » est ambigu.
- **Correction :** ajouter `tests/scenarios/steps` aux chemins mutés et au filtre du script, ou expliquer explicitement le sens de « scénarios compris ».

#### M3 : seuil de 80 % sans origine
- **Lignes :** 418, 423, 428, 631.
- **Description :** le seuil de 80 % (pour un fichier nouveau et pour la mutation de nuit) n'apparaît ni dans les objectifs (ligne 61), ni dans le Technical Plan (ligne 235), ni dans le niveau 1.
- **Raison :** c'est une exigence ajoutée, contraire à la règle de la ligne 97. Le lecteur ne sait pas qui l'a décidée ni pourquoi.
- **Correction :** l'inscrire dans le tableau des décisions (§1), avec sa raison et qui l'a tranchée, ou la retirer.

#### M4 : l'objectif 5 ne correspond pas à ce qui est testé
- **Lignes :** 55, 109, 224, 577.
- **Description :** l'objectif 5 promet que « la masse monétaire […] reste dans les fourchettes ». La décision de la ligne 109 explique au contraire que la masse ne peut que croître et que seules l'émission et la destruction par tranche sont bornées. Le test de la ligne 577 ne vérifie que ces deux grandeurs.
- **Correction :** reformuler l'objectif 5, par exemple « l'émission et la destruction par motif, par tranche de 1 000 ticks, restent dans leurs bornes ; la masse monétaire est affichée ».

#### M5 : renvois cassés ou ambigus sur les bornes et sur la mesure de durée
- **Lignes :** 224, 335, 588.
- **Description :** la ligne 224 renvoie à « plan détaillé (point 1) ». Or le point 1 du plan détaillé est la création du document lui-même, et les bornes sont au point 27 (lignes 577, 581). La ligne 335 renvoie au « point 28 » pour la mesure de durée de la CI : ce paragraphe est bien là (ligne 588), mais au milieu de la fiche du notebook. Enfin, la ligne 335 dit « première pull request de fonctionnalité », la ligne 588 « de cette tranche » (la C), ce qui ne désigne pas la même PR.
- **Correction :** à la ligne 224, écrire « Plan détaillé, point 27 ». Sortir la mesure de durée dans un point à part, ou dans l'en-tête de la tranche C, et utiliser la même formulation aux deux endroits.

#### M6 : le scénario de déplacement dépend d'un ordre de chaîne tiré au hasard
- **Lignes :** 121, 455.
- **Description :** selon la ligne 121, la graine fixe l'ordre des systèmes dans la chaîne. Le scénario de la ligne 455 (« de `system_1` à `system_3` en deux sauts ») suppose que cet ordre est fixe.
- **Correction :** soit fixer la chaîne dans l'ordre des identifiants et ne tirer que l'emplacement des sites, soit faire construire au scénario un état explicite, soit fixer une graine dont l'ordre est documenté.

#### M7 : type des identifiants non précisé
- **Lignes :** 104, 138, 169.
- **Description :** le niveau 1 parle de « tables indexées par un identifiant entier », alors que le document montre des identifiants comme `system_1`. Le parcours en largeur « dans l'ordre des identifiants » et le tri des tables changent si l'identifiant est une chaîne (en ordre lexicographique, `system_10` passe avant `system_2`).
- **Correction :** écrire que l'identifiant dans l'état est un entier et que `system_1` n'en est que le libellé (ou l'inverse), puis indiquer l'ordre de tri.

#### M8 : visibilité des événements incomplète
- **Lignes :** 180, 181.
- **Description :** la visibilité n'est donnée que pour trois types d'événements (vente, régénération d'un champ, écriture du registre). Pour « personnage créé », « ordre refusé », « départ », « arrivée », « début de minage (avec le débit) » et « fin de minage », rien n'est dit. Or l'activité d'un vaisseau est privée (ligne 180) : un événement public « début de minage » la révélerait.
- **Raison :** l'objectif 6 (aucun champ caché dans une observation) et le test de propriétés de la ligne 510 en dépendent.
- **Correction :** ajouter un tableau qui donne, pour chaque type d'événement v0, sa classe de visibilité.

#### M9 : tâches de CI sans tests entre les phases 2 et 3
- **Lignes :** 352, 357, 403 à 407.
- **Description :** les tâches `rejeu`, `proprietes` et `lent` sont créées à la phase 2, mais leurs tests arrivent aux points 19 et 27. Sans test collecté, pytest renvoie le code 5, donc la tâche est rouge. La ligne 357 dit que le propriétaire ne fusionne pas une PR dont une tâche est rouge : la PR de la phase 2 elle-même ne pourrait pas être fusionnée.
- **Correction :** préciser le comportement attendu, par exemple « le code 5 est traité comme un succès jusqu'à la phase 4 », ou créer chaque tâche avec son premier test.

#### M10 : le rejeu est demandé avant d'exister
- **Lignes :** 518, 560.
- **Description :** le scénario CUJ 1 de la tranche B exige que « la partie rejouée depuis son journal donne les mêmes empreintes ». Le rejeu (`tools/replay.py`) n'arrive qu'à la tranche C.
- **Correction :** déplacer cette clause dans `rejeu.feature` (ligne 553), ou dire quel code fait le rejeu dès la tranche B.

#### M11 : algorithme de départage non spécifié
- **Lignes :** 149, 154, 171, 487.
- **Description :** la clé (graine, tick, champ, « minage ») donne un seul tirage. Le texte ne dit pas comment ce tirage produit un ordre entre N vaisseaux. Le champ « entité » de la clé générique (ligne 171) est ici le champ, pas le vaisseau.
- **Raison :** deux agents de code écriraient deux départages différents, et les empreintes de référence ne seraient pas reproductibles d'une implémentation à l'autre.
- **Correction :** décrire l'algorithme, par exemple « un tirage par vaisseau, clé (graine, tick, vaisseau, "minage") ; tri par tirage croissant, puis par identifiant ».

#### M12 : les invariants sont cités sans être énoncés, et l'invariant 3 est restreint
- **Lignes :** 53, 103, 109, 165.
- **Description :** le document renvoie à « l'invariant 2 » et à « l'invariant 3 » du niveau 1, §4, sans jamais les énoncer. De plus, sa reformulation de l'invariant 3 (ligne 165) supprime la clause « aucune quantité n'est négative » du niveau 1.
- **Correction :** recopier les trois invariants en une ligne chacun au §3, en gardant la non-négativité.

#### M13 : « liste des attrapés » non définie
- **Ligne :** 632.
- **Description :** l'essai réel parle d'« un correctif canari retiré de la liste des attrapés ». Le script des lignes 592 à 602 n'a aucune liste de ce nom.
- **Correction :** décrire l'essai concret, par exemple « on remplace la commande visée d'un correctif par une commande qui réussit, et l'on vérifie que `canari` échoue », et le relier au point 30.

#### M14 : budget initial et ordres d'administration non précisés
- **Lignes :** 130, 141, 143, 152, 178, 207, 463, 489.
- **Description :** le texte ne donne pas le budget d'actions de départ (0 ? `budget_max` ?). Il ne dit pas non plus si l'ordre « créer un personnage » coûte une action, quel `actor_id` il porte, ni s'il passe par la validation sans état et le quota.
- **Raison :** le scénario de la ligne 463 (« un ordre au-delà du budget d'actions est refusé ») et le calcul des bornes de la ligne 581 en dépendent.
- **Correction :** ajouter ces règles au §2.

### Nit

- **N1** (ligne 38, à comparer avec les lignes 62 et 229 à 235) : « six nouveaux contrôles obligatoires », alors que la table en liste cinq, dont `imports` qui existe déjà. Rectifier le compte.
- **N2** (ligne 117) : l'arrondi de la taxe est une « proposition de l'agent de code », placée dans un tableau de « décisions ». Le propriétaire l'a-t-il acceptée ? Le dire.
- **N3** (ligne 99) : « la revue du lore et du plan de game design » renvoie à des documents sans lien. Ajouter les liens ou retirer la mention.
- **N4** (lignes 154, 171, 281) : le mot « motif » désigne à la fois l'étiquette d'un tirage à clé et le `Reason` du registre. Le niveau 1 fait déjà ce double usage. Préciser « motif du tirage » pour éviter qu'on ajoute `MINING` à `Reason`.
- **N5** (lignes 237, 612) : « par `!` » n'est pas expliqué (préfixe shell de Claude Code). Ajouter une incise.
- **N6** (ligne 366) : « étapes 5 à 9 » de la revue EGM ne sont définies ni ici ni dans le glossaire. Nommer les étapes ou mettre un lien.
- **N7** (ligne 630) : le « contrôle des termes interdits » n'est pas défini. Renvoyer au document de M0.
- **N8** (ligne 577) : « hors de la première » tranche n'est pas justifié (sans doute le régime transitoire du départ). Ajouter la raison.
- **N9** (lignes 243, 579) : le texte attribue « trois systèmes et 30 vaisseaux » au niveau 1, §8, qui ne dit que « quelques dizaines d'entités ». Par ailleurs, la mesure porte sur « `core` seul, sans serveur », mais avec 30 PNJ scriptés : le temps des politiques est-il compté ? À préciser.
- **N10** (ligne 404) : « les tests de l'outillage gardent leur tâche de M0 » ne donne pas le nom de cette tâche. Le donner.
- **N11** (ligne 567) : « Seule exception permise » ne dit pas à quelle règle. Citer la règle de `CLAUDE.md`.
- **N12** (ligne 576) : le cas de la première révision n'est pas traité (`main` n'a encore ni `RULES_REVISION` ni références). La comparaison avec `main` suppose aussi que la CI ait l'historique de `main`. Préciser les deux.
- **N13** (lignes 218, 565 ; glossaire) : les références sont rangées par numéro de révision (`rules-1`), alors que le glossaire dit « par `rules_version` », qui inclut l'empreinte de `tunables.toml`. Harmoniser.
- **N14** (lignes 131, 212) : « attendre à quai » est ambigu pour un vaisseau qui n'est pas à la station. Définir l'activité « à quai ».
- **N15** (par exemple lignes 132, 150, 389, 407, 489) : les renvois « point N » nus ne suivent pas la convention de la ligne 11. Le contexte suffit presque toujours. Appliquer la convention au moins dans le Technical Plan.
- **N16** (ligne 616) : le `<date>` du dossier du compte rendu n'est pas défini, et ce dossier est aussi celui des rapports de revue (ligne 366). Dire quelle date utiliser.
- **N17** (lignes 6, 17) : le sigle CUJ n'est défini ni dans le document ni dans le glossaire. Le développer une fois.
- **N18** (lignes 156, 489, 497, 527) : `version.py` (dans `core`) calcule `rules_version` « à partir de l'empreinte de `tunables.toml` », alors que le noyau ne lit aucun fichier et que ce fichier vit dans `core` mais est lu par le serveur. Écrire que l'empreinte est calculée par `server` et passée en paramètre.
- **N19** (lignes 474, 204) : `RefusalCode` inclut des refus prononcés à la réception, alors que le glossaire le décrit comme produit par `step`. Le texte ne dit pas comment ces refus parviennent au client (dans `TickUpdate` ?). Le préciser.

## 4. Recoupements avec l'étape 5

- B1 et le Major 1 de l'étape 5 ont la même cause : avec `field_stock` = 20 000, aucun champ ne se vide dans la partie de référence. B1 en tire une conséquence plus grave : le canari du départage ne peut pas être attrapé.
- M2 et M3 recoupent les Majors 2 et Nit 8 de l'étape 5 (seuil de 80 %, « scénarios compris »).
- M4 recoupe le Nit 1 de l'étape 5 (masse monétaire).
- N9, N10 et N12 recoupent les Nits 9, 6 et le Major 5 de l'étape 5.

## Décompte

1 Blocker, 14 Major, 19 Nit (34 constats).
