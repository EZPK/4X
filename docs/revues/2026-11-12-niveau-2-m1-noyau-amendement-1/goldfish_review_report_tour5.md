# Goldfish Annotated Review Report — étape 7, tour 5 (dernier tour)

**Status: resolved** (2026-11-21). Aucune décision du propriétaire n'est demandée : le seul majeur de conception porte sur un choix de l'agent, et sa correction (K1) supprime l'écart au niveau 1 sans rien ajouter. Les corrections K1 à K6 sont appliquées. L'étape 7 se termine après cinq tours, sans deux tours propres consécutifs (décision E7 du propriétaire, 2026-11-21) ; les constats déclinés ci-dessous restent ouverts et seront cités dans le résumé de la pull request.

**Target :** `docs/designs/niveau-2-m1-noyau.md` (spécification, lignes 1 à 1102 ; plan détaillé, points 23 bis à 23 sexies et 27) ; ADR 0004.

**Source :** `critic_report_tour5.md`.

## À décider par le propriétaire (ESCALATE)

Aucun.

## Corrections appliquées (PROPOSE FIX)

| N° | Sources | Gravité | Correction appliquée |
| :-- | :-- | :-- | :-- |
| K1 | conception-M1 | majeur | La graine n'est plus affichée dans la barre d'état : `__main__.py` affiche la graine et le dossier de la partie au lancement et à la fermeture du client. Il ne reste qu'une exception locale, la fonction de rappel de vitesse, qui commande l'horloge sans apporter d'information du jeu ; objectifs 6 et 14, CUJ A, Technical Plan, points 6 et 13, maquette et plan détaillé, point 23 quater, alignés sur l'ADR 0003. |
| K2 | conception, détails | détail | Toutes les fenêtres sont contrôlées, la première comprise ; phrase sur `npc_min` et `npc_max` dans `rules_version` ; l'alerte est traitée dans la même étape synchrone que le retrait de la file ; paliers relatifs à la période de lancement ; test de génération sous deux `PYTHONHASHSEED` par deux sous-processus ; gisement régénéré hors de portée et joueur PNJ (hôte et politique) écrits au Technical Plan, point 7. |
| K3 | structure, détails | détail | Portée de la marque en ligne ; règle 5 étendue au paragraphe d'une puce ou d'un objectif ; `FourxApp` au point 13 ; trois marques de remplacement (livrable 5, ordre « vendre », départage) ; ligne « Prix des stations » signalée dans l'introduction des propositions ; renvoi à la légende en tête des conventions. |
| K4 | style-1, style-2 ; style, détail 3 | majeur | « À la régénération des références : l'outil de régénération refuse… » ; « de ces trois indices, seuls les prix restent publics » ; bornes énumérées de la même façon partout (vente, plafond d'émission, destruction, croissance). |
| K5 | style, détails 4 à 13 | détail | « Trois systèmes en chaîne » ; « partie sans `--dev` » ; renvoi au point 23 sexies pour la partie d'essai ; exception de langue Given / When / Then marquée à l'en-tête ; tâche de relais définie dans les conventions ; « exception : … (règle 1) » ; phrases découpées ; « le plus souvent (78 % des mondes) » ; « cas attendu des liens de l'arbre (part mesurée) » ; « au moins une station … dans 84 % des mondes » ; ordre des paires de liens ; « ensemble d'identifiants (`frozenset[int]`) » ; `S1` libellé court de `station_1` ; « qui n'est pas connu comme vide ». |
| K6 | style, détail 14 | détail | « Le rendu se limite à… » ; dates des lignes « Rythme du temps » ; « utiles » ; fin de minage reformulée ; « il ne fait pas partie de l'état » ; « la dernière puce de chaque alternative ». |

## Notés sans correction (DECLINE)

- **Structure, détail 6 (titre de la section CUJ) :** la marque seule sur sa ligne couvre la section jusqu'au titre du CUJ A, lui-même marqué ; les titres `##` suivent le gabarit.
- **Style, « partie de test du 2026-11-11 » et « univers » :** la date distingue la partie ; le sens de « univers » (simulation qui tourne) est clair dans chaque passage de l'amendement.
- **Style, ligne 854 (redite des changements de types) :** la redite sert de résumé au point 13.

## Contestés (CONTEST)

Aucun.
