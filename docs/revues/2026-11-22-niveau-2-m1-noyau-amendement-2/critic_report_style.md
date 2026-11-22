# Étape 7 — Style (amendement 2)

**Fichiers relus :**
- `docs/designs/niveau-2-m1-noyau.md`, uniquement les passages marqués « amendement 2 » : lignes 4-8, 49, 92-94, 126-128, 158, 169, 178-183, 205, 533, 537, 577-614, 880-887, 1071-1093, 1143-1152 et 1514-1550.
- `docs/adr/0006-client-retro-8-bits.md`.

**Références lues :** la persona `agents/style.md`, `docs/glossaire.md` (convention de langue et vocabulaire), `docs/termes-interdits.md`, et le reste du document quand il fallait vérifier la cohérence (conventions, objectifs, Technical Plan 7 bis, CUJ A, plan détaillé 23 quinquies et 28 bis).

**Bilan :** 1 bloquant, 14 majeurs, 22 détails. Aucun terme de `docs/termes-interdits.md` n'apparaît (liste des termes retirée de ce rapport par l'agent de code). Les titres `##` et les intitulés du gabarit sont bien en anglais. Pour la typographie, tout le document met une espace ordinaire avant « : ; ? ! » et à l'intérieur des guillemets « », sans espace insécable. L'amendement 2 suit cet usage : je ne le relève donc pas comme un écart.

---

## Bloquant

### B1. La graine affichée dans la barre du haut contredit le point 7 bis
- **Ligne 583 :** « En haut, une barre : tick, durée de jeu estimée, solde, graine ; »
- **Problème :** la ligne 512 (amendement 1, toujours en vigueur) dit que la graine et le dossier de la partie « restent hors de l'écran de jeu : le client ne reçoit du jeu que l'observation (niveau 1, §5 ; ADR 0003) ». Or la graine ne fait pas partie de l'observation. Les deux textes se contredisent. La règle de préséance donnerait raison à l'amendement 2 en silence, et la règle de la même porte serait rompue sans qu'on le voie.
- **Réécriture proposée :** « En haut, la barre d'état : tick, durée de jeu estimée, solde du portefeuille ; en mode développement, la vitesse demandée. » Si l'on veut vraiment la graine à l'écran, il faut le dire et motiver l'exception au point 7 bis et dans l'ADR 0003.

---

## Majeurs

### M1. Les mêmes éléments s'appellent tantôt « panneau », tantôt « cadre »
- **Lignes 94 et 180 :** « un panneau « Prochaine étape » ». **Ligne 605 :** « **Panneaux.** ». **Lignes 1148, 1542 et 1545 :** « panneaux ». **Ligne 581 :** couleur « panneau ».
- **Ailleurs :** ligne 583, « Chaque cadre reste un widget indépendant » ; ligne 887, « un widget Textual par cadre ».
- **Problème :** les points 7 bis et 79 (amendement 1) et le CUJ A emploient « cadre ». Le lecteur ne sait pas si un panneau est un cadre ou une autre unité d'affichage.
- **Réécriture proposée :** garder « cadre » partout (« le cadre « Prochaine étape » », « **Cadres.** », « carte et cadres tronqués »). Garder « panneau » uniquement comme nom de rôle de couleur, entre guillemets : couleur « panneau ».

### M2. « Journal » entre en collision avec le terme du glossaire
- **Ligne 180 :** « prochaine étape, puis vaisseau, puis marché, puis journal ». **Ligne 583 :** « le journal (quatre lignes) ». **Ligne 608 :** « **Journal :** les dernières lignes de l'historique ». Aussi lignes 887 et 1542.
- **Problème :** dans le glossaire, « journal » désigne le journal des ordres soumis (`OrderLog`). La ligne 509 précise même « Ce n'est pas le journal des ordres ». L'amendement 1 appelait ce cadre « historique » (lignes 79 et 532 ; `history` à la ligne 876). Introduire « journal » pour l'historique du client crée une ambiguïté.
- **Réécriture proposée :** « prochaine étape, puis vaisseau, puis stations, puis historique » ; « En bas, l'historique (quatre lignes) » ; « **Historique :** ses dernières lignes, chacune avec son tick… ».

