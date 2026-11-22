# Étape 5 — Compréhension (amendement 2)

**Cible :** `docs/designs/niveau-2-m1-noyau.md`, passages marqués « amendement 2 ».
**Pièces liées :** `docs/adr/0006-client-retro-8-bits.md`, `docs/designs/architecture-niveau-1.md` (ligne 16), `docs/glossaire.md`.
**Méthode :** lecteur naïf (persona Comprehension Goldfish, mode REVIEW). J'ai lu la cible en entier pour vérifier les renvois, ainsi que l'ADR 0006, la ligne Overview du niveau 1 et le glossaire. Aucune norme n'était fournie en plus de ces pièces. Je n'ai modifié aucun fichier.

**Bilan :** 1 constat bloquant, 13 majeurs, 20 détails.

---

## Paraphrase

### Ce que propose l'amendement 2

L'amendement 2 refait l'écran du client sans toucher aux règles, au protocole ni à l'observation. Le client reste une application Textual dans le terminal, mais il ne se limite plus au texte : il dessine en couleurs (une palette fixe de 16 couleurs définies en hexadécimal, dite « 8 bits ») et en demi-blocs, et se pilote aussi à la souris. L'écran se compose de quatre parties :
- une carte du graphe des systèmes, disposée par un algorithme de forces déterministe, calculé une fois par partie, qu'on zoome (×1 à ×4) et qu'on déplace ;
- un panneau « Prochaine étape », calculé par sept règles ordonnées, qui conseille l'action suivante sans jamais envoyer d'ordre ;
- les panneaux Vaisseau, Marché et Journal ;
- une aide « Comment jouer », ouverte au lancement et par la touche `h`.

L'ADR 0006 justifie ce choix contre trois options : garder l'ASCII, écrire un client graphique natif, ou passer au navigateur. Elle modifie aussi une ligne de l'Overview du niveau 1. Le plan ajoute quatre étapes :
- 23 septies : une pull request protégée (documents) ;
- 23 octies : une pull request de scénarios ;
- 23 nonies : une pull request de fonctionnalité, qui supprime `map_layout.py` ;
- 23 decies : une partie d'essai du propriétaire, qui rend son verdict sur les objectifs 12 et 17 à 19.

### Le système existant, tel que le document le décrit

À la fin de l'amendement 1, le client est un « écran unique » fait de cadres indépendants : carte, vaisseau, stations, historique, barre d'état, alertes. Il affiche du texte et des tableaux, sans couleur. La logique vit dans des modules purs : `ClientModel`, `texts.py` et `map_layout.py`, la mise en page en colonnes de la carte. Le client ne reçoit du jeu que l'observation. Celle-ci contient l'état visible, les événements, les résultats d'ordre et deux réglages publics (`jump_ticks`, `mining_rate`), mais ni la graine ni le taux de taxe. Une fonction de rappel `set_speed` commande l'horloge, en mode `--dev` seulement. Le propriétaire a joué sur cet écran le 2026-11-22. Il a validé la boucle de jeu (objectif 11), mais juge l'écran peu clair (objectif 12 non atteint).

Le document ne dit pas quels points du plan sont livrés au moment de l'amendement 2 : la ligne 44, qui le disait, n'a pas été mise à jour (voir le constat M9).

---

## Constats bloquants

### B1. La graine affichée dans la barre contredit la règle « rien que l'observation »
- **Passage :** l. 583, « En haut, une barre : tick, durée de jeu estimée, solde, graine ».
- **Problème :** la l. 512 (Technical Plan, point 6) dit l'inverse : « Graine et dossier de la partie […] restent hors de l'écran de jeu : le client ne reçoit du jeu que l'observation (niveau 1, §5 ; ADR 0003) ». Or :
  - la graine n'est pas dans `Observation` (l. 758-761) ;
  - `FourxApp(connection, actor_id, set_speed)` ne la reçoit pas (l. 867) ;
  - le point 7 ter, l. 579, affirme que « rien ne change dans le protocole, l'observation ou les règles ».

  Un développeur ne peut pas suivre la l. 583 sans enfreindre l'une de ces trois règles, et rien ne lui dit laquelle céder.
