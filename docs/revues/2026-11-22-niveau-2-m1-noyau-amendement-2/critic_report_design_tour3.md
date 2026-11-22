# Étape 7, tour 3 — Conception (amendement 2)

**Cible :** `docs/designs/niveau-2-m1-noyau.md`, passages « amendement 2 ». J'ai surtout lu le Technical Plan, point 7 ter (l. 586-692), les objectifs 12 et 17 à 19 (l. 161-184), le point 13 (l. 944-976), l'alternative AH (l. 1198-1205), les risques de l'amendement 2 (l. 1255-1264), le volet B ter (l. 1631-1685) et le Verification Plan (l. 1853-1861).

**Pièces lues :**
- `docs/adr/0006-client-retro-8-bits.md` ;
- `docs/designs/architecture-niveau-1.md`, §5 ;
- le Technical Plan, points 2, 5 et 7 ;
- le code : `src/fourx/schema/observation.py`, `src/fourx/policies/scripted_miner.py`, `src/fourx/policies/geometry.py`, `src/fourx/policies/cargo.py`, `src/fourx/clients/model.py`, `src/fourx/clients/texts.py`, `src/fourx/core/tunables.toml` ;
- la configuration : `.github/workflows/ci.yml`, `pytest.ini`, `setup.cfg` ;
- la revue : `critic_report_design_tour2.md` et `goldfish_review_report.md` du dossier de revue.

**Persona :** design_critic, mode REVIEW. On ne m'a fourni aucun gabarit en plus de ces pièces.

**Revue complète :** j'ai pu lire tous les fichiers requis. Je ne rediscute pas les décisions E1 à E5.

## Verdict

**Non approuvable en l'état : 0 bloquant, 4 majeurs, 15 détails.**

Les cinq majeurs du tour 2 sont traités :
- quatre sont corrigés entièrement ;
- la disposition (M1) l'est sur le fond, avec un reste : le calibrage des boîtes dépend d'une hauteur de carte que le document ne fixe pas (**Majeur 4**).

Le choix du gain par tick (E5) est bien rédigé :
- tout est calculé en entiers ;
- les départages sont complets ;
- chaque entrée se lit dans l'observation.

Mais les règles 5 et 6 ont deux défauts qui tromperaient le joueur :
- la règle 6 ignore la cargaison déjà à bord (**Majeur 1**) ;
- les deux règles ne mesurent pas le gain de la même façon : le plan annoncé au départ n'est pas celui que le guide conseille ensuite (**Majeur 2**).

Côté carte, les étiquettes du zoom 2, coupées au milieu d'un nombre, affichent de faux prix et de faux stocks (**Majeur 3**).

Les quatre corrections sont locales : quelques phrases du point 7 ter, et des tests.

---

## 1. Suivi des majeurs du tour 2

| Majeur du tour 2 | État | Où | Commentaire |
| :-- | :-- | :-- | :-- |
| **M1** Distance minimale contre encombrement des glyphes | **Corrigé en partie** | l. 624, 626, 1263 | Séparation par boîtes, retour dans [0,05 ; 0,95]² à chaque passe, arrêt après 100 passes, test de non-recouvrement **dans la grille** en 120 × 36 et en 100 × 30, parade du risque réécrite : tout cela est fait. Reste ceci : les boîtes (0,125 × 0,15) sont calées au pixel près sur une hauteur de carte de 40 pixels, que le document ne fixe pas. À 30 lignes avec une bordure, la carte n'a que 38 pixels de haut : la marge disparaît, et le `▲` des systèmes du haut sort de la grille. Le bord haut, signalé au tour 2 (M1, point 4), n'est donc pas réglé. Voir **Majeur 4**. |
| **M2** Liens hors de portée presque invisibles | **Corrigé** | l. 598-602 | J'ai refait le calcul (WCAG 2.1) : `trait_faible` sur `fond` donne 3,66 pour 1, `trait_fort` 5,68. `GRAPHIC_PAIRS` est à 3 pour 1, les fonds sont fixés, et la portée est aussi portée par le trait plein ou pointillé. Seul oubli : `GRAPHIC_PAIRS` manque à la liste des tests du point 23 nonies (détail d11). |
| **M3** Durées inobservable et fausse | **Corrigé** | l. 652, 658, 1670 | La règle 4 est observable (`other_ships[i].system_id`). « Miner ici » donne la fin du minage, avec q borné par le stock. Les deux cas sont dans `test_guide.py`. |
| **M4** « Conseil = PNJ » non pesé | **Corrigé** | l. 322, 1198-1205, 1264 | E5 est tranchée et AH ajoutée. Le risque nomme les conséquences et un signal : la durée du premier cycle est consignée (l. 1685). |
| **M5** Coût des 2 000 graines sous la mutation | **Corrigé** | l. 626 ; `setup.cfg` | La mutation lance `not lent` : les 2 000 graines en sont exclues, et `proprietes` garde 50 graines. Une petite redondance en CI reste (détail d12). |

