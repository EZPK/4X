# Rapport de revue — Étape 5 (Zoom Out initial)

*   **Document revu :** [architecture-niveau-1.md](./docs/designs/architecture-niveau-1.md), lignes 1 à 581
*   **Standard appliqué :** zoom-out-standard (EGM)
*   **Relecteur :** egm-zoom-out, sans contexte de la conversation
*   **Date :** 2026-10-31
*   **Verdict :** à reprendre. 1 bloquant, 10 majeurs, 8 mineurs.

Le relecteur a lu le document, la RFC liée, son persona et le standard. Comme il n'y a pas encore de code, la recherche de réutilisation n'a porté que sur les bibliothèques externes. Il juge l'objectif et la motivation clairs.

---

## Bloquant

### B1. « Aucun client n'importe le noyau » contredit plusieurs usages prévus

*   **Où :** plan technique §1 (l. 141, 159), §5 (l. 218), §8 (l. 250), §9 (l. 276), CUJ 4.
*   **Problème :** plusieurs usages prévus par le document violent cette règle.
    - Le client Textual sert aussi de visualiseur de rejeu et porte l'outil de divergence. Rejouer et comparer des empreintes exige d'appeler `step`, donc d'importer le noyau.
    - L'entraînement a besoin de l'agent scripté et des PNJ dans le même processus que `step`, sans réseau. Or la l. 141 les définit comme des clients WebSocket.
    - L'encodeur commun sert à la fois à l'entraînement, qui importe le noyau, et à l'hôte IA en direct, qui ne doit pas l'importer. Son emplacement n'est pas défini.
*   **Pourquoi c'est grave :** c'est la frontière que tous les documents de niveau 2 devront respecter, et un contrôle automatique la fera appliquer. Telle qu'elle est écrite, M3, M4 et l'outil de divergence la violent forcément. Les agents de code contourneront le contrôle ou inventeront chacun leur solution.
*   **Correction proposée :**
    - Définir « la même porte » au niveau des données, pas du transport : un joueur est une fonction `observation -> ordres`, et WebSocket n'est qu'un moyen de la faire circuler.
    - Écrire les couches de paquets et les contrats d'imports :
      - `core` : état, `step`, `observe`, registre ;
      - `schema` : types d'observation et d'ordre, encodeur, sans import du noyau ;
      - `server` ;
      - `clients` : n'importent que `schema` ;
      - `tools/replay` : autorisé à importer `core`.
    - Le rejeu est servi par un processus qui fait tourner le noyau et envoie des observations au client.

---

## Majeurs

### M1. La frontière entre la CI de GitHub et le réseau local n'est pas définie

*   **Où :** Goals 6 et 7, §8 (l. 261), §9 (l. 267), §10 Preuves (l. 319-324), NFR Sécurité, jalon M2.
*   **Problème :**
    - La page d'accueil est « générée par la CI », mais les fichiers Parquet restent sur le portable.
    - La preuve d'entraînement est un lien MLflow, injoignable depuis GitHub, et l'entraînement ne tourne pas en CI. Pour cette preuve, aucun producteur autre que l'agent n'existe donc.
    - La page d'accueil de M2 doit afficher des domaines qui n'existent qu'à M4 (joueurs IA) ou à M5 (durée du tick).
*   **Correction proposée :**
    - Un paragraphe « où tourne quoi » :
      - la CI ne calcule que sur des simulations qu'elle lance elle-même ;
      - la page d'accueil réelle est générée sur le portable ;
      - les preuves d'entraînement sont publiées depuis le PC d'entraînement par un script du propriétaire ou un runner auto-hébergé.
    - Indiquer quels domaines de la page d'accueil existent à chaque jalon.
    - Ne jamais publier l'adresse MLflow du réseau local dans une pull request publique.

### M2. La documentation à créer recopie le document lui-même

