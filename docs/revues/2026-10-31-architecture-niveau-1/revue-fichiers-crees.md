# Revue EGM des fichiers créés ou modifiés par le plan du niveau 1

**Date :** 2026-10-31

**Référence :** /home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md. Sa section « Detailed Implementation Plan » (lignes 641 à 862) est le plan exécuté ; le reste fait office de spécification.

**Fichiers relus :**
- /home/ezpk/Projects/4X/CLAUDE.md
- /home/ezpk/Projects/4X/docs/glossaire.md
- /home/ezpk/Projects/4X/docs/feuille-de-route.md
- /home/ezpk/Projects/4X/docs/noms-valides.md
- /home/ezpk/Projects/4X/docs/termes-interdits.md
- /home/ezpk/Projects/4X/docs/adr/README.md
- /home/ezpk/Projects/4X/docs/designs/mmo-gestion-spatiale-ia.md (ligne de statut et note de tête, lignes 5 à 16)
- /home/ezpk/Projects/4X/docs/revues/2026-10-31-architecture-niveau-1/README.md

Les rapports déplacés dans `docs/revues/` n'ont pas été relus.

## État des relecteurs

| Relecteur | Statut | Tentatives |
| --- | --- | --- |
| `egm-codebase-details` | terminé | 1 |
| `egm-comprehension` | terminé | 1 |

Chaque relecteur a démarré sans contexte et n'a modifié aucun fichier.

## Bilan

| Sévérité | Nombre |
| --- | --- |
| Blocker | 0 |
| Major | 13 |
| Nit | 16 |

**Conformité au plan (egm-codebase-details) :**
- Les trois textes imposés « exactement » sont identiques au plan, au caractère près : `CLAUDE.md` (lignes 1 à 31, comparées aux lignes 745 à 775 du plan), la note de la RFC (lignes 802 à 811) et la phrase du README de `docs/revues/` (ligne 818). Seul écart : un titre ajouté, voir codebase-details-v-3.
- La recherche de seuils du Verification Plan (ligne 840) ne trouve rien. Une recherche plus large trouve un seul chiffre recopié (codebase-details-v-1).
- Glossaire :
  - les 97 termes des huit groupes à identifiant sont tous présents ;
  - la règle des trois cas est respectée partout ;
  - aucun identifiant n'est inventé et aucun terme n'est ajouté hors liste ;
  - seul le groupe « Mots à plusieurs sens » n'a pas d'entrée de tableau (codebase-details-v-2).
- `CLAUDE.md` contient chacune des règles listées par le Verification Plan (lignes 841 à 849). Aucune n'est absente ni déformée.
- Tous les liens relatifs et toutes les ancres sont valides.

**Point de méthode pour les constats sur `CLAUDE.md`.** Le texte de `CLAUDE.md` est imposé mot pour mot par le plan, et il est conforme. Les constats de compréhension sur ce fichier ne viennent donc pas d'une erreur d'exécution : ils portent sur le texte que le plan impose. Le document de niveau 1 a le statut `Approved`. Pour corriger ces points, le propriétaire doit d'abord modifier le texte imposé, à la ligne 745 et suivantes du niveau 1, puis `CLAUDE.md`. Il faut aussi modifier §10 si la règle elle-même change. Ces constats portent la mention « origine : texte imposé ». Il en va de même pour les fichiers dont le plan fixe une phrase.

**Sévérité recalculée.** egm-comprehension avait classé comprehension-v-1 en Blocker. La synthèse le ramène à Major. Le titre de la section concernée de `CLAUDE.md` (ligne 22) renvoie à §10. L'étape 5 de l'ordre de lecture (ligne 6) demande de lire les sections vers lesquelles une règle renvoie. Or §10 contient la liste des chemins protégés (niveau 1, lignes 433 à 440). Le lecteur n'est donc pas bloqué. Il doit seulement sortir de `CLAUDE.md` pour une règle de base.