Détails du tour 2 : d1 à d12, d14 et d15 sont corrigés. Pour d13 (maquettes hors du dépôt), la l. 588 dit maintenant que le point 7 ter les décrit et fait foi : raison acceptable.

---

## 2. Majeurs

### Majeur 1. La règle 6 ignore la cargaison déjà à bord : gain faux, vente oubliée, « attendre » avec une cargaison à vendre

- **Passages :** l. 653-654 (conditions des règles 5 et 6) et l. 658 (G = q × prix ; repli « Aucun gisement connu disponible »).
- **Problème :** la règle 5 ne s'applique qu'à une cargaison pleine, ou non vide dans le système d'une station. La règle 6 reçoit donc aussi **une cargaison partielle hors du système d'une station**. Ce cas n'a rien de rare :
  - le minage s'arrête parce que le gisement se vide. Les PNJ s'entassent sur un gisement (l. 536), et le risque de la l. 1264 en parle ;
  - le joueur interrompt un minage par un autre ordre.

  Or G = q × prix de s ne compte que le minerai à extraire. La cargaison déjà à bord est oubliée, alors que `v` la vendra à s avec le reste (`sell_all`). Trois effets :
  1. **Cargaison mêlée :** avec 40 `ore_a` à bord et un conseil de miner `ore_b`, la station du cycle est choisie sur le seul prix de `ore_b`. La valeur des 40 `ore_a` à cette station n'entre pas dans le choix.
  2. **Presque pleine :** à 99/100, q ≤ 1 pour tous les gisements. La règle peut conseiller « Aller miner ore_b à system_k (2 sauts) » pour une seule unité. Aller vendre tout de suite n'est jamais envisagé.
  3. **Aucun gisement candidat :** le cadre affiche « tous les gisements connus sont vides : attendre leur régénération », alors que le joueur a une cargaison à vendre.
- **Conséquence :** le guide conseille mal, ou pas du tout, dans un cas courant. Le « meilleur gain par tick » (objectif 18, l. 181 ; AH) est faux dès que la cargaison n'est pas vide.
- **Proposition :**
  - dans la règle 6, G(g, s) = V_cargaison(s) + q × prix de s pour le minerai de g, avec V_cargaison(s) au sens de la règle 5 ;
  - quand la cargaison n'est pas vide, ajouter aux candidats « aller vendre à s », avec G = V(s) et T = t(s) (ou t(s) + 1 si s est ici, comme la règle 5) ;
  - réserver le repli « Aucun gisement connu disponible » à une cargaison vide ; sinon, appliquer la règle 5 ;
  - ajouter à `test_guide.py` trois cas : cargaison mêlée, 99/100, et cargaison non vide sans gisement candidat.

### Majeur 2. Le plan annoncé n'est pas celui que le guide conseille ensuite : les règles 5 et 6 ne mesurent pas le gain de la même façon

