# Étape 6, tour 3 — Préparation à l'implémentation (amendement 2)

**Cible :** les passages « amendement 2 » de `docs/designs/niveau-2-m1-noyau.md` :
- Technical Plan, point 7 ter (l. 586-692) et point 13 (l. 944, 957-976) ;
- objectifs 12 et 17 à 19 (l. 170, 179-184) ;
- volet B ter, points 23 septies à 23 undecies (l. 1631-1685) ;
- point 28 bis (l. 1749) et Verification Plan (l. 1853-1861).

Pièce liée : `docs/adr/0006-client-retro-8-bits.md`.

**Mode :** REVIEW, sans contexte, lecture seule. J'ai lu la cible, l'ADR, le rapport du tour 2 et la synthèse (décisions E1 à E5, que je ne rediscute pas), puis le code demandé. Aucun fichier n'a été modifié.

## Verdict

**Prêt sous une réserve : 0 bloquant, 1 majeur, 11 détails.**

Les cinq majeurs du tour 2 sont corrigés. Il en reste un, nouveau : il vient du passage de la règle du PNJ à celle du gain par tick (E5). La condition de graine du scénario du cycle ne peut pas être calculée là où le texte la place.

**Peut-on implémenter à partir du texte seul ?**
- **23 nonies : oui.** Les règles 5 et 6 se calculent avec ce que l'observation et `ClientModel` donnent déjà (détail plus bas). Les formules sont en entiers et le dénominateur n'est jamais nul. Les départages sont complets. Restent des points de texte (D1, D2, D3).
- **23 decies : oui.** La disposition, la vue et la grille sont précisées. Les détails restants portent sur la façon d'écrire les tests (D5 à D8).
- **23 octies : la suite de touches attendue est juste avec la règle du gain par tick** (je l'ai vérifiée ci-dessous). Mais la condition de graine demande une décision de conception (MA1).

---

## 1. Suivi des majeurs du tour 2

| Constat du tour 2 | État | Où |
| :-- | :-- | :-- |
| MA1 scénario du cycle : monde, ordre des gestes, arrêt, commande | Corrigé, un reste | Condition de graine, procédure à un seul geste par tick, arrêt après `("v",)`, répétitions fondues : l. 1654-1656. `Step.command` : l. 643, 968. `steps_partie.py` ajouté : l. 1658. **Reste :** la condition n'est pas calculable dans `monde_convient` (MA1 ci-dessous) |
| MA2 règle 4 non observable | Corrigé | l. 652 : « un autre vaisseau visible est dans le même système ». `OtherShipView.system_id` existe (`src/fourx/schema/observation.py:51-55`) |
| MA3 lignes des touches de l'aide | Corrigé | l. 676-688 : les lignes mot pour mot, dans l'ordre ; ligne du mode développement si `dev` ; `help_pages(observation, dev)` l. 971 ; test « avec et sans mode développement » l. 1670 |
| MA4 disposition sous mutmut | Corrigé | Les quatre étapes sont exposées et testées sur de petits graphes avec `pytest.approx` (l. 620-624, 962, 1680). 50 graines sous `proprietes`, 2 000 sous `proprietes` et `lent` (l. 626). `lent` est bien exclu de mutmut (`setup.cfg:9-10`). Conversion par `observe` (l. 626). Petite incohérence de marques : voir D9 |
| MA5 `z`, `x`, `c` dans une saisie et aux bornes | Corrigé | l. 629, 631, 692 ; `x` devient `y` (l. 1680). Seul l'appui de `test_textual_app.py:317` (hors saisie) changeait vraiment de sens. Ceux des l. 162, 174, 186 et 228 restent sans effet, et le remplacement ne gêne pas |

Les détails du tour 2 sont presque tous traités : D1 (cas dégénérés), D2 (conventions de la grille), D3 (`sauts`, `duration_text`, vente par `sell_all`), D4 (règle 0 bis, ordres joints par « ; »), D5, D6, D8, D9 et D10. D7 est en partie traité : voir D10 ci-dessous.

---

## 2. Vérification des règles 5 et 6 contre le code

| Donnée lue | Source réelle |
| :-- | :-- |
| cargaison, capacité, système, activité | `OwnShipView.cargo`, `capacity`, `system_id`, `activity` (`observation.py:38-48`) ; `Activity.IDLE / EN_ROUTE / MINING` (`schema/actors.py:15-18`) |
| prix | `StationView.ore_prices`, indice = identifiant de minerai − 1 (comme `scripted_miner.py:55-57`) |
| sauts | `policies.geometry.distances(systems, start)`, depuis le vaisseau et depuis le système de g |
| `jump_ticks`, `mining_rate` | `Observation.public_tunables` (`observation.py:58-62`) |
| stock visible | `DepositView.stock: Int64 \| None` |
| gisements vus vides | `scripted_miner.mettre_a_jour` existe, avec la signature du point 13 (`scripted_miner.py:33`) ; `seen_empty` s'ajoute à `ClientModel` (l. 958, 1667) |
| libellés | `station`, `systeme`, `minerai`, `sauts`, `duration_text` existent (`src/fourx/clients/texts.py:30-64`) |
| commande | `Move(ship_id, target_system_id)` et `Mine(ship_id, ore_id)` ; `Command = Move \| Mine \| Sell \| CreateCharacter` (`schema/orders.py:40-60`) |

- **Dénominateurs :** dans la règle 6, le vaisseau est à l'arrêt sans cargaison pleine, donc la capacité libre est positive. Le stock retenu est positif ou inconnu, puisque le stock nul est écarté. On a donc q ≥ 1 et T ≥ ⌈q ÷ `mining_rate`⌉ ≥ 1. Dans la règle 5, t + 1 ≥ 1.
- **Départages :** ils sont complets dans les deux règles.

**Le scénario du cycle avec la règle du gain par tick.** Réglages de test : `jump_ticks` = 5, `mining_rate` = 10, `cargo_capacity` = 100, `deposit_stock` = 20 000, prix `[[10, 15], [12, 12], [8, 18]]` (`src/fourx/core/tunables.toml:7-10` ; `steps_partie.py:223`). Aucun PNJ n'est créé par `Game` seul.

| Moment | Règle | Touches |
| :-- | :-- | :-- |
| départ, à l'arrêt dans le système de la station 1, cargaison vide | 6 ; g ailleurs | `("d",)` |
| ordre envoyé, puis en route | 2, puis 3 | `()` |
| `Arrived`, route vide (`model.py:202-207`) | 1 | `("enter",)` |
| tick suivant, à l'arrêt sur g | 6 ; g ici, si la condition « reste conseillé » tient | `("m",)` |
| minage, y compris le tick où la cargaison devient pleine (`MiningEnded` arrive au tick suivant, `ecrans.feature:81-83`) | 2, puis 4 | `()` |
| `MiningEnded` sans `causation_id` (`model.py:208-216`) | 1 | `("enter",)` |
| cargaison pleine ; g n'est pas dans le système d'une station | 5 ; station ailleurs | `("d",)` |
| en route, arrivée | 3, puis 1 | `()`, `("enter",)` |
| dans le système de la station | 5 : V(ici) ÷ 1 contre V(s′) ÷ (5k + 1) ; les écarts de prix (au plus 18 ÷ 8 = 2,25) ne compensent jamais un facteur d'au moins 6 | `("v",)` |

**La suite attendue (l. 1656) est donc juste.** Deux des trois conditions sont nécessaires :
- « g n'est pas dans le système d'une station » : sinon la règle 5 vend sur place, sans `("d",)` ;
- « g reste conseillé à l'arrivée » : T de g perd le trajet d'approche, mais les autres cycles changent aussi.

La première condition (« le système de la station 1 n'a pas de gisement ») est inutile, mais sans danger.

---

## 3. Majeur

### MA1. La condition de graine du scénario du cycle ne peut pas être calculée dans `monde_convient`

**Passage :** l. 1654 (« dont le gisement que conseille la prochaine étape au départ […] et dont ce gisement reste conseillé une fois le vaisseau arrivé (les étapes le vérifient sur l'observation d'arrivée […]) »), et l. 1658 (« la condition de graine […] s'ajoute à `monde_convient` »).

**Problème :**
1. `monde_convient(etat, condition)` ne reçoit que l'état rendu par `world.generate` (`tests/scenarios/steps/steps_partie.py:233`). Il est appelé avant la création de `Game` (`steps_partie.py:279-288`). À ce moment, il n'y a :
   - ni personnage du joueur : `create_character` le crée au tick suivant (`steps_partie.py:20`) ;
   - ni observation, ni `ClientModel`.

   Ni « le gisement que conseille la prochaine étape », ni « l'observation d'arrivée » n'existent donc à cet endroit.
2. Le développeur doit choisir entre deux conceptions :
   - (a) refaire le calcul de la règle 6 dans les étapes, sur l'état ;
   - (b) jouer une partie d'essai par graine candidate (créer le joueur, jouer jusqu'à l'arrivée, appeler `next_step`). Cela change la structure de `partie_serveur`, que `partie.feature` partage.
3. La voie (b) a trois coûts cachés :
   - une partie d'essai créée sous `serveur.dossier` casse `Serveur.evenements()`, qui exige un seul `*/events.jsonl` (`steps_partie.py:203-204`) ;
   - la graine serait choisie par le code testé lui-même : une erreur de `next_step` déplacerait la graine au lieu de faire échouer le scénario ;
   - la pull request de scénarios modifie les étapes, donc chaque mutant de `core` rejoue les scénarios (`.github/scripts/mutation.py:85`), parties d'essai comprises.
4. « Vérifient sur l'observation d'arrivée » ne correspond pas à la procédure. Le `("m",)` est relevé au tick qui suit l'acquittement, et non sur l'observation d'arrivée. Sans autre vaisseau, le résultat est le même, mais le texte doit le dire.

**Proposition :** choisir la voie (a) et l'écrire dans 23 octies.
- Sur les réglages de test, le stock (20 000) dépasse la capacité (100), et aucun autre vaisseau ne mine. Donc q = `cargo_capacity` pour tout gisement, et la visibilité du stock ne compte pas.
- La condition se calcule alors sur l'état seul, dans `monde_convient`, sans le code testé. Avec S₀ le système de la station 1 :
  - g₀ = argmax de G ÷ T, avec G = `cargo_capacity` × prix(s, minerai de g) et T = `jump_ticks` × (d(S₀, g) + d(g, s)) + ⌈`cargo_capacity` ÷ `mining_rate`⌉ ;
  - départages de la règle 6 : plus petit T, puis plus petit identifiant de gisement, puis de station ;
  - g₁ = le même calcul depuis le système de g₀, où d(g₀, g₀) = 0 ;
  - la graine convient si g₁ = g₀, et si aucun système de station n'est celui de g₀.
- Écrire la phrase de condition exacte, qui doit égaler la chaîne testée par `monde_convient` (`steps_partie.py:247`). Retirer « les étapes le vérifient sur l'observation d'arrivée ».
- La première condition peut tomber.

---

## 4. Détails

- **D1. Règles 5 et 6 : systèmes inaccessibles** (l. 657-658). Le client traite déjà les systèmes isolés (`tests/clients/test_textual_app.py:515-525`, « inaccessible »). `distances` ne rend pas ces systèmes, et un calcul naïf lève `KeyError`. *Proposition :* « stations et gisements absents de `distances` sont ignorés », comme `_gisement_vise` (`scripted_miner.py:63`).
- **D2. Textes des règles 1 et 4** (l. 649, 652).
  - Règle 1 : « suivi de « (+n) » » ne dit pas s'il y a une espace avant.
  - Règle 4 : « au plus [durée] » remplace-t-il tout le détail, ou seulement « dans [durée] » ? `test_guide.py` compare les chaînes. *Proposition :* donner les deux détails en entier, par exemple « fin du minage dans au plus [durée] : cargaison pleine ou gisement vide ».
- **D3. Aide avec observation sans vaisseau** (l. 667, 670). La capacité vient du vaisseau du joueur, et le cas de la règle 0 bis n'est pas couvert. *Proposition :* « (connue au premier tick) » aussi dans ce cas.
- **D4. Objectif 17 et 23 decies : « distance minimale »** (l. 180, l. 1680). C'est un reste de la version précédente. Le point 7 ter ne garantit plus de distance, mais un non-recouvrement de boîtes (l. 624, 626). *Proposition :* remplacer par « aucun recouvrement des boîtes, ni des cases dans la grille ».
- **D5. Scénario de la disposition : « sans recouvrement »** (l. 1652). Les étapes n'importent que `force_layout` (l. 1658), il s'agit donc des boîtes. *Proposition :* « aucune paire de boîtes 0,125 × 0,15 ne se recouvre ».
- **D6. Test de non-recouvrement dans la grille : les vaisseaux et le modèle** (l. 626).
  - `render` demande un `ClientModel` (l. 967).
  - Un monde tout juste généré n'a aucun vaisseau, et l'observation de l'acteur 1 non plus : la ligne des vaisseaux ne serait jamais dessinée, donc jamais testée.
  - *Proposition :* le test construit l'observation par `msgspec.structs.replace` : un vaisseau du joueur dans un système, et deux `OtherShipView` dans chaque système (pour avoir « ▲2 »). Le modèle la reçoit par `on_update`.
- **D7. Taille du canevas dans ce test.**
  - « Les places comprennent les bordures » (l. 604), mais le texte ne dit pas si `#carte` a une bordure.
  - Le test doit construire `View(width, height)` pour 120 × 36 et pour 100 × 30. Selon le tableau, c'est 72 × 27 et 52 × 21, ou 70 × 25 et 50 × 19 avec bordure.
  - *Proposition :* donner les deux tailles. Mes calculs montrent que la marge des boîtes tient dans les deux cas : 4,75 colonnes au moins pour 4 cases occupées, et 2 lignes d'écart au moins.
- **D8. Signatures des quatre étapes** (l. 962, « mêmes types »). `relax` a besoin du graphe. *Proposition :*
  - `initial_layers(systems) -> dict[int, tuple[float, float]]` ;
  - `relax(systems, positions)` ;
  - `normalize(positions)` ;
  - `separate(positions)`.

  Dans `separate`, dire aussi le sens de l'écart quand les deux coordonnées sont égales sur l'axe retenu (par exemple, le plus petit identifiant à gauche ou en haut).
- **D9. Marques du test des 2 000 graines.**
  - Le point 7 ter dit `proprietes` et `lent` (l. 626) ; 23 decies ne dit que `lent` (l. 1680). À aligner sur les deux marques.
  - Le module a déjà `pytestmark = pytest.mark.proprietes` (`tests/proprietes/test_proprietes.py:35`). Il suffit d'ajouter `@pytest.mark.lent`.
  - Ce test tourne trois fois en CI : `tests-outillage` (`uv run pytest`, `.github/workflows/ci.yml:116`), `rejeu` (`ci.yml:194`) et `proprietes` (`ci.yml:215`). À relever au point 28 bis.
- **D10. Cadre Stations en 100 × 30** (l. 612, 618). Il reste 21 lignes entre la barre d'état et l'historique : 7 + 8 pour les deux premiers cadres, donc 6 lignes pour Stations, bordure comprise. Or il faut jusqu'à 3 stations et 2 lignes de minerai. Le défilement n'est prévu que pour la liste des destinations. *Proposition :* le cadre défile, ou les lignes en trop sont coupées.
- **D11. Procédure du scénario : envoi** (l. 1655). « envoyer la commande du `Step` par `model.send` » sous-entend la soumission du message par la connexion, comme le fixe la convention de `steps_ecrans.py:16-17`. *Proposition :* écrire « par `Serveur.envoyer` » (`steps_partie.py:175-184`).

---

## 5. Points vérifiés qui tiennent

- **Signatures du point 13 :**
  - `mettre_a_jour` existe ;
  - `Step(..., command: Command | None)` est cohérent avec `orders.Command` ;
  - `HistoryEntry` remplace `history: tuple[str, ...]` (`model.py:61, 73-75, 151, 183-201`) ; la l. 957 est marquée ;
  - `help_pages(observation, dev)` est cohérent avec `FourxApp(..., set_speed)`, où `set_speed is None` hors mode développement (l. 948) ;
  - `View`, `Cell`, `zoom`, `pan`, `system_at` et `render` sont cohérents avec la projection et les conventions de la l. 630-638.
- **Contrats d'imports :** `clients` peut importer `policies` et `schema`, mais ni `core` ni `server` (`.importlinter:48-56`). La portée est recalculée par `distances`.
- **Mutation :**
  - `proprietes` n'est pas exclu de mutmut : les 50 graines y passent, comme voulu ;
  - `lent` en est exclu (`setup.cfg:9-10`) ;
  - `palette.py` n'a pas de fonction, donc aucun mutant et pas d'échec (`mutation.py:92-97, 144-145`) ;
  - les fichiers neufs de `clients` n'ont pas de plancher (`mutation.py:141-143`) ;
  - `frames.py` et `textual_app.py` restent exclus (`setup.cfg:17-20`).
- **Scénarios en attente :** `xfail(strict=True)` (`tests/scenarios/conftest.py:70-71`). Les trois scénarios nouveaux ou réécrits échouent sur le code de l'amendement 1, faute de `force_layout`, `next_step` et `help_pages`. Les deux scénarios de refus échouent dès que l'étape lit `.text` (`steps_ecrans.py:151`). Le scénario de la disposition échoue encore après 23 nonies.
- **Touches existantes :** aucun test n'utilise `h`, `z` ou `c` comme touche sans effet. Seul `x` est concerné, et il est traité.
- **ADR 0006 :** cohérente avec le point 7 ter (seize couleurs RGB, demi-blocs, aucune dépendance nouvelle, verdict non bloquant).

## 6. Fichiers lus

- **Document et revues :** `docs/designs/niveau-2-m1-noyau.md` (passages cités), `docs/adr/0006-client-retro-8-bits.md`, `docs/revues/2026-11-22-niveau-2-m1-noyau-amendement-2/implementation_readiness_report_tour2.md`, `goldfish_review_report.md`.
- **Code :** `src/fourx/clients/model.py`, `texts.py` ; `src/fourx/policies/scripted_miner.py` ; `src/fourx/schema/observation.py`, `orders.py`, `actors.py` ; `src/fourx/core/tunables.toml`.
- **Tests :** `tests/scenarios/ecrans.feature`, `steps/steps_partie.py`, `steps/steps_ecrans.py`, `conftest.py` ; `tests/clients/test_textual_app.py` (en partie) ; `tests/proprietes/test_proprietes.py` (en-tête et marques).
- **Configuration :** `setup.cfg`, `pytest.ini`, `.importlinter`, `.github/scripts/mutation.py`, `.github/workflows/ci.yml`.

Je n'ai pas relu `frames.py`, `textual_app.py`, `map_layout.py`, `geometry.py` ni `events.py` à ce tour : je me suis fié au rapport du tour 2 et à leur usage dans les fichiers lus.