### M3. « Marché » contredit les Non-Goals
- **Lignes 180, 583, 607, 887 et 1542 :** « Marché ».
- **Problème :** les Non-Goals rangent « Un marché (M6) » et « le marché entre joueurs » hors de M1, et la ligne 209 définit le marché comme le mécanisme qui « fixera les prix selon la nature du minerai et la demande ». Appeler « Marché » le tableau des prix fixes des stations suggère un mécanisme que M1 ne livre pas. L'amendement 1 appelait ce cadre « stations ».
- **Réécriture proposée :** « **Stations :** une ligne par station, une colonne par minerai… ». Sinon, « **Prix :** ».

### M4. « Soute » remplace « cargaison » sans justification
- **Lignes 598 à 600 et 606 :** « soute pleine dans n ticks », « soute non vide dans le système d'une station », « soute pleine ailleurs », « la soute ».
- **Problème :** tout le document (`cargo`, `cargo_capacity`, règle 1 du PNJ « cargaison non vide », messages de refus « cargaison pleine ») dit « cargaison ». Le synonyme oblige à se demander s'il s'agit d'une autre grandeur.
- **Réécriture proposée :** « cargaison pleine dans n ticks », « cargaison non vide dans le système d'une station », « cargaison pleine ailleurs », « le remplissage de la cargaison ».

### M5. « Barre » et « barre des touches » : laquelle est la barre d'état ?
- **Ligne 583 :** « En haut, une barre : … En bas, le journal (quatre lignes) et la barre des touches. » **Ligne 887 :** « … journal, barre d'état, alerte, aide ».
- **Problème :** le CUJ A (ligne 232) et le point 7 bis (ligne 553 : ligne d'aide, « pause », palier) parlent de la « barre d'état ». Le point 7 ter nomme une barre du haut sans la nommer et ajoute une « barre des touches » que la ligne 887 ne mentionne pas. On ne sait pas laquelle reçoit la ligne d'aide d'une touche sans effet.
- **Réécriture proposée :** « En haut, la barre d'état : tick, durée de jeu estimée, solde ; en mode développement, la vitesse demandée ; c'est elle qui affiche la ligne d'aide d'une touche sans effet (point 7 bis). En bas, l'historique (quatre lignes) et la barre des touches, qui rappelle les touches utiles. » Ajouter « barre des touches » à la liste de la ligne 887.

### M6. « Au premier lancement » ou « à chaque lancement » ?
- **Ligne 94 :** « une aide au premier lancement ». **Lignes 49 et 205 :** « aide au premier lancement ». **Ligne 182 :** « s'ouvre au lancement ». **Ligne 610 :** « L'aide s'ouvre au lancement de chaque partie ».
- **Problème :** « premier lancement » se comprend comme la toute première partie, une seule fois. La spécification (ligne 610) dit chaque partie. Le test de la ligne 183 (« ouverture au lancement ») ne tranche pas.
- **Réécriture proposée :** partout, « une aide qui s'ouvre au lancement de chaque partie ».

### M7. Prochaine étape : « l'observation seule » contredit la signature
- **Ligne 180 :** « donne l'action utile suivante, sa durée et sa touche, à partir de l'observation seule ».
- **Problème :** la ligne 579 dit « à partir de l'observation et du modèle client », et la signature (lignes 595 et 881) est `next_step(observation, model)`. La règle 1 (« une alerte attend ») lit d'ailleurs le modèle.
- **Réécriture proposée :** « …à partir de l'observation et de l'état du client (alertes, ordres envoyés), sans autre source d'information du jeu. »

### M8. Les réserves sur la boucle de jeu sont obscures
- **Ligne 128 :** « en gardant en tête qu'il faudra l'étoffer : les mécaniques des jalons suivants (exploration, piraterie…) se répondent. »
- **Ligne 158 :** « la boucle devra être étoffée, ses mécaniques se répondant. »
- **Problème :** « se répondent » ne dit ni qui répond à quoi, ni ce qui en découle pour M1. La forme participiale de la ligne 158 attribue en plus les mécaniques à la boucle actuelle. « Piraterie » ne correspond à aucun terme du document (les Non-Goals disent « les pirates », M6), et « exploration » n'apparaît dans aucun jalon. « En gardant en tête » relève du registre oral.
- **Réécriture proposée :** ligne 128, « Il valide la boucle de jeu actuelle (objectif 11), avec une réserve : elle devra être étoffée par des mécaniques qui interagissent entre elles, attendues des jalons suivants (par exemple les pirates, M6). » Ligne 158, « Le propriétaire l'a validée le 2026-11-22, avec une réserve : les jalons suivants devront l'étoffer de mécaniques qui interagissent entre elles. »

### M9. « 8 bits » et « 16 couleurs » : un jargon contradictoire
- **ADR, ligne 8 :** « choisi la palette 8 bits (16 couleurs) ». **ADR, ligne 14 :** « au style rétro 8 bits (palette fixe de 16 couleurs) ». **Document, lignes 94 et 205 :** « style rétro 8 bits », « palette 8 bits unique ».
- **Problème :** en profondeur de couleur, 16 couleurs font 4 bits, et 8 bits font 256 couleurs. Le chiffre 256 apparaît justement dans le même texte (ADR, ligne 18 ; document, lignes 614 et 1147) avec le sens technique. « 8 bits » désigne ici une esthétique, celle des consoles des années 1980, mais cela n'est dit nulle part.
- **Réécriture proposée :** à la première occurrence, dans l'ADR (Contexte) et dans le document (ligne 94), écrire « style rétro 8 bits (l'esthétique des consoles 8 bits : palette réduite, gros pixels ; ici une palette fixe de 16 couleurs, sans rapport avec la profondeur de couleur du terminal) ».

