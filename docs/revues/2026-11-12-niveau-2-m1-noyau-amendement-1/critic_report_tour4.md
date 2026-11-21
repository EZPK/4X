# Étape 7, tour 4 — Revue critique (amendement 1, après les corrections du tour 3)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, spécification (lignes 1 à 1091) ; pour la conception, aussi le plan détaillé, points 26 et 27.
*   **Relecteurs :** `egm-design`, `egm-structural`, `egm-style`, tous sans contexte ; tous ont rendu leur rapport.
*   **Bilan :**
    - conception : 0 bloquant, 3 majeurs, 6 détails ;
    - structure : 0 bloquant, 1 majeur, 11 détails (plus deux remarques sur le plan détaillé) ;
    - style : 0 bloquant, 7 majeurs, 17 détails.

    Le tour n'est pas propre au sens d'EGM. Avec cinq tours au plus, deux tours propres consécutifs ne sont plus possibles.
*   **Vérifié par l'agent :**
    - règle 3 du PNJ relue (Technical Plan, point 7) et portée de la proximité (Technical Plan, point 5) : la boucle à un seul gisement vide du constat conception-M1 est réelle ;
    - essai hors du dépôt (génération écrite d'après le document) : dans leur cycle établi, tous les PNJ minent le même gisement dans 7 766 graines sur 10 000, et deux gisements dans 2 171 ; graine 1 : gisements 6, 4, 6, 4, 6 ;
    - 20 000 ÷ (5 × 100 ÷ 101) = 4 040 ticks pour vider un gisement colocalisé miné par cinq PNJ ; 10 000 − 97 = 9 903, d'où 2 × 9 903 = 19 806 par la méthode.

## Majeurs

- **[conception-M1] La règle « viser l'autre minerai » (G2, confirmée par E4) fait pire que rien avec un seul gisement vide.** B1, gisement de `ore_b` vide dans le système X d'une station ; A1, gisement de `ore_a` le plus proche de X, à deux sauts ou plus ; B1 est aussi le gisement de `ore_b` le plus proche de A1. Le PNJ va de X à A1, n'y mine pas (il revise `ore_b`), retrouve B1 inconnu car hors de portée, revient à X, et recommence, sans miner, jusqu'à la régénération. Sans la règle, il irait miner B2. Le risque accepté décrit le cas à deux gisements vides, pas ce cas, qui est le plus fréquent.
- **[conception-M2] Tous les PNJ convergent vers un même gisement.** La règle 2 envoie toute cargaison pleine de `ore_b` à la station qui le paie le mieux ; de là, la règle 3 vise le même gisement pour tous. Seuls les PNJ retenus par la règle 1 (vente sur place) y échappent. Le document ne parle que des PNJ partis de la même station. Un gisement colocalisé miné par cinq PNJ se vide en environ 4 040 ticks.
- **[conception-M3] Le refus de l'outil (borne basse nulle) n'a ni ligne au tableau des risques ni parade décidée**, alors que l'essai lui donne environ une chance sur trois par monde, que la graine 1 peut basculer sur le code livré ou après un changement de réglage, et que le contrôle est obligatoire.
- **[structure-1] L'introduction des alternatives J à AA est rangée sous le titre de l'alternative I**, alors que le tableau des amendements cite « introduction des alternatives ».
- **[style-1] « Rang » a trois sens** (rang de station à partir de 0, « ligne de rang égal à l'identifiant », rang de la carte) : à la lettre, la station 1 prendrait la deuxième ligne de prix.
- **[style-2, structure-2] Règles de portée incomplètes** : marque dans l'intitulé en gras d'un objectif ou d'une puce, marque en tête d'un paragraphe sans titre ni intitulé, marque dans la première cellule d'une ligne de tableau ; conflit à la l. 229 entre « après un titre » et « seule sur sa ligne ».
- **[style-3] La règle de rédaction ne cite que les décisions du 2026-11-12**, alors que le document en applique du 2026-11-15 et du 2026-11-21.
- **[style-4] L'objectif 14 dit qu'aucun autre canal n'existe**, alors que l'objectif 6 décrit deux exceptions locales.
- **[style-5] Entrée acquitte une alerte « sans autre effet » et confirme aussi les saisies** ; aucune priorité n'est dite.
- **[style-6] Règle 3 du PNJ mal ordonnée** : l'exception avant la règle, « cette règle » ambigu, « l'autre minerai » sans repère.
- **[style-7] « Où aller » promis pour tout refus** (Overview, CUJ A), alors que seuls les refus liés à un lieu le donnent.

## Détails

- **Conception :** 19 802 cité au lieu de 19 806 donné par la méthode (l. 1077) ; refus de la maquette (t803) impossible avec la touche `m` ; la règle 1 vend à la station du système quel que soit son prix (l. 194, 294) ; « réellement minée » à lire « minée dans le déroulé » (point 27) ; l. 612 ne cite que deux des trois cas de refus ; justification de la l. 636 inexacte ; objectif 1, « la station », non marqué.
- **Structure :** l. 10, Open Questions et point 11 modifiés ou déplacés sans marque ; l. 149-150 (marque d'ajout qui couvre une marque de remplacement) ; l. 429 (marque au milieu d'un groupe nominal) ; deux formes de marque dans les cellules de tableau et une forme hybride « remplacé…, voir … : … » absente de la légende ; titre de la section CUJ non marqué ; « alternative R » du niveau 1 à préfixer ; renvoi périmé de la l. 482 ; « code d'origine » inexact pour la touche `v` (correctif de la PR #22) ; intitulé « Avantages d'un client synchrone attaché » ; plan détaillé, points 20, 22, 23 et 26 : forme « (amendement 1) » au lieu de « Proposed Changes (amendement 1, ajout) ».
- **Style :** convention « ajoute des passages » ; préséance circulaire ; redite « en revue » ; « rendu très simple » ; parenthèse sur le stock (l. 80) ; jugement non attribué (l. 111) ; « surtout » deux fois à l'objectif 5 ; définition de la portée ; l. 161 ; place de « sans touche de vitesse » (l. 164) ; « ticks de retard sur le tick suivant » ; « joueur » pour « personnage », « à une station », deux choix pour un geste ; dates absentes (l. 291-294) ; l. 378 ; « un type qui porte un événement », « compterait », « arrêt à la prochaine alerte », « liste des systèmes », file de vente ; l. 636, l. 986, « plus de 1 600 ticks ».