## Constats par ordre de priorité (Major, puis Nit)

### codebase-details-v-1 : un plafond chiffré est recopié dans le glossaire (Major)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/glossaire.md, ligne 24 (opérateur)
- **Problème :** la définition « Elle a un plafond de comptes, réglable, qui vaut 1 pour un humain » recopie une valeur de §5 (niveau 1, ligne 305). La règle de précédence (plan, ligne 646) l'interdit. La recherche du Verification Plan ne l'attrape pas, car « 1 » ne figure pas dans sa liste.
- **Correction :** « Elle a un plafond de comptes, réglable (valeur pour un humain : voir §5). »

### codebase-details-v-2 : « agent » et « rôle » n'ont pas d'entrée de tableau (Major)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/glossaire.md, ligne 32
- **Problème :** les deux termes du groupe « Mots à plusieurs sens » (plan, ligne 688) sont traités dans un paragraphe. Ce paragraphe n'a ni identifiant ni lien, alors que le Verification Plan (ligne 852) demande une entrée par terme. Il ajoute aussi une règle absente du plan : « « Rôle » n'est pas employé seul ». Or la spécification écrit elle-même « Un *métier* est un rôle économique » (niveau 1, ligne 115).
- **Correction :** ajouter deux lignes de tableau :
  - `agent` | — | « Ne désigne que l'agent de code (voir joueur IA, référence scriptée, client tiers). » | Overview ;
  - `rôle` | — | « Voir les entrées métier et rang. » | Overview.

  Retirer « n'est pas employé seul ».

### comprehension-v-1 : la liste des chemins protégés n'est donnée nulle part hors du niveau 1 (Major, ramené de Blocker)
- **Relecteur :** `egm-comprehension`
- **Fichiers :** /home/ezpk/Projects/4X/CLAUDE.md, lignes 24 et 26 ; /home/ezpk/Projects/4X/docs/glossaire.md, ligne 141
- **Problème :**
  - La pull request de fonctionnalité « ne touche aucun chemin protégé », mais ni `CLAUDE.md` ni le glossaire ne disent quels chemins le sont.
  - Le lecteur ne devine pas que la pull request de scénarios en touche toujours un.
  - Il ne devine pas non plus que `CLAUDE.md`, le glossaire, la feuille de route et les deux listes de noms sont protégés.
- **Correction :** recopier dans `CLAUDE.md` les sept entrées de §10 (lignes 434 à 440), sous « Circuit des pull requests ». Ajouter : « La pull request de scénarios touche donc toujours un chemin protégé. » Origine : texte imposé.

### comprehension-v-2 : « revue EGM sans contexte » n'est pas définie, et on ne sait pas qui agit (Major)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 26
- **Problème :**
  - « EGM » n'est défini qu'à la ligne 8 du niveau 1.
  - La phrase est au passif. L'agent ne sait pas s'il lance la revue et s'il rédige le résumé en français.
  - Il ne sait pas non plus où placer ce résumé.
- **Correction :** ajouter « revue EGM » au groupe Projet du glossaire. Réécrire la règle à la voix active : qui lance la revue, et où va le résumé. Origine : texte imposé.

### comprehension-v-3 : les invariants de déterminisme sont donnés comme « non exhaustifs » (Major)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 29
- **Problème :**
  - Des interdits importants ne sont connus qu'en lisant §2 : pas de réseau, de disque ni d'horloge, pas de module non déterministe, pas de parcours direct d'un `set`.
  - Le lecteur ne sait pas quoi utiliser à la place de `/`, `//` et `%`.
  - « Générateur à clé » n'est pas défini.
- **Correction :** recopier dans `CLAUDE.md` les sept invariants de §2 (lignes 253 à 259) et retirer « non exhaustif ». Le plan permet à `CLAUDE.md` de résumer des règles. Ajouter « générateur à clé » au glossaire. Origine : texte imposé.