### M10. « Seize couleurs », dont deux identiques
- **Ligne 581 :** « Seize couleurs fixes, nommées par leur rôle : … accent `#3FD0E0`, … `ore_b` `#3FD0E0` ». Aussi ligne 882 (« seize couleurs ») et ADR, ligne 14 (« 16 couleurs »).
- **Problème :** deux rôles partagent la même valeur, si bien qu'il y a seize rôles mais quinze couleurs distinctes. Le chiffre est faux ou mal formulé. La graphie varie aussi : « seize » dans le document, « 16 » dans l'ADR.
- **Réécriture proposée :** « Seize rôles de couleur, sur quinze valeurs distinctes (accent et `ore_b` partagent `#3FD0E0`) : … », ou bien changer l'une des deux valeurs. Adopter une seule graphie (« 16 » dans les deux fichiers, comme les autres valeurs chiffrées du document).

### M11. Le contraste « 4,5:1 » est un jargon sans référence ni périmètre
- **Ligne 581 :** « Chaque couple texte et fond employé a un contraste d'au moins 4,5:1 ; un test le calcule. »
- **Problème :** la formule de contraste n'est pas nommée (WCAG). « Employé » ne dit pas où la liste des couples est fixée, donc ce que le test énumère.
- **Réécriture proposée :** « Chaque couple texte et fond de la liste `CONTRAST_PAIRS` de `clients/palette.py` a un rapport de contraste d'au moins 4,5 pour 1 (formule WCAG 2.1, niveau AA) ; `tests/clients/test_palette.py` le calcule. » Le nom de la constante est à fixer au point 13.