*   **Où :** plan d'implémentation (ADR 0001 à 0006, `questions-ouvertes.md`, `feuille-de-route.md`), Goal 9, §7, NFR.
*   **Problème :** plusieurs informations seraient recopiées à plusieurs endroits.
    - Les six ADR recopient des décisions déjà écrites dans ce document.
    - Le registre des questions recopie la section Open Questions.
    - La feuille de route existerait en trois copies : §11, le fichier, et les jalons GitHub.
    - La procédure de mise à jour figure déjà deux fois, et l'ADR 0006 en ferait une troisième.
*   **Pourquoi c'est grave :** des copies multiples, maintenues par des agents sans mémoire, sont le terrain des versions divergentes que le document veut empêcher.
*   **Correction proposée :**
    - Garder ce document comme seule source des décisions existantes.
    - Créer le dossier ADR avec seulement son modèle, pour les décisions futures.
    - Tenir la feuille de route à un seul endroit.
    - Ne décrire la procédure de mise à jour qu'une fois.

### M3. Toute la mécanique de migration est imposée avant qu'il existe des données à migrer

*   **Où :** The Problem, Goal 5, §3, §6, §7, jalon M5.
*   **Problème :**
    - Le monde n'est en ligne qu'à M5, et avant, toutes les données sont jetables.
    - Les événements sont recalculables : on peut les régénérer par rejeu au lieu de les convertir.
    - L'écriture de l'ordre avant confirmation et SQLite en mode WAL servent la reprise d'un serveur en direct, pas le rejeu hors ligne de M1.
*   **Correction proposée :**
    - Garder dès le départ les numéros de version, qui coûtent peu.
    - Écrire qu'avant M5, un changement incompatible se traite par une montée de version et une régénération des données.
    - Les migrations testées, la conversion à la lecture et la dépréciation du protocole arrivent avec M5.

### M4. Les chemins protégés oublient les fichiers qui gouvernent l'agent lui-même

*   **Où :** §10, chemins protégés, interdictions, et `CLAUDE.md`.
*   **Problème :** la liste ne contient ni `CLAUDE.md`, ni `.claude/` (règles `deny`, hook), ni `docs/designs/`, ni `docs/adr/`. Une pull request de fonctionnalité pourrait affaiblir les règles de l'agent ou réécrire l'architecture sans que le contrôle de garde réagisse.
*   **Correction proposée :** ajouter ces quatre chemins à la liste et au critère de sortie de M0.

### M5. La protection de branche ne dit pas qu'elle s'applique à l'administrateur

*   **Où :** §10, Goal 8, critère de M0.
*   **Problème :** l'agent utilise les identifiants du propriétaire, qui est administrateur. Sans l'option « ne pas autoriser le contournement », un administrateur peut fusionner une pull request rouge (`gh pr merge --admin` ou interface). La RFC le prévoyait, le document l'a perdu.
*   **Correction proposée :** écrire « appliquée aux administrateurs, aucun acteur de contournement ». Le test de sortie de M0 doit inclure une tentative de fusion d'une pull request rouge en tant qu'administrateur.

### M6. Les définitions d'étapes : le problème racine de la RFC est étiqueté, pas résolu

*   **Où :** CUJ 3, §10, `CLAUDE.md`. Voir RFC §4.
*   **Problème :** ce sont les définitions d'étapes qui décident de ce qu'un scénario vérifie. Le document les fait changer par une pull request écrite par l'agent et fusionnée par un propriétaire qui ne lit pas le code. L'étiquette signale le changement, mais personne n'est en mesure de le juger.
*   **Correction proposée :** soit déclarer ce point comme un risque accepté, soit nommer le contrôle qui remplace la lecture du propriétaire. Par exemple, une revue sans contexte obligatoire pour ces fichiers, ou une preuve en CI que chaque étape échoue quand on casse le comportement visé (mutation ciblée).

### M7. Rien ne dit à quel jalon chaque contrôle CI devient obligatoire