### comprehension-v-4 : on ne sait pas si les garde-fous sont actifs, et la frontière « vérifié / non vérifié » est inexacte (Major)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, lignes 18 à 20
- **Problème :**
  - « À partir du jalon M0 » peut se lire « dès le début de M0 » ou « une fois M0 livré ». Aujourd'hui, ni `.claude/` ni `.github/` n'existent : la synthèse l'a vérifié par Glob. Aucun garde-fou n'est donc actif.
  - La ligne 20 dit que « les autres interdictions ne sont vérifiées par aucun mécanisme ». Elle omet la protection de `main`, qui s'applique aussi aux administrateurs (§10, lignes 422 à 425).
  - Elle omet aussi des contrôles obligatoires qui vérifient des règles de la section « Code » : termes interdits à M0, contrats d'imports par `import-linter` à M1, invariants « vérifiés mécaniquement » (niveau 1, lignes 173, 252 et 455-456).
- **Correction :**
  - Écrire « une fois M0 livré », et ajouter : « Aujourd'hui, aucun de ces mécanismes n'est en place. »
  - Remplacer « les autres interdictions » par « les autres points de la liste Ne jamais ».
  - Mentionner la protection de branche et les contrôles obligatoires par jalon.

  Origine : texte imposé.

### comprehension-v-5 : l'identité GitHub de l'agent n'est pas dite, et « propriétaire » n'est pas défini (Major)
- **Relecteur :** `egm-comprehension`
- **Fichiers :** /home/ezpk/Projects/4X/CLAUDE.md, lignes 9 et 14 ; /home/ezpk/Projects/4X/docs/glossaire.md (pas d'entrée « propriétaire »)
- **Problème :**
  - `CLAUDE.md` ne dit pas que l'agent utilise les identifiants GitHub du propriétaire (§10, lignes 403 à 407). Sans ce fait, la ligne 20 est difficile à comprendre.
  - La règle « ne traite que les tickets ouverts par le propriétaire » ne peut pas être vérifiée : un ticket ouvert par l'agent apparaît comme ouvert par le propriétaire.
  - Le texte ne dit pas si une demande faite en session, sans ticket, est permise.
  - Le fait que le dépôt est public n'est pas dit.
- **Correction :**
  - Ajouter « propriétaire » au glossaire.
  - Ajouter une ligne à `CLAUDE.md` : l'agent utilise le compte GitHub du propriétaire, et le dépôt est public.
  - Dire si une demande faite en session vaut ticket.
  - Interdire de traiter un ticket ouvert par l'agent lui-même.

  Origine : texte imposé.

### comprehension-v-6 : le circuit des pull requests ne couvre ni la tâche permise aujourd'hui ni les travaux de M0 (Major)
- **Relecteur :** `egm-comprehension`
- **Fichiers :** /home/ezpk/Projects/4X/CLAUDE.md, lignes 5 et 22 à 26 ; /home/ezpk/Projects/4X/docs/feuille-de-route.md, ligne 7
- **Problème :**
  - La seule tâche permise aujourd'hui est de rédiger le document de niveau 2 de M0. Ce n'est ni une pull request de scénarios ni une pull request de fonctionnalité.
  - Les travaux de M0 (`.github/`, `.claude/`, configuration du linter) touchent tous des chemins protégés. Une pull request de fonctionnalité de M0 contredit donc forcément la ligne 24.
  - Même trou pour les ADR, les mises à jour du glossaire et les corrections de documentation.
- **Correction :** définir un troisième type de pull request, pour la documentation ou la configuration protégée : pas de scénarios, revue EGM obligatoire, fusion par le propriétaire. Ou bien écrire que, jusqu'à la livraison de M0, le circuit est celui que fixe le niveau 2 de M0. Origine : texte imposé et §10.

### comprehension-v-7 : l'attente de la fusion des scénarios n'est pas écrite (Major)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, lignes 23 et 24
- **Problème :**
  - « D'abord… Ensuite… » ne dit pas que la pull request de fonctionnalité s'ouvre seulement après la fusion de la pull request de scénarios. Le CUJ 3 pose pourtant cette précondition.
  - On ne sait pas non plus si la limite « une seule à la fois » vaut pour les scénarios.
- **Correction :** écrire « Ouvrir la pull request de fonctionnalité seulement après la fusion, par le propriétaire, de la pull request de scénarios correspondante. » Préciser la limite pour les pull requests de scénarios. Origine : texte imposé.

### comprehension-v-8 : « aucun identifiant ne doit être inventé » se lit comme une interdiction de coder, et « nom propre » est flou (Major)
- **Relecteur :** `egm-comprehension`
- **Fichiers :** /home/ezpk/Projects/4X/docs/glossaire.md, ligne 10 ; /home/ezpk/Projects/4X/CLAUDE.md, ligne 31 ; /home/ezpk/Projects/4X/docs/noms-valides.md, ligne 3
- **Problème :**
  - Lue seule, la ligne 10 du glossaire interdit d'écrire du code. Elle ne vise sans doute que la colonne du glossaire.
  - « Nom propre » n'est pas défini.
  - Le lecteur ne sait pas comment nommer une entité de test.
  - Il ne sait pas quoi faire si un identifiant « à fixer au niveau 2 » lui manque.
- **Correction :**
  - Glossaire, ligne 10 : écrire « Le glossaire n'invente aucun identifiant… ». Cette phrase vient de l'exécutant, pas du plan.
  - Dans `CLAUDE.md`, définir « nom propre » (lieu, objet ou personnage du jeu).
  - Ajouter : « Si un identifiant nécessaire n'est pas encore fixé, s'arrêter et demander. »

  Origine : texte imposé pour `CLAUDE.md` et `noms-valides.md`.

### comprehension-v-9 : la portée des termes interdits n'est pas claire (Major)
- **Relecteur :** `egm-comprehension`
- **Fichiers :** /home/ezpk/Projects/4X/docs/termes-interdits.md, lignes 3 et 5 ; /home/ezpk/Projects/4X/CLAUDE.md, ligne 31
- **Problème :**
  - « Vocabulaire d'EVE Online à ne pas reprendre », suivi de trois termes seulement : le lecteur ne sait pas s'il doit éviter tout le vocabulaire d'EVE, ou seulement ces trois mots.
  - « Corporation », mot d'EVE, figure dans le glossaire, ce qui renforce le doute.
  - La portée n'est pas dite : code, documents, commits, branches ?
  - « La RFC » (ligne 5) n'est pas désignée par son chemin.
- **Correction :**
  - Écrire « Seuls les termes de cette liste sont interdits ; en cas de doute sur un autre terme, demander. »
  - Préciser la portée.
  - Remplacer « la RFC » par `docs/designs/mmo-gestion-spatiale-ia.md`.

### comprehension-v-10 : l'étape 5 de l'ordre de lecture fait lire presque tout le niveau 1 (Major)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 6
- **Problème :** presque chaque règle renvoie à une section (§1, §2, §3, §8, §9bis, §10, Non-Functional Requirements). Le lecteur ne sait pas si les liens donnent une justification facultative ou un complément obligatoire. Tant que comprehension-v-1 et comprehension-v-3 ne sont pas corrigés, ils sont obligatoires pour §2 et §10.
- **Correction :** une fois ces deux constats corrigés, écrire « Les règles ci-dessous se suffisent à elles-mêmes ; les liens donnent la raison. Lire le niveau 1 en entier seulement pour rédiger un document de niveau 2 ou une ADR. » Origine : texte imposé.

### comprehension-v-11 : aucune consigne quand le niveau 1 paraît faux ou incomplet (Major)
- **Relecteur :** `egm-comprehension`
- **Fichiers :** /home/ezpk/Projects/4X/CLAUDE.md (consigne absente) ; /home/ezpk/Projects/4X/docs/adr/README.md, ligne 3
- **Problème :**
  - `CLAUDE.md` ne parle pas des ADR. L'agent ne sait pas s'il peut en proposer une.
  - Il ne sait pas quoi faire en cas de contradiction entre le niveau 1, le niveau 2 et `CLAUDE.md`.
  - L'ordre de priorité entre ces trois documents n'est pas donné.
- **Correction :** ajouter : « En cas de contradiction ou de manque, s'arrêter et signaler au propriétaire ; l'agent peut rédiger une ADR au statut « proposée », jamais « acceptée ». » Donner l'ordre de priorité. Origine : texte imposé.

### codebase-details-v-3 : un titre est ajouté dans deux fichiers à texte « exact » (Nit)
- **Relecteur :** `egm-codebase-details`
- **Fichiers :** /home/ezpk/Projects/4X/docs/adr/README.md, ligne 1 ; /home/ezpk/Projects/4X/docs/revues/2026-10-31-architecture-niveau-1/README.md, ligne 1
- **Problème :** le plan dit « contient exactement le texte suivant » (ligne 730) et « avec exactement ce texte » (ligne 818). Ces deux fichiers ajoutent pourtant un titre `#`, alors que `CLAUDE.md` n'en a pas. Le plan ne dit pas si un titre est permis.
- **Correction :** retirer les deux titres, ou faire confirmer par le propriétaire qu'un titre est permis.

### codebase-details-v-4 : une convention de nommage des ADR est inventée (Nit)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/adr/README.md, ligne 7
- **Problème :** « Fichier `docs/adr/NNNN-titre-court.md` » ne figure ni dans le plan (ligne 734) ni dans la spécification. C'est une décision de l'exécutant, dans un chemin protégé.
- **Correction :** retirer la ligne, ou la faire valider par le propriétaire.

### codebase-details-v-5 : plusieurs définitions ne reprennent pas une phrase de la spécification (Nit)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/glossaire.md, lignes 8, 16, 21, 28, 29, 41, 52, 71, 110, 139 et 140
- **Problème :**
  - La ligne 8 affirme que chaque définition reprend la phrase du niveau 1. C'est faux pour humain, client tiers, corporation, rang, tick, motif, scénario en attente et définition d'étapes : l'exécutant les a rédigées faute de phrase de définition dans la spécification.
  - Deux définitions restreignent le sens :
    - arrêt d'urgence (ligne 52) : la spécification ne le limite pas aux joueurs IA ;
    - protocole (ligne 71) : il est défini par ses transports, alors que §1 sépare protocole et transport.
  - Le plan (ligne 673) ne dit pas quoi faire en l'absence de phrase de définition. C'est une lacune du plan.
- **Correction :**
  - Ligne 8 : « reprend ou résume ».
  - Arrêt d'urgence : « Ordre d'administration ; le disjoncteur l'émet pour un joueur IA ».
  - Protocole : « Messages échangés entre clients et serveur (`schema`). Transports : en mémoire à M1, WebSocket à M3 ».

### codebase-details-v-6 : huit tableaux au lieu d'un, et un « — » sans mention (Nit)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/glossaire.md, lignes 12 à 149
- **Problème :** le plan demande « un tableau » (ligne 670) ; le glossaire en contient un par groupe. Les cellules « — » ne portent pas « (pas d'identifiant de code) ». La mention n'apparaît qu'une fois, à la ligne 10. Le Verification Plan (ligne 852) accepte « — » seul.
- **Correction :** accepter l'écart, ou fusionner les tableaux en un seul avec une colonne « groupe ».

### codebase-details-v-7 : deux liens ne visent pas la section qui contient la phrase (Nit)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/glossaire.md, lignes 50 et 61
- **Problème :**
  - Budget d'actions : « vérifiée dans `step` » vient de §2, mais le lien vise §5.
  - Graine du monde : « Celle du monde en ligne reste hors du dépôt » vient de §3 et des Non-Functional Requirements, mais le lien vise §2.
- **Correction :** ligne 50, lier §2, ou §2 et §5. Ligne 61, ajouter le lien vers §3, ou retirer la seconde phrase.

### codebase-details-v-8 : la phrase des termes interdits est retouchée, et une phrase est ajoutée (Nit)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/termes-interdits.md, lignes 3 et 5
- **Problème :**
  - Ligne 3 : la mention « lien `designs/…` » du plan (ligne 723) est devenue un lien Markdown. Le sens est le même, et le texte n'était pas imposé « exactement ».
  - Ligne 5 : cette phrase n'est pas demandée. Elle reprend une consigne destinée à l'exécutant.
  - Avec le format « un terme par ligne », un contrôle naïf prendrait les lignes 1, 3 et 5 pour des termes.
- **Correction :** garder la ligne 5 et signaler au niveau 2 de M0 que l'en-tête doit être exclu du contrôle, ou retirer la ligne.

### codebase-details-v-9 : la « liste vide » n'est pas visible (Nit)
- **Relecteur :** `egm-codebase-details`
- **Fichier :** /home/ezpk/Projects/4X/docs/noms-valides.md, ligne 4
- **Problème :** le fichier ne contient que la phrase imposée. Rien ne marque l'endroit où la liste commence (plan, ligne 717).
- **Correction :** facultatif. Ajouter un titre « ## Noms » ou un commentaire.

### codebase-details-v-10 : les valeurs de statut ne sont pas listées dans la feuille de route (Nit)
- **Relecteurs :** `egm-codebase-details`, `egm-comprehension` (doublon fusionné)
- **Fichiers :** /home/ezpk/Projects/4X/docs/feuille-de-route.md, lignes 5 à 13 ; /home/ezpk/Projects/4X/CLAUDE.md, ligne 5
- **Problème :**
  - `CLAUDE.md` teste la valeur exacte « approuvé », qui n'apparaît nulle part dans la feuille de route.
  - Les quatre valeurs du plan (ligne 708) ne sont pas écrites. Le plan ne l'exigeait pas : c'est un risque de dérive, pas un écart.
  - Le texte ne dit pas qui change le statut, ni par quel canal « demander au propriétaire ».
- **Correction :** ajouter « Statuts possibles : à écrire, en revue, approuvé, livré. Seul le propriétaire change un statut. »

### codebase-details-v-11 : le README des revues renvoie à un compte rendu qui n'existe pas encore (Nit)
- **Relecteurs :** `egm-codebase-details`, `egm-comprehension` (doublon fusionné)
- **Fichier :** /home/ezpk/Projects/4X/docs/revues/2026-10-31-architecture-niveau-1/README.md, ligne 3
- **Problème :**
  - « Le compte rendu de vérification » ne nomme aucun fichier.
  - `compte-rendu-implementation.md` n'existe pas encore : la synthèse l'a vérifié par Glob. Le plan l'exige pourtant (lignes 819, 832 et 856).
  - « Ce document » est ambigu : il peut désigner le README ou le niveau 1.
- **Correction :** créer `compte-rendu-implementation.md` à la fin de la vérification, comme prévu. La phrase du README est imposée « exactement » : la changer demande l'accord du propriétaire. Si la vérification est déclarée terminée sans ce fichier, le constat devient Major.

### comprehension-v-12 : des termes de la ligne 13 de `CLAUDE.md` manquent au glossaire (Nit)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 13 ; /home/ezpk/Projects/4X/docs/glossaire.md, ligne 61
- **Problème :** « PC d'entraînement », « serveur MLflow » et « monde en ligne » n'ont pas d'entrée. « Monde en ligne » sert pourtant à définir « graine du monde ». La liste du glossaire est fermée par le plan (ligne 683).
- **Correction :** le propriétaire ajoute ces trois termes à la liste fermée du plan, puis au glossaire.

### comprehension-v-13 : la régénération des empreintes repose sur des éléments non définis (Nit)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 24
- **Problème :** « l'outil prévu » n'est pas nommé, le « rapport de différences » n'est pas défini, et la manière de monter `rules_version` n'est pas dite.
- **Correction :** écrire « l'outil fixé au niveau 2 de M1 ». Préciser que la montée de version consiste à incrémenter le numéro de révision tenu à la main. Origine : texte imposé.

### comprehension-v-14 : « l'état n'est modifié que par `step` » semble contredire l'immuabilité de l'état (Nit)
- **Relecteur :** `egm-comprehension`
- **Fichiers :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 30 ; /home/ezpk/Projects/4X/docs/glossaire.md, ligne 60
- **Problème :** le glossaire dit qu'un état produit par `step` n'est jamais modifié. Le lecteur peut croire que `step` modifie l'état en place.
- **Correction :** écrire « Seul `step` produit un nouvel état ; aucun état n'est modifié en place. » Origine : texte imposé.

### comprehension-v-15 : les contrats d'imports renvoient à §1, alors que le glossaire les donne déjà (Nit)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 30
- **Problème :** les règles d'import figurent déjà dans le glossaire (lignes 91 à 97). La règle « le client n'appelle jamais `step` » (§1, ligne 173) n'y figure pas.
- **Correction :** renvoyer aussi à la section « Paquets » du glossaire, et y ajouter « le client n'appelle jamais `step` ». Origine : texte imposé.

### comprehension-v-16 : rien ne prévient que la RFC et `docs/revues/` sont de l'historique (Nit)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md (mention absente) ; /home/ezpk/Projects/4X/docs/designs/mmo-gestion-spatiale-ia.md
- **Problème :** un agent qui parcourt `docs/designs/` peut lire la RFC. Elle emploie « agents IA » au sens de joueurs IA. Son en-tête la dit dépassée, mais `CLAUDE.md` ne prévient pas.
- **Correction :** ajouter à `CLAUDE.md` : « Ne pas suivre `docs/designs/mmo-gestion-spatiale-ia.md` (RFC close) ni `docs/revues/` : historique seulement. » Origine : texte imposé.

### comprehension-v-17 : trois noms provisoires ne suivent pas la convention de langue (Nit)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/docs/glossaire.md, lignes 51, 70 et 111
- **Problème :** `K_ordres`, `N_empreinte` et `T_inactif` sont en partie en français, alors que la ligne 5 impose l'anglais pour le code. Le lecteur ne sait pas s'il peut les utiliser tels quels.
- **Correction :**
  - Ajouter « ne pas utiliser dans le code avant le niveau 2 » à ces trois entrées.
  - Ne pas proposer d'équivalent anglais : ces noms sont fixés par le plan (ligne 689 et suivantes), et la règle « aucun identifiant inventé » interdit d'en ajouter un.

### comprehension-v-18 : le cas de la fusion automatique n'est pas couvert (Nit)
- **Relecteur :** `egm-comprehension`
- **Fichier :** /home/ezpk/Projects/4X/CLAUDE.md, ligne 9
- **Problème :** le texte ne dit pas si activer la fusion automatique (`gh pr merge --auto`) compte comme « fusionner ».
- **Correction :** ajouter « y compris activer la fusion automatique ». Origine : texte imposé.

## Remarques sans constat

- `CLAUDE.md`, ligne 13 : §3 dit « jamais publiés ». La ligne 13 limite l'interdiction au dépôt, aux pull requests et aux commentaires ; les artefacts de CI et les releases ne sont pas nommés. Le texte est imposé et conforme (signalé par egm-codebase-details).
- egm-codebase-details a aussi vérifié, hors périmètre, l'état du niveau 1 et de la racine. Le statut `Approved` est présent dans le niveau 1, et l'encadré « Plan corrigé après la revue » n'y figure plus. Il ne reste à la racine ni `concepts_brief.md`, ni `design_draft.md`, ni `plan_propose_etape9.md`, ni aucun `*_report*.md`.
