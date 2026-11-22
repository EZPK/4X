# Étape 8 : Prise de recul (amendement 2)

**Persona :** Skeptical Architect (zoom_out), mode REVIEW, sans contexte.
**Standard appliqué :** `(plugin EGM) resources/document_standards/zoom-out-standard.md`
**Cible :**
- `docs/designs/niveau-2-m1-noyau.md` : les passages « amendement 2 » (l. 49, 92-94, 126-128, 158, 169, 178-183, 205, 533-537, 577-614, 880-887, 1071-1093, 1143-1152, 1514-1550)
- `docs/adr/0006-client-retro-8-bits.md`

**Contexte lu :** `docs/feuille-de-route.md`, `docs/designs/architecture-niveau-1.md` (§11, l. 493-503, et l. 16), le code de `src/fourx/clients/` (pour voir ce qui existe déjà) et `.github/scripts/mutation.py` (règle de score par fichier).

Tous les fichiers nécessaires ont pu être lus. La revue est complète.

---

## Verdict

**Aucun constat bloquant. Six constats majeurs, neuf détails.**

Le contexte suffit : le paragraphe « (amendement 2) » de The Problem (l. 128) dit ce qui manque et pourquoi. L'amendement répond bien au besoin exprimé :
- l'information est hiérarchisée ;
- il y a une aide et une explication des mécaniques ;
- l'esthétique est rétro ;
- le graphe est disposé par forces et se zoome.

Il a aussi de bonnes retenues :
- le tutoriel complet reste à M3 ;
- il n'y a qu'un thème de couleur ;
- la disposition est calculée une fois, sans simulation physique animée ;
- rien ne change dans le protocole, l'observation ni les règles.

Il en fait pourtant un peu plus que le besoin, surtout du côté de la souris (survol, glisser, mini-carte). Il refait en double la logique de décision du PNJ dans la « Prochaine étape ». Il regroupe tout dans une seule grosse pull request de fonctionnalité. Enfin, il laisse ouverte la question qui compte le plus pour le calendrier : le verdict subjectif sur l'écran bloque-t-il la livraison de M1 ? Le critère de sortie du niveau 1 ne demande qu'un « client Textual minimal » et la validation de la boucle, qui est déjà obtenue (l. 158).

## Le besoin face à l'amendement

| Besoin du propriétaire (l. 128) | Réponse de l'amendement | Ce qui dépasse le besoin |
| :-- | :-- | :-- |
| « L'information n'est pas hiérarchisée » | panneau « Prochaine étape », ordre des panneaux (l. 180, 583) | rien |
| « Pas d'aide, pas de tuto, pas d'explication des mécaniques » | aide « Comment jouer » (l. 182, 610) | une deuxième page de touches, qui répète la barre des touches |
| « Esthétique rétro, 4 ou 8 bits » ; palette choisie | palette fixe, demi-blocs (l. 581) | test de contraste (petit) |
| « Graphe clair et joli », « gravité entre les nodes » | disposition par forces, calculée une fois (l. 585) | rien |
| « Qu'on puisse zoomer » | molette, `z`/`x`, ×1 à ×4 par pas de 1,25 (l. 591) | mini-carte ; zoom continu |
| (rien de demandé) | glisser à la souris, survol avec bulle, clic qui ouvre la confirmation de déplacement (l. 592-593) | survol et glisser : surplus net. Le clic est discutable mais bon marché |

---

## Constats majeurs

### Majeur 1 : la livraison de M1 dépend d'un verdict subjectif sur l'écran, que le niveau 1 ne demande pas

