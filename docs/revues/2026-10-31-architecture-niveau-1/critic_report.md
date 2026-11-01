# Rapport de relecture critique (Goldfish), tour 1

**Cible :** /home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md (lignes 1 à 459, soit tout ce qui précède « ## Detailed Implementation Plan »)
**Étape :** 7 (relecture critique), boucle egm-review-loop, tour 1
**Contexte fourni aux relecteurs :** la cible et la RFC liée (/home/ezpk/Projects/4X/docs/designs/mmo-gestion-spatiale-ia.md). Projet neuf, sans code. Document de niveau 1.

## État des relecteurs

| Relecteur | Norme appliquée | État |
| --- | --- | --- |
| `egm-design` | /home/ezpk/.claude/plugins/cache/egm/egm/0.1.0/resources/document_standards/feature-spec-standard.md | terminé |
| `egm-structural` | /home/ezpk/.claude/plugins/cache/egm/egm/0.1.0/resources/document_standards/feature-spec-standard.md | terminé |
| `egm-style` | aucune (persona seul) | terminé |

Aucun relecteur n'a échoué et aucune relance n'a été nécessaire.

## Bilan

| Gravité | Nombre |
| --- | --- |
| Blocker | 3 |
| Major | 23 |
| Nit | 33 |
| **Total après dédoublonnage** | **59** |

Fusions effectuées (le constat retenu garde l'identifiant du relecteur le plus complet ; les autres sont cités en « aussi relevé par ») :
- l'absence de section « Risques » : design B3 + structural M1, dans **design-1-3** ;
- le contournement par l'administrateur : design M13 + structural M3, dans **design-1-16** ;
- le seuil de 347 pas/s : design M4 + style M1 + structural N2 (partie Rust), dans **design-1-7** ;
- « il ne connaît que des entiers » : design Nit 2 + style N4, dans **design-1-19** ;
- l'interdiction de `float` par TID251 : design Nit 1 + style N16 (deuxième partie), dans **design-1-18** ;
- le mélange des langues dans les titres : structural N10 + style N16 (première partie), dans **structural-1-10** ;
- la procédure de mise à jour écrite deux fois : structural N2 (deuxième partie) + style N10, dans **style-1-17**.

Divergence de gravité : `egm-design` classe l'absence de section « Risques » en Blocker, `egm-structural` en Major. Le constat fusionné reste en Blocker, parce que la norme exige explicitement cette rubrique.

Les numéros de ligne de la RFC cités ci-dessous viennent des relecteurs. La synthèse en a vérifié quelques-uns par recherche (RFC l. 76 « aucune exception, même pour l'administrateur », l. 88 « un serveur en retard ralentit le temps du jeu », l. 232 « argent en nombres flottants, sans registre »). Les autres n'ont pas été revérifiés. Les calculs (par exemple 10 000 000 / 28 800 s ≈ 347) sont ceux des relecteurs et n'ont pas été refaits par la synthèse.

---

## Constats par ordre de priorité (Blocker, puis Major, puis Nit)

### Blocker

#### design-1-1 : on ne sait pas qui valide les ordres, la réception ou `step`
* **Relecteur :** `egm-design`
* **Lignes :** 43, 50, 139-141, 184-186, 203, 250
* **Problème :** le schéma place « Réception ordres : limites, refus, budget par tick » hors du noyau (l. 139-141), et le journal stocke les « ordres acceptés » (l. 203), donc déjà filtrés. Pourtant, « l'ordre d'un tick » met la validation (permissions, budget, format) dans le tick (l. 185). La RFC (l. 180) demande que les permissions soient vérifiées au moment de l'application. Enfin, l'environnement d'entraînement n'enveloppe que `step`, `observe` et l'encodeur (l. 250), sans la réception.
* **Pourquoi c'est grave :** si une partie de la validation reste hors de `step`, l'objectif 1 (une seule fonction pour les règles) est faux, l'objectif 4 (même porte pour tous) est faux en entraînement, et l'objectif 2 (rejeu) devient ambigu : un ordre accepté par la réception puis refusé par `step` doit être dans le journal pour que le rejeu reproduise le refus. M1 et M3 risquent de trancher ce point de deux façons différentes.
* **Correction proposée :** écrire que la réception ne fait que des contrôles sans état (format, taille, nombre brut d'ordres par connexion). Tout contrôle qui dépend de l'état (permissions, budget, solde) se fait dans `step` et produit un code de refus. Le journal contient tous les ordres transmis à `step`, y compris ceux qu'il refusera (renommer en « ordres soumis au tick »). Réutiliser la même validation sans état dans l'environnement d'entraînement.

#### design-1-2 : la CI GitHub ne peut joindre ni MLflow, ni les fichiers Parquet, ni le PC d'entraînement
* **Relecteur :** `egm-design`
* **Lignes :** 54-55, 104, 119, 261, 266-267, 322, 324, 427
* **Problème :** la CI doit générer la page d'accueil à partir des événements (l. 54, 267), produire pour l'entraînement le lien MLflow et le verdict (l. 322), et garantir que l'agent ne produit jamais la preuve lui-même (l. 324). Or les fichiers Parquet et les exécutions MLflow sont hors du dépôt (l. 427), MLflow tourne sur le réseau local (l. 261), et un runner GitHub hébergé n'a ni GPU ni accès au réseau local.
* **Pourquoi c'est grave :** les CUJ 2, 3 et 5 et les objectifs 6 à 8 dépendent d'une chaîne de preuve qui ne fonctionne pas telle qu'écrite. La solution qu'un agent de code choisira probablement, un runner auto-hébergé, exécuterait du code de pull request d'un dépôt public sur une machine du réseau local. Rien dans le document ne l'interdit.
* **Correction proposée :** pour chaque preuve, dire qui la produit et où. La CI hébergée produit ce qui se calcule à partir du dépôt seul (scénarios, rejeu, métriques sur parties générées, captures, vidéo). Une tâche planifiée sur une machine locale, lancée depuis `main`, produit la page d'accueil et le verdict. Interdire les runners auto-hébergés sur ce dépôt, ou au minimum sur les pull requests. Dire comment un verdict est rattaché à un commit sans que l'agent le fabrique (par exemple une tâche lancée à la main par le propriétaire).

#### design-1-3 : la section « Risques et parades » exigée par la norme est absente
* **Relecteur :** `egm-design` (aussi relevé par `egm-structural`, en Major)
* **Lignes :** tout le document ; risques épars aux l. 176, 178-182, 281-285, 293, 325, 418-440
* **Problème :** la norme demande les modes de défaillance, les implications de sécurité et les limites de montée en charge, chacun avec sa parade. Le document en cite quelques-uns au fil du texte, sans inventaire. Plusieurs risques n'apparaissent nulle part : journal SQLite corrompu ou disque plein, PC d'entraînement ou MLflow injoignable, divergence de rejeu découverte en production, migration ratée après reprise, fuite d'un champ caché par `observe`, joueur IA déployé qui exploite un bug, mise à jour de `msgspec` ou de Python qui change les empreintes, temps de relecture du propriétaire comme goulot (RFC l. 183), injection de consignes dans les agents de code par le contenu du dépôt public.
* **Pourquoi c'est grave :** un lecteur ne peut pas vérifier que les risques majeurs sont traités sans tout relire, et les agents sans mémoire n'ont pas de liste unique à respecter.
* **Correction proposée :** ajouter un H2 « Risques et parades » (ou « Risks & Mitigations », dans la langue des autres H2), en tableau : risque, effet ou impact, signal de détection, parade, jalon. Y renvoyer les éléments déjà écrits (Rust, comptes GitHub, AI Act) au lieu de les recopier.

### Major

#### design-1-4 : décalage d'un tick entre le direct et l'entraînement
* **Relecteur :** `egm-design`
* **Lignes :** 186, 218, 250
* **Problème :** en direct, le joueur IA observe après le tick T, décide, puis son ordre arrive dans la fenêtre suivante. Avec la règle « reçu pendant T, appliqué à T+1 », il s'applique à T+1 ou T+2 selon la latence et le temps d'inférence. En entraînement, l'action calculée sur l'observation k s'applique au pas k+1, sans latence ni tick manqué.
* **Pourquoi c'est important :** un réseau entraîné sans ce délai se comporte autrement en production, et la dégradation est silencieuse, exactement ce que la contrainte 2 (l. 34) veut éviter. Le test de parité de l'objectif 4 compare les observations, pas la chronologie.
* **Correction proposée :** fixer une chronologie de référence (quel état l'observation reflète, quand se ferme la fenêtre de collecte, sort d'un ordre en retard : reporté ou refusé). Faire reproduire ce délai par l'environnement d'entraînement, avec un taux de ticks manqués réglable.

#### design-1-5 : l'objectif 6 (« chaque métrique se recalcule à partir des événements ») se contredit
* **Relecteur :** `egm-design`
* **Lignes :** 54, 115-119, 163, 275
* **Problème :** les métriques techniques (durée du tick p50/p99, file d'ordres, pas par seconde) ne peuvent pas venir des événements du noyau, puisque `step` n'a pas d'horloge (l. 163). L'avancement du projet vient de GitHub, la progression des joueurs IA de MLflow.
* **Pourquoi c'est important :** soit l'objectif est faux, soit on le tient en mettant des mesures d'horloge dans les événements déterministes, et les empreintes ne sont plus reproductibles.
* **Correction proposée :** limiter l'objectif 6 aux métriques d'économie et de jeu. Déclarer un flux de télémétrie séparé, non déterministe, hors du noyau et hors des empreintes, pour la santé technique, et nommer les sources des autres domaines (MLflow, API GitHub).

#### design-1-6 : « aucun client n'importe le noyau » contredit le client Textual en mode rejeu
* **Relecteur :** `egm-design`
* **Lignes :** 113, 153, 159, 218, 276
* **Problème :** un rejeu appelle `step`, donc le client Textual en mode rejeu (l. 276) et l'outil de divergence qui lui est rattaché importent le noyau. De plus, l'encodeur commun, partagé par l'hôte des joueurs IA (un client du protocole) et l'entraînement, doit vivre quelque part : s'il est dans le paquet du noyau, l'hôte l'importe.
* **Pourquoi c'est important :** la règle `import-linter` posée dès M0 sera soit violée, soit contournée par une exception ponctuelle.
* **Correction proposée :** décrire le mode rejeu comme un serveur de rejeu local qui appelle `step` et sert les observations par le protocole ; le client reste un pur client. Créer un paquet partagé, distinct du noyau, pour les schémas d'observation et d'action et pour l'encodeur et le décodeur. Faire figurer ces paquets et leurs dépendances autorisées dans le schéma.

#### design-1-7 : le déclencheur Rust est mal défini, et son budget ignore les 5 entraînements
* **Relecteur :** `egm-design` (aussi relevé par `egm-style` et, pour la duplication, par `egm-structural`)
* **Lignes :** 178-179, 254, 429-433
* **Problème :**
  - l. 179 : « 347 pas par seconde (calculé) une fois le coût du réseau de neurones **déduit** » ; l. 431 : « coût du réseau **compris** » ;
  - l. 178 parle de pas « par cœur », alors que 347 correspond à un débit total (10 000 000 / 28 800 s, d'après les relecteurs) ;
  - « pas » n'est pas défini (pas d'environnement ou pas d'agent ; l'écart vaut un facteur égal au nombre d'agents par scénario) ;
  - l'évaluation demande au moins 5 entraînements par configuration (l. 254), soit environ 50 millions de pas par verdict, donc 5 nuits au même débit ;
  - la définition existe en deux exemplaires (section 2 et exigences non fonctionnelles), qui divergent déjà.
* **Pourquoi c'est important :** c'est le seul seuil chiffré qui commande un changement d'architecture majeur. S'il est ambigu, il sera interprété au plus pratique.
* **Correction proposée :** définir « pas » (pas d'environnement multi-agents), choisir « compris » ou « déduit », préciser le nombre de processus, fixer le budget au niveau du verdict (5 graines × 10 millions de pas, en parallèle ou non) et recalculer le seuil avec un outil. N'écrire la définition qu'une fois (section 2) et y renvoyer depuis la l. 431. Retirer « (calculé) ».

#### design-1-8 : le banc d'essai ne mesure pas la représentation retenue, et le rejet de l'alternative A ignore le traitement en bloc
* **Relecteur :** `egm-design`
* **Lignes :** 165-176, 346-348
* **Problème :** la décision porte sur des `msgspec.Struct` figés avec copie partielle, mais le document ne dit pas si le banc A mesurait ce mode immuable ou des objets modifiables. « Ne recopier que ce qui change » dans des tables triées suppose une structure à partage ; copier un dictionnaire de 10 000 entrées à chaque modification coûte O(n). Enfin, le rejet de A compare un seul petit scénario, alors que l'avantage cité pour A (l. 346) est de traiter de nombreuses copies d'entraînement d'un bloc, ce qui est le mode habituel en apprentissage par renforcement (par exemple 64 copies × 30 entités ≈ 2 000 entités).
* **Pourquoi c'est important :** la décision est présentée comme mesurée, mais la mesure ne correspond ni à la représentation choisie ni à l'usage prévu.
* **Correction proposée :** dire ce que mesurait exactement le banc A, préciser la structure des tables et la stratégie de copie (par exemple une copie par phase). Reformuler le rejet de A en reconnaissant le cas des copies en bloc et en expliquant pourquoi on l'écarte malgré tout (lisibilité, Rust en recours).

#### design-1-9 : le contrôle de débordement 64 bits ne couvre que deux fonctions
* **Relecteur :** `egm-design`
* **Lignes :** 192
* **Problème :** seules `div_floor` et `mul_div` vérifient les bornes. Les `+` et `*` ordinaires sur les entiers Python, qui ne débordent jamais, ne sont pas contrôlés.
* **Pourquoi c'est important :** une valeur au-delà de 2^63 passe en Python et ne casse qu'au portage Rust ou à la sérialisation, alors que la règle est justement là pour faciliter le portage.
* **Correction proposée :** ajouter un invariant, vérifié à chaque tick en test et à la sérialisation de l'instantané : tout champ entier de l'état tient dans un entier signé de 64 bits. Ou typer les champs avec des bornes `msgspec.Meta` qui échouent à l'encodage.

#### design-1-10 : l'invariant de conservation de l'argent est soit vide, soit ambigu
* **Relecteur :** `egm-design`
* **Lignes :** 49, 213-214
* **Problème :** en partie double, si les comptes d'émission et de taxes sont des comptes du registre (l. 213), la somme de tous les soldes vaut toujours zéro et l'invariant ne peut pas échouer. Si on les exclut, il faut dire quels comptes forment la masse monétaire (le séquestre en fait-il partie ?).
* **Pourquoi c'est important :** un test qui ne peut pas échouer est un test creux, ce que la mutation et les tests de propriétés sont censés traquer.
* **Correction proposée :** définir deux invariants : somme de tous les comptes = 0 ; masse monétaire (somme d'une liste explicite de comptes non système) = valeur précédente + écritures depuis l'émission − écritures vers les sorties. Ajouter l'invariant de conservation des biens (aucune cargaison négative ; minerai extrait = stocké + vendu), présent dans la RFC (l. 175) et absent ici.

#### design-1-11 : la visibilité est définie de façon incohérente et ne couvre pas l'état
* **Relecteur :** `egm-design`
* **Lignes :** 50-52, 205, 218-219, 231
* **Problème :** la l. 219 donne une classe de visibilité à chaque champ d'événement, la l. 231 une seule par événement. `observe` lit l'état, mais aucun champ de l'état n'a de classe de visibilité, donc le test « aucun champ caché ne fuit » n'a rien à vérifier. Les événements servent aussi « au client » (l. 205), ce qui crée un second canal vers le joueur, hors de `observe`.
* **Pourquoi c'est important :** cela contredit l'objectif 4 (« une seule fonction calcule ce qu'un joueur voit ») et rend son test invérifiable.
* **Correction proposée :** choisir la visibilité par champ, l'étendre aux champs de l'état, et faire passer les événements reçus par un acteur par `observe` (état visible + événements visibles du dernier tick).

#### design-1-12 : les entrées qui ne sont pas des ordres de joueur ne sont pas journalisées
* **Relecteur :** `egm-design`
* **Lignes :** 128, 186, 203 (et RFC l. 280, décision 5)
* **Problème :** plusieurs entrées changent le monde sans être des ordres : départ du vaisseau à la déconnexion (règle de sécurité hors ligne de la RFC), arrêt d'urgence et disjoncteur d'un joueur IA (l. 128), commandes d'administration, création de personnage, passage en mode observation. Le journal ne contient que des ordres.
* **Pourquoi c'est important :** le rejeu du monde en direct, et la reprise après plantage de M5, divergeront dès la première déconnexion.
* **Correction proposée :** déclarer que toute entrée qui influe sur l'état est un ordre journalisé, de catégorie « système » ou « administration », avec son `actor_kind`. Le serveur ne modifie jamais l'état autrement que par `step`.

#### design-1-13 : la cohérence entre journal, instantanés et Parquet après un plantage n'est pas définie
* **Relecteur :** `egm-design`
* **Lignes :** 143-147, 203-205, 337
* **Problème :** un fichier Parquet ne se complète pas après écriture, donc les « segments tournants » impliquent un tampon en mémoire, perdu en cas de plantage. DuckDB peut lire un segment à moitié écrit. La fréquence des instantanés, qui borne la durée de reprise, n'est pas fixée. Le mode WAL de SQLite ne garantit la durabilité d'un ordre confirmé qu'avec `synchronous=FULL`, ce qui n'est pas dit, alors que M5 exige « sans perte d'ordre confirmé ».
* **Pourquoi c'est important :** le critère de sortie de M5 n'est pas tenable sans ces règles.
* **Correction proposée :** poser que le journal fait foi et que les événements non publiés d'un tick sont régénérés par rejeu au redémarrage. Écrire les segments sous un nom temporaire puis les renommer de façon atomique. Fixer un ordre de grandeur pour la fréquence des instantanés et le réglage de durabilité de SQLite.

#### design-1-14 : le tableau des versions oublie le journal des ordres, et `rules_version` est mal défini
* **Relecteur :** `egm-design`
* **Lignes :** 203, 205, 207, 237-244
* **Problème :** le schéma des enregistrements du journal des ordres n'a pas de ligne dans le tableau des versions, alors que c'est lui qui doit rester lisible le plus longtemps ; `protocol_version` versionne le fil, pas le stockage. « Version du code des règles » (l. 207) n'est pas définie : un numéro manuel peut être oublié par un agent, une empreinte des sources change à chaque refactorisation. Rejouer un vieux journal exige l'ancien code, donc « recalculable » (l. 205) suppose de savoir retrouver ce code.
* **Correction proposée :** ajouter une ligne « Journal des ordres » (`order_log_schema_version`, migrations testées sur des fichiers de référence figés). Définir `rules_version` de façon mécanique (par exemple numéro manuel + empreinte de `tunables.toml`, avec un contrôle CI qui exige une hausse dès que les empreintes de référence changent). Enregistrer le commit à côté.

#### design-1-15 : les chemins protégés reposent sur la relecture d'un propriétaire qui ne lit pas le code
* **Relecteur :** `egm-design` (voir aussi style-1-18 pour le flou de « lecture explicite »)
* **Lignes :** 35, 300-307
* **Problème :** les pull requests qui touchent des chemins protégés « se fusionnent seulement après une lecture explicite du propriétaire » (l. 307). Or ces chemins sont du code (définitions d'étapes, configuration de la CI, des tests, de la mutation), et le propriétaire ne lit pas le code (l. 35).
* **Pourquoi c'est important :** la faiblesse relevée par la RFC (l. 67-68 : un agent qui affaiblit ses propres contrôles) reste ouverte.
* **Correction proposée :** pour chaque catégorie de chemin protégé, dire ce que le propriétaire vérifie sans lire le code : résumé en français généré depuis `main`, relecteur indépendant lancé par le contrôle de garde sur le diff sans l'exécuter, ou test « canari » (un bug volontaire que les contrôles doivent toujours attraper). Sinon, assumer ce trou dans la section Risques (design-1-3).

#### design-1-16 : les administrateurs peuvent contourner la protection de branche
* **Relecteur :** `egm-design` (aussi relevé par `egm-structural`)
* **Lignes :** 56, 106, 282, 294-299, 332
* **Problème :** l'objectif 8, le CUJ 3 et le critère de M0 promettent qu'« une pull request aux contrôles rouges ne peut pas être fusionnée ». L'agent utilise les identifiants du propriétaire, administrateur du dépôt. Les protections de `main` (l. 294-297) ne précisent pas qu'elles s'appliquent aussi aux administrateurs ; par défaut, un administrateur peut passer outre. La l. 282 dit d'ailleurs que GitHub ne peut pas empêcher l'agent de fusionner. La RFC l'avait prévu (l. 76 : « aucune exception, même pour l'administrateur »), mais le point a disparu ici.
* **Pourquoi c'est important :** le critère de sortie de M0 passe ou échoue selon un réglage que le document ne fixe pas.
* **Correction proposée :** ajouter « s'applique aussi aux administrateurs, sans contournement » aux réglages de `main` (option dédiée ou liste de contournement vide dans un ruleset) et au critère de M0. Ajouter aux interdictions de Claude Code les appels `gh api` ou `curl` qui modifient cette option, en rappelant que ce n'est pas une barrière. Sinon, reformuler le critère : « refusée sauf contournement explicite d'administrateur ».

#### design-1-17 : l'identité des acteurs et la machine du serveur persistant ne sont pas définies
* **Relecteur :** `egm-design`
* **Lignes :** 136, 221, 229, 337
* **Problème :** on ne sait pas qui fixe `actor_kind` ; si c'est le client, la décision de signaler les joueurs IA repose sur sa bonne foi. `policy_id` et `policy_version` doivent entrer dans `step` par les ordres, ce qui n'est pas dit. Rien sur l'authentification du protocole. Le plafond de personnages par opérateur (RFC l. 98) a disparu. Le schéma place le serveur sur le portable de développement alors que M5 vise un monde qui tourne sans le propriétaire, et il ne dit pas où tourne l'hôte des joueurs IA en production.
* **Correction proposée :** `actor_kind` est attribué par le serveur à la création du compte, jamais déclaré par le client. Les métadonnées de politique voyagent dans l'ordre et sont journalisées. Fixer un modèle d'authentification minimal. Préciser la machine du serveur à M5 (portable, PC d'entraînement, VPS) et celle de l'hôte des joueurs IA, ou en faire une question ouverte avec une échéance.

#### structural-1-1 : mauvaise imbrication des titres de fin
* **Relecteur :** `egm-structural`
* **Lignes :** 418, 444, 450
* **Problème :** « ### Additional Resources » et « ### Future Improvements » sont des H3 placés sous « ## Non-Functional Requirements ». Le trait horizontal de la l. 442 ne change pas la hiérarchie : une table des matières les rangera comme sous-parties des exigences non fonctionnelles.
* **Correction proposée :** les passer en H2, ou les regrouper sous un H2 « Annexes ».

#### style-1-1 : des critères de sortie de jalon ne sont pas mesurables
* **Relecteur :** `egm-style`
* **Lignes :** 57, 333, 336, 338
* **Problème :** la l. 57 annonce un critère de sortie mesurable pour chaque jalon, mais M1 contient « le propriétaire juge la boucle amusante » et « prix stables », M4 « capacité de la carte mesurée » sans dire quelle mesure, M6 « fonctionne de bout en bout ».
* **Pourquoi c'est important :** un agent de code ne peut pas savoir si le jalon est atteint, et la promesse de la l. 57 est contredite.
* **Correction proposée :** définir « stables » (par exemple variation de l'indice de prix sous X % entre deux fenêtres de N ticks). Écrire « le propriétaire valide explicitement la boucle (validation subjective assumée) », ou corriger la l. 57 en « mesurable ou validé par le propriétaire ». Dire ce qu'on mesure sur la carte (mémoire maximale, débit d'inférence). Remplacer « de bout en bout » par un scénario nommé.

#### style-1-2 : la règle de promotion et le critère de M4 ne disent pas ce qu'ils mesurent
* **Relecteur :** `egm-style`
* **Lignes :** 259, 336
* **Problème :** on ne sait pas de quelle grandeur on prend « la borne basse de l'intervalle à 95 % », ni de quoi « 10 % » est un pourcentage. « Aucune anomalie » dans le registre n'est pas défini.
* **Pourquoi c'est important :** c'est une règle de décision automatique, invérifiable sans métrique nommée.
* **Correction proposée :** nommer la métrique (par exemple différence de revenu net moyen par épisode entre la nouvelle et l'ancienne version, sur les cartes mises de côté). Remplacer « anomalie » par une condition testable : invariant de conservation respecté et argent tiré des sources sous un seuil.

#### style-1-3 : le mot « agent » désigne plusieurs choses
* **Relecteur :** `egm-style`
* **Lignes :** 259, 336, 377, 454, et partout pour « agent de code »
* **Problème :** « agent de code » désigne Claude Code ; « un agent apprendrait à exploiter des failles » (l. 377) désigne un joueur IA ; « agent scripté » (l. 259, 336) côtoie « PNJ scriptés » (l. 50, 141) et « référence scriptée » (l. 55, 96) sans dire si c'est la même chose ; « agents de tiers » (l. 454) est un quatrième sens.
* **Pourquoi c'est important :** le document prévoit un glossaire (l. 306) et s'adresse à des agents sans mémoire ; un mot à plusieurs sens produit plusieurs implémentations.
* **Correction proposée :** réserver « agent » à « agent de code ». Ailleurs, utiliser « joueur IA », « joueur scripté de référence », « client tiers ». Dire si la référence scriptée est un PNJ scripté.

#### style-1-4 : plusieurs mots pour les flux d'argent
* **Relecteur :** `egm-style`
* **Lignes :** 49, 97, 213-214, 258, 270
* **Problème :** pour l'argent qui entre : « argent émis », « émission », « sources d'argent », « entrées d'argent ». Pour l'argent qui sort : « argent détruit », « taxes (sortie d'argent) », « sorties d'argent ». « L'argent tiré des sources d'argent du jeu » (l. 97, 258) reste obscur.
* **Pourquoi c'est important :** ces termes alimentent l'invariant de conservation et les métriques ; un écart de mots peut devenir un écart de code.
* **Correction proposée :** choisir une paire (par exemple « émission » / « destruction »), la définir une fois en section 4 et l'utiliser partout. Reformuler la l. 97, par exemple : « l'argent émis au profit du joueur IA (indicateur d'exploitation de failles) ».

#### style-1-5 : le choix des identifiants GitHub est expliqué environ sept fois
* **Relecteur :** `egm-style`
* **Lignes :** 56, 107, 281-285, 293, 299-300, 325, 384, 428
* **Problème :** l'idée « l'agent utilise les identifiants du propriétaire ; GitHub n'impose rien ; les garde-fous évitent les erreurs, pas le contournement » revient dans les objectifs, le CUJ 3, quatre fois en section 10, dans l'alternative G et dans les exigences non fonctionnelles. « L'approbation n'est pas exigible » apparaît trois fois (l. 282, 299, 300).
* **Pourquoi c'est important :** autant d'endroits à corriger si la décision change, ce que les l. 285 et 456 prévoient.
* **Correction proposée :** garder l'explication complète en section 10 (l. 281-285) et renvoyer à cette section ailleurs. Supprimer les reformulations des l. 293, 299, 325 et 428.

#### style-1-6 : l'objectif 8 mélange un contrôle CI et une règle de travail
* **Relecteur :** `egm-style`
* **Lignes :** 56
* **Problème :** le titre dit « contrôlé par la CI », mais le corps ajoute une règle que rien ne contrôle (« seul le propriétaire fusionne »), et la vérification cite un refus « avant le commit », qui relève d'un hook local et non de la CI. « Sont définis ici » ne dit pas où.
* **Pourquoi c'est important :** la section Goals promet des objectifs vérifiables automatiquement ; y mêler une règle non imposée affaiblit cette promesse.
* **Correction proposée :** limiter l'objectif 8 à ce que la CI vérifie, déplacer la règle de fusion en section 10, remplacer « ici » par « en section 10 ».

#### style-1-7 : des verbes promettent plus que les outils ne garantissent
* **Relecteur :** `egm-style`
* **Lignes :** 43, 51, 55
* **Problème :** l. 51, « des tests de propriétés prouvent qu'aucun champ caché ne fuit » : un test de propriétés cherche des contre-exemples, il ne prouve rien. l. 43, « un contrôle d'imports interdit tout autre chemin vers les règles » : il n'empêche pas de réécrire une règle hors du noyau. l. 55, « se prouve », alors qu'il s'agit d'un intervalle de confiance.
* **Pourquoi c'est important :** une affirmation plus forte que l'outil donne une fausse assurance.
* **Correction proposée :** l. 51 : « vérifient sur N cas générés qu'aucun champ caché n'apparaît » ; l. 43 : « interdit d'importer le noyau ailleurs que par `step` » ; l. 55 : « se mesure » ou « se démontre statistiquement ».

#### style-1-8 : statuts vert/orange/rouge et disjoncteur sans critère
* **Relecteur :** `egm-style`
* **Lignes :** 119, 128, 267
* **Problème :** rien ne dit comment un domaine passe au vert, à l'orange ou au rouge. « Variations anormales de portefeuille » (l. 128) n'a pas de seuil.
* **Pourquoi c'est important :** un statut sans règle reste un jugement, et un disjoncteur sans seuil ne peut pas être implémenté.
* **Correction proposée :** au minimum, renvoyer ces seuils aux documents de niveau 2 de M2 (statuts) et de M5 (disjoncteur). Mieux : donner la forme de la règle, par exemple « rouge si un invariant est violé ».

### Nit

#### design-1-18 : interdictions incomplètes dans le noyau (`//`, `%`, `float`)
* **Relecteur :** `egm-design` (aussi relevé par `egm-style`)
* **Lignes :** 195
* **Problème :** le test d'arbre syntaxique rejette `/` mais pas `//` ni `%`, qui se comportent différemment en Rust avec des nombres négatifs (RFC l. 54). `ruff` TID251 vise des imports : rien ne dit qu'il peut interdire le type natif `float`. La liste mélange modules et type natif.
* **Correction proposée :** interdire `//` et `%` et passer par `div_floor` et `mod_floor`. Séparer « modules interdits » (TID251) et « type interdit » (test d'arbre syntaxique), ou noter le point TID251 comme à vérifier.

#### design-1-19 : « il ne connaît que des entiers » est trop fort
* **Relecteur :** `egm-design` (aussi relevé par `egm-style`)
* **Lignes :** 163
* **Problème :** l'état contiendra des Structs, des identifiants et des chaînes (codes, noms).
* **Correction proposée :** « Toutes les grandeurs numériques des règles sont des entiers » ou « aucun nombre flottant ».

#### design-1-20 : tirage d'un entier borné à partir de BLAKE2b non précisé
* **Relecteur :** `egm-design`
* **Lignes :** 194
* **Problème :** la méthode pour obtenir un entier dans un intervalle sans biais n'est pas fixée, alors qu'il faudra la reproduire en Rust.
* **Correction proposée :** préciser la méthode (rejet, ou multiplication sur 128 bits).

#### design-1-21 : fréquence et encodage des empreintes non fixés
* **Relecteur :** `egm-design`
* **Lignes :** 196-197
* **Problème :** la fréquence de calcul en production n'est pas donnée (la RFC, l. 197, dit tous les N ticks). Si l'empreinte dépend de l'encodage de `msgspec`, une mise à jour change toutes les empreintes de référence.
* **Correction proposée :** fixer la fréquence et calculer les empreintes sur un encodage propre au projet.

#### design-1-22 : sélection des ordres au-delà de K non définie
* **Relecteur :** `egm-design`
* **Lignes :** 186, 220
* **Problème :** quand plus de K ordres arrivent dans un tick, on ne sait pas lesquels sont refusés. Garder « les K premiers » réintroduit l'avantage à l'ordre d'arrivée que la l. 188 supprime. La règle de la RFC « un serveur en retard ralentit le temps du jeu » (l. 88) n'est pas reprise.
* **Correction proposée :** fixer une règle indépendante de l'ordre d'arrivée, et reprendre ou écarter explicitement la règle de la RFC.

#### design-1-23 : « conversion à la lecture » incompatible avec une lecture directe par DuckDB
* **Relecteur :** `egm-design`
* **Lignes :** 233, 240, 266
* **Problème :** DuckDB lit les fichiers Parquet directement ; rien ne dit où se fait la conversion des anciens événements.
* **Correction proposée :** préciser la couche de lecture (vues DuckDB par version) ou réécrire les segments lors d'une migration.

#### design-1-24 : limite de stockage sans estimation
* **Relecteur :** `egm-design`
* **Lignes :** 434
* **Problème :** « moins de 1 Go par jour » n'a ni calcul ni hypothèse de population. Le journal SQLite et les instantanés n'ont pas de politique de conservation.
* **Correction proposée :** donner un calcul, même grossier, et une politique de conservation pour le journal et les instantanés.

#### design-1-25 : graine secrète du monde en ligne contenue dans les instantanés et le journal
* **Relecteur :** `egm-design`
* **Lignes :** 204, 421, 446
* **Problème :** la graine doit rester hors du dépôt, mais elle sera dans les instantanés ou le journal.
* **Correction proposée :** préciser qu'aucun de ces fichiers n'est publié, et que l'historique public vient seulement des événements de classe « public ».

#### design-1-26 : décodeur d'actions et référence du score de mutation non mentionnés
* **Relecteur :** `egm-design`
* **Lignes :** 218, 243, 313
* **Problème :** le décodeur d'actions (sortie du réseau vers ordre) n'est pas cité alors qu'il doit être unique et lié à `action_spec_version`. On ne sait pas où est stockée la référence du score de mutation « qui ne peut pas baisser », ni si elle est un chemin protégé.
* **Correction proposée :** citer le décodeur à côté de l'encodeur, et dire où vit la référence de mutation (et l'ajouter aux chemins protégés).

#### structural-1-2 : schéma ASCII mal aligné et sources de vérité sans boîte
* **Relecteur :** `egm-structural`
* **Lignes :** 136-156
* **Problème :** le bord droit des cadres change de colonne d'une ligne à l'autre (le relecteur mesure de 107 à 112 caractères pour le cadre du haut, de 111 à 114 pour celui du bas), et la boîte NOYAU est décalée d'une colonne. Le journal des ordres et les instantanés n'ont pas de boîte : leurs libellés sont posés sur des flèches qui entrent dans la boîte Parquet, ce qui suggère « journal → Parquet » et contredit la section 3.
* **Correction proposée :** réaligner les bords, donner une boîte à « Journal des ordres (SQLite WAL) » et à « Instantanés », et ne relier à Parquet que la flèche des événements.

#### structural-1-3 : renvois internes sans lien
* **Relecteur :** `egm-structural`
* **Lignes :** 360, 366, 428
* **Problème :** « section 2 du plan technique », « (section 3) », « (alternative G) » sont en texte simple.
* **Correction proposée :** utiliser des ancres Markdown.

#### structural-1-4 : références externes sans URL
* **Relecteur :** `egm-structural`
* **Lignes :** 447-448
* **Problème :** rapports d'EVE, Neural MMO, PufferLib, AI Economist, Screeps, Evennia, SpaceMolt, Golemreach sont cités sans lien. La RFC (l. 297, selon le relecteur) signale SpaceMolt et Golemreach comme non vérifiés.
* **Correction proposée :** ajouter les liens, ou marquer « à sourcer » ceux qui ne sont pas vérifiés.

#### structural-1-5 : la rubrique « Raison du rejet » décrit souvent le choix retenu
* **Relecteur :** `egm-structural`
* **Lignes :** 366, 372, 378, 390, 396, 402, 414
* **Problème :** pour D, E, F, H, I, J et L, cette ligne décrit la solution adoptée ; la raison est dans « Inconvénients ».
* **Correction proposée :** commencer par la raison (« Parce que … »), puis « Retenu : … ».

#### structural-1-6 : choix structurants présentés sans alternative
* **Relecteur :** `egm-structural`
* **Lignes :** 165, 194, 205, 250
* **Problème :** pas d'alternative écrite pour les segments Parquet (contre une table SQLite ou DuckDB), le générateur à clé (contre un flux séquentiel), PettingZoo `ParallelEnv`, ni la copie partielle immuable.
* **Correction proposée :** une ligne par choix dans « Alternatives Considered », ou un renvoi au document de niveau 2 qui tranchera.

#### structural-1-7 : la phrase de cadrage des alternatives est inexacte
* **Relecteur :** `egm-structural`
* **Lignes :** 342
* **Problème :** elle dit que la RFC contient les alternatives de règles du jeu, mais la RFC contient aussi des alternatives d'architecture non reprises : « argent en flottants sans registre » (RFC l. 232) et « interface web dès le départ » (RFC l. 240, selon le relecteur).
* **Correction proposée :** reprendre ces deux alternatives, ou écrire « les autres alternatives écartées sont dans la RFC ».

#### structural-1-8 : mise en forme des listes et des libellés irrégulière
* **Relecteur :** `egm-structural`
* **Lignes :** 25-27, 44-52, 178, 220, 261, 267, 277, 300, et l'ensemble des listes
* **Problème :** puces `*   ` et `- ` mélangées ; libellés gras tantôt « **Libellé :** », tantôt « **Phrase,** » ; « Vérification » en ligne pour les objectifs 1, 3, 5 à 9, mais en liste ou paragraphe séparé pour 2 et 4.
* **Correction proposée :** un seul marqueur de puce et une seule forme de libellé.

#### structural-1-9 : traits horizontaux irréguliers
* **Relecteur :** `egm-structural`
* **Lignes :** 8, 416, 442, 458
* **Problème :** ils séparent certains H2 et pas d'autres.
* **Correction proposée :** les supprimer, ou en mettre entre tous les H2.

#### structural-1-10 : langues mélangées dans les titres et les gabarits
* **Relecteur :** `egm-structural` (aussi relevé par `egm-style`)
* **Lignes :** 4, titres H2, CUJ (80-129)
* **Problème :** H2 en anglais, H3 en français, « Proposed » et « Given / When / Then » dans un texte français.
* **Correction proposée :** si l'anglais vient du gabarit, l'écrire une fois en tête du document ; sinon, tout passer en français.

#### structural-1-11 : place des questions ouvertes et traçabilité des CUJ
* **Relecteur :** `egm-structural`
* **Lignes :** 70, 80-121, 330-338
* **Problème :** les questions ouvertes précèdent les notions qu'elles utilisent (tick, budget d'actions). Seul le CUJ 6 indique son jalon, et le tableau des jalons ne cite que les CUJ 1 et 6.
* **Correction proposée :** déplacer « Open Questions » après les exigences non fonctionnelles, et indiquer le jalon de chaque CUJ (CUJ 3 → M0, CUJ 1 et 4 → M1, CUJ 5 → M2, CUJ 2 → M4, selon la proposition du relecteur).

#### style-1-9 : formulations vagues ou présentées comme certaines
* **Relecteur :** `egm-style`
* **Lignes :** 29, 35
* **Problème :** « chacun aura sa propre idée » prête une intention à un système ; « sera réinventé différemment à chaque session » présente un risque comme une certitude.
* **Correction proposée :** « risque d'utiliser une définition différente », « risque d'être réimplémenté différemment ».

#### style-1-10 : quantités floues
* **Relecteur :** `egm-style`
* **Lignes :** 26, 37, 49
* **Problème :** « en milliers de copies », « un petit nombre d'interfaces », « des milliers de parties générées ».
* **Correction proposée :** donner un ordre de grandeur ou renvoyer à la liste (section 7), ou retirer le qualificatif.

#### style-1-11 : la signature de `step` change entre l. 43 et l. 163
* **Relecteur :** `egm-style`
* **Lignes :** 43, 163
* **Problème :** `graine` / `graine_du_monde`, `nouvel état` / `nouvel_état`.
* **Correction proposée :** une seule signature, reprise à l'identique.

#### style-1-12 : « jouet » familier et non quantifié
* **Relecteur :** `egm-style`
* **Lignes :** 74, 176
* **Correction proposée :** « banc d'essai simplifié », en disant quelles opérations il omet.

#### style-1-13 : adverbe inutile à côté de chiffres
* **Relecteur :** `egm-style`
* **Lignes :** 346
* **Correction proposée :** supprimer « nettement » ; les chiffres suffisent.

#### style-1-14 : « plus tôt que prévu » sans calendrier de référence
* **Relecteur :** `egm-style`
* **Lignes :** 178, 360
* **Problème :** aucun calendrier n'est écrit, la RFC ne fixe pas de date ; « à la demande du propriétaire » n'apporte rien de technique.
* **Correction proposée :** « La mesure démarre à M1. »

#### style-1-15 : termes et symboles non définis
* **Relecteur :** `egm-style`
* **Lignes :** 127, 180, 189, 220, 230, 273
* **Problème :** N dans « à N exemplaires » ; « seul » ambigu ; « la population visée » ; « changement de rang » (quel rang ?) ; K désigne deux grandeurs (ordres par tick l. 220, ancienneté de l'argent inactif l. 273) ; `correlation_id` non défini ; « personnage » (l. 220) au milieu d'une section qui dit « acteur ».
* **Correction proposée :** définir chaque terme ou renvoyer à un réglage nommé ; deux symboles différents à la place de K.

#### style-1-16 : pléonasme et contradiction sur les segments Parquet
* **Relecteur :** `egm-style`
* **Lignes :** 146, 205
* **Problème :** « lus en lecture seule » est redondant, et le schéma annote les segments « (lecture seule) » alors que le serveur y écrit.
* **Correction proposée :** « ajoutés par le serveur, lus par DuckDB » et « (DuckDB n'y écrit pas) ».

#### style-1-17 : contenus répétés à plusieurs endroits
* **Relecteur :** `egm-style` (aussi relevé par `egm-structural`)
* **Lignes :** 20 et 61-62 ; 68, 246 et 414 ; 204 et 390 ; 246 et 435-438
* **Problème :** exclusions du document, « arrêts courts, temps du jeu suspendu », réversibilité de MessagePack et procédure de mise à jour écrits deux ou trois fois. Avec des agents sans mémoire, les copies finiront par diverger (c'est déjà le cas pour le seuil Rust, voir design-1-7).
* **Correction proposée :** une seule occurrence par contenu, avec des renvois.

#### style-1-18 : mots non mesurés
* **Relecteur :** `egm-style`
* **Lignes :** 246, 285, 307, 456
* **Problème :** « journal récent », « si la confiance baisse », « lecture explicite » (voir aussi design-1-15).
* **Correction proposée :** une durée en ticks pour « récent », un événement déclencheur pour la confiance, une action observable pour la lecture (par exemple un commentaire d'approbation sur la pull request).

#### style-1-19 : jugements subjectifs dans les alternatives et le plan
* **Relecteur :** `egm-style`
* **Lignes :** 251, 347-348, 353, 371, 377, 401
* **Problème :** « difficile à relire », « plus lisibles », « un seul fichier lisible », « une frontière qui tend à se brouiller », « forcément mauvais », « trop lent… trop gourmand » sans chiffre, « un second projet aussi gros que le jeu ».
* **Correction proposée :** remplacer par des faits, des estimations chiffrées ou le conditionnel.

#### style-1-20 : question ouverte cachée dans le plan (PufferLib)
* **Relecteur :** `egm-style`
* **Lignes :** 251, 70-76
* **Problème :** « PufferLib est à évaluer : son état actuel n'est pas vérifié » n'est pas dans Open Questions, et « état actuel » est flou.
* **Correction proposée :** l'ajouter aux questions ouvertes en disant quoi vérifier (maintenance, compatibilité).

#### style-1-21 : renvoi en avant vers le hook
* **Relecteur :** `egm-style`
* **Lignes :** 293, 325
* **Problème :** « Comme le hook » (l. 293) cite le hook avant sa présentation (l. 325).
* **Correction proposée :** présenter le hook avant les permissions, ou écrire « comme le hook local (voir plus bas) ».

#### style-1-22 : libellés de domaines différents
* **Relecteur :** `egm-style`
* **Lignes :** 119, 267
* **Problème :** « avancement du projet » d'un côté, « projet » de l'autre.
* **Correction proposée :** un seul libellé.

---

## Ce qui reste supposé

- Les numéros de ligne de la RFC et les mesures faites sur le schéma ASCII viennent des relecteurs ; la synthèse n'en a revérifié qu'une partie (RFC l. 76, 88, 232).
- Les affirmations sur le comportement par défaut de GitHub (contournement par l'administrateur), de SQLite WAL (`synchronous=FULL`) et de `ruff` TID251 sont celles des relecteurs. Elles n'ont pas été vérifiées dans une documentation ni par un outil pendant cette synthèse.
