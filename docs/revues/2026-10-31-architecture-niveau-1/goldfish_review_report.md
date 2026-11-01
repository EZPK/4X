# Goldfish Annotated Review Report

Status: resolved (2026-10-31, « auto accept » : 62 corrections appliquées, 4 constats écartés, 1 mixte)

**Target:** `docs/designs/architecture-niveau-1.md` (lignes 1-459, partie spécification)

**Constats traités :** les 59 constats de l'étape 7 ([critic_report.md](./critic_report.md)), plus 8 constats des étapes 5 et 6 ([zoom_out_report.md](./zoom_out_report.md), [comprehension_report.md](./comprehension_report.md)) qui portent sur la même partie et qui reviendraient à l'étape 8 s'ils n'étaient pas traités maintenant. Les constats qui portent sur le plan d'implémentation (lignes 460 et suivantes) sont laissés à l'étape 9.

**Bilan des suggestions :** 67 constats, dont 62 PROPOSE FIX, 4 DECLINE, 1 mixte (n° 67), 0 CONTEST et 0 ESCALATE.

Trois corrections changent l'architecture et méritent votre attention avant d'accepter en bloc :
1. **M1 reçoit une version minimale du protocole, sans réseau** (Z-B1, C-1, Z-M8). Le client Textual parle au serveur par un appel de fonction dans le même processus dès M1. WebSocket n'arrive qu'en M3.
2. **Le déclencheur Rust est recalculé sur la base d'un verdict complet** (design-1-7). Un verdict demande 5 entraînements de 10 millions de pas, à faire tenir en une nuit, soit 1 736 pas par seconde au total (calculé : 50 000 000 / 28 800). Le seuil était de 347 pas par seconde.
3. **La visibilité est portée par les champs de l'état et par chaque événement entier** (design-1-11, Z-M9). Les événements qu'un joueur reçoit passent tous par `observe`.

---

## Prioritized Findings & AI Suggestions

### Bloquants (High)

#### [1] [`egm-design`] design-1-1 — on ne sait pas qui valide les ordres
*   **Affected Scope:** l. 43-50, 139-141, 184-186, 203, 250 (Goals, §1, §2, §3, §8)
*   **Discrepancy Description:** la réception filtre-t-elle les ordres hors du noyau, ou est-ce `step` ? Le journal ne contient que des ordres « acceptés », et l'entraînement n'a pas de réception.
*   **Rationale:** les objectifs 1, 2 et 4 deviennent faux ou ambigus.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide. Je l'avais laissée ambiguë.
*   ***Proposed Edit:***
    *   Location: §2 « Ordre d'un tick », §3 tableau, §1 schéma, §8.
    *   Change :
        - La réception ne fait que des contrôles **sans état** : format, taille, authentification, quota K d'ordres par acteur et par tick.
        - Tout contrôle qui dépend de l'état (permissions, budget d'actions, solde, position) se fait **dans `step`** et produit un code de refus.
        - Le journal contient **tous les ordres transmis à `step`**, y compris ceux qu'il refusera. Il est renommé « journal des ordres soumis ».
        - La validation sans état est une fonction du paquet `schema`, réutilisée par l'environnement d'entraînement.

