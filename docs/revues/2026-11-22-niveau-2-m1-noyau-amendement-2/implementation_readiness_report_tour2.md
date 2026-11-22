# Étape 6, tour 2 — Préparation à l'implémentation (amendement 2)

**Cible :** les passages « amendement 2 » de `docs/designs/niveau-2-m1-noyau.md` :
- Technical Plan, point 7 ter (l. 580-672) et point 13 (l. 940-954) ;
- objectifs 12 et 17 à 19 (l. 169, 178-183) ;
- volet B ter, points 23 septies à 23 undecies (l. 1599-1649) ;
- point 28 bis (l. 1713) et Verification Plan (l. 1817-1824).

Pièce liée : `docs/adr/0006-client-retro-8-bits.md`.

**Mode :** REVIEW, sans contexte, lecture seule. J'ai lu la cible, l'ADR, le rapport du tour 1 et la synthèse, puis le code demandé (liste en fin de rapport). Aucun fichier n'a été modifié.

## Verdict

**Presque prêt : 0 bloquant, 5 majeurs, 12 détails.**

Les 3 bloquants et les 12 majeurs du tour 1 sont corrigés. Deux le sont en partie (M3/M4 et D4 ; voir le tableau).

**Peut-on implémenter à partir du texte seul ?**
- **23 nonies :** oui pour l'essentiel. Restent deux trous qui demandent une décision : les lignes des touches dans l'aide (MA3) et la condition « au plus » de la règle 4, que l'observation ne permet pas de calculer (MA2).
- **23 decies :** oui pour la disposition et la vue. Restent le coût et la portée des tests de la disposition (MA4), et le comportement de `z`, `x` et `c` dans une saisie, qui casse des tests existants (MA5).
- **23 octies :** la suite de touches attendue est **juste** : je l'ai vérifiée contre `ClientModel` et `scripted_miner`. Mais le scénario ne peut pas s'écrire sans décisions : le monde, l'ordre des gestes dans un tick, la condition d'arrêt et la façon d'obtenir l'ordre conseillé (MA1).

---

## 1. Suivi des constats du tour 1 (bloquants et majeurs)