- **Proposition :** retirer « graine » de la barre. Sinon, l'écrire comme seconde exception locale, à la manière de `set_speed`, avec le paramètre de `FourxApp` qui la porte, et réécrire la l. 512 avec la marque « (amendement 2, réécrit) ».

---

## Constats majeurs

### M1. « Palette 8 bits » pour seize couleurs
- **Passages :** l. 94 (« style rétro 8 bits »), l. 205 (« une palette 8 bits unique »), l. 581 (« Seize couleurs fixes ») ; ADR 0006, l. 8 (« la palette 8 bits (16 couleurs) ») et l. 14 (« palette fixe de 16 couleurs ») ; niveau 1, l. 16.
- **Problème :** pour un développeur, « 8 bits » de couleur veut dire 256 couleurs, et 16 couleurs correspondent à 4 bits. Les couleurs sont données en hexadécimal 24 bits, et l'ADR parle de « couleurs vraies ». Le risque de la l. 1147 et la l. 614 évoquent en plus une dégradation en 256 couleurs. On peut donc comprendre trois choses :
  - les 16 couleurs ANSI du terminal ;
  - une palette indexée sur 8 bits ;
  - 16 couleurs RGB arbitraires, rendues en couleurs vraies.

  Seule la troisième lecture semble voulue.
- **Proposition :** dire une fois, dans l'ADR et au point 7 ter, que « 8 bits » désigne l'esthétique des consoles 8 bits, et non une profondeur de couleur. Préciser que les 16 couleurs sont des valeurs RGB rendues en couleurs vraies, et non les 16 couleurs ANSI du terminal.

### M2. Aide au « premier lancement », ou à chaque lancement ?
- **Passages :** l. 94 et l. 205, et ADR, l. 17 (« aide au premier lancement ») ; à l'opposé, objectif 19, l. 182 (« s'ouvre au lancement ») et l. 610 (« L'aide s'ouvre au lancement de chaque partie »).
- **Problème :** « premier lancement » laisse entendre une seule ouverture, donc un état gardé d'une partie à l'autre (un fichier de préférences ?). Le point 7 ter dit « chaque partie ». Un développeur ne sait pas s'il doit mémoriser quelque chose.
- **Proposition :** garder une formule unique, « aide ouverte au lancement de chaque partie », dans l'Overview, les Non-Goals et l'ADR.

### M3. Le panneau Marché « rappelle la taxe », que l'observation ne contient pas
- **Passage :** l. 607, « la taxe est rappelée ».
- **Problème :** la vue des réglages publics ne contient que `jump_ticks` et `mining_rate`. L'objectif 14 (l. 172) dit que la taxe n'arrive au joueur que dans l'événement de vente. Avant la première vente, le client ne connaît donc pas le taux. Comme la l. 579 exclut tout changement de l'observation, la phrase est irréalisable, ou cache un ajout à `PublicTunablesView`.
- **Proposition :** soit « la taxe de la dernière vente est rappelée, s'il y en a une », soit ajouter `tax_rate_bp` aux réglages publics, ce qui change l'ADR 0003, `protocol_version` et les tests de visibilité, et doit alors être dit.

