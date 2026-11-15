# Étape 7, tour 2 — Revue critique (amendement 1, après les corrections du tour 1)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md`, spécification (lignes 1 à 1070).
*   **Relecteurs :** `egm-design`, `egm-structural`, `egm-style`, tous sans contexte ; tous ont rendu leur rapport.
*   **Bilan :**
    - conception : 0 bloquant, 3 majeurs, 8 détails ;
    - structure : 0 bloquant, 6 majeurs, 9 détails ;
    - style : 0 bloquant, 12 majeurs, 15 détails.

    Le tour n'est pas propre au sens d'EGM.
*   **Chiffres revérifiés par l'agent :** colocalisation d'une station et d'un gisement de `ore_b` dans 52 % des mondes ; E_max = 909 000 par fenêtre (N = 5, C_min = 100, p_max = 18), contre environ 44 000 attendus hors boucle ; empreintes de chaque tick, environ 284 octets par tick, soit environ 284 Mo pour 1 000 000 de ticks.

## Majeurs

- **[conception-M1] Épuisement affirmé, pas démontré.** « La partie de référence exerce ainsi l'épuisement » n'est pas garanti. Il faut au moins trois vaisseaux en boucle sur un gisement de `ore_b` situé dans le système d'une station, ce qui n'arrive que dans une partie des mondes (52 % pour la condition nécessaire). Le chiffre de 84 % compte aussi les gisements de `ore_a`, qu'aucun PNJ ne mine.
- **[conception-M2] L'objectif 5 devient un contrôle à une seule borne.** La borne basse vaut 0 pour presque toute graine (C_max ≥ 6 108 dès que d_max ≥ 3). La borne haute est très lâche (909 000 contre environ 44 000). Une régression qui arrête toute vente passerait le test, qui ne détecte plus que des explosions de l'émission.
- **[conception-M3] Le PNJ v2 peut faire l'aller-retour entre deux gisements vides.** Politique sans mémoire, stock inconnu hors de portée : sur A vide, il part vers B (inconnu) ; sur B vide, il repart vers A (inconnu). Cela dure jusqu'à la régénération, et c'est atteignable dans la partie de référence avec N = 5. L'hypothèse de C_max (« jusqu'à G visites ») est fausse.
- **[structure-1, style-4, conception-N1] Marques placées avant le texte visé** (« Le placement des sites », « Le client », « Elle décide de l'activité voulue »), alors que la légende dit qu'une marque couvre ce qui la précède. Les touches d'origine et « le client ne connaît que `schema` » restent en vigueur à la lettre.
- **[structure-2, style-5] « (amendement 1, précisé) » sur la règle de rédaction**, alors que la phrase d'origine (« n'en ajoute aucune ») devient fausse.
- **[structure-3] Portée des marques de bloc non définie** (marque seule sur sa ligne, ou en tête de paragraphe).
- **[structure-4, style-6] Tableau et en-tête des amendements incomplets** : objectif 6, alternative AA, introduction des CUJ ; la puce de l'en-tête omet la proximité.
- **[structure-5] Lignes d'interface périmées sans marque** au point 13 : `DepositView` (« champs publics »), `OtherShipView`, signature d'`Observation`, définition de l'observation au point 5.
- **[structure-6] Verification Plan** : « plancher de 80 % sur les fichiers modifiés » ; la règle d'origine vise les fichiers nouveaux.
- **[style-1, conception-N2] « Un seul cycle dure plus d'une heure »** ne vaut que pour un gisement à deux sauts (85 min). À un saut, il dure environ 45 min ; en colocalisation, environ 5 min.
- **[style-2, conception-N3] « Zéro ou une vente » par fenêtre de 1 000 ticks** : c'est par PNJ (0 ou 2 avec deux PNJ).
- **[style-3] Formes de marques absentes de la légende** : « remplacé … : <texte> », « Remplacé » en phrase autonome, « Précisé par », « Ces deux phrases… », marques en ligne dans un tableau ou sans valeur.
- **[style-7] Convention sur les CUJ ambiguë** : le CUJ A est défini ici, et non dans le niveau 1 ; aucun scénario ne le traduit.
- **[style-8] « un de ses vaisseaux »** : le possessif renvoie à « autrui », ce qui inverse la règle de proximité.
- **[style-9] « gisement voisin d'une station »** pour un même système, alors que « voisin » est un terme technique (système relié).
- **[style-10] `DepositView.stock` présenté comme « le nouveau champ »** ; il change seulement de type.
- **[style-11] « les points 5, 6, 7 et 13 du noyau »** : renvoi hors convention, et le mot « noyau » est ambigu.
- **[style-12] « fichier d'empreintes d'environ 300 Mo »** : le fichier visé n'est pas nommé ; ce chiffre ne vaut que pour les empreintes de chaque tick.

## Détails

- **Conception :**
  - N4 : parcours en largeur encore dupliqué avec `core.step.plus_court_chemin` ; l'option d'une fonction dans `schema` n'est pas évaluée ;
  - N5 : `npc_min` et `npc_max` dans `Tunables` font varier `rules_version` avec la population ;
  - N6 : le décodage ne vérifie ni `extra_links_max` ≥ 1, ni `npc_min` ≥ 1 ;
  - N7 : `set_period` joue un tick même pour ralentir ; `--periode` sans `--dev` contredit « l'univers tourne à son rythme » ; aux paliers rapides, la décision la plus ancienne gagne ;
  - N8 : « ces fourchettes dépassent celles du CUJ 1 » est déjà faux ; l'ADR 0004 dit que le CUJ 1 reprend les PNJ ; la règle générale hors de portée (disparaître, ou `None`) n'est pas écrite ; rien n'est prévu si la carte dépasse la hauteur du cadre.
- **Structure :**
  - 7 : formes de marques hors légende ;
  - 8 : puce d'en-tête incomplète ;
  - 9 : position des marques dans les titres ;
  - 10 : alternative AA avec « Raison du rejet » et « Retenu » ; titres hétérogènes ;
  - 11 : « Leurs valeurs sont au plan détaillé, point 17 » sans marque ;
  - 12 : « voir ce point » ;
  - 13 : « Vérification : inchangée » sous un objectif réécrit ;
  - 14 : « placement des sites » au point 29 ;
  - 15 : listes coupées par une ligne vide.
- **Style :** 15 détails :
  - règle de numérotation « bis » ;
  - préséance limitée à une seule forme de marque ;
  - « vitesse = durée » ;
  - « enchaînement » ;
  - « plus tard » ;
  - « risque vérifié » et « veille » ;
  - indices i et k, « minerai 1 » contre `ore_a` ;
  - « portée » non défini ;
  - « Sinon » ;
  - première personne ;
  - « ou aucune » ;
  - « disait jamais exécutés » ;
  - doublons, `10 000` contre `10_000`, `npc_count(1, réglages)`, indicatif pour une option rejetée.
