# MMO de gestion spatiale en ASCII avec agents IA entraînés en local

* **Auteur :** Thomas (thom.bruyer)
* **Date :** 2026-10-31
* **Statut :** RFC close le 2026-10-31, dépassée par [architecture-niveau-1.md](./architecture-niveau-1.md)

**Dépassée pour l'architecture et les jalons** par [architecture-niveau-1.md](./architecture-niveau-1.md), qui fait foi. Les renvois « §N » ci-dessous désignent ce document, pas les sections de cette RFC. Écarts connus :
- Décision acquise n° 12 : l'agent de code utilise les identifiants du propriétaire, et non un compte séparé ([§10 du niveau 1](./architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia)).
- Ordre de construction et critères de sortie ([§11 du niveau 1](./architecture-niveau-1.md#11-le-découpage-en-documents-de-niveau-2)). Le critère de M0 devient : une pull request qui touche un chemin protégé est « étiquetée et signalée » au lieu d'être « bloquée ».
- Protocole en mémoire et client Textual dès M1, au lieu de M3 ([§1 du niveau 1](./architecture-niveau-1.md#1-les-composants-et-les-paquets)).
- « Ordres acceptés » devient « ordres soumis » ([§3 du niveau 1](./architecture-niveau-1.md#3-les-sources-de-vérité)).
- Décision acquise n° 13 : les preuves sont produites par la CI et par des scripts identifiés ([§9bis du niveau 1](./architecture-niveau-1.md#9bis-où-tourne-quoi)).
- Déclencheur Rust : il porte sur un verdict complet, soit 5 entraînements, et non sur un seul ([§2 du niveau 1](./architecture-niveau-1.md#2-le-noyau-de-simulation)).
- Décision n° 6 après revue (retour arrière) et autres décisions du 2026-10-31 : pas d'ADR. Elles restent dans le document de niveau 1 ([§7 du niveau 1](./architecture-niveau-1.md#7-les-versions-et-les-migrations)).
- Vocabulaire : « agent » ne désigne plus que l'agent de code ([glossaire](../glossaire.md)).
- Points à vérifier tranchés ou repoussés : le stockage de MLflow est remplacé par un serveur sur le PC d'entraînement ([§8 du niveau 1](./architecture-niveau-1.md#8-lentraînement)) ; `textual-serve` est repoussé ([Future Improvements du niveau 1](./architecture-niveau-1.md#future-improvements)).

## Vue d'ensemble

Un jeu en ligne, persistant, de gestion spatiale, affiché en ASCII. Le joueur dirige une corporation minière : il extrait du minerai, organise le transport, gère une flotte de vaisseaux de types différents, vend sur un marché, et affronte concurrents et pirates. C'est un jeu de gestion, pas un jeu d'action. Le monde avance par « ticks » de quelques secondes et continue de tourner quand le joueur est déconnecté.

Le jeu s'inspire ouvertement des systèmes d'EVE Online (économie produite par les joueurs, zones plus ou moins sûres, transport risqué, corporations) et du rythme d'OGame (ordres donnés puis exécutés). Il reste un jeu original : univers, noms, règles et chiffres propres.

Sa particularité : **des agents IA jouent dans le même univers que les humains, avec exactement les mêmes règles et par le même protocole.** Ce sont de petits réseaux de neurones qui apprennent à jouer par renforcement, entraînés sur le PC du propriétaire (RTX 4070 Ti Super), hors ligne, dans des copies accélérées du jeu, avant d'être déployés. Les modèles de langage ne serviront qu'au dialogue. Plus tard, d'autres personnes pourront brancher leurs propres agents.

Le projet comprend trois systèmes conçus ensemble :

1. **Le jeu** : la simulation, le serveur et le client ASCII.
2. **L'entraînement des agents** : les environnements accélérés, l'entraînement par métier et l'évaluation.
3. **L'observabilité et le pilotage** : la santé de l'économie, la progression des agents, l'avancement du projet et les journaux.

Le propriétaire est seul. Il joue le rôle de responsable et de concepteur : il ne lit pas le code. Tout le code est écrit par des agents de code IA, sous des garde-fous qu'il peut vérifier sans lire le code.

## Analyse

Six relecteurs ont examiné le concept sans connaître la conversation qui l'a produit. Ils ont relevé 9 problèmes bloquants, 21 majeurs et 8 mineurs. Cette section les regroupe par thème, du plus grave au moins grave.

### 1. Le périmètre : trois produits pour une seule personne

Le concept réunit trois produits : un MMO, une plateforme de recherche en apprentissage par renforcement et une suite d'analyse de données. S'y ajoute un processus de contrôle lourd. Les six relecteurs l'ont signalé.

Le risque concret : si l'économie dérive, impossible de savoir si la cause est une règle, un agent, le réseau ou une institution scriptée, puisque tout aura été construit en même temps. Un monde en ligne et persistant dès le premier jour fige aussi les mauvais chiffres du début.

**Réponse retenue :** construire d'abord un noyau hors ligne, sur un seul processus, puis ajouter les couches une à une (voir « Décisions clés »).

### 2. La source de vérité : les ordres, pas les événements

J'avais proposé que tout se calcule à partir des événements émis par la simulation. Les relecteurs ont montré que c'est faux tel quel. Les événements sont un *résultat* (« le vaisseau X a extrait 40 unités »). Ils permettent de redessiner le passé, mais pas de le rejouer. Il serait alors impossible :
- de retrouver le tick où deux exécutions divergent ;
- de tester une modification de règle sur une partie réelle ;
- de corriger un historique abîmé par un bug.

**Réponse retenue :** trois éléments distincts.
- **Le journal des ordres acceptés**, dans leur ordre d'application, avec la graine aléatoire et la version des règles. C'est lui qui permet de rejouer.
- **Des instantanés de l'état**, versionnés, pour repartir d'un point donné.
- **Les événements**, recalculables, chacun avec sa version de schéma. Ils restent l'interface commune pour l'analyse, les récompenses d'entraînement et le client.

Un rejeu n'est garanti que pour une même version des règles, à partir d'un instantané.

### 3. Le déterminisme se conçoit, il ne s'affirme pas

« Même état, même graine, mêmes ordres, même résultat » ne tient pas en Python sans précautions. Les pièges relevés :
- l'ordre de parcours d'un ensemble de chaînes varie d'une exécution à l'autre ;
- les nombres à virgule flottante donnent des résultats différents selon la plateforme et selon le langage ;
- `round()`, `//` et `%` ne se comportent pas comme en Rust ;
- un générateur aléatoire unique fait que chaque nouveau tirage décale tous les suivants. Chaque modification changerait alors toutes les empreintes de référence, et l'agent de code apprendrait à « mettre à jour les références » au lieu de corriger.

**Réponse retenue :**
- uniquement des nombres entiers (ou à virgule fixe) dans les règles ;
- un parcours toujours trié par identifiant ;
- un générateur aléatoire « à clé » : chaque tirage dépend de (graine du monde, tick, entité, motif), pas des tirages précédents ;
- une empreinte calculée par composant, pour savoir *où* la divergence se produit ;
- des contrôles automatiques : imports interdits dans la simulation (`math`, `random`, `time`, `os`, réseau), rejet des nombres flottants, rejeu sous deux configurations différentes, versions de Python et des dépendances figées.

### 4. Les garde-fous sur le code écrit par l'IA peuvent être contournés

C'est le point qui touche le plus directement à votre méfiance. Tels que je les avais décrits, les garde-fous ne tiennent pas :
- **La CI de GitHub exécute les fichiers de configuration de la branche proposée.** Un agent peut affaiblir les contrôles dans la même pull request (configuration des tests, du linter, de la mutation, de la CI elle-même), et tout reste vert.
- **Verrouiller le texte des scénarios en français ne verrouille pas ce qu'ils testent.** Chaque phrase est reliée à du code de test (les « définitions d'étapes »). Si c'est l'agent qui écrit ce code, il décide de ce que la phrase vérifie réellement.
- **Si l'agent utilise votre compte GitHub,** chaque pull request semble venir de vous, et l'agent peut fusionner lui-même.
- **Le hook local de Claude Code se contourne facilement** (pousser vers `master` sous un autre nom de branche, script écrit sur le disque, `gh pr merge`).

**Réponse retenue :**
- un compte GitHub séparé pour l'agent, avec un jeton limité à ce dépôt, sans droit d'administration ;
- vous seul propriétaire d'une liste de chemins protégés : configuration CI, scénarios, définitions d'étapes, configuration des tests et des outils, références. Toute modification de ces chemins exige votre approbation ;
- un contrôle qui s'exécute depuis la branche principale (pas depuis la branche proposée) et signale bruyamment toute modification de ces chemins ;
- aucune exception, même pour l'administrateur ;
- une protection côté serveur GitHub, qui suppose un abonnement payant ou un dépôt public (à trancher en premier, voir « Questions ouvertes ») ;
- le hook local reste en place comme seconde ligne de défense, pas comme protection principale.

### 5. Le temps de jeu n'est pas défini, et l'ordre d'arrivée favorise les bots

« Des ordres à quelques secondes d'intervalle » peut désigner quatre choses : la durée d'un tick, une limite d'ordres par joueur, une fenêtre de collecte des ordres, ou la durée d'une action. Rien ne dit ce qui se passe quand deux mineurs visent le même astéroïde, ou quand deux acheteurs visent la même offre. Si les ordres sont traités dans leur ordre d'arrivée, un bot installé à côté du serveur gagne toujours contre un humain à distance.

**Réponse retenue :**
- dans les règles, le temps se compte uniquement en ticks. La durée réelle d'un tick (par exemple 5 secondes) est un réglage du serveur ;
- les ordres reçus pendant le tick T s'appliquent au tick T+1, par phases : déplacement, minage, commerce, combat, règlement ;
- les égalités se tranchent par un tirage reproductible, jamais par l'ordre d'arrivée ;
- un serveur en retard ralentit le temps du jeu au lieu de sauter des règles.

### 6. Égalité des règles ne veut pas dire équité

Avec la même limite par seconde, un bot qui ne dort jamais donne plusieurs fois plus d'ordres par jour qu'un humain. Il capte les opportunités de marché, les primes et les cibles déconnectées.

**Réponse retenue :**
- un budget d'actions par personnage, en temps de jeu ;
- des ordres permanents et conditionnels accessibles à tous, pour que la compétition porte sur les décisions et non sur la présence ;
- des règles de sécurité hors ligne (par exemple : un vaisseau à quai est protégé) ;
- un plafond de personnages par opérateur ;
- écrire explicitement ce qui n'est pas égalisé (présence, temps de réaction) ;
- des règles qui peuvent varier selon le rang ou le métier, jamais selon que le joueur est un humain ou une IA.

**Décidé :** les joueurs IA sont signalés comme tels dans le jeu (voir « Décisions prises après la revue »).

### 7. Le type d'agent n'est pas choisi, et c'est lui qui fixe le budget de calcul

« Petits modèles entraînés » peut désigner deux choses très différentes :
- **un petit réseau de neurones** qui lit des données structurées (position, cargaison, prix) et choisit une action. Il s'entraîne vite et tourne même sur processeur ;
- **un petit modèle de langage** (0,5 à 4 milliards de paramètres) entraîné par renforcement. C'est lent, fragile, et la carte ne pourra servir que quelques dizaines d'agents au plus (estimation, à mesurer).

Autre contrainte : la carte graphique ne peut pas entraîner et servir en même temps. Pendant un entraînement, les agents en jeu, y compris ceux qui gèrent votre corporation en votre absence, s'arrêteraient. Avec de petits réseaux servis sur processeur, ce conflit disparaît pour les métiers économiques.

**Réponse proposée par les relecteurs :**
- des réseaux structurés entraînés par renforcement (PPO) pour les métiers économiques (mineur, transporteur, marchand), servis sur processeur en production ;
- des modèles de langage seulement pour les rôles conversationnels et les décisions rares de haut niveau ;
- un comportement scripté de secours pour chaque rôle tenu par un agent ;
- des créneaux séparés pour l'entraînement et le service ;
- un banc d'essai écrit : temps de décision et mémoire vidéo à 1, 10, 100 et 1000 agents.

**Décision du propriétaire (2026-10-31) :** proposition adoptée. Les joueurs IA des métiers économiques sont de petits réseaux de neurones qui apprennent à jouer. Les modèles de langage ne serviront éventuellement qu'au dialogue.

La carte est une **RTX 4070 Ti Super** (16 Go de mémoire vidéo selon la fiche du constructeur, non vérifié sur la machine). Elle n'est **pas** dans la machine de développement actuelle, qui n'a qu'un circuit graphique Intel UHD (constaté avec `lspci`). L'entraînement se fera donc sur une autre machine, ce que l'architecture doit prévoir : l'environnement d'entraînement doit pouvoir s'installer et tourner sur le PC à carte graphique, et ses résultats (modèles, métriques MLflow) doivent revenir vers le projet.

### 8. L'économie : un registre comptable, et des objectifs qui se contredisent

**Il faut un registre en partie double dès le premier jour.** Avec de l'argent en nombres flottants et des portefeuilles modifiés directement, chaque paiement (contrat, prime, assurance, achat PNJ) devient une source d'argent impossible à tracer. Chaque mouvement doit donc être une écriture entre deux comptes typés (émission, taxes, caisse d'assurance, séquestre, portefeuille, corporation), en unités entières. Une règle est vérifiée à chaque tick : la masse monétaire d'aujourd'hui égale celle d'hier, plus les entrées, moins les sorties. Ajouter ce registre plus tard, dans un monde persistant, obligerait à migrer tout l'historique.

**Plusieurs objectifs économiques se contredisent :**
- **« Pas de thésaurisation » contredit « portefeuille personnel intouchable » :** ce portefeuille est la cachette parfaite. Un joueur rationnel videra le portefeuille de sa corporation vers le sien.
- **Les taxes ne frappent que l'activité.** L'argent qui dort n'est jamais touché.
- **La destruction d'objets retire des biens, pas de l'argent.** Elle relance la demande, mais ce n'est pas une sortie d'argent.
- **Une assurance payée par le gouvernement transforme la destruction en planche à billets :** on détruit soi-même ses vaisseaux pour toucher l'indemnité. Un agent entraîné le trouvera vite.
- **Un plafond d'émission fixe ne réagit pas à la situation.** Il faut une règle d'émission qui s'ajuste aux mesures, à l'intérieur de bornes fixées dans le code.

**Réponse retenue :**
- chaque objectif devient une mesure : croissance de la masse monétaire dans une fourchette, indice de prix sur un panier fixe, vitesse de circulation, part de l'argent inactif depuis plus de K ticks, inégalité des portefeuilles ;
- un mécanisme anti-thésaurisation explicite (frais de garde, entretien, taxe sur les transferts de la corporation vers le portefeuille personnel), ou la décision assumée d'accepter l'argent qui dort ;
- une assurance bornée (indemnité inférieure à la valeur, franchise, primes qui sortent du circuit, pas d'indemnité en cas de destruction volontaire), repoussée après le tableau de bord du registre ;
- des tableaux de bord calqués sur le rapport économique mensuel d'EVE.

### 9. Rien n'est versionné

Renommer un seul événement casse en silence les récompenses d'entraînement, les notebooks et le rejeu. Un agent entraîné est figé sur le format d'observation qu'il a appris : un changement de protocole le dégrade sans prévenir.

**Réponse retenue :** un numéro de version sur les instantanés, les événements, le protocole, le format d'observation et chaque agent déployé, avec des migrations numérotées et testées. Le serveur refuse un agent incompatible. Chaque entraînement enregistre les versions qu'il a utilisées. Une mise à jour suit toujours la même procédure : arrêt des ticks, instantané, migration, vérification des invariants, reprise. Pendant l'arrêt du serveur, le temps du jeu est suspendu.

### 10. « L'agent s'améliore » n'a pas de définition

Une courbe de récompense qui monte peut être du bruit, du sur-apprentissage ou de la triche. Vous ne pourrez pas faire la différence.

**Réponse retenue, par métier :**
- une mesure nommée, valorisée à prix de référence fixes (pour le mineur : valeur nette de minerai livré pour 1000 ticks) ;
- trois points de comparaison : un agent aléatoire, un agent scripté et la version précédente ;
- des cartes d'évaluation mises de côté, au moins 5 entraînements, un intervalle de confiance ;
- un verdict en une phrase, généré automatiquement : « la v3 bat l'agent scripté de X % ± Y sur N cartes d'évaluation ». Vous fixez X ; les relecteurs suggèrent 10 % pour la première tranche ;
- chaque évaluation indique aussi combien d'argent l'agent a tiré des sources d'argent du jeu, pour faire apparaître les failles exploitées.

### 11. La preuve vidéo, telle que prévue, n'est pas fiable

Une vidéo produite par l'agent lui-même peut être choisie pour bien paraître. Elle ne montre rien pour une modification de l'économie. Et elle encombre le dépôt.

**Réponse retenue (qui conserve votre exigence de vidéo) :** les preuves sont **générées par la CI** à partir du code exact de la pull request, pas par l'agent :
- le rapport d'exécution des scénarios en français ;
- un panneau fixe de 3 à 5 métriques comparées à la branche principale ;
- un rejeu ;
- des captures d'écran du client pour les modifications d'interface ;
- **une vidéo rendue par la CI à partir d'un rejeu déterministe**, et non enregistrée à la main.

Le type de preuve dépend du type de modification : interface, simulation et économie, ou entraînement.

### 12. Les autres points majeurs

- **Les informations visibles peuvent fuiter.** Une seule fonction calcule ce qu'un joueur voit. Le client, les agents et l'entraînement l'utilisent tous, et des tests prouvent que les champs cachés ne sortent jamais. On n'entraîne jamais les agents sur des instantanés bruts du monde réel, sinon vos agents apprendraient grâce à des informations invisibles aux joueurs.
- **Trop d'outils d'observabilité au départ.** Grafana suppose aussi Prometheus et Loki, ce qui fait 6 ou 7 interfaces à surveiller. Phase 1 : DuckDB et marimo sur des fichiers Parquet, MLflow dès que l'entraînement commence, et une page d'accueil unique avec un statut vert / orange / rouge par domaine. Le visualiseur de rejeu est le client Textual en mode rejeu : un seul affichage, pas deux. Grafana viendra quand un serveur tournera 24 h/24, et seulement pour la santé technique.
- **Volume des événements.** Un événement par entité et par tick fait exploser le stockage. Les relecteurs estiment 1,7 Go par jour pour 200 acteurs (chiffre non recalculé). Règle : pas d'événement par entité et par tick. Une activité continue s'enregistre comme un début et une fin, avec un débit.
- **Test de mutation.** Il coûte trop cher sur tout le dépôt à chaque pull request. On le lance seulement sur les modules modifiés, avec un score qui ne peut pas baisser, et un passage complet chaque nuit. Le contrôle principal à chaque pull request : des tests de propriétés (l'argent est conservé, aucune cargaison n'est négative, le résultat est reproductible).
- **Vitesse de la simulation pour l'entraînement.** L'apprentissage par renforcement demande de 1 à 10 millions de pas par métier. Une simulation Python pourrait demander des jours par métier (estimation non vérifiée). On mesure dès le premier jour le nombre de pas par seconde : c'est ce chiffre qui décidera, preuve à l'appui, du passage éventuel à Rust.
- **Déployer un agent dans le monde.** Un agent entraîné exploitera les bugs. Il faut un arrêt d'urgence par agent, un mode observation sans effet, puis 1 agent, puis N, un disjoncteur sur les variations anormales de portefeuille et un retour à la version précédente.
- **Persistance.** Un ordre est écrit sur disque avant d'être confirmé. Un tick est enregistré d'un bloc. Après un plantage, on repart d'un instantané et on rejoue le journal. Sauvegarde chaque nuit hors de la machine. Plus tard, le serveur ira sur un VPS, et votre PC s'y connectera comme un joueur ordinaire, ce qui prouve aussi que vos agents n'ont aucun accès privilégié.
- **Mots ambigus.** « Agent » a cinq sens (joueur IA, PNJ scripté, bot tiers, agent de code, relecteur) et « rôle » en a quatre (rang en corporation, métier entraîné, rôle PNJ spécial, fonction gouvernementale). Un glossaire impose un mot par sens : *joueur IA*, *PNJ*, *institution*, *agent de code* ; *rang et permissions*, *métier*, *fonction*.
- **Corporations et vol.** Permissions vérifiées au moment de l'application, dans un ordre fixe. Un changement de rang prend effet au tick suivant. Le journal public de la corporation est tiré du registre. Plafonds de retrait optionnels par rang. Toute nouvelle permission est refusée par défaut. **Le vol ne doit pas exister avant que l'historique public existe.**
- **Gouvernement et élections.** Celui qui crée le plus de comptes gagne les élections. Avant d'ouvrir les fonctions publiques, il faut un coût par compte (votes pondérés par l'ancienneté, l'enjeu ou la réputation), un plafond de comptes par opérateur, et l'opérateur de chaque compte visible dans l'historique.
- **Objectifs choisis par les agents eux-mêmes.** Ils supposent un entraînement conditionné par l'objectif. À repousser, ou à limiter à des paramètres choisis dans une liste que vous fixez.
- **Votre temps de relecture est le vrai goulot.** Une seule pull request de fonctionnalité ouverte à la fois. Vous ne relisez que deux choses : les scénarios avant le code et un résumé d'un écran par pull request. Les jalons sont des portes à franchir. Un scénario « les dix premières minutes d'un joueur humain » fait partie de la validation de chaque tranche.

### 13. Travaux existants à étudier

Ils répondent en partie à la question « personne n'a fait ça » (état actuel non vérifié) :
- **Neural MMO** et **PufferLib** : apprentissage par renforcement massivement multi-agents dans des jeux de type MMO.
- **Salesforce AI Economist** : des agents entraînés par renforcement face à un gouvernement, lui aussi entraîné, qui fixe les impôts. C'est très proche de votre modèle gouvernement-économie.
- **Screeps** : un monde persistant où des programmes jouent 24 h/24 sous des quotas de calcul.
- **Evennia** : un cadre Python pour serveurs de MUD et de MMO textuels.
- **SpaceMolt** (MMO spatial textuel réservé aux IA) et **Golemreach** (humains et IA dans le même monde), trouvés pendant le brainstorm.

### Points mineurs

- Abandonner « portable en Rust » comme contrainte (les relecteurs ne sont pas d'accord sur la gravité du point). Garder la pureté et le déterminisme, et une seule jonction : `step(état, ordres, graine, réglages) -> (nouvel état, événements)`.
- Calculer l'empreinte de tout l'état à chaque tick coûte cher en production : chaque tick en CI sur de petits cas, tous les N ticks en production.
- `textual-serve` lance probablement un processus Python par session navigateur (non vérifié). Terminal et SSH d'abord.
- Le nom de la branche principale : vous dites « master », GitHub crée « main » par défaut. Il faut le même nom partout.
- Les agents de code reprendront spontanément le vocabulaire d'EVE (ISK, CONCORD, null-sec). Il faut une liste de noms validés par vous et un contrôle CI qui refuse les termes interdits.
- La mort d'un personnage et les règles de perte ne sont pas définies. Il faut une table de pertes sous forme de données.
- La topologie de la carte est fondatrice : une « petite région avec des hubs » est déjà un graphe. À décider dès le premier jalon.

## Objectifs et non-objectifs

* **Objectifs inclus :**
  - un jeu de gestion spatiale original, en ASCII, persistant, au tick, centré sur les corporations minières, la logistique, le marché et la piraterie ;
  - des joueurs IA soumis exactement aux mêmes règles que les humains, par le même protocole, avec des règles d'équité écrites ;
  - un entraînement hors ligne par métier mesurable sur la RTX 4070 Ti Super, avec un verdict d'amélioration chiffré ;
  - une économie avec registre en partie double, des objectifs mesurés, des entrées et sorties d'argent explicites ;
  - une observabilité commune aux trois systèmes, construite sur des outils existants ;
  - des garde-fous appliqués côté serveur GitHub, et des preuves générées par la CI, vidéo comprise.
* **Non-objectifs (pour l'instant) :**
  - un monde en ligne et persistant dès le premier jour ;
  - un entraînement en direct dans le monde partagé ;
  - des modèles de langage pour les métiers économiques ;
  - Rust ;
  - Grafana et Loki en phase 1 ;
  - élections, banques, guildes, cartels, assurance et PNJ conversationnels dans la première tranche ;
  - les agents de tiers et le client navigateur ;
  - le lore (repoussé, mais il devra accueillir les grandes institutions : gouvernement, armée, guildes de marchands et de transporteurs, cartels, grandes corporations minières, industriels, armuriers, pirates).

## Alternatives écartées

| Alternative | Raison du rejet |
| :-- | :-- |
| Rust dès le départ | Le propriétaire ne le lit pas. L'entraînement reste en Python. La vitesse de la simulation n'est pas mesurée. On passera à Rust si le nombre de pas par seconde le justifie. |
| Un modèle de langage pour chaque métier | Lent, trop gourmand pour une seule carte graphique, difficile à entraîner par renforcement. Gardé pour les rôles conversationnels. |
| Un entraînement en direct dans le monde persistant | Trop peu de décisions par jour, des risques de triche visibles par les joueurs, et la carte graphique serait occupée en permanence. |
| L'apprentissage par renforcement sur un monde aux minuteurs de plusieurs heures (modèle OGame) | Trop lent pour apprendre, et trop lent pour le rythme souhaité. |
| Les événements comme unique source de vérité | Impossible de rejouer, de corriger ou de tester une modification de règle. Remplacé par journal des ordres + instantanés + événements recalculables. |
| De l'argent en nombres flottants, sans registre | Sources d'argent impossibles à tracer, résultats non reproductibles. |
| Un monde en ligne et persistant dès le premier jour | Mauvais chiffres figés, causes d'une dérive impossibles à isoler. |
| Le hook local comme seul garde-fou | Contournable par plusieurs moyens simples. |
| Une vidéo enregistrée par l'agent comme preuve d'acceptation | Peut être choisie pour bien paraître. Remplacée par une vidéo rendue par la CI à partir d'un rejeu. |
| Le test de mutation complet à chaque pull request | Trop lent. Remplacé par les modules modifiés plus un passage nocturne. |
| Un compte, une voix aux élections | Celui qui crée le plus de comptes gagne. |
| Une application d'observabilité entièrement sur mesure | Un second projet aussi gros que le jeu. Remplacée par des outils existants, avec des vues sur mesure seulement pour le rejeu et les flux de corporation. |
| Une monnaie fondée sur le troc des ressources (modèle OGame) | Commerce trop rudimentaire pour l'économie visée. |
| Une interface entièrement web dès le départ | Textual en terminal suffit pour un seul joueur. Le protocole commun permet de changer de client plus tard. |
| gRPC, Postgres, Kubernetes, migrations sans interruption | Disproportionné pour un projet à un seul serveur. WebSocket, SQLite et des arrêts courts suffisent. |

## Décisions clés et étapes suivantes

### Décisions acquises pendant le brainstorm

1. Jeu de gestion, pas d'action. Temps en ticks, et ordres collectés pendant un tick appliqués au suivant, par phases, avec départage reproductible.
2. Mêmes règles et même protocole pour les humains et les joueurs IA. Les règles peuvent varier selon le rang ou le métier, jamais selon le type de joueur.
3. Portefeuille personnel intouchable, tout le reste destructible. Le vol en corporation est possible si on a les droits, sans règle pour l'empêcher. La sanction est sociale, ce qui suppose un historique public d'abord.
4. Rangs et permissions dans les corporations. Un joueur IA peut monter au-dessus d'un humain et lui confier des tâches facultatives.
5. Joueurs et joueurs IA peuvent devenir pirates et former des corporations de pirates.
6. Économie : le gouvernement émet l'argent (contrats, primes) et le retire (taxes, frais), les banques le font circuler, des bornes inscrites dans le code encadrent le gouvernement. Les fonctions publiques ne s'ouvrent aux joueurs qu'ensuite.
7. Institutions majoritairement scriptées au début.
8. Simulation en Python : pure, déterministe, en nombres entiers, avec générateur aléatoire à clé.
9. Source de vérité : journal des ordres + instantanés + événements recalculables et versionnés.
10. Client Textual en terminal.
11. Observabilité sur outils existants : DuckDB et marimo d'abord, puis MLflow. Grafana plus tard.
12. Garde-fous côté serveur GitHub, chemins protégés, compte séparé pour l'agent de code, preuves générées par la CI.
13. Preuve exigée pour chaque livrable, vidéo de préférence.

### Ordre de construction proposé

| Jalon | Contenu | Critère de sortie |
| :-- | :-- | :-- |
| **M0** | Garde-fous : dépôt public, protection côté serveur, compte de l'agent, chemins protégés, CI de base, `.gitignore`, scanner de secrets (pre-commit et CI), glossaire, liste de noms | Une pull request de test qui modifie un chemin protégé est bloquée, et un faux secret est refusé avant le commit et en CI |
| **M1 – Tranche 0** | Noyau déterministe hors ligne : carte en graphe (3 à 5 nœuds), 1 ou 2 minerais, minage, transport, vente à des PNJ à prix fixe, une taxe, perte de vaisseau, registre en partie double, journal des ordres, instantanés, empreintes, test de rejeu | Un notebook marimo montre masse monétaire, entrées, sorties et prix stables sur 100 000 ticks, et vous jugez la boucle amusante en y jouant |
| **M2** | Schéma d'événements v1, stockage Parquet, DuckDB et marimo, page d'accueil de statut | Les métriques de M1 sont lisibles sans lire de code |
| **M3** | Protocole v1, client Textual local, fonction d'observation unique | Le scénario « dix premières minutes d'un joueur » se joue |
| **M4** | Environnement d'entraînement, agent scripté de référence, mineur entraîné par PPO, MLflow, mesure de capacité de la 4070 Ti Super | Verdict chiffré « le mineur bat l'agent scripté de X % » |
| **M5** | Serveur, persistance, migrations, déploiement d'agents | Le monde tourne sans vous, un plantage se rattrape sans perte |
| **M6** | Marché entre joueurs, corporations et permissions, pirates scriptés | Une corporation à deux membres fonctionne de bout en bout |
| **Plus tard** | Assurance, institutions, élections, banques, PNJ conversationnels, agents de tiers, navigateur, lore | — |

### Décisions prises après la revue (2026-10-31)

1. **Joueurs IA :** petits réseaux de neurones entraînés par renforcement pour les métiers économiques. Modèles de langage seulement pour le dialogue, plus tard.
2. **GitHub :** dépôt public. La protection de branche y est disponible sans abonnement. Conséquences : aucun secret dans le dépôt (jetons, mots de passe), et la graine et la configuration du monde en ligne restent hors du dépôt, sinon n'importe qui pourrait calculer la carte et les tirages à l'avance.
3. **Thésaurisation :** acceptée au départ. On la mesure (part de l'argent inactif depuis plus de K ticks) sans la pénaliser. Le portefeuille personnel est sûr mais ne rapporte rien. Les banques rémunèrent les dépôts avec les intérêts payés par les emprunteurs, ce qui crée une incitation à faire circuler l'argent sans création monétaire. Des frais de garde ne seront ajoutés que si la mesure montre un problème. Raison : pénaliser l'argent qui dort punit d'abord le joueur humain absent quelques semaines.
4. **Signalement des joueurs IA :** discernables. Un joueur IA est signalé comme tel dans le jeu (profil, listes de membres, historique public). Le serveur connaît aussi le type de chaque joueur (champ `actor_kind` dans les événements), pour l'observabilité et l'équité. Ce choix rejoint la recommandation des relecteurs et devance les obligations de transparence de l'AI Act européen, dont l'application à un jeu reste à vérifier avant une ouverture au public. Les règles restent identiques : le signalement est une information, pas un traitement différent.
5. **Sécurité hors ligne :** principe d'EVE. Ce qui est à quai dans une station PNJ est protégé. Un vaisseau piloté personnellement quitte le monde peu après la déconnexion. Les vaisseaux confiés à la corporation (pilotés par des joueurs IA ou des ordres permanents) restent exposés. Les structures des joueurs sont attaquables, avec des délais de renfort qui laissent le temps de réagir. **Confirmé :** les stations PNJ sont indestructibles ; seules les structures des joueurs peuvent être détruites.
6. **Retour arrière :** décision technique. Avant chaque mise à jour, on rejoue le journal d'ordres récent sur la nouvelle version (sans effet sur le monde) pour détecter les écarts. En cas de retour arrière, on restaure l'instantané d'avant la mise à jour, et les ticks joués sur la nouvelle version sont perdus. Rejouer ces ordres sur l'ancienne version serait trompeur, car certains ordres n'y auraient pas de sens. Acceptable tant que le monde compte peu de joueurs. À consigner dans un ADR.
7. **Seuil d'amélioration :** deux règles distinctes.
   - *Promotion d'une nouvelle version :* elle remplace la précédente si elle fait mieux de façon statistiquement établie (borne basse de l'intervalle de confiance à 95 % au-dessus de zéro), quelle que soit la taille du gain, et sans anomalie dans le registre comptable. Un gain de 1 % suffit s'il est réel. Mais mesurer un écart de 1 % demande beaucoup plus de parties d'évaluation qu'un écart de 10 %.
   - *Critère du jalon M4 :* le premier mineur entraîné doit battre l'agent scripté d'au moins 10 %. Cela prouve que le réseau a appris quelque chose qu'un script simple ne fait pas.
   - Attention aux gains cumulés : 1 % par itération donnerait ×2,7 en 100 itérations et ×20 959 en 1000 (calculé). Dans la réalité, les gains s'essoufflent vite. Une suite de petits gains signale plus souvent un plafond, ou un agent qui exploite une faille, qu'un progrès sans fin.
8. **Branche principale :** `main`.
9. **Aucun secret dans le dépôt.** Aucune clé, aucun jeton, aucun mot de passe ne doit être poussé. Mesures, toutes dans le jalon M0 :
   - un `.gitignore` construit sur les modèles de référence (Python, environnements virtuels, caches, notebooks, données et modèles entraînés, fichiers d'éditeur) et qui exclut explicitement `.env*`, `*.key`, `*.pem`, les fichiers d'identifiants et la configuration du monde en ligne ;
   - un fichier `.env.example` sans valeurs réelles, pour documenter les variables attendues ;
   - un scanner de secrets avant chaque commit (par exemple `gitleaks` en hook pre-commit) et le même scanner en CI comme contrôle obligatoire ;
   - l'analyse des secrets et le blocage des push de GitHub, activés sur le dépôt public (disponibilité à vérifier au moment de la création) ;
   - les données lourdes (journaux d'événements, Parquet, modèles entraînés, exécutions MLflow) restent hors du dépôt.
10. **Machine d'entraînement :** la RTX 4070 Ti Super est sur un autre PC, accessible par le réseau local. L'environnement d'entraînement doit s'installer sur ce PC à partir du dépôt (versions figées), et les modèles et métriques reviennent par le réseau local (par exemple un serveur MLflow sur le réseau local). Aucun identifiant d'accès à ce PC ne va dans le dépôt.

### Points à vérifier (une tâche d'exploration chacun)

Protection de branche effective sur le dépôt public ; mémoire réelle de la RTX 4070 Ti Super et mise en place de l'environnement sur le PC qui la porte ; `textual-serve` ; support du français dans `pytest-bdd` ou `behave` ; stockage par fichiers de MLflow 3.x ; maintenance de PufferLib et SuperSuit ; tous les chiffres de capacité de la carte graphique, de pas par seconde et de volume d'événements ; état actuel de SpaceMolt et Golemreach.
