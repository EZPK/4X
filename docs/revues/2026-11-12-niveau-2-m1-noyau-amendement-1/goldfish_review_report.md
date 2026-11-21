# Goldfish Annotated Review Report — étape 7, tour 1

**Status: resolved** (2026-11-12). Décisions du propriétaire : E1 → (b) la colocalisation est acceptée (alternative AA documentée ; bornes et risques revus) ; E2 → (b) le stock des gisements devient de classe proximité (`DepositView.stock` facultatif ; règle du PNJ et refus `DEPOSIT_EMPTY` adaptés). Les 32 corrections F1 à F32 sont appliquées, F7 et F13 ajustées à ces deux décisions. Aucun constat contesté ; 4 détails notés sans correction. Le tour 1 n'est pas « propre » au sens d'EGM (un bloquant y a été relevé) : la convergence demande deux tours propres consécutifs.

**Target :** `docs/designs/niveau-2-m1-noyau.md` (spécification, lignes 1 à 1039 ; et les points du plan détaillé que les constats citent)

**Sources :**
- `critic_report.md` (conception, structure, style) ;
- les points restants de `zoom_out_report_tour2.md` (A à I) ;
- les points restants de `comprehension_report.md` (1 à 15).

Les doublons sont fusionnés. Chaque point est classé : PROPOSE FIX (correction proposée), CONTEST (constat contesté, preuve à l'appui), ESCALATE (décision qui revient au propriétaire), DECLINE (détail noté, non corrigé).

## À décider par le propriétaire (ESCALATE)

### [E1] Station et gisement dans le même système — conception-1 — gravité : bloquant
*   **Constat :** colocalisation dans 84 % des mondes ; boucle de 101 ticks sans trajet, stratégie dominante ; gisement vidé par les PNJ ; lignes « aucun gisement vidé » et bornes fausses.
*   ***Suggestion :*** ESCALATE. C'est une règle du jeu, avec deux réponses défendables.
    - **(a) Interdire la colocalisation.** Les gisements sont tirés parmi les systèmes sans station. Il faut alors `systems_min` ≥ `stations_max` + `deposits_max` = 9 : la fourchette devient **9 à 12 systèmes** (ADR 0004 et objectif 16 modifiés). Toute boucle passe par au moins un saut aller et un retour (cycle ≥ 2 × 400 + 100 = 900 ticks). Au plus 5 × ⌈10 000 ÷ 900⌉ × 100 = 6 000 unités sont alors extraites par gisement et par fenêtre, pour un stock de 20 000 : aucun gisement ne se vide, ce qui résout aussi le constat D de l'étape 5.
    - **(b) Accepter la colocalisation**, comme une richesse de la carte : alternative documentée, réécriture des passages sur l'épuisement, bornes d'économie qui modélisent l'épuisement et la régénération.
*   ***Recommandation de l'agent :*** (a). C'est la seule option qui garde « tout prend du temps » vrai sur chaque monde, et elle simplifie les bornes.

### [E2] Le stock public trahit les mineurs hors de portée — conception-5 — gravité : majeur
*   **Constat :** avec `mining_rate` = 1, la baisse de `DepositView.stock` compte les vaisseaux qui minent un gisement, où qu'il soit, ce qui contourne l'ADR 0005.
*   ***Suggestion :*** ESCALATE. Deux réponses :
    - **(a)** accepter ce canal comme limite connue, écrite dans l'ADR 0005 et au Technical Plan, point 5, en attendant les scanners ;
    - **(b)** rendre le stock `NEARBY`, rapporté au système du gisement. Le joueur ne connaîtrait alors plus le stock des gisements lointains, et la carte en dirait moins.
*   ***Recommandation de l'agent :*** (a). On voit moins de choses avec (b), et la carte reste lisible avec (a).

## Corrections proposées (PROPOSE FIX)

| N° | Sources | Gravité | Correction proposée |
| :-- | :-- | :-- | :-- |
| F1 | structure-M1 ; étape 6-2 | majeur | En tête, une **règle de préséance** (un passage « (amendement 1) » l'emporte sur le texte d'origine, marqué ou non) et une **légende complète des marques** : réécrit, précisé, remplace, complète, « Ajoutés par l'amendement 1 », marque en ligne dans les blocs de code, « remplacé par l'amendement 1, voir … ». |
| F2 | conception-9 ; structure-M3, M4 ; étape 5-M1/H ; étape 6-2 | majeur | Marquer les passages encore faux : conventions (CUJ « sans les adapter ») ; règle du minimum et « seule exigence ajoutée » (les décisions du 2026-11-12 priment aussi, étape 6-9) ; « copiés de `ore_prices` » et la phrase de `world.generate` ; refus et création liés à une station unique ; tableau des événements (départ, arrivée → `NEARBY`) ; « position publique » ; risque du bug volontaire (placement des sites) ; point 17 (« 10 200 unités ») ; fenêtre de 1 000 ticks et « Calcul des bornes » au point 27. Ramener la marque de « La carte » aux deux premières phrases, et placer la marque du client avant la description de l'affichage. |
| F3 | structure-M2 ; style-M3 | majeur | Renvoi cassé : « voir le Technical Plan, point 9 ». |
| F4 | structure-M6 ; style-M4 | majeur | Renvois préfixés : « plan détaillé, point 23 quater / 28 bis / 23 quinquies ». |
| F5 | conception-2 ; étape 6-5 | majeur | Clé complète de chaque tirage : (graine, tick 0, entité, motif). Entité = 0 pour la taille, le nombre de liens et `npc_count` ; k pour le parent du système k ; i (rang du lien, de la station, du gisement) pour les autres. L = 1 + `keyed_below`(…, `extra_links_max`). |
| F6 | conception-3 | majeur | Raisonnement corrigé (Technical Plan, point 5, et ADR 0005) : `Event.visibility` est encodé, et la valeur `nearby` casse la lecture par l'ancien code ; c'est accepté parce qu'avant M5 les données sont régénérées (niveau 1, §7). `snapshot_schema_version` reste à 1, puisque l'instantané pris au tick 0 a un `last_tick` vide ; `event_schema_version` reste à 0 pour la même raison. |
| F7 | conception-4 | majeur | Règle du filtre `NEARBY` : le système de référence est le `system_id` de l'entité, ou celui de la charge utile d'un événement ; un type qui porte un champ `NEARBY` doit avoir un `system_id` (vérifié par un test) ; les champs `NEARBY` d'une entité sont visibles tous ensemble ou pas du tout ; les positions qui comptent sont celles de l'état T, que `observe` reçoit. Le « test générique entre vues et état » est étendu. |
| F8 | conception-6 ; étape 5-M7 | majeur | Risque M4 chiffré : environ 4 ordres par cycle de 1 701 ticks, soit environ 425 ticks par décision. La définition du pas et du verdict du niveau 1, §2 et §8, est à revoir à M4 (risque signalé, sans modifier le niveau 1 ici). Piste qui ne change pas `rules_version` : un environnement d'entraînement qui enchaîne les ticks sans décision jusqu'à la suivante. |
| F9 | conception-7 ; étape 6-14 ; style-M7, M8 | majeur | Horloge rapide : « vitesse maximale » = palier ×1000 (0,003 s), et le plancher de 0,001 s est retiré ; en surcharge, la vitesse réelle reste sous la vitesse demandée (le tick dure ce qu'il dure, puis l'horloge attend la période) ; au réveil, un tick est joué tout de suite ; **contre-pression** : sous 0,05 s par tick, l'horloge attend que la file de mises à jour du propriétaire soit vide avant le tick suivant, ce qui borne à un tick le débordement de l'arrêt « à la prochaine alerte ». Une alternative (arrêt décidé par le serveur) est ajoutée ; le débordement est mesuré au point 28 bis. Un seul terme partout : « vitesse de l'univers », par palier nommé. |
| F10 | conception-8 ; structure-N9 ; étape 5-C ; étape 6-3, 13 | majeur | Règle de mise en page améliorée : le rang d'un système est celui de son parent dans le parcours en largeur s'il est libre, sinon le premier rang libre en dessous ; les liens de l'arbre deviennent ainsi le plus souvent horizontaux. Maquette **recalculée par un script** sur un graphe d'exemple (avec au moins un lien en plus), colonnes de 8 caractères, barre d'état de 80 caractères au plus, historique chronologique, refus possibles. Tests de propriétés : part des liens tracés et hauteur de la carte, publiées au compte rendu. |
| F11 | structure-M5 | majeur | `station_ore_prices` : mention « proposition de l'agent de code, confirmée par le propriétaire le 2026-11-12 ». |
| F12 | structure-M7 ; conception-13 ; style-M10 | majeur | Les noms nouveaux passent en anglais, comme le veut la convention du glossaire, et vont dans un module neutre : `policies/geometry.py` (`distances(systems, start)`) et `policies/cargo.py` (`most_abundant(cargo)`) ; client : `clients/model.py`, `clients/map_layout.py`, `clients/texts.py`, `clients/frames.py` ; dossier de la partie : `speed.jsonl`. Le point 13 les liste tous ; `public_tunables` est le dernier champ de `Observation` ; marques sur `OtherShipView`, `Visibility` et `world.npc_count`. |
| F13 | étape 6-4 ; étape 5-D | majeur | Formule des bornes complète : nombre de ventes possibles = N × (⌈W ÷ C_min⌉ + 1) × 2 (au plus deux ventes par cycle, une par minerai) ; croissance entre E_min − (E_min × `tax_rate_bp` ÷ 10 000 + ventes possibles) et E_max − E_max × `tax_rate_bp` ÷ 10 000. Si E1 (a) est retenu, d_min ≥ 1 et l'épuisement est exclu par le calcul ; sinon, la limite est écrite. |
| F14 | étape 6-6 | majeur | Écrire au Technical Plan, point 5, ce que fait le code : une fin de minage spontanée (cargaison pleine, gisement vide) porte `causation_id` = `None` ; une fin provoquée par un ordre qui remplace le minage porte l'identité de cet ordre (`_arreter_minage`, `core/step.py`). |
| F15 | étape 5-A ; étape 6-1 | majeur | La veille de l'ordinateur portable quitte les Open Questions et reste un risque vérifié au plan détaillé, point 23 quater. Open Questions : « aucune ». |
| F16 | étape 5-B | majeur | Scénario « temps comme ressource » : il échoue sur le code d'origine parce qu'il lit les durées dans `observation.public_tunables`, qui n'existe pas encore, et les compare à `tunables.toml`. Le trajet observé doit durer `jump_ticks`. Il est écrit que la valeur 400 n'est vérifiée par aucun test, puisque `tunables.toml` fait foi. |
| F17 | étape 5-G ; style-M12 | majeur | La proximité devient le quatrième changement de l'Overview et figure dans l'objet du tableau des amendements ; l'objectif 6 reçoit une vérification de la proximité. |
| F18 | étape 6-8 ; style-M2 | majeur | « le noyau » au sens du document → « ce document (version d'origine) ». |
| F19 | style-M1 | majeur | « propriétaire » d'un vaisseau → « détenteur », dans le document, l'ADR 0005 et le glossaire. |
| F20 | style-M5 | majeur | « plus de 99 % du temps en trajet » → « environ 94 % d'un cycle en trajet (1 600 ticks sur 1 701) ». |
| F21 | style-M6 | majeur | « 400 » écrit en dur → « `jump_ticks` ticks (400 dans les valeurs initiales) ». |
| F22 | style-M9 | majeur | « rappel » → « fonction de rappel `set_period` », typée `Callable[[float \| None], None]`, nommée comme seule exception locale à « la même porte » ; elle disparaît à M3, quand le client et le serveur ne partagent plus de processus (conception-14). |
| F23 | style-M11 | majeur | « 4 à 6 gisements, au moins deux par minerai ». |
| F24 | style-M13 ; structure-N7 | majeur | Alternatives J à Z : le libellé « Raison du rejet » est remplacé par « Retenu » quand il décrit le choix fait. |
| F25 | style-M14 ; étape 6-7 | majeur | « code actuel », « carte actuelle » → « code d'origine », « carte d'origine ». En tête : les volets A et B (points 15 à 23) sont livrés, et le texte d'origine non marqué de ces points décrit le code fusionné. « Tâche de relais » est relié à « une tâche de `__main__.py` lui transmet les mises à jour ». |
| F26 | conception-10 | détail | `speed.jsonl` commence par une ligne d'en-tête versionnée (`speed_log_schema_version` = 1). |
| F27 | conception-11 ; étape 5-F | détail | Objectif 15 : la vérification inopérante est retirée ; seul reste le rejeu d'une partie accélérée. |
| F28 | conception-12 | détail | Écrit : les modules purs du client sont mutés sans plancher, comme tout ce qui sort de `core` et `schema` (Technical Plan, point 1, seuil de mutation). |
| F29 | conception-15 | détail | Une ligne justifie `npc_count` dans `core.world` : c'est un tirage de la graine du monde, comme la génération. |
| F30 | conception-16, 17 ; étape 6-14 | détail | Colonne « Signal » ajoutée à la table des risques de l'amendement ; l'estimation en minutes est libellée « ≈ … à 3 s par tick » ; la taxe n'est connue qu'après une vente (écrit) ; formule du minage restant = min(⌈libre ÷ débit⌉, ⌈stock ÷ débit⌉), le test croisé seulement sans partage du gisement. |
| F31 | structure-N2, N3, N4, N6, N8 ; étape 6-10, 11, 15 ; étape 5-H | détail | Marque sortie de l'intitulé H2 des CUJ ; tableau des amendements complété (Additional Resources, conventions, introduction des alternatives) ; introduction des alternatives marquée ; termes du glossaire déplacés au point 12 ; non-objectif en double fusionné ; point 23 bis réécrit (l'intégration est faite) ; point 20 « réécrit » au lieu de « complété » ; liens vers les ADR dans l'en-tête ; renvoi au point 26. |
| F32 | style, détails | détail | Corrections de forme groupées : « le fun » entre guillemets, « fonctionnent », « ont la même durée », identifiant *n* au lieu de « a », « arrondi vers le haut », `10_000`, « forment une file », doubles négations, accords, backticks, 1 701 au lieu de « plus de 1 600 », « partie de test » partout. |

## Notés sans correction (DECLINE)

- **Étape 5-N6 (altitude) :** `asyncio.Event`, le format JSON et les chaînes de motifs restent ; ils servent l'exécutant sans mémoire.
- **Étape 5-I (borne basse souvent nulle) :** assumé ; la valeur pour la graine 1 sera citée au compte rendu (ajouté au point 27 par F13).
- **Étape 6-12 (alternative R) :** les renvois d'origine disent déjà « le niveau 1 (alternative R) » ; pas d'ambiguïté réelle.
- **Style, autres détails :** subjectifs ou sans effet sur la compréhension.

## Contestés (CONTEST)

Aucun.