#### [2] [`egm-design`] design-1-2 — la CI GitHub ne peut joindre ni MLflow, ni Parquet, ni le PC d'entraînement
*   **Affected Scope:** l. 54-55, 104, 119, 261, 266-267, 322-324, 427
*   **Discrepancy Description:** des preuves et la page d'accueil sont attribuées à la CI, alors que leurs données sont hors de sa portée. Rien n'interdit un runner auto-hébergé, qui exécuterait le code de pull requests d'un dépôt public sur le réseau local.
*   **Rationale:** les CUJ 2, 3 et 5 et les objectifs 6 à 8 reposent sur une chaîne de preuve impossible, et une faille de sécurité reste ouverte.
*   ***AI Suggestion:*** PROPOSE FIX (fusionné avec Z-M1)
*   ***Justification:*** critique valide, avec un risque de sécurité réel.
*   ***Proposed Edit:***
    *   Location: nouvelle sous-section §9bis « Où tourne quoi », §10 Preuves, CUJ 2 et 5.
    *   Change : un tableau « preuve → producteur → machine » :
        - **CI hébergée par GitHub :** scénarios, rejeu, métriques sur des parties générées à graine fixe et comparées à `main`, captures, vidéo rendue depuis un rejeu.
        - **Portable, tâche planifiée lancée depuis `main` :** page d'accueil réelle.
        - **PC d'entraînement, script lancé par le propriétaire depuis un commit de `main` :** verdicts. Le script publie en commentaire de la pull request le verdict, l'empreinte du commit et l'identifiant de l'exécution, mais jamais d'adresse du réseau local.

        Ajouter une règle : **aucun runner auto-hébergé sur ce dépôt.**

#### [3] [`egm-design` + `egm-structural`] design-1-3 — section « Risques et parades » absente
*   **Affected Scope:** tout le document
*   **Discrepancy Description:** la norme exige un inventaire des risques avec leurs parades. Plusieurs risques ne figurent nulle part.
*   **Rationale:** sans inventaire unique, des agents sans mémoire ne peuvent pas vérifier qu'un risque est traité.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide, la norme est explicite.
*   ***Proposed Edit:***
    *   Location: nouveau H2 « Risks & Mitigations », placé après les exigences non fonctionnelles.
    *   Change : un tableau « risque / effet / signal de détection / parade / jalon », d'environ 14 lignes :
        - journal SQLite corrompu ou disque plein ;
        - PC d'entraînement ou MLflow injoignable ;
        - divergence de rejeu découverte en production ;
        - migration ratée ;
        - fuite d'un champ caché par `observe` ;
        - joueur IA qui exploite un bug ;
        - mise à jour de Python ou de `msgspec` qui change les empreintes ;
        - temps de relecture du propriétaire comme goulot ;
        - injection de consignes dans les agents de code par du contenu du dépôt public (issues, pull requests externes) ;
        - affaiblissement des contrôles par l'agent (renvoi à design-1-15) ;
        - fusion par l'agent avec les identifiants du propriétaire (renvoi au §10) ;
        - vitesse insuffisante (renvoi au déclencheur Rust) ;
        - AI Act ;
        - runner auto-hébergé.

        Les risques déjà décrits ailleurs y figurent par un renvoi, sans être recopiés.

### Majeurs (Medium)

#### [4] [`egm-zoom-out`] Z-B1 + [`egm-design`] design-1-6 — « aucun client n'importe le noyau » contredit le rejeu et l'entraînement
*   **Affected Scope:** §1 (l. 135-159), §5 (l. 218), §8 (l. 250), §9 (l. 276), CUJ 4
*   **Discrepancy Description:** le client Textual en mode rejeu, l'outil de divergence, les PNJ en entraînement et l'encodeur commun violent ou contournent la règle.
*   **Rationale:** la frontière que le contrôle d'imports fera respecter est intenable telle qu'écrite.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide. Étape 5 (bloquant) et étape 7 (majeur) la relèvent toutes deux.
*   ***Proposed Edit:***
    *   Location: §1, nouveau tableau des paquets.
    *   Change :
        - « La même porte » est définie **au niveau des données** : un joueur, quel qu'il soit, est une fonction `observation -> ordres`, et le transport est secondaire.
        - Les paquets et les imports autorisés :

          | Paquet | Contenu | Peut importer |
          | :-- | :-- | :-- |
          | `core` | état, `step`, `observe`, registre | — |
          | `schema` | types d'ordre et d'observation, validation sans état, encodeur et décodeur | — |
          | `server` | boucle des ticks, transport, persistance | `core`, `schema` |
          | `clients` | client Textual, hôte des joueurs IA, PNJ scriptés | `schema` |
          | `training` | environnement d'entraînement | `core`, `schema`, `clients` (les politiques des PNJ) |
          | `tools` | rejeu, divergence | `core`, `schema` |

        - Le mode rejeu est un serveur de rejeu (`tools`) qui envoie des observations au client. Le client n'appelle jamais `step`.

