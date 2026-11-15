# Goldfish Annotated Review Report — étape 7, tour 2

**Target :** `docs/designs/niveau-2-m1-noyau.md` (spécification, lignes 1 à 1070 ; plus le plan détaillé quand un constat le cite) ; ADR 0004 et 0005.

**Source :** `critic_report_tour2.md`. Les doublons entre relecteurs sont fusionnés. Aucun constat ne rouvre un point réglé au tour 1 (contesté ou noté sans correction).

## À décider par le propriétaire (ESCALATE)

### [E3] Les bornes d'économie ne vérifient presque plus rien — conception-M2 — majeur
*   **Constat :** avec la formule géométrique du tour 1, la borne basse vaut 0 pour presque toute graine, et la borne haute est environ vingt fois trop lâche (909 000 contre environ 44 000). Le test ne détecte qu'une explosion de l'émission ; une panne qui arrête toute vente passe.
*   ***Suggestion :*** ESCALATE. Cette décision revient sur un choix fait à l'étape 5 (bornes indépendantes de la logique du PNJ). Deux réponses :
    - **(a) Accepter des bornes lâches, et l'écrire** dans l'objectif 5 et le Technical Plan, point 9 : la borne basse est en pratique nulle, et le test ne garde que la borne haute et l'égalité « destruction = somme des taxes arrondies ». Aucun calcul de plus.
    - **(b) Calculer les bornes à partir de la politique du PNJ**, à la régénération des références. L'outil déroule, sur le monde de la graine 1, le cycle établi de chaque PNJ selon la règle v2 (gisement visé, station de vente, distances), sans lire les ventes de la partie. Il en tire des bornes serrées, à une ou deux ventes près par PNJ et par fenêtre, et les range dans `reference.json`. C'est la méthode du document d'origine (calcul par cycle). Le calcul dépend de la politique du PNJ, mais seulement au moment de la régénération : le test, lui, rejoue le journal et reste valable si la politique change ensuite. Si le calcul prévoit qu'un gisement se vide (au moins trois PNJ en boucle sur un même gisement), l'outil le signale, et les bornes de ce PNJ s'élargissent à la formule géométrique.
*   ***Recommandation de l'agent :*** (b). Un contrôle obligatoire doit pouvoir échouer sur une vraie régression ; (a) le réduit presque à rien.

## Corrections proposées (PROPOSE FIX)