### M4. « Durée de jeu estimée » n'est pas définie
- **Passage :** l. 583.
- **Problème :** on ne sait pas s'il s'agit de tick × 3 s (l'estimation à la période nominale), du temps réel écoulé (horloge murale) ou d'autre chose. En mode `--dev` à ×100, ces valeurs divergent d'un facteur 100. Le client ne connaît pas la vitesse jouée (l. 575), ce qui interdit certains calculs.
- **Proposition :** donner la formule, par exemple « tick × `NOMINAL_TICK_PERIOD_S`, écrit par `duration_text`, suivi de « à 3 s » », ou retirer ce champ.

### M5. La vérification automatique de l'objectif 12 ne colle plus à la nouvelle carte
- **Passage :** l. 169, « des tests du pilote de Textual, sur un terminal de 120 × 36 et sur un monde de 12 systèmes (amendement 2, réécrit), vérifient […] que ces informations figurent dans leur cadre, au besoin après défilement du cadre Carte : le test lit le contenu du cadre ».
- **Problème :** la carte n'est plus un cadre de texte qui défile. C'est une `MapView` en demi-blocs, qu'on zoome et qu'on déplace (l. 587-593). À ×1, chaque système n'est qu'une « pastille numérotée » : les prix et les noms n'apparaissent qu'à partir de ×2 (l. 591). On ne sait plus :
  - ce que « défilement » veut dire ;
  - ce que le test « lit » dans un widget dessiné en pixels ;
  - dans quel cadre il cherche « où se trouve chaque minerai, et à quel prix chaque station le rachète » : la carte zoomée, la bulle, ou le panneau Marché ?
- **Proposition :** réécrire la vérification avec le cadre visé pour chaque information. Par exemple : prix dans « Marché », emplacement des minerais dans la carte à ×2 ou dans la bulle, ticks restants dans « Vaisseau » et « Prochaine étape ». Remplacer « défilement » par « déplacement de la vue ».

### M6. Prochaine étape, règle 3 : « soute pleine dans n ticks » est faux quand le stock limite
- **Passage :** l. 598, « en minage : soute pleine dans n ticks ».
- **Problème :** le point 7 bis (l. 572) dit qu'un minage s'arrête au premier de deux seuils : la capacité libre ou le stock. Si le stock du gisement est plus petit que la place libre, la soute ne sera pas pleine. Un développeur qui suit la règle à la lettre affichera une durée et un titre faux.
- **Proposition :** « en minage : fin du minage dans n ticks (`remaining_ticks()`), soute pleine ou gisement vide ».

### M7. Prochaine étape, règle 7 : ni repli, ni sens de « connu comme vide »
- **Passages :** l. 601 (« dont le stock n'est pas connu comme nul ») et l. 602 (« aller au plus proche gisement du minerai le mieux payé qui n'est pas connu comme vide »).
- **Problème :** trois points restent ouverts.
  1. « Le minerai le mieux payé » : on ne sait pas si c'est toutes stations confondues, comme pour le PNJ (l. 525), ni comment départager deux prix égaux.
  2. Aucun repli n'est prévu si tous les gisements de ce minerai sont connus comme vides, alors que la règle du PNJ en a un (passer à l'autre minerai, sinon rester à l'arrêt).
  3. « Connu comme vide » n'est défini nulle part. `ClientModel` (l. 868-879) ne garde aucune mémoire des gisements vus vides. Le terme veut donc probablement dire « visible maintenant, de stock 0 », mais on peut aussi comprendre « déjà vu vide », comme la liste du PNJ.
- **Proposition :** définir « connu comme vide » une fois, par exemple « stock observé égal à 0 dans la dernière observation ». Écrire le départage et le repli de la règle 7, en renvoyant si possible à la règle 3 du PNJ.

### M8. Mesure du temps de rendu : renvoi vers un point qui n'en dit rien
- **Passages :** l. 614 (« Le temps de rendu d'une mise à jour est mesuré au plan détaillé, point 28 bis ») ; risque de la l. 1150.
- **Problème :** le point 28 bis (l. 1607-1612) ne parle pas de rendu. Il n'a pas d'ajout de l'amendement 2, et le tableau des amendements (l. 49) ne le liste pas parmi les passages touchés. On ne sait ni quoi mesurer, ni sur quelle pull request, ni à partir de quel seuil alerter le propriétaire.
- **Proposition :** ajouter au point 28 bis une puce « **Proposed Changes (amendement 2, ajout)** » : mesure, palier, graine, seuil, conduite à tenir. Ajouter aussi le point 28 bis au tableau de la l. 49.

### M9. L'état du code livré n'est pas à jour, et « code de l'amendement 1 » n'est pas défini
- **Passages :** l. 44 (« les points 23 bis à 23 sexies, ajoutés par l'amendement, ne le sont pas ») ; l. 1534 (« chaque scénario qui échoue sur le code de l'amendement 1 ») ; l. 1516 (« le volet C peut avancer en parallèle »).
- **Problème :** l'amendement 2 suppose que l'écran de l'amendement 1 est livré et a été joué (l. 128). La l. 44 dit pourtant encore le contraire, et « l'amendement » y devient ambigu maintenant qu'il y en a deux. La l. 44 définit « code d'origine », mais pas « code de l'amendement 1 ». Si le volet C est fusionné entre-temps, la référence d'échec des scénarios de 23 octies n'est plus le code de l'amendement 1.
- **Proposition :** réécrire la l. 44 (« (amendement 2, réécrit) ») avec les points livrés à la date de l'amendement 2. Remplacer « code de l'amendement 1 » par « le code de `main` à l'ouverture de la pull request de scénarios ».

### M10. `layout`, `map_layout.py` : des noms apparaissent sans présentation
- **Passages :** l. 1533 (« la convention sur la sortie de `layout` est retirée ») ; l. 1093 (« `clients/map_layout.py` est retiré »).
- **Problème :** la l. 533 a été réécrite, et le module de la carte de l'amendement 1 n'est plus nommé dans le Technical Plan. Le lecteur découvre `map_layout.py` dans l'alternative AE sans savoir ce qu'il faisait. « La convention sur la sortie de `layout` » ne renvoie à rien de lisible : on ne sait ni quelle fonction, ni quelle convention, ni où elle est écrite.
- **Proposition :** au point 7 bis, garder une phrase du type « remplace `clients/map_layout.py` (mise en page en colonnes de l'amendement 1, point 23 quinquies) ». En 23 octies, citer la convention retirée, ou renvoyer à l'étape et au fichier exacts.

### M11. `force_layout` : la garantie de distance et les paramètres manquent
- **Passage :** l. 585.
- **Problème :** l. 105, le document se donne pour règle qu'un agent de code doit pouvoir livrer chaque livrable « sans décision ouverte ». Or plusieurs choix restent ouverts :
  - la longueur du ressort, les constantes de répulsion et de rappel, la loi de décroissance du pas, le rayon du cercle initial ;
  - le passage des positions brutes au carré [0, 1]², par une mise à l'échelle avec ou sans conservation des proportions.

  Surtout, « Deux systèmes sont toujours à une distance d'au moins 0,08 » est énoncé comme une garantie, alors qu'une simulation de forces ne la garantit pas. Le développeur ne sait pas s'il doit ajouter une étape de correction, ou seulement espérer que les tests passent.
- **Proposition :** donner les constantes, ou les déclarer libres mais figées dans le module. Écrire la normalisation. Dire si la distance minimale est imposée par une passe finale ou seulement vérifiée par les tests, et ce qui se passe en cas d'échec.

### M12. Partie d'essai 23 decies : la conséquence du verdict n'est pas dite
- **Passages :** l. 1550 (« Il rend son verdict sur la lisibilité (objectif 12) et sur les objectifs 17 à 19 ») ; objectifs 17 à 19, l. 179, 181 et 183.
- **Problème :** les vérifications des objectifs 17 à 19 sont entièrement automatiques, et ne mentionnent aucun verdict du propriétaire. La l. 132 dit pourtant qu'un objectif est validé par le propriétaire « quand le document le dit ». On ne sait pas :
  - si un verdict négatif bloque la livraison de M1 ;
  - s'il ouvre un amendement 3 ;
  - s'il déclenche la condition de révision de l'ADR 0006, qui ne vise que les causes « propres au terminal ».
- **Proposition :** ajouter aux objectifs 17 à 19 « et le verdict du propriétaire (plan détaillé, point 23 decies) », puis dire en 23 decies ce qui suit un verdict défavorable, selon qu'il vient du terminal ou du contenu.

### M13. « Journal » et « Marché » : deux noms déjà pris
- **Passages :** l. 180 (« prochaine étape, puis vaisseau, puis marché, puis journal ») ; l. 583 ; l. 607-608 ; l. 887 ; l. 1542.
- **Problème :**
  - Dans tout le document, « journal » désigne le journal des ordres soumis (`OrderLog`), comme dans « rien dans le protocole, le journal ou les règles » (l. 310). Le panneau « Journal » affiche en réalité l'historique du client (`ClientModel.history`, l. 608).
  - « Marché » est un Non-Goal explicite (« Un marché (M6) », l. 209).
  - Les cadres de l'amendement 1 s'appelaient « historique » et « stations » (l. 79, l. 1501). Le changement de nom n'est pas dit.

  Un lecteur peut croire que le panneau lit le journal des ordres, ou que M1 introduit un marché.
- **Proposition :** dire une fois que le panneau « Journal » affiche l'historique du client, et non le journal des ordres soumis, et que « Marché » est le nouveau nom du cadre « stations » (prix fixes, pas de marché). Mieux encore : appeler les panneaux « Historique » et « Prix des stations ».

### M14. Le test des contrastes : quels couples ?
- **Passages :** l. 581 (« Chaque couple texte et fond employé a un contraste d'au moins 4,5:1 ; un test le calcule ») ; l. 1545 (`test_palette.py`).
- **Problème :** la liste des couples « employés » n'existe nulle part. Le test doit-il couvrir les éléments atténués (systèmes hors de portée, vaisseaux proches), le ★ en couleur succès sur le fond d'un panneau, les étiquettes colorées du journal ? Le développeur du test choisira lui-même les couples, donc ce qu'il vérifie.
- **Proposition :** donner la liste des couples (rôle du texte, rôle du fond) dans `palette.py`, sous forme d'une constante que le test parcourt, et l'énumérer au point 7 ter.

---

## Détails

### D1. Les lettres d'alternatives ne sont pas mises à jour
- **Passages :** l. 25 (« alternatives J à AA ») ; l. 896 (« Les alternatives J à AA, plus bas, s'y ajoutent »).
- **Problème :** les alternatives AB à AE n'y figurent pas.
- **Proposition :** « J à AE », ou une phrase marquée amendement 2 à la suite.

### D2. Le renvoi désigne la partie d'essai au lieu de l'écran
- **Passage :** l. 128, « Sur l'écran unique de l'amendement 1 (plan détaillé, point 23 sexies) ».
- **Problème :** le point 23 sexies est la partie d'essai ; l'écran est livré par le point 23 quinquies.
- **Proposition :** « (plan détaillé, point 23 quinquies), lors de la partie d'essai du point 23 sexies ».

### D3. Une phrase obscure
- **Passages :** l. 128 (« les mécaniques des jalons suivants (exploration, piraterie…) se répondent ») ; l. 158 (« ses mécaniques se répondant »).
- **Problème :** « se répondent » est obscur. « Exploration » n'est pas une mécanique annoncée par le document (la piraterie arrive à M6, l. 187).
- **Proposition :** « les mécaniques à venir (piraterie à M6, …) devront interagir avec la boucle ».

### D4. Marques de l'objectif 12
- **Passage :** l. 169.
- **Problème :** la marque « (amendement 2, réécrit) » est placée au milieu d'une phrase. Selon la portée des marques (l. 43), elle ne couvre que le membre de phrase qui la précède, sans qu'on sache où ce membre commence. Par ailleurs, « rendue après la partie d'essai de l'amendement 2 (plan détaillé, point 23 decies) » est du texte de l'amendement 2 sans marque. L'objectif entier étant marqué « (amendement 1) », ce texte est attribué à l'amendement 1.
- **Proposition :** marquer explicitement ces deux passages.

### D5. Passages de l'amendement 1 contredits sans marque
- **Passages :**
  - l. 79, « sans thème de couleur » ;
  - l. 204, « La disposition définitive de l'écran. L'amendement fixe une première disposition simple » ;
  - l. 249, « le point 7 bis est nouveau », sans mention du point 7 ter ;
  - schéma de la l. 270, « cadres Textual (écran unique) ».
- **Problème :** la règle de préséance tranche, mais le lecteur voit des contradictions sans renvoi.
- **Proposition :** une marque « (amendement 2, précisé) » qui renvoie au point 7 ter.

### D6. Parades et mesures obsolètes après le retrait de `map_layout.py`
- **Passages :** risque « Carte illisible pour certaines graines », l. 1138 (« rang du parent pour les liens de l'arbre ; deux bandes au-delà de la largeur ; autres liens écrits en texte ») ; 23 quater, l. 1470 (« la part des liens tracés et la hauteur […] citées au compte rendu de M1 »).
- **Problème :** ces parades et ces mesures décrivent `map_layout.py`, que l'amendement 2 supprime.
- **Proposition :** les marquer « remplacé par l'amendement 2 », et dire ce que le compte rendu cite désormais.

### D7. Entre 100 × 30 et 120 × 36
- **Passage :** l. 583.
- **Problème :** on ne sait pas comment l'écran se comporte à ces tailles : les cadres se réduisent-ils, ou sont-ils tronqués ?
- **Proposition :** une phrase sur le comportement intermédiaire.

### D8. Palette : couleur partagée et rôles sans emploi
- **Passage :** l. 581.
- **Problème :** « accent » et `ore_b` ont la même valeur, `#3FD0E0`. Il n'y a donc que quinze couleurs distinctes, et un élément en couleur d'accent ne se distingue pas d'un gisement de `ore_b`. Les rôles « accent », « trait fort », « trait faible » et « panneau clair » ne sont reliés à aucun élément de l'écran.
- **Proposition :** différencier les deux couleurs, ou justifier le partage, et dire où chaque rôle est employé.

### D9. Pas de zoom et seuils
- **Passage :** l. 591.
- **Problème :** avec des pas de 1,25 à partir de ×1, on n'atteint exactement ni ×2 ni ×4 (1,95 ; 2,44 ; … ; 3,81 ; 4,77). On ne sait ni quand les libellés apparaissent, ni s'il faut borner le zoom.
- **Proposition :** dire « borné à ×4 », et un seuil des libellés « dès que le zoom dépasse 2 ».

### D10. Clic ou glissement
- **Passages :** l. 592-593.
- **Problème :** rien ne distingue un clic d'un glissement avec le bouton gauche, et le clic sur le système où se trouve déjà le vaisseau n'est pas traité.
- **Proposition :** fixer un seuil de déplacement, et dire que le clic sur le système du vaisseau affiche « déjà dans system_k ».

### D11. Le « nom » d'un système
- **Passages :** l. 591 et l. 593.
- **Problème :** les systèmes n'ont pas de nom (Non-Goals, l. 197 ; libellés neutres, l. 285), et `SystemView` n'a pas de champ « nom ».
- **Proposition :** « son libellé neutre (`system_k`) ».

### D12. Aide et touches
- **Passage :** l. 610.
- **Problème :** plusieurs comportements restent ouverts :
  - quand l'aide et une alerte sont affichées en même temps, que fait Entrée, qui sert aux deux (l. 549) ?
  - quelles flèches changent de page ?
  - Échap ferme-t-il l'aide ? `h` la referme-t-il ?
  - l'univers continue-t-il de tourner pendant que l'aide ouverte au lancement est lue (sans `--dev`, il n'y a pas de pause) ?
- **Proposition :** une phrase pour chacun de ces points.

### D13. Signature de `next_step`, et « l'observation seule »
- **Passages :** l. 881 ; objectif 18, l. 180 (« à partir de l'observation seule »).
- **Problème :** `next_step(observation, model)` n'est pas typé, alors que les autres signatures le sont. `ClientModel` contient déjà l'observation, ce qui rend le premier paramètre redondant. La règle 1 lit les alertes du modèle, ce qui contredit « l'observation seule ».
- **Proposition :** typer la fonction (`ClientModel -> Step`), et écrire dans l'objectif « à partir de l'observation et de l'état du client, sans autre canal ».

### D14. Règle 2 : quel système ?
- **Passage :** l. 597, « arrivée à `system_k` dans n ticks ».
- **Problème :** on ne sait pas s'il s'agit du prochain saut ou de la destination finale.
- **Proposition :** « destination finale ».

### D15. « Soute » ou « cargaison »
- **Passages :** l. 598-600 et l. 606.
- **Problème :** « soute » apparaît comme un synonyme non annoncé de « cargaison », le terme employé partout ailleurs (Vente, `cargo_capacity`).
- **Proposition :** garder « cargaison ».

### D16. « Un premier objectif »
- **Passages :** objectif 19, l. 182 ; l. 610.
- **Problème :** le contenu de ce premier objectif n'est pas dit.
- **Proposition :** l'écrire, par exemple « vendre une première cargaison ».

### D17. « ASCII »
- **Passages :** l. 128 et alternative AB, l. 1071 ; ADR, titre et l. 8 ; niveau 1, l. 16.
- **Problème :** le document de M1 n'appelait jamais le client « ASCII » avant l'amendement 2. Il disait « texte, tableaux et cadres ». Par ailleurs, « mode texte » (la nouvelle formule) et « ASCII » se distinguent mal pour un lecteur : les deux sont du texte.
- **Proposition :** dans l'ADR, une phrase : « ASCII désigne ici le rendu en caractères seuls, sans couleur ». Au niveau 1, écrire « en couleurs et demi-blocs ».

### D18. L'amendement ne prévoit aucune mise à jour du glossaire
- **Passages :** 23 septies, l. 1518-1526 ; glossaire.
- **Problème :** l'amendement 1 mettait à jour le glossaire (l. 1422). L'amendement 2 ne prévoit rien, alors qu'il introduit ou emploie des termes absents du glossaire : portée (définie seulement à l'objectif 6, l. 149), prochaine étape, demi-bloc, disposition par forces, style rétro 8 bits.
- **Proposition :** ajouter `docs/glossaire.md` (Modify) en 23 septies, ou dire pourquoi ce n'est pas nécessaire.

### D19. La carte manque à la hiérarchie
- **Passage :** objectif 18, l. 180.
- **Problème :** la carte, qui occupe 60 % de l'écran, n'a pas de place dans la hiérarchie annoncée.
- **Proposition :** la situer dans cette hiérarchie.

### D20. Risque « Rendu différent selon le terminal »
- **Passages :** l. 1147 (« palette pensée pour rester lisible en 256 couleurs ») ; l. 614.
- **Problème :** rien ne vérifie la lisibilité en 256 couleurs, et le cas des terminaux à 16 couleurs n'est pas traité. La position de la mini-carte n'est pas donnée (l. 591). Les maquettes citées sont « hors du dépôt » (l. 128 ; ADR, l. 8) : le lecteur ne peut pas les consulter.
- **Proposition :** dire ce qu'on accepte de ne pas vérifier ; placer la mini-carte ; ranger une capture des maquettes dans le dossier de revue, si le propriétaire le souhaite.

---

## Fichiers examinés
- `docs/designs/niveau-2-m1-noyau.md`
- `docs/adr/0006-client-retro-8-bits.md`
- `docs/designs/architecture-niveau-1.md` (l. 16 et l. 604)
- `docs/glossaire.md`