#### [5] [`egm-zoom-out`] Z-M8 + [`egm-comprehension`] C-1 — M1 a besoin d'un client et d'événements qui arrivent en M2 et M3
*   **Affected Scope:** CUJ 1, §11 (l. 333-335), Goal 6
*   **Discrepancy Description:** le CUJ 1 fait jouer dans Textual en M1, mais le protocole arrive en M3. Le notebook de M1 doit lire des événements livrés en M2.
*   **Rationale:** M1 inventerait un format parallèle, ou violerait les règles.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide, relevée par deux étapes.
*   ***Proposed Edit:***
    *   Location: §11, CUJ 1, Goal 6.
    *   Change :
        - **M1** livre le protocole **en mémoire** (le client appelle le serveur dans le même processus, à travers `schema`), le client Textual minimal et un **schéma d'événements v0** jetable, lu par le notebook de M1.
        - **M2** stabilise les événements v1, Parquet et la page d'accueil.
        - **M3** ajoute le transport WebSocket et le parcours des « dix premières minutes ».

#### [6] [`egm-design`] design-1-4 — décalage d'un tick entre le direct et l'entraînement
*   **Affected Scope:** l. 186, 218, 250
*   **Discrepancy Description:** la latence et le report au tick suivant existent en direct, pas en entraînement.
*   **Rationale:** la politique entraînée se comporterait autrement en production, sans que rien ne le signale.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide.
*   ***Proposed Edit:***
    *   Location: §2, « Ordre d'un tick ».
    *   Change : une chronologie de référence.
        - Après le calcul du tick T, chaque acteur reçoit `observe` de l'état T.
        - Les ordres reçus avant le début du tick T+1 s'y appliquent.
        - Un ordre arrivé plus tard est reporté au tick suivant, pas refusé.
        - L'environnement d'entraînement applique l'action calculée sur T au tick T+1, et la reporte à T+2 selon une probabilité réglable, pour simuler la latence.

#### [7] [`egm-design`] design-1-5 — l'objectif 6 se contredit pour les métriques techniques, GitHub et MLflow
*   **Affected Scope:** l. 54, 115-119, 163, 275
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide : `step` n'a pas d'horloge.
*   ***Proposed Edit:***
    *   Change : l'objectif 6 ne porte plus que sur les métriques de **jeu et d'économie**. Les autres métriques ont leurs propres sources, nommées :
        - **télémétrie technique :** un flux séparé, non déterministe, hors du noyau et hors des empreintes ;
        - **entraînement :** MLflow ;
        - **avancement :** API GitHub.

#### [8] [`egm-design` + `egm-style` + `egm-comprehension`] design-1-7 — le déclencheur Rust est mal défini
*   **Affected Scope:** l. 178-179, 254, 429-433, 510
*   ***AI Suggestion:*** PROPOSE FIX (fusionné avec Z-N7 et C-3)
*   ***Justification:*** critique valide. Les deux définitions divergent déjà.
*   ***Proposed Edit:***
    *   Location: §2 (seule définition) ; les exigences non fonctionnelles et l'alternative C y renvoient.
    *   Change :
        - **« Pas » =** un appel à l'environnement, c'est-à-dire un tick pour tous les acteurs du scénario.
        - **Mesure =** le débit de bout en bout (simulation, inférence et apprentissage), sur le PC d'entraînement, tous cœurs utilisés.
        - **Seuil =** un verdict (5 entraînements de 10 millions de pas) doit tenir en une nuit de 8 heures, soit **1 736 pas par seconde** au total (calculé avec un outil : 50 000 000 / 28 800).
        - La mention « par cœur » et le mot « (calculé) » sont retirés.
        - **Second déclencheur :** le p99 de la durée du tick en direct dépasse sa période.

