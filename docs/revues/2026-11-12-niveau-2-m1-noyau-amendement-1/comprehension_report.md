# Étape 6 — Test de compréhension (amendement 1)

*   **Cible :** `docs/designs/niveau-2-m1-noyau.md` ; spécification lignes 1 à 1039, plan détaillé lignes 1040 à 1542.
*   **Relecteur :** `egm-comprehension`, sans contexte, mode REVIEW, sans standard.
*   **Bilan :** le document se reformule sans difficulté, sans point bloquant ; 6 points majeurs et 9 mineurs.

## Ce que propose le document

L'amendement 1 répond à une partie de test de 97 ticks, jouée le 2026-11-11, qui a montré quatre gênes : rythme trop rapide, écran confus, touches peu claires, refus incompris. Il change trois choses dans M1, avant le volet C (rejeu, divergence, économie) :

1. **Un monde plus grand.** La graine tire 8 à 12 systèmes (un arbre plus 1 à 3 liens), 4 à 6 gisements, 2 à 3 stations, chacune avec ses prix (`station_ore_prices`), et 3 à 5 PNJ. L'ADR 0004 élargit les fourchettes du CUJ 1.
2. **Un client Textual à écran unique.** Il est fait de cadres indépendants qui lisent un modèle pur (`ClientModel`), avec une carte calculée en colonnes, des refus traduits en français qui disent où aller, deux alertes et des touches AZERTY sans Majuscule.
3. **Le temps devient une ressource, et les durées sont des règles.** Un saut dure 400 ticks, remplir une cargaison 100 ticks, la période nominale passe à 3 s. Pour que le joueur connaisse les durées, `observe` reçoit les réglages et publie `jump_ticks` et `mining_rate` (ADR 0003, `protocol_version` 2).

S'y ajoutent :
- une visibilité par proximité des autres vaisseaux (classe `NEARBY`, ADR 0005) ;
- un PNJ `scripted_miner` v2, qui choisit entre plusieurs gisements et plusieurs stations ;
- une accélération de l'univers en mode `--dev` seulement : rappel local, rien dans les règles ni dans le journal ;
- des fenêtres d'économie de 10 000 ticks, avec des bornes calculées par l'outil de régénération à partir de la géométrie du monde de la graine 1.

Le tout est livré par un « volet B bis » (points 23 bis à 23 sexies), qui s'insère avant le volet C et se termine par une partie d'essai du propriétaire.

## Comment fonctionne le système existant, selon ce document

Les volets A (noyau, règles, registre) et B (serveur, client, PNJ) sont fusionnés.

- **Le monde.** Une graine génère un monde fixe : trois systèmes en chaîne, une station, un gisement par minerai. Les sites sont placés par une permutation tirée.
- **Le serveur.** Il tourne en mémoire, dans un seul processus `asyncio`. Une horloge (1 s par défaut) appelle `step` (un état figé, déterministe), journalise les ordres soumis dans SQLite, écrit les événements v0 en JSONL, et envoie à chaque acteur une observation produite par `observe(état, acteur)`, seul canal vers le joueur.
- **Les acteurs.** Le client Textual affiche une carte ASCII et se commande par chiffre (Majuscule requise sur AZERTY). Un PNJ `scripted_miner` v1 reçoit ses mises à jour par une tâche de `__main__.py`, et joue le minerai le mieux payé, avec `jump_ticks` = 5 et `mining_rate` = 10.
- **L'économie.** Les ventes se font à prix fixes : elles créent de l'argent par émission, et la taxe en détruit.
- **À venir.** Le volet C (rejeu de la partie de référence, outil de divergence, fourchettes économiques par fenêtres de 1 000 ticks) n'est pas commencé, et `RULES_REVISION` vaut 0.

## Constats

### Majeurs

