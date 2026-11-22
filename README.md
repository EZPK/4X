# 4X

Jeu de gestion spatiale dans le terminal, au style rétro 8 bits, avec des joueurs IA entraînés hors ligne.

Pour commencer : `CLAUDE.md`, `docs/feuille-de-route.md` et `docs/designs/architecture-niveau-1.md`.

## Jouer

`make jouer` lance la dernière version stable du jeu : le dernier état de la branche `main` sur GitHub, joué depuis un dossier de travail à part (`.worktrees/stable`), sans toucher à la branche en cours. `make jouer-ici` lance la version du dossier courant. Options : `GRAINE=42`, `DEV=1` (mode développement). Le terminal doit faire au moins 120 colonnes × 36 lignes. `make` seul affiche l'aide.

## Développer

Installation d'un clone : `uv sync --locked`, puis `uv run pre-commit install`. `gitleaks` 8.30.1 doit être dans le `PATH` : voir `docs/designs/niveau-2-m0-garde-fous.md`, plan détaillé, point 4.

Tous droits réservés. Aucune licence n'accorde de droit de réutilisation de ce code.