#### [9] [`egm-design`] design-1-8 — le banc d'essai ne mesure pas la représentation retenue
*   **Affected Scope:** l. 165-176, 346-348
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique en partie valide. Le banc A utilisait bien des `msgspec.Struct` figés avec `structs.replace`. Mais il **reconstruisait toute la table à chaque tick**, avec tous les vaisseaux modifiés, et ne testait ni la copie partielle ni le traitement de copies en bloc. Le document doit le dire.
*   ***Proposed Edit:***
    *   Change :
        - Décrire exactement le banc : Structs figés, toute la table reconstruite à chaque tick, chaque entité modifiée à chaque tick.
        - Préciser la stratégie de copie retenue : une nouvelle table par phase, et non une copie par modification.
        - Reformuler le rejet de l'alternative A : reconnaître que le traitement de nombreuses copies en bloc favorise les tableaux, puis expliquer pourquoi on l'écarte quand même (lisibilité pour des agents sans mémoire, Rust en recours, mesure refaite à M1 et M4).

#### [10] [`egm-design`] design-1-9 — le contrôle des 64 bits ne couvre que deux fonctions
*   ***AI Suggestion:*** PROPOSE FIX (fusionné avec Z-N3)
*   ***Proposed Edit:*** ajouter un invariant, vérifié en test à chaque tick et à l'encodage : tout champ entier de l'état tient dans un entier signé de 64 bits. La justification devient les formats de stockage (MessagePack, Parquet), et non Rust.

#### [11] [`egm-design`] design-1-10 — l'invariant de l'argent est vide ou ambigu, et celui des biens manque
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide. En partie double, la somme de tous les comptes vaut toujours zéro.
*   ***Proposed Edit:***
    *   Location: §4, Goal 3.
    *   Change : trois invariants.
        - (a) Somme de tous les comptes = 0.
        - (b) Masse monétaire, c'est-à-dire la somme des comptes de portefeuille, de corporation et de séquestre, = valeur précédente + émission − destruction.
        - (c) Conservation des biens : aucune quantité négative, et le minerai extrait = le minerai stocké + transporté + vendu.

        Une seule paire de mots, « émission / destruction », est définie ici et reprise partout (style-1-4).

#### [12] [`egm-design`] design-1-11 + [`egm-zoom-out`] Z-M9 — la visibilité est incohérente et ne couvre pas l'état
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide. Les deux relecteurs proposent des solutions opposées (par champ, par événement). Ma proposition retient de chacun la partie qui tient.
*   ***Proposed Edit:***
    *   Change :
        - **Chaque champ de l'état** porte une classe de visibilité. C'est ce que lit `observe`, et ce que vérifient les tests.
        - **Chaque événement** porte une seule classe. Un fait mi-public, mi-privé est découpé en deux événements.
        - Les événements qu'un acteur reçoit lui parviennent **par `observe`** (état visible et événements visibles du dernier tick). Il n'y a pas de second canal.

#### [13] [`egm-design`] design-1-12 — les entrées qui ne sont pas des ordres ne sont pas journalisées
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** toute entrée qui modifie l'état est un **ordre journalisé**, de catégorie joueur, système ou administration. Exemples : déconnexion, arrêt d'urgence, création de personnage, passage en mode observation. Le serveur ne modifie jamais l'état autrement que par `step`.

#### [14] [`egm-design`] design-1-13 — cohérence journal / instantanés / Parquet après plantage
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:***
    - Le journal fait foi. Les événements non publiés sont régénérés par rejeu au redémarrage.
    - Les segments Parquet sont écrits sous un nom temporaire, puis renommés d'un coup.
    - SQLite tourne en `synchronous=FULL` à partir de M5.
    - Un instantané est pris tous les N ticks. N est fixé au niveau 2 de M5, avec comme objectif une reprise en moins d'une minute.

