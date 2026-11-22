# Étape 7, tour 2 — Conception (amendement 2)

**Cible :** `docs/designs/niveau-2-m1-noyau.md`, passages marqués « amendement 2 » : objectifs 12 et 17 à 19 (l. 161-183), Technical Plan, point 7 ter (l. 580-672), point 13 (l. 940-954), alternatives AB à AG (l. 1138-1175), risques ajoutés par l'amendement 2 (l. 1225-1234), volet B ter (l. 1599-1649), point 28 bis (l. 1713), Verification Plan (l. 1817-1824).
**Pièces lues :** `docs/adr/0006-client-retro-8-bits.md`, `docs/designs/architecture-niveau-1.md`, `docs/glossaire.md` ; code : `src/fourx/policies/scripted_miner.py`, `src/fourx/schema/observation.py`, `src/fourx/schema/events.py`, `src/fourx/clients/model.py`, `src/fourx/core/world.py`, `src/fourx/core/step.py`, `src/fourx/core/tunables.toml`, `setup.cfg` ; tour 1 : `docs/revues/2026-11-22-niveau-2-m1-noyau-amendement-2/critic_report_design.md` et `goldfish_review_report.md`.
**Gabarit :** `(plugin EGM) resources/document_standards/feature-spec-standard.md`. **Persona :** design_critic, mode REVIEW.
**Revue complète :** j'ai lu tous les fichiers requis. Les décisions E1 à E4 ne sont pas rediscutées.

## Verdict

**Non approuvable en l'état : 0 bloquant, 5 majeurs, 15 détails.**

Le tour 1 a été bien corrigé :
- Le bloquant (graine et taxe) est levé.
- Six des huit majeurs sont corrigés entièrement.
- Les deux autres (M2, prochaine étape ; M3, disposition) sont corrigés sur le fond, mais laissent chacun un défaut résiduel.

Choisir `scripted_miner.decide` pour fonder la prochaine étape est une bonne idée : une seule règle de décision, et les départages et le repli viennent avec. J'ai vérifié la traduction contre le code. Elle est juste pour l'arrêt : `_commande` ne rend `None`, pour un vaisseau `IDLE`, que si aucun gisement ne convient. La séquence du scénario du point 23 octies est cohérente.

Les nouveaux défauts portent sur cinq points :
- la garantie de lisibilité de la carte (critère euclidien contre l'encombrement réel des glyphes) ;
- le contraste des liens, exclu des tests ;
- deux durées de la prochaine étape, l'une inobservable, l'autre fausse ;
- les conséquences non pesées du choix « conseil = PNJ » ;
- le coût du test sur 2 000 graines sous la mutation.

---

## 1. Suivi des constats du tour 1

| Constat du tour 1 | État | Où | Commentaire |
| :-- | :-- | :-- | :-- |
| **B1** Graine et taxe hors de l'observation | **Corrigé** | l. 582, 598, 663 | La graine est retirée de la barre ; la taxe n'est plus qu'évoquée (« moins une taxe »), sans taux. |
| **M1** Règle du minimum, ADR, §11 | **Corrigé** | l. 279, 300, 49 ; ADR, Conséquences | Objectifs 12 à 19, ADR 0003 à 0006, priorité des décisions du 2026-11-22, critère du §11 inchangé. |
| **M2** Prochaine étape | **Corrigé, avec résidus** | l. 633-651 | Règles « ordre envoyé », « fin du minage », repli et départages : traités, par réutilisation de `decide`. Restent une condition inobservable (règle 4) et une durée fausse (traduction de `Mine`) : voir **Majeur 3**. |
| **M3** Disposition sans garantie | **Partiellement corrigé** | l. 610-616 | Constantes, normalisation, passe de séparation, départ en couches, croisements mesurés : faits. Au zoom 1, il ne reste que la pastille et le losange. Mais la distance minimale n'est toujours pas dérivée de l'encombrement des glyphes (proposition du tour 1, non reprise) : voir **Majeur 1**. |
| **M4** Palette | **Corrigé, avec un nouvel écart** | l. 592, 1229 | L'accent est distinct (`ore_b` passe à `#5AA0FF`), la lettre `a`/`b` est ajoutée, `CONTRAST_PAIRS` est listé (j'ai recalculé le minimum : `alerte` sur `cadre` = 5,07, conforme). La tenue en 256 couleurs est renvoyée à la partie d'essai, avec `COLORTERM` consigné : choix acceptable. Nouvel écart : les traits sont exclus du test, et les liens hors de portée sont presque invisibles (**Majeur 2**). |
| **M5** Redessin et mesure | **Corrigé** | l. 631, 1713, 1232 | Entrées de la grille explicites, plafond de 10 Hz, puce au point 28 bis avec seuils (30 ms en moyenne, 100 ms au plus). |
| **M6** Vérification de l'objectif 12 | **Corrigé** | l. 169 | Chaque information a un cadre texte ; la carte est vérifiée par ses propres tests. |
| **M7** Passages caducs, Verification Plan | **Corrigé** | l. 94, 1220, 1555, 1811, 1813, 1817-1824 | Marques de remplacement et bloc « (amendement 2) » présents. |
| **M8** Animation et méthodes non pesées | **Corrigé** | l. 1162-1175 ; ADR, option (b′) | Alternatives AF et AG ajoutées ; (b′) est citée dans la condition de révision. |
| D1, D2, D3, D4, D6, D7, D8, D10, D11, D12, D13, D15 | Corrigés | — | D15 réglé par E3. |
| D5 Clic | Corrigé pour l'essentiel | l. 621, 630 | Le clic pendant un trajet suit le comportement de `d` (refus `SHIP_EN_ROUTE` traduit) : cohérent. |
| D9 Fenêtre entre 100 × 30 et 120 × 36 | Partiellement corrigé | l. 608 | La largeur est réglée, pas la hauteur : voir détail d3. |
| D14 Maquettes hors du dépôt | Non corrigé, sans justification | l. 1243 ; l. 1147 | Voir détail d13. |
| D16 Glossaire | Écarté avec raison | l. 764 | Raison acceptable : termes propres au client, comme au point 7 bis. |

