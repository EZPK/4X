# Rapport de revue : étape 8 (Zoom Out intermédiaire)

*   **Document revu :** [architecture-niveau-1.md](./docs/designs/architecture-niveau-1.md). Spécification : l. 1 à 622. Plan d'implémentation (l. 625 et suivantes) : seulement comparé à la spécification, sous la mention « étape 9 ».
*   **Standard appliqué :** zoom-out-standard (EGM)
*   **Relecteur :** egm-zoom-out, nouvelle instance sans contexte de la conversation
*   **Date :** 2026-10-31
*   **Verdict :** à reprendre, mais sur peu de points. Presque tous les constats de l'étape 5 qui portaient sur la spécification sont résolus. Les corrections en introduisent 1 bloquant, 3 majeurs et 10 mineurs. Le bloquant se règle en modifiant une seule cellule du tableau des paquets.

---

## Suivi des constats de l'étape 5

| Constat | Statut | Remarque |
| :-- | :-- | :-- |
| B1 : les clients importent le noyau | Résolu | Le nouveau tableau des paquets crée une autre contradiction (N-B1). |
| M1 : frontière entre la CI et le réseau local | Résolu | §9bis, disponibilité des domaines par jalon. |
| M2 : documentation recopiée | Non résolu | Renvoyé à l'étape 9. L'objectif 9 s'appuie même sur la copie (N-N8). |
| M3 : migrations trop tôt | Résolu | §7 distingue avant et après M5. |
| M4 : chemins protégés incomplets | Résolu | |
| M5 : contournement par l'administrateur | Résolu | |
| M6 : définitions d'étapes | Résolu | Recouvre en partie la mutation (N-N4). |
| M7 : contrôles par jalon | Résolu | Deux lignes ne sont pas des contrôles de pull request (N-M1). |
| M8 : événements à M1 | Résolu | Le support des événements v0 n'est pas précisé (N-N6). |
| M9 : visibilité | Résolu | |
| M10 : PPO écrit à la main | Résolu | |
| N1 : `CODEOWNERS` et hook | En partie | `CODEOWNERS` est retiré. La justification du hook est fausse (N-M2). |
| N2 : « seule barrière » | Résolu dans la spécification | Encore présent dans le plan (étape 9). |
| N3 : borne de 64 bits | Résolu | |
| N4 : détails d'outillage | En partie | D'autres détails sont entrés depuis (N-N9). |
| N5 : `correlation_id`, `event_id` | Résolu | |
| N6 : réservations inutiles | Résolu | |
| N7 : déclencheur Rust mesuré de deux façons | Résolu dans la spécification | Le plan dit encore 347. Un nouveau problème apparaît (N-M3). |
| N8 : incohérences du plan | Non résolu | Étape 9. |

---

## Nouveaux constats

### N-B1. Bloquant : le noyau ne peut pas importer les types d'ordre, d'observation et d'événement

*   **Où :** §1, tableau des paquets ; §2, contrat ; §5 ; §6 ; objectif 4.
*   **Problème :** `core` « ne peut importer rien du projet ». Or `step` reçoit des ordres et `observe` renvoie des observations, et ces types sont définis dans `schema`. Il en va de même pour les types d'événements, que le noyau produit et que les clients doivent lire sans importer `core`.
*   **Pourquoi c'est grave :** `import-linter` appliquera cette frontière dès M1, depuis un chemin protégé. Un agent de code n'aurait alors que deux issues :
    - redéfinir les formats dans `core`, ce qui donne deux définitions des formats centraux ;
    - modifier le contrat d'imports.
*   **Correction :**
    - `core` peut importer `schema`, et `schema` n'importe toujours rien du projet.
    - Les types d'événements vont dans `schema`.
    - Corriger le schéma de §1 en conséquence.

### N-M1. Majeur : le verdict d'entraînement et la suite canari sont rangés parmi les contrôles obligatoires

*   **Où :** §10, tableau des contrôles ; §9bis ; CUJ 2 ; objectif 8.
*   **Problème :**
    - Le verdict est calculé depuis un commit de `main`, donc après la fusion. Pour qu'il bloque une fusion, il faudrait exécuter le code de la branche sur le PC d'entraînement, ce que §9bis interdit.
    - La suite canari tourne chaque nuit sur `main` : elle ne bloque aucune pull request non plus.
*   **Pourquoi c'est important :** un agent de code chercherait à brancher le verdict comme contrôle de pull request, donc à faire tourner du code de branche sur le réseau local. De son côté, le propriétaire croirait qu'une régression d'un joueur IA bloque la fusion.
*   **Correction :**
    - Ajouter une rubrique « contrôles après fusion ».
    - Écrire que le verdict conditionne la promotion et le déploiement (CUJ 6), pas la fusion.
    - Écrire qu'une suite canari en échec fait passer la page d'accueil au rouge.

### N-M2. Majeur : le hook Claude Code promet d'arrêter les commandes « même lancées par un script »