- **Passages :** l. 657 (règle 5 : V(s) ÷ (t(s) + 1)), l. 658 (règle 6 : G ÷ T, avec T qui compte l'approche, le minage et la vente ; « puis vendre à [station] » ; « cycle complet : [durée de T] »), l. 1654 (le scénario choisit une graine « dont ce gisement reste conseillé une fois le vaisseau arrivé »), l. 1198-1205 (AH), l. 1264 (risque).
- **Problème :**
  1. **Le guide change de station en cours de cycle.** Au départ, la règle 6 choisit la station en comptant l'approche et le minage. Une fois la cargaison pleine, la règle 5 la rechoisit en ne comptant que le trajet. Exemple, avec les prix de `tunables.toml`, `jump_ticks` = 400 et q = 100 :
     - le vaisseau est dans le système de S2 après une vente ; le gisement g (`ore_b`) est à 1 saut ; S3 (`ore_b` à 18) est à 2 sauts de g ; S2 (`ore_b` à 12) est à 1 saut de g ; on suppose les autres gisements moins rentables ;
     - règle 6 : (g, S3) donne 1 800 ÷ 1 300 ≈ 1,38, et (g, S2) donne 1 200 ÷ 900 ≈ 1,33. Le guide dit « Aller miner ore_b […] ; cycle complet : 1 300 ticks » et, à l'arrivée, « puis vendre à S3 » ;
     - cargaison pleine, règle 5 : S3 donne 1 800 ÷ 801 ≈ 2,25, et S2 donne 1 200 ÷ 401 ≈ 2,99. Le guide dit « Aller vendre à S2 ».
  2. **Le guide peut changer de gisement à l'arrivée, même sans rien apprendre.** Révéler le stock à l'arrivée peut changer le conseil, ce qui est inévitable. Mais la géométrie seule le peut aussi : la durée d'approche, comptée au départ, ne compte plus à l'arrivée. Un cycle à fort gain choisi de loin peut alors céder la place à un cycle moins payé mais plus court depuis le nouveau point. Exemple :
     - le vaisseau part d'un système A sans station ; g (`ore_b`, vente à S3, à 2 sauts de g) est à 1 saut ; g″ (`ore_a`, dans le système de S2, qui le paie 12) est à 2 sauts, par g ;
     - au départ, (g, S3) donne 1 800 ÷ 1 300 ≈ 1,38, contre 1 200 ÷ 900 ≈ 1,33 pour (g″, S2) ;
     - arrivé en g, (g, S3) donne 1 800 ÷ 900 = 2,0, contre 1 200 ÷ 500 = 2,4 pour (g″, S2). Le guide l'envoie ailleurs.
  3. Le document ne nomme ce comportement nulle part. Seule la condition de graine du scénario du point 23 octies le contourne.

  Bonne nouvelle : à information fixe, la règle 6 ne peut pas faire d'aller-retour entre deux gisements. Si chacun battait l'autre une fois le vaisseau sur place, on aurait (q + d_g,s)(q + d_g″,s″) > (d + q + d_g,s)(d + q + d_g″,s″), ce qui est impossible pour d > 0. Voir la section 4.
- **Conséquence :** le joueur suit le conseil, et le guide le contredit en cours de cycle. Le « cycle complet » affiché n'est pas celui qui sera conseillé. C'est le risque « Prochaine étape trompeuse » (l. 1264), mais avec une cause que ni le risque ni AH ne citent, et que les tests ne verront pas, puisque le scénario choisit sa graine pour l'éviter.
- **Proposition :**
  - **Station (sans mémoire, peu coûteux) :** dans la règle 6, la station d'un gisement g est celle que la règle 5 choisirait depuis g, avec la cargaison prévue après le minage. Le plan annoncé est alors celui que la règle 5 confirmera, et le minage ne fait plus changer de station.
  - **Gisement :** au choix, avec ses raisons datées dans AH :
    - (a) `ClientModel` garde le gisement conseillé (`planned_deposit`), effacé à la vente ou quand le gisement est connu vide ; à l'arrivée, la règle 6 conseille de le miner s'il convient encore ;
    - (b) accepter la révision, l'écrire dans AH et dans le risque de la l. 1264, et l'afficher (« conseil révisé : … »).
  - **Tests :** ajouter les deux exemples ci-dessus à `test_guide.py`. Dire au point 23 octies si la condition « reste conseillé une fois arrivé » ne vise plus que la révélation du stock.

### Majeur 3. Au zoom 2, les étiquettes sont coupées au milieu d'un nombre et affichent de faux prix et de faux stocks

- **Passages :** l. 638 (« chaque ligne est coupée avant la première case déjà occupée »), l. 624 (boîte de 0,125 de large).
- **Problème :** deux systèmes voisins en largeur sont souvent juste à la distance de séparation : la passe de séparation les y pousse. Au zoom 2 :
  - en 120 × 36, l'écart minimal vaut 0,125 × 2 × 50 = 12,5 colonnes. L'étiquette commence après le gisement, 4 colonnes après la case d'ancrage, et compte 9 ou 10 caractères (`system_12`, `S1 a10 b15`). Elle est coupée vers la 8e ou 9e colonne : « S1 a10 b1 » ;
  - en 100 × 30, l'écart tombe à environ 10 colonnes, et l'étiquette est coupée vers la 6e colonne : « S1 a10 » ou « S1 a1 ». Le stock « 20000 » devient « 200 ».

  Une coupe au caractère près produit une **valeur fausse**, et non une valeur tronquée visible.
- **Conséquence :** le joueur lit sur la carte un prix ou un stock faux. La carte contredit le cadre « Stations », justement sur l'information de l'objectif 12 (« à quel prix chaque station le rachète »). Le test « étiquettes coupées » (l. 1680) passerait.
- **Proposition :**
  - couper à la fin d'un mot entier (`system_5`, `S1`, `a10`, `b15`, `20000`) et marquer la coupe par « … », ou ne pas dessiner une ligne qui ne tient pas entière ;
  - tester un mot coupé dans `test_map_view.py` ;
  - fixer aussi les trois lignes des étiquettes, et leur place pour un système sans gisement (détail d7).

### Majeur 4. Les boîtes sont calées sur une hauteur de carte que le document ne fixe pas ; à 30 lignes, le `▲` du haut sort de la grille

- **Passages :** l. 604 (« les places comprennent les bordures »), l. 609 (carte, lignes 3 à 29), l. 618 (entre 100 × 30 et 120 × 36), l. 623-624 (marge de 0,05 ; boîte 0,125 × 0,15 « avec une case de marge, au zoom 1 en 100 × 30 »), l. 630 (le carré occupe toute la hauteur, deux pixels par ligne), l. 637 (vaisseaux sur la ligne au-dessus de la pastille), l. 626 (test de la grille).
- **Problème :** à 30 lignes, le cadre de la carte fait 21 lignes. La hauteur utile est de 19 lignes s'il a une bordure, comme le dit la l. 604, soit 38 pixels ; de 21 lignes sans bordure, soit 42 pixels. Les constantes valent exactement 5 ÷ 40 et 6 ÷ 40 : elles supposent 40 pixels. À 38 pixels :
  - **largeur :** 0,125 × 38 = 4,75 pixels. Après arrondi, deux systèmes peuvent être à 4 colonnes l'un de l'autre, donc collés (« ␣5◆a12◆b »), sans la case de marge promise ;
  - **hauteur :** 0,15 × 38 = 5,7 pixels. Deux systèmes peuvent être à 2 lignes l'un de l'autre : le `▲` du système du bas touche la pastille de celui du haut ;
  - **bord haut :** y = 0,05 donne 1,9 pixel, donc la ligne 0. Le `▲` irait en ligne −1, hors de la grille. Après la normalisation, le système le plus haut est à y = 0,05 chaque fois que la boîte englobante est plus haute que large, soit environ un monde sur deux. Si c'est le système du joueur, **son vaisseau n'est pas dessiné** au zoom 1.

  Le test de la l. 626 ne vérifie que l'absence de case partagée entre deux systèmes. Il ne voit ni la marge absente ni une case hors de la grille.
- **Conséquence :** à la taille minimale, le vaisseau du joueur peut être invisible sur la vue initiale. Or l'objectif 17 dit que « la position du vaisseau se voi[t] ». La promesse de marge (l. 624) est fausse, avec des tests verts.
- **Proposition :**
  - fixer la taille utile de la carte en 100 × 30 et en 120 × 36 (bordure ou non) ;
  - donner aux boîtes de la marge par rapport au cas le plus serré : au moins 5 pixels de large et 6 pixels de haut à la hauteur réelle, soit environ 0,135 × 0,16 pour 38 pixels ;
  - ramener chaque position dans [0,05 ; 0,95 − largeur] × [0,05 + hauteur ; 0,95], pour que la boîte entière tienne dans le carré ;
  - ajouter au test de la grille deux vérifications : chaque case d'un système (pastille, gisement, `▲`) est dans la grille ; deux systèmes sont séparés par au moins une case.

---

## 3. Détails

| N° | Passage (ligne) | Problème | Conséquence | Proposition |
| :-- | :-- | :-- | :-- | :-- |
| d1 | l. 657 | Avec les prix actuels, « ici » gagne toujours à une station : V ÷ 1 contre au plus 2,25 × V ÷ 401. La formule ne compare des stations qu'hors station. | La règle a l'air de comparer, sans le faire. | Le dire, et tester le cas « cargaison pleine hors station ». |
| d2 | l. 657 | « La taxe ne change pas ce classement » : la taxe est arrondie vers le haut, à chaque vente, et chaque minerai a sa vente. | Vrai à un ou deux crédits près ; une égalité peut se créer ou se défaire. | « à l'arrondi près ». |
| d3 | l. 658 | Gisement hors de portée, au stock inconnu : q = capacité libre, hypothèse optimiste ; « cycle complet » s'affiche sans réserve. | Les gisements hors de portée sont favorisés ; la durée affichée peut être fausse. | Ajouter « (stock inconnu) » au détail ; le citer dans le risque de la l. 1264. |
| d4 | l. 658 | « Miner ici » : pas de « au plus » quand un autre vaisseau est visible, alors que la règle 4 le met. Avec la station dans le même système, le texte donne « (0 sauts) ». | Incohérence avec la règle 4 ; texte maladroit. | Même mention « au plus » ; « puis vendre ici ». |
| d5 | l. 658, l. 170 | T ne compte pas les ticks des ordres : environ 4, chaque ordre entrant au tick suivant. L'objectif 12 vérifie que « chaque durée affichée est égale » aux ticks observés. | Le test de l'objectif 12 échouerait sur T. | Dire que T est une estimation, hors de ce test. |
| d6 | l. 658 ; `mettre_a_jour` | Comme `mettre_a_jour` se vide quand tous les gisements y sont, « Aucun gisement connu disponible » n'arrive que si tous les gisements sont à portée et vides. Sinon, le guide renvoie vers un gisement déjà vu vide. | Comportement juste, comme le PNJ, mais non dit ; le texte « attendre leur régénération » ne sera presque jamais vu. | Le dire au point 7 ter et dans le risque de la l. 1264. |
| d7 | l. 638 | Les trois lignes des étiquettes ne sont pas fixées (pastille et deux lignes dessous ?). Rien n'est dit pour un système sans gisement. | Choix implicite pour l'agent de code ; collision possible avec la ligne des `▲`. | Fixer : ligne de la pastille et deux lignes dessous ; à droite de la pastille sans gisement. |
| d8 | l. 664, l. 612, l. 618 | Une ligne par minerai, avec jusqu'à 3 gisements : environ 55 caractères, pour 45 colonnes utiles. À 100 × 30, « Stations » n'a que 4 lignes utiles, pour 4 à 5 lignes de contenu. Seule la liste des destinations défile. | Gisements coupés : information de l'objectif 12 perdue. | Retour à la ligne et défilement de « Stations » ; tester le pilote en 100 × 30. |
| d9 | l. 616, l. 639 | Bulle de 36 × 6 : la ligne de distance (« 2 sauts, 800 ticks (≈ 40 min à 3 s) ») fait environ 35 caractères pour 34. Près du bord droit ou bas, la bulle déborde. | Bulle coupée. | Deux lignes pour la distance ; bulle placée de l'autre côté du pointeur près des bords. |
| d10 | l. 180, l. 1680 | « distance minimale entre deux systèmes » reste dans la vérification de l'objectif 17 et dans les tests du point 23 decies. | Critère dépassé par les boîtes. | « aucun recouvrement des boîtes, ni dans la grille ». |
| d11 | l. 1670 | `test_palette.py` ne cite que `CONTRAST_PAIRS`. | `GRAPHIC_PAIRS` risque de rester sans test. | Ajouter `GRAPHIC_PAIRS` (3 pour 1). |
| d12 | l. 626 ; `ci.yml` ; `pytest.ini` | Les 2 000 graines, marquées `proprietes` et `lent`, tournent dans deux tâches : `-m proprietes`, puis `-m lent` dans `rejeu`. `pytest.ini` décrit `lent` comme les « fourchettes économiques ». | Deux à quatre minutes en double ; description fausse. | Marque `lent` seule pour les 2 000 graines ; corriger la description dans la pull request protégée. |
| d13 | l. 624, l. 1263 | Au-delà de 100 passes, les positions sont rendues telles quelles, et les graines au-delà de 2 000 ne sont pas vérifiées. | Recouvrement possible pour une graine de joueur. | L'écrire comme risque résiduel accepté. |
| d14 | l. 663 | Les couleurs des barres de progression (`█`, `░`) ne sont pas fixées et ne figurent pas dans `GRAPHIC_PAIRS`. | Contraste non testé. | Fixer leurs rôles et compléter `GRAPHIC_PAIRS`. |
| d15 | l. 652 | La mention « au plus » de la règle 4 bascule à chaque passage d'un PNJ dans le système. | Texte qui clignote pendant le minage. | Garder « au plus » jusqu'à la fin du minage, une fois un autre vaisseau vu. |

---

## 4. Questions posées : cas limites des règles 5 et 6

- **Cargaison mêlée :** la règle 5 la traite bien : V(s) somme les deux minerais, et `v` les vend tous. La règle 6 l'ignore : **Majeur 1**.
- **Minerai que la station ne rachète pas :** le cas n'existe pas à M1. Chaque station rachète chaque minerai (point 2, l. 334 et l. 368), et le décodage exige deux prix positifs (l. 411). Le graphe est connexe : toute station est accessible. Le dire en une phrase éviterait une garde inutile.
- **Stock visible nul :** il est exclu. La mention double `mettre_a_jour`, qui l'ajoute déjà à `seen_empty`, mais reste juste. Voir d6 pour le cas où l'ensemble se vide.
- **Gisement hors de portée au stock inconnu :** q = capacité libre, hypothèse optimiste, non signalée (d3). Le stock révélé à l'arrivée peut changer le conseil (**Majeur 2**, point 2).
- **Plusieurs ordres :** la règle 2 les joint par « ; ». Entre deux ventes de la file, `on_update` envoie la suivante avant le calcul de l'étape : la règle 2 reste en place, sans retour à la règle 5. C'est correct.
- **Égalités :** les départages sont complets et déterministes : plus petit T, puis plus petit identifiant de gisement, puis de station ; pour la règle 5, la plus proche, puis le plus petit identifiant. Les divisions sont sûres : T ≥ 1 puisque q ≥ 1, et t + 1 ≥ 1.
- **La règle 6 peut-elle osciller d'un tick à l'autre ?** Non, à l'arrêt. Le vaisseau ne bouge pas. Le score de chaque gisement à portée, G ÷ T = q·p ÷ (d + ⌈q ÷ r⌉ + d′), croît avec q, et q ne fait que baisser entre deux régénérations. Le conseil peut donc changer une fois quand deux scores se croisent, sans revenir en arrière avant une régénération. Il n'y a pas non plus d'aller-retour entre gisements à information fixe (preuve au **Majeur 2**). En revanche, le conseil **change sans information nouvelle** entre le départ et l'arrivée, ou entre la règle 6 et la règle 5 (**Majeur 2**). Le texte de la règle 4 clignote (d15).
- **Ce que l'observation permet de savoir (niveau 1, §5 ; proximité) :** les règles 0 à 6 ne lisent que l'observation et l'état du client : prix publics, voisins, stock à portée, `other_ships` à portée, `capacity`, `public_tunables`, `seen_empty`. Le caractère proportionnel de la taxe est une règle connue du code, pas une donnée : aucun canal nouveau. C'est conforme.

## 5. Séparation par boîtes et palette

- **Boîtes :** le principe est bon : la boîte suit l'encombrement réel, l'axe du plus petit déplacement est choisi, les positions sont ramenées dans le carré à chaque passe, et la séparation s'arrête au plus tard après 100 passes. En revanche, le calibrage à 40 pixels et le bord haut posent problème (**Majeur 4**).
- **Zoom 1 :** lisible en 120 × 36, avec des écarts de 6,25 pixels et de 3,75 lignes au moins. À la limite en 100 × 30 (**Majeur 4**).
- **Zoom 2 :** les étiquettes coupées sont trompeuses (**Majeur 3**).
- **Palette :** j'ai recalculé les valeurs. `trait_faible` et `trait_fort` sur `fond` donnent 3,66 et 5,68 ; `alerte` sur `cadre`, 5,07 ; `texte_attenue` sur `cadre_clair`, 5,29 ; `fond` sur `station`, 7,17. Tout est conforme. La portée ne repose jamais sur la seule couleur : chaque système à portée a au moins un lien plein vers le système du vaisseau. Il reste les barres de progression (d14).

## 6. Cohérence avec le reste

- **ADR 0006 :** cohérente. Rien de ce tour ne touche sa décision ni sa condition de révision.
- **AH et risque « Prochaine étape trompeuse » :** à compléter par les causes du **Majeur 2** (conseil révisé en route) et par l'optimisme sur les stocks inconnus (d3).
- **Volet B ter :** le découpage est cohérent. Il faut ajouter à `test_guide.py` les cas des Majeurs 1 et 2, à `test_map_view.py` le mot coupé et les cases hors de la grille, et corriger les mentions « distance minimale » (d10).
