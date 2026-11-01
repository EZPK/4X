# Rapport de revue : étape 8 (Zoom Out intermédiaire), document de M0

*   **Document revu :** [niveau-2-m0-garde-fous.md](../../designs/niveau-2-m0-garde-fous.md), lignes 1 à 811
*   **Standard :** zoom-out-standard (EGM)
*   **Relecteur :** egm-zoom-out, sans contexte de la conversation
*   **Date :** 2026-11-01
*   **Verdict :** l'ossature est proportionnée, mais trois zones sont sur-spécifiées et ne convergent pas. Trois simplifications sont recommandées avant l'implémentation, sans refonte. Aucun bloquant, 2 nouveaux majeurs, 5 nouveaux mineurs.

## 1. Statut des constats de l'étape 5

| Constat | Statut |
| :-- | :-- |
| B1 : le hook bloque les lectures | Résolu |
| B2 : la 3e exception ne se ferme pas | Partiellement résolu. La contradiction du PATCH reste (acceptée). La variante « amorcer avant d'activer le hook » n'a été ni retenue ni écartée (M-A) |
| M1 : un hook qui plante laisse passer | Partiellement résolu. `python3` absent, erreur de syntaxe et délai réseau dépassé ne sont pas couverts (accepté) |
| M2 : l'analyse du shell est trouée | Partiellement résolu. « Déterminer la branche cible » réintroduit l'analyse du shell (accepté) |
| M3 : le test des termes interdits fait échouer la CI | Résolu |
| M4 : `pyproject.toml` est protégé | Résolu. Le trou des configurations par dossier est accepté |
| M5 : le garde dispute la tête de la description au résumé EGM | Partiellement résolu. Une course entre deux exécutions reste possible (accepté) |
| M6 : le niveau 1 est modifié sans ADR | Partiellement résolu. La dispense d'ADR est fausse pour E4 et E5 (accepté, ADR à faire) |
| M7 : injection dans les workflows | Résolu |
| N1 à N14 | Résolus, sauf N2 et N8, partiellement (voir N-1 ; `fnmatch` est accepté). N13 est écarté avec une raison recevable |

## 2. Verdict à haute altitude

**L'objectif et l'ossature conviennent.** Le document vise la vraie cause : faire passer les règles de `CLAUDE.md` de la discipline de l'agent à des mécanismes. Il réutilise les outils de la plateforme quand ils existent.

**Le document pose lui-même le bon principe :** M0 protège contre les erreurs, pas contre un contournement délibéré. Trois zones sont pourtant spécifiées comme si elles devaient tenir face à un adversaire :
1. **L'amorçage logé dans le hook :**
   - ce que ça coûte : lectures réseau depuis le hook, copies de référence des JSON, égalité exacte, quatre états testés pour chacune des trois commandes ;
   - à quoi ça sert : trois commandes lancées une seule fois, à la demande du propriétaire.
2. **La politique du hook,** qui mélange liste noire, liste blanche et analyse de la branche cible. Chaque tour de revue trouve de nouvelles variantes : une énumération de ce type ne converge pas. Avec une liste blanche fermée, l'énumération des variantes peut aller dans les tests.
3. **La tâche `en-attente` et le mécanisme de `conftest.py`,** livrés à M0 alors qu'aucun scénario n'existe avant M1.

**Les 15 majeurs acceptés au tour 2 de l'étape 7 confirment ce verdict.** Sept d'entre eux tombent dans ces trois zones ou dans les règles `gitleaks` propres au projet. Les simplifications en font disparaître la plupart.

**Essentiel, à garder :**
- le dépôt et le commit initial ;
- les secrets : blocage avant le push, `gitleaks` en pre-commit et en CI, `gitleaks git` avant le push initial ;
- la protection de `main`, avec la relecture des réglages et la procédure de reprise ;
- les règles `deny` (y compris Edit et Write sur `.claude/**` et `.git/hooks/**`) ;
- un hook pour les écritures GitHub et le push vers `main` ;
- le contrôle de garde lancé depuis `main`, avec les règles contre l'injection ;
- le script des termes interdits, et les tâches `lint`, `typage` et `tests-outillage` ;
- les essais E1 à E7, E9 et E10 ;
- le tableau des décisions et celui des écarts.