*   **Où :** §10 ; décision n° 67 du rapport de résolution ; Risks.
*   **Problème :**
    - Un hook `PreToolUse` ne voit que la commande passée à l'outil, pas ce que fait un script lancé par `python x.py` ou `bash x.sh`.
    - La RFC le dit explicitement (§4).
    - Or c'est précisément cet argument qui justifie de garder le hook.
*   **Pourquoi c'est important :** le propriétaire s'appuie sur ce que le document affirme. La ligne de risque compte ce hook comme une parade, alors que seule la fusion d'une pull request rouge est réellement bloquée. Une pull request verte peut être fusionnée par un script.
*   **Correction :**
    - Retirer « même lancées par un script ».
    - Écrire que le hook n'attrape que les commandes directes et les fautes d'inattention.
    - Ajouter au risque que la fusion d'une pull request verte par un script n'est arrêtée par aucun mécanisme technique : seuls l'historique des fusions et la suite canari la détectent.

### N-M3. Majeur : le déclencheur Rust « se mesure dès M1 », mais il ne peut s'appliquer qu'à M4

*   **Où :** §2 ; §9 (télémétrie à M5) ; Risks.
*   **Problème :**
    - Le débit de bout en bout (simulation, inférence et apprentissage), sur le PC d'entraînement, n'existe qu'à M4.
    - Le p99 du tick en direct suppose un serveur en direct et sa télémétrie.
    - Pourtant, le document dit que « la mesure démarre à M1 ».
*   **Pourquoi c'est important :** à M1, un agent fabriquera un faux banc « de bout en bout », ou mesurera autre chose sous le même nom.
*   **Correction :**
    - À M1, suivre un indicateur avancé : les ticks par seconde du noyau seul, sur un scénario de la taille de ceux de l'entraînement.
    - N'évaluer le déclencheur qu'à partir de M4 (débit) et de M5 (p99).
    - Corriger la colonne « Jalon » de la ligne de risque correspondante.

### Mineurs

| Constat | Où | Problème | Correction |
| :-- | :-- | :-- | :-- |
| N-N1 | §1 | `training` importe `clients`, donc aussi l'interface en terminal et le processus hôte. | Créer un paquet `policies` (PNJ scriptés et références), qui n'importe que `schema`. |
| N-N2 | §2, §3, Risks | Il y a deux encodages canoniques du même état (instantanés et empreintes). | Calculer les empreintes sur l'encodage des instantanés, composant par composant. Traiter une montée de version de `msgspec` comme un changement d'encodage. |
| N-N3 | objectif 5, §7 | Les versions d'observation et d'action sont exigées dès M1, alors qu'aucun réseau n'existe avant M4. | Les exiger à partir de M4. |
| N-N4 | §10, alternative K | La mutation apparaît sous trois formes qui se recouvrent, et la mutation complète nocturne a disparu de §10. | Une seule ligne : modules modifiés à chaque pull request (scénarios compris), plus une mutation complète chaque nuit. |
| N-N5 | Risks | Le tableau invente des mécanismes absents ailleurs : alerte d'espace disque, « preuves d'un écran », « tickets ouverts par le propriétaire ». | Les décrire dans leur section, ou les retirer. Un risque renvoie à une parade, il ne la crée pas. |
| N-N6 | §9, §11, CUJ 1 | Le support des événements v0 n'est pas dit. L'indice de prix est constant à M1 (prix fixes), donc le critère qui le concerne ne peut pas échouer. | Préciser le support de v0 (JSONL ou Parquet simple, jetables). À M1, ne garder que la masse monétaire, l'émission et la destruction par motif. |
| N-N7 | §9, CUJ 6, §3 | Le disjoncteur arrête un joueur IA sans passer par un ordre. | Le disjoncteur émet un ordre d'administration « arrêt d'urgence ». Les ordres en mode observation sont soumis à `step`, qui les refuse avec un code dédié. |
| N-N8 | objectif 9 | La vérification exige la copie de la feuille de route. | « Chaque ligne de §11 a un critère de sortie et un document de niveau 2. » |
| N-N9 | §2, §3, §10, alternatives A et R | Des détails de niveau 2 sont remontés dans le document (copie par phase, renommage temporaire, `pull_request_target`, `pytest-textual-snapshot`, « calculé avec un outil », chiffres recopiés). | Garder l'invariant, renvoyer le moyen au niveau 2, et renvoyer au tableau de §2 au lieu de recopier les chiffres. |
| N-N10 | alternative G, §10 | Le coût du choix des identifiants du propriétaire est sous-estimé : il impose de maintenir le hook, les règles `deny` et la règle de travail. | Ajouter une ligne aux inconvénients. La décision reste au propriétaire. |

---

## Incohérences entre la spécification et le plan (à traiter à l'étape 9)

*   Le document cible est marqué « (Create) » et qualifié de « ce brouillon ».
*   « C'est la seule barrière » contredit §10.
*   L'ADR 0001 reprend « 347 pas par seconde » au lieu de 1 736.
*   La condition de révision de l'ADR 0004 (« si la confiance baisse ») contredit le déclencheur de §10.
*   Les ADR 0001 à 0006, `questions-ouvertes.md` et `feuille-de-route.md` recopient le document. L'ADR 0006 contredit « seule description de cette procédure » (§7).
*   Les règles de `CLAUDE.md` présentent plusieurs manques :
    - la borne de 64 bits est oubliée ;
    - la règle contre les injections de consignes est absente ;
    - le circuit en deux pull requests n'y figure qu'en partie ;
    - la feuille de route manque dans l'ordre de lecture.
