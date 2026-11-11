# Glossaire

**Convention de langue (révisable par le propriétaire).**
- En français : documents, scénarios, messages destinés au propriétaire, titres et descriptions de pull request, messages de commit.
- En anglais : identifiants du code (paquets, classes, fonctions, champs d'événements) et commentaires du code.
- Le glossaire fait la correspondance entre les deux.

Chaque définition reprend ou résume la phrase qui définit le terme, dans le [document de niveau 1](designs/architecture-niveau-1.md) ou dans le document de niveau 2 qui introduit le terme. En cas d'écart, le document de niveau 1 fait foi.

**Colonne « identifiant du code »** : l'identifiant fixé par le document de niveau 1, ou par un document de niveau 2, s'il en fixe un, sinon « à fixer au niveau 2 de Mx », sinon « — » (pas d'identifiant de code). Ce glossaire n'invente aucun identifiant ni aucune valeur. Un nom marqué « nom provisoire » ne s'emploie pas dans le code avant que le niveau 2 indiqué ait fixé le nom définitif.

## Acteurs

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| humain | — | Joueur humain, l'une des valeurs de `actor_kind` (humain, joueur IA, PNJ). | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité) |
| joueur IA | — | Personnage du jeu piloté par un réseau de neurones entraîné. | [Overview](designs/architecture-niveau-1.md#overview) |
| PNJ | — | Personnage piloté par un script. | [Overview](designs/architecture-niveau-1.md#overview) |
| référence scriptée | `scripted_miner` (`policy_id`) | PNJ scripté qui sert de point de comparaison pour l'entraînement. | [Overview](designs/architecture-niveau-1.md#overview), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| agent de code | — | L'IA qui écrit le code du projet. Le mot « agent » seul ne désigne que l'agent de code. | [Overview](designs/architecture-niveau-1.md#overview) |
| client tiers | — | Client logiciel écrit par d'autres que le projet. Hors périmètre : le protocole le rend possible, mais rien n'est construit pour lui. | [Non-Goals](designs/architecture-niveau-1.md#non-goals) |
| acteur (= personnage) | `actor_id` | L'unité qui a un `actor_id`, un budget d'actions et une observation. Un compte = un personnage. | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité) |
| compte | à fixer au niveau 2 de M3 | Un compte = un personnage. Il est authentifié par un jeton. | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité) |
| opérateur | à fixer au niveau 2 de M3 | La personne responsable de comptes. Elle a un plafond de comptes, réglable (valeur : voir §5). | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité) |
| type d'acteur | `actor_kind`, de type `ActorKind` : `HUMAN`, `AI_PLAYER`, `NPC` | Humain, joueur IA ou PNJ. Attribué par le serveur à la création du compte, jamais déclaré par le client. N'influe jamais sur les règles. | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| hôte des joueurs IA | à fixer au niveau 2 de M4 | Processus client qui fait jouer plusieurs comptes de joueurs IA. Chaque compte garde son propre budget et sa propre observation. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| hôte des PNJ | `NpcHost` | Processus client qui fait jouer les PNJ. Il fait partie du paquet `clients`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| corporation | à fixer au niveau 2 de M6 | Organisation de joueurs, dotée d'un portefeuille et d'un journal public tiré du registre. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation) |
| rang dans une corporation | à fixer au niveau 2 de M6 | Position d'un acteur dans sa corporation. Un changement de rang prend effet au tick suivant. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation) |
| métier | à fixer au niveau 2 de M4 | Rôle économique entraîné séparément : mineur, transporteur, marchand. | [CUJ 2](designs/architecture-niveau-1.md#cuj-2--un-mineur-ia-est-entraîné-et-jugé-jalon-m4) |
| agent | — | Ne désigne que l'agent de code. Pour les autres sens, voir joueur IA, référence scriptée et client tiers. | [Overview](designs/architecture-niveau-1.md#overview) |
| rôle | — | Voir les entrées métier et rang dans une corporation. | [Overview](designs/architecture-niveau-1.md#overview) |
| propriétaire | — | La personne qui dirige le projet. Seul le propriétaire fusionne, et l'agent de code agit avec son compte GitHub. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |


## Règles et temps

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| fonction `step` | `step` | `step(state, orders, world_seed, tunables) -> (state, events)`, l'unique point d'entrée des règles. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation) |
| fonction `observe` | `observe` | `observe(état, acteur)` ne renvoie que les champs visibles pour cet acteur, avec les événements visibles du dernier tick. | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité) |
| observation | `Observation` | Ce que reçoit un acteur : l'état visible et les événements visibles du dernier tick. | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| tick | `tick` | Unité de temps du jeu. Les durées sont des nombres entiers de ticks. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation) |
| phase | `Phase` : `MOVEMENT`, `MINING`, `TRADE`, `COMBAT`, `SETTLEMENT` | Étape d'un tick, dans un ordre fixe : déplacement, minage, commerce, combat, règlement. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| réception | `Reception` | Partie du serveur qui applique les contrôles sans état aux ordres reçus. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| validation sans état | `validate_orders` | Contrôles qui ne dépendent pas de l'état : format, taille, authentification, quota d'ordres. Elle vit dans le paquet `schema`. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| ordre | `Order` (`orders` est le paramètre de `step`) | Entrée qui modifie l'état. Toute entrée qui modifie l'état est un ordre journalisé. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| catégorie d'ordre | `OrderCategory` : `PLAYER`, `SYSTEM`, `ADMIN` | Joueur ; système (déconnexion, départ d'un vaisseau hors ligne) ; administration (arrêt d'urgence, création de personnage, passage en mode observation). | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| journal des ordres soumis | `OrderLog` | Il fait foi et permet de rejouer. Il contient tous les ordres soumis à `step` par tick, y compris ceux que `step` refusera. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| ordre soumis | `SubmittedOrder` | Un ordre tel que le journal et `step` le reçoivent : l'ordre, le tick où il entre, l'acteur du point de connexion qui l'a soumis (aucun pour un ordre du serveur) et le code de refus de la réception, s'il y en a un. | [niveau 2 de M1, §5](designs/niveau-2-m1-noyau.md#5-les-formats-schema), [niveau 2 de M1, §13](designs/niveau-2-m1-noyau.md#13-les-interfaces) |
| code de refus | `RefusalCode` | Code stable d'un ordre refusé : par la réception quand un contrôle sans état refuse l'ordre, ou par `step` quand un contrôle qui dépend de l'état le refuse. Le refus de la réception est journalisé avec l'ordre, puis rendu par `step`. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| résultat d'ordre | `OrderResult` | Réponse structurée à chaque ordre : code stable, texte, budget restant. | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| budget d'actions | `action_budget` | Limite d'actions d'un acteur, vérifiée dans `step`. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| quota d'ordres | `ORDER_QUOTA_PER_TICK` | Nombre maximal d'ordres par acteur et par tick. Au-delà, on garde les plus petits numéros choisis par l'acteur. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| arrêt d'urgence | à fixer au niveau 2 de M5 | Ordre d'administration. Le disjoncteur l'émet pour un joueur IA. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité) |
| mode observation | à fixer au niveau 2 de M5 | Le joueur IA reçoit des observations et produit des ordres, que `step` refuse avec un code dédié. | [CUJ 6](designs/architecture-niveau-1.md#cuj-6--un-joueur-ia-est-déployé-dans-le-monde-jalon-m5) |
| mode rejeu | `replay_mode` | Mode du client Textual servi par le serveur de rejeu (`tools`), qui fait tourner `step` et envoie des observations au client. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |

## Données

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| état | `State` (`state` est le paramètre de `step`) | Ensemble des entités du monde, en enregistrements `msgspec.Struct` figés. Un état produit par `step` n'est jamais modifié ensuite. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| graine du monde | `world_seed` | Graine dont dépend chaque tirage aléatoire. Celle du monde en ligne reste hors du dépôt. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité) |
| monde en ligne | — | Le monde persistant que fait tourner le serveur à partir de M5, par opposition aux mondes générés pour les tests et l'entraînement. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité) |
| générateur à clé | `keyed_draw` | Générateur aléatoire dont chaque tirage dépend de (graine du monde, tick, entité, motif), via BLAKE2b. Ajouter un tirage ne décale pas les autres. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| réglages | `tunables` (fichier `tunables.toml`) | Les chiffres des règles du jeu. Leur empreinte entre dans `rules_version`. | [Non-Goals](designs/architecture-niveau-1.md#non-goals) |
| instantané | `Snapshot` | Point de départ d'un rejeu ou d'une reprise, en MessagePack canonique. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| événement | `Event` (`events` est le résultat de `step`) | Interface pour l'analyse, les récompenses et l'historique public. Recalculable en rejouant le journal. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| identifiant d'événement | `tick` + `seq` | `tick` et `seq` identifient un événement de façon unique. | [§6](designs/architecture-niveau-1.md#6-lenveloppe-des-événements) |
| cause | `causation_id` | L'ordre qui a causé l'événement. | [§6](designs/architecture-niveau-1.md#6-lenveloppe-des-événements) |
| classe de visibilité | `Visibility` : `PUBLIC`, `CORPORATION`, `PRIVATE`, `ADMIN` | Public, corporation, privé ou administration. Portée par chaque champ de l'état et par chaque événement. | [§5](designs/architecture-niveau-1.md#5-acteurs-égalité-daccès-et-visibilité), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| empreinte | `Fingerprints` (une valeur par composant) | Calculée par composant de l'état, sur l'encodage des instantanés. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| empreinte de référence | `reference_fingerprints` | Empreinte attendue, rangée par `rules_version`. La changer exige une montée de version et un rapport de différences. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| intervalle des empreintes en production | `N_empreinte` (nom provisoire, nom définitif au niveau 2 de M5) | En production, les empreintes sont calculées tous les `N_empreinte` ticks. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation) |
| protocole | `protocol_version` ; messages `SubmitOrders`, `TickUpdate` | Messages échangés entre clients et serveur, définis dans `schema`. Transports : appel de fonction dans le même processus à partir de M1, WebSocket à partir de M3. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| gisement | `Deposit` | Entité du jeu où l'on mine un minerai. Son stock baisse au minage et revient à `deposit_stock` tous les `regen_ticks` ticks (régénération d'un gisement). | [niveau 2 de M1, §2](designs/niveau-2-m1-noyau.md#2-les-règles-de-la-tranche-0) |

## Versions

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| version du journal des ordres | `order_log_schema_version` | Version du schéma des enregistrements du journal des ordres soumis. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations) |
| version des instantanés | `snapshot_schema_version` | Version du schéma des instantanés. Une montée de version de `msgspec` en entraîne une nouvelle. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations) |
| version des événements | `event_schema_version` | Version du schéma des événements. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations) |
| version des règles | `rules_version` | Un numéro de révision des règles, tenu à la main, + l'empreinte de `tunables.toml`. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité) |
| version du protocole | `protocol_version` | Version du protocole, échangée à la connexion à partir de M5. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations) |
| version de l'observation | `obs_spec_version` | Version du format d'observation, à partir de M4. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations) |
| version de l'action | `action_spec_version` | Version du format d'action, à partir de M4. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations) |
| politique | `policy_id`, `policy_version` | Ce qui décide des ordres d'un joueur IA. Chaque ordre d'un joueur IA porte `policy_id` et `policy_version`. | [§3](designs/architecture-niveau-1.md#3-les-sources-de-vérité) |
| manifeste | à fixer au niveau 2 de M4 | Les versions d'un joueur IA déployé, plus l'empreinte de ses poids. | [§7](designs/architecture-niveau-1.md#7-les-versions-et-les-migrations) |

## Paquets

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| paquet racine | `fourx` | Paquet qui contient les paquets du niveau 1 ; l'identifiant `core` s'importe par `fourx.core`. | [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#1-décisions-prises-pour-m0) |
| paquet `schema` | `schema` | Types d'ordre, d'observation et d'événement ; messages du protocole ; validation sans état ; encodeur et décodeur. N'importe rien du projet. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| paquet `core` | `core` | État, `step`, `observe`, registre. Importe `schema`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| paquet `policies` | `policies` | Toute fonction `observation -> ordres` : PNJ, références scriptées et réseaux entraînés. Importe `schema`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| paquet `server` | `server` | Boucle des ticks, transports, persistance. Importe `core` et `schema`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| paquet `clients` | `clients` | Client Textual, hôte des joueurs IA, hôte des PNJ. Importe `schema` et `policies`. Un client n'appelle jamais `step`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| paquet `training` | `training` | Environnement d'entraînement. Importe `core`, `schema` et `policies`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| paquet `tools` | `tools` | Serveur de rejeu, outil de divergence. Importe `core`, `schema` et `server`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |

## Économie

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| registre | `Ledger` | Registre comptable en partie double. Il fournit aussi le journal public de chaque corporation. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| écriture | `LedgerEntry` | Chaque mouvement est une écriture : compte débité, compte crédité, montant, code de motif, ordre qui l'a causé. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| compte du registre | `Account`, de type `AccountKind` : `ISSUANCE`, `DESTRUCTION`, `ESCROW`, `PERSONAL_WALLET`, `CORPORATION_WALLET` | Émission, destruction, séquestre, portefeuille personnel, portefeuille de corporation. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| émission | `AccountKind.ISSUANCE` | L'argent créé par le compte d'émission. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| destruction | `AccountKind.DESTRUCTION` | L'argent qui part vers le compte de destruction (taxes et frais). | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| masse monétaire | `money_supply` | La somme des comptes de portefeuille, de corporation et de séquestre. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| séquestre | `AccountKind.ESCROW` | Type de compte du registre, compté dans la masse monétaire. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| motif | `Reason` : `ORE_SALE`, `SALE_TAX` (le motif d'un tirage à clé est une simple chaîne) | Code qui dit pourquoi une écriture a lieu. Émission et destruction sont mesurées par motif. | [§4](designs/architecture-niveau-1.md#4-le-registre-comptable-et-la-conservation), [niveau 2 de M1, §12](designs/niveau-2-m1-noyau.md#12-les-identifiants-fixés-par-m1) |
| seuil d'inactivité | `T_inactif` (nom provisoire, nom définitif au niveau 2 de M2) | On mesure la part de l'argent inactif depuis plus de `T_inactif` ticks. | [§9](designs/architecture-niveau-1.md#9-lobservabilité) |

## Entraînement

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| environnement d'entraînement | à fixer au niveau 2 de M4 | Environnement multi-acteurs PettingZoo `ParallelEnv` qui enveloppe `step`, `observe`, la validation sans état, l'encodeur et le décodeur. | [§8](designs/architecture-niveau-1.md#8-lentraînement) |
| pas | à fixer au niveau 2 de M4 | Un appel à l'environnement d'entraînement, c'est-à-dire un tick pour tous les acteurs du scénario. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation) |
| métrique du métier | à fixer au niveau 2 de M4 | Une grandeur par métier, qui sert à comparer les versions d'un joueur IA. | [§8](designs/architecture-niveau-1.md#8-lentraînement) |
| scénario d'évaluation | à fixer au niveau 2 de M4 | Scénario mis de côté, sur lequel on évalue les joueurs IA. | [§8](designs/architecture-niveau-1.md#8-lentraînement) |
| verdict | à fixer au niveau 2 de M4 | Une phrase générée automatiquement, du type « la v3 bat la v2 de X ± Y sur N scénarios d'évaluation ». | [§8](designs/architecture-niveau-1.md#8-lentraînement) |
| verdict favorable | à fixer au niveau 2 de M4 | La règle de promotion est satisfaite. | [§8](designs/architecture-niveau-1.md#8-lentraînement) |
| règle de promotion | à fixer au niveau 2 de M4 | Condition pour qu'une nouvelle version d'un joueur IA remplace la précédente. | [§8](designs/architecture-niveau-1.md#8-lentraînement) |
| encodeur | à fixer au niveau 2 de M4 | Transforme une observation en entrée du réseau. Il vit dans `schema`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| décodeur | à fixer au niveau 2 de M4 | Transforme la sortie du réseau en ordre. Il vit dans `schema`. | [§1](designs/architecture-niveau-1.md#1-les-composants-et-les-paquets) |
| déclencheur Rust | — | Conditions qui font rouvrir la question du passage à Rust. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation) |
| indicateur avancé | — | Les ticks par seconde du paquet `core` seul, de M1 à M3. Il ne déclenche rien. | [§2](designs/architecture-niveau-1.md#2-le-noyau-de-simulation) |
| PC d'entraînement | — | La machine du réseau local qui porte la carte graphique, où tournent l'entraînement et le serveur MLflow. Son adresse n'entre jamais dans le dépôt. | [§8](designs/architecture-niveau-1.md#8-lentraînement) |
| serveur MLflow | — | Serveur qui enregistre les exécutions d'entraînement. Il tourne sur le PC d'entraînement. Son adresse est lue depuis une variable d'environnement. | [§8](designs/architecture-niveau-1.md#8-lentraînement) |

## Projet

| Terme | Identifiant du code | Définition | Lien |
| :-- | :-- | :-- | :-- |
| tranche 0 | — | La première version jouable : un petit monde hors ligne avec juste assez de règles pour miner, transporter et vendre. | [CUJ 1](designs/architecture-niveau-1.md#cuj-1--le-propriétaire-joue-la-tranche-0-jalon-m1) |
| jalon | — | Étape de construction, de M0 à M6, avec un critère de sortie et un document de niveau 2. | [§11](designs/architecture-niveau-1.md#11-le-découpage-en-documents-de-niveau-2) |
| document de niveau 1 | — | Le document d'architecture commun. Il ne liste pas les fichiers de code à écrire. | [Overview](designs/architecture-niveau-1.md#overview) |
| document de niveau 2 | — | Document propre à un jalon, avec un plan fichier par fichier qui respecte le niveau 1. | [Overview](designs/architecture-niveau-1.md#overview) |
| pull request de scénarios | — | Rédigée par l'agent de code : scénarios en français et définitions d'étapes, marqués *en attente*. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| pull request de fonctionnalité | — | Le code, et le retrait de la marque *en attente*. Elle s'ouvre après la fusion de la pull request de scénarios correspondante. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| pull request protégée | — | Ne contient que des chemins protégés autres que les scénarios (documents de niveau 2, ADR, glossaire, feuille de route, listes, configuration), sans code du jeu. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| revue EGM | — | Relecture d'un document ou d'un changement par des relecteurs IA lancés sans le contexte de la conversation (méthode Elephant-Goldfish Model). L'agent de code la lance, et son résumé en français va en tête de la pull request. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| scénario en attente | — | Scénario dont le code n'existe pas encore, listé dans `tests/scenarios/en_attente.txt`. La CI exige qu'il échoue, et un ajout exige une pull request qui modifie un `.feature` (tâche `en-attente`). | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) ; [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#10-les-scénarios-et-leur-marque--en-attente-) |
| définition d'étapes | `steps` | Code de test qui donne son sens à une phrase de scénario ; dossier `tests/scenarios/steps/`. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) ; [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#1-décisions-prises-pour-m0) |
| chemin protégé | — | Fichier ou dossier dont toute modification est signalée par le contrôle de garde. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| contrôle de garde | — | Contrôle lancé depuis la version de `main`, sans exécuter le code de la branche, qui signale toute modification d'un chemin protégé. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| contrôle obligatoire | — | Tâche (job GitHub Actions) que la protection de `main` exige avant la fusion (required status check). | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) ; [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#5-la-protection-de-main-et-les-contrôles-obligatoires) |
| contrôle après fusion | — | Contrôle qui tourne sur `main` et ne bloque aucune fusion. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| tâche | — | Tâche (job) de GitHub Actions. | [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#5-la-protection-de-main-et-les-contrôles-obligatoires) |
| commande d'amorçage | — | L'une des trois commandes de création du dépôt de M0 (blocage des secrets, push initial, protection de main), que le hook n'autorise qu'une fois. | [niveau 2 de M0](designs/niveau-2-m0-garde-fous.md#3-lamorçage) |
| suite canari | — | Bugs volontaires, sur `main`, que les contrôles doivent toujours attraper. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| hook Claude Code | — | Hook `PreToolUse`, configuré dans `.claude/settings.json`, qui refuse certaines commandes directes. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| hook pre-commit | — | Hook qui lance `gitleaks` avant chaque commit. | [§10](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia) |
| disjoncteur | — | Quand l'émission ou la variation de portefeuille d'un joueur IA dépasse un seuil, le serveur émet un ordre d'arrêt d'urgence. | [§9](designs/architecture-niveau-1.md#9-lobservabilité) |
| page d'accueil | — | Page statique de l'observabilité : un statut vert, orange ou rouge par domaine disponible. | [§9](designs/architecture-niveau-1.md#9-lobservabilité) |
