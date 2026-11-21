# M1 : noyau déterministe et tranche 0 (document de niveau 2)

*   **Auteur :** Thomas (thom.bruyer)
*   **Statut :** Proposed (amendement 1 en revue ; le document était Approved depuis le 2026-11-08)
*   **Date :** 2026-11-02 ; mis à jour le 2026-11-06 (décisions du propriétaire sur le contenu du jeu ; corrections de la revue EGM, étapes 5 à 9) ; approuvé par le propriétaire le 2026-11-08 ; amendement 1 rédigé le 2026-11-12, en revue
*   **Niveau 1 :** [architecture-niveau-1.md](./architecture-niveau-1.md) (CUJ 1, CUJ 4, §1 à §7, §10, §11 ligne M1)
*   **Intentions reprises :** [RFC du brainstorm](./mmo-gestion-spatiale-ia.md), jalon « M1 – Tranche 0 ». Le niveau 1 fait foi en cas d'écart.
*   **Amendements :** amendement 1 du 2026-11-12 (un monde plus grand, un écran lisible, le temps comme ressource, la visibilité par proximité), voir le tableau ci-dessous. ADR liées : [0003](../adr/0003-observe-recoit-les-reglages.md), [0004](../adr/0004-fourchettes-de-la-tranche-0.md) et [0005](../adr/0005-visibilite-par-proximite.md).

Les titres de section (`##`), le statut et les intitulés du gabarit du plan (sous-titres, Type / Scope, Proposed Changes, Create / Modify / Delete) suivent le gabarit de conception d'EGM, en anglais, pour que les outils de revue s'y retrouvent. Tout le reste est en français.

**Chemins protégés nouveaux.** Un fichier nouveau ajouté à `.github/chemins-proteges.txt` dans la pull request protégée qui le crée compte comme protégé dans cette pull request. Un fichier qui existe déjà sans être protégé doit être protégé par une pull request antérieure avant d'être modifié dans une pull request protégée (d'où le plan détaillé, point 3 bis).

**Conventions de renvoi.** « Technical Plan, point N » désigne une section du Technical Plan de ce document. « Plan détaillé, point N » désigne un point du Detailed Implementation Plan de ce document. Un « point N » sans préfixe renvoie à la même partie du document que le passage qui le cite. Un renvoi au niveau 1 le dit toujours (« niveau 1, §2 »).

