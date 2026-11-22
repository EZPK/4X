# Étape 7 — Structure (amendement 2)

**Cible :** `docs/designs/niveau-2-m1-noyau.md`, passages de l'amendement 2. Pièce liée : `docs/adr/0006-client-retro-8-bits.md`.
**Référentiels lus :** le persona structurel EGM, `resources/document_standards/feature-spec-standard.md`, l'en-tête « Amendements » du document (lignes 23 à 49), `docs/adr/README.md`, les ADR 0003 et 0005, et le niveau 1 (Overview, alternative N).
**Limite :** je n'avais pas accès à git. Je n'ai donc pas pu comparer le texte au document tel qu'approuvé après l'amendement 1. Les marques « réécrit » sont vérifiées sur leur forme et leur portée, pas contre le texte qu'elles remplacent.

**Verdict : aucun bloquant, 9 majeurs, 12 détails.** La structure de l'amendement est saine : numéros, titres, marques en titre et lignes de code marquées sont conformes. Les défauts sont tous du même ordre : des passages d'origine ou de l'amendement 1 devenus faux sans être marqués, et deux renvois qui promettent un contenu absent.

## Ce qui est conforme

- **Numéros nouveaux.** Ils suivent la convention de la ligne 25 :
  - objectifs 17 à 19, à la suite du 16 ;
  - point 7 ter, après 7 bis ;
  - alternatives AB à AE, à la suite de AA ;
  - points 23 septies, octies, nonies et decies, après 23 sexies ;
  - volet B ter, après B bis.
- **Marques en titre** (portée : toute la section) : 7 ter (l. 577), AB à AE (l. 1071 à 1089), 23 septies à 23 decies (l. 1518 à 1547).
- **Marques en tête de puce ou d'objectif :** objectifs 17 à 19 (l. 178 à 183), Non-Goals (l. 205), 7 bis (l. 537).
- **Marques seules sur leur ligne :** Overview (l. 92) et The Problem (l. 126).
- **Tableau de risques :** « Risques ajoutés par l'amendement 2 » (l. 1143) suit la légende.
- **Point 13 :** les lignes de code des l. 880 à 883 et 887 portent « (amendement 2) » en fin de ligne.
- **Renvois au point 7 ter :** ceux des l. 533, 537, 579 et 1540 pointent vers une section qui existe. Le renvoi au point 23 decies (l. 169) aussi.
- **Liste « Passages touchés » (l. 49) :** chaque élément cité porte bien une marque de l'amendement 2. Rien n'y est en trop.
- **ADR 0006 :** elle suit le modèle de `docs/adr/README.md` (onze puces, dans l'ordre). Son titre est identique à celui de l'index (l. 28 du README), et son statut « proposée » concorde. Le niveau 1, Overview l. 16, est déjà modifié comme l'annonce sa puce « Section du niveau 1 modifiée ».
- **Gabarit feature-spec :** Problem, Goals, Non-Goals, Architecture (7 ter), Alternatives (AB à AE) et Risks sont présents pour l'amendement.

## Constats

### Majeurs

**M1. Technical Plan, point 1, l. 276 : règle du minimum devenue fausse, hors de la liste des passages touchés.**
- Problème : la ligne dit que le document « n'en ajoute aucune sauf le seuil de mutation ci-dessous et les objectifs 12 à 16, et ne le change que par les ADR 0003 à 0005 ». Or l'amendement 2 ajoute les objectifs 17 à 19, et l'ADR 0006 modifie le niveau 1 (23 septies, l. 1525). La phrase « (amendement 1, précisé) » de la même ligne ne couvre que les décisions de l'amendement 1. La l. 297 répète aussi « comme les objectifs 12 à 16 ».
- Proposition : récrire « objectifs 12 à 19 » et « ADR 0003 à 0006 » avec la marque « (amendement 2, réécrit) ». Ajouter « (amendement 2, précisé) Les décisions du propriétaire du 2026-11-22 (palette 8 bits, souris, disposition par forces) priment aussi… ». Ajouter « Technical Plan, point 1 » à la ligne 2 du tableau. Ajouter au besoin des lignes de décisions datées du 2026-11-22 au tableau du point 1.

**M2. Point 7 ter, l. 614, et risque l. 1150 : renvoi au point 28 bis sans contenu correspondant.**
- Problème : « Le temps de rendu d'une mise à jour est mesuré au plan détaillé, point 28 bis ». Le point 28 bis (l. 1607 à 1612) n'a reçu aucun ajout de l'amendement 2. Il n'y a ni mesure du rendu, ni palier, ni seuil, ni conduite en cas de dépassement. Le signal du risque « Rendu trop lent » ne repose donc sur rien.
- Proposition : ajouter au point 28 bis une puce « **Proposed Changes (amendement 2, ajout) :** à partir de la pull request du point 23 nonies, mesurer le temps de rendu d'une mise à jour au palier ×100 (graine, taille 120 × 36, seuil au-delà duquel l'agent le signale) ». Ajouter « 28 bis » à la liste des passages touchés.