### M12. Des paramètres vagues dans la disposition par forces
- **Ligne 585 :** « une répulsion en 1/d² entre tous les systèmes, un ressort de longueur fixe sur chaque lien et un faible rappel vers le centre, avec un pas qui décroît. … à une distance d'au moins 0,08 ».
- **Problème :** `d` n'est pas défini. « Faible », « longueur fixe » et « qui décroît » ne sont pas mesurables. Or la ligne 105 exige qu'un agent livre « sans décision ouverte ». La distance 0,08 n'a pas d'unité explicite.
- **Réécriture proposée :** « une répulsion en 1/d², où d est la distance entre deux systèmes ; un ressort de longueur L sur chaque lien ; un rappel vers le centre de raideur k ; un pas qui décroît de façon linéaire de p₀ à 0 (valeurs de L, k et p₀ dans `force_layout.py`, fixées par la pull request de fonctionnalité) … à une distance d'au moins 0,08, en coordonnées du carré [0, 1] × [0, 1]. » Autre solution : écrire explicitement que ces valeurs sont laissées au choix de l'implémentation.

### M13. Le zoom « par pas de 1,25 » est ambigu
- **Ligne 591 :** « par pas de 1,25, de ×1 à ×4. À partir de ×2, … ».
- **Problème :** on ne sait pas si le pas est additif ou multiplicatif. Aucune des deux lectures ne retombe sur ×4 (en additif : 1 ; 2,25 ; 3,5 ; en multiplicatif : … 3,05 ; 3,81 ; 4,77). En plus, la notation « ×1 … ×4 » reprend celle des paliers de vitesse (×1, ×10, ×100) du même client.
- **Réécriture proposée :** « Zoom : la molette, ou `z` (avant) et `x` (arrière) ; chaque cran multiplie ou divise le facteur de zoom par 1,25, borné entre 1 et 4. À partir d'un facteur 2, … » Écrire « facteur de zoom 2 » plutôt que « ×2 » pour ne pas confondre avec la vitesse.

### M14. Les touches partagées (flèches, Entrée) n'ont pas d'ordre de priorité
- **Ligne 592 :** « ou les flèches quand aucune saisie n'est ouverte ». **Ligne 610 :** « Entrée la ferme, et les flèches changent de page ». **Ligne 612 :** « les flèches déplacent la vue quand aucune saisie n'est ouverte ».
- **Problème :** le texte ne dit pas si l'aide ouverte est une « saisie » au sens du point 7 bis (liste des destinations, confirmation). Le point 7 bis (ligne 549) donne à Entrée deux sens, acquitter une alerte ou confirmer, et l'aide en ajoute un troisième sans ordre de priorité. Or l'aide s'ouvre au lancement, alors qu'une alerte peut déjà être affichée.
- **Réécriture proposée :** ajouter au point 7 ter « L'aide ouverte est une saisie : les flèches y changent de page, Entrée la ferme, et les autres touches sont sans effet. Si une alerte arrive pendant que l'aide est ouverte, elle s'affiche à la fermeture de l'aide. »

### M15. Deux renvois faux : la mesure du temps de rendu et la taxe rappelée
- **Lignes 614 et 1150 :** « Le temps de rendu d'une mise à jour est mesuré au plan détaillé, point 28 bis ».
  - **Problème :** le point 28 bis (lignes 1607 à 1612) ne mentionne pas cette mesure, et le tableau des amendements (ligne 49) ne cite pas 28 bis parmi les passages touchés.
  - **Réécriture proposée :** ajouter au point 28 bis « **Proposed Changes (amendement 2, ajout) :** sur la pull request du point 23 nonies, mesurer le temps de rendu d'une mise à jour au palier ×100… », puis ajouter « 28 bis » à la ligne 49. Sinon, renvoyer au point 23 nonies.
