# Goldfish Annotated Review Report — étape 7, tour 4

**Status: open** (2026-11-21). Décisions du propriétaire : E5 → (a), la règle « viser l'autre minerai » est retirée (« si les gisements sont vides, il n'y a plus rien à miner : les mineurs doivent faire autre chose, ou aller ailleurs ») ; E7 → (a), un tour 5, le dernier, puis l'étape 8. Les corrections J1 à J9 sont appliquées. E6 est sans objet : le propriétaire a ensuite décidé (2026-11-21) de simplifier les bornes d'économie (au moins une vente par fenêtre, plafond tiré de la carte, destruction égale à la somme des taxes ; plus de calcul par cycle, de repli ni de refus pour borne basse nulle), et de donner au PNJ une mémoire des gisements vus vides, effacée quand elle les contient tous (« si l'endroit où je mine est vide, je vais aller miner ailleurs »). Les deux sont écrits au Technical Plan, points 7 et 9, à l'objectif 5, aux alternatives V et W et au plan détaillé, point 27.

**Target :** `docs/designs/niveau-2-m1-noyau.md` (spécification, lignes 1 à 1091 ; plan détaillé, points 26 et 27).

**Source :** `critic_report_tour4.md`. Les doublons entre relecteurs sont fusionnés. E5 revient sur la décision E4 du tour 3, parce qu'un cas nouveau la contredit ; aucun autre constat ne rouvre un point réglé.

## À décider par le propriétaire (ESCALATE)

### [E5] La règle « viser l'autre minerai » aggrave le cas d'un seul gisement vide — conception-M1 — majeur
*   **Constat :** la règle ajoutée au tour 2 (G2) et confirmée par E4 fait boucler un PNJ sans miner dès qu'un seul gisement de `ore_b` est vide, si ce gisement est aussi le plus proche du gisement de `ore_a` où la règle l'envoie : arrivé là, il revise `ore_b`, ne voit plus le gisement vide (hors de portée) et y retourne. Sans la règle, il irait miner l'autre gisement de `ore_b` ; la boucle ne naîtrait que si les deux gisements de `ore_b` les plus proches étaient vides. L'erreur vient de l'agent, qui a proposé G2.
*   ***Suggestion :*** ESCALATE.
    - **(a) Retirer la règle**, et revenir à la règle 3 d'origine de la version 2 : aller au plus proche gisement du minerai visé dont on ne sait pas qu'il est vide. Le risque décrit le seul cas restant (deux gisements vides, aller-retour jusqu'à la régénération) ; un test de la politique couvre le cas d'un seul gisement vide (le PNJ va miner l'autre).
    - **(b) Donner à l'hôte des PNJ une mémoire bornée** des gisements vus vides, effacée à la régénération. La boucle disparaît, mais la politique n'est plus « sans mémoire », `NpcHost` change, et ses tests aussi.
    - **(c) Garder la règle**, et décrire dans le risque le cas d'un seul gisement vide.
*   ***Recommandation de l'agent :*** (a). C'est la plus simple, et elle fait mieux que la règle dans le cas le plus fréquent.

### [E6] Que faire quand l'outil refuse d'écrire les références — conception-M3 — majeur
*   **Constat :** l'outil refuse si la borne basse de l'émission est nulle (correction H2). D'après l'essai, environ un monde sur trois est dans ce cas. La graine 1 ne l'est pas, mais elle peut le devenir sur le code livré ou après un changement de réglage, et le refus bloque le volet C ou la régénération. Aucune parade n'est décidée.
*   ***Suggestion :*** ESCALATE.
    - **(a) Une règle de choix de graine écrite d'avance :** la partie de référence prend la plus petite graine ≥ 1 dont les bornes ont une borne basse non nulle ; l'outil la range dans `reference.json` et dans l'en-tête de `orders.jsonl`, et `test_rejeu.py` la relit au lieu de supposer 1. Le refus ne demande plus de décision, mais « la graine 1 » devient « la graine de référence » dans le document.
    - **(b) Le propriétaire décide au moment du refus** (changer de graine, de prix ou de règle). Une ligne au tableau des risques le dit, avec le chiffre de l'essai.
*   ***Recommandation de l'agent :*** (a). Les régénérations reviendront à chaque changement de réglage, jusqu'à M5 ; une règle fixe évite une décision à chaque fois, et reste vérifiable.

### [E7] La suite de la revue, plafond de cinq tours atteint de fait
*   **Constat :** EGM demande deux tours propres consécutifs, en cinq tours au plus. Le tour 4 n'est pas propre : les tours 4 et 5 ne peuvent plus être propres tous les deux.
*   ***Suggestion :*** ESCALATE.
    - **(a) Appliquer les corrections, faire un tour 5, le dernier, puis passer à l'étape 8,** en écrivant dans le résumé de la pull request que l'étape 7 n'a pas convergé, avec les constats restants.
    - **(b) Appliquer les corrections et passer à l'étape 8 sans tour 5.**
    - **(c) Relever le plafond** pour cet amendement, et continuer jusqu'à deux tours propres.
*   ***Recommandation de l'agent :*** (a). Le tour 5 vérifie les corrections de ce tour, qui touchent encore la politique du PNJ et les bornes ; les constats restants deviennent visibles dans la pull request.

## Corrections proposées (PROPOSE FIX)

| N° | Sources | Gravité | Correction proposée |
| :-- | :-- | :-- | :-- |
| J1 | conception-M2 | majeur | Technical Plan, point 7, alternative W et risque « Peu de PNJ visibles » : tous les PNJ que la règle 1 ne retient pas convergent vers le gisement de `ore_b` le plus proche de la station qui le paie le mieux ; dans l'essai, tous les PNJ minent le même gisement dans environ 78 % des mondes, et deux gisements dans environ 22 % ; un gisement colocalisé miné par cinq PNJ se vide en environ 4 040 ticks. |
| J2 | structure-1 | majeur | Introduction des alternatives J à AA déplacée juste après l'introduction de la section, avant l'alternative A, avec sa marque. |
| J3 | style-1 | majeur | « La ligne i de `station_ore_prices` pour la station d'identifiant i » partout ; « rang » garde ses deux autres sens, chacun dit à partir de 0. |
| J4 | style-2 ; structure-2 | majeur | Légende : une marque en tête d'un paragraphe, d'une puce, d'un objectif ou d'une ligne de tableau, ou dans son intitulé en gras, couvre tout ce paragraphe, cette puce, cet objectif (sous-listes et *Vérification* comprises) ou cette ligne ; une marque seule sur sa ligne suit toujours la règle « jusqu'au prochain titre ». |
| J5 | style-3, 4, 5, 7 | majeur | Règle de rédaction : décisions du propriétaire prises pour l'amendement 1, du 2026-11-12 au 2026-11-21. Objectif 14 : « hors des deux exceptions locales de l'objectif 6 ». Entrée : si une alerte est affichée, Entrée l'acquitte et ne confirme rien. « Et, pour un refus lié à un lieu, où aller » (Overview, CUJ A). |
| J6 | style-6 | majeur | Règle 3 du PNJ réordonnée (minerai visé, puis gisement, puis replis nommés), selon la décision E5. |
| J7 | conception, détails | détail | 19 806 par la méthode (19 802 au plus en réalité) ; refus de la maquette remplacé par un refus atteignable ; la règle 1 vend sur place, quel que soit le prix (l. 194, 294) ; « minée dans le déroulé » ; l. 612 renvoie aux trois cas de refus du point 27 ; l. 636 : `world.generate` place les gisements dans des systèmes distincts ; objectif 1 et Overview, livrable 2 : « une station », marqués. |
| J8 | structure, détails ; plan détaillé | détail | l. 10, Open Questions et point 11 : texte d'origine rétabli, ajouts marqués ; objectif 11 : *Vérification* hors de la portée de la phrase précisée ; l. 429 : marque après « des gisements », texte de substitution complet ; une seule forme dans les cellules de tableau, et forme « remplacé…, voir … : … » ajoutée à la légende ; marque « section ajoutée par l'amendement 1 » sous le titre des CUJ ; « niveau 1, alternative R » ; renvoi de la l. 482 vers la puce de remplacement du point 27 ; « code d'origine » : sauf la touche `v` (correctif de la PR #22) ; intitulé « Avantages : » à l'alternative X ; points 20, 22, 23 et 26 : forme « Proposed Changes (amendement 1, ajout) ». |
| J9 | style, détails | détail | Corrections de forme groupées : convention « ne renumérote jamais » ; préséance « passage ajouté ou réécrit » ; redite « en revue » retirée ; « pas de couleurs, pas de thèmes » ; parenthèse de la l. 80 ; jugement attribué au propriétaire (l. 111) ; objectif 5 sans « surtout » ; portée « les systèmes de ses vaisseaux et leurs voisins », un seul mot ; l. 161 découpée ; « sans touche de vitesse » déplacé ; « au deuxième tick suivant, ou plus tard » ; « personnage », « dans le système de la station », un seul choix ; dates des l. 291-294 ; l. 378 ; « un type qui porte un champ ou émet un événement », « permettrait de compter », « avancer jusqu'à la prochaine alerte », « liste des destinations », file de vente ; l. 986 sans renvoi au processus de revue ; « 1 701 ticks ». |

## Notés sans correction (DECLINE)

Aucun.

## Contestés (CONTEST)

Aucun.
