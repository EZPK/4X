# Étape 5 — Zoom Out initial (amendement 1)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, lignes 1 à 1535, centrée sur les passages « (amendement 1) ».
*   **Relecteur :** `egm-zoom-out`, sans contexte, standard `zoom-out-standard.md`.
*   **Liste de lecture :** ADR 0003 à 0005, niveau 1 (CUJ 1 et §5), glossaire, `CLAUDE.md`, code de `src/fourx/`. Le brief du brainstorm n'a pas été fourni.
*   **Verdict :** à reprendre. Aucun bloqueur, 7 points majeurs, 10 détails.

L'objectif est clair et motivé par la partie de test. Mais l'amendement laisse le document en contradiction avec lui-même, alors qu'il doit pouvoir être exécuté « à partir de ce document seul, sans décision ouverte ». Il ajoute une mécanique que le problème posé ne motive pas, et laisse sans décision une branche d'échec du calcul des bornes d'économie.

## Majeurs

**M1. Des passages d'origine devenus faux ne portent aucune marque de remplacement.** Seule la ligne « Taille de la tranche 0 » le fait.
- Contradictions avec un passage amendé, sans renvoi depuis l'original :
  - la carte en chaîne de 3 systèmes ;
  - `ore_prices` dans la station ;
  - les champs des vaisseaux « publics » ;
  - `protocol_version` = 1 ;
  - la période de 1 s ;
  - « un propriétaire, un PNJ » ;
  - les touches et le PNJ en version 1 ;
  - les fenêtres de 1 000 ticks ;
  - `observe(state, actor_id)` ;
  - `Visibility` sans `NEARBY`.
- Contradictions sans aucun passage amendé :
  - « Fourchettes économiques par fenêtre de 1 000 ticks », au Technical Plan, point 1 ;
  - « Partie de référence jouée par deux PNJ » (point 1, Technical Plan, point 8, plan détaillé, point 27) ;
  - l'indicateur avancé « trois systèmes et 30 PNJ » (points 11 et 27), désormais impossible ;
  - le notebook « par fenêtre de 1 000 ticks ».
- Proposition : marquer chaque phrase d'origine devenue fausse « (remplacé par l'amendement 1, voir …) » ; compléter le tableau des passages touchés avec le Technical Plan, points 8 et 11, et le plan détaillé, point 28.