- **Ligne 607 :** « la taxe est rappelée ».
  - **Problème :** la ligne 172 précise que la taxe n'est connue que par « l'événement de vente », et la ligne 575 que le montant net « n'est connu qu'après la vente ». On ne sait pas quelle taxe est rappelée, ni d'où le client la tient.
  - **Réécriture proposée :** « le taux de taxe de la dernière vente observée est rappelé, ou « taxe connue après la première vente » s'il n'y en a pas encore. » Autre solution : retirer la mention.

---

## Détails

| N° | Ligne | Texte cité | Problème | Réécriture proposée |
| :-- | :-- | :-- | :-- | :-- |
| D1 | 49, 94 | « carte disposée par forces » | Calque de *force-directed layout*, défini seulement à l'objectif 17 (ligne 178). | Ligne 94 : « une carte de l'univers disposée par forces (les systèmes se repoussent, les liens les retiennent) ». |
| D2 | 94 | « (couleurs et demi-blocs, ADR 0006) » | « Demi-blocs » n'est défini qu'à la ligne 579. | « (couleurs et caractères demi-blocs ▀ ▄, ADR 0006) ». |
| D3 | 94 | « qu'on zoome et qu'on déplace à la souris » | Le clavier est omis, alors que l'ADR insiste : « Le clavier suffit toujours à tout faire ». | « qu'on zoome et qu'on déplace à la souris ou au clavier ». |
| D4 | 49 | « objectifs 11 et 12, objectifs 17 à 19 » | Répétition de « objectifs ». | « objectifs 11, 12 et 17 à 19 ». |
| D5 | 25 | « (CUJ A ; alternatives J à AA) » | Exemple périmé : les alternatives AB à AE existent maintenant. | « (CUJ A ; alternatives J à AE) », ou « (par exemple CUJ A, alternative J) ». |
| D6 | 128, ADR 8 | « une forme de gravité entre les nodes » | Anglicisme, dans une citation exacte. À garder, mais à gloser. | « … entre les nodes [les nœuds] » ou « entre les *nodes* (nœuds) ». |
| D7 | 169 | « sur un terminal de 120 × 36 et sur un monde de 12 systèmes (amendement 2, réécrit) » | Unités absentes. D'après la règle de portée (ligne 43), on ne sait pas si la marque couvre les deux compléments ou seulement le second. | « (amendement 2, réécrit) sur un terminal de 120 colonnes × 36 lignes et sur un monde de 12 systèmes », avec la marque en tête de la phrase. Mêmes unités aux lignes 583, 1148, 1543 et 1545. |
| D8 | 178 | « La carte montre l'univers d'un coup d'œil. » | Formule non mesurable dans un objectif qui doit être « vérifiable ». | « La carte montre tous les systèmes à la fois, sans défilement, au facteur de zoom 1. » |
| D9 | 178 | « un clic sur un système propose d'y aller » | Imprécis, et différent de la ligne 593. | « un clic sur un système ouvre la confirmation du déplacement vers ce système ». |
| D10 | 179 | « la bulle d'information » | Élément cité dans la Vérification sans avoir été introduit dans l'objectif. | Ajouter à l'objectif : « le survol d'un système affiche une bulle d'information (sites, stock, distance) ». |
| D11 | 182, 610 | « les trois gestes (miner, transporter, vendre) » | Terme nouveau, absent du glossaire. Le document dit ailleurs « la boucle extraire, transporter, vendre » (objectif 11, CUJ 1). | « les trois étapes de la boucle de jeu (miner, transporter, vendre) », en gardant ensuite « étapes ». |
| D12 | 182 | « le rythme du temps ; un premier objectif » | Vague : on ne sait pas quel rythme ni quel objectif. | « la durée d'un tick et des actions ; un premier objectif (par exemple, une première vente) ». |
| D13 | 205 | « une palette 8 bits unique » | « Unique » peut se lire comme « originale ». | « une seule palette 8 bits ». |
| D14 | 537 | « ceux du Technical Plan, point 7 ter … de ce point restent en vigueur » | La convention (ligne 14) rend le préfixe inutile à l'intérieur du Technical Plan, et « ce point » est ambigu. | « …sont ceux du point 7 ter. Les touches, …, et les durées du présent point (7 bis) restent en vigueur… ». |
| D15 | 579 | « deux pixels de couleur par case » | « Case » n'est pas défini. | « deux pixels de couleur par case de caractère du terminal ». |
| D16 | 583 | « Au centre à gauche » ; « l'écran demande d'agrandir la fenêtre » ; « durée de jeu estimée » | « Au centre à gauche » se contredit ; l'écran est personnifié ; la durée n'est pas définie. | « À gauche » ; « le client affiche un message qui demande d'agrandir la fenêtre » ; « durée de jeu estimée (ticks écoulés × 3 s) ». |
| D17 | 585 | « Les systèmes partent d'un cercle » ; « Aucun hasard : » | Formulations elliptiques. | « Les systèmes sont d'abord placés sur un cercle » ; « La fonction ne fait aucun tirage aléatoire : ». |
| D18 | 588 à 590 | « pleins entre deux systèmes à portée, pointillés sinon » ; « couleur vaisseau » ; « Une station porte son libellé court » ; « avec son stock ou « ? » » | « Sinon » est ambigu quand un seul des deux systèmes est à portée. Les noms de rôle ne sont pas signalés comme tels. « Une station porte » est flou. La condition du « ? » manque. | « pleins quand les deux systèmes sont à portée, pointillés dans les autres cas » ; « de la couleur « vaisseau » » ; « un système qui a une station affiche le libellé court de celle-ci (`S1`) » ; « avec son stock, ou « ? » hors de portée ». |
| D19 | 591 à 592 | « chaque système affiche aussi son nom » ; « glisser avec le bouton gauche » ; « Une mini-carte » | Aucun nom n'est inventé (Non-Goals) : il s'agit de l'identifiant. « Glisser » est elliptique. La position de la mini-carte n'est pas donnée. | « son libellé (`system_5`) » ; « faire glisser la vue, bouton gauche enfoncé » ; « une mini-carte, dans le coin inférieur droit de la carte ». |
| D20 | 597 à 603 | « arrivée à `system_k` dans n ticks » ; « soute pleine dans n ticks » ; « stock … connu comme nul » / « connu comme vide » ; « le prix d'ici » ; phrase de la ligne 603 collée à la liste | Les marqueurs de champ varient : le point 23 quinquies (ligne 1491) utilise `[system_k]` et `[n]`. La règle 3 oublie l'épuisement du gisement (le minimum de la ligne 572). « Nul » et « vide » alternent. « D'ici » est familier. Sans ligne vide, la phrase de la ligne 603 s'intègre en Markdown à l'élément 7. | `[system_k]`, `[n]` ; « fin du minage dans [n] ticks » ; « connu comme vide » dans les deux règles ; « le prix de cette station » ; une ligne vide avant « La prochaine étape ne fait que guider ». |
| D21 | 606, 610 | « deux barres de progression en demi-blocs, le trajet (ou le minage) et la soute » ; « (1) … ; (2) toutes les touches » | L'apposition est elliptique. L'énumération en ligne, avec des points-virgules imbriqués, est trop longue pour une phrase. | « deux barres de progression en demi-blocs : l'une pour le trajet ou le minage en cours, l'autre pour le remplissage de la cargaison » ; découper l'aide en liste : « - page 1 : … ; - page 2 : toutes les touches. ». |
| D22 | 887, 1532, 1533, 1542, 1545 | « carte MapView » ; « devient « la carte place … et toujours les mêmes » » ; « la convention sur la sortie de `layout` » ; « « Journal », l'aide » ; « (Create ou Modify) » | Le nom de classe n'est pas en code. Le nouveau nom de scénario est en minuscule, contrairement à l'ancien, et « toujours les mêmes » est vague. `layout` n'est pas défini. La liste n'a pas de « et ». Pour l'opération de fichier, le gabarit attend Create/Modify fichier par fichier. | « carte (`MapView`) » ; « « La carte place chaque système une fois, à des positions distinctes, identiques d'un appel à l'autre » » ; nommer la fonction ou le point concerné ; « « Journal » et l'aide » ; « `test_palette.py`, `test_force_layout.py`, `test_guide.py` (Create) ; `test_texts.py` (Modify) », avec le chemin `tests/clients/` complet. |