*   « carte d'évaluation » au lieu de « scénario d'évaluation ».
*   La note de renvoi dans la RFC doit aussi signaler trois changements :
    - le passage aux « ordres soumis » ;
    - le protocole en mémoire dès M1 ;
    - l'exception administrateur.

---

# Deuxième passage de l'étape 8 (seule nouvelle relecture autorisée)

*   **Relecteur :** egm-zoom-out, nouvelle instance sans contexte
*   **Verdict :** à reprendre. Les 14 constats du premier passage sont résolus. Ce passage en trouve 1 nouveau bloquant, 2 majeurs et 4 mineurs, tous dans §1 et §10. Chaque correction tient en une ou deux phrases.

## Suivi du premier passage

Les 14 constats N-B1 à N-N10 sont résolus. Restent deux petits écarts de formulation :
- « mutation complète du noyau » (§10) contre « mutation complète » (alternative K) ;
- le Parquet est annoncé en §3 et dans le schéma de §1 sans la mention « à partir de M2 ».

## Nouveaux constats

### N2-B1. Bloquant : le circuit en deux pull requests ne peut pas aboutir à partir de M1

*   **Où :** §10 (types de pull request, chemins protégés, contrôles obligatoires) ; CUJ 3.
*   **Problème :** les définitions d'étapes sont protégées et arrivent donc avec la pull request de scénarios, avant le code. Or, à partir de M1, les scénarios sont un contrôle obligatoire. Une pull request de scénarios sans le code correspondant est donc rouge par construction et ne peut jamais être fusionnée.
*   **Pourquoi c'est grave :** c'est le circuit de travail principal, et il casse dès la première fonctionnalité. L'agent de code n'aurait que de mauvaises issues :
    - mettre les définitions d'étapes dans la pull request de fonctionnalité, qui sera étiquetée à chaque fois, si bien que l'étiquette perdrait son sens ;
    - désactiver les scénarios ;
    - toucher la configuration des tests.
*   **Correction :** poser l'invariant suivant et laisser le moyen au niveau 2 de M0.
    - Les nouveaux scénarios d'une pull request de scénarios sont marqués *en attente*, et la CI exige qu'un scénario en attente échoue.
    - La pull request de fonctionnalité retire la marque sans toucher de fichier protégé, ce qui suppose que la liste des scénarios en attente soit hors des chemins protégés.
    - Comme un scénario en attente doit échouer, on ne peut pas s'en servir pour cacher une régression.

### N2-M1. Majeur : les références protégées doivent changer avec chaque fonctionnalité

*   **Où :** §10, §3, §7.
*   **Problème :**
    - Tout changement de règles change les empreintes de référence. Celles-ci sont protégées, alors que la pull request de fonctionnalité n'a pas le droit de toucher un chemin protégé.
    - La référence du score de mutation est un fichier protégé que personne n'est chargé de relever.
*   **Correction :**
    - La pull request de fonctionnalité régénère les empreintes de référence, uniquement avec l'outil prévu, avec la montée de `rules_version` et le rapport de différences en tête du résumé. L'étiquette est distincte : « références régénérées ».
    - La référence de mutation devient le score mesuré par la CI sur `main`, et non plus un fichier.

### N2-M2. Majeur : `tools` ne peut lire ni le journal ni le transport

*   **Où :** §1, tableau des paquets ; CUJ 4 ; M1.
*   **Problème :** la persistance et les transports sont dans `server`, et `tools` n'importe que `core` et `schema`. Or l'outil de divergence doit lire le journal et les instantanés, et le serveur de rejeu doit passer par un transport.
*   **Correction :** `tools` peut importer `server`.

### Mineurs

| Constat | Correction |
| :-- | :-- |
| N2-N1 : entre M1 et M2, les échecs de nuit n'ont nulle part où s'afficher ; §9bis ne dit pas où tournent les tâches de nuit ; « rouge si un contrôle obligatoire échoue » est ambigu | Jusqu'à M2, notification d'échec de GitHub Actions. Ajouter à §9bis la ligne « tâches de nuit : CI GitHub planifiée sur `main` ». Écrire « un contrôle après fusion échoue sur `main` ». |
| N2-N2 : le réseau entraîné n'a pas de paquet commun entre `training` et l'hôte des joueurs IA | `policies` contient toute fonction `observation -> ordres`, scriptée ou apprise (architecture du réseau et chargement des poids). |
| N2-N3 : les messages du protocole n'ont pas de paquet | Les ajouter au contenu de `schema`. |
| N2-N4 : on ne sait pas si les « 10 % » de M4 comparent des moyennes ou une borne ; « la pull request concernée » est vague | « La borne basse de l'intervalle à 95 % du gain sur la référence scriptée dépasse 10 % » ; « la pull request qui a fusionné ce commit ». |
