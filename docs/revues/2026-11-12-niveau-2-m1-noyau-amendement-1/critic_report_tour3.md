# Étape 7, tour 3 — Revue critique (amendement 1, après les corrections du tour 2)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, spécification (lignes 1 à 1080) ; pour la conception, aussi le plan détaillé, points 26 et 27 (bornes d'économie, réécrites après la décision E3).
*   **Relecteurs :** `egm-design`, `egm-structural`, `egm-style`, tous sans contexte ; tous ont rendu leur rapport.
*   **Bilan :**
    - conception : 0 bloquant, 3 majeurs, 5 détails ;
    - structure : 0 bloquant, 2 majeurs, 11 détails (plus une remarque sur le plan détaillé) ;
    - style : 0 bloquant, 5 majeurs, 22 détails.

    Le tour n'est pas propre au sens d'EGM.
*   **Chiffres revérifiés par l'agent** (essai hors du dépôt, génération écrite d'après le document, avec `keyed_below` du noyau) :
    - un PNJ dans le système d'une station (d = 0) a une période réelle de 101 ticks : au plus ⌊10 000 ÷ 101⌋ = 99 périodes, soit 99 × 100 + 1 = 9 901 unités par fenêtre ; deux PNJ, au plus 19 802 < 20 000 ;
    - la méthode actuelle met pourtant ces deux PNJ au repli (2 × 101 × 100 = 20 200 ≥ 20 000) : sur la graine 1, émission bornée entre 45 000 et 361 500 ; la borne basse vaut 15,7 % de l'émission réelle (287 100 à 294 000), et les PNJ au repli produisent 82,8 % de celle-ci ;
    - avec le plafond proposé (extraction d'un PNJ au plus `mining_rate` × (W − a_i × s_i), s_i ticks sans minage par cycle) et les cargaisons d'avant le cycle établi comptées une à une : graine 1, aucun PNJ au repli, émission entre 277 800 et 300 900 ; graines 1 à 10 000, au moins un PNJ au repli dans 3 479, tous dans 3 366 (au lieu de 4 675 et 3 518) ;
    - la borne basse de groupe proposée au constat conception-M2 ne ramène les graines à borne basse nulle que de 3 366 à 2 407 ;
    - règle 3 du PNJ (Technical Plan, point 7) relue : la boucle B1 → A1 → B2 → A2 du constat conception-M3 est réelle.

## Majeurs

- **[conception-M1] Repli à tort de deux PNJ dans le système d'une station.** Le critère d'épuisement compte b_i = ⌈W ÷ c_i⌉ + 1 cycles et ignore le tick de vente de chaque cycle : deux PNJ à d = 0 passent au repli alors que leur gisement ne peut pas se vider. Les bornes de la graine 1 ne sont plus « serrées » comme le promet le Technical Plan, point 9. Correction : plafonner l'extraction par les ticks sans minage, compter les cargaisons du transitoire une à une, refaire l'essai.
- **[conception-M2] Rien ne protège contre une borne basse nulle**, défaut qui a fait rejeter l'option géométrique de l'alternative V ; un tiers des mondes y tombe. En CI, les empreintes du registre (compteurs cumulés par motif, relevés tous les 1 000 ticks) fixent déjà chaque grandeur des fenêtres de 10 000 ticks : le contrôle économique effectif a lieu à la régénération. La consigne du plan détaillé, point 27, n'interdit pas de modifier le calcul des bornes.
- **[conception-M3] La règle « sur un gisement vide, viser l'autre minerai » déplace l'aller-retour sans le rompre.** Pour cette décision seulement : arrivé au gisement de l'autre minerai, le vaisseau revient au minerai visé et repart vers un autre gisement inconnu. Boucle à quatre étapes sans minage jusqu'à la régénération. L'affirmation « ce qui rompt l'aller-retour » (risques) est fausse.
- **[structure-1, style-1] Du texte de l'amendement échappe aux règles de portée** : Overview (l. 65-85), The Problem (l. 98-113), introduction du Technical Plan et son schéma (l. 223-246), l. 813-834 ; règle 4 de la légende ambiguë (l. 40) ; bloc des conventions non marqué.
- **[structure-2] Marques de remplacement employées pour des ajouts** (l. 419) : à la lettre, l'observation n'aurait plus de résultats d'ordre et `observe` ne lirait plus l'état.
- **[style-2] Seconde marque de la l. 17** : sa portée est ambiguë, et une lecture fait disparaître le CUJ 4 et l'antécédent de « les ».
- **[style-3] « Le PNJ ignore le temps de trajet »** (l. 188, 286) contredit sa règle, qui choisit le gisement par la distance.
- **[style-4] Nombre de lignes de `station_ore_prices`** énoncé de trois façons (l. 367, 379, 929).
- **[style-5] Critère du repli vague** (l. 603), et prévision de l'épuisement (avant la partie) confondue avec son relevé (après) (l. 604, 1057).

## Détails

- **Conception :**
  - N4 : la graine affichée dans la barre d'état est un second canal local non déclaré (Technical Plan, point 6, ne cite que `set_period`) ; `CharacterCreated` public révèle la position de départ de chaque vaisseau (l. 450) ;
  - N5 : R n'est pas une borne (un PNJ au repli peut miner plus longtemps sur un autre gisement), et le texte ne dit pas que l'ensemble des PNJ au repli ne fait que croître ;
  - N6 : le calcul suppose `regen_ticks` = W sans le vérifier ;
  - N7 : l'outil ne vérifie pas que `scripted_miner` est en version 2 ;
  - N8 : la carte qui défile peut cacher l'emplacement d'un gisement, alors que l'objectif 12 vérifie qu'il figure à l'écran ; la contre-pression ne couvre pas les files de relais des PNJ.
- **Structure :**
  - 3 et 4 : marques d'ajout en milieu de puce qui couvrent du texte d'origine (l. 426-440, tableau des événements compris ; l. 143-144, marque redondante) ;
  - 5 : schéma des l. 225-246 et phrase de la l. 834 hors de portée (fusionné avec structure-1) ;
  - 6 : marque de la l. 263 placée après le mauvais membre de phrase ;
  - 7 : la « Vue d'ensemble » (l. 223) redéfinit une seule forme de marque au lieu de renvoyer à la légende ;
  - 8 : tableau des amendements sans l'introduction du Technical Plan ; en-tête daté du seul 2026-11-12 ;
  - 9 : alternatives J à AA sous deux formes (avantages et inconvénients, ou liste d'options), non annoncées ;
  - 10 : « Given / When / Then » absents de l'exception de langue (l. 10) ;
  - 11 : « la ligne k » employée avant la définition de k (l. 302) ;
  - 12 : l'exception de `set_period` à l'objectif 6 n'est pas signalée à l'objectif ;
  - plan détaillé : titres des points 23 bis à 23 sexies sans marque.
- **Style :** durées de cycle données comme une fourchette (l. 143, 1045) et « plus de 1 600 ticks » sans « carte d'origine » (l. 1003) ; « 6 000 unités » sans calcul (l. 1008) ; « Vue d'ensemble » inexacte (l. 223) ; intitulé de ligne mal cité (l. 260) ; « la ligne k » (l. 302) ; variables i et k mêlées (l. 347-348) ; « un ordre par saut » (l. 371) ; « le décodage » non défini (l. 379, 627) ; « Sinon » ambigu (l. 449, 997) ; cause du protocole 2 donnée de deux façons (l. 451-452) ; format de la ligne « période initiale » de `speed.jsonl` absent (l. 486) ; règle du PNJ à resserrer (l. 503-505, 564) ; « pour cette décision seulement » contre « pour sa décision suivante » (l. 505, 1058) ; « tous les PNJ visent `ore_b` et s'entassent » trop fort (l. 507, 984) ; parenthèse de la mise en page incomplète (l. 541) ; « ordre manuel » non défini (l. 559, 1048) ; « exercer l'épuisement » (l. 268, 604) ; force de l'affirmation sur l'épuisement (l. 287, 604) ; dates de l'en-tête ; termes vagues (l. 914, 995, 184 et 1074, 200, 1066) ; formulations à reprendre (l. 110, 1032, 155, 158 et 1056, 42).