**M3. Verification Plan, l. 1705 à 1714 : rien pour l'amendement 2, et deux lignes devenues fausses.**
- Problème :
  - l. 1710 : « `clients/model.py`, `map_layout.py` et `texts.py` sont mutés sans plancher » ; or `map_layout.py` est supprimé (l. 1544) ;
  - l. 1712 : la « part des liens tracés et hauteur de la carte » doit être « publiées au compte rendu de M1 » ; cette mesure n'existe plus avec la disposition par forces (et voir aussi l. 1470, point 23 quater) ;
  - aucune entrée ne couvre l'amendement 2 : `ecrans.feature` vidé de `en_attente.txt` à la fin du point 23 nonies, mutation de `force_layout.py`, `guide.py` et `palette.py`, partie d'essai du point 23 decies.
- Proposition : ajouter un bloc **(amendement 2)** au Verification Plan, couvrant :
  - Tests : aucun scénario d'`ecrans.feature` en attente à la fin du point 23 nonies ;
  - Mutation : `model.py`, `force_layout.py`, `guide.py`, `palette.py` et `texts.py`, sans plancher ;
  - Carte : distance minimale vérifiée sur de nombreuses graines ;
  - Manuel : point 23 decies.

  Y écrire que les puces « Mutation » et « Carte » de l'amendement 1 ne valent plus pour `map_layout.py`. Ajouter « Verification Plan » à la liste des passages touchés.

**M4. Objectif 12, *Vérification*, l. 169 : texte nouveau non marqué, et description devenue fausse.**
- Problème :
  - « sa décision, rendue après la partie d'essai de l'amendement 2 (plan détaillé, point 23 decies) » est forcément du texte de l'amendement 2. Pourtant, la seule marque du paragraphe, « (amendement 2, réécrit) », est placée plus loin. Selon la portée de la l. 43, elle ne couvre que le membre de phrase qui la précède (« sur un terminal de 120 × 36 et sur un monde de 12 systèmes »). La première phrase passe donc pour du texte de l'amendement 1.
  - « au besoin après défilement du cadre Carte : le test lit le contenu du cadre » décrit l'ancienne carte en texte qui défile. La carte du point 7 ter se zoome et se déplace, et elle est dessinée en demi-blocs, donc elle ne se lit pas comme du texte.
- Proposition : placer « (amendement 2, réécrit) » après « … consignée dans le compte rendu de M1. ». Récrire la fin, par exemple « au besoin après zoom ou déplacement de la carte : le test lit l'état du widget `MapView` (systèmes, sites, stock) et le contenu des panneaux », avec la même marque.

**M5. Plan détaillé, volet B ter, l. 1514 à 1516 : « Règles d'intégration » non marquées.**
- Problème : la marque de « **Volet B ter : l'écran rétro (amendement 2)** » est placée dans un paragraphe en gras, pas dans un titre `####`. Selon la l. 40, elle ne couvre que ce paragraphe. Le paragraphe « Règles d'intégration » qui suit est donc du texte non marqué, alors qu'il pose une règle nouvelle : le volet C peut avancer en parallèle.
- Proposition : écrire « **Règles d'intégration (amendement 2).** », ou mettre « **(amendement 2)** » seul sur sa ligne après le titre du volet. Le volet B bis (l. 1407 à 1409) a le même défaut, hors du périmètre de cette revue.

**M6. En-tête, puce « Code livré », l. 44 : texte faux et terme non défini.**
- Problème : « les points 23 bis à 23 sexies, ajoutés par l'amendement, ne le sont pas ». Or le point 23 quinquies est fusionné (pull request n° 27), et la partie d'essai du point 23 sexies a eu lieu (l. 128). L'amendement 2 emploie aussi le « code de l'amendement 1 » (l. 1534), un terme défini nulle part, alors que le « code d'origine » l'est ici.
- Proposition : ajouter « (amendement 2, précisé) Les points 23 bis à 23 sexies sont livrés ; les points 23 septies à 23 decies ne le sont pas. Le *code de l'amendement 1* est le code fusionné à la fin du point 23 quinquies. »

