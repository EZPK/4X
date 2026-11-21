# Étape 7, tour 5 — Revue critique (amendement 1, dernier tour)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, spécification (lignes 1 à 1102) ; pour la conception, aussi le plan détaillé, points 23 bis à 23 sexies et 27.
*   **Relecteurs :** `egm-design`, `egm-structural`, `egm-style`, tous sans contexte ; tous ont rendu leur rapport.
*   **Bilan :**
    - conception : 0 bloquant, 1 majeur, 7 détails ;
    - structure : 0 bloquant, 0 majeur, 7 détails ;
    - style : 0 bloquant, 2 majeurs, 12 détails.

    Le tour n'est pas propre au sens d'EGM. C'est le cinquième et dernier tour (décision E7 du propriétaire) : l'étape 7 se termine sans deux tours propres consécutifs, et la pull request le dira.
*   **Vérifié par les relecteurs, sans écart :** borne haute de l'émission pour la graine 1 (5 × 101 × 100 × 15 = 757 500, valable quelle que soit la politique) ; épuisement d'un gisement colocalisé par cinq PNJ en environ 4 040 ticks ; colocalisation dans 84 % des mondes et avec `ore_b` dans 52 % ; durées, maquette, 18 codes de refus, contrats d'imports, versions.

## Majeurs

- **[conception-M1] L'affichage de la graine dans la barre d'état contredit le niveau 1, §5 (« il n'y a pas d'autre canal vers le joueur ») et l'ADR 0003, sans ADR.** La justification donnée (la graine d'une partie locale n'est pas secrète) ne répond pas à la règle du canal unique. L'affichage venait d'un objectif proposé au brainstorm, pas d'une décision du propriétaire.
- **[style-1] Objectif 5 : « dès la régénération » et « l'outil » ambigus** (régénération des références ou d'un gisement ; outil non nommé).
- **[style-2] « Seuls les prix restent publics »** se lit comme une règle de visibilité générale, alors qu'elle ne vise que les trois indices de la phrase d'origine.

## Détails

- **Conception :** l'exclusion de la première fenêtre n'a plus de raison avec des bornes larges ; `npc_min` et `npc_max` entrent dans `rules_version` sans que `step` les lise (choix déjà noté au tour 2, à écrire) ; le débordement d'un tick suppose que l'alerte est traitée dans la même étape que le retrait de la file ; paliers et `--periode` ; test « même monde sous deux `PYTHONHASHSEED` » impossible dans un seul processus ; un gisement régénéré hors de portée reste dans la liste des gisements vus vides ; politique avec mémoire face à « fonction observation → ordres » (niveau 1, §1).
- **Structure :** portée de la marque en ligne d'un bloc de code ; règle 5 limitée au paragraphe ; nouvelle interface de `FourxApp` absente du point 13 ; trois « la station » ou « un PNJ » d'origine sans marque ; introduction des propositions de l'agent de code contredite par la ligne « Prix des stations » ; titre de la section CUJ sans marque ; marques employées avant la légende.
- **Style :** bornes énumérées de façon inégale ; « trois systèmes en ligne » ; « partie de test », « partie d'essai », « partie normale », « univers » ; exception de langue Given / When / Then ; définition de la tâche de relais mal placée ; « sauf que » ; phrases à plusieurs idées ; « 78 % » et « la plupart des liens » ; lecture de « une station … dans 84 % des mondes » ; ordre des paires de liens ; « liste » contre `frozenset` ; libellés `S1` et double négation ; corrections de rédaction.
