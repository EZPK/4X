# Rapport de revue : étape 5 (Zoom Out initial), document de M0

*   **Document revu :** [niveau-2-m0-garde-fous.md](../../designs/niveau-2-m0-garde-fous.md), lignes 1 à 630
*   **Standard :** zoom-out-standard (EGM)
*   **Contexte fourni :** `CLAUDE.md`, `docs/glossaire.md`, `docs/termes-interdits.md`, `docs/feuille-de-route.md`. Le niveau 1, lié dans le document, a été lu en entier.
*   **Relecteur :** egm-zoom-out, sans contexte de la conversation
*   **Date :** 2026-10-31
*   **Verdict :** à corriger avant approbation. 2 bloquants, 7 majeurs, 14 mineurs.

Le relecteur juge que l'objectif est clair et vise le vrai problème : faire passer les règles de `CLAUDE.md` de la discipline de l'agent à des mécanismes.

## Bloquants

### B1. Le hook bloque les lectures dont le plan a besoin

*   **Où :** Technical Plan §3 (l. 191), §4 (l. 205), point 16 (l. 518), étape 25 (l. 594).
*   **Problème :** le point 16 refuse tout `gh api` sur `/protection` ou `/branches/main`, quelle que soit la méthode. Or §4 et l'étape 25 demandent de *lire* la protection pour vérifier `enforce_admins.enabled`. L'agent serait arrêté dès la phase 2.
*   **Correction :** ne refuser que les écritures. Un `gh api` en lecture pure passe : sans `-X` ni `--method` autre que GET, et sans `-f`, `-F`, `--field`, `--raw-field` ni `--input`. Ajouter le cas « lecture de la protection autorisée » aux tests.

### B2. La troisième exception d'amorçage ne se ferme jamais

*   **Où :** Goals 3 (l. 46), §3 (l. 178 et 184), 19 ter (l. 563), étape 25 (l. 594).
*   **Problème :**
    - Plusieurs passages disent que chaque exception se ferme d'elle-même, mais la l. 184 dit que la troisième reste ouverte.
    - Le hook vérifie le texte de la commande, pas le contenu du fichier. Or ce fichier est local, et le contrôle de garde n'en signale les modifications qu'en pull request.
    - Un PATCH sur `repos/EZPK/4X` peut donc changer n'importe quel réglage : visibilité, branche par défaut, archivage.
*   **Correction :** fermer l'exception par l'état de GitHub : refus dès que `secret_scanning_push_protection.status` vaut `enabled`, ou que la fonction n'est pas disponible. À défaut, le hook lit le fichier et refuse toute autre clé. Aligner ensuite les lignes 46, 178, 184, 563 et 594.
*   **Variante signalée, sans remettre en cause le choix du propriétaire :**
    - lancer les trois commandes d'amorçage avant de créer `.claude/settings.json`, puis faire entrer `.claude/` par la première pull request protégée ;
    - cela supprime toute la logique d'exception du hook et sert aussi d'essai réel ;
    - l'agent garde la main sur le push et les réglages.

## Majeurs