#### [15] [`egm-design`] design-1-14 — le journal n'a pas de version et `rules_version` est mal défini
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:***
    - Ajouter une ligne au tableau des versions : `order_log_schema_version`.
    - `rules_version` = un numéro de révision des règles, tenu à la main, + l'empreinte de `tunables.toml`. Un contrôle CI exige une hausse de ce numéro dès que les empreintes de référence changent.
    - L'empreinte du commit est enregistrée à côté de chaque instantané.

#### [16] [`egm-zoom-out`] Z-M3 — toute la mécanique de migration est imposée avant qu'il existe des données
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** critique valide. Avant M5, toutes les données sont jetables.
*   ***Proposed Edit:***
    - Les numéros de version sont présents **dès M1**.
    - **Avant M5,** un changement incompatible se traite par une montée de version et une régénération des données (rejeu).
    - Les migrations testées, la conversion des anciens événements et la dépréciation du protocole arrivent **avec M5**.
    - La période de dépréciation du protocole est retirée tant que les clients tiers restent hors périmètre (Z-N6).

#### [17] [`egm-design`] design-1-15 — les chemins protégés reposent sur une lecture que le propriétaire ne peut pas faire
*   ***AI Suggestion:*** PROPOSE FIX (fusionné avec Z-M6)
*   ***Proposed Edit:*** trois parades nommées, et le reste assumé comme risque.
    - (a) **Une suite « canari » vit sur `main` et tourne chaque nuit :** des bugs volontaires que les contrôles doivent toujours attraper. Si une modification fusionnée a affaibli les contrôles, la nuit passe au rouge.
    - (b) **Toute pull request qui touche un chemin protégé reçoit une revue EGM sans contexte,** avec un résumé en français que le propriétaire lit.
    - (c) **Pour les définitions d'étapes,** la CI prouve que chaque étape échoue quand on casse le comportement visé (mutation ciblée).

    Le risque résiduel figure dans la section Risques.

#### [18] [`egm-design` + `egm-structural`] design-1-16 — un administrateur peut contourner la protection de branche
*   ***AI Suggestion:*** PROPOSE FIX (fusionné avec Z-M5)
*   ***Proposed Edit:***
    - Les règles de `main` s'appliquent aussi aux administrateurs : option « ne pas autoriser le contournement », ou ensemble de règles (ruleset) avec une liste de contournement vide.
    - Les interdictions de Claude Code couvrent aussi `gh pr merge --admin` et tout appel qui modifie ces réglages.
    - Le critère de M0 inclut une tentative de fusion d'une pull request rouge en tant qu'administrateur, qui doit échouer.