| Constat du tour 1 | État | Où |
| :-- | :-- | :-- |
| B1 graine dans la barre | Corrigé | l. 582 (« la graine et le dossier de la partie restent hors de l'écran de jeu ») ; l. 598, la barre n'a plus de graine |
| B2 rappel de la taxe | Corrigé | l. 663 : « moins une taxe », sans taux ; plus aucun rappel du taux |
| B3 disposition par forces | Corrigé | l. 610-614 : constantes, départ en couches, 300 itérations, normalisation, séparation bornée à 50 passes. Cas dégénérés en détail D1 |
| M1 sorties de `Step` | Corrigé | l. 633-649 : titres, détails, touches en noms Textual ; `Step` gelé dans `guide.py` (l. 946) ; suite du scénario donnée (l. 1620). Conditions du scénario : voir MA1 |
| M2 cas limites de `next_step` | Corrigé, un reste | Règles 0 et 2, décision de `scripted_miner` (départages et repli), « fin du minage », signature `next_step(model)`. Reste : la règle 4 n'est pas observable (MA2), et l'observation sans vaisseau (D4) |
| M3 contenu de l'aide | En partie | Lignes 1 à 8 et 10 fixées ; `capacity` du vaisseau ; `Observation \| None` ; assertion du scénario. La ligne 9 (les touches) n'est pas fixée (MA3) |
| M4 score de `texts.py` | En partie | « comparés en entier » (l. 183, l. 1634). Impossible pour la ligne 9 tant que son texte n'est pas fixé (MA3) |
| M5 logique de carte dans `frames.py` | Corrigé | `clients/map_view.py`, signatures l. 941-945 |
| M6 vérification de l'objectif 12 | Corrigé | l. 169 : les cadres de texte, et la carte par ses propres tests |
| M7 historique typé | Corrigé, un reste | `HistoryEntry` (l. 656, l. 949-950) ; `model.py` et son test dans 23 nonies ; étape adaptée dans 23 octies (l. 1622). Reste : l. 936 non marquée (D10) |
| M8 disposition des cadres | Corrigé, un reste | Tableau l. 596-606. Restent des hauteurs incohérentes (D7) |
| M9 clic | Corrigé | l. 630 |
| M10 touches de l'aide | Corrigé, un reste | l. 670 : widget superposé, priorité sur les alertes, ↑ ↓, `q`, tests qui ferment l'aide. Reste D9 |
| M11 zoom, vue, étiquettes | Corrigé, un reste | l. 619-628 : `ZOOMS`, point d'ancrage, pas d'un dixième, projection uniforme, étiquettes coupées ; mini-carte retirée (E2). Restent des conventions de dessin (D2) |
| M12 point 28 bis et Verification Plan | Corrigé | l. 1713 ; l. 1811, l. 1813 marquées ; bloc l. 1817-1824 |
| D4 (tour 1) propriétés sous mutmut | Non traité | MA4 |

---

## 2. Majeurs

### MA1. Le scénario du cycle (23 octies) : la suite attendue est juste, mais quatre choix restent au rédacteur

**Passage :** l. 1620, et liste des fichiers l. 1622.

**Ce qui est vérifié et tient.** Avec un seul geste par tick, fait après le relevé, voici le déroulé contre le code réel :

| Moment | Règle | Touches | Preuve |
| :-- | :-- | :-- | :-- |
| départ | 5, `Move` (règle 3 du PNJ) | `("d",)` | |
| ordre envoyé | 2 | `()` | `pending`, `src/fourx/clients/model.py:63-66, 179` |
| en route | 3 | `()`, confondu avec le précédent | |
| `Arrived`, route vide | 1 | `("enter",)` | `model.py:202-207` |
| acquitté | 5, `Mine` | `("m",)` | `src/fourx/policies/scripted_miner.py:92-96` |
| ordre envoyé, puis minage | 2, puis 4 | `()` | |
| `MiningEnded` sans `causation_id` | 1 | `("enter",)` | `model.py:208-216` |
| acquitté | 5, `Move`, cargaison pleine | `("d",)` | `scripted_miner.py:80-88` |
| ordre envoyé, en route | 2, 3 | `()` | |
| arrivée | 1 | `("enter",)` | |
| acquitté | 5, `Sell` | `("v",)` | `scripted_miner.py:78-79` |

**Problèmes :**
1. **Le monde n'est pas constructible tel qu'écrit, et les conditions ne garantissent pas la suite.**
   - `Game` ne prend qu'une graine (`tests/scenarios/steps/steps_partie.py:288`). Un « monde fixé par les étapes » doit donc passer par « sur la première graine dont… ». Le texte de la condition est contrôlé par `monde_convient` (`steps_partie.py:233-258`, qui fait `assert condition == …` sur toute condition inconnue).
   - Or `steps_partie.py` n'est pas dans la liste de 23 octies (l. 1622).
   - Les conditions données (« un gisement à un saut ; une station à un saut du gisement ») ne portent pas sur ce qui compte. La suite n'est juste que si :
     - (a) le système de départ (celui de la station 1) n'a pas de gisement ;
     - (b) le gisement que `decide` vise depuis la station 1 n'est pas dans le système d'une station. S'il l'est, après la fin du minage, la règle 1 du PNJ vend sur place : on a `("enter",)` puis `("v",)`, sans `("d",)` (`scripted_miner.py:76-79`).
   - La distance « un saut » est sans effet, puisqu'un saut intermédiaire ne lève pas d'alerte.
2. **L'ordre des gestes dans un tick n'est pas dit.** Si le scénario acquitte puis envoie l'ordre conseillé dans le même tick sans refaire de relevé, `("m",)` n'est jamais relevé (la suite devient `("enter",), ()`).
3. **Aucune condition d'arrêt.** Après `("v",)`, la vente part, la cargaison se vide, et `decide` renvoie un `Move` : `("d",)` s'ajoute, et l'égalité « exactement » échoue. Le relevé ne doit pas non plus commencer avant la première observation : la règle 0 donnerait `()` en tête.
4. **« L'ordre conseillé » n'est pas lisible dans `Step`.** `Step(title, detail, keys)` (l. 946) ne porte pas la commande. Le rédacteur devra soit relire le titre (« Aller miner ore_b à system_3 »), soit rappeler `scripted_miner.decide` lui-même.

**Proposition :** écrire, dans 23 octies :
- **Étant donné :** « sur la première graine dont le système de la station 1 n'a pas de gisement, et dont le gisement visé par `scripted_miner` depuis la station 1 n'est pas dans le système d'une station ». Ajouter `tests/scenarios/steps/steps_partie.py` (Modify, `monde_convient`) à la liste, ou dire que l'étape vit dans `steps_ecrans.py`.
- **Procédure, à chaque tick après le premier :**
  1. relever `next_step(model).keys` ;
  2. faire un seul geste : `("enter",)` → `acknowledge()` ; `("d",)` ou `("m",)` → la commande de `scripted_miner.decide(model.observation, model.seen_empty)` envoyée par `model.send` ; `("v",)` → `model.sell_all()` ;
  3. jouer un tick.
- **Arrêt :** juste après le relevé de `("v",)`.
- « Valeurs successives distinctes » veut dire : les répétitions consécutives sont fondues.

### MA2. Règle 4 : « si un autre vaisseau visible mine le même gisement » ne se lit pas dans l'observation

**Passage :** l. 641.

**Problème :**
- `OtherShipView` n'a que `id`, `owner_id`, `system_id` et `capacity`, sans activité (`src/fourx/schema/observation.py:51-55`).
- `MiningStarted` est `PRIVATE` (`src/fourx/schema/events.py:89`) : le client ne voit jamais qu'un autre vaisseau mine.
- `test_guide.py` (« chaque règle », l. 1634) ne peut donc pas construire le cas, et le développeur doit inventer un critère.

**Proposition :** remplacer par « si un autre vaisseau visible est dans le même système » (`other_ships`, même `system_id`), ou supprimer la variante « au plus ». Le point 7 bis dit déjà que la durée est une borne haute dans ce cas (l. 575).

### MA3. Aide, ligne 9 : le texte des touches n'est pas fixé, alors que l'aide est « comparée en entier »

**Passages :** l. 667, et l. 183 et 1634 (« comparée ligne par ligne »).

**Problème :**
- « une ligne par touche du tableau du point 7 bis et des touches ajoutées » ne donne ni le gabarit (« d : déplacer… » ? le libellé complet du tableau ?), ni l'ordre, ni le sort des touches du mode développement.
- `help_pages(observation)` (l. 948) ne reçoit aucun indicateur de mode développement : faut-il toujours lister `p`, `a`/`r` et Espace, ou jamais ?
- `texts.py` a déjà un score de base, que la pull request ne doit pas faire baisser (`.github/scripts/mutation.py:146-147` ; l. 1822). Le texte doit donc être figé dans le document pour que le test le compare.
- La numérotation « 1 à 10 » devient fausse, puisque la ligne 9 s'étend sur plusieurs lignes.

**Proposition :**
- donner les lignes mot pour mot, par exemple « d : déplacer (liste des destinations, Entrée confirme, Échap annule) », dans l'ordre `d m v h z x c ← → ↑ ↓ Entrée Échap q`, puis « En mode développement : p pause, a / r vitesse, Espace avancer jusqu'à la prochaine alerte » ;
- décider si la ligne du mode développement est toujours présente. Sinon, ajouter un paramètre `dev: bool` à `help_pages` (l. 948).

### MA4. Tests de la disposition : 2 000 graines exécutées sous mutmut, et une phase des forces que rien ne contraint

**Passages :** l. 616, l. 1644 ; Verification Plan l. 1822.

**Problème :**
- La marque `proprietes` n'est pas exclue de mutmut (`setup.cfg:8-12`, où ne sont exclus que `rejeu`, `lent` et `mesure`). Le test des graines 1 à 2 000 sera rejoué pour chaque mutant de `force_layout.py` qu'il couvre.
- Les propriétés vérifiées (placé une fois, dans le carré, distance d'au moins 0,08, même résultat à chaque appel) sont **garanties par les étapes 3 et 4** (normalisation et séparation), quelles que soient les constantes des étapes 1 et 2. Les mutants des constantes 0,5, 0,01, 0,05, 0,1, 300 et du ressort `(d − 1)` survivent donc tous.
- Chaque survivant rejoue tout le test : 2 000 générations plus 300 itérations sur 8 à 12 systèmes, de l'ordre d'une à quelques minutes par mutant selon mon estimation.
- Le score de `force_layout.py`, sans plancher, ne fait pas échouer le contrôle. Mais la durée risque de dépasser le seuil de 30 minutes du point 28 bis (l. 1709), et la mutation ne prouve rien sur la phase des forces.
- La mise en `SystemView` n'est pas dite. L'usage du dépôt est `observe(generate(graine, reglages), 1, reglages)` (`tests/clients/test_map_layout.py:136`).

**Proposition :**
- exposer les quatre étapes comme fonctions de module (départ, itération, normalisation, séparation), avec des tests unitaires sur de petits graphes (2 ou 3 systèmes) aux résultats calculables à la main : le départ en couches exact, une itération entre deux points, la boîte normalisée [0,05 ; 0,95], la séparation d'une paire confondue sur l'axe horizontal. Les comparaisons se font avec `pytest.approx`, ce qui est sûr en IEEE 754 sur une même version de Python ;
- marquer le test des 2 000 graines `proprietes` **et** `lent`. Il reste exécuté par la tâche `proprietes` (`.github/workflows/ci.yml:215`), mais sort de mutmut, sans toucher `setup.cfg`, qui est protégé. Le coût : il tourne aussi dans la tâche `rejeu` (`ci.yml:194`). Autre voie : ramener la boucle de `test_force_layout.py` à 150 graines, comme `test_map_layout.py:135`, et garder les 2 000 hors de mutmut ;
- écrire la conversion par `observe`.

### MA5. `z`, `x` et `c` : comportement non dit dans une saisie et aux bornes, alors que cinq tests existants utilisent `x` comme touche sans effet

**Passages :** l. 619 et l. 672 (seules les flèches sont réservées à « aucune saisie ouverte ») ; l. 1642-1644.

**Problème :**
- `tests/clients/test_textual_app.py` emploie `x` comme touche sans effet :
  - aux l. 162, 174, 186 et 228, dans une saisie ;
  - à la l. 317, hors saisie, où il attend `AIDE_DEV`.
- À partir de 23 decies, `x` est « zoom arrière ». Le texte ne dit pas :
  - si `z`, `x` et `c` agissent pendant la liste des destinations, la confirmation, le choix du minerai ou la confirmation de quitter ;
  - si `x` au zoom 1, ou `z` au zoom 4, est « sans effet » (avec la ligne d'aide) ou silencieux.
- Le test de la l. 317 casse quel que soit le choix, et le développeur doit décider du comportement visible.

**Proposition :**
- « `z`, `x` et `c` n'agissent que quand aucune saisie n'est ouverte ; dans une saisie, ils sont sans effet (ligne d'aide de la saisie) ; aux bornes de `ZOOMS`, sans effet, avec la ligne d'aide » ;
- dire que 23 decies remplace, dans ces tests, la touche sans effet par une touche libre (par exemple `y`).

---

## 3. Détails

- **D1. Cas dégénérés de `force_layout`** (l. 611-614).
  - Un système absent de `distances` (graphe non connexe, comme dans les observations fabriquées de `tests/clients/test_textual_app.py:515-525`) n'a pas de couche.
  - Deux points confondus n'ont pas de direction de répulsion (seule la norme est bornée à 0,01).
  - Une boîte de largeur et de hauteur nulles (un seul système) divise par zéro.
  - La séparation « tant que… au plus 50 fois » ne dit pas quoi faire si la 50ᵉ passe laisse une paire sous 0,08, ni si l'écart d'une paire est appliqué tout de suite (passe séquentielle) ou en fin de passe.
  - *Proposition :* les systèmes inaccessibles forment une dernière couche ; direction (1, 0) si d = 0 ; échelle 1 si la boîte est nulle ; passe séquentielle ; au-delà de 50 passes, positions rendues telles quelles (le test de propriétés tranche).
- **D2. Conventions de la grille** (l. 620-628, l. 942, l. 945).
  - `Cell.fg` et `Cell.bg` : nom de rôle de `PALETTE` ou valeur `#RRGGBB` ? Les tests de `map_view` en dépendent.
  - Codage des demi-blocs : `▀` avec avant-plan = pixel du haut et fond = pixel du bas.
  - Format de la pastille pour un numéro à un chiffre (« 5 » suivi d'une espace ? précédé d'une espace ? « 05 » ?) et case d'ancrage.
  - La route est-elle une droite ou suit-elle les liens de `route` ?
  - Effet de `hovered` sur la grille : aucun n'est décrit.
  - Place de `◆a` par rapport aux étiquettes à partir du zoom 2, et le `▲` du joueur « sur » la pastille : recouvre-t-il le numéro ?
  - Unité de `pan(dx, dy)` (cases ?) et sens du glisser.
  - Axe y vers le bas ou vers le haut.
- **D3. Règle 5, traductions** (l. 645-648).
  - « [s] sauts » donne « 1 sauts » : écrire `sauts(s)` (`src/fourx/clients/texts.py:43-44`).
  - [durée] vaut `duration_text(s × jump_ticks)` : à écrire.
  - [station′] en cas d'égalité de prix : la plus proche, puis le plus petit identifiant ?
  - `Sell(ore)` ne nomme qu'un minerai, alors que `v` vend toute la cargaison.
- **D4. Observation sans vaisseau, plusieurs ordres envoyés** (l. 637-639).
  - La règle 0 ne couvre pas une observation sans `own_ships`, qui sert dans les tests (`test_textual_app.py:441`) et pour laquelle `model.vaisseau()` rend `None` (`model.py:77-81`).
  - Règle 2 avec plusieurs ordres en attente : lequel nommer ? *Proposition :* tous, joints par « ; », comme le cadre Vaisseau (`src/fourx/clients/frames.py:66-67`).
- **D5. Règle 1 : texte de l'alerte** (l. 638). Avec ou sans le tick (« t840 … »), et avec ou sans « (1 de plus) » comme aujourd'hui (`frames.py:89-96`) ?
- **D6. Texte de `HistoryEntry`** (l. 656). `text` contient-il encore le préfixe « t803 » ? La l. 936 donne les chaînes avec ce préfixe, et le tick a désormais son propre champ. Le format d'affichage du cadre Historique (`test_textual_app.py:288-291`) en dépend.
- **D7. Hauteurs de la disposition** (l. 600-608).
  - L'historique occupe les lignes 31 à 35, soit 5 lignes. Avec une bordure, comme les cadres actuels (`src/fourx/clients/textual_app.py:45-57`), il ne reste que 3 lignes pour « les quatre dernières entrées ».
  - En 100 × 30, la colonne de droite (7 + 8 + 13 = 28 lignes) ne tient pas dans les 22 lignes laissées par la barre d'état, l'historique et la barre des touches.
  - *Proposition :* dire si les places incluent la bordure ; Stations en hauteur `1fr`.
- **D8. Plafond de 10 rafraîchissements par seconde** (l. 631). Ne vaut-il que pour `MapCanvas` ? S'il vaut pour tout l'écran, les tests du pilote qui lisent un cadre juste après `pilot.pause()` (`test_textual_app.py:203-205, 286-288`) liraient un affichage périmé. *Proposition :* « la carte seulement ; les autres cadres sont redessinés à chaque mise à jour ».
- **D9. Aide et autres saisies** (l. 670). `q` pendant l'aide : l'aide se ferme-t-elle, et Échap y revient-il ? `h` pendant la liste des destinations : la saisie en cours est-elle remplacée ?
- **D10. Point 13, l. 936.** `history: tuple[str, ...]` reste sans marque de remplacement, alors que la l. 950 le remplace. Ajouter « *(remplacé par l'amendement 2)* ».
- **D11. Textes laissés libres dans `frames.py`** (non muté).
  - Contenu de la barre des touches `#touches` dans chaque saisie (l. 604) ; la constante `AIDE` (`textual_app.py:37`) doit-elle citer `h`, `z`, `x`, `c` ?
  - Affichage des noms de touches de `Step` (`"enter"` → « Entrée »).
  - Format de la ligne de station avec ★ (le test actuel attend « S1 sys 1  a 10  b 15 », `test_textual_app.py:415`).
  - 100 % de la barre du trajet : le saut en cours ou toute la route ? Le client ne connaît pas la longueur initiale de la route.
  - Place de la bulle, que je recommande hors du pointeur : sinon elle capte les `MouseMove`.
- **D12. Scénarios et tests de la souris.**
  - Le pilote de Textual 8.2.8 n'a ni défilement de molette ni glisser : `hover` envoie `MouseMove` avec `button=0` (`.venv/lib/python3.15/site-packages/textual/pilot.py:349-379`). Les tests « zoom » et « déplacement » (l. 1644) doivent poster eux-mêmes `MouseScrollUp`/`Down` et des `MouseMove` avec `button=1`. Seuls `click` et `hover` sont fournis.
  - Les `Étant donné` des scénarios de la disposition et de l'aide (l. 1619, l. 1621) ne sont pas nommés. Je suppose « réglages de test à 12 systèmes, graine 1 » et « réglages de test, graine 1 ».
  - Les deux scénarios de refus (`tests/scenarios/ecrans.feature:10-28`) échoueront sur le code de l'amendement 1 dès que l'étape lira `.text`. La règle de la l. 1623 les couvre, mais les nommer éviterait un oubli.

---

## 4. Points vérifiés qui tiennent

- **Contrats d'imports :** `guide.py` → `policies.scripted_miner`, `map_view.py` et `force_layout.py` → `policies.geometry`, `model.py` → `policies.scripted_miner.mettre_a_jour` sont permis (`.importlinter:48-56`), sans cycle (`scripted_miner.py:23-27`).
- **`seen_empty` :** `mettre_a_jour` est idempotente sur une même observation (`scripted_miner.py:33-48`). Le double appel, par `ClientModel` puis par `decide` dans `next_step`, ne change rien.
- **Signatures du point 13 :** `force_layout(tuple[SystemView, ...])` correspond à `Observation.systems` (`observation.py:68`). `help_pages(Observation | None)` couvre l'aide ouverte avant le premier tick (`textual_app.py:89-91`).
- **Mutation :**
  - `palette.py` n'a pas de fonction, donc aucun mutant, ce qui est accepté (`mutation.py:92-97`) ;
  - `guide.py`, `force_layout.py` et `map_view.py` sont neufs, sans base, donc sans plancher (`mutation.py:141-149`) ;
  - `model.py` et `texts.py` ne doivent pas baisser (l. 1822) ;
  - la suppression de `map_layout.py` n'est pas un échec (`mutation.py:185-189`) ;
  - `frames.py` et `textual_app.py` restent exclus (`setup.cfg:17-20`).
- **Palette :** seize valeurs distinctes. Mes calculs confirment le plus faible des couples : `alerte` sur `cadre`, environ 5,07 pour 1. `texte_attenue` sur `cadre_clair` fait environ 5,3, et `fond` sur `station` environ 7,2.
- **Scénarios avant le code :** les étapes importent le code dans les fonctions (`tests/scenarios/steps/steps_partie.py:51-53`) ; `en_attente.txt` exige des titres exacts (`tests/scenarios/conftest.py:57-60`), et les trois titres sont donnés (l. 1619-1621).
- **Aide ouverte au lancement :** « les tests du pilote ferment l'aide avant d'agir » (l. 670) suffit pour `piloter` (`test_textual_app.py:103-116`). Le passage en 120 × 36 est nécessaire : avec `TAILLE = (80, 24)` (`test_textual_app.py:44`), le client n'afficherait que le message de petite fenêtre.
- **Versions :** Textual 8.2.8 et Rich 15.0.0 (`uv.lock:941-942, 1041-1042`), aucune dépendance nouvelle.

## 5. Fichiers lus

- **Document, ADR et revues :** `docs/designs/niveau-2-m1-noyau.md`, `docs/adr/0006-client-retro-8-bits.md`, `docs/revues/2026-11-22-niveau-2-m1-noyau-amendement-2/implementation_readiness_report.md`, `goldfish_review_report.md`.
- **Client :** `src/fourx/clients/model.py`, `texts.py`, `frames.py`, `textual_app.py` (`map_layout.py` par ses tests).
- **Politiques :** `src/fourx/policies/scripted_miner.py`.
- **Formats :** `src/fourx/schema/observation.py`, `src/fourx/schema/events.py`.
- **Scénarios :** `tests/scenarios/ecrans.feature`, `tests/scenarios/steps/steps_ecrans.py`, `tests/scenarios/steps/steps_partie.py`, `tests/scenarios/conftest.py`.
- **Tests :** `tests/clients/test_textual_app.py`, `tests/clients/test_map_layout.py`, `tests/proprietes/test_proprietes.py`.
- **Configuration et outillage :** `setup.cfg`, `pytest.ini`, `.importlinter`, `.github/chemins-proteges.txt`, `.github/scripts/mutation.py`, `.github/workflows/ci.yml`, `uv.lock`, `textual/pilot.py` (environnement virtuel).

`geometry.py` et `cargo.py` : je ne les ai pas lus directement. Je me suis fié à leur usage dans `scripted_miner.py`, `texts.py` et `model.py`, et aux signatures du point 13 (l. 921-922).
