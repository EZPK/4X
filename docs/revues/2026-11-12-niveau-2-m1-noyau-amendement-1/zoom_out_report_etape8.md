# Étape 8 — Zoom Out intermédiaire (amendement 1)

**Status: resolved** (2026-11-21). Décision du propriétaire : Z1 → (a). Le texte périmé est supprimé des Goals, des Non-Goals, du Technical Plan et des risques : 66 lignes récrites à leur version en vigueur, avec la marque « (amendement 1, réécrit) », ou supprimées (placement des sites, règle du PNJ version 1, client d'origine, ligne « Taille de la tranche 0 » d'origine) ; les blocs de code du point 13 donnent les nouvelles signatures. Les marques de remplacement ne restent que dans le plan détaillé, et la légende est réduite en conséquence.

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, lu en entier (lignes 1 à 1603).
*   **Relecteur :** `egm-zoom-out`, sans contexte, standard `zoom-out-standard.md`.
*   **Verdict du relecteur :** presque prêt. L'amendement répond au problème posé ; chaque grand changement remonte à une gêne de la partie de test ou à une décision du propriétaire, et les décisions ne se contredisent pas. 0 bloquant, 5 majeurs, 5 détails.

## À décider par le propriétaire (ESCALATE)

### [Z1] Le texte périmé reste dans le document — majeur
*   **Constat :** les passages d'origine remplacés restent dans les Goals, les Non-Goals et le Technical Plan, suivis de « *(remplacé par l'amendement 1…)* ». Un agent sans mémoire doit appliquer la légende des marques (onze formes, six règles de portée) phrase par phrase pour savoir ce qui vaut. La règle « ne jamais renuméroter » n'oblige pas à garder l'ancien texte ; seule la description du code livré (plan détaillé, points 15 à 23) a besoin de le garder.
*   ***Suggestion :*** ESCALATE, car cela change la forme de l'amendement.
    - **(a) Supprimer le texte périmé** dans les Goals, les Non-Goals et le Technical Plan, et réécrire chaque passage à sa version en vigueur, avec la marque « (amendement 1, réécrit) ». Les marques de remplacement ne restent que dans le plan détaillé, points 15 à 23. La légende tombe à trois ou quatre formes. L'ancien texte reste dans git et sur `main` ; le diff de la pull request montre ce qui change.
    - **(b) Garder la forme actuelle.**
*   ***Recommandation de l'agent :*** (a). C'est le premier obstacle au critère « implémentable à partir de ce document seul », et l'étape 9 vérifie justement ce critère.

## Corrections appliquées (PROPOSE FIX)

| N° | Source | Gravité | Correction appliquée |
| :-- | :-- | :-- | :-- |
| Z2 | majeur 2 | majeur | Les fourchettes du monde (`systems_min` à `npc_max`) sont exclues de la voie « une pull request sur `tunables.toml` » : elles viennent du CUJ 1 du niveau 1, élargi par l'ADR 0004, et les changer demande une ADR et un amendement (point 23 sexies). « 20 minutes avec les valeurs initiales » (objectif 11, point 23 sexies). Les autres valeurs recopiées sont déjà dites « valeurs initiales ». |
| Z3 | majeur 3 | majeur | Interface minimale de `ClientModel` au Technical Plan, point 13 (constructeur, `on_update`, `send`, `sell_all`, `acknowledge`, `remaining_ticks`, attributs, `Alert`), et `duration_text` de `texts.py`. |
| Z4 | majeur 4 | majeur | La vitesse du mode développement (`set_period`, `speed.jsonl`, `--dev`, tests) passe du point 23 quater au point 23 quinquies, avec son seul utilisateur, le client. |
| Z5 | majeur 5 | majeur | Paliers ×1, ×10 et ×100, sans contre-pression (le palier ×1000 et la contre-pression étaient des choix de l'agent ; le brief disait « par exemple ×1, ×10, ×100 ») ; le débordement est mesuré au point 28 bis, et une contre-pression ne s'ajoute que si la mesure le demande. |
| Z8 | détail 8 | détail | L'essai de la veille dit ce qui suit son résultat : un rattrapage des ticks au réveil est signalé au propriétaire avant la partie d'essai. |
| Z9 | détail 9 | détail | Verification Plan de l'amendement réduit aux lignes nouvelles. |
| Z10 | détail 10 | détail | La vérification de déterminisme est portée par le test de propriétés du point 23 quater (génération sous deux `PYTHONHASHSEED`) ; la partie de 2 000 ticks, doublon du rejeu du volet C, est retirée. |

## Notés sans correction (DECLINE)

- **Détail 6 (file de vente) :** décision du propriétaire n° 14 du brief (« la vente en file arrivera avec l'amendement »).
- **Détail 7 (`speed.jsonl`) :** il répond à une gêne relevée au brainstorm (« la période n'est enregistrée nulle part ») et sert à la vérification de l'objectif 15 ; son en-tête versionné coûte une ligne.
- **Détail 9 (règle du PNJ recopiée) :** les mentions hors du point 7 sont des résumés d'une phrase, avec renvoi.