- **Passages :**
  - l. 169 (objectif 12, verdict « rendu après la partie d'essai de l'amendement 2 ») ;
  - l. 1550 (point 23 decies, verdict sur les objectifs 17 à 19) ;
  - l. 1516 (« s'insèrent entre le point 23 sexies et le volet C » puis « le volet C peut avancer en parallèle ») ;
  - ADR, l. 20 ;
  - niveau 1, §11, l. 498 (« client Textual minimal ».)
- **Pourquoi c'est un problème :**
  - Le critère de sortie de M1, au niveau 1, porte sur le CUJ 1, le CUJ 4, l'économie, le rejeu et la validation de la boucle. La boucle est validée depuis le 2026-11-22 (l. 158).
  - L'amendement fait des objectifs 17 à 19, et du verdict de l'objectif 12, des conditions de M1, sans dire ce qui se passe si le verdict est négatif. Un écran est un objet qu'on peut retoucher sans fin : M1 risque de rester ouvert sur une question d'esthétique.
  - La l. 1516 se contredit. « Entre 23 sexies et le volet C » dit un ordre ; « en parallèle » dit le contraire.
- **Proposition :**
  1. Écrire que le volet C démarre dès maintenant depuis `main`. La partie d'essai du point 23 sexies a eu lieu, et la boucle comme les réglages sont validés. Le volet C n'attend ni la fusion du point 23 septies ni le point 23 decies.
  2. Écrire que les objectifs 17 à 19 sont tenus par leurs tests automatiques. Le verdict du point 23 decies est consigné. S'il est négatif, il déclenche au plus une pull request de correction dans M1. Au-delà, c'est la condition de révision de l'ADR 0006 qui s'applique, au niveau 2 de M3, sans bloquer la livraison de M1.
  3. Remplacer « s'insèrent entre le point 23 sexies et le volet C » par « suivent le point 23 sexies, indépendamment du volet C ».
- **Gain :** M1 a une fin bornée, et le volet C (rejeu, économie), qui porte les vrais risques du jalon (The Problem, l. 98-103), n'attend pas l'écran.
- **Perte :** M1 pourrait être livré avec un écran que le propriétaire juge encore perfectible. Le niveau 1 l'accepte : il ne demande qu'un client minimal.

### Majeur 2 : la pull request de fonctionnalité du point 23 nonies est trop grosse, et livre en dernier ce qui répond le mieux à la plainte

- **Passages :** l. 1536-1545.
- **Pourquoi c'est un problème :**
  - Une seule pull request regroupe la palette, la disposition par forces, la prochaine étape, l'aide, `MapView` (demi-blocs, zoom, déplacement, survol, clic, mini-carte), quatre panneaux, la disposition 120 × 36, l'écran « agrandir », de nouvelles touches, la suppression de `map_layout.py`, et environ huit fichiers de tests.
  - Le cœur de la plainte (« pas clair, pas d'aide, pas d'explication ») se règle avec la prochaine étape, l'aide et la hiérarchie des panneaux. Ce sont des fonctions pures, peu risquées. La carte rétro est la partie chère et la plus incertaine (rendu selon le terminal, souris, performance).
- **Proposition :** découper en deux pull requests de fonctionnalité, après une seule pull request de scénarios (point 23 octies, inchangé) :
  - **(a)** palette, `guide.py`, `help_pages`, panneaux Prochaine étape, Vaisseau, Marché et Journal, disposition 120 × 36, touche `h`. La carte d'origine reste en place.
  - **(b)** `force_layout.py`, `MapView`, zoom, déplacement et clic, et la suppression de `map_layout.py`.

  Le scénario de la carte reste en attente jusqu'à (b).
- **Gain :**
  - des revues plus courtes et une mutation par pull request plus légère ;
  - le propriétaire peut, s'il le veut, jouer après (a) et dire si la carte est aussi urgente qu'il le pensait ;
  - un problème de rendu de la carte ne retarde pas l'aide.
- **Perte :** un cycle de pull request de plus. Entre (a) et (b), l'écran mêle panneaux rétro et ancienne carte en colonnes.

### Majeur 3 : la « Prochaine étape » réécrit la règle du PNJ, et en diverge

- **Passages :** l. 595-603 (sept règles), à comparer aux l. 523-525 (règles 1 à 3 de `scripted_miner`) ; l. 1545 (« les sept règles ».)
- **Pourquoi c'est un problème :**
  - Les règles 4, 5 et 7 du guide reprennent presque mot pour mot les règles 1, 2 et 3 du PNJ : vendre si l'on est dans le système d'une station avec une soute non vide ; aller à la station qui paie le mieux le minerai le plus abondant ; aller au plus proche gisement du minerai le mieux payé.
  - La règle 6 du guide diverge : elle fait miner le gisement local, quel que soit son minerai, alors que le PNJ vise le minerai le mieux payé. Le jeu aurait donc deux définitions de « la bonne action ».
  - Le contrat d'imports permet déjà à `clients` d'importer `policies` (l. 527).
  - C'est le constat « Reinventing the Wheel » du standard, §4.
- **Proposition :** `next_step` garde ses trois premières règles, qui dépendent de l'état du joueur : alerte, en route, en minage. Pour le reste, il appelle `scripted_miner.decide(observation, frozenset())` sur le vaisseau du joueur et traduit l'ordre rendu en conseil :
  - `Move` donne `d`, avec sauts et ticks ;
  - `Mine` donne `m` ;
  - `Sell` donne `v`, avec le prix d'ici.

  Le « meilleur prix ailleurs » de la règle 4 reste un petit calcul du guide. À défaut, s'il ne faut pas lier le conseil à `policy_version`, ramener les sept règles à quatre : alerte ; en cours, avec la durée ; soute non vide, donc vendre ou aller vendre ; sinon, aller miner.
- **Gain :** une seule règle de décision dans le dépôt, des tests du guide réduits à la traduction et aux trois états, et aucune contradiction possible entre ce que fait le PNJ et ce que conseille l'écran.
- **Perte :**
  - Le conseil hérite de la naïveté du PNJ : il ne pèse pas la durée du trajet.
  - Une future version 3 de la politique changerait le conseil.
  - La liste des gisements vus vides n'est pas tenue par le client. Ce n'est pas grave : le guide ne la connaît pas non plus.

### Majeur 4 : la souris en fait plus que le besoin

- **Passages :** l. 591-593 ; l. 179 (tests « zoom, déplacement, clic et bulle d'information ») ; l. 1149 ; l. 1542 et 1545.
- **Pourquoi c'est un problème :**
  - Le propriétaire a demandé de pouvoir zoomer. L'amendement ajoute trois choses : le déplacement de la vue au bouton gauche, en plus des flèches ; une bulle au survol (`MouseMove`), en plus des étiquettes affichées dès ×2 et de la confirmation de `d`, qui donne déjà sauts, ticks et minutes ; une mini-carte.
  - Avec 8 à 12 systèmes sur environ 72 × 60 pixels de demi-blocs, la carte entière tient à ×1, et la mini-carte n'apporte presque rien.
  - Le zoom continu par pas de 1,25 donne 7 niveaux, avec des étiquettes qui apparaissent à ×2. Trois niveaux suffisent.
  - La règle « le clavier suffit à tout faire » (l. 579) double chaque geste de souris : deux chemins, deux tests.
- **Proposition :** garder la molette avec `z`/`x` sur trois niveaux fixes (×1, ×2, ×3), le clic sur un système qui ouvre la confirmation de déplacement, et les flèches avec `c` pour déplacer la vue. Reporter à M3 le glisser, le survol et la mini-carte (Non-Goals, l. 205). Si les maquettes vues par le propriétaire montraient l'un de ces éléments, le lui demander plutôt que de le supposer.
- **Gain :** plus de gestion de `MouseMove` ni de glisser, plus de rendu de mini-carte, moins de tests du pilote de Textual (qui joue la souris de façon fragile), et une table des touches inchangée.
- **Perte :** une carte un peu moins proche de « l'effet Obsidian ». Le glisser est le plus naturel des trois : s'il est jugé indispensable, c'est lui qu'il faut garder.

### Majeur 5 : la règle de mutation par fichier rendra probablement la pull request rouge sur `frames.py` et `textual_app.py`

- **Passages :**
  - l. 649 (« le score de chaque fichier ne doit pas être inférieur à celui du commit de base ») ;
  - l. 1542-1543 (`MapView` et les panneaux dans `frames.py`, la disposition dans `textual_app.py`) ;
  - `.github/scripts/mutation.py`, l. 146 (un fichier modifié échoue sous son score de base ; un fichier nouveau hors de `core` et `schema` n'a pas de plancher, l. 141-143.)
- **Pourquoi c'est un problème :** le code de dessin (couleurs, décalages de pixels, tirets, halos, interpolation) donne des mutants que les tests du pilote tuent mal. L'ajouter à `frames.py`, qui existe déjà, fera presque sûrement baisser son score. Le plan ne prévoit pas ce cas. Le point 23 ter, l. 1449, l'avait prévu pour un cas voisin.
- **Proposition :** dire dans le Technical Plan, point 7 ter, comment ces mutants sont tués :
  1. Extraire le calcul de la vue dans un module pur, testé sans Textual : passage du carré [0, 1]² aux pixels selon le zoom et le décalage, bornes du zoom, position du vaisseau en cours de saut, système sous un clic.
  2. Mettre `MapView` dans son propre module, ce qui suit déjà le principe « un widget par cadre » (l. 535).
  3. Reprendre la conduite de la l. 1449 : scores avant et après dans la description, décision du propriétaire, aucun test affaibli.

  Le module à part ne doit pas servir à échapper au contrôle : le point 1 suffit à tuer les mutants qui comptent.
- **Gain :** une pull request qui ne bute pas sur un contrôle obligatoire, et un dessin dont la géométrie est vraiment testée.
- **Perte :** un ou deux fichiers de plus.

### Majeur 6 : la vérification automatique de l'objectif 12 ne tient plus avec une carte en pixels

- **Passages :** l. 169 (« au besoin après défilement du cadre Carte : le test lit le contenu du cadre ») ; l. 589 et 591 (gisement = losange coloré, noms seulement à partir de ×2) ; l. 607 (le Marché ne donne que les prix.)
- **Pourquoi c'est un problème :**
  - Le cadre Carte ne défile plus : il se zoome et se déplace.
  - « Où se trouve chaque minerai » n'est plus écrit nulle part en texte à ×1 : c'est un losange de couleur. Le test devrait lire des pixels, ou zoomer à ×2 et déplacer la vue. C'est fragile et coûteux.
- **Proposition :** ajouter au panneau Marché une ligne par minerai : « ore_a : system_3, system_7 ; ore_b : … ». La carte reste purement visuelle, et le test de l'objectif 12 lit les panneaux texte (Prochaine étape, Vaisseau, Marché). Récrire la phrase « défilement du cadre Carte ».
- **Gain :**
  - tests de l'objectif 12 simples ;
  - l'information reste lisible si le terminal rend mal les demi-blocs (risque de la l. 1147) ;
  - les tests de la carte se réduisent à la disposition et à la géométrie.
- **Perte :** deux lignes de panneau ; un peu de redite avec la carte.

---

## Détails

### Détail 1 : palette

- **Passages :** l. 581, l. 1147.
- **Constats :**
  - `ore_b` et l'accent ont la même valeur, `#3FD0E0`. Il n'y a donc que 15 couleurs distinctes, et `ore_b` se confond avec les éléments mis en avant.
  - `noir #000000` n'a pas de rôle dit, et se distingue à peine du fond `#0B0E1A`.
  - « Palette pensée pour rester lisible en 256 couleurs » n'est vérifié par rien.
  - « Chaque couple texte et fond employé » ne dit pas quels couples sont testés.
- **Proposition :**
  - donner à `ore_b` une couleur propre, ou à l'accent ;
  - dire le rôle du noir, ou le retirer ;
  - nommer les couples testés (texte et texte atténué sur fond, panneau et panneau clair) ;
  - retirer l'affirmation sur les 256 couleurs, ou la laisser à la partie d'essai.

  Garder les valeurs hexadécimales dans le document est justifié : les maquettes sont hors du dépôt, et le document est la seule trace du choix du propriétaire. Il faut seulement préciser que ce sont des valeurs initiales, qu'on peut retoucher sans amendement.
- **Gain :** un test bien défini et une couleur de minerai qui ne trompe pas.
- **Perte :** aucune.

### Détail 2 : la disposition par forces descend trop dans le code

- **Passage :** l. 585.
- **Constats :**
  - « 300 itérations », « répulsion en 1/d² », « faible rappel vers le centre », « pas qui décroît » : ce sont des choix d'implémentation (standard, §3). Seul le contrat compte : déterministe, calculé une fois, dans [0, 1]², distance minimale.
  - Un algorithme de forces ne garantit pas, à lui seul, une distance minimale de 0,08. Le document l'affirme (« toujours ») sans dire comment.
- **Proposition :** ne garder que le contrat, et ajouter « au besoin, une passe finale écarte les systèmes trop proches ». Côté réutilisation : `networkx.spring_layout` ferait le calcul, mais ajouterait une dépendance pour une quarantaine de lignes, ce qui ne vaut pas la peine. Pour le tracé en demi-blocs, la bibliothèque `textual-canvas` (un widget de dessin en demi-blocs, avec lignes et cercles) mérite un coup d'œil avant d'écrire un tracé maison. Il faut vérifier qu'elle tourne sous Python 3.15 et qu'elle est maintenue, puis l'épingler dans `uv.lock`. Je ne l'ai pas vérifié ici.
- **Gain :** l'agent de code garde la main sur l'algorithme, et la garantie testée a un mécanisme.
- **Perte :** aucune.

### Détail 3 : une optimisation de rendu sans effet, et une mesure annoncée qui n'existe pas

- **Passages :** l. 614 et l. 1150 (« la carte n'est redessinée que si … l'observation change » ; « temps de rendu mesuré au plan détaillé, point 28 bis ») ; l. 1607-1612 (le point 28 bis, sans ajout de l'amendement 2.)
- **Constats :**
  - L'observation change à chaque tick, et le vaisseau avance le long du lien pendant un saut. La carte est donc redessinée à chaque tick : la condition n'économise rien.
  - Le point 28 bis ne contient aucune mesure de rendu.
- **Proposition :** retirer la phrase d'optimisation. Soit ajouter une ligne explicite au point 28 bis, soit ne mesurer le rendu que si la partie d'essai montre que l'écran saccade, ce qui est plus simple. La parade existante, « l'écran ne redessine que la dernière mise à jour », suffit.
- **Gain :** plus de renvoi qui ne mène nulle part, plus d'optimisation prématurée.
- **Perte :** aucune.

### Détail 4 : l'aide sur deux pages ; « premier lancement » contre « chaque partie »

- **Passages :** l. 610 ; l. 94 et ADR, l. 17 (« aide au premier lancement ».)
- **Constats :**
  - La page 2, « toutes les touches », répète la barre des touches. Elle impose aussi une pagination aux flèches et ses tests.
  - Le Technical Plan dit « s'ouvre au lancement de chaque partie ». L'Overview et l'ADR disent « au premier lancement », ce qui demanderait de garder une trace d'un lancement à l'autre (un fichier, par exemple).
- **Proposition :**
  - une seule page qui défile (gestes, portée, rythme, premier objectif, puis la liste des touches en bas) ;
  - écrire partout « au lancement de chaque partie », qui ne demande aucune persistance.

  Les widgets `Footer` et `HelpPanel` de Textual afficheraient les touches tout seuls, mais il faudrait passer de `on_key` aux `BINDINGS` (voir `src/fourx/clients/textual_app.py`, l. 146). Ce refactor ne se justifie pas maintenant.
- **Gain :** moins de navigation et de tests, et une formulation cohérente.
- **Perte :** une aide un peu plus longue à faire défiler.

### Détail 5 : taille d'écran

- **Passages :** l. 583, l. 1148.
- **Constat :** viser 120 × 36 et afficher « agrandir la fenêtre » en dessous de 100 × 30 coûte peu, et protège la partie d'essai.
- **Proposition :** garder tel quel. Noter seulement que les tests du pilote passent de 80 × 24 (l. 1507) à 120 × 36.

### Détail 6 : ornements des panneaux

- **Passages :** l. 606-608 (barres de progression en demi-blocs, ★, étiquettes de couleur dans le journal.)
- **Constat :** ils coûtent peu et servent l'esthétique demandée.
- **Proposition :** les garder, mais les désigner comme les premiers à couper si la pull request (a) du Majeur 2 s'allonge.

### Détail 7 : l'option (a) de l'ADR est mal justifiée

- **Passages :** ADR, l. 10 ; alternative AB, l. 1074.
- **Constat :** « Un terminal en caractères seuls ne donne ni graphe disposé par forces lisible, ni zoom » est inexact : on peut disposer un graphe par forces et le zoomer en caractères (cadres, braille). Les vraies différences sont la couleur, que l'amendement 1 avait exclue (« sans thème de couleur », l. 79), et la finesse de deux pixels par case.
- **Proposition :** récrire l'inconvénient de (a) ainsi : « sans couleur ni pixels, le graphe reste pauvre et l'information se hiérarchise mal ; et c'est le choix "sans thème de couleur" de l'amendement 1 que le propriétaire remet en cause ».

  Remarque mineure : seize couleurs, c'est plutôt une palette « 4 bits » que « 8 bits ». Le propriétaire a employé les deux mots ; ce n'est pas à corriger, seulement à ne pas prendre au pied de la lettre.
- **Gain :** une ADR qui ne pourra pas être contestée sur un argument faux.
- **Perte :** aucune.

### Détail 8 : la pull request de scénarios du point 23 octies

- **Passages :** l. 1528-1534 ; l. 651 (une pull request qui touche des définitions d'étapes déclenche la mutation de tout `core`.)
- **Constat :** cette pull request est inévitable : le scénario protégé de la carte utilise `map_layout`, qui disparaît. La mutation de tout `core` qu'elle déclenche est un coût fixe, pour un changement qui ne touche que le client.
- **Proposition :** la garder, mais en un seul passage, qui couvre aussi les deux pull requests de fonctionnalité du Majeur 2. Les deux scénarios nouveaux (prochaine étape au long d'un cycle, durées de l'aide) pourraient être de simples tests de `tests/clients/`. Le gain serait faible, puisque la mutation de `core` a lieu de toute façon : à laisser au choix du propriétaire.

### Détail 9 : « client Textual minimal » au niveau 1, §11

- **Passage :** niveau 1, l. 498.
- **Constat :** l'amendement modifie l'Overview du niveau 1 (l. 16), mais pas §11, qui garde « client Textual minimal ». Cette cohérence est voulue si l'on retient le Majeur 1 : le critère de sortie ne change pas, et l'écran rétro n'en fait pas partie.
- **Proposition :** l'écrire explicitement dans les conséquences de l'ADR (« le critère de sortie de M1, au niveau 1, §11, ne change pas »).

---

## Ce qu'il faut garder tel quel

- Textual dans le terminal, plutôt qu'un client natif ou un navigateur : c'est la solution la plus simple qui réponde au besoin, et elle a une condition de révision bornée à M3.
- Une disposition calculée une fois, sans animation physique.
- Aucun changement du protocole, de l'observation ou des règles.
- Une seule palette, et le tutoriel complet à M3.
- Le clic sur un système qui ouvre la même confirmation que `d` : il réutilise le chemin existant.
- La position du vaisseau interpolée pendant un saut : un petit calcul, qui sert directement l'objectif 12.

## Le découpage en pull requests est-il proportionné ?

- La pull request protégée (23 septies) et celle de scénarios (23 octies) sont proportionnées.
- La pull request de fonctionnalité (23 nonies) ne l'est pas : la découper en deux (Majeur 2).
- La partie d'essai (23 decies) est utile, mais son verdict ne doit pas pouvoir bloquer M1 indéfiniment (Majeur 1).

## L'amendement retarde-t-il trop le volet C ?

Le texte dit « en parallèle », mais le place aussi « entre le point 23 sexies et le volet C ». En pratique, le vrai goulot est le temps de revue du propriétaire, et la règle « une pull request de chaque type à la fois » fait alterner les deux volets.

Si l'on applique le Majeur 1 (volet C lancé tout de suite, verdict sur l'écran qui ne bloque pas), le retard sur le volet C devient quasi nul. Si l'on ne l'applique pas, M1 dépend de l'écran sans que le niveau 1 l'exige.

## Y a-t-il une solution plus simple au même problème ?

Pour la plainte de fond, oui : la Prochaine étape, l'aide et une hiérarchie des panneaux en couleurs règlent « pas clair, pas d'aide, pas d'explication » sans carte en pixels. C'est la pull request (a) du Majeur 2, à livrer en premier.

La carte disposée par forces et zoomable est une demande explicite du propriétaire, qui a vu et approuvé des maquettes. Elle ne doit pas être retirée, seulement allégée (Majeur 4) et livrée séparément.
