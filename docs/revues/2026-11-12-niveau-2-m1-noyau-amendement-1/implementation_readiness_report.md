# Étape 9 — Prêt à l'implémentation (amendement 1)

**Status: resolved** (2026-11-21). Aucune décision du propriétaire n'est demandée : les constats portent sur des noms, des formats et des conduites à tenir ; le comportement de la touche `m` relève du choix des touches, délégué à l'agent (décision n° 17 du brief). Les corrections R1 à R10 sont appliquées.

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, lu en entier (lignes 1 à 1602), surtout le volet B bis (points 23 bis à 23 sexies) et les points 25, 27, 28 bis, 29 et 32 bis.
*   **Relecteur :** `egm-implementation-readiness`, sans contexte, standard `implementation-readiness-standard.md`, avec lecture du code et des tests actuels.
*   **Verdict du relecteur :** pas prêt, mais proche. Le circuit des pull requests (23 bis protégée, 23 ter scénarios, 23 quater et 23 quinquies fonctionnalité) respecte `CLAUDE.md` et `.github/chemins-proteges.txt` ; les fichiers que le plan modifie existent ; les valeurs de `tunables.toml` sont complètes. 1 bloquant, 7 majeurs, 13 détails.
*   **Vérifié par l'agent :** `OrderResult` et l'événement `OrderRefused` ne portent pas la commande (`src/fourx/schema/results.py`, `src/fourx/schema/events.py`) ; les scénarios en attente sont en `xfail(strict=True)` (`tests/scenarios/conftest.py`) ; le scénario `FORBIDDEN_CATEGORY` de `partie.feature` suppose la carte de la graine 1 ; `OrderLog.orders_by_tick()` et `fingerprints_by_tick()` existent.

## Corrections appliquées

| N° | Source | Gravité | Correction appliquée |
| :-- | :-- | :-- | :-- |
| R1 | B1 | bloquant | `refusal_text(result, command, observation)` : le modèle passe la commande gardée sous le numéro de l'ordre ; départage à distance égale, singulier de « 1 saut », cas où tous les gisements connus sont vides. |
| R2 | M1 | majeur | La fonction de rappel s'appelle `set_speed` et reçoit un facteur (1, 10, 100) ou `None` ; `__main__.py` la construit sur `Game.set_period`, qui reçoit des secondes ; `speed.jsonl` : T est le dernier tick joué, P vaut `null` en pause. |
| R3 | M2 | majeur | Format de sortie de `layout` (cases de 8 caractères, `─`, ligne « liens : a–b, … » triée, bandes séparées par une ligne vide ; la ligne des vaisseaux est ajoutée par `frames.py`). |
| R4 | M3, M4, M5 | majeur | Réglages de test (valeurs de `tunables.toml` sauf `jump_ticks` = 5, `mining_rate` = 10, et 12 systèmes pour la carte) ; graine : la première qui donne le monde voulu ; recette de la cargaison mêlée ; les trois refus de `partie.feature` réécrits sans position supposée, en attente ; règle d'attente : tout scénario qui échoue sur le code d'origine, et lui seul ; conduite si le score de mutation baisse (scores cités, propriétaire averti, aucun test affaibli) ; `REGLAGES_M1` et `station_ore_prices[0]`. |
| R5 | M6 | majeur | Touche `m` dans un système sans gisement : choix du minerai, puis l'ordre part et son refus traduit dit où aller. |
| R6 | M7 | majeur | `bornes(etat_initial, n_pnj, tunables)` dans `tests/economie/bornes.py`, partagée par le test et l'outil ; « au moins une vente » = émission strictement positive ; le test parcourt les `Sale` ; vidage et départage relevés en rejouant les états par `step`. |
| R7 | N1, N4, N5 | détail | Format de `duration_text` ; types et textes de `ClientModel` (`pending`, numérotation, `alerts`, `history`, `Alert.text`) ; `most_abundant` rend un identifiant de minerai, ou `None`. |
| R8 | N3 | détail | Cas limites des touches de vitesse et affichage de la pause. |
| R9 | N6, N7, N8, N12, N13 | détail | `System.neighbors` trié ; rejeu accéléré par `step` sur `OrderLog` ; `creer_pnj` testable ; « le code d'origine n'affiche que la graine » ; fichiers et marques des tests de la carte et du déterminisme par sous-processus. |
| R10 | N9, N10 | détail | Seuils chiffrés au point 28 bis (2 ticks ; un refus par PNJ et par cycle), procédure de mesure, à partir du point 23 quinquies ; tirage `"world_size"` visé par le bug volontaire du point 29. |

## Notés sans correction

- **N2, refus `SHIP_EN_ROUTE` dans le tick d'arrivée :** `step` examine les ordres avant la phase de déplacement ; le message reprend `ticks_to_next_jump` de l'observation, sans cas particulier.
- **N11, valeurs des nouveaux champs de `REGLAGES_M1` :** ce sont celles de `tunables.toml` (R4).
