# Goldfish Annotated Review Report : document de M0, étapes 5 à 7

Status: resolved (2026-11-01, « auto accept » : document réécrit ; copie de la version précédente gardée hors du dépôt)

**Target:** `docs/designs/niveau-2-m0-garde-fous.md` (document entier : la plupart des corrections de la spécification entraînent celles du plan détaillé)

**Constats traités :**
- les 51 constats de l'étape 7 ([critic_report.md](./critic_report.md)) ;
- les 23 constats de l'étape 5 ([zoom_out_report.md](./zoom_out_report.md)) ;
- les 21 constats de l'étape 6 ([comprehension_report.md](./comprehension_report.md)).

Beaucoup se recoupent. Les doublons sont rattachés au constat de l'étape 7 qu'ils répètent.

**Bilan :** aucun constat contesté ni remonté au propriétaire. 49 constats de l'étape 7 reçoivent une correction. 2 sont écartés : egm-structural-1-13 en partie, egm-style-1-14 en partie. Tous les constats des étapes 5 et 6 sont couverts par une correction, sauf N13 de l'étape 5 (`actions/labeler`), écarté avec sa raison.

## Trois choix de conception contenus dans les corrections

Ils ne remettent en cause aucune décision du propriétaire, mais ils changent la façon dont elles s'appliquent.

1. **Nouvel ordre de l'amorçage** (egm-design-1-9) :
   1. création du dépôt ;
   2. activation du blocage des secrets ;
   3. push initial ;
   4. protection de `main`.

   Le blocage des secrets protège ainsi le commit initial lui-même. La protection vient en dernier, parce qu'elle exige que `main` existe.
2. **Les fichiers de `.claude/` deviennent non modifiables par les outils d'édition de l'agent de code** (règles `deny` sur Edit et Write, egm-design-1-4). Sans cela, l'agent pourrait désactiver ses propres garde-fous en éditant le hook. Conséquence : toute modification future de `.claude/` demande au propriétaire de lever la règle localement. La procédure est écrite.
3. **`docs/revues/` devient un chemin protégé** (étape 5 N10, étape 6 n° 14, egm-style-1-5). Le compte rendu de M0 et les rapports de revue passent alors par une pull request protégée, au lieu de n'avoir aucun type.

   C'est un écart de plus par rapport au niveau 1, ajouté à la liste des écarts. Les deux autres viennent des décisions du 2026-10-31 :
   - trois exceptions d'amorçage au lieu d'une ;
   - le push vers `main` et les réglages filtrés par le hook plutôt que par les règles `deny` ;
   - les fichiers exclus du contrôle des termes interdits.

   Les écarts au niveau 1 passent ainsi de trois à quatre.

## Prioritized Findings & AI Suggestions

### Bloquants (High)

| Constat | Doublons | Suggestion | Correction |
| :-- | :-- | :-- | :-- |
| egm-structural-1-1 : la 3e exception d'amorçage ne se referme jamais ; le hook vérifie un nom de fichier, pas son contenu | étape 5 B2 ; étape 6 n° 1, 2 | PROPOSE FIX | Chaque exception d'amorçage a une condition d'état GitHub **et** une vérification de contenu. Le hook contient une copie de référence de `securite-depot.json` et de `protection-main.json`, et refuse si le fichier sur le disque n'est pas identique (comparaison du JSON analysé). La 3e se ferme dès que `secret_scanning_push_protection.status` vaut `enabled`. Les trois commandes sont énumérées dès la première phrase du point 3, et les l. 46, 178, 184, 338, 563 et 594 sont alignées |
| egm-style-1-1 : l'essai du faux secret ne peut pas prouver à la fois le hook pre-commit et la CI | étape 6 n° 6 | PROPOSE FIX | Deux faux secrets :<br>– un jeton au format `ghp_`, pour essayer le blocage au push. S'il passe, le résultat est consigné « blocage non démontré », et non « indisponible » ;<br>– une valeur détectée par une règle `gitleaks` propre au projet (`FOURX_ESSAI_SECRET_…`), que GitHub ignore, et qui atteint toujours la CI.<br>Le Goal 4, le CUJ 4 et le §12 reçoivent la même formulation. Le texte précise qui agit et quel hook est contourné, et que le jeton reste lisible dans la pull request fermée |
| egm-design-1-1 : un ajout dans `en_attente.txt` cache une régression | — | PROPOSE FIX | Une tâche requise de `garde.yml` (version de `main`) échoue si `en_attente.txt` gagne des entrées dans une pull request qui ne modifie aucun `.feature`. Les retraits sont libres. Le cas est ajouté aux tests et au tableau des risques |