| N° | Sources | Gravité | Correction proposée |
| :-- | :-- | :-- | :-- |
| G1 | conception-M1 | majeur | « La partie de référence exerce ainsi l'épuisement » → « peut exercer » ; l'outil de régénération relève si un gisement s'est vidé ou si un départage a eu lieu, et le compte rendu le cite ; les scénarios et tests de propriétés à stock bas restent la parade principale. Le chiffre de 84 % est complété par celui qui compte pour les PNJ : 52 % des mondes ont un gisement de `ore_b` dans le système d'une station. |
| G2 | conception-M3 | majeur | Règle 3 du PNJ : un vaisseau qui se trouve sur un gisement vide du minerai visé vise l'autre minerai pour cette décision. Cela rompt l'aller-retour entre deux gisements vides. La parade du risque « gisement vide découvert à l'arrivée » est corrigée, et la limite de C_max (« jusqu'à G visites ») est revue en conséquence. |
| G3 | structure-1, 3, 7 ; style-3, 4 ; conception-N1 | majeur | Légende complétée. Une marque **placée après un titre ou une phrase d'introduction** couvre tout le paragraphe ou toute la liste qui suit. Une marque **seule sur sa ligne** couvre tout ce qui suit jusqu'au prochain titre. Formes ajoutées : « remplacé par l'amendement N : <texte en vigueur> » et marque en ligne « (amendement N : …) » dans un tableau. Les formes hors légende sont ramenées aux formes définies (« Précisé par… », « Remplacé » en phrase autonome, « Ces deux phrases… »). La préséance vaut pour toutes les formes de marque. |
| G4 | structure-2 ; style-5 | majeur | Règle de rédaction : marque de remplacement sur « n'en ajoute aucune sauf le seuil de mutation […] et ne redéfinit rien » ; « précisé » ne reste que sur la phrase qui reste vraie. |
| G5 | structure-4, 8 ; style-6 | majeur | Tableau des amendements : objectifs 5, 6 et 11 à 16, introduction des CUJ, alternatives J à AA. La puce de l'en-tête cite la visibilité par proximité. Les règles d'intégration citent le point 28. |
| G6 | structure-5 | majeur | Point 13 : marques en ligne sur `SystemView, DepositView, …` (stock de classe proximité, `Int64 \| None`), `OtherShipView` (`NEARBY`) et la signature d'`Observation` (`public_tunables`) ; marque sur la définition de l'observation au point 5. |
| G7 | structure-6 | majeur | Verification Plan : « fichiers nouveaux » au lieu de « fichiers modifiés » (erreur de l'agent). |
| G8 | style-1 ; conception-N2 | majeur | « Un seul cycle dure plus d'une heure » → « un cycle dure de 5 minutes (gisement dans le système d'une station) à plus d'une heure (gisement à deux sauts : 85 min) ». L'objectif 11 garde son protocole : enchaînement en accéléré, rythme sur un saut à la période nominale. |
| G9 | style-2 ; conception-N3 | majeur | « zéro ou une vente par PNJ ». |
| G10 | style-7 | majeur | Convention : « Un CUJ est un parcours utilisateur critique, défini par le niveau 1 (CUJ 1 à 6) ou par ce document (CUJ A, amendement 1) » ; le CUJ A est traduit par `ecrans.feature` (plan détaillé, point 23 ter). |
| G11 | style-8, 9, 10, 11, 12 | majeur | « un des vaisseaux de l'acteur » partout ; « un gisement dans le système d'une station » au lieu de « voisin » ; `DepositView.stock` « change de type » (seul `public_tunables` est nouveau) ; « Technical Plan, points 5, 6, 7 et 13 » ; « les empreintes de chaque tick, écrites par la tâche `rejeu` (environ 284 octets par tick, soit environ 284 Mo) ». |
| G12 | conception-N6 | détail | Décodage : `extra_links_max` ≥ 1 et `npc_min` ≥ 1. |
| G13 | conception-N7 | détail | `set_period` réveille la boucle, qui recalcule l'attente restante : un tick n'est joué tout de suite que si l'attente déjà écoulée dépasse la nouvelle période. `--periode` est décrit comme une option de lancement, qui sert aussi aux essais. Aux paliers rapides, la décision la plus ancienne d'un PNJ en retard gagne (règle du plus petit numéro) : écrit dans le risque « PNJ décalés ». |
| G14 | conception-N8 | détail | « Ces fourchettes dépassent celles d'origine du CUJ 1 » ; l'ADR 0004 : « le CUJ 1 reprend les fourchettes de systèmes, de gisements et de stations » ; règle générale hors de portée : une entité dont l'identité est de classe proximité disparaît, et un champ de classe proximité d'une entité publique vaut `None` ; le cadre Carte défile verticalement s'il dépasse sa hauteur. |
| G15 | structure-9 à 15 ; style, détails | détail | Corrections de forme groupées : position de la marque dans les titres (« … (amendement 1) » après l'intitulé), alternative AA sans « Retenu » en double, « Leurs valeurs sont au plan détaillé, point 17 » marqué, « voir ce point » → « voir le Technical Plan, point 11 », vérification de l'objectif 5 écrite en clair, « placement des sites » au point 29 marqué, listes recollées ; numérotation « bis » précisée (points insérés entre deux points existants ; CUJ et alternatives lettrés) ; « se règle par la durée réelle d'un tick » ; « l'enchaînement des étapes du cycle » ; « plus tard qu'au tick suivant » ; « mise en veille » ; « portée » défini à la première occurrence (le système d'un des vaisseaux de l'acteur et ses voisins) ; correspondance minerai 1 = `ore_a`, minerai 2 = `ore_b` ; troisième personne dans les maquettes ; `10_000` ; conditionnel pour les options rejetées. |

## Notés sans correction (DECLINE)

- **Conception-N4 (parcours en largeur dans `schema`) :** le coût affiché et la route réelle utilisent la même règle (plus court chemin, voisins par identifiant croissant), écrite au Technical Plan, point 2. Une fonction partagée dans `schema` serait un changement de `core` hors du sujet de l'amendement. Noté pour plus tard.
- **Conception-N5 (`npc_min` et `npc_max` dans `Tunables`) :** c'est un choix assumé, puisque la population fait partie du monde de référence. Le risque M4 reste noté au tableau des risques.
- **Style, autres détails :** subjectifs ou sans effet sur la compréhension.

## Contestés (CONTEST)

Aucun.