**M7. Textes de l'amendement 1 que l'amendement 2 rend faux, sans marque.** La préséance (l. 27) règle le conflit sur le principe, mais ces passages se trouvent dans des sections que l'amendement 2 touche déjà, et la légende interdit les marques de remplacement hors du plan détaillé.
- l. 79, Overview, point 2 : « sans thème de couleur », et la liste « carte, vaisseau, stations, historique, barre d'état et alertes ». Les deux contredisent la l. 94 et le point 7 ter. Proposition : « (amendement 2, réécrit) » sur ces deux membres de phrase, ou une phrase de la l. 94 qui dise que l'amendement 2 remplace ce point 2.
- l. 1138, risque « Carte illisible pour certaines graines » : sa parade (« rang du parent… deux bandes… autres liens écrits en texte ») décrit `map_layout`, qui est supprimé. Proposition : récrire la ligne avec « (amendement 2, réécrit) » en tête, en renvoyant au risque « Disposition illisible » (l. 1151).
- l. 204, Non-Goals : « L'amendement fixe une première disposition simple, faite de cadres indépendants ». Proposition : « (amendement 2, réécrit) L'amendement 2 fixe la disposition du point 7 ter ; elle n'est pas figée. »

**M8. Point 7 ter, l. 583, et point 13, l. 887 : place des alertes et des barres non définie.**
- Problème : le point 7 bis garde ses alertes, « affichée[s] jusqu'à Entrée » (l. 537 et 568), mais la disposition du point 7 ter énumère les zones de l'écran sans dire où s'affiche une alerte. Le point 13 cite pourtant des widgets « barre d'état, alerte ». De même :
  - le point 7 ter nomme « une barre » en haut et une « barre des touches » en bas ;
  - le point 7 bis (l. 553) et le risque de la l. 1129 parlent de « barre d'état », pour la ligne d'aide et pour la vitesse ;
  - la barre des touches manque à la liste des widgets de la l. 887.
- Proposition : dans la disposition du point 7 ter, nommer la barre du haut « barre d'état » et dire où s'affichent l'alerte (par exemple en surimpression ou dans le panneau « Prochaine étape ») et la ligne d'aide. Aligner la l. 887 sur cette liste (ajouter « barre des touches »).

**M9. Point 7 ter, l. 608, objectif 18, l. 180, et point 23 nonies, l. 1542 : le panneau « Journal » contredit l'alternative K.**
- Problème : l'alternative K (l. 959) écarte notamment un onglet « Journal », parce que « « Journal » désigne déjà `OrderLog` ». L'amendement 1 a pour cela employé « historique ». L'amendement 2 réintroduit « Journal » comme nom de panneau sans en discuter.
- Proposition : nommer le panneau « Historique », ou justifier l'écart dans le point 7 ter et dans une puce de l'alternative AE.

### Détails

**D1. l. 25 et l. 896 : listes de lettres non mises à jour.** La l. 25 dit « alternatives J à AA » et l'introduction des alternatives (l. 896) ne présente que J à AA. Proposition : « (amendement 2) Les alternatives AB à AE s'y ajoutent, avec la marque « (amendement 2) » ». Mettre la l. 25 à jour et ajouter « introduction des alternatives » à la liste des passages touchés.

**D2. l. 23 et l. 49 : marque de la ligne 2 du tableau.** La marque « **(amendement 1)** » seule sur sa ligne (l. 23) couvre tout jusqu'à « ## Overview », y compris la ligne 2 du tableau, qui passe ainsi pour un ajout de l'amendement 1. Proposition : « | 2 (amendement 2) | … ». La l. 40 permet une marque en tête de ligne de tableau.

**D3. l. 49 : passages non cités dans la liste.** Elle ne cite ni l'en-tête (statut, date, puce « Amendements ») ni le volet B ter. La ligne 1 cite les « conventions ». Proposition : ajouter « en-tête » et « volet B ter », en plus des ajouts proposés en M1, M2, M3 et D1.

**D4. l. 533 : forme de la marque.** « (amendement 2, réécrit ; Technical Plan, point 7 ter) » glisse un renvoi dans la marque, alors que la légende donne la forme « (amendement N, réécrit) ». Proposition : « la disposition par forces de la carte (Technical Plan, point 7 ter) (amendement 2, réécrit) ».