### Détails propres à l'ADR 0006 et aux alternatives AB à AE

- **ADR, lignes 11 et 18, « couleurs vraies » :** calque de *true color*, non défini. → « couleurs 24 bits (*true color*) ».
- **ADR, ligne 11, « seul le dessin du client change » :** inexact, puisque la même option introduit la souris et la molette. → « seuls le dessin et les commandes du client changent ».
- **ADR, ligne 13, et document, ligne 1086, « le transport WebSocket avancé de M3 à M1 » :** « avancé » peut se lire comme un adjectif (perfectionné) ou comme un participe (déplacé plus tôt). → « le transport WebSocket, prévu à M3, à avancer à M1 ».
- **ADR, ligne 17, « rangées dans ses Non-Goals pour M3 » :** le possessif est ambigu. → « rangées pour M3 dans les Non-Goals du niveau 2 de M1 ».
- **ADR, ligne 19, « le pilote de Textual, qui joue aussi la souris » :** « jouer » est impropre ici. → « qui simule aussi la souris ».
- **ADR, ligne 8 :** le paragraphe Contexte enchaîne cinq phrases et quatre citations. On peut le scinder en « Constat » (partie d'essai) et « Demande » (esthétique, graphe, palette).
- **ADR, ligne 20, et document, ligne 1074, « illisible » :** le propriétaire a dit « visible, mais vraiment pas clair ». « Illisible » déforme la citation. → « peu clair » (alternative AB : « c'est ce que le propriétaire a jugé peu clair »).
- **Document, ligne 1080, « le terminal suffit, comme les maquettes l'ont montré » :** affirmation invérifiable, les maquettes étant hors du dépôt. → « le propriétaire a jugé suffisantes les maquettes dans le terminal ».
- **Document, ligne 1081, « bute sur le terminal » :** registre familier, et différent de la condition de l'ADR. → « échoue pour une raison propre au terminal (rendu, taille, police) ».
- **Document, lignes 1071 et 1089 :** les alternatives AB (« garder l'ASCII et le soigner ») et AE (« garder la mise en page en colonnes ») se recouvrent presque entièrement. Il faudrait les fusionner, ou préciser que AB porte sur le style et AE sur la disposition.
- **Document, ligne 1093, « `clients/map_layout.py` est retiré » :** → « est supprimé », pour correspondre au « Delete » de la ligne 1544.
- **Document, ligne 1147, « palette pensée pour rester lisible en 256 couleurs » :** affirmation invérifiable, puisque le test de contraste porte sur les 16 couleurs, pas sur la palette dégradée. → « contraste vérifié sur les 16 couleurs ; rendu en 256 couleurs jugé à la partie d'essai », ou ajouter un test sur la conversion en 256 couleurs.
- **Document, ligne 1152, « règles simples et ordonnées » :** jugement subjectif. → « sept règles ordonnées, testées cas par cas ».
- **Document, ligne 1516, « une seule pull request de chaque type étant ouverte à la fois » :** le participe ne dit pas s'il s'agit d'une condition ou d'un constat. → « …peut avancer en parallèle, à condition qu'une seule pull request de chaque type (protégée, de scénarios, de fonctionnalité) soit ouverte à la fois. » Gravité limite entre majeur et détail.
- **Document, ligne 1550, « avec la graine, la taille et le nom du terminal » :** → « avec la graine, la taille du terminal (colonnes × lignes) et son nom ».
