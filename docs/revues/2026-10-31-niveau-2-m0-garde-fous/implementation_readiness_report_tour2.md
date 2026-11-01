# Rapport de revue Goldfish : étape 9 (test de préparation à l'implémentation), tour 2

**Cible :** /home/ezpk/Projects/4X/docs/designs/niveau-2-m0-garde-fous.md (l. 563 à 1069 : « Detailed Implementation Plan » et « Verification Plan »). Les l. 1 à 562 (la spécification) servent de référence.
**Date :** 2026-11-01
**Tour :** 2, la seule réaudit autorisée.
**Standard :** /home/ezpk/.claude/plugins/cache/egm/egm/0.1.0/resources/document_standards/implementation-readiness-standard.md (pour egm-implementation-readiness et egm-codebase-details). egm-style a travaillé avec sa persona seule.
**Rapport du tour 1 :** /home/ezpk/Projects/4X/docs/revues/2026-10-31-niveau-2-m0-garde-fous/implementation_readiness_report.md
**Résolution appliquée :** /home/ezpk/Projects/4X/docs/revues/2026-10-31-niveau-2-m0-garde-fous/goldfish_review_report_etape9.md

## État des relecteurs

| Relecteur | État | Constats bruts |
| --- | --- | --- |
| `egm-implementation-readiness` | terminé, au premier essai | 1 Blocker, 2 Major nouveaux + 3 restes Major, 10 Nit nouveaux + 4 restes Nit |
| `egm-codebase-details` | terminé, au premier essai | 1 Blocker, 9 Major nouveaux + 3 restes Major, 12 Nit |
| `egm-style` | terminé, au premier essai | 7 Major (dont 1 « Blocker si confirmé »), 22 Nit |

Aucun relecteur n'a échoué, et aucun n'a dû être relancé.

**Après dédoublonnage : 1 Blocker, 14 Major et 29 Nit nouveaux.** Les restes des constats du tour 1 partiellement résolus ne sont pas comptés dans ces nombres. Ils figurent dans la section 1 : un seul d'entre eux, cd-1-12, est encore Major. Quand plusieurs relecteurs signalent le même point, le constat garde la sévérité la plus haute.

**Règle de rattachement.** Un problème qui existait déjà au tour 1 et qui n'a pas été corrigé reste sous son identifiant du tour 1. Un défaut apparu avec le nouveau texte (une commande, une interface ou un « avant » faux) reçoit un identifiant nouveau, même s'il découle d'une correction du tour 1.