---

## 2. Majeurs

### Majeur 1. La distance minimale de 0,08 ne garantit pas que les systèmes ne se recouvrent pas à l'écran

- **Passages :** l. 614 (séparation à 0,08, puis retour dans [0, 1]²), l. 616 (tests sur les graines 1 à 2 000), l. 620 (le carré occupe toute la hauteur, deux pixels par ligne), l. 626-627 (une pastille de deux caractères, puis `◆a`, et `▲3` au-dessus du système), l. 608 (100 × 30 au moins), l. 1233 (parade du risque).
- **Problème :**
  1. **Le critère est euclidien, l'encombrement est rectangulaire.** À 120 × 36, la carte fait environ 26 lignes utiles, donc environ 52 pixels de haut : 0,08 vaut environ 4,2 pixels, soit environ 4 colonnes ou 2 lignes. Un système occupe 4 colonnes sur une ligne (pastille et `◆a`), plus une ligne au-dessus s'il a des vaisseaux (`▲3`). Trois cas :
     - deux systèmes alignés horizontalement à 0,08 se touchent (« 05◆a07◆b » : à quel système appartient le losange ?) ;
     - en diagonale (environ 3 colonnes et 1,5 ligne d'écart), le `▲` de l'un tombe sur le `◆a` de l'autre ;
     - à 100 × 30, la carte ne fait plus qu'environ 20 lignes utiles, et 0,08 vaut environ 3 colonnes, moins que les 4 de l'encombrement : le recouvrement est certain pour deux systèmes alignés.
  2. **Rien ne règle les collisions au zoom 1.** L'ordre de dessin (liens, route, systèmes, vaisseaux, étiquettes) fait qu'un élément écrase le précédent. La règle « coupée avant la première case occupée » ne vaut que pour les étiquettes, à partir du zoom 2.
  3. **La séparation n'est pas garantie.** Au bout de 50 passes, rien n'est prévu si une paire reste trop proche. Le retour dans [0, 1]² peut recréer une violation. Le texte ne dit pas non plus si ce retour se fait à chaque passe ou une seule fois à la fin. Enfin, le test ne couvre que les graines 1 à 2 000, alors que le joueur peut lancer n'importe quelle graine.
  4. **Le bord n'est pas traité.** Ramené à x = 1 ou à y = 0, un système voit son `◆a` déborder à droite, ou son `▲` en haut, hors du carré : il est coupé à 100 × 30, où les marges latérales ne font que 4 à 6 colonnes.
- **Conséquence :** l'objectif 17 (« tous les systèmes à la fois ») et le risque « Disposition illisible » peuvent échouer à la partie d'essai alors que les tests sont verts. C'est le défaut exact signalé au tour 1 (M3), qui n'est corrigé qu'à moitié.
- **Proposition :**
  - tester la non-superposition **dans la grille**, et non dans le carré : pour chaque graine, `render` au zoom 1, en 120 × 36 et en 100 × 30, ne doit poser aucune case de pastille, de losange ou de `▲` sur une case d'un autre système (avec une case de marge) ;
  - faire travailler la séparation sur une distance anisotrope, ou sur des boîtes (largeur ≈ 4 pixels, hauteur ≈ 4 pixels avec la ligne du `▲`), exprimée dans le pire cas de 100 × 30 ;
  - ramener dans [0,05 ; 0,95]² à chaque passe, et non dans [0, 1]² ;
  - dire ce qui se passe après 50 passes sans succès (par exemple, réduire l'échelle autour du centre et recommencer, ou accepter et consigner) ;
  - corriger la parade de la l. 1233 en conséquence.

### Majeur 2. Les liens hors de portée sont presque invisibles, et leur contraste n'est pas testé

- **Passages :** l. 592 (« Les traits ne sont pas du texte : ils n'y figurent pas » ; `trait_faible` `#26304F`, `fond` `#0B0E1A`), l. 625 (liens hors de portée : « un pixel sur deux, en `trait_faible` »), l. 178 (objectif 17).
- **Problème :** calcul WCAG 2.1, que j'ai refait sur les valeurs du document :
  - `trait_faible` sur `fond` : environ **1,48 pour 1** (1,35 sur `cadre`, si c'est le fond de la carte, que le document ne fixe pas) ;
  - `trait_fort` sur `fond` : environ 3,5 pour 1.

  La portée ne couvre que le système du vaisseau et ses voisins, sur 8 à 12 systèmes. La plupart des liens, donc la plus grande partie du graphe, sont dessinés en pointillé, à un pixel demi-bloc sur deux, sous 1,5 pour 1. Le critère WCAG 1.4.11 (contraste des éléments graphiques non textuels) demande 3 pour 1 pour un élément nécessaire à la compréhension. En 256 couleurs, les deux teintes peuvent même tomber sur la même entrée.
- **Conséquence :** le joueur ne voit pas les routes au-delà de son voisinage. C'est la vue d'ensemble du graphe que demandait le propriétaire (« clair et joli »), et elle sert au choix de route de l'objectif 12. Le test de palette ne le signalera pas, puisqu'il exclut les traits.
- **Proposition :**
  - ajouter à `palette.py` une liste `GRAPHIC_PAIRS` (trait et fond de la carte), testée à au moins 3 pour 1 ;
  - éclaircir `trait_faible` (vers `#4A5580`, environ 2,6 pour 1, ou plus) ;
  - ou distinguer la portée par la continuité du trait (plein ou pointillé) et non par une teinte presque noire ;
  - fixer la couleur de fond de la carte.

### Majeur 3. Deux durées de la prochaine étape : l'une est inobservable, l'autre est fausse

- **Passages :** l. 641 (règle 4 : « au plus [durée] si un autre vaisseau visible **mine** le même gisement »), l. 648 (traduction de `Mine(ore)` : « cargaison pleine dans [durée] »), l. 169 (objectif 12 : « chaque durée affichée est égale au nombre de ticks observé avant l'événement »), l. 575.
- **Problème :**
  1. **La condition de la règle 4 est inobservable.** `OtherShipView` ne porte que `id`, `owner_id`, `system_id` et `capacity` (`src/fourx/schema/observation.py`). `MiningStarted` est de classe `PRIVATE` (`src/fourx/schema/events.py`). Le glossaire et l'ADR 0005 excluent l'activité des vaisseaux d'autrui. Le client ne peut donc pas savoir qu'un autre vaisseau mine. Il sait seulement qu'un autre vaisseau est dans le système, ou il peut le déduire d'une baisse du stock supérieure à `mining_rate` entre deux observations.
  2. **La traduction de `Mine` refait l'erreur corrigée à la règle 4.** Avant de miner, le stock du gisement local est connu (le système est à portée). Si le stock est inférieur à la capacité libre, « cargaison pleine dans [durée] » est faux. Le test de l'objectif 12 (durée affichée = ticks observés) échouerait sur ce cas.
- **Conséquence :** l'agent de code doit inventer la règle 4. Pire, il pourrait chercher l'activité d'autrui ailleurs que dans l'observation, ce qui violerait le niveau 1, §5. La seconde phrase contredit la vérification de l'objectif 12.
- **Proposition :**
  - règle 4 : « au plus [durée] si un autre vaisseau est visible dans ce système » (observable : `other_ships[i].system_id`), ou « si le stock a baissé de plus de `mining_rate` au dernier tick » (le modèle garde l'observation précédente) ;
  - `Mine(ore)` : « fin du minage dans [durée] » avec la formule de la l. 575 (min de la capacité libre et du stock), et la même mention « au plus » ;
  - ajouter ces deux cas aux tests du point 23 nonies.

### Majeur 4. « Conseil = règle du PNJ » : les conséquences pour le joueur ne sont ni pesées ni rangées dans les risques

- **Passages :** l. 642-651 (« Comme elle, il ne pèse pas la durée du trajet »), l. 530 (avec les prix proposés, tous les PNJ visent `ore_b` et minent souvent un seul gisement : environ 78 % des mondes), l. 668 (aide : « Premier objectif : vendre une première cargaison »), l. 1234 (risque « Prochaine étape trompeuse », parade : « une seule règle de décision »), alternatives AB à AG.
- **Problème :** avec `station_ore_prices = [[10, 15], [12, 12], [8, 18]]`, `ore_b` a toujours le meilleur prix. La prochaine étape enverra donc toujours le joueur :
  - au gisement de `ore_b` le plus proche, même s'il y a un gisement de `ore_a` dans son système ou à un saut ;
  - puis à la station qui paie le mieux `ore_b`, quelle que soit la distance.

  Trois conséquences :
  - le premier objectif peut demander un cycle de plusieurs sauts, plus d'une heure à 3 s par tick, alors qu'un cycle local dure environ 5 minutes (l. 158) ;
  - le joueur est envoyé là où se tassent les PNJ : un gisement miné par cinq PNJ se vide en environ 4 040 ticks (l. 530) ;
  - avec un seul vaisseau et sans activité visible des autres, le joueur risque d'arriver sur un gisement vide.

  Aucune alternative ne compare ce choix à un conseil propre au joueur : gain par tick du cycle, ou deux options affichées (« le plus rentable » et « le plus proche »). La parade du risque (« une seule règle de décision ») est la cause du risque, pas sa parade.
- **Conséquence :** la règle des alternatives du gabarit n'est pas satisfaite pour un choix central de l'objectif 18. Le propriétaire peut juger à la partie d'essai que le guide le dessert (attentes longues, conseils identiques à ceux des PNJ), sans que le document l'ait prévu.
- **Proposition :**
  - ajouter une alternative AH, « prochaine étape : règle du PNJ, règle propre au joueur (gain par tick), ou deux options affichées », avec ses raisons datées ;
  - nommer les conséquences dans le risque de la l. 1234 (cycle long, entassement avec les PNJ), avec un signal réel : la partie d'essai, et la durée du premier cycle consignée au compte rendu ;
  - option peu coûteuse et compatible avec « une seule règle » : ajouter au détail la durée du cycle complet conseillé (aller, minage, vente), pour que le joueur voie le prix en temps ;
  - faire confirmer le choix par le propriétaire.

### Majeur 5. Le test de la disposition sur 2 000 graines peut faire exploser la mutation du point 23 decies

- **Passages :** l. 616 (graines 1 à 2 000, « une graine qui échoue rend la pull request rouge »), l. 612 (300 itérations), l. 1644, l. 1822 (`force_layout.py` est muté), l. 1184 et point 28 bis (au-delà de 30 minutes par tâche, l'agent de code s'arrête) ; `setup.cfg` (la mutation lance `-m "not rejeu and not lent and not mesure"`, donc les tests `proprietes`).
- **Problème :**
  - En Python pur, une disposition coûte environ 300 itérations × (66 paires de répulsion, plus les ressorts), soit de l'ordre de 50 à 100 ms. Avec la génération du monde et le comptage des croisements, 2 000 graines font donc 2 à 4 minutes par lancement.
  - `mutmut` relance, pour chaque mutant de `force_layout.py`, les tests qui l'appellent, ce test compris : 50 à 100 mutants × 2 à 4 minutes, soit plusieurs heures.
  - Les tests de propriétés existants se limitent à 30 à 60 exemples (`tests/proprietes/test_proprietes.py`).
  - Aucune mesure ni aucun marqueur n'est prévu.
- **Conséquence :** la tâche `mutation` du point 23 decies dépasse le seuil de 30 minutes. Le point 23 decies risque d'être bloqué par le plan lui-même.
- **Proposition :**
  - marquer la passe sur 2 000 graines `lent`, exclue de la mutation, lancée par la tâche `rejeu` comme le test des fourchettes, ou par une tâche dédiée ;
  - garder dans `proprietes` un échantillon d'environ 50 graines ;
  - mesurer le temps d'une disposition dans la description de la pull request du point 23 decies.

---

## 3. Détails

| N° | Passage (ligne) | Problème | Conséquence | Proposition |
| :-- | :-- | :-- | :-- | :-- |
| d1 | l. 626-627, 623, 625 | La case d'ancrage de la pastille n'est pas définie : centrée sur le pixel projeté, ou commençant à sa colonne ? Les liens vont « entre les centres » sans dire de quoi. Le `▲` du joueur « sur son système » écrase le numéro (les vaisseaux se dessinent après les systèmes) | `system_at` et les tests de la grille dépendront d'un choix implicite ; le joueur perd le numéro de son propre système | Fixer : colonne = arrondi de x, ligne = ⌊y ÷ 2⌋, pastille sur cette case et la suivante ; le `▲` du joueur à gauche de la pastille ; axe y vers le bas |
| d2 | l. 616 | « Croisement » n'est pas défini (liens qui partagent une extrémité ?). Une moyenne masque les pires graines. Un lien qui passe sous la pastille d'un tiers (fausse connexion visuelle) n'est pas mesuré | Seuil d'alerte peu parlant | Définir le croisement (extrémités communes exclues) ; publier aussi le maximum et la part des mondes qui en ont ; compter les liens qui traversent une pastille |
| d3 | l. 608, 600-602 | Entre 36 et 30 lignes, la colonne de droite perd 6 lignes, sans dire lesquelles | Disposition à 100 × 30 non testable telle quelle | Dire quel cadre rétrécit (Stations) et tester le pilote en 100 × 30 |
| d4 | l. 602, l. 546 | La liste des destinations (jusqu'à 12 systèmes, plus la ligne de coût) s'ouvre à la place de Stations : 13 lignes moins le cadre, soit environ 11 lignes utiles, encore moins à 100 × 30 | Liste tronquée sans défilement prévu | Dire que la liste défile, ou l'ouvrir sur la carte et Stations ensemble |
| d5 | l. 655, l. 628 ; CUJ A, l. 235 ; Overview, l. 81 | Le stock des gisements proches n'apparaît dans aucun cadre texte : seulement au zoom 2 et plus, et dans la bulle. Le CUJ A (amendement 1, toujours en vigueur) l'attend sur l'écran | Information du CUJ A cachée au zoom 1 | Ajouter le stock, ou « ? », dans les lignes par minerai de Stations (« ore_b : system_3 (20000), system_7 (?) ») |
| d6 | l. 645 et l. 548 | Le titre dit « Vendre [ore] » (le minerai le plus abondant), mais `v` vend toute la cargaison, minerai par minerai | Petit écart entre le conseil et l'effet de la touche | « Vendre la cargaison à [station] », le détail donnant le prix de chaque minerai |
| d7 | l. 646-647 | Le conseil `Move` donne `d`, mais la liste s'ouvre sur la première ligne : le joueur doit retrouver le système conseillé | Friction inutile | Ouvrir la liste sur la destination conseillée quand `d` suit un conseil `Move` |
| d8 | l. 651, l. 889 et 923-925 ; l. 530 | `clients` appelle `scripted_miner.decide` et `mettre_a_jour`, alors que la l. 530 justifie l'import de `policies` par des modules « sans logique de décision ». `mettre_a_jour` ne figure pas au point 13 | Interface implicite ; justification de l'import devenue partielle | Ajouter `mettre_a_jour(observation, seen_empty) -> frozenset[int]` au point 13 ; compléter la l. 530 (« et `scripted_miner`, pour la prochaine étape, point 7 ter ») |
| d9 | l. 656, l. 600 | L'alerte est rouge (`alerte`) dans « Prochaine étape », mais jaune (`vaisseau`) dans l'historique ; le rouge sert aussi aux refus | Même événement en deux couleurs ; une arrivée lue comme une erreur | Une seule couleur pour l'alerte (`vaisseau`), le rouge réservé aux refus |
| d10 | l. 667, l. 658, l. 183 | La ligne 9 de l'aide (« une ligne par touche ») n'a pas de texte fixé, alors que les tests comparent l'aide « en entier ». Les touches du mode développement : affichées sans `--dev` ? `help_pages(observation)` n'a pas de paramètre qui le dise | Texte non contractuel ; aide qui montre des touches inactives | Écrire les lignes des touches ; ajouter `dev: bool` à `help_pages` |
| d11 | l. 665 | « un tick dure environ 3 secondes » ignore `--periode` et les paliers, contrairement à la règle des l. 578 et 598 (« à 3 s ») | Estimation trompeuse en `--dev` | « environ 3 secondes à la vitesse normale » |
| d12 | l. 1620 | Le monde du scénario ne dit pas que le système du gisement n'a pas de station. S'il en a une, la suite devient … ("enter",), ("v",) sans le second ("d",) | Scénario fragile selon les étapes | Ajouter « sans station dans le système du gisement » ; dire aussi que le gisement à un saut est du minerai le mieux payé, ou accepter explicitement un trajet plus long |
| d13 | l. 1243, l. 1147 ; ADR, option (b′) | Les maquettes, qui fondent le rejet des options (b′) et (c) (« les demi-blocs suffisent aux maquettes »), restent hors du dépôt (constat D14 du tour 1, non traité et non justifié) | Justification invérifiable par un relecteur sans contexte | Verser une capture SVG (export de Textual) dans le dossier de revue, ou écrire pourquoi ce n'est pas fait |
| d14 | l. 592, l. 605-606 | Le fond de l'aide, de la bulle et de la carte n'est pas fixé. Si c'est `cadre_clair`, les textes colorés (accent, minerais) sur `cadre_clair` ne sont pas dans `CONTRAST_PAIRS` | Couples réellement employés non testés | Fixer ces fonds et compléter `CONTRAST_PAIRS` |
| d15 | l. 631 | Les stocks visibles font partie des entrées de la grille, même au zoom 1 où ils ne sont pas dessinés. En minage à portée, la grille se recalcule donc à chaque tick | Calcul inutile, borné par les 10 Hz | Ne compter les stocks qu'à partir du zoom 2 |

---

## 4. Cohérence avec le reste du document et le niveau 1

- **Niveau 1, §5 (aucun autre canal) :** respecté pour la graine, la taxe et les durées. Seule la règle 4 de la prochaine étape demande une information absente de l'observation (Majeur 3).
- **Niveau 1, §1 (imports) :** `clients` → `policies` est permis (§1, l. 169 du niveau 1). L'appel à une fonction de décision change la justification de la l. 530 (d8).
- **Niveau 1, Overview et §11 :** l'Overview est déjà modifiée sur la branche ; le critère « client Textual minimal » est maintenu par la l. 279 et par l'ADR. Cohérent.
- **Déterminisme :** les flottants sont confinés au client, hors de toute empreinte (l. 582). Cohérent avec le niveau 1, §2.
- **ADR 0005 (proximité) :** cohérente pour les halos de portée, le « ? », `▲n` et la portée recalculée. Seul écart : la règle 4 (Majeur 3).
- **Point 7 bis :** le renvoi de la l. 540 est propre. Les touches ajoutées (`h`, `z`, `x`, `c`, flèches) n'entrent pas en conflit avec la table d'origine hors saisie.
- **Plan détaillé :** le découpage en deux pull requests (E3) est bien reflété aux points 23 nonies et 23 decies. La seule faiblesse est le coût de la mutation (Majeur 5).
- **Gabarit (feature-spec) :** Problem, Goals, Non-Goals, Architecture et Risks sont présents. Il manque une alternative pour le choix « conseil = PNJ » (Majeur 4). Les risques de lisibilité de la carte ont une parade qui ne couvre pas leur cause réelle (Majeurs 1 et 2).