### Majeurs (Medium)

| Constat | Doublons | Suggestion | Correction |
| :-- | :-- | :-- | :-- |
| egm-design-1-2 : un hook qui plante laisse passer la commande | étape 5 M1 | PROPOSE FIX | Bibliothèque standard seulement ; lancé par `python3 -I` avec un chemin explicite ; tout le corps dans un `try/except` qui sort avec le code 2 ; une commande `git` ou `gh` impossible à analyser est refusée ; tests « plantage » et « analyse impossible » ; ligne de risque. Le comportement des codes de sortie est à vérifier contre la version installée (question ouverte) |
| egm-design-1-3 : la liste noire du hook laisse passer des variantes | étape 5 M2 ; étape 6 n° 3, 15 | PROPOSE FIX | **Écritures GitHub en liste blanche :**<br>– `gh api` en lecture pure toujours autorisé ;<br>– en écriture, autorisé seulement sur `issues`, `milestones`, `labels`, `pulls` (création) et les commentaires ;<br>– GraphQL refusé ;<br>– `gh repo` limité à `view` et à `create` tant que le dépôt n'existe pas ;<br>– `gh pr edit --remove-label` refusé pour les étiquettes du garde.<br>**Pour `git push` :** le hook détermine la branche cible réelle (refspec, sinon branche suivie) et refuse `--all`, `--mirror` et `--delete`.<br>**Il refuse aussi** `-n`, `SKIP=`, `core.hooksPath` et `pre-commit uninstall`.<br>**Méthode :** égalité exacte pour les commandes d'amorçage, recherche des motifs dans toute la chaîne brute pour le reste. Chaque variante a son test |
| egm-design-1-4 : les outils autres que Bash échappent aux deux mécanismes | — | PROPOSE FIX | Règles `deny` Edit et Write sur `.claude/**` et `.git/hooks/**` (choix de conception 2). Aucun serveur MCP GitHub n'est configuré aujourd'hui ; si un l'est un jour, ses outils d'écriture sont refusés. La limite figure au tableau des risques |
| egm-design-1-5 : le garde peut bloquer le dépôt, sans procédure de reprise | — | PROPOSE FIX | Le point 4 vérifie que chaque contrôle requis correspond à une tâche réellement lancée sur la première pull request d'essai, et que l'état de `pull_request_target` est rattaché au commit de tête. Une procédure de reprise est écrite, réservée au propriétaire, par l'interface : retirer `enforce_admins`, fusionner la réparation, remettre `enforce_admins`, relire. Ligne de risque |
| egm-design-1-6 : signal du garde non durable, et conflit avec le résumé EGM | étape 5 M5 | PROPOSE FIX | Un seul mot, « description ». Ordre fixé : bloc du garde, puis résumé EGM. Déclencheurs `opened`, `synchronize`, `reopened` et `edited`, pour le garde et pour les termes interdits. Copie de la liste dans le résumé de la tâche (`$GITHUB_STEP_SUMMARY`). Retrait des étiquettes du garde refusé par le hook. L'étiquette attendue est nommée aux l. 51 et 115 |
| egm-design-1-7 : injection par `pull_request_target` | étape 5 M7 | PROPOSE FIX | Exigences :<br>– aucune expression `${{ github.event.* }}` dans un `run:` ;<br>– données lues par les scripts depuis `$GITHUB_EVENT_PATH` ou des variables d'environnement ;<br>– noms de fichiers échappés dans le bloc ;<br>– aucun cache ni artefact partagé ;<br>– test avec un nom de fichier hostile ;<br>– parade du tableau des risques corrigée |
| egm-design-1-8 : une pull request peut neutraliser ses propres contrôles | — | PROPOSE FIX | Limite écrite dans The Problem et au tableau des risques : une pull request qui modifie `.github/` peut affaiblir ses propres contrôles. Le garde le signale, mais rien ne l'empêche. C'est le risque accepté du niveau 1 |
| egm-design-1-9 : ordre de l'amorçage et détection en CI après exposition | — | PROPOSE FIX | Nouvel ordre (choix de conception 1) ; `gitleaks git` sur le commit initial juste avant le push. Le Goal 4 et la l. 209 disent que la CI détecte après exposition, et qu'une détection en CI impose de révoquer le secret |
| egm-design-1-10 : `gitleaks` ne couvre pas ce que le niveau 1 interdit | — | PROPOSE FIX | `.gitleaks.toml` avec des règles propres au projet : plages IPv4 privées, variables du projet avec une valeur hors `.env.example`, et la règle d'essai `FOURX_ESSAI_SECRET_`. Le Goal 4 précise que les graines ne sont pas détectables par motif : elles restent couvertes par `.gitignore` et la règle de travail |
| egm-design-1-11 : le hook pre-commit n'existe que dans un clone | — | PROPOSE FIX | Le hook Claude Code refuse `git commit` si `.git/hooks/pre-commit` est absent ou n'appelle pas `pre-commit`. Ligne de risque |
| egm-design-1-12 : le contrôle des termes interdits bloque ses propres pull requests | étape 5 M3 ; étape 6 n° 7 | PROPOSE FIX | Le script accepte le chemin d'une liste en argument, et les tests lui passent des termes inventés écrits dans `tmp_path`. Aucun terme interdit dans un fichier suivi. Une pull request qui ne modifie que `docs/termes-interdits.md` est dispensée de la vérification de sa description et de ses messages de commit |
| egm-design-1-13 : `pyproject.toml` protégé, alors que les dépendances y vivent | étape 5 M4 ; étape 6 n° 10 (partie) | PROPOSE FIX | La configuration des outils va dans des fichiers séparés et protégés (`ruff.toml`, `mypy.ini`, `pytest.ini`, `.importlinter`). `pyproject.toml` et `uv.lock` restent hors des chemins protégés |
| egm-structural-1-2 : qui applique la protection de `main` | étape 6 n° 5 | PROPOSE FIX | L. 178 et 219 : l'agent de code, par une commande d'amorçage |
| egm-structural-1-3 : Goal 3 plus large que son CUJ et que les essais | — | PROPOSE FIX | Un essai « interdictions de Claude Code » liste chaque commande du Goal 3 et les trois secondes tentatives d'amorçage. Le push forcé est essayé sur une branche `essai/…`. L'essai de fusion se fait sur une pull request **verte** |
| egm-structural-1-4 : Goal 1 sans essai ; refus d'un push direct par GitHub jamais exercé | — | PROPOSE FIX | Essai du propriétaire `! git push origin HEAD:main`, avec le message de refus de GitHub cité. Essai de lecture : `gh repo view --json visibility` et `git log --first-parent main` |
| egm-structural-1-5 : `!` non défini ; essais du propriétaire réussis pour une mauvaise raison | étape 5 N1 ; étape 6 n° 4 | PROPOSE FIX | `!` est défini à sa première occurrence. L'origine attendue du refus (GitHub, et non Claude Code) et un extrait du message sont donnés. Une question ouverte : les commandes `!` échappent-elles au hook ? C'est vérifié par une commande sans danger avant les essais ; sinon, les essais se font dans un terminal séparé |
| egm-structural-1-6 : solutions de rechange différentes si `enforce_admins` manque | — | PROPOSE FIX | Une seule liste, dans le même ordre :<br>1. ruleset, appliqué par le propriétaire avec `!` à partir de `.github/ruleset-main.json`, versionné ;<br>2. abonnement ;<br>3. critère réduit, consigné comme risque accepté |
| egm-structural-1-7 : écarts au niveau 1 dispersés, renvoi faux, alternative E inexacte | étape 5 M6 ; étape 6 n° 11, 12 | PROPOSE FIX | Une sous-section « Écarts au niveau 1 » liste les quatre écarts, leur décision et le point du plan qui les reporte. Elle dit qu'ils relèvent des décisions du 2026-10-31, donc sans ADR, et qu'ils sont couverts par cette revue. Les renvois et la raison de l'alternative E sont corrigés |
| egm-style-1-2 : « avant tout le reste », alors que la vérification suit l'amorçage | — | PROPOSE FIX | Titre « juste après l'amorçage », et l. 69 et 205 alignées |
| egm-style-1-3 : « seule la tâche tests de l'outillage est requise » | étape 5 N7 ; étape 6 n° 9 | PROPOSE FIX | Une seule liste des tâches requises de M0 :<br>– `lint`, `typage`, `gitleaks`, `termes-interdits`, `tests-outillage` ;<br>– `garde` et `en-attente`, dans `garde.yml`.<br>L'ajout de `tests-outillage` par rapport au niveau 1 est signalé. À M1, la tâche `tests-outillage` devient `tests` (outillage, scénarios et propriétés) |
| egm-style-1-4 : « contrôle obligatoire » et « contrôle requis » | — | PROPOSE FIX | « contrôle obligatoire » partout, avec une phrase qui définit « tâche » (job GitHub Actions) |
| egm-style-1-5 : « compte rendu de M0 » non défini | étape 5 N10 ; étape 6 n° 14 | PROPOSE FIX | Défini à sa première mention : `docs/revues/2026-10-31-niveau-2-m0-garde-fous/compte-rendu-m0.md`, rédigé par l'agent de code et ajouté par une pull request protégée (choix de conception 3) |
| egm-style-1-6 : on ne sait pas quand la tâche de garde réussit | — | PROPOSE FIX | Elle réussit dès qu'elle a terminé son analyse, et n'échoue qu'en cas d'erreur technique |
| egm-style-1-7 : alternative B, phrase à contresens | — | PROPOSE FIX | Reformulée sans affirmation sans source |
| egm-style-1-8 : parade du risque « une exception se rouvre » contraire à The Problem | — | PROPOSE FIX | Reformulée : le hook refuse toute écriture directe sur `/protection` ; un retrait par l'interface ou par un script reste possible (risque accepté du niveau 1). Aucun contrôle répété à M0 : la vérification de la protection devient un contrôle après fusion à M1 |