*   **Où :** §10, contrôles obligatoires et preuves, critère de M0.
*   **Problème :** beaucoup de contrôles n'ont pas d'objet avant M1 (rejeu, mutation) ou M3 (captures, vidéo). Le niveau 2 de M0 risque de construire tout l'outillage de preuve avant la première règle du jeu.
*   **Correction proposée :** un tableau « contrôle → jalon où il devient obligatoire » :

    | Jalon | Contrôles |
    | :-- | :-- |
    | M0 | linter, typage, `gitleaks`, garde, termes interdits |
    | M1 | rejeu, tests de propriétés, contrôle d'imports, mutation |
    | M2 | panneau de métriques |
    | M3 | captures et vidéo |
    | M4 | preuves d'entraînement |

### M8. M1 a besoin d'événements et de notebooks qui n'arrivent qu'à M2

*   **Où :** §11, Goal 6.
*   **Problème :** le critère de M1 exige un notebook de métriques économiques. Le Goal 6 impose que toute métrique vienne des événements, mais le schéma d'événements arrive à M2. M1 devrait donc inventer un format provisoire ou lire le registre directement, ce qui contredit le Goal 6.
*   **Correction proposée :** soit déplacer un schéma d'événements minimal (v0, jetable) dans M1, soit exempter explicitement le notebook de M1 du Goal 6 jusqu'à M2.

### M9. Visibilité par champ ou par événement : le document dit les deux

*   **Où :** §5 (l. 219) contre §6 (l. 231).
*   **Problème :** §5 parle d'une visibilité par champ, alors que l'enveloppe de §6 la porte au niveau de l'événement. Ce sont deux complexités très différentes.
*   **Correction proposée :** visibilité par événement. Un fait mi-public mi-privé est découpé en deux événements.

### M10. PPO écrit à la main en plus de Stable-Baselines3, sans justification

*   **Où :** §8, algorithme.
*   **Problème :** deux implémentations du même algorithme sont à maintenir, et le choix d'une bibliothèque n'a pas sa place au niveau 1.
*   **Correction proposée :** au niveau 1, fixer seulement l'interface (`ParallelEnv`) et la règle « réutiliser d'abord ». Le choix d'une implémentation unique, justifiée, se fait au niveau 2 de M4.

---

## Mineurs

*   **N1. Garde-fous redondants ou sans effet :**
    - `CODEOWNERS` ne fait rien quand l'auteur des pull requests est le propriétaire lui-même ;
    - le hook local fait double emploi avec les règles `deny`.

    Il faut les supprimer, ou dire ce qu'ils apportent.
*   **N2. « C'est la seule barrière » (l. 480) est inexact.** Les règles `deny` et la protection de branche existent aussi. Reformuler en « règle de travail, doublée par les interdictions de permissions ».
*   **N3. La borne de 64 bits est justifiée par Rust, qui est un non-objectif.** La justifier plutôt par les formats de stockage (MessagePack, Parquet).
*   **N4. Des détails d'outillage relèvent du niveau 2** (`div_floor`, TID251, chemins `gh api`). De plus, TID251 ne peut pas interdire `float`, qui est un builtin. Garder l'invariant, renvoyer les outils au niveau 2.
*   **N5. `correlation_id` n'est pas défini, et `event_id` double peut-être (`tick`, `seq`).** Il faut les définir ou les retirer.
*   **N6. Réservations inutiles :** comptes assurance et banque réservés, dépréciation du protocole. Les retirer.
*   **N7. Le déclencheur Rust est mesuré de deux façons différentes** (« coût du réseau déduit » au §2, « compris » dans les NFR). Fixer une seule mesure : étapes d'environnement par seconde, de bout en bout, sur le PC d'entraînement, tous cœurs utilisés.
*   **N8. Incohérences du plan d'implémentation :**
    - le document cible est marqué « Create » alors qu'il existe déjà ;
    - la note de renvoi dans la RFC doit aussi mentionner l'exception administrateur (M5) et l'abandon du portage Rust comme contrainte (N3).