**Autres conventions.**
- Un *CUJ* (Critical User Journey) est un parcours utilisateur critique du niveau 1 *(remplacé par l'amendement 1 : un parcours utilisateur critique, défini par le niveau 1, CUJ 1 à 6, ou par ce document, CUJ A)* ; M1 reprend le CUJ 1 et le CUJ 4 sans les adapter *(remplacé par l'amendement 1 : le CUJ 1 est élargi par l'ADR 0004)*, et les scénarios du plan détaillé, points 20 et 24, les traduisent. **(amendement 1)** Le CUJ A est traduit par `tests/scenarios/ecrans.feature` (plan détaillé, point 23 ter).
- « Par `!` » veut dire que le propriétaire tape la commande dans Claude Code en la préfixant de `!`, ce qui l'exécute dans la session sous son propre nom.
- Un *site* est une station ou un gisement. Un *gisement* est l'entité du jeu où l'on mine ; « champ » ne désigne que les champs de données.
- Les deux machines sont l'*ordinateur portable* du propriétaire et le *PC d'entraînement*.

**Amendements.** Un amendement ajoute des passages sans jamais renuméroter les passages existants, qu'une trentaine de fichiers du dépôt citent. Un point inséré entre deux points existants prend le numéro du point qui le précède, suivi de « bis », « ter »… Un CUJ ou une alternative nouveaux prennent une lettre, à la suite des lettres existantes (CUJ A ; alternatives J à AA).

- **Préséance.** En cas de conflit dans ce document, un passage marqué par l'amendement N, sous l'une des formes de la légende ci-dessous, l'emporte sur le texte d'origine, que celui-ci soit marqué ou non, et un amendement plus récent l'emporte sur un plus ancien.
- **Légende des marques :**
  - « (amendement N) » : passage ajouté par l'amendement N ;
  - « (amendement N, réécrit) » : le passage d'origine est remplacé sur place, et sa version d'origine ne figure plus dans le document ;
  - « (amendement N, précisé) » : le passage d'origine reste vrai, et l'amendement le complète à la suite ;
  - « (amendement N, remplace / complète la ligne d'origine) » : dans un tableau, ligne nouvelle qui remplace ou complète une ligne gardée plus haut ;
  - « **Ajoutés par l'amendement N :** » : liste d'éléments ajoutés à la suite d'une liste d'origine ;
  - « **Risques ajoutés par l'amendement N :** » : tableau de risques ajouté à la suite du tableau d'origine ;
  - « (amendement N : …) » : marque en ligne dans un bloc de code ou dans une cellule de tableau, qui donne la nouvelle valeur ;
  - « **Proposed Changes (amendement N, ajout) :** » ou « **Proposed Changes (amendement N, remplacement) :** » : dans le plan détaillé, puce ajoutée à un point existant, qui complète ses puces d'origine, ou remplace celles qui portent une marque de remplacement ;
  - « *(remplacé par l'amendement N, voir …)* » : le passage d'origine est gardé mais ne vaut plus ; le renvoi donne le texte en vigueur ;
  - « *(remplacé par l'amendement N : …)* » : de même, mais le texte en vigueur suit les deux-points.
- **Portée des marques :**
  - une marque placée dans un titre couvre toute la section ;
  - une marque placée après un titre, après l'intitulé en gras d'un paragraphe ou après une phrase d'introduction couvre tout le paragraphe ou toute la liste qui suit ;
  - une marque seule sur sa ligne couvre tout ce qui suit, jusqu'au prochain titre ;
  - une marque d'ajout (« (amendement N) » ou « (amendement N, précisé) ») placée en tête d'une phrase, au milieu d'un paragraphe ou d'une puce, couvre cette phrase et la fin du paragraphe ou de la puce ;
  - placée ailleurs, une marque de remplacement ne couvre que la phrase ou le membre de phrase qui la précède.
- **Code livré.** Les volets A et B (plan détaillé, points 15 à 23) sont livrés. Le texte d'origine non marqué de ces points décrit le code fusionné ; l'amendement l'appelle « code d'origine ». La « tâche de relais » est la tâche de `__main__.py` qui transmet les mises à jour à l'hôte des PNJ (Technical Plan, point 7).

| N° | Date | Objet | Passages touchés | Dossier de revue |
| :-- | :-- | :-- | :-- | :-- |
| 1 | 2026-11-12 | un monde plus grand, un écran lisible, le temps comme ressource, la visibilité par proximité ; à la suite de la partie de test du 2026-11-11 | conventions ; Overview ; The Problem ; objectifs 5, 6 et 11 à 16 ; Non-Goals ; Open Questions ; introduction des CUJ, CUJ A ; Technical Plan, points 1, 2, 5, 6, 7, 7 bis, 8, 9, 11, 12, 13 ; introduction des alternatives, alternatives J à AA ; Risks & Mitigations ; Additional Resources ; Future Improvements ; plan détaillé, points 5, 17, 20, 22, 23, 23 bis à 23 sexies, 25, 26, 27, 28, 28 bis, 29, 32 bis ; Verification Plan | `docs/revues/2026-11-12-niveau-2-m1-noyau-amendement-1/` |


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

**(amendement 1)** L'amendement 1 change quatre choses dans M1, avant le volet C (rejeu, divergence, économie) :

1. **Le monde de la tranche 0 grandit.** La graine tire sa taille dans des fourchettes :
   - 8 à 12 systèmes reliés en graphe ;
   - 4 à 6 gisements, au moins deux par minerai ; une station et un gisement peuvent partager un système ;
   - 2 à 3 stations, chacune avec ses propres prix fixes, écrits dans les réglages ;
   - 3 à 5 PNJ, chacun avec un vaisseau.

   Ces fourchettes dépassent celles d'origine du CUJ 1 du niveau 1 : l'ADR 0004 les élargit.
2. **Le client devient un écran unique et lisible.** Il est fait de cadres indépendants : carte, vaisseau, stations, historique, barre d'état et alertes. Le rendu est très simple : du texte, des tableaux, des cadres, peu ou pas de couleurs. L'écran montre :
   - la carte en graphe ;
   - où se trouve chaque minerai (le stock des seuls gisements proches), et à quel prix chaque station le rachète ;
   - combien de ticks il reste avant la fin d'un trajet ou d'un minage ;
   - quels ordres attendent leur résultat ;
   - pourquoi un ordre a été refusé, en français, et où aller.

   Une alerte signale la fin d'un minage et l'arrivée à destination. Les touches fonctionnent sur un clavier AZERTY, sans Majuscule.
3. **Le temps devient une ressource.** Un saut entre deux systèmes voisins dure `jump_ticks` ticks (400 dans les valeurs initiales), soit 20 minutes à la période nominale de 3 s. Remplir une cargaison de 100 unités prend 100 ticks, soit 5 minutes. La vente reste instantanée. Pour donner ces durées au client, `observe` reçoit les réglages et en publie une partie dans l'observation : c'est un changement d'interface du niveau 1, qui passe par l'ADR 0003. En mode développement seulement (option `--dev`), on peut accélérer l'univers, le mettre en pause, ou avancer jusqu'à la prochaine alerte. Cette vitesse de l'univers se règle par la durée réelle d'un tick ; elle ne change pas la durée d'un saut en ticks, qui est une règle (`jump_ticks`).
4. **On ne voit que ce qui est proche.** Les vaisseaux d'autrui et le stock des gisements ne sont visibles que dans le système d'un des vaisseaux de l'acteur et les systèmes voisins (ADR 0005), en attendant des scanners qui porteront plus loin. La carte elle-même (systèmes, liens, emplacement des gisements et des stations, prix) reste visible partout.

L'amendement redimensionne aussi le test d'économie du volet C : les fenêtres passent de 1 000 à 10 000 ticks, et les bornes sont calculées à la régénération des références, à partir du cycle de chaque PNJ sur le monde de la partie de référence (graine 1).

## The Problem

Le niveau 1 fixe les interfaces et les invariants, mais aucun code ne les met encore en œuvre. Tant qu'un premier noyau n'existe pas, trois choses restent inconnues :
- **si les invariants tiennent sur un vrai tick.** Le déterminisme, la conservation de l'argent et des biens et la visibilité par champ de données n'ont été vérifiés que sur papier, et sur un banc d'essai simplifié (niveau 1, §2) ;
- **si la boucle de jeu fonctionne.** Extraire, transporter et vendre doit former une boucle que le propriétaire a envie de rejouer. C'est un jugement subjectif, que le niveau 1 assume ;
- **comment l'économie évolue sur la durée.** Sur 100 000 ticks, la masse monétaire, l'émission et la destruction doivent rester dans des fourchettes connues. Sans cela, on ne saura pas si une dérive future vient d'une règle ou d'un joueur IA.

Tous les jalons suivants reposent sur ce noyau. L'entraînement (M4) fait tourner `step` dans de nombreux processus en parallèle, le serveur persistant (M5) rejoue son journal, l'observabilité (M2) lit ses événements. Une erreur de format ou de déterminisme laissée à M1 se paierait plus tard en migrations, ou en joueurs IA entraînés sur un monde faux.

Le jalon est large : six livrables, et cinq contrôles obligatoires de plus (dont `imports`, qui tourne déjà sans être obligatoire). Le risque principal est donc l'exécution, pas la conception. Un agent de code sans mémoire doit pouvoir livrer chaque livrable à partir de ce document seul, sans décision ouverte : les noms et les signatures sont au Technical Plan, point 13.

**(amendement 1) La partie de test du 2026-11-11.** Le 2026-11-11, après la fusion du volet B, le propriétaire a joué la tranche 0 pendant 97 ticks, environ une minute et demie. Son verdict : « intéressant, pas encore fun ». Le « fun » est attendu des mécaniques des jalons suivants ; ce n'est pas l'objet de l'amendement. Quatre gênes, en revanche, l'empêchent de juger la boucle de jeu, ce que demande l'objectif 11 :

- **Le rythme est trop rapide.** L'écran change chaque seconde, le PNJ enchaîne ses cycles pendant que le joueur cherche quoi faire, et les événements passent inaperçus.
- **L'affichage est confus.** La carte est une simple liste de systèmes, on ne voit pas où est chaque minerai, l'historique défile, et l'état du vaisseau est dense.
- **Les touches sont peu claires.** Le choix du système se fait par un chiffre, qui demande Majuscule sur un clavier AZERTY.
- **Un refus est resté incompris.** Au tick 51, un ordre de minage a été refusé, parce que le minerai demandé n'avait pas de gisement dans ce système. Le client affichait le code anglais `no_deposit_for_ore`, sans dire où était ce minerai.

Le propriétaire veut un jeu plus lent, stratégique et réfléchi, où le temps compte : tout prend du temps, et l'on passera plus tard à l'échelle par plus de vaisseaux ou de plus gros, pas par des actions plus rapides. Il veut aussi, « sans rentrer dans l'excessif », un monde un peu plus grand : plus de nœuds, plus d'endroits où miner, plus de vaisseaux qui bougent, et plus de points de vente. Avec trois systèmes en ligne, une station et un PNJ, il n'y a ni choix de route, ni choix du lieu de vente, et presque rien ne bouge à l'écran. Enfin, il ne veut pas qu'on voie tout : un autre vaisseau, ou le stock d'un gisement, n'est visible qu'à proximité, dans le système d'un des vaisseaux de l'acteur ou un système voisin, en attendant des scanners qui porteront plus loin. C'est une décision de jeu : la détection deviendra une mécanique des jalons suivants, et M1 en pose la règle de base (ADR 0005). Elle a un prix assumé : on voit moins de PNJ bouger à l'écran.

Ralentir seulement la période de l'horloge ne suffit pas. Le jeu attendrait plus longtemps entre des décisions qui restent les mêmes, et le PNJ resterait aussi rapide en ticks. Les durées doivent donc être des règles : elles changent `rules_version`. La taille du monde est aussi une règle, puisque `world.generate` la tire de la graine. C'est le moment le moins coûteux de M1 pour ce changement : les références du volet C n'existent pas encore, et `RULES_REVISION` vaut 0.

Ces changements ont des conséquences, que l'amendement traite :
- **Le test d'économie ne vérifierait plus rien.** Sur la carte d'origine et avec les nouvelles durées, un cycle du PNJ (aller vers le gisement le plus lointain, minage, retour, vente) dure 1 701 ticks : chiffre obtenu par simulation, graine 1, deux PNJ. Une fenêtre de 1 000 ticks contiendrait donc zéro ou une vente par PNJ. Sur la carte agrandie, les cycles varient avec la graine : les bornes sont calculées à la régénération des références (plan détaillé, point 27).
- **Les scénarios protégés de `partie.feature` cassent.** Ils lisent les vrais réglages, et supposent la carte de la graine 1 (station dans `system_1`, `ore_a` dans `system_2`, `ore_b` dans `system_3`).
- **Le client ne connaît pas les durées.** Il ne voit que l'observation, et le niveau 1 interdit tout autre canal vers le joueur (niveau 1, §5).
- **Le PNJ doit savoir choisir parmi plusieurs gisements et plusieurs stations.** Sa politique change de version, en restant simple.

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
5. **(amendement 1, réécrit) L'économie reste dans ses fourchettes sur 100 000 ticks.** Sur la partie de référence, l'émission par motif, la destruction par motif et la croissance de la masse monétaire, **par fenêtre de 10 000 ticks**, restent dans les bornes du plan détaillé, point 27. Ces bornes sont calculées à la régénération des références, à partir du cycle de chaque PNJ sur le monde de la graine 1, sans lire les ventes de la partie. Les prix sont fixes à ce jalon.
   *Vérification :* le test `tests/economie/test_fourchettes.py`, lancé en CI par la tâche `rejeu`, rejoue le journal de la partie de référence et compare chaque fenêtre, sauf la première, aux bornes rangées dans `reference.json` ; il vérifie aussi que la destruction est égale à la somme des taxes de chaque vente, arrondies vers le haut. Le notebook marimo affiche les mêmes grandeurs, par la même fonction `window_stats` (plan détaillé, point 25).
6. **Tous les acteurs passent par la même porte.** Le client Textual et le PNJ reçoivent leurs observations de la seule fonction `observe`, et leurs ordres passent par la même réception, puis par `step`. Aucun champ de données caché n'apparaît dans une observation.
   *Vérification :* des tests de propriétés sur la visibilité ; les contrats d'imports interdisent à `clients` et `policies` d'importer `core`. **(amendement 1)** Les tests de propriétés couvrent aussi la classe proximité : un vaisseau d'autrui ou un stock de gisement hors de portée n'apparaît pas dans l'observation. La *portée* d'un acteur est le système d'un des vaisseaux de l'acteur et les systèmes voisins (Technical Plan, point 5).
7. **Tout ce qui persiste ou circule porte un numéro de version.** Le journal des ordres soumis, les instantanés, les événements, le protocole et les règles portent leurs champs de version (niveau 1, §3 et §7).
   *Vérification :* `tests/core/test_versions.py` et `tests/server/test_versions_journal.py` (plan détaillé, points 18 et 23) ; le contrôle de garde exige que `RULES_REVISION` augmente de un quand les références changent.
8. **Les contrôles de M1 deviennent obligatoires** (niveau 1, §10) : tests et scénarios ; rejeu sous deux `PYTHONHASHSEED` ; tests de propriétés ; contrats d'imports ; mutation sur les fichiers modifiés, scénarios compris (Technical Plan, point 10), avec un score jamais inférieur à celui du commit de base de la pull request. La suite canari et la mutation complète du noyau tournent chaque nuit sur `main`.
   *Vérification :* les cinq contrôles figurent dans la protection de `main` ; les essais du plan détaillé, point 32 bis, montrent qu'une pull request en échec sur chacun d'eux est refusée ; la suite canari échoue si l'un de ses bugs volontaires n'est pas attrapé.
9. **L'indicateur avancé est mesuré.** Les ticks par seconde de `step` et `observe`, sur un monde de la taille de ceux de l'entraînement, sont mesurés et publiés. Ils ne déclenchent rien (niveau 1, §2).
   *Vérification :* la mesure figure dans le compte rendu de M1, avec la commande qui l'a produite.
10. **Les identifiants du glossaire sont fixés.** Chaque terme marqué « à fixer au niveau 2 de M1 » reçoit son identifiant du code, et le glossaire est mis à jour.
    *Vérification :* plus aucune entrée du glossaire ne porte « à fixer au niveau 2 de M1 ».
11. **Le propriétaire valide la boucle de jeu.** Après avoir joué, il déclare que la boucle extraire, transporter, vendre lui convient. C'est une validation subjective, assumée par le niveau 1, §11. **(amendement 1, précisé)** Il la valide sur le client et le monde de l'amendement, en mode développement accéléré pour l'enchaînement des étapes du cycle (à la période nominale, un cycle dure de 5 minutes, pour un gisement dans le système d'une station, à plus d'une heure, pour un gisement à deux sauts : 85 minutes), et sur au moins un saut complet joué à la période nominale (20 minutes) pour le rythme.
    *Vérification :* sa décision, consignée dans le compte rendu de M1 ; **(amendement 1)** avec la graine et les paliers de vitesse joués.
12. **(amendement 1) Le propriétaire lit l'écran sans se perdre.** Après une partie, il déclare savoir à tout moment :
    - où est son vaisseau, et s'il est à l'arrêt, en route ou en minage ;
    - combien de ticks il reste avant la fin de son trajet ou de son minage ;
    - où se trouve chaque minerai, et à quel prix chaque station le rachète ;
    - quels ordres attendent leur résultat ;
    - pourquoi un ordre a été refusé.

    C'est un jugement subjectif, distinct de l'objectif 11.
    *Vérification :* sa décision, consignée dans le compte rendu de M1. Pour la part automatique, des tests du pilote de Textual, sur un terminal de 80 × 24 et sur un monde de 12 systèmes, vérifient pour chaque état du vaisseau que ces informations figurent à l'écran. Des tests avec `Game.advance` vérifient que chaque durée affichée est égale au nombre de ticks observé avant l'événement, quand aucun autre vaisseau ne mine le même gisement.
13. **(amendement 1) Le temps est une ressource, et les durées sont des règles.** Un saut dure `jump_ticks` ticks (400 dans les valeurs initiales). Remplir une cargaison vide prend `cargo_capacity` ÷ `mining_rate` ticks (100). La vente reste instantanée. Les durées sont en ticks ; les minutes ne sont qu'une estimation d'affichage, à la période nominale de 3 s.
    *Vérification :* un scénario sur les vrais réglages : les durées lues dans `observation.public_tunables` sont celles de `tunables.toml`, un trajet observé dure `jump_ticks` ticks, et la cargaison n'est pleine qu'au bout de `cargo_capacity` ÷ `mining_rate` ticks de minage. La valeur 400 n'est vérifiée par aucun test : `tunables.toml` fait foi ; `rules_version` change avec les réglages, et `RULES_REVISION` reste à 0.
14. **(amendement 1) Le joueur connaît les durées par l'observation seule.** `observe` reçoit les réglages et publie, dans l'observation, une vue des réglages publics : `jump_ticks` et `mining_rate`. La capacité est déjà dans la vue du vaisseau, et la taxe dans l'événement de vente. Aucun autre canal n'apporte d'information du jeu au joueur. L'ADR 0003 change l'interface du niveau 1.
    *Vérification :* les tests de visibilité s'étendent à la nouvelle vue, et vérifient qu'aucun autre réglage n'apparaît dans l'observation ; `protocol_version` passe à 2.
15. **(amendement 1) L'univers s'accélère en mode développement.** Lancée avec `--dev`, une partie locale offre des paliers de vitesse de l'univers, la pause, et « avancer jusqu'à la prochaine alerte ». Sans `--dev`, l'univers tourne à la période nominale, ou à celle de l'option de lancement `--periode`, qui sert aussi aux essais, sans touche de vitesse. La vitesse de l'univers n'est pas celle du vaisseau : un saut dure toujours `jump_ticks` ticks. Rien de cela ne passe par le protocole, le journal des ordres ou les règles : seule la période de l'horloge change, et chaque changement est enregistré dans le dossier de la partie. En mode avec horloge, les PNJ reçoivent leurs mises à jour par la tâche de relais : aux paliers rapides (×100 et ×1000), une décision peut entrer un ou plusieurs ticks plus tard qu'au tick suivant. La partie jouée dépend donc de la vitesse ; le rejeu de son journal, lui, redonne toujours les mêmes empreintes.
    *Vérification :* un test rejoue le journal d'une partie jouée en accéléré et retrouve ses empreintes ; `speed.jsonl` garde la période initiale et chaque changement.
16. **(amendement 1) Le monde est plus grand, et sa taille vient de la graine.** `world.generate` tire, de façon déterministe, 8 à 12 systèmes reliés en un graphe connexe, 4 à 6 gisements (au moins deux par minerai), 2 à 3 stations, et `__main__.py` crée 3 à 5 PNJ (nombre tiré par `core.world.npc_count`). Une station et un gisement peuvent partager un système. Chaque station rachète chaque minerai à son prix fixe, lu dans les réglages. L'ADR 0004 élargit les fourchettes du CUJ 1.
    *Vérification :* des tests de propriétés sur de nombreuses graines (tailles dans les fourchettes, graphe connexe, au moins deux gisements de chaque minerai, même monde pour la même graine sous deux `PYTHONHASHSEED`) ; le scénario du CUJ 1 joue sur un monde généré, sans supposer sa forme.

## Non-Goals

*   **Le marché entre joueurs, les corporations, les permissions, le combat et les pirates.** Ils arrivent à M6. La phase « combat » existe dans l'ordre des phases du tick (niveau 1, §2), mais reste vide à M1.
*   **La perte de vaisseau.** Aucun vaisseau n'est détruit à M1 (Technical Plan, point 1).
*   **Les prix variables.** La station rachète chaque minerai à un prix fixe *(remplacé par l'amendement 1 : chaque station rachète chaque minerai à son propre prix fixe)*.
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
*   **La disposition définitive de l'écran.** L'amendement fixe une première disposition simple, faite de cadres indépendants. Elle n'est pas figée.
*   **La souris, les thèmes de couleur, le tutoriel et le mode rejeu du client** (M3).
*   **Une flotte : plusieurs vaisseaux pour un même joueur.** Chaque personnage, humain ou PNJ, a un vaisseau. Il n'y a pas non plus de types de vaisseaux, de lasers de minage ni de distances variables. Plus tard, la durée d'un minage dépendra du laser du vaisseau et de sa capacité, et celle d'un saut de sa vitesse et de la distance. À M1, tous les sauts entre voisins ont la même durée.
*   **Les dommages.** Il n'y en a pas à M1. Les alertes de dommages viendront avec eux.
*   **D'autres alertes que la fin du minage et l'arrivée à destination.** La table des alertes sera retravaillée plus tard (ventes, refus, dommages).
*   **Un marché** (M6). Plus tard, le marché fixera les prix selon la nature du minerai et la demande, et non selon la distance.
*   **Un PNJ plus habile.** La politique `scripted_miner` reste simple. Sa nouvelle version choisit parmi plusieurs gisements et plusieurs stations par une règle fixe, sans tenir compte du temps de trajet. Plus tard, les PNJ prendront des décisions individuelles, voire collectives, par exemple miner un minerai peu rentable parce que leur corporation en a besoin (M6).
*   **Un ordre « arrêter » ou un changement de route pendant un saut.** Ce serait un changement des règles.
*   **La reprise d'une partie interrompue** (M5).
*   **La période ou l'accélération transmises au joueur par le protocole ou l'observation.** La période n'est pas une donnée du jeu.
*   **Une hausse de `RULES_REVISION`.** Il passera de 0 à 1 à la première création des références, au volet C.

## Open Questions

Ces questions sont posées au propriétaire une à une pendant la rédaction. Une question tranchée quitte cette liste et rejoint le Technical Plan.

Le propriétaire a confirmé, le 2026-11-08, toutes les lignes du Technical Plan, point 1, marquées « proposition de l'agent de code ».

**(amendement 1)** Aucune question ouverte. La mise en veille de l'ordinateur portable, qui n'a d'effet ni sur les règles ni sur le rejeu, est un risque, vérifié par un essai au plan détaillé, point 23 quater.

## Critical User Journeys (CUJs)

**(amendement 1)** Le CUJ 1 et le CUJ 4 du niveau 1 sont inchangés, à l'élargissement des fourchettes près (ADR 0004). Ce parcours précise ce que le propriétaire vit sur le client de l'amendement.

### CUJ A : un cycle complet, lu sur l'écran (amendement 1)

*   **Given :** une partie locale vient de démarrer. Le vaisseau du propriétaire est à une station, cargaison vide. L'écran montre la carte en graphe, les gisements de chaque minerai (stock connu pour les seuls gisements proches), les prix de chaque station, les vaisseaux proches (dans son système et les systèmes voisins) et la barre d'état (tick, solde, graine ; en mode développement, la vitesse de l'univers).
*   **When :** il choisit un gisement, y envoie son vaisseau en choisissant sa destination dans une liste, confirme, puis (en mode développement) accélère l'univers. À l'arrivée, il mine ; à la fin du minage, il va à la station de son choix et vend.
*   **Then :**
    - avant de confirmer un déplacement, il voit son coût : nombre de sauts, ticks, et une estimation en minutes à la période nominale ;
    - pendant le trajet, l'écran montre « en route », le système visé et les ticks restants ;
    - une alerte, qu'il acquitte par Entrée, signale l'arrivée à destination ; une autre signale la fin du minage ;
    - si un ordre est refusé, le message dit pourquoi, en français, et où aller ;
    - la vente affiche le prix de la station, le paiement et la taxe ;
    - la vitesse de l'univers ne change pas les règles : un saut dure toujours `jump_ticks` ticks ; rejouée depuis son journal, la partie redonne les mêmes empreintes.


--------------------------------------------------------------------------------

## Technical Plan (Architecture)

**(amendement 1) Vue d'ensemble.** Chaque passage marqué « (amendement 1) » complète le point du Technical Plan où il se trouve ; un passage qui remplace un texte d'origine le dit, et le texte d'origine porte la marque de remplacement. Rien n'est renuméroté : le point 7 bis est nouveau, les autres passages s'insèrent dans les points existants avec la marque « (amendement 1) ».

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

**Règle de rédaction (propriétaire, 2026-11-02).** M1 fait le minimum possible **dans le cadre déjà fixé** par le niveau 1. Ce document ne réduit aucune exigence du niveau 1, n'en ajoute aucune sauf le seuil de mutation ci-dessous *(remplacé par l'amendement 1 : il en ajoute aussi d'autres, les objectifs 12 à 16)*, et ne redéfinit rien *(remplacé par l'amendement 1 : les ADR 0003 à 0005 changent le niveau 1)* : chaque contrôle obligatoire de M1 est livré. Quand une question de contenu du jeu a plusieurs réponses, la plus petite qui respecte le niveau 1 est retenue. **(amendement 1, précisé)** Les décisions du propriétaire du 2026-11-12 priment aussi sur cette règle du minimum : elles vont au-delà (objectifs 12 à 16).

**Décisions sur le contenu du jeu (propriétaire, 2026-11-06).** Après la rédaction, pendant la revue de l'univers et de la conception du jeu (documents hors de `main`), le propriétaire a tranché quatre points du contenu de la tranche 0. Ils priment sur la règle du minimum et figurent dans le tableau ci-dessous (lignes datées du 2026-11-06, sans autre mention). Aucun ne change le niveau 1.

**Propositions de l'agent de code (2026-11-06), confirmées par le propriétaire le 2026-11-08.** Pendant la revue EGM de ce document, le propriétaire a délégué à l'agent de code les choix techniques que la revue a fait apparaître. Ces lignes portent la mention « proposition de l'agent de code » ; le propriétaire les a toutes confirmées le 2026-11-08, au passage à Approved.

| Question | Décision | Raison |
| :-- | :-- | :-- |
| Perte de vaisseau | aucune à M1 | le niveau 1 ne l'exige pas ; l'ajouter changerait l'invariant 3 du niveau 1, §4 |
| Noms et identifiants | dans l'état, chaque entité a un identifiant entier, propre à sa table, à partir de 1 ; les scénarios et le client affichent des libellés neutres tirés de l'identifiant (Technical Plan, point 13) | le niveau 1, §2, exige des tables indexées par un identifiant entier ; `docs/noms-valides.md` est vide ; les exemples de `CLAUDE.md` (`station_a`, `ore_1`) ne sont que des exemples |
| Taille de la tranche 0 | 3 systèmes, 2 minerais, 1 station, 1 vaisseau pour le propriétaire, 1 PNJ *(remplacé par l'amendement 1, voir la ligne « Taille de la tranche 0 (amendement 1) » de ce tableau)* | le bas des fourchettes du niveau 1, CUJ 1 |
| Rythme du temps | une horloge du serveur fait avancer les ticks ; sa période est un paramètre du serveur, hors des règles | le niveau 1, §2, ordonne chaque tick autour de la réception des ordres (« reçus avant le début du tick T+1 »), ce qui suppose des ticks cadencés par le serveur ; voir l'alternative C |
| Preuve sur le PC d'entraînement | le propriétaire lance la commande de rejeu sur le PC d'entraînement, à la fin du jalon, et sa sortie va dans le compte rendu de M1 | seul le propriétaire a accès à cette machine ; aucune adresse ni aucun identifiant n'entre dans le dépôt |
| Fourchettes économiques | les fourchettes portent sur l'émission par motif, la destruction par motif et la croissance de la masse monétaire, **par fenêtre de 1 000 ticks** ; les bornes sont au plan détaillé, point 27 *(remplacé par l'amendement 1, voir le Technical Plan, point 9 : 10 000 ticks)* | à prix fixes, la station paie chaque vente par une émission et seule la taxe détruit de l'argent : la masse monétaire ne peut que croître, et seule sa croissance par fenêtre peut rester dans une fourchette ; par l'invariant 2, cette croissance vaut l'émission moins la destruction |
| Point de départ du jeu | un module à la racine du paquet, `fourx/__main__.py`, assemble le serveur en mémoire et le client | `clients` ne peut pas importer `server`, ni `server` importer `clients` (niveau 1, §1) ; seule la racine du paquet peut les relier, et les contrats d'imports ne la contraignent pas |
| Outil de mutation | `mutmut` 3.8.0 (choix du propriétaire) | essayé sous Python 3.15 avec pytest 9.1.1 le 2026-11-02 : fonctionne ; cassé par pytest 9.2.0, donc pytest est plafonné sous 9.2 et toute montée de pytest est vérifiée avec `mutmut` avant d'être acceptée |
| Mode rejeu du client | son identifiant est fixé ici ; il est construit à M3, avec la vidéo rendue depuis un rejeu | aucun critère de sortie de M1 ne l'exige ; l'outil de divergence suffit au CUJ 4 |
| Station (2026-11-06) | une structure du jeu, pas un personnage : sans `actor_id` ni portefeuille ; elle paie chaque vente par une émission | décision du propriétaire ; le niveau 1, CUJ 1, dit « station PNJ » : la formule désigne ici une structure dont le comportement est fixé par les règles, pas un acteur |
| Gisements (2026-11-06) | finis : chaque gisement a un stock, qui baisse au minage et revient à `deposit_stock` tous les `regen_ticks` ticks (régénération d'un gisement) | décision du propriétaire : un stock large, qui finit par se vider, oblige les mineurs, surtout quand ils viennent à plusieurs, à changer de gisement ; dans le monde en ligne, la régénération d'un gisement a lieu environ chaque semaine. À M1, avec les valeurs du plan détaillé, point 17, la partie de référence ne vide aucun gisement : le stock n'a aucun effet sur les fourchettes *(remplacé par l'amendement 1 : un gisement peut se vider, surtout s'il partage son système avec une station ; la partie de référence peut alors exercer l'épuisement et la régénération, Technical Plan, point 9)*, et l'épuisement comme le départage sont vérifiés par les scénarios et les tests de propriétés |
| Visibilité de la vente (2026-11-06) | le vendeur voit sa vente, son paiement et sa taxe dans un événement privé ; les écritures du registre et les compteurs d'émission et de destruction relèvent de l'administration ; aucun acteur ne voit le portefeuille d'un autre | décision du propriétaire (personne ne voit le compte en banque d'un autre, ni l'argent créé par le jeu) ; le niveau 1, CUJ 1, exige que le client affiche le paiement |
| Argent de départ (2026-11-06) | aucun : tout portefeuille commence à zéro ; le vaisseau de départ est une dotation, sans écriture | décision du propriétaire |
| Arrondi de la taxe | vers le haut, au profit du compte de destruction | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : arrondie vers zéro, une taxe s'annulerait sur des ventes découpées en petits lots |
| Seuil de mutation | le contrôle `mutation` échoue si un fichier nouveau de `core` ou de `schema` a moins de 80 % de mutants tués ; la mutation complète du noyau, de nuit, aussi ; le seuil est revu au plan détaillé, point 28 bis | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, seule exigence ajoutée au niveau 1 *(remplacé par l'amendement 1 : l'amendement en ajoute d'autres, voir la règle de rédaction)* : à M1, tous les fichiers sont nouveaux, donc la règle du niveau 1 (« jamais inférieur au score de `main` ») ne vérifie rien sans plancher ; il est limité à `core` et `schema`, où les mutants équivalents sont rares, et non au code d'entrées et de sorties |
| Résultats d'ordre | `State` garde les événements et les résultats d'ordre du dernier tick ; la réception applique la validation sans état (niveau 1, §2) ; un ordre qu'elle refuse est quand même journalisé, avec son code de refus, et `step` le refuse avec ce code, sans autre contrôle | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, dans le cadre du niveau 1, §2 (la réception fait les contrôles sans état, `step` ceux qui dépendent de l'état) : `observe` ne lit que l'état et le joueur n'a pas d'autre canal que l'observation (niveau 1, §5) ; le refus de la réception doit donc passer par le journal, puis par `step`, pour arriver dans l'observation et être reproduit au rejeu |
| Ordres d'un même tick | un seul ordre examiné par vaisseau et par tick, celui de plus petit numéro, comme pour le quota ; les autres sont refusés (« ordre remplacé ») ; tout ordre sur un vaisseau en route est refusé | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : sinon deux ventes validées contre le même état pourraient vendre plus que la cargaison (invariant 3) |
| Partie de référence | jouée une fois par deux PNJ *(remplacé par l'amendement 1, voir le Technical Plan, point 9 : `npc_count(1, réglages)` PNJ)* à la régénération des références ; son journal des ordres soumis est exporté en JSONL versionné, avec ses empreintes, dans `tests/references/` ; le contrôle `rejeu` l'importe et le rejoue par `step` seul, avec l'outil de rejeu de `tools` | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : sinon un changement du PNJ ou du serveur, sans changement de règle, changerait les empreintes et ferait monter `rules_version`, que M4 enregistre et que M5 compare au déploiement |
| Concurrence | une seule boucle `asyncio` : l'horloge est une tâche de cette boucle, à côté de Textual ; un mode sans horloge, synchrone, sert aux tests, aux outils et à la partie de référence | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : Textual tourne déjà sur `asyncio`, et le transport WebSocket de M3 aussi |
| Tâche `tests-outillage` | inchangée jusqu'au palier 4 ; au palier 4, limitée à `tests/outillage`, quand la tâche `tests` devient obligatoire | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : le document de M0 prévoyait que `tests-outillage` « devient `tests` » ; renommer un contrôle obligatoire bloquerait toute fusion entre la pull request qui le renomme et la commande de protection ; jusqu'au palier 4, `tests-outillage` lance toute la suite et garde l'échec attendu des scénarios en attente dans un contrôle obligatoire (niveau 2 de M0) |
| Relecture de la protection | une tâche de nuit relit la protection de `main` par la route `GET /repos/EZPK/4X/branches/main`, avec le `GITHUB_TOKEN` en lecture seule (palier 4) | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, qui tient l'engagement du document de M0 : cette route ne demande aucun droit d'administration ; lue sans jeton le 2026-11-06, elle renvoie `protected`, `required_status_checks.enforcement_level` (`everyone`) et la liste des contrôles exigés ; `strict`, `allow_force_pushes` et `allow_deletions` n'y figurent pas et restent vérifiés à la main (plan détaillé, point 31) |
| Fichiers de configuration du dépôt | `pyproject.toml`, `uv.lock` et `.gitignore` deviennent des chemins protégés, au palier 1 | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08, qui revient sur l'alternative K du document de M0 (`pyproject.toml` non protégé) : la pull request protégée du palier 2 doit les modifier, or une pull request protégée ne contient que des chemins protégés (`CLAUDE.md`) ; une table `[tool.mutmut]` dans `pyproject.toml` masquerait aussi la configuration protégée de `setup.cfg`. Conséquence : toute nouvelle dépendance passe ensuite par une pull request protégée |
| Copie de référence de la protection dans le hook | au palier 4, le propriétaire met à jour `REFERENCE_PROTECTION` de `.claude/hooks/garde_commandes.py` avec la nouvelle liste des contrôles, selon la procédure de `CLAUDE.md` | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08 : `tests/outillage/test_garde_commandes.py` exige que `.github/protection-main.json` soit égal à cette copie ; l'agent de code n'édite pas `.claude/` |
| Taille de la tranche 0 (amendement 1, remplace la ligne d'origine) | tirée par la graine : 8 à 12 systèmes, 4 à 6 gisements, 2 à 3 stations, 2 minerais, 3 à 5 PNJ ; 1 vaisseau par personnage | décision du propriétaire (2026-11-12) : plus de nœuds, d'endroits où miner, de vaisseaux qui bougent et de points de vente, « sans rentrer dans l'excessif » ; ADR 0004 |
| Rythme du temps (amendement 1, complète la ligne d'origine) | les durées sont des règles, en ticks : `jump_ticks` ticks par saut (400 dans les valeurs initiales), `cargo_capacity` ÷ `mining_rate` ticks pour remplir une cargaison vide (100) ; période nominale de l'horloge : 3 s | décision du propriétaire : le temps est une ressource ; les minutes ne sont qu'une estimation d'affichage |
| Réglages publics (amendement 1) | `observe` reçoit les réglages et publie `jump_ticks` et `mining_rate` dans l'observation | décision du propriétaire ; le niveau 1 interdit tout autre canal vers le joueur ; ADR 0003 |
| Visibilité des autres vaisseaux (amendement 1) | par proximité : un vaisseau d'autrui, et le stock d'un gisement, ne sont visibles que dans le système d'un des vaisseaux de l'acteur ou dans un système voisin ; d'un vaisseau d'autrui, on ne voit que l'identifiant, le détenteur, le système et la capacité | décision du propriétaire ; plus tard, des scanners porteront plus loin ; ADR 0005 |
| Accélération de l'univers (amendement 1) | en mode développement seulement (`--dev`) : paliers de vitesse, pause, « avancer jusqu'à la prochaine alerte », par une fonction de rappel locale ; rien dans le protocole, le journal ou les règles | décisions du propriétaire (2026-11-12) : utile au développement et aux essais ; en partie normale, l'univers tourne à son rythme ; ce n'est pas l'alternative C (ticks avancés à la demande d'un joueur, sur un serveur partagé) ; la vitesse de l'univers (secondes par tick) n'est pas celle du vaisseau (ticks par saut, une règle) |
| PNJ (amendement 1) | `scripted_miner` version 2 (règle au point 7) ; en mode avec horloge, la tâche de relais lui transmet les mises à jour | décisions du propriétaire ; la politique reste simple et ignore le temps de trajet |
| Colocalisation (amendement 1) | une station et un gisement peuvent partager un système | décision du propriétaire (2026-11-12) : un gisement dans le système d'une station s'épuise vite, et l'épuisement oblige joueurs et PNJ à aller miner ailleurs ; voir l'alternative AA |
| Prix des stations (amendement 1) | `station_ore_prices` = [[10, 15], [12, 12], [8, 18]] | proposition de l'agent de code, confirmée par le propriétaire le 2026-11-12 ; la station 1 garde les prix d'origine |

### 2. Les règles de la tranche 0

**La carte.** Trois systèmes, `system_1` à `system_3`, reliés en chaîne dans l'ordre de leurs identifiants *(remplacé par l'amendement 1, voir la génération du monde, plus bas dans ce point)*. La graine du monde fixe le système de chaque site (plan détaillé, point 17, `world.py`) : la station, le gisement de `ore_a` et le gisement de `ore_b` sont chacun dans un système différent *(remplacé par l'amendement 1, voir la génération du monde, plus bas dans ce point)*. Un saut vers un système voisin dure `jump_ticks` ticks. Chaque gisement a un stock : il commence à `deposit_stock` unités, baisse de ce qui est extrait, et revient à `deposit_stock` aux ticks multiples de `regen_ticks` (phase de règlement). Un gisement vide ne rend plus rien jusqu'à sa régénération.

**Le placement des sites.** *(remplacé par l'amendement 1, voir la génération du monde, plus bas dans ce point)* Le tirage borné (Technical Plan, point 4) donne, pour (graine du monde, tick 0, entité 0, motif du tirage « carte »), un nombre de 0 à 5 : c'est le rang, dans l'ordre lexicographique, d'une des six permutations de (`system_1`, `system_2`, `system_3`) ; la permutation donne, dans l'ordre, le système de la station, du gisement de `ore_a` et du gisement de `ore_b`.

**Les entités** (types au Technical Plan, point 13).

| Entité | Champs de données principaux |
| :-- | :-- |
| système | identifiant, voisins |
| gisement | identifiant, système, minerai, stock |
| station | identifiant, système, prix de rachat de chaque minerai (copiés de `ore_prices` *(remplacé par l'amendement 1 : de la ligne k de `station_ore_prices`)* à la génération du monde ; une structure du jeu : ni acteur ni portefeuille) |
| acteur | identifiant (`id`, l'`actor_id` des formats), type d'acteur (`kind`, l'`actor_kind` des formats), budget d'actions |
| vaisseau | identifiant, acteur détenteur, système, activité (à l'arrêt, en route, en minage), route restante et ticks avant le prochain saut, cargaison par minerai, capacité |
| registre | comptes et leurs soldes, écritures du tick, compteurs cumulés d'émission et de destruction par motif (Technical Plan, point 3) |
| dernier tick | événements et résultats d'ordre produits par le dernier `step` |

**Les ordres.** Les codes de refus d'une ligne sont examinés de gauche à droite : le premier qui s'applique est retenu.

| Catégorie | Ordre | Effet | Refusé si (dans cet ordre) |
| :-- | :-- | :-- | :-- |
| joueur | déplacer un vaisseau vers un système | calcule le plus court chemin (parcours en largeur, voisins par identifiant croissant) et met le vaisseau en route | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, système inconnu, déjà sur place |
| joueur | miner un minerai | le vaisseau extrait à chaque tick, jusqu'à ce que la cargaison soit pleine ou que le gisement soit vide (il passe alors à l'arrêt), ou qu'un autre ordre remplace son activité | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, pas de gisement de ce minerai dans le système, gisement vide, cargaison pleine |
| joueur | vendre une quantité d'un minerai | la station rachète au prix fixe ; la taxe est prélevée ; le vaisseau passe à l'arrêt | vaisseau inconnu, vaisseau d'un autre acteur, vaisseau en route, vaisseau hors du système de la station *(remplacé par l'amendement 1 : aucune station dans le système du vaisseau)*, quantité nulle ou négative, quantité supérieure à la cargaison |
| administration | créer un personnage | crée l'acteur, son portefeuille personnel et un vaisseau vide, à l'arrêt, dans le système de la station *(remplacé par l'amendement 1, voir « Système de départ » plus bas dans ce point)* | — (émis par le serveur seulement) |

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

**Le départage.** La seule égalité possible à M1 est celle de plusieurs vaisseaux sur un gisement dont le stock ne suffit pas. Chaque vaisseau concerné reçoit un tirage à clé sur (graine du monde, tick, identifiant du vaisseau, motif du tirage « minage ») ; les vaisseaux sont servis par tirage croissant, puis par identifiant croissant en cas d'égalité des tirages. La station rachète sans limite : aucune vente n'est donc départagée.

**Les réglages.** Toutes les valeurs vivent dans `tunables.toml`, sous les noms du type `Tunables` (Technical Plan, point 13) : `jump_ticks`, `mining_rate`, `cargo_capacity`, `ore_prices` *(remplacé par l'amendement 1, voir le tableau des réglages, plus bas dans ce point : `station_ore_prices`)*, `tax_rate_bp` (taux de taxe en points de base), `deposit_stock`, `regen_ticks`, `budget_regen`, `budget_max`. Leurs valeurs sont au plan détaillé, point 17 *(remplacé par l'amendement 1 : les valeurs initiales sont au tableau des réglages, plus bas dans ce point)*. Le serveur lit ce fichier et passe les réglages à `step` ; le noyau ne lit aucun fichier. `world.generate` copie `ore_prices` dans la station *(remplacé par l'amendement 1 : chaque station reçoit sa ligne de `station_ore_prices`)* : pendant la partie, le prix qui fait foi est celui de la station, et il est public, pour que le client et la politique le voient.

**(amendement 1)**

**Génération du monde (`world.generate`).** Chaque tirage est `keyed_below(graine, 0, entité, motif, n)` (Technical Plan, point 4), avec l'entité et le motif donnés à chaque étape ; deux tirages n'ont jamais la même clé. Un nombre tiré « entre a et b » vaut a + `keyed_below`(…, b − a + 1). Chaque liste de candidats est triée par identifiant avant le tirage : le même monde sort de la même graine sous tout `PYTHONHASHSEED`.

1. **Nombre de systèmes** N, entre `systems_min` et `systems_max` (8 et 12) : entité 0, motif `"world_size"`.
2. **Arbre.** Pour k = 2 à N, le système k se relie à un système déjà placé, tiré parmi ceux qui ont moins de `max_neighbors` voisins (4) : entité k, motif `"tree"`. Le plafond garde la carte dessinable.
3. **Liens en plus.** Leur nombre L est tiré entre 1 et `extra_links_max` (3) : entité 0, motif `"extra_link_count"`. Le lien i (i = 1 à L) relie une paire de systèmes non voisins, tous deux sous le plafond, tirée parmi toutes les paires triées : entité i, motif `"extra_links"`. S'il ne reste aucune paire, on s'arrête.
4. **Stations.** Leur nombre S est tiré entre `stations_min` et `stations_max` (2 et 3) : entité 0, motif `"station_count"`. La station i (i = 1 à S) est placée parmi les systèmes qui n'ont pas encore de station : entité i, motif `"stations"`. La station k (identifiant k) rachète aux prix de la ligne k de `station_ore_prices`.
5. **Gisements.** Leur nombre G est tiré entre `deposits_min` et `deposits_max` (4 et 6) : entité 0, motif `"deposit_count"`. Le gisement i (i = 1 à G) est placé parmi les systèmes qui n'ont pas encore de gisement : entité i, motif `"deposits"`. Le gisement k porte le minerai 1 (`ore_a`) si k est impair et le minerai 2 (`ore_b`) sinon, donc au moins deux gisements de chaque minerai. Un système peut avoir une station et un gisement : c'est voulu (colocalisation, alternative AA). Il a au plus une station et au plus un gisement.
6. **Nombre de PNJ.** `npc_count(graine, réglages)` le tire entre `npc_min` et `npc_max` (3 et 5) : entité 0, motif `"npc_count"`. Ce n'est pas un champ de l'état : `__main__.py` crée les PNJ par des ordres d'administration au tick 1, comme dans le code d'origine. La fonction vit dans `core.world` parce que c'est un tirage de la graine du monde, comme la génération.

**Déplacement.** Inchangé : route la plus courte (`plus_court_chemin`, voisins par identifiant croissant), un saut tous les `jump_ticks` ticks. Seule la valeur change : 400 dans les valeurs initiales.

**Minage.** Inchangé, au débit `mining_rate` = 1 unité par tick. Le gisement visé est celui du système du vaisseau, s'il porte le minerai demandé. La durée pour remplir une cargaison vide est `cargo_capacity` ÷ `mining_rate` = 100 ticks.

**Vente.** Elle se fait à la station du système du vaisseau, au prix de cette station. Sans station dans le système, l'ordre est refusé (`NOT_AT_STATION`). La taxe est inchangée.

**Système de départ.** Le vaisseau d'un nouveau personnage d'identifiant *n* démarre à la station de rang `rem_trunc(n − 1, S)`, les stations étant triées par identifiant (rang 0 : la station d'identifiant le plus petit). Le propriétaire, créé le premier, part de la station 1 ; les PNJ se répartissent sur les stations.

**Réglages (`tunables.toml`).** `tunables.toml` fait foi (niveau 1). Le tableau donne les valeurs initiales de l'amendement ; une valeur changée plus tard ne change que `tunables.toml`.

| Réglage | Avant | Après | Effet |
| :-- | :-- | :-- | :-- |
| `jump_ticks` | 5 | 400 | 20 min par saut à 3 s |
| `mining_rate` | 10 | 1 | 100 ticks pour remplir une cargaison vide |
| `cargo_capacity` | 100 | 100 | inchangé |
| `ore_prices` | [10, 15] | supprimé | remplacé par `station_ore_prices` |
| `station_ore_prices` | — | [[10, 15], [12, 12], [8, 18]] (proposition de l'agent de code, confirmée par le propriétaire le 2026-11-12) | autant de lignes que `stations_max` ; la station k prend la ligne k |
| `tax_rate_bp` | 1000 | 1000 | inchangé |
| `deposit_stock` | 20 000 | 20 000 | inchangé |
| `regen_ticks` | 1 000 | 10 000 | aligné sur les fenêtres d'économie ; à 1 000, plus court qu'un aller-retour, il n'avait plus d'effet ; un gisement vidé redevient plein au plus tard 10 000 ticks après |
| `budget_regen`, `budget_max` | 1, 10 | 1, 10 | inchangés : avec un ordre par saut, le budget ne limite personne ; il resservira avec plusieurs vaisseaux |
| `systems_min`, `systems_max` | — | 8, 12 | fourchettes de l'ADR 0004 |
| `deposits_min`, `deposits_max` | — | 4, 6 | idem |
| `stations_min`, `stations_max` | — | 2, 3 | idem |
| `npc_min`, `npc_max` | — | 3, 5 | idem |
| `extra_links_max` | — | 3 | liens qui créent des boucles |
| `max_neighbors` | — | 4 | plafond de voisins, pour la carte à l'écran |

Le décodage vérifie en plus : chaque minimum ne dépasse pas son maximum ; `station_ore_prices` a au moins `stations_max` lignes, chacune de 2 prix positifs ; `deposits_min` ≥ 4 (deux gisements par minerai) ; `systems_min` ≥ `deposits_max` et ≥ `stations_max` (assez de systèmes distincts) ; `max_neighbors` ≥ 2 (sinon l'arbre n'a plus de candidat dès le troisième système) ; `extra_links_max` ≥ 1 (le nombre de liens en plus est tiré à partir de 1) ; `npc_min` ≥ 1.

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
- **Résultat d'ordre :** acteur destinataire (celui du point de connexion ; `None` pour un ordre du serveur, dont le résultat n'est observé par personne), identité de l'ordre, accepté ou code de refus, texte, budget restant (niveau 1, §5). Chaque ordre examiné par `step` reçoit un résultat.
- **Observation :** le tick, l'état visible pour l'acteur, les événements du dernier tick qui lui sont visibles, et ses résultats d'ordre *(remplacé par l'amendement 1 : et la vue des réglages publics, voir ci-dessous)*. `observe` lit tout cela dans l'état (table « dernier tick ») *(remplacé par l'amendement 1 : et dans les réglages qu'il reçoit, ADR 0003)*.
- **Visibilité.** Chaque champ de données des entités de l'état déclare sa classe de visibilité par `Annotated[T, msgspec.Meta(extra={"visibility": ...})]` ; `observe` relit ces métadonnées par `msgspec.inspect.type_info` (mécanisme essayé sur `msgspec` 0.22.0 le 2026-11-06 : la métadonnée revient comme `Metadata` avec son `extra`). Chaque type d'événement a une seule classe. « Privé » veut dire visible par le seul acteur qui détient l'entité. Les vues de l'observation reprennent les noms des champs de données de l'état. À M1 :
  - publics : les systèmes et leurs voisins, les sites, le minerai et le stock *(remplacé par l'amendement 1 : le stock est de classe proximité)* des gisements, les prix de rachat de la station, l'identifiant, le détenteur, le système et la capacité des vaisseaux *(remplacé par l'amendement 1, voir ci-dessous : classe `NEARBY`, ADR 0005)*, le `kind` de chaque acteur (`actor_kind`, niveau 1, §5) ;
  - privés : la cargaison, l'activité, la route, les ticks avant le prochain saut et le minage en cours d'un vaisseau, le budget d'actions, le solde (`balance`) du portefeuille personnel ;
  - administration : les écritures du registre, les comptes d'émission et de destruction, les compteurs cumulés.

  Un acteur attentif peut déduire une partie de l'activité d'un autre acteur (position publique, stock public, prix fixes) : c'est accepté à M1 *(remplacé par l'amendement 1 : la position des vaisseaux d'autrui et le stock des gisements sont de classe proximité, et seuls les prix restent publics ; cette déduction n'est donc possible qu'à portée)*.
- **Événements v0** (`event_schema_version` = 0) : l'enveloppe du niveau 1, §6 : `tick` et `seq`, `event_schema_version` et `rules_version`, `actor_id` et `actor_kind`, `policy_id` et `policy_version`, `causation_id`, la classe de visibilité. `actor_id`, `actor_kind` et `causation_id` sont `None` pour un fait des règles (régénération d'un gisement). `causation_id` est l'identité de l'ordre qui a causé l'événement. **(amendement 1, précisé)** Une fin de minage arrêtée par les règles (cargaison pleine, gisement vide) a `causation_id` = `None` ; une fin de minage provoquée par un ordre qui remplace le minage porte l'identité de cet ordre (`_arreter_minage`, `core/step.py`). `seq` croît avec la production dans le tick : examen des ordres, puis phases du tick dans leur suite fixe, puis, dans une phase, identifiants croissants. Les types sont des types `msgspec`, exportables en JSON Schema :

  | Type d'événement | Classe | Contenu | Émis |
  | :-- | :-- | :-- | :-- |
  | personnage créé | public | acteur, `actor_kind`, vaisseau | à l'examen de l'ordre |
  | ordre refusé | privé | identité de l'ordre, code de refus | à l'examen de l'ordre |
  | départ | public *(remplacé par l'amendement 1 : proximité)* | vaisseau, système quitté | à chaque saut, en phase de déplacement |
  | arrivée | public *(remplacé par l'amendement 1 : proximité)* | vaisseau, système atteint | à chaque saut, en phase de déplacement |
  | début de minage | privé | vaisseau, minerai, débit (`mining_rate`) | à l'examen de l'ordre « miner » accepté |
  | fin de minage | privé | vaisseau, quantité extraite depuis le début | quand le minage s'arrête, pour toute raison |
  | vente | privé | quantité, prix, paiement, taxe | en phase de commerce |
  | régénération d'un gisement | public *(remplacé par l'amendement 1 : proximité)* | gisement, stock | en phase de règlement |
  | écriture du registre | administration | l'écriture | quand l'écriture est passée |

  Le montant d'une vente n'est jamais public ; l'événement de vente suffit au client (niveau 1, CUJ 1). Il n'y a jamais un événement par entité et par tick (niveau 1, §6).
- **Protocole** (`protocol_version` = 1 *(remplacé par l'amendement 1, voir ci-dessous : 2)*) : deux messages. Le client envoie « soumettre des ordres » ; le serveur envoie, après chaque tick, une « mise à jour du tick » qui porte l'observation.
- **Validation sans état** (`validate_orders`, fonction pure) : format (numéro positif ou nul, `policy_id` d'au plus 64 caractères), numéro répété dans un tick (le second et les suivants sont refusés), quota d'ordres par tick (`ORDER_QUOTA_PER_TICK`, valeur au plan détaillé, point 16 ; au-delà, les plus petits numéros sont gardés), ordre au nom d'un autre acteur que celui du point de connexion, catégorie autre que « joueur ». Les contrôles sont faits dans cet ordre, et le premier qui s'applique donne le code. La fonction reçoit, en une fois, tous les ordres d'un même point de connexion pour un tick : les numéros répétés et le quota se comptent par acteur du point de connexion (`sender_actor_id`), jamais par l'`actor_id` écrit dans l'ordre. Elle vit dans `schema` : la réception l'applique (niveau 1, §2), et, plus tard, l'entraînement l'appliquera de la même façon. Les ordres d'administration du serveur ne passent pas par elle.

**(amendement 1)**

- **`Observation`** reçoit le champ `public_tunables: PublicTunablesView` (`jump_ticks`, `mining_rate`), placé en dernier pour l'ordre d'encodage. La vue est construite en recopiant ces deux champs de `Tunables`, nommés un à un. La capacité de cargaison est déjà dans `OwnShipView.capacity`, et le paiement et la taxe d'une vente dans l'événement `Sale`. `Tunables` ne porte pas de classe de visibilité : ce n'est pas un champ de l'état. Un test vérifie que les noms de la vue existent dans `Tunables`.
- **Classe de visibilité `NEARBY` (proximité)**, ajoutée à `Visibility` (ADR 0005). **Règle :** un champ ou un événement de classe `NEARBY` est visible d'un acteur si son *système de référence* est le système d'un des vaisseaux de l'acteur, ou un système voisin. Le système de référence est le `system_id` de l'entité, celui de la charge utile d'un événement, ou, pour un événement de gisement, le système du gisement ; un type qui porte un champ ou un événement `NEARBY` doit avoir un tel système, ce qu'un test vérifie. Les positions qui comptent sont celles de l'état que reçoit `observe`. Un acteur sans vaisseau ne voit rien de classe proximité. **Hors de portée,** une entité dont l'identité est de classe proximité (un vaisseau d'autrui) disparaît de l'observation, et un champ de classe proximité d'une entité publique (le stock d'un gisement) vaut `None`.
  - **Vaisseaux d'autrui :** `id`, `owner_id`, `system_id` et `capacity` passent de `PUBLIC` à `NEARBY`. Un vaisseau d'autrui hors de portée n'apparaît pas du tout dans l'observation. Les vaisseaux de l'acteur restent entièrement visibles pour lui.
  - **Gisements :** `stock` passe de `PUBLIC` à `NEARBY` (décision du propriétaire, 2026-11-12) ; le gisement lui-même (identifiant, système, minerai) reste public. Hors de portée, la vue porte `stock` = `None` (`DepositView.stock: Int64 | None`). Sinon, la baisse du stock, à un débit d'une unité par tick, compterait les vaisseaux qui minent loin.
  - **Événements :** `Departed` et `Arrived` passent à `NEARBY`, rapportés à leur `system_id` ; `DepositRegenerated` aussi, rapporté au système du gisement, puisqu'il donne le stock. `CharacterCreated` reste public : il dit qu'un personnage existe, pas où est son vaisseau.
- **`PROTOCOL_VERSION`** passe à 2 (nouveau champ de l'observation). La réception ne vérifie toujours pas la version à M1 (M3 le fera).
- **Versions des formats.** Les classes de visibilité des champs de l'état ne sont pas encodées, mais `Event.visibility` l'est, et `State.last_tick.events` entre dans l'instantané et dans l'empreinte `last_tick`. La valeur `nearby` casse donc la lecture d'un fichier récent par le code d'origine, pas l'inverse. C'est accepté parce qu'avant M5 les données sont régénérées, et non migrées (niveau 1, §7). `snapshot_schema_version` reste à 1 : l'instantané est pris au tick 0, avec un `last_tick` vide. `event_schema_version` reste à 0 : les événements v0 sont jetables. `DepositView.stock` change de type (il devient facultatif) ; avec le seul champ nouveau, `public_tunables`, ce changement fait passer `protocol_version` à 2.
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
- **Le mode sans horloge** sert aux tests, aux outils et à la partie de référence. `Game.advance(n)` joue `n` ticks, de façon synchrone. À chaque tick : il prend les ordres soumis, appelle `step`, envoie la mise à jour à chaque client, puis appelle, pour chaque client synchrone attaché (`SyncClient`, Technical Plan, point 13), `on_update(mise à jour)` ; les ordres que cette méthode renvoie entrent au tick suivant. Une décision prend donc exactement un tick (plan détaillé, point 27, calcul des bornes).
- **L'horloge** déclenche un tick à chaque période. La période est un paramètre du serveur (1 seconde par défaut à M1 *(remplacé par l'amendement 1, voir ci-dessous : période nominale de 3 s)*), hors de `tunables.toml` et hors de `rules_version`.
- **La réception** lie chaque ordre reçu à l'acteur de son point de connexion et au tick où il entre, applique la validation sans état à l'ensemble des ordres de ce point de connexion pour ce tick, puis le journalise avec son code de refus éventuel. `step` refuse un ordre qui porte un code, avec ce code, et adresse le résultat à l'acteur du point de connexion, par son observation.
- **Le journal des ordres soumis** est une base SQLite en mode WAL (`synchronous=NORMAL` avant M5), `orders.sqlite`, avec deux tables (schéma au plan détaillé, point 21). Il contient sa version (`order_log_schema_version` = 1), `rules_version`, la graine du monde, l'identifiant (SHA) du commit et un indicateur « dossier de travail modifié », les ordres soumis par tick et les empreintes de chaque tick. Il s'exporte et s'importe en JSONL versionné (plan détaillé, point 21).
- **Les fichiers d'une partie** sont rangés dans `runs/<AAAAMMJJ-HHMMSS-micro>/`, ignoré par git : `orders.sqlite`, `snapshot.msgpack` (instantané initial, tick 0, `snapshot_schema_version` = 1, avec `rules_version`, la graine, l'identifiant du commit et l'indicateur « dossier de travail modifié », fournis par le serveur) et `events.jsonl`.
- **Les personnages** sont créés par des ordres d'administration journalisés pour le tick 1, l'un pour le propriétaire, l'autre pour le PNJ *(remplacé par l'amendement 1, voir ci-dessous : `npc_count` PNJ)* ; l'instantané initial est l'état du tick 0, avant ces ordres, et le premier `step` les applique.

**(amendement 1)**

- **Période nominale.** `Game(..., period_s=NOMINAL_TICK_PERIOD_S)`, et `--periode` a la même valeur par défaut. La valeur n'est écrite qu'à un endroit : `NOMINAL_TICK_PERIOD_S` (Technical Plan, point 5). `--periode` est une option de lancement, fixée pour toute la partie, qui sert aussi aux essais ; elle existe sans `--dev`, mais seul `--dev` permet de changer la période en cours de partie.
- **Premier tick immédiat.** `Game.run` joue un tick dès son lancement, puis attend une période entre deux ticks. Le joueur voit le monde tout de suite.
- **Vitesse.** `Game.set_period(period_s: float | None)` change la période ; `None` met en pause. Le changement réveille la boucle (par un `asyncio.Event`), qui recalcule l'attente restante avec la nouvelle période : un tick n'est joué tout de suite que si le temps déjà écoulé depuis le dernier tick dépasse la nouvelle période ; sinon, la boucle attend le reste. En pause, aucun tick n'est joué. Les paliers sont ×1, ×10, ×100 et ×1000 (3 s, 0,3 s, 0,03 s et 0,003 s) ; la « vitesse maximale » est le palier ×1000. En surcharge, un tick dure ce qu'il dure, puis l'horloge attend la période : la vitesse réelle reste sous la vitesse demandée (niveau 1, §2). **Contre-pression :** sous 0,05 s par tick (paliers ×100 et ×1000), l'horloge attend que la file des mises à jour du propriétaire soit vide avant le tick suivant ; l'arrêt « à la prochaine alerte » déborde donc d'un tick au plus.
- **Enregistrement.** `speed.jsonl`, dans le dossier de la partie, commence par un en-tête versionné (`{"speed_log_schema_version": 1}`), puis la période initiale ; chaque changement ajoute une ligne `{"tick": T, "period_s": P}`. Ce n'est pas le journal des ordres, et le rejeu ne le lit pas.
- **PNJ.** `__main__.py` crée `npc_count(graine, réglages)` PNJ. Chacun a sa connexion et sa tâche de relais (code d'origine), avec `NpcHost(acteur, scripted_miner.decide)`.
- **Fonction de rappel de vitesse, mode développement.** Avec `--dev`, `__main__.py` passe à `FourxApp` une fonction de rappel `set_period: Callable[[float | None], None]`, qui appelle `Game.set_period`. Sans `--dev`, il passe `None`, et le client n'offre aucune commande de vitesse. Le client n'importe pas `server` : il reçoit une simple fonction, ou rien. C'est la seule exception locale à « la même porte » (objectif 6) : elle ne commande que l'horloge de la partie locale, ni les règles ni le journal, et disparaît à M3, quand le client et le serveur ne partagent plus de processus.

### 7. Le client Textual et le PNJ

- **Le client.** *(remplacé par l'amendement 1, voir le Technical Plan, point 7 bis)* Il affiche la carte en ASCII, l'état du vaisseau (système, route, activité, cargaison), le solde du portefeuille, et un historique des résultats d'ordre et des ventes, avec le paiement et la taxe. Le propriétaire donne ses ordres au clavier : `d` (déplacer, puis le numéro du système), `m` (miner, puis la lettre du minerai), `v` (vendre toute la cargaison), `q` (quitter). Le client ne connaît que `schema` (niveau 1, §1).
- **Le PNJ de M1** joue la politique `scripted_miner` de `policies`, la référence scriptée du glossaire. Elle décide de l'activité voulue *(remplacé par l'amendement 1, voir ci-dessous : version 2)* :
  - si la cargaison est pleine : aller à la station, puis tout vendre ;
  - sinon : parmi les gisements non vides, aller à celui dont le minerai est le mieux payé, puis miner ;
  - si tous les gisements sont vides : rester à l'arrêt.

  Elle n'émet un ordre que si l'activité observée diffère de l'activité voulue : un vaisseau qui mine déjà ne reçoit pas de nouvel ordre « miner ». **L'hôte des PNJ** (`NpcHost`) la fait jouer par le même protocole que le client : il implémente `SyncClient` pour le mode sans horloge, et une tâche de `__main__.py` lui transmet les mises à jour en mode avec horloge.

**(amendement 1)**

`scripted_miner`, `policy_version` = 2, sans mémoire d'un tick à l'autre. Pour chaque vaisseau à l'arrêt ou en minage :
1. **À une station, hors minage, cargaison non vide :** vendre le minerai le plus abondant (à quantités égales, le plus petit identifiant).
2. **Cargaison pleine, ailleurs :** aller à la station qui paie le mieux le minerai le plus abondant de la cargaison (à prix égal, la plus proche en sauts, puis le plus petit identifiant).
3. **Sinon :** viser le minerai qui a le meilleur prix dans une station (à prix égal, le plus petit identifiant de minerai). Un vaisseau qui se trouve sur un gisement vide du minerai visé vise l'autre minerai, pour cette décision seulement : sans mémoire, il ferait sinon l'aller-retour entre deux gisements vides du même minerai, dont chacun redevient inconnu dès qu'il est hors de portée. Aller au plus proche des gisements du minerai visé dont le stock n'est pas connu pour nul (stock hors de portée, donc inconnu, ou stock positif), en sauts puis par identifiant, puis miner. Si aucun gisement de ce minerai ne convient, prendre l'autre minerai ; si aucun gisement ne convient, rester à l'arrêt.

La distance en sauts se calcule par une seule fonction publique, `distances(systems, start)` de `policies/geometry.py` (parcours en largeur sur les voisins de l'observation, par identifiant croissant). Le client la réutilise pour la carte, le coût d'un déplacement et les messages de refus, comme `most_abundant(cargo)` de `policies/cargo.py`, sans dupliquer le parcours ; ces deux modules n'ont aucune logique de décision, et changer la politique ne les touche pas ; les contrats d'imports permettent à `clients` d'importer `policies`. Le PNJ n'émet un ordre que si l'activité voulue diffère de l'activité observée. Avec les prix proposés, tous les PNJ visent `ore_b` et s'entassent : le propriétaire l'accepte, la référence scriptée devant rester simple.

### 7 bis. L'écran unique (amendement 1)

**Architecture du client.** `FourxApp` ne garde que l'affichage et les touches. La logique vit dans des modules purs, testés sans Textual et mutés sans plancher (le plancher de 80 % ne vaut que pour `core` et `schema`, Technical Plan, point 1) :
- `clients/model.py` : `ClientModel`, l'état du client. Il garde la dernière observation, les ordres envoyés sans résultat (numéro → commande), la file de vente, les alertes non acquittées et l'historique. Il reçoit une mise à jour et rend les messages à envoyer (par exemple la vente suivante de la file).
- `clients/map_layout.py` : la mise en page de la carte.
- `clients/texts.py` : les messages de refus en français, et la mise en forme des durées.
- `clients/frames.py` : un widget Textual par cadre. Chaque cadre lit `ClientModel` et ne connaît pas les autres. On peut en ajouter, en retirer ou les réarranger sans toucher au reste : c'est la modularité demandée par le propriétaire.

**Première disposition (80 × 24), à titre de maquette :**

```text
┌ Carte ────────────────────────────────────────────┐┌ Vaisseau ──────────────┐
│ [1]S1───[2]─────[4]b────[6]S2b──[9]─────[12]      ││ system_5  en minage    │
│         [3]─────[5]a────[7]a────[10]              ││ ore_a 37/100           │
│                         [8]─────[11]S3            ││ plein dans 63 ticks    │
│ liens : 1–3, 4–8, 10–11                           ││ (≈ 3 min 9 s à 3 s)    │
│                                                   ││ ordre envoyé : aucun   │
│ @ joueur : [5]   o vaisseaux proches : [3] [7]    │└────────────────────────┘
└───────────────────────────────────────────────────┘┌ Stations ──────────────┐
┌ Historique ───────────────────────────────────────┐│ S1 sys 1  a 10  b 15   │
│ t3 ordre « déplacer vers system_5 » : accepté     ││ S2 sys 6  a 12  b 12   │
│ t802 arrivée : system_5                           ││ S3 sys 11 a  8  b 18   │
│ t803 ordre « miner ore_b » refusé : pas de        │└────────────────────────┘
│      gisement de ore_b ici ; le plus proche est   │
│      dans system_4 (4 sauts)                      │
│ t804 ordre « miner ore_a » : accepté              │
└───────────────────────────────────────────────────┘
 Tick 840 │ Solde 0 │ Graine 1 │ dev ×1 │ d m v q · dev : p a r ␣
```

Maquette calculée par un script avec la règle de mise en page ci-dessous, sur un graphe d'exemple de 12 systèmes et 12 liens, dont le lien en plus 10–11. `S1`… marquent les stations, `a` et `b` les gisements de `ore_a` et `ore_b` (`[6]S2b` : une station et un gisement dans le même système), `@` le vaisseau du joueur, `o` les vaisseaux proches. Le cadre d'alerte, quand il y en a une, s'affiche en vidéo inverse au-dessus de l'historique. La liste des destinations donne le stock des gisements proches, et « ? » pour les autres.

**Mise en page de la carte (`clients/map_layout.py`, fonction pure).** Les systèmes sont rangés en colonnes de 8 caractères selon leur distance en sauts depuis le système 1 (fonction `distances`). Le parent d'un système est son voisin de plus petit identifiant dans la colonne précédente. Les colonnes sont traitées de gauche à droite et, dans une colonne, les systèmes par identifiant croissant : chacun prend le rang de son parent s'il est libre, sinon le premier rang libre en dessous ; le système 1 prend le rang 0. Un lien entre deux systèmes de colonnes voisines et de même rang est tracé en traits horizontaux : c'est le cas de la plupart des liens de l'arbre. Tout autre lien (même colonne, rangs différents, ou colonne sautée) est écrit en texte sous la carte (« liens : 1–3, 4–8 »). Aucun trait vertical ni oblique. Comme les colonnes ne dépendent que du système 1, la carte ne bouge pas quand le vaisseau se déplace. Une chaîne de 12 systèmes donne 12 colonnes, soit 96 caractères : au-delà de la largeur du cadre (6 colonnes), la carte passe sur deux bandes, coupées après la sixième colonne ; un lien qui traverse la coupe est écrit en texte. Si la carte dépasse la hauteur du cadre, le cadre Carte défile verticalement. Les tests de propriétés vérifient, sur de nombreuses graines, que chaque système et chaque lien apparaissent une fois, dessinés ou écrits ; la part des liens tracés et la hauteur de la carte sont mesurées et publiées au compte rendu de M1.

**Touches (clavier AZERTY, aucune Majuscule).**

| Touche | Effet |
| :-- | :-- |
| `d` | déplacer : ouvre la liste des systèmes (flèches, Entrée). Pour la ligne choisie, l'écran montre sauts, ticks et ≈ minutes ; Entrée confirme, Échap annule |
| `m` | miner le gisement du système, après confirmation (Entrée) |
| `v` | vendre toute la cargaison : met en file une vente par minerai, le plus abondant d'abord ; chaque vente part après le résultat de la précédente |
| `p` | (mode développement) pause, ou reprise de l'univers |
| `a` / `r` | (mode développement) accélérer / ralentir l'univers, par paliers : ×1, ×10, ×100, ×1000 (période 3 s, 0,3 s, 0,03 s, 0,003 s) |
| Espace | (mode développement) avancer jusqu'à la prochaine alerte (palier ×1000, retour à ×1 à l'alerte) |
| Entrée | acquitter l'alerte affichée, sans autre effet |
| Échap | annuler la saisie en cours |
| `q` | quitter, après confirmation : « Quitter termine la partie (pas de reprise avant M5). Entrée pour confirmer. » |

Une touche sans effet dans la saisie en cours (liste des destinations, confirmation, ou aucune saisie) affiche une ligne d'aide dans la barre d'état.

**Ordres envoyés.** Le modèle garde, pour chaque ordre envoyé, sa commande, jusqu'au résultat qui porte le même numéro. Le cadre Vaisseau l'affiche (« ordre envoyé : déplacer vers system_9 »). L'historique désigne un ordre par son contenu, jamais par son numéro. Un ordre manuel ou un refus vide la file de vente.

**Refus en français.** `clients/texts.py` traduit chacun des 18 codes de `RefusalCode`. Un refus lié à un lieu dit où aller, à partir de l'observation :
- `NO_DEPOSIT_FOR_ORE` : « pas de gisement de ore_a ici ; le plus proche est dans system_7 (2 sauts) » ;
- `NOT_AT_STATION` : « pas de station ici ; la plus proche est S1, dans system_1 (2 sauts) » ;
- `DEPOSIT_EMPTY` : « gisement vide ; le plus proche dont le stock n'est pas connu pour nul est dans system_7 (2 sauts) » (le client ne connaît que le stock des gisements proches).

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

### 8. Le rejeu, la divergence et les empreintes de référence

- **Le rejeu** part d'un état initial et d'une suite d'ordres soumis par tick, applique `step` tick par tick, et produit les empreintes et les événements de chaque tick. Une seule fonction de `tools` le fait (`replay_orders`, Technical Plan, point 13) ; elle sert à l'outil de rejeu d'un dossier de partie (état initial lu dans l'instantané), au contrôle `rejeu` et au test des fourchettes.
- **L'outil de divergence** (`tools`, niveau 1, CUJ 4) compare deux suites d'empreintes (deux dossiers de partie, ou deux fichiers d'empreintes), et indique le premier tick qui diffère et les composants concernés.
- **La partie de référence** est générée par la graine 1 et jouée par deux PNJ *(remplacé par l'amendement 1, voir le Technical Plan, point 9 : `npc_count(1, réglages)` PNJ)*, à travers le serveur en mode sans horloge. Elle n'est jouée qu'à la régénération des références. On enregistre alors, dans `tests/references/rules-<révision>/` :
  - `orders.jsonl`, l'export versionné de son journal des ordres soumis (en-tête : les valeurs de la table `meta` du journal et le dernier tick ; puis un ordre soumis par ligne) ;
  - `reference.json`, son `rules_version` et les empreintes de chaque composant tous les 1 000 ticks et au dernier tick.

  L'état initial n'est pas enregistré : il est régénéré par `world.generate` à partir de la graine, ce qui vérifie aussi la génération du monde. Le contrôle `rejeu` n'a besoin que de `core`, de `schema`, de `tools` et de l'import JSONL de `server`. Un changement du PNJ, de l'hôte des PNJ ou du serveur ne touche donc pas les références ; un changement des règles ou des réglages les fait diverger, et oblige à les régénérer. Une régénération des références remplace le dossier de la révision précédente ; l'historique git le garde (environ 4 Mo par révision, à mesurer au plan détaillé, point 28 bis).
- **La régénération des références** se fait avec l'outil de régénération (plan détaillé, point 27), lancé sur l'ordinateur portable. Il assemble `server`, `clients` et `policies` ; or `tools` peut importer `server`, mais ni `clients` ni `policies` (niveau 1, §1). Il vit donc sous `tests/`, que les contrats d'imports ne contraignent pas (choix du propriétaire), et produit aussi un rapport de différences. Le dossier `tests/references/` devient un chemin protégé. Le contrôle de garde exige que `RULES_REVISION` augmente de un quand les références changent, et pose l'étiquette « références régénérées » sur la pull request (`CLAUDE.md`, circuit des pull requests).
- **`rules_version`** est formé du numéro de révision, tenu à la main dans le noyau (`RULES_REVISION`), et de l'empreinte des réglages (niveau 1, §3) : `"rules-<RULES_REVISION>+<empreinte>"`. Le noyau calcule l'empreinte sur l'encodage MessagePack de `Tunables` (et non sur les octets du fichier, pour qu'un commentaire ne la change pas) : `step` la connaît donc, et la met dans chaque événement.

### 9. L'économie sur 100 000 ticks

- Le contrôle `rejeu` lance aussi un test marqué `lent` : il rejoue le journal enregistré de la partie de référence par `replay_orders` et collecte ses événements v0.
- Une seule fonction de `tools` (`window_stats`) calcule, à partir des événements v0, par fenêtre de 1 000 ticks (ticks 1 à 1 000, 1 001 à 2 000…) *(remplacé par l'amendement 1, voir ci-dessous : 10 000 ticks)* : l'émission par motif, la destruction par motif, la croissance de la masse monétaire, et la masse monétaire en fin de fenêtre. Le test vérifie les trois premières grandeurs contre les bornes du plan détaillé, point 27, sur chaque fenêtre sauf la première, qui contient le départ à vide des vaisseaux.
- Un notebook marimo appelle la même fonction et affiche les mêmes grandeurs pour le propriétaire. Il lit aussi les événements avec DuckDB, pour les explorer, sans calcul propre : le niveau 1 (§9, « DuckDB + notebooks marimo » dès M1) fixe ces deux outils pour l'économie.

**(amendement 1)**

- **Partie de référence :** graine 1, jouée par ses `npc_count(1, réglages)` PNJ, à travers le serveur en mode sans horloge, sur 100 000 ticks (inchangé).
- **Fenêtres :** `window_stats(..., window=10_000)`. Les empreintes de référence restent relevées tous les 1 000 ticks.
- **Bornes (décision du propriétaire, 2026-11-15) :** calculées par l'outil de régénération, avant de jouer la partie de référence, à partir du monde de la graine 1, des réglages et de la règle du PNJ version 2 (Technical Plan, point 7), sans lire les ventes de la partie. L'outil déroule le cycle établi de chaque PNJ (gisement visé, station de vente, distances) et en tire des bornes serrées, à une ou deux ventes près par PNJ et par fenêtre ; il les range dans `reference.json` avec les empreintes (plan détaillé, point 27). Le calcul dépend de la politique du PNJ, mais seulement au moment de la régénération : le test rejoue le journal enregistré, et reste valable si la politique change ensuite (alternative H). Un PNJ dont le gisement peut se vider passe à des bornes larges, dites de repli. La première fenêtre reste exclue (départ à vide).
- **Épuisement :** une station et un gisement peuvent partager un système (alternative AA). Des PNJ peuvent alors y boucler sans trajet et vider le gisement avant sa régénération. La partie de référence peut ainsi exercer l'épuisement, la régénération et le départage, sans garantie : cela dépend du monde de la graine 1. L'outil de régénération relève si un gisement s'est vidé et si un départage a eu lieu pendant la partie, et le compte rendu de M1 le cite. Les scénarios et les tests de propriétés à stock bas restent la parade principale (Risks & Mitigations).

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

Un test marqué `mesure`, sous `tests/` pour la même raison que l'outil de régénération (Technical Plan, point 8), mesure les ticks par seconde de `step` et de `observe` (une observation par acteur et par tick), sans serveur. Le monde a la taille de ceux de l'entraînement : le niveau 1, §8, dit « quelques dizaines d'entités », et M1 retient trois systèmes et 30 PNJ, un vaisseau chacun *(remplacé par l'amendement 1, voir ci-dessous : un monde généré de 12 systèmes, et 30 PNJ)*.

**(amendement 1)** Le monde mesuré est généré par `world.generate` avec `systems_min` = `systems_max` = 12 (réglages de mesure, hors de `tunables.toml`), et 30 PNJ sont créés par des ordres d'administration. Trois systèmes ne sont plus possibles : le décodage impose `systems_min` ≥ `deposits_max`. Les ordres des PNJ sont calculés hors du temps mesuré. Le test affiche le résultat ; rien ne dépend de sa valeur.

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
| classe de visibilité | `Visibility` : `PUBLIC`, `CORPORATION`, `PRIVATE`, `ADMIN` (amendement 1 : et `NEARBY`) |
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
observation.py  SystemView, DepositView, StationView, ActorView (champs publics)
                    (amendement 1 : DepositView.stock est de classe proximité, Int64 | None)
                OwnShipView (tous les champs de Ship, mêmes noms) ; OtherShipView (champs publics de Ship)
                    (amendement 1 : les champs d'OtherShipView sont de classe NEARBY)
                (StationView reprend ore_prices ; wallet_balance est le balance du portefeuille personnel de l'acteur)
                Observation(tick: Int64, actor_id: Id, systems, deposits, stations, actors,
                            own_ships, other_ships, wallet_balance: Int64, action_budget: Int64,
                            events: tuple[Event, ...], results: tuple[OrderResult, ...])
                    (amendement 1 : + public_tunables: PublicTunablesView, dernier champ)
protocol.py     PROTOCOL_VERSION = 1   (amendement 1 : 2)
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
                (amendement 1 : ore_prices est remplacé par station_ore_prices, et les fourchettes s'ajoutent ;
                 voir le Technical Plan, point 2)
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
observe.py      observe(state: State, actor_id: int) -> Observation   (amendement 1 : + tunables, ADR 0003)
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
server/game.py             Game(runs_dir: Path, world_seed: int, tunables: Tunables, period_s: float = 1.0)
                           (amendement 1 : period_s = NOMINAL_TICK_PERIOD_S, et set_period)
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
                           (amendement 1 : window = 10_000)
```

Les noms des composants affichés par l'outil de divergence sont ceux des champs de `Fingerprints` (`ledger` pour le registre).

**(amendement 1) Interfaces et identifiants ajoutés.**

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
policies/cargo.py      most_abundant(cargo: tuple[int, ...]) -> tuple[int, int]   (minerai, quantité)
policies/scripted_miner.py  POLICY_VERSION = 2
clients/model.py       ClientModel
clients/map_layout.py  layout(observation: Observation) -> list[str]
clients/texts.py       refusal_text(result: OrderResult, observation: Observation) -> str
clients/frames.py      un widget Textual par cadre (carte, vaisseau, stations, historique, barre d'état, alerte)
```

Autres changements de types (ADR 0005) : `DepositView.stock: Int64 | None` (`None` hors de portée) ; les champs de `OtherShipView` sont de classe `NEARBY`. `Observation.public_tunables` est le dernier champ de `Observation`.

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
*   **Raison du rejet :** proposition de l'agent de code, confirmée par le propriétaire le 2026-11-08. Retenu : le journal de la partie de référence est exporté à la régénération des références, au format versionné du journal des ordres soumis, et le contrôle `rejeu` le rejoue par `step` seul. Le serveur et le PNJ restent vérifiés par les scénarios et par leurs tests.

### Alternative I : garder tout l'historique des écritures dans l'état

*   **Avantages :** l'état contient tout le registre, sans recours aux événements.
*   **Inconvénients :** l'empreinte du registre réencode tout l'historique à chaque tick, donc le coût total d'une partie croît comme le carré de son nombre de ticks ; chaque phase recopie l'historique, et l'instantané du monde en ligne grossirait sans limite à M5.
*   **Raison du rejet :** proposition de l'agent de code, approuvée avec le document le 2026-11-08. Retenu : soldes, écritures du tick et compteurs cumulés dans l'état ; l'historique dans les événements (Technical Plan, point 3).

**(amendement 1)** Les alternatives A à I du document restent. Celles-ci s'y ajoutent, avec la marque « (amendement 1) » ; leur dernière puce, « Retenu », donne l'option choisie. L'alternative C (« des ticks avancés à la demande du joueur ») reste rejetée : l'accélération de l'amendement n'existe qu'en mode développement d'une partie locale, ne passe ni par le protocole ni par le journal, et ne change que la période de l'horloge (alternative S).

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

*   **Dans les fourchettes du niveau 1** (5 systèmes, une station) : aucune ADR, mais un seul point de vente, donc aucun choix du lieu de vente.
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
*   **Retenu :** choix du propriétaire : des prix propres à chaque station, écrits dans les réglages (`station_ore_prices`, une ligne par station, jusqu'à `stations_max`). Plus tard, le marché fixera les prix (M6).

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
*   **Commandes de vitesse pour tous :** pratiques, mais en partie normale l'univers doit tourner à son rythme ; le propriétaire ne les veut que pour le développement.
*   **Retenu :** en mode développement seulement (`--dev`), une fonction de rappel locale, passée par `__main__.py`, change la période de l'horloge (paliers, pause, avancer jusqu'à la prochaine alerte) ; chaque changement est enregistré dans `speed.jsonl`.

### Alternative T : afficher les durées en minutes, ou transmettre la période au client (amendement 1)

*   **Avantages :** le joueur lit directement le temps réel.
*   **Inconvénients :** la période change avec l'accélération, et ce n'est pas une donnée du jeu ; la transmettre dans l'observation ou dans `TickUpdate` serait un autre canal.
*   **Retenu :** les ticks restent l'information principale ; les minutes sont une estimation à la période nominale, précédée de « ≈ ».

### Alternative U : la durée du minage au-delà de 100 ticks (amendement 1)

*   **Un compteur de cycles de minage, ou un réglage « ticks par lot » :** des durées aussi longues qu'on veut, mais `step`, `Tunables`, le sens de `MiningStarted.rate`, et peut-être `State` et l'instantané, changeraient.
*   **Un changement d'échelle des unités** (cargaison de 4 000, prix et stocks à l'avenant) : seuls les réglages changeraient, mais tous les montants des scénarios et des bornes seraient à refaire.
*   **Retenu :** choix du propriétaire : 100 ticks (5 minutes) suffisent à M1 ; la durée dépendra plus tard du laser et de la capacité du vaisseau.

### Alternative V : le test d'économie (amendement 1)

*   **Garder des fenêtres de 1 000 ticks :** chaque fenêtre contiendrait zéro ou une vente par PNJ ; la borne basse tomberait à 0, et le test ne prouverait plus rien.
*   **Allonger la partie de référence à 1 000 000 de ticks :** environ dix fois plus de temps de rejeu, et des empreintes de chaque tick, écrites par la tâche `rejeu`, d'environ 284 octets par tick, soit environ 284 Mo.
*   **Des bornes tirées de la seule géométrie du monde, indépendantes de la politique du PNJ** (version de l'étape 5 de la revue) : aucun calcul ne dépendrait du PNJ, mais la borne basse vaudrait 0 pour presque toute graine, et la borne haute serait environ vingt fois trop lâche. Une panne qui arrête toute vente passerait le test.
*   **Descendre sous 100 000 ticks :** fixé par le niveau 1 ; il faudrait une ADR, sans bénéfice.
*   **Retenu :** des fenêtres de 10 000 ticks, sur les 100 000 ticks du niveau 1, et des bornes calculées à partir du cycle de chaque PNJ, à la régénération des références (décision du propriétaire, 2026-11-15 ; plan détaillé, point 27).

### Alternative W : la politique du PNJ (amendement 1)

*   **Le gisement le plus proche, la station la plus proche :** très simple, mais les prix propres des stations ne changeraient rien à son jeu.
*   **Un gisement attitré, déduit de l'identifiant :** les PNJ se répartiraient sur la carte, mais la répartition serait arbitraire.
*   **Une politique attentive au temps de trajet :** plus crédible comme adversaire, mais ce ne serait plus une référence simple, et M1 veut le PNJ simple.
*   **Retenu :** choix du propriétaire : « le mieux payé » (Technical Plan, point 7). Les PNJ s'entassent : c'est accepté.

### Alternative X : l'attache du PNJ en mode avec horloge (amendement 1)

*   **Avantages d'un client synchrone attaché :** la décision du PNJ entre toujours au tick suivant, à toute vitesse, comme dans la partie de référence.
*   **Inconvénients :** son calcul bloquerait la boucle des ticks, et le Technical Plan, point 7, serait réécrit.
*   **Retenu :** choix du propriétaire : la tâche de relais du code d'origine. Aux paliers rapides (×100 et ×1000), la partie locale ne joue pas tout à fait comme la partie de référence ; le rejeu reste exact, puisqu'il suit le journal.

### Alternative Y : la carte à l'écran et la visibilité des autres vaisseaux (amendement 1)

*   **Positions des systèmes dans l'état :** le client dessinerait aux coordonnées, et cela préparerait les distances variables ; mais `State` et l'observation recevraient deux champs par système, et la génération du graphe se compliquerait.
*   **Un tableau, sans dessin :** fidèle au rendu « façon tableur », mais sans vue d'ensemble du graphe, ce qui était l'une des gênes relevées.
*   **Visibilité :** voir le saut des autres vaisseaux, ou leur activité, partout (plus de mouvement visible, mais une information donnée à tous les concurrents) ; ou le statu quo (tout vaisseau visible partout, mais immobile pendant ses sauts).
*   **Stock des gisements public :** la carte en dirait plus, mais la baisse du stock, à une unité par tick, compterait les vaisseaux qui minent loin, malgré la proximité.
*   **Retenu :** choix du propriétaire : mise en page calculée par le client ; les vaisseaux d'autrui et le stock des gisements ne sont visibles qu'à proximité (système d'un des vaisseaux de l'acteur, ou système voisin), sans l'activité des vaisseaux (ADR 0005). Des scanners porteront plus loin plus tard.

### Alternative Z : les scénarios de partie sur les vrais réglages seulement (amendement 1)

*   **Avantages :** un seul jeu de réglages à suivre.
*   **Inconvénients :** chaque essai de réglage repasserait par une pull request de scénarios protégée, et la CI comme la mutation s'allongeraient (un cycle dure plus de 1 600 ticks).
*   **Retenu :** des réglages de test explicites dans les étapes, plus un seul scénario sur les vrais réglages.

### Alternative AA : interdire qu'une station et un gisement partagent un système (amendement 1)

*   **Avantages :** tout cycle passe par au moins un saut aller et un saut retour (900 ticks ou plus) ; aucun gisement ne peut se vider (6 000 unités extraites au plus par fenêtre, pour un stock de 20 000) ; les bornes d'économie sont plus étroites.
*   **Inconvénients :** il faudrait au moins 9 systèmes (`stations_max` + `deposits_max`), donc une fourchette de 9 à 12 ; la carte perdrait une situation de jeu, le gisement dans le système d'une station, qui rapporte vite puis s'épuise.
*   **Retenu :** décision du propriétaire (2026-11-12) : la colocalisation est voulue ; dans le pire des cas, le gisement s'épuise, et joueurs et PNJ doivent aller miner ailleurs. Une station et un gisement peuvent donc partager un système (Technical Plan, point 2). Une station partage son système avec un gisement dans 84 % des mondes générés, et avec un gisement de `ore_b`, le seul minerai que visent les PNJ avec les prix proposés, dans 52 % (calculs du 2026-11-12 et du 2026-11-13, moyenne sur les tailles équiprobables).


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
| L'épuisement et le départage ne sont jamais exécutés par la partie de référence *(remplacé par l'amendement 1 : avec la colocalisation, la partie de référence peut les exécuter)* | Un défaut de départage échappe au contrôle `rejeu` | — | Scénarios et tests de propriétés à stock bas ; le bug volontaire de la suite canari vise le placement des sites, toujours exécuté *(remplacé par l'amendement 1 : le placement devient la génération du monde, Technical Plan, point 2 ; l'ancre du bug volontaire suit la fonction de génération, plan détaillé, point 29)* |
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
| Parties manuelles très longues | à 3 s par tick, un cycle dure de 5 minutes (gisement dans le système d'une station) à plus d'une heure (gisement à deux sauts : 85 minutes) ; la validation de la boucle et les essais deviennent pénibles | durée de la partie d'essai | accélération en mode développement (paliers ×1 à ×1000, « avancer jusqu'à la prochaine alerte ») ; enchaînement des étapes du cycle (objectif 11) validé en accéléré, rythme sur un saut à la période nominale |
| Accélération oubliée | le joueur croit le jeu figé, ou rate une alerte à ×1000 | retour du propriétaire à la partie d'essai | en mode développement, vitesse toujours affichée dans la barre d'état ; retour à ×1 à chaque alerte pendant « avancer jusqu'à la prochaine alerte » |
| Dérive entre `tunables.toml`, les réglages de test et le document | un test ou un scénario passe sur des valeurs qui ne sont plus celles du jeu | scénario sur les vrais réglages en échec | `tunables.toml` est la seule source ; le scénario sur les vrais réglages les lit au lieu de recopier des nombres ; le tableau du document donne les valeurs initiales |
| File de vente coincée | une vente refusée laisse la file attendre | tests du modèle client | la file avance au résultat de la vente précédente ; un refus ou un ordre manuel la vide |
| Jeu d'attente avec un seul vaisseau | environ 94 % d'un cycle en trajet (1 600 ticks sur 1 701, carte d'origine) ; une décision par trajet | verdict de la partie d'essai | accepté à M1 ; la flotte et les scanners viendront plus tard |
| Conséquences pour M4 | environ 4 ordres par cycle de 1 701 ticks, soit environ 425 ticks par décision : des épisodes faits surtout d'attente, des récompenses rares, et un « pas » du niveau 1 (§2 et §8) qui compte surtout des ticks sans décision | mesure au document de niveau 2 de M4 | risque ouvert : la définition du pas et du verdict du niveau 1 est à revoir à M4 ; entraîner sur d'autres réglages n'est pas une issue, puisque M5 compare `rules_version` au déploiement (alternative H) ; piste qui ne change pas `rules_version` : un environnement d'entraînement qui enchaîne les ticks sans décision jusqu'à la suivante |
| Mise en veille de l'ordinateur portable | l'univers se fige probablement pendant la mise en veille | essai du plan détaillé, point 23 quater | vérifiée par cet essai ; sans effet sur les règles ni sur le rejeu |
| Écritures disque à vitesse élevée | à ×1000, un commit SQLite par tick | mesure du plan détaillé, point 28 bis | la contre-pression et le palier ×1000 (0,003 s) bornent le débit |
| Mises à jour accumulées | aux paliers rapides, la file des mises à jour du client grossit | débordement mesuré au plan détaillé, point 28 bis | sous 0,05 s par tick, l'horloge attend que la file du propriétaire soit vide ; le modèle client traite toutes les mises à jour, et l'écran ne redessine que la dernière |
| Peu de PNJ visibles | avec la visibilité par proximité, la plupart des 3 à 5 PNJ, et le stock des gisements lointains, sont hors de vue sur 8 à 12 systèmes | verdict de la partie d'essai | accepté par le propriétaire (décision de jeu, ADR 0005) ; à revoir à la partie d'essai, qui dira si l'écran paraît vide |
| Carte illisible pour certaines graines | une chaîne longue ou beaucoup de liens hors de l'arbre | part des liens tracés, mesurée sur de nombreuses graines | rang du parent pour les liens de l'arbre ; deux bandes au-delà de la largeur ; autres liens écrits en texte |
| PNJ décalés aux paliers rapides | avec la tâche de relais, une décision peut entrer un ou plusieurs ticks plus tard qu'au tick suivant ; si plusieurs décisions d'un PNJ en retard entrent dans le même tick, la plus ancienne gagne (un ordre par vaisseau et par tick, celui de plus petit numéro ; Technical Plan, point 2) | rejeu d'une partie accélérée | accepté par le propriétaire, qui a gardé la tâche de relais (alternative X) ; le rejeu suit le journal, il reste exact |
| Épuisement par colocalisation | des PNJ bouclent sur un gisement dans le système d'une station et le vident avant sa régénération | épuisement prévu par l'outil de régénération ; stock à 0 dans la partie de référence | accepté (alternative AA) : le PNJ vise l'autre minerai (Technical Plan, point 7) ; l'outil de régénération prévoit l'épuisement et le signale, et les PNJ de ce gisement passent aux bornes de repli (plan détaillé, point 27) |
| Gisement vide découvert à l'arrivée | hors de portée, le stock est inconnu : un vaisseau peut faire un trajet vers un gisement vide | tests de la politique du PNJ | accepté (ADR 0005) : sur un gisement vide du minerai visé, le PNJ vise l'autre minerai pour sa décision suivante (Technical Plan, point 7), ce qui rompt l'aller-retour entre deux gisements vides du même minerai ; la borne basse d'un PNJ au repli est 0, et aucune durée maximale de cycle n'est supposée (plan détaillé, point 27) |

## Additional Resources

*   [Niveau 1](./architecture-niveau-1.md), [RFC du brainstorm](./mmo-gestion-spatiale-ia.md), [glossaire](../glossaire.md), [document de M0](./niveau-2-m0-garde-fous.md).
*   Essais du 2026-11-02, hors du dépôt : `mutmut` 3.8.0 et `cosmic-ray` 8.7.0 sous Python 3.15 ; lecture du chargement de la configuration de `mutmut` 3.8.0 (`pyproject.toml` d'abord, sinon section `[mutmut]` de `setup.cfg`).
*   Essais du 2026-11-06, hors du dépôt, sous Python 3.15.2 : lecture du code de `mutmut` 3.8.0 (clés `source_paths`, `only_mutate`, `do_not_mutate`, `also_copy`, `pytest_add_cli_args` ; filtrage de `mutmut run` par motifs de noms de mutants ; `export-cicd-stats` ne donne que des totaux ; sortie de `mutmut results --all true`) et une mutation d'un petit projet ; métadonnées `msgspec.Meta(extra=...)` relues par `msgspec.inspect.type_info` sur `msgspec` 0.22.0 ; route `GET /repos/EZPK/4X/branches/main` lue sans jeton.
*   Rapports de la revue EGM de ce document : `docs/revues/2026-11-06-niveau-2-m1-noyau/`.
*   **(amendement 1)** Brief du brainstorm et rapports de revue de l'amendement : `docs/revues/2026-11-12-niveau-2-m1-noyau-amendement-1/`. Simulation du 2026-11-12, hors du dépôt : cycle de 1 701 ticks et 10 à 12 ventes par fenêtre de 10 000 ticks (carte d'origine, `jump_ticks` = 400, `mining_rate` = 1, deux PNJ). Calculs du 2026-11-12 et du 2026-11-13 : une station partage son système avec un gisement dans 84 % des mondes générés, et avec un gisement de `ore_b` dans 52 % (moyenne sur les tailles équiprobables). Essai du 2026-11-15, hors du dépôt, de la méthode des bornes du plan détaillé, point 27, sur la génération du Technical Plan, point 2, écrite d'après ce document avec `keyed_below` du noyau : pour la graine 1 (11 systèmes, 2 stations, 6 gisements, 5 PNJ), deux PNJ bouclent sur un gisement de `ore_b` dans le système de la station 2 et passent au repli, et l'émission `ORE_SALE` est bornée entre 45 000 et 361 500 par fenêtre ; sur les graines 1 à 10 000, 47 % des mondes ont au moins un PNJ au repli, et 35 % les ont tous (borne basse nulle). Ces chiffres sont à refaire sur le code livré.

## Future Improvements

*   **Le mode rejeu du client Textual**, à M3, avec la vidéo rendue depuis un rejeu.
*   **Le journal public de chaque corporation** (niveau 1, §4), à M6 : il sera construit à partir des événements « écriture du registre », puisque l'état ne garde que les écritures du tick.
*   **Une seconde partie de référence, contrainte par le stock** (plusieurs PNJ sur un gisement, `deposit_stock` bas), si les scénarios et les tests de propriétés ne suffisent pas à couvrir l'épuisement et le départage.
*   **(amendement 1) Des événements pendant les trajets** (idée du propriétaire, 2026-11-12) : ce qui peut arriver à un vaisseau en route, une fois les sauts longs. Hors de M1.
*   **(amendement 1) La vitesse propre à chaque vaisseau et la distance entre systèmes :** la durée d'un saut en dépendra, comme celle d'un minage dépendra du laser et de la capacité.
*   **(amendement 1) Des scanners** pour voir plus loin que les systèmes voisins (ADR 0005).
*   **(amendement 1) Des PNJ qui décident seuls ou en groupe**, par exemple pour leur corporation (M6).


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

**Règles d'intégration.** Aucun point du plan détaillé de ce document n'est renuméroté. Les points 17, 25, 26, 27, 28 et 28 bis sont modifiés sur place, et les points 29 et 32 bis reçoivent une marque de remplacement. Les points 5, 20, 22 et 23 (déjà livrés) reçoivent une ligne de renvoi vers ce volet. Le nouveau **volet B bis** (points 23 bis à 23 sexies) s'insère entre les points 23 et 24. **Aucune pull request du volet C ne s'ouvre avant la fin du point 23 sexies.** Une seule pull request de chaque type est ouverte à la fois.

#### 23 bis. Pull request protégée de l'amendement

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

#### 23 ter. Pull request de scénarios

*   **Type / Scope :** pull request de scénarios, chemins protégés. Elle s'ouvre après la fusion du point 23 bis.
*   **Proposed Changes :**
    - `tests/scenarios/partie.feature` (Modify) : réécrit sur des mondes générés, sans supposer la carte de la graine 1. Les étapes lisent la géométrie dans l'observation (« le gisement de ore_b le plus proche », « la station qui paie le mieux ore_b »). Les scénarios distinguent l'ancienne règle de la nouvelle, pour échouer sur le code d'origine :
      - CUJ 1 : un cycle complet sur des réglages de test explicites (saut de 5 ticks, minage de 10 unités par tick), sur un monde de 8 systèmes au moins ;
      - le temps comme ressource, sur les vrais réglages : les durées lues dans `observation.public_tunables` sont celles de `tunables.toml`, un trajet observé dure `jump_ticks` ticks, et la cargaison n'est pleine qu'après `cargo_capacity` ÷ `mining_rate` ticks de minage. Il échoue sur le code d'origine, où `public_tunables` n'existe pas. La valeur 400 n'est vérifiée par aucun test ;
      - la vente à une station autre que la station 1, au prix de cette station ;
      - la visibilité par proximité : un vaisseau deux sauts plus loin n'apparaît pas dans l'observation, et le stock d'un gisement à deux sauts vaut `None` ; un vaisseau voisin apparaît, sans son activité ;
      - la colocalisation : sur un monde où une station et un gisement partagent un système, un vaisseau y mine puis y vend sans saut ;
      - le PNJ vend une cargaison dans les 2 000 ticks, sur les réglages de test ;
      - les trois refus de réception déjà présents, conservés.
    - `tests/scenarios/ecrans.feature` (Create) : le modèle client et la mise en page, sans Textual :
      - un refus `NO_DEPOSIT_FOR_ORE` est traduit en français et nomme le gisement le plus proche du minerai ; un refus `DEPOSIT_EMPTY` nomme le plus proche gisement dont le stock n'est pas connu pour nul ;
      - les ticks restants d'un trajet et d'un minage, comparés à `Game.advance` ;
      - la vente de toute la cargaison part en deux ordres, sur deux ticks, tous deux acceptés ;
      - les deux alertes, et leur absence sur un saut intermédiaire ou sur un minage interrompu par un ordre ;
      - la carte d'un monde de 12 systèmes contient chaque système et chaque lien une fois.
    - `tests/scenarios/steps/steps_partie.py` (Modify) et `tests/scenarios/steps/steps_ecrans.py` (Create) : les définitions d'étapes, avec des réglages de test explicites.
    - `tests/scenarios/steps/steps_noyau.py` (Modify) : `REGLAGES_M1` prend les nouveaux champs de `Tunables` (il garde son nom) ; la phrase « les réglages de M1 » de `tests/scenarios/noyau.feature` (Modify) devient « des réglages de test ». Les scénarios du noyau dont les étapes changent échouent sur le code d'origine (champs inconnus de `Tunables`) : ils sont marqués *en attente* comme les nouveaux.
    - `tests/scenarios/test_scenarios.py` (Modify) : importe `steps_ecrans`.
    - `tests/scenarios/en_attente.txt` (Modify) : les scénarios nouveaux et modifiés.

#### 23 quater. Pull request de fonctionnalité : règles, formats, serveur et PNJ

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
    - `src/fourx/server/game.py` (Modify) : la période nominale par défaut, le premier tick immédiat, `set_period` (paliers ×1 à ×1000, `None` pour la pause, réveil par `asyncio.Event` et recalcul de l'attente restante, contre-pression sous 0,05 s par tick), `speed.jsonl` (avec son en-tête versionné), l'appel à `observe` avec les réglages. Le nombre de PNJ vient de `core.world.npc_count`, appelé par `__main__.py`.
    - `src/fourx/__main__.py` (Modify) : `--periode` par défaut à `NOMINAL_TICK_PERIOD_S` ; l'option `--dev`, qui seule donne au client la fonction de rappel `set_period` ; création de `npc_count` PNJ, chacun avec sa connexion et sa tâche de relais ; la fonction `set_period` passée au client. La graine est déjà dans le dossier de la partie (instantané, journal) et s'affiche dans la barre d'état.
    - `src/fourx/policies/scripted_miner.py` (Modify) : la règle du Technical Plan, point 7 (dont le stock inconnu hors de portée), `POLICY_VERSION` = 2.
    - `src/fourx/policies/geometry.py` et `src/fourx/policies/cargo.py` (Create) : `distances(systems, start)` et `most_abundant(cargo)`, sans logique de décision, réutilisées par le PNJ et par le client.
    - `src/fourx/clients/textual_app.py` (Modify) : adaptation minimale à l'observation nouvelle (prix de la station du système, stock `None` affiché « ? »), pour que le client d'origine reste jouable jusqu'au point 23 quinquies.
    - Tests non protégés (Modify) : `tests/aide_monde.py` (nouveaux champs de `REGLAGES`, plusieurs stations) ; `tests/aide_observation.py` (`public_tunables`) ; `tests/core/test_step.py` (vente à plusieurs stations, système de départ, colocalisation) ; `tests/core/test_observe.py` (proximité des vaisseaux, des événements et du stock ; réglages publics ; aucun champ caché ; tout type qui porte un champ `NEARBY` a un système de référence) ; `tests/core/test_monde_version_empreintes.py` (génération : fourchettes, connexité, plafond de voisins, déterminisme) ; `tests/core/test_versions.py` (`PROTOCOL_VERSION` 2) ; `tests/schema/test_schema.py` ; `tests/proprietes/test_proprietes.py` (génération sur de nombreuses graines, proximité) ; `tests/policies/test_scripted_miner.py` (règle version 2, dont le départ vers l'autre minerai d'un gisement trouvé vide, et l'absence d'aller-retour entre deux gisements vides du même minerai) ; `tests/policies/test_geometry.py` et `tests/policies/test_cargo.py` (Create) ; `tests/server/test_partie.py` (période nominale, premier tick, `set_period`, `speed.jsonl`, rejeu exact d'une partie jouée en accéléré) ; `tests/test_point_d_entree.py` (plusieurs PNJ).
    - **Essai de la veille** (risque) : une partie lancée, l'ordinateur portable mis en veille cinq minutes ; le tick avant et après est relevé et cité dans la description de la pull request, puis dans le compte rendu de M1.

#### 23 quinquies. Pull request de fonctionnalité : l'écran unique

*   **Type / Scope :** pull request de fonctionnalité, après la fusion du point 23 quater. Elle retire de `en_attente.txt` les scénarios de `ecrans.feature`.
*   **Proposed Changes :**
    - `src/fourx/clients/model.py` (Create) : `ClientModel` (Technical Plan, point 7 bis), sans Textual.
    - `src/fourx/clients/map_layout.py` (Create) : la mise en page de la carte, fonction pure.
    - `src/fourx/clients/texts.py` (Create) : la table des 18 codes de refus, les durées, l'estimation en minutes. Table des refus :

      | Code | Message (exemples de données entre crochets) |
      | :-- | :-- |
      | `UNKNOWN_SHIP` | vaisseau inconnu |
      | `NOT_OWNER` | ce vaisseau n'est pas le vôtre |
      | `SHIP_EN_ROUTE` | vaisseau en route : arrivée dans [N] ticks |
      | `UNKNOWN_SYSTEM` | système inconnu |
      | `ALREADY_THERE` | déjà dans [system_k] |
      | `NO_DEPOSIT_FOR_ORE` | pas de gisement de [ore_a] ici ; le plus proche est dans [system_k] ([n] sauts) |
      | `DEPOSIT_EMPTY` | gisement vide ; le plus proche dont le stock n'est pas connu pour nul est dans [system_k] ([n] sauts) |
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
    - `src/fourx/clients/textual_app.py` (Modify) : `FourxApp` réduit à l'affichage et aux touches ; la disposition du Technical Plan, point 7 bis ; la table des touches ; la fonction `set_period` reçue de `__main__.py`, ou `None` hors mode développement (aucune touche de vitesse).
    - `tests/clients/test_model.py`, `tests/clients/test_map_layout.py`, `tests/clients/test_texts.py` (Create) : les fonctions pures, et le modèle joué comme client synchrone par `Game.advance` (trajet de `jump_ticks` ticks, file de vente, alertes, ordres envoyés).
    - `tests/clients/test_textual_app.py` (Modify) : le pilote de Textual en `run_test(size=(80, 24))`, sur des observations fabriquées à des ticks éloignés : chaque touche du tableau, chaque état du vaisseau, la confirmation de `q`.

#### 23 sexies. Action : partie d'essai du propriétaire

*   **Type / Scope :** action du propriétaire, après la fusion du point 23 quinquies, **avant la pull request de scénarios du volet C**. Après le volet C, toute retouche de `tunables.toml` impose de régénérer les références et d'augmenter `RULES_REVISION`.
*   **Proposed Changes :** le propriétaire joue au moins un cycle complet en mode développement accéléré (`--dev`), et au moins un saut complet à la période nominale (20 minutes), qui juge le rythme. Il rend deux verdicts, consignés dans le compte rendu de M1 avec la graine et les vitesses jouées : l'écran est lisible (objectif 12) ; la boucle et son rythme lui conviennent (objectif 11). Un réglage à changer passe par une seule pull request de fonctionnalité sur `tunables.toml` (chemin non protégé), qui fait foi ; les scénarios lisent les réglages, et le tableau du Technical Plan, point 2, ne donne que les valeurs initiales.

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
*   **(amendement 1)** `reference.json` contient aussi les bornes d'économie et le cycle établi de chaque PNJ, calculés par l'outil de régénération (point 27).

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

*   **Proposed Changes (amendement 1, remplacement) :** les bornes ne sont plus des nombres écrits ici (décision du propriétaire, 2026-11-15). L'outil de régénération les calcule pour le monde de la graine 1, avant de jouer la partie de référence, à partir de la géométrie du monde (état initial), des réglages et de la règle du PNJ version 2 (Technical Plan, point 7), **sans lire les ventes de la partie**. Il les range dans `reference.json` (point 26), et `test_fourchettes.py` les y relit. L'outil écrit sa propre version de la règle, avec `distances` et `most_abundant` de `policies` (Technical Plan, point 7), sans appeler `scripted_miner.decide` : un défaut de la politique fait alors sortir la partie des bornes dès la régénération. Notations : W = 10 000 ; J = `jump_ticks` ; M = `cargo_capacity` ÷ `mining_rate` ; Q = `cargo_capacity` ; t = `tax_rate_bp` ÷ 10 000.

    1. **Le cycle établi de chaque PNJ.** Chaque PNJ part de son système de départ (Technical Plan, point 2), cargaison vide. L'outil applique la règle version 2 décision après décision, sur la géométrie seule, en supposant positif le stock de chaque gisement. Chaque décision a une durée : d × J pour un trajet de d sauts, M pour un minage qui remplit la cargaison, 0 pour une vente ; chaque décision ajoute au plus un tick de délai (Technical Plan, point 6). La politique n'a pas de mémoire : le PNJ revient donc à un état déjà vu (système, cargaison), et la boucle ainsi trouvée est son *cycle établi*. L'outil en retient :
       - la durée sans délai c_i et le nombre de décisions k_i du cycle ;
       - le gisement miné ;
       - l'émission par cycle e_i (somme des q × p de ses ventes, q la quantité et p le prix de la station) et la taxe par cycle x_i (somme des taxes de ses ventes, chacune arrondie vers le haut) ;
       - le tick où commence le cycle établi.
    2. **Le nombre de cycles par fenêtre.** Un PNJ fait, dans une fenêtre, entre a_i = ⌊W ÷ (c_i + k_i)⌋ − 1 et b_i = ⌈W ÷ c_i⌉ + 1 cycles (un cycle coupé à chaque bord). Dans la fenêtre où commence son cycle établi, a_i vaut 0.
    3. **L'épuisement prévu.** Tant que tous les gisements ont du stock, chaque PNJ suit son cycle établi : un premier écart suppose donc qu'un gisement s'est vidé, au seul profit des PNJ qui le minent dans leur cycle. Pour chaque gisement, l'outil additionne Q × b_i sur ces PNJ, plus Q par cargaison minée sur ce gisement avant le cycle établi, plus R = max(0, Q × Σ b'_j − `deposit_stock`), qui borne ce que les PNJ déjà au repli (point 4) peuvent miner hors de leur propre gisement, la somme portant sur ces PNJ. Si le total atteint `deposit_stock`, le gisement peut se vider avant sa régénération, qui a lieu au bord de chaque fenêtre (`regen_ticks` = W) : l'outil le signale, et les PNJ qui le minent passent au repli. Le calcul recommence jusqu'à ce que l'ensemble des PNJ au repli ne change plus.
    4. **Le repli.** Un PNJ au repli a une borne basse nulle, et une borne haute géométrique : au plus b'_i = ⌈W ÷ C_min⌉ + 1 cycles, avec C_min = 2 × d_min × J + M (d_min : plus petite distance en sauts entre une station et un gisement, 0 en cas de colocalisation) ; chaque cycle vend au plus Q unités, au plus grand prix de rachat du monde, p_max, en au plus deux ventes (une par minerai d'une cargaison mêlée). Aucune durée maximale de cycle n'est supposée : un PNJ qui trouve des gisements vides peut perdre un temps que la géométrie ne borne pas.
    5. **Les bornes.** Sur chaque fenêtre sauf la première, qui contient le départ, avec des sommes en a_i et b_i sur les PNJ hors repli, et des sommes en b'_i sur les PNJ au repli :
       - émission `ORE_SALE` entre Σ a_i × e_i et Σ b_i × e_i + Σ b'_i × Q × p_max ;
       - destruction `SALE_TAX` entre Σ a_i × x_i et Σ b_i × x_i + Σ b'_i × (Q × p_max × t + 2), le « + 2 » couvrant l'arrondi vers le haut de deux ventes par cycle ; elle reste égale à la somme des taxes de chaque vente, arrondies vers le haut ;
       - croissance de la masse monétaire entre Σ a_i × (e_i − x_i) et Σ b_i × (e_i − x_i) + Σ b'_i × Q × p_max × (1 − t). Une vente ne fait jamais baisser la masse monétaire : la taxe ne dépasse pas le paiement.

    Les bornes basses sont arrondies vers le bas et les bornes hautes vers le haut, par les fonctions de `core.arith`. `reference.json` garde, pour chaque PNJ, son cycle établi (c_i, k_i, gisement, ventes par cycle) ou son passage au repli, pour que le rapport de différences les montre. L'outil vérifie aussi que la partie jouée reste dans les bornes : sinon, il refuse d'écrire les références, et l'agent de code le signale au propriétaire, sans changer de graine, de règle ni de politique de lui-même. L'outil relève enfin, dans la partie jouée, si un gisement s'est vidé et si un départage a eu lieu ; le compte rendu de M1 cite ces relevés, les bornes de la graine 1 et la valeur réelle de chaque fenêtre.

    Le calcul dépend de la politique du PNJ, mais seulement au moment de la régénération : le test rejoue le journal enregistré, et reste valable si la politique change ensuite (alternative H). Un changement de la politique ne touche donc pas les références ; c'est à la régénération suivante, après un changement des règles ou des réglages, que l'outil doit suivre la version de la politique alors en vigueur. Un essai de la méthode sur la génération écrite d'après ce document est cité dans Additional Resources.

#### 28. `notebooks/economie_m1.py` (Create)

*   **Type / Scope :** notebook marimo.
*   **Proposed Changes :** lit le fichier `events.jsonl` d'une partie, appelle `window_stats`, et affiche par fenêtre de 1 000 ticks *(remplacé par l'amendement 1, voir le plan détaillé, point 25 : 10 000 ticks)* la masse monétaire, sa croissance, l'émission et la destruction par motif. Il lit aussi les événements avec DuckDB pour les explorer, sans calculer lui-même ces grandeurs.

#### 28 bis. Action — mesure de durée et revue du seuil de mutation

*   **Type / Scope :** action de l'agent de code, sur chaque pull request du palier 3.
*   **Proposed Changes :** relever la durée des tâches `rejeu`, `mutation` et `tests-outillage` (qui lance toute la suite jusqu'au palier 4) dans la description de la pull request ; la mutation la plus longue est celle d'une pull request de scénarios, qui mute tout `core`. Au premier dépassement de 30 minutes, l'agent de code s'arrête et le signale au propriétaire. Sur la pull request de fonctionnalité du volet C, relever aussi la taille de `tests/references/rules-1/`, et les scores de mutation de `core` et `schema` : si l'un d'eux est sous 80 % malgré des tests complets (mutants équivalents), l'agent de code le signale au propriétaire, qui décide du seuil.

*   **Proposed Changes (amendement 1, ajout) :** mesurer aussi le débordement de l'arrêt « à la prochaine alerte » au palier ×1000 (au plus un tick attendu, grâce à la contre-pression). Remesurer la durée des tâches `tests`, `rejeu` et `mutation` après les points 23 ter à 23 quinquies (scénarios plus longs, mutation des étapes), et le débit d'écriture à ×1000.

### Palier 4 : contrôles obligatoires, contrôles de nuit et suite canari (pull request protégée)

#### 29. `.github/canaris/` et `.github/scripts/canaris.py` (Create)

*   **Type / Scope :** suite canari, chemins protégés.
*   **Proposed Changes :** six bugs volontaires, chacun décrit par un fichier JSON : le contrôle visé, et une liste de modifications (fichier visé ; ancre : début du corps d'une fonction nommée, fin du module, ou expression nommée à remplacer ; texte inséré ou de remplacement). `canaris.py` applique chaque bug par l'analyse de la syntaxe (module `ast`), pas par un patch de lignes, puis lance la commande du contrôle visé, et échoue si cette commande réussit. Table contrôle → commande : celles du point 8.
    - un nombre flottant dans `step` (`core/step.py`) → `tests` ;
    - `core` qui importe `server` → `imports` ;
    - une vente sans écriture de taxe, mais avec le compteur cumulé de destruction augmenté → `tests` (invariants) ;
    - le portefeuille d'un autre acteur laissé dans une observation (`observe`) → `proprietes` ;
    - le placement des sites *(remplacé par l'amendement 1 : un tirage de la génération du monde, Technical Plan, point 2)* tiré par `hash()` d'une chaîne au lieu de `keyed_below` (`world.generate`) → `rejeu` (ce tirage a lieu dans chaque partie, et `hash()` d'une chaîne change avec `PYTHONHASHSEED`) ;
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

*   **Build et types :** `uv sync --locked`, `uv run mypy`.
*   **Tests :** `uv run pytest` (tests, scénarios, tests de propriétés), sans aucun scénario de `partie.feature` ni de `ecrans.feature` dans `en_attente.txt` à la fin du point 23 quinquies.
*   **Analyse statique :** `uv run ruff check`, `uv run ruff format --check`, `uv run lint-imports` (`clients` n'importe toujours ni `core` ni `server`).
*   **Mutation :** `.github/scripts/mutation.py` ; plancher de 80 % sur les fichiers nouveaux de `core` et `schema` (l'amendement n'en crée aucun) ; pour les fichiers modifiés, un score jamais inférieur à celui du commit de base (Technical Plan, point 10) ; `clients/model.py`, `map_layout.py` et `texts.py` mutés sans plancher.
*   **Déterminisme :** la génération du monde et une partie de 2 000 ticks donnent les mêmes empreintes sous `PYTHONHASHSEED=0` et `1`.
*   **Carte :** part des liens tracés et hauteur de la carte, mesurées par les tests de propriétés sur de nombreuses graines, publiées au compte rendu de M1.
*   **Manuel :** la partie d'essai du point 23 sexies, et l'essai de la veille du point 23 quater.
*   **CI :** chaque pull request cite les liens des contrôles verts.

*Drafted with EGM*
