# Rapport de revue critique (étape 7, tour 1)

**Cible :** /home/ezpk/Projects/4X/docs/designs/niveau-2-m0-garde-fous.md (lignes 1 à 388, avant « ## Detailed Implementation Plan »)
**Date :** 2026-10-31
**Standard :** /home/ezpk/.claude/plugins/cache/egm/egm/0.1.0/resources/document_standards/feature-spec-standard.md (egm-design, egm-structural) ; persona seul (egm-style)
**Contexte fourni aux relecteurs :** /home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md, /home/ezpk/Projects/4X/CLAUDE.md, /home/ezpk/Projects/4X/docs/glossaire.md, /home/ezpk/Projects/4X/docs/termes-interdits.md, /home/ezpk/Projects/4X/docs/feuille-de-route.md

Les décisions du propriétaire inscrites dans le document n'ont pas été remises en cause : dépôt public `EZPK/4X`, aucune licence, Python 3.15, `mypy --strict`, `pytest-bdd`, amorçage par l'agent de code avec des exceptions qui se referment d'elles-mêmes, exclusions du contrôle des termes interdits. Les relecteurs n'ont relevé que les risques et les incohérences qui en découlent.

## État des relecteurs

| Relecteur | État | Constats bruts (avant fusion) |
| --- | --- | --- |
| `egm-design` | completed | 1 Blocker, 15 Major, 8 Nit (24) |
| `egm-structural` | completed | 1 Blocker, 11 Major, 13 Nit (25) |
| `egm-style` | completed | 1 Blocker, 16 Major, 13 Nit (30) |

Les trois relecteurs ont répondu dès le premier essai. Aucune relance n'a été nécessaire.

## Méthode de fusion

- Quand plusieurs relecteurs signalent le même défaut, il n'y a qu'un constat. Son identifiant vient du relecteur dont la formulation sert de base, et les autres sont cités dans « Signalé aussi par ».
- La sévérité retenue est la plus haute parmi celles proposées.
- Les numéros de ligne renvoient à la cible. Le synthétiseur a vérifié par relecture les citations qui portent un Blocker (lignes 184, 269, 279 à 281, 301).

## Bilan après fusion

| Sévérité | Nombre |
| --- | --- |
| Blocker | 3 |
| Major | 25 |
| Nit | 23 |
| **Total** | **51** |

--------------------------------------------------------------------------------

## Blockers

### egm-structural-1-1 : la troisième exception d'amorçage ne se referme jamais, et le hook vérifie un nom de fichier, pas son contenu

- **Sévérité :** Blocker
- **Lentille :** `egm-structural` ; signalé aussi par `egm-design` (Major) et `egm-style` (Major, deux constats)
- **Lignes :** 46, 178, 183-184, 230, 338, 382
- **Problème :**
  - Trois passages promettent que chaque exception se ferme après sa première exécution : l. 46 (« ne sont acceptées qu'une fois »), l. 178 (« Chaque exception se ferme donc d'elle-même ») et l. 338 (« chacune refermée par l'état de GitHub »). La l. 184 dit l'inverse pour `gh api -X PATCH repos/EZPK/4X --input .github/securite-depot.json` : « le hook continue de n'accepter que ce fichier ». L'exception reste donc ouverte pour toujours.
  - « Le fichier passé en entrée est exactement celui-ci » (l. 183-184) ne dit pas si le hook vérifie le chemin ou le contenu. Le hook lit le fichier sur le disque. Une modification locale (désactivation du blocage des secrets, `allow_auto_merge`, `visibility`, `archived`…) passe alors par la commande autorisée, sans pull request ni contrôle de garde. L'argument « c'est un chemin protégé » ne vaut que pour la version commitée : selon le glossaire, un chemin protégé est signalé dans une pull request, pas empêché dans la copie de travail. La même faiblesse existe pour `.github/protection-main.json` (l. 183), dans une fenêtre plus courte.
  - La l. 178 annonce « ces trois commandes » alors que la phrase précédente n'en nomme que deux. Le Goal 3 (l. 46) emploie le terme avant de l'avoir défini.
- **Raison :** c'est une contradiction interne sur le mécanisme de sécurité central de M0. Le niveau 1 (§10) demande au hook de refuser les modifications des réglages. Le standard demande de nommer les modes de défaillance, et celui-ci n'est pas dans le tableau des risques.
- **Correction proposée :**
  - Donner une vraie condition de fermeture à la troisième commande, par exemple : autorisée seulement si `security_and_analysis.secret_scanning_push_protection.status` n'est pas encore `enabled`. Ou bien écrire franchement qu'elle est permanente, et ajouter la ligne de risque correspondante.
  - Dans les deux cas, le hook vérifie le contenu : comparaison octet pour octet avec la version de `main` lue sur GitHub, ou empreinte écrite dans le hook, ou analyse du JSON contre une liste de clés figée. Même règle pour `protection-main.json`.
  - Énumérer les trois commandes dès la l. 178, et corriger en conséquence les l. 46, 178 et 338.

### egm-style-1-1 : l'essai du faux secret ne peut pas prouver à la fois le refus par le hook pre-commit et le refus en CI

- **Sévérité :** Blocker
- **Lentille :** `egm-style` ; signalé aussi par `egm-structural` (Major) et `egm-design` (Major)
- **Lignes :** 49, 105-109, 195, 301, 306, 373
- **Problème :**
  - Trois attendus différents : le Goal 4 (l. 49) exige l'échec de la CI et vérifie le blocage GitHub « s'il est disponible » ; le CUJ 4 (l. 109) attend l'échec de la CI **et**, si le blocage existe, le refus du push ; le §12 (l. 301) attend l'un **ou** l'autre. Si le push est refusé, il n'y a pas de pull request, donc pas de CI.
  - Le critère de sortie du niveau 1 (§11, ligne M0) dit « refusé par le hook pre-commit **et** en CI ». Si le blocage au push est actif, l'essai prévu ne montre jamais le refus en CI.
  - À l'inverse, un jeton GitHub inventé n'a pas la somme de contrôle d'un vrai jeton `ghp_`. Le blocage de GitHub peut le laisser passer, et l'on conclurait à tort que la fonction n'est pas disponible (egm-design).
  - Le CUJ 4 dit « on tente » et « en contournant le hook » : on ne sait ni qui agit (le propriétaire, selon la l. 195) ni quel hook est contourné (le glossaire en distingue deux). Le contournement a lieu au commit, pas au push.
  - « Il ne reste dans aucune branche » (l. 306) peut laisser croire que le jeton disparaît. La l. 373 dit qu'il reste lisible dans la pull request fermée, et la référence `refs/pull/N/head` le garde public.
- **Raison :** l'objectif, le parcours, l'essai et le critère du niveau 1 ne disent pas la même chose. L'essai ne peut pas satisfaire le critère de sortie dans le cas où le blocage de GitHub fonctionne.
- **Correction proposée :**
  - Prévoir deux faux secrets : l'un au format qu'un blocage de GitHub reconnaît selon sa documentation, pour prouver le blocage au push ; l'autre détecté par une règle `gitleaks` personnalisée que GitHub ne connaît pas, pour qu'il atteigne toujours la CI. Ou bien écrire explicitement comment la barrière CI est prouvée quand le blocage au push est actif (contournement volontaire du blocage par le propriétaire, par exemple, ce qui relève de sa décision).
  - Aligner le Goal 4, le CUJ 4 et le §12 sur une seule formulation.
  - Au CUJ 4 : « le propriétaire tente de le committer, puis le committe avec `--no-verify` (hook pre-commit contourné) et le pousse dans une pull request ».
  - Aux l. 306 et 373 : « Il n'est fusionné dans aucune branche, mais reste lisible dans la pull request fermée. Il ne donne accès à rien. »

### egm-design-1-1 : un ajout dans la liste « en attente » cache une régression

- **Sévérité :** Blocker
- **Lentille :** `egm-design`
- **Lignes :** 253, 272-283, 355-356
- **Problème :** `tests/scenarios/en_attente.txt` est hors des chemins protégés, et rien ne distingue un ajout d'un retrait. Une pull request de fonctionnalité qui casse un scénario déjà livré peut l'ajouter à la liste : le scénario devient `xfail(strict=True)`, échoue comme prévu, et la CI est verte. Le contrôle de garde ne signale rien, puisque le fichier en est exclu (l. 253). C'est la réaction typique d'un agent qui n'arrive pas à faire passer un test.
- **Raison :** le niveau 1 (§10, pull request de scénarios) exige qu'« on ne puisse pas utiliser la marque pour cacher une régression ». Le `strict` empêche seulement de laisser une marque sur un scénario qui passe ; il n'empêche pas d'en poser une sur un scénario qui échoue. M0 fixe le mécanisme, donc c'est ici que la propriété doit tenir.
- **Correction proposée :** seule une pull request qui touche des `.feature` peut ajouter une entrée ; ailleurs, la liste ne peut que rétrécir. Deux façons de l'imposer : une tâche de CI compare la liste à celle de `main` et échoue sur tout ajout fait sans `.feature` modifié ; ou le garde classe les ajouts dans `en_attente.txt` en `protege` et laisse passer les retraits. Ajouter le cas au tableau des risques et aux tests de l'outillage.

--------------------------------------------------------------------------------

## Major

### egm-design-1-2 : un hook qui plante laisse passer la commande

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural`
- **Lignes :** 230, 233, 235, 383
- **Problème :** la l. 230 retire des règles `deny` le push vers `main` et les écritures de réglages : le hook est la seule barrière côté Claude Code pour ces commandes. La l. 233 traite l'échec de la lecture de GitHub, pas le plantage du hook lui-même (exception Python, JSON inattendu, interpréteur absent ou trop ancien, `uv` indisponible), ni une commande que le découpage ne sait pas analyser (guillemets non fermés, heredoc). Selon les deux relecteurs, Claude Code ne bloque que sur le code de sortie 2 ; un autre code non nul laisse la commande s'exécuter. Le hook serait donc ouvert en cas de panne. Le risque de la l. 383 suppose l'inverse.
- **Raison :** mode de défaillance non nommé, qui touche directement le Goal 3. Le comportement des codes de sortie est à confirmer contre la documentation de la version installée, comme le prévoit déjà la question ouverte de la l. 70.
- **Correction proposée :** le hook enveloppe tout son code et sort en code 2 sur toute exception ; toute commande `git` ou `gh` qu'il ne sait pas analyser est refusée ; l'interpréteur appelé est fixé (chemin explicite ou `uv run --frozen`) ; des tests couvrent « plantage » et « analyse impossible » ; une ligne s'ajoute au tableau des risques.

### egm-design-1-3 : la liste noire du hook laisse passer des variantes courantes, et sa portée est floue

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural` et `egm-style`
- **Lignes :** 46, 224-233
- **Problème :**
  - **Push vers `main` :** après `git push -u origin main`, un simple `git push` depuis `main` pousse vers `main` sans que le texte contienne « main ». Aussi : `x:main`, `x:refs/heads/main`, `--all`, `--mirror`, `--delete main`, `:main`.
  - **Contournement du hook pre-commit :** `git commit -n` (alias court de `--no-verify`), `SKIP=gitleaks git commit`, `git -c core.hooksPath=… commit`, `pre-commit uninstall`.
  - **Réglages et fusion :** `gh api --method PATCH`, `-XPATCH`, `gh api -f …` (POST implicite) ; mutations GraphQL (`mergePullRequest`, `enablePullRequestAutoMerge`, `updateRepository`, `deleteBranchProtectionRule`) ; POST sur `…/merges`, `…/transfer`, `…/hooks`, `…/keys`, `…/actions/runners/registration-token` (contraire au Goal 8) ; `gh repo archive`, `gh repo rename`, `gh workflow disable`, `gh secret set`, `gh variable set`, `gh label delete`.
  - **Portée (egm-style) :** « en PATCH, PUT ou DELETE sur le dépôt » (l. 230) peut viser `repos/EZPK/4X` seul ou toute route sous ce préfixe ; dans le second cas, la création des jalons (l. 192) serait refusée. « qui n'autorise que les trois commandes d'amorçage » se lit comme un refus de toute autre commande, `gh repo create` compris (l. 189). La liste des enchaînements (`&&`, `;`, sous-shell, l. 233) omet `||` et `|`.
- **Raison :** le niveau 1 accepte que les scripts échappent au hook, pas les commandes directes. /home/ezpk/Projects/4X/CLAUDE.md promet que ces commandes sont filtrées. Le Goal 3 annonce plus que le mécanisme décrit.
- **Correction proposée :** passer en liste blanche pour les écritures GitHub : `gh api` hors `GET` autorisé seulement sur une courte liste de routes nommées (issues, jalons, étiquettes, création de pull request, commentaires), GraphQL compris dans le refus par défaut ; `gh repo` limité à `view` et `create`. Pour `git push`, déterminer la vraie branche cible (refspec, sinon branche suivie) et refuser `--all`, `--mirror`, `--delete`. Ajouter `-n`, `SKIP=`, `core.hooksPath`, `pre-commit uninstall`. Mettre toutes ces variantes dans les tests. Sinon, restreindre le Goal 3 à ce qui est réellement couvert et consigner le reste comme risque.

### egm-design-1-4 : les outils autres que Bash échappent aux deux mécanismes

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 141-148, 221-235
- **Problème :** le hook ne porte que sur l'outil Bash. Un serveur MCP GitHub, s'il est configuré, peut fusionner ou modifier un réglage sans passer par Bash. Les outils Edit et Write peuvent modifier `.claude/settings.json`, `.claude/hooks/garde_commandes.py` ou `.git/hooks/pre-commit` dans la copie de travail, ce qui désactive les garde-fous pour les sessions suivantes ; une « correction » du hook pendant une pull request protégée suffit.
- **Raison :** le Goal 3 vise des effets (fusion, réglages), pas seulement des commandes Bash.
- **Correction proposée :** règles `deny` sur les outils MCP GitHub d'écriture, ou hook `PreToolUse` sur tous les outils ; règles `deny` Edit et Write sur `.claude/**` et `.git/hooks/**` ; inscrire la limite au tableau des risques.

### egm-design-1-5 : le contrôle de garde peut bloquer le dépôt, sans procédure de reprise

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural` (point à vérifier)
- **Lignes :** 176-219, 250, 254
- **Problème :**
  - `garde.yml` tourne sur `pull_request_target`, donc dans la version de `main`, et sa tâche est requise. Si cette version est cassée (bug, nom de tâche changé, étiquette absente, droits insuffisants), toutes les pull requests échouent, y compris celle qui répare `garde.yml`. Avec `enforce_admins`, plus aucune fusion n'est possible.
  - Si les noms des contrôles requis de `protection-main.json` ne correspondent pas exactement aux noms des tâches, chaque pull request attend indéfiniment. Le point 4 ne vérifie que `enforce_admins` et le blocage au push.
  - L'agent ne peut pas réparer, puisque l'exception `PUT` est fermée. La protection est posée avant que le garde ait tourné une seule fois.
  - egm-structural ajoute un point à vérifier : l'état d'un workflow `pull_request_target` est-il bien attaché au commit de tête de la pull request, et peut-il donc servir de contrôle requis ?
- **Correction proposée :** au point 4, vérifier que chaque contrôle requis correspond à une tâche réellement lancée, par exemple en comparant avec les contrôles d'une première pull request d'essai ; vérifier le rattachement de l'état de `pull_request_target` ; écrire dans `docs/m0/commandes-proprietaire.md` une procédure de reprise réservée au propriétaire (désactiver `enforce_admins` dans l'interface, fusionner la réparation, réactiver, relire) ; ajouter une ligne au tableau des risques.

### egm-design-1-6 : le signal du garde n'est pas durable, et il dispute la tête de la description au résumé EGM

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural` et `egm-style`
- **Lignes :** 51, 115, 250-254, 262, 302
- **Problème :**
  - Les Goals et le CUJ 5 disent « en tête de son résumé », le §8 et le §12 « en tête de la description ». /home/ezpk/Projects/4X/CLAUDE.md demande aussi à l'agent de mettre le résumé de la revue EGM en tête de la description. Le texte ne dit pas lequel passe en premier.
  - Les événements de `pull_request_target` ne sont pas listés. Par défaut, `edited` n'en fait pas partie : un `gh pr edit --body` efface ou déplace le bloc sans que le garde tourne de nouveau, et la tâche reste verte. Même problème pour le contrôle des termes interdits sur le titre et la description (l. 262).
  - L'étiquette se retire par `gh pr edit --remove-label`, que le hook n'interdit pas.
  - « L'étiquette du contrôle de garde » (l. 51, 115) : le §8 en définit deux ; celle qui est attendue n'est pas nommée.
- **Raison :** le niveau 1 (§10) fait du garde le signal principal pour le propriétaire, qui ne lit pas le code. Le Goal 5 s'en trouve affaibli.
- **Correction proposée :** un seul mot (« description ») ; ordre fixé (bloc du garde, puis résumé EGM) ; déclencheurs `opened`, `synchronize`, `reopened`, `edited` pour le garde et pour les termes ; copie de la liste dans le résumé de la tâche (`$GITHUB_STEP_SUMMARY`), que l'auteur ne peut pas modifier ; refus par le hook du retrait des étiquettes du garde ; nommer « fichiers protégés modifiés » aux l. 51 et 115.

### egm-design-1-7 : `pull_request_target` : la parade ne couvre pas l'injection

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 250, 370, 385
- **Problème :** ne pas récupérer le code de la branche ne suffit pas. Le garde lit des données contrôlées par tout auteur de pull request venue d'un fork : noms de fichiers, titre, nom de branche. Insérées dans un `run:` par `${{ … }}` ou passées telles quelles au shell, elles font exécuter du code avec un jeton en écriture. Un nom de fichier comme `$(curl …)` est valide pour git. Recopiés dans la description, ces noms peuvent aussi injecter du Markdown.
- **Correction proposée :** exigences de conception : aucune expression `${{ github.event.* }}` dans un `run:` ; données passées par variables d'environnement ou fichier JSON lu par le script ; noms échappés dans le bloc ; aucun cache ni artefact partagé avec `pull_request`. Ajouter un test avec un nom de fichier hostile et corriger la parade du tableau des risques (l. 385).

### egm-design-1-8 : une pull request peut neutraliser ses propres contrôles requis

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 34, 44-45, 158-160, 214, 376-385
- **Problème :** `ci.yml` et les scripts de `.github/scripts/` tournent dans la version de la branche. Un `if: false` sur une tâche requise la fait passer à « skipped », que GitHub compte comme une réussite ; une étape peut aussi être remplacée par `true`. « Une pull request rouge ne peut pas être fusionnée » ne tient donc que si la pull request ne touche pas `.github/`. Le garde le signale, mais le document ne l'écrit pas comme limite.
- **Raison :** le niveau 1 accepte un affaiblissement des contrôles signalé après coup ; le document doit dire la même chose au lieu d'annoncer une garantie.
- **Correction proposée :** l'écrire dans The Problem et dans le tableau des risques. Envisager une tâche requise dans `garde.yml` (version de `main`) qui échoue si un contrôle requis est absent ou sauté.

### egm-design-1-9 : secrets : ordre de l'amorçage, et détection en CI après exposition

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural` (point à vérifier)
- **Lignes :** 19, 33, 48-49, 178-190, 209, 242, 369
- **Problème :**
  - La l. 33 dit que la protection doit précéder le premier commit qui pourrait contenir un secret. Pourtant, le blocage au push est activé en dernier, après le push initial.
  - La tâche `gitleaks` en CI tourne quand la branche est déjà publique : elle détecte, elle n'empêche pas. « Le critère reste atteignable » (l. 209) est vrai pour la lettre du niveau 1, pas pour le Goal 4 (« ne peut pas entrer dans le dépôt »).
  - « `gitleaks` sur tout le dossier » (l. 369) analyse aussi des fichiers ignorés, dont `.venv/` après `uv sync`, qui peut contenir des secrets de test de bibliothèques, et peut manquer le contenu exact du commit.
- **Correction proposée :** ordre `gh repo create`, puis `PATCH` de sécurité, puis push initial, puis `PUT` de protection (qui exige que `main` existe). Lancer `gitleaks git` sur le commit initial juste avant le push. Reformuler le Goal 4 et la l. 209 : la CI détecte après exposition, et une détection en CI impose de révoquer le secret.

### egm-design-1-10 : les règles de `gitleaks` ne couvrent pas ce que le niveau 1 interdit

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 48, 237-245
- **Problème :** les règles par défaut de `gitleaks` cherchent des formats de jetons connus. Elles ne trouvent ni l'adresse du PC d'entraînement ou du serveur MLflow (IP privée, nom d'hôte local), ni une valeur assignée aux variables de `.env.example`, ni une graine du monde en ligne. Ces éléments sont interdits par les Non-Functional Requirements du niveau 1 et par /home/ezpk/Projects/4X/CLAUDE.md. Le Goal 4 promet plus que le mécanisme.
- **Correction proposée :** un `.gitleaks.toml` avec des règles propres au projet (plages IPv4 privées, variables du projet suivies d'une valeur non vide hors `.env.example`). Ou bien restreindre le Goal 4 aux formats de jetons et écrire le reste comme non vérifié.

### egm-design-1-11 : le hook pre-commit n'existe que dans le clone où il a été installé

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 152, 241, 369
- **Problème :** `pre-commit install` écrit dans `.git/hooks/`, qui n'est pas versionné. Dans un nouveau clone, il n'y a plus de barrière avant le commit, et rien ne le signale. Il ne reste que la CI, qui arrive après l'exposition (egm-design-1-9).
- **Correction proposée :** le hook Claude Code refuse `git commit` si `.git/hooks/pre-commit` est absent ou n'appelle pas `pre-commit` ; ou un hook `SessionStart` le vérifie. Ajouter une ligne au tableau des risques.

### egm-design-1-12 : le contrôle des termes interdits bloque ses propres pull requests

- **Sévérité :** Major
- **Lentille :** `egm-design`
- **Lignes :** 256-270
- **Problème :** la portée inclut la description, les messages de commit et le nom de la branche. Une pull request qui ajoute un terme à `docs/termes-interdits.md` le cite presque forcément dans un message de commit ou dans le résumé EGM : le contrôle échoue, et avec `enforce_admins` le propriétaire ne peut pas fusionner. Par ailleurs, `tests/outillage/test_termes_interdits.py` doit contenir un terme pour tester le cas « trouvé », et ce fichier n'est pas exclu : `main` serait rouge.
- **Correction proposée :** le script accepte un chemin de liste en argument, et les tests lui passent des termes inventés. Écrire une règle pour les pull requests qui modifient la liste (décrire sans citer), ou exclure description et messages quand la pull request ne touche que `docs/termes-interdits.md`.

### egm-design-1-13 : `pyproject.toml` devient un chemin protégé, alors que toute nouvelle dépendance passe par lui

- **Sévérité :** Major
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural`
- **Lignes :** 249, 287-289
- **Problème :** la configuration de `ruff`, `mypy`, `pytest` et `import-linter` vit dans `pyproject.toml`, qui devient protégé (niveau 1, §10 : « configuration des tests, du linter, du typage »). Les dépendances y vivent aussi. Dès M1, une pull request de fonctionnalité qui ajoute une dépendance (`msgspec`, par exemple) touche un chemin protégé, ce que le niveau 1 interdit. Soit l'étiquette apparaît presque partout et perd son sens, soit chaque dépendance exige une pull request protégée. Le choix n'a ni alternative ni ligne de risque.
- **Correction proposée :** configuration des outils dans des fichiers séparés et protégés (`ruff.toml`, `mypy.ini`, `pytest.ini`, `.importlinter`), `pyproject.toml` et `uv.lock` hors des chemins protégés. Ou bien décider que les dépendances passent par une pull request protégée, et le reporter au niveau 1 (ADR).

### egm-structural-1-2 : qui applique la protection de `main` : le point 5 contredit le point 3

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 178, 219 (comparées à 78, 183, 190, 338)
- **Problème :** la l. 219 dit « C'est cette requête que le propriétaire applique ». Le point 3, la décision de la l. 78 et l'alternative E disent que c'est l'agent de code, par une commande d'amorçage. À la l. 178, dans « Choix du propriétaire, le 2026-10-31 : il applique aussi les réglages du dépôt », le pronom « il » renvoie grammaticalement au propriétaire.
- **Raison :** deux sections du Technical Plan se contredisent sur l'auteur d'une action privilégiée, dans la section qui sert justement à dire « qui lance quoi ».
- **Correction proposée :** l. 178 : « l'agent de code applique aussi la protection de `main` et le blocage des secrets ». l. 219 : « C'est cette requête que l'agent de code applique, par la deuxième commande d'amorçage (point 3). »

### egm-structural-1-3 : le Goal 3 est plus large que son CUJ et que ses essais

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-design` (Nit) et `egm-style`
- **Lignes :** 46-47, 99-103, 296-304
- **Problème :** le Goal 3 couvre la fusion (avec `--admin` et `--auto`), le push vers `main`, le push forcé, `--no-verify`, la protection, les réglages et l'acceptation unique de l'amorçage. Le CUJ 3 ne couvre que `gh pr merge`. Le §12 n'a aucun essai pour le push forcé, `gh api` sur `/protection`, `gh repo edit` ou `gh repo delete`, ni pour une seconde tentative d'amorçage. Le CUJ 3 part d'une pull request verte, mais l'essai « Fusion par l'agent » utilise la pull request rouge : le cas où seul Claude Code peut arrêter la fusion n'est jamais joué, et sur une pull request rouge le refus peut venir de GitHub.
- **Raison :** la vérification du Goal 3 (« chaque commande … est refusée ») n'est rattachée à aucun essai du critère de sortie.
- **Correction proposée :** ajouter au §12 une ligne « Interdictions de Claude Code » listant chaque commande du Goal 3 et les trois secondes tentatives d'amorçage, avec des essais sans danger (push forcé sur une branche `essai/…`, par exemple) ; jouer l'essai de fusion sur une pull request verte (par exemple `essai/chemin-protege`), ou aligner le CUJ 3 sur la rouge en donnant la raison ; élargir le CUJ 3 ou ajouter un CUJ pour les autres commandes. Si certains cas ne sont couverts que par les tests du hook (l. 235), l'écrire dans le Goal.

### egm-structural-1-4 : le Goal 1 n'a pas d'essai, et le refus par GitHub d'un push direct n'est jamais exercé

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-design` et `egm-style`
- **Lignes :** 42-43, 91, 300
- **Problème :** la vérification du Goal 1 (`gh repo view`, historique qui commence par le commit initial, « aucun autre commit sans pull request ») n'a pas d'essai au §12, ni de méthode pour la dernière clause. Le CUJ 1 affirme qu'« un second push direct sur `main` est refusé », mais la l. 300 ne teste que Claude Code, et le refus de GitHub reste au conditionnel (« serait refusé »).
- **Correction proposée :** ajouter un essai où le propriétaire lance `! git push origin HEAD:main` depuis un commit d'essai, avec le message de refus de GitHub cité ; ajouter un essai de lecture (`gh repo view --json visibility`, `git log --first-parent main`) avec l'attendu. Remplacer « serait refusé » par un résultat observé, ou supprimer la phrase.

### egm-structural-1-5 : le préfixe `!` n'est pas défini, et les essais du propriétaire peuvent réussir pour une mauvaise raison

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-design` et `egm-style`
- **Lignes :** 194-195, 298, 301, 337
- **Problème :**
  - En bash, `! cmd` inverse le code de sortie. Suivi de « la commande doit échouer » (l. 194), le texte se lit comme une assertion de test shell. Le sens voulu (commande tapée par le propriétaire dans la session Claude Code) n'est défini qu'à la l. 391, hors du périmètre.
  - L'attendu est seulement « échoue ». Un échec dû à une règle `deny`, au réseau, à un mauvais numéro ou à une pull request déjà fermée compterait comme un succès.
  - Le document suppose sans le dire que les commandes préfixées par `!` échappent au hook et aux règles `deny`. Si ce n'est pas le cas, `! gh pr merge --admin` serait refusé par Claude Code et non par GitHub, et le Goal 2 ne serait pas démontré ; `! git commit --no-verify` serait bloqué de la même façon.
- **Raison :** le Goal 2 exige que le refus vienne de GitHub.
- **Correction proposée :** définir `!` à sa première apparition. Pour chaque commande du propriétaire, donner l'origine attendue du refus et un extrait du message (protection de branche pour la fusion, blocage des secrets pour le push). Ajouter aux Open Questions : « les hooks et les règles `deny` s'appliquent-ils aux commandes `!` ? » ; sinon, lancer ces essais dans un terminal séparé.

### egm-structural-1-6 : les solutions de rechange si `enforce_admins` manque diffèrent selon la section

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 208, 228, 344, 380
- **Problème :** le point 4 propose « abonnement payant, critère réduit … ou autre » ; l'alternative F fait du ruleset « la première solution de rechange à essayer » ; le tableau des risques cite « ruleset, abonnement ou critère réduit ». Le point 4, qui fait foi pour l'exécutant, ne cite pas le ruleset. La l. 228 interdit à l'agent tout `gh api` sur `rulesets`, sans exception : personne n'est désigné pour l'appliquer.
- **Correction proposée :** une seule liste, dans le même ordre, aux trois endroits. Dire qui applique le ruleset (le propriétaire avec `!`, ou une exception d'amorçage supplémentaire) et où est son fichier versionné.

### egm-structural-1-7 : les écarts au niveau 1 sont dispersés, le renvoi « point 19 bis » est faux, et la raison de l'alternative E est inexacte

- **Sévérité :** Major
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style` et `egm-design` (Nit)
- **Lignes :** 178, 230, 269, 338
- **Problème :**
  - Le document s'écarte du niveau 1 (Approved, prioritaire selon /home/ezpk/Projects/4X/CLAUDE.md) sur trois points : le commit initial n'est plus « la seule exception » (niveau 1, §10) ; le push vers `main` et les réglages sortent des règles `deny` (niveau 1, §10) ; la liste des fichiers exclus des termes interdits change (niveau 1, plan détaillé, point 4). Ces écarts ne sont signalés qu'en passant, dans trois sections.
  - La l. 269 dit « reporté dans le niveau 1 au point 19 bis ». Le plan détaillé du niveau 1 va de 1 à 11 ; le 19 bis est un point du plan détaillé de ce document-ci.
  - Le document ne dit pas sur quelle règle il s'appuie pour modifier un niveau 1 approuvé sans ADR. Une session neuve qui suit l'ordre de priorité de CLAUDE.md appliquerait le niveau 1 et refuserait les exceptions d'amorçage.
  - Alternative E (l. 338) : « s'en tenir au niveau 1 » ne vaut que pour le push initial. Pour les deux réglages, le niveau 1 et CLAUDE.md interdisent à l'agent toute modification, ce qui est plus proche de l'alternative E elle-même. Le choix reste celui du propriétaire, mais sa justification doit être exacte.
- **Correction proposée :** une sous-section « Écarts au niveau 1 » (Overview ou tête du Technical Plan) qui liste les trois écarts, leur décision (propriétaire, 2026-10-31), la règle qui permet la modification ou l'ADR requise, et le point du plan qui les reporte. l. 269 : « reporté dans le niveau 1 par le point 19 bis du plan détaillé de ce document ». l. 338 : « le niveau 1 prévoit le push initial par l'agent ; le propriétaire étend l'exception aux deux réglages (plan détaillé, point 19 bis) ».

### egm-style-1-2 : le point 4 dit « avant tout le reste » et « juste après la création du dépôt », alors que la vérification suit l'amorçage

- **Sévérité :** Major
- **Lentille :** `egm-style` ; signalé aussi par `egm-structural` (Nit)
- **Lignes :** 69, 191, 199, 205
- **Problème :** tant que la protection n'est pas appliquée, la lecture de `…/branches/main/protection` renvoie 404 (c'est la condition de la l. 183). Le tableau des l. 186-191 place la vérification après les trois commandes d'amorçage. Le titre et les l. 69 et 205 disent le contraire ; lu à la lettre, l'exécutant vérifierait avant d'appliquer.
- **Correction proposée :** titre « 4. La vérification des réglages GitHub, juste après l'amorçage » ; l. 205 et 69 : « juste après les trois commandes d'amorçage ».

### egm-style-1-3 : « seule la tâche "tests de l'outillage" est requise » contredit le point 5 et le Goal 6

- **Sévérité :** Major
- **Lentille :** `egm-style` ; signalé aussi par `egm-structural` (Nit)
- **Lignes :** 52, 160, 214, 283
- **Problème :** la l. 214 rend requises toutes les tâches de `ci.yml`. La l. 283 se lit « une seule tâche requise ». Le Goal 6 liste les cinq contrôles du niveau 1, sans les tests de l'outillage, qui sont pourtant requis : c'est un ajout par rapport au niveau 1, non signalé.
- **Correction proposée :** l. 283 : « À M0, parmi les tests, seule la tâche "tests de l'outillage" est requise ; "tests et scénarios" s'ajoute à M1. » Goal 6 : ajouter « et les tests de l'outillage (hook et scripts) », en signalant l'ajout.

### egm-style-1-4 : deux mots pour le même concept : « contrôle obligatoire » et « contrôle requis »

- **Sévérité :** Major
- **Lentille :** `egm-style`
- **Lignes :** 21, 52, 95 (« obligatoire ») ; 168, 214, 254, 283 (« requis ») ; « tâche » passim
- **Problème :** le glossaire ne définit que « contrôle obligatoire ». Le lecteur peut croire qu'un « contrôle requis » (required status check de GitHub) est une autre notion. « Tâche » (job GitHub Actions) n'est pas défini.
- **Correction proposée :** « contrôle obligatoire » partout, ou une phrase au point 5 : « les contrôles obligatoires (required status checks de GitHub) sont les tâches (jobs) suivantes : … ».

### egm-style-1-5 : « compte rendu de M0 » n'est pas défini

- **Sévérité :** Major
- **Lentille :** `egm-style`
- **Lignes :** 191, 294, 382
- **Problème :** le compte rendu reçoit les preuves de plusieurs Goals et sert de signal de risque (l. 382), mais le document ne dit ni ce qu'il est (fichier, ticket, pull request), ni où il se trouve, ni qui le rédige.
- **Correction proposée :** le définir à sa première mention, par exemple « le compte rendu de M0 (`docs/m0/compte-rendu.md`, rédigé par l'agent de code et relu par le propriétaire) », ou tout autre emplacement choisi par le propriétaire.

### egm-style-1-6 : on ne sait pas quand la tâche du contrôle de garde réussit

- **Sévérité :** Major
- **Lentille :** `egm-style`
- **Lignes :** 254
- **Problème :** « La tâche réussit toujours quand elle a pu étiqueter » ne dit rien d'une pull request qui ne touche aucun chemin protégé : il n'y a rien à étiqueter. Lu à la lettre, ce contrôle requis bloquerait toute fusion.
- **Correction proposée :** « La tâche réussit dès qu'elle a terminé son analyse et posé l'étiquette éventuelle. Elle n'échoue qu'en cas d'erreur technique (lecture de l'API, écriture de l'étiquette). »

### egm-style-1-7 : alternative B : une phrase qui se lit à contresens, et une justification sans source

- **Sévérité :** Major
- **Lentille :** `egm-style`
- **Lignes :** 320
- **Problème :** « mypy est le plus connu des agents de code » se lit « mypy est, parmi les agents de code, le plus connu ». Sous l'une ou l'autre lecture, l'affirmation n'a pas de source.
- **Correction proposée (sans toucher au choix) :** « parce que les agents de code connaissent mieux mypy, d'après l'expérience du propriétaire, et que mypy 2.4.1 a été vérifié sous Python 3.15 ».

### egm-style-1-8 : risque « une exception d'amorçage se rouvre » : la parade contredit The Problem

- **Sévérité :** Major
- **Lentille :** `egm-style` ; signalé aussi par `egm-design` (Nit)
- **Lignes :** 382 (comparée à 32)
- **Problème :** « seul le propriétaire peut retirer la protection, par l'interface » contredit la l. 32 : GitHub ne distingue pas l'agent du propriétaire. L'agent peut aussi la retirer par GraphQL (egm-design-1-3). Si la protection disparaît, l'exception `PUT` se rouvre et applique le fichier tel qu'il est sur le disque (egm-structural-1-1). Le signal (« contrôle de la protection dans le compte rendu ») n'a lieu qu'une fois.
- **Correction proposée :** « la suppression de `main` est interdite par la protection ; le hook refuse toute écriture directe sur `/protection` ; un retrait par l'interface ou par un script reste possible : c'est le risque accepté de §10 du niveau 1 ». Pour le signal, indiquer un contrôle répété (lequel, à quelle fréquence), ou écrire qu'il n'y en a pas. Reprendre le texte une fois egm-structural-1-1 et egm-design-1-3 traités.

--------------------------------------------------------------------------------

## Nits

### egm-design-1-14 : les conditions d'amorçage confondent « absent » et « lecture en échec »

- **Sévérité :** Nit
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural`
- **Lignes :** 182-183, 233
- **Problème :** un `git ls-remote` en échec ne renvoie rien non plus. GitHub renvoie aussi 404 pour un dépôt ou une branche introuvable, ou faute de droits. Ces conditions peuvent ouvrir l'exception à tort, contrairement à la l. 233.
- **Correction proposée :** « code de sortie 0 et sortie vide » ; « 404 avec le message `Branch not protected` », tout autre 404 étant refusé.

### egm-design-1-15 : la catégorie `references` : libellé ambigu et cas mixte non défini

- **Sévérité :** Nit
- **Lentille :** `egm-design` ; signalé aussi par `egm-structural`
- **Lignes :** 252
- **Problème :** « si seuls des fichiers de catégorie `references` sont modifiés » ne se produit jamais, car une pull request de fonctionnalité modifie aussi du code. Le cas d'une pull request qui touche à la fois `protege` et `references` n'est pas défini.
- **Correction proposée :** « si, parmi les chemins protégés modifiés, il n'y a que des `references` », et dire quelle étiquette s'applique dans le cas mixte.

### egm-design-1-16 : identifier les scénarios en attente par leur titre est fragile

- **Sévérité :** Nit
- **Lentille :** `egm-design`
- **Lignes :** 279-281
- **Problème :** deux scénarios d'un même fichier peuvent avoir le même titre. Un plan de scénario (`Scenario Outline`) produit plusieurs tests : si certains exemples passent et d'autres non, `strict` fait échouer la CI.
- **Correction proposée :** interdire, et vérifier, les titres en double dans un fichier ; définir le cas du plan de scénario (tous ses exemples, ou un exemple précis).

### egm-design-1-17 : les scripts de l'outillage échappent au typage strict

- **Sévérité :** Nit
- **Lentille :** `egm-design`
- **Lignes :** 287
- **Problème :** `mypy` ne porte que sur `src/` et `tests/`. `.claude/hooks/garde_commandes.py` et les scripts de `.github/scripts/`, cœur de M0, ne sont pas typés strictement. Les tests devront importer depuis un dossier dont le nom commence par un point.
- **Correction proposée :** ajouter ces chemins à la configuration de mypy, et dire comment les tests chargent les scripts (`importlib`, ou module partagé).

### egm-design-1-18 : réglages du dépôt et préalables absents

- **Sévérité :** Nit
- **Lentille :** `egm-design`
- **Lignes :** 184, 250, 371-372
- **Problème :** ni `securite-depot.json` ni la vérification ne couvrent le jeton par défaut des workflows en lecture seule, l'interdiction aux Actions de créer ou d'approuver des pull requests, l'approbation des workflows lancés par les forks. Les étiquettes du garde doivent exister avant sa première exécution, sinon la tâche requise est rouge. La CI n'impose pas `uv sync --locked`.
- **Correction proposée :** trancher ces réglages (ou les écarter) dans la conception ; créer les étiquettes pendant l'amorçage ; imposer `--locked` en CI.

### egm-structural-1-8 : les renvois « point N » s'écrivent de quatre façons

- **Sévérité :** Nit
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** 69, 230, 243, 253, 344, 380
- **Problème :** « Technical Plan, point 4 », « point 4 », « point 3 », « point 4 du plan ». Le plan détaillé a lui aussi des points numérotés : « point 4 du plan » (l. 344) se lit comme le point 4 du plan détaillé.
- **Correction proposée :** « Technical Plan, point N » partout, et « plan détaillé, point N » pour l'autre série.

### egm-structural-1-9 : le Goal 7 promet une raison pour chaque décision, toutes ne l'ont pas

- **Sévérité :** Nit
- **Lentille :** `egm-structural`
- **Lignes :** 55, 133, 258, 276
- **Problème :** le format des termes interdits et l'identifiant `steps` n'ont pas de raison écrite ; la raison de `pytest-bdd` est dans l'alternative A et non dans le Technical Plan comme l'annonce la l. 55 ; la l. 133 attribue le choix de `ruff` au niveau 1, qui dit seulement « linter ».
- **Correction proposée :** une raison d'une ligne pour chaque décision concernée ; origine de `ruff` : « choix de ce document ».

### egm-structural-1-10 : le Goal 8 réunit deux objectifs, et plusieurs vérifications n'ont pas d'essai

- **Sévérité :** Nit
- **Lentille :** `egm-structural`
- **Lignes :** 52-53, 56-57, 304
- **Problème :** les runners ont un essai, pas les jalons GitHub. « CI verte sur `main` » (Goal 6) n'en a pas non plus.
- **Correction proposée :** séparer en Goal 8 et Goal 9, et ajouter les essais correspondants au §12.

### egm-structural-1-11 : les Open Questions contiennent des décisions prises, et les puces sont mélangées

- **Sévérité :** Nit
- **Lentille :** `egm-structural`
- **Lignes :** 16-22, 61-79
- **Problème :** les décisions tranchées sont rangées sous « Open Questions » et répètent le tableau du point 1. Les listes de premier niveau utilisent tantôt `-`, tantôt `*   `.
- **Correction proposée :** déplacer ces décisions vers le point 1 du Technical Plan, ou les remplacer par un renvoi ; uniformiser le marqueur de puce.

### egm-structural-1-12 : sections du gabarit absentes et sources non citées

- **Sévérité :** Nit
- **Lentille :** `egm-structural` ; signalé aussi par `egm-style`
- **Lignes :** document entier, notamment 201, 326, 344
- **Problème :** le niveau 1 a « Additional Resources » et « Future Improvements », pas la cible. La licence à revoir, le ruleset de rechange et le compte séparé y auraient leur place. « La documentation consultée » (l. 201) n'est ni liée ni datée.
- **Correction proposée :** ajouter les deux sections, avec les liens et les dates de consultation de la documentation GitHub (protection de branche, blocage des secrets au push).

### egm-structural-1-13 : petits défauts de mise en forme

- **Sévérité :** Nit
- **Lentille :** `egm-structural`
- **Lignes :** 8, 186, 364
- **Problème :** séparateur `----` entre Alternatives et Non-Functional Requirements, absent du niveau 1 ; second tableau du point 3 collé au premier, sans phrase d'introduction ; la convention de langue (l. 8) ne cite pas les intitulés du gabarit du plan, contrairement au niveau 1.
- **Correction proposée :** retirer le séparateur, introduire le second tableau (« Qui lance chaque étape : »), reprendre la phrase de la l. 8 du niveau 1.

### egm-structural-1-14 : le CUJ 3 du niveau 1, marqué « M0 et suivants », n'est pas rattaché

- **Sévérité :** Nit
- **Lentille :** `egm-structural`
- **Lignes :** 81-121
- **Problème :** la cible ne dit pas quelles conditions de ce CUJ du niveau 1 M0 couvre, ni lesquelles attendent M1.
- **Correction proposée :** une phrase de correspondance en tête des CUJs.

### egm-structural-1-15 : le type des pull requests d'essai n'est pas dit

- **Sévérité :** Nit
- **Lentille :** `egm-structural`
- **Lignes :** 292-306
- **Problème :** le niveau 1 limite à une pull request ouverte par type. Le document ne dit pas le type de chaque pull request d'essai, ni que les essais se jouent l'un après l'autre.
- **Correction proposée :** une colonne « type » au tableau, ou la phrase « une seule pull request d'essai ouverte à la fois ».

### egm-structural-1-16 : des risques cités ailleurs manquent au tableau des risques

- **Sévérité :** Nit
- **Lentille :** `egm-structural`
- **Lignes :** 130, 332, 376-385
- **Problème :** le risque de Python 3.15 sur le PC d'entraînement (alternative D) et l'absence de licence sur un dépôt public (alternative C) ne sont pas au tableau. La l. 130 parle des « clients tiers prévus par le niveau 1 », alors que le niveau 1 les range en Non-Goals.
- **Correction proposée :** ajouter les deux lignes ; écrire « rendus possibles par le protocole » au lieu de « prévus ».

### egm-style-1-9 : antécédent flou de « eux »

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 32
- **Correction proposée :** « GitHub ne distingue pas l'agent de code du propriétaire. »

### egm-style-1-10 : « aucun dépôt n'existe » alors qu'un dépôt git local existe

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 85
- **Correction proposée :** « aucun dépôt GitHub n'existe ».

### egm-style-1-11 : « pull request de test » et « essai » désignent la même chose

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 45, 51, 292-306
- **Correction proposée :** « pull request d'essai » partout, en accord avec les branches `essai/…`.

### egm-style-1-12 : « étiquette » et « empreinte » ont chacune plusieurs sens

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 51, 115, 137, 242, 251-252, 350, 371
- **Problème :** « étiquette » sert pour le label GitHub et pour le tag git (l. 137). « Empreinte » sert pour le SHA de commit, la somme de contrôle d'un binaire et, au glossaire, l'empreinte d'état (« empreintes de référence »).
- **Correction proposée :** « tag git » à la l. 137 ; « SHA du commit » et « somme de contrôle SHA-256 » pour les deux autres sens.

### egm-style-1-13 : justifications du tableau du point 1 : jargon et jugement sans raison

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 136-137, 361
- **Problème :** « décision mécanique » relève du jargon, et la relative « qui ne peut pas commencer par un chiffre » est lourde. « Bonne pratique de sécurité » est un jugement sans raison. La l. 361 (« entrent en conflit ») affirme plus que le conditionnel de la l. 136.
- **Correction proposée :** « contrainte technique : `4X` commence par un chiffre, ce qu'un nom de paquet Python interdit » ; « un tag peut être déplacé vers un autre commit, pas un SHA » ; aligner le mode des l. 136 et 361.

### egm-style-1-14 : tournures familières ou imprécises

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 157, 193, 298
- **Correction proposée :** « (si disponible) » ; « Mener les essais » ; « un fichier qui enfreint une règle de `ruff` ».

### egm-style-1-15 : « à juste titre » et « les lui interdisent »

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 197
- **Correction proposée :** « …parce que les règles de l'agent de code lui interdisent la fusion et `--no-verify`. »

### egm-style-1-16 : formats des listes insuffisamment précis

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 258-259, 279, 281
- **Problème :** « les lignes non vides qui suivent le titre `## Termes` » : jusqu'où ? « Mot entier » n'est pas défini pour un terme qui contient un tiret. `<fichier>` (l. 279) : relatif à quel dossier ? « Un nom de la liste », puis « entrée », dans la même puce.
- **Correction proposée :** « jusqu'à la fin du fichier » ou « jusqu'au titre suivant » ; définir le mot entier pour les termes à tiret ; « chemin relatif à `tests/scenarios/` » ; « entrée » les deux fois.

### egm-style-1-17 : points divers

- **Sévérité :** Nit
- **Lentille :** `egm-style`
- **Lignes :** 55, 63, 276, 314-362, 374
- **Problème et correction :**
  - l. 374 : « runners gratuits de GitHub, gratuits pour un dépôt public » : « runners hébergés par GitHub, gratuits pour un dépôt public ».
  - l. 314 à 362 : « Raison du rejet : parce que … » : supprimer « parce que ».
  - l. 63 : « alternative G du niveau 1 » partage sa lettre avec l'alternative G de ce document ; garder « du niveau 1 » bien visible.
  - l. 55 et 276 : « le glossaire est mis à jour » : préciser quand (« sera mis à jour, plan détaillé, point 20 »).

--------------------------------------------------------------------------------

## Remarque hors périmètre

egm-structural signale que /home/ezpk/Projects/4X/docs/feuille-de-route.md affiche encore M0 « à écrire ». Selon le circuit du niveau 1 (§10), le statut passe à « en revue » dès la rédaction, sur décision du propriétaire. Ce n'est pas un constat sur la cible.

## Correspondance des constats bruts

| Identifiant | egm-design | egm-structural | egm-style |
| --- | --- | --- | --- |
| egm-structural-1-1 | 2 | 1 | M2, M3 |
| egm-style-1-1 | 11 | 3 | B1, N2, N12 |
| egm-design-1-1 | 1 | | |
| egm-design-1-2 | 3 | 7 | |
| egm-design-1-3 | 4 | 8 | M12, N13 (enchaînements) |
| egm-design-1-4 | 5 | | |
| egm-design-1-5 | 6 | 25 (1er point) | |
| egm-design-1-6 | 7 | 12 | M11, N4 |
| egm-design-1-7 | 8 | | |
| egm-design-1-8 | 9 | | |
| egm-design-1-9 | 10 | 25 (3e point) | |
| egm-design-1-10 | 12 | | |
| egm-design-1-11 | 13 | | |
| egm-design-1-12 | 14 | | |
| egm-design-1-13 | 15 | 11 | |
| egm-structural-1-2 | | 2 | M1 |
| egm-structural-1-3 | 18 | 4 | M14 (Goal 3) |
| egm-structural-1-4 | 16 (2e point) | 5 | M14 (CUJ 1) |
| egm-structural-1-5 | 16 (1er point) | 6 | M6 |
| egm-structural-1-6 | | 9 | M5 |
| egm-structural-1-7 | 19 | 10 | M8 |
| egm-style-1-2 | | 14 | M4 |
| egm-style-1-3 | | 15 | M9 |
| egm-style-1-4 | | | M10 |
| egm-style-1-5 | | | M7 |
| egm-style-1-6 | | | M13 |
| egm-style-1-7 | | | M15 |
| egm-style-1-8 | 20 | | M16 |
| egm-design-1-14 | 17 | 23 | |
| egm-design-1-15 | 21 | 25 (2e point) | |
| egm-design-1-16 | 22 | | |
| egm-design-1-17 | 23 | | |
| egm-design-1-18 | 24 | | |
| egm-structural-1-8 | | 13 | N13 (l. 344) |
| egm-structural-1-9 | | 16 | |
| egm-structural-1-10 | | 17 | |
| egm-structural-1-11 | | 18 | |
| egm-structural-1-12 | | 19 | N10 (l. 201) |
| egm-structural-1-13 | | 20 | |
| egm-structural-1-14 | | 21 | |
| egm-structural-1-15 | | 22 | |
| egm-structural-1-16 | | 24 | |
| egm-style-1-9 | | | N1 |
| egm-style-1-10 | | | N3 |
| egm-style-1-11 | | | N5 |
| egm-style-1-12 | | | N6 |
| egm-style-1-13 | | | N7, N8 |
| egm-style-1-14 | | | N9 |
| egm-style-1-15 | | | N10 (l. 197) |
| egm-style-1-16 | | | N11 |
| egm-style-1-17 | | | N13 (reste) |

Les 79 constats bruts se retrouvent tous dans ce tableau.