**Vérifié par le synthétiseur dans les fichiers :**
- /home/ezpk/Projects/4X/CLAUDE.md l. 4 et /home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md l. 412 : « jamais « acceptée » » ;
- /home/ezpk/Projects/4X/docs/glossaire.md l. 8 : « la phrase du [document de niveau 1](designs/architecture-niveau-1.md) qui définit le terme ». La chaîne « avant » de la l. 923 du plan n'y figure pas telle quelle ;
- /home/ezpk/Projects/4X/docs/adr/README.md l. 17-18 (« Conséquences », « Condition de révision ») et l. 23 (« Aucune ADR pour l'instant. ») ;
- /home/ezpk/Projects/4X/CLAUDE.md l. 47 : la puce « Le dépôt est créé au début de M0. » contient trois phrases, dont « C'est la seule exception […], et elle ne vaut qu'une fois » ;
- /home/ezpk/Projects/4X/CLAUDE.md l. 32 : la liste actuelle des chemins protégés nomme `docs/termes-interdits.md`.

**Non vérifié par exécution.** Aucun relecteur n'a lancé d'outil, et le synthétiseur non plus. Ce que ce rapport dit de `pytest-bdd`, `gh`, de l'API GitHub, de `uv`, `gitleaks` et `pytester` vient des connaissances des relecteurs, avec le degré de confiance qu'ils ont indiqué. Le Blocker (`NoScenariosFound`) est donné avec une confiance haute par les trois relecteurs, mais il doit être confirmé par une commande avant d'être corrigé.

## Verdict

**Le plan ne peut pas encore être exécuté étape par étape sans décision importante.** La réécriture règle 33 des 43 constats du tour 1. Les 10 autres sont partiellement résolus, et aucun ne reste entièrement ouvert. Mais le nouveau texte apporte des défauts propres :
- `uv run pytest` échoue dès la collecte : le point 37 s'arrête avant le commit initial, et E1 tombe ;
- le garde est rouge sur toute pull request qui ne touche aucun chemin protégé ;
- les appels `gh` des workflows n'ont pas de jeton ;
- le contrôle des termes interdits n'a pas de comportement défini sur un push, ni pour les fichiers supprimés, ni pour lire ses exclusions ;
- plusieurs gestes des essais ne passent pas la liste blanche du hook, ou contredisent `CLAUDE.md`.

Réponses aux quatre questions du standard :
1. **Exécutable fichier par fichier sans décision importante ?** Non. Restent à décider : `test_scenarios.py` à M0, le comportement de `termes_interdits.py` sur un push et pour un fichier supprimé, le format des exclusions, la conduite à tenir si `exclude-newer` rend les bornes basses impossibles à satisfaire, la politique du hook pour fermer une pull request et réécrire une description, et la manière d'accepter l'ADR sans enfreindre `CLAUDE.md`.
2. **Chaque fichier touché est-il listé ?** Oui. Mais `tests/scenarios/test_scenarios.py` est annoncé comme chemin protégé, alors qu'aucun motif de la liste ne le couvre (cd-1-12).
3. **Les préconditions sont-elles en place ?** Dans l'ensemble, oui. Les exceptions : le hook pre-commit n'est pas encore installé au point 36 (ir-1-15) ; E4 a besoin d'une pull request E7 verte, ce qui est impossible tant que le Blocker n'est pas réglé ; `notes-m0.md` est écrit avant d'être créé.
4. **Le Verification Plan peut-il passer tel qu'il est écrit ?** Non. « Tests » échoue (Blocker), E1 échoue (`tests-outillage`, et `termes-interdits` sur le push), et `uv lock` peut échouer (egm-implementation-readiness-2-3).

---

## 1. Statut des constats du tour 1

Bilan : **33 résolus, 10 partiellement résolus, 0 non résolu.**

| Constat | Statut | Justification (lignes du plan actuel) |
| :-- | :-- | :-- |
| ir-1-1, commentaire de `en_attente.txt` | résolu | l. 402, 764, 846, 849, 887, 895 |
| ir-1-2, `gitleaks` au premier push | résolu | l. 808, 810, 817. Le même cas n'est pas réglé pour `termes-interdits` : voir cd-2-4 |
| ir-1-3, commit initial exécutable | résolu | l. 1003-1016. La suite échoue pour une autre raison : cd-2-1 |
| ir-1-4, statut du document et de la feuille de route | résolu | l. 575-582, 1052-1055 |
| ir-1-5, hook testé avant son activation | résolu | l. 978-989, 996 |
| ir-1-6, procédure de la phase 0 | résolu | l. 594, 1000 |
| ir-1-7, vérification de `!` | résolu | l. 592, 1035. Reste le décompte de « quatre » points : style-2-3 |
| ir-1-8, entrées et sorties des scripts | **partiellement** | Les interfaces sont fixées (l. 735-765). Mais le comportement sur un push, les fichiers supprimés, le format des exclusions et la « forme échappée » restent ouverts : cd-2-4, cd-2-5, ir-2-1, style-2-13 |
| ir-1-9, contenu des fichiers de configuration | résolu | l. 667-677. Les noms de sections de `.importlinter` ne sont pas écrits, mais ils se déduisent |
| ir-1-10, disposition des tests | résolu | l. 855-900. La session imbriquée garde un reste : cd-2-11 |
| ir-1-11, textes imposés | **partiellement** (reste Nit, et Major par style-2-2) | Les textes de `CLAUDE.md`, `termes-interdits.md` et `.env.example` sont donnés mot pour mot (l. 647, 938, 944-960). Au niveau 1, « reçoit la même mention » (l. 966) ne donne pas de texte, et la place du lien §10 conservé (l. 951) n'est pas dite. Voir aussi style-2-2 |
| ir-1-12, `.gitleaks.toml` | résolu | l. 701-711 |
| ir-1-13, actions et Python en CI | résolu | l. 809-813, 827-828. Reste la version de `uv` sur le runner : cd-2-13 |
| ir-1-14, `settings.local.json` et modèle de `.gitignore` | résolu | l. 638, 641 |
| ir-1-15, commande d'essai du hook | **partiellement** (reste Nit) | La commande est fixée (l. 1001). Mais `.git/hooks/pre-commit` n'est installé qu'au point 37, étape 2 (l. 1008). Au point 36, le hook peut donc refuser pour « hook pre-commit absent » (spéc. l. 319), et non pour le contournement attendu. Correction : lancer `uv run pre-commit install` avant le point 36, ou accepter les deux messages |
| ir-1-16, chemins protégés dans `CLAUDE.md` et au niveau 1 | résolu | l. 45, 957, 968 |
| ir-1-17, étiquettes et jalons | résolu | l. 1026, 1031. Restes : cd-2-2 (retrait de l'étiquette) et ir-2-2 (boucle des jalons) |
| ir-1-18, textes qui citent des commandes | **partiellement**, comme la résolution le prévoyait | l. 569. Mais E7 (spéc. l. 430) emploie `gh pr edit --body` : voir ir-2-2 |
| ir-1-19, forme de `required_status_checks` | résolu | l. 781, 807. Le test des `name:` reste imprécis : style-2-16 |
| cd-1-1, `[build-system]` | résolu | l. 659-660 (fait vérifié) |
| cd-1-2, `.pre-commit-config.yaml` | résolu | l. 716-729, 1066 |
| cd-1-3, règle des 14 jours | résolu | l. 603-607, 660-661. La correction ouvre deux points nouveaux : ir-2-3 et cd-2-9 |
| cd-1-4, Python, cache et droits de `garde.yml` | résolu | l. 827-829 |
| cd-1-5, pagination et renommages | **partiellement** | `--paginate` et `previous_filename` sont prévus (l. 750, 753, 832, 876). Mais la commande donnée produit un JSON invalide au-delà d'une page : cd-2-7 |
| cd-1-6, copies de référence du hook | résolu | l. 861, 976 |
| cd-1-7, glossaire | **partiellement** | Le Modify de l'entrée existante et les nouvelles entrées sont donnés (l. 923-931). Mais le texte « avant » de la l. 8 est faux : cd-2-8 |
| cd-1-8, couverture annoncée | résolu | l. 854-900, 1067 |
| cd-1-9, REST et description vide | résolu (refus partiel motivé) | l. 751, 833, 835 |
| cd-1-10, `ruleset-main.json` | résolu par report décidé | Le fichier n'est écrit que si la solution de rechange est déclenchée (spéc. l. 272 ; étape 8, N-2) |
| cd-1-11, `push -u` à E5 | résolu | spéc. l. 428 |
| cd-1-12, module qui appelle `scenarios()` | **partiellement** (**reste Major**) | L'emplacement est fixé (l. 847, « chemin protégé »). Mais la liste des l. 338-360, reprise « exactement » au point 20 (l. 770), ne couvre sous `tests/scenarios/` que `**/*.feature`, `steps/**` et `conftest.py`. Le risque du tour 1 reste donc entier : une pull request de fonctionnalité peut vider `test_scenarios.py` sans recevoir l'étiquette. Correction : ajouter `tests/scenarios/test_scenarios.py` (ou `tests/scenarios/*.py`) au Technical Plan, point 8, avec un cas dans `test_garde.py`. À régler avec cd-2-1. Signalé par les trois relecteurs |
| style-1-1, où garder les résultats | résolu | l. 567, 620-623, 642. L'ordre reste à revoir : style-2-3 |
| style-1-2, une demande par commande | résolu | l. 1020-1025. La tournure reste à revoir : style-2-8 |
| style-1-3, renvois au plan du niveau 1 | résolu | l. 970-971 |
| style-1-4, marque « propriétaire » et état en tête de phase | **partiellement** (reste Nit) | La marque existe (l. 575, 914, 1035). Mais la l. 565 promet que chaque phase dit en tête l'état qu'elle laisse, et les phases 3, 4 et 5 ne le disent pas (l. 1029, 1033, 1038). Le point 48, une décision du propriétaire, ne porte pas la marque |
| style-1-5, forme des étapes | **partiellement** (reste Nit) | Les actions des phases 0 et 1 sont des titres `#### N. Action —`, celles des phases 2 à 4 une liste numérotée (l. 1022-1046). Les trois relecteurs le relèvent |
| style-1-6, mention « chemin protégé » | résolu | La mention est présente partout où elle s'applique. Reste un point mineur : « hors des chemins protégés » manque aux points 8, 13 et 14. La mention du point 25 sur `test_scenarios.py` est fausse : voir cd-1-12 |
| style-1-7, renvois mal formés | résolu | l. 818, 834, 970-971, 976 |
| style-1-8, texte du `README.md` | **partiellement** (reste Nit) | Le plan n'a plus qu'un texte (l. 696). Mais la spéc. l. 416 en cite toujours un autre (« Tous droits réservés, aucune licence »). La l. 618 dit que le README « reprend ces étapes », alors qu'il renvoie seulement au point 4 (l. 695) |
| style-1-9, termes du point 18 | résolu | l. 793, 800 |
| style-1-10, « manque ou diffère » | résolu | l. 1027 |
| style-1-11, formulations vagues | résolu | l. 667, 742, 756, 763, 864 |
| style-1-12, langue et nommage | résolu | l. 647, 849, 889, 1048, 1069 |

Désaccords tranchés :
- **cd-1-5 et cd-1-7.** implementation-readiness et style les jugent résolus, codebase-details partiellement résolus. Le synthétiseur retient « partiellement », sur des faits techniques et sur un fait textuel vérifié (glossaire l. 8).
- **style-1-4 et style-1-8.** Seul style les juge partiellement résolus. Les manques sont vérifiables (l. 1029, 1033, 1038 ; spéc. l. 416 ; l. 618), et le synthétiseur retient donc « partiellement ».

---

## 2. Constats acceptés : effet sur le plan tel qu'il est écrit

- **egm-design-2-2 (liste blanche du hook).** Le plan échoue à cause de lui : E7 et la fermeture des pull requests d'essai. Les trois relecteurs le disent. Le cas est traité dans **ir-2-2**.
- **egm-style-2-2 (condition du `PATCH`).** Si le blocage des secrets est déjà actif sur un dépôt public neuf, le hook refuse le point 39, et le plan ne dit pas que ce refus vaut succès. L'agent s'arrête alors et demande au propriétaire : c'est un arrêt, pas un échec. Confiance basse sur la valeur par défaut. Le reste à écrire est dans style-2-7.
- **egm-structural-2-1, 2-2, 2-4, 2-16, 2-17 ; egm-design-1-6, 2-6, 2-7 ; M-A et M-B (zoom-out intermédiaire).** Ils sont bien traités, et le plan n'échoue pas à cause d'eux. Ils ne sont pas signalés à nouveau. Pour 2-4 (ADR), la façon d'accepter l'ADR contredit `CLAUDE.md` : c'est le constat nouveau **cd-2-6**.

---

## 3. Nouveaux constats

### 3.1 Blocker

#### egm-codebase-details-2-1 : `scenarios(".")` sans aucun `.feature` fait échouer la collecte de pytest. Sévérité : Blocker
- **Relecteurs :** codebase-details (B-1), implementation-readiness (N1), style (N-M1, « Blocker si confirmé »).
- **Lignes :** 847 ; effets aux l. 819 (`tests-outillage`), 1013 (point 37, étape 7), 1060 (Verification Plan), et spéc. l. 424 (E1), 427 (E4), 430 (E7).
- **Problème :** la l. 847 affirme que `scenarios(".")` « ne produit aucun test » quand il n'existe aucun `.feature`. Or `pytest_bdd.scenarios()` lève `NoScenariosFound` quand il ne trouve aucun scénario. Les trois relecteurs donnent une confiance haute pour les versions 4 à 8, sans l'avoir vérifié pour la 9.0.1. L'appel a lieu à l'import du module, donc pendant la collecte, et `uv run pytest` s'arrête en code 2.
- **Raison :**
  - le point 37 exige « tous verts » : le plan s'arrête avant le commit initial ;
  - si l'on passe outre, `tests-outillage` est rouge sur `main` (E1) et sur chaque pull request ;
  - E7 ne peut pas être vert, et E4, qui en dépend, ne peut pas se jouer.

  Le choix de la correction est une décision de conception, que le standard ne laisse pas à l'exécutant.
- **Correction :**
  1. D'abord, vérifier par une commande, dans un dossier jetable, `scenarios(".")` avec `pytest-bdd` 9.0.1 et aucun `.feature`.
  2. Si l'exception se confirme, écrire au point 25 l'une des deux options :
     - **(a), recommandée par implementation-readiness :** ne pas créer `test_scenarios.py` à M0. M1, qui écrit le premier `.feature`, le crée. Le chemin est protégé dès M0 (cd-1-12).
     - **(b), proposée par codebase-details :** n'appeler la fonction que s'il existe un `.feature` (`if any(Path(__file__).parent.rglob("*.feature")): scenarios(".")`). Le risque de cd-1-12 revient alors : si tous les `.feature` disparaissent, rien ne le signale.
  3. Ne pas attraper l'exception sans condition, et corriger la phrase de la l. 847.

### 3.2 Major

#### egm-codebase-details-2-2 : le garde est rouge sur toute pull request qui ne touche aucun chemin protégé. Sévérité : Major
- **Relecteurs :** codebase-details (M-1), style (N-M4).
- **Lignes :** 754, 756, 835 ; spéc. l. 378 (« retire l'étiquette et le bloc s'ils existent »).
- **Problème :**
  - La l. 835 fait `DELETE` de l'étiquette sans condition, et la sortie `{"etiquette": false}` ne distingue pas « à retirer » de « rien à faire ».
  - Un `DELETE …/issues/$N/labels/<nom>` sur une étiquette absente renvoie 404 (confiance haute). `gh api` sort alors en erreur, et la tâche échoue, puisque la l. 378 la fait échouer sur une erreur d'écriture.
  - Le nom, avec ses espaces et ses accents, doit être encodé dans l'URL, ce que le plan ne dit pas. Le comportement de `gh` sans encodage est incertain (confiance basse).
- **Raison :** à partir de M1, plus aucune pull request de fonctionnalité ne peut être fusionnée. À M0, E3, E6, E8 et E9 portent un échec de plus que celui attendu, et la vérification de la l. 1036 sur E3 tombe sur une erreur d'API.
- **Correction :** `garde.py` lit les étiquettes présentes (`pull_request.labels` de l'événement), et sa sortie dit `poser`, `retirer` ou `rien`. Le `DELETE` n'a lieu que pour `retirer`, avec le nom encodé. Ajouter le cas à `test_garde.py`.

#### egm-codebase-details-2-3 : `gh` n'a pas de jeton dans les workflows. Sévérité : Major
- **Relecteurs :** codebase-details (M-2), implementation-readiness (N4, en Nit).
- **Lignes :** 817, 826-840.
- **Problème :** dans GitHub Actions, `gh` exige `GH_TOKEN` (ou `GITHUB_TOKEN`) dans l'environnement de l'étape, et cette variable n'est pas posée d'office (confiance haute). Le plan n'en parle pas.
- **Raison :** tous les appels `gh api` de `garde` et de `en-attente` échouent, et les deux contrôles obligatoires sont rouges.
- **Correction :** au niveau de la tâche, `env: GH_TOKEN: ${{ github.token }}`. Ce n'est pas une expression `github.event.*`, la règle de la l. 829 est donc respectée. Dire aussi comment `gitleaks` est téléchargé en CI à la l. 817 (par exemple `curl -sSfLO https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz`, puis `sha256sum -c`).

#### egm-codebase-details-2-4 : sur un push, `termes-interdits` reçoit un événement sans pull request et un intervalle vide. Sévérité : Major
- **Relecteurs :** codebase-details (M-3), implementation-readiness (R2), style (N-M3).
- **Lignes :** 738, 739, 741, 742, 808, 818 ; spéc. l. 386-390.
- **Problème :**
  - Sur un push, la l. 818 passe encore `--evenement "$GITHUB_EVENT_PATH"`. L'événement `push` n'a pas de clé `pull_request` (confiance haute). Le point 17 y lit pourtant le titre, la description et la branche, et sort en code 2 sur « une erreur d'entrée ».
  - `BASE` et `HEAD` viennent de `github.event.pull_request.*` et sont vides sur un push. `git log … $BASE..$HEAD` devient `git log ..`, qui ne vérifie aucun message (confiance moyenne).
  - Sur une pull request, la l. 739 (« sans ce paramètre, tous les fichiers suivis sont analysés ») laisse entendre qu'avec `--fichiers`, seuls les fichiers listés le sont. La spéc. l. 387 veut « tous les fichiers suivis ».
- **Raison :** la tâche est rouge, ou d'un comportement inventé, dès le push initial (E1). La portée réelle du contrôle dépend d'une lecture.
- **Correction :**
  - Au point 17 : « Le script analyse toujours tous les fichiers suivis (`git ls-files`). `--fichiers` ne sert qu'à l'exception. Sans `--evenement`, ou si l'événement n'a pas de `pull_request`, le titre, la description et la branche ne sont pas analysés. »
  - Au point 23 : sur un push, omettre `--evenement`, et soit omettre `--messages`, soit prendre `$BEFORE..$AFTER` avec la règle du SHA nul de `gitleaks`.
  - Ajouter un test « événement de push ».

#### egm-codebase-details-2-5 : les fichiers supprimés font sortir `termes_interdits.py` en erreur, et le diff à deux points se trompe de base. Sévérité : Major
- **Relecteurs :** codebase-details (M-4) ; implementation-readiness (R2) et style (N-M3) en parlent en passant.
- **Lignes :** 739, 742, 818.
- **Problème :**
  - `git diff --name-only $BASE $HEAD` liste aussi les fichiers supprimés et l'ancien nom des fichiers renommés (confiance haute). Le plan ne dit pas ce que fait le script d'un fichier absent du disque, et une lecture impossible est une « erreur d'entrée » (code 2).
  - Le diff à deux points compare la pointe de `main` à la tête. Si `main` a avancé, il compte les changements de `main` à l'envers. Le diff à trois points (`$BASE...$HEAD`) ne donne que ceux de la pull request (confiance haute).
- **Raison :** toute pull request qui supprime ou renomme un fichier a `termes-interdits` rouge, et l'exception « ne modifie que la liste » peut être mal évaluée.
- **Correction :** utiliser `git diff --name-only "$BASE...$HEAD"`. Écrire au point 17 qu'un fichier listé mais absent est ignoré. Ajouter le test.

#### egm-codebase-details-2-6 : au point 28, l'agent écrit « acceptée », ce que `CLAUDE.md` et le niveau 1 interdisent. Sévérité : Major
- **Relecteurs :** codebase-details (M-6), implementation-readiness (N7, en Nit).
- **Lignes :** 917 ; /home/ezpk/Projects/4X/CLAUDE.md l. 4 ; /home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md l. 412 (vérifiés).
- **Problème :** les deux textes disent que l'agent « peut rédiger une ADR au statut « proposée », jamais « acceptée » ». Or le point 28 lui fait passer le statut à « acceptée », dans l'ADR et dans l'index.
- **Raison :** le niveau 1 fait foi sur ce document. Un agent qui suit `CLAUDE.md` s'arrête au point 28, sur la règle « en cas de contradiction, s'arrêter ». S'il continue, il enfreint le niveau 1.
- **Correction :** le propriétaire change lui-même le statut dans l'ADR et dans l'index, ou bien une exception est écrite dans le niveau 1 et dans `CLAUDE.md` (points 31 et 32).

#### egm-codebase-details-2-7 : `gh api --paginate … --jq '[…]'` produit un JSON invalide au-delà d'une page. Sévérité : Major
- **Relecteurs :** codebase-details (reste de cd-1-5) ; style le signale hors de son angle.
- **Lignes :** 750, 832.
- **Problème :**
  - Avec `--paginate`, `--jq` s'applique page par page. Au-delà de 30 fichiers, la sortie est une suite de tableaux `[…][…]`. `json.load` échoue alors, et `garde` sort en code 2 (confiance haute).
  - `{filename, previous_filename}` donne `"previous_filename": null`, alors que la l. 750 annonce un champ « absent » (confiance haute).
- **Raison :** une grosse pull request fait tomber le garde, donc bloque la fusion. Le contrat d'entrée de `garde.py` est faux.
- **Correction :** `--jq '.[] | {filename, previous_filename}'`, qui écrit un objet par ligne. `garde.py` lit ce format (JSON Lines) et accepte `null`. Ou bien utiliser `--slurp`, si la version de `gh` installée le permet (à vérifier : gh 2.102.0). Corriger la l. 750 et ajouter un test sur plusieurs pages.

#### egm-codebase-details-2-8 : le texte « avant » de la l. 8 du glossaire est faux, et l'ajout casse la phrase. Sévérité : Major
- **Relecteurs :** codebase-details (reste de cd-1-7), implementation-readiness (R6, en Nit), style (n10).
- **Lignes :** 923, 925-931 ; /home/ezpk/Projects/4X/docs/glossaire.md l. 8 (vérifiée).
- **Problème :**
  - La l. 8 écrit « la phrase du [document de niveau 1](designs/architecture-niveau-1.md) qui définit le terme ». La chaîne citée à la l. 923 ne s'y trouve pas.
  - Appliqué à la lettre, l'ajout donne « …de niveau 1, ou d'un document de niveau 2 pour les termes qu'il introduit qui définit le terme ».
  - Le tableau qui reçoit « tâche », « paquet racine » et « commande d'amorçage » n'est pas nommé.
  - Pour « scénario en attente » et « contrôle obligatoire », on ne sait pas si le nouveau lien remplace le lien §10 ou s'y ajoute.
- **Raison :** l'exécutant réécrit lui-même une phrase d'un chemin protégé, ou il produit une phrase fausse.
- **Correction :** donner la phrase entière de la l. 8, avant et après, lien compris. Nommer le tableau de chaque entrée, et dire si chaque lien remplace ou complète le lien existant.

#### egm-codebase-details-2-9 : le SHA du commit d'une action ne se lit pas dans `/releases`. Sévérité : Major
- **Relecteurs :** codebase-details (M-8), implementation-readiness (N5, en Nit) ; style le signale hors de son angle.
- **Lignes :** 605.
- **Problème :** l'API `releases` donne `tag_name`, `published_at` et `target_commitish`. Ce dernier est le plus souvent un nom de branche (confiance haute). Pour un tag annoté, `git/ref/tags/<tag>` renvoie l'objet tag, pas le commit. « `<propriétaire>` » se confond en outre avec le propriétaire du projet.
- **Raison :** l'épinglage par SHA est une garantie de sécurité (Technical Plan, point 1), et la commande donnée ne la fournit pas.
- **Correction :** prendre la version dans `releases`, puis le SHA par `gh api repos/<organisation>/<action>/commits/<tag> --jq .sha` (confiance moyenne à haute que la route accepte un nom de tag), ou par `git/ref/tags/<tag>` suivi du déréférencement d'un tag annoté.

#### egm-codebase-details-2-10 : la lecture de `en_attente.txt` par l'API n'est pas utilisable telle quelle, et un échec d'API peut ouvrir le contrôle. Sévérité : Major
- **Relecteurs :** codebase-details (M-9), implementation-readiness (N4, en Nit) ; style le signale hors de son angle.
- **Lignes :** 838.
- **Problème :**
  - Par défaut, `contents/…` renvoie du JSON avec le contenu en base64 (confiance haute).
  - « Absente = vide » suppose de distinguer un 404 des autres erreurs. Si toutes les erreurs donnent une liste vide, une panne d'API fait passer la tâche.
  - L'origine de `HEAD_SHA` n'est pas dite, et le `?` hors guillemets est un caractère de motif du shell.
- **Raison :** le contrôle `en-attente` peut se fermer à tort, ou s'ouvrir à tort.
- **Correction :** `gh api -H "Accept: application/vnd.github.raw+json" "repos/EZPK/4X/contents/tests/scenarios/en_attente.txt?ref=$HEAD_SHA"`. Seul « HTTP 404 » vaut liste vide, et toute autre erreur fait échouer la tâche. `HEAD_SHA` est lu dans `$GITHUB_EVENT_PATH`.

#### egm-implementation-readiness-2-1 : la liste des fichiers exclus n'est pas lisible par un script. Sévérité : Major
- **Relecteurs :** implementation-readiness (R3), codebase-details (M-5).
- **Lignes :** 737, 938, 1013, 1065 ; spéc. l. 391.
- **Problème :**
  - Le script lit ses exclusions dans `docs/termes-interdits.md`. Or le point 30 les écrit dans une phrase en prose : « Fichiers exclus : ce fichier, `docs/designs/mmo-gestion-spatiale-ia.md`, `docs/revues/**`, … ».
  - « Ce fichier » n'est pas un chemin, et aucune règle d'extraction n'est donnée.
  - On ne sait pas quelle fonction traduit `docs/revues/**`. Celle de `garde.py` est dans un autre script, et les deux sont limités à la bibliothèque standard.
- **Raison :** c'est un format de données propre au projet, dans un chemin protégé, laissé à l'exécutant. Si « ce fichier » n'est pas compris, `docs/termes-interdits.md` est analysé, ses propres termes y sont trouvés, et le point 37, la l. 1065 et la CI échouent.
- **Correction :** ajouter à `docs/termes-interdits.md` un titre `## Fichiers exclus`, placé après `## Termes`, avec un motif par ligne dans la syntaxe de `chemins-proteges.txt`, `docs/termes-interdits.md` écrit en toutes lettres. Définir ce format au Technical Plan, point 9. Dire si `termes_interdits.py` charge la traduction de `garde.py` ou en a une copie testée par les mêmes cas. Adapter le texte du point 30 et ajouter un test « exclusions lues dans la liste ».

#### egm-implementation-readiness-2-2 : plusieurs gestes des essais ne passent pas la liste blanche du hook (dû au constat accepté egm-design-2-2). Sévérité : Major
- **Relecteurs :** implementation-readiness (N3), codebase-details (M-7, N-5), style (N-M5).
- **Lignes :** 569, 1031, 1036 ; spéc. l. 308, 311-317, 420, 430.
- **Problème :**
  1. **E7** réécrit la description par `gh pr edit --body` (spéc. l. 430). Cette commande n'est pas dans la liste blanche, et elle contredit la l. 569 (`--body-file`).
  2. **Chaque pull request d'essai est « fermée sans fusion »** (spéc. l. 420), mais personne n'est désigné pour la fermer. Aucune commande autorisée ne le fait : `gh pr close` n'est pas listé, et `pulls` n'est permis qu'en « création et description ». Supprimer la branche de tête ferme la pull request (confiance haute), mais la l. 420 met la fermeture avant la suppression, et cette règle n'est écrite nulle part. Comme une seule pull request d'essai peut être ouverte à la fois, la suite se bloque.
  3. **Les commandes `gh` de lecture autres que `gh api`** (`gh pr view`, `gh pr checks`, `gh run view`) n'ont pas de règle. Or la l. 308 fait refuser toute commande `gh` « que le hook ne sait pas analyser ».
  4. **Point 44 :** « pour N de 0 à 6 » invite à une boucle shell, que le hook risque de refuser comme impossible à analyser.
- **Raison :** l'exécutant doit écrire lui-même la politique du hook pour ces cas, ou il est bloqué à E3 et à E7.
- **Correction :**
  - E7 : `gh api -X PATCH repos/EZPK/4X/pulls/<n> -F body=@<fichier>`.
  - Fermeture : écrire que la suppression de la branche ferme la pull request. Ou bien autoriser et tester `gh pr close <n>`, ou `PATCH pulls/<n>` avec `state=closed`, et nommer qui ferme.
  - Dire si les sous-commandes `gh` de lecture sont permises, ou imposer `gh api` en lecture.
  - Point 44 : sept commandes séparées.

#### egm-implementation-readiness-2-3 : `exclude-newer` peut rendre impossibles les bornes basses de `pyproject.toml`. Sévérité : Major
- **Relecteurs :** implementation-readiness (N2), codebase-details (N-2, en Nit).
- **Lignes :** 183, 606-607, 660-661, 682.
- **Problème :**
  - Le point 10 fixe des minimums égaux aux versions vérifiées le 2026-10-31 (`ruff>=0.17.3`, `pytest>=9.2.0`…), et le point 3 fixe `exclude-newer` à la date d'exécution moins 14 jours. Si l'une de ces versions a moins de 14 jours le jour de l'exécution, `uv lock` (point 12) ne trouve aucune solution.
  - La même tension vaut pour `required-version` : la version de `uv` installée peut avoir moins de 14 jours, ce que la l. 183 interdit. L'opérateur (`==` ou `>=`) n'est pas donné.
  - Confiance : le mécanisme est sûr, mais le cas dépend de dates de publication que personne n'a vérifiées.
- **Raison :** l'exécutant doit choisir seul entre baisser une borne et avancer la date.
- **Correction :** au point 3, noter la date de publication de chaque version vérifiée. Écrire la règle, par exemple : « si `uv lock` échoue à cause de `exclude-newer`, la borne de l'outil concerné descend à la dernière version publiée avant cette date, et le changement est noté », ou « s'arrêter et demander ». Donner la forme exacte de `required-version`, et dire si la règle des 14 jours s'applique à `uv`.

#### egm-style-2-1 : les tentatives volontaires de commandes interdites ne sont autorisées nulle part. Sévérité : Major
- **Relecteurs :** style (N-M6), implementation-readiness (N8, en Nit).
- **Lignes :** 1027 (seconde tentative des commandes d'amorçage), 1036 ; spéc. l. 427 (E4), 432 (E9) ; /home/ezpk/Projects/4X/CLAUDE.md l. 4, 13-16, 64.
- **Problème :**
  - En phase 4, `CLAUDE.md` dit de « ne jamais » fusionner, pousser vers `main` ou utiliser `--no-verify`, et de ne jamais employer un terme interdit dans le dépôt, une branche ou une pull request.
  - Or E4 et le point 43 font lancer ces commandes à l'agent, et E9 lui fait écrire un terme interdit dans `src/`, puis ouvrir une pull request.
  - Le plan ne dit pas que ces tentatives sont autorisées, ni qui les demande, ni quoi faire si l'une n'est pas refusée.
- **Raison :** l'exécutant peut lancer ces commandes, ou s'arrêter sur la contradiction comme `CLAUDE.md` l'y oblige.
- **Correction :** en tête de la phase 4 et au point 43, écrire : « Ces tentatives sont des essais, demandés explicitement par le propriétaire. L'agent de code les lance une par une et attend un refus. Si une commande n'est pas refusée, il s'arrête et le signale. Le terme de E9 n'est écrit que dans un fichier de la branche `essai/terme-interdit`, jamais dans le titre, la branche ou le message, et cette branche n'est jamais fusionnée. »

#### egm-style-2-2 : aux points 31 et 32, « la phrase qui commence par » ne dit pas ce qui est remplacé. Sévérité : Major
- **Relecteurs :** style (N-M7), implementation-readiness (R5, en Nit), codebase-details (reste de ir-1-11).
- **Lignes :** 944-960, 966-967 ; /home/ezpk/Projects/4X/CLAUDE.md l. 47 (vérifiée).
- **Problème :**
  - Les éléments à remplacer sont des puces de plusieurs phrases. La puce « Le dépôt est créé au début de M0. » en a trois (`CLAUDE.md` l. 47, niveau 1 §10). Si l'on ne remplace que la première, il reste « C'est la seule exception […], et elle ne vaut qu'une fois », qui contredit le nouveau texte sur les trois commandes d'amorçage.
  - Le même point emploie « Après la puce » (l. 952) : les deux formules ne désignent donc pas la même chose.
  - On ne sait pas où vont le lien §10 conservé (l. 951) et le « (voir …) » ajouté (l. 967), avant ou après le point final.
- **Raison :** ce sont les règles de travail de l'agent lui-même, dans deux chemins protégés, et le point 32 recopie le résultat du point 31 : une erreur passe dans les deux fichiers.
- **Correction :** écrire « la puce entière qui commence par… », et donner chaque puce finale complète, lien compris. Au point 32, donner aussi le texte exact de la puce sur les réglages (voir ir-1-11).

### 3.3 Nits

| Id | Lignes | Problème | Correction |
| :-- | :-- | :-- | :-- |
| egm-style-2-3 | 573, 587, 603, 620-623 | La l. 573 annonce « quatre points » vérifiés, le point 2 en vérifie cinq. Les points 2 et 3 écrivent dans `notes-m0.md`, que le point 5 ne crée qu'ensuite. « Aucun fichier du dépôt n'existe encore » est inexact (`CLAUDE.md` et `docs/` existent). Trois relecteurs le relèvent | « cinq » ; créer `notes-m0.md` au point 2 ; « aucun fichier de M0 n'existe encore » |
| egm-style-2-4 | 594, 596, 565 | « Si le point 4 donne… » et « Si le point 5 donne… » visent des vérifications du point 2. La même phrase cite les points 35 et 36 du plan, alors que les points 4 et 5 du plan sont l'installation de `gitleaks` et `notes-m0.md`. La forme courte « point N » n'est pas prévue par la convention de la l. 10 | Repérer les vérifications par des lettres (a à e) ; écrire à la l. 565 que « point N » désigne un point du plan détaillé |
| egm-style-2-5 | 596, 1035 | La l. 596 parle des étapes propriétaire « des phases 2 à 4 », la l. 1035 des étapes « suivantes ». La phase 2 n'a aucune commande du propriétaire | « les commandes `!` de la phase 4 » |
| egm-style-2-6 | 996 | La reprise ne prévoit pas le cas « nouvelle session seulement » du point 2. Dans ce cas, renommer `settings.json` n'agit qu'après une nouvelle session | L'ajouter |
| egm-style-2-7 | 1023-1025 | Rien ne rappelle que le hook exige la chaîne exacte du Technical Plan, point 3. Au point 39, rien ne dit quoi faire si le hook refuse parce que le blocage est déjà actif (reste du constat accepté egm-style-2-2) | « chaîne exacte, sans option ajoutée » ; « si le refus vient d'un blocage déjà actif, noter la lecture et passer au point 40 » |
| egm-style-2-8 | 1020, 1031 | « demande une demande explicite » ; `title="MN"` se lit comme un texte littéral | « exige une demande explicite » ; `title="M<N>"`, ou les sept titres écrits |
| egm-style-2-9 | 741, 938 ; spéc. l. 392 | Le plan dispense aussi le **titre** de la pull request qui ne modifie que la liste ; la spécification et le texte de `termes-interdits.md` ne le dispensent pas | Aligner les trois textes |
| egm-style-2-10 | 931 | La définition de « commande d'amorçage » (« commandes de création du dépôt ») fait penser à `gh repo create`, qui n'en est pas une | « L'une des trois commandes qui suivent la création du dépôt : activation du blocage des secrets, push initial, protection de `main`. » |
| egm-style-2-11 | 943, 949, 954, 957 | Point 31 : l'annonce « quatre remplacements, puis un ajout » ne suit pas l'ordre réel. « (même renvoi) » n'a pas de sens dans `CLAUDE.md`, qui se lit seul. La puce ajoutée est une sous-puce non indentée. Le nouveau texte des chemins protégés ne nomme plus `docs/termes-interdits.md` (nommé à la l. 32 de `CLAUDE.md`), et « les listes de noms » est ambigu | Suivre l'ordre réel ; répéter le chemin ; indenter ; nommer `docs/noms-valides.md` et `docs/termes-interdits.md` |
| egm-style-2-12 | 968, 971 | Point 32 : ajouter « - `docs/revues/` ; » après une puce qui finit par un point inverse la ponctuation de la liste. « On vérifie par script » ne dit ni qui vérifie ni avec quoi. Préfixer chaque ligne de `    > ` laisse une espace finale sur les lignes vides, alors que la forme actuelle est `    >` (niveau 1, l. 772) | Ponctuation corrigée ; « l'agent de code compare les deux textes par `diff` » ; règle des lignes vides |
| egm-style-2-13 | 755 | « Leur forme échappée » n'est pas définie | Donner la règle, par exemple accent grave → `&#96;`, retour à la ligne → `\n` |
| egm-style-2-14 | 748-751, 833 ; spéc. l. 368 | La spécification fait lire `$GITHUB_EVENT_PATH` par les scripts. Le plan le fait lire par le workflow, qui passe la description dans un fichier | Aligner la spéc. l. 368 sur le plan |
| egm-style-2-15 | 954, 996 ; spéc. l. 303 | La spécification dit que le propriétaire « fait la modification » de `.claude/`. Le plan écrit « fait ou demande » (l. 954) et « l'agent de code corrige » (l. 996) | Aligner la spéc. l. 303 |
| egm-style-2-16 | 807, 822-830, 899 | Un test « par lecture du texte » ne distingue pas le `name:` d'une tâche de celui d'une étape ou du workflow. Le point 24 ne reprend pas la règle « pas de `name:` » pour `garde` et `en-attente` | « clé `name:` au niveau de la tâche » ; reprendre la règle au point 24 |
| egm-style-2-17 | 586 | Anglicisme : « vérification contre la documentation » | « d'après la documentation » |
| egm-style-2-18 | 808, 838 | « etc. » cache la liste des variables `env:`. `$HEAD` (`ci.yml`) et `$HEAD_SHA` (`garde.yml`) désignent la même chose | Lister `BASE`, `HEAD`, `BEFORE`, `AFTER`, `N` ; un seul nom |
| egm-style-2-19 | 604 | `gitleaks` 8.30.1 est écrit en dur. Si le plan s'exécute plus tard, la règle des 14 jours peut désigner une autre version | Dire laquelle des deux règles l'emporte |
| egm-implementation-readiness-2-4 | 1040-1055 ; /home/ezpk/Projects/4X/CLAUDE.md l. 37-38 | Les points 47 et 48 ouvrent chacun une pull request protégée, sans revue EGM prévue, alors que `CLAUDE.md` en impose une avant la demande de fusion. L'ordre des deux n'est pas dit, et le propriétaire déclare M0 « livré » avant la fusion du compte rendu | Une seule pull request, ou le point 48 après la fusion du point 47 ; prévoir la revue EGM |
| egm-implementation-readiness-2-5 | 569, 1014 | Les fichiers passés par `-F` et `--body-file` n'ont pas d'emplacement. Écrits à la racine, ils seraient pris par un `git add -A` suivant. Trois relecteurs le relèvent | Les écrire hors du dépôt, ou sous un nom ignoré par `.gitignore` |
| egm-implementation-readiness-2-6 | 1066 | `gitleaks dir` sur « tout le dossier » : le moment n'est pas fixé, le parcours inclut `.venv/`, les caches et peut-être `.git/` (faux positifs possibles, confiance basse à moyenne), et rien ne dit quoi faire si quelque chose est trouvé. Trois relecteurs le relèvent | Le lancer avant le point 47, sur les fichiers suivis et `notes-m0.md` ; reprendre la règle d'arrêt du point 37 |
| egm-implementation-readiness-2-7 | 584-598, 1024 | Pousser `.github/workflows/` en HTTPS avec le jeton de `gh` exige la portée `workflow` (confiance moyenne : elle est en général incluse) | En phase 0 : `gh auth status`, et noter les portées et le protocole de git |
| egm-implementation-readiness-2-8 | 1036 ; spéc. l. 425 | La branche `essai/push-direct` de E2 n'est jamais poussée : le `DELETE` du point 46 échoue sur elle. La suppression des branches locales n'est prévue nulle part | Le dire ; prévoir `git branch -D` |
| egm-codebase-details-2-11 | 846, 889-900 | Session imbriquée : `steps_exemple.py` ne suit pas le motif `test_*.py`, et rien n'appelle `scenarios()` dans `pytester`. `pytester` change de dossier courant (confiance haute), donc le chemin relatif `tests/scenarios/conftest.py` ne se lit plus. Le plan ne dit pas que `conftest.py` cherche `en_attente.txt` à partir de son propre dossier, ni par quel hook de pytest il fait échouer la session. Les cas « en attente qui échoue », « titre en double » et « plan de scénario » exigent d'autres `.feature`. Trois relecteurs le relèvent | Lire la copie depuis `Path(__file__)` ou `request.config.rootpath` ; recopier `steps_exemple.py` sous le nom `test_exemple.py` avec `scenarios("exemple.feature")` ; chaque test écrit ses `.feature` ; liste lue à côté de `conftest.py` ; nommer le hook pytest |
| egm-codebase-details-2-12 | 906-912 ; /home/ezpk/Projects/4X/docs/adr/README.md l. 17-18, 23 | Les champs « Conséquences » et « Condition de révision » de l'ADR 0001 n'ont pas de contenu. On ne sait pas si la ligne d'index remplace « Aucune ADR pour l'instant. ». Trois relecteurs le relèvent | Donner les deux champs ; « la ligne remplace “Aucune ADR pour l'instant.” » |
| egm-codebase-details-2-13 | 606, 661, 811 | `astral-sh/setup-uv` n'a pas d'entrée `version`. Le runner peut donc prendre une version de `uv` plus récente que la règle des 14 jours ne le permet, ou refusée par `required-version` (confiance moyenne qu'il lit `required-version`) | `required-version = "==X.Y.Z"` et `with: version: "X.Y.Z"` dans les deux workflows |
| egm-codebase-details-2-14 | 856 | La fonction de chargement définie dans `tests/outillage/conftest.py` n'est pas importable de façon fiable en `--import-mode=importlib` (confiance moyenne) | En faire une fixture |
| egm-codebase-details-2-15 | 1009-1012, 1024 ; spéc. l. 308 | Rien ne dit que le hook accepte `git add`, `status`, `diff`, `switch` et `log`. `gitleaks git --pre-commit …` contient « git » suivi d'options que git ne connaît pas, et une analyse naïve le refuserait (seconde moitié de N-5, étape 8) | Lister les commandes acceptées et les tester |
| egm-codebase-details-2-16 | spéc. l. 428 (E5), joué au point 46 | Un `ghp_` suivi de 36 caractères au hasard n'a pas de somme CRC32 valide, et le blocage de GitHub ne le refusera probablement pas (confiance moyenne). Le plan le prévoit (« blocage non démontré ») | Un jeton fabriqué avec une somme valide rendrait la démonstration possible |
| egm-codebase-details-2-17 | 986-987 | Le JSON d'essai du hook n'a ni `hook_event_name`, ni `cwd`, ni `session_id`. Si le hook refuse une « entrée JSON inattendue », la commande `ls` donne 2 au lieu de 0 | Dire quels champs le hook exige, et les mettre dans le JSON d'essai |

---

## 4. Bilan

- **Relecteurs :** egm-implementation-readiness, egm-codebase-details et egm-style ont tous terminé au premier essai.
- **Tour 1 :** 33 résolus, 10 partiellement résolus, 0 non résolu. Les constats partiellement résolus sont ir-1-8, ir-1-11, ir-1-15, ir-1-18, cd-1-5, cd-1-7, cd-1-12, style-1-4, style-1-5 et style-1-8. Un seul reste Major par lui-même : cd-1-12.
- **Nouveaux constats :** 1 Blocker, 14 Major, 29 Nit.
- **Ordre conseillé des corrections :**
  1. cd-2-1 et cd-1-12, ensemble ;
  2. cd-2-2, cd-2-3, cd-2-4, cd-2-5, ir-2-1 (CI et garde) ;
  3. ir-2-2, style-2-1, cd-2-6 (hook et règles de l'agent) ;
  4. style-2-2, cd-2-8 (textes des chemins protégés) ;
  5. cd-2-7, cd-2-9, cd-2-10, ir-2-3 (commandes et versions) ;
  6. les Nits.
- **Le plan peut-il être exécuté étape par étape sans décision importante ?** **Non.** Le Blocker arrête le point 37. Au moins six Major font échouer une étape ou un contrôle tel qu'il est écrit : cd-2-2, cd-2-3, cd-2-4, cd-2-5, ir-2-1 et cd-2-7. D'autres laissent un choix de conception à l'exécutant : ir-2-2, ir-2-3, cd-2-6 et style-2-1. Comme ce tour était la seule réaudit autorisée, ces corrections devront être appliquées sans nouveau passage de l'étape 9. Les constats techniques non vérifiés (cd-2-1 en tête, puis cd-2-2, cd-2-7, cd-2-9 et cd-2-10) doivent être confirmés par une commande avant d'être corrigés.

---

## Décision du propriétaire (2026-11-01) : corriger, puis conclure

La limite de relecture de l'étape 9 est atteinte. Le propriétaire a choisi de corriger le bloquant et les majeurs sans nouvelle relecture, puis de conclure la revue.

**Faits vérifiés par commande avant correction (2026-11-01) :**
- `scenarios(".")` sans `.feature` : `NoScenariosFound` à la collecte, code 2 (pytest-bdd 9.0.1). Le bloquant est confirmé ;
- `gh api --paginate --jq '[…]'` : JSON invalide sur plusieurs pages ; `--jq '.[] | …'` donne un objet par ligne, et `previous_filename` vaut `null` ;
- `gh api repos/actions/checkout/commits/<tag> --jq .sha` donne le SHA du commit ;
- `gh api -H "Accept: application/vnd.github.raw+json" …/contents/…` : un fichier absent donne « HTTP 404 », code 1 ;
- dates de publication : ruff 0.17.3 (2026-10-27), mypy 2.4.1 (2026-10-28), pytest 9.2.0 (2026-10-27) et pytest-bdd 9.0.1 (2026-10-31) ont moins de 14 jours. Avec `exclude-newer = 2026-10-18`, les versions retenues sont ruff 0.17.1, mypy 2.4.0, pytest 9.1.1, pytest-bdd 9.0.0, import-linter 2.15 et pre-commit 4.7.0. Elles fonctionnent sous Python 3.15 (scénario en français, `mypy --strict`, `ruff`).

**Corrigés :** le bloquant cd-2-1, les 14 majeurs (cd-2-2 à cd-2-10, ir-2-1 à ir-2-3, style-2-1 et 2-2), et le reste majeur cd-1-12. Quelques mineurs ont été corrigés au passage : cd-2-14 (fixture), ir-2-8 (branches locales), style-2-8 (sept commandes de jalons).

**Restent ouverts, et deviennent des risques acceptés à vérifier pendant l'implémentation :** les autres mineurs de ce rapport, et les réglages qui n'ont pas pu être vérifiés sans dépôt. Ce sont le retrait d'une étiquette absente (contourné, car on ne retire que si l'étiquette est présente) et la portée `workflow` du jeton `gh` (ir-2-7).