1. **La question ouverte ne peut pas être fermée avant le retour à Approved.** La seule question (la veille de l'ordinateur portable) n'est tranchée qu'au point 23 quater, qui suit la fusion des points 23 bis et 23 ter. Or le point 23 bis ne fusionne qu'après le retour à Approved, qui exige une liste vide. Il faut trancher la question avant, ou dire qu'elle peut rester ouverte. (Même constat que le point A de la seconde relecture de l'étape 5.)
2. **Aucune règle ne dit quel texte l'emporte, et des passages devenus faux restent sans marque.** La convention de l'en-tête décrit les marques sans dire que le passage « (amendement 1) » l'emporte sur l'original en cas de conflit. Marques manquantes ou mal placées :
   - « La carte » : la marque couvre aussi le stock et la régénération des gisements, qui restent vrais ;
   - le refus de la vente, « vaisseau hors du système de la station » (station unique) ;
   - « créer un personnage… dans le système de la station » ;
   - « `world.generate` copie `ore_prices` dans la station » ;
   - « position publique » ;
   - le tableau des événements (« départ » et « arrivée » publics) ;
   - la marque du client, placée après « au clavier », qui ne dit pas si l'affichage décrit avant est aussi remplacé ;
   - le point 17 (« Avec deux PNJ, au plus 10 200 unités… ») ;
   - « chaque fenêtre de 1 000 ticks » au point 27, où la marque ne couvre que la première borne ;
   - le « Calcul des bornes » d'origine, qui dit encore « à refaire si un réglage change ».
3. **La maquette de la carte contredit la règle qu'elle dit suivre.** Les liens 3–5, 5–7, 7–10 et 8–11 relient des colonnes voisines au même rang, et sont écrits en texte au lieu d'être tracés. La maquette n'a aucun lien en plus (11 liens pour 12 systèmes), et ses colonnes font 7 caractères au lieu de 8.
4. **La formule des bornes d'économie n'est pas complète.** « Une unité par vente possible » ne définit pas le nombre de ventes possibles, et la combinaison qui donne les bornes de croissance n'est pas dite. L'outil doit pouvoir reconstituer le calcul à partir du texte seul.
5. **L'« entité » des tirages de la génération n'est pas définie.** Avec un générateur à clé, deux tirages de même clé donnent la même valeur ; l'ordre ne distingue rien. La valeur d'« entité » de chaque tirage (rang dans l'arbre, numéro du lien, de la station, du gisement) n'est donnée nulle part.
6. **L'alerte de fin de minage repose sur une propriété de `causation_id` que le document ne dit pas** : une fin spontanée (cargaison pleine, gisement vide) porte `causation_id` = `None`, et une fin provoquée par un ordre porte l'identité de cet ordre.

### Mineurs

7. Le document ne dit pas quels points décrivent du code déjà livré. « Tâche de relais » n'est pas relié à « une tâche de `__main__.py` lui transmet les mises à jour ». « Volet B » est employé avant d'être défini.
8. « Le noyau » désigne à la fois le paquet `core` et le document d'origine (« le point 7 du noyau »).
9. La règle du minimum (Technical Plan, point 1) n'étend pas sa préséance aux décisions du 2026-11-12, alors que l'amendement va au-delà du minimum et change le niveau 1.
10. Le point 23 bis parle encore de « l'intégration de ce brouillon », et d'une puce et d'un tableau déjà présents.
11. Les listes des passages touchés (en-tête, règles d'intégration) ne concordent pas : points 26, 28 et 28 bis, et Additional Resources. Le point 20 dit « complété », alors que `partie.feature` est réécrit.
12. « Alternative R » désigne aussi une alternative du niveau 1.
13. La maquette contredit le format des refus : format de `NOT_AT_STATION`, historique non chronologique, et un refus au tick 420 qui serait `SHIP_EN_ROUTE`.
14. Plusieurs termes du client restent vagues : « vitesse maximale » (×1000 ou plancher de 0,001 s ?), « borné par le stock » (ticks ou unités ?), « mode courant », coupe de la carte « sur deux bandes ».
15. Les ADR ne sont pas liées dans l'en-tête.

## Points qui se relient bien

Le fil problème, objectifs, Technical Plan, plan détaillé et vérification se suit. Les trois ADR concordent avec le Technical Plan. Les nombres concordent : 400 ticks valent 20 min, un cycle d'environ 1 700 ticks à 3 s dure plus d'une heure, et l'extraction maximale (5 × 101 × 100 = 50 500) reste sous 80 000.
