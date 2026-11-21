# Étape 7, tour 1 — Revue critique (amendement 1)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, spécification (lignes 1 à 1039).
*   **Relecteurs :** `egm-design` (feature-spec-standard), `egm-structural` (feature-spec-standard), `egm-style` ; tous sans contexte, tous ont rendu leur rapport.
*   **Bilan :**
    - conception : 1 bloquant, 8 majeurs, 7 détails ;
    - structure : 0 bloquant, 7 majeurs, 9 détails ;
    - style : 0 bloquant, 14 majeurs, 22 détails.

Les constats sont regroupés et dédoublonnés ci-dessous. Leur traitement est dans `goldfish_review_report.md`.

## Bloquant

- **[conception-1] Une station et un gisement dans le même système.** Les gisements sont tirés parmi tous les systèmes. La colocalisation se produit dans 84 % des mondes en moyenne (calcul refait par l'agent : 79 % pour 8 systèmes, 2 stations et 4 gisements ; 100 % pour 8, 3 et 6 ; 91 % pour 12, 3 et 6 ; 58 % pour 12, 2 et 4). Sur un tel système, le cycle « miner 100, vendre » dure environ 101 ticks, contre 800 ou plus avec un trajet : c'est une stratégie dominante, qui annule le temps comme ressource. Les PNJ peuvent y boucler à 3 à 5, et vider le gisement avant sa régénération. Cela rend fausses la ligne d'origine « la partie de référence ne vide aucun gisement », le risque « l'épuisement n'est jamais exécuté », et le calcul des bornes.

## Majeurs

- **[conception-2] La clé de chaque tirage de `world.generate` n'est pas fixée** (l'entité de chaque tirage, et la clé de `npc_count`). Deux tirages de même clé donnent la même valeur ; le monde ne serait pas reproductible d'une implémentation à l'autre. *(Recoupe l'étape 6, constat 5.)*
- **[conception-3] « Les classes de visibilité ne sont pas encodées » est faux pour les événements.** `Event.visibility` est encodé, et `State.last_tick.events` entre dans l'instantané et l'empreinte. Ajouter `nearby` casse la lecture par l'ancien code. C'est acceptable avant M5 seulement parce que les données sont régénérées.
- **[conception-4] Le filtre `NEARBY` n'est pas spécifié.** Il manque :
  - le système de référence d'un champ ;
  - le cas d'une entité dont seuls certains champs sont `NEARBY` ;
  - le cas d'un type sans `system_id` ;
  - l'état dont les positions comptent.
- **[conception-5] Canal d'inférence.** `DepositView.stock` reste public : avec `mining_rate` = 1, sa baisse compte les vaisseaux qui minent, où qu'ils soient. La ligne d'origine « position publique » n'est pas marquée.
- **[conception-6] Conséquences sur M4 et sur le déclencheur Rust non évaluées.** Le niveau 1 définit le pas et le verdict en ticks. Avec des sauts 80 fois plus longs, il faut 50 à 100 fois plus de ticks par décision.
- **[conception-7] Horloge à grande vitesse.** Plusieurs points ne sont pas spécifiés :
  - la valeur de la « vitesse maximale » ;
  - le comportement en surcharge ;
  - le réveil par l'événement ;
  - le débordement de l'arrêt « à la prochaine alerte », puisque la file du client n'est pas bornée.
- **[conception-8, structure-N9, style] La maquette de la carte contredit sa règle.**
  - Les liens 3–5, 5–7, 7–10 et 8–11 relient des colonnes voisines au même rang ; ils devraient être tracés.
  - Il n'y a aucun lien en plus.
  - Les colonnes font 7 caractères, et la barre d'état 83 caractères.
  - L'historique n'est pas chronologique.

  Sur le fond, avec la règle actuelle, une bonne part des liens finira en texte, ce qui recrée la carte en liste. Aucun critère ne le mesure. *(Recoupe les étapes 5 et 6.)*
- **[conception-9, structure-M3, M4] Passages devenus faux sans marque :**
  - les conventions (« le CUJ 1 et le CUJ 4 sans les adapter ») ;
  - la règle du minimum et « seule exigence ajoutée » ;
  - « copiés de `ore_prices` » et la phrase de `world.generate` ;
  - les deux refus et la création liés à une station unique ;
  - le tableau des événements (départ et arrivée publics) ;
  - « position publique » ;
  - le risque du bug volontaire sur le placement des sites ;
  - le paragraphe « La carte », marqué en entier alors qu'il contient le stock et la régénération, encore en vigueur ;
  - la marque du client, mal placée.
- **[structure-M1] Légende des marques incomplète.** Six formes de marques sont employées sans définition. Deux régimes coexistent (réécrit sur place, ou gardé et marqué), et aucune règle de préséance n'est donnée. *(Recoupe l'étape 6, constat 2.)*
- **[structure-M2, style-M3] Renvoi cassé** : « voir la ligne « fenêtres » plus bas » ; aucune ligne de ce nom n'existe.
- **[structure-M5] Statut de `station_ore_prices` inconnu** : la mention « proposition de l'agent de code » renvoie aux confirmations du 2026-11-08.
- **[structure-M6, style-M4] Renvois sans préfixe** dans les risques (« point 23 quater », « point 28 bis ») et « au plan détaillé » sans numéro.
- **[structure-M7] Interfaces nouvelles absentes du point 13** :
  - `distances`, `plus_abondant`, `textes.py`, `cadres.py` ;
  - la position de `public_tunables` dans `Observation` ;
  - les marques sur `OtherShipView`, `Visibility` et `world.py`.
