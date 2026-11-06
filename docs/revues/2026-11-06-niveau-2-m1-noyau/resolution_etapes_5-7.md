# Résolution des constats des étapes 5 à 7

*   **Document :** `docs/designs/niveau-2-m1-noyau.md`, réécrit le 2026-11-06 (765 lignes).
*   **Rapports traités :** `zoom_out_report.md` (étape 5), `comprehension_report.md` (étape 6), `critique_report.md` (étape 7).
*   **Décisions du propriétaire (2026-11-06) :** le stock des gisements reste tel quel ; que la partie de référence ne vide jamais un gisement « n'est pas hyper grave ». Le propriétaire précise l'intention : un stock large, qui finit par se vider, oblige les mineurs, surtout à plusieurs, à changer de gisement ; recharge environ chaque semaine. Pour le reste : « tranche toi-même ».
*   **Choix de l'agent de code :** inscrits au Technical Plan, point 1, avec la mention « proposition de l'agent de code », à confirmer par le propriétaire au passage à Approved.
*   **Vérification :** script de contrôle (bornes recalculées, tableaux, renvois « plan détaillé, point N », termes interdits, chemins personnels, restes des anciens termes) : tout est conforme ; le seul « station PNJ » restant cite le niveau 1.

## Décisions de fond

| Constats | Issue | Où |
| :-- | :-- | :-- |
| É5 Major 1, É6 B1, C-M11 (stock jamais limitant, canari du départage inatteignable) | Valeurs gardées (propriétaire) ; vraie raison écrite ; épuisement et départage couverts par les scénarios et par des tests de propriétés à stock bas ; le bug volontaire `rejeu` vise le placement des sites, toujours exécuté ; alternative G corrigée ; seconde partie contrainte en Future Improvements | Technical Plan, points 1, 2, 10 ; plan détaillé, points 17, 19, 29 ; Risks |
| É5 Major 3, C-M12 (références dépendantes du PNJ et du serveur) | Journal des ordres de référence enregistré et rejoué par `step` seul ; alternative H | Technical Plan, points 1, 8 ; plan détaillé, points 26, 27 |
| C-B1, É6 Q12 et N19 (résultats d'ordre, refus de la réception) | Table « dernier tick » dans `State` ; refus de la réception journalisés, puis refusés par `step` avec leur code | Technical Plan, points 1, 2, 5, 6 |
| C-M2 (plusieurs ordres d'un vaisseau dans un tick) | Un ordre par vaisseau et par tick (plus grand numéro), « ordre remplacé » ; tout ordre sur un vaisseau en route refusé ; scénario « double vente » | Technical Plan, points 1, 2 ; plan détaillé, point 15 |
| É5 Major 2, É6 M3, S-M4, C-N1 (seuil de 80 %) | Inscrit comme proposition de l'agent de code, seule exigence ajoutée, avec sa raison ; porté au Technical Plan, point 10 | Technical Plan, points 1, 10 |
| C-M10 (concurrence) | Une seule boucle `asyncio`, files `asyncio.Queue`, mode sans horloge synchrone | Technical Plan, points 1, 6 |
| S-M8 (contrôle de nuit de la protection, promis par M0) | Reporté, en Non-Goals et Future Improvements ; raison : droit d'administration absent du jeton des GitHub Actions (à vérifier), donc nouveau secret | Non-Goals ; Technical Plan, point 1 |
| É5 Major 5, C-M14 (`tests-outillage` lance tout) | Limitée à `tests/outillage` ; l'écart avec le document de M0 (« devient `tests` ») est écrit et justifié | Technical Plan, point 1 ; plan détaillé, point 8 |
| Y-M1, Y-M2, Y-M3 (« champ », « tranche », « phase ») | « gisement » pour l'entité du jeu (ajouté au glossaire au point 3), « fenêtre de 1 000 ticks », « palier » et « volet » pour le plan | tout le document |

## Corrections sans choix de fond

- **Étape 5 :** Major 4 (`mutation.py` refuse une table `tool.mutmut`, test au point 10) ; Major 6 (point 11 bis, `test_workflows.py`) ; Major 7 (une seule fonction `fourx.tools.economie`) ; Nit 1 (borne de croissance de la masse monétaire, exclusion de la première fenêtre justifiée) ; Nit 2 (références produites sur le portable) ; Nit 3 (ligne « Découpage du jalon » retirée, alternative E réduite) ; Nit 4 (six bugs volontaires, un pour `mutation`) ; Nit 6 (`fetch-depth: 0`) ; Nit 8 (« scénarios compris » défini) ; Nit 9 (indicateur : `step` et `observe`, ordres hors mesure) ; Nit 10 (raison de l'horloge).
- **Étape 6 :** M1 (`tools` peut importer `server`) ; M4 (objectif 5) ; M5 (renvois, point 28 bis) ; M6 (chaîne dans l'ordre des identifiants, scénarios sur état explicite) ; M7 (identifiants entiers) ; M8 (tableau des classes d'événements) ; M9 (code de sortie 5 toléré jusqu'au palier 4, point 31 bis) ; M10 (rejeu retiré du scénario CUJ 1, ajouté à `rejeu.feature`) ; M11 (algorithme de départage) ; M12 (invariants énoncés, non-négativité rétablie) ; M13 (essai réel réécrit) ; M14 (budget initial, ordres d'administration) ; N1, N2, N3, N4, N5, N6, N7, N8, N10, N11, N12, N13, N14, N15, N16, N17, N18.
- **Étape 7, conception :** C-M1 (registre : soldes, écritures du tick, compteurs ; alternative I) ; C-M3 (politique idempotente, test) ; C-M4 ; C-M5 (encodage canonique de la clé, numéro d'essai, valeurs figées) ; C-M6 (liste fermée d'imports, fonctions intégrées interdites, exemption de `arith.py`) ; C-M7 (enveloppe, `seq`, identité d'un ordre, numéro répété) ; C-M8 (catégorie refusée à la réception, scénario) ; C-M9 (classe en métadonnée, test générique) ; C-M13 (première création de `rules-1`) ; C-M15 ; C-M16 (profil `hypothesis` sans hasard) ; C-M17 ; C-M18 ; C-M19 ; C-N2 (empreinte de l'encodage canonique de `Tunables`) ; C-N3 (graine hors de l'état) ; C-N4 ; C-N5 (`actor_kind` public) ; C-N6 (déduction acceptée, écrite) ; C-N8 (indicateur « dossier de travail modifié ») ; C-N9 ; C-N10 (création au tick 1).
- **Étape 7, structure :** S-B1 (section Risks & Mitigations) ; S-M1 (mention Given / When / Then retirée, CUJ du niveau 1 repris sans adaptation) ; S-M2 ; S-M3 ; S-M5 (entiers sur 64 bits dans les deux contrôles) ; S-M6 ; S-M7 (`test_versions.py`) ; S-N1 (volets en paragraphes) ; S-N2 ; S-N4 ; S-N5 ; S-N6 ; S-N8 ; S-N9 ; S-N10 ; S-N11.
- **Étape 7, style :** Y-M4 à Y-M17 ; Y-N1 (sauf « notebook ») ; Y-N2 en partie ; Y-N3 ; Y-N4 ; Y-N5 ; Y-N6 ; Y-N7 en partie ; Y-N8 ; Y-N9 ; Y-N10 ; Y-N11 ; Y-N12 ; Y-N13.

## Écartés (DECLINE)

- **É5 Nit 5** (une seule exécution de la partie de référence) : sans objet ; le contrôle rejoue maintenant un journal par `step` seul, rapide.
- **É5 Nit 7** (aligner `CLAUDE.md` sur les noms neutres) : `CLAUDE.md` ne donne que des exemples ; le Technical Plan, point 1, le dit. Pas de modification de `CLAUDE.md`.
- **C-N7** (contrat d'imports pour `fourx.__main__`) : le niveau 1 ne contraint pas la racine du paquet ; l'ajouter serait une exigence nouvelle.
- **S-N3** (doublons entre le tableau des décisions et le Technical Plan) : gardés en partie ; le tableau garde la décision et sa raison, ce qui aide la confirmation par le propriétaire.
- **S-N7** (points « Action » pour la protection et la seconde machine) : la protection reste au point 31 et la seconde machine au Verification Plan ; seule la mesure de durée devient un point « Action » (28 bis).
- **Y-N1, « notebook »** : terme gardé, employé par le niveau 1.

## À confirmer par le propriétaire au passage à Approved

Les lignes « proposition de l'agent de code » du Technical Plan, point 1 : arrondi de la taxe, seuil de mutation, résultats d'ordre, ordres d'un même tick, partie de référence, concurrence, tâche `tests-outillage`, relecture de la protection (qui revient sur un engagement du document de M0).
