# Étape 9, tour 1 — Synthèse de la revue (amendement 2)

*   **Cible :** l'amendement 2 de `docs/designs/niveau-2-m1-noyau.md` et `docs/adr/0006-client-retro-8-bits.md` (commit a8e8f50).
*   **Rapports :** `comprehension_report.md` (étape 5), `implementation_readiness_report.md` (étape 6), `critic_report_design.md`, `critic_report_structure.md`, `critic_report_style.md` (étape 7), `zoom_out_report.md` (étape 8). Six relecteurs sans contexte ; tous ont rendu leur rapport.
*   **Bilan brut :** 6 bloquants, 66 majeurs, 96 détails, dont beaucoup en double. Une fois dédoublonnés : 2 bloquants, 19 groupes majeurs, et les détails.
*   **Verdict :** non approuvable en l'état. La décision de fond (Textual dans le terminal, rien ne change dans le protocole, l'observation ou les règles) n'est contestée par aucun relecteur. Les défauts portent sur deux données affichées qui ne viennent pas de l'observation, sur une spécification trop vague pour être implémentée sans décision (disposition, prochaine étape, aide, touches), et sur des passages devenus faux sans marque.

Sources : C = compréhension, I = préparation, D = conception, S = structure, St = style, Z = prise de recul.

## Décisions du propriétaire

Quatre points changent ce que l'on construit. Ils sont posés au propriétaire avant toute correction.

| N° | Question | Constats | Recommandation de l'agent |
| :-- | :-- | :-- | :-- |
| E1 | Carte fixe (disposition calculée une fois) ou animée comme le graphe d'Obsidian (les systèmes bougent et se tirent) ? | D-M8 | fixe à M1 ; l'animation reportée, avec une alternative AF qui le dit |
| E2 | Souris : tout garder (molette, glisser, survol avec bulle, clic, mini-carte), ou seulement molette, clic et clavier, le reste à M3 ? | Z-M4, I-M9, I-M11, D-D5 | tout garder sauf la mini-carte, inutile sur 8 à 12 systèmes |
| E3 | Découper la pull request de fonctionnalité en deux : (a) prochaine étape, aide, panneaux, palette ; (b) carte rétro ? | Z-M2, D-D15 | oui |
| E4 | Le verdict de la partie d'essai sur l'écran bloque-t-il la livraison de M1 ? Le volet C démarre-t-il tout de suite ? | Z-M1, C-M12, S-D8 | non bloquant (une pull request de correction au plus dans M1, au-delà la condition de révision de l'ADR) ; volet C en parallèle dès maintenant |

**Réponses du propriétaire (2026-11-22) :** E1 carte fixe ; E2 tout sauf la mini-carte ; E3 deux pull requests de fonctionnalité ; E4 verdict non bloquant, volet C en parallèle dès maintenant. Les quatre recommandations sont retenues.

## Bloquants

- **G1. La graine dans la barre du haut** (St-B1, C-B1, D-B1, I-B1). Elle n'est pas dans l'observation, et le Technical Plan, point 6, la tient hors de l'écran de jeu. *Traitement :* retirée de la barre (erreur de l'agent).
- **G2. « La taxe est rappelée »** (C-M3, D-B1, I-B2, St-M15). Le taux n'est pas dans l'observation avant la première vente. *Traitement :* mention retirée ; le montant de la taxe reste dans l'historique après chaque vente.

## Majeurs

