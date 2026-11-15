# Étape 5, seconde relecture — Zoom Out (amendement 1, version révisée)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, lu en entier (lignes 1 à 1543).
*   **Relecteur :** `egm-zoom-out`, sans contexte, standard `zoom-out-standard.md`, avec le premier rapport (`zoom_out_report.md`).
*   **Verdict :** presque prêt. Aucun bloqueur. Sur les 17 points du premier rapport, 12 sont résolus et 5 en partie. La révision introduit 2 points majeurs et 7 détails.
*   **Plafond EGM :** c'est la seule nouvelle relecture permise pour l'étape 5. Les points restants sont corrigés sans troisième relecture, ou repris à l'étape 7.

## Suivi du premier rapport

- **M1 : résolu en partie.** Restent faux sans marque :
  - le tableau des événements, où « départ » et « arrivée » sont encore publics (le plus gênant : tableau normatif) ;
  - « position publique » ;
  - « `OtherShipView` (champs publics de `Ship`) » ;
  - « copiés de `ore_prices` », et la phrase « `world.generate` copie `ore_prices` dans la station » ;
  - « sur chaque fenêtre de 1 000 ticks » dans `test_fourchettes.py` ;
  - le bloc « Calcul des bornes » d'origine.

  Le tableau des passages touchés oublie aussi Additional Resources.
- **M2, M3, M5, M7 : résolus.** M3 garde une faiblesse de raisonnement (détail D).
- **M4 : la justification est maintenant cohérente.** La tension avec « plus de vaisseaux qui bougent » est reconnue et arbitrée. Restes de forme au détail G.
- **M6 : résolu,** mais la correction crée le point majeur B.
- **N1, N2, N3, N4, N8, N9, N10 : résolus.** N5 et N6 en partie : `vitesse.jsonl` reste (justification acceptable) ; `asyncio.Event`, le plancher de 0,001 s, le format JSON et les chaînes de motifs restent dans le texte. N7 en partie (détail C).

## Nouveaux points majeurs

**A. La seule question ouverte ne peut pas être fermée avant le retour à Approved.** Le document exige une liste vide avant ce retour, qui précède la fusion du point 23 bis. Or la question de la veille ne se ferme qu'à l'essai du point 23 quater, après cette fusion. Elle n'a d'effet ni sur les règles ni sur le rejeu, et aucune décision n'attend sa réponse. Proposition : la retirer des Open Questions et la garder comme risque vérifié au point 23 quater.

**B. Le scénario « le temps comme ressource » ne peut pas échouer sur le code actuel pour la raison donnée.** Depuis la correction de M6, il lit `jump_ticks` et `mining_rate` dans `tunables.toml`. Sur le code actuel, il lirait 5 et 10, et passerait. Or la CI exige qu'un scénario en attente échoue (`xfail(strict=True)`). Proposition :
- ancrer l'échec sur ce qui est nouveau : la durée lue dans `observation.public_tunables` est celle de `tunables.toml`, et le trajet observé tombe juste ;
- corriger la phrase ;
- assumer que la valeur 400 n'est plus vérifiée par aucun test automatique, puisque `tunables.toml` fait foi.

## Nouveaux détails

- **C.** La maquette de la carte contredit encore sa règle, alors que le texte la dit « conforme » :
  - les liens 3–5, 5–7, 7–10 et 8–11 relient des colonnes voisines au même rang, donc devraient être tracés ;
  - le vaisseau proche [4] n'est pas voisin de [5], où se trouve le joueur ;
  - la maquette compte 11 liens pour 12 systèmes, soit un arbre sans lien en plus, alors que la génération en impose au moins un ;
  - les colonnes font environ 7 caractères au lieu de 8.
- **D.** L'argument d'accessibilité des bornes est incomplet. Tous les PNJ visent le même gisement : avec d petit, N × 101 × 100 unités peuvent dépasser les 20 000 d'un seul gisement. Un gisement vidé en cours de cargaison ajoute un trajet jusqu'à 2 × d_max, et la borne basse peut ne plus tenir. L'affirmation « la partie de référence ne vide aucun gisement » n'est plus garantie.
- **E.** Le client dépend de `policies/scripted_miner.py` pour `distances` et `plus_abondant`. Un petit module neutre dans `policies`, sans logique de décision, éviterait ce couplage.
- **F.** La vérification « en mode sans horloge, les règles ne dépendent pas de la période » ne prouve rien, puisque `Game.advance` ne lit jamais `period_s`. Le test de rejeu d'une partie accélérée suffit.
- **G.** La proximité n'apparaît ni dans les « trois choses » de l'Overview, ni dans l'objet du tableau des amendements, ni dans les objectifs, alors qu'elle modifie le niveau 1. À relier à l'objectif 6, ou lui donner un objectif.
- **H.** Les restes de M1 listés plus haut.
- **I.** Le seuil bas des bornes vaut souvent 0 (d_max ≥ 7). C'est assumé ; à citer dans le compte rendu, avec la valeur réelle pour la graine 1.

## Points vérifiés sans remarque

- Les contrats d'imports permettent `clients` → `policies`, et `__main__.py` peut appeler `core.world.npc_count`.
- La génération du monde est cohérente : `max_neighbors` ≥ 2, `systems_min` suffisant, gisements alternés, station de départ par `rem_trunc`.
- Le niveau 1 et le glossaire sont alignés sur les ADR 0003 à 0005.
- `public_tunables` à deux champs respecte « pas d'autre canal ». `NOMINAL_TICK_PERIOD_S` est une constante partagée, pas une donnée transmise.
