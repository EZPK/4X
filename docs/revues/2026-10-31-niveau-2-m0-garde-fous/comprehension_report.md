# Rapport de revue : étape 6 (test de compréhension), document de M0

*   **Document revu :** [niveau-2-m0-garde-fous.md](../../designs/niveau-2-m0-garde-fous.md). Spécification : l. 1 à 388. Plan : l. 389 à 630.
*   **Relecteur :** egm-comprehension, sans contexte de la conversation et sans standard.
*   **Fichiers lus :** la cible, `CLAUDE.md`, `docs/glossaire.md`, `docs/termes-interdits.md`, `docs/feuille-de-route.md`, et §10, §11 et le plan du niveau 1.
*   **Date :** 2026-10-31
*   **Résultat :** 12 majeurs, 9 mineurs.

## Ce que propose le document, selon moi (FeatureRange, lignes 1-388)

M0 crée le dépôt public `EZPK/4X` et met en place des garde-fous avant tout code du jeu :
- la protection de `main`, appliquée aussi aux administrateurs ;
- des règles `deny` et un hook `PreToolUse`, qui empêchent l'agent de code de fusionner, de pousser sur `main`, de forcer un push, d'utiliser `--no-verify` ou de modifier les réglages ;
- `gitleaks` à trois niveaux : avant chaque commit, en CI et, si GitHub le permet, au push ;
- un contrôle de garde, qui étiquette les pull requests touchant un chemin protégé ;
- une CI (linter, `mypy --strict`, termes interdits) sur un squelette Python vide (`fourx.*`).

L'agent de code crée lui-même le dépôt et applique les réglages, par trois « commandes d'amorçage ». Le hook ne les autorise que tant que leur effet n'existe pas encore sur GitHub.

Le document tranche aussi les choix que le niveau 1 lui confie : `pytest-bdd`, la liste `en_attente.txt` hors des chemins protégés, le format des termes interdits et l'identifiant `steps`.

La preuve repose sur sept essais réels, faits sur des branches `essai/…` dont les pull requests sont fermées sans fusion.

## Ce que dit le plan d'implémentation, selon moi (DetailedRange, lignes 389-630)

- **Phase 1 :** l'agent prépare tout en local. Il écrit la configuration, les scripts (termes interdits, garde), le hook et leurs tests. Il modifie le niveau 1, `CLAUDE.md`, le glossaire et la liste des termes interdits, puis fait un commit initial vérifié.
- **Phase 2 :** il crée le dépôt, lance les trois commandes d'amorçage et vérifie que les exceptions sont refermées.
- **Phases 3 et 4 :** il crée les jalons GitHub, puis joue les sept essais avec le propriétaire. Le propriétaire lance lui-même, avec `!`, les deux commandes interdites à l'agent.
- **Phase 5 :** un compte rendu, ajouté par pull request, rassemble les preuves. Le propriétaire déclare ensuite M0 livré.

Selon le document, le système actuel n'a ni dépôt, ni CI, ni mécanisme d'aucune sorte : toutes les règles de `CLAUDE.md` reposent sur la discipline de l'agent.

## Constats

### Majeurs

