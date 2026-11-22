# M1 : noyau déterministe et tranche 0 (document de niveau 2)

*   **Auteur :** Thomas (thom.bruyer)
*   **Statut :** Proposed (amendement 2 en revue ; le document est Approved depuis le 2026-11-08, et l'amendement 1 depuis le 2026-11-21)
*   **Date :** 2026-11-02 ; mis à jour le 2026-11-06 (décisions du propriétaire sur le contenu du jeu ; corrections de la revue EGM, étapes 5 à 9) ; approuvé par le propriétaire le 2026-11-08 ; amendement 1 rédigé le 2026-11-12, mis à jour pendant sa revue, approuvé par le propriétaire le 2026-11-21 ; amendement 2 rédigé le 2026-11-22, en revue
*   **Niveau 1 :** [architecture-niveau-1.md](./architecture-niveau-1.md) (CUJ 1, CUJ 4, §1 à §7, §10, §11 ligne M1)
*   **Intentions reprises :** [RFC du brainstorm](./mmo-gestion-spatiale-ia.md), jalon « M1 – Tranche 0 ». Le niveau 1 fait foi en cas d'écart.
*   **Amendements :** amendement 1 du 2026-11-12 (un monde plus grand, un écran lisible, le temps comme ressource, la visibilité par proximité), voir le tableau ci-dessous. ADR liées : [0003](../adr/0003-observe-recoit-les-reglages.md), [0004](../adr/0004-fourchettes-de-la-tranche-0.md) et [0005](../adr/0005-visibilite-par-proximite.md). Amendement 2 du 2026-11-22 (l'écran rétro), ADR liée : [0006](../adr/0006-client-retro-8-bits.md).

Les titres de section (`##`), le statut et les intitulés du gabarit du plan (sous-titres, Type / Scope, Proposed Changes, Create / Modify / Delete) suivent le gabarit de conception d'EGM, en anglais, pour que les outils de revue s'y retrouvent. Tout le reste est en français, sauf les étiquettes Given / When / Then des CUJ (amendement 1, réécrit).

**Chemins protégés nouveaux.** Un fichier nouveau ajouté à `.github/chemins-proteges.txt` dans la pull request protégée qui le crée compte comme protégé dans cette pull request. Un fichier qui existe déjà sans être protégé doit être protégé par une pull request antérieure avant d'être modifié dans une pull request protégée (d'où le plan détaillé, point 3 bis).

**Conventions de renvoi.** « Technical Plan, point N » désigne une section du Technical Plan de ce document. « Plan détaillé, point N » désigne un point du Detailed Implementation Plan de ce document. Un « point N » sans préfixe renvoie à la même partie du document que le passage qui le cite. Un renvoi au niveau 1 le dit toujours (« niveau 1, §2 »).

**Autres conventions** (les marques d'amendement employées ci-dessous sont définies plus bas, sous « Amendements »).
- **(amendement 1, réécrit)** Un *CUJ* (Critical User Journey) est un parcours utilisateur critique, défini par le niveau 1 (CUJ 1 à 6) ou par ce document (CUJ A). M1 reprend le CUJ 4 tel quel et le CUJ 1 élargi par l'ADR 0004 ; les scénarios du plan détaillé, points 20 et 24, les traduisent, et `tests/scenarios/ecrans.feature` traduit le CUJ A (plan détaillé, point 23 ter).
- « Par `!` » veut dire que le propriétaire tape la commande dans Claude Code en la préfixant de `!`, ce qui l'exécute dans la session sous son propre nom.
- Un *site* est une station ou un gisement. Un *gisement* est l'entité du jeu où l'on mine ; « champ » ne désigne que les champs de données.
- Les deux machines sont l'*ordinateur portable* du propriétaire et le *PC d'entraînement*.
- **(amendement 1)** La *tâche de relais* est la tâche de `__main__.py` qui transmet les mises à jour à l'hôte des PNJ (Technical Plan, point 7).

**(amendement 1)**

**Amendements.** Un amendement ne renumérote jamais les passages existants, qu'une trentaine de fichiers du dépôt citent. Un point inséré entre deux points existants prend le numéro du point qui le précède, suivi de « bis », « ter »… Un CUJ ou une alternative nouveaux prennent une lettre, à la suite des lettres existantes (CUJ A ; alternatives J à AH (amendement 2, réécrit)).

- **Préséance.** En cas de conflit dans ce document, un passage ajouté, réécrit ou donné comme texte en vigueur par l'amendement N, sous l'une des formes de la légende ci-dessous, l'emporte sur le texte d'origine, que celui-ci soit marqué ou non, et un amendement plus récent l'emporte sur un plus ancien.
- **Légende des marques :**
  - « (amendement N) » : passage ajouté par l'amendement N ;
  - « (amendement N, réécrit) » : le passage d'origine est récrit sur place, et sa version d'origine ne figure plus dans le document (elle reste dans l'historique git et sur `main`) ;
  - « (amendement N, précisé) » : le passage d'origine reste vrai, et l'amendement le complète à la suite ;
  - « (amendement N, complète la ligne d'origine) » : dans un tableau, ligne nouvelle qui complète une ligne gardée plus haut ;
  - « **Ajoutés par l'amendement N :** » : liste d'éléments ajoutés à la suite d'une liste d'origine ;
  - « **Risques ajoutés par l'amendement N :** » : tableau de risques ajouté à la suite du tableau d'origine ;
  - « (amendement N) » à la fin d'une ligne de bloc de code : ligne ajoutée ou récrite ; elle ne couvre que cette ligne ;
  - dans le plan détaillé seulement, où le texte d'origine des points déjà rédigés ou livrés est gardé : « **Proposed Changes (amendement N, ajout) :** » ou « **Proposed Changes (amendement N, remplacement) :** », puce ajoutée à un point existant, qui complète ses puces d'origine, ou remplace celles qui portent une marque de remplacement ; « (amendement N : …) », marque en ligne qui donne la nouvelle valeur ; « *(remplacé par l'amendement N, voir …)* », « *(remplacé par l'amendement N : …)* » et « *(remplacé par l'amendement N, voir … : …)* » : le passage d'origine est gardé mais ne vaut plus, et le renvoi ou le texte qui suit les deux-points donne le texte en vigueur. **(amendement 2, précisé)** Le Verification Plan fait partie du plan détaillé.
- **Portée des marques :**
  - une marque placée dans un titre couvre toute la section ;
  - une marque seule sur sa ligne couvre tout ce qui suit, jusqu'au prochain titre, même quand elle suit elle-même un titre ;
  - une marque placée en tête d'un paragraphe, d'une puce, d'un objectif ou d'une ligne de tableau, dans son intitulé en gras ou juste après cet intitulé, couvre tout ce paragraphe, cette puce, cet objectif (sous-listes et *Vérification* comprises) ou cette ligne ;
  - une marque placée après une phrase d'introduction couvre la liste qui suit ;
  - une marque d'ajout (« (amendement N) » ou « (amendement N, précisé) ») placée en tête d'une phrase qui n'ouvre pas son paragraphe couvre cette phrase et la suite, jusqu'à la fin du paragraphe où elle se trouve, dans une puce ou un objectif compris ;
  - placée ailleurs, une marque de réécriture ou de remplacement ne couvre que la phrase ou le membre de phrase qui la précède.
- **Code livré.** Les volets A et B (plan détaillé, points 15 à 23) sont livrés ; les points 23 bis à 23 sexies, ajoutés par l'amendement 1, sont livrés (pull requests n° 23 à 27, et partie d'essai du 2026-11-22) (amendement 2, réécrit). Le texte d'origine non marqué des points 15 à 23 décrit le code fusionné, que l'amendement appelle « code d'origine », à une exception près : depuis le correctif de la pull request n° 22, la touche `v` vend le minerai le plus abondant, et non toute la cargaison. **(amendement 2, précisé)** Les points 23 septies à 23 undecies, ajoutés par l'amendement 2, ne le sont pas. Le *code de l'amendement 1* est le code de `main` à la fusion du point 23 quinquies.

| N° | Date | Objet | Passages touchés | Dossier de revue |
| :-- | :-- | :-- | :-- | :-- |
| 1 | 2026-11-12, mis à jour pendant la revue jusqu'au 2026-11-21 | un monde plus grand, un écran lisible, le temps comme ressource, la visibilité par proximité ; à la suite de la partie de test du 2026-11-11 | conventions ; Overview ; The Problem ; objectifs 1, 5, 6 et 11 à 16 ; Non-Goals ; Open Questions ; introduction des CUJ, CUJ A ; Technical Plan, vue d'ensemble, points 1, 2, 5, 6, 7, 7 bis, 8, 9, 11, 12, 13 ; introduction des alternatives, alternatives J à AA ; Risks & Mitigations ; Additional Resources ; Future Improvements ; plan détaillé, points 5, 17, 20, 22, 23, 23 bis à 23 sexies, 25, 27, 28, 28 bis, 29, 32 bis ; Verification Plan | `docs/revues/2026-11-12-niveau-2-m1-noyau-amendement-1/` |
| 2 (amendement 2) | 2026-11-22, mis à jour pendant la revue | l'écran rétro : style 8 bits, carte disposée par forces et zoomable, information hiérarchisée, aide au lancement ; à la suite de la partie d'essai du 2026-11-22 | en-tête (statut, date, puce Amendements, numérotation des amendements, légende des marques, code livré) ; Overview ; The Problem ; objectifs 11, 12 et 17 à 19 ; Non-Goals ; Open Questions ; CUJ A ; Technical Plan, vue d'ensemble, points 1, 7 bis, 7 ter, 12 et 13 ; introduction des alternatives, alternatives AB à AH ; Risks & Mitigations ; Additional Resources ; Future Improvements ; plan détaillé, introduction, palier 3, points 23 quater, volet B ter (points 23 septies à 23 undecies), 28 bis ; Verification Plan | `docs/revues/2026-11-22-niveau-2-m1-noyau-amendement-2/` |


--------------------------------------------------------------------------------

## Overview

M1 est le premier jalon qui contient des règles du jeu. Il construit la *tranche 0* : un petit monde hors ligne, généré à partir d'une graine, où le propriétaire peut extraire du minerai, le transporter jusqu'à une station et le vendre à prix fixes (niveau 1, CUJ 1).

Tout tourne dans un seul processus, sur l'ordinateur portable. M1 livre six livrables, qui dépendent les uns des autres :
1. **le noyau** (`core`) : l'état du monde, la fonction `step`, la fonction `observe` et le registre comptable, avec les invariants de déterminisme du niveau 1, §2 ;
2. **les règles de la tranche 0** : déplacement sur une carte en graphe, minage dans des gisements finis qui se régénèrent, vente à la station du système du vaisseau (amendement 1, réécrit), taxe ;
3. **les formats** (`schema`) : ordres, résultats d'ordre, observations, événements v0 et messages du protocole, chacun avec son numéro de version ;
4. **le serveur en mémoire** (`server`) : la boucle des ticks, la réception des ordres, le journal des ordres soumis, les instantanés et l'enregistrement des événements v0 ;
5. **le client Textual minimal** (`clients`), relié au serveur dans le même processus, et 3 à 5 PNJ (`policies`) (amendement 1, réécrit), qui jouent la même boucle que le propriétaire ;
6. **l'outillage de vérification** (`tools` et CI) : l'outil de divergence, le test de rejeu, et les contrôles obligatoires de M1 (niveau 1, §10).

M1 fixe aussi les identifiants que le glossaire marque « à fixer au niveau 2 de M1 ».

**(amendement 1)**

L'amendement 1 change quatre choses dans M1, avant le volet C (rejeu, divergence, économie) :

1. **Le monde de la tranche 0 grandit.** La graine tire sa taille dans des fourchettes :
   - 8 à 12 systèmes reliés en graphe ;
   - 4 à 6 gisements, au moins deux par minerai ; une station et un gisement peuvent partager un système ;
   - 2 à 3 stations, chacune avec ses propres prix fixes, écrits dans les réglages ;
   - 3 à 5 PNJ, chacun avec un vaisseau.

   Ces fourchettes dépassent celles d'origine du CUJ 1 du niveau 1 : l'ADR 0004 les élargit.
2. **Le client devient un écran unique et lisible.** Il est fait de cadres indépendants : carte, vaisseau, stations, historique, barre d'état et alertes. Le rendu se limite à du texte, des tableaux et des cadres, sans thème de couleur. L'écran montre :
   - la carte en graphe ;
   - où se trouve chaque minerai, avec le stock des seuls gisements proches, et à quel prix chaque station le rachète ;
   - combien de ticks il reste avant la fin d'un trajet ou d'un minage ;
   - quels ordres attendent leur résultat ;
   - pourquoi un ordre a été refusé, en français, et, pour un refus lié à un lieu, où aller.

   Une alerte signale la fin d'un minage et l'arrivée à destination. Les touches fonctionnent sur un clavier AZERTY, sans Majuscule.
3. **Le temps devient une ressource.** Un saut entre deux systèmes voisins dure `jump_ticks` ticks (400 dans les valeurs initiales), soit 20 minutes à la période nominale de 3 s. Remplir une cargaison de 100 unités prend 100 ticks, soit 5 minutes. La vente reste instantanée. Pour donner ces durées au client, `observe` reçoit les réglages et en publie une partie dans l'observation : c'est un changement d'interface du niveau 1, qui passe par l'ADR 0003. En mode développement seulement (option `--dev`), on peut accélérer l'univers, le mettre en pause, ou avancer jusqu'à la prochaine alerte. Cette vitesse de l'univers se règle par la durée réelle d'un tick ; elle ne change pas la durée d'un saut en ticks, qui est une règle (`jump_ticks`).
4. **On ne voit que ce qui est proche.** Les vaisseaux d'autrui et le stock des gisements ne sont visibles que dans le système d'un des vaisseaux de l'acteur et les systèmes voisins (ADR 0005), en attendant des scanners qui porteront plus loin. La carte elle-même (systèmes, liens, emplacement des gisements et des stations, prix) reste visible partout.

L'amendement redimensionne aussi le test d'économie du volet C : les fenêtres passent de 1 000 à 10 000 ticks, et ses bornes deviennent larges : au moins une vente par fenêtre, une émission sous un plafond tiré de la carte de la partie de référence (graine 1), et une destruction égale à la somme des taxes.

**(amendement 2)**

L'amendement 2 refait l'écran du client, sans toucher aux règles, au protocole ni à l'observation : un style rétro 8 bits dans le terminal (couleurs et caractères demi-blocs ▀ ▄, ADR 0006) ; une carte de l'univers disposée par forces (les systèmes se repoussent, les liens les retiennent), qu'on zoome et qu'on déplace à la souris ou au clavier ; une information hiérarchisée autour d'un cadre « Prochaine étape » ; une aide, ouverte au lancement de chaque partie, qui explique les mécaniques. Pour la disposition et le rendu, il remplace le point 2 de la liste ci-dessus : l'écran a désormais des couleurs, et ses cadres sont ceux du Technical Plan, point 7 ter.

## The Problem

Le niveau 1 fixe les interfaces et les invariants, mais aucun code ne les met encore en œuvre. Tant qu'un premier noyau n'existe pas, trois choses restent inconnues :
- **si les invariants tiennent sur un vrai tick.** Le déterminisme, la conservation de l'argent et des biens et la visibilité par champ de données n'ont été vérifiés que sur papier, et sur un banc d'essai simplifié (niveau 1, §2) ;
- **si la boucle de jeu fonctionne.** Extraire, transporter et vendre doit former une boucle que le propriétaire a envie de rejouer. C'est un jugement subjectif, que le niveau 1 assume ;
- **comment l'économie évolue sur la durée.** Sur 100 000 ticks, la masse monétaire, l'émission et la destruction doivent rester dans des fourchettes connues. Sans cela, on ne saura pas si une dérive future vient d'une règle ou d'un joueur IA.

Tous les jalons suivants reposent sur ce noyau. L'entraînement (M4) fait tourner `step` dans de nombreux processus en parallèle, le serveur persistant (M5) rejoue son journal, l'observabilité (M2) lit ses événements. Une erreur de format ou de déterminisme laissée à M1 se paierait plus tard en migrations, ou en joueurs IA entraînés sur un monde faux.

Le jalon est large : six livrables, et cinq contrôles obligatoires de plus (dont `imports`, qui tourne déjà sans être obligatoire). Le risque principal est donc l'exécution, pas la conception. Un agent de code sans mémoire doit pouvoir livrer chaque livrable à partir de ce document seul, sans décision ouverte : les noms et les signatures sont au Technical Plan, point 13.

**(amendement 1)**

**La partie de test du 2026-11-11.** Le 2026-11-11, après la fusion du volet B, le propriétaire a joué la tranche 0 pendant 97 ticks, environ une minute et demie. Son verdict : « intéressant, pas encore fun ». Le « fun » est attendu des mécaniques des jalons suivants ; ce n'est pas l'objet de l'amendement. Quatre gênes, en revanche, l'empêchent de juger la boucle de jeu, ce que demande l'objectif 11 :

- **Le rythme est trop rapide.** L'écran change chaque seconde, le PNJ enchaîne ses cycles pendant que le joueur cherche quoi faire, et les événements passent inaperçus.
- **L'affichage est confus.** La carte est une simple liste de systèmes, on ne voit pas où est chaque minerai, l'historique défile, et l'état du vaisseau est dense.
- **Les touches sont peu claires.** Le choix du système se fait par un chiffre, qui demande Majuscule sur un clavier AZERTY.
- **Un refus est resté incompris.** Au tick 51, un ordre de minage a été refusé, parce que le minerai demandé n'avait pas de gisement dans ce système. Le client affichait le code anglais `no_deposit_for_ore`, sans dire où était ce minerai.

Le propriétaire veut un jeu plus lent, stratégique et réfléchi, où le temps compte : tout prend du temps, et l'on passera plus tard à l'échelle par plus de vaisseaux ou de plus gros, pas par des actions plus rapides. Il veut aussi, « sans rentrer dans l'excessif », un monde un peu plus grand : plus de nœuds, plus d'endroits où miner, plus de vaisseaux qui bougent, et plus de points de vente. Avec trois systèmes en chaîne, une station et un PNJ, il n'y a ni choix de route, ni choix du lieu de vente, et presque rien ne bouge à l'écran. Enfin, il ne veut pas qu'on voie tout : un autre vaisseau, ou le stock d'un gisement, n'est visible qu'à proximité, dans le système d'un des vaisseaux de l'acteur ou un système voisin, en attendant des scanners qui porteront plus loin. C'est une décision de jeu : la détection deviendra une mécanique des jalons suivants, et M1 en pose la règle de base (ADR 0005). Elle a un prix assumé : on voit moins de PNJ bouger à l'écran.

Ralentir seulement la période de l'horloge ne suffit pas. Le jeu attendrait plus longtemps entre des décisions qui restent les mêmes, et le PNJ resterait aussi rapide en ticks. Les durées doivent donc être des règles : elles changent `rules_version`. La taille du monde est aussi une règle, puisque `world.generate` la tire de la graine. C'est le moment le moins coûteux de M1 pour ce changement : les références du volet C n'existent pas encore, et `RULES_REVISION` vaut 0.

Ces changements ont des conséquences, que l'amendement traite :
- **Le test d'économie ne vérifierait plus rien.** Sur la carte d'origine et avec les nouvelles durées, un cycle du PNJ (aller vers le gisement du minerai le mieux payé, qui se trouvait le plus loin, minage, retour, vente) dure 1 701 ticks : chiffre obtenu par simulation, graine 1, deux PNJ. Une fenêtre de 1 000 ticks contiendrait donc zéro ou une vente par PNJ. Sur la carte agrandie, les cycles varient avec la graine : les bornes sont calculées à partir de la carte de la partie de référence (plan détaillé, point 27).
- **Les scénarios protégés de `partie.feature` cassent.** Ils lisent les vrais réglages, et supposent la carte de la graine 1 (station dans `system_1`, `ore_a` dans `system_2`, `ore_b` dans `system_3`).
- **Le client ne connaît pas les durées.** Il ne voit que l'observation, et le niveau 1 interdit tout autre canal vers le joueur (niveau 1, §5).
- **Le PNJ doit savoir choisir parmi plusieurs gisements et plusieurs stations.** Sa politique change de version, en restant simple.

**(amendement 2)**

**La partie d'essai du 2026-11-22.** À la partie d'essai du plan détaillé, point 23 sexies, sur l'écran unique de l'amendement 1 (point 23 quinquies), le propriétaire juge que « l'écran est visible, mais l'interface est vraiment pas claire. L'information n'est pas hiérarchisée. C'est très difficile de comprendre ce qui se passe, il n'y a pas beaucoup d'aide, il n'y a pas de tuto, il n'y a pas d'explication sur les mécaniques ». L'objectif 12 n'est donc pas atteint. Il estime que l'ASCII était « une mauvaise idée au final », et demande une esthétique rétro, 4 ou 8 bits, avec un graphe de l'univers « clair et joli », qu'on puisse zoomer, avec « une forme de gravité entre les nodes », comme le graphe d'Obsidian. Il a vu des maquettes de cet écran dans le terminal (hors du dépôt), les a jugées « pas mal du tout », et a choisi la palette 8 bits. Il valide la boucle de jeu actuelle (objectif 11), avec une réserve : elle devra être étoffée par des mécaniques qui interagissent entre elles, attendues des jalons suivants (par exemple les pirates, M6). Pendant la revue, il a retenu une carte fixe, la souris sans mini-carte, deux pull requests de fonctionnalité, un verdict sur l'écran qui ne bloque pas la livraison de M1, et une prochaine étape qui conseille le cycle au meilleur gain par tick (Technical Plan, point 1, décisions du 2026-11-22).

## Goals

Chaque objectif est vérifiable par un contrôle automatique, ou validé explicitement par le propriétaire quand le document le dit.

1. **Le propriétaire joue la tranche 0 de bout en bout** (niveau 1, CUJ 1). Dans le client Textual, il choisit un minerai, envoie un vaisseau l'extraire, le ramène à une station (amendement 1, réécrit) et vend sa cargaison. Le client affiche le trajet, la cargaison et le paiement.
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
5. **(amendement 1, réécrit) L'économie reste dans ses fourchettes sur 100 000 ticks.** Sur la partie de référence, l'émission par motif, la destruction par motif et la croissance de la masse monétaire, **par fenêtre de 10 000 ticks**, restent dans les bornes du plan détaillé, point 27. Ces bornes sont larges (décision du propriétaire, 2026-11-21) : au moins une vente par fenêtre ; une émission sous un plafond tiré de la carte du monde de la graine 1 ; une destruction égale à la somme des taxes ; une croissance égale à l'émission moins la destruction. Elles détectent une panne (plus aucune vente) ou une émission au-dessus du plafond, pas une baisse partielle des ventes. Les prix sont fixes à ce jalon. Les bornes sont vérifiées sur la partie jouée à la régénération des références : l'outil de régénération refuse d'écrire des références dont la partie sort des bornes. En CI, les empreintes du registre, qui contiennent les compteurs cumulés par motif, fixent déjà les grandeurs de chaque fenêtre : le test protège alors `window_stats` et le calcul des bornes.
   *Vérification :* le test `tests/economie/test_fourchettes.py`, lancé en CI par la tâche `rejeu`, rejoue le journal de la partie de référence et compare chaque fenêtre, la première comprise, aux bornes qu'il calcule à partir du monde de la graine 1 ; il vérifie aussi que la destruction est égale à la somme des taxes de chaque vente, arrondies vers le haut. Le notebook marimo affiche les mêmes grandeurs, par la même fonction `window_stats` (plan détaillé, point 25).
6. **Tous les acteurs passent par la même porte.** Le client Textual et le PNJ reçoivent leurs observations de la seule fonction `observe`, et leurs ordres passent par la même réception, puis par `step`. Aucun champ de données caché n'apparaît dans une observation.
   *Vérification :* des tests de propriétés sur la visibilité ; les contrats d'imports interdisent à `clients` et `policies` d'importer `core`. **(amendement 1)** Les tests de propriétés couvrent aussi la classe proximité : un vaisseau d'autrui ou un stock de gisement hors de portée n'apparaît pas dans l'observation. La *portée* d'un acteur est l'ensemble des systèmes de ses vaisseaux et de leurs voisins : un champ ou un événement de classe proximité n'est visible qu'à portée (Technical Plan, point 5). Une exception, limitée à la partie locale et retirée à M3, est décrite au Technical Plan, point 6 : la fonction de rappel de vitesse, une commande de l'horloge locale qui n'apporte aucune information du jeu.
7. **Tout ce qui persiste ou circule porte un numéro de version.** Le journal des ordres soumis, les instantanés, les événements, le protocole et les règles portent leurs champs de version (niveau 1, §3 et §7).
   *Vérification :* `tests/core/test_versions.py` et `tests/server/test_versions_journal.py` (plan détaillé, points 18 et 23) ; le contrôle de garde exige que `RULES_REVISION` augmente de un quand les références changent.
8. **Les contrôles de M1 deviennent obligatoires** (niveau 1, §10) : tests et scénarios ; rejeu sous deux `PYTHONHASHSEED` ; tests de propriétés ; contrats d'imports ; mutation sur les fichiers modifiés, scénarios compris (Technical Plan, point 10), avec un score jamais inférieur à celui du commit de base de la pull request. La suite canari et la mutation complète du noyau tournent chaque nuit sur `main`.
   *Vérification :* les cinq contrôles figurent dans la protection de `main` ; les essais du plan détaillé, point 32 bis, montrent qu'une pull request en échec sur chacun d'eux est refusée ; la suite canari échoue si l'un de ses bugs volontaires n'est pas attrapé.
9. **L'indicateur avancé est mesuré.** Les ticks par seconde de `step` et `observe`, sur un monde de la taille de ceux de l'entraînement, sont mesurés et publiés. Ils ne déclenchent rien (niveau 1, §2).
   *Vérification :* la mesure figure dans le compte rendu de M1, avec la commande qui l'a produite.
10. **Les identifiants du glossaire sont fixés.** Chaque terme marqué « à fixer au niveau 2 de M1 » reçoit son identifiant du code, et le glossaire est mis à jour.
    *Vérification :* plus aucune entrée du glossaire ne porte « à fixer au niveau 2 de M1 ».
11. **Le propriétaire valide la boucle de jeu.** Après avoir joué, il déclare que la boucle extraire, transporter, vendre lui convient. C'est une validation subjective, assumée par le niveau 1, §11. **(amendement 1, précisé)** Il la valide sur le client et le monde de l'amendement, en mode développement accéléré pour l'enchaînement des étapes du cycle (à la période nominale, un cycle dure par exemple 5 minutes pour un gisement dans le système d'une station, 85 minutes pour un gisement à deux sauts, et davantage plus loin), et sur au moins un saut complet joué à la période nominale (20 minutes avec les valeurs initiales) pour le rythme. **(amendement 2, précisé)** Le propriétaire l'a validée le 2026-11-22, avec une réserve : les jalons suivants devront l'étoffer de mécaniques qui interagissent entre elles.

    *Vérification :* sa décision, consignée dans le compte rendu de M1 avec la graine et les paliers de vitesse joués (amendement 1, réécrit).
12. **(amendement 1) Le propriétaire lit l'écran sans se perdre.** Après une partie, il déclare savoir à tout moment :
    - où est son vaisseau, et s'il est à l'arrêt, en route ou en minage ;
    - combien de ticks il reste avant la fin de son trajet ou de son minage ;
    - où se trouve chaque minerai, et à quel prix chaque station le rachète ;
    - quels ordres attendent leur résultat ;
    - pourquoi un ordre a été refusé.

    C'est un jugement subjectif, distinct de l'objectif 11.

    *Vérification (amendement 2, réécrit) :* sa décision, rendue après la partie d'essai de l'amendement 2 (plan détaillé, point 23 undecies) et consignée dans le compte rendu de M1 ; elle ne bloque pas la livraison de M1 (point 23 undecies). Pour la part automatique, des tests du pilote de Textual, sur un terminal de 120 colonnes × 36 lignes et sur un monde de 12 systèmes, vérifient pour chaque état du vaisseau que ces informations figurent dans les cadres de texte : la position et l'état dans « Vaisseau » et « Prochaine étape » ; les ticks restants dans les mêmes cadres ; l'emplacement de chaque minerai et les prix dans « Stations » ; les ordres en attente dans « Vaisseau » ; les refus dans « Historique ». La carte n'est pas lue par ces tests : elle a ses propres tests (objectif 17). Des tests avec `Game.advance` vérifient que chaque durée affichée est égale au nombre de ticks observé avant l'événement, quand aucun autre vaisseau ne mine le même gisement.
13. **(amendement 1) Le temps est une ressource, et les durées sont des règles.** Un saut dure `jump_ticks` ticks (400 dans les valeurs initiales). Remplir une cargaison vide prend `cargo_capacity` ÷ `mining_rate` ticks (100). La vente reste instantanée. Les durées sont en ticks ; les minutes ne sont qu'une estimation d'affichage, à la période nominale de 3 s.
    *Vérification :* un scénario sur les vrais réglages : les durées lues dans `observation.public_tunables` sont celles de `tunables.toml`, un trajet observé dure `jump_ticks` ticks, et la cargaison n'est pleine qu'au bout de `cargo_capacity` ÷ `mining_rate` ticks de minage. Aucun test ne vérifie la valeur 400 : `tunables.toml` fait foi. Un changement de réglage change `rules_version` ; `RULES_REVISION` reste à 0.
14. **(amendement 1) Le joueur connaît les durées par l'observation seule.** `observe` reçoit les réglages et publie, dans l'observation, une vue des réglages publics : `jump_ticks` et `mining_rate`. La capacité est déjà dans la vue du vaisseau, et la taxe dans l'événement de vente. Aucun autre canal n'apporte d'information du jeu au joueur ; la fonction de rappel de vitesse (objectif 6) commande l'horloge locale sans rien apporter du jeu. L'ADR 0003 change l'interface du niveau 1.
    *Vérification :* les tests de visibilité s'étendent à la nouvelle vue, et vérifient qu'aucun autre réglage n'apparaît dans l'observation ; `protocol_version` passe à 2.
15. **(amendement 1) L'univers s'accélère en mode développement.** Lancée avec `--dev`, une partie locale offre des paliers de vitesse de l'univers, la pause, et « avancer jusqu'à la prochaine alerte ». Sans `--dev`, il n'y a aucune touche de vitesse : l'univers tourne à la période nominale, ou à celle de l'option de lancement `--periode`, qui sert aussi aux essais. La vitesse de l'univers n'est pas celle du vaisseau : un saut dure toujours `jump_ticks` ticks. Rien de cela ne passe par le protocole, le journal des ordres ou les règles : seule la période de l'horloge change, et chaque changement est enregistré dans le dossier de la partie. En mode avec horloge, les PNJ reçoivent leurs mises à jour par la tâche de relais : au palier rapide (×100), une décision peut entrer au deuxième tick suivant, ou plus tard, au lieu du tick suivant. La partie jouée dépend donc de la vitesse ; le rejeu de son journal, lui, redonne toujours les mêmes empreintes.
    *Vérification :* un test rejoue le journal d'une partie jouée en accéléré et retrouve ses empreintes ; `speed.jsonl` garde la période initiale et chaque changement.
16. **(amendement 1) Le monde est plus grand, et sa taille vient de la graine.** `world.generate` tire, de façon déterministe, 8 à 12 systèmes reliés en un graphe connexe, 4 à 6 gisements (au moins deux par minerai), 2 à 3 stations, et `__main__.py` crée 3 à 5 PNJ (nombre tiré par `core.world.npc_count`). Une station et un gisement peuvent partager un système. Chaque station rachète chaque minerai à son prix fixe, lu dans les réglages. L'ADR 0004 élargit les fourchettes du CUJ 1.
    *Vérification :* des tests de propriétés sur de nombreuses graines (tailles dans les fourchettes, graphe connexe, au moins deux gisements de chaque minerai, même monde pour la même graine sous deux `PYTHONHASHSEED`, comparé par un test qui lance la génération dans deux sous-processus) ; le scénario du CUJ 1 joue sur un monde généré, sans supposer sa forme.
17. **(amendement 2) La carte montre tous les systèmes à la fois.** Au zoom 1, la carte montre tous les systèmes sans déplacement de la vue. Ils sont disposés par forces : ils se repoussent, les liens les retiennent ; la disposition est calculée une fois par partie, et la carte ne bouge pas quand les vaisseaux bougent. La carte se zoome et se déplace à la souris et au clavier ; le survol d'un système affiche une bulle d'information (sites, stock, distance) ; un clic sur un système ouvre la liste des destinations sur ce système. Les systèmes à portée se distinguent des autres, et la route et la position du vaisseau se voient, même pendant un saut.
    *Vérification :* des tests de la disposition (même résultat à chaque appel, chaque système placé une fois dans le carré, aucun recouvrement des boîtes ni des cases de la grille, sur de nombreuses graines) ; des tests de la vue (projection, zoom, déplacement, système sous le pointeur, grille dessinée) ; des tests du pilote de Textual pour le zoom, le déplacement, le clic et la bulle ; le verdict du propriétaire (plan détaillé, point 23 undecies).
18. **(amendement 2) L'écran dit quoi faire ensuite.** Un cadre « Prochaine étape », en tête de la colonne de droite, donne l'action utile suivante, sa durée et sa touche, à partir de l'observation et de l'état du client (alertes, ordres envoyés, gisements vus vides), sans autre source d'information du jeu. À l'arrêt, il conseille le cycle (aller miner, miner, aller vendre) qui rapporte le plus par tick. L'information est hiérarchisée : à droite, prochaine étape, puis vaisseau, puis stations ; à gauche, la carte ; en bas, l'historique.
    *Vérification :* des tests de la fonction qui calcule la prochaine étape, règle par règle ; un scénario qui la suit au long d'un cycle joué ; le verdict du propriétaire (point 23 undecies).
19. **(amendement 2) Les mécaniques sont expliquées dans le jeu.** Une aide « Comment jouer » s'ouvre au lancement de chaque partie et sur la touche `h` : les trois étapes de la boucle (miner, transporter, vendre) avec leurs touches et leurs durées, lues dans l'observation ; ce que l'on voit et ne voit pas ; la durée d'un tick ; un premier objectif, vendre une première cargaison ; les touches.
    *Vérification :* des tests des textes de l'aide, comparés en entier ; des tests du pilote de Textual (ouverture au lancement, touche `h`, fermeture par Entrée, Échap et `h`) ; un scénario qui vérifie que les durées de l'aide sont celles de l'observation ; le verdict du propriétaire (point 23 undecies).

## Non-Goals

*   **Le marché entre joueurs, les corporations, les permissions, le combat et les pirates.** Ils arrivent à M6. La phase « combat » existe dans l'ordre des phases du tick (niveau 1, §2), mais reste vide à M1.
*   **La perte de vaisseau.** Aucun vaisseau n'est détruit à M1 (Technical Plan, point 1).
*   **Les prix variables.** Chaque station rachète chaque minerai à son propre prix fixe (amendement 1, réécrit).
*   **Le transport WebSocket, les comptes et l'authentification par jeton.** Ils arrivent à M3. À M1, le client et le serveur partagent un processus, et les messages circulent déjà typés : un message illisible ne peut pas exister. M3 fixera son traitement.
*   **Le serveur persistant, les migrations testées, `synchronous=FULL` et la reprise après plantage.** Ils arrivent à M5. Avant M5, un changement incompatible de format fait monter sa version, et les données sont régénérées (niveau 1, §7).
*   **Les événements v1, Parquet et la page d'accueil.** Ils arrivent à M2. Les événements v0 sont des fichiers JSONL jetables.
*   **L'environnement d'entraînement, l'encodeur, le décodeur, `obs_spec_version` et `action_spec_version`.** Ils arrivent à M4.
*   **La télémétrie technique.** Elle arrive à M5.
*   **Le scénario « dix premières minutes d'un joueur », les captures du client et la vidéo.** Ils arrivent à M3.
*   **L'assurance, le gouvernement, les banques et les institutions** (niveau 1, Non-Goals).
*   **L'univers du jeu et les noms propres.** Aucun nom de lieu, de minerai ou de vaisseau n'est inventé : `docs/noms-valides.md` est vide.
*   **Rust.** Le passage n'est envisagé que si le déclencheur du niveau 1, §2, est atteint, et il ne peut pas l'être avant M4.

**Ajoutés par l'amendement 1 :**

*   **Le « fun ».** Il est attendu des mécaniques des jalons suivants.
*   **Un monde au-delà des fourchettes, ou un troisième minerai.** Le monde reste petit : 12 systèmes au plus, deux minerais.
*   **(amendement 2, réécrit) La disposition définitive de l'écran.** L'amendement 2 fixe la disposition du Technical Plan, point 7 ter, faite de cadres indépendants. Elle n'est pas figée.
*   **(amendement 2, réécrit) Le tutoriel complet, le choix entre plusieurs thèmes de couleur et le mode rejeu du client** (M3). L'amendement 2 apporte la souris, une seule palette 8 bits et une aide ouverte au lancement de chaque partie.
*   **(amendement 2) Une carte animée et une mini-carte.** La disposition est calculée une fois (décision du propriétaire, 2026-11-22, alternative AF) ; la mini-carte sert peu sur 8 à 12 systèmes (Future Improvements).
*   **Une flotte : plusieurs vaisseaux pour un même personnage.** Chaque personnage, humain ou PNJ, a un vaisseau. Il n'y a pas non plus de types de vaisseaux, de lasers de minage ni de distances variables. Plus tard, la durée d'un minage dépendra du laser du vaisseau et de la capacité de sa cargaison, et celle d'un saut de sa vitesse et de la distance. À M1, tous les sauts entre voisins ont la même durée.
*   **Les dommages.** Il n'y en a pas à M1. Les alertes de dommages viendront avec eux.
*   **D'autres alertes que la fin du minage et l'arrivée à destination.** La table des alertes sera retravaillée plus tard (ventes, refus, dommages).
*   **Un marché** (M6). Plus tard, le marché fixera les prix selon la nature du minerai et la demande, et non selon la distance.
*   **Un PNJ plus habile.** La politique `scripted_miner` reste simple. Sa nouvelle version choisit parmi plusieurs gisements et plusieurs stations par une règle fixe, avec pour seule mémoire les gisements vus vides : le prix choisit le minerai et la station de vente, sans peser la durée du trajet ; exception : un vaisseau déjà dans le système d'une station y vend (règle 1) ; la distance ne sert qu'à choisir le gisement et à départager. Plus tard, les PNJ prendront des décisions individuelles, voire collectives, par exemple miner un minerai peu rentable parce que leur corporation en a besoin (M6).
*   **Un ordre « arrêter » ou un changement de route pendant un saut.** Ce serait un changement des règles.
*   **La reprise d'une partie interrompue** (M5).
*   **La période ou l'accélération transmises au joueur par le protocole ou l'observation.** La période n'est pas une donnée du jeu.
*   **Une hausse de `RULES_REVISION`.** Il passera de 0 à 1 à la première création des références, au volet C.

## Open Questions

Ces questions sont posées au propriétaire une à une pendant la rédaction. Une question tranchée quitte cette liste et rejoint le Technical Plan.

Aucune question ouverte. Le propriétaire a confirmé, le 2026-11-08, toutes les lignes du Technical Plan, point 1, marquées « proposition de l'agent de code ».

**(amendement 1)** L'amendement n'ouvre aucune question. La mise en veille de l'ordinateur portable, qui n'a d'effet ni sur les règles ni sur le rejeu, est un risque, que mesure un essai au plan détaillé, point 23 quater.

**(amendement 2)** L'amendement 2 n'ouvre aucune question : les cinq décisions posées pendant sa revue ont été prises par le propriétaire le 2026-11-22, et rejoignent le tableau du Technical Plan, point 1.

## Critical User Journeys (CUJs)

**(amendement 1)**

Cette section est ajoutée par l'amendement 1. Le CUJ 1 et le CUJ 4 du niveau 1 sont inchangés, à l'élargissement des fourchettes près (ADR 0004). Ce parcours précise ce que le propriétaire vit sur le client de l'amendement. Ses étiquettes Given / When / Then suivent le gabarit d'EGM, en anglais.

### CUJ A : un cycle complet, lu sur l'écran (amendement 1)

*   **Given :** une partie locale vient de démarrer. Le vaisseau du propriétaire est dans le système d'une station, cargaison vide. L'écran montre la carte en graphe, les gisements de chaque minerai (stock connu pour les seuls gisements proches), les prix de chaque station, les vaisseaux proches (dans son système et les systèmes voisins) et la barre d'état (tick, solde ; en mode développement, la vitesse demandée). **(amendement 2, précisé)** L'aide « Comment jouer » est ouverte au démarrage ; il la ferme par Entrée. L'écran est celui du Technical Plan, point 7 ter.
*   **When :** il choisit dans la liste des destinations le système d'un gisement, confirme, puis (en mode développement) accélère l'univers. À l'arrivée, il mine ; à la fin du minage, il va à la station de son choix et vend.
*   **Then :**
    - avant de confirmer un déplacement, il voit son coût : nombre de sauts, ticks, et une estimation en minutes à la période nominale ;
    - pendant le trajet, l'écran montre « en route », le système visé et les ticks restants ;
    - une alerte, qu'il acquitte par Entrée, signale l'arrivée à destination ; une autre signale la fin du minage ;
    - si un ordre est refusé, le message dit pourquoi, en français, et, pour un refus lié à un lieu, où aller ;
    - la vente affiche le prix de la station, le paiement et la taxe ;
    - la vitesse de l'univers ne change pas les règles : un saut dure toujours `jump_ticks` ticks ; rejouée depuis son journal, la partie redonne les mêmes empreintes.


--------------------------------------------------------------------------------

## Technical Plan (Architecture)

**(amendement 1)**

**Vue d'ensemble.** Les passages de l'amendement s'insèrent dans les points existants du Technical Plan, sous les formes de la légende des marques (en-tête) ; le texte d'origine qu'ils remplacent est récrit sur place, avec la marque « (amendement 1, réécrit) ». Rien n'est renuméroté : le point 7 bis est nouveau. **(amendement 2, précisé)** L'amendement 2 ajoute de même le point 7 ter.

```text
             graine + réglages
                    │
                    ▼
   core.world.generate ── 8 à 12 systèmes (arbre + liens), 4 à 6 gisements, 2 à 3 stations
                    │
                    ▼
   core.step  (durées en ticks : saut 400, minage 1 unité/tick ; vente à la station du système)
                    │
                    ▼
   core.observe(état, acteur, réglages)            ADR 0003 : vue des réglages publics
     ├─ carte complète (systèmes, liens, emplacement des gisements, stations et leurs prix)
     ├─ mes vaisseaux (tous leurs champs)
     ├─ autres vaisseaux et stock des gisements : proximité seulement    ADR 0005
     └─ réglages publics : jump_ticks, mining_rate
                    │ TickUpdate (protocol_version 2), seul canal vers le joueur
                    ▼
   server.game.Game ── horloge : période nominale 3 s ; vitesse, pause (fonction de rappel, --dev)
       │                         speed.jsonl dans le dossier de la partie
       ├── connexion du propriétaire ──► clients : modèle pur ─► cadres Textual (écran unique)
       └── connexions des PNJ ──► tâche de relais ─► NpcHost(scripted_miner v2)
```

### 1. Décisions prises pour M1

**Règle de rédaction (propriétaire, 2026-11-02).** M1 fait le minimum possible **dans le cadre déjà fixé** par le niveau 1. Ce document ne réduit aucune exigence du niveau 1, n'en ajoute aucune sauf le seuil de mutation ci-dessous et les objectifs 12 à 19, et ne le change que par les ADR 0003 à 0006 (amendement 2, réécrit) : chaque contrôle obligatoire de M1 est livré. Quand une question de contenu du jeu a plusieurs réponses, la plus petite qui respecte le niveau 1 est retenue. **(amendement 1, précisé)** Les décisions du propriétaire prises pour l'amendement 1, du 2026-11-12 au 2026-11-21, priment aussi sur cette règle du minimum : elles vont au-delà (objectifs 12 à 16). **(amendement 2, précisé)** Les décisions du propriétaire du 2026-11-22 (écran rétro, objectifs 17 à 19, et les lignes datées du 2026-11-22 du tableau ci-dessous) priment de même. Le critère de sortie de M1 (niveau 1, §11, « client Textual minimal ») ne change pas : le verdict sur l'écran rétro ne bloque pas la livraison (plan détaillé, point 23 undecies).

**Décisions sur le contenu du jeu (propriétaire, 2026-11-06).** Après la rédaction, pendant la revue de l'univers et de la conception du jeu (documents hors de `main`), le propriétaire a tranché quatre points du contenu de la tranche 0. Ils priment sur la règle du minimum et figurent dans le tableau ci-dessous (lignes datées du 2026-11-06, sans autre mention). Aucun ne change le niveau 1.

**Propositions de l'agent de code (2026-11-06), confirmées par le propriétaire le 2026-11-08.** Pendant la revue EGM de ce document, le propriétaire a délégué à l'agent de code les choix techniques que la revue a fait apparaître. Ces lignes portent la mention « proposition de l'agent de code » ; le propriétaire les a toutes confirmées le 2026-11-08, au passage à Approved. **(amendement 1, précisé)** La ligne « Prix des stations », proposée par l'agent de code pour l'amendement, a été confirmée le 2026-11-12.

| Question | Décision | Raison |
| :-- | :-- | :-- |
| Perte de vaisseau | aucune à M1 | le niveau 1 ne l'exige pas ; l'ajouter changerait l'invariant 3 du niveau 1, §4 |
| Noms et identifiants | dans l'état, chaque entité a un identifiant entier, propre à sa table, à partir de 1 ; les scénarios et le client affichent des libellés neutres tirés de l'identifiant (Technical Plan, point 13) | le niveau 1, §2, exige des tables indexées par un identifiant entier ; `docs/noms-valides.md` est vide ; les exemples de `CLAUDE.md` (`station_a`, `ore_1`) ne sont que des exemples |
| Rythme du temps | une horloge du serveur fait avancer les ticks ; sa période est un paramètre du serveur, hors des règles | le niveau 1, §2, ordonne chaque tick autour de la réception des ordres (« reçus avant le début du tick T+1 »), ce qui suppose des ticks cadencés par le serveur ; voir l'alternative C |
| Preuve sur le PC d'entraînement | le propriétaire lance la commande de rejeu sur le PC d'entraînement, à la fin du jalon, et sa sortie va dans le compte rendu de M1 | seul le propriétaire a accès à cette machine ; aucune adresse ni aucun identifiant n'entre dans le dépôt |
| Fourchettes économiques (amendement 1, réécrit) | les fourchettes portent sur l'émission par motif, la destruction par motif et la croissance de la masse monétaire, **par fenêtre de 10 000 ticks** (Technical Plan, point 9) ; les bornes sont au plan détaillé, point 27 | à prix fixes, la station paie chaque vente par une émission et seule la taxe détruit de l'argent : la masse monétaire ne peut que croître, et seule sa croissance par fenêtre peut rester dans une fourchette ; par l'invariant 2, cette croissance vaut l'émission moins la destruction |
| Point de départ du jeu | un module à la racine du paquet, `fourx/__main__.py`, assemble le serveur en mémoire et le client | `clients` ne peut pas importer `server`, ni `server` importer `clients` (niveau 1, §1) ; seule la racine du paquet peut les relier, et les contrats d'imports ne la contraignent pas |
| Outil de mutation | `mutmut` 3.8.0 (choix du propriétaire) | essayé sous Python 3.15 avec pytest 9.1.1 le 2026-11-02 : fonctionne ; cassé par pytest 9.2.0, donc pytest est plafonné sous 9.2 et toute montée de pytest est vérifiée avec `mutmut` avant d'être acceptée |
| Mode rejeu du client | son identifiant est fixé ici ; il est construit à M3, avec la vidéo rendue depuis un rejeu | aucun critère de sortie de M1 ne l'exige ; l'outil de divergence suffit au CUJ 4 |
| Station (2026-11-06) | une structure du jeu, pas un personnage : sans `actor_id` ni portefeuille ; elle paie chaque vente par une émission | décision du propriétaire ; le niveau 1, CUJ 1, dit « station PNJ » : la formule désigne ici une structure dont le comportement est fixé par les règles, pas un acteur |
| Gisements (2026-11-06 ; amendement 1, réécrit) | finis : chaque gisement a un stock, qui baisse au minage et revient à `deposit_stock` tous les `regen_ticks` ticks (régénération d'un gisement) | décision du propriétaire : un stock large, qui finit par se vider, oblige les mineurs, surtout quand ils viennent à plusieurs, à changer de gisement ; dans le monde en ligne, la régénération d'un gisement a lieu environ chaque semaine. À M1, un gisement peut se vider, surtout s'il partage son système avec une station ; la partie de référence peut alors faire jouer l'épuisement et la régénération (Technical Plan, point 9), et l'épuisement comme le départage sont vérifiés par les scénarios et les tests de propriétés |
| Visibilité de la vente (2026-11-06) | le vendeur voit sa vente, son paiement et sa taxe dans un événement privé ; les écritures du registre et les compteurs d'émission et de destruction relèvent de l'administration ; aucun acteur ne voit le portefeuille d'un autre | décision du propriétaire (personne ne voit le compte en banque d'un autre, ni l'argent créé par le jeu) ; le niveau 1, CUJ 1, exige que le client affiche le paiement |
| Argent de départ (2026-11-06) | aucun : tout portefeuille commence à zéro ; le vaisseau de départ est une dotation, sans écriture | décision du propriétaire |
| Arrondi de la taxe | vers le haut, au profit du compte de destruction | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : arrondie vers zéro, une taxe s'annulerait sur des ventes découpées en petits lots |
| Seuil de mutation | le contrôle `mutation` échoue si un fichier nouveau de `core` ou de `schema` a moins de 80 % de mutants tués ; la mutation complète du noyau, de nuit, aussi ; le seuil est revu au plan détaillé, point 28 bis | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, exigence ajoutée au niveau 1, comme les objectifs 12 à 19 des amendements (amendement 2, réécrit) : à M1, tous les fichiers sont nouveaux, donc la règle du niveau 1 (« jamais inférieur au score de `main` ») ne vérifie rien sans plancher ; il est limité à `core` et `schema`, où les mutants équivalents sont rares, et non au code d'entrées et de sorties |
| Résultats d'ordre | `State` garde les événements et les résultats d'ordre du dernier tick ; la réception applique la validation sans état (niveau 1, §2) ; un ordre qu'elle refuse est quand même journalisé, avec son code de refus, et `step` le refuse avec ce code, sans autre contrôle | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, dans le cadre du niveau 1, §2 (la réception fait les contrôles sans état, `step` ceux qui dépendent de l'état) : `observe` ne lit que l'état et le joueur n'a pas d'autre canal que l'observation (niveau 1, §5) ; le refus de la réception doit donc passer par le journal, puis par `step`, pour arriver dans l'observation et être reproduit au rejeu |
| Ordres d'un même tick | un seul ordre examiné par vaisseau et par tick, celui de plus petit numéro, comme pour le quota ; les autres sont refusés (« ordre remplacé ») ; tout ordre sur un vaisseau en route est refusé | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : sinon deux ventes validées contre le même état pourraient vendre plus que la cargaison (invariant 3) |
| Partie de référence | jouée une fois par ses `npc_count(1, réglages)` PNJ (amendement 1, réécrit) à la régénération des références ; son journal des ordres soumis est exporté en JSONL versionné, avec ses empreintes, dans `tests/references/` ; le contrôle `rejeu` l'importe et le rejoue par `step` seul, avec l'outil de rejeu de `tools` | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : sinon un changement du PNJ ou du serveur, sans changement de règle, changerait les empreintes et ferait monter `rules_version`, que M4 enregistre et que M5 compare au déploiement |
| Concurrence | une seule boucle `asyncio` : l'horloge est une tâche de cette boucle, à côté de Textual ; un mode sans horloge, synchrone, sert aux tests, aux outils et à la partie de référence | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : Textual tourne déjà sur `asyncio`, et le transport WebSocket de M3 aussi |
| Tâche `tests-outillage` | inchangée jusqu'au palier 4 ; au palier 4, limitée à `tests/outillage`, quand la tâche `tests` devient obligatoire | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : le document de M0 prévoyait que `tests-outillage` « devient `tests` » ; renommer un contrôle obligatoire bloquerait toute fusion entre la pull request qui le renomme et la commande de protection ; jusqu'au palier 4, `tests-outillage` lance toute la suite et garde l'échec attendu des scénarios en attente dans un contrôle obligatoire (niveau 2 de M0) |
| Relecture de la protection | une tâche de nuit relit la protection de `main` par la route `GET /repos/EZPK/4X/branches/main`, avec le `GITHUB_TOKEN` en lecture seule (palier 4) | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, qui tient l'engagement du document de M0 : cette route ne demande aucun droit d'administration ; lue sans jeton le 2026-11-06, elle renvoie `protected`, `required_status_checks.enforcement_level` (`everyone`) et la liste des contrôles exigés ; `strict`, `allow_force_pushes` et `allow_deletions` n'y figurent pas et restent vérifiés à la main (plan détaillé, point 31) |
| Fichiers de configuration du dépôt | `pyproject.toml`, `uv.lock` et `.gitignore` deviennent des chemins protégés, au palier 1 | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, qui revient sur l'alternative K du document de M0 (`pyproject.toml` non protégé) : la pull request protégée du palier 2 doit les modifier, or une pull request protégée ne contient que des chemins protégés (`CLAUDE.md`) ; une table `[tool.mutmut]` dans `pyproject.toml` masquerait aussi la configuration protégée de `setup.cfg`. Conséquence : toute nouvelle dépendance passe ensuite par une pull request protégée |
| Copie de référence de la protection dans le hook | au palier 4, le propriétaire met à jour `REFERENCE_PROTECTION` de `.claude/hooks/garde_commandes.py` avec la nouvelle liste des contrôles, selon la procédure de `CLAUDE.md` | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : `tests/outillage/test_garde_commandes.py` exige que `.github/protection-main.json` soit égal à cette copie ; l'agent de code n'édite pas `.claude/` |
| Taille de la tranche 0 (amendement 1, réécrit) | tirée par la graine : 8 à 12 systèmes, 4 à 6 gisements, 2 à 3 stations, 2 minerais, 3 à 5 PNJ ; 1 vaisseau par personnage | décision du propriétaire (2026-11-12) : plus de nœuds, d'endroits où miner, de vaisseaux qui bougent et de points de vente, « sans rentrer dans l'excessif » ; ADR 0004 |
| Rythme du temps (amendement 1, complète la ligne d'origine) | les durées sont des règles, en ticks : `jump_ticks` ticks par saut (400 dans les valeurs initiales), `cargo_capacity` ÷ `mining_rate` ticks pour remplir une cargaison vide (100) ; période nominale de l'horloge : 3 s | décision du propriétaire (2026-11-12) : le temps est une ressource ; les minutes ne sont qu'une estimation d'affichage |
| Réglages publics (amendement 1) | `observe` reçoit les réglages et publie `jump_ticks` et `mining_rate` dans l'observation | décision du propriétaire (2026-11-12) ; le niveau 1 interdit tout autre canal vers le joueur ; ADR 0003 |
| Visibilité des autres vaisseaux (amendement 1) | par proximité : un vaisseau d'autrui, et le stock d'un gisement, ne sont visibles que dans le système d'un des vaisseaux de l'acteur ou dans un système voisin ; d'un vaisseau d'autrui, on ne voit que l'identifiant, le détenteur, le système et la capacité | décision du propriétaire (2026-11-12) ; plus tard, des scanners porteront plus loin ; ADR 0005 |
| Accélération de l'univers (amendement 1) | en mode développement seulement (`--dev`) : paliers de vitesse, pause, « avancer jusqu'à la prochaine alerte », par une fonction de rappel locale ; rien dans le protocole, le journal ou les règles | décisions du propriétaire (2026-11-12) : utiles au développement et aux essais ; en partie sans `--dev`, l'univers tourne à son rythme ; ce n'est pas l'alternative C (ticks avancés à la demande d'un joueur, sur un serveur partagé) ; la vitesse de l'univers (secondes par tick) n'est pas celle du vaisseau (ticks par saut, une règle) |
| PNJ (amendement 1) | `scripted_miner` version 2 (règle au point 7), qui retient les gisements vus vides ; en mode avec horloge, la tâche de relais lui transmet les mises à jour | décisions du propriétaire (2026-11-12 et 2026-11-21) ; la politique reste simple : elle choisit le minerai et la station par le prix, sans peser la durée du trajet ; exception : un vaisseau déjà dans le système d'une station y vend (règle 1) |
| Colocalisation (amendement 1) | une station et un gisement peuvent partager un système | décision du propriétaire (2026-11-12) : un gisement dans le système d'une station peut s'épuiser vite, et l'épuisement oblige joueurs et PNJ à aller miner ailleurs ; voir l'alternative AA |
| Prix des stations (amendement 1) | `station_ore_prices` = [[10, 15], [12, 12], [8, 18]] | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-12 ; la station 1 garde les prix d'origine |
| (amendement 2) Carte de l'écran rétro | disposition calculée une fois par partie, sans animation (alternative AF) | décision du propriétaire, 2026-11-22 |
| (amendement 2) Souris | molette, glisser, survol et clic ; pas de mini-carte (Future Improvements) | décision du propriétaire, 2026-11-22 |
| (amendement 2) Découpage du code de l'écran | deux pull requests de fonctionnalité : cadres, prochaine étape, aide et palette (plan détaillé, point 23 nonies), puis la carte (point 23 decies) | décision du propriétaire, 2026-11-22 |
| (amendement 2) Verdict sur l'écran rétro | il ne bloque pas la livraison de M1 ; le volet C avance en parallèle (plan détaillé, volet B ter et point 23 undecies) | décision du propriétaire, 2026-11-22 |
| (amendement 2) Conseil de la prochaine étape, à l'arrêt | le cycle qui rapporte le plus par tick (Technical Plan, point 7 ter ; alternative AH) | décision du propriétaire, 2026-11-22 |

### 2. Les règles de la tranche 0

**La carte.** Elle est tirée par la graine : 8 à 12 systèmes reliés en graphe, 4 à 6 gisements et 2 à 3 stations (génération du monde, plus bas dans ce point) (amendement 1, réécrit). Un saut vers un système voisin dure `jump_ticks` ticks. Chaque gisement a un stock : il commence à `deposit_stock` unités, baisse de ce qui est extrait, et revient à `deposit_stock` aux ticks multiples de `regen_ticks` (phase de règlement). Un gisement vide ne rend plus rien jusqu'à sa régénération.

**Les entités** (types au Technical Plan, point 13).

| Entité | Champs de données principaux |
| :-- | :-- |
| système | identifiant, voisins |
| gisement | identifiant, système, minerai, stock |
| station | identifiant, système, prix de rachat de chaque minerai (ceux de la ligne i de `station_ore_prices` pour la station d'identifiant i, copiés à la génération du monde (amendement 1, réécrit) ; une structure du jeu : ni acteur ni portefeuille) |
| acteur | identifiant (`id`, l'`actor_id` des formats), type d'acteur (`kind`, l'`actor_kind` des formats), budget d'actions |
| vaisseau | identifiant, acteur détenteur, système, activité (à l'arrêt, en route, en minage), route restante et ticks avant le prochain saut, cargaison par minerai, capacité |
| registre | comptes et leurs soldes, écritures du tick, compteurs cumulés d'émission et de destruction par motif (Technical Plan, point 3) |
| dernier tick | événements et résultats d'ordre produits par le dernier `step` |

**Les ordres.** Les codes de refus d'une ligne sont examinés de gauche à droite : le premier qui s'applique est retenu.

| Catégorie | Ordre | Effet | Refusé si (dans cet ordre) |
| :-- | :-- | :-- | :-- |
| joueur | déplacer un vaisseau vers un système | calcule le plus court chemin (parcours en largeur, voisins par identifiant croissant) et met le vaisseau en route | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, système inconnu, déjà sur place |
| joueur | miner un minerai | le vaisseau extrait à chaque tick, jusqu'à ce que la cargaison soit pleine ou que le gisement soit vide (il passe alors à l'arrêt), ou qu'un autre ordre remplace son activité | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, pas de gisement de ce minerai dans le système, gisement vide, cargaison pleine |
| joueur | vendre une quantité d'un minerai | la station du système rachète à son prix fixe (amendement 1, réécrit) ; la taxe est prélevée ; le vaisseau passe à l'arrêt | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, aucune station dans le système du vaisseau (amendement 1, réécrit), quantité nulle ou négative, quantité supérieure à la cargaison |
| administration | créer un personnage | crée l'acteur, son portefeuille personnel et un vaisseau vide, à l'arrêt, dans le système de sa station de départ (« Système de départ », plus bas dans ce point ; amendement 1, réécrit) | — (émis par le serveur seulement) |

- **Budget d'actions.** Un acteur commence avec `budget_max` actions. Chaque ordre de joueur accepté coûte une action ; un ordre refusé ne coûte rien. Un ordre qui passe tous les contrôles mais trouve le budget à zéro est refusé (« budget épuisé »).
- **Un ordre par vaisseau et par tick.** Si un acteur soumet plusieurs ordres sur le même vaisseau pour un tick, seul celui de plus petit numéro est examiné ; les autres sont refusés (« ordre remplacé »). Un ordre accepté remplace l'activité en cours du vaisseau dès l'examen, avant les phases du tick.
- **Ordres d'administration.** Le serveur les écrit directement dans le journal, sans passer par la réception, avec un acteur émetteur absent (`sender_actor_id` = `None`) et sans code de refus : ni validation sans état, ni quota, ni budget. `step` refuse (« catégorie interdite ») un ordre sans acteur émetteur qui n'est pas de la catégorie « administration ». L'acteur créé reçoit le prochain identifiant libre de la table des acteurs (le plus grand identifiant plus un) ; son vaisseau et son portefeuille font de même dans leur table. L'ordre porte comme `actor_id` l'identifiant que recevra l'acteur. Un client qui soumet, sous son propre `actor_id`, un ordre d'une autre catégorie que « joueur » voit son ordre refusé par la réception (« catégorie interdite »).
- La catégorie « système » existe dans les formats, mais aucun ordre système n'est émis à M1 : la déconnexion et le départ hors ligne arrivent avec les comptes, à M3.

**Le tick.** `step` suit la chronologie du niveau 1, §2 :
1. il examine chaque ordre soumis, par `actor_id` croissant puis par numéro croissant :
   - un ordre sans acteur émetteur qui n'est pas d'administration est refusé (`FORBIDDEN_CATEGORY`) ;
   - un ordre qui porte un code de refus de la réception (validation sans état, Technical Plan, point 5) est refusé avec ce code ;
   - puis un ordre par vaisseau, puis les contrôles du tableau, puis le budget.

   Chaque ordre reçoit un résultat ; un refus produit aussi un événement ;
2. il exécute les phases du tick, dans leur suite fixe :
   - **déplacement :** chaque vaisseau en route décompte son trajet ; à la fin d'un saut, il quitte son système (événement « départ ») et entre dans le suivant (événement « arrivée ») ; au bout de sa route, il passe à l'arrêt ;
   - **minage :** chaque vaisseau en minage extrait jusqu'à `mining_rate` unités, sans dépasser sa capacité libre ni le stock du gisement. Quand plusieurs vaisseaux minent le même gisement et que le stock ne suffit pas à tous, ils sont servis dans l'ordre du départage : chacun reçoit le minimum de `mining_rate`, de sa capacité libre et du stock restant ; un vaisseau servi après l'épuisement ne reçoit rien. Un vaisseau dont la cargaison devient pleine, ou dont le gisement est vide, passe à l'arrêt (événement « fin de minage ») ;
   - **commerce :** chaque vente acceptée retire le minerai de la cargaison et produit deux écritures (Technical Plan, point 3) ;
   - **combat :** vide à M1 ;
   - **règlement :** chaque acteur regagne `budget_regen` actions, sans dépasser `budget_max` ; aux ticks multiples de `regen_ticks`, chaque gisement revient à `deposit_stock` (événement « régénération d'un gisement »).

**Le départage.** La seule égalité possible à M1 est celle de plusieurs vaisseaux sur un gisement dont le stock ne suffit pas. Chaque vaisseau concerné reçoit un tirage à clé sur (graine du monde, tick, identifiant du vaisseau, motif du tirage « minage ») ; les vaisseaux sont servis par tirage croissant, puis par identifiant croissant en cas d'égalité des tirages. Chaque station rachète sans limite (amendement 1, réécrit) : aucune vente n'est donc départagée.

**Les réglages.** (amendement 1, réécrit) Toutes les valeurs vivent dans `tunables.toml`, sous les noms du type `Tunables` (Technical Plan, point 13) : `jump_ticks`, `mining_rate`, `cargo_capacity`, `station_ore_prices`, `tax_rate_bp` (taux de taxe en points de base), `deposit_stock`, `regen_ticks`, `budget_regen`, `budget_max`, et les fourchettes de la génération du monde. Leurs valeurs initiales sont au tableau des réglages, plus bas dans ce point. Le serveur lit ce fichier et passe les réglages à `step` ; le noyau ne lit aucun fichier. `world.generate` donne à chaque station sa ligne de `station_ore_prices` : pendant la partie, le prix qui fait foi est celui de la station, et il est public, pour que le client et la politique le voient.

**(amendement 1)**

**Génération du monde (`world.generate`).** Chaque tirage est `keyed_below(graine, 0, entité, motif, n)` (Technical Plan, point 4), avec l'entité et le motif donnés à chaque étape ; deux tirages n'ont jamais la même clé. Un nombre tiré « entre a et b » vaut a + `keyed_below`(…, b − a + 1). Chaque liste de candidats est triée par identifiant avant le tirage : le même monde sort de la même graine sous tout `PYTHONHASHSEED`.

1. **Nombre de systèmes** N, entre `systems_min` et `systems_max` (8 et 12) : entité 0, motif `"world_size"`.
2. **Arbre.** Pour k = 2 à N, le système k se relie à un système déjà placé, tiré parmi ceux qui ont moins de `max_neighbors` voisins (4) : entité k, motif `"tree"`. Le plafond garde la carte dessinable. `System.neighbors` est toujours trié par identifiant croissant : l'ordre entre dans l'encodage, donc dans les empreintes.
3. **Liens en plus.** Leur nombre L est tiré entre 1 et `extra_links_max` (3) : entité 0, motif `"extra_link_count"`. Le lien i (i = 1 à L) relie une paire de systèmes non voisins, tous deux sous le plafond, tirée parmi toutes les paires (a, b), a < b, triées par a puis par b : entité i, motif `"extra_links"`. S'il ne reste aucune paire, on s'arrête.
4. **Stations.** Leur nombre S est tiré entre `stations_min` et `stations_max` (2 et 3) : entité 0, motif `"station_count"`. La station d'identifiant i (i = 1 à S) est placée parmi les systèmes qui n'ont pas encore de station : entité i, motif `"stations"` ; elle rachète aux prix de la ligne i de `station_ore_prices`.
5. **Gisements.** Leur nombre G est tiré entre `deposits_min` et `deposits_max` (4 et 6) : entité 0, motif `"deposit_count"`. Le gisement d'identifiant i (i = 1 à G) est placé parmi les systèmes qui n'ont pas encore de gisement : entité i, motif `"deposits"` ; il porte le minerai 1 (`ore_a`) si i est impair et le minerai 2 (`ore_b`) sinon, donc au moins deux gisements de chaque minerai. Un système peut avoir une station et un gisement : c'est voulu (colocalisation, alternative AA). Un système a au plus une station et au plus un gisement.
6. **Nombre de PNJ.** `npc_count(graine, réglages)` le tire entre `npc_min` et `npc_max` (3 et 5) : entité 0, motif `"npc_count"`. Ce n'est pas un champ de l'état : `__main__.py` crée les PNJ par des ordres d'administration au tick 1, comme dans le code d'origine. La fonction vit dans `core.world` parce que c'est un tirage de la graine du monde, comme la génération. `npc_min` et `npc_max` sont dans `Tunables`, donc dans `rules_version`, bien que `step` ne les lise pas : c'est voulu, la population fait partie du monde de référence.

**Déplacement.** Inchangé : route la plus courte (`plus_court_chemin`, voisins par identifiant croissant), un saut tous les `jump_ticks` ticks. Seule la valeur change : 400 dans les valeurs initiales.

**Minage.** Inchangé, au débit `mining_rate` = 1 unité par tick. Le gisement visé est celui du système du vaisseau, s'il porte le minerai demandé. La durée pour remplir une cargaison vide est `cargo_capacity` ÷ `mining_rate` = 100 ticks.

**Vente.** Elle se fait à la station du système du vaisseau, au prix de cette station. Sans station dans le système, l'ordre est refusé (`NOT_AT_STATION`). La taxe est inchangée.

**Système de départ.** Le vaisseau d'un nouveau personnage d'identifiant *n* démarre dans le système de la station de rang `rem_trunc(n − 1, S)`, les stations étant triées par identifiant (rang 0 : la station d'identifiant le plus petit). Le propriétaire, créé le premier, part de la station 1 ; les PNJ se répartissent sur les stations.

**Réglages (`tunables.toml`).** `tunables.toml` fait foi (niveau 1). Le tableau donne les valeurs initiales de l'amendement ; une valeur changée plus tard ne change que `tunables.toml`.

| Réglage | Avant | Après | Effet |
| :-- | :-- | :-- | :-- |
| `jump_ticks` | 5 | 400 | 20 min par saut à 3 s |
| `mining_rate` | 10 | 1 | 100 ticks pour remplir une cargaison vide |
| `cargo_capacity` | 100 | 100 | inchangé |
| `ore_prices` | [10, 15] | supprimé | remplacé par `station_ore_prices` |
| `station_ore_prices` | — | [[10, 15], [12, 12], [8, 18]] (proposition de l'agent de code, confirmée par le propriétaire le 2026-11-12) | au moins `stations_max` lignes ; la station d'identifiant i prend la ligne i |
| `tax_rate_bp` | 1000 | 1000 | inchangé |
| `deposit_stock` | 20 000 | 20 000 | inchangé |
| `regen_ticks` | 1 000 | 10 000 | aligné sur les fenêtres d'économie ; à 1 000, un gisement se régénérait avant d'avoir pu se vider, et le stock n'avait plus d'effet ; un gisement vidé redevient plein au plus tard 10 000 ticks après |
| `budget_regen`, `budget_max` | 1, 10 | 1, 10 | inchangés : avec quelques ordres par cycle, qui dure au moins 100 ticks, le budget ne limite personne ; il resservira avec plusieurs vaisseaux |
| `systems_min`, `systems_max` | — | 8, 12 | fourchettes de l'ADR 0004 |
| `deposits_min`, `deposits_max` | — | 4, 6 | idem |
| `stations_min`, `stations_max` | — | 2, 3 | idem |
| `npc_min`, `npc_max` | — | 3, 5 | idem |
| `extra_links_max` | — | 3 | liens qui créent des boucles |
| `max_neighbors` | — | 4 | plafond de voisins, pour la carte à l'écran |

Le décodage de `tunables.toml` en `Tunables` vérifie en plus : chaque minimum ne dépasse pas son maximum ; `station_ore_prices` a au moins `stations_max` lignes, chacune de 2 prix positifs ; `deposits_min` ≥ 4 (deux gisements par minerai) ; `systems_min` ≥ `deposits_max` et ≥ `stations_max` (assez de systèmes distincts) ; `max_neighbors` ≥ 2 (sinon l'arbre n'a plus de candidat dès le troisième système) ; `extra_links_max` ≥ 1 (le nombre de liens en plus est tiré à partir de 1) ; `npc_min` ≥ 1.

`rules_version` change sans autre intervention, par l'empreinte des réglages. `RULES_REVISION` reste à 0.

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

- **L'état** est un enregistrement `msgspec.Struct` figé, qui contient une table par type d'entité. Une table est un tuple d'enregistrements figés, trié par identifiant croissant. Chaque phase du tick produit de nouvelles tables à partir des précédentes (`msgspec.structs.replace`) : c'est la stratégie de copie par défaut du niveau 1 (niveau 1, alternative R), confirmée ici. Aucun dictionnaire ni ensemble n'apparaît dans l'état. La graine du monde n'est pas dans l'état : elle est passée à `step` (niveau 1, §2), et elle est enregistrée dans l'instantané initial et dans le journal.
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
- **Résultat d'ordre :** acteur destinataire (celui du point de connexion ; `None` pour un ordre du serveur, dont le résultat n'est observé par personne), identité de l'ordre, accepté ou code de refus, texte, budget restant (niveau 1, §5). Chaque ordre examiné par `step` reçoit un résultat.
- **Observation :** (amendement 1, réécrit) le tick, l'état visible pour l'acteur, les événements du dernier tick qui lui sont visibles, ses résultats d'ordre et la vue des réglages publics (voir ci-dessous). `observe` lit tout cela dans l'état (table « dernier tick ») et dans les réglages qu'il reçoit (ADR 0003).
- **Visibilité.** Chaque champ de données des entités de l'état déclare sa classe de visibilité par `Annotated[T, msgspec.Meta(extra={"visibility": ...})]` ; `observe` relit ces métadonnées par `msgspec.inspect.type_info` (mécanisme essayé sur `msgspec` 0.22.0 le 2026-11-06 : la métadonnée revient comme `Metadata` avec son `extra`). Chaque type d'événement a une seule classe. « Privé » veut dire visible par le seul acteur qui détient l'entité. Les vues de l'observation reprennent les noms des champs de données de l'état. À M1 :
  - publics (amendement 1, réécrit) : les systèmes et leurs voisins, les sites, le minerai des gisements, les prix de rachat des stations, le `kind` de chaque acteur (`actor_kind`, niveau 1, §5) ; le stock des gisements et les vaisseaux d'autrui (identifiant, détenteur, système, capacité) sont de classe proximité (voir ci-dessous) ;
  - privés : la cargaison, l'activité, la route, les ticks avant le prochain saut et le minage en cours d'un vaisseau, le budget d'actions, le solde (`balance`) du portefeuille personnel ;
  - administration : les écritures du registre, les comptes d'émission et de destruction, les compteurs cumulés.

  Un acteur attentif peut déduire une partie de l'activité d'un autre acteur à partir de la position de ses vaisseaux, du stock des gisements et des prix fixes. Les deux premiers indices étant de classe proximité, cette déduction n'est possible qu'à portée ; c'est accepté à M1 (amendement 1, réécrit).
- **Événements v0** (`event_schema_version` = 0) : l'enveloppe du niveau 1, §6 : `tick` et `seq`, `event_schema_version` et `rules_version`, `actor_id` et `actor_kind`, `policy_id` et `policy_version`, `causation_id`, la classe de visibilité. `actor_id`, `actor_kind` et `causation_id` sont `None` pour un fait des règles (régénération d'un gisement). `causation_id` est l'identité de l'ordre qui a causé l'événement. `seq` croît avec la production dans le tick : examen des ordres, puis phases du tick dans leur suite fixe, puis, dans une phase, identifiants croissants. Les types sont des types `msgspec`, exportables en JSON Schema :

  | Type d'événement | Classe | Contenu | Émis |
  | :-- | :-- | :-- | :-- |
  | personnage créé | public | acteur, `actor_kind`, vaisseau | à l'examen de l'ordre |
  | ordre refusé | privé | identité de l'ordre, code de refus | à l'examen de l'ordre |
  | départ | proximité (amendement 1, réécrit) | vaisseau, système quitté | à chaque saut, en phase de déplacement |
  | arrivée | proximité (amendement 1, réécrit) | vaisseau, système atteint | à chaque saut, en phase de déplacement |
  | début de minage | privé | vaisseau, minerai, débit (`mining_rate`) | à l'examen de l'ordre « miner » accepté |
  | fin de minage | privé | vaisseau, quantité extraite depuis le début | quand le minage s'arrête, pour toute raison |
  | vente | privé | quantité, prix, paiement, taxe | en phase de commerce |
  | régénération d'un gisement | proximité (amendement 1, réécrit) | gisement, stock | en phase de règlement |
  | écriture du registre | administration | l'écriture | quand l'écriture est passée |

  Le montant d'une vente n'est jamais public ; l'événement de vente suffit au client (niveau 1, CUJ 1). Il n'y a jamais un événement par entité et par tick (niveau 1, §6). **(amendement 1, précisé)** Quand les règles arrêtent un minage (cargaison pleine, gisement vide), sa fin de minage a `causation_id` = `None` ; quand un ordre remplace le minage, sa fin de minage porte l'identité de cet ordre (`_arreter_minage`, `core/step.py`).
- **Protocole** (`protocol_version` = 2 ; amendement 1, réécrit) : deux messages. Le client envoie « soumettre des ordres » ; le serveur envoie, après chaque tick, une « mise à jour du tick » qui porte l'observation.
- **Validation sans état** (`validate_orders`, fonction pure) : format (numéro positif ou nul, `policy_id` d'au plus 64 caractères), numéro répété dans un tick (le second et les suivants sont refusés), quota d'ordres par tick (`ORDER_QUOTA_PER_TICK`, valeur au plan détaillé, point 16 ; au-delà, les plus petits numéros sont gardés), ordre au nom d'un autre acteur que celui du point de connexion, catégorie autre que « joueur ». Les contrôles sont faits dans cet ordre, et le premier qui s'applique donne le code. La fonction reçoit, en une fois, tous les ordres d'un même point de connexion pour un tick : les numéros répétés et le quota se comptent par acteur du point de connexion (`sender_actor_id`), jamais par l'`actor_id` écrit dans l'ordre. Elle vit dans `schema` : la réception l'applique (niveau 1, §2), et, plus tard, l'entraînement l'appliquera de la même façon. Les ordres d'administration du serveur ne passent pas par elle.

**(amendement 1)**

- **`Observation`** reçoit le champ `public_tunables: PublicTunablesView` (`jump_ticks`, `mining_rate`), placé en dernier pour l'ordre d'encodage. La vue est construite en recopiant ces deux champs de `Tunables`, nommés un à un. La capacité de cargaison est déjà dans `OwnShipView.capacity`, et le paiement et la taxe d'une vente dans l'événement `Sale`. `Tunables` ne porte pas de classe de visibilité : il ne fait pas partie de l'état. Un test vérifie que les noms de la vue existent dans `Tunables`.
- **Classe de visibilité `NEARBY` (proximité)**, ajoutée à `Visibility` (ADR 0005). **Règle :** un champ ou un événement de classe `NEARBY` est visible d'un acteur si son *système de référence* est le système d'un des vaisseaux de l'acteur, ou un système voisin. Le système de référence est le `system_id` de l'entité, celui de la charge utile d'un événement, ou, pour un événement de gisement, le système du gisement ; un type qui porte un champ `NEARBY`, ou un type d'événement de classe `NEARBY`, doit avoir un tel système, ce qu'un test vérifie. Les positions qui comptent sont celles de l'état que reçoit `observe`. Un acteur sans vaisseau ne voit rien de classe proximité. **Hors de portée,** une entité dont l'identité est de classe proximité (un vaisseau d'autrui) disparaît de l'observation, et un champ de classe proximité d'une entité publique (le stock d'un gisement) vaut `None`.
  - **Vaisseaux d'autrui :** `id`, `owner_id`, `system_id` et `capacity` passent de `PUBLIC` à `NEARBY`. Un vaisseau d'autrui hors de portée n'apparaît pas du tout dans l'observation. Les vaisseaux de l'acteur restent entièrement visibles pour lui.
  - **Gisements :** `stock` passe de `PUBLIC` à `NEARBY` (décision du propriétaire, 2026-11-12) ; le gisement lui-même (identifiant, système, minerai) reste public. Hors de portée, la vue porte `stock` = `None` (`DepositView.stock: Int64 | None`). Sans cette règle, la baisse du stock, à un débit d'une unité par tick, permettrait de compter les vaisseaux qui minent loin.
  - **Événements :** `Departed` et `Arrived` passent à `NEARBY`, rapportés à leur `system_id` ; `DepositRegenerated` aussi, rapporté au système du gisement, puisqu'il donne le stock. `CharacterCreated` reste public : il dit qu'un personnage existe. Avec la règle publique du système de départ (Technical Plan, point 2), il révèle aussi la station de départ de son vaisseau ; c'est accepté, puisque la carte est publique et la politique des PNJ déterministe.
- **`PROTOCOL_VERSION`** passe à 2 : l'observation reçoit un champ nouveau, `public_tunables`, et `DepositView.stock` change de type (il devient facultatif). La réception ne vérifie toujours pas la version à M1 (M3 le fera).
- **Versions des formats.** Les classes de visibilité des champs de l'état ne sont pas encodées, mais `Event.visibility` l'est, et `State.last_tick.events` entre dans l'instantané et dans l'empreinte `last_tick`. La valeur `nearby` casse donc la lecture d'un fichier récent par le code d'origine, pas l'inverse. C'est accepté parce qu'avant M5 les données sont régénérées, et non migrées (niveau 1, §7). `snapshot_schema_version` reste à 1 : l'instantané est pris au tick 0, avec un `last_tick` vide. `event_schema_version` reste à 0 : les événements v0 sont jetables.
- **`NOMINAL_TICK_PERIOD_S` = 3.0**, constante de `schema/protocol.py`, lue par le serveur (période par défaut) et par le client (estimation en minutes). C'est une constante du code, pas une donnée transmise : elle ne crée aucun canal.

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

- **La concurrence :** une seule boucle `asyncio`. L'horloge est une tâche de cette boucle. Chaque point de connexion est une paire de `asyncio.Queue` (ordres, mises à jour), derrière le protocole `Connection` de `schema`. Au début de chaque tick, l'horloge vide les files d'ordres : un ordre reçu avant ce moment entre dans ce tick (niveau 1, §2). Tous les messages vidés d'un même point de connexion sont remis ensemble à la réception, en un seul appel par point de connexion et par tick.
- **Le mode sans horloge** sert aux tests, aux outils et à la partie de référence. `Game.advance(n)` joue `n` ticks, de façon synchrone. À chaque tick : il prend les ordres soumis, appelle `step`, envoie la mise à jour à chaque client, puis appelle, pour chaque client synchrone attaché (`SyncClient`, Technical Plan, point 13), `on_update(mise à jour)` ; les ordres que cette méthode renvoie entrent au tick suivant. Une décision prend donc exactement un tick (amendement 1, réécrit).
- **L'horloge** déclenche un tick à chaque période. La période est un paramètre du serveur (la période nominale de 3 s par défaut, voir ci-dessous ; amendement 1, réécrit), hors de `tunables.toml` et hors de `rules_version`.
- **La réception** lie chaque ordre reçu à l'acteur de son point de connexion et au tick où il entre, applique la validation sans état à l'ensemble des ordres de ce point de connexion pour ce tick, puis le journalise avec son code de refus éventuel. `step` refuse un ordre qui porte un code, avec ce code, et adresse le résultat à l'acteur du point de connexion, par son observation.
- **Le journal des ordres soumis** est une base SQLite en mode WAL (`synchronous=NORMAL` avant M5), `orders.sqlite`, avec deux tables (schéma au plan détaillé, point 21). Il contient sa version (`order_log_schema_version` = 1), `rules_version`, la graine du monde, l'identifiant (SHA) du commit et un indicateur « dossier de travail modifié », les ordres soumis par tick et les empreintes de chaque tick. Il s'exporte et s'importe en JSONL versionné (plan détaillé, point 21).
- **Les fichiers d'une partie** sont rangés dans `runs/<AAAAMMJJ-HHMMSS-micro>/`, ignoré par git : `orders.sqlite`, `snapshot.msgpack` (instantané initial, tick 0, `snapshot_schema_version` = 1, avec `rules_version`, la graine, l'identifiant du commit et l'indicateur « dossier de travail modifié », fournis par le serveur) et `events.jsonl`.
- **Les personnages** sont créés par des ordres d'administration journalisés pour le tick 1, l'un pour le propriétaire, les autres pour les `npc_count` PNJ (amendement 1, réécrit) ; l'instantané initial est l'état du tick 0, avant ces ordres, et le premier `step` les applique.

**(amendement 1)**

- **Période nominale.** `Game(..., period_s=NOMINAL_TICK_PERIOD_S)`, et `--periode` a la même valeur par défaut. La valeur n'est écrite qu'à un endroit : `NOMINAL_TICK_PERIOD_S` (Technical Plan, point 5). `--periode` est une option de lancement, fixée pour toute la partie, qui sert aussi aux essais ; elle existe sans `--dev`, mais seul `--dev` permet de changer la période en cours de partie.
- **Premier tick immédiat.** `Game.run` joue un tick dès son lancement, puis attend une période entre deux ticks. Le joueur voit le monde tout de suite.
- **Vitesse.** `Game.set_period(period_s: float | None)` change la période ; `None` met en pause. Le changement réveille la boucle (par un `asyncio.Event`), qui recalcule l'attente restante avec la nouvelle période : un tick n'est joué tout de suite que si le temps déjà écoulé depuis le dernier tick dépasse la nouvelle période ; sinon, la boucle attend le reste. En pause, aucun tick n'est joué. Les paliers sont ×1, ×10 et ×100 de la période de lancement (3 s, 0,3 s et 0,03 s à la période nominale) ; la partie démarre au palier ×1, et le retour à ×1 ramène à la période de lancement ; la « vitesse maximale » est le palier ×100, où un saut dure 12 s et un cycle à deux sauts environ 51 s. En surcharge, un tick dure ce qu'il dure, puis l'horloge attend la période : la vitesse réelle reste sous la vitesse demandée (niveau 1, §2). Aucune contre-pression : le débordement de « avancer jusqu'à la prochaine alerte » est mesuré au plan détaillé, point 28 bis, et une contre-pression ou un palier plus rapide ne s'ajoutent que si la mesure le demande.
- **Enregistrement.** `speed.jsonl`, dans le dossier de la partie, commence par un en-tête versionné (`{"speed_log_schema_version": 1}`), puis la période initiale, sur une ligne `{"tick": 0, "period_s": P}` ; chaque changement ajoute une ligne `{"tick": T, "period_s": P}`, où T est le dernier tick joué et P la période en secondes, ou `null` en pause. Ce n'est pas le journal des ordres, et le rejeu ne le lit pas.
- **PNJ.** `__main__.py` crée `npc_count(graine, réglages)` PNJ. Chacun a sa connexion et sa tâche de relais (code d'origine), avec `NpcHost(acteur, scripted_miner.decide)`.
- **Fonction de rappel de vitesse, mode développement.** Avec `--dev`, `__main__.py` passe à `FourxApp` une fonction de rappel `set_speed: Callable[[int | None], None]`. Elle reçoit un facteur (1, 10 ou 100), ou `None` pour la pause, et appelle `Game.set_period(None if facteur is None else période de lancement ÷ facteur)` : le client choisit un palier sans connaître la période, et `Game.set_period` reçoit toujours des secondes. Sans `--dev`, il passe `None`, et le client n'offre aucune commande de vitesse. Le client n'importe pas `server` : il reçoit une simple fonction, ou rien. C'est la seule exception locale à « la même porte » (objectif 6) : elle ne commande que l'horloge de la partie locale, ni les règles ni le journal, et disparaît à M3, quand le client et le serveur ne partagent plus de processus.
- **Graine et dossier de la partie.** `__main__.py` les affiche au lancement (le code d'origine n'affiche que la graine), et de nouveau à la fermeture du client, puisque Textual efface l'affichage du lancement. Ils restent hors de l'écran de jeu : le client ne reçoit du jeu que l'observation (niveau 1, §5 ; ADR 0003).

### 7. Le client Textual et le PNJ

- **Le client** est décrit au Technical Plan, point 7 bis (amendement 1, réécrit).
- **Le PNJ de M1** joue la politique `scripted_miner` de `policies`, la référence scriptée du glossaire, en version 2 ; sa règle est ci-dessous (amendement 1, réécrit).
  Elle n'émet un ordre que si l'activité observée diffère de l'activité voulue : un vaisseau qui mine déjà ne reçoit pas de nouvel ordre « miner ». **L'hôte des PNJ** (`NpcHost`) la fait jouer par le même protocole que le client : il implémente `SyncClient` pour le mode sans horloge, et une tâche de `__main__.py` lui transmet les mises à jour en mode avec horloge.

**(amendement 1)**

`scripted_miner`, `policy_version` = 2. La politique reste une fonction pure. Sa seule mémoire, d'un tick à l'autre, est la liste des gisements que le vaisseau a vus vides : `decide` la reçoit et rend la liste à jour, que l'hôte des PNJ garde et lui repasse à la décision suivante (décision du propriétaire, 2026-11-21). Avant de décider, `decide` met la liste à jour à partir de l'observation : un gisement visible de stock nul y entre ; un gisement visible de stock positif en sort ; quand tous les gisements du monde y sont, la liste se vide, et le vaisseau recommence à chercher. La liste est un ensemble d'identifiants (`frozenset[int]`). Un gisement régénéré hors de portée y reste jusqu'à ce que le vaisseau le revoie, ou que la liste se vide : le PNJ peut miner plus loin pendant ce temps, ce qui est accepté. Vu du niveau 1, §1, le joueur PNJ est l'hôte et sa politique ensemble : il reçoit une observation et rend des ordres. La liste ne vit que dans l'hôte des PNJ : elle n'entre ni dans l'état ni dans le journal, et le rejeu, qui suit le journal des ordres, reste exact. Pour chaque vaisseau à l'arrêt ou en minage :
1. **Dans le système d'une station, hors minage, cargaison non vide :** vendre le minerai le plus abondant (à quantités égales, le plus petit identifiant).
2. **Cargaison pleine, ailleurs :** aller à la station qui paie le mieux le minerai le plus abondant de la cargaison (à prix égal, la plus proche en sauts, puis le plus petit identifiant).
3. **Sinon :** viser le minerai qui a le meilleur prix, toutes stations confondues (à prix égal, le plus petit identifiant de minerai). Aller au plus proche des gisements de ce minerai qui ne sont pas dans la liste des gisements vus vides, en sauts puis par identifiant, puis miner. Si tous les gisements de ce minerai sont dans la liste, faire de même avec l'autre minerai ; si aucun gisement ne convient, rester à l'arrêt. Un vaisseau qui trouve un gisement vide va donc miner ailleurs, plus loin s'il le faut ; il ne pèse ni le temps de trajet ni la rentabilité (Non-Goals, « Un PNJ plus habile »).

La distance en sauts se calcule par une seule fonction publique, `distances(systems, start)` de `policies/geometry.py` (parcours en largeur sur les voisins de l'observation, par identifiant croissant). Le client la réutilise pour la carte, le coût d'un déplacement et les messages de refus, sans dupliquer le parcours, et `most_abundant(cargo)` de `policies/cargo.py` pour l'ordre des ventes. Ces deux modules n'ont aucune logique de décision : changer la politique ne les touche pas. **(amendement 2, précisé)** Le client importe aussi `scripted_miner.mettre_a_jour`, pour tenir l'ensemble des gisements vus vides que la prochaine étape écarte (point 7 ter) ; il n'appelle pas `decide`. Les contrats d'imports permettent à `clients` d'importer `policies`. Le PNJ n'émet un ordre que si l'activité voulue diffère de l'activité observée. Avec les prix proposés, tous les PNJ visent `ore_b`. Après leur première vente, tous ceux qui ne bouclent pas sur un gisement situé dans le système d'une autre station (règle 1) se retrouvent à la station qui paie le mieux `ore_b`, et minent donc le même gisement, le plus proche de cette station : dans l'essai cité dans Additional Resources, tous les PNJ minent un seul gisement dans environ 78 % des mondes, et deux gisements dans environ 22 %. Miné par cinq PNJ, un gisement dans le système d'une station se vide en environ 4 040 ticks. Le propriétaire accepte cet entassement, la référence scriptée devant rester simple.

### 7 bis. L'écran unique (amendement 1)

**Architecture du client.** `FourxApp` ne garde que l'affichage et les touches. La logique vit dans des modules purs, testés sans Textual et mutés sans plancher (le plancher de 80 % ne vaut que pour `core` et `schema`, Technical Plan, point 1) :
- `clients/model.py` : `ClientModel`, l'état du client. Il garde la dernière observation, les ordres envoyés sans résultat (numéro → commande), la file de vente, les alertes non acquittées et l'historique. Il reçoit une mise à jour et rend les messages à envoyer (par exemple la vente suivante de la file).
- **(amendement 2, réécrit)** `clients/force_layout.py`, `clients/map_view.py`, `clients/guide.py` et `clients/palette.py` : la disposition, la vue de la carte, la prochaine étape et la palette du Technical Plan, point 7 ter. Ils remplacent `clients/map_layout.py`, la mise en page en colonnes de l'amendement 1.
- `clients/texts.py` : les messages de refus en français, et la mise en forme des durées.
- `clients/frames.py` : un widget Textual par cadre. Chaque cadre lit `ClientModel` et ne connaît pas les autres. On peut en ajouter, en retirer ou les réarranger sans toucher au reste : c'est la modularité demandée par le propriétaire.

**Disposition et carte (amendement 2, réécrit).** La disposition de l'écran, la carte et leur style sont ceux du point 7 ter. Les touches, les ordres envoyés, les refus, les alertes et les durées du présent point (7 bis) restent en vigueur, avec les ajouts du point 7 ter ; l'alerte s'affiche désormais dans le cadre « Prochaine étape ».

**Touches (clavier AZERTY, aucune Majuscule).**

| Touche | Effet |
| :-- | :-- |
| `d` | déplacer : ouvre la liste des destinations, qui contient tous les systèmes (flèches, Entrée). Pour la ligne choisie, l'écran montre sauts, ticks et ≈ minutes ; Entrée confirme, Échap annule |
| `m` | miner le gisement du système, après confirmation (Entrée) ; dans un système sans gisement, choisir d'abord le minerai (`a` ou `b`) : l'ordre part, et son refus traduit dit où aller |
| `v` | vendre toute la cargaison : met en file une vente par minerai, le plus abondant d'abord ; chaque vente part après le résultat de la précédente |
| `p` | (mode développement) pause, ou reprise de l'univers |
| `a` / `r` | (mode développement) accélérer / ralentir l'univers, par paliers : ×1, ×10, ×100 (période 3 s, 0,3 s, 0,03 s à la période nominale) |
| Espace | (mode développement) avancer jusqu'à la prochaine alerte (palier ×100, retour à ×1 à l'alerte) |
| Entrée | si une alerte est affichée, l'acquitter, sans rien confirmer ; sinon, confirmer la saisie en cours |
| Échap | annuler la saisie en cours |
| `q` | quitter, après confirmation : « Quitter termine la partie (pas de reprise avant M5). Entrée pour confirmer. » |

Une touche sans effet dans la saisie en cours (liste des destinations, confirmation, ou aucune saisie) affiche une ligne d'aide dans la barre d'état. En mode développement : `a` au palier ×100 et `r` au palier ×1 sont sans effet ; en pause, `a` et `r` changent le palier qui reprendra à `p` ; Espace est sans effet tant qu'une alerte est affichée ; `a` ou `r` pendant « avancer jusqu'à la prochaine alerte » arrêtent l'avance et prennent le palier demandé ; la barre d'état affiche « pause » ou le palier demandé.

**Ordres envoyés.** Le modèle garde, pour chaque ordre envoyé, sa commande, jusqu'au résultat qui porte le même numéro. Le cadre Vaisseau l'affiche (« ordre envoyé : déplacer vers system_9 »). L'historique désigne un ordre par son contenu, jamais par son numéro. Le refus d'une vente de la file, ou un autre ordre du joueur, vide la file de vente.

**Refus en français.** `clients/texts.py` traduit chacun des 18 codes de `RefusalCode`, à partir de la commande refusée, que le modèle garde sous le numéro de l'ordre (le résultat d'ordre ne porte pas la commande), et de l'observation. Un refus lié à un lieu dit où aller ; à distance égale, le lieu de plus petit identifiant est nommé, et « 1 saut » s'écrit au singulier :
- `NO_DEPOSIT_FOR_ORE` : « pas de gisement de ore_a ici ; le plus proche est dans system_7 (2 sauts) » ;
- `NOT_AT_STATION` : « pas de station ici ; la plus proche est S1, dans system_1 (2 sauts) » ;
- `DEPOSIT_EMPTY` : « gisement vide ; le plus proche gisement de ore_a qui n'est pas connu comme vide est dans system_7 (2 sauts) » (le client ne connaît que le stock des gisements proches), ou « gisement vide ; tous les gisements de ore_a connus sont vides » s'il n'y en a aucun.

La table complète est au plan détaillé, point 23 quinquies. Le texte de `OrderResult`, construit par `step` et pris dans l'empreinte, ne change pas.

**Alertes (deux à M1).**
- **Arrivée à destination :** un `Arrived` du vaisseau du joueur, quand sa route est vide après le saut.
- **Fin de minage :** un `MiningEnded` du vaisseau du joueur, sans `causation_id` (le minage s'est arrêté seul : cargaison pleine ou gisement vide ; Technical Plan, point 5). La cause se lit dans la cargaison et le stock.

Une alerte reste affichée jusqu'à Entrée. Plusieurs alertes forment une file : la plus ancienne s'affiche d'abord. Chacune est aussi copiée dans l'historique. Pendant « avancer jusqu'à la prochaine alerte », l'arrivée d'une alerte remet la vitesse à ×1.

**Durées affichées.** Le client les calcule à partir de l'observation, réglages publics compris :
- ticks restants d'un trajet = `ticks_to_next_jump + (len(route) − 1) × jump_ticks` ;
- ticks restants d'un minage = min(⌈capacité libre ÷ `mining_rate`⌉, ⌈stock ÷ `mining_rate`⌉), exact si aucun autre vaisseau ne mine le même gisement, borne haute sinon ;
- coût d'un déplacement = nombre de sauts × `jump_ticks`.

Les minutes sont une estimation à `NOMINAL_TICK_PERIOD_S`, précédées de « ≈ » et suivies de « à 3 s » : lancée avec un autre `--periode`, la partie ne suit plus l'estimation, et le libellé le rappelle. Le montant net d'une vente n'est connu qu'après la vente (événement `Sale`). Le client ne connaît pas la vitesse jouée ; en mode développement, il affiche celle qu'il a demandée.

### 7 ter. L'écran rétro (amendement 2)

**Principe.** Le client reste un client Textual dans le terminal (ADR 0006). Il dessine en couleurs et en caractères demi-blocs (▀ ▄ : deux pixels de couleur par case de caractère), au style rétro 8 bits : l'esthétique des consoles 8 bits (palette réduite, gros pixels), et non une profondeur de couleur. Il se pilote au clavier et à la souris ; le clavier suffit à tout faire. Rien ne change dans le protocole, l'observation ou les règles : tout ce que l'écran montre se calcule à partir de l'observation et de l'état du client (`ClientModel`), sans autre canal ; la graine et le dossier de la partie restent hors de l'écran de jeu (point 6). Les invariants de déterminisme ne valent que pour `core` : la disposition calcule en flottants, et n'entre dans aucune empreinte. Aucune dépendance nouvelle : le dessin passe par les segments de Rich, déjà fournis par Textual. Les maquettes vues par le propriétaire sont hors du dépôt (canevas privé) ; ce point les décrit et fait foi.

**Modules.** Les modules purs sont testés sans Textual et mutés sans plancher, comme ceux du point 7 bis ; `frames.py` (exclu de la mutation) ne fait que peindre ce qu'ils calculent.
- `clients/palette.py` (Create) : la palette et les couples testés.
- `clients/force_layout.py` (Create) : la disposition par forces.
- `clients/map_view.py` (Create) : la vue de la carte : projection, zoom, déplacement, système sous le pointeur, grille de cases à peindre.
- `clients/guide.py` (Create) : la prochaine étape.
- `clients/texts.py` (Modify) : les textes de l'aide.
- `clients/model.py` (Modify) : l'historique typé, et les gisements vus vides.

**Palette (`clients/palette.py`).** `PALETTE` donne seize couleurs, une par rôle, toutes distinctes. Ce sont des valeurs RGB rendues en couleurs 24 bits (*true color*), et non les seize couleurs ANSI du terminal. Valeurs initiales, retouchables sans amendement (les tests de contraste font foi) : `fond` `#0B0E1A`, `cadre` `#121830`, `cadre_clair` `#1B2444`, `trait` `#2B3557`, `trait_fort` `#7B89C2`, `trait_faible` `#5E6A99`, `texte_attenue` `#8B97C3`, `texte` `#E8ECF8`, `accent` `#3FD0E0`, `ore_a` `#F2A33A`, `ore_b` `#5AA0FF`, `succes` `#5BD46A`, `alerte` `#F0506E`, `vaisseau` `#F5E14A`, `station` `#A98BFF`, `ombre` `#000000` (ombre portée de l'aide et de la bulle).
- **Fonds.** La carte et la barre d'état sont sur `fond` ; les cadres, l'aide et la bulle, sur `cadre` ; les pastilles à portée, sur `cadre_clair`.
- **Texte.** `CONTRAST_PAIRS` liste les couples (couleur du texte, couleur du fond) employés : les neuf couleurs de texte (`texte`, `texte_attenue`, `accent`, `ore_a`, `ore_b`, `succes`, `alerte`, `vaisseau`, `station`) sur `fond` et sur `cadre` ; `texte` et `texte_attenue` sur `cadre_clair` ; `fond` sur `station`, `alerte`, `accent`, `succes` et `vaisseau` (étiquettes). Chaque couple a un rapport de contraste d'au moins 4,5 pour 1 (formule WCAG 2.1, niveau AA).
- **Traits.** `GRAPHIC_PAIRS` liste `trait_fort` et `trait_faible` sur `fond`, et les deux couleurs des barres de progression, `accent` (fait) et `trait_faible` (à faire), sur `cadre` : au moins 3 pour 1 (WCAG 2.1, critère 1.4.11). `trait`, qui borde les cadres, est décoratif : les cadres se distinguent aussi par leur fond.
- `tests/clients/test_palette.py` calcule ces rapports. Le minerai n'est jamais porté par la seule couleur : la lettre `a` ou `b` l'accompagne. La portée non plus : les liens à portée sont pleins, les autres pointillés.

**Disposition de l'écran (120 colonnes × 36 lignes).** Les places comprennent les bordures.

| Cadre (`id`) | Place | Contenu |
| :-- | :-- | :-- |
| barre d'état (`#barre`) | lignes 1 et 2 | ligne 1 : tick, durée de jeu estimée (`duration_text` du tick, qui donne « ≈ … à 3 s »), solde ; en mode développement, la vitesse demandée ; ligne 2 : la ligne d'aide d'une touche sans effet et les invites (quitter, déjà ici) |
| carte (`#carte`) | lignes 3 à 29, colonnes 1 à 72, sans bordure : 72 × 27 cases (52 × 21 en 100 × 30) | la carte (`MapCanvas`) |
| prochaine étape (`#etape`) | lignes 3 à 9, colonnes 74 à 120 | la prochaine étape ; une alerte non acquittée s'y affiche, en couleur `vaisseau` |
| vaisseau (`#vaisseau`) | lignes 10 à 17, colonnes 74 à 120 | état, route, ordre envoyé, deux barres de progression |
| stations (`#stations`) | lignes 18 à 29, colonnes 74 à 120 | prix des stations, puis emplacement et stock des gisements, avec retour à la ligne ; le cadre défile ; la liste des destinations s'ouvre à sa place, et défile aussi |
| historique (`#historique`) | lignes 30 à 35 | les quatre dernières entrées de l'historique |
| barre des touches (`#touches`) | ligne 36 | les touches utiles dans la saisie en cours (« d déplacer · m miner · v vendre · h aide · q quitter » hors saisie ; « ↑↓ choisir · Entrée confirmer · Échap annuler » dans la liste) |
| aide (`#aide`) | fenêtre de 90 × 28 centrée, avec une ombre | l'aide « Comment jouer » |
| bulle (`#bulle`) | 40 × 7, deux cases à droite et en dessous du pointeur ; à gauche ou au-dessus près des bords | la bulle d'information |

Entre 100 × 30 et 120 × 36, la carte et le cadre « Stations » rétrécissent ; les autres cadres gardent leur taille, et les cadres de droite leurs 47 colonnes. En dessous de 100 × 30, le client n'affiche qu'un message : « Agrandis la fenêtre : 100 colonnes × 30 lignes au moins (actuellement C × L). » ; seule la touche `q` agit, et l'univers continue de tourner.

**Disposition de la carte (`clients/force_layout.py`, fonctions pures).** `force_layout(systems)` rend la position de chaque système dans le carré [0, 1] × [0, 1], axe des y vers le bas. Elle ne fait aucun tirage aléatoire : les mêmes systèmes donnent les mêmes positions. La disposition ne dépend que du graphe, qui ne change pas pendant la partie : elle est calculée une fois, et la carte ne bouge pas quand les vaisseaux bougent. Ses quatre étapes sont des fonctions du module, testées une à une sur de petits graphes :
1. **Départ en couches (`initial_layers`).** Les systèmes sont rangés par distance en sauts depuis le système de plus petit identifiant (fonction `distances`) ; ceux qu'elle n'atteint pas forment une dernière couche. La couche k est répartie régulièrement sur un cercle de rayon k, centré à l'origine, par identifiants croissants, à partir de l'angle 0,5 × k radian, dans le sens trigonométrique ; la couche 0 est à l'origine.
2. **300 itérations (`relax`).** À chaque itération, la force sur chaque système est la somme d'une répulsion 1 ÷ d² de chacun des autres (d, leur distance, bornée en dessous à 0,01 ; direction (1, 0) si les deux points sont confondus), d'un ressort (d − 1) vers chacun de ses voisins, et d'un rappel −0,05 × p vers l'origine (p, sa position). Chaque système se déplace dans la direction de sa force, d'une longueur égale au minimum de la norme de la force et du pas ; le pas vaut 0,1 × (1 − i ÷ 300) à l'itération i (de 0 à 299). Tous les systèmes se déplacent ensemble, à partir des positions de l'itération précédente.
3. **Normalisation (`normalize`).** Une échelle uniforme, la même sur les deux axes, place la boîte englobante des positions au centre du rectangle utile R = [0,05 ; 0,95 − 0,135] × [0,05 + 0,16 ; 0,95] ; si la boîte est réduite à un point, l'échelle vaut 1.
4. **Séparation (`separate`).** Chaque système occupe une boîte de 0,135 de large et de 0,16 de haut, à partir de sa position vers la droite et vers le haut : sa pastille et son gisement (4 colonnes), sa ligne de vaisseaux (une ligne au-dessus), et une case de marge. Ces dimensions viennent du cas le plus serré, la carte de 52 × 21 cases du terminal de 100 × 30, soit 42 pixels de haut au zoom 1 : 5 colonnes valent 0,119 et 3 lignes 0,143, plus une réserve pour l'arrondi. Le rectangle utile R garde toute la boîte dans le carré. Deux boîtes ne doivent pas se recouvrir. Au plus 100 passes : chaque paire en recouvrement, prise par identifiants croissants, est écartée tout de suite, symétriquement, sur l'axe qui demande le plus petit déplacement (l'axe horizontal à égalité ; à positions égales sur cet axe, le plus petit identifiant va à gauche, ou en haut), puis les deux positions sont ramenées dans R. Une passe sans recouvrement arrête la séparation ; au-delà de 100 passes, les positions sont rendues telles quelles (risque résiduel accepté : seules les graines 1 à 2 000 sont vérifiées).

Les tests vérifient, sur 50 graines (marque `proprietes`), puis sur les graines 1 à 2 000 (marque `lent` seule, hors de la mutation, lancée par la tâche `rejeu`), que chaque système est placé une fois, dans le carré, sans recouvrement des boîtes, et que la grille de la carte au zoom 1, sur 72 × 27 et sur 52 × 21 cases : pose chaque case d'un système (pastille, gisement, vaisseaux) dans la grille ; ne pose aucune case d'un système sur celle d'un autre ; laisse au moins une case libre entre deux systèmes. Une graine qui échoue rend la pull request rouge. Les systèmes passent par `observe(generate(graine, réglages), 1, réglages).systems` ; pour dessiner la ligne des vaisseaux, le test ajoute à l'observation, par `msgspec.structs.replace`, un vaisseau du joueur et deux autres vaisseaux dans chaque système (« ▲2 »), et la donne au modèle par `on_update`. Les tests écrivent aussi, dans leur sortie (`-s`), le nombre de croisements de liens par monde (deux liens qui se coupent, extrémités communes exclues) : sa moyenne, son maximum, la part des mondes qui en ont, et le nombre de liens qui traversent la pastille d'un autre système ; ces chiffres sont cités au compte rendu de M1, et au-delà d'un croisement par monde en moyenne, l'agent de code le signale au propriétaire.

**Vue de la carte (`clients/map_view.py`, fonctions pures).**
- **Zoom.** Cinq niveaux, `ZOOMS = (1.0, 1.5, 2.0, 3.0, 4.0)`. La molette, ou `z` (avant) et `x` (arrière), passe au niveau suivant ou précédent ; aux bornes, la touche est sans effet et la barre d'état affiche la ligne d'aide. La molette zoome autour du pointeur (le point sous le pointeur y reste) ; le clavier, autour du centre de la vue.
- **Projection.** Échelle uniforme : au zoom 1, le carré occupe toute la hauteur de la carte, à deux pixels par ligne, et il est centré en largeur ; au zoom z, l'échelle est multipliée par z. La case d'ancrage d'un système est la colonne arrondie de son x en pixels, et la ligne ⌊y en pixels ÷ 2⌋.
- **Déplacement.** La vue initiale est au zoom 1, centrée. `pan(view, dx, dy)` déplace la vue de `dx` colonnes et `dy` lignes. Les flèches déplacent la vue d'un dixième de la zone visible ; le glisser, bouton gauche enfoncé, fait suivre le pointeur au contenu, dès que le pointeur a bougé d'une case entre l'appui et le relâchement. Le centre de la vue reste dans le carré. `c` recentre la vue sur le vaisseau. Les flèches, `z`, `x` et `c` n'agissent que quand aucune saisie n'est ouverte ; dans une saisie, elles sont sans effet, avec la ligne d'aide de la saisie.
- **Portée.** Les systèmes à portée sont le système du vaisseau du joueur et ses voisins (`distances` ≤ 1), recalculés par le client, qui n'importe pas `core`.
- **Système sous le pointeur.** `system_at` rend le système dont la pastille couvre une case, ou aucun.
- **Grille.** `render` rend la grille de cases que `MapCanvas` peint. Chaque `Cell` porte un caractère et deux noms de rôle de `PALETTE` (avant-plan, fond) ; pour un caractère `▀`, l'avant-plan est le pixel du haut et le fond celui du bas. Ordre de dessin : liens, route, systèmes, vaisseaux, étiquettes.
  - Liens : tracés de pixel en pixel entre les cases d'ancrage ; pleins en `trait_fort` quand les deux systèmes sont à portée ; un pixel sur deux, en `trait_faible`, dans les autres cas. La route du vaisseau suit ses liens (`system_id`, puis chaque système de `route`) : trois pixels sur quatre, en `vaisseau`.
  - Systèmes : une pastille de deux caractères, à partir de la case d'ancrage (le numéro, aligné à droite : « ␣5 », « 12 »), en `texte` sur `cadre_clair` à portée, en `texte_attenue` sur `fond` hors de portée ; un système qui a une station a une pastille en `fond` sur `station` ; le système survolé, une pastille en `fond` sur `accent`. Un gisement : `◆` suivi de la lettre du minerai, dans la couleur du minerai, juste après la pastille.
  - Vaisseaux, sur la ligne au-dessus de la pastille : le vaisseau du joueur, `▲` en `vaisseau`, à la colonne d'ancrage ; puis les vaisseaux proches, `▲` en `texte_attenue`, suivi de leur nombre s'ils sont plusieurs (`▲3`). Pendant un saut, le vaisseau du joueur est dessiné sur le lien de `system_id` à `route[0]`, à la fraction 1 − `ticks_to_next_jump` ÷ `jump_ticks`.
  - Étiquettes, à partir du zoom 2 : à droite du gisement (ou de la pastille, s'il n'y a pas de gisement), sur la ligne de la pastille et les deux lignes en dessous : le libellé (`system_5`), la station et ses prix (`S1 a10 b15`), le stock (`20000`, ou `?` hors de portée). Une ligne n'écrit que des mots entiers (`system_5`, `S1`, `a10`, `b15`, `20000`) ; un mot qui ne tient pas avant la première case déjà occupée est remplacé par « … », et les suivants ne sont pas écrits. Aucun nombre n'est donc coupé.
- **Bulle.** Au survol d'un système : son libellé, ses sites, le stock ou « ? », et la distance en sauts, en ticks et en ≈ minutes depuis le vaisseau (pendant un saut, depuis `route[0]`, plus `ticks_to_next_jump`) ; « déjà ici » sur le système du vaisseau.
- **Clic.** Un clic sur un système (relâché sans glisser) a l'effet de `d` suivi du choix de ce système : la liste des destinations s'ouvre sur sa ligne ; Entrée envoie l'ordre, Échap annule. Sur le système du vaisseau, la barre d'état affiche « déjà dans system_k ». Le clic est ignoré pendant une saisie ou quand l'aide est ouverte.
- **Redessin.** La grille n'est recalculée que si l'une de ses entrées change : vue, taille, position du vaisseau en pixels, systèmes à portée, vaisseaux visibles, survol, et les stocks visibles à partir du zoom 2. L'affichage de la carte est plafonné à 10 rafraîchissements par seconde, et seule la dernière mise à jour est dessinée ; les autres cadres sont redessinés à chaque mise à jour. Le temps de rendu est mesuré au plan détaillé, point 28 bis.

**Prochaine étape (`clients/guide.py`, fonction pure).** `next_step(model)` rend un `Step` : un titre, un détail, des touches (noms de touches de Textual : `"enter"`, `"d"`), et la commande conseillée, s'il y en a une. La première règle qui s'applique donne l'étape :

| Règle | Condition | Titre | Détail | Touches | Commande |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 0 | aucune observation encore | « En attente du premier tick » | « » | () | aucune |
| 0 bis | l'observation n'a aucun vaisseau du joueur | « Aucun vaisseau » | « » | () | aucune |
| 1 | une alerte attend | le texte de l'alerte la plus ancienne, sans son tick, suivi de « ␣(+n) » (une espace, puis le nombre entre parenthèses) s'il en attend n autres | « Entrée : acquitter » | ("enter",) | aucune |
| 2 | des ordres envoyés attendent leur résultat | « Ordre envoyé : [ordres] » | « résultat au prochain tick » | () | aucune |
| 3 | en route | « En route vers [system_k] » (destination finale) | « arrivée dans [durée] » | () | aucune |
| 4 | en minage | « Minage de [ore] » | « fin du minage dans [durée] : cargaison pleine ou gisement vide » ; si un autre vaisseau visible est dans le même système, « fin du minage dans au plus [durée] : cargaison pleine ou gisement vide » (l'indication suit l'observation du tick) | () | aucune |
| 5 | à l'arrêt, cargaison pleine, ou non vide dans le système d'une station | la vente, ci-dessous | | | |
| 6 | à l'arrêt, sinon | le cycle, ci-dessous (la cargaison peut être vide ou partielle) | | | |

[ordres] est le contenu des ordres, comme dans l'historique, joints par « ; » ; [durée] est écrite par `duration_text` ; [sauts] par `sauts`. Toutes les comparaisons de gains par tick se font en entiers, par produits croisés (a ÷ b > c ÷ d si a × d > c × b).
- **Stations et gisements pris en compte.** Ceux qu'atteint `distances` depuis le vaisseau ; les autres sont ignorés, comme par le PNJ. À M1, chaque station rachète chaque minerai à un prix positif (Technical Plan, point 2) : aucune garde n'est nécessaire.
- **Vente depuis un système x, avec une cargaison c (`best_sale`).** Pour chaque station s : la valeur V(c, s) de la cargaison au prix brut de s (somme des quantités × prix), et la durée t(x, s) du trajet (nombre de sauts × `jump_ticks`). La station retenue a le plus grand V(c, s) ÷ (t(x, s) + 1) ; à égalité, la plus proche, puis le plus petit identifiant. La taxe, proportionnelle et la même partout, ne change pas ce classement, à l'arrondi près. Avec les prix initiaux, une station du système x l'emporte toujours (un écart de prix d'au plus 2,25 ne compense pas un trajet d'au moins 400 ticks) : la comparaison ne joue qu'hors du système d'une station.
- **Règle 5, la vente.** La station retenue par `best_sale` depuis le système du vaisseau, avec sa cargaison. Si elle est ici : « Vendre la cargaison ici » ; « valeur avant taxe : [V] » ; ("v",) ; aucune commande (la vente passe par `sell_all`). Sinon : « Aller vendre à [station] » ; « [sauts], [durée] ; valeur avant taxe : [V] » ; ("d",) ; `Move` vers son système.
- **Règle 6, le cycle.** Les candidats sont :
  - chaque gisement g qui n'est pas connu comme vide (stock visible nul, ou présent dans `seen_empty`) : la quantité q = la capacité libre, bornée par le stock de g s'il est visible ; la cargaison prévue c′ = la cargaison plus q unités du minerai de g ; la station s = celle que retient `best_sale` depuis le système de g avec c′ ; le gain G = V(c′, s) ; la durée T = trajet jusqu'à g + ⌈q ÷ `mining_rate`⌉ + t(g, s) ;
  - si la cargaison n'est pas vide, la vente directe : la station s retenue par `best_sale` depuis le système du vaisseau ; G = V(cargaison, s) ; T = t(ici, s) + 1.

  Le candidat retenu a le plus grand G ÷ T ; à égalité, le plus petit T, puis la vente directe avant les gisements, puis le plus petit identifiant de gisement. Textes :
  - gisement ici : « Miner [ore] ici » ; « fin du minage dans [durée] (ou « dans au plus [durée] » si un autre vaisseau visible est dans le système) ; puis vendre à [station] ([sauts]) », ou « ; puis vendre ici » si la station est dans le système ; ("m",) ; `Mine` de ce minerai ;
  - gisement ailleurs : « Aller miner [ore] à [system_k] » ; « [sauts], [durée] ; cycle complet estimé : [durée de T] », suivi de « (stock inconnu) » si le stock de g n'est pas visible ; ("d",) ; `Move` vers le système de g ;
  - vente directe : les textes de la règle 5 (« Aller vendre à [station] ») ;
  - aucun candidat (cargaison vide, aucun gisement qui convienne) : « Aucun gisement connu disponible » ; « tous les gisements connus sont vides : attendre leur régénération » ; () ; aucune commande. Comme `seen_empty` se vide quand il contient tous les gisements, ce cas n'arrive que si tous les gisements sont à portée et vides.

T est une estimation : il ne compte pas le tick que met chaque ordre à entrer en vigueur, et n'entre pas dans les durées que vérifie l'objectif 12. Le stock d'un gisement hors de portée est inconnu, et la règle suppose qu'il suffit : le conseil est optimiste pour ces gisements, et le détail le signale. Comme la station d'un cycle est celle que la règle 5 retiendra une fois la cargaison pleine, la station annoncée ne change pas au fil du cycle, sauf si le stock révélé change la quantité. Le gisement, lui, peut changer à l'arrivée : la durée d'approche, comptée au départ, ne compte plus une fois sur place, et un cycle plus court depuis ce point peut l'emporter. Ce changement est accepté (alternative AH) ; à information fixe, il ne peut pas faire d'aller-retour entre deux gisements.

Ce conseil est propre au joueur (alternative AH) : il pèse la durée, à la différence de la règle du PNJ, qui ne change pas. `ClientModel` garde l'ensemble des gisements vus vides (`seen_empty`), mis à jour à chaque observation par `scripted_miner.mettre_a_jour`, comme l'hôte des PNJ. Quand la prochaine étape conseille un `Move`, `d` ouvre la liste des destinations sur sa destination. La prochaine étape ne fait que guider : elle n'envoie jamais d'ordre. Dans le cadre, les touches s'affichent par leur nom français (`"enter"` : « Entrée »).

**Cadres.**
- **Vaisseau :** état, route, ordre envoyé ; deux barres de progression de 20 cases (`█` fait, `░` à faire) : le saut ou le minage en cours, et le remplissage de la cargaison.
- **Stations :** une ligne par station (« S1 system_2  a 10  b 15★ ») ; le meilleur prix de chaque minerai est marqué ★, en `succes` (toutes les stations à égalité le sont) ; puis une ligne par minerai, qui donne les systèmes de ses gisements et leur stock, ou « ? » hors de portée (« ore_b : system_3 (20000), system_7 (?) »), avec retour à la ligne ; le cadre défile quand son contenu dépasse sa hauteur.
- **Historique :** ses quatre dernières entrées, chacune écrite « t[tick] [texte] », l'étiquette colorée selon son type. `ClientModel.history` devient un tuple de `HistoryEntry(tick, kind, text)`, où `text` n'a plus le préfixe du tick ; `kind` vaut `ORDER`, `SALE`, `ALERT` ou `REFUSAL`, et donne la couleur (`accent`, `succes`, `vaisseau`, `alerte`). Le rouge (`alerte`) est réservé aux refus.

**Aide (`clients/texts.py`).** `help_pages(observation, dev)` rend les lignes de l'aide, une seule page qui défile. L'observation peut manquer (aide ouverte avant le premier tick), ou n'avoir aucun vaisseau du joueur : chaque durée qui en dépend est alors remplacée par « (connue au premier tick) ». `dev` dit si la partie est en mode développement. Texte, ligne par ligne :
- « COMMENT JOUER »
- « Tu pilotes un vaisseau minier. Tu gagnes ta vie en trois étapes, qui prennent du temps : »
- « 1. Miner (m), dans un système qui a un gisement : remplir une cargaison vide prend [durée]. » (⌈`capacity` ÷ `mining_rate`⌉ ticks, `capacity` du vaisseau du joueur)
- « 2. Transporter (d, ou un clic sur la carte) : un saut entre deux systèmes voisins dure [durée]. » (`jump_ticks`)
- « 3. Vendre (v), dans le système d'une station : au prix de cette station, moins une taxe. La vente est immédiate. »
- « Ce que tu vois : toute la carte, les gisements et les prix des stations. Les autres vaisseaux et le stock d'un gisement, seulement dans ton système et les systèmes voisins ; ailleurs, « ? ». »
- « Le temps : un tick dure environ 3 secondes à la vitesse normale, et le monde avance même si tu ne fais rien. Une alerte te prévient à l'arrivée et à la fin du minage. »
- « Premier objectif : vendre une première cargaison. Le cadre « Prochaine étape » te guide. »
- « Les touches : »
- « d : déplacer (liste des destinations ; Entrée envoie, Échap annule) »
- « m : miner le gisement du système »
- « v : vendre toute la cargaison »
- « h : ouvrir ou fermer cette aide »
- « z / x : zoomer, dézoomer la carte »
- « c : recentrer la carte sur ton vaisseau »
- « flèches : déplacer la carte »
- « Entrée : confirmer, ou acquitter une alerte »
- « Échap : annuler »
- « q : quitter »
- si `dev` : « Mode développement : p pause, a / r accélérer / ralentir, Espace avancer jusqu'à la prochaine alerte »
- « Entrée, Échap ou h : fermer »

L'aide s'ouvre au lancement de chaque partie (aucune mémoire d'une partie à l'autre) et sur la touche `h`. C'est une saisie : un widget superposé, et non un écran modal de Textual, pour que `FourxApp` reçoive toujours les touches. `h` pendant une autre saisie annule celle-ci et ouvre l'aide. Tant qu'elle est ouverte : Entrée, Échap et `h` la ferment, avant toute alerte, qui s'affiche ensuite ; ↑ et ↓ la font défiler ; `q` la ferme et ouvre la confirmation de quitter ; les touches du mode développement restent actives ; toute autre touche affiche la ligne d'aide. L'univers continue de tourner. Les tests du pilote ferment l'aide avant d'agir.

**Touches ajoutées (AZERTY, aucune Majuscule).** `h` : aide ; `z` et `x` : zoom avant et arrière ; `c` : recentrer la vue sur le vaisseau ; ← → ↑ ↓ : déplacer la vue. Hors de l'aide, toutes n'agissent que quand aucune saisie n'est ouverte, sauf `h`. Les touches du point 7 bis ne changent pas.

### 8. Le rejeu, la divergence et les empreintes de référence

- **Le rejeu** part d'un état initial et d'une suite d'ordres soumis par tick, applique `step` tick par tick, et produit les empreintes et les événements de chaque tick. Une seule fonction de `tools` le fait (`replay_orders`, Technical Plan, point 13) ; elle sert à l'outil de rejeu d'un dossier de partie (état initial lu dans l'instantané), au contrôle `rejeu` et au test des fourchettes.
- **L'outil de divergence** (`tools`, niveau 1, CUJ 4) compare deux suites d'empreintes (deux dossiers de partie, ou deux fichiers d'empreintes), et indique le premier tick qui diffère et les composants concernés.
- **La partie de référence** est générée par la graine 1 et jouée par ses `npc_count(1, réglages)` PNJ (amendement 1, réécrit), à travers le serveur en mode sans horloge. Elle n'est jouée qu'à la régénération des références. On enregistre alors, dans `tests/references/rules-<révision>/` :
  - `orders.jsonl`, l'export versionné de son journal des ordres soumis (en-tête : les valeurs de la table `meta` du journal et le dernier tick ; puis un ordre soumis par ligne) ;
  - `reference.json`, son `rules_version` et les empreintes de chaque composant tous les 1 000 ticks et au dernier tick.

  L'état initial n'est pas enregistré : il est régénéré par `world.generate` à partir de la graine, ce qui vérifie aussi la génération du monde. Le contrôle `rejeu` n'a besoin que de `core`, de `schema`, de `tools` et de l'import JSONL de `server`. Un changement du PNJ, de l'hôte des PNJ ou du serveur ne touche donc pas les références ; un changement des règles ou des réglages les fait diverger, et oblige à les régénérer. Une régénération des références remplace le dossier de la révision précédente ; l'historique git le garde (environ 4 Mo par révision, à mesurer au plan détaillé, point 28 bis).
- **La régénération des références** se fait avec l'outil de régénération (plan détaillé, point 27), lancé sur l'ordinateur portable. Il assemble `server`, `clients` et `policies` ; or `tools` peut importer `server`, mais ni `clients` ni `policies` (niveau 1, §1). Il vit donc sous `tests/`, que les contrats d'imports ne contraignent pas (choix du propriétaire), et produit aussi un rapport de différences. Le dossier `tests/references/` devient un chemin protégé. Le contrôle de garde exige que `RULES_REVISION` augmente de un quand les références changent, et pose l'étiquette « références régénérées » sur la pull request (`CLAUDE.md`, circuit des pull requests).
- **`rules_version`** est formé du numéro de révision, tenu à la main dans le noyau (`RULES_REVISION`), et de l'empreinte des réglages (niveau 1, §3) : `"rules-<RULES_REVISION>+<empreinte>"`. Le noyau calcule l'empreinte sur l'encodage MessagePack de `Tunables` (et non sur les octets du fichier, pour qu'un commentaire ne la change pas) : `step` la connaît donc, et la met dans chaque événement.

### 9. L'économie sur 100 000 ticks

- Le contrôle `rejeu` lance aussi un test marqué `lent` : il rejoue le journal enregistré de la partie de référence par `replay_orders` et collecte ses événements v0.
- **(amendement 1, réécrit)** Une seule fonction de `tools` (`window_stats`) calcule, à partir des événements v0, par fenêtre de 10 000 ticks (ticks 1 à 10 000, 10 001 à 20 000…) : l'émission par motif, la destruction par motif, la croissance de la masse monétaire, et la masse monétaire en fin de fenêtre. Le test vérifie les trois premières grandeurs contre les bornes du plan détaillé, point 27, sur chaque fenêtre, la première comprise, puisque le départ à vide ne fait que réduire l'émission.
- Un notebook marimo appelle la même fonction et affiche les mêmes grandeurs pour le propriétaire. Il lit aussi les événements avec DuckDB, pour les explorer, sans calcul propre : le niveau 1 (§9, « DuckDB + notebooks marimo » dès M1) fixe ces deux outils pour l'économie.

**(amendement 1)**

- **Partie de référence :** graine 1, jouée par ses `npc_count(1, réglages)` PNJ, à travers le serveur en mode sans horloge, sur 100 000 ticks (inchangé).
- **Fenêtres :** `window_stats(..., window=10_000)`. Les empreintes de référence restent relevées tous les 1 000 ticks.
- **Bornes (décision du propriétaire, 2026-11-21, qui remplace celle du 2026-11-15) :** larges, et calculées par `test_fourchettes.py` lui-même à partir du monde de la graine 1, du nombre de PNJ et des réglages, sans lire la partie ni dépendre de la politique du PNJ (plan détaillé, point 27). Sur chaque fenêtre, la première comprise : au moins une vente ; une émission au plus égale à ce que les PNJ pourraient vendre en enchaînant les cycles les plus courts de la carte, au prix le plus haut ; une destruction égale à la somme des taxes de chaque vente, arrondies vers le haut. C'est une alarme contre une panne (plus aucune vente) ou une émission au-dessus du plafond, pas une mesure fine : une baisse partielle des ventes passerait. La conservation de l'argent reste vérifiée à chaque tick (objectif 4). L'outil de régénération refuse d'écrire des références dont la partie sort de ces bornes.
- **Épuisement :** une station et un gisement peuvent partager un système (alternative AA). Des PNJ peuvent alors y boucler sans trajet et vider le gisement avant sa régénération. La partie de référence peut ainsi faire jouer l'épuisement, la régénération et le départage, sans garantie : cela dépend du monde de la graine 1. Après la partie, l'outil de régénération relève si un gisement s'est vidé et si un départage a eu lieu pendant la partie, et le compte rendu de M1 le cite. Les scénarios et les tests de propriétés à stock bas restent la parade principale (Risks & Mitigations).

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

Un test marqué `mesure`, sous `tests/` pour la même raison que l'outil de régénération (Technical Plan, point 8), mesure les ticks par seconde de `step` et de `observe` (une observation par acteur et par tick), sans serveur. Le monde a la taille de ceux de l'entraînement : le niveau 1, §8, dit « quelques dizaines d'entités », et M1 retient un monde généré de 12 systèmes et 30 PNJ, un vaisseau chacun (amendement 1, réécrit ; voir ci-dessous). Les ordres des PNJ sont calculés hors du temps mesuré. Le test affiche le résultat ; rien ne dépend de sa valeur.

**(amendement 1)** Le monde mesuré est généré par `world.generate` avec `systems_min` = `systems_max` = 12 (réglages de mesure, hors de `tunables.toml`), et 30 PNJ sont créés par des ordres d'administration. Trois systèmes ne sont plus possibles : `world.generate` place jusqu'à `deposits_max` gisements dans des systèmes distincts.

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
| classe de visibilité | `Visibility` : `PUBLIC`, `CORPORATION`, `PRIVATE`, `ADMIN`, `NEARBY` (amendement 1) |
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

**(amendement 1)** Termes du glossaire ajoutés, seulement ceux qu'un autre paquet ou document emploie : réglages publics (`public_tunables`), proximité (`NEARBY`), période nominale (`NOMINAL_TICK_PERIOD_S`), mode développement (`--dev`). Les termes internes du client (cadre, historique, ordre envoyé, alerte, file de vente) restent propres au Technical Plan, point 7 bis, qui les emploie. L'argent s'affiche « Solde », comme `wallet_balance`.

**(amendement 2)** Les termes de l'écran rétro (prochaine étape, disposition par forces, vue de la carte, aide, palette) ne servent qu'au client : ils restent au point 7 ter, et le glossaire ne change pas. La portée est la proximité du glossaire (`NEARBY`).

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
                OrderResult(recipient_actor_id: Id | None, order_id: OrderId, accepted: bool,
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
observation.py  SystemView, DepositView, StationView, ActorView (champs publics ; DepositView.stock : Int64 | None, de classe proximité)   (amendement 1)
                OwnShipView (tous les champs de Ship, mêmes noms) ; OtherShipView (champs de Ship de classe NEARBY)   (amendement 1)
                (StationView reprend ore_prices ; wallet_balance est le balance du portefeuille personnel de l'acteur)
                Observation(tick: Int64, actor_id: Id, systems, deposits, stations, actors,
                            own_ships, other_ships, wallet_balance: Int64, action_budget: Int64,
                            events: tuple[Event, ...], results: tuple[OrderResult, ...],
                            public_tunables: PublicTunablesView)   (amendement 1)
protocol.py     PROTOCOL_VERSION = 2   (amendement 1)
                SubmitOrders(protocol_version: Int64, orders: tuple[Order, ...])
                TickUpdate(protocol_version: Int64, observation: Observation)
                Connection(typing.Protocol) : submit(message: SubmitOrders) -> None ;
                                              async next_update() -> TickUpdate
                SyncClient(typing.Protocol) : on_update(update: TickUpdate) -> SubmitOrders | None
```

**`core`**

```text
tunables.py     Tunables(jump_ticks, mining_rate, cargo_capacity: Int64,
                         station_ore_prices: tuple[tuple[Int64, ...], ...],
                         tax_rate_bp, deposit_stock, regen_ticks, budget_regen, budget_max: Int64,
                         systems_min, systems_max, deposits_min, deposits_max, stations_min, stations_max,
                         npc_min, npc_max, extra_links_max, max_neighbors: Int64)   (amendement 1)
                (chaque ligne de station_ore_prices, comme Station.ore_prices et Ship.cargo, est indexée
                 par identifiant de minerai moins un)
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
observe.py      observe(state: State, actor_id: int, tunables: Tunables) -> Observation   (amendement 1, ADR 0003)
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
server/reception.py        Reception.receive(sender_actor_id: int, messages: tuple[SubmitOrders, ...], tick: int)
                               (tous les messages du point de connexion pour ce tick ; applique validate_orders
                                une seule fois et remplit reception_refusal)
                               -> tuple[SubmittedOrder, ...]
server/order_log.py        OrderLog.create(path, rules_version, world_seed, commit, worktree_dirty) ;
                           append(orders: tuple[SubmittedOrder, ...], fingerprints: Fingerprints) ;
                           orders_by_tick() -> tuple[tuple[SubmittedOrder, ...], ...] ;
                           export_jsonl(path) ; import_jsonl(path) -> en-tête et ordres par tick
                           (l'en-tête porte aussi le dernier tick de la partie)
server/game.py             Game(runs_dir: Path, world_seed: int, tunables: Tunables, period_s: float = NOMINAL_TICK_PERIOD_S)   (amendement 1)
                           set_period(period_s: float | None) -> None   (amendement 1)
                           (crée runs_dir/<AAAAMMJJ-HHMMSS-micro>/ ; les tests passent un dossier temporaire)
                           create_character(kind: ActorKind) -> int ; connect(actor_id) -> Connection ;
                           attach(actor_id, client: SyncClient) ; advance(n: int) -> None ;
                           async run() -> None
policies/scripted_miner.py decide(observation, seen_empty) : voir les interfaces ajoutées ci-dessous   (amendement 1)
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
                           window_stats(events: Iterable[Event], window: int = 10_000) -> tuple[WindowStats, ...]   (amendement 1)
```

Les noms des composants affichés par l'outil de divergence sont ceux des champs de `Fingerprints` (`ledger` pour le registre).

**(amendement 1)**

**Interfaces et identifiants ajoutés.**

```text
core/world.py      generate(world_seed: int, tunables: Tunables) -> State          (inchangée)
                   npc_count(world_seed: int, tunables: Tunables) -> int           (nouvelle)
core/observe.py    observe(state: State, actor_id: int, tunables: Tunables) -> Observation   (ADR 0003)
schema/observation.py  PublicTunablesView(jump_ticks, mining_rate)
                       Observation.public_tunables: PublicTunablesView
schema/visibility.py   Visibility.NEARBY = "nearby"                                  (ADR 0005)
schema/protocol.py     PROTOCOL_VERSION = 2 ; NOMINAL_TICK_PERIOD_S = 3.0
server/game.py     Game(runs_dir, world_seed, tunables, period_s=NOMINAL_TICK_PERIOD_S)
                   Game.set_period(period_s: float | None) -> None
policies/geometry.py   distances(systems: tuple[SystemView, ...], start: int) -> dict[int, int]
policies/cargo.py      most_abundant(cargo: tuple[int, ...]) -> tuple[int, int] | None   (identifiant de minerai à partir de 1, quantité ; None si la cargaison est vide)
policies/scripted_miner.py  POLICY_VERSION = 2
                       mettre_a_jour(observation: Observation, seen_empty: frozenset[int]) -> frozenset[int]   (amendement 2)
                            decide(observation: Observation, seen_empty: frozenset[int])
                                -> tuple[tuple[Order, ...], frozenset[int]]
clients/npc_host.py    NpcHost garde la liste rendue par decide, et la lui repasse
clients/textual_app.py FourxApp(connection, actor_id, set_speed: Callable[[int | None], None] | None)   facteur 1, 10, 100, ou None
clients/model.py       ClientModel(actor_id: int)                implémente SyncClient
                       on_update(update: TickUpdate) -> SubmitOrders | None   vente suivante de la file
                       send(command: Command) -> SubmitOrders     ordre du joueur ; vide la file de vente
                       sell_all() -> SubmitOrders | None          une vente par minerai, en file
                       acknowledge() -> None                      retire l'alerte la plus ancienne
                       remaining_ticks() -> int | None            trajet ou minage en cours
                       observation: Observation | None ; pending: tuple[tuple[int, Command], ...]
                       (numéros d'ordre attribués par le modèle, à partir de 1) ; alerts: tuple[Alert, ...] ;
                       history: tuple[HistoryEntry, ...] (textes : « ordre « miner ore_a » : accepté », « arrivée : system_5 »,   (amendement 2)
                       « vente : 100 ore_b à 15, paiement 1500, taxe 150 », alertes et refus traduits) ; seen_empty: frozenset[int]   (amendement 2)
                       Alert(kind: AlertKind, tick: int, text: str) ; AlertKind : ARRIVED, MINING_ENDED ;
                       text : « arrivée : system_5 », « fin de minage : ore_a 100/100 »
clients/force_layout.py  force_layout(systems: tuple[SystemView, ...]) -> dict[int, tuple[float, float]] ;   (amendement 2)
                       initial_layers(systems) -> dict[int, tuple[float, float]] ; relax(systems, positions) ;   (amendement 2)
                       normalize(positions) ; separate(positions) : chacune rend dict[int, tuple[float, float]]   (amendement 2)
clients/map_view.py    View(zoom_index: int, center: tuple[float, float], width: int, height: int), gelée ;   (amendement 2)
                       Cell(char: str, fg: str, bg: str), gelée (fg et bg : rôles de PALETTE) ; ZOOMS ;   (amendement 2)
                       zoom(view, step: int, anchor: tuple[int, int] | None) -> View ; pan(view, dx: int, dy: int) -> View ;   (amendement 2)
                       system_at(view, positions, x: int, y: int) -> int | None ;   (amendement 2)
                       render(view, positions, model: ClientModel, hovered: int | None) -> tuple[tuple[Cell, ...], ...]   (amendement 2)
clients/guide.py       Step(title: str, detail: str, keys: tuple[str, ...], command: Command | None), gelée ;   (amendement 2)
                       next_step(model: ClientModel) -> Step ;   (amendement 2)
                       best_sale(observation, system_id: int, cargo: tuple[int, ...]) -> tuple[int, int, int] | None   (amendement 2)
                       (station retenue, valeur V, durée du trajet ; None si aucune station n'est atteinte)   (amendement 2)
clients/palette.py     PALETTE : dict[str, str] (seize rôles) ; CONTRAST_PAIRS, GRAPHIC_PAIRS : tuple[tuple[str, str], ...]   (amendement 2)
clients/texts.py       help_pages(observation: Observation | None, dev: bool) -> tuple[str, ...]   (amendement 2)
clients/model.py       HistoryEntry(tick: int, kind: HistoryKind, text: str) ; HistoryKind : ORDER, SALE, ALERT, REFUSAL ;   (amendement 2)
clients/texts.py       refusal_text(result: OrderResult, command: Command, observation: Observation) -> str
                       duration_text(ticks: int) -> str           « 400 ticks (≈ 20 min à 3 s) » ; « 62 ticks (≈ 3 min 6 s à 3 s) »
                                                                  (ticks × 3 s, écrits en h, min et s, sans les unités nulles)
clients/frames.py      un widget Textual par cadre (carte MapCanvas, prochaine étape, vaisseau, stations, historique, barre d'état, barre des touches, aide, bulle)   (amendement 2)
```

Autres changements de types (ADR 0005) : `DepositView.stock: Int64 | None` (`None` hors de portée) ; les champs de `OtherShipView` sont de classe `NEARBY`. `Observation.public_tunables` est le dernier champ de `Observation`.

## Alternatives Considered

Ces alternatives ont été pesées pendant la rédaction et la revue de ce document. Les alternatives d'architecture sont dans le niveau 1, et celles qui portent sur les règles du jeu dans la [RFC du brainstorm](./mmo-gestion-spatiale-ia.md).

**(amendement 1)** Les alternatives A à I du document restent. Les alternatives J à AA, plus bas, s'y ajoutent, avec la marque « (amendement 1) ». Chacune prend l'une de deux formes : les avantages et les inconvénients de l'option rejetée, ou la liste des options pesées, chacune avec son défaut ; la dernière puce de chaque alternative, « Retenu », donne l'option choisie. L'alternative C (« des ticks avancés à la demande du joueur ») reste rejetée : l'accélération de l'amendement n'existe qu'en mode développement d'une partie locale, ne passe ni par le protocole ni par le journal, et ne change que la période de l'horloge (alternative S). **(amendement 2)** Les alternatives AB à AH s'y ajoutent, avec la marque « (amendement 2) ».

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

*   **Raison du rejet :** le niveau 1, à son alternative R, retient par défaut une nouvelle table par phase du tick, et rien à M1 ne justifie d'en changer.

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
*   **Raison du rejet :** proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08. Retenu : le journal de la partie de référence est exporté à la régénération des références, au format versionné du journal des ordres soumis, et le contrôle `rejeu` le rejoue par `step` seul. Le serveur et le PNJ restent vérifiés par les scénarios et par leurs tests.

### Alternative I : garder tout l'historique des écritures dans l'état

*   **Avantages :** l'état contient tout le registre, sans recours aux événements.
*   **Inconvénients :** l'empreinte du registre réencode tout l'historique à chaque tick, donc le coût total d'une partie croît comme le carré de son nombre de ticks ; chaque phase recopie l'historique, et l'instantané du monde en ligne grossirait sans limite à M5.
*   **Raison du rejet :** proposition de l'agent de code, approuvée avec le document le 2026-11-08. Retenu : soldes, écritures du tick et compteurs cumulés dans l'état ; l'historique dans les événements (Technical Plan, point 3).

### Alternative J : un document de niveau 2 séparé pour l'écran (amendement 1)

*   **Avantages :** ce document, déjà approuvé, n'est pas touché.
*   **Inconvénients :** la feuille de route n'a qu'une cellule et un statut par jalon, et `CLAUDE.md` parle du document du jalon au singulier ; il aurait fallu changer le circuit. Deux textes auraient fait foi, et le nouveau aurait contredit le Technical Plan, points 5, 6, 7 et 13, de ce document.
*   **Retenu :** choix du propriétaire, après le premier tour de revue : un amendement.

### Alternative K : quatre onglets, Carte, Vaisseau, Station et Journal (amendement 1)

*   **Avantages :** chaque écran serait aéré.
*   **Inconvénients :** un onglet caché cacherait aussi ses événements, alors que le joueur se plaignait d'en rater. Les touches 1 à 4 entreraient en conflit avec le choix de la destination. « Journal » désigne déjà `OrderLog`.
*   **Retenu :** choix du propriétaire : un écran unique, fait de cadres réarrangeables.

### Alternative L : ralentir seulement la période de l'horloge (amendement 1)

*   **Avantages :** aucun changement des règles, ni de `rules_version`.
*   **Inconvénients :** les décisions resteraient les mêmes, avec plus d'attente entre elles ; le PNJ resterait aussi rapide en ticks. Le temps ne deviendrait pas une ressource.
*   **Retenu :** choix du propriétaire : les durées sont des règles (`jump_ticks` ticks par saut, 400 dans les valeurs initiales ; 100 ticks de minage), et la période nominale passe aussi à 3 s.

### Alternative M : la taille du monde (amendement 1)

*   **Le haut des fourchettes du niveau 1** (5 systèmes, une station) : aucune ADR, mais un seul point de vente, donc aucun choix du lieu de vente.
*   **Une taille fixe** (8 ou 12 systèmes) : scénarios et bornes plus simples, mais chaque graine donnerait le même monde, à l'emplacement des sites près.
*   **Trois minerais :** plus de choix, mais l'ADR toucherait aussi « deux minerais » du CUJ 1, et les prix et les bornes s'étendraient.
*   **Retenu :** choix du propriétaire : fourchettes tirées par la graine (8 à 12 systèmes, 2 à 3 stations, 4 à 6 gisements, 3 à 5 PNJ), deux minerais, « sans rentrer dans l'excessif ».

### Alternative N : la forme du graphe (amendement 1)

*   **Grille partielle** (cases d'une petite grille, liens entre cases voisines) : affichage direct, mais aspect régulier, et des positions de grille dans l'état.
*   **Anneau et cordes :** toujours connexe, mais forme semblable d'une graine à l'autre, et un anneau de 12 systèmes se dessinerait mal en 80 × 24.
*   **Retenu :** choix du propriétaire : un arbre, plus quelques liens qui créent des boucles. Le prix en est une mise en page calculée par le client.

### Alternative O : les prix des stations (amendement 1)

*   **Mêmes prix partout :** simple, mais le lieu de vente ne compterait plus, sinon par la distance.
*   **Prix tirés par la graine dans une fourchette :** plus de variété, mais des bornes d'économie à calculer sur toutes les combinaisons.
*   **Retenu :** choix du propriétaire : des prix propres à chaque station, écrits dans les réglages (`station_ore_prices`, au moins `stations_max` lignes, la ligne i pour la station d'identifiant i). Plus tard, le marché fixera les prix (M6).

### Alternative P : comment le client connaît les durées (amendement 1)

*   **Aucune donnée nouvelle** (durées déduites de `ticks_to_next_jump` et de `MiningStarted.rate`) : rien ne changerait dans `schema`. Mais aucune durée ne serait connue avant le premier départ, et la déduction serait fragile.
*   **Un champ dans `TickUpdate` hors de l'observation, ou un message d'accueil :** `observe` ne changerait pas. Mais ce serait un second canal vers le joueur, interdit par le niveau 1, §5 (« il n'y a pas d'autre canal ») ; les joueurs IA, qui s'entraînent sur l'observation seule, en seraient privés. Cette option avait d'abord été retenue pendant le brainstorm, puis écartée pour cette raison.
*   **Les valeurs copiées sur les entités de l'état** (vitesse et laser sur le vaisseau, taxe sur la station) : `observe` et le niveau 1 ne changeraient pas, et cela préparerait des valeurs propres à chaque vaisseau. Mais `State`, `step`, les empreintes et l'instantané changeraient, et un rééquilibrage ne toucherait pas les vaisseaux déjà créés.
*   **Retenu :** choix du propriétaire : `observe` reçoit les réglages et publie une vue des réglages publics (ADR 0003). Quand ces valeurs deviendront propres à chaque vaisseau, elles passeront dans la vue du vaisseau.

### Alternative Q : les refus en français construits par `step` (amendement 1)

*   **Avantages :** le texte du résultat d'ordre serait déjà en français, pour tous les clients.
*   **Inconvénients :** ce texte entre dans l'empreinte `last_tick`. Après le volet C, chaque retouche d'un libellé coûterait une régénération des références et une hausse de `RULES_REVISION`. Un champ structuré dans `OrderResult` changerait `schema`, l'instantané et le protocole sans nécessité.
*   **Retenu :** le client traduit le code de refus, à partir de l'observation (Technical Plan, point 7 bis).

### Alternative R : la façon de signaler les alertes (amendement 1)

*   **`App.notify` de Textual :** déjà là, mais la notification disparaîtrait au bout d'un délai réel, utiliserait des couleurs, et rendrait les tests dépendants de l'horloge.
*   **La comparaison de deux observations successives :** aucun événement à interpréter, mais elle casserait dès qu'une mise à jour manque, ce qui arrivera avec les reconnexions de M3.
*   **Retenu :** les alertes viennent des événements de l'observation (`Arrived`, `MiningEnded`), filtrés par le modèle client, et restent affichées jusqu'à Entrée.

### Alternative S : la façon d'accélérer (amendement 1)

*   **`--periode` seul, au lancement :** rien à construire, mais on ne pourrait ni ralentir ni mettre en pause en cours de partie, et chaque attente de 20 minutes resterait entière.
*   **Un message du protocole :** c'est l'alternative C, déjà rejetée ; un joueur commanderait l'horloge d'un serveur partagé.
*   **`Game.advance(n)` appelé depuis l'interface :** il bloquerait la boucle de Textual, enverrait n mises à jour d'un coup, et mélangerait les deux modes du serveur.
*   **Un fichier de réglages « de développement » :** ce serait un changement des règles, avec un autre `rules_version`, pas une accélération.
*   **Commandes de vitesse pour tous :** pratiques, mais en partie sans `--dev` l'univers doit tourner à son rythme ; le propriétaire ne les veut que pour le développement.
*   **Retenu :** en mode développement seulement (`--dev`), une fonction de rappel locale, passée par `__main__.py`, change la période de l'horloge (paliers, pause, avancer jusqu'à la prochaine alerte) ; chaque changement est enregistré dans `speed.jsonl`.

### Alternative T : afficher les durées en minutes, ou transmettre la période au client (amendement 1)

*   **Avantages :** le joueur lit directement le temps réel.
*   **Inconvénients :** la période change avec l'accélération, et ce n'est pas une donnée du jeu ; la transmettre dans l'observation ou dans `TickUpdate` serait un autre canal.
*   **Retenu :** les ticks restent l'information principale ; les minutes sont une estimation à la période nominale, précédée de « ≈ ».

### Alternative U : la durée du minage au-delà de 100 ticks (amendement 1)

*   **Un compteur de cycles de minage, ou un réglage « ticks par lot » :** des durées aussi longues qu'on veut, mais `step`, `Tunables`, le sens de `MiningStarted.rate`, et peut-être `State` et l'instantané, changeraient.
*   **Un changement d'échelle des unités** (cargaison de 4 000, prix et stocks à l'avenant) : seuls les réglages changeraient, mais tous les montants des scénarios et des bornes seraient à refaire.
*   **Retenu :** choix du propriétaire : 100 ticks (5 minutes) suffisent à M1 ; la durée dépendra plus tard du laser du vaisseau et de la capacité de sa cargaison.

### Alternative V : le test d'économie (amendement 1)

*   **Garder des fenêtres de 1 000 ticks :** chaque fenêtre contiendrait zéro ou une vente par PNJ ; la borne basse tomberait à 0, et le test ne prouverait plus rien.
*   **Allonger la partie de référence à 1 000 000 de ticks :** environ dix fois plus de temps de rejeu, et des empreintes de chaque tick, écrites par la tâche `rejeu`, d'environ 284 octets par tick, soit environ 284 Mo.
*   **Des bornes calculées à partir du cycle de chaque PNJ** (décision du propriétaire du 2026-11-15, abandonnée le 2026-11-21) : serrées, à une ou deux ventes près, mais le calcul devait suivre la politique du PNJ, prévoir l'épuisement des gisements, élargir les bornes des PNJ dont le gisement pouvait se vider, et refuser les mondes à borne basse nulle (environ un sur trois) : beaucoup de mécanique pour une alarme, et un frein à toute évolution du PNJ.
*   **Des bornes tirées de la seule géométrie, sans borne basse** (première version de l'amendement) : une panne qui arrête toute vente passerait le test.
*   **Descendre sous 100 000 ticks :** fixé par le niveau 1 ; il faudrait une ADR, sans bénéfice.
*   **Retenu :** des fenêtres de 10 000 ticks, sur les 100 000 ticks du niveau 1, et des bornes larges tirées de la carte : au moins une vente par fenêtre, un plafond géométrique, et une destruction égale à la somme des taxes (décision du propriétaire, 2026-11-21 ; plan détaillé, point 27). Pour la graine 1, le plafond est environ 2,6 fois l'émission attendue ; une baisse partielle des ventes passe, ce qui est accepté.

### Alternative W : la politique du PNJ (amendement 1)

*   **Le gisement le plus proche, la station la plus proche :** très simple, mais les prix propres des stations ne changeraient rien à son jeu.
*   **Un gisement attitré, déduit de l'identifiant :** les PNJ se répartiraient sur la carte, mais la répartition serait arbitraire.
*   **Une politique attentive au temps de trajet :** plus crédible comme adversaire, mais ce ne serait plus une référence simple, et M1 veut le PNJ simple.
*   **Sans mémoire :** la politique la plus simple, mais un PNJ qui ne voit le stock que de près ferait l'aller-retour entre deux gisements vides jusqu'à leur régénération.
*   **Retenu :** choix du propriétaire : « le mieux payé » (Technical Plan, point 7), avec pour seule mémoire les gisements vus vides (décision du propriétaire, 2026-11-21). Les PNJ convergent le plus souvent (78 % des mondes dans l'essai) vers le gisement le plus proche de la station qui paie le mieux (Technical Plan, point 7) : c'est accepté.

### Alternative X : l'attache du PNJ en mode avec horloge (amendement 1)

*   **Avantages :** avec un client synchrone attaché, la décision du PNJ entre toujours au tick suivant, à toute vitesse, comme dans la partie de référence.
*   **Inconvénients :** son calcul bloquerait la boucle des ticks, et le Technical Plan, point 7, serait réécrit.
*   **Retenu :** choix du propriétaire : la tâche de relais du code d'origine. Au palier rapide (×100), la partie locale ne joue pas tout à fait comme la partie de référence ; le rejeu reste exact, puisqu'il suit le journal.

### Alternative Y : la carte à l'écran et la visibilité des autres vaisseaux (amendement 1)

*   **Positions des systèmes dans l'état :** le client dessinerait aux coordonnées, et cela préparerait les distances variables ; mais `State` et l'observation recevraient deux champs par système, et la génération du graphe se compliquerait.
*   **Un tableau, sans dessin :** fidèle au rendu « façon tableur », mais sans vue d'ensemble du graphe, ce qui était l'une des gênes relevées.
*   **Visibilité :** voir le saut des autres vaisseaux, ou leur activité, partout (plus de mouvement visible, mais une information donnée à tous les concurrents) ; ou le statu quo (tout vaisseau visible partout, mais immobile pendant ses sauts).
*   **Stock des gisements public :** la carte en dirait plus, mais la baisse du stock, à une unité par tick, permettrait de compter les vaisseaux qui minent loin, hors de portée.
*   **Retenu :** choix du propriétaire : mise en page calculée par le client ; les vaisseaux d'autrui et le stock des gisements ne sont visibles qu'à proximité (système d'un des vaisseaux de l'acteur, ou système voisin), sans l'activité des vaisseaux (ADR 0005). Des scanners porteront plus loin plus tard.

### Alternative Z : les scénarios de partie sur les vrais réglages seulement (amendement 1)

*   **Avantages :** un seul jeu de réglages à suivre.
*   **Inconvénients :** chaque essai de réglage repasserait par une pull request de scénarios protégée, et la CI comme la mutation s'allongeraient (sur la carte d'origine, un cycle dure 1 701 ticks).
*   **Retenu :** des réglages de test explicites dans les étapes, plus un seul scénario sur les vrais réglages.

### Alternative AA : interdire qu'une station et un gisement partagent un système (amendement 1)

*   **Avantages :** tout cycle passe par au moins un saut aller et un saut retour (900 ticks ou plus) ; aucun gisement ne peut se vider (au plus 6 000 unités extraites par fenêtre de 10 000 ticks : 5 PNJ, chacun au plus 12 cargaisons de 100, pour un stock de 20 000) ; les bornes d'économie sont plus étroites.
*   **Inconvénients :** il faudrait au moins 9 systèmes (`stations_max` + `deposits_max`), donc une fourchette de 9 à 12 ; la carte perdrait une situation de jeu, le gisement dans le système d'une station, qui rapporte vite puis s'épuise.
*   **Retenu :** décision du propriétaire (2026-11-12) : la colocalisation est voulue ; dans le pire des cas, le gisement s'épuise, et joueurs et PNJ doivent aller miner ailleurs. Une station et un gisement peuvent donc partager un système (Technical Plan, point 2). Au moins une station partage son système avec un gisement dans 84 % des mondes générés, et avec un gisement de `ore_b`, le seul minerai que visent les PNJ avec les prix proposés, dans 52 % (calculs du 2026-11-12 et du 2026-11-13, nombres de systèmes, de stations et de gisements supposés équiprobables).

### Alternative AB : garder le rendu en caractères seuls, sans couleur, et le soigner (amendement 2)

*   **Avantages :** aucune décision du niveau 1 ne change.
*   **Inconvénients :** sans couleur ni pixels, le graphe reste pauvre et l'information se hiérarchise mal ; c'est le choix « sans thème de couleur » de l'amendement 1 que le propriétaire remet en cause, après l'avoir jugé « pas clair ». Cette alternative porte sur le style ; l'alternative AE, sur la disposition de la carte.
*   **Retenu :** l'écran rétro en couleurs et demi-blocs (ADR 0006).

### Alternative AC : un client graphique natif en Python (amendement 2)

*   **Avantages :** pixel art libre, police choisie par le jeu.
*   **Inconvénients :** cadres, listes et texte à construire soi-même ; une seconde boîte à outils à tester ; le propriétaire a jugé suffisantes des maquettes de l'écran dans le terminal.
*   **Retenu :** Textual dans le terminal ; option réexaminée si la partie d'essai de l'amendement 2 échoue pour une raison propre au terminal (ADR 0006).

### Alternative AD : un client dans le navigateur (amendement 2)

*   **Avantages :** le plus souple pour le graphe et la mise en page.
*   **Inconvénients :** un second langage et ses outils, et le transport WebSocket, prévu à M3, à avancer à M1.
*   **Retenu :** pas à M1 ; à réexaminer au niveau 2 de M3, qui prévoit déjà un client relié par WebSocket.

### Alternative AE : garder la mise en page en colonnes de l'amendement 1 (amendement 2)

*   **Avantages :** déjà livrée et testée.
*   **Inconvénients :** des liens écrits en texte, aucune vue d'ensemble ni zoom ; elle ne répond pas à la demande d'un graphe « clair et joli ».
*   **Retenu :** la disposition par forces ; `clients/map_layout.py` est supprimé.

### Alternative AF : une carte animée, comme le graphe d'Obsidian (amendement 2)

*   **Avantages :** au plus près de la demande (« une forme de gravité entre les nodes ») ; les systèmes bougent et se tirent.
*   **Inconvénients :** un rendu à chaque image, y compris au palier ×100 ; une carte qui bouge sous le pointeur ; des tests du pilote plus fragiles.
*   **Retenu :** une disposition calculée une fois par partie (décision du propriétaire, 2026-11-22). L'animation reste possible plus tard (Future Improvements).

### Alternative AG : la méthode de disposition (amendement 2)

*   **Options pesées :**
    - des coordonnées tirées par `world.generate` : elles entreraient dans l'état et les empreintes, pour une donnée d'affichage ;
    - des couches par distance seules : lisibles, mais sans « gravité » entre voisins ;
    - les forces, en partant d'un cercle : plus de croisements de liens pour un arbre ;
    - les forces, en partant des couches, avec une passe de séparation.
*   **Retenu :** la dernière (Technical Plan, point 7 ter).

### Alternative AH : le conseil de la prochaine étape, à l'arrêt (amendement 2)

*   **Options pesées :**
    - la décision du PNJ (`scripted_miner.decide`) : une seule règle de décision dans le dépôt, mais elle vise toujours le minerai le mieux payé sans peser la durée ; avec les prix proposés, elle envoie le joueur vers `ore_b`, parfois à une heure de route alors qu'un cycle local de 5 minutes existe, là où les PNJ s'entassent ;
    - la même, avec la durée du cycle affichée : le joueur voit le prix en temps, mais reste mal conseillé ;
    - deux options affichées, la mieux payée et la plus proche : enseigne le compromis, mais charge le cadre ;
    - le cycle au meilleur gain par tick : colle à l'objectif 13 (le temps est une ressource), au prix d'une petite règle de plus, testée règle par règle.
*   **Retenu :** le gain par tick (décision du propriétaire, 2026-11-22 ; Technical Plan, point 7 ter). La station d'un cycle est celle que la règle de vente retiendra, pour que le plan annoncé ne change pas en route. Le gisement conseillé peut changer à l'arrivée ; garder en mémoire le gisement prévu éviterait ce changement, mais ajouterait un état au client et un cas à chaque règle : ce n'est pas retenu à M1.


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
| L'épuisement et le départage ne sont exécutés par la partie de référence que si le monde de la graine 1 le permet (amendement 1, réécrit) | Un défaut de départage échappe au contrôle `rejeu` | — | Scénarios et tests de propriétés à stock bas ; le bug volontaire de la suite canari vise la génération du monde (Technical Plan, point 2), toujours exécutée, et son ancre suit la fonction de génération (plan détaillé, point 29) |
| Une pull request de fonctionnalité casse un bug volontaire de la suite canari | Le contrôle de nuit `canari` échoue sans qu'un contrôle ne le signale avant la fusion | Tâche `canari` en échec | Les bugs volontaires sont ancrés sur des symboles (fonction nommée, fin du module, expression nommée), pas sur des lignes ; la nuit suivante, l'agent de code corrige l'ancre par une pull request protégée |
| Les tâches de CI dépassent 30 minutes | Pull requests lentes, contrôle trop coûteux à garder | Mesure du plan détaillé, point 28 bis | Arrêt et signalement au propriétaire avant de continuer |
| Entre les paliers 2 et 4, une pull request en échec est fusionnée | Une régression entre dans `main` | Tâches en échec sur la pull request | Le propriétaire ne fusionne pas une pull request en échec ; l'intervalle se ferme au palier 4 |
| Entre les paliers 2 et 4, l'étiquette « références régénérées » est retirée | Une régénération des références passe sans attention particulière | Historique des étiquettes | Le contrôle de garde exige quand même la montée de révision ; le hook est mis à jour au palier 4 (plan détaillé, point 31 ter) ; risque accepté pendant cet intervalle |
| Entre le volet C et le palier 4, `tests/rejeu/**` et `tests/economie/**` ne sont pas protégés | Une pull request de fonctionnalité pourrait affaiblir le rejeu ou les fourchettes sans étiquette | Revue des pull requests par le propriétaire | Protection au palier 4 (plan détaillé, point 31 bis) ; risque accepté pendant cet intervalle, comme le niveau 1 l'accepte pour le code avant M1 |
| `duckdb` se compile depuis ses sources sous Python 3.15 | Chaque tâche de CI ralentit de plusieurs minutes | Durée de `uv sync` | Groupe `notebooks` que la CI n'installe pas (plan détaillé, point 14) |
| Le PC d'entraînement est indisponible à la fin du jalon | L'objectif 2 n'a pas de preuve sur le PC d'entraînement | Compte rendu incomplet | Le jalon n'est pas livré tant que la sortie manque ; aucune adresse ni aucun identifiant n'entre dans le dépôt |

**Risques ajoutés par l'amendement 1 :**

| Risque | Effet | Signal | Parade |
| :-- | :-- | :-- | :-- |
| Parties manuelles très longues | à 3 s par tick, un cycle dure par exemple 5 minutes (gisement dans le système d'une station) ou 85 minutes (gisement à deux sauts), et davantage plus loin ; la validation de la boucle et les essais deviennent pénibles | durée de la partie d'essai (plan détaillé, point 23 sexies) | accélération en mode développement (paliers ×1 à ×100, « avancer jusqu'à la prochaine alerte ») ; enchaînement des étapes du cycle (objectif 11) validé en accéléré, rythme sur un saut à la période nominale |
| Accélération oubliée | le joueur croit le jeu figé, ou rate une alerte à ×100 | retour du propriétaire à la partie d'essai | en mode développement, vitesse toujours affichée dans la barre d'état ; retour à ×1 à chaque alerte pendant « avancer jusqu'à la prochaine alerte » |
| Dérive entre `tunables.toml`, les réglages de test et le document | un test ou un scénario passe sur des valeurs qui ne sont plus celles du jeu | scénario sur les vrais réglages en échec | `tunables.toml` est la seule source ; le scénario sur les vrais réglages les lit au lieu de recopier des nombres ; le tableau du document donne les valeurs initiales |
| File de vente coincée | une vente refusée laisse la file attendre | tests du modèle client | la file avance au résultat de la vente précédente ; un refus ou un autre ordre du joueur la vide |
| Jeu d'attente avec un seul vaisseau | environ 94 % d'un cycle en trajet (1 600 ticks sur 1 701, carte d'origine) ; une décision par trajet | verdict de la partie d'essai | accepté à M1 ; la flotte et les scanners viendront plus tard |
| Conséquences pour M4 | environ 4 ordres par cycle de 1 701 ticks, soit environ 425 ticks par décision : des épisodes faits surtout d'attente, des récompenses rares, et un « pas » du niveau 1 (§2 et §8) qui compte surtout des ticks sans décision | mesure au document de niveau 2 de M4 | risque ouvert : la définition du pas et du verdict du niveau 1 est à revoir à M4 ; entraîner sur d'autres réglages n'est pas une issue, puisque M5 compare `rules_version` au déploiement (alternative H) ; piste qui ne change pas `rules_version` : un environnement d'entraînement qui enchaîne les ticks sans décision jusqu'à la suivante |
| Mise en veille de l'ordinateur portable | l'univers se fige probablement pendant la mise en veille | essai du plan détaillé, point 23 quater | vérifiée par cet essai ; sans effet sur les règles ni sur le rejeu |
| Écritures disque à vitesse élevée | à ×100, un commit SQLite par tick | mesure du plan détaillé, point 28 bis | le palier ×100 (0,03 s par tick) borne le débit |
| Mises à jour accumulées | au palier ×100, la file des mises à jour du client grossit | débordement mesuré au plan détaillé, point 28 bis | le modèle client traite toutes les mises à jour, et l'écran ne redessine que la dernière ; la longueur des files, celle du propriétaire et celles de relais des PNJ, et les refus d'ordres qu'elles causent sont mesurés au plan détaillé, point 28 bis ; une contre-pression ne s'ajoute que si la mesure le demande |
| Peu de PNJ visibles | avec la visibilité par proximité, la plupart des 3 à 5 PNJ, et le stock des gisements lointains, sont hors de vue sur 8 à 12 systèmes, d'autant que les PNJ se regroupent autour d'un ou deux gisements (Technical Plan, point 7) | verdict de la partie d'essai | accepté par le propriétaire (décision de jeu, ADR 0005) ; à revoir à la partie d'essai, qui dira si l'écran paraît vide |
| (amendement 2, réécrit) Carte illisible pour certaines graines | voir le risque « Disposition illisible pour certaines graines », ajouté par l'amendement 2 | | |
| PNJ décalés au palier rapide | avec la tâche de relais, une décision peut entrer au deuxième tick suivant, ou plus tard, au lieu du tick suivant ; si plusieurs décisions d'un PNJ en retard entrent dans le même tick, la plus ancienne gagne (un ordre par vaisseau et par tick, celui de plus petit numéro ; Technical Plan, point 2) | rejeu d'une partie accélérée | accepté par le propriétaire, qui a gardé la tâche de relais (alternative X) ; le rejeu suit le journal, il reste exact |
| Épuisement par colocalisation | des PNJ bouclent sur un gisement dans le système d'une station et le vident avant sa régénération | stock à 0 relevé par l'outil de régénération après la partie | accepté (alternative AA) : le PNJ retient le gisement vide et va miner ailleurs (Technical Plan, point 7) ; les bornes d'économie, larges, ne dépendent pas de l'épuisement (plan détaillé, point 27) |
| Gisement vide découvert à l'arrivée | hors de portée, le stock est inconnu : un vaisseau peut faire un trajet vers un gisement vide | tests de la politique du PNJ | accepté (ADR 0005) : le trajet est perdu, mais le PNJ retient le gisement vide et va au plus proche gisement qu'il n'a pas vu vide, plus loin s'il le faut (décision du propriétaire, 2026-11-21 ; Technical Plan, point 7) |

**Risques ajoutés par l'amendement 2 :**

| Risque | Effet | Signal | Parade |
| :-- | :-- | :-- | :-- |
| Rendu différent selon le terminal | couleurs dégradées, demi-blocs mal dessinés, police peu lisible | partie d'essai de l'amendement 2 | contraste testé sur les couples de `CONTRAST_PAIRS` et `GRAPHIC_PAIRS` ; rendu en 256 couleurs essayé à la partie d'essai (point 23 undecies), avec le nom du terminal et `COLORTERM` consignés ; condition de révision de l'ADR 0006 |
| Terminal trop petit | carte et cadres tronqués | taille de la fenêtre | cible 120 × 36 ; carte qui rétrécit jusqu'à 100 × 30 ; en dessous, un message qui demande d'agrandir la fenêtre |
| Souris absente ou mal transmise par le terminal | zoom et clic impossibles | essai du propriétaire | toutes les actions ont une touche (`z`, `x`, `c`, flèches, `d`) |
| Rendu trop lent aux paliers rapides | écran qui saccade, mises à jour accumulées | temps de rendu mesuré au plan détaillé, point 28 bis | grille recalculée seulement quand ses entrées changent ; au plus 10 rafraîchissements par seconde ; seule la dernière mise à jour est dessinée |
| Disposition illisible pour certaines graines | systèmes trop proches, liens qui se croisent | aucun recouvrement dans la grille, vérifié sur les graines 1 à 2 000 en 120 × 36 et en 100 × 30 ; croisements mesurés et publiés | départ en couches ; séparation par boîtes, calculée pour le cas le plus serré ; étiquettes seulement à partir du zoom 2 ; bulle d'information |
| Prochaine étape trompeuse | le joueur suit un conseil inadapté : un gisement qui se vide, que les PNJ minent sans que le joueur voie leur activité ; un gisement hors de portée au stock supposé suffisant ; un gisement qui cède la place à un autre une fois arrivé | tests règle par règle ; partie d'essai, avec la durée du premier cycle consignée au compte rendu | conseil au meilleur gain par tick, qui écarte les gisements connus vides ; il ne fait que guider ; le joueur garde toutes les touches |

## Additional Resources

*   [Niveau 1](./architecture-niveau-1.md), [RFC du brainstorm](./mmo-gestion-spatiale-ia.md), [glossaire](../glossaire.md), [document de M0](./niveau-2-m0-garde-fous.md).
*   Essais du 2026-11-02, hors du dépôt : `mutmut` 3.8.0 et `cosmic-ray` 8.7.0 sous Python 3.15 ; lecture du chargement de la configuration de `mutmut` 3.8.0 (`pyproject.toml` d'abord, sinon section `[mutmut]` de `setup.cfg`).
*   Essais du 2026-11-06, hors du dépôt, sous Python 3.15.2 : lecture du code de `mutmut` 3.8.0 (clés `source_paths`, `only_mutate`, `do_not_mutate`, `also_copy`, `pytest_add_cli_args` ; filtrage de `mutmut run` par motifs de noms de mutants ; `export-cicd-stats` ne donne que des totaux ; sortie de `mutmut results --all true`) et une mutation d'un petit projet ; métadonnées `msgspec.Meta(extra=...)` relues par `msgspec.inspect.type_info` sur `msgspec` 0.22.0 ; route `GET /repos/EZPK/4X/branches/main` lue sans jeton.
*   Rapports de la revue EGM de ce document : `docs/revues/2026-11-06-niveau-2-m1-noyau/`.
*   **(amendement 1)** Brief du brainstorm et rapports de revue de l'amendement : `docs/revues/2026-11-12-niveau-2-m1-noyau-amendement-1/`. Simulation du 2026-11-12, hors du dépôt : cycle de 1 701 ticks et 10 à 12 ventes par fenêtre de 10 000 ticks pour les deux PNJ ensemble (carte d'origine, `jump_ticks` = 400, `mining_rate` = 1, deux PNJ). Calculs du 2026-11-12 et du 2026-11-13 : une station partage son système avec un gisement dans 84 % des mondes générés, et avec un gisement de `ore_b` dans 52 % (nombres de systèmes, de stations et de gisements supposés équiprobables). Essai du 2026-11-21, hors du dépôt, sur la génération du Technical Plan, point 2, écrite d'après ce document avec `keyed_below` du noyau : la graine 1 donne 11 systèmes, 2 stations, 6 gisements et 5 PNJ ; la borne haute de l'émission du plan détaillé, point 27, y vaut 757 500 par fenêtre, pour une émission de 287 100 à 294 000 calculée d'après le cycle de chaque PNJ ; sur les graines 1 à 10 000, le cycle de tous les PNJ passe par un seul gisement dans 78 % des mondes, et par deux gisements dans 22 %. Ces chiffres sont à refaire sur le code livré.
*   **(amendement 2)** Rapports de revue de l'amendement 2 : `docs/revues/2026-11-22-niveau-2-m1-noyau-amendement-2/`. Maquettes de l'écran rétro, vues par le propriétaire le 2026-11-22, hors du dépôt (canevas privé) : poste de pilotage, carte zoomée, aide.

## Future Improvements

*   **Le mode rejeu du client Textual**, à M3, avec la vidéo rendue depuis un rejeu.
*   **Le journal public de chaque corporation** (niveau 1, §4), à M6 : il sera construit à partir des événements « écriture du registre », puisque l'état ne garde que les écritures du tick.
*   **Une seconde partie de référence, contrainte par le stock** (plusieurs PNJ sur un gisement, `deposit_stock` bas), si les scénarios et les tests de propriétés ne suffisent pas à couvrir l'épuisement et le départage.
*   **(amendement 1) Des événements pendant les trajets** (idée du propriétaire, 2026-11-12) : ce qui peut arriver à un vaisseau en route, une fois les sauts longs. Hors de M1.
*   **(amendement 1) La vitesse propre à chaque vaisseau et la distance entre systèmes :** la durée d'un saut en dépendra, comme celle d'un minage dépendra du laser et de la capacité de la cargaison.
*   **(amendement 1) Des scanners** pour voir plus loin que les systèmes voisins (ADR 0005).
*   **(amendement 1) Des PNJ qui décident seuls ou en groupe**, par exemple pour leur corporation (M6).
*   **(amendement 2) Une carte animée et une mini-carte** (alternative AF ; décision du propriétaire, 2026-11-22).
*   **(amendement 2) Un client graphique natif ou dans le navigateur**, à réexaminer au niveau 2 de M3 (alternatives AC et AD, ADR 0006).


--------------------------------------------------------------------------------

## Detailed Implementation Plan

**Ordre des pull requests.** `CLAUDE.md` impose une pull request de scénarios fusionnée avant chaque pull request de fonctionnalité, et une seule pull request de chaque type ouverte à la fois. M1 avance donc en cinq paliers :
1. décision et documents (pull request protégée) ;
2. outillage de M1 (pull request protégée) : les nouvelles tâches de CI tournent, sans être encore obligatoires ;
3. trois volets de jeu, chacun en deux pull requests : scénarios, puis fonctionnalité ; **(amendement 2, précisé)** les volets B bis (amendement 1) et B ter (amendement 2) s'y insèrent ;
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
*   **Proposed Changes :** ce document, rédigé au statut Proposed, puis la revue EGM complète (étapes 5 à 9 : prise de recul, test de compréhension, critique, prise de recul intermédiaire, préparation à l'implémentation) avec ses rapports dans `docs/revues/2026-11-06-niveau-2-m1-noyau/`. Le propriétaire décide du passage à Approved ; il l'a décidé le 2026-11-08.

#### 2. `docs/feuille-de-route.md` (Modify)

*   **Type / Scope :** feuille de route, chemin protégé.
*   **Proposed Changes :** M1 passe à « en revue » avec la pull request du document, puis à « approuvé » sur décision explicite du propriétaire.

#### 3. `docs/glossaire.md` (Modify)

*   **Type / Scope :** glossaire, chemin protégé. Dans la pull request protégée du point 1, une fois le document approuvé.
*   **Proposed Changes :** chaque « à fixer au niveau 2 de M1 » est remplacé par l'identifiant du Technical Plan, point 12 ; `K_ordres` devient `ORDER_QUOTA_PER_TICK`, et la mention « nom provisoire » disparaît ; les entrées « gisement » (`Deposit`) et « ordre soumis » (`SubmittedOrder`) sont ajoutées. La colonne « Lien » renvoie à ce document pour les identifiants qu'il fixe.

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

*   **(amendement 1)** Complété par le volet B bis.

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

**(amendement 2, précisé)** Les volets B bis et B ter s'insèrent entre les volets B et C.

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
    - `tunables.py` et `tunables.toml`. Valeurs de M1 : `jump_ticks` = 5, `mining_rate` = 10, `cargo_capacity` = 100, `ore_prices` = [10, 15], `tax_rate_bp` = 1 000 (10 %), `budget_regen` = 1, `budget_max` = 10, `deposit_stock` = 20 000, `regen_ticks` = 1 000 *(remplacé par l'amendement 1, voir ci-dessous)*. Ce fichier est une donnée du paquet, lue par le serveur.

      La régénération d'un gisement tous les 1 000 ticks *(remplacé par l'amendement 1 : tous les 10 000 ticks)* est alignée sur les fenêtres des fourchettes économiques. Avec deux PNJ, au plus 10 200 unités sont extraites par fenêtre (point 27) : aucun gisement ne se vide, et les bornes du point 27 restent valables *(remplacé par l'amendement 1 : un gisement peut se vider, voir le point 27)*. Les valeurs du monde en ligne (stock plus large, régénération d'un gisement environ chaque semaine) seront fixées à M5 ;
    - `state.py`, `ledger.py`, `world.py` (génération et placement des sites, Technical Plan, point 2 ; libellés neutres), `step.py`, `observe.py`, `fingerprints.py`, `snapshot.py` ;
    - `version.py` : `RULES_REVISION` = 0 au volet A ; il passe à 1 avec la première création des références (point 26), selon la règle « plus un » du contrôle de garde.

*   **Proposed Changes (amendement 1, remplacement) :** les valeurs de `tunables.toml` sont celles du Technical Plan, point 2 (amendement 1). Les valeurs d'origine (saut de 5 ticks, minage de 10 unités par tick, `regen_ticks` = 1 000, un seul jeu de prix) ne valent plus.

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

*   **(amendement 1)** `partie.feature` et `steps_partie.py` sont réécrits par le volet B bis (point 23 ter).

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

*   **(amendement 1)** Complété par le volet B bis.

#### 23. `tests/server/`, `tests/policies/`, `tests/clients/` (Create)

*   **Type / Scope :** tests unitaires.
*   **Proposed Changes :** réception (dont deux messages d'un même point de connexion dans le même tick : quota et numéros répétés comptés sur les deux) ; journal (enregistrement, relecture, export et import JSONL) ; `tests/server/test_versions_journal.py` (`order_log_schema_version`, `rules_version`, commit et indicateur dans le journal ; objectif 7) ; sortie JSONL des événements ; boucle des ticks en mode sans horloge ; politique `scripted_miner` sur des observations construites à la main (dont : aucun ordre pendant 10 ticks de minage) ; hôte des PNJ. Le client Textual est testé par le pilote de test de Textual (`async with app.run_test() as pilot`, dans une fonction appelée par `asyncio.run`) : envoi d'un ordre au clavier et affichage d'une mise à jour.

*   **(amendement 1)** Complété par le volet B bis.

**Volet B bis : un monde plus grand, un écran lisible, le temps comme ressource (amendement 1)**

**Règles d'intégration.** Aucun point du plan détaillé de ce document n'est renuméroté. Les points 17, 25, 27, 28 et 28 bis sont modifiés sur place, et les points 29 et 32 bis reçoivent une marque de remplacement. Les points 5, 20, 22 et 23 (déjà livrés) reçoivent une ligne de renvoi vers ce volet. Le nouveau **volet B bis** (points 23 bis à 23 sexies) s'insère entre les points 23 et 24. **Aucune pull request du volet C ne s'ouvre avant la fin du point 23 sexies.** Une seule pull request de chaque type est ouverte à la fois.

#### 23 bis. Pull request protégée de l'amendement (amendement 1)

*   **Type / Scope :** pull request protégée, avec une revue EGM complète sans contexte (étapes 5 à 9), dont le résumé en français ouvre la description.
*   **Proposed Changes :**
    - `docs/designs/niveau-2-m1-noyau.md` (Modify) : l'amendement 1, intégré selon les règles d'intégration, avec son en-tête (puce « Amendements », préséance, légende des marques, tableau des amendements). Le statut passe à Proposed **sur la branche seulement**, puis revient à Approved, sur demande explicite du propriétaire, avant la fusion.
    - `docs/feuille-de-route.md` (Modify) : M1 passe à « en revue » sur la branche seulement, puis revient à « approuvé » avant la fusion. Sur `main`, rien ne change : M1 n'est jamais gelé.
    - `docs/adr/0003-observe-recoit-les-reglages.md` (Create) : `observe(état, acteur, réglages)` et la vue des réglages publics. Statut « proposée ».
    - `docs/adr/0004-fourchettes-de-la-tranche-0.md` (Create) : 8 à 12 systèmes, 4 à 6 gisements, 2 à 3 stations à prix propres, deux minerais, 3 à 5 PNJ ; une station et un gisement peuvent partager un système. Statut « proposée ».
    - `docs/adr/0005-visibilite-par-proximite.md` (Create) : la classe `NEARBY` et sa règle, pour les vaisseaux d'autrui et le stock des gisements ; les scanners comme extension future. Statut « proposée ».
    - `docs/adr/README.md` (Modify) : les trois lignes d'index.
    - `docs/designs/architecture-niveau-1.md` (Modify) : les sections touchées par les trois ADR, comme l'exige le README des ADR. CUJ 1 (puces « Given ») : les fourchettes. Niveau 1, §5 (puce « Chaque champ de l'état porte une classe de visibilité ») : la classe de proximité et la signature d'`observe` ; la puce « Il n'y a pas d'autre canal vers le joueur » reste mot pour mot. Le propriétaire passe lui-même les ADR à « acceptée » avant de fusionner. S'il en refuse une, la modification correspondante du niveau 1 et les passages de l'amendement qui en dépendent sont retirés avant la fusion.
    - `docs/glossaire.md` (Modify) : les termes du Technical Plan, points 12 et 13 (réglages publics, proximité, période nominale, mode développement), et la mise à jour de « référence scriptée » (`policy_version` 2).
    - `setup.cfg` (Modify) : `src/fourx/clients/frames.py` s'ajoute à `do_not_mutate`, comme `textual_app.py` : ce sont des widgets d'affichage. `model.py`, `map_layout.py` et `texts.py` restent mutés. `tests/outillage/test_mutation.py` (Modify) : sa copie de la liste (`EXCLUS`) suit `setup.cfg`.
    - `docs/revues/2026-11-12-niveau-2-m1-noyau-amendement-1/` (Create) : `README.md`, le brief `concepts_brief.md` (déplacé depuis la racine du worktree), et les rapports de la revue EGM.

#### 23 ter. Pull request de scénarios (amendement 1)

*   **Type / Scope :** pull request de scénarios, chemins protégés. Elle s'ouvre après la fusion du point 23 bis.
*   **Proposed Changes :**
    - `tests/scenarios/partie.feature` (Modify) : réécrit sur des mondes générés, sans supposer la carte de la graine 1. Les étapes lisent la géométrie dans l'observation (« le gisement de ore_b le plus proche », « la station qui paie le mieux ore_b »). Les scénarios distinguent l'ancienne règle de la nouvelle, pour échouer sur le code d'origine :
      - **Réglages de test :** les valeurs de `tunables.toml`, sauf `jump_ticks` = 5 et `mining_rate` = 10 ; pour un monde de 12 systèmes, aussi `systems_min` = `systems_max` = 12. **Graines :** une étape qui demande un monde particulier (colocalisation, système à deux sauts du vaisseau du joueur) prend la première graine, à partir de 1, dont `world.generate` donne ce monde ; les autres prennent la graine 1 ;
      - CUJ 1 : un cycle complet sur les réglages de test, sur un monde de 8 systèmes au moins ;
      - le temps comme ressource, sur les vrais réglages : les durées lues dans `observation.public_tunables` sont celles de `tunables.toml`, un trajet observé dure `jump_ticks` ticks, et la cargaison n'est pleine qu'après `cargo_capacity` ÷ `mining_rate` ticks de minage. Il échoue sur le code d'origine, où `public_tunables` n'existe pas. La valeur 400 n'est vérifiée par aucun test ;
      - la vente à une station autre que la station 1, au prix de cette station ;
      - la visibilité par proximité : un vaisseau deux sauts plus loin n'apparaît pas dans l'observation, et le stock d'un gisement à deux sauts vaut `None` ; un vaisseau voisin apparaît, sans son activité ;
      - la colocalisation : sur un monde où une station et un gisement partagent un système, un vaisseau y mine puis y vend sans saut ;
      - le PNJ vend une cargaison dans les 2 000 ticks, sur les réglages de test ;
      - les trois refus de réception déjà présents, réécrits sans position supposée (« son vaisseau dans son système de départ, à l'arrêt ») et sur les réglages de test, donc en attente.
    - `tests/scenarios/ecrans.feature` (Create) : le modèle client et la mise en page, sans Textual :
      - un refus `NO_DEPOSIT_FOR_ORE` est traduit en français et nomme le gisement le plus proche du minerai ; un refus `DEPOSIT_EMPTY` nomme le plus proche gisement du même minerai qui n'est pas connu comme vide ;
      - les ticks restants d'un trajet et d'un minage, comparés à `Game.advance` ;
      - la vente de toute la cargaison part en deux ordres, sur deux ticks, tous deux acceptés ; la cargaison mêlée s'obtient en minant `ore_a` 2 ticks, puis en allant miner `ore_b` au gisement le plus proche jusqu'à la cargaison pleine ;
      - les deux alertes, et leur absence sur un saut intermédiaire ou sur un minage interrompu par un ordre ;
      - la carte d'un monde de 12 systèmes contient chaque système et chaque lien une fois.
    - `tests/scenarios/steps/steps_partie.py` (Modify) et `tests/scenarios/steps/steps_ecrans.py` (Create) : les définitions d'étapes, avec des réglages de test explicites.
    - `tests/scenarios/steps/steps_noyau.py` (Modify) : `REGLAGES_M1` perd `ore_prices` et prend `station_ore_prices` = ((10, 15), (12, 12), (8, 18)) et les fourchettes de `tunables.toml` (il garde son nom) ; l'étape qui construit la station lit `station_ore_prices[0]` ; la phrase « les réglages de M1 » de `tests/scenarios/noyau.feature` (Modify) devient « des réglages de test ». Les scénarios du noyau dont les étapes changent échouent sur le code d'origine (champs inconnus de `Tunables`) : ils sont marqués *en attente* comme les nouveaux.
    - `tests/scenarios/test_scenarios.py` (Modify) : importe `steps_ecrans`.
    - `tests/scenarios/en_attente.txt` (Modify) : chaque scénario qui échoue sur le code d'origine, et lui seul (un scénario en attente qui passe fait échouer la CI : `xfail(strict=True)`).
    - **Mutation :** les scénarios du noyau passant en attente ne tuent plus de mutants, et la mutation de tout `core`, déclenchée par `steps_noyau.py`, peut descendre sous le score du commit de base. L'agent de code relève alors les scores avant et après dans la description de la pull request et le signale au propriétaire, qui décide ; il n'affaiblit aucun test pour remonter le score. La même conduite vaut aux points 23 quater et 23 quinquies.

#### 23 quater. Pull request de fonctionnalité : règles, formats, serveur et PNJ (amendement 1)

*   **Type / Scope :** pull request de fonctionnalité, après la fusion du point 23 ter. Elle retire de `en_attente.txt` les scénarios qu'elle fait passer, c'est-à-dire tous sauf ceux du client (`ecrans.feature`).
*   **Proposed Changes :**
    - `src/fourx/core/tunables.toml` et `src/fourx/core/tunables.py` (Modify) : les réglages du Technical Plan, point 2 ; les contrôles croisés au décodage (minimums et maximums, nombre de lignes de prix, assez de systèmes).
    - `src/fourx/core/world.py` (Modify) : la génération en six tirages du Technical Plan, point 2 ; `npc_count`. Les clés de tirage (entité et motif) sont celles du Technical Plan, point 2 ; les motifs sont des chaînes constantes du module (`"world_size"`, `"tree"`, `"extra_link_count"`, `"extra_links"`, `"station_count"`, `"stations"`, `"deposit_count"`, `"deposits"`, `"npc_count"`).
    - `src/fourx/core/step.py` (Modify) : la station du système du vaisseau remplace `t.station()` (vente, refus `NOT_AT_STATION`) ; le départ d'un nouveau personnage à la station de rang `rem_trunc(n − 1, S)` ; le nombre de minerais lu dans la première ligne de `station_ore_prices`.
    - `src/fourx/schema/visibility.py` (Modify) : `NEARBY`.
    - `src/fourx/core/state.py` (Modify) : les champs `id`, `owner_id`, `system_id` et `capacity` de `Ship`, et le champ `stock` de `Deposit`, passent à `NEARBY`.
    - `src/fourx/schema/events.py` (Modify) : `Departed`, `Arrived` et `DepositRegenerated` passent à `NEARBY`.
    - `src/fourx/schema/observation.py` (Modify) : `PublicTunablesView`, le champ `public_tunables` (dernier champ de `Observation`), et `DepositView.stock: Int64 | None`.
    - `src/fourx/schema/protocol.py` (Modify) : `PROTOCOL_VERSION` = 2 et `NOMINAL_TICK_PERIOD_S` = 3.0.
    - `src/fourx/core/observe.py` (Modify) : la signature `observe(state, actor_id, tunables)`, la vue des réglages publics, le filtre de proximité, selon la règle du Technical Plan, point 5 (système de référence, positions de l'état reçu, stock `None` hors de portée).
    - `src/fourx/server/game.py` (Modify) : la période nominale par défaut, le premier tick immédiat, l'appel à `observe` avec les réglages. Le nombre de PNJ vient de `core.world.npc_count`, appelé par `__main__.py`. La vitesse (`set_period`, `speed.jsonl`) vient au point 23 quinquies, avec son seul utilisateur, le client.
    - `src/fourx/__main__.py` (Modify) : `--periode` par défaut à `NOMINAL_TICK_PERIOD_S` ; création de `npc_count` PNJ, chacun avec sa connexion et sa tâche de relais ; la graine et le dossier de la partie affichés au lancement et à la fermeture du client (Technical Plan, point 6). L'option `--dev` vient au point 23 quinquies.
    - `src/fourx/policies/scripted_miner.py` (Modify) : la règle du Technical Plan, point 7 (dont la liste des gisements vus vides, reçue et rendue par `decide`), `POLICY_VERSION` = 2.
    - `src/fourx/clients/npc_host.py` (Modify) : `NpcHost` garde la liste rendue par `decide` et la lui repasse à la décision suivante.
    - `src/fourx/policies/geometry.py` et `src/fourx/policies/cargo.py` (Create) : `distances(systems, start)` et `most_abundant(cargo)`, sans logique de décision, réutilisées par le PNJ et par le client.
    - `src/fourx/clients/textual_app.py` (Modify) : adaptation minimale à l'observation nouvelle (prix de la station du système, stock `None` affiché « ? »), pour que le client d'origine reste jouable jusqu'au point 23 quinquies.
    - Tests non protégés (Modify) : `tests/aide_monde.py` (nouveaux champs de `REGLAGES`, plusieurs stations) ; `tests/aide_observation.py` (`public_tunables`) ; `tests/core/test_step.py` (vente à plusieurs stations, système de départ, colocalisation) ; `tests/core/test_observe.py` (proximité des vaisseaux, des événements et du stock ; réglages publics ; aucun champ caché ; tout type qui porte un champ `NEARBY` a un système de référence) ; `tests/core/test_monde_version_empreintes.py` (génération : fourchettes, connexité, plafond de voisins, déterminisme) ; `tests/core/test_versions.py` (`PROTOCOL_VERSION` 2) ; `tests/schema/test_schema.py` ; `tests/proprietes/test_proprietes.py` (marque `proprietes` : génération sur de nombreuses graines, proximité ; la carte, avec la part des liens tracés et la hauteur écrites dans la sortie du test, `-s`, et citées au compte rendu de M1 *(remplacé par l'amendement 2, voir le plan détaillé, point 23 decies : le recouvrement et les croisements de la disposition par forces)*) ; `tests/core/test_monde_version_empreintes.py` (aussi : même monde sous `PYTHONHASHSEED=0` et `1`, par deux `subprocess.run`) ; `tests/policies/test_scripted_miner.py` (règle version 2 et liste des gisements vus vides : un vaisseau qui trouve un gisement vide va miner ailleurs, y compris quand les deux gisements les plus proches sont vides ; un gisement revu plein sort de la liste ; la liste se vide quand elle contient tous les gisements) ; `tests/clients/test_npc_host.py` (l'hôte repasse la liste rendue par `decide`) ; `tests/policies/test_geometry.py` et `tests/policies/test_cargo.py` (Create) ; `tests/server/test_partie.py` (période nominale, premier tick) ; `tests/test_point_d_entree.py` (plusieurs PNJ, par une fonction d'assemblage testable de `__main__.py`, `creer_pnj(game, graine, tunables) -> tuple[int, ...]`, qui crée les PNJ et rend leurs identifiants, sans lancer Textual).
    - **Essai de la veille** (risque) : une partie lancée, l'ordinateur portable mis en veille cinq minutes ; le tick avant et après est relevé et cité dans la description de la pull request, puis dans le compte rendu de M1. Si l'univers rattrape au réveil les ticks de la veille au lieu de se figer, l'agent de code le signale au propriétaire avant la partie d'essai : ces ticks seraient joués sans que le joueur les voie.

#### 23 quinquies. Pull request de fonctionnalité : l'écran unique et la vitesse du mode développement (amendement 1)

*   **Type / Scope :** pull request de fonctionnalité, après la fusion du point 23 quater. Elle retire de `en_attente.txt` les scénarios de `ecrans.feature`.
*   **Proposed Changes :**
    - `src/fourx/clients/model.py` (Create) : `ClientModel` (Technical Plan, point 7 bis), sans Textual.
    - `src/fourx/clients/map_layout.py` (Create) : la mise en page de la carte, fonction pure.
    - `src/fourx/clients/texts.py` (Create) : `refusal_text` (la table des 18 codes de refus, avec la commande refusée), `duration_text` (les durées et l'estimation en minutes). Table des refus :

      | Code | Message (exemples de données entre crochets) |
      | :-- | :-- |
      | `UNKNOWN_SHIP` | vaisseau inconnu |
      | `NOT_OWNER` | ce vaisseau n'est pas le vôtre |
      | `SHIP_EN_ROUTE` | vaisseau en route : arrivée dans [N] ticks |
      | `UNKNOWN_SYSTEM` | système inconnu |
      | `ALREADY_THERE` | déjà dans [system_k] |
      | `NO_DEPOSIT_FOR_ORE` | pas de gisement de [ore_a] ici ; le plus proche est dans [system_k] ([n] sauts) |
      | `DEPOSIT_EMPTY` | gisement vide ; le plus proche gisement de [ore_a] qui n'est pas connu comme vide est dans [system_k] ([n] sauts) |
      | `CARGO_FULL` | cargaison pleine : allez vendre ; la station la plus proche est [Sk] ([n] sauts) |
      | `NOT_AT_STATION` | pas de station ici ; la plus proche est [Sk], dans [system_k] ([n] sauts) |
      | `QUANTITY_NOT_POSITIVE` | quantité nulle ou négative |
      | `QUANTITY_EXCEEDS_CARGO` | quantité supérieure à la cargaison ([q] à bord) |
      | `NO_ACTION_LEFT` | plus d'action disponible ce tick |
      | `SUPERSEDED` | remplacé par un autre ordre du même tick |
      | `INVALID_FORMAT` | ordre mal formé |
      | `DUPLICATE_NUMBER` | numéro d'ordre déjà utilisé |
      | `QUOTA_EXCEEDED` | trop d'ordres ce tick |
      | `ACTOR_MISMATCH` | ordre au nom d'un autre personnage |
      | `FORBIDDEN_CATEGORY` | catégorie d'ordre interdite |
    - `src/fourx/clients/frames.py` (Create) : un widget par cadre (carte, vaisseau, stations, historique, barre d'état, alerte), chacun relié au modèle seul.
    - `src/fourx/clients/textual_app.py` (Modify) : `FourxApp` réduit à l'affichage et aux touches ; la disposition du Technical Plan, point 7 bis ; la table des touches ; la fonction `set_speed` reçue de `__main__.py`, ou `None` hors mode développement (aucune touche de vitesse).
    - `src/fourx/server/game.py` (Modify) : `set_period` (une période en secondes, `None` pour la pause, réveil par `asyncio.Event` et recalcul de l'attente restante), `speed.jsonl` (avec son en-tête versionné).
    - `src/fourx/__main__.py` (Modify) : l'option `--dev`, qui seule donne au client la fonction de rappel `set_speed`, construite sur `Game.set_period` et la période de lancement.
    - `tests/server/test_partie.py` (Modify) : `set_period`, `speed.jsonl`, rejeu exact d'une partie jouée en accéléré (les ordres de `OrderLog.orders_by_tick()` rejoués par `step` redonnent les empreintes de `OrderLog.fingerprints_by_tick()` ; l'outil de rejeu n'existe qu'au volet C) ; `tests/test_point_d_entree.py` (Modify) : `--dev`.
    - `tests/clients/test_model.py`, `tests/clients/test_map_layout.py`, `tests/clients/test_texts.py` (Create) : les fonctions pures, et le modèle joué comme client synchrone par `Game.advance` (trajet de `jump_ticks` ticks, file de vente, alertes, ordres envoyés).
    - `tests/clients/test_textual_app.py` (Modify) : le pilote de Textual en `run_test(size=(80, 24))`, sur des observations fabriquées à des ticks éloignés : chaque touche du tableau, chaque état du vaisseau, la confirmation de `q`.

#### 23 sexies. Action : partie d'essai du propriétaire (amendement 1)

*   **Type / Scope :** action du propriétaire, après la fusion du point 23 quinquies, **avant la pull request de scénarios du volet C**. Après le volet C, toute retouche de `tunables.toml` impose de régénérer les références et d'augmenter `RULES_REVISION`.
*   **Proposed Changes :** le propriétaire joue au moins un cycle complet en mode développement accéléré (`--dev`), et au moins un saut complet à la période nominale (20 minutes avec les valeurs initiales), qui juge le rythme. Il rend deux verdicts, consignés dans le compte rendu de M1 avec la graine et les vitesses jouées : l'écran est lisible (objectif 12) ; la boucle et son rythme lui conviennent (objectif 11). Un réglage à changer passe par une seule pull request de fonctionnalité sur `tunables.toml` (chemin non protégé), qui fait foi, sauf les fourchettes du monde (`systems_min` à `npc_max`) : elles viennent du CUJ 1 du niveau 1, élargi par l'ADR 0004, et les changer demande une nouvelle ADR et un amendement ; les scénarios lisent les réglages, et le tableau du Technical Plan, point 2, ne donne que les valeurs initiales.

**Volet B ter : l'écran rétro (amendement 2)**

**Règles d'intégration (amendement 2).** Les points 23 septies à 23 undecies suivent le point 23 sexies, indépendamment du volet C : le volet C peut démarrer depuis `main` dès le 2026-11-22 (décision du propriétaire), à condition qu'une seule pull request de chaque type (protégée, de scénarios, de fonctionnalité) soit ouverte à la fois. Dans `src/`, ils ne touchent que `clients`.

#### 23 septies. Pull request protégée de l'amendement 2 (amendement 2)

*   **Type / Scope :** pull request protégée, avec une revue EGM sans contexte (étapes 5 à 9), dont le résumé en français ouvre la description.
*   **Proposed Changes :**
    - `docs/designs/niveau-2-m1-noyau.md` (Modify) : l'amendement 2. Le statut passe à Proposed sur la branche seulement, puis revient à Approved, sur demande explicite du propriétaire, avant la fusion.
    - `docs/feuille-de-route.md` (Modify) : M1 passe à « en revue » sur la branche seulement, puis revient à « approuvé » avant la fusion.
    - `docs/adr/0006-client-retro-8-bits.md` (Create) : statut « proposée » ; le propriétaire l'accepte avant la fusion. `docs/adr/README.md` (Modify) : la ligne d'index.
    - `docs/designs/architecture-niveau-1.md` (Modify) : Overview, « le client en mode texte (Textual), au style rétro 8 bits » au lieu de « le client ASCII ».
    - `docs/revues/2026-11-22-niveau-2-m1-noyau-amendement-2/` (Create) : les rapports de la revue EGM.
    - `pytest.ini` (Modify) : la description de la marque `lent` devient « tests longs, hors de la mutation : fourchettes économiques sur 100 000 ticks, disposition de la carte sur 2 000 graines (tâche rejeu) ».
    - Le glossaire ne change pas (Technical Plan, point 12).
    - Si le propriétaire refuse l'ADR 0006, la modification du niveau 1 et l'amendement 2 sont retirés de la pull request avant la fusion.

#### 23 octies. Pull request de scénarios (amendement 2)

*   **Type / Scope :** pull request de scénarios, chemins protégés, après la fusion du point 23 septies. Elle couvre les deux pull requests de fonctionnalité qui suivent.
*   **Proposed Changes :**
    - `tests/scenarios/ecrans.feature` (Modify) :
      - le scénario « La carte d'un monde de 12 systèmes contient chaque système et chaque lien une fois » devient « La disposition de la carte place chaque système une fois, dans le carré, sans recouvrement, et la même à chaque appel » (réglages de test à 12 systèmes, graine 1) : aucune paire de boîtes de 0,135 × 0,16 ne se recouvre ; la comparaison porte sur deux appels dans le même processus, jamais sur des positions écrites en dur ;
      - « La prochaine étape suit un cycle joué : aller miner, miner, aller vendre, vendre » :
        - *Étant donné :* « sur la première graine dont le gisement conseillé depuis la station 1 n'est pas dans le système d'une station, et le reste depuis son propre système ». `monde_convient` le calcule sur l'état généré, sans le code testé : avec les réglages de test, le stock initial dépasse la capacité et aucun autre vaisseau ne mine, donc q = `cargo_capacity` pour tout gisement. Depuis un système x, le gisement conseillé est celui qui maximise G ÷ T, où, pour chaque gisement g et chaque station s, G = `cargo_capacity` × le prix de s pour le minerai de g, et T = `jump_ticks` × (d(x, g) + d(g, s)) + ⌈`cargo_capacity` ÷ `mining_rate`⌉ (départages : plus petit T, puis plus petit identifiant de gisement, puis de station). La graine convient si g₀, conseillé depuis le système de la station 1, n'est pas dans le système d'une station, et si g₀ est encore conseillé depuis son propre système. Le vaisseau du joueur part à l'arrêt, cargaison vide, dans le système de la station 1 ;
        - *procédure :* à chaque tick après le premier, (1) relever les touches de `next_step(model)` ; (2) faire un seul geste : pour ("enter",), `acknowledge()` ; pour ("d",) ou ("m",), envoyer la commande du `Step` (`model.send`, puis `Serveur.envoyer`) ; pour ("v",), `model.sell_all()` ; (3) jouer un tick ; s'arrêter juste après avoir relevé ("v",) ;
        - *alors :* la suite des touches relevées, répétitions consécutives fondues, est exactement : ("d",), (), ("enter",), ("m",), (), ("enter",), ("d",), (), ("enter",), ("v",) ;
      - « L'aide donne les durées lues dans l'observation » (réglages de test, graine 1) : les lignes de l'aide sur le minage et sur le transport contiennent `duration_text` de ⌈`capacity` ÷ `mining_rate`⌉ et de `jump_ticks`, lus dans l'observation.
    - `tests/scenarios/steps/steps_ecrans.py` (Modify) : les étapes correspondantes, avec `force_layout`, `next_step` et `help_pages` ; l'étape `carte_complete` et sa lecture de la sortie de `map_layout.layout` sont retirées ; l'étape qui lit l'historique lit le texte des `HistoryEntry` ; la condition de graine du scénario du cycle s'ajoute à `monde_convient`. `tests/scenarios/steps/steps_partie.py` (Modify) : cette condition.
    - `tests/scenarios/en_attente.txt` (Modify) : chaque scénario qui échoue sur le code de l'amendement 1, et lui seul : les trois scénarios nouveaux ou réécrits, et les deux scénarios de refus d'`ecrans.feature`, dont l'étape lit désormais le texte des `HistoryEntry`. Le scénario de la disposition y reste jusqu'au point 23 decies.

#### 23 nonies. Pull request de fonctionnalité : cadres, prochaine étape, aide et palette (amendement 2)

*   **Type / Scope :** pull request de fonctionnalité, après la fusion du point 23 octies. Elle retire de `en_attente.txt` les scénarios qu'elle fait passer. L'ancienne carte en colonnes reste en place jusqu'au point 23 decies.
*   **Proposed Changes :**
    - `src/fourx/clients/palette.py` et `src/fourx/clients/guide.py` (Create) : la palette et la prochaine étape du Technical Plan, point 7 ter.
    - `src/fourx/clients/texts.py` (Modify) : `help_pages`.
    - `src/fourx/clients/model.py` (Modify) : `HistoryEntry`, `seen_empty`.
    - `src/fourx/clients/frames.py` (Modify) : les cadres « Prochaine étape » (avec l'alerte), « Vaisseau », « Stations », « Historique », la barre d'état, la barre des touches, l'aide, en couleurs.
    - `src/fourx/clients/textual_app.py` (Modify) : la disposition 120 × 36 (la carte en colonnes dans le cadre de la carte), le message de petite fenêtre, la touche `h`, l'aide au lancement.
    - Tests : `tests/clients/test_palette.py` (Create : contrastes de `CONTRAST_PAIRS` à 4,5 pour 1 et de `GRAPHIC_PAIRS` à 3 pour 1, seize valeurs distinctes) ; `tests/clients/test_guide.py` (Create : chaque règle ; `best_sale` ; les gains par tick et leurs départages ; le stock qui borne la quantité ; la durée « au plus » ; une cargaison mêlée ; une cargaison à 99 sur 100 ; une cargaison non vide sans gisement candidat ; un système inaccessible ; la station d'un cycle égale à celle de la règle 5 une fois la cargaison pleine ; un gisement qui cède la place à l'arrivée) ; `tests/clients/test_texts.py` (Modify : l'aide, comparée ligne par ligne, avec et sans observation, avec et sans mode développement) ; `tests/clients/test_model.py` (Modify : historique typé, gisements vus vides) ; `tests/clients/test_textual_app.py` (Modify : pilote en 120 × 36, chaque cadre, l'aide et ses touches, la petite fenêtre).

#### 23 decies. Pull request de fonctionnalité : la carte rétro (amendement 2)

*   **Type / Scope :** pull request de fonctionnalité, après la fusion du point 23 nonies. Elle retire de `en_attente.txt` le scénario de la disposition.
*   **Proposed Changes :**
    - `src/fourx/clients/force_layout.py` et `src/fourx/clients/map_view.py` (Create) : la disposition et la vue de la carte du Technical Plan, point 7 ter.
    - `src/fourx/clients/frames.py` (Modify) : `MapCanvas` (peinture de la grille, molette, glisser, survol, clic) et la bulle ; l'import de `map_layout` est retiré.
    - `src/fourx/clients/textual_app.py` (Modify) : les touches `z`, `x`, `c` et les flèches ; `d` ouvre la liste sur la destination conseillée.
    - `src/fourx/clients/map_layout.py` et `tests/clients/test_map_layout.py` (Delete).
    - Tests : `tests/clients/test_force_layout.py` et `tests/clients/test_map_view.py` (Create : même résultat à chaque appel, positions dans le carré, aucun recouvrement des boîtes, projection, zoom autour d'un point, déplacement borné, système sous le pointeur, ordre de dessin, étiquettes coupées par mots entiers avec « … », position du vaisseau pendant un saut) ; `tests/clients/test_textual_app.py` (Modify : zoom, déplacement, survol, clic ; le pilote n'ayant ni molette ni glisser, les tests postent eux-mêmes `MouseScrollUp`, `MouseScrollDown` et des `MouseMove` bouton enfoncé ; la touche sans effet des tests existants, `x`, devient `y`) ; `tests/proprietes/test_proprietes.py` (Modify : disposition et grille sur 50 graines) ; `tests/clients/test_force_layout.py` (aussi : les graines 1 à 2 000, sous la marque `lent` seule, avec les croisements écrits dans la sortie) ; les tests des quatre étapes de `force_layout` sur de petits graphes, comparés par `pytest.approx`.

#### 23 undecies. Action : partie d'essai de l'écran rétro (amendement 2)

*   **Type / Scope :** action du propriétaire, après la fusion du point 23 decies (ou dès le point 23 nonies, s'il le souhaite, pour juger les cadres et l'aide).
*   **Proposed Changes :** le propriétaire joue au moins un cycle complet (`--dev` permis), en suivant la prochaine étape ; s'il le peut, il essaie aussi un terminal limité à 256 couleurs. La durée de son premier cycle est consignée. Il rend son verdict sur la lisibilité (objectif 12) et sur les objectifs 17 à 19, consigné dans le compte rendu de M1 avec la graine, la taille du terminal (colonnes × lignes), son nom et `COLORTERM`. Le verdict ne bloque pas la livraison de M1 (décision du propriétaire, 2026-11-22) : s'il est défavorable, au plus une pull request de fonctionnalité de correction suit dans M1 ; au-delà, la condition de révision de l'ADR 0006 s'applique, au niveau 2 de M3.

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

*   **Proposed Changes (amendement 1, ajout) :** `window_stats` prend des fenêtres de **10 000** ticks par défaut.

#### 26. `tests/references/rules-1/` (Create)

*   **Type / Scope :** références, chemin protégé (point 4). Produites par l'outil de régénération du point 27, dans la pull request de fonctionnalité du volet C : c'est le seul chemin protégé qu'une pull request de fonctionnalité peut modifier (`CLAUDE.md`, circuit des pull requests). La même pull request passe `RULES_REVISION` de 0 à 1.
*   **Proposed Changes :** `orders.jsonl` et `reference.json` (Technical Plan, point 8), pour la révision 1 des règles.

#### 27. `tests/rejeu/partie_reference.py`, `tests/rejeu/test_rejeu.py`, `tests/economie/test_fourchettes.py`, `tests/mesure/test_indicateur_avance.py` (Create)

*   **Type / Scope :** tests du contrôle `rejeu`, tests marqués `lent` et `mesure`, et outil de régénération lancé par pytest. Ils vivent sous `tests/` parce que l'outil de régénération assemble `server`, `clients` et `policies` (choix du propriétaire, Technical Plan, point 8). Le point 26 est produit par ce point.
*   **Proposed Changes :**
    - `partie_reference.py` : la partie de référence : graine 1, deux PNJ *(remplacé par l'amendement 1, voir ci-dessous : `npc_count(1, réglages)` PNJ)* joués par l'hôte des PNJ, 100 000 ticks, serveur en mode sans horloge ;
    - `test_rejeu.py` (marque `rejeu`) : importe `tests/references/rules-<RULES_REVISION>/orders.jsonl`, régénère l'état initial par `world.generate(1, tunables)`, rejoue par `replay_orders`, compare `rules_version` et les empreintes tous les 1 000 ticks à `reference.json`, et écrit les empreintes de chaque tick dans `runs/rejeu-<PYTHONHASHSEED>/fingerprints.jsonl` (`runs/rejeu-aleatoire/` si la variable n'est pas définie, comme dans `tests-outillage` avant le palier 4 ; comparées entre elles par la tâche `rejeu`, point 8) ;
    - **outil de régénération :** `FOURX_REGENERER_REFERENCES=1 uv run pytest -m rejeu tests/rejeu/test_rejeu.py`, lancé sur l'ordinateur portable, joue la partie de référence, exporte son journal et ses empreintes dans `tests/references/rules-<RULES_REVISION>/` au lieu de comparer, supprime l'ancien dossier, et affiche le rapport de différences avec la révision précédente. C'est l'outil de régénération que cite `CLAUDE.md` ;
    - `test_fourchettes.py` (marque `lent`) : rejoue le journal enregistré de la partie de référence par `replay_orders`, calcule les grandeurs par `window_stats`, et vérifie, sur chaque fenêtre de 1 000 ticks sauf la première *(remplacé par l'amendement 1, voir les bornes ci-dessous : fenêtres de 10 000 ticks, bornes calculées)* :
      - émission `ORE_SALE` entre 84 000 et 153 000 ;
      - destruction `SALE_TAX` entre 8 400 et 15 300, et égale à la somme des taxes de chaque vente, arrondies vers le haut ;
      - croissance de la masse monétaire entre 75 600 et 137 700 ;
    - `test_indicateur_avance.py` (marque `mesure`, lancé à la main par `FOURX_MESURE=1 uv run pytest -m mesure -s`) : mesure les ticks par seconde de `step` et `observe` sur trois systèmes et 30 PNJ *(remplacé par l'amendement 1, voir le Technical Plan, point 11 : 12 systèmes générés)*, et affiche le résultat (Technical Plan, point 11).

    **Calcul des bornes** *(remplacé par l'amendement 1, voir les bornes ci-dessous)* (fait avec un script le 2026-11-02, refait le 2026-11-06 ; à refaire si un réglage change) :
    - durée minimale d'un aller-retour : `2 × jump_ticks + cargo_capacity / mining_rate` = 20 ticks (gisement voisin de la station) ;
    - durée maximale : `4 × jump_ticks + cargo_capacity / mining_rate + 4` = 34 ticks (gisement à deux sauts, et un tick de délai à chacune des quatre décisions, Technical Plan, point 6) ;
    - ventes par PNJ et par fenêtre : au moins 28 (1 000 / 34, arrondi en dessous, moins une vente coupée par la fenêtre), au plus 51 (1 000 / 20, arrondi au-dessus, plus une) ;
    - chaque vente : 100 unités de `ore_b` à 15, soit 1 500 d'émission et 150 de taxe ;
    - deux PNJ : émission de 84 000 à 153 000, destruction de 8 400 à 15 300, croissance de la masse monétaire de 75 600 à 137 700.

*   **Proposed Changes (amendement 1, remplacement) :** les bornes ne sont plus des nombres écrits ici (décision du propriétaire, 2026-11-21, qui remplace la méthode par cycle du 2026-11-15). La fonction `bornes(etat_initial: State, n_pnj: int, tunables: Tunables) -> Bornes`, de `tests/economie/bornes.py`, les calcule, pour `test_fourchettes.py` comme pour l'outil de régénération, à partir de l'état initial de la graine 1 (`world.generate(1, tunables)`), de `npc_count(1, tunables)` et des réglages, sans lire la partie ni dépendre de la politique du PNJ. Ce sont des bornes larges : une alarme contre une panne (plus aucune vente) ou une explosion de l'argent créé, pas une mesure fine. Notations : W = 10 000 ; N = `npc_count(1, tunables)` ; J = `jump_ticks` ; M = `cargo_capacity` ÷ `mining_rate` ; Q = `cargo_capacity` ; p_max, le plus grand prix de rachat des stations du monde ; d_min, la plus petite distance en sauts entre une station et un gisement (0 en cas de colocalisation) ; C_min = 2 × d_min × J + M, la durée minimale d'un cycle ; b' = ⌈W ÷ C_min⌉ + 1, le nombre maximal de cycles d'un PNJ dans une fenêtre. Sur chaque fenêtre, la première comprise (le départ à vide ne fait que réduire l'émission, et le premier cycle d'un PNJ dure moins de 10 000 ticks même sur la plus longue chaîne : 2 × 11 × 400 + 100 = 8 900 ticks, plus quelques ticks de décision) :
       - émission `ORE_SALE` : au moins une vente (émission strictement positive), et au plus N × b' × Q × p_max (chaque cycle vend au plus une cargaison, au plus au prix p_max) ;
       - destruction `SALE_TAX` : égale à la somme des taxes de chaque vente, arrondies vers le haut ; le test parcourt lui-même les événements `Sale` de la fenêtre, que `WindowStats` ne détaille pas ;
       - croissance de la masse monétaire : égale à l'émission moins la destruction (invariant 2), donc positive ou nulle, et au plus la borne haute de l'émission.

    L'outil de régénération vérifie aussi la partie jouée contre ces bornes : si elle en sort, il refuse d'écrire les références, et l'agent de code le signale au propriétaire, sans changer de lui-même ni la graine, ni les règles, ni la politique, ni le calcul des bornes. Il relève enfin, dans la partie jouée, la valeur de chaque fenêtre, et si un gisement s'est vidé ou si un départage a eu lieu : il rejoue les états par `step` et relève, à chaque tick, un gisement dont le stock tombe à 0 (vidé), et un gisement où plusieurs vaisseaux minaient alors que son stock avant le tick était inférieur à la somme de leurs débits (départage) ; le compte rendu de M1 cite ces relevés et les bornes. Pour la graine 1 (essai cité dans Additional Resources : 5 PNJ, colocalisation, p_max = 15), la borne haute de l'émission vaut 5 × 101 × 100 × 15 = 757 500 par fenêtre, pour une émission d'environ 290 000 calculée d'après le cycle de chaque PNJ.

#### 28. `notebooks/economie_m1.py` (Create)

*   **Type / Scope :** notebook marimo.
*   **Proposed Changes :** lit le fichier `events.jsonl` d'une partie, appelle `window_stats`, et affiche par fenêtre de 1 000 ticks *(remplacé par l'amendement 1, voir le plan détaillé, point 25 : 10 000 ticks)* la masse monétaire, sa croissance, l'émission et la destruction par motif. Il lit aussi les événements avec DuckDB pour les explorer, sans calculer lui-même ces grandeurs.

#### 28 bis. Action — mesure de durée et revue du seuil de mutation

*   **Type / Scope :** action de l'agent de code, sur chaque pull request du palier 3.
*   **Proposed Changes :** relever la durée des tâches `rejeu`, `mutation` et `tests-outillage` (qui lance toute la suite jusqu'au palier 4) dans la description de la pull request ; la mutation la plus longue est celle d'une pull request de scénarios, qui mute tout `core`. Au premier dépassement de 30 minutes, l'agent de code s'arrête et le signale au propriétaire. Sur la pull request de fonctionnalité du volet C, relever aussi la taille de `tests/references/rules-1/`, et les scores de mutation de `core` et `schema` : si l'un d'eux est sous 80 % malgré des tests complets (mutants équivalents), l'agent de code le signale au propriétaire, qui décide du seuil.

*   **Proposed Changes (amendement 1, ajout) :** à partir de la pull request du point 23 quinquies, qui apporte la vitesse, mesurer aussi le débordement de « avancer jusqu'à la prochaine alerte » au palier ×100, sur la graine 1 pendant 20 000 ticks, par un script hors du dépôt dont la sortie est citée dans la description de la pull request ; au-delà de 2 ticks, l'agent de code le signale au propriétaire, qui décide d'une contre-pression. Remesurer la durée des tâches `tests`, `rejeu` et `mutation` après les points 23 ter à 23 quinquies (scénarios plus longs, mutation des étapes), et le débit d'écriture à ×100. Au palier ×100, mesurer aussi la longueur de la file du propriétaire et des files de relais des PNJ, et le nombre d'ordres de PNJ refusés (`SHIP_EN_ROUTE`, `QUOTA_EXCEEDED`) ; au-delà d'un refus par PNJ et par cycle en moyenne, l'agent de code le signale au propriétaire.

*   **Proposed Changes (amendement 2, ajout) :** sur la pull request du point 23 decies, mesurer le temps de calcul de la grille et de peinture de la carte pour une mise à jour, au palier ×100, sur la graine 1, en 120 × 36, pendant 2 000 ticks, par un script hors du dépôt dont la sortie est citée dans la description de la pull request ; au-delà de 30 ms en moyenne, ou de 100 ms au plus, l'agent de code le signale au propriétaire. Relever aussi la durée du test de la disposition sur 2 000 graines, dans la tâche `rejeu`.

### Palier 4 : contrôles obligatoires, contrôles de nuit et suite canari (pull request protégée)

#### 29. `.github/canaris/` et `.github/scripts/canaris.py` (Create)

*   **Type / Scope :** suite canari, chemins protégés.
*   **Proposed Changes :** six bugs volontaires, chacun décrit par un fichier JSON : le contrôle visé, et une liste de modifications (fichier visé ; ancre : début du corps d'une fonction nommée, fin du module, ou expression nommée à remplacer ; texte inséré ou de remplacement). `canaris.py` applique chaque bug par l'analyse de la syntaxe (module `ast`), pas par un patch de lignes, puis lance la commande du contrôle visé, et échoue si cette commande réussit. Table contrôle → commande : celles du point 8.
    - un nombre flottant dans `step` (`core/step.py`) → `tests` ;
    - `core` qui importe `server` → `imports` ;
    - une vente sans écriture de taxe, mais avec le compteur cumulé de destruction augmenté → `tests` (invariants) ;
    - le portefeuille d'un autre acteur laissé dans une observation (`observe`) → `proprietes` ;
    - le placement des sites *(remplacé par l'amendement 1 : le tirage `"world_size"` de `world.generate`, Technical Plan, point 2, ancré sur ce motif)* tiré par `hash()` d'une chaîne au lieu de `keyed_below` (`world.generate`) → `rejeu` (ce tirage a lieu dans chaque partie, et `hash()` d'une chaîne change avec `PYTHONHASHSEED`) ;
    - une fonction insérée à la fin de `core/arith.py` (ancre : fin du module), et un appel inséré au début de `step` dont aucun test ne vérifie le résultat → `mutation` (`mutation.py --base main --tete <commit de la copie>` : le score de `arith.py` baisse par rapport à `main`).

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
    | E2 | `essai-rejeu` | le bug volontaire « placement des sites par `hash()` » (amendement 1 : un tirage de la génération du monde par `hash()`) | `rejeu` en échec, fusion refusée |
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

**(amendement 1)**

Les commandes ci-dessus restent valables. S'y ajoutent :

*   **Tests :** aucun scénario de `partie.feature` ni de `ecrans.feature` dans `en_attente.txt` à la fin du point 23 quinquies ; `clients` n'importe toujours ni `core` ni `server` (`lint-imports`).
*   **Mutation :** l'amendement ne crée aucun fichier dans `core` ni dans `schema` ; `clients/model.py`, `map_layout.py` et `texts.py` sont mutés sans plancher *(remplacé par l'amendement 2, voir le bloc « (amendement 2) » ci-dessous)*.
*   **Déterminisme :** la génération du monde donne le même monde sous `PYTHONHASHSEED=0` et `1` (test de propriétés du point 23 quater, par deux sous-processus) ; le rejeu de 100 000 ticks sous deux valeurs vient au volet C.
*   **Carte :** part des liens tracés et hauteur de la carte, mesurées par les tests de propriétés sur de nombreuses graines, publiées au compte rendu de M1 *(remplacé par l'amendement 2, voir le bloc « (amendement 2) » ci-dessous)*.
*   **Manuel :** la partie d'essai du point 23 sexies, et l'essai de la veille du point 23 quater.
*   **CI :** chaque pull request cite les liens des contrôles verts.

**(amendement 2)**

S'y ajoutent :

*   **Tests :** aucun scénario de `ecrans.feature` dans `en_attente.txt` à la fin du point 23 decies ; `clients` n'importe toujours ni `core` ni `server` (`lint-imports`).
*   **Mutation :** `clients/model.py`, `texts.py`, `palette.py`, `guide.py`, `force_layout.py` et `map_view.py` sont mutés sans plancher ; le score de `model.py` et de `texts.py` ne baisse pas ; `frames.py` et `textual_app.py` restent exclus.
*   **Carte :** aucun recouvrement dans la grille, et les croisements de liens, sur les graines 1 à 2 000, publiés au compte rendu de M1 ; le temps de rendu du point 28 bis.
*   **Manuel :** la partie d'essai du point 23 undecies.
*   **Critère de sortie :** pour les objectifs 12 et 17 à 19, la preuve est le verdict consigné, favorable ou non (point 23 undecies) ; le critère de sortie du niveau 1, §11, ne change pas.

*Drafted with EGM*