| Constat | Où | Problème | Correction |
| :-- | :-- | :-- | :-- |
| M1 : le hook laisse passer la commande s'il plante | §6, point 16 | Claude Code ne bloque qu'avec le code 2. Une exception Python, un interpréteur introuvable ou un JSON inattendu laisseraient donc passer la commande | Bibliothèque standard seulement, tout le corps dans un `try/except` qui sort avec le code 2, interpréteur explicite, tests « entrée invalide » et « exception interne » → code 2 |
| M2 : découper le shell laisse passer des variantes | §6, points 16 et 18 | Analyser le shell (`bash -c`, `eval`, variables) est un petit analyseur. La liste noire de `gh api` est trouée : `--method PATCH`, `-XPATCH`, POST implicite avec `-f`, `repos/{owner}/{repo}`, `transfer`, `collaborators`, `actions/permissions` | Commandes d'amorçage reconnues par égalité exacte ; motifs interdits cherchés dans la chaîne brute, sans découpage ; pour `gh api`, toute écriture refusée sauf une liste de chemins autorisés (`/issues`, `/milestones`) |
| M3 : le test des termes interdits fait échouer la CI | §9, point 18 | Le test contiendrait un terme interdit en clair, dans un fichier suivi et non exclu | Le test lit les termes dans `docs/termes-interdits.md` ou les écrit dans `tmp_path`. Ne pas exclure `tests/` |
| M4 : protéger tout `pyproject.toml` crée une impasse | §11, points 4 et 10 ; niveau 1 §10 | Les dépendances vivent dans le même fichier. Dès M1, ajouter `msgspec` toucherait un chemin protégé | Mettre la configuration des contrôles dans des fichiers à part (`ruff.toml`, `mypy.ini`, `pytest.ini`, `.importlinter`) et ne protéger que ceux-là ; laisser `pyproject.toml` et `uv.lock` hors protection |
| M5 : le contrôle de garde et l'agent se disputent le haut de la description | §8, points 9 et 13 ; `CLAUDE.md` | Le résumé EGM de l'agent écrase le bloc de garde, et `pull_request_target` ne se relance pas sur `edited` | Déclencher aussi sur `edited`, fixer l'ordre (bloc de garde, puis résumé EGM) ; ou un commentaire unique mis à jour |
| M6 : le niveau 1 approuvé est modifié sans ADR | §9, points 19 bis et 19 ter ; niveau 1 ; `docs/adr/README.md` | Trois changements de choix du niveau 1 ; seules les décisions déjà écrites le 2026-10-31 sont dispensées d'ADR | Une ADR `0001` en phase 1, proposée par l'agent et acceptée par le propriétaire ; ou une trace explicite du rattachement aux décisions du 2026-10-31 |
| M7 : injection de script dans les workflows | §8, points 8, 9 et 13 ; NFR | Titre, description, commits, branche et noms de fichiers viennent de l'auteur. Les insérer avec `${{ github.event.* }}` dans un `run:` permet d'exécuter du code, ici avec `pull-requests: write` | Règle : aucune expression `${{ github.event.* }}` dans un `run:`. Les données passent par `env:` ou par `$GITHUB_EVENT_PATH`, lu par les scripts |

## Mineurs

| Constat | Correction |
| :-- | :-- |
| N1 : on suppose sans le vérifier que les commandes `!` échappent aux règles de Claude Code | L'ajouter aux questions ouvertes, ou lancer ces commandes dans un terminal hors de Claude Code |
| N2 : catégorie `references` et exclusion de `en_attente.txt` sans usage à M0 | Les reporter à M1 |
| N3 : `hypothesis` et contrats `import-linter` sans usage à M0 | Les reporter, ou lancer `lint-imports` en contrôle non requis |
| N4 : `.env.example` invente des noms de variables | Un seul commentaire, ou ajouter ces noms au glossaire |
| N5 : `.gitignore` non ancré à la racine | `/data/`, `/snapshots/`… |
| N6 : mypy ne couvre ni `.claude/hooks/` ni `.github/scripts/` | Les ajouter |
| N7 : « tests de l'outillage » absent de Goals 6 | L'ajouter, en le notant comme ajout au niveau 1 |
| N8 : la liste des chemins protégés est ambiguë et incomplète (`.python-version`, `uv.lock`, `tests/outillage/`) | Donner la liste complète des motifs |
| N9 : `docs/m0/commandes-proprietaire.md` fait une troisième copie | Une seule section dans le document ou le compte rendu |
| N10 : la pull request du compte rendu n'a pas de type valide (`docs/revues/` n'est pas protégé) | Lui donner un type explicite |
| N11 : deux sources pour les versions des outils | Dire laquelle l'emporte |
| N12 : « au moins vingt » et « dix » sont des chiffres arbitraires | S'en tenir à la règle de couverture par catégorie |
| N13 : `actions/labeler` couvre déjà l'étiquetage | L'envisager, ou justifier le script maison |
| N14 : deux voies d'installation pour `gitleaks` | Choisir un hook local qui appelle le même binaire qu'en CI |