#### [19] [`egm-design`] design-1-17 + [`egm-comprehension`] C-10 — identité des acteurs, authentification, machine du serveur
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:***
    - **Acteur =** personnage = l'unité qui a un `actor_id`, un budget et une observation. Un compte = un personnage.
    - **Un opérateur** (la personne responsable de comptes) a un plafond de comptes. Il est réglable, et vaut 1 pour un humain.
    - **`actor_kind`** est attribué par le serveur à la création du compte, jamais déclaré par le client.
    - **`policy_id` et `policy_version`** voyagent dans l'ordre et sont journalisés.
    - **Authentification minimale :** un jeton par compte, identique pour le client Textual et pour l'hôte des joueurs IA.
    - **Hôte des joueurs IA :** un processus client qui fait jouer plusieurs comptes de joueurs IA, chacun avec son propre budget.
    - **La machine du serveur persistant** (portable, PC d'entraînement ou VPS) devient une question ouverte, à trancher avant le niveau 2 de M5.

#### [20] [`egm-structural`] structural-1-1 — « Additional Resources » et « Future Improvements » mal imbriqués
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** les passer en H2.

#### [21] [`egm-style`] style-1-1 — des critères de jalon ne sont pas mesurables
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:***
    - La l. 57 devient « mesurable, ou validé explicitement par le propriétaire ».
    - « Amusante » devient « le propriétaire valide la boucle (validation subjective assumée) ».
    - « Stables » devient « la masse monétaire et l'indice de prix restent dans une fourchette fixée au niveau 2 de M1, sur 100 000 ticks ».
    - La capacité de la carte graphique devient « mémoire maximale et débit d'inférence mesurés ».
    - « De bout en bout » est remplacé par un scénario nommé, écrit au niveau 2 de M6.

#### [22] [`egm-style`] style-1-2 + [`egm-comprehension`] C-4 — promotion et M4 sans métrique nommée
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:***
    - La règle porte sur la **métrique du métier**, définie au niveau 2 de M4 (pour le mineur : la valeur nette de minerai livré pour 1 000 ticks, à prix de référence).
    - **Promotion :** l'intervalle à 95 % de la différence entre la nouvelle version et l'ancienne, mesurée sur les scénarios d'évaluation, a une borne basse au-dessus de zéro.
    - « Aucune anomalie » devient « invariants respectés, et émission au profit du joueur IA sous un seuil défini au niveau 2 ». Ce seuil sert à repérer l'exploitation de failles.
    - **Verdict favorable =** règle de promotion satisfaite.

#### [23] [`egm-style`] style-1-3 — « agent » a plusieurs sens
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** « agent » est réservé à « agent de code ». Ailleurs, on écrit « joueur IA », « référence scriptée » (qui est un PNJ scripté) et « client tiers ».

#### [24] [`egm-style`] style-1-4 — plusieurs mots pour les flux d'argent
*   ***AI Suggestion:*** PROPOSE FIX (traité avec [11])

#### [25] [`egm-style`] style-1-5 — le choix des identifiants GitHub est expliqué sept fois
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** une seule explication complète en §10. Ailleurs, un renvoi d'une ligne.

#### [26] [`egm-style`] style-1-6 — l'objectif 8 mélange un contrôle et une règle de travail
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** l'objectif 8 ne garde que ce que la CI et les hooks vérifient. La règle de fusion part en §10, et le texte renvoie à « §10 » au lieu de « ici ».

#### [27] [`egm-style`] style-1-7 — des verbes promettent plus que les outils
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** « prouvent » devient « vérifient sur des cas générés ». « Interdit tout autre chemin » devient « interdit d'importer le noyau hors des paquets autorisés ». « Se prouve » devient « se mesure statistiquement ».

#### [28] [`egm-style`] style-1-8 — statuts et disjoncteur sans critère
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:***
    - Forme de la règle : **rouge** si un invariant est violé ou un contrôle obligatoire échoue, **orange** si une métrique sort de sa fourchette.
    - Les seuils sont fixés au niveau 2 de M2 (statuts) et de M5 (disjoncteur).

#### [29] [`egm-zoom-out`] Z-M4 — les chemins protégés oublient les fichiers qui gouvernent l'agent
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** ajouter à la liste `CLAUDE.md`, `.claude/`, `docs/designs/`, `docs/adr/`, la référence du score de mutation et la liste des termes interdits.

#### [30] [`egm-zoom-out`] Z-M7 — rien ne dit à quel jalon chaque contrôle devient obligatoire
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** un tableau « contrôle → jalon » :

    | Jalon | Contrôles obligatoires |
    | :-- | :-- |
    | M0 | linter, typage, `gitleaks`, contrôle de garde, termes interdits |
    | M1 | rejeu, tests de propriétés, contrôle d'imports, mutation, canari |
    | M2 | panneau de métriques |
    | M3 | captures et vidéo |
    | M4 | verdicts d'entraînement |

#### [31] [`egm-zoom-out`] Z-M10 — PPO écrit à la main en plus de Stable-Baselines3
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** le niveau 1 ne fixe que l'interface (`ParallelEnv` qui enveloppe `step`, `observe`, l'encodeur et le décodeur) et la règle « réutiliser d'abord ». Le choix d'une implémentation unique, justifiée, se fait au niveau 2 de M4. PufferLib passe dans les questions ouvertes (style-1-20).