**Couper ou simplifier :**
- **Le hook :** une seule liste blanche fermée pour les verbes sensibles (écritures `gh`, `git push`, `git commit`). Quelques formes exactes sont acceptées, et tout le reste de ces verbes est refusé. Le hook ne détermine plus la branche suivie : la protection de GitHub est la vraie barrière. Les variantes refusées vont dans le plan de tests.
- **L'amorçage :** le sortir du hook (M-A).

**Reporter :**
- à M1 : l'application de la marque « en attente » (M-B) et l'étiquette « références régénérées » (N-1) ;
- à M4 : les règles `gitleaks` sur les adresses IPv4 privées et sur les variables `FOURX_`. On ne garde que la règle d'essai. Ce report règle aussi le constat accepté egm-structural-2-2 (« le document se détecte lui-même ») ;
- jusqu'à ce que la solution de rechange soit déclenchée : `ruleset-main.json` (N-2).

## 3. Nouveaux constats

### M-A (Majeur) : la variante la plus simple de l'amorçage n'est pas pesée

*   **Où :** Technical Plan, points 3 et 6 ; alternative E ; plan détaillé, points 24 et 25 ; essai E4 ; risque « une exception se rouvre ».
*   **Problème :** la variante proposée à l'étape 5 (B2) n'est traitée nulle part. Elle consiste à lancer les trois commandes d'amorçage avant que `.claude/settings.json` existe, puis à faire entrer `.claude/settings.json` par la première pull request protégée.
*   **Pourquoi c'est important :**
    - L'écart E1 est conservé, puisque c'est toujours l'agent de code qui lance les commandes.
    - Toute la logique d'amorçage sort du hook : lectures réseau, copies de référence, douze cas de test, condition de `gh repo create`, contradiction du PATCH, risque « une exception se rouvre ».
    - Une seconde tentative reste refusée par la liste blanche générale.
    - Le coût : pendant les quatre commandes de la phase 2, demandées une à une par le propriétaire, l'agent de code travaille sans hook, comme aujourd'hui.
*   **Correction :** ajouter cette variante aux alternatives, avec la décision du propriétaire.
    - Si elle est retenue : déplacer `.claude/settings.json` après l'amorçage, le faire entrer par une pull request protégée, réduire le point 3 à l'ordre des commandes, et ajuster les écarts E1 et E2.
    - Sinon : consigner la raison du rejet.

### M-B (Majeur) : la marque « en attente » est appliquée un jalon trop tôt

*   **Où :** Overview, Goal 6, CUJ 6, Technical Plan, points 8 et 10 ; plan détaillé, points 15, 21, 22 et 23 ; essai E8 ; écart E5.
*   **Problème :** le niveau 1 demande à M0 de *fixer* le moyen, pas de l'appliquer. Or il n'y a aucun scénario à M0. Le document livre pourtant un contrôle obligatoire, des scripts, un `conftest.py`, des sessions imbriquées, un essai, un objectif et un CUJ.
*   **Pourquoi c'est important :** c'est du YAGNI. Les défauts ouverts de ce mécanisme se règlent mieux à M1, face à de vrais scénarios. Le report réduit aussi l'écart E5, donc l'ADR qu'il demande.
*   **Correction :**
    - garder à M0 la décision (liste, format, règle des ajouts) et un fichier `en_attente.txt` vide ;
    - reporter le reste à M1 ;
    - retirer le Goal 6, le CUJ 6 et `en-attente` des contrôles obligatoires.

    C'est au propriétaire d'accepter ce report.

### Mineurs

| Constat | Correction |
| :-- | :-- |
| N-1 : l'étiquette « références régénérées » est créée à M0, alors que les Non-Goals la reportent | La créer à M1 |
| N-2 : `ruleset-main.json` est écrit d'avance. C'est une troisième copie des mêmes exigences, qui divergera à M1 | Ne l'écrire que si la solution de rechange est déclenchée |
| N-3 : l'installation locale du binaire `gitleaks` n'est pas prévue | Une étape en tête de la phase 1 (téléchargement, somme de contrôle, emplacement), reprise dans `README.md` |
| N-4 : le hook est appelé par un chemin relatif. Après un changement de dossier, toutes les commandes Bash seraient refusées | `python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/garde_commandes.py"`, à vérifier en phase 0 |
| N-5 : le hook est activé et vérifié avant `git init` | `git init -b main` au début de la phase 1 ; lister les commandes `git` locales que le hook accepte |