**M2. « La vitesse ne change ni les ordres ni les empreintes » contredit l'alternative X.** Avec la tâche de relais, à vitesse élevée, une décision du PNJ entre un ou plusieurs ticks plus tard. Les ordres journalisés et les empreintes d'une partie locale dépendent donc de la vitesse. L'objectif 15 et le CUJ A affirment le contraire. Il faut restreindre l'affirmation (rejeu d'un même journal, ou mode sans horloge), ou retenir l'attache synchrone.

**M3. La formule des bornes ne correspond pas à la politique version 2 dans certaines géométries, et le cas d'échec reste sans décision.**
- **Station dans le système du gisement :** si le gisement visé partage son système avec une station autre que S*, le PNJ vend sur place, au prix local, et ne revient jamais à S*. La formule est alors fausse.
- **d = 0 :** C = 101, donc N × ⌈W ÷ C⌉ × 100 ≥ 30 000 > `deposit_stock`. Le gisement se vide, et le document dit seulement « le test échoue ».
- La simulation citée ne couvre aucun de ces deux cas. Avec la graine 1 fixée, c'est une décision ouverte laissée au volet C.
- Proposition : calculer les bornes une fois par simulation à la régénération des références, et les ranger avec elles, plutôt que réimplémenter dans un test la logique de visée du PNJ.

**M4. La visibilité par proximité (ADR 0005) n'est pas motivée par le problème posé, et va contre lui.** Aucune gêne de la partie de test, aucun des objectifs 11 à 16 ne demande de cacher des vaisseaux. Elle va même à l'encontre du souhait « plus de vaisseaux qui bougent » : sur 8 à 12 systèmes, la plupart des PNJ seront invisibles. Le CUJ A promet pourtant que l'écran montre « les vaisseaux des PNJ ». Il s'agit d'une modification du niveau 1, justifiée surtout par une évolution future (les scanners). Proposition : la reporter, ou écrire dans The Problem pourquoi M1 en a besoin maintenant, et corriger le CUJ A.

**M5. La boucle n'est validée qu'en accéléré, ce qui ne valide pas le rythme lent demandé.** À ×1000, un saut dure 1,2 s : plus vite que le rythme qui posait problème. Le verdict portera sur la lisibilité et l'enchaînement, pas sur le temps comme ressource. Il faut le dire, ou faire jouer au propriétaire un segment à la période nominale (un saut complet, par exemple).

**M6. Les réglages font foi à deux endroits.** Le niveau 1 dit que les chiffres vivent dans `tunables.toml`. Or le tableau du Technical Plan, point 2, `test_reglages.py` (qui en recopie les valeurs) et un scénario protégé qui fige 400 et 100 en font d'autres sources. Changer `jump_ticks` après la partie d'essai demanderait trois pull requests, alors que le point 23 sexies n'en décrit que deux. Proposition : `tunables.toml` comme seule source, le tableau présenté comme « valeurs initiales », `test_reglages.py` supprimé, et le scénario écrit en fonction de `jump_ticks` lu dans les réglages.

**M7. Une parade du tableau des risques contredit le document.** « Des réglages réduits pour l'entraînement, avec leur propre `rules_version` » est une impasse : l'alternative H rappelle que M5 compare `rules_version` au déploiement. À reformuler en risque ouvert pour M4.

## Détails

- **N1.** L'objectif 16 dit « au moins un gisement par minerai » ; l'ADR 0004, le Technical Plan, point 2, et le décodage disent « au moins deux ».
- **N2.** Dans les réglages publics, `cargo_capacity` double `OwnShipView.capacity`, et `tax_rate_bp` ne sert à aucun objectif (la taxe s'affiche depuis `Sale`). Réduire la liste fermée coûte moins maintenant qu'après.
- **N3.** La vérification « l'observation d'un joueur IA contient les mêmes réglages publics » ne vérifie rien à M1.
- **N4.** Le parcours en largeur est dupliqué : `plus_court_chemin` dans `core`, un nouveau dans `policies`, et un besoin dans le client, sans dire où. Proposition : une seule fonction pure de distance dans `schema`, ou réutiliser celle de `policies` depuis le client.
- **N5.** La graine est déjà dans le dossier de la partie (instantané, journal) : la réécrire est redondant. `vitesse.jsonl` n'a pour lecteur que le compte rendu.
- **N6.** Altitude : `asyncio.Event`, le plancher de 0,001 s, le format de `vitesse.jsonl`, les numéros de ligne du niveau 1 et les chaînes de motifs relèvent de l'implémentation. Les numéros de ligne se périment vite.
- **N7.** La maquette de la carte contredit la règle de mise en page (liens tracés dans une même colonne, [3] dans la colonne de [1]). La règle ne dit pas non plus comment placer les systèmes dans une colonne.
- **N8.** Le glossaire gonfle : dix termes, dont la plupart sont des détails internes du client.
- **N9.** Les renvois « décision 7 », « décision 15 », « décision 24 » et « décision 25 » pointent vers une numérotation absente du document (celle du brief rangé dans `docs/revues/`, classé historique par `CLAUDE.md`).
- **N10.** `Game.npc_count` double `core.world.npc_count`. Le décodage ne vérifie pas `max_neighbors` ≥ 2. Renommer `REGLAGES_M1` en `REGLAGES_DE_TEST` est inutile.

## Points vérifiés sans remarque

- Le découpage du client en modules purs, avec des cadres exclus de la mutation, reprend un motif existant et reste bien placé.
- L'alternative P et l'ADR 0003 respectent le niveau 1, §5.
- Le rappel `set_period` passé par `__main__.py` respecte les contrats d'imports.
- La génération par `keyed_below` sur des listes triées est cohérente avec le Technical Plan, point 4.
- L'enchaînement des pull requests 23 bis à 23 sexies respecte la règle d'une pull request de chaque type à la fois.