#### [32] [`egm-comprehension`] C-2 — on ne sait pas où les ordres sont validés
*   ***AI Suggestion:*** PROPOSE FIX (traité avec [1])

#### [33] [`egm-comprehension`] C-11 — on ne sait pas qui écrit les scénarios
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** deux types de pull request, définis en §10.
    - La **PR de scénarios** est rédigée par l'agent de code. Le propriétaire lit les scénarios en français, puis la fusionne.
    - La **PR de fonctionnalité** vient ensuite, et ne touche aucun chemin protégé.

    Une seule PR de fonctionnalité peut être ouverte à la fois.

#### [34] [`egm-comprehension`] C-6 + [`egm-style`] style-1-21 — on ne sait pas de quel hook on parle
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Proposed Edit:*** présenter le « hook Claude Code » (un hook `PreToolUse`, configuré dans `.claude/settings.json`) avant sa première mention, et le distinguer partout du « hook pre-commit » (`gitleaks`).

### Mineurs (Low)

| # | Constat | Suggestion | Correction proposée |
| :-- | :-- | :-- | :-- |
| 35 | design-1-18 : `//`, `%` et `float` | PROPOSE FIX | Garder au niveau 1 l'invariant (« aucun flottant, aucune division ni modulo natifs, aucun module non déterministe dans le noyau, vérifié mécaniquement ») et renvoyer les outils (TID251, test d'arbre syntaxique) au niveau 2 de M1. Fusionné avec Z-N4. |
| 36 | design-1-19 : « il ne connaît que des entiers » | PROPOSE FIX | « Toutes les grandeurs numériques sont des entiers. » |
| 37 | design-1-20 : tirage borné à partir de BLAKE2b | PROPOSE FIX | « Méthode par rejet, fixée au niveau 2 de M1. » |
| 38 | design-1-21 : fréquence et encodage des empreintes | PROPOSE FIX | Les empreintes sont calculées sur un encodage canonique propre au projet, indépendant de la version de `msgspec`. Chaque tick en CI, tous les N ticks en production (fixé à M5). |
| 39 | design-1-22 : ordres au-delà de K | PROPOSE FIX | Chaque ordre porte un numéro d'ordre choisi par l'acteur. On garde les K premiers numéros, ce qui ne dépend pas de l'heure d'arrivée. La règle de la RFC « un serveur en retard ralentit le temps du jeu » est reprise. |
| 40 | design-1-23 : conversion à la lecture contre DuckDB | PROPOSE FIX | Avant M5 : régénération par rejeu. À partir de M5 : des vues DuckDB par version. |
| 41 | design-1-24 : 1 Go par jour sans estimation | PROPOSE FIX | Devient un budget à mesurer au niveau 2 de M2, avec une politique de conservation du journal et des instantanés. |
| 42 | design-1-25 : graine secrète dans les instantanés | PROPOSE FIX | Le journal et les instantanés du monde en ligne ne sont jamais publiés. L'historique public vient seulement des événements de classe « public ». |
| 43 | design-1-26 : décodeur et référence de mutation | PROPOSE FIX | Citer le décodeur à côté de l'encodeur. Placer la référence de mutation dans un chemin protégé (voir [29]). |
| 44 | structural-1-2 : schéma ASCII | PROPOSE FIX | Redessiner : une boîte par stockage, `observe` près du noyau, les paquets du tableau [4]. |
| 45 | structural-1-3 : renvois sans lien | PROPOSE FIX | Ancres Markdown. |
| 46 | structural-1-4 : références sans URL | PROPOSE FIX | Liens vérifiés pendant le brainstorm pour SpaceMolt, Golemreach et le rapport économique d'EVE ; « à sourcer » pour les autres. |
| 47 | structural-1-5 : « Raison du rejet » décrit le choix retenu | PROPOSE FIX | « Parce que … », puis « Retenu : … ». |
| 48 | structural-1-6 : choix sans alternative | PROPOSE FIX | Une ligne chacun pour Parquet, le générateur à clé, `ParallelEnv` et la copie par phase. |
| 49 | structural-1-7 : phrase de cadrage des alternatives inexacte | PROPOSE FIX | Reprendre « argent en flottants » et « interface web dès le départ ». |
| 50 | structural-1-8 : mise en forme des listes | DECLINE | Cosmétique. Le document sera remis en forme lors de la réécriture. |
| 51 | structural-1-9 : traits horizontaux | DECLINE | Viennent du gabarit EGM, sans effet sur le sens. |
| 52 | structural-1-10 : langues mélangées dans les titres | PROPOSE FIX | Une phrase en tête : « Les titres de niveau 2 et les termes Given/When/Then suivent le gabarit EGM, en anglais, pour que les outils de revue s'y retrouvent. » |
| 53 | structural-1-11 : place des questions ouvertes ; jalon des CUJ | PROPOSE FIX (en partie) | Indiquer le jalon de chaque CUJ. Laisser les questions ouvertes à la place que leur donne le gabarit EGM, juste après les non-objectifs. |
| 54 | style-1-9 : formulations certaines | PROPOSE FIX | « risque d'utiliser… », « risque d'être réimplémenté… ». |
| 55 | style-1-10 : quantités floues | DECLINE | Les ordres de grandeur apparaissent plus loin dans le document (scénarios, verdict). |
| 56 | style-1-11 : signature de `step` | PROPOSE FIX | Une seule forme : `step(state, orders, world_seed, tunables) -> (state, events)`, identifiants en anglais selon la convention de langue. |
| 57 | style-1-12 : « jouet » | PROPOSE FIX | « banc d'essai simplifié », traité avec [9]. |
| 58 | style-1-13 : « nettement » | PROPOSE FIX | Supprimé. |
| 59 | style-1-14 : « plus tôt que prévu » | PROPOSE FIX | « La mesure démarre à M1. » |
| 60 | style-1-15 : termes non définis (N, K, rang, `correlation_id`, personnage) | PROPOSE FIX | `K_ordres` et `T_inactif` à la place des deux K. « Rang » renvoie au glossaire. `correlation_id` est retiré. « Personnage » est défini avec [19]. |
| 61 | style-1-16 : Parquet « en lecture seule » | PROPOSE FIX | « ajoutés par le serveur, lus par DuckDB ». |
| 62 | style-1-17 : contenus répétés | PROPOSE FIX | Une seule occurrence, et des renvois. |
| 63 | style-1-18 : « récent », « confiance », « lecture explicite » | PROPOSE FIX | « récent » = depuis le dernier instantané. « Confiance » : la condition de retour au compte séparé devient « dès qu'un contrôle canari ou une revue détecte un contournement ». « Lecture explicite » est remplacée par [17]. |
| 64 | style-1-19 : jugements subjectifs | DECLINE | Les jugements restants sont étayés par les chiffres du banc d'essai ou par la RFC. |
| 65 | style-1-20 : PufferLib caché dans le plan | PROPOSE FIX | Ajouté aux questions ouvertes (maintenance, compatibilité avec PettingZoo). |
| 66 | style-1-22 : libellés de domaines différents | PROPOSE FIX | « avancement du projet » partout. |
| 67 | Z-N1 : `CODEOWNERS` et hook redondants | DECLINE (en partie) | `CODEOWNERS` est retiré : il n'a aucun effet quand l'auteur est le propriétaire. Le hook Claude Code est gardé : il couvre des commandes que les règles `deny` ne savent pas filtrer (scripts). |

Constats laissés sans suite (DECLINE) : 50, 51, 55, 64, et 67 pour sa partie hook.

Constats renvoyés à l'étape 9, car ils portent sur le plan d'implémentation : Z-M2 (ADR recopiées), Z-N2/C-5 (« seule barrière »), Z-N8/C-8 (statut des fichiers), C-7 (jalon en cours), C-9 (EGM non expliqué), C-12.
