# Rapport de revue — Étape 6 (Test de compréhension)

*   **Document revu :** [architecture-niveau-1.md](./docs/designs/architecture-niveau-1.md) — spécification l. 1 à 459, plan d'implémentation l. 460 à 581
*   **Relecteur :** egm-comprehension, sans contexte de la conversation, sans standard (le test porte sur l'autonomie du document, pas sur son niveau de détail)
*   **Date :** 2026-10-31
*   **Résultat :** 11 majeurs, 6 mineurs.

## Ce que propose la spécification (paraphrase, l. 1-459)

Le document fixe, avant toute ligne de code, l'architecture commune à trois systèmes qui partagent une même simulation : le jeu (noyau, serveur, client terminal Textual), l'entraînement des joueurs IA et l'observabilité.

Au centre se trouve une fonction pure et déterministe, `step(état, ordres, graine, réglages)`. Elle ne manipule que des entiers, et tout le monde l'appelle. Les sources de vérité sont :
- un journal des ordres en SQLite ;
- des instantanés en MessagePack ;
- des événements en Parquet, considérés comme recalculables.

Une seule fonction `observe` produit ce que chaque acteur voit. Un registre comptable en partie double conserve l'argent. Chaque format porte un numéro de version et évolue par migration.

L'entraînement (PPO, MLflow) tourne sur un second PC. L'observabilité repose sur DuckDB, marimo et une page d'accueil statique avec des statuts vert, orange ou rouge. Les agents de code IA sont encadrés par la CI, avec un risque assumé : ils utilisent les identifiants GitHub du propriétaire. La construction suit les jalons M0 à M6, et un déclencheur chiffré dit quand passer à Rust.

## Ce que dit le plan d'implémentation (paraphrase, l. 460-581)

Le plan ne produit que de la documentation, aucun code. Il finalise ce document, puis crée :
- `CLAUDE.md` (règles de l'agent) ;
- un glossaire ;
- un index d'ADR et six ADR ;
- un registre des questions ouvertes ;
- une feuille de route.

Il ajoute une note de renvoi en tête de la RFC et de `concepts_brief.md`, puis supprime `design_draft.md`.

La vérification comprend une revue EGM, un contrôle des liens, un tableau de couverture des décisions de la RFC, et un test : une session d'agent neuve, qui ne lit que `CLAUDE.md`, doit savoir ce qui lui est interdit et quel document lire pour M0.

Le document ne décrit pas l'état actuel des choses, en dehors de « pas de code » et de l'existence de la RFC. `concepts_brief.md` et `design_draft.md` n'y sont jamais présentés.

## Constats

### 1. Majeur : le client Textual sert dès M1, alors que le protocole n'arrive qu'en M3

*   **Où :** CUJ 1 (l. 80-88), §1 (l. 159), tableau des jalons (l. 333-335), §9 (l. 266).
*   **Problème :**
    - Le CUJ 1 fait jouer le propriétaire avec le client Textual, et le critère de M1 exige ce CUJ.
    - Or tout client passe par le protocole (§1), et le protocole comme le client arrivent en M3.
    - Même chose pour le notebook de M1 : les événements v1 arrivent en M2, alors que l'objectif 6 impose que toute métrique vienne des événements.
    - Le lecteur ne peut donc pas dire comment on joue, ni d'où vient la métrique, en M1.
*   **Correction :** dire ce qui existe en M1. Soit un client de développement provisoire, autorisé à importer le noyau jusqu'à M3, avec des événements provisoires non versionnés. Soit déplacer ces critères vers M2 et M3.

### 2. Majeur : on ne sait pas où les ordres sont validés

*   **Où :** schéma §1 (l. 138-143), objectif 4 (l. 50), « Ordre d'un tick » (l. 184-189), §3 (l. 203), §8 (l. 250).
*   **Problème :**
    - Le schéma place la réception des ordres (limites, refus, budget) hors du noyau. Pourtant, « Ordre d'un tick » met la validation à l'étape 2, donc apparemment dans `step`.
    - Le journal ne contient que les ordres « acceptés ». On ne sait ni qui les accepte, ni si les refus sont rejoués.
    - L'environnement d'entraînement ne contient que le noyau, `observe` et l'encodeur. On ne voit pas comment il applique les mêmes limites et les mêmes codes de refus.
    - « Écrit avant d'être confirmé » : confirmé à qui ?
*   **Correction :**
    - Séparer en une phrase ce qui se vérifie à la réception (format, quota, sans dépendre de l'état) et ce qui se vérifie dans `step` (permissions, budget selon l'état).
    - Dire si les ordres refusés sont journalisés.
    - Faire figurer la partie partagée de la réception dans l'environnement d'entraînement.

### 3. Majeur : le déclencheur Rust est ambigu

*   **Où :** §2 (l. 178-180), NFR Performance (l. 429-433), ADR 0001 (l. 510).
*   **Problème :**
    - Le coût du réseau est « déduit » au §2 et « compris » dans les NFR.
    - On ne sait pas ce que vaut un « pas » : un tick ? pour combien d'agents ?
    - On ignore aussi combien de cœurs sont utilisés.
    - La phrase « 347 pas par seconde par nuit de 8 heures » (l. 510) est incompréhensible.
    - Au total, on ne peut pas dire si le déclencheur est atteint.
*   **Correction :**
    - Définir le « pas ».
    - Énoncer un seul seuil : débit total de bout en bout (simulation + inférence) sur N cœurs ≥ 347 pas/s (10 M / 28 800 s).
    - Expliquer comment on en déduit la mesure par cœur, et corriger la l. 510.

### 4. Majeur : les règles de promotion et de jalon ne disent pas sur quelle grandeur elles portent

*   **Où :** §8 (l. 259), objectif 7 (l. 55), CUJ 2 (l. 96), CUJ 6 (l. 123), M4 (l. 336).
*   **Problème :**
    - « Intervalle à 95 % au-dessus de zéro » et « bat l'agent scripté de 10 % » : on ne sait pas de quelle grandeur il s'agit.
    - « Verdict favorable » (CUJ 6) n'est pas relié à la règle de promotion.
    - « L'argent tiré des sources d'argent du jeu » est rapporté sans que le document dise pourquoi.
*   **Correction :**
    - Écrire « intervalle de la différence de [métrique du métier, définie au niveau 2] entre la nouvelle version et la précédente ».
    - Définir « verdict favorable = règle de promotion satisfaite ».
    - Expliquer en une phrase que l'argent tiré sert à repérer l'exploitation d'une faille.

### 5. Majeur : `CLAUDE.md` est présenté comme « la seule barrière », ce que le §10 contredit

*   **Où :** plan, point 2 (l. 480) ; §10 (l. 286-293, 325) ; CUJ 3 (l. 107).
*   **Problème :** la l. 480 dit « seule barrière », alors que le §10 décrit des règles `deny`, un hook et des contrôles obligatoires. Un agent qui lit `CLAUDE.md` en premier retiendra une image fausse.
*   **Correction :** « C'est la seule barrière que GitHub ne double pas. Les règles `deny` de `.claude/settings.json` et le hook local réduisent les erreurs, sans empêcher un contournement. »

### 6. Majeur : on ne sait pas de quel hook on parle

*   **Où :** §10 (l. 293, 325), ADR 0004 (l. 528), NFR (l. 425).
*   **Problème :**
    - Le hook est cité (« comme le hook… ») avant d'être présenté.
    - Deux hooks coexistent : le hook pre-commit `gitleaks` et le hook local de Claude Code. On ignore lequel « se contourne par un script », ce que fait le second, et où il est configuré.
*   **Correction :** présenter le hook Claude Code avant sa première mention (type, fichier, commandes bloquées), et toujours l'appeler « hook Claude Code », par opposition au « hook pre-commit ».

### 7. Majeur : une session neuve ne peut pas trouver le jalon en cours

*   **Où :** plan, point 2 (l. 487), vérification (l. 581), point 12 (l. 551-554).
*   **Problème :** l'ordre de lecture renvoie au « document de niveau 2 du jalon en cours », mais le statut des jalons vit dans `docs/feuille-de-route.md`, absent de cet ordre. Au moment du test, le document de niveau 2 de M0 n'existe pas encore.
*   **Correction :** ajouter la feuille de route à l'ordre de lecture, et dire quoi faire si le document de niveau 2 n'existe pas : s'arrêter et demander.

### 8. Majeur : le statut de ce fichier et des brouillons est confus

*   **Où :** plan, points 1, 14 et 15 (l. 471-474, 565-573).
*   **Problème :**
    - Le point 1 demande de « créer » le fichier même qu'on est en train de lire, et l'appelle « ce brouillon ».
    - On ne sait pas lequel, de ce fichier ou de `design_draft.md`, fait foi.
    - `concepts_brief.md` n'est jamais présenté.
*   **Correction :** écrire « (Modify) : ce fichier devient la version de référence », et présenter `design_draft.md` et `concepts_brief.md` en une phrase chacun, avec leur lien à la RFC.

### 9. Majeur : EGM et la vérification ne sont pas expliqués

*   **Où :** l. 474 (« étape 6 d'EGM »), l. 578 (`/egm:egm-review`), l. 579-581 (« compte rendu »).
*   **Problème :**
    - EGM n'est ni défini ni lié.
    - L'« étape 6 » ne correspond pas à l'étape 6 de la revue, qui est le test de compréhension.
    - On ne sait pas où se trouve le « compte rendu » ni qui l'écrit.
    - La commande de vérification des liens n'est pas donnée.
*   **Correction :** une phrase et un lien pour EGM, le bon intitulé d'étape, l'emplacement du compte rendu et la commande exacte de vérification des liens.

### 10. Majeur : l'unité à laquelle s'appliquent les limites n'est pas claire (acteur, personnage, joueur)

*   **Où :** §5 (l. 218-221), objectif 4 (l. 50).
*   **Problème :**
    - Les limites sont fixées « par personnage », l'observation « par acteur », l'égalité « entre joueurs ».
    - Un humain qui pilote plusieurs personnages a-t-il un budget par personnage ou par joueur ?
    - Un « hôte joueurs IA » (non défini) compte-t-il comme un seul client pour N acteurs ?
    - C'est pourtant ce qui garantit l'équité.
*   **Correction :** définir « acteur = personnage = l'unité qui a un budget, un `actor_id` et une observation », dire combien d'acteurs un joueur peut avoir, et définir « hôte ».

### 11. Majeur : on ne sait pas qui écrit les scénarios

*   **Où :** CUJ 3 (l. 101), plan, point 2 (l. 482-483), §10 (l. 302, 326).
*   **Problème :**
    - On ne sait pas qui écrit la pull request dédiée aux scénarios.
    - On ne sait pas si elle compte dans la règle « une seule pull request de fonctionnalité ouverte ».
    - La notion de « pull request de fonctionnalité » n'est pas définie.
*   **Correction :** décrire le flux en deux temps : d'abord une PR de scénarios, rédigée par l'agent et lue par le propriétaire, puis une PR de fonctionnalité. Définir les deux types de PR.

### 12. Mineur : la RFC est mal citée

*   **Où :** plan, point 13 (l. 559-561).
*   **Problème :** « décision 12 » est ambigu, car la RFC a deux listes numérotées. « Format des instantanés » et « emplacement de MLflow » ne figurent pas dans les « Points à vérifier » de la RFC, qui parle de « stockage par fichiers de MLflow 3.x ».
*   **Correction :** écrire « décision acquise n° 12 » et citer les intitulés exacts de la RFC.

### 13. Mineur : « carte » désigne deux choses

*   **Où :** l. 55, 92, 253 (« cartes d'évaluation ») ; l. 262, 336 (« capacité de la carte »).
*   **Correction :** écrire « carte graphique » partout où c'est le sens, ou « scénario d'évaluation » pour l'autre.

### 14. Mineur : plusieurs mots ont deux sens

*   **« Propriétaire » :** propriétaire d'une question (l. 545) et propriétaire du projet. Écrire « responsable » pour la question.
*   **« Phase » :** phases d'un tick et « observabilité de phase 1 ». Écrire « étape 1 de l'observabilité ».
*   **« K » :** quota d'ordres et seuil d'argent inactif. Utiliser deux lettres différentes.
*   **« Enveloppe » :** règles du gouvernement et enveloppe des événements. Écrire « bornes » pour le gouvernement.
*   **« Agent » :** « agent scripté » et « un agent apprendrait », contre la règle « un mot par sens ». Écrire « référence scriptée » ou « PNJ scripté », et « joueur IA ».

### 15. Mineur : des termes du projet sont employés sans définition

Termes concernés : « tranche 0 », « métier », « rang », « hôte », « empreintes de référence », `correlation_id`, « mode observation », « période de dépréciation », « verdict en une phrase » (son format). « EVE » n'est développé qu'à la l. 447, et on ne sait ni pourquoi son vocabulaire est interdit, ni où se trouve la liste des termes interdits, absente des chemins protégés.

*   **Correction :** une définition d'une ligne à la première occurrence de chacun, ou un mini-glossaire en tête du document.

### 16. Mineur : le schéma de §1 est trompeur

*   **Où :** l. 143-146.
*   **Problème :**
    - Les flèches font croire que le journal SQLite et les instantanés alimentent les fichiers Parquet.
    - `observe()` est dessiné entre la réception et le protocole, et non à côté du noyau.
    - On ne sait pas si « serveur » désigne le portable, y compris pour le serveur 24 h/24 de M5.
*   **Correction :** séparer les stockages, placer `observe` près du noyau, et dire où tournera le serveur persistant.

### 17. Mineur : des incohérences mineures

*   **Signature de `step` :** le troisième paramètre s'appelle `graine` (l. 43) puis `graine_du_monde` (l. 163).
*   **Événements « recalculables » (l. 205) :** ils ne le sont qu'avec le code de la même `rules_version`. Il faut le préciser, et `policy_id` et `policy_version` doivent alors figurer dans le journal des ordres.
*   **`CODEOWNERS` (l. 300) :** si le propriétaire est aussi l'auteur, GitHub ne lui demande rien. Seul le contrôle de garde signale les modifications.
*   **Mutation « au score qui ne peut pas baisser » (l. 313) :** préciser par rapport à quoi, a priori `main`.