### Mineurs (Low)

| Constat | Doublons | Suggestion | Correction |
| :-- | :-- | :-- | :-- |
| egm-design-1-14 : « absent » confondu avec « lecture en échec » | — | PROPOSE FIX | « code de sortie 0 et sortie vide » ; « 404 avec `Branch not protected` », tout autre 404 étant refusé |
| egm-design-1-15 : catégorie `references`, cas mixte | étape 5 N2 ; étape 6 n° 10 | PROPOSE FIX | La catégorie `references` est reportée à M1, avec son motif ; M0 n'a que `protege`. Le format de `chemins-proteges.txt` est donné en entier |
| egm-design-1-16 : titres de scénarios fragiles | — | PROPOSE FIX | Titres en double interdits et vérifiés. Un plan de scénario est en attente pour tous ses exemples |
| egm-design-1-17 : scripts hors de mypy ; import par les tests | étape 5 N6 | PROPOSE FIX | `.claude/hooks/` et `.github/scripts/` ajoutés à mypy ; les tests les chargent par `importlib` |
| egm-design-1-18 : réglages et préalables absents | étape 6 n° 16 | PROPOSE FIX | `securite-depot.json` fixe aussi le jeton des workflows en lecture seule et interdit aux Actions d'approuver des pull requests. Les étiquettes sont créées pendant l'amorçage. La CI lance `uv sync --locked` |
| egm-structural-1-8 : renvois « point N » | étape 6 n° 12 | PROPOSE FIX | « Technical Plan, point N » et « plan détaillé, point N » partout |
| egm-structural-1-9 : raisons manquantes | — | PROPOSE FIX | Une ligne de raison pour le format des termes, `steps` et `pytest-bdd` ; `ruff` attribué à ce document |
| egm-structural-1-10 : Goal 8 double, vérifications sans essai | étape 6 n° 19 | PROPOSE FIX | Goal 8 (runners) et Goal 9 (jalons) séparés ; essais ajoutés, y compris pour « CI verte sur `main` » |
| egm-structural-1-11 : décisions sous Open Questions, puces mélangées | — | PROPOSE FIX | Les décisions vont dans le tableau du point 1, puces uniformisées |
| egm-structural-1-12 : sections et sources absentes | — | PROPOSE FIX | Additional Resources (documentation GitHub consultée, avec liens et date) et Future Improvements (licence, ruleset, compte séparé) ajoutées |
| egm-structural-1-13 : mise en forme | — | PROPOSE FIX (en partie) | Second tableau introduit, phrase de langue alignée sur le niveau 1. Le séparateur est gardé : il vient du gabarit EGM |
| egm-structural-1-14 : CUJ 3 du niveau 1 non rattaché | — | PROPOSE FIX | Phrase de correspondance en tête des CUJs |
| egm-structural-1-15 : type des pull requests d'essai | — | PROPOSE FIX | Colonne « type » ; une seule pull request d'essai ouverte à la fois |
| egm-structural-1-16 : risques manquants | — | PROPOSE FIX | Lignes pour Python 3.15 sur le PC d'entraînement et pour l'absence de licence ; « clients tiers rendus possibles par le protocole » |
| egm-style-1-9 à 1-13, 1-15 à 1-17 : formulations | étape 6 n° 13, 17, 18, 20, 21 | PROPOSE FIX | Antécédents, « dépôt GitHub », « pull request d'essai », « tag git », « SHA du commit », « somme de contrôle SHA-256 », justifications reformulées, formats de listes précisés, règle de version (les versions vérifiées le 2026-10-31 sont des minimums, et la règle des 14 jours choisit la version épinglée), identifiant `core` avec le chemin `fourx.core`, moment où le hook prend effet |
| egm-style-1-14 : tournures familières | — | PROPOSE FIX (en partie) | « (si disponible) », « mener les essais », « enfreint ». « Jouer » est gardé dans « jouer un essai », qui est clair |
| Étape 5 N3 : `hypothesis` et `import-linter` sans usage | — | PROPOSE FIX | `hypothesis` reporté à M1 ; `lint-imports` lancé en CI comme contrôle non requis |
| Étape 5 N4 : variables inventées dans `.env.example` | — | PROPOSE FIX | Un seul commentaire, sans nom de variable |
| Étape 5 N5 : `.gitignore` non ancré | — | PROPOSE FIX | Motifs ancrés à la racine |
| Étape 5 N8 : liste des chemins protégés incomplète | étape 6 n° 10 | PROPOSE FIX | Liste complète des motifs, y compris `.python-version`, `tests/outillage/` et `.gitleaks.toml` |
| Étape 5 N9 : `docs/m0/commandes-proprietaire.md` en trop | — | PROPOSE FIX | Supprimé ; les commandes du propriétaire restent dans le §12 |
| Étape 5 N12 : chiffres arbitraires de tests | — | PROPOSE FIX | Règle de couverture : chaque catégorie et chaque variante a au moins un test |
| Étape 5 N13 : `actions/labeler` | — | DECLINE | Il étiquette, mais n'écrit pas le bloc de liste et ne lit pas `en_attente.txt` : un script reste nécessaire, et deux mécanismes pour un seul contrôle seraient plus fragiles. La raison est ajoutée aux alternatives |
| Étape 5 N14 : deux voies d'installation de `gitleaks` | — | PROPOSE FIX | Un seul binaire épinglé, appelé par un hook local de `pre-commit` et par la CI |
| Étape 6 n° 8 : test de la marque « en attente » incompréhensible | — | PROPOSE FIX | Le test lance une session pytest imbriquée (`pytester`), avec une copie du `conftest.py` et sa propre liste |