- **Style :**
  - [M1] « propriétaire » employé pour le détenteur d'un vaisseau (aussi dans le glossaire et l'ADR 0005) ;
  - [M2] « le noyau » désigne aussi ce document ;
  - [M5] « plus de 99 % du temps en trajet » : le calcul donne environ 94 % ;
  - [M6] « 400 » écrit en dur avec « toujours » ;
  - [M7, M8] vocabulaire de la vitesse instable, « vitesse maximale » non définie ;
  - [M9] « rappel » pour *callback* ;
  - [M10] identifiants et noms de fichiers en français (`plus_abondant`, `modele.py`, `vitesse.jsonl`…), contre la convention du glossaire ;
  - [M11] « 4 à 6 gisements des deux minerais » ambigu ;
  - [M12] « trois choses », mais l'Overview en annonce cinq, et la proximité y est reléguée ;
  - [M13] le libellé « Raison du rejet » décrit souvent l'option retenue ;
  - [M14] mots relatifs au moment de la rédaction (« code actuel », « carte actuelle »).

## Détails

- **Conception :**
  - [10] `vitesse.jsonl` sans version ;
  - [11] une vérification de l'objectif 15 ne prouve rien ;
  - [12] pas de plancher de mutation pour les modules purs du client ;
  - [13] `distances` et `plus_abondant` dans le fichier d'une politique versionnée ;
  - [14] `set_period`, canal hors protocole à typer et à nommer ;
  - [15] place de `npc_count` à justifier ;
  - [16] table des risques sans colonne « Signal » ; estimation en minutes fausse avec `--periode` ; taxe inconnue avant la première vente ;
  - [17] formule de durée de minage ambiguë.
- **Structure :**
  - [N1] marques hétérogènes ;
  - [N2] marque dans un intitulé H2 du gabarit ;
  - [N3] tableau des amendements inexact (point 26, Additional Resources, introduction des alternatives, conventions) ;
  - [N4] introduction des alternatives sans marque ;
  - [N5] la promesse « chaque sous-section dit ce qu'elle complète » n'est tenue qu'en partie ;
  - [N6] termes du glossaire au point 13 au lieu du point 12 ;
  - [N7] formats de listes divergents ;
  - [N8] non-objectif en double (prix variables).
- **Style :** 22 détails : formes familières, accords, anglicismes, backticks, doubles négations, chiffres incohérents (1 600 contre 1 701), arrondis, etc.