- **G3. Disposition par forces sous-spécifiée** (I-B3, D-M3, C-M11, St-M12, Z-D2). Constantes, normalisation dans le carré et garantie de distance sans mécanisme ; libellés qui se chevauchent au zoom 1 ; croisements non mesurés. *Traitement :* fixer les constantes et la normalisation (échelle uniforme, marge) ; une passe finale déterministe de séparation ; au zoom 1, pastille et losange seuls (libellés à partir du zoom 2) ; nombre de croisements mesuré et publié au compte rendu ; départ en couches par distance plutôt qu'en cercle.
- **G4. Prochaine étape : règles incomplètes et logique en double du PNJ** (D-M2, Z-M3, C-M6, C-M7, I-M1, I-M2, St-M7). Pas de règle pour un ordre en attente ; règle 3 fausse quand le stock limite ; règle 7 sans repli ni départage ; sorties non fixées ; « observation seule » contredit la signature. *Traitement :* règle « ordre envoyé : attendre le résultat » ; « fin du minage dans n ticks » ; pour les cas à l'arrêt, reprendre la décision de `scripted_miner` (départages et repli compris) et la traduire en conseil ; fixer titres, gabarits et touches (noms Textual) ; signature `next_step(model: ClientModel) -> Step`.
- **G5. Aide : contenu, signature, touches** (I-M3, I-M10, C-D12, D-D2, D-D3, St-M14). Ouverte avant la première observation ; durée du minage hors des réglages publics (la capacité est dans `OwnShipView`) ; priorité d'Entrée face aux alertes ; flèches page ou vue. *Traitement :* `help_pages(observation: Observation | None)` ; textes contractuels fixés ; l'aide est une saisie modale : Entrée et Échap la ferment, avant les alertes ; ← → changent de page ; une seule page qui défile (prise de recul, détail 4).
- **G6. Mutation** (I-M4, I-M5, Z-M5). Les textes de l'aide feraient baisser le score de `texts.py` ; la logique de la carte tomberait dans `frames.py`, exclu de la mutation, ou ferait baisser son score. *Traitement :* module pur `clients/map_view.py` (projection, zoom, vue, système sous le pointeur, grille de cases) muté sans plancher ; textes de l'aide comparés en entier par les tests.
- **G7. Vérification de l'objectif 12 caduque** (C-M5, D-M6, I-M6, Z-M6, S-M4). La carte ne défile plus et ne se lit plus comme du texte. *Traitement :* chaque information a un cadre texte : emplacement des minerais ajouté au cadre des stations (une ligne par minerai), prix dans ce cadre, état et durées dans Vaisseau ; la carte est vérifiée par la grille de `map_view.py`.
- **G8. Rendu** (D-M5, S-M2, C-M8, I-M12, Z-D3). Le critère de redessin est sans effet (l'observation change à chaque tick) ; le point 28 bis ne contient aucune mesure. *Traitement :* redessin plafonné à 10 par seconde et seulement si les données de la carte changent ; puce « amendement 2, ajout » au point 28 bis (mesure au palier ×100, seuil 30 ms signalé au propriétaire).
- **G9. Palette** (St-M9, St-M10, St-M11, C-M1, C-M14, D-M4, Z-D1, I-D6). Accent et `ore_b` identiques ; minerai porté par la seule couleur ; couples testés non listés ; « 8 bits » pour 16 couleurs. *Traitement :* accent distinct ; lettre `a` ou `b` dans le losange ; constante `CONTRAST_PAIRS` testée (WCAG 2.1, 4,5 pour 1) ; dire que « 8 bits » désigne l'esthétique des consoles, et que les 16 couleurs sont des valeurs RGB.
- **G10. Noms des cadres** (St-M1 à St-M5, C-M13, S-M9, C-D15). « Journal » (pris par `OrderLog`, écarté par l'alternative K), « Marché » (Non-Goal, M6), « panneau » contre « cadre », « soute » contre « cargaison », deux barres. *Traitement :* cadres « Historique » et « Stations » ; « cadre » partout ; « cargaison » ; « barre d'état » en haut, « barre des touches » en bas.
- **G11. Disposition de l'écran incomplète** (I-M8, S-M8, D-D8, D-D9, C-D7). Place de l'alerte, de la liste des destinations, de la ligne d'invite ; identifiants des widgets ; comportement entre 100 × 30 et 120 × 36. *Traitement :* un tableau des widgets (identifiant, position, taille).
- **G12. Clic et glisser** (I-M9, C-D10, D-D5, D-D6). Il n'y a pas de confirmation après `d` ; clic sur le système du vaisseau, pendant une saisie ou un saut ; seuil clic / glisser. *Traitement :* le clic ouvre la liste des destinations sur ce système ; ignoré pendant une saisie ; seuil d'une case.
- **G13. Zoom** (St-M13, C-D9, D-D4, I-M11). Le pas de 1,25 n'atteint ni 2 ni 4. *Traitement :* table de niveaux fixée (selon E2), zoom autour du pointeur.
- **G14. Historique typé** (I-M7). Les étiquettes colorées par type demandent un historique typé. *Traitement :* `HistoryEntry(tick, kind, text)` ; `model.py` et son test ajoutés au point 23 nonies ; l'étape protégée qui lit l'historique adaptée au point 23 octies.
- **G15. Règle du minimum et niveau 1, §11** (S-M1, D-M1, Z-D9). Le point 1 cite encore les objectifs 12 à 16 et les ADR 0003 à 0005 ; le « client Textual minimal » du §11. *Traitement :* point 1 précisé ; l'ADR dit que le critère de sortie du §11 ne change pas.
- **G16. Passages devenus faux sans marque** (S-M6, S-M7, C-M9, C-D5, C-D6, D-M7, I-D8). « Code livré » (l. 44), Overview point 2 de l'amendement 1, Non-Goals l. 204, risque « Carte illisible », point 23 quater (mesures de la carte en colonnes). *Traitement :* marques de réécriture ou de remplacement.
- **G17. Verification Plan** (S-M3, D-M7, I-M12). Rien pour l'amendement 2 ; `map_layout.py` encore cité. *Traitement :* un bloc « (amendement 2) ».
- **G18. Marques et liste des passages touchés** (S-M4, S-M5, S-D1 à S-D4, C-D1, C-D4). *Traitement :* corrigées.
- **G19. ADR 0006** (St, D-M8, Z-D7, S-D12, C-D17). Option (a) mal justifiée ; aucune technique de dessin du terminal comparée (Braille, kitty, sixel) ; renvois vagues à l'alternative N du niveau 1 ; « illisible » déforme la citation. *Traitement :* corrigée ; option (b′) « graphismes du terminal » ajoutée et citée dans la condition de révision.
- **G20. Scénarios du point 23 octies** (I-D3, D-D11, D-D12). Titres exacts, monde fixé, déterminisme comparé entre deux appels, jamais à des valeurs écrites en dur. *Traitement :* fixés.
- **G21. Glossaire** (C-D18, D-D16). « Portée », « prochaine étape », « disposition par forces » n'ont pas d'entrée. *Traitement :* ces termes ne servent qu'au client ; ils restent au Technical Plan, point 7 ter, comme ceux du point 7 bis, et le glossaire ne change pas (point 12, précisé). La portée est la proximité du glossaire.

## Détails

Les détails des six rapports (typographie, unités, renvois, formulations) sont traités avec les groupes ci-dessus, sauf avis contraire du propriétaire. Ils ne sont pas recopiés ici.

## Corrections appliquées (tour 1)

Toutes les corrections ci-dessus sont appliquées au document et à l'ADR, avec les réponses E1 à E4 : point 7 ter réécrit (palette avec `ore_b` en `#5AA0FF`, contrastes calculés : le plus faible des couples retenus vaut 5,07 pour 1 ; tableau des cadres ; disposition en quatre étapes, constantes fixées ; vue de la carte ; prochaine étape fondée sur la décision du PNJ ; aide ligne par ligne) ; objectifs 12 et 17 à 19 ; plan détaillé, volet B ter (points 23 septies à 23 undecies, deux pull requests de fonctionnalité) ; points 1, 12, 13, 23 quater et 28 bis ; alternatives AB à AG ; risques ; Verification Plan ; ADR 0006 (options (a) et (b′), critère du §11, condition de révision).

## Tour 2

*   **Rapports :** `critic_report_design_tour2.md`, `implementation_readiness_report_tour2.md`, `critic_report_structure_tour2.md`. Aucun bloquant ; 13 majeurs, 41 détails. Tous les bloquants et majeurs du tour 1 sont corrigés, deux en partie (disposition, prochaine étape).
*   **Décision du propriétaire (E5, 2026-11-22) :** à l'arrêt, la prochaine étape conseille le cycle au meilleur gain par tick, et non la décision du PNJ (alternative AH).
*   **Corrections :**
    - disposition : séparation par boîtes (0,125 × 0,15, calculées pour 100 × 30), test de non-recouvrement dans la grille, en 120 × 36 et en 100 × 30 ; 50 graines sous `proprietes`, 2 000 sous `lent`, hors de la mutation ; quatre étapes exposées et testées sur de petits graphes ; cas dégénérés ;
    - traits : `trait_faible` `#5E6A99` (3,66 pour 1 sur le fond), `trait_fort` `#7B89C2` (5,68), `GRAPHIC_PAIRS` à 3 pour 1 ; fonds fixés ;
    - prochaine étape : règles 5 (vente, V ÷ (t + 1)) et 6 (cycle, G ÷ T, en entiers) ; règle 4 observable (un autre vaisseau visible dans le système) ; `Step.command` ; règle 0 bis ; textes de l'alerte et des ordres ;
    - aide : lignes des touches fixées, paramètre `dev` ;
    - touches `z`, `x`, `c` hors saisie, sans effet aux bornes ; `x` des tests existants remplacé par `y` ;
    - scénario du cycle : condition de graine, procédure, arrêt ; `steps_partie.py` ajouté ;
    - structure : décisions du 2026-11-22 en lignes du tableau du point 1 (le libellé « E1 à E4 » sort du document) ; critère de sortie ; point 13 (`history`, `mettre_a_jour`) ; marques ; CUJ A ; palier 3 ; clause de refus de l'ADR ; ADR au passé.