| # | Constat | Où | Correction |
| :-- | :-- | :-- | :-- |
| 1 | La 3e commande d'amorçage ne se referme jamais. Le document dit le contraire ailleurs, et l'étape 25 échouera | l. 46, 178, 184, 594 | Une condition d'état, par exemple `secret_scanning_push_protection.status` différent de `enabled` ; ou bien dire que l'exception reste ouverte, et pourquoi |
| 2 | « Le fichier passé en entrée est exactement celui-ci » est ambigu : texte, chemin ou contenu ? « Chemin protégé » laisse croire que le fichier ne peut pas être modifié en local | l. 183-184, 520 | Préciser ce que le hook vérifie (contenu identique à `origin/main`, ou empreinte) ; retirer l'argument « chemin protégé » |
| 3 | Le hook bloque les lectures que le plan demande : lecture de la protection, `rulesets` dans les règles `deny` | l. 191, 205, 228, 518, 594 | Ne refuser que les écritures (`-X PUT/PATCH/POST/DELETE`, `--method`, `-f`, `-F`, `--input`) et autoriser explicitement les GET |
| 4 | La notation `!` n'est jamais expliquée, et elle se lit comme une négation shell. L'hypothèse selon laquelle ces commandes échappent au hook n'est pas écrite | l. 194-195, 298, 301, 391, 545 | Expliquer `!` à sa première occurrence ; vérifier le comportement et l'ajouter aux questions ouvertes |
| 5 | Qui applique la protection ? « C'est cette requête que le propriétaire applique » contredit le point 3 et la phase 2 | l. 219 contre l. 178, 190, 593 | « que l'agent de code applique par la 2e commande d'amorçage » |
| 6 | La preuve « gitleaks en CI » peut manquer : si le blocage au push marche, la CI ne voit jamais le secret | l. 49, 109, 301 ; §11 | Un essai qui atteint la CI quand le blocage est actif (jeton reconnu par gitleaks mais pas par GitHub), ou dire que la preuve CI passe par les tests de la tâche |
| 7 | Les tests des termes interdits contiennent forcément un terme interdit, dans un fichier non exclu | l. 270, 536 | Liste factice passée au script, ou exclusion justifiée |
| 8 | On ne comprend pas comment la marque « en attente » est testée : le conftest de `tests/scenarios/` ne s'applique pas à `tests/outillage/`, et « fait échouer la session » laisse croire à une CI rouge | l. 282, 538-541 | Dire que le test lance une session pytest imbriquée (`pytester`), avec quel conftest et quelle liste |
| 9 | La liste des tâches requises n'est pas cohérente : « tests de l'outillage » absent de l'objectif 6, alors que la tâche lance déjà `tests/scenarios` | l. 52, 214, 283, 487 | Une liste unique des noms de tâches requises à M0, et ce que devient `tests-outillage` à M1 |
| 10 | Le format de `.github/chemins-proteges.txt` n'est pas défini : séparateur, syntaxe des motifs, exhaustivité, motif `references`, exclusion de `en_attente.txt` | l. 249, 252, 460-463 | Donner le contenu complet, ou la grammaire avec un exemple par catégorie |
| 11 | Le niveau 1 approuvé est modifié sans citer la règle qui l'autorise | l. 269, 550-557 | Une phrase qui cite la règle des décisions du 2026-10-31 et la couverture par la revue EGM |
| 12 | « point 4 du plan », « point 6 du plan » et « au point 19 bis » sont ambigus entre les deux documents | l. 269, 556-557 | « Detailed Implementation Plan du niveau 1, point 4 », « par le point 19 bis de ce document » |

### Mineurs

| # | Constat | Correction |
| :-- | :-- | :-- |
| 13 | « Amorçage » est employé avant d'être défini (l. 46, 78) | Renvoi au Technical Plan, point 3 |
| 14 | Le compte rendu passerait par une « pull request protégée », alors que `docs/revues/` n'est pas protégé (l. 609) | Nommer le type de pull request |
| 15 | L'exception `/issues` du hook n'est pas expliquée (l. 518) | Une demi-phrase de raison |
| 16 | La création des étiquettes n'est pas prévue (l. 251-252, 494) | Les créer en phase 3, ou par `garde.yml` |
| 17 | La phrase sur `git init -b main` est mal tournée (l. 584) | « …parce que la configuration git crée `master` par défaut » |
| 18 | On ne sait pas qui l'emporte entre la règle des 14 jours et les versions citées (l. 131, 393) | Le dire |
| 19 | Des vérifications d'objectifs sont vagues (l. 43, 57, 598) | La commande de contrôle ; renvoyer au fichier, pas à une ligne de tableau |
| 20 | Le glossaire n'est pas aligné sur `fourx.*` (l. 573) | L'identifiant reste `core`, le chemin d'import est `fourx.core` |
| 21 | On ne sait pas quand le hook devient actif dans la session (l. 502-507) | Une phrase sur le moment où il prend effet |