**D5. l. 1533 : renvoi mort.** « la convention sur la sortie de `layout` est retirée » renvoie à une fonction `layout` que le document ne décrit plus. Proposition : « la convention de `steps_ecrans.py` sur la sortie de `map_layout.layout` (…) est retirée », en résumant la convention en une phrase.

**D6. l. 1545 : « (Create ou Modify) ».** Le gabarit attend Create, Modify ou Delete par fichier. Proposition : `test_palette.py`, `test_force_layout.py` et `test_guide.py` en Create ; `test_texts.py` en Modify (créé au point 23 quinquies).

**D7. l. 1530 : « chemins protégés » manque.** Le Type / Scope du point 23 octies omet « chemins protégés », contrairement aux points 23 ter (l. 1428) et 20. Proposition : « pull request de scénarios, chemins protégés, après la fusion du point 23 septies ».

**D8. l. 1550 et objectifs 17 à 19 : vérifications incomplètes.** Le point 23 decies demande au propriétaire un verdict sur les objectifs 17 à 19, mais leurs *Vérification* (l. 179, 181, 183) ne citent que des tests. Or l'introduction des Goals (l. 132) exige que le document le dise. Proposition : ajouter « et le verdict du propriétaire (plan détaillé, point 23 decies) » à ces trois vérifications.

**D9. l. 128 : renvoi imprécis.** « Sur l'écran unique de l'amendement 1 (plan détaillé, point 23 sexies) » : l'écran est celui du point 23 quinquies, et le point 23 sexies est la partie d'essai. Proposition : « À la partie d'essai du plan détaillé, point 23 sexies, sur l'écran unique de l'amendement 1 (point 23 quinquies)… ».

**D10. Passages non marqués, légèrement dépassés.** Proposition : une précision marquée sur chacun, ou les laisser sous la préséance en le disant.
- l. 249 : « Rien n'est renuméroté : le point 7 bis est nouveau » ; le point 7 ter l'est aussi.
- l. 270 : le schéma indique « cadres Textual (écran unique) ».
- l. 978 : l'alternative N donne encore pour raison « 80 × 24 » ; c'est une raison historique, acceptable.
- l. 232 : le « Given » du CUJ A ne dit pas que l'aide s'ouvre au lancement.
- l. 704 : les termes du client sont dits « propres au point 7 bis », alors que le point 7 ter en ajoute (prochaine étape, panneaux).

**D11. Sections du gabarit sans mention de l'amendement 2.**
- Open Questions (l. 222) : l'amendement 1 y a écrit qu'il n'ouvre aucune question ; l'amendement 2 ne dit rien.
- Additional Resources (l. 1160) : rien sur les maquettes (hors du dépôt) ni sur le dossier de revue `docs/revues/2026-11-22-…`.
- Future Improvements : rien sur le client graphique natif ou le navigateur à réexaminer à M3 (alternatives AC et AD).

  Proposition : une ligne « (amendement 2) » dans chacune, puis les ajouter à la liste des passages touchés.

**D12. ADR 0006, l. 8 et l. 16 : renvois vagues.** « alternatives rejetées : la même porte… » et « l'alternative « Textual en terminal » » désignent l'alternative N du niveau 1 (« une interface web dès le départ », l. 600 à 604). Proposition : « (niveau 1, alternative N) » aux deux endroits. Détail de forme : les ADR voisines écrivent « l'option (a) », l'ADR 0006 écrit « (b) » seul. Écrire « l'option (b) ». Il y a aussi deux lignes vides de suite avant l'alternative AB (l. 1069 et 1070) dans le document.

## Synthèse pour le correcteur

1. **Correctifs de fond, à faire en priorité :**
   - M2 : ajouter au point 28 bis la mesure du temps de rendu ;
   - M3 : ajouter un bloc amendement 2 au Verification Plan ;
   - M1 : récrire la règle du minimum du point 1 (objectifs 17 à 19, ADR 0006).
2. **Marques à ajouter :**
   - M4 : objectif 12 ;
   - M5 : règles d'intégration du volet B ter ;
   - M6 : puce « Code livré » ;
   - M7 : l. 79, 204 et 1138 ;
   - D2 : ligne 2 du tableau.
3. **Cohérence du point 7 ter :** M8 (alertes et barres), M9 (« Journal »), D5 (convention `layout`).
4. **Liste « Passages touchés » à compléter :** point 1 du Technical Plan, plan détaillé point 28 bis, Verification Plan, introduction des alternatives, volet B ter, en-tête, et les sections de D11 si elles sont amendées.
